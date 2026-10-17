from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
        }


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    proficiency_level = db.Column(db.String(32), nullable=False, default="INTERMEDIATE")
    years_experience = db.Column(db.Float, nullable=False, default=0)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship(
        "User",
        backref=db.backref("skills", cascade="all, delete-orphan"),
    )
    skill = db.relationship("Skill")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "skill": self.skill.to_dict() if self.skill else None,
            "proficiency_level": self.proficiency_level,
            "years_experience": self.years_experience,
            "is_primary": self.is_primary,
        }


class JobSkill(db.Model):
    __tablename__ = "job_skills"

    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    skill = db.relationship("Skill")


user_skills = UserSkill.__table__
job_skills = JobSkill.__table__
