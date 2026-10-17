"""Career routes: career goals CRUD and the Career Radar endpoint."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.career_goal import CareerGoal
from ..schemas import CareerGoalSchema
from ..services.career_radar_service import career_radar_service
from ..utils.decorators import get_current_user
from ..utils.errors import NotFoundError
from ..utils.responses import success

career_bp = Blueprint("career", __name__)


# --- Career goals --------------------------------------------------------
@career_bp.get("/goals")
@jwt_required()
def list_goals():
    user = get_current_user()
    goals = CareerGoal.query.filter_by(user_id=user.id).order_by(CareerGoal.priority.asc()).all()
    return success(data={"goals": [g.to_dict() for g in goals]}, message="Career goals retrieved")


@career_bp.post("/goals")
@jwt_required()
def create_goal():
    user = get_current_user()
    payload = CareerGoalSchema().load(request.get_json(silent=True) or {})
    goal = CareerGoal(user_id=user.id, **payload)
    db.session.add(goal)
    db.session.commit()
    return success(data=goal.to_dict(), message="Career goal created", status_code=201)


@career_bp.put("/goals/<int:goal_id>")
@jwt_required()
def update_goal(goal_id):
    user = get_current_user()
    goal = CareerGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if goal is None:
        raise NotFoundError("Career goal not found.", code="GOAL_NOT_FOUND")
    payload = CareerGoalSchema(partial=True).load(request.get_json(silent=True) or {})
    for key, value in payload.items():
        setattr(goal, key, value)
    db.session.commit()
    return success(data=goal.to_dict(), message="Career goal updated")


@career_bp.delete("/goals/<int:goal_id>")
@jwt_required()
def delete_goal(goal_id):
    user = get_current_user()
    goal = CareerGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if goal is None:
        raise NotFoundError("Career goal not found.", code="GOAL_NOT_FOUND")
    db.session.delete(goal)
    db.session.commit()
    return success(message="Career goal deleted")


# --- Career Radar --------------------------------------------------------
@career_bp.get("/radar")
@jwt_required()
def career_radar():
    """Authenticated: the signature Career Radar analysis."""
    user = get_current_user()
    data = career_radar_service.build_career_radar(user)
    return success(data=data, message="Career radar generated")


@career_bp.get("/skill-demand")
def skill_demand():
    """Public: how in-demand each skill is across stored jobs."""
    data = career_radar_service.skill_demand()
    return success(data={"demand": data}, message="Skill demand calculated")
