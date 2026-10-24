import os
import joblib
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "random_forest_model.pkl")
IMPUTER_PATH = os.path.join(MODELS_DIR, "imputer.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "encoder.pkl")
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "feature_names.pkl")
CATEGORICAL_COLS_PATH = os.path.join(MODELS_DIR, "categorical_cols.pkl")

model = joblib.load(MODEL_PATH)
imputer = joblib.load(IMPUTER_PATH)
encoder = joblib.load(ENCODER_PATH)
feature_names = joblib.load(FEATURE_NAMES_PATH)
categorical_cols = joblib.load(CATEGORICAL_COLS_PATH)


def get_risk_category(risk_score):
    if risk_score < 30:
        return "Legitimate"
    elif risk_score < 70:
        return "Suspicious"
    return "High Risk"


def create_transaction_input(form_data):
    transaction = pd.DataFrame(
        np.zeros((1, len(feature_names))),
        columns=feature_names
    )

    for feature in feature_names:
        if feature in form_data:
            value = form_data.get(feature)

            if value == "":
                value = 0

            try:
                value = float(value)
            except ValueError:
                transaction[feature] = transaction[feature].astype(object)
            
            transaction.loc[0, feature] = value

    return transaction


def predict_transaction(form_data):
    transaction = create_transaction_input(form_data)

    transaction[categorical_cols] = encoder.transform(
        transaction[categorical_cols].astype(str)
    )

    transaction = pd.DataFrame(
        imputer.transform(transaction),
        columns=feature_names
    )

    fraud_probability = model.predict_proba(transaction)[:, 1][0]
    risk_score = fraud_probability * 100
    risk_score = apply_behavioral_adjustment(form_data, risk_score)
    risk_category = get_risk_category(risk_score)

    return {
        "fraud_probability": round(float(fraud_probability), 4),
        "risk_score": round(float(risk_score), 2),
        "risk_category": risk_category
    }

# For simulation
def apply_behavioral_adjustment(form_data, risk_score):
    amount = float(form_data.get("TransactionAmt", 0) or 0)
    distance = float(form_data.get("dist1", 0) or 0)
    email_domain = form_data.get("P_emaildomain", "").lower()
    product_code = form_data.get("ProductCD", "").upper()

    adjustment = 0

    if amount > 1000:
        adjustment += 25

    if amount > 3000:
        adjustment += 25

    if distance > 100:
        adjustment += 15

    if distance > 300:
        adjustment += 15

    trusted_email_domains = [
        "yahoo.ro",
        "outlook.com",
        "mapn.ro",
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "hotmail.com",
        "icloud.com",
        "protonmail.com",
        "aol.com",
        "live.com",
        "msn.com",
    ]

    if email_domain and email_domain not in trusted_email_domains:
        adjustment += 10

    if product_code == "C":
        adjustment += 10

    final_score = min(risk_score + adjustment, 100)

    return final_score