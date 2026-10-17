"""Career insights derived from the user's profile and stored job listings."""

from sqlalchemy import func

from ..extensions import db
from ..models.career_goal import CareerGoal
from ..models.job import Job
from ..models.skill import JobSkill, Skill, UserSkill


def skill_gaps(user, top=5):
    user_skill_ids = {
        row.skill_id for row in UserSkill.query.filter_by(user_id=user.id).all()
    }
    demand = (
        JobSkill.query.with_entities(
            JobSkill.skill_id,
            func.count(JobSkill.job_id).label("job_count"),
        )
        .group_by(JobSkill.skill_id)
        .order_by(func.count(JobSkill.job_id).desc())
        .all()
    )
    gaps = []
    for skill_id, job_count in demand:
        if skill_id in user_skill_ids:
            continue
        skill = db.session.get(Skill, skill_id)
        if skill is not None:
            gaps.append({"skill": skill.name, "skill_id": skill.id, "job_count": job_count})
        if len(gaps) >= top:
            break
    return gaps


class CareerRadarService:
    def skill_demand(self):
        rows = (
            JobSkill.query.with_entities(
                JobSkill.skill_id,
                func.count(JobSkill.job_id).label("job_count"),
            )
            .group_by(JobSkill.skill_id)
            .order_by(func.count(JobSkill.job_id).desc())
            .all()
        )
        return [
            {"skill": skill.name, "skill_id": skill.id, "job_count": count}
            for skill_id, count in rows
            if (skill := db.session.get(Skill, skill_id)) is not None
        ]

    def build_career_radar(self, user):
        skills = UserSkill.query.filter_by(user_id=user.id).all()
        goals = (
            CareerGoal.query.filter_by(user_id=user.id)
            .order_by(CareerGoal.priority.asc())
            .all()
        )
        active_jobs = Job.query.filter_by(is_active=True).count()
        return {
            "profile": user.profile.to_dict() if user.profile else None,
            "skills": [entry.to_dict() for entry in skills],
            "goals": [goal.to_dict() for goal in goals],
            "skill_gaps": skill_gaps(user),
            "active_job_count": active_jobs,
            "skill_demand": self.skill_demand(),
        }


career_radar_service = CareerRadarService()
