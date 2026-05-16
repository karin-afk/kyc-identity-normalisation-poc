"""Session-scoped trace logging for frontend and backend debugging."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import current_app, has_request_context, request, session

_WRITE_LOCK = threading.Lock()


def ensure_session_context() -> tuple[str, bool]:
    """Ensure a stable session identifier exists for the browser session."""
    existing = session.get("trace_session_id")
    if isinstance(existing, str) and existing:
        return existing, False

    session_id = f"sess_{uuid4().hex}"
    session["trace_session_id"] = session_id
    session["trace_started_at"] = _utcnow_iso()
    session.permanent = False
    return session_id, True


def get_session_id() -> str:
    """Get the current session id or a fallback when no request context exists."""
    if not has_request_context():
        return "no-request-context"

    session_id, _ = ensure_session_context()
    return session_id


def log_event(event_name: str, details: dict[str, Any] | None = None, source: str = "backend") -> None:
    """Append a single trace event to the current session log file."""
    safe_details = _sanitize(details or {})

    try:
        entry: dict[str, Any] = {
            "ts": _utcnow_iso(),
            "event": event_name,
            "source": source,
            "session_id": get_session_id(),
            "details": safe_details,
        }

        if has_request_context():
            entry["request"] = {
                "method": request.method,
                "path": request.path,
                "endpoint": request.endpoint,
                "is_htmx": bool(request.headers.get("HX-Request")),
                "remote_addr": request.remote_addr,
            }

        log_path = _session_log_path(entry["session_id"])
        with _WRITE_LOCK:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        # Logging should never break user flows.
        try:
            current_app.logger.warning("session trace logging failed: %s", exc)
        except Exception:
            pass


def _session_log_path(session_id: str) -> Path:
    configured = current_app.config.get("SESSION_LOG_DIR", "")
    if configured:
        root = Path(configured)
    else:
        root = Path(current_app.root_path).parent / "logs" / "sessions"

    root.mkdir(parents=True, exist_ok=True)
    return root / f"{session_id}.jsonl"


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _sanitize(value: Any) -> Any:
    """Keep logs JSON-safe and reasonably compact."""
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str) and len(value) > 600:
            return value[:600] + "...<truncated>"
        return value
    return str(value)
