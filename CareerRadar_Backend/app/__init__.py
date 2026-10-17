import click
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from .extensions import db, migrate, bcrypt, jwt, limiter
from marshmallow import ValidationError as MarshmallowValidationError
from .utils.errors import ApiError
from werkzeug.exceptions import HTTPException

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)

    # Import models so Flask-Migrate can detect their tables.
    from . import models

    # Import blueprints
    from .routes.auth import auth_bp
    from .routes.jobs import jobs_bp
    from .routes.saved_jobs import saved_jobs_bp
    from .routes.alerts import alerts_bp
    from .routes.applications import applications_bp
    from .routes.career import career_bp
    from .routes.dashboard import dashboard_bp
    from .routes.matches import matches_bp
    from .routes.notifications import notifications_bp
    from .routes.profile import profile_bp
    from .routes.skills import skills_bp
    from .routes.users import users_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(saved_jobs_bp, url_prefix="/saved-jobs")
    app.register_blueprint(alerts_bp, url_prefix="/alerts")
    app.register_blueprint(applications_bp, url_prefix="/applications")
    app.register_blueprint(career_bp, url_prefix="/career")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(matches_bp, url_prefix="/matches")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(skills_bp, url_prefix="/skills")
    app.register_blueprint(users_bp, url_prefix="/users")

    @app.cli.command("promote-admin")
    @click.argument("email")
    def promote_admin(email):
        """Promote one existing account to administrator by email."""
        from .models.user import User

        user = User.query.filter(db.func.lower(User.email) == email.strip().lower()).first()
        if user is None:
            raise click.ClickException(
                f"No account found for {email!r}. Register and sign in first, then retry."
            )
        if user.role.upper() == "ADMIN":
            click.echo(f"{user.email} already has administrator access.")
            return
        if not click.confirm(f"Promote {user.email} to administrator?"):
            click.echo("No changes made.")
            return

        user.role = "ADMIN"
        db.session.commit()
        click.echo(f"Administrator access granted to {user.email}. Sign out and sign in again.")

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({
            "success": False,
            "error": {"code": error.code, "message": error.message},
        }), error.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(error):
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR", 
                "message": "Request validation failed.", 
                "details": error.messages
            },
        }), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "success": False,
            "error": {
                "code": f"HTTP_{error.code}",
                "message": error.description,
            },
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled API error", exc_info=error)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "The server encountered an unexpected error. Please try again.",
            },
        }), 500

    @app.get("/")
    def index():
        method_order = ("GET", "POST", "PUT", "PATCH", "DELETE")
        api_endpoints = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            for method in method_order:
                if method in rule.methods:
                    api_endpoints.append({"method": method, "path": rule.rule})

        api_endpoints.sort(key=lambda item: (item["path"], method_order.index(item["method"])))
        return jsonify({
            "message": "CareerRadar API is running",
            "endpoints": api_endpoints,
        })

    @app.get("/health")
    def health():
        return jsonify({"message": "CareerRadar API is running"})

    return app