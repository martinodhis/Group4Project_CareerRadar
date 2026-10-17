from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    """A message shown to a user (table: notifications).

    Created by the notification service, for example when a new job matches
    one of the user's alerts. A notification can optionally point to a job.
    """

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_id = db.Column(
        db.Integer, db.ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    message = db.Column(db.String, nullable=False)
    kind = db.Column(db.String, nullable=False, default="general")  # e.g. "job_alert"
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # user.notifications gives all of a user's notifications.
    user = db.relationship(
        "User", backref=db.backref("notifications", cascade="all, delete-orphan")
    )
    job = db.relationship("Job")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "message": self.message,
            "kind": self.kind,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Notification {self.id} user={self.user_id}>"