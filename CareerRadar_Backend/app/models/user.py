from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(32), unique=True, nullable=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    phone_verified = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    last_login = db.Column(db.DateTime(timezone=True))
    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(
        db.String(20), nullable=False, default="USER", server_default="USER"
    )
    is_active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=db.true()
    )

    # Keep these aligned with the columns in your PostgreSQL users table.
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now
    )

    activities = db.relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    saved_jobs = db.relationship(
        "SavedJob",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def username_for_email(cls, email):
        base = email.split("@", 1)[0][:80] or "user"
        username = base
        suffix = 1

        while cls.query.filter_by(username=username).first() is not None:
            tail = f"-{suffix}"
            username = f"{base[:80 - len(tail)]}{tail}"
            suffix += 1

        return username

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }