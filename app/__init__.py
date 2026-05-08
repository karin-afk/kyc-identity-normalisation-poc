"""
KYC Identity Normalisation - Flask application factory.
"""

import os
from pathlib import Path

from flask import Flask, redirect, url_for

from app.config import config
from app.extensions import db, migrate


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

    _register_blueprints(app)
    _register_cli(app)

    app.add_url_rule("/", "root", lambda: redirect(url_for("upload.index")))

    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp
    from app.routes.paste import paste_bp
    from app.routes.review import review_bp
    from app.routes.upload import upload_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(paste_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)


def _register_cli(app: Flask) -> None:
    from app.cli.seed_repository import seed_repository_cmd

    app.cli.add_command(seed_repository_cmd)
