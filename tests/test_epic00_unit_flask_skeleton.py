"""Unit tests for Epic 00 Flask skeleton."""

from flask import Flask

from app import create_app


def test_create_app_returns_flask_instance() -> None:
    app = create_app("testing")
    assert isinstance(app, Flask)


def test_create_app_testing_config_flags() -> None:
    app = create_app("testing")
    assert app.config["TESTING"] is True
    assert app.config["LLM_ENABLED"] is False


def test_secret_key_present_in_testing() -> None:
    app = create_app("testing")
    assert app.config["SECRET_KEY"] == "test-secret-key-not-for-production"


def test_upload_and_backup_folders_configured() -> None:
    app = create_app("testing")
    assert isinstance(app.config["UPLOAD_FOLDER"], str)
    assert isinstance(app.config["BACKUP_FOLDER"], str)


def test_root_route_registered() -> None:
    app = create_app("testing")
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/" in rules
