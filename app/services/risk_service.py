from utils.customer_alert import send_customer_notification
from utils.email_alert import send_fraud_alert


# Safely converts form or database values to float.
def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


# Returns the trusted email domains used by behavioral rules.
def get_trusted_email_domains():
    return [
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
    ]


# Builds the visible risk factor list for a simulated transaction.
def get_risk_factors_from_form(form_data, risk_category):
    risk_factors = []

    transaction_amt = safe_float(form_data.get("TransactionAmt"))
    dist1 = safe_float(form_data.get("dist1"))
    product_cd = form_data.get("ProductCD", "").upper()
    email_domain = form_data.get("P_emaildomain", "").lower()

    if transaction_amt > 1000:
        risk_factors.append("High transaction amount")

    if dist1 > 100:
        risk_factors.append("Large distance from usual location")

    if email_domain and email_domain not in get_trusted_email_domains():
        risk_factors.append("Email domain not found in trusted provider list")

    if product_cd in ["C", "H"]:
        risk_factors.append("High-risk product category")

    if risk_category == "High Risk":
        risk_factors.append("Transaction classified as high risk")

    return risk_factors


# Converts prediction output into values that are easier to explain in the UI.
def build_prediction_scores(result):
    base_ml_score = round(float(result["fraud_probability"]) * 100, 2)
    final_risk_score = round(float(result["risk_score"]), 2)
    behavioral_adjustment = round(final_risk_score - base_ml_score, 2)

    if behavioral_adjustment < 0:
        behavioral_adjustment = 0

    return base_ml_score, final_risk_score, behavioral_adjustment


# Builds the transaction dictionary saved in the database.
def build_transaction_from_form(form_data, result, final_risk_score, risk_factors):
    return {
        "transaction_amt": form_data.get("TransactionAmt"),
        "transaction_dt": form_data.get("TransactionDT"),
        "card1": form_data.get("card1"),
        "card2": form_data.get("card2"),
        "card4": form_data.get("card4"),
        "addr1": form_data.get("addr1"),
        "dist1": form_data.get("dist1"),
        "product_cd": form_data.get("ProductCD"),
        "email": form_data.get("P_emaildomain"),
        "customer_email": form_data.get("customer_email"),
        "fraud_probability": result["fraud_probability"],
        "risk_score": final_risk_score,
        "risk_category": result["risk_category"],
        "risk_factors": ", ".join(risk_factors),
        "email_alert_sent": False,
        "customer_alert_sent": False
    }


# Sends email alerts for suspicious and high-risk transactions.
def handle_transaction_alerts(transaction):
    if transaction["risk_category"] not in ["Suspicious", "High Risk"]:
        return transaction

    admin_email_sent = send_fraud_alert(transaction)
    customer_email_sent = send_customer_notification(transaction)

    transaction["email_alert_sent"] = admin_email_sent
    transaction["customer_alert_sent"] = customer_email_sent

    return transaction
