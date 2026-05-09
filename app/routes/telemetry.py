"""Telemetry endpoints for browser-side session event tracing."""

from __future__ import annotations

from flask import Blueprint, request

from app.utils.session_trace import log_event

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/telemetry")


@telemetry_bp.route("/event", methods=["POST"])
def event() -> tuple[str, int]:
    payload = request.get_json(silent=True) or {}

    event_name = payload.get("event_name") or "frontend_event"
    details = payload.get("details") if isinstance(payload.get("details"), dict) else {}
    if payload.get("client_ts") is not None:
        details["client_ts"] = payload.get("client_ts")

    log_event(str(event_name), details=details, source="frontend")
    return "", 204


@telemetry_bp.route("/session-end", methods=["POST"])
def session_end() -> tuple[str, int]:
    payload = request.get_json(silent=True) or {}
    details = payload.get("details") if isinstance(payload.get("details"), dict) else {}
    details["reason"] = payload.get("reason", "window_unload")
    details["client_ts"] = payload.get("client_ts")

    log_event("session_ended", details=details, source="frontend")
    return "", 204
