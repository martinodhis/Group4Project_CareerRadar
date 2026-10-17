"""Profile routes: profile, skills, education, experience."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.education import Education
from ..models.experience import Experience
from ..models.profile import Profile
from ..models.skill import Skill, UserSkill
from ..schemas import (
    EducationSchema,
    ExperienceSchema,
    ProfileSchema,
    UserSkillSchema,
)
from ..utils.decorators import get_current_user
from ..utils.errors import ConflictError, NotFoundError
from ..utils.responses import success

profile_bp = Blueprint("profile", __name__)


def _ensure_profile(user):
    if user.profile is None:
        user.profile = Profile(user_id=user.id)
        db.session.flush()
    return user.profile


def _compute_completion(user):
    """Rough profile-completion percentage used by the dashboard."""
    profile = user.profile
    checks = [
        bool(profile and profile.headline),
        bool(profile and profile.current_job_title),
        bool(profile and profile.location),
        bool(profile and profile.career_level),
        len(user.skills) >= 3,
        len(user.education) >= 1,
        len(user.experience) >= 1,
        len(user.career_goals) >= 1,
    ]
    return int(sum(checks) / len(checks) * 100)


@profile_bp.get("")
@jwt_required()
def get_profile():
    user = get_current_user()
    profile = _ensure_profile(user)

    completion = _compute_completion(user)
    if profile.profile_completion != completion:
        profile.profile_completion = completion
    db.session.commit()

    data = profile.to_dict()
    data["user"] = user.to_dict()
    data["skills"] = [us.to_dict() for us in user.skills]
    data["education"] = [e.to_dict() for e in user.education]
    data["experience"] = [x.to_dict() for x in user.experience]
    return success(data=data, message="Profile retrieved")


@profile_bp.put("")
@jwt_required()
def update_profile():
    user = get_current_user()
    payload = ProfileSchema().load(request.get_json(silent=True) or {})

    profile = _ensure_profile(user)

    for key, value in payload.items():
        setattr(profile, key, value)

    profile.profile_completion = _compute_completion(user)
    db.session.commit()
    return success(data=profile.to_dict(), message="Profile updated successfully")


# --- Skills --------------------------------------------------------------
@profile_bp.post("/skills")
@jwt_required()
def add_skill():
    user = get_current_user()
    profile = _ensure_profile(user)
    payload = UserSkillSchema().load(request.get_json(silent=True) or {})

    skill = None
    if payload.get("skill_id"):
        skill = Skill.query.get(payload["skill_id"])
    elif payload.get("name"):
        skill = Skill.query.filter(
            db.func.lower(Skill.name) == payload["name"].strip().lower()
        ).first()
        if skill is None:
            skill = Skill(name=payload["name"].strip(), category="Custom")
            db.session.add(skill)
            db.session.flush()

    if skill is None:
        raise NotFoundError("The requested skill could not be found.", code="SKILL_NOT_FOUND")

    if UserSkill.query.filter_by(user_id=user.id, skill_id=skill.id).first():
        raise ConflictError("This skill is already on your profile.", code="SKILL_EXISTS")

    user_skill = UserSkill(
        user_id=user.id,
        skill_id=skill.id,
        proficiency_level=payload.get("proficiency_level") or "INTERMEDIATE",
        years_experience=payload.get("years_experience") or 0,
        is_primary=bool(payload.get("is_primary")),
    )
    db.session.add(user_skill)
    profile.profile_completion = _compute_completion(user)
    db.session.commit()
    return success(data=user_skill.to_dict(), message="Skill added", status_code=201)


@profile_bp.delete("/skills/<int:skill_id>")
@jwt_required()
def remove_skill(skill_id):
    user = get_current_user()
    user_skill = UserSkill.query.filter_by(user_id=user.id, skill_id=skill_id).first()
    if user_skill is None:
        raise NotFoundError("This skill is not on your profile.", code="SKILL_NOT_FOUND")
    profile = _ensure_profile(user)
    db.session.delete(user_skill)
    profile.profile_completion = _compute_completion(user)
    db.session.commit()
    return success(message="Skill removed")


# --- Education -----------------------------------------------------------
@profile_bp.post("/education")
@jwt_required()
def add_education():
    user = get_current_user()
    profile = _ensure_profile(user)
    payload = EducationSchema().load(request.get_json(silent=True) or {})
    edu = Education(user_id=user.id, **payload)
    db.session.add(edu)
    profile.profile_completion = _compute_completion(user)
    db.session.commit()
    return success(data=edu.to_dict(), message="Education added", status_code=201)


@profile_bp.delete("/education/<int:education_id>")
@jwt_required()
def delete_education(education_id):
    user = get_current_user()
    edu = Education.query.filter_by(id=education_id, user_id=user.id).first()
    if edu is None:
        raise NotFoundError("Education record not found.", code="EDUCATION_NOT_FOUND")
    db.session.delete(edu)
    db.session.commit()
    return success(message="Education removed")


# --- Experience ----------------------------------------------------------
@profile_bp.post("/experience")
@jwt_required()
def add_experience():
    user = get_current_user()
    profile = _ensure_profile(user)
    payload = ExperienceSchema().load(request.get_json(silent=True) or {})
    exp = Experience(user_id=user.id, **payload)
    db.session.add(exp)
    profile.profile_completion = _compute_completion(user)
    db.session.commit()
    return success(data=exp.to_dict(), message="Experience added", status_code=201)


@profile_bp.delete("/experience/<int:experience_id>")
@jwt_required()
def delete_experience(experience_id):
    user = get_current_user()
    exp = Experience.query.filter_by(id=experience_id, user_id=user.id).first()
    if exp is None:
        raise NotFoundError("Experience record not found.", code="EXPERIENCE_NOT_FOUND")
    db.session.delete(exp)
    db.session.commit()
    return success(message="Experience removed")
