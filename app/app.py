import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from routes.auth_routes import register_auth_routes
from routes.dashboard_routes import register_dashboard_routes
from routes.file_routes import register_file_routes
from routes.live_routes import register_live_routes
from routes.simulation_routes import register_simulation_routes
from utils.database import init_db


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "fraud_detection_secret_key")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.config["UPLOAD_DIR"] = UPLOAD_DIR

init_db()


# Prevents browser cache from showing protected pages after logout.
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# Registers all application routes.
register_auth_routes(app)
register_dashboard_routes(app)
register_simulation_routes(app)
register_file_routes(app)
register_live_routes(app)


# Starts the Flask development server.
if __name__ == "__main__":
    app.run(debug=True)
