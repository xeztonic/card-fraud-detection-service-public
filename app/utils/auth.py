from functools import wraps

from flask import jsonify, redirect, session, url_for


# Protects normal HTML routes that require authentication.
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# Protects JSON routes used by JavaScript fetch requests.
def json_login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "Unauthorized"}), 401

        return route_function(*args, **kwargs)

    return wrapper
