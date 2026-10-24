from flask import jsonify

from services.dashboard_service import (
    build_live_chart_data,
    calculate_dashboard_stats
)
from utils.auth import json_login_required
from utils.database import get_recent_transactions, get_transactions
from utils.live_monitor import process_live_transaction


# Registers live monitoring JSON routes.
def register_live_routes(app):

    # Processes one random live transaction and saves it in the database.
    @app.route("/live-step", methods=["POST"])
    @json_login_required
    def live_step():
        transaction = process_live_transaction()

        return jsonify({
            "status": "success",
            "transaction": transaction
        })

    # Returns recent transactions for live dashboard components.
    @app.route("/live-data")
    @json_login_required
    def live_data():
        transactions = get_recent_transactions(limit=150)

        return jsonify(transactions)

    # Returns the latest transactions displayed in the live table.
    @app.route("/live-table-data")
    @json_login_required
    def live_table_data():
        transactions = get_recent_transactions(limit=15)
        transactions = transactions[::-1]

        return jsonify(transactions)

    # Returns transaction points used by the live risk chart.
    @app.route("/live-chart-data")
    @json_login_required
    def live_chart_data():
        transactions = get_recent_transactions(limit=30)
        transactions = transactions[::-1]

        chart_data = build_live_chart_data(transactions)

        return jsonify(chart_data)

    # Returns dashboard statistics used by live JavaScript updates.
    @app.route("/live-stats")
    @json_login_required
    def live_stats():
        transactions = get_transactions()
        stats = calculate_dashboard_stats(transactions)

        return jsonify(stats)
