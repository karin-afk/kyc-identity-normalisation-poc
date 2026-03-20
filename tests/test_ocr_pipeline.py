"""
tests/test_ocr_pipeline.py

Integration tests for the OCR → pipeline flow, driven by the IMG* rows in
the golden dataset.

Design principles:
- The OpenAI Vision call is always mocked — no API key required.
- LLM layer (enrich_with_llm) is mocked for TRANSLATE_NORMALISE fields so
  that these tests remain deterministic.
- PRESERVE and TRANSLITERATE assertions use actual pipeline output so tests
  pass and fail for the right reasons.
"""

import csv
import json
import struct
import zlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_GOLDEN = Path(__file__).parent.parent / "data" / "golden_dataset.csv"


# ---------------------------------------------------------------------------
# Helpers — load the golden dataset
# ---------------------------------------------------------------------------

def _load_img_rows() -> list[dict]:
    """Return all IMG* rows from the golden dataset."""
    with open(_GOLDEN, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["case_id"].startswith("IMG")]


def _rows_for_image(basename: str) -> list[dict]:
    return [r for r in _load_img_rows() if Path(r["image_path"]).name == basename]


# ---------------------------------------------------------------------------
# Helpers — fake images and mock OpenAI responses
# ---------------------------------------------------------------------------

def _tiny_png(path: Path) -> None:
    """Write a valid 1×1 white PNG so open()+base64 work without errors."""
    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(b"\x00\xFF\xFF\xFF"))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def _make_openai_response(fields: list[dict]) -> MagicMock:
    msg = MagicMock()
    msg.content = json.dumps(fields)
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _ocr_fields_from_rows(rows: list[dict], confidence: float = 0.95) -> list[dict]:
    """Convert golden dataset rows to the dict format OCR gate produces."""
    return [
        {
            "field_type": r["field_type"],
            "original_text": r["original_text"],
            "language": r["language"],
            "document_type": r["document_type"],
            "ocr_confidence": confidence,
            "source_image": r["image_path"],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 1. PRESERVE fields — parametrised over all IMG PRESERVE rows
# ---------------------------------------------------------------------------

_preserve_rows = [r for r in _load_img_rows() if r["expected_treatment"] == "PRESERVE"]


@pytest.mark.parametrize("row", _preserve_rows, ids=[r["case_id"] for r in _preserve_rows])
def test_preserve_field_from_image_row(row):
    """
    All PRESERVE fields extracted from images (passport_no, email) must be
    returned unchanged by the pipeline regardless of which image they came from.
    """
    from pipeline.pipeline import process_field

    result = process_field(row)

    assert result["normalised_form"] == row["expected_normalised"]
    assert result["processing_method"] == "RULE"
    assert result["review_required"] is False


# ---------------------------------------------------------------------------
# 2. TRANSLITERATE — Latin-script names (MRZ / stamp format)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case_id,original_text,language,expected_normalised", [
    ("IMG001", "KUSAKA HIROSHI",  "ja", "KUSAKA HIROSHI"),
    ("IMG006", "AHMED SAMIR NASR ABDELNASER", "ar", "AHMED SAMIR NASR ABDELNASER"),
    ("IMG009", "GAIMU SAKURA",   "ja", "GAIMU SAKURA"),
    ("IMG011", "GAIMU NATSUKO",  "ja", "GAIMU NATSUKO"),
    ("IMG016", "NITOH SHINJI",   "ja", "NITOH SHINJI"),
])
def test_transliterate_latin_script_name(case_id, original_text, language, expected_normalised):
    """
    Latin-script names extracted from MRZ / stamps are already romanised.
    The transliteration engine must pass them through and produce the correct
    uppercase normalised form.
    """
    from pipeline.pipeline import process_field

    row = {
        "field_type": "person_name",
        "original_text": original_text,
        "language": language,
        "document_type": "passport",
    }
    result = process_field(row)

    assert result["normalised_form"] == expected_normalised, (
        f"{case_id}: expected {expected_normalised!r}, got {result['normalised_form']!r}"
    )


# ---------------------------------------------------------------------------
# 3. TRANSLITERATE — Cyrillic Russian name (IMG004)
# ---------------------------------------------------------------------------

def test_img004_russian_cyrillic_name_transliterated():
    """
    IMG004: Cyrillic text ЛИТВИНОВ АНДРЕЙ ВЯЧЕСЛАВОВИЧ is transliterated to
    Latin. The exact form depends on the `transliterate` library's scheme;
    we verify structure and that Latin ASCII is produced.
    """
    from pipeline.pipeline import process_field

    row = {
        "field_type": "person_name",
        "original_text": "ЛИТВИНОВ АНДРЕЙ ВЯЧЕСЛАВОВИЧ",
        "language": "ru",
        "document_type": "passport",
    }
    result = process_field(row)

    nf = result["normalised_form"]
    assert nf, "normalised_form must not be empty"
    assert nf == nf.upper(), "normalised_form must be uppercase"
    assert nf.isascii(), "normalised_form must be ASCII"
    assert "LITVINOV" in nf, "Surname LITVINOV must appear in transliteration"
    assert result["processing_method"] == "TRANSLITERATE"
    assert result["review_required"] is False


# ---------------------------------------------------------------------------
# 4. TRANSLITERATE — Arabic script name (IMG007)
# ---------------------------------------------------------------------------

def test_img007_arabic_script_name_routed_to_llm():
    """
    IMG007: Arabic-script name نهاد إبراهيم السيد النجار — now routed to the
    LLM layer for accurate vowel insertion. Verify the pipeline calls
    enrich_with_llm and returns ASCII Latin output.
    """
    from pipeline.pipeline import process_field

    row = {
        "field_type": "person_name",
        "original_text": "نهاد إبراهيم السيد النجار",
        "language": "ar",
        "document_type": "passport",
    }
    llm_mock = {
        "original_text": "نهاد إبراهيم السيد النجار",
        "normalised_form": "NIHAD IBRAHIM ELSAYED ALNAGGAR",
        "processing_method": "LLM",
        "confidence": 0.85,
        "review_required": False,
    }
    with patch("pipeline.pipeline.enrich_with_llm", return_value=llm_mock) as mock_llm:
        result = process_field(row)
        mock_llm.assert_called_once()

    assert result["processing_method"] == "LLM"
    assert result["normalised_form"] == "NIHAD IBRAHIM ELSAYED ALNAGGAR"
    assert result["normalised_form"].isascii()


# ---------------------------------------------------------------------------
# 5. TRANSLITERATE — Greek company acronym (IMG014)
# ---------------------------------------------------------------------------

def test_img014_greek_company_acronym_via_llm():
    """
    IMG014: company_name field goes through the LLM layer (not transliteration).
    Verify the pipeline routes company_name to enrich_with_llm and uses its output.
    """
    from pipeline.pipeline import process_field

    row = {
        "field_type": "company_name",
        "original_text": "ΔΕΗ",
        "language": "el",
        "document_type": "proof_of_address",
    }
    mock_result = {
        "original_text": "ΔΕΗ",
        "normalised_form": "DEI",
        "processing_method": "LLM",
        "confidence": 0.85,
        "review_required": True,
    }
    with patch("pipeline.pipeline.enrich_with_llm", return_value=mock_result) as mock_llm:
        result = process_field(row)
        mock_llm.assert_called_once()

    assert result["normalised_form"] == "DEI"


# ---------------------------------------------------------------------------
# 6. Full OCR → pipeline per image (mocked OpenAI)
# ---------------------------------------------------------------------------

@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_japanese4(mock_openai_cls, tmp_path):
    """
    japanese4.jpg → IMG001 (person_name), IMG002 (passport_no), IMG003 (address).
    Passport number must be preserved exactly; name must pass through uppercase.
    """
    img = tmp_path / "japanese4.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("japanese4.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    lmock = {"original_text": "TOKYO", "normalised_form": "TOKYO",
             "processing_method": "LLM", "confidence": 0.95, "review_required": False}

    with patch("pipeline.pipeline.enrich_with_llm", return_value=lmock):
        fields = extract_fields_from_image(str(img))
        results = {f["field_type"]: process_field(f) for f in fields}

    assert results["person_name"]["normalised_form"] == "KUSAKA HIROSHI"
    assert results["passport_no"]["normalised_form"] == "TH4572902"
    assert results["passport_no"]["processing_method"] == "RULE"
    assert results["address"]["normalised_form"] == "TOKYO"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_russia1(mock_openai_cls, tmp_path):
    """
    russia1.jpg → IMG004 (Cyrillic person_name), IMG005 (Cyrillic address via LLM).
    Name must be transliterated to Latin ASCII; address goes via mocked LLM.
    """
    img = tmp_path / "russia1.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("russia1.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    lmock = {"original_text": "ХУТОР ЯНГИТАУ", "normalised_form": "YANGITAU HAMLET",
             "processing_method": "LLM", "confidence": 0.80, "review_required": True}

    with patch("pipeline.pipeline.enrich_with_llm", return_value=lmock):
        fields = extract_fields_from_image(str(img))
        results = {f["field_type"]: process_field(f) for f in fields}

    name_nf = results["person_name"]["normalised_form"]
    assert name_nf.isascii(), "Name must be ASCII after transliteration"
    assert name_nf == name_nf.upper(), "Name must be uppercase"
    assert "LITVINOV" in name_nf
    assert results["address"]["normalised_form"] == "YANGITAU HAMLET"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_egypt1(mock_openai_cls, tmp_path):
    """
    egypt1.jpg → IMG006 (Latin-script Arabic name in MRZ format).
    Language=ar so it goes through LLM; name is already Latin so LLM returns it unchanged.
    """
    img = tmp_path / "egypt1.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("egypt1.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    lmock = {
        "original_text": "AHMED SAMIR NASR ABDELNASER",
        "normalised_form": "AHMED SAMIR NASR ABDELNASER",
        "processing_method": "LLM",
        "confidence": 0.90,
        "review_required": False,
    }
    with patch("pipeline.pipeline.enrich_with_llm", return_value=lmock):
        fields = extract_fields_from_image(str(img))
        results = [process_field(f) for f in fields]

    assert len(results) == 1
    assert results[0]["normalised_form"] == "AHMED SAMIR NASR ABDELNASER"
    assert results[0]["processing_method"] == "LLM"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_egypt2(mock_openai_cls, tmp_path):
    """
    egypt2.jpg → IMG007 (Arabic-script name via LLM) + IMG008 (passport_no PRESERVE).
    Arabic names now route through enrich_with_llm for better vowel accuracy.
    """
    img = tmp_path / "egypt2.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("egypt2.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    llm_mock = {
        "original_text": "\u0646\u0647\u0627\u062f \u0625\u0628\u0631\u0627\u0647\u064a\u0645 \u0627\u0644\u0633\u064a\u062f \u0627\u0644\u0646\u062c\u0627\u0631",
        "normalised_form": "NIHAD IBRAHIM ELSAYED ALNAGGAR",
        "processing_method": "LLM",
        "confidence": 0.85,
        "review_required": False,
    }
    with patch("pipeline.pipeline.enrich_with_llm", return_value=llm_mock):
        fields = extract_fields_from_image(str(img))
        by_type = {f["field_type"]: process_field(f) for f in fields}

    # Arabic-script name: routed to LLM, produces ICAO-standard Latin
    assert by_type["person_name"]["processing_method"] == "LLM"
    assert by_type["person_name"]["normalised_form"] == "NIHAD IBRAHIM ELSAYED ALNAGGAR"
    assert by_type["person_name"]["normalised_form"].isascii()
    # Passport number: exact preservation (unaffected by Arabic routing)
    assert by_type["passport_no"]["normalised_form"] == "A20799893"
    assert by_type["passport_no"]["processing_method"] == "RULE"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_japanese1(mock_openai_cls, tmp_path):
    """japanese1.png → IMG009 (person_name) + IMG010 (passport_no)."""
    img = tmp_path / "japanese1.png"
    _tiny_png(img)

    rows = _rows_for_image("japanese1.png")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    fields = extract_fields_from_image(str(img))
    by_type = {f["field_type"]: process_field(f) for f in fields}

    assert by_type["person_name"]["normalised_form"] == "GAIMU SAKURA"
    assert by_type["passport_no"]["normalised_form"] == "MJ0991103"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_japanese2(mock_openai_cls, tmp_path):
    """japanese2.jpg → IMG016 (person_name) + IMG017 (passport_no)."""
    img = tmp_path / "japanese2.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("japanese2.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    fields = extract_fields_from_image(str(img))
    by_type = {f["field_type"]: process_field(f) for f in fields}

    assert by_type["person_name"]["normalised_form"] == "NITOH SHINJI"
    assert by_type["passport_no"]["normalised_form"] == "TR0834772"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_japanese3(mock_openai_cls, tmp_path):
    """japanese3.jpg → IMG011 (person_name) + IMG012 (passport_no)."""
    img = tmp_path / "japanese3.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    rows = _rows_for_image("japanese3.jpg")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    fields = extract_fields_from_image(str(img))
    by_type = {f["field_type"]: process_field(f) for f in fields}

    assert by_type["person_name"]["normalised_form"] == "GAIMU NATSUKO"
    assert by_type["passport_no"]["normalised_form"] == "MJ4564879"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_full_pipeline_greece1(mock_openai_cls, tmp_path):
    """
    greece1.png → IMG013 (Greek address), IMG014 (Greek company acronym),
    IMG015 (Greek city name). All TRANSLATE_NORMALISE: LLM is mocked.
    """
    img = tmp_path / "greece1.png"
    _tiny_png(img)

    rows = _rows_for_image("greece1.png")
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(_ocr_fields_from_rows(rows))
    )

    from pipeline.ocr_gate import extract_fields_from_image
    from pipeline.pipeline import process_field

    # Map original_text → expected LLM normalised output per golden dataset
    _expected = {
        "Λεωφόρος Κηφισίας 30": "KIFISIAS AVENUE 30",
        "ΔΕΗ": "DEI",
        "Αθήνα": "ATHENS",
    }

    def _fake_llm(text: str, row: dict) -> dict:
        nf = _expected.get(text, text.upper())
        return {"original_text": text, "normalised_form": nf,
                "processing_method": "LLM", "confidence": 0.90, "review_required": False}

    with patch("pipeline.pipeline.enrich_with_llm", side_effect=_fake_llm):
        fields = extract_fields_from_image(str(img))
        results = [process_field(f) for f in fields]

    normalised_outputs = {r["original_text"]: r["normalised_form"] for r in results}
    assert normalised_outputs["Λεωφόρος Κηφισίας 30"] == "KIFISIAS AVENUE 30"
    assert normalised_outputs["ΔΕΗ"] == "DEI"
    assert normalised_outputs["Αθήνα"] == "ATHENS"


# ---------------------------------------------------------------------------
# 7. OCR confidence gating
# ---------------------------------------------------------------------------

def test_check_ocr_confidence_at_boundary():
    """Confidence exactly at the threshold (0.75) should pass."""
    from pipeline.ocr_gate import check_ocr_confidence, OCR_CONFIDENCE_THRESHOLD

    assert check_ocr_confidence({"ocr_confidence": OCR_CONFIDENCE_THRESHOLD}) is True


def test_check_ocr_confidence_below_boundary():
    """Confidence just below the threshold must fail."""
    from pipeline.ocr_gate import check_ocr_confidence, OCR_CONFIDENCE_THRESHOLD

    assert check_ocr_confidence({"ocr_confidence": OCR_CONFIDENCE_THRESHOLD - 0.01}) is False


def test_check_ocr_confidence_string_value():
    """check_ocr_confidence must accept string-encoded floats (as produced by CSV loading)."""
    from pipeline.ocr_gate import check_ocr_confidence

    assert check_ocr_confidence({"ocr_confidence": "0.92"}) is True
    assert check_ocr_confidence({"ocr_confidence": "0.50"}) is False


def test_low_ocr_confidence_field_still_processed():
    """
    A low-confidence field still goes through the pipeline.
    The caller (run_ocr.py) is responsible for adding the review flag.
    """
    from pipeline.ocr_gate import check_ocr_confidence
    from pipeline.pipeline import process_field

    field = {
        "field_type": "passport_no",
        "original_text": "TH4572902",
        "language": "en",
        "document_type": "passport",
        "ocr_confidence": 0.40,
    }
    assert check_ocr_confidence(field) is False
    result = process_field(field)
    # Pipeline itself does not know about OCR confidence — it preserves the number
    assert result["normalised_form"] == "TH4572902"
    assert result["review_required"] is False


# ---------------------------------------------------------------------------
# 8. OCR gate returns source_image on every field
# ---------------------------------------------------------------------------

@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_extract_fields_source_image_attached(mock_openai_cls, tmp_path):
    """Every field returned by extract_fields_from_image must include source_image."""
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    fields = [
        {"field_type": "passport_no", "original_text": "X1234567",
         "language": "en", "document_type": "passport", "ocr_confidence": 0.99},
    ]
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(fields)
    )

    from pipeline.ocr_gate import extract_fields_from_image

    result = extract_fields_from_image(str(img))
    assert all("source_image" in r for r in result)
    assert result[0]["source_image"] == img.name  # stored as basename, not full path


# ---------------------------------------------------------------------------
# 9. OCR gate — multiple fields structure
# ---------------------------------------------------------------------------

@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_extract_fields_all_required_keys_present(mock_openai_cls, tmp_path):
    """Every field from extract_fields_from_image must have the required keys."""
    img = tmp_path / "test.png"
    _tiny_png(img)

    ocr_out = [
        {"field_type": "person_name", "original_text": "山田 太郎",
         "language": "ja", "document_type": "passport", "ocr_confidence": 0.95},
        {"field_type": "passport_no", "original_text": "TK9988776",
         "language": "en", "document_type": "passport", "ocr_confidence": 0.99},
    ]
    mock_openai_cls.return_value.chat.completions.create.return_value = (
        _make_openai_response(ocr_out)
    )

    from pipeline.ocr_gate import extract_fields_from_image

    results = extract_fields_from_image(str(img))
    required_keys = {"field_type", "original_text", "language", "document_type",
                     "ocr_confidence", "source_image"}
    for r in results:
        missing = required_keys - r.keys()
        assert not missing, f"Missing keys {missing} in field {r}"
