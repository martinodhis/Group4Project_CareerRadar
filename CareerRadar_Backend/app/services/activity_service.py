"""Helpers for recording authenticated user actions."""

from ..extensions import db
from ..models.user_activity import UserActivity


def record_activity(user, action, endpoint, details=None):
    db.session.add(
        UserActivity(
            user_id=user.id,
            action=action,
            endpoint=endpoint,
            details=details or {},
        )
    )
    db.session.commit()
