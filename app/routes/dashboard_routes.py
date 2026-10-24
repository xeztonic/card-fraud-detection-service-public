from flask import render_template, request

from services.dashboard_service import (
    calculate_dashboard_stats,
    filter_transactions,
    paginate_transactions
)
from utils.auth import login_required
from utils.database import get_transactions


# Registers dashboard page routes.
def register_dashboard_routes(app):

    # Displays the main fraud monitoring dashboard.
    @app.route("/dashboard")
    @login_required
    def dashboard():
        all_transactions = get_transactions()

        all_transactions = sorted(
            all_transactions,
            key=lambda t: int(t.get("id", 0)),
            reverse=True
        )

        search_query = request.args.get("search", "").strip().lower()
        selected_category = request.args.get("category", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = 15

        filtered_transactions = filter_transactions(
            all_transactions,
            search_query,
            selected_category
        )

        paginated_transactions, page, total_pages = paginate_transactions(
            filtered_transactions,
            page,
            per_page
        )

        stats = calculate_dashboard_stats(all_transactions)

        return render_template(
            "dashboard.html",
            transactions=paginated_transactions,
            total_transactions=stats["total_transactions"],
            legitimate_count=stats["legitimate_count"],
            suspicious_count=stats["suspicious_count"],
            high_risk_count=stats["high_risk_count"],
            legitimate_percent=stats["legitimate_percent"],
            suspicious_percent=stats["suspicious_percent"],
            high_risk_percent=stats["high_risk_percent"],
            alerts_sent=stats["alerts_sent"],
            average_risk_score=stats["average_risk_score"],
            high_risk_rate=stats["high_risk_rate"],
            search_query=request.args.get("search", ""),
            selected_category=(
                selected_category if selected_category else "All Risk Categories"
            ),
            page=page,
            total_pages=total_pages
        )
