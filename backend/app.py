import os
import sqlite3
import pandas as pd
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import joblib

from utils.suggestions import generate_suggestions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"]}})

# Load Model and Preprocessor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')
PREPROCESSOR_PATH = os.path.join(BASE_DIR, 'preprocessor.pkl')
DB_PATH = os.path.join(BASE_DIR, 'database.db')

model = None
preprocessor = None

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print("Model and Preprocessor loaded successfully.")
except Exception as e:
    print(f"Error loading model/preprocessor: {e}")

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            gender TEXT,
            tenure INTEGER,
            usage_frequency INTEGER,
            support_calls INTEGER,
            payment_delay INTEGER,
            subscription_type TEXT,
            contract_length TEXT,
            total_spend REAL,
            last_interaction INTEGER,
            prediction TEXT,
            probability REAL,
            risk_level TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Customer Churn Prediction API Running"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Extract features
        features = {
            'Age': [int(data.get('age', 0))],
            'Gender': [data.get('gender', '')],
            'Tenure': [int(data.get('tenure', 0))],
            'Usage Frequency': [int(data.get('usage_frequency', 0))],
            'Support Calls': [int(data.get('support_calls', 0))],
            'Payment Delay': [int(data.get('payment_delay', 0))],
            'Subscription Type': [data.get('subscription_type', '')],
            'Contract Length': [data.get('contract_length', '')],
            'Total Spend': [float(data.get('total_spend', 0))],
            'Last Interaction': [int(data.get('last_interaction', 0))]
        }

        # Convert to DataFrame
        df = pd.DataFrame(features)

        # Preprocess
        X_processed = preprocessor.transform(df)

        # Predict
        prob = model.predict_proba(X_processed)[0][1] # Probability of Class 1 (Churn)
        pred_class = model.predict(X_processed)[0]

        prediction_text = "Likely to Churn" if pred_class == 1 else "Likely to Stay"
        probability = round(prob, 4)

        # Determine Risk Level
        if probability >= 0.7:
            risk_level = "High"
        elif probability >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Generate Suggestions
        suggestions = generate_suggestions(data, risk_level)

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO predictions (
                age, gender, tenure, usage_frequency, support_calls, payment_delay,
                subscription_type, contract_length, total_spend, last_interaction,
                prediction, probability, risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('age'), data.get('gender'), data.get('tenure'), data.get('usage_frequency'),
            data.get('support_calls'), data.get('payment_delay'), data.get('subscription_type'),
            data.get('contract_length'), data.get('total_spend'), data.get('last_interaction'),
            prediction_text, probability, risk_level
        ))
        conn.commit()
        conn.close()

        return jsonify({
            "prediction": prediction_text,
            "probability": probability,
            "risk_level": risk_level,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM predictions ORDER BY timestamp DESC')
        rows = c.fetchall()
        conn.close()

        history = [dict(ix) for ix in rows]
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<int:id>', methods=['DELETE'])
def delete_history(id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM predictions WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
