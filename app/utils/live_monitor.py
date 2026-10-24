import os
import pandas as pd

from utils.predictor import (
    model,
    imputer,
    encoder,
    feature_names,
    categorical_cols,
    get_risk_category,
    apply_behavioral_adjustment
)

from utils.database import save_transaction


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "data", "dataset-ieee", "train_transaction.csv")

live_df = None
live_index = 0


def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value)


def clean_number(value, default=0):
    if pd.isna(value):
        return default

    try:
        return float(value)
    except ValueError:
        return default


def load_live_data():
    global live_df

    if live_df is None:
        df = pd.read_csv(CSV_PATH, nrows=20000)
        df = df.sample(n=5000, random_state=42).reset_index(drop=True)
        live_df = df

    return live_df


def get_risk_factors(row, risk_category):
    risk_factors = []

    transaction_amt = clean_number(row.get("TransactionAmt", 0))
    dist1 = clean_number(row.get("dist1", 0))
    product_cd = clean_text(row.get("ProductCD", "")).upper()
    email_domain = clean_text(row.get("P_emaildomain", "")).lower()

    trusted_email_domains = [
        "yahoo.ro",
        "mapn.ro",
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "hotmail.com",
        "icloud.com",
        "protonmail.com",
        "aol.com",
        "live.com",
        "msn.com"
    ]

    if transaction_amt > 1000:
        risk_factors.append("High transaction amount")

    if dist1 > 100:
        risk_factors.append("Large distance from usual location")

    if email_domain and email_domain not in trusted_email_domains:
        risk_factors.append("Email domain not found in trusted provider list")

    if product_cd in ["C", "H"]:
        risk_factors.append("High-risk product category")

    if risk_category == "High Risk":
        risk_factors.append("Transaction classified as high risk")

    return risk_factors


def process_live_transaction():
    global live_index

    df = load_live_data()

    if live_index >= len(df):
        live_index = 0

    row = df.iloc[live_index]
    live_index += 1

    row_df = pd.DataFrame([row])

    for col in feature_names:
        if col not in row_df.columns:
            row_df[col] = 0

    df_model = row_df[feature_names].copy()

    df_model[categorical_cols] = encoder.transform(
        df_model[categorical_cols].astype(str)
    )

    df_model = pd.DataFrame(
        imputer.transform(df_model),
        columns=feature_names
    )

    fraud_probability = model.predict_proba(df_model)[0, 1]
    risk_score = fraud_probability * 100

    form_like_data = {
        "TransactionAmt": clean_number(row.get("TransactionAmt", 0)),
        "dist1": clean_number(row.get("dist1", 0)),
        "P_emaildomain": clean_text(row.get("P_emaildomain", "")),
        "ProductCD": clean_text(row.get("ProductCD", ""))
    }

    risk_score = apply_behavioral_adjustment(form_like_data, risk_score)
    risk_category = get_risk_category(risk_score)

    risk_factors = get_risk_factors(row, risk_category)

    transaction = {
        "transaction_amt": clean_number(row.get("TransactionAmt", 0)),
        "transaction_dt": clean_number(row.get("TransactionDT", 0)),
        "card1": clean_text(row.get("card1", "")),
        "card2": clean_text(row.get("card2", "")),
        "card4": clean_text(row.get("card4", "")),
        "addr1": clean_text(row.get("addr1", "")),
        "dist1": clean_number(row.get("dist1", 0)),
        "product_cd": clean_text(row.get("ProductCD", "")),
        "email": clean_text(row.get("P_emaildomain", "")),
        "customer_email": "",
        "fraud_probability": round(float(fraud_probability), 4),
        "risk_score": round(float(risk_score), 2),
        "risk_category": risk_category,
        "risk_factors": ", ".join(risk_factors),
        "email_alert_sent": False,
        "customer_alert_sent": False
    }

    save_transaction(transaction)

    return transaction