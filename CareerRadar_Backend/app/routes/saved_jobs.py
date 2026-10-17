"""Saved-jobs routes: bookmark interesting opportunities."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.job import Job
from ..models.saved_job import SavedJob
from ..services.activity_service import record_activity
from ..utils.decorators import get_current_user
from ..utils.errors import ConflictError, NotFoundError
from ..utils.responses import success

saved_jobs_bp = Blueprint("saved_jobs", __name__)


@saved_jobs_bp.get("")
@jwt_required()
def list_saved_jobs():
    user = get_current_user()
    saved = (
        SavedJob.query.filter_by(user_id=user.id)
        .order_by(SavedJob.created_at.desc())
        .all()
    )
    record_activity(user, "SAVED_JOBS_VIEW", request.path)
    return success(
        data={
            "saved_jobs": [
                {**item.to_dict(), "job": item.job.to_dict()}
                for item in saved
            ]
        },
        message="Saved jobs retrieved",
    )


@saved_jobs_bp.post("")
@jwt_required()
def save_job():
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    job_id = body.get("job_id")
    if not job_id:
        raise NotFoundError("A job_id is required.", code="VALIDATION_ERROR")

    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")

    if SavedJob.query.filter_by(user_id=user.id, job_id=job_id).first():
        raise ConflictError("This job is already saved.", code="ALREADY_SAVED")

    saved = SavedJob(user_id=user.id, job_id=job_id, notes=body.get("notes"))
    db.session.add(saved)
    db.session.commit()
    record_activity(user, "JOB_SAVED", request.path, {"job_id": job.id})
    return success(data=saved.to_dict(), message="Job saved", status_code=201)


@saved_jobs_bp.delete("/<int:job_id>")
@jwt_required()
def remove_saved_job(job_id):
    user = get_current_user()
    saved = SavedJob.query.filter_by(user_id=user.id, job_id=job_id).first()
    if saved is None:
        raise NotFoundError("This job is not saved.", code="NOT_SAVED")
    db.session.delete(saved)
    db.session.commit()
    record_activity(user, "JOB_UNSAVED", request.path, {"job_id": job_id})
    return success(message="Job removed from saved jobs")
