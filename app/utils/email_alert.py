import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_RECEIVER = os.getenv("MAIL_RECEIVER")


def send_fraud_alert(transaction):
    if not MAIL_USERNAME or not MAIL_PASSWORD or not MAIL_RECEIVER:
        print("Email settings are missing.")
        return False

    subject = f"Fraud Alert - {transaction['risk_category']} Transaction Detected"

    body = f"""
A suspicious transaction has been detected by the Fraud Detection System.

Transaction Details:
- Amount: {transaction.get('transaction_amt')}
- Card ID: {transaction.get('card1')}
- Email Domain: {transaction.get('email')}
- Risk Score: {transaction.get('risk_score')}
- Risk Category: {transaction.get('risk_category')}

This transaction may require manual review.
"""

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = MAIL_USERNAME
    message["To"] = MAIL_RECEIVER
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(message)

        return True

    except Exception as e:
        print("Email alert failed:", e)
        return False