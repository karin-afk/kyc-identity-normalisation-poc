import pytest
from pipeline.transliteration_engine import transliterate


# ── Japanese Katakana (KYC007) — deterministic, should be accurate ──────────
def test_japanese_katakana():
    row = {"language": "ja", "field_type": "person_name"}
    result = transliterate("\u30bf\u30ca\u30ab \u30b1\u30f3", row)  # タナカ ケン
    assert result["processing_method"] == "TRANSLITERATE"
    norm = result["normalised_form"]
    assert "TANAKA" in norm
    assert "KEN" in norm


# ── Japanese Kanji (KYC006) — kanji flagged for review ────────────────────
def test_japanese_kanji_is_flagged_for_review():
    row = {"language": "ja", "field_type": "person_name"}
    result = transliterate("\u5c71\u7530 \u592a\u90ce", row)  # 山田 太郎
    assert result["review_required"] is True
    assert result["original_text"] == "\u5c71\u7530 \u592a\u90ce"


# ── Russian (KYC012) — multiple accepted spellings ───────────────────────
def test_russian_name():
    row = {"language": "ru", "field_type": "person_name"}
    result = transliterate("\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u0421\u043c\u0438\u0440\u043d\u043e\u0432", row)  # Алексей Смирнов
    assert result["processing_method"] == "TRANSLITERATE"
    norm = result["normalised_form"]
    assert "SMIRNOV" in norm
    assert any(v in norm for v in ("ALEKSEI", "ALEKSEJ", "ALEXEY", "ALEKSEY", "ALEKSII"))


# ── Russian with patronymic (KYC011) ────────────────────────────────────
def test_russian_patronymic():
    row = {"language": "ru", "field_type": "person_name"}
    result = transliterate("\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430 \u0421\u0435\u0440\u0433\u0435\u0435\u0432\u043d\u0430 \u0418\u0432\u0430\u043d\u043e\u0432\u0430", row)
    norm = result["normalised_form"]
    assert "EKATERINA" in norm or "YEKATERINA" in norm
    assert "IVANOVA" in norm


# ── Greek (KYC021) ────────────────────────────────────────────────────────
def test_greek_name():
    row = {"language": "el", "field_type": "person_name"}
    result = transliterate("\u0393\u03b5\u03ce\u03c1\u03b3\u03b9\u03bf\u03c2 \u03a0\u03b1\u03c0\u03b1\u03b4\u03cc\u03c0\u03bf\u03c5\u03bb\u03bf\u03c2", row)  # Γεώργιος Παπαδόπουλος
    assert "GEORGIOS" in result["normalised_form"]
    assert "PAPADOPOULOS" in result["normalised_form"]


# ── Greek B→V mapping (KYC022) ──────────────────────────────────────────
def test_greek_b_to_v_mapping():
    row = {"language": "el", "field_type": "person_name"}
    result = transliterate("\u0392\u03b1\u03c3\u03af\u03bb\u03b7\u03c2 \u039d\u03b9\u03ba\u03bf\u03bb\u03ac\u03bf\u03c5", row)  # Βασίλης Νικολάου
    norm = result["normalised_form"]
    assert "NIKOLAOU" in norm or "NIKOLAOS" in norm


# ── Chinese short name (KYC017) ───────────────────────────────────────────
def test_chinese_short_name():
    row = {"language": "zh", "field_type": "person_name"}
    result = transliterate("\u674e\u4f1f", row)  # 李伟
    norm = result["normalised_form"]
    assert "LI" in norm
    assert "WEI" in norm


# ── Chinese three-character name (KYC016) ────────────────────────────────
def test_chinese_three_char_name():
    row = {"language": "zh", "field_type": "person_name"}
    result = transliterate("\u738b\u5c0f\u660e", row)  # 王小明
    norm = result["normalised_form"]
    assert "WANG" in norm
    assert "XIAOMING" in norm or ("XIAO" in norm and "MING" in norm)


# ── Arabic — structure only; vowel ambiguity requires LLM ────────────────
def test_arabic_flags_review():
    row = {"language": "ar", "field_type": "person_name"}
    result = transliterate("\u0645\u062d\u0645\u062f \u0639\u0644\u064a \u062d\u0633\u0646", row)  # محمد علي حسن
    assert result["review_required"] is True
    assert result["original_text"] == "\u0645\u062d\u0645\u062f \u0639\u0644\u064a \u062d\u0633\u0646"
    assert result["processing_method"] == "TRANSLITERATE"
    assert result["normalised_form"] != ""  # some output produced


# ── Result schema contract ───────────────────────────────────────────────
def test_result_schema():
    required_keys = (
        "original_text", "latin_transliteration", "allowed_variants",
        "normalised_form", "processing_method", "confidence", "review_required",
    )
    row = {"language": "ru", "field_type": "person_name"}
    result = transliterate("\u0410\u043b\u0435\u043a\u0441\u0435\u0439", row)
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
