"""
Environment-based configuration for the KYC Identity Normalisation Flask app.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "")

    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 52428800))
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    ALLOWED_EXTENSIONS: set[str] = set(
        os.environ.get("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png,tiff,docx,txt").split(",")
    )

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

    LLM_ENABLED: bool = os.environ.get("LLM_ENABLED", "false").lower() == "true"
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")
    OPENAI_MAX_TOKENS: int = int(os.environ.get("OPENAI_MAX_TOKENS", 1000))

    BACKUP_FOLDER: str = os.environ.get("BACKUP_FOLDER", str(BASE_DIR / "backups"))
    BACKUP_RETENTION_COUNT: int = int(os.environ.get("BACKUP_RETENTION_COUNT", 30))

    OCR_CONFIDENCE_THRESHOLD: float = float(os.environ.get("OCR_CONFIDENCE_THRESHOLD", 0.85))

    GEONAMES_DATA_PATH: str = os.environ.get(
        "GEONAMES_DATA_PATH", str(BASE_DIR / "data" / "geonames" / "allCountries.txt")
    )

    AUDIT_GENESIS_HASH: str = os.environ.get("AUDIT_GENESIS_HASH", "")

    CELERY_BROKER_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_TASK_TIME_LIMIT: int = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 300))

    SESSION_TRACE_ENABLED: bool = os.environ.get("SESSION_TRACE_ENABLED", "true").lower() == "true"
    SESSION_LOG_DIR: str = os.environ.get("SESSION_LOG_DIR", str(BASE_DIR / "logs" / "sessions"))


class DevelopmentConfig(Config):
    DEBUG: bool = True
    TEMPLATES_AUTO_RELOAD: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///kyc_dev.db"
    )


class ProductionConfig(Config):
    DEBUG: bool = False


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
