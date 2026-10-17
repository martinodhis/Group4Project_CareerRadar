"""Database model for a user's career goals."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db


class CareerGoal(db.Model):
	"""A role or career target the user is working toward."""

	__tablename__ = "career_goals"

	id = db.Column(Integer, primary_key=True)
	user_id = db.Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	target_title = db.Column(String(160), nullable=False)
	target_industry = db.Column(String(120))
	target_location = db.Column(String(160))
	target_salary = db.Column(Numeric(12, 2))
	target_timeline = db.Column(String(80))
	priority = db.Column(Integer, nullable=False, default=1, server_default="1")
	notes = db.Column(Text)
	created_at = db.Column(
		DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
	)
	updated_at = db.Column(
		DateTime(timezone=True),
		nullable=False,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
	)
	user = relationship("User", backref=db.backref("career_goals", cascade="all, delete-orphan"))

	def to_dict(self):
		"""Return this goal as JSON-compatible data."""
		return {
			"id": self.id,
			"user_id": self.user_id,
			"target_title": self.target_title,
			"target_industry": self.target_industry,
			"target_location": self.target_location,
			"target_salary": float(self.target_salary) if self.target_salary is not None else None,
			"target_timeline": self.target_timeline,
			"priority": self.priority,
			"notes": self.notes,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}