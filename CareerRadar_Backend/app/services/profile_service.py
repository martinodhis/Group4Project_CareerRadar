"""Profile completion calculations shared by profile and career routes."""

from ..extensions import db
from ..models.career_goal import CareerGoal
from ..models.education import Education
from ..models.experience import Experience
from ..models.profile import Profile
from ..models.skill import UserSkill


def refresh_profile_completion(user):
    profile = user.profile
    if profile is None:
        profile = Profile(user_id=user.id)
        db.session.add(profile)

    checks = [
        bool(profile.headline),
        bool(profile.current_job_title),
        bool(profile.location),
        bool(profile.career_level),
        UserSkill.query.filter_by(user_id=user.id).count() >= 3,
        Education.query.filter_by(user_id=user.id).count() >= 1,
        Experience.query.filter_by(user_id=user.id).count() >= 1,
        CareerGoal.query.filter_by(user_id=user.id).count() >= 1,
    ]
    profile.profile_completion = int(sum(checks) / len(checks) * 100)
    return profile.profile_completion
