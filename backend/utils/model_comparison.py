import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def get_model_metrics():
    """
    Generates comparison metrics for all four supported models dynamically.
    Returns the best model name based on highest accuracy (not hardcoded).
    """
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    models_dir  = os.path.join(backend_dir, 'models')
    data_path   = os.path.join(backend_dir, '..', 'customer_churn_dataset-training-master.csv')

    # Model display name → actual .pkl filename in models/
    model_files = {
        "Logistic Regression": "logistic_model.pkl",
        "KNN":                 "knn_model.pkl",
        "Naive Bayes":         "naive_bayes.pkl",   # correct filename
        "SVM":                 "svm_model.pkl"
    }

    # Verify all model files exist before proceeding
    for name, fname in model_files.items():
        fpath = os.path.join(models_dir, fname)
        if not os.path.exists(fpath):
            return {"error": f"Model file '{fname}' not found. Train models first."}

    # Load dataset for evaluation
    if not os.path.exists(data_path):
        return {"error": "Training dataset not found."}

    df = pd.read_csv(data_path).dropna()
    if len(df) > 10000:
        df = df.sample(n=10000, random_state=42)

    numerical_features  = ['Age', 'Tenure', 'Usage Frequency', 'Support Calls',
                            'Payment Delay', 'Total Spend', 'Last Interaction']
    categorical_features = ['Gender', 'Subscription Type', 'Contract Length']

    scaler  = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
    encoder = joblib.load(os.path.join(models_dir, 'encoder.pkl'))

    X_num = scaler.transform(df[numerical_features])
    X_cat = encoder.transform(df[categorical_features])
    X_processed = np.hstack((X_num, X_cat))

    y = df['Churn']
    _, X_test, _, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    metrics = {}

    for name, fname in model_files.items():
        clf    = joblib.load(os.path.join(models_dir, fname))
        y_pred = clf.predict(X_test)

        metrics[name] = {
            "accuracy":  round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall":    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1_score":  round(float(f1_score(y_test, y_pred, zero_division=0)), 4)
        }

    # Determine best model dynamically by highest accuracy
    best_model = max(metrics, key=lambda m: metrics[m]["accuracy"])

    return {
        "models":     metrics,
        "best_model": best_model
    }
