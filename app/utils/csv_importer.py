import pandas as pd

from utils.database import save_transaction
from utils.predictor import (
    apply_behavioral_adjustment,
    categorical_cols,
    encoder,
    feature_names,
    get_risk_category,
    imputer,
    model
)


# Required IEEE-CIS columns needed by the application import flow.
REQUIRED_IEEE_CIS_COLUMNS = {
    "TransactionDT",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "card2",
    "card4",
    "addr1",
    "dist1",
    "P_emaildomain"
}


# Trusted email domains used for behavioral risk explanation.
TRUSTED_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "yahoo.ro",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "protonmail.com",
    "aol.com",
    "live.com",
    "msn.com",
    "mail.com",
    "zoho.com",
    "gmx.com",
    "mapn.ro"
}


# Converts missing values to a default value.
def clean_value(value, default=""):
    if pd.isna(value):
        return default

    return value


# Converts values to text and handles missing values.
def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


# Converts values to numbers and handles invalid values.
def clean_number(value, default=0):
    if pd.isna(value):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# Validates that the uploaded CSV matches the IEEE-CIS transaction structure.
def validate_ieee_cis_csv(csv_path):
    try:
        header_df = pd.read_csv(csv_path, nrows=0)
    except Exception:
        raise ValueError(
            "Invalid CSV file. Please upload a readable IEEE-CIS transaction CSV file."
        )

    csv_columns = set(header_df.columns)
    missing_columns = sorted(REQUIRED_IEEE_CIS_COLUMNS - csv_columns)

    if missing_columns:
        missing_preview = ", ".join(missing_columns)

        raise ValueError(
            "Invalid CSV structure. Please upload an IEEE-CIS transaction CSV file, "
            "such as train_transaction.csv or test_transaction.csv. "
            f"Missing required columns: {missing_preview}."
        )


# Reads a valid IEEE-CIS CSV file and returns a random sample.
def load_csv_sample(csv_path, limit):
    validate_ieee_cis_csv(csv_path)

    df = pd.read_csv(csv_path, nrows=15000)

    if len(df) > limit:
        df = df.sample(n=limit, random_state=42)

    return df.reset_index(drop=True)


# Ensures all model features exist before prediction.
def prepare_model_dataframe(df):
    missing_feature_data = {
        col: 0
        for col in feature_names
        if col not in df.columns
    }

    if missing_feature_data:
        df = pd.concat(
            [df, pd.DataFrame(missing_feature_data, index=df.index)],
            axis=1
        )

    df_model = df[feature_names].copy()

    df_model[categorical_cols] = encoder.transform(
        df_model[categorical_cols].astype(str)
    )

    df_model = pd.DataFrame(
        imputer.transform(df_model),
        columns=feature_names
    )

    return df_model


# Builds risk factors shown in the dashboard details column.
def build_risk_factors(transaction_amt, dist1, email_domain, product_cd, risk_category):
    risk_factors = []

    if transaction_amt > 1000:
        risk_factors.append("High transaction amount")

    if dist1 > 100:
        risk_factors.append("Large distance from usual location")

    if email_domain and email_domain not in TRUSTED_EMAIL_DOMAINS:
        risk_factors.append("Email domain not found in trusted provider list")

    if product_cd in ["C", "H"]:
        risk_factors.append("High-risk product category")

    if risk_category == "High Risk":
        risk_factors.append("Transaction classified as high risk")

    return risk_factors


# Converts one CSV row into the database transaction format.
def build_transaction_from_row(row, fraud_probability):
    transaction_amt = clean_number(row.get("TransactionAmt", 0))
    dist1 = clean_number(row.get("dist1", 0))

    email_domain = clean_text(row.get("P_emaildomain", "")).lower()
    product_cd = clean_text(row.get("ProductCD", "")).upper()

    form_like_data = {
        "TransactionAmt": transaction_amt,
        "dist1": dist1,
        "P_emaildomain": email_domain,
        "ProductCD": product_cd
    }

    risk_score = fraud_probability * 100
    risk_score = apply_behavioral_adjustment(form_like_data, risk_score)
    risk_category = get_risk_category(risk_score)

    risk_factors = build_risk_factors(
        transaction_amt,
        dist1,
        email_domain,
        product_cd,
        risk_category
    )

    return {
        "transaction_amt": transaction_amt,
        "transaction_dt": clean_value(row.get("TransactionDT", "")),
        "card1": clean_value(row.get("card1", "")),
        "card2": clean_value(row.get("card2", "")),
        "card4": clean_text(row.get("card4", "")),
        "addr1": clean_value(row.get("addr1", "")),
        "dist1": dist1,
        "product_cd": product_cd,
        "email": email_domain,
        "customer_email": "",
        "fraud_probability": round(float(fraud_probability), 4),
        "risk_score": round(float(risk_score), 2),
        "risk_category": risk_category,
        "risk_factors": ", ".join(risk_factors),
        "email_alert_sent": False,
        "customer_alert_sent": False
    }


# Imports historical transactions from an IEEE-CIS CSV file.
def import_transactions_from_csv(csv_path, limit=1000):
    df = load_csv_sample(csv_path, limit)
    df_model = prepare_model_dataframe(df)

    probabilities = model.predict_proba(df_model)[:, 1]

    imported_count = 0

    for index, row in df.iterrows():
        transaction = build_transaction_from_row(
            row,
            probabilities[index]
        )

        save_transaction(transaction)
        imported_count += 1

    return imported_count