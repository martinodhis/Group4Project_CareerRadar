"""Match routes: personalized recommendations."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..services.matching_service import matching_service, recommend_jobs
from ..utils.decorators import get_current_user
from ..utils.responses import success

matches_bp = Blueprint("matches", __name__)


@matches_bp.get("")
@jwt_required()
def get_matches():
    """
    Authenticated: recommended jobs for the current user.

    Query params: limit (default 20), min_score (default 0).
    """
    user = get_current_user()
    limit = min(request.args.get("limit", 20, type=int), 100)
    min_score = request.args.get("min_score", 0, type=float)

    results = recommend_jobs(user, limit=limit)
    results = [r for r in results if r["match_score"] >= min_score]

    payload = [
        {
            "job_id": r["job_id"],
            "match_score": r["match_score"],
            "breakdown": r["breakdown"],
            "missing_skills": r["missing_skills"],
            "recommendation": r["recommendation"],
            "job": r["job"].to_dict(include_description=False),
        }
        for r in results
    ]

    return success(data={"matches": payload, "count": len(payload)}, message="Matches retrieved")


@matches_bp.post("/recalculate")
@jwt_required()
def recalculate():
    """Authenticated: recompute and persist matches for the user's top jobs."""
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    limit = min(int(body.get("limit", 20)), 100)
    results = recommend_jobs(user, limit=limit)
    for r in results:
        matching_service.match_job(user, r["job"])
    db.session.commit()
    return success(data={"recalculated": len(results)}, message="Matches recalculated")
