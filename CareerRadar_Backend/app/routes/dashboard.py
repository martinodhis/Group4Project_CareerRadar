"""Dashboard route: aggregated workspace data for the current user."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.application import Application
from ..models.job import Job
from ..models.saved_job import SavedJob
from ..models.skill import Skill, UserSkill
from ..models.user import User
from ..models.user_activity import UserActivity
from ..services.application_service import PIPELINE
from ..services.career_radar_service import skill_gaps
from ..services.matching_service import recommend_jobs
from ..utils.decorators import admin_required, get_current_user
from ..utils.errors import ValidationError
from ..utils.responses import success

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("")
@jwt_required()
def dashboard():
    user = get_current_user()

    saved_count = SavedJob.query.filter_by(user_id=user.id).count()
    applications = Application.query.filter_by(user_id=user.id).all()
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    recommendations = recommend_jobs(user, limit=5)
    gaps = skill_gaps(user, top=5)

    return success(
        data={
            "profile_completion": user.profile.profile_completion if user.profile else 0,
            "saved_jobs": saved_count,
            "applications": len(applications),
            "interviews": status_counts.get("INTERVIEW", 0),
            "offers": status_counts.get("OFFER", 0) + status_counts.get("ACCEPTED", 0),
            "recommended_jobs": len(recommendations),
            "applications_by_status": status_counts,
            "top_missing_skills": [g["skill"] for g in gaps],
            "top_goal": (
                sorted(user.career_goals, key=lambda g: g.priority or 1)[0].target_title
                if user.career_goals
                else None
            ),
            "recommended": [
                {
                    "job_id": r["job_id"],
                    "title": r["job"].title,
                    "company": r["job"].company_name,
                    "match_score": r["match_score"],
                }
                for r in recommendations
            ],
        },
        message="Dashboard data retrieved",
    )


@dashboard_bp.get("/admin")
@jwt_required()
@admin_required
def admin_dashboard():
    """Return aggregate administrator dashboard statistics."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()

    popular_skills = (
        UserSkill.query.with_entities(
            UserSkill.skill_id, db.func.count(UserSkill.skill_id).label("c")
        )
        .group_by(UserSkill.skill_id)
        .order_by(db.text("c DESC"))
        .limit(10)
        .all()
    )
    skill_names = [
        {"skill": skill.name, "count": count}
        for sid, count in popular_skills
        if (skill := db.session.get(Skill, sid)) is not None
    ]

    return success(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "applications": Application.query.count(),
            "pending_applications": Application.query.filter_by(status="APPLIED").count(),
            "activity_events": UserActivity.query.count(),
            "popular_skills": skill_names,
        },
        message="Admin dashboard data retrieved",
    )


@dashboard_bp.get("/admin/activity")
@jwt_required()
@admin_required
def admin_activity():
    """Return paginated activity and application history for administrators."""
    activity_page = request.args.get("activity_page", 1, type=int)
    application_page = request.args.get("application_page", 1, type=int)
    limit = min(max(request.args.get("limit", 25, type=int), 1), 100)
    application_status = (request.args.get("application_status") or "ALL").strip().upper()
    if activity_page < 1 or application_page < 1:
        raise ValidationError("Page numbers must be positive.", code="VALIDATION_ERROR")
    if application_status not in {"ALL", "PENDING", *PIPELINE}:
        raise ValidationError("The application status filter is not supported.", code="VALIDATION_ERROR")

    activities = (
        UserActivity.query.order_by(UserActivity.created_at.desc(), UserActivity.id.desc())
        .paginate(page=activity_page, per_page=limit, error_out=False)
    )
    application_query = Application.query
    if application_status == "PENDING":
        application_query = application_query.filter_by(status="APPLIED")
    elif application_status != "ALL":
        application_query = application_query.filter_by(status=application_status)
    applications = (
        application_query.order_by(Application.updated_at.desc(), Application.id.desc())
        .paginate(page=application_page, per_page=limit, error_out=False)
    )
    return success(
        data={
            "activities": [activity.to_dict() for activity in activities.items],
            "applications": [
                {
                    **application.to_dict(),
                    "user": {
                        "username": application.user.username,
                        "email": application.user.email,
                        "first_name": application.user.first_name,
                        "last_name": application.user.last_name,
                    },
                }
                for application in applications.items
            ],
            "activity_pagination": {
                "page": activities.page,
                "pages": activities.pages,
                "total": activities.total,
                "has_next": activities.has_next,
                "has_prev": activities.has_prev,
            },
            "application_pagination": {
                "page": applications.page,
                "pages": applications.pages,
                "total": applications.total,
                "has_next": applications.has_next,
                "has_prev": applications.has_prev,
            },
            "application_status": application_status,
        },
        message="User activity and applications retrieved",
    )
