"""Skill routes: the shared skill catalogue.

A user's own skills (with proficiency, years, etc.) are managed in
routes/profile.py under /profile/skills, so they are not repeated here.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.skill import JobSkill, Skill, UserSkill
from ..utils.decorators import admin_required
from ..utils.errors import ConflictError, NotFoundError, ValidationError
from ..utils.responses import success

skills_bp = Blueprint("skills", __name__)


def find_skill_by_name(name):
    """Case-insensitive lookup, so "Python" and "python" count as one skill."""
    return Skill.query.filter(db.func.lower(Skill.name) == name.lower()).first()


@skills_bp.get("")
def list_skills():
    """Public: list skills. Optional filters: ?search=py and ?category=Programming"""
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = Skill.query
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(db.func.lower(Skill.category) == category.lower())

    skills = query.order_by(Skill.name).all()
    return success(
        data={"skills": [skill.to_dict() for skill in skills]},
        message="Skills retrieved",
    )


@skills_bp.get("/<int:skill_id>")
def get_skill(skill_id):
    """Public: get one skill."""
    skill = db.session.get(Skill, skill_id)
    if skill is None:
        raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
    return success(data=skill.to_dict(), message="Skill retrieved")


@skills_bp.post("")
@jwt_required()
@admin_required
def create_skill():
    """Add a new skill to the shared catalogue."""
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Skill name is required.", code="VALIDATION_ERROR")
    name = name.strip()

    category = data.get("category")
    if category is not None and not isinstance(category, str):
        raise ValidationError("Category must be text.", code="VALIDATION_ERROR")

    if find_skill_by_name(name):
        raise ConflictError("That skill already exists.", code="SKILL_EXISTS")

    skill = Skill(name=name, category=(category or "Custom").strip() or "Custom")
    db.session.add(skill)
    db.session.commit()
    return success(data=skill.to_dict(), message="Skill created", status_code=201)


@skills_bp.route("/<int:skill_id>", methods=["PUT", "PATCH"])
@jwt_required()
@admin_required
def update_skill(skill_id):
    skill = db.session.get(Skill, skill_id)
    if skill is None:
        raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not any(key in data for key in ("name", "category")):
        raise ValidationError("Provide a skill name or category to update.", code="VALIDATION_ERROR")

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Skill name is required.", code="VALIDATION_ERROR")
        name = name.strip()
        duplicate = find_skill_by_name(name)
        if duplicate is not None and duplicate.id != skill.id:
            raise ConflictError("That skill already exists.", code="SKILL_EXISTS")
        skill.name = name

    if "category" in data:
        category = data["category"]
        if category is not None and not isinstance(category, str):
            raise ValidationError("Category must be text.", code="VALIDATION_ERROR")
        skill.category = (category or "Custom").strip() or "Custom"

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("That skill already exists.", code="SKILL_EXISTS")
    return success(data=skill.to_dict(), message="Skill updated")


@skills_bp.delete("/<int:skill_id>")
@jwt_required()
@admin_required
def delete_skill(skill_id):
    skill = db.session.get(Skill, skill_id)
    if skill is None:
        raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")

    UserSkill.query.filter_by(skill_id=skill.id).delete(synchronize_session=False)
    JobSkill.query.filter_by(skill_id=skill.id).delete(synchronize_session=False)
    db.session.delete(skill)
    db.session.commit()
    return success(message="Skill deleted")