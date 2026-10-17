from datetime import datetime, timezone

from app.extensions import db


class Profile(db.Model):
    """Extra personal details for a user (table: profiles).

    One user has one profile. Kept separate from users so the login details
    (username, email, password) stay small.
    """

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name = db.Column(db.String)
    headline = db.Column(db.String)  # e.g. "Junior Backend Developer"
    current_job_title = db.Column(db.String)
    career_level = db.Column(db.String)
    bio = db.Column(db.Text)
    location = db.Column(db.String)
    years_of_experience = db.Column(db.Float, nullable=False, default=0)
    profile_completion = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # user.profile gives the single profile (uselist=False). Deleting the user
    # deletes the profile.
    user = db.relationship(
        "User",
        back_populates="profile",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "headline": self.headline,
            "current_job_title": self.current_job_title,
            "career_level": self.career_level,
            "bio": self.bio,
            "location": self.location,
            "years_of_experience": self.years_of_experience,
            "profile_completion": self.profile_completion,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Profile user={self.user_id}>"