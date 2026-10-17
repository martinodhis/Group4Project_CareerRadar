"""Database model for a user's job application pipeline."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db


class Application(db.Model):
	"""A user's tracked application to a job listing."""

	__tablename__ = "applications"
	__table_args__ = (
		Index("ix_applications_user_status", "user_id", "status"),
	)

	id = db.Column(Integer, primary_key=True)
	user_id = db.Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	job_id = db.Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
	status = db.Column(String(32), nullable=False, default="SAVED", server_default="SAVED")
	notes = db.Column(Text)
	applied_at = db.Column(DateTime(timezone=True))
	interview_date = db.Column(DateTime(timezone=True))
	created_at = db.Column(
		DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
	)
	updated_at = db.Column(
		DateTime(timezone=True),
		nullable=False,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
	)

	user = relationship("User", backref=db.backref("applications", cascade="all, delete-orphan"))
	job = relationship("Job")

	def to_dict(self):
		"""Serialize the application, including its associated job when loaded."""
		return {
			"id": self.id,
			"user_id": self.user_id,
			"job_id": self.job_id,
			"status": self.status,
			"notes": self.notes,
			"applied_at": self.applied_at.isoformat() if self.applied_at else None,
			"interview_date": self.interview_date.isoformat() if self.interview_date else None,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
			"job": self.job.to_dict(include_description=False) if self.job else None,
		}