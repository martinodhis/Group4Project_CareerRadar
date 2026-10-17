"""Authentication routes: register, login, me, logout, password reset."""
from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
)
from marshmallow import ValidationError as MarshmallowError
from sqlalchemy.exc import IntegrityError

from ..extensions import db, jwt, limiter
from ..models.user import User
from ..models.profile import Profile
from ..models.user_activity import UserActivity
from ..schemas import (
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
)
from ..utils.decorators import get_current_user
from ..utils.errors import ApiError, ConflictError, UnauthorizedError, ValidationError
from ..utils.responses import success

auth_bp = Blueprint("auth", __name__)

# In-memory revocation set. Use Redis in production.
REVOKED_TOKENS = set()
# In-memory reset tokens. Use a DB table / Redis in production.
RESET_TOKENS = {}


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in REVOKED_TOKENS


def _tokens_for(user):
    claims = {"role": user.role}
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=claims)
    return access, refresh


@auth_bp.post("/register")
@limiter.limit("10 per minute")
def register():
    """Create a new user account."""
    data = RegisterSchema().load(request.get_json(silent=True) or {})
    email = data["email"].lower()

    if User.query.filter_by(email=email).first():
        raise ConflictError("An account with this email already exists.", code="EMAIL_IN_USE")

    username = (data.get("username") or "").strip() or User.username_for_email(email)
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
        db.session.flush()
        db.session.add(Profile(user_id=user.id))
        db.session.add(
            UserActivity(
                user_id=user.id,
                action="USER_REGISTERED",
                endpoint=request.path,
                details={},
            )
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError(
            "An account with these details already exists.",
            code="USER_EXISTS",
        )

    return success(
        data={"user": user.to_dict()},
        message="Account created successfully",
        status_code=201,
    )


@auth_bp.post("/login")
@limiter.limit("20 per minute")
def login():
    """Authenticate and return JWT tokens."""
    data = LoginSchema().load(request.get_json(silent=True) or {})
    user = User.query.filter_by(email=data["email"].lower()).first()

    if user is None or not user.check_password(data["password"]):
        raise UnauthorizedError("Invalid email or password.")
    if not user.is_active:
        raise ApiError("ACCOUNT_DISABLED", "This account has been deactivated.", 403)

    access, refresh = _tokens_for(user)
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    from ..services.activity_service import record_activity

    record_activity(user, "LOGIN", request.path)

    return success(
        data={
            "access_token": access,
            "refresh_token": refresh,
            "user": user.to_dict(),
        },
        message="Login successful",
        # Top-level access_token kept for spec compatibility.
        access_token=access,
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token from a valid refresh token."""
    identity = get_current_user()
    access, _ = _tokens_for(identity)
    return success(data={"access_token": access}, message="Token refreshed")


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the currently authenticated user."""
    user = get_current_user()
    payload = user.to_dict()
    payload["profile"] = user.profile.to_dict() if user.profile else None
    return success(data=payload, message="Current user retrieved")


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """Revoke the current access token."""
    from ..services.activity_service import record_activity

    record_activity(get_current_user(), "LOGOUT", request.path)
    jti = get_jwt()["jti"]
    REVOKED_TOKENS.add(jti)
    return success(message="Logged out successfully")


@auth_bp.post("/forgot-password")
@limiter.limit("10 per minute")
def forgot_password():
    """Generate a password reset token (would be emailed in production)."""
    data = ForgotPasswordSchema().load(request.get_json(silent=True) or {})
    user = User.query.filter_by(email=data["email"].lower()).first()

    # Always respond with success to avoid leaking which emails exist.
    token = None
    if user is not None:
        import secrets

        token = secrets.token_urlsafe(32)
        RESET_TOKENS[token] = user.id

    return success(
        data={"reset_token": token},
        message="If that email exists, a reset link has been sent.",
    )


@auth_bp.post("/reset-password")
@limiter.limit("10 per minute")
def reset_password():
    """Reset a password using a valid reset token."""
    data = ResetPasswordSchema().load(request.get_json(silent=True) or {})
    user_id = RESET_TOKENS.pop(data["token"], None)
    if user_id is None:
        raise ValidationError("This reset token is invalid or has expired.", code="INVALID_TOKEN")

    user = User.query.get(user_id)
    if user is None:
        raise ValidationError("This reset token is invalid or has expired.", code="INVALID_TOKEN")

    user.set_password(data["password"])
    db.session.commit()
    return success(message="Password has been reset successfully.")
