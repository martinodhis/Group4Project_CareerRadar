"""Notification routes."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.notification import Notification
from ..utils.decorators import get_current_user
from ..utils.errors import NotFoundError
from ..utils.responses import success

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.get("")
@jwt_required()
def list_notifications():
    user = get_current_user()
    only_unread = request.args.get("unread", "false").lower() == "true"
    query = Notification.query.filter_by(user_id=user.id)
    if only_unread:
        query = query.filter_by(is_read=False)
    items = query.order_by(Notification.created_at.desc()).limit(100).all()
    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    return success(
        data={"notifications": [n.to_dict() for n in items], "unread_count": unread_count},
        message="Notifications retrieved",
    )


@notifications_bp.patch("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    user = get_current_user()
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if notification is None:
        raise NotFoundError("Notification not found.", code="NOTIFICATION_NOT_FOUND")
    notification.is_read = True
    db.session.commit()
    return success(data=notification.to_dict(), message="Notification marked as read")


@notifications_bp.patch("/read-all")
@jwt_required()
def mark_all_read():
    user = get_current_user()
    Notification.query.filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return success(message="All notifications marked as read")
