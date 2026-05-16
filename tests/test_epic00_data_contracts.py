"""Data contract tests for Epic 00 module and config contracts."""

import importlib

from app import create_app


def test_normalisation_modules_importable() -> None:
    modules = [
        "app.pipeline.normalisation.field_types",
        "app.pipeline.normalisation.preserve",
        "app.pipeline.normalisation.calendar_rules",
        "app.pipeline.normalisation.vocabulary_lookup",
        "app.pipeline.normalisation.geographic_lookup",
        "app.pipeline.normalisation.repository_lookup",
        "app.pipeline.normalisation.transliteration",
        "app.pipeline.normalisation.character_map_normaliser",
        "app.pipeline.normalisation.nmt_translator",
        "app.pipeline.normalisation.router",
    ]
    for module_name in modules:
        importlib.import_module(module_name)


def test_required_config_keys_present() -> None:
    app = create_app("testing")
    required_keys = [
        "SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "UPLOAD_FOLDER",
        "BACKUP_FOLDER",
        "LLM_ENABLED",
        "OCR_CONFIDENCE_THRESHOLD",
        "GEONAMES_DATA_PATH",
    ]
    for key in required_keys:
        assert key in app.config


def test_logging_contract_exposes_get_logger() -> None:
    from app.utils.logging_utils import get_logger

    logger = get_logger("epic00-contract")
    assert logger is not None
