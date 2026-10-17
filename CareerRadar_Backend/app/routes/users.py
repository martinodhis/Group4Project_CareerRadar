"""User account routes."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.user import User
from ..schemas import AccountUpdateSchema, RegisterSchema, password_strength_error
from ..utils.decorators import admin_required, get_current_user
from ..utils.errors import ConflictError, NotFoundError, ValidationError
from ..utils.responses import success

users_bp = Blueprint("users", __name__)


@users_bp.get("")
@jwt_required()
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return success(data={"users": [user.to_dict() for user in users]}, message="Users retrieved")


@users_bp.get("/<int:user_id>")
@jwt_required()
@admin_required
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.", code="USER_NOT_FOUND")
    return success(data=user.to_dict(), message="User retrieved")


@users_bp.post("")
@jwt_required()
@admin_required
def create_user():
    data = RegisterSchema().load(request.get_json(silent=True) or {})
    email = data["email"].lower()
    username = (data.get("username") or "").strip() or User.username_for_email(email)
    if User.query.filter_by(email=email).first():
        raise ConflictError("An account with this email already exists.", code="EMAIL_IN_USE")
    if User.query.filter_by(username=username).first():
        raise ConflictError("That username is already taken.", code="USERNAME_IN_USE")

    user = User(
        username=username,
        email=email,
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
    )
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("An account with these details already exists.", code="USER_EXISTS")
    return success(data=user.to_dict(), message="User created", status_code=201)


@users_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@admin_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.", code="USER_NOT_FOUND")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("A JSON object is required.", code="VALIDATION_ERROR")
    fields = ("username", "email", "first_name", "last_name", "password", "role", "is_active")
    if not any(field in data for field in fields):
        raise ValidationError("Provide at least one user field to update.", code="VALIDATION_ERROR")

    for field in ("username", "email", "first_name", "last_name"):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"{field} must be a non-empty string.", code="VALIDATION_ERROR")
            value = value.strip()
            if field == "email":
                value = value.lower()
            existing = User.query.filter(getattr(User, field) == value, User.id != user.id).first()
            if existing:
                raise ConflictError(f"That {field} is already in use.", code="USER_EXISTS")
            setattr(user, field, value)

    if "password" in data:
        password = data["password"]
        password_error = password_strength_error(password) if isinstance(password, str) else "Password must be a string."
        if password_error:
            raise ValidationError(password_error, code="VALIDATION_ERROR")
        user.set_password(password)
    if "role" in data:
        if data["role"] not in ("USER", "ADMIN"):
            raise ValidationError("Role must be USER or ADMIN.", code="VALIDATION_ERROR")
        user.role = data["role"]
    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            raise ValidationError("is_active must be a boolean.", code="VALIDATION_ERROR")
        user.is_active = data["is_active"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("An account with these details already exists.", code="USER_EXISTS")
    return success(data=user.to_dict(), message="User updated")


@users_bp.delete("/<int:user_id>")
@jwt_required()
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.", code="USER_NOT_FOUND")
    db.session.delete(user)
    db.session.commit()
    return success(message="User deleted")


@users_bp.get("/me")
@jwt_required()
def get_me():
    """Return the logged-in user's details."""
    user = get_current_user()
    return success(data=user.to_dict(), message="User retrieved")


@users_bp.patch("/me")
@jwt_required()
def update_me():
    """Update the logged-in user's first name, last name, and/or email.

    Passwords are handled by the auth routes (password reset), not here.
    """
    user = get_current_user()
    payload = AccountUpdateSchema().load(request.get_json(silent=True) or {})
    if not payload:
        raise ValidationError(
            "Provide first_name, last_name, or email to update.",
            code="VALIDATION_ERROR",
        )

    try:
        for field, value in payload.items():
            value = value.strip()
            if not value:
                raise ValidationError(f"{field} must not be empty.", code="VALIDATION_ERROR")
            if field == "email":
                value = value.lower()
            setattr(user, field, value)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        raise ValidationError(str(exc), code="VALIDATION_ERROR")
    except IntegrityError:
        db.session.rollback()
        raise ConflictError(
            "An account with this email already exists.", code="EMAIL_IN_USE"
        )

    return success(data=user.to_dict(), message="Account updated")


@users_bp.delete("/me")
@jwt_required()
def delete_me():
    """Delete the logged-in user's account and everything linked to it."""
    user = get_current_user()
    db.session.delete(user)
    db.session.commit()
    return success(message="Account deleted")