"""Application-tracking routes."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.application import Application
from ..schemas import ApplicationSchema
from ..schemas.application import ApplicationUpdateSchema
from ..services import application_service
from ..services.activity_service import record_activity
from ..utils.decorators import get_current_user
from ..utils.errors import NotFoundError
from ..utils.responses import success

applications_bp = Blueprint("applications", __name__)


@applications_bp.get("")
@jwt_required()
def list_applications():
    """Authenticated: list the current user's applications."""
    user = get_current_user()
    status = request.args.get("status")
    query = Application.query.filter_by(user_id=user.id)
    if status:
        query = query.filter(Application.status == status.upper())
    query = query.order_by(Application.updated_at.desc())
    record_activity(user, "APPLICATIONS_VIEW", request.path, {"status": status})
    return success(
        data={
            "applications": [a.to_dict() for a in query.all()],
            "pipeline": application_service.PIPELINE,
        },
        message="Applications retrieved",
    )


@applications_bp.post("")
@jwt_required()
def create_application():
    """Authenticated: start tracking a job."""
    user = get_current_user()
    payload = ApplicationSchema().load(request.get_json(silent=True) or {})
    application = application_service.create_application(
        user,
        job_id=payload["job_id"],
        status=payload.get("status"),
        notes=payload.get("notes"),
        applied_at=payload.get("applied_at"),
        interview_date=payload.get("interview_date"),
    )
    record_activity(
        user,
        "APPLICATION_CREATED",
        request.path,
        {"application_id": application.id, "job_id": application.job_id, "status": application.status},
    )
    return success(data=application.to_dict(), message="Application created", status_code=201)


@applications_bp.get("/<int:application_id>")
@jwt_required()
def get_application(application_id):
    """Authenticated: fetch one of the user's applications."""
    user = get_current_user()
    application = Application.query.filter_by(id=application_id, user_id=user.id).first()
    if application is None:
        raise NotFoundError("Application not found.", code="APPLICATION_NOT_FOUND")
    return success(data=application.to_dict(), message="Application retrieved")


@applications_bp.put("/<int:application_id>")
@applications_bp.patch("/<int:application_id>")
@jwt_required()
def update_application(application_id):
    """Authenticated: update status / notes / dates."""
    user = get_current_user()
    application = Application.query.filter_by(id=application_id, user_id=user.id).first()
    if application is None:
        raise NotFoundError("Application not found.", code="APPLICATION_NOT_FOUND")
    payload = ApplicationUpdateSchema().load(request.get_json(silent=True) or {})
    application_service.update_application(application, payload)
    record_activity(
        user,
        "APPLICATION_UPDATED",
        request.path,
        {"application_id": application.id, "status": application.status},
    )
    return success(data=application.to_dict(), message="Application updated")


@applications_bp.delete("/<int:application_id>")
@jwt_required()
def delete_application(application_id):
    """Authenticated: stop tracking an application."""
    user = get_current_user()
    application = Application.query.filter_by(id=application_id, user_id=user.id).first()
    if application is None:
        raise NotFoundError("Application not found.", code="APPLICATION_NOT_FOUND")
    db.session.delete(application)
    db.session.commit()
    record_activity(user, "APPLICATION_DELETED", request.path, {"application_id": application_id})
    return success(message="Application deleted")
