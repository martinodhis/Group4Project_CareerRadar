"""Authentication helpers shared by API routes."""

from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..services.activity_service import record_activity
from ..models.user import User
from .errors import ForbiddenError, UnauthorizedError

_EXPLICIT_ACTIVITY_ENDPOINTS = {
    "jobs.list_jobs",
    "jobs.search_jobs",
    "jobs.get_job",
    "applications.list_applications",
    "applications.create_application",
    "applications.update_application",
    "applications.delete_application",
    "saved_jobs.list_saved_jobs",
    "saved_jobs.save_job",
    "saved_jobs.remove_saved_job",
    "auth.logout",
}


def get_current_user():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise UnauthorizedError("Authentication required.")
    user = db.session.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("This account is unavailable.")
    if request.endpoint not in _EXPLICIT_ACTIVITY_ENDPOINTS:
        record_activity(
            user,
            "API_REQUEST",
            request.path,
            {"method": request.method},
        )
    return user


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user.role.upper() != "ADMIN":
            raise ForbiddenError("Administrator privileges are required.")
        return view(*args, **kwargs)

    return wrapped
