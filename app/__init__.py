"""
KYC Identity Normalisation - Flask application factory.
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, redirect, request, url_for

from app.config import config
from app.extensions import db, migrate

# Load environment variables from .env file before anything else
load_dotenv()


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[config_name])

    if config_name != "testing" and not app.config.get("SECRET_KEY"):
        raise ValueError("SECRET_KEY environment variable is not set.")

    # Allow skeleton startup even when DATABASE_URL is not configured yet.
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["BACKUP_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    _register_services(app)

    _register_blueprints(app)
    _register_cli(app)
    _register_context_processors(app)
    _register_request_tracing(app)

    app.add_url_rule("/", "root", lambda: redirect(url_for("upload.index")))

    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp
    from app.routes.paste import paste_bp
    from app.routes.review import review_bp
    from app.routes.telemetry import telemetry_bp
    from app.routes.upload import upload_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(paste_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(telemetry_bp)


def _register_cli(app: Flask) -> None:
    from app.cli.seed_repository import seed_repository_cmd

    app.cli.add_command(seed_repository_cmd)


def _register_services(app: Flask) -> None:
    from app.pipeline.normalisation.vocabulary_lookup import VocabularyLookupService
    from app.pipeline.normalisation.geographic_lookup import GeographicLookupService

    tables_dir = Path(app.root_path).parent / "data" / "lookup_tables"
    app.vocab_service = VocabularyLookupService(tables_dir)  # type: ignore[attr-defined]

    geonames_path = app.config.get("GEONAMES_DATA_PATH") or None
    app.geo_service = GeographicLookupService(geonames_path=geonames_path)  # type: ignore[attr-defined]


def _register_context_processors(app: Flask) -> None:
    @app.context_processor
    def inject_user_flags() -> dict[str, bool]:
        """Inject native speaker visibility flag for template navigation."""
        try:
            from app.models.user import User

            user = User.query.filter_by(is_native_speaker=True).first()  # type: ignore[attr-defined]
            return {"current_user_is_native_speaker": user is not None}
        except Exception:
            return {"current_user_is_native_speaker": True}

    @app.context_processor
    def inject_session_trace_context() -> dict[str, str]:
        """Expose session trace id to templates for diagnostics."""
        try:
            from app.utils.session_trace import get_session_id

            return {"session_trace_id": get_session_id()}
        except Exception:
            return {"session_trace_id": ""}


def _register_request_tracing(app: Flask) -> None:
    @app.before_request
    def trace_request_start() -> None:
        if not app.config.get("SESSION_TRACE_ENABLED", True):
            return

        if request.path.startswith("/static/"):
            return

        from app.utils.session_trace import ensure_session_context, log_event

        g.request_started_at = time.perf_counter()
        _, is_new = ensure_session_context()
        if is_new:
            log_event("session_started", {"entry_path": request.path}, source="system")

        log_event(
            "request_started",
            {
                "query": request.args.to_dict(flat=True),
                "form": request.form.to_dict(flat=True),
                "files": sorted(list(request.files.keys())),
            },
            source="backend",
        )

    @app.after_request
    def trace_request_end(response):
        if not app.config.get("SESSION_TRACE_ENABLED", True):
            return response

        if request.path.startswith("/static/"):
            return response

        from app.utils.session_trace import log_event

        started = getattr(g, "request_started_at", None)
        duration_ms = round((time.perf_counter() - started) * 1000, 2) if started else None
        log_event(
            "request_completed",
            {
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
            source="backend",
        )
        return response
