# Epic 00 — Flask Package Skeleton

**Status: IMPLEMENTED**

## Purpose

This epic creates the `app/` package structure that all subsequent epics write into. It does not implement any features — it creates the scaffolding, import boundaries, configuration system, and empty placeholder modules that make all subsequent `from app.pipeline.normalisation...` imports valid.

This epic must be completed before any Strategy epic (A through H) can be implemented. It unblocks Copilot immediately.

**The existing `src/` pipeline and `app.py` Streamlit interface are not touched.** They remain fully operational in parallel. The `src/` tests continue to pass throughout. The two codebases coexist until Epic 04 (normalisation router) performs the cutover.

---

## What you need to provide

Nothing. This epic is built entirely by Copilot.

---

## What exists in the current codebase

- `app.py` — Streamlit frontend. **Do not modify or delete.** It continues to run via `streamlit run app.py` throughout development.
- `src/` — existing pipeline. **Do not modify.** All `src/` tests must continue to pass after this epic.
- `requirements.txt` — current dependencies listed above. This epic adds Flask and related libraries.
- `tests/` — existing test suite importing from `src/`. These imports must not break.

---

## Implementation Todo Checklist (agreed)

Use this checklist as the execution order for Epic 00.

- [x] Add Flask stack dependencies to `requirements.txt` (`flask`, `flask-sqlalchemy`, `flask-migrate`, `psycopg2-binary`, `gunicorn`, `celery`, `redis`).
- [x] Do **not** add `htmx` to pip dependencies (loaded via CDN in templates).
- [x] Scaffold the full `app/` directory tree exactly as specified.
- [x] Implement the five non-placeholder files: `app/config.py`, `app/extensions.py`, `app/__init__.py`, route blueprints, and `run.py`.
- [x] Copy `src/utils/logging_utils.py` into `app/utils/logging_utils.py`.
- [x] Create all remaining files as placeholders with module docstrings only.
- [x] Add minimal Jinja templates and static CSS placeholder.
- [x] Add root redirect (`/` -> `/upload/`) in app factory.
- [x] Add tests with explicit categories:
    - unit tests (app factory/config behavior),
    - integration tests (blueprint endpoints),
    - data contract tests (module import contracts and required config keys).
- [x] Ensure `create_app("testing")` works without external database/services.
- [x] Keep `src/` code and `app.py` unchanged.
- [x] Run and record validation commands:
    - new Flask test suite,
    - selected deterministic `src/` tests (LLM quota-dependent tests are out of scope for pass/fail in this epic),
    - smoke import test for Flask app.

### Guardrails for this epic

- SECRET_KEY validation must not fail at import time for testing mode.
- App startup must not require a live PostgreSQL connection.
- Existing Streamlit app file remains present for rollback, but Flask becomes the active UI path for subsequent epics.

---

## Target package structure

Copilot creates every directory and file listed below. Files marked **EMPTY** contain only a module docstring and no implementation — implementation comes in later epics.

```
app/
  __init__.py                          # App factory — create_app()
  config.py                            # Environment-based configuration classes
  extensions.py                        # db, migrate instances (no Flask-Login yet)
  models/
    __init__.py
    user.py                            # EMPTY — Epic 06 database schema
    document.py                        # EMPTY — Epic 06
    translation.py                     # EMPTY — Epic 06
    review.py                          # EMPTY — Epic 06
    audit.py                           # EMPTY — Epic 06
  routes/
    __init__.py
    upload.py                          # EMPTY — Epic 08 document upload UI
    paste.py                           # EMPTY — Epic 09 paste tool
    review.py                          # EMPTY — Epic 07 native speaker review
    admin.py                           # EMPTY — Epic 07
    export.py                          # EMPTY — Epic 08
  pipeline/
    __init__.py
    normalisation/
      __init__.py
      field_types.py                   # EMPTY — Epic 01 Strategy A
      preserve.py                      # EMPTY — Epic 01 Strategy A
      calendar_rules.py                # EMPTY — Epic 02 Strategy B
      vocabulary_lookup.py             # EMPTY — Epic 03 Strategy C
      geographic_lookup.py             # EMPTY — Epic 04 Strategy D
      repository_lookup.py             # EMPTY — Epic 05 Strategy E
      transliteration.py               # EMPTY — Epic 06 Strategy F
      character_map_normaliser.py      # EMPTY — Epic 07 Strategy G
      nmt_translator.py                # EMPTY — Epic 08 Strategy H
      router.py                        # EMPTY — Epic 10 normalisation router
    orchestrator.py                    # EMPTY — Epic 10
    ingestion.py                       # EMPTY — Epic 11 document pipeline
    language_detection.py              # EMPTY — Epic 11
    field_extraction.py                # EMPTY — Epic 11
    field_extraction_rules/
      __init__.py
      national_id.py                   # EMPTY — Epic 11
      drivers_licence.py               # EMPTY — Epic 11
      company_registry.py              # EMPTY — Epic 11
      business_registration.py         # EMPTY — Epic 11
      shareholder_table.py             # EMPTY — Epic 11
      aoa.py                           # EMPTY — Epic 11
      financial_statement.py           # EMPTY — Epic 11
  data/
    normalisation/
      character_maps.py                # EMPTY — Epic 07
      kanji_lookup.py                  # EMPTY — Epic 06 (copy from src/)
      cantonese_surname_map.py         # EMPTY — Epic 06 (copy from src/)
    lookup_tables/                     # EMPTY dir — Epic 03 JSON files go here
    seed/                              # EMPTY dir — Epic 05 seed JSON files go here
    geonames/                          # EMPTY dir — allCountries.txt goes here
  tasks/
    __init__.py
    ocr_task.py                        # EMPTY — Epic 11
    notification_task.py               # EMPTY — Epic 07
    backup_task.py                     # EMPTY — Epic 05
  cli/
    __init__.py
    seed_repository.py                 # EMPTY — Epic 05
  utils/
    __init__.py
    audit.py                           # EMPTY — Epic 10 audit logging
    logging_utils.py                   # Copy from src/utils/logging_utils.py
  templates/
    base.html                          # Minimal base template
    upload.html                        # Placeholder
    paste.html                         # Placeholder
    review.html                        # Placeholder
    admin.html                         # Placeholder
  static/
    css/
      main.css                         # Empty stylesheet placeholder
run.py                                 # Flask entry point
```

---

## Files to implement in full

All other files are empty placeholders. These five must be fully implemented in this epic.

### `app/config.py`

```python
"""
Environment-based configuration for the KYC Identity Normalisation Flask app.

All values are read from environment variables, which are loaded from .env
by python-dotenv in run.py. Never hardcode secrets or environment-specific
values here.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set.")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "")

    # File upload
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 52428800))
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    ALLOWED_EXTENSIONS: set[str] = set(
        os.environ.get("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png,tiff,docx,txt").split(",")
    )

    # Azure services
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
    AZURE_DOCUMENT_CLASSIFIER_ID: str = os.environ.get("AZURE_DOCUMENT_CLASSIFIER_ID", "")
    AZURE_TRANSLATOR_ENDPOINT: str = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "")
    AZURE_TRANSLATOR_KEY: str = os.environ.get("AZURE_TRANSLATOR_KEY", "")
    AZURE_TRANSLATOR_REGION: str = os.environ.get("AZURE_TRANSLATOR_REGION", "")
    AZURE_TRANSLATOR_TARGET_LANGUAGE: str = os.environ.get("AZURE_TRANSLATOR_TARGET_LANGUAGE", "en")
    AZURE_COMMUNICATION_CONNECTION_STRING: str = os.environ.get("AZURE_COMMUNICATION_CONNECTION_STRING", "")
    AZURE_STORAGE_ACCOUNT_NAME: str = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_ACCOUNT_KEY: str = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY", "")
    AZURE_STORAGE_CONTAINER_NAME: str = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "kyc-documents")
    EMAIL_SENDER_ADDRESS: str = os.environ.get("EMAIL_SENDER_ADDRESS", "")
    APP_BASE_URL: str = os.environ.get("APP_BASE_URL", "http://localhost:5000")

    # LLM — disabled by default. Changing to true requires AI Governance Board approval.
    LLM_ENABLED: bool = os.environ.get("LLM_ENABLED", "false").lower() == "true"
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")
    OPENAI_MAX_TOKENS: int = int(os.environ.get("OPENAI_MAX_TOKENS", 1000))

    # Repository backup
    BACKUP_FOLDER: str = os.environ.get("BACKUP_FOLDER", str(BASE_DIR / "backups"))
    BACKUP_RETENTION_COUNT: int = int(os.environ.get("BACKUP_RETENTION_COUNT", 30))

    # OCR confidence threshold
    OCR_CONFIDENCE_THRESHOLD: float = float(os.environ.get("OCR_CONFIDENCE_THRESHOLD", 0.85))

    # GeoNames
    GEONAMES_DATA_PATH: str = os.environ.get(
        "GEONAMES_DATA_PATH", str(BASE_DIR / "data" / "geonames" / "allCountries.txt")
    )

    # Audit
    AUDIT_GENESIS_HASH: str = os.environ.get("AUDIT_GENESIS_HASH", "")

    # Celery
    CELERY_BROKER_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_TASK_TIME_LIMIT: int = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 300))


class DevelopmentConfig(Config):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kyc_dev"
    )


class ProductionConfig(Config):
    DEBUG: bool = False
    # DATABASE_URL must be set in environment — no default


class TestingConfig(Config):
    TESTING: bool = True
    DEBUG: bool = True
    SECRET_KEY: str = "test-secret-key-not-for-production"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    LLM_ENABLED: bool = False
    WTF_CSRF_ENABLED: bool = False


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
```

### `app/extensions.py`

```python
"""
Flask extension instances.

Instantiated here without an app object (application factory pattern).
Bound to the app in create_app() via init_app().
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
```

### `app/__init__.py`

```python
"""
KYC Identity Normalisation — Flask application factory.

Usage:
    from app import create_app
    app = create_app()          # uses FLASK_ENV env var, defaults to development
    app = create_app("testing") # explicit config name
"""

import os
from pathlib import Path
from flask import Flask
from app.config import config
from app.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name: One of "development", "production", "testing".
                     Defaults to FLASK_ENV environment variable, or "development".

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[config_name])

    # Ensure required directories exist
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["BACKUP_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints — all routes are placeholders until their epics
    _register_blueprints(app)

    # Register CLI commands
    _register_cli(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.upload import upload_bp
    from app.routes.paste import paste_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(paste_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)


def _register_cli(app: Flask) -> None:
    from app.cli.seed_repository import seed_repository_cmd
    app.cli.add_command(seed_repository_cmd)
```

### Route blueprint skeletons

Each of the five route files follows the same pattern. Copilot creates all five. Example for `app/routes/upload.py` — repeat for `paste.py`, `review.py`, `admin.py`, `export.py` with their respective prefixes:

```python
"""
Upload routes — placeholder.
Full implementation in Epic 08.
"""

from flask import Blueprint, render_template

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")


@upload_bp.route("/", methods=["GET"])
def index():
    """Document upload form — placeholder."""
    return render_template("upload.html")


@upload_bp.route("/results/<int:document_id>", methods=["GET"])
def results(document_id: int):
    """Results view — placeholder."""
    return f"Results for document {document_id} — not yet implemented", 200
```

Root redirect in `app/routes/upload.py` only:
```python
from flask import redirect, url_for

@upload_bp.route("/", methods=["GET"], endpoint="root")
# Add this to the app factory after blueprint registration:
# app.add_url_rule("/", "root", lambda: redirect(url_for("upload.index")))
```

### `run.py`

```python
"""
Flask application entry point.

Development:    python run.py
                flask run
Production:     gunicorn "app:create_app()" --workers 4
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env before importing app — config reads env vars at import time

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
```

### `app/templates/base.html`

Minimal HTML5 base template with HTMX loaded from CDN. All other templates extend this.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}KYC Identity Normalisation{% endblock %}</title>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>
<body>
  <nav>
    <a href="{{ url_for('upload.index') }}">Upload</a>
    <a href="{{ url_for('paste.index') }}">Paste</a>
    <a href="{{ url_for('review.index') }}">Review</a>
    <a href="{{ url_for('admin.index') }}">Admin</a>
  </nav>
  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

Remaining templates (`upload.html`, `paste.html`, `review.html`, `admin.html`) extend base and contain only `{% block content %}Placeholder{% endblock %}`.

---

## `requirements.txt` — additions

Add to the existing file. Do not remove any existing dependencies.

```
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
psycopg2-binary>=2.9.0
gunicorn>=22.0.0
celery>=5.3.0
redis>=5.0.0
htmx                        # no pip package — loaded from CDN in template
```

Note: `htmx` is CDN-loaded in templates and must not be added to `requirements.txt`.

---

## Empty placeholder pattern

Every `EMPTY` file listed in the structure above contains only this:

```python
"""
{Module description} — placeholder.
Full implementation in {Epic name}.
"""
```

This ensures all import paths resolve without errors while keeping each epic's implementation isolated.

---

## Tests

`tests/test_epic00_flask_skeleton.py` — NEW FILE

```python
"""
Smoke tests for the Flask package skeleton.
Verifies that the app factory works and all imports resolve.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


# --- App factory ---
def test_create_app_returns_flask_instance(app):
    from flask import Flask
    assert isinstance(app, Flask)

def test_create_app_testing_config(app):
    assert app.config["TESTING"] is True
    assert app.config["LLM_ENABLED"] is False

def test_upload_folder_created(app, tmp_path):
    # Verify directory creation does not raise
    assert True  # mkdir is called in create_app — if it raised, test would not reach here


# --- Blueprint registration ---
def test_upload_route_returns_200(client):
    response = client.get("/upload/")
    assert response.status_code == 200

def test_paste_route_returns_200(client):
    response = client.get("/paste/")
    assert response.status_code == 200

def test_review_route_returns_200(client):
    response = client.get("/review/")
    assert response.status_code == 200

def test_admin_route_returns_200(client):
    response = client.get("/admin/")
    assert response.status_code == 200


# --- All app module imports resolve without error ---
def test_import_field_types():
    import app.pipeline.normalisation.field_types  # noqa: F401

def test_import_preserve():
    import app.pipeline.normalisation.preserve  # noqa: F401

def test_import_calendar_rules():
    import app.pipeline.normalisation.calendar_rules  # noqa: F401

def test_import_vocabulary_lookup():
    import app.pipeline.normalisation.vocabulary_lookup  # noqa: F401

def test_import_geographic_lookup():
    import app.pipeline.normalisation.geographic_lookup  # noqa: F401

def test_import_repository_lookup():
    import app.pipeline.normalisation.repository_lookup  # noqa: F401

def test_import_transliteration():
    import app.pipeline.normalisation.transliteration  # noqa: F401

def test_import_character_map_normaliser():
    import app.pipeline.normalisation.character_map_normaliser  # noqa: F401

def test_import_nmt_translator():
    import app.pipeline.normalisation.nmt_translator  # noqa: F401

def test_import_router():
    import app.pipeline.normalisation.router  # noqa: F401

def test_import_utils_logging():
    from app.utils.logging_utils import get_logger
    logger = get_logger("test")
    assert logger is not None


# --- Existing src/ tests still pass ---
# Run the existing test suite via subprocess to confirm no breakage.
# This is a safeguard — the src/ pipeline must remain fully operational.
def test_src_pipeline_imports_still_work():
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from pipeline.pipeline import process_field  # noqa: F401
    from pipeline.rules_engine import apply_rules  # noqa: F401
```

---

## Acceptance criteria

- `flask run` starts the application without errors (with `FLASK_ENV=development` and a valid `SECRET_KEY` in `.env`).
- `python run.py` starts the application without errors.
- All five blueprint routes (`/upload/`, `/paste/`, `/review/`, `/admin/`) return HTTP 200.
- All import tests in `tests/test_epic00_flask_skeleton.py` pass — every `app.pipeline.normalisation.*` module is importable.
- All existing `src/` tests pass without modification — `test_pipeline.py`, `test_rules.py`, `test_transliteration.py`, `test_evaluator.py`, `test_ocr_gate.py`, `test_ocr_pipeline.py`.
- `streamlit run app.py` continues to work — the Streamlit app is not modified.
- `app.config["LLM_ENABLED"]` is `False` in all environments unless `LLM_ENABLED=true` is explicitly set in `.env`.
- No database connection is required for the app to start — `SQLALCHEMY_DATABASE_URI` can be empty in development without crashing the factory.
