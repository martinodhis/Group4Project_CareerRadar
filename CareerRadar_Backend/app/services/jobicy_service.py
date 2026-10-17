"""Synchronize remote job listings from Jobicy into the local database."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import requests

from ..extensions import db
from ..models.job import Job
from .notification_service import notify_matching_alerts


def _text(value):
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value if item is not None)
    return str(value) if value is not None else None


def _salary(value):
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


class JobicyService:
    endpoint = "https://jobicy.com/api/v2/remote-jobs"

    def sync(self, count=None, tag=None, geo=None, industry=None):
        params = {"count": min(max(int(count or 20), 1), 100)}
        if tag:
            params["tag"] = tag
        if geo:
            params["geo"] = geo
        if industry:
            params["industry"] = industry

        response = requests.get(self.endpoint, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        external_jobs = payload.get("jobs")
        if not isinstance(external_jobs, list):
            raise ValueError("Jobicy returned an invalid jobs response")

        created = 0
        updated = 0
        newly_created_jobs = []
        for external in external_jobs:
            if not isinstance(external, dict):
                continue
            external_id = external.get("id") or external.get("jobId")
            title = external.get("jobTitle") or external.get("title")
            if external_id is None or not title:
                continue

            job = Job.query.filter_by(source="jobicy", external_id=str(external_id)).first()
            is_new = job is None
            if is_new:
                job = Job(source="jobicy", external_id=str(external_id), title=title)
                newly_created_jobs.append(job)

            published_value = external.get("pubDate") or external.get("publishedAt")
            published_at = None
            if published_value:
                try:
                    published_at = datetime.fromisoformat(
                        published_value.replace("Z", "+00:00")
                    )
                except (AttributeError, TypeError, ValueError):
                    published_at = None

            job.title = title
            job.company_name = external.get("companyName") or external.get("company")
            job.company_logo = external.get("companyLogo")
            job.description = external.get("jobDescription") or external.get("jobExcerpt")
            job.url = external.get("url") or external.get("jobUrl")
            job.location = external.get("jobGeo") or external.get("location")
            job.remote_type = _text(external.get("remoteType") or external.get("jobRemoteType"))
            job.employment_type = _text(external.get("jobType") or external.get("employmentType"))
            job.experience_level = _text(external.get("jobLevel") or external.get("experienceLevel"))
            job.industry = _text(external.get("jobIndustry") or external.get("industry"))
            job.category = _text(external.get("jobCategory") or external.get("category"))
            job.salary_min = _salary(external.get("salaryMin") or external.get("salary_min"))
            job.salary_max = _salary(external.get("salaryMax") or external.get("salary_max"))
            job.salary_currency = external.get("salaryCurrency") or external.get("salary_currency")
            raw_tags = external.get("jobTag") or external.get("tags") or []
            if isinstance(raw_tags, str):
                job.tags = [raw_tags]
            elif isinstance(raw_tags, list):
                job.tags = [str(tag) for tag in raw_tags if tag is not None]
            else:
                job.tags = []
            job.published_at = published_at
            job.last_synced_at = datetime.now(timezone.utc)
            job.is_active = True
            db.session.add(job)
            if is_new:
                created += 1
            else:
                updated += 1

        db.session.commit()
        for job in newly_created_jobs:
            notify_matching_alerts(job)
        return {
            "fetched": len(external_jobs),
            "created": created,
            "updated": updated,
        }


jobicy_service = JobicyService()
