"""Paste route HTTP integration tests.

Monkeypatches only at the LLM API boundary (detect_field_type).
All downstream processing — router, strategies A/B/C — runs against real code
and real lookup tables. Assertions verify actual normalised output values.
"""

from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app("testing")


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Template contract
# ---------------------------------------------------------------------------


def test_paste_form_field_name_is_original_text():
    """Template must use name='original_text'; the route reads request.form.get('original_text')."""
    template = Path(__file__).resolve().parents[1] / "app" / "templates" / "paste_sentence.html"
    html = template.read_text("utf-8")
    assert 'name="original_text"' in html, (
        "Form field must be named 'original_text' — route and template have diverged"
    )


# ---------------------------------------------------------------------------
# Strategy A — PRESERVE via HTTP
# ---------------------------------------------------------------------------


def test_paste_translate_preserve_field_real_result(client, monkeypatch):
    """Route must return the real Strategy A normalised value, not a mocked placeholder."""
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("passport_no", 0.99, "en"),
    )
    response = client.post("/paste/translate", data={"original_text": "TK1234567"})
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "TK1234567" in html       # normalised_form — proves Strategy A ran with the real router
    assert "PRESERVE" in html        # processing_method from the real router


# ---------------------------------------------------------------------------
# Strategy B — CALENDAR via HTTP
# ---------------------------------------------------------------------------


def test_paste_translate_strategy_b_calendar_real_result(client, monkeypatch):
    """Route must convert Thai Buddhist date via real Strategy B calendar logic."""
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("date_of_birth", 0.95, "th"),
    )
    response = client.post("/paste/translate", data={"original_text": "2568/5/8"})
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "2025-05-08" in html      # Gregorian conversion — proves Strategy B ran
    assert "CALENDAR" in html


# ---------------------------------------------------------------------------
# Strategy C — VOCABULARY via HTTP
# ---------------------------------------------------------------------------


def test_paste_translate_strategy_c_vocabulary_real_result(client, monkeypatch):
    """Route must resolve a German legal form via real Strategy C vocabulary lookup."""
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("legal_form", 0.97, "de"),
    )
    response = client.post("/paste/translate", data={"original_text": "GmbH"})
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "GMBH" in html            # canonical form — proves Strategy C ran with real lookup
    assert "VOCABULARY" in html


# ---------------------------------------------------------------------------
# UNRESOLVED — review notice
# ---------------------------------------------------------------------------


def test_paste_translate_unresolved_shows_review_notice(client, monkeypatch):
    """UNRESOLVED fields must render the native-speaker review notice in the partial."""
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("person_name", 0.88, "ar"),
    )
    response = client.post("/paste/translate", data={"original_text": "محمد علي"})
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Awaiting native speaker review" in html


# ---------------------------------------------------------------------------
# Input validation (400 responses)
# ---------------------------------------------------------------------------


def test_paste_translate_empty_text_returns_400(client):
    response = client.post("/paste/translate", data={"original_text": ""})
    assert response.status_code == 400


def test_paste_translate_text_too_long_returns_400(client):
    response = client.post("/paste/translate", data={"original_text": "x" * 2001})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# LLM error — graceful degradation
# ---------------------------------------------------------------------------


def test_paste_translate_llm_api_error_degrades_gracefully(client, monkeypatch):
    """If the OpenAI client raises on every call the route must return 200, not 500."""
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector, "_get_client",
        lambda: (_ for _ in ()).throw(RuntimeError("no key")),
    )
    response = client.post(
        "/paste/translate",
        data={"original_text": "some text that will trigger fallback"},
    )
    assert response.status_code == 200
