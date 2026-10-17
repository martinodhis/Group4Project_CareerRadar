"""Database model for a user's work experience."""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db


class Experience(db.Model):
	"""A work experience record associated with one user."""

	__tablename__ = "experiences"

	id = db.Column(Integer, primary_key=True)
	user_id = db.Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	job_title = db.Column(String(160), nullable=False)
	company_name = db.Column(String(180), nullable=False)
	location = db.Column(String(160))
	employment_type = db.Column(String(40))
	start_date = db.Column(Date)
	end_date = db.Column(Date)
	is_current = db.Column(Boolean, nullable=False, default=False, server_default="false")
	description = db.Column(Text)
	created_at = db.Column(
		DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
	)
	user = relationship("User", backref=db.backref("experience", cascade="all, delete-orphan"))

	def to_dict(self):
		"""Return this experience record as JSON-compatible data."""
		return {
			"id": self.id,
			"user_id": self.user_id,
			"job_title": self.job_title,
			"company_name": self.company_name,
			"location": self.location,
			"employment_type": self.employment_type,
			"start_date": self.start_date.isoformat() if isinstance(self.start_date, date) else None,
			"end_date": self.end_date.isoformat() if isinstance(self.end_date, date) else None,
			"is_current": self.is_current,
			"description": self.description,
			"created_at": self.created_at.isoformat() if self.created_at else None,
		}