import os

from flask import redirect, render_template, request, session, url_for


# Registers authentication and session routes.
def register_auth_routes(app):

    # Redirects the base URL to the login page.
    @app.route("/")
    def home():
        return redirect(url_for("login"))

    # Handles admin login and creates the user session.
    @app.route("/login", methods=["GET", "POST"])
    def login():
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin")
        error = None

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == admin_username and password == admin_password:
                session.clear()
                session.permanent = True
                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("dashboard"))

            error = "Invalid username or password"

        return render_template("login.html", error=error)

    # Logs out the admin and clears the current session.
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
