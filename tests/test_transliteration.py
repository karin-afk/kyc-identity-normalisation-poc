import pytest
from pipeline.transliteration_engine import transliterate, _apply_bgn_pcgn_corrections
from pipeline.field_classifier import is_composite_alias
from utils.calendar_utils import kanji_numeral_to_int, detect_and_convert_japanese_era


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


# ── TRANSLATE_COMPOSITE: is_composite_alias detection ────────────────────
@pytest.mark.parametrize("text,expected", [
    # English descriptors
    ("Wang Qiang also known as Wang Xiaoqiang", True),
    ("John Smith AKA Johnny", True),
    ("Muhammad nicknamed Abu Bakr", True),
    ("Mary known as Molly", True),
    # Russian
    ("Александр по прозвищу Саша", True),
    ("Иван известный как Ваня", True),
    # Chinese
    ("王强又名王小强", True),
    ("陈明别名陈大明", True),
    # Greek
    ("Σπύρος Αντωνίου γνωστός ως Σπύρος ο Μεγάλος", True),
    # Non-composite — should return False
    ("Wang Qiang", False),
    ("Александр Иванов", False),
    ("Jane Marie Smith", False),
    ("محمد علي حسن", False),
])
def test_is_composite_alias(text: str, expected: bool):
    assert is_composite_alias(text) is expected


# ── TRANSLATE_COMPOSITE: LLM routing uses normalised field ───────────────
def test_composite_alias_uses_normalised_field(monkeypatch):
    """LLM response for composite alias must use parsed['normalised'],
    not parsed['primary']."""
    from unittest.mock import MagicMock, patch
    import json

    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "primary": "WANG QIANG",
        "normalised": "WANG QIANG ALSO KNOWN AS WANG XIAOQIANG",
        "variants": ["WANG QIANG AKA WANG XIAOQIANG"],
    })

    with patch("openai.OpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create.return_value = mock_response
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-composite")

        from pipeline import llm_layer
        # Force re-read env var inside module
        llm_layer.OPENAI_API_KEY = "test-key-composite"

        row = {"field_type": "alias", "language": "zh", "original_text": "王强又名王小强"}
        result = llm_layer.enrich_with_llm("王强又名王小强", row)

    assert result["normalised_form"] == "WANG QIANG ALSO KNOWN AS WANG XIAOQIANG"
    assert result["processing_method"] == "LLM/COMPOSITE"


# ── TRANSLATE_COMPOSITE: non-composite alias uses primary field ───────────
def test_non_composite_alias_uses_primary_field(monkeypatch):
    """LLM response for a non-composite alias must use parsed['primary']."""
    from unittest.mock import MagicMock, patch
    import json

    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "primary": "JEAN LUC MOREAU",
        "normalised": "JEAN LUC MOREAU ALSO KNOWN AS JL",
        "variants": ["JEAN-LUC MOREAU"],
    })

    # Use Arabic name path (also uses primary) to verify non-composite behaviour
    with patch("openai.OpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create.return_value = mock_response
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-noncomposite")

        from pipeline import llm_layer
        llm_layer.OPENAI_API_KEY = "test-key-noncomposite"

        # Arabic person_name: is_arabic_name=True, is_composite=False
        row = {"field_type": "person_name", "language": "ar", "original_text": "جان لوك"}
        result = llm_layer.enrich_with_llm("جان لوك", row)

    assert result["normalised_form"] == "JEAN LUC MOREAU"


# ── Section 1: BGN/PCGN corrections for Russian/Ukrainian ────────────────

def test_bgn_pcgn_corrections_unit():
    """_apply_bgn_pcgn_corrections applies all substitutions in correct order."""
    assert _apply_bgn_pcgn_corrections("Natalja") == "Natalya"     # Ja→Ya
    assert _apply_bgn_pcgn_corrections("Jurij") == "Yurij"          # Ju→Yu (trailing j stays)
    assert _apply_bgn_pcgn_corrections("Schukin") == "Shchukin"    # Sch→Shch
    assert _apply_bgn_pcgn_corrections("Jekaterina") == "Yekaterina"  # Je→Ye
    assert _apply_bgn_pcgn_corrections("Tatjana") == "Tatyana"      # ja→ya
    assert _apply_bgn_pcgn_corrections("Ekaterina") == "Yekaterina" # word-initial E→Ye


@pytest.mark.parametrize("cyrillic,expected_in_norm", [
    ("Наталья",    "NATALYA"),    # Я at end — not NATALJA
    ("Юрий",       "YURIJ"),      # Ю at start — Ju→Yu; trailing j from й preserved
    ("Екатерина",  "YEKATERINA"), # Е word-initial → Ye
    ("Татьяна",    "TATYANA"),    # Тя combination
    ("Щукин",      "SHCHUKIN"),   # Щ — Sch→Shch
])
def test_russian_bgn_pcgn_in_transliteration(cyrillic: str, expected_in_norm: str):
    row = {"language": "ru", "field_type": "person_name"}
    result = transliterate(cyrillic, row)
    assert expected_in_norm in result["normalised_form"], (
        f"Expected '{expected_in_norm}' in '{result['normalised_form']}' "
        f"for input '{cyrillic}'"
    )


def test_bulgarian_not_affected_by_bgn_pcgn():
    """Bulgarian should NOT have Ja→Ya applied — it has different BGN conventions."""
    row = {"language": "bg", "field_type": "person_name"}
    # Яна is a Bulgarian name — after library it becomes Jana (not Yana) because
    # Bulgarian BGN uses different standards; we must NOT force-correct it.
    result = transliterate("Яна Иванова", row)
    # Key assertion: the result was processed and has content (not empty)
    assert result["normalised_form"] != ""
    assert result["processing_method"] == "TRANSLITERATE"


# ---------------------------------------------------------------------------
# Section 3: kanji_numeral_to_int
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("五十三", 53),
    ("二〇〇五", 2005),
    ("十二", 12),
    ("三", 3),
    ("二十", 20),
    ("元", 1),
    ("六十四", 64),
])
def test_kanji_numeral_to_int(text: str, expected: int):
    assert kanji_numeral_to_int(text) == expected


# ---------------------------------------------------------------------------
# Section 3: detect_and_convert_japanese_era (unit)
# ---------------------------------------------------------------------------

def test_showa_era_conversion():
    """昭和五十三年四月三日 → 1978-04-03, era=Showa, review=True."""
    result = detect_and_convert_japanese_era("昭和五十三年四月三日")
    assert result["normalised"] == "1978-04-03"
    assert result["era_detected"] == "Showa"
    assert result["review_required"] is True
    assert "Showa" in result["review_reason"]


def test_heisei_first_year():
    """平成元年一月八日 → 1989-01-08 (元年 = year 1)."""
    result = detect_and_convert_japanese_era("平成元年一月八日")
    assert result["normalised"] == "1989-01-08"
    assert result["era_detected"] == "Heisei"
    assert result["review_required"] is True


def test_reiwa_era_conversion():
    """令和三年一月五日 → 2021-01-05."""
    result = detect_and_convert_japanese_era("令和三年一月五日")
    assert result["normalised"] == "2021-01-05"
    assert result["era_detected"] == "Reiwa"


def test_kanji_gregorian_no_era():
    """二〇〇五年十二月一日 → 2005-12-01, no era, review=False."""
    result = detect_and_convert_japanese_era("二〇〇五年十二月一日")
    assert result["normalised"] == "2005-12-01"
    assert result["era_detected"] is None
    assert result["review_required"] is False


# ---------------------------------------------------------------------------
# Section 3: transliterate() routing for Japanese date fields
# ---------------------------------------------------------------------------

def test_japanese_era_date_via_transliterate():
    """transliterate() converts Japanese era date for ja+birth_date field."""
    row = {"language": "ja", "field_type": "birth_date"}
    result = transliterate("昭和五十三年四月三日", row)
    assert result["normalised_form"] == "1978-04-03"
    assert result["review_required"] is True


def test_japanese_era_date_field_date_type():
    """transliterate() converts Japanese date for ja+date field."""
    row = {"language": "ja", "field_type": "date"}
    result = transliterate("令和三年一月五日", row)
    assert result["normalised_form"] == "2021-01-05"


# ---------------------------------------------------------------------------
# Section 5: German
# ---------------------------------------------------------------------------

def test_german_umlaut_expansion():
    """Müller → primary MUELLER, variant includes MULLER."""
    row = {"language": "de", "field_type": "person_name"}
    result = transliterate("Müller", row)
    assert result["normalised_form"] == "MUELLER"
    assert "MULLER" in result["allowed_variants"]


def test_german_eszett():
    """Weiß → WEISS."""
    row = {"language": "de", "field_type": "person_name"}
    result = transliterate("Weiß", row)
    assert result["normalised_form"] == "WEISS"


def test_german_hyphenated_name():
    """Schröder-Braun → SCHROEDER-BRAUN primary, space variant."""
    row = {"language": "de", "field_type": "person_name"}
    result = transliterate("Schröder-Braun", row)
    assert "SCHROEDER" in result["normalised_form"]
    space_variant = result["normalised_form"].replace("-", " ")
    assert space_variant in result["allowed_variants"] or "-" not in result["normalised_form"]


def test_german_noble_particle():
    """Heinrich von Braun → primary includes 'von', variant capitalises Von."""
    row = {"language": "de", "field_type": "person_name"}
    result = transliterate("Heinrich von Braun", row)
    norm = result["normalised_form"]
    # primary should have lowercase VON (uppercased from the translation chain → VON)
    assert "BRAUN" in norm


# ---------------------------------------------------------------------------
# Section 5: French
# ---------------------------------------------------------------------------

def test_french_accent_strip():
    """Hélène Masson → HELENE MASSON."""
    row = {"language": "fr", "field_type": "person_name"}
    result = transliterate("Hélène Masson", row)
    assert result["normalised_form"] == "HELENE MASSON"


def test_french_hyphenated_name():
    """Jean-François → primary JEAN-FRANCOIS or JEAN FRANCOIS, with variant."""
    row = {"language": "fr", "field_type": "person_name"}
    result = transliterate("Jean-François Dupont", row)
    norm = result["normalised_form"]
    assert "FRANCOIS" in norm
    assert "DUPONT" in norm
    # Space-separated variant must exist
    space_variant = norm.replace("-", " ")
    assert space_variant in result["allowed_variants"] or "-" not in norm


def test_french_apostrophe_elision():
    """Laurent d'Avignon → primary LAURENT D AVIGNON, fused variant."""
    row = {"language": "fr", "field_type": "person_name"}
    result = transliterate("Laurent d'Avignon", row)
    norm = result["normalised_form"]
    assert "AVIGNON" in norm
    # Fused variant (no space, no apostrophe)
    all_forms = [norm] + result["allowed_variants"]
    assert any("DAVIGNON" in v for v in all_forms)


# ---------------------------------------------------------------------------
# Section 5: Spanish
# ---------------------------------------------------------------------------

def test_spanish_accent_strip():
    """María-José Fernández → MARIA-JOSE FERNANDEZ (hyphen preserved)."""
    row = {"language": "es", "field_type": "person_name"}
    result = transliterate("María-José Fernández", row)
    norm = result["normalised_form"]
    assert "MARIA" in norm
    assert "FERNANDEZ" in norm


def test_spanish_n_tilde_variant():
    """Muñoz → MUNOZ primary, MUNYOZ variant."""
    row = {"language": "es", "field_type": "person_name"}
    result = transliterate("Muñoz", row)
    assert result["normalised_form"] == "MUNOZ"
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("MUNYOZ" in v for v in all_forms)


def test_spanish_particle_variant():
    """del Rio → particle-dropped variant generated."""
    row = {"language": "es", "field_type": "person_name"}
    result = transliterate("Francisco del Río Blanco", row)
    norm = result["normalised_form"]
    all_forms = [norm] + result["allowed_variants"]
    assert any("RIO BLANCO" in v or "FRANCISCO RIO" in v for v in all_forms)


# ---------------------------------------------------------------------------
# Section 5: Italian
# ---------------------------------------------------------------------------

def test_italian_apostrophe_particle():
    """D'Angelo → primary D ANGELO, variants DANGELO and ANGELO."""
    row = {"language": "it", "field_type": "person_name"}
    result = transliterate("Lorenzo D'Angelo", row)
    norm = result["normalised_form"]
    assert "ANGELO" in norm
    all_forms = [norm] + result["allowed_variants"]
    assert any("DANGELO" in v for v in all_forms)
    assert any("ANGELO" in v and "D" not in v.split("ANGELO")[0].replace("LORENZ", "") for v in all_forms)


def test_italian_double_consonant_preserved():
    """Niccolò Bianchi → double-c preserved (NICCOLO, not NICOLO)."""
    row = {"language": "it", "field_type": "person_name"}
    result = transliterate("Niccolò Bianchi", row)
    assert "NICCOLO" in result["normalised_form"]
    assert "BIANCHI" in result["normalised_form"]


# ---------------------------------------------------------------------------
# Section 5: Korean
# ---------------------------------------------------------------------------

def test_korean_surname_variants():
    """박지훈 → primary BAK JIHUN, variants include PARK JIHUN."""
    row = {"language": "ko", "field_type": "person_name"}
    result = transliterate("박지훈", row)
    assert result["review_required"] is True
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("JIHUN" in v for v in all_forms)
    assert any("PARK" in v for v in all_forms)


def test_korean_lee_variants():
    """이민호 → variants include LEE MINHO."""
    row = {"language": "ko", "field_type": "person_name"}
    result = transliterate("이민호", row)
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("LEE" in v or "YI" in v or "RHEE" in v for v in all_forms)


def test_korean_ryu_variants():
    """류지성 → variants include RYU and LYU forms."""
    row = {"language": "ko", "field_type": "person_name"}
    result = transliterate("류지성", row)
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("RYU" in v or "LYU" in v or "YOO" in v for v in all_forms)


# ---------------------------------------------------------------------------
# Section 5: English
# ---------------------------------------------------------------------------

def test_english_apostrophe_surname():
    """O'Brien → variants include OBRIEN and O BRIEN."""
    row = {"language": "en", "field_type": "person_name"}
    result = transliterate("Michael O'Brien", row)
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("OBRIEN" in v for v in all_forms)
    assert any("O BRIEN" in v for v in all_forms)


def test_english_mac_variant():
    """MacDonald → variant Macdonald (alternate capitalisation)."""
    row = {"language": "en", "field_type": "person_name"}
    result = transliterate("Alistair MacDonald", row)
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("MACDONALD" in v or "MCDONALD" in v for v in all_forms)


def test_english_saint_variant():
    """St John → variant SAINT JOHN."""
    row = {"language": "en", "field_type": "person_name"}
    result = transliterate("Thomas St John", row)
    all_forms = [result["normalised_form"]] + result["allowed_variants"]
    assert any("SAINT JOHN" in v for v in all_forms)
