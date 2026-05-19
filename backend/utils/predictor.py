import numpy as np

def predict_churn(model, scaler, encoder, df):
    numerical_features = ['Age', 'Tenure', 'Usage Frequency', 'Support Calls', 'Payment Delay', 'Total Spend', 'Last Interaction']
    categorical_features = ['Gender', 'Subscription Type', 'Contract Length']
    
    X_num = scaler.transform(df[numerical_features])
    X_cat = encoder.transform(df[categorical_features])
    X_processed = np.hstack((X_num, X_cat))

    prob = model.predict_proba(X_processed)[0][1]
    pred_class = model.predict(X_processed)[0]
    
    return pred_class, prob
