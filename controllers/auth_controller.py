"""
AuthController - handles login, logout, and the dashboard.
Routes: /login, /logout, /dashboard
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from repositories.user_repository import UserRepository
from repositories.audit_log_repository import AuditLogRepository


# A Blueprint groups related routes together
auth_bp = Blueprint("auth", __name__)

user_repository = UserRepository()
audit_repository = AuditLogRepository()


# ============================================
# Helper: get the currently logged-in user
# ============================================
def get_current_user():
    """Return the logged-in User object, or None if not logged in."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return user_repository.find_by_id(user_id)


# ============================================
# Route: /login
# ============================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, go straight to the dashboard
    if get_current_user() is not None:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Find the user
        user = user_repository.find_by_username(username)

        # Check the password
        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        if not user.is_active:
            flash("Your account is disabled.", "error")
            return render_template("login.html")

        # Success - save the user in the session
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role_name"] = user.role.name

        # Log the action
        audit_repository.log_action(user, "user logged in")

        flash(f"Welcome, {user.username}!", "success")
        return redirect(url_for("auth.dashboard"))

    # GET request - just show the form
    return render_template("login.html")


# ============================================
# Route: /logout
# ============================================
@auth_bp.route("/logout")
def logout():
    user = get_current_user()
    if user is not None:
        audit_repository.log_action(user, "user logged out")

    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


# ============================================
# Route: /dashboard
# ============================================
@auth_bp.route("/dashboard")
def dashboard():
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html", user=user)