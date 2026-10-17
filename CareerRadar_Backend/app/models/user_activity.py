"""Persisted, non-sensitive records of authenticated user actions."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from ..extensions import db


class UserActivity(db.Model):
    __tablename__ = "user_activity"
    __table_args__ = (
        Index("ix_user_activity_user_created", "user_id", "created_at"),
        Index("ix_user_activity_action_created", "action", "created_at"),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = db.Column(String(80), nullable=False)
    endpoint = db.Column(String(240), nullable=False)
    details = db.Column(JSON)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="activities")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "endpoint": self.endpoint,
            "details": self.details or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user": {
                "username": self.user.username,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
            }
            if self.user
            else None,
        }
