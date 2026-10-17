from datetime import datetime, timezone

from app.extensions import db


class JobAlert(db.Model):
    """A saved search that a user wants to be notified about (table: job_alerts).
    """

    __tablename__ = "job_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    keyword = db.Column(db.String, nullable=False)  # e.g. "python"
    job_type = db.Column(db.String)  # e.g. "Full-time" (optional)
    location = db.Column(db.String)  # optional
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # user.job_alerts gives all of a user's alerts.
    user = db.relationship(
        "User", backref=db.backref("job_alerts", cascade="all, delete-orphan")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "keyword": self.keyword,
            "job_type": self.job_type,
            "location": self.location,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<JobAlert {self.id} '{self.keyword}'>"