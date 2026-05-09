# Session Debug Logging

## Purpose

This branch adds end-to-end trace logging so each app session can be debugged from browser actions through backend orchestration and strategy execution.

A session is defined as one browser interaction lifecycle. A unique `trace_session_id` is created and all events for that session are written to one file.

## Log File Location

- Default directory: `logs/sessions/`
- One file per session: `sess_<uuid>.jsonl`
- Format: JSON Lines (one JSON object per line)

## What's Captured

### Frontend events
- Page loads
- Tab clicks (Document/Sentence/Review)
- Form submits
- Clipboard actions (paste/copy/cut)
- HTMX request start/end
- Visibility changes
- Session end on window unload (via `sendBeacon`)

### Backend events
- Request start and completion (with duration)
- Paste route payload and validation decisions
- Upload route payload and validation decisions
- Field detector lifecycle:
  - detector start
  - raw LLM response
  - parsed result or detector error
- Orchestrator lifecycle:
  - input row
  - output result
- Router lifecycle:
  - strategy selection
  - misses and unresolved fallbacks
- Strategy C vocabulary lookup:
  - skip reasons
  - hit/miss decisions

## Key Files

- `app/utils/session_trace.py`: session id creation + JSONL appender
- `app/routes/telemetry.py`: frontend telemetry ingestion endpoints
- `app/static/js/session_trace.js`: browser event capture and POST/beacon sender
- `app/__init__.py`: request hooks and blueprint registration

## Config

- `SESSION_TRACE_ENABLED` (default `true`)
- `SESSION_LOG_DIR` (default `logs/sessions`)

Set in `app/config.py`.

## Notes

- Logs are local runtime artifacts and ignored by git via `.gitignore` (`logs/`).
- Tracing is defensive: failures in logging do not break user flows.
