"""
Small helpers shared by all controllers.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, abort

from repositories.user_repository import UserRepository


user_repository = UserRepository()


def get_current_user():
    """Return the logged-in User, or None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return user_repository.find_by_id(user_id)


def login_required(view_function):
    """Decorator: only logged-in users can access this route."""
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if get_current_user() is None:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator: only users with one of these roles can access this route."""
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                flash("Please log in first.", "error")
                return redirect(url_for("auth.login"))
            if user.role.name not in allowed_roles:
                flash("You don't have permission to access this page.", "error")
                return redirect(url_for("auth.dashboard"))
            return view_function(*args, **kwargs)
        return wrapper
    return decorator