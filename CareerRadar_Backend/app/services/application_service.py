"""Application pipeline operations."""

from ..extensions import db
from ..models.application import Application
from ..models.job import Job
from ..utils.errors import ConflictError, NotFoundError, ValidationError

PIPELINE = ["SAVED", "APPLIED", "SCREENING", "INTERVIEW", "OFFER", "ACCEPTED", "REJECTED"]


def create_application(user, job_id, status="SAVED", notes=None, applied_at=None, interview_date=None):
    if db.session.get(Job, job_id) is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    if Application.query.filter_by(user_id=user.id, job_id=job_id).first():
        raise ConflictError(
            "This job is already in your application tracker.",
            code="APPLICATION_ALREADY_TRACKED",
        )
    status = (status or "SAVED").upper()
    if status not in PIPELINE:
        raise ValidationError("The application status is not supported.")

    application = Application(
        user_id=user.id,
        job_id=job_id,
        status=status,
        notes=notes,
        applied_at=applied_at,
        interview_date=interview_date,
    )
    db.session.add(application)
    db.session.commit()
    return application


def update_application(application, payload):
    if "status" in payload:
        status = payload["status"].upper()
        if status not in PIPELINE:
            raise ValidationError("The application status is not supported.")
        application.status = status
    for field in ("notes", "applied_at", "interview_date"):
        if field in payload:
            setattr(application, field, payload[field])
    db.session.commit()
    return application
