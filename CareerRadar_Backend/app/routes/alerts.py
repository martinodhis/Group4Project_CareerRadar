"""Job-alert routes: personalized saved searches."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.job_alert import JobAlert
from ..schemas import JobAlertSchema
from ..utils.decorators import get_current_user
from ..utils.errors import NotFoundError
from ..utils.responses import success

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.get("")
@jwt_required()
def list_alerts():
    user = get_current_user()
    alerts = JobAlert.query.filter_by(user_id=user.id).order_by(JobAlert.created_at.desc()).all()
    return success(data={"alerts": [a.to_dict() for a in alerts]}, message="Alerts retrieved")


@alerts_bp.post("")
@jwt_required()
def create_alert():
    user = get_current_user()
    payload = JobAlertSchema().load(request.get_json(silent=True) or {})
    alert = JobAlert(user_id=user.id, **payload)
    db.session.add(alert)
    db.session.commit()
    return success(data=alert.to_dict(), message="Alert created", status_code=201)


@alerts_bp.put("/<int:alert_id>")
@jwt_required()
def update_alert(alert_id):
    user = get_current_user()
    alert = JobAlert.query.filter_by(id=alert_id, user_id=user.id).first()
    if alert is None:
        raise NotFoundError("Alert not found.", code="ALERT_NOT_FOUND")
    payload = JobAlertSchema(partial=True).load(request.get_json(silent=True) or {})
    for key, value in payload.items():
        setattr(alert, key, value)
    db.session.commit()
    return success(data=alert.to_dict(), message="Alert updated")


@alerts_bp.delete("/<int:alert_id>")
@jwt_required()
def delete_alert(alert_id):
    user = get_current_user()
    alert = JobAlert.query.filter_by(id=alert_id, user_id=user.id).first()
    if alert is None:
        raise NotFoundError("Alert not found.", code="ALERT_NOT_FOUND")
    db.session.delete(alert)
    db.session.commit()
    return success(message="Alert deleted")
