# Flask Template Caching Issue & Resolution

## Problem

Flask's development server was serving stale Jinja2 compiled templates even after:
- Clearing `__pycache__/` directories
- Setting `PYTHONDONTWRITEBYTECODE=1`
- Restarting the server multiple times

**Root Cause:** By default, Flask/Jinja2 disables `TEMPLATES_AUTO_RELOAD` even in debug mode because it adds a filesystem stat call per request. This means template changes are not detected on subsequent requests—Flask holds the compiled template in memory until the process restarts.

**Symptom:** After committing UI amendments (e.g., removing dropdowns, updating result display templates), the browser consistently showed old HTML structure despite correct template files on disk. Direct Jinja2 rendering worked, confirming the template file was correct—the issue was Flask's cache.

## Solution Implemented

Add a single configuration flag to enable template auto-reloading in development:

**File: `app/config.py`**

```python
class DevelopmentConfig(Config):
    DEBUG: bool = True
    TEMPLATES_AUTO_RELOAD: bool = True  # ← This line
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///kyc_dev.db"
    )
```

Additionally, ensure `FLASK_ENV=development` is set in `.env` so the correct config class is loaded:

**File: `.env`**

```
FLASK_ENV=development
OPENAI_API_KEY=...
```

Also required: `load_dotenv()` must be called early in app initialization to load `.env` variables before Flask/extensions initialize:

**File: `app/__init__.py`**

```python
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

def create_app(config_name: str | None = None) -> Flask:
    ...
```

## How It Works

- `TEMPLATES_AUTO_RELOAD = True` tells Jinja2 to check the file modification timestamp on every request
- If the template file has changed, it recompiles and reloads
- Development only: This adds one filesystem stat call per request (negligible impact)
- Production must never have this enabled: Templates are compiled once at startup for performance

## Testing After Deploy

1. Start Flask: `python -m flask --app app:create_app run --host 127.0.0.1 --port 5001`
2. Hard refresh browser: **Ctrl+Shift+R** (clears browser-side cache)
3. Make a template change (e.g., edit `app/templates/paste_sentence.html`)
4. Refresh browser without restarting server—change should appear instantly

## Related Issues

This was discovered during LLM classifier UI amendment implementation where:
- Route was correctly calling detector and passing detected field type/language
- Template was correctly rendering new metadata fields
- But browser kept showing old dropdown-based UI from previous template version

The fix ensures template changes are always visible during development, preventing confusion between stale caches and actual code issues.
