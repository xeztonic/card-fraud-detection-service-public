from flask import render_template, request

from services.risk_service import (
    build_prediction_scores,
    build_transaction_from_form,
    get_risk_factors_from_form,
    handle_transaction_alerts
)
from utils.auth import login_required
from utils.database import save_transaction
from utils.predictor import predict_transaction


# Registers transaction simulation routes.
def register_simulation_routes(app):

    # Displays the transaction simulation form and prediction result.
    @app.route("/simulate", methods=["GET", "POST"])
    @login_required
    def simulate():
        prediction = None

        if request.method == "POST":
            result = predict_transaction(request.form)

            base_ml_score, final_risk_score, behavioral_adjustment = (
                build_prediction_scores(result)
            )

            risk_factors = get_risk_factors_from_form(
                request.form,
                result["risk_category"]
            )

            transaction = build_transaction_from_form(
                request.form,
                result,
                final_risk_score,
                risk_factors
            )

            transaction = handle_transaction_alerts(transaction)

            save_transaction(transaction)

            prediction = {
                **result,
                "base_ml_score": base_ml_score,
                "behavioral_adjustment": behavioral_adjustment,
                "final_risk_score": final_risk_score,
                "email_alert_sent": transaction["email_alert_sent"],
                "customer_alert_sent": transaction["customer_alert_sent"],
                "risk_factors": risk_factors
            }

        return render_template("simulate.html", prediction=prediction)
