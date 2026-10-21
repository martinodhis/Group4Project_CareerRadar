"""Request validation schemas used by the API routes."""

from marshmallow import RAISE, Schema, ValidationError, fields, validates_schema, validate


class StrictSchema(Schema):
    class Meta:
        unknown = RAISE


def password_strength_error(password):
    requirements = (
        (len(password) >= 8, "at least 8 characters"),
        (any(char.islower() for char in password), "a lowercase letter"),
        (any(char.isupper() for char in password), "an uppercase letter"),
        (any(char.isdigit() for char in password), "a number"),
        (any(not char.isalnum() and not char.isspace() for char in password), "a symbol"),
    )
    missing = [requirement for satisfied, requirement in requirements if not satisfied]
    if missing:
        return "Password must contain " + ", ".join(missing) + "."
    return None


def validate_password_strength(password):
    error = password_strength_error(password)
    if error:
        raise ValidationError(error)


class RegisterSchema(StrictSchema):
    email = fields.Email(required=True)
    username = fields.String(load_default=None, validate=validate.Length(min=1, max=80))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    password = fields.String(required=True, load_only=True, validate=validate_password_strength)


class AccountUpdateSchema(StrictSchema):
    email = fields.Email(validate=validate.Length(max=120))
    first_name = fields.String(validate=validate.Length(min=1, max=120))
    last_name = fields.String(validate=validate.Length(min=1, max=120))


class LoginSchema(StrictSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class GoogleLoginSchema(StrictSchema):
    credential = fields.String(required=True, validate=validate.Length(min=20))


class ForgotPasswordSchema(StrictSchema):
    email = fields.Email(required=True)


class ResetPasswordSchema(StrictSchema):
    token = fields.String(required=True)
    password = fields.String(required=True, load_only=True, validate=validate_password_strength)


class JobQuerySchema(Schema):
    class Meta:
        unknown = RAISE

    keyword = fields.String(load_default=None)
    q = fields.String(load_default=None)
    location = fields.String(load_default=None)
    country = fields.String(load_default=None)
    industry = fields.String(load_default=None)
    category = fields.String(load_default=None)
    company = fields.String(load_default=None)
    remote_type = fields.String(load_default=None)
    employment_type = fields.String(load_default=None)
    experience_level = fields.String(load_default=None)
    minimum_salary = fields.Decimal(as_string=False, load_default=None)
    sort = fields.String(load_default="newest", validate=validate.OneOf(
        ["newest", "oldest", "salary", "title"]
    ))
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    limit = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))


class ProfileSchema(StrictSchema):
    full_name = fields.String(allow_none=True)
    headline = fields.String(allow_none=True)
    current_job_title = fields.String(allow_none=True)
    career_level = fields.String(allow_none=True)
    bio = fields.String(allow_none=True)
    location = fields.String(allow_none=True)
    years_of_experience = fields.Float(validate=validate.Range(min=0))


class UserSkillSchema(StrictSchema):
    skill_id = fields.Integer(load_default=None, allow_none=True)
    name = fields.String(load_default=None, allow_none=True)
    proficiency_level = fields.String(load_default="INTERMEDIATE")
    years_experience = fields.Float(load_default=0, validate=validate.Range(min=0))
    is_primary = fields.Boolean(load_default=False)

    @validates_schema
    def validate_input(self, data, **kwargs):
        if not data.get("skill_id") and not data.get("name"):
            raise ValidationError({"skill_id": ["Provide either skill_id or name."]})


class EducationSchema(StrictSchema):
    institution = fields.String(required=True, validate=validate.Length(min=1))
    degree = fields.String(allow_none=True, load_default=None)
    field_of_study = fields.String(allow_none=True, load_default=None)
    start_date = fields.Date(allow_none=True, load_default=None)
    end_date = fields.Date(allow_none=True, load_default=None)
    is_current = fields.Boolean(load_default=False)
    description = fields.String(allow_none=True, load_default=None)


class ExperienceSchema(StrictSchema):
    job_title = fields.String(required=True, validate=validate.Length(min=1))
    company_name = fields.String(required=True, validate=validate.Length(min=1))
    location = fields.String(allow_none=True, load_default=None)
    employment_type = fields.String(allow_none=True, load_default=None)
    start_date = fields.Date(allow_none=True, load_default=None)
    end_date = fields.Date(allow_none=True, load_default=None)
    is_current = fields.Boolean(load_default=False)
    description = fields.String(allow_none=True, load_default=None)


class CareerGoalSchema(StrictSchema):
    target_title = fields.String(required=True, validate=validate.Length(min=1, max=160))
    target_industry = fields.String(allow_none=True)
    target_location = fields.String(allow_none=True)
    target_salary = fields.Decimal(as_string=False, allow_none=True)
    target_timeline = fields.String(allow_none=True)
    priority = fields.Integer(validate=validate.Range(min=1), load_default=1)
    notes = fields.String(allow_none=True)


class JobAlertSchema(StrictSchema):
    keyword = fields.String(required=True, validate=validate.Length(min=1))
    job_type = fields.String(allow_none=True, load_default=None)
    location = fields.String(allow_none=True, load_default=None)
    is_active = fields.Boolean(load_default=True)


class ApplicationSchema(StrictSchema):
    job_id = fields.Integer(required=True, validate=validate.Range(min=1))
    status = fields.String(load_default="SAVED")
    notes = fields.String(allow_none=True, load_default=None)
    applied_at = fields.DateTime(allow_none=True, load_default=None)
    interview_date = fields.DateTime(allow_none=True, load_default=None)


__all__ = [
    "AccountUpdateSchema",
    "ApplicationSchema",
    "CareerGoalSchema",
    "EducationSchema",
    "ExperienceSchema",
    "ForgotPasswordSchema",
    "GoogleLoginSchema",
    "JobAlertSchema",
    "JobQuerySchema",
    "LoginSchema",
    "ProfileSchema",
    "RegisterSchema",
    "ResetPasswordSchema",
    "UserSkillSchema",
]
