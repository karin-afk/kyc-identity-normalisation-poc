"""
tests/test_ocr_gate.py

Unit tests for the OCR gate module.
The actual GPT-4o call is mocked so no API key is needed to run the tests.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


def _make_mock_response(fields: list[dict]) -> MagicMock:
    msg = MagicMock()
    msg.content = json.dumps(fields)
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_extract_fields_returns_list(mock_openai_cls, tmp_path):
    # Create a minimal 1x1 white PNG so the file can be read
    import struct, zlib
    def _tiny_png(path):
        def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        data += chunk(b"IDAT", zlib.compress(b"\x00\xFF\xFF\xFF"))
        data += chunk(b"IEND", b"")
        path.write_bytes(data)
    img = tmp_path / "test_passport.png"
    _tiny_png(img)

    fields = [
        {"field_type": "person_name", "original_text": "山田 太郎",
         "language": "ja", "document_type": "passport", "ocr_confidence": 0.95},
        {"field_type": "passport_no", "original_text": "TK1234567",
         "language": "en", "document_type": "passport", "ocr_confidence": 0.99},
    ]
    mock_openai_cls.return_value.chat.completions.create.return_value = _make_mock_response(fields)

    from pipeline.ocr_gate import extract_fields_from_image
    result = extract_fields_from_image(str(img))

    assert len(result) == 2
    assert result[0]["field_type"] == "person_name"
    assert result[0]["original_text"] == "山田 太郎"
    assert result[1]["field_type"] == "passport_no"
    assert all("source_image" in r for r in result)


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("pipeline.ocr_gate.openai.OpenAI")
def test_extract_fields_strips_markdown_fences(mock_openai_cls, tmp_path):
    img = tmp_path / "doc.jpg"
    img.write_bytes(b"\xff\xd8\xff")  # minimal JPEG header

    fields = [{"field_type": "email", "original_text": "a@b.com",
               "language": "en", "document_type": "passport", "ocr_confidence": 1.0}]
    wrapped = "```json\n" + json.dumps(fields) + "\n```"
    mock_openai_cls.return_value.chat.completions.create.return_value = _make_mock_response_raw(wrapped)

    from pipeline.ocr_gate import extract_fields_from_image
    result = extract_fields_from_image(str(img))
    assert result[0]["original_text"] == "a@b.com"


def _make_mock_response_raw(raw: str) -> MagicMock:
    msg = MagicMock()
    msg.content = raw
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def test_no_api_key_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    img = tmp_path / "doc.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    from pipeline.ocr_gate import extract_fields_from_image
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        extract_fields_from_image(str(img))


def test_check_ocr_confidence_above_threshold():
    from pipeline.ocr_gate import check_ocr_confidence
    assert check_ocr_confidence({"ocr_confidence": "0.9"}) is True


def test_check_ocr_confidence_below_threshold():
    from pipeline.ocr_gate import check_ocr_confidence
    assert check_ocr_confidence({"ocr_confidence": "0.5"}) is False
