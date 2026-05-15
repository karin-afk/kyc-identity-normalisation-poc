"""LLM-based field/language classifier for sentence normalisation."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re

from openai import OpenAI

from app.utils.session_trace import log_event

logger = logging.getLogger(__name__)

FIELD_TYPES = [
    # Identifiers
    "passport_no",
    "id_no",
    "id_number",
    "national_id_no",
    "registration_no",
    "company_no",
    "commercial_registration_no",
    "business_registration_no",
    "tax_id",
    "vat_number",
    "licence_no",
    "drivers_licence_no",
    "document_number",
    "reference_no",
    "email",
    "lei_code",
    "swift_code",
    "iban",
    # Dates
    "date_of_birth",
    "issue_date",
    "expiry_date",
    "incorporation_date",
    "registration_date",
    "financial_period_start",
    "financial_period_end",
    "date_of_dissolution",
    "date_of_change",
    # Names
    "person_name",
    "given_name",
    "family_name",
    "full_name",
    "alias",
    "maiden_name",
    "company_name",
    "trading_name",
    # Corporate structure
    "legal_form",
    "status",
    "role",
    "share_class",
    "capital_change_type",
    "industry_code",
    "document_type",
    # Geography
    "nationality",
    "country_of_birth",
    "country_of_residence",
    "country_of_incorporation",
    "country_of_registration",
    "address",
    "registered_address",
    "business_address",
    "place_of_birth",
    "city",
    "region",
    # Financial
    "share_capital",
    "total_assets",
    "total_liabilities",
    "net_assets",
    "revenue",
    "expenses",
    "profit",
    "number_of_shares",
    "number_of_issued_shares",
    "ownership_percentage",
    "voting_rights",
    # Prose
    "nature_of_business",
    "business_purpose",
    "accounting_policies",
    "locality_information",
    "capital_changes_narrative",
    "issuing_authority",
    "unstructured_text",
]

LANGUAGE_CODES = [
    "ar",
    "be",
    "bg",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fa",
    "fr",
    "he",
    "it",
    "ja",
    "ko",
    "nl",
    "no",
    "pl",
    "pt",
    "ru",
    "sv",
    "th",
    "tr",
    "uk",
    "zh",
]

_EXAMPLES = json.dumps([
    {"input": "AB123456", "output": {"field_type": "passport_no", "language_code": "en", "confidence": 0.92}},
    {"input": "FR76 3000 6000 0112 3456 7890 189", "output": {"field_type": "iban", "language_code": "fr", "confidence": 0.99}},
    {"input": "user@bank.co.uk", "output": {"field_type": "email", "language_code": "en", "confidence": 0.99}},
    {"input": "2510/3/22", "output": {"field_type": "date_of_birth", "language_code": "th", "confidence": 0.93}},
    {"input": "98/12/25", "output": {"field_type": "date_of_birth", "language_code": "zh", "confidence": 0.88}},
    {"input": "1385/6/31", "output": {"field_type": "date_of_birth", "language_code": "fa", "confidence": 0.91}},
    {"input": "▲12,500", "output": {"field_type": "total_assets", "language_code": "ja", "confidence": 0.94}},
    {"input": "€2.500.000,00", "output": {"field_type": "share_capital", "language_code": "de", "confidence": 0.91}},
    {"input": "有限公司", "output": {"field_type": "legal_form", "language_code": "zh", "confidence": 0.97}},
    {"input": "ЗАО", "output": {"field_type": "legal_form", "language_code": "ru", "confidence": 0.94}},
    {"input": "청산중", "output": {"field_type": "status", "language_code": "ko", "confidence": 0.93}},
    {"input": "attiva", "output": {"field_type": "status", "language_code": "it", "confidence": 0.91}},
    {"input": "نشط", "output": {"field_type": "status", "language_code": "ar", "confidence": 0.91}},
    {"input": "감사", "output": {"field_type": "role", "language_code": "ko", "confidence": 0.91}},
    {"input": "สัญชาติ ไทย", "output": {"field_type": "nationality", "language_code": "th", "confidence": 0.90}},
    {"input": "İran", "output": {"field_type": "nationality", "language_code": "tr", "confidence": 0.92}},
    {"input": "Björk", "output": {"field_type": "person_name", "language_code": "sv", "confidence": 0.91}},
    {"input": "Παπαδόπουλος", "output": {"field_type": "person_name", "language_code": "el", "confidence": 0.95}},
    {"input": "Ли Мин Чжун", "output": {"field_type": "person_name", "language_code": "ru", "confidence": 0.88}},
    {"input": "Chen Wei", "output": {"field_type": "person_name", "language_code": "zh", "confidence": 0.85}},
    {"input": "Kärntnerstraße 22, 1010 Wien", "output": {"field_type": "registered_address", "language_code": "de", "confidence": 0.94}},
    {"input": "輸出入業及び国内商業", "output": {"field_type": "nature_of_business", "language_code": "ja", "confidence": 0.92}},
    {"input": "中国", "output": {"field_type": "nationality", "language_code": "zh", "confidence": 0.93}},
    {"input": "ألمانيا", "output": {"field_type": "nationality", "language_code": "ar", "confidence": 0.92}},
    {"input": "سعودي", "output": {"field_type": "nationality", "language_code": "ar", "confidence": 0.91}},
], indent=2)

_SYSTEM_PROMPT = f"""You are a KYC document data classifier. Your only job is to identify:
1. The KYC field type of the text
2. The language it is written in

Return ONLY a JSON object with exactly three fields:
- "field_type": one of {json.dumps(FIELD_TYPES)}
- "language_code": one of {json.dumps(LANGUAGE_CODES)}
- "confidence": a float between 0.0 and 1.0

Rules:
- field_type must be exactly one of the values listed above. No other values allowed.
- language_code must be exactly one of the ISO 639-1 codes listed above. No other values allowed.
- Classify only.
- Return only the JSON object. No explanation. No markdown. No backticks.

Calendar disambiguation rules (critical):
- A 4-digit year above 2400 followed by date separators → Thai Buddhist Era → language_code: "th"
- A 2 or 3 digit year followed by date separators, no other context → Minguo/ROC calendar → language_code: "zh"
- A 4-digit year between 1300 and 1499 followed by date separators → Solar Hijri calendar → language_code: "fa"
- Japanese era name prefix (明治/大正/昭和/平成/令和) → language_code: "ja", field_type: "date_of_birth"
- Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) in a date pattern → language_code: "ar"

Identifier rules:
- Short alphanumeric strings (6–20 chars, no spaces, may contain hyphens) → likely passport_no or id_no
- Starts with 2-letter country code followed by digits (e.g. FR, GB, SA) → registration_no or tax_id
- Contains @ symbol → email
- Purely numeric string in an Arabic or Asian script context → id_no
- IBAN pattern (2 letters + 2 digits + up to 30 alphanumeric) → iban

Financial value rules:
- Contains △, ▲, or full-width parentheses （） around a number → total_assets or net_assets
- Number with European format (period thousands, comma decimal: 1.234,56) → total_assets
- Number with apostrophe thousands separator → total_assets
- Pure digit string with currency symbol (¥, €, £, $, ﷼, ₪) → share_capital

Language hint rule:
- If the user message starts with "Language hint provided by analyst:", extract the language code that follows and treat it as authoritative for language_code. Use it to resolve calendar system ambiguity — e.g. hint "zh" + short numeric date → Minguo/ROC calendar; hint "th" → Thai Buddhist Era; hint "fa" → Solar Hijri.

Examples:
{_EXAMPLES}
"""

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _coerce_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, confidence))


# ── Regex / deterministic classifier ──────────────────────────────────────────

_EMAIL_RE    = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')
_IBAN_RE     = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9 ]{4,32}$')
_LEI_RE      = re.compile(r'^[A-Z0-9]{18}[0-9]{2}$')            # 20-char LEI
_DATE_ISO_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_DATE_COMPACT_RE = re.compile(r'^\d{8}$')                         # YYYYMMDD
_DATE_DOT_EU_RE  = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}$')     # DD.MM.YYYY
_DATE_SLASH_RE   = re.compile(r'^(\d{1,4})/(\d{1,2})/(\d{2,4})$')  # any slash date
_THAI_ERA_RE     = re.compile(r'พ\.ศ\.|พศ\.')
_KOREAN_DATE_RE  = re.compile(r'\d+년\s*\d+월\s*\d+일')
_JAPANESE_DATE_RE= re.compile(r'\d+年\d+月\d+日')
_HAN_DATE_RE     = re.compile(r'[〇一二三四五六七八九十百千]+年[〇一二三四五六七八九十百千]+月[〇一二三四五六七八九十百千]+日')
_HEBREW_MONTHS   = ('ניסן','אייר','סיוון','תמוז','אב','אלול',
                    'תשרי','חשון','כסלו','טבת','שבט','אדר')
_CURRENCY_RE = re.compile(
    r'^[¥€£\$﷼₪₩฿₺]'            # leading currency symbol
    r'|[\u0660-\u0669\uff10-\uff19]'  # Arabic-Indic / full-width digits
    r'|[△▲\uff08\uff09（）]'           # accounting notation
    r'|^\d[\d,.\' ]+$'               # plain number with separators only
)
_AKA_RE = re.compile(
    r'\b(?:also\s+known\s+as|known\s+as|a\.?k\.?a\.?|по\s+прозвищу'
    r'|γνωστός\s+ως|noto\s+come|detto|dite?)\b'
    r'|又名|별칭',
    re.IGNORECASE,
)


def _detect_language_from_script(text: str) -> str:
    """Return an ISO 639-1 code from the dominant Unicode script block."""
    thai = kana = hangul = cjk = arabic = hebrew = cyrillic = greek = fa = 0
    for ch in text:
        cp = ord(ch)
        if 0x0E00 <= cp <= 0x0E7F:
            thai += 1
        elif 0x3040 <= cp <= 0x30FF:          # Hiragana + Katakana
            kana += 1
        elif (0xAC00 <= cp <= 0xD7FF or 0x1100 <= cp <= 0x11FF
              or 0x3130 <= cp <= 0x318F):      # Hangul
            hangul += 1
        elif (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF
              or 0xF900 <= cp <= 0xFAFF):      # CJK Unified Ideographs
            cjk += 1
        elif 0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF:   # Arabic
            arabic += 1
        elif 0x0660 <= cp <= 0x0669 or 0x06F0 <= cp <= 0x06F9:   # Arabic-Indic digits
            arabic += 1
        elif 0x0590 <= cp <= 0x05FF:           # Hebrew
            hebrew += 1
        elif 0x0400 <= cp <= 0x04FF:           # Cyrillic
            cyrillic += 1
        elif 0x0370 <= cp <= 0x03FF or 0x1F00 <= cp <= 0x1FFF:   # Greek
            greek += 1
    if thai:     return "th"
    if hangul:   return "ko"
    if kana:     return "ja"
    if cjk:      return "zh"   # CJK without kana → Chinese (not Japanese)
    if arabic:   return "ar"
    if hebrew:   return "he"
    if cyrillic: return "ru"
    if greek:    return "el"
    return "en"


def detect_field_type_regex(text: str, language_hint: str = "") -> tuple[str, float, str]:
    """Deterministic field-type detector.

    Covers structural patterns (email, IBAN, LEI, dates, currency amounts,
    AKA prose) and uses Unicode script detection for language. Falls back to
    ``person_name`` with low confidence for unrecognised inputs.

    Returns:
        (field_type, confidence, language_code)
    """
    t = (text or "").strip()
    if not t:
        return "person_name", 0.5, language_hint or "en"

    lang = language_hint or _detect_language_from_script(t)

    # 1. Email
    if _EMAIL_RE.search(t):
        return "email", 0.99, "en"

    # 2. IBAN — 2 uppercase letters + 2 digits + 4-32 alphanum, min 15 chars
    compact = t.replace(" ", "")
    if (len(compact) >= 15 and _IBAN_RE.match(compact.upper())
            and compact[:2].isalpha() and compact[2:4].isdigit()):
        return "iban", 0.99, "en"

    # 3. LEI — 20 chars uppercase alphanumeric, last 2 digits
    if len(compact) == 20 and _LEI_RE.match(compact.upper()):
        return "lei_code", 0.95, "en"

    # 4. AKA prose connector → alias (checked before long-sentence prose)
    if _AKA_RE.search(t):
        return "alias", 0.88, lang

    # 5. Long prose sentence → free_text
    #    Heuristic: >8 whitespace-separated tokens AND contains end-punctuation
    #    or Arabic/Japanese/Chinese prose marker
    tokens = t.split()
    has_prose_punct = bool(re.search(r'[.!?،。、！？…]', t))
    if len(tokens) > 8 and (has_prose_punct or lang in ("ar", "ja", "zh", "ko")):
        return "free_text", 0.75, lang

    # 6. Thai era label (year-only Buddhist Era)
    if _THAI_ERA_RE.search(t):
        return "issue_date", 0.92, "th"

    # 7. Korean date (year/month/day labels)
    if _KOREAN_DATE_RE.search(t):
        return "date_of_birth", 0.92, "ko"

    # 8. Japanese/Chinese Han numeral date
    if _JAPANESE_DATE_RE.search(t) or _HAN_DATE_RE.search(t):
        return "date_of_birth", 0.92, lang

    # 9. Hebrew spelled-out month → date
    if any(m in t for m in _HEBREW_MONTHS):
        return "date_of_birth", 0.88, "he"

    # 10. ISO date YYYY-MM-DD
    if _DATE_ISO_RE.match(t):
        return "date_of_birth", 0.93, lang

    # 11. Compact 8-digit date YYYYMMDD
    if _DATE_COMPACT_RE.match(t) and 19000101 <= int(t) <= 20991231:
        return "date_of_birth", 0.88, lang

    # 12. European dot date DD.MM.YYYY
    if _DATE_DOT_EU_RE.match(t):
        return "date_of_birth", 0.90, lang

    # 13. Slash-separated date — classify by year magnitude
    m = _DATE_SLASH_RE.match(t)
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        # Thai Buddhist: last component 2400–2700
        if 2400 <= c <= 2800:
            return "date_of_birth", 0.90, "th"
        # Solar Hijri: first component 1300–1499
        if 1300 <= a <= 1499:
            return "date_of_birth", 0.88, "fa"
        # Minguo: first component 50–200 (years since 1912)
        if 50 <= a <= 200:
            return "date_of_birth", 0.85, "zh"
        return "date_of_birth", 0.85, lang

    # 14. Arabic-Indic slash date (digits in Arabic-Indic range)
    ar_indic_slash = re.match(
        r'^[\u0660-\u0669]{1,4}[/\u060C][\u0660-\u0669]{1,2}[/\u060C][\u0660-\u0669]{2,4}$',
        t,
    )
    if ar_indic_slash:
        return "date_of_birth", 0.88, "ar"

    # 15. Currency / financial amount
    if _CURRENCY_RE.match(t) and re.search(r'\d', t):
        # Plain number string with only digits + separators → share_capital
        if re.match(r'^[\d\s,.\u0660-\u0669\uff10-\uff19\u066c\']+$', t):
            return "share_capital", 0.82, lang
        return "share_capital", 0.82, lang

    # 16. Default — unstructured / name-like
    return "person_name", 0.50, lang


# ── LLM classifier (GPT-4o-mini) ──────────────────────────────────────────────

_LLM_CACHE: dict[str, tuple[str, float, str]] = {}


def _detect_field_type_llm(text: str, language_hint: str = "") -> tuple[str, float, str]:
    """Classify pasted text with GPT-4o-mini.

    Args:
        text: The text to classify.
        language_hint: Optional ISO 639-1 code provided by the analyst. When
            supplied it is injected into the user message so the model treats
            it as authoritative for language_code and calendar disambiguation.

    Returns:
        (field_type, confidence, language_code)

    On any error, returns a safe fallback so processing can continue.
    """
    # SHA-256 cache — avoids re-paying latency on repeated inputs across a run
    cache_key = hashlib.sha256(f"{text}\x00{language_hint}".encode()).hexdigest()
    if cache_key in _LLM_CACHE:
        return _LLM_CACHE[cache_key]

    if language_hint:
        user_message = f"Language hint provided by analyst: {language_hint}\n\nText to classify:\n{(text or '')[:500]}"
    else:
        user_message = (text or "")[:500]

    try:
        log_event(
            "field_detector_started",
            {
                "text_length": len(text or ""),
                "text_preview": (text or "")[:180],
                "model": "gpt-4o-mini",
                "language_hint": language_hint or None,
            },
            source="backend",
        )
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=60,
            temperature=0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        content = response.choices[0].message.content or "{}"
        log_event("field_detector_raw_response", {"content": content}, source="backend")
        parsed = json.loads(content)

        field_type = parsed.get("field_type", "unstructured_text")
        detected_language = parsed.get("language_code", "en")
        confidence = _coerce_confidence(parsed.get("confidence", 0.5))

        if field_type not in FIELD_TYPES:
            field_type = "unstructured_text"
        if detected_language not in LANGUAGE_CODES:
            detected_language = "en"

        log_event(
            "field_detector_completed",
            {
                "field_type": field_type,
                "detected_language": detected_language,
                "confidence": confidence,
            },
            source="backend",
        )

        result: tuple[str, float, str] = (field_type, confidence, detected_language)
        _LLM_CACHE[cache_key] = result
        return result
    except Exception as e:
        logger.error(f"Field type detection failed: {e}", exc_info=True)
        log_event("field_detector_error", {"error": str(e)}, source="backend")
        return "unstructured_text", 0.5, "en"


def detect_field_type(text: str, language_hint: str = "") -> tuple[str, float, str]:
    """Dispatch to regex or LLM classifier based on ``CLASSIFIER_MODE`` env var.

    Set ``CLASSIFIER_MODE=llm`` in ``.env`` to use GPT-4o-mini.
    The default (``CLASSIFIER_MODE=regex``) uses the deterministic regex
    detector — fully reproducible, zero latency, zero cost.

    Returns:
        (field_type, confidence, language_code)
    """
    mode = os.environ.get("CLASSIFIER_MODE", "regex").lower()
    if mode == "llm":
        return _detect_field_type_llm(text, language_hint)
    return detect_field_type_regex(text, language_hint)
