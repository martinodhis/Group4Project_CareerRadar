from datetime import datetime, timezone

from app.extensions import db


class SavedJob(db.Model):
    """Connects a user to a job they saved (table: saved_jobs).

    One user can save many jobs, and one job can be saved by many users.
    """

    __tablename__ = "saved_jobs"
    __table_args__ = (
        # A user cannot save the same job twice.
        db.UniqueConstraint("user_id", "job_id", name="uq_saved_jobs_user_job"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_id = db.Column(
        db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # The user side is declared in user.py (back_populates).
    user = db.relationship("User", back_populates="saved_jobs")

    # The job side is created here with a backref, so job.py does not need to
    # change: job.saved_jobs becomes available automatically.
    job = db.relationship(
        "Job", backref=db.backref("saved_jobs", cascade="all, delete-orphan")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<SavedJob user={self.user_id} job={self.job_id}>"