import os
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, send_file # type: ignore
from flask_cors import CORS # type: ignore
import joblib

from utils.suggestions import generate_suggestions
from utils.model_comparison import get_model_metrics
from database.mongo import MongoDBHandler
from reports.report_generator import generate_pdf_report
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"]}})

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Shared preprocessors (loaded once at startup)
scaler = None
encoder = None
db_handler = MongoDBHandler()

# Supported classifiers map: display name → .pkl filename
SUPPORTED_MODELS = {
    "Logistic Regression": "logistic_model.pkl",
    "KNN":                 "knn_model.pkl",
    "Naive Bayes":         "naive_bayes.pkl",
    "SVM":                 "svm_model.pkl"
}

try:
    scaler  = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
    encoder = joblib.load(os.path.join(MODELS_DIR, 'encoder.pkl'))
    print("Scaler and Encoder loaded successfully.")
except Exception as e:
    print(f"Error loading preprocessors: {e}. Train the models first!")


def load_selected_model(selected_model: str):
    """
    Load and return the joblib model corresponding to the user-selected
    classifier name. Raises ValueError for unknown names.
    """
    if selected_model not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unknown model '{selected_model}'. "
            f"Supported: {list(SUPPORTED_MODELS.keys())}"
        )
    model_file = SUPPORTED_MODELS[selected_model]
    model_path = os.path.join(MODELS_DIR, model_file)
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file '{model_file}' not found in models directory. "
            "Please retrain the models."
        )
    return joblib.load(model_path)


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Customer Churn Prediction API Running with MongoDB"})


@app.route('/available-models', methods=['GET'])
def available_models():
    """Return the list of supported classifier names for the frontend selector."""
    return jsonify({"models": list(SUPPORTED_MODELS.keys())})


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        # ── Validate selected_model ──────────────────────────────────────────
        selected_model = data.get('selected_model', '').strip()
        if not selected_model:
            return jsonify({"error": "Please select a prediction model before submitting."}), 400
        if selected_model not in SUPPORTED_MODELS:
            return jsonify({"error": f"Invalid model '{selected_model}'. Choose from: {list(SUPPORTED_MODELS.keys())}"}), 400

        # ── Load the user-selected model ─────────────────────────────────────
        model = load_selected_model(selected_model)

        # ── Build feature dataframe ──────────────────────────────────────────
        features_dict = {
            'Age':               [int(data.get('age', 0))],
            'Gender':            [data.get('gender', '')],
            'Tenure':            [int(data.get('tenure', 0))],
            'Usage Frequency':   [int(data.get('usage_frequency', 0))],
            'Support Calls':     [int(data.get('support_calls', 0))],
            'Payment Delay':     [int(data.get('payment_delay', 0))],
            'Subscription Type': [data.get('subscription_type', '')],
            'Contract Length':   [data.get('contract_length', '')],
            'Total Spend':       [float(data.get('total_spend', 0))],
            'Last Interaction':  [int(data.get('last_interaction', 0))]
        }

        df = pd.DataFrame(features_dict)

        from utils.predictor import predict_churn
        pred_class, prob = predict_churn(model, scaler, encoder, df)

        prediction_text = "Likely to Churn" if int(pred_class) == 1 else "Likely to Stay"
        probability = round(float(prob), 4)

        if probability >= 0.7:
            risk_level = "High"
        elif probability >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Strip selected_model from customer_data before storing
        customer_data = {k: v for k, v in data.items() if k != 'selected_model'}
        suggestions = generate_suggestions(customer_data, risk_level)

        # ── Persist to MongoDB ───────────────────────────────────────────────
        db_doc = {
            "selected_model": selected_model,
            "customer_data":  customer_data,
            "prediction":     prediction_text,
            "probability":    probability,
            "risk_level":     risk_level,
            "suggestions":    suggestions,
            "timestamp":      datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db_handler.insert_prediction(db_doc)

        return jsonify({
            "prediction":     prediction_text,
            "probability":    probability,
            "risk_level":     risk_level,
            "selected_model": selected_model,
            "suggestions":    suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/model-comparison', methods=['GET'])
def model_comparison():
    try:
        metrics = get_model_metrics()
        if "error" in metrics:
            return jsonify(metrics), 400
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        model_filter = request.args.get('model', '').strip()
        history = db_handler.get_all_predictions(model_filter=model_filter if model_filter else None)

        flattened_history = []
        for doc in history:
            flat_doc = {
                "id":             doc['_id'],
                "prediction":     doc.get('prediction'),
                "probability":    doc.get('probability'),
                "risk_level":     doc.get('risk_level'),
                "timestamp":      doc.get('timestamp'),
                "selected_model": doc.get('selected_model') or doc.get('used_model', 'Unknown')
            }
            # Merge customer fields to the top level for the frontend
            cust = doc.get('customer_data', {})
            flat_doc.update(cust)
            flattened_history.append(flat_doc)

        return jsonify(flattened_history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<id>', methods=['DELETE'])
def delete_history(id):
    try:
        success = db_handler.delete_prediction(id)
        if success:
            return jsonify({"message": "Deleted successfully"})
        return jsonify({"error": "Failed to delete"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    try:
        count = db_handler.clear_all_predictions()
        return jsonify({"message": f"Cleared {count} records successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate-report', methods=['GET'])
def generate_report():
    try:
        history = db_handler.get_all_predictions()
        pdf_bytes = generate_pdf_report(history)

        temp_pdf_path = os.path.join(BASE_DIR, 'reports', 'churn_report.pdf')
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        return send_file(
            temp_pdf_path,
            as_attachment=True,
            download_name='Churn_Prediction_Report.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate-report/<id>', methods=['GET'])
def generate_specific_report(id):
    try:
        doc = db_handler.get_prediction_by_id(id)
        if not doc:
            return jsonify({"error": "Prediction not found"}), 404
        
        pdf_bytes = generate_pdf_report([doc])

        temp_pdf_path = os.path.join(BASE_DIR, 'reports', f'churn_report_{id}.pdf')
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        return send_file(
            temp_pdf_path,
            as_attachment=True,
            download_name=f'Churn_Prediction_Report_{id}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
