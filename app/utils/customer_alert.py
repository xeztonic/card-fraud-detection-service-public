import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


def send_customer_notification(transaction):

    customer_email = transaction.get("customer_email")

    if not customer_email:
        return False

    subject = "Card Transaction Security Review Notification"

    body = f"""
Dear cardholder,

We are contacting you because our fraud monitoring system has identified a transaction that requires additional review.

Please do not worry. Our team is already analyzing the transaction marked as suspicious. If the review confirms any negative or unauthorized activity, we will contact you as soon as possible using the contact methods provided to us.

Transaction details:
- Amount: {transaction.get("transaction_amt", "-")}
- Card identifier: {transaction.get("card1", "-")}
- Transaction email domain: {transaction.get("email", "-")}
- Risk score: {transaction.get("risk_score", "-")}
- Risk category: {transaction.get("risk_category", "-")}

Detected risk factors:
{transaction.get("risk_factors", "-")}

If you recognize this transaction, no immediate action is required. If you do not recognize it, please remain attentive to further communication from our team.

Kind regards,
Fraud Detection Monitoring Team
"""

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = MAIL_USERNAME
    message["To"] = customer_email

    message.set_content(body)

    try:

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(message)

        return True

    except Exception as e:
        print("Customer notification failed:", e)
        return False