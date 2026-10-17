from ..extensions import db
from ..models.job_alert import JobAlert
from ..models.notification import Notification


def notify_matching_alerts(job):
    """Create one notification for each active alert matched by a new job."""
    searchable = " ".join(
        value for value in (
            job.title,
            job.company_name,
            job.description,
            job.category,
            job.industry,
        )
        if value
    ).lower()

    alerts = JobAlert.query.filter_by(is_active=True).all()
    notifications = []
    for alert in alerts:
        if alert.keyword.lower() not in searchable:
            continue
        if alert.location and alert.location.lower() not in (job.location or "").lower():
            continue
        if alert.job_type and alert.job_type.lower() not in (job.employment_type or "").lower():
            continue
        notifications.append(
            Notification(
                user_id=alert.user_id,
                job_id=job.id,
                message=f"New job matching “{alert.keyword}”: {job.title} at {job.company_name or 'a company'}",
                kind="job_alert",
            )
        )

    if notifications:
        db.session.add_all(notifications)
        db.session.commit()
    return len(notifications)
