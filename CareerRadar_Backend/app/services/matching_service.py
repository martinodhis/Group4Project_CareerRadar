"""Skill-based matching helpers for job recommendations."""

from ..models.job import Job
from ..models.skill import JobSkill, Skill, UserSkill


def calculate_skill_match(user_skills, job_skills):
    if not user_skills or not job_skills:
        return 0
    matches = set(user_skills).intersection(set(job_skills))
    return int((len(matches) / len(job_skills)) * 100)


def score_job(user, job):
    user_skill_ids = {
        row.skill_id for row in UserSkill.query.filter_by(user_id=user.id).all()
    }
    job_skill_ids = {
        row.skill_id for row in JobSkill.query.filter_by(job_id=job.id).all()
    }
    matched_ids = user_skill_ids.intersection(job_skill_ids)
    missing_ids = job_skill_ids.difference(user_skill_ids)
    score = calculate_skill_match(user_skill_ids, job_skill_ids)

    skills = {
        skill.id: skill.name
        for skill in Skill.query.filter(Skill.id.in_(job_skill_ids)).all()
    } if job_skill_ids else {}
    return {
        "job_id": job.id,
        "match_score": score,
        "breakdown": {"skills": score},
        "missing_skills": [skills.get(skill_id) for skill_id in sorted(missing_ids)],
        "matched_skills": [skills.get(skill_id) for skill_id in sorted(matched_ids)],
        "recommendation": "Strong match" if score >= 70 else "Potential match",
    }


def recommend_jobs(user, limit=20):
    jobs = (
        Job.query.filter_by(is_active=True)
        .order_by(Job.published_at.desc().nulls_last(), Job.id.desc())
        .limit(limit)
        .all()
    )
    recommendations = [
        {**score_job(user, job), "job": job}
        for job in jobs
    ]
    return sorted(
        recommendations,
        key=lambda result: (result["match_score"], result["job_id"]),
        reverse=True,
    )


class MatchingService:
    def match_job(self, user, job):
        return score_job(user, job)


matching_service = MatchingService()
