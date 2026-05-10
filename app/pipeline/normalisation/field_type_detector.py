"""LLM-based field/language classifier for sentence normalisation."""

from __future__ import annotations

import json
import logging

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


def detect_field_type(text: str, language_hint: str = "") -> tuple[str, float, str]:
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

        return field_type, confidence, detected_language
    except Exception as e:
        logger.error(f"Field type detection failed: {e}", exc_info=True)
        log_event("field_detector_error", {"error": str(e)}, source="backend")
        return "unstructured_text", 0.5, "en"
