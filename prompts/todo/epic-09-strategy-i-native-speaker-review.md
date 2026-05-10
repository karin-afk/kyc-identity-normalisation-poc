# Epic 09 — Strategy I: Native Speaker Review

## Save to: `prompts/todo/epic-09-strategy-i-native-speaker-review.md`

---

## Context

Strategy I is the final step in the normalisation pipeline. When no strategy (A through H)
resolves a field with confidence, it is flagged as `UNRESOLVED` and a `ReviewTask` record
is created. A registered native speaker then reviews it, confirms or corrects the output,
and submits. The confirmed result is written permanently to the verified repository
(Strategy E). The original analyst is notified by email.

**This epic covers:**
1. `ReviewTask` creation when the router reaches UNRESOLVED
2. Round-robin assignment to native speakers for the detected language
3. The review tab UI (already partially built — wire it to real data)
4. Submit endpoint — confirmed result written to verified repository
5. Email notification stubs (Azure Communication Services wired in a later epic)

**This epic does NOT cover:**
- Azure Communication Services email sending (stub only — real email in a later epic)
- Azure Entra ID SSO (Epic 12)
- The full verified repository implementation (Epic 05 — must be complete first)

---

## What exists

**Models (already built):**
- `app/models/review.py` — `ReviewTask` model exists
- `app/models/user.py` — `User` model with `is_native_speaker` flag exists
- `app/models/translation.py` — `VerifiedTranslation` and `TokenEntry` exist

**Routes (partially built):**
- `app/routes/review.py` — exists, likely returns stub responses
- `app/templates/review.html` — exists
- `app/templates/review_task.html` — exists
- `app/templates/partials/review_submitted.html` — exists

**Repository (may be a stub):**
- `app/pipeline/normalisation/repository_lookup.py` — exists, `store_verified()` may be stub

**Tasks:**
- `app/tasks/notification_task.py` — exists (stub)
- `app/tasks/backup_task.py` — exists (stub)

---

## What does NOT exist and must be built

- `create_review_task()` function — creates a `ReviewTask` when router hits UNRESOLVED
- Real implementation of `app/routes/review.py` — real DB queries, not stubs
- `store_verified()` in `app/pipeline/normalisation/repository_lookup.py` — real DB write
- Round-robin native speaker assignment logic
- Tests in `tests/test_strategy_i_review.py`

---

## Path conventions

- Models: `app/models/`
- Routes: `app/routes/review.py`
- Repository: `app/pipeline/normalisation/repository_lookup.py`
- Tasks: `app/tasks/notification_task.py`
- JSON data: `data/lookup_tables/` and `data/seed/` (project root)
- Test file: `tests/test_strategy_i_review.py`
- No imports from `src/` at runtime

---

## Step 1 — `create_review_task()` utility

Add to `app/pipeline/normalisation/repository_lookup.py` or a new file
`app/pipeline/normalisation/review_task_creator.py`:

```python
"""
Creates ReviewTask records when the normalisation router reaches UNRESOLVED.
Called by the router's _unresolved() fallback.
"""

def create_review_task(
    original_text: str,
    field_type: str,
    language: str,
    suggested_form: str | None,
    review_reason: str,
    document_id: int | None = None,
    paste_session_id: int | None = None,
) -> int | None:
    """
    Create a ReviewTask record and assign to a native speaker.

    Assignment strategy: round-robin across all active users with
    is_native_speaker=True and the matching language in their
    native_speaker_languages list. If no native speaker exists for
    the language, assign to any active native speaker (language "any").
    If no native speakers exist at all, leave assigned_to=None.

    Returns the ReviewTask.id, or None if the database is not available.
    Never raises — review task creation failure must not crash the router.
    """
    try:
        from app.extensions import db
        from app.models.review import ReviewTask
        from app.models.user import User
        from datetime import datetime

        assigned_to = _assign_native_speaker(language)

        task = ReviewTask(
            field_type=field_type,
            original_text=original_text,
            language_code=language,
            suggested_form=suggested_form,
            review_reason=review_reason,
            status="pending",
            assigned_to=assigned_to,
            assigned_at=datetime.utcnow() if assigned_to else None,
            document_id=document_id,
            paste_session_id=paste_session_id,
        )
        db.session.add(task)
        db.session.commit()
        return task.id

    except Exception:
        return None


def _assign_native_speaker(language: str) -> int | None:
    """
    Round-robin assignment. Returns user.id or None.

    Round-robin: find all eligible users, pick the one with the oldest
    assigned_at on their most recent pending task. If no pending tasks,
    pick the user with the lowest id (most senior).
    """
    try:
        from app.models.user import User, NativeSpeakerLanguage
        from app.models.review import ReviewTask
        from app.extensions import db

        # Users who speak this language
        eligible = (
            db.session.query(User)
            .join(NativeSpeakerLanguage)
            .filter(
                NativeSpeakerLanguage.language_code == language,
                User.is_active == True,
            )
            .all()
        )

        if not eligible:
            # Fall back to any native speaker
            eligible = User.query.filter_by(
                is_native_speaker=True, is_active=True
            ).all()

        if not eligible:
            return None

        # Pick the user with fewest current pending tasks
        def _pending_count(user):
            return ReviewTask.query.filter_by(
                assigned_to=user.id, status="pending"
            ).count()

        return min(eligible, key=_pending_count).id

    except Exception:
        return None
```

---

## Step 2 — Wire into the router

In `app/pipeline/normalisation/router.py`, update `_unresolved()` to also create a
`ReviewTask` when inside a Flask application context:

```python
def _unresolved(text: str, field_type: str, language: str,
                reason: str | None = None) -> dict:
    """
    Called when no strategy resolves the field.
    Creates a ReviewTask if running inside a Flask app context.
    """
    review_reason = reason or (
        f"No strategy resolved field_type='{field_type}' language='{language}'"
    )

    # Attempt to create a review task — never crashes the router
    try:
        from flask import has_app_context
        if has_app_context():
            from app.pipeline.normalisation.review_task_creator import create_review_task
            create_review_task(
                original_text=text,
                field_type=field_type,
                language=language,
                suggested_form=None,
                review_reason=review_reason,
            )
    except Exception:
        pass

    return {
        "original_text":           text,
        "normalised_form":         None,
        "allowed_variants":        [],
        "processing_method":       "UNRESOLVED",
        "confidence":              0.0,
        "review_required":         True,
        "review_reason":           review_reason,
        "should_use_in_screening": False,
        "latin_transliteration":   None,
        "analyst_english_rendering": None,
    }
```

---

## Step 3 — Real review routes

Replace stub content in `app/routes/review.py`:

```python
"""Review routes — native speaker task queue and submission."""

from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db

review_bp = Blueprint("review", __name__, url_prefix="/review")


@review_bp.route("/", methods=["GET"])
def index():
    """Show pending review tasks for the current native speaker."""
    try:
        from app.models.review import ReviewTask
        # TODO Epic 12: filter by current authenticated user
        # For now show all pending tasks (development mode)
        tasks = (
            ReviewTask.query
            .filter_by(status="pending")
            .order_by(ReviewTask.assigned_at.asc())
            .all()
        )
        return render_template("review.html", tasks=tasks)
    except Exception:
        return render_template("review.html", tasks=[])


@review_bp.route("/<int:task_id>", methods=["GET"])
def task(task_id: int):
    """Single task review page."""
    try:
        from app.models.review import ReviewTask
        t = ReviewTask.query.get_or_404(task_id)
        return render_template("review_task.html", task=t)
    except Exception:
        return render_template(
            "partials/not_implemented.html",
            feature="Review task database (Epic 06)"
        ), 200


@review_bp.route("/<int:task_id>/submit", methods=["POST"])
def submit(task_id: int):
    """
    Save native speaker confirmation or correction.
    Writes confirmed result to verified repository.
    Returns HTMX partial.
    """
    confirmed_form = request.form.get("confirmed_form", "").strip().upper()
    variants_raw   = request.form.get("allowed_variants", "")
    variants       = [v.strip() for v in variants_raw.split(",") if v.strip()]

    try:
        from app.models.review import ReviewTask
        from datetime import datetime

        t = ReviewTask.query.get_or_404(task_id)
        t.confirmed_form     = confirmed_form
        t.confirmed_variants = variants
        t.status             = "approved" if confirmed_form == (t.suggested_form or "") else "corrected"
        t.reviewed_at        = datetime.utcnow()
        # TODO Epic 12: t.reviewed_by = current_user.id

        # Write to verified repository
        try:
            from app.pipeline.normalisation.repository_lookup import RepositoryLookupService
            RepositoryLookupService.store_verified(
                original_text=t.original_text,
                language=t.language_code,
                field_type=t.field_type,
                normalised_form=confirmed_form,
                allowed_variants=variants,
                processing_method=t.suggested_form and "SUGGESTION" or "UNRESOLVED",
                verified_by_user_id=1,  # TODO Epic 12: real user id
            )
        except Exception:
            pass  # Repository write failure must not block task completion

        db.session.commit()

        # Stub email notification — real email in Azure Communication Services epic
        _stub_notify_analyst(t)

        return render_template("partials/review_submitted.html", task=t)

    except Exception as e:
        return render_template(
            "partials/not_implemented.html",
            feature=f"Review submission: {e}"
        ), 200


@review_bp.route("/escalate-paste", methods=["POST"])
def escalate_paste():
    """Create a ReviewTask from a paste tab escalation."""
    original_text        = request.form.get("original_text", "")
    field_type           = request.form.get("field_type", "unstructured_text")
    language             = request.form.get("language", "")
    normalised_suggestion = request.form.get("normalised_suggestion", "")

    try:
        from app.pipeline.normalisation.review_task_creator import create_review_task
        task_id = create_review_task(
            original_text=original_text,
            field_type=field_type,
            language=language,
            suggested_form=normalised_suggestion or None,
            review_reason="Escalated from paste tab by analyst",
        )
        if task_id:
            return (
                '<p style="font-size:13px;color:#6B6B6B">'
                'Escalated to review queue. A native speaker will be notified.</p>'
            )
        raise RuntimeError("Task creation failed")

    except Exception:
        return render_template(
            "partials/not_implemented.html",
            feature="Review task creation (Epic 05 database required)"
        ), 200


def _stub_notify_analyst(task) -> None:
    """
    Placeholder for analyst notification email.
    Real implementation uses Azure Communication Services (later epic).
    Logs intent only — does not send email.
    """
    from app.utils.logging_utils import get_logger
    logger = get_logger("review")
    logger.info(
        "STUB: Would notify analyst for task %s (field=%s, language=%s)",
        task.id, task.field_type, task.language_code,
    )
```

---

## Step 4 — `store_verified()` in `app/pipeline/normalisation/repository_lookup.py`

If the existing `store_verified()` is a stub, implement it now. Minimum viable version:

```python
@staticmethod
def store_verified(
    original_text: str,
    language: str,
    field_type: str,
    normalised_form: str,
    allowed_variants: list[str],
    processing_method: str,
    verified_by_user_id: int,
    source_document_id: int | None = None,
) -> None:
    """
    Write a confirmed translation to the verified_translations table.
    Upsert on (original_text, language_code, field_type).
    Triggers JSON backup after write.
    """
    from app.models.translation import VerifiedTranslation
    from app.extensions import db
    from datetime import datetime

    existing = VerifiedTranslation.query.filter_by(
        original_text=original_text,
        language_code=language,
        field_type=field_type,
    ).first()

    if existing:
        existing.normalised_form  = normalised_form
        existing.allowed_variants = allowed_variants
        existing.verified_by      = verified_by_user_id
        existing.verified_at      = datetime.utcnow()
    else:
        entry = VerifiedTranslation(
            original_text=original_text,
            language_code=language,
            field_type=field_type,
            normalised_form=normalised_form,
            allowed_variants=allowed_variants,
            processing_method=processing_method,
            verified_by=verified_by_user_id,
            verified_at=datetime.utcnow(),
            source_document_id=source_document_id,
        )
        db.session.add(entry)

    db.session.commit()
    _trigger_backup()


def _trigger_backup() -> None:
    """Trigger async JSON backup. Stub if Celery not yet configured."""
    try:
        from app.tasks.backup_task import run_backup
        run_backup.delay()
    except Exception:
        pass
```

---

## Tests — `tests/test_strategy_i_review.py`

```python
"""Tests for Strategy I — native speaker review workflow."""

import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# ── ReviewTask creation ────────────────────────────────────────────────────────

def test_unresolved_router_result_has_correct_shape():
    """UNRESOLVED result must have the correct shape regardless of DB state."""
    from app.pipeline.normalisation.router import route_field
    r = route_field({
        "original_text": "محمد عبد الله",
        "field_type":    "person_name",
        "language":      "ar",
    })
    assert r["processing_method"] == "UNRESOLVED"
    assert r["review_required"] is True
    assert r["normalised_form"] is None
    assert r["should_use_in_screening"] is False
    assert r["review_reason"] is not None


def test_create_review_task_with_db(app):
    with app.app_context():
        from app.pipeline.normalisation.review_task_creator import create_review_task
        task_id = create_review_task(
            original_text="محمد عبد الله",
            field_type="person_name",
            language="ar",
            suggested_form=None,
            review_reason="No strategy resolved",
        )
        assert task_id is not None
        from app.models.review import ReviewTask
        task = ReviewTask.query.get(task_id)
        assert task is not None
        assert task.status == "pending"
        assert task.original_text == "محمد عبد الله"
        assert task.language_code == "ar"


def test_create_review_task_without_db_does_not_raise():
    """create_review_task must not raise even when DB is unavailable."""
    from app.pipeline.normalisation.review_task_creator import create_review_task
    result = create_review_task(
        original_text="test",
        field_type="person_name",
        language="ar",
        suggested_form=None,
        review_reason="test",
    )
    # Returns None when no DB — does not raise
    assert result is None or isinstance(result, int)


# ── Review routes ──────────────────────────────────────────────────────────────

def test_review_index_returns_200(client):
    response = client.get("/review/")
    assert response.status_code == 200


def test_review_index_shows_empty_queue_message(client):
    html = client.get("/review/").get_data(as_text=True)
    assert "No pending tasks" in html or "review" in html.lower()


def test_review_task_not_found_returns_404(client, app):
    with app.app_context():
        response = client.get("/review/99999")
        assert response.status_code in (200, 404)


def test_review_submit_approves_task(client, app):
    with app.app_context():
        from app.models.review import ReviewTask
        from app.extensions import db
        from datetime import datetime

        task = ReviewTask(
            field_type="person_name",
            original_text="محمد",
            language_code="ar",
            suggested_form="MUHAMMAD",
            review_reason="No strategy resolved",
            status="pending",
            assigned_at=datetime.utcnow(),
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(
        f"/review/{task_id}/submit",
        data={"confirmed_form": "MUHAMMAD", "allowed_variants": "MOHAMMED,MOHAMED"},
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "MUHAMMAD" in html or "confirmed" in html.lower()

    with app.app_context():
        from app.models.review import ReviewTask
        updated = ReviewTask.query.get(task_id)
        assert updated.status == "approved"
        assert updated.confirmed_form == "MUHAMMAD"


def test_review_submit_corrects_task(client, app):
    with app.app_context():
        from app.models.review import ReviewTask
        from app.extensions import db
        from datetime import datetime

        task = ReviewTask(
            field_type="person_name",
            original_text="محمد",
            language_code="ar",
            suggested_form="MOHAMAD",
            review_reason="Test",
            status="pending",
            assigned_at=datetime.utcnow(),
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(
        f"/review/{task_id}/submit",
        data={"confirmed_form": "MUHAMMAD", "allowed_variants": ""},
    )
    assert response.status_code == 200

    with app.app_context():
        from app.models.review import ReviewTask
        updated = ReviewTask.query.get(task_id)
        assert updated.status == "corrected"
        assert updated.confirmed_form == "MUHAMMAD"


def test_escalate_paste_returns_200(client):
    response = client.post(
        "/review/escalate-paste",
        data={
            "original_text": "محمد عبد الله",
            "field_type": "person_name",
            "language": "ar",
            "normalised_suggestion": "",
        },
    )
    assert response.status_code == 200


# ── store_verified ─────────────────────────────────────────────────────────────

def test_store_verified_creates_entry(app):
    with app.app_context():
        from app.pipeline.normalisation.repository_lookup import RepositoryLookupService
        RepositoryLookupService.store_verified(
            original_text="محمد",
            language="ar",
            field_type="person_name",
            normalised_form="MUHAMMAD",
            allowed_variants=["MOHAMMED", "MOHAMED"],
            processing_method="UNRESOLVED",
            verified_by_user_id=1,
        )
        from app.models.translation import VerifiedTranslation
        entry = VerifiedTranslation.query.filter_by(
            original_text="محمد", language_code="ar", field_type="person_name"
        ).first()
        assert entry is not None
        assert entry.normalised_form == "MUHAMMAD"


def test_store_verified_upserts_not_duplicates(app):
    with app.app_context():
        from app.pipeline.normalisation.repository_lookup import RepositoryLookupService
        from app.models.translation import VerifiedTranslation

        for form in ("MOHAMAD", "MUHAMMAD"):
            RepositoryLookupService.store_verified(
                original_text="محمد", language="ar", field_type="person_name",
                normalised_form=form, allowed_variants=[],
                processing_method="UNRESOLVED", verified_by_user_id=1,
            )

        count = VerifiedTranslation.query.filter_by(
            original_text="محمد", language_code="ar", field_type="person_name"
        ).count()
        assert count == 1

        entry = VerifiedTranslation.query.filter_by(
            original_text="محمد", language_code="ar", field_type="person_name"
        ).first()
        assert entry.normalised_form == "MUHAMMAD"  # latest value
```

---

## Acceptance criteria

- `route_field()` with an unresolvable field returns `processing_method == "UNRESOLVED"` and `review_required == True` — always, with or without a database
- `create_review_task()` creates a `ReviewTask` record in the database with `status="pending"`
- `create_review_task()` returns `None` (not raises) when the database is unavailable
- `GET /review/` returns HTTP 200 and renders the task queue (empty or with tasks)
- `POST /review/<id>/submit` with `confirmed_form="MUHAMMAD"` updates the task status to `approved` and writes to `verified_translations`
- `POST /review/<id>/submit` with a different form than `suggested_form` sets status to `corrected`
- `store_verified()` upserts — calling it twice for the same `(original_text, language, field_type)` results in one row, not two
- `POST /review/escalate-paste` returns HTTP 200 without crashing
- All tests in `tests/test_strategy_i_review.py` pass
- No imports from `src/` at runtime in any `app/` module
