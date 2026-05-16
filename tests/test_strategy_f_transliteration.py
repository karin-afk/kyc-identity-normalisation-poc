"""
tests/test_strategy_f_transliteration.py

Strategy F — Transliteration tests.
No mocks. Calls apply_transliteration() and route_field() directly.
"""

import pytest
import sys
from pathlib import Path

# Ensure app and src are importable
ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="module")
def app_context():
    from app import create_app
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()


from app.pipeline.normalisation.transliteration import apply_transliteration


# ── Existing languages — must still pass after wiring ─────────────────────────

def test_russian_bgn_pcgn_natalya(app_context):
    r = apply_transliteration("Наталья", "ru", "person_name")
    assert r is not None
    assert r["normalised_form"] == "NATALYA", (
        f"Expected NATALYA, got {r['normalised_form']}. "
        "Check BGN/PCGN corrections in transliteration_engine.py"
    )


def test_russian_bgn_pcgn_aleksandr(app_context):
    r = apply_transliteration("Александр", "ru", "person_name")
    assert r is not None
    assert r["normalised_form"] == "ALEKSANDR"


def test_russian_full_name(app_context):
    r = apply_transliteration("Иванова Наталья Александровна", "ru", "person_name")
    assert r is not None
    assert "IVANOVA" in r["normalised_form"]
    assert "NATALYA" in r["normalised_form"]


def test_greek_nikos(app_context):
    r = apply_transliteration("Νίκος", "el", "person_name")
    assert r is not None
    assert r["normalised_form"] == "NIKOS"


def test_greek_full_name(app_context):
    r = apply_transliteration("Νίκος Παπαδόπουλος", "el", "person_name")
    assert r is not None
    assert "NIKOS" in r["normalised_form"]
    assert "PAPADOPOULOS" in r["normalised_form"]


def test_japanese_surname_tanaka(app_context):
    r = apply_transliteration("田中", "ja", "person_name")
    assert r is not None
    assert "TANAKA" in r["normalised_form"]


def test_japanese_full_name(app_context):
    r = apply_transliteration("田中 太郎", "ja", "person_name")
    assert r is not None
    assert "TANAKA" in r["normalised_form"]
    assert "TARO" in r["normalised_form"]


def test_chinese_full_name_fusion(app_context):
    r = apply_transliteration("王小明", "zh", "person_name")
    assert r is not None
    assert r["normalised_form"] == "WANG XIAOMING"


def test_korean_name(app_context):
    r = apply_transliteration("이민준", "ko", "person_name")
    assert r is not None
    assert "MINJUN" in r["normalised_form"]


def test_arabic_always_review_required(app_context):
    r = apply_transliteration("محمد عبد الله", "ar", "person_name")
    assert r is not None
    assert r["review_required"] is True
    assert r["normalised_form"] is not None


def test_german_umlaut(app_context):
    r = apply_transliteration("Müller", "de", "person_name")
    assert r is not None
    assert r["normalised_form"] == "MUELLER"
    assert "MULLER" in r["allowed_variants"]


def test_french_accent(app_context):
    r = apply_transliteration("Élodie", "fr", "person_name")
    assert r is not None
    assert r["normalised_form"] == "ELODIE"


# ── New language handlers ─────────────────────────────────────────────────────

def test_hebrew_standard_name(app_context):
    r = apply_transliteration("דוד לוי", "he", "person_name")
    assert r is not None
    assert r["normalised_form"] is not None
    assert len(r["normalised_form"]) > 0
    assert r["review_required"] is False


def test_hebrew_not_falling_to_unidecode(app_context):
    """Hebrew must use its dedicated handler, not the unidecode fallback."""
    r = apply_transliteration("שרה", "he", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"
    # If all chars are ASCII or space/hyphen, the handler worked (unidecode produces garbage)
    assert all(c.isascii() or c in " -" for c in r["normalised_form"])


def test_persian_always_review_required(app_context):
    r = apply_transliteration("احمد", "fa", "person_name")
    assert r is not None
    assert r["review_required"] is True
    reason = r.get("review_reason") or ""
    assert "vowel" in reason.lower() or "Persian" in reason or "persian" in reason.lower()


def test_persian_not_falling_to_unidecode(app_context):
    r = apply_transliteration("محمد", "fa", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"


def test_thai_standard_name(app_context):
    r = apply_transliteration("สมชาย", "th", "person_name")
    assert r is not None
    assert r["normalised_form"] is not None
    assert len(r["normalised_form"]) > 0
    assert r["review_required"] is False


def test_thai_not_falling_to_unidecode(app_context):
    r = apply_transliteration("นารี", "th", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"
    assert all(c.isascii() or c in " -" for c in r["normalised_form"])


# ── Fallback for unknown languages ────────────────────────────────────────────

def test_unknown_language_falls_back_gracefully(app_context):
    r = apply_transliteration("Tëst", "xyz", "person_name")
    assert r is not None
    assert r["review_required"] is True


# ── Empty/non-transliteration-field returns None ──────────────────────────────

def test_empty_text_returns_none(app_context):
    r = apply_transliteration("", "ru", "person_name")
    assert r is None


def test_non_transliteration_field_returns_none(app_context):
    """Geographic/preserve/date fields must not be handled by Strategy F."""
    r = apply_transliteration("GmbH", "de", "legal_form")
    assert r is None


# ── Router integration ────────────────────────────────────────────────────────

def test_russian_routes_to_transliteration(app_context):
    from app.pipeline.normalisation.router import route_field
    r = route_field({"original_text": "Наталья", "field_type": "person_name", "language": "ru"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "NATALYA"


def test_japanese_routes_to_transliteration(app_context):
    from app.pipeline.normalisation.router import route_field
    r = route_field({"original_text": "田中", "field_type": "person_name", "language": "ja"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert "TANAKA" in r["normalised_form"]


def test_greek_routes_to_transliteration(app_context):
    from app.pipeline.normalisation.router import route_field
    r = route_field({"original_text": "Νίκος", "field_type": "person_name", "language": "el"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "NIKOS"


def test_chinese_routes_to_transliteration(app_context):
    from app.pipeline.normalisation.router import route_field
    r = route_field({"original_text": "王小明", "field_type": "person_name", "language": "zh"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "WANG XIAOMING"


def test_passport_does_not_route_to_transliteration(app_context):
    """Preserve fields must never reach Strategy F."""
    from app.pipeline.normalisation.router import route_field
    r = route_field({"original_text": "TK1234567", "field_type": "passport_no"})
    assert r["processing_method"] == "PRESERVE"
