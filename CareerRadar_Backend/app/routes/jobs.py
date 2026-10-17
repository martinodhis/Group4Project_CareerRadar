"""Job routes: browse, search, filter, sync (admin), status and match."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import requests
from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ..extensions import db, limiter
from ..models.application import Application
from ..models.job import Job
from ..models.saved_job import SavedJob
from ..models.skill import JobSkill
from ..schemas import JobQuerySchema
from ..services.jobicy_service import jobicy_service
from ..services.activity_service import record_activity
from ..services.matching_service import score_job
from ..utils.decorators import admin_required, get_current_user
from ..utils.errors import ApiError, ConflictError, NotFoundError, ValidationError
from ..utils.responses import success

jobs_bp = Blueprint("jobs", __name__)


def _apply_filters(query, params):
    keyword = params.get("keyword") or params.get("q")
    if keyword:
        like = f"%{keyword.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Job.title).like(like),
                db.func.lower(Job.company_name).like(like),
                db.func.lower(Job.description).like(like),
                db.func.lower(Job.category).like(like),
            )
        )
    if params.get("location"):
        query = query.filter(db.func.lower(Job.location).like(f"%{params['location'].lower()}%"))
    if params.get("country"):
        query = query.filter(db.func.lower(Job.country).like(f"%{params['country'].lower()}%"))
    if params.get("industry"):
        query = query.filter(db.func.lower(Job.industry).like(f"%{params['industry'].lower()}%"))
    if params.get("category"):
        query = query.filter(db.func.lower(Job.category).like(f"%{params['category'].lower()}%"))
    if params.get("company"):
        query = query.filter(db.func.lower(Job.company_name).like(f"%{params['company'].lower()}%"))
    if params.get("remote_type") and params["remote_type"].lower() != "any":
        query = query.filter(Job.remote_type == params["remote_type"].upper())
    if params.get("employment_type"):
        query = query.filter(
            db.func.lower(Job.employment_type) == params["employment_type"].lower().replace("-", "_")
        )
    if params.get("experience_level"):
        query = query.filter(
            db.func.lower(Job.experience_level).like(f"%{params['experience_level'].lower()}%")
        )
    if params.get("minimum_salary") is not None:
        query = query.filter(Job.salary_max >= params["minimum_salary"])
    return query


def _sort(query, sort):
    if sort == "oldest":
        return query.order_by(Job.published_at.asc().nulls_last())
    if sort == "salary":
        return query.order_by(Job.salary_max.desc().nulls_last())
    if sort == "title":
        return query.order_by(Job.title.asc())
    return query.order_by(Job.published_at.desc().nulls_last(), Job.id.desc())


def _paginate(query, page, limit):
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return pagination


def _sync_public_jobs_if_needed(query, keyword=None):
    active_jobs = Job.query.filter_by(is_active=True).count()
    latest_sync = db.session.query(db.func.max(Job.last_synced_at)).filter_by(
        source="jobicy"
    ).scalar()
    if latest_sync is not None and latest_sync.tzinfo is None:
        latest_sync = latest_sync.replace(tzinfo=timezone.utc)

    stale = (
        latest_sync is None
        or latest_sync < datetime.now(timezone.utc) - timedelta(minutes=15)
    )
    missing_search_results = bool(keyword and not query.first())
    if not stale and not missing_search_results:
        return

    try:
        jobicy_service.sync(count=50, tag=keyword if missing_search_results else None)
    except (requests.RequestException, ValueError):
        current_app.logger.exception("Automatic Jobicy synchronization failed")
        if active_jobs == 0 or missing_search_results:
            raise ApiError(
                "JOB_SYNC_FAILED",
                "Job listings could not be loaded from Jobicy. Please try again later.",
                502,
            )


@jobs_bp.get("")
@jwt_required(optional=True)
def list_jobs():
    """Public: browse / filter jobs."""
    params = JobQuerySchema().load(request.args.to_dict())
    query = _apply_filters(Job.query.filter_by(is_active=True), params)
    query = _sort(query, params["sort"])
    _sync_public_jobs_if_needed(query, params.get("keyword") or params.get("q"))
    query = _sort(_apply_filters(Job.query.filter_by(is_active=True), params), params["sort"])
    pagination = _paginate(query, params["page"], params["limit"])
    user_id = get_jwt_identity()
    if user_id:
        from ..models.user import User

        user = db.session.get(User, int(user_id))
        if user and user.is_active:
            record_activity(
                user,
                "JOB_SEARCH",
                request.path,
                {
                    key: float(value) if isinstance(value, Decimal) else value
                    for key, value in params.items()
                    if value is not None
                },
            )

    return success(
        data={
            "jobs": [j.to_dict() for j in pagination.items],
            "pagination": {
                "page": pagination.page,
                "limit": params["limit"],
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        },
        message="Jobs retrieved",
    )


@jobs_bp.get("/search")
@jwt_required(optional=True)
def search_jobs():
    """Public: search jobs by keyword (?q=)."""
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)

    query = Job.query.filter_by(is_active=True)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Job.title).like(like),
                db.func.lower(Job.company_name).like(like),
                db.func.lower(Job.description).like(like),
            )
        )
    _sync_public_jobs_if_needed(query, q)
    query = Job.query.filter_by(is_active=True)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Job.title).like(like),
                db.func.lower(Job.company_name).like(like),
                db.func.lower(Job.description).like(like),
            )
        )
    query = query.order_by(Job.published_at.desc().nulls_last())
    pagination = _paginate(query, page, limit)
    user_id = get_jwt_identity()
    if user_id:
        from ..models.user import User

        user = db.session.get(User, int(user_id))
        if user and user.is_active:
            record_activity(user, "JOB_SEARCH", request.path, {"q": q, "page": page, "limit": limit})
    return success(
        data={
            "jobs": [j.to_dict() for j in pagination.items],
            "pagination": {"page": pagination.page, "limit": limit, "total": pagination.total},
        },
        message="Search results",
    )


@jobs_bp.post("/sync")
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def sync_jobs():
    """Admin: fetch fresh jobs from Jobicy and upsert them locally."""
    body = request.get_json(silent=True)
    if body is None:
        body = {}
    if not isinstance(body, dict):
        raise ValidationError("A JSON object is required.", code="VALIDATION_ERROR")
    count = body.get("count")
    if count is not None and (isinstance(count, bool) or not isinstance(count, int)):
        raise ValidationError("count must be an integer.", code="VALIDATION_ERROR")
    for field in ("tag", "geo", "industry"):
        if field in body and body[field] is not None and not isinstance(body[field], str):
            raise ValidationError(f"{field} must be text.", code="VALIDATION_ERROR")

    try:
        summary = jobicy_service.sync(
            count=count,
            tag=body.get("tag"),
            geo=body.get("geo"),
            industry=body.get("industry"),
        )
    except (requests.RequestException, ValueError):
        current_app.logger.exception("Job synchronization failed")
        raise ApiError(
            "JOB_SYNC_FAILED",
            "Job listings could not be synchronized. Please try again later.",
            502,
        )
    return success(data=summary, message="Job synchronization complete")


@jobs_bp.get("/<int:job_id>")
@jwt_required(optional=True)
def get_job(job_id):
    """Public: fetch a single job."""
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    user_id = get_jwt_identity()
    if user_id:
        from ..models.user import User

        user = db.session.get(User, int(user_id))
        if user and user.is_active:
            record_activity(user, "JOB_VIEW", request.path, {"job_id": job.id})
    return success(data=job.to_dict(), message="Job retrieved")


@jobs_bp.get("/<int:job_id>/status")
def job_status(job_id):
    """Public: quick availability check for a job."""
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    return success(
        data={
            "job_id": job.id,
            "is_active": job.is_active,
            "last_synced_at": job.to_dict(include_description=False, skills=False)["last_synced_at"],
            "expires_at": job.to_dict(skills=False)["expires_at"],
        },
        message="Job status retrieved",
    )


@jobs_bp.get("/<int:job_id>/match")
@jwt_required()
def job_match(job_id):
    """Authenticated: compute the match between the user and a single job."""
    user = get_current_user()
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    result = score_job(user, job)
    return success(data=result, message="Match calculated")


@jobs_bp.post("")
@jwt_required()
@admin_required
def create_job():
    """Admin: manually create a job (used for testing / curated listings)."""
    body = request.get_json(silent=True) or {}
    if not body.get("title"):
        raise ValidationError("A job title is required.", code="VALIDATION_ERROR")
    job = Job(
        title=body["title"],
        company_name=body.get("company_name"),
        description=body.get("description"),
        location=body.get("location"),
        remote_type=body.get("remote_type"),
        employment_type=body.get("employment_type"),
        source=body.get("source", "manual"),
        external_id=body.get("external_id"),
    )
    db.session.add(job)
    db.session.commit()
    return success(data=job.to_dict(), message="Job created", status_code=201)


@jobs_bp.route("/<int:job_id>", methods=["PUT", "PATCH"])
@jwt_required()
@admin_required
def update_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("A JSON object is required.", code="VALIDATION_ERROR")

    text_fields = (
        "title", "company_name", "company_logo", "description", "url", "location",
        "country", "remote_type", "employment_type", "experience_level", "category",
        "industry", "salary_currency", "source", "external_id",
    )
    if not any(field in data for field in (*text_fields, "salary_min", "salary_max", "tags", "is_active")):
        raise ValidationError("Provide at least one job field to update.", code="VALIDATION_ERROR")

    for field in text_fields:
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, str):
                raise ValidationError(f"{field} must be text or null.", code="VALIDATION_ERROR")
            if field == "title" and (value is None or not value.strip()):
                raise ValidationError("A job title is required.", code="VALIDATION_ERROR")
            setattr(job, field, value.strip() if isinstance(value, str) else value)

    for field in ("salary_min", "salary_max"):
        if field in data:
            value = data[field]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                raise ValidationError(f"{field} must be a number or null.", code="VALIDATION_ERROR")
            setattr(job, field, value)

    if "tags" in data:
        if not isinstance(data["tags"], list) or not all(isinstance(tag, str) for tag in data["tags"]):
            raise ValidationError("tags must be a list of strings.", code="VALIDATION_ERROR")
        job.tags = data["tags"]
    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            raise ValidationError("is_active must be a boolean.", code="VALIDATION_ERROR")
        job.is_active = data["is_active"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("The job conflicts with an existing listing.", code="JOB_EXISTS")
    return success(data=job.to_dict(), message="Job updated")


@jobs_bp.delete("/<int:job_id>")
@jwt_required()
@admin_required
def delete_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")

    Application.query.filter_by(job_id=job.id).delete(synchronize_session=False)
    SavedJob.query.filter_by(job_id=job.id).delete(synchronize_session=False)
    JobSkill.query.filter_by(job_id=job.id).delete(synchronize_session=False)
    db.session.delete(job)
    db.session.commit()
    return success(message="Job deleted")
