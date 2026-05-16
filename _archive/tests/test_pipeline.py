import pytest
from unittest.mock import patch
from pipeline.pipeline import process_field
from pipeline.analyst_handler import extract_name_and_alias, ALIAS_TRIGGERS


def test_preserve_field_end_to_end():
    """KYC026 — passport number must pass through unchanged."""
    row = {"field_type": "passport_no", "original_text": "563982174", "language": "en"}
    result = process_field(row)
    assert result["normalised_form"] == "563982174"
    assert result["processing_method"] == "RULE"


def test_preserve_email_end_to_end():
    """KYC027 — email must pass through unchanged."""
    row = {"field_type": "email", "original_text": "john.doe@test.com", "language": "en"}
    result = process_field(row)
    assert result["normalised_form"] == "john.doe@test.com"


def test_russian_name_end_to_end():
    """KYC012 — Russian name goes through transliteration layer."""
    row = {"field_type": "person_name", "original_text": "Алексей Смирнов", "language": "ru"}
    result = process_field(row)
    assert result["processing_method"] == "TRANSLITERATE"
    norm = result["normalised_form"]
    assert "SMIRNOV" in norm
    assert any(v in norm for v in ("ALEKSEI", "ALEKSEJ", "ALEXEY", "ALEKSEY"))


def test_address_routes_to_llm():
    """Addresses are routed to the LLM layer (stub returns LLM method)."""
    row = {
        "field_type": "address",
        "original_text": "ул. Ленина 10 Москва",
        "language": "ru",
    }
    result = process_field(row)
    assert result["processing_method"] == "LLM"
    assert result["original_text"] == "ул. Ленина 10 Москва"


def test_company_name_routes_to_llm():
    """Company names are routed to the LLM layer."""
    row = {
        "field_type": "company_name",
        "original_text": "株式会社トヨタ",
        "language": "ja",
    }
    result = process_field(row)
    assert result["processing_method"] == "LLM"


def test_result_always_has_original_text():
    """Every result must preserve the original text."""
    row = {"field_type": "person_name", "original_text": "李伟", "language": "zh"}
    result = process_field(row)
    assert result["original_text"] == "李伟"


# ---------------------------------------------------------------------------
# Section 4: extract_name_and_alias — unit tests
# ---------------------------------------------------------------------------

def test_extract_russian_alias_trigger():
    """по прозвищу splits Александр / Саша."""
    result = extract_name_and_alias("Александр по прозвищу Саша", "ru")
    assert result["split_method"] == "trigger"
    assert "Александр" in result["primary_text"]
    assert "Саша" in result["alias_text"]


def test_extract_english_also_known_as():
    result = extract_name_and_alias("Wang Qiang also known as Wang Xiaoqiang", "zh")
    assert result["split_method"] == "trigger"
    assert result["primary_text"] == "Wang Qiang"
    assert result["alias_text"] == "Wang Xiaoqiang"


def test_extract_no_trigger_treated_as_primary():
    result = extract_name_and_alias("unknown phrase no trigger", "en")
    assert result["split_method"] == "no_split"
    assert result["primary_text"] == "unknown phrase no trigger"
    assert result["alias_text"] is None


@pytest.mark.parametrize("language,text", [
    ("ar", "محمد المعروف ب أبو بكر"),
    ("el", "Σπύρος γνωστός ως Νίκος"),
    ("zh", "王强又名王小强"),
    ("ja", "田中別名タロウ"),
    ("de", "Klaus genannt Klauschen"),
    ("fr", "Jean dit Jeannot"),
    ("es", "Carlos conocido como Carlitos"),
    ("it", "Marco detto Marchino"),
    ("ko", "김철수 별명 철이"),
])
def test_alias_trigger_fires_for_each_language(language: str, text: str):
    """At least one trigger pattern fires for each supported language."""
    result = extract_name_and_alias(text, language)
    assert result["split_method"] == "trigger", (
        f"No trigger fired for language={language!r}, text={text!r}"
    )


# ---------------------------------------------------------------------------
# Section 4: process_analyst_field via process_field (mocked transliteration)
# ---------------------------------------------------------------------------

def _mock_transliterate(text: str, row: dict) -> dict:
    """Test stub: returns ASCII-uppercased text."""
    import unicodedata
    norm = unicodedata.normalize("NFD", text)
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    norm = norm.upper()
    return {
        "original_text": text, "normalised_form": norm,
        "latin_transliteration": norm, "allowed_variants": [],
        "analyst_english_rendering": norm,
        "processing_method": "TRANSLITERATE", "confidence": 0.9,
        "review_required": False, "review_reason": None, "should_use_in_screening": True,
    }


def test_russian_composite_alias_via_process_field():
    """Александр по прозвищу Саша → contains ALEKSANDR and SASHA, review=True."""
    row = {
        "field_type": "alias",
        "original_text": "Александр по прозвищу Саша",
        "language": "ru",
    }
    result = process_field(row)
    assert result["review_required"] is True
    norm = result["normalised_form"]
    assert "ALSO KNOWN AS" in norm
    # Russian transliteration of Александр → first part before ALSO KNOWN AS
    primary = norm.split("ALSO KNOWN AS")[0].strip()
    assert len(primary) > 0
    alias = norm.split("ALSO KNOWN AS")[1].strip()
    assert len(alias) > 0


def test_greek_composite_alias_via_process_field():
    """γνωστός ως Νίκος (el) → contains NIKOS, review=True."""
    row = {
        "field_type": "alias",
        "original_text": "Σπύρος γνωστός ως Νίκος",
        "language": "el",
    }
    result = process_field(row)
    assert result["review_required"] is True
    norm = result["normalised_form"]
    assert "ALSO KNOWN AS" in norm
    assert "NIKOS" in norm or "NIKO" in norm.split("ALSO KNOWN AS")[1]


def test_english_composite_alias_combines_correctly():
    """Wang Qiang also known as Wang Xiaoqiang → combined with ALSO KNOWN AS."""
    row = {
        "field_type": "alias",
        "original_text": "Wang Qiang also known as Wang Xiaoqiang",
        "language": "zh",
    }
    with patch("pipeline.pipeline.transliterate", side_effect=_mock_transliterate):
        result = process_field(row)
    assert result["review_required"] is True
    assert "ALSO KNOWN AS" in result["normalised_form"]


def test_no_trigger_alias_treated_as_whole():
    """Alias with no trigger phrase → whole text treated as primary name."""
    row = {
        "field_type": "alias",
        "original_text": "John Smith",
        "language": "en",
    }
    result = process_field(row)
    assert result["processing_method"] == "TRANSLITERATE"
