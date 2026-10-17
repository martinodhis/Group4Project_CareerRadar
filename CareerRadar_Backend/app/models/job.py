"""Database model for locally stored job listings."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint

from ..extensions import db


class Job(db.Model):
	"""A job listing imported from an external source or entered manually."""

	__tablename__ = "jobs"
	__table_args__ = (
		UniqueConstraint("source", "external_id", name="uq_jobs_source_external_id"),
		Index("ix_jobs_is_active_published_at", "is_active", "published_at"),
	)

	id = db.Column(Integer, primary_key=True)
	external_id = db.Column(String(160))
	source = db.Column(String(80), nullable=False, default="jobicy", server_default="jobicy")
	title = db.Column(String(240), nullable=False)
	company_name = db.Column(String(180))
	company_logo = db.Column(String(500))
	description = db.Column(Text)
	url = db.Column(String(1000))
	location = db.Column(String(240))
	country = db.Column(String(120))
	remote_type = db.Column(String(32))
	employment_type = db.Column(String(60))
	experience_level = db.Column(String(80))
	category = db.Column(String(120))
	industry = db.Column(String(120))
	salary_min = db.Column(Numeric(12, 2))
	salary_max = db.Column(Numeric(12, 2))
	salary_currency = db.Column(String(8))
	tags = db.Column(JSON, nullable=False, default=list)
	published_at = db.Column(DateTime(timezone=True))
	expires_at = db.Column(DateTime(timezone=True))
	is_active = db.Column(Boolean, nullable=False, default=True, server_default="true")
	last_synced_at = db.Column(DateTime(timezone=True))
	created_at = db.Column(
		DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
	)
	updated_at = db.Column(
		DateTime(timezone=True),
		nullable=False,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
	)

	def to_dict(self, include_description=True, skills=True):
		"""Return a JSON-compatible representation of this listing.

		``skills`` is accepted for compatibility with callers that can omit
		associated skill data; skill relationships are managed separately.
		"""
		data = {
			"id": self.id,
			"external_id": self.external_id,
			"source": self.source,
			"title": self.title,
			"company_name": self.company_name,
			"company_logo": self.company_logo,
			"location": self.location,
			"country": self.country,
			"remote_type": self.remote_type,
			"employment_type": self.employment_type,
			"experience_level": self.experience_level,
			"category": self.category,
			"industry": self.industry,
			"salary_min": float(self.salary_min) if self.salary_min is not None else None,
			"salary_max": float(self.salary_max) if self.salary_max is not None else None,
			"salary_currency": self.salary_currency,
			"tags": self.tags or [],
			"url": self.url,
			"published_at": self.published_at.isoformat() if self.published_at else None,
			"expires_at": self.expires_at.isoformat() if self.expires_at else None,
			"is_active": self.is_active,
			"last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}
		if include_description:
			data["description"] = self.description
		if skills:
			data["skills"] = []
		return data