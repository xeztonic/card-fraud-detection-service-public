import os

from flask import current_app, redirect, request, send_file, url_for
from werkzeug.utils import secure_filename

from utils.auth import login_required
from utils.csv_importer import import_transactions_from_csv
from utils.database import (
    clear_transactions,
    export_transactions_to_csv
)


# Registers CSV import, CSV export, and clear-history routes.
def register_file_routes(app):

    # Deletes all stored transactions from the database.
    @app.route("/clear-history", methods=["POST"])
    @login_required
    def clear_history():
        clear_transactions()
        return redirect(url_for("dashboard"))

    # Exports all stored transactions to a CSV file.
    @app.route("/export-csv")
    @login_required
    def export_csv():
        csv_path = export_transactions_to_csv()

        return send_file(
            csv_path,
            as_attachment=True,
            download_name="transactions_export.csv"
        )

    # Imports historical transactions from an uploaded IEEE-CIS CSV file.
    @app.route("/import-csv", methods=["POST"])
    @login_required
    def import_csv():
        uploaded_file = request.files.get("csv_file")

        if not uploaded_file or uploaded_file.filename == "":
            return redirect(
                url_for("dashboard", import_error="No CSV file selected.")
            )

        filename = secure_filename(uploaded_file.filename)

        if not filename.lower().endswith(".csv"):
            return redirect(
                url_for(
                    "dashboard",
                    import_error="Invalid file type. Please upload a CSV file."
                )
            )
        
        upload_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)

        uploaded_file.save(upload_path)

        try:
            imported_count = import_transactions_from_csv(upload_path, limit=2000)
            return redirect(url_for("dashboard", imported=imported_count))

        except ValueError as error:
            return redirect(url_for("dashboard", import_error=str(error)))
