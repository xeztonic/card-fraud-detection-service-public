import math

from services.risk_service import safe_float


# Calculates dashboard metrics and risk category distribution.
def calculate_dashboard_stats(transactions):
    total_transactions = len(transactions)

    legitimate_count = len([
        t for t in transactions
        if t.get("risk_category") == "Legitimate"
    ])

    suspicious_count = len([
        t for t in transactions
        if t.get("risk_category") == "Suspicious"
    ])

    high_risk_count = len([
        t for t in transactions
        if t.get("risk_category") == "High Risk"
    ])

    legitimate_percent = (
        legitimate_count / total_transactions * 100
        if total_transactions else 0
    )

    suspicious_percent = (
        suspicious_count / total_transactions * 100
        if total_transactions else 0
    )

    high_risk_percent = (
        high_risk_count / total_transactions * 100
        if total_transactions else 0
    )

    alerts_sent = len([
        t for t in transactions
        if t.get("email_alert_sent") or t.get("customer_alert_sent")
    ])

    average_risk_score = (
        sum(safe_float(t.get("risk_score")) for t in transactions)
        / total_transactions
        if total_transactions else 0
    )

    high_risk_rate = (
        high_risk_count / total_transactions * 100
        if total_transactions else 0
    )

    return {
        "total_transactions": total_transactions,
        "legitimate_count": legitimate_count,
        "suspicious_count": suspicious_count,
        "high_risk_count": high_risk_count,
        "legitimate_percent": round(legitimate_percent, 2),
        "suspicious_percent": round(suspicious_percent, 2),
        "high_risk_percent": round(high_risk_percent, 2),
        "alerts_sent": alerts_sent,
        "average_risk_score": round(average_risk_score, 2),
        "high_risk_rate": round(high_risk_rate, 2)
    }


# Filters transactions by search text and selected risk category.
def filter_transactions(transactions, search_query, selected_category):
    searchable_fields = [
        "id",
        "transaction_amt",
        "transaction_dt",
        "card1",
        "card2",
        "card4",
        "addr1",
        "dist1",
        "product_cd",
        "email",
        "customer_email",
        "fraud_probability",
        "risk_score",
        "risk_category",
        "risk_factors",
        "email_alert_sent",
        "customer_alert_sent",
        "created_at"
    ]

    filtered_transactions = []

    for transaction in transactions:
        matches_search = True
        matches_category = True

        if search_query:
            matches_search = any(
                search_query in str(transaction.get(field, "")).lower()
                for field in searchable_fields
            )

        if selected_category and selected_category != "All Risk Categories":
            matches_category = (
                transaction.get("risk_category") == selected_category
            )

        if matches_search and matches_category:
            filtered_transactions.append(transaction)

    return filtered_transactions


# Paginates the transactions displayed in the dashboard table.
def paginate_transactions(transactions, page, per_page):
    total_pages = max(1, math.ceil(len(transactions) / per_page))

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    return transactions[start:end], page, total_pages


# Builds compact chart data for the live monitoring chart.
def build_live_chart_data(transactions):
    chart_data = []

    for transaction in transactions:
        chart_data.append({
            "id": transaction["id"],
            "risk_score": safe_float(transaction.get("risk_score")),
            "risk_category": transaction.get("risk_category", "Legitimate"),
            "transaction_amt": transaction.get("transaction_amt", ""),
            "card1": transaction.get("card1", ""),
            "email": transaction.get("email", ""),
            "customer_email": transaction.get("customer_email", "")
        })

    return chart_data
