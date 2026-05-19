import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.compose import ColumnTransformer
import joblib
import os

def train_model():
    print("Loading dataset...")
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', 'customer_churn_dataset-training-master.csv')
    df = pd.read_csv(data_path)

    df = df.dropna()

    # Sample to 50k to ensure models train in a reasonable time locally without overfitting
    if len(df) > 50000:
        df = df.sample(n=50000, random_state=42)

    # Features and Target
    X = df.drop(columns=['CustomerID', 'Churn'])
    y = df['Churn']

    categorical_features = ['Gender', 'Subscription Type', 'Contract Length']
    numerical_features = ['Age', 'Tenure', 'Usage Frequency', 'Support Calls', 'Payment Delay', 'Total Spend', 'Last Interaction']

    print("Preprocessing data...")
    # Separate preprocessing to match requested scaler.pkl and encoder.pkl
    # We will manually apply scaling and encoding to save them separately
    scaler = StandardScaler()
    encoder = OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False)
    
    # Fit scaler and encoder
    X_num = scaler.fit_transform(X[numerical_features])
    X_cat = encoder.fit_transform(X[categorical_features])
    
    # Combine processed features
    X_processed = np.hstack((X_num, X_cat))

    # Train-test split (80-20)
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
    
    # Downsample for SVM to avoid extremely long training times on 440k rows
    svm_sample_size = min(10000, len(X_train))
    idx = np.random.choice(len(X_train), svm_sample_size, replace=False)
    X_train_svm = X_train[idx]
    y_train_svm = y_train.iloc[idx] if hasattr(y_train, 'iloc') else y_train[idx]

    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "KNN": KNeighborsClassifier(),
        "Naive Bayes": GaussianNB(),
        "SVM": SVC(probability=True)
    }

    results = {}
    best_model_name = ""
    best_accuracy = 0
    best_model = None

    print("\nTraining models...\n")

    for name, clf in classifiers.items():
        print(f"Training {name}...")
        if name == "SVM":
            clf.fit(X_train_svm, y_train_svm)
        else:
            clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1
        }
        
        # We will follow user request to use SVM results predominantly
        # but still track the 'natural' best for metrics if needed.
        # However, user said "generate results with SVM", so we ensure it's saved.
        if name == "SVM" or acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = clf

    # Print Comparison
    print("\n==================================")
    print("MODEL COMPARISON RESULTS")
    print("==================================\n")
    for name, metrics in results.items():
        print(f"{name}")
        print(f"Accuracy: {metrics['accuracy']:.0%}")
        print(f"Precision: {metrics['precision']:.0%}")
        print(f"Recall: {metrics['recall']:.0%}")
        print(f"F1 Score: {metrics['f1_score']:.0%}\n")

    # Force SVM as best model for the prediction flow as requested
    if "SVM" in classifiers:
        best_model = classifiers["SVM"]
        best_model_name = "SVM"

    print("==================================")
    print(f"BEST MODEL (USER SELECTED): {best_model_name}")
    print(f"Accuracy: {results[best_model_name]['accuracy']:.0%}")
    print("==================================\n")

    # Save models
    print("Saving models...")
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Save individual models
    joblib.dump(classifiers["Logistic Regression"], os.path.join(models_dir, 'logistic_model.pkl'))
    joblib.dump(classifiers["KNN"], os.path.join(models_dir, 'knn_model.pkl'))
    joblib.dump(classifiers["Naive Bayes"], os.path.join(models_dir, 'naive_bayes_model.pkl'))
    joblib.dump(classifiers["SVM"], os.path.join(models_dir, 'svm_model.pkl'))
    
    # Save best model (SVM as requested)
    joblib.dump(best_model, os.path.join(models_dir, 'best_model.pkl'))
    
    # Save Scaler and Encoder
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    joblib.dump(encoder, os.path.join(models_dir, 'encoder.pkl'))

    print(f"Training complete! Models saved to backend/models/.")

if __name__ == "__main__":
    train_model()
