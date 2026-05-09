import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.compose import ColumnTransformer
import joblib
import os

def train_model():
    print("Loading dataset...")
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', 'customer_churn_dataset-training-master.csv')
    df = pd.read_csv(data_path)

    # Drop missing values
    df = df.dropna()

    # Features and Target
    # We will ignore CustomerID
    X = df.drop(columns=['CustomerID', 'Churn'])
    y = df['Churn']

    # Define categorical and numerical features
    categorical_features = ['Gender', 'Subscription Type', 'Contract Length']
    numerical_features = ['Age', 'Tenure', 'Usage Frequency', 'Support Calls', 'Payment Delay', 'Total Spend', 'Last Interaction']

    print("Preprocessing data...")
    # Preprocessing
    # Using ColumnTransformer to apply different preprocessing to different columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
        ])

    X_processed = preprocessor.fit_transform(X)

    # Train-test split (80-20)
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Train Logistic Regression
    print("Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Predictions
    print("Evaluating model...")
    y_pred = model.predict(X_test)

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("-" * 30)
    print("Model Evaluation Results:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("-" * 30)

    # Save model and preprocessor
    print("Saving model and preprocessor...")
    backend_dir = os.path.dirname(__file__)
    joblib.dump(model, os.path.join(backend_dir, 'model.pkl'))
    joblib.dump(preprocessor, os.path.join(backend_dir, 'preprocessor.pkl'))
    
    # We save a unified preprocessor rather than separate scaler and encoder for simpler inference.
    print("Training complete! Model saved to backend/model.pkl and backend/preprocessor.pkl.")

if __name__ == "__main__":
    train_model()
