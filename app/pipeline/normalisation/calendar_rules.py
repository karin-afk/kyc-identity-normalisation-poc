"""Strategy B calendar and numeric normalisation rules."""

from __future__ import annotations

import re
from pathlib import Path

from convertdate import hebrew, persian

from .numeric_rules import (
	normalise_all_digits,
	normalise_parenthetical_negative,
)
from utils.calendar_utils import detect_and_convert_japanese_era, normalise_date_field

CALENDAR_DATE_FIELDS: set[str] = {
	"date_of_birth",
	"birth_date",
	"date",
	"issue_date",
	"expiry_date",
	"incorporation_date",
	"document_date",
	"registry_date",
	"financial_period",
}

FINANCIAL_NUMERIC_FIELDS: set[str] = {
	"number_of_shares",
	"voting_rights",
	"ownership_percentage",
	"share_capital",
	"number_of_issued_shares",
	"total_assets",
	"total_liabilities",
	"net_assets",
	"revenue",
	"expenses",
}

_HAS_DIGIT_RE = re.compile(r"\d")
# Matches any non-ASCII digit script: Arabic-Indic, extended Arabic-Indic, full-width, Thai, Devanagari
_NON_ASCII_DIGIT_RE = re.compile(
	r"[\u0660-\u0669\u06f0-\u06f9\uff10-\uff19\u0e50-\u0e59\u0966-\u096f]"
)
# Matches strings composed entirely of non-ASCII digits, ASCII digits, and common separators
_ALL_DIGIT_CONTENT_RE = re.compile(
	r"^[\u0660-\u0669\u06f0-\u06f9\uff10-\uff19\u0e50-\u0e59\u0966-\u096f\d\s,.\/\-]+$"
)
_THAI_DATE_RE = re.compile(r"^(\d{1,4})[\/\-.](\d{1,2})[\/\-.](\d{1,4})$")
_MINGUO_DATE_RE = re.compile(r"^(\d{2,3})[\/\-.](\d{1,2})[\/\-.](\d{1,2})$")
_SOLAR_HIJRI_RE = re.compile(r"^(1[34]\d{2})[\/\-.](\d{1,2})[\/\-.](\d{1,2})$")
_HEBREW_TISHREI_RE = re.compile(r"^(\d{1,2})\s+ב?תשרי\s+(\d{4})$")
_HEBREW_NUMERIC_RE = re.compile(r"^(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})$")

_CURRENCY_SYMBOLS = {
	"€": "EUR",
	"£": "GBP",
	"₪": "ILS",
	"$": "USD",
}


def apply_calendar_rules(
	field_type: str,
	text: str,
	language: str = "",
	country: str = "",
) -> dict | None:
	"""Apply Strategy B date normalisation for date-type fields only."""
	if field_type not in CALENDAR_DATE_FIELDS:
		return None

	raw_text = text or ""
	ascii_text = normalise_all_digits(raw_text.strip())
	lang = (language or "").lower()
	ctry = (country or "").upper()

	detected = _detect_calendar_and_convert(ascii_text, lang, ctry)
	if detected is None:
		fallback = normalise_date_field(ascii_text, language=lang)
		normalised = fallback.get("normalised", ascii_text)
		original_calendar = fallback.get("original_calendar", "unknown")
		review_required = bool(fallback.get("review_required", False))
		review_reason = fallback.get("review_reason")
	else:
		normalised = detected.get("normalised_form", ascii_text)
		original_calendar = detected.get("original_calendar", "unknown")
		review_required = bool(detected.get("review_required", False))
		review_reason = detected.get("review_reason")

	return {
		"original_text": raw_text,
		"normalised_form": normalised,
		"allowed_variants": [],
		"processing_method": "CALENDAR",
		"confidence": 0.95,
		"review_required": review_required,
		"review_reason": review_reason,
		"should_use_in_screening": True,
		"original_calendar": original_calendar,
	}


def apply_numeric_rules(
	field_type: str,
	text: str,
	language: str = "",
	country: str = "",
) -> dict | None:
	"""Apply Strategy B numeric normalisation for financial numeric fields.

	For fields whose type is unstructured_text (i.e. the LLM classifier could not
	identify a specific field type), also fires when the text consists entirely of
	non-ASCII digits and separators, converting the digit glyphs to ASCII without
	financial number formatting.
	"""
	if field_type not in FINANCIAL_NUMERIC_FIELDS:
		# Content-driven path: fire for unstructured_text when the value is pure
		# digit glyphs (e.g. Arabic-Indic digits pasted without a known field context).
		# Preserve fields (id_no, passport_no, etc.) never reach this because they
		# are not classified as unstructured_text by the field detector.
		if field_type != "unstructured_text":
			return None
		raw = (text or "").strip()
		if not raw or not (_NON_ASCII_DIGIT_RE.search(raw) and _ALL_DIGIT_CONTENT_RE.match(raw)):
			return None
		converted = normalise_all_digits(raw)
		return {
			"original_text": raw,
			"normalised_form": converted,
			"allowed_variants": [],
			"processing_method": "NUMERIC",
			"confidence": 0.9,
			"review_required": False,
			"review_reason": None,
			"should_use_in_screening": True,
			"original_calendar": None,
			"currency_code": "",
		}

	raw_text = text or ""
	if not raw_text.strip():
		return None

	lang = (language or "").lower()
	ctry = (country or "").upper()

	converted = normalise_all_digits(raw_text.strip())
	converted = normalise_parenthetical_negative(converted)
	amount, currency = _extract_currency(converted, language=lang, country=ctry)
	normalised = _normalise_number_text(amount)

	if not _HAS_DIGIT_RE.search(normalised):
		return None

	return {
		"original_text": raw_text,
		"normalised_form": normalised,
		"allowed_variants": [],
		"processing_method": "NUMERIC",
		"confidence": 0.95,
		"review_required": False,
		"review_reason": None,
		"should_use_in_screening": True,
		"original_calendar": None,
		"currency_code": currency,
	}


def _detect_calendar_and_convert(text: str, language: str, country: str) -> dict | None:
	"""Apply calendar detection priority rules and return first conversion hit."""
	if language == "ja":
		era = detect_and_convert_japanese_era(text)
		if era.get("era_detected"):
			return {
				"normalised_form": era.get("normalised", text),
				"original_calendar": "japanese_era",
				"review_required": bool(era.get("review_required", True)),
				"review_reason": era.get("review_reason"),
			}

	if language == "he":
		result = _detect_hebrew_date(text)
		if result:
			return result

	if language == "th" or country == "TH":
		result = _detect_thai_date(text)
		if result:
			return result

	if (language == "zh" and country == "TW") or country == "TW":
		result = _detect_minguo_date(text)
		if result:
			return result

	if language in ("fa", "ps") or country in ("IR", "AF"):
		result = _detect_solar_hijri_date(text)
		if result:
			return result

	return None


def _detect_thai_date(text: str) -> dict | None:
	"""Detect Thai Buddhist dates in numeric forms and convert to Gregorian."""
	match = _THAI_DATE_RE.match(text)
	if not match:
		return None

	a, b, c = int(match.group(1)), int(match.group(2)), int(match.group(3))
	# DD/MM/YYYY with BE year
	if 1 <= a <= 31 and 1 <= b <= 12 and 2400 <= c <= 2700:
		return {
			"normalised_form": f"{c - 543:04d}-{b:02d}-{a:02d}",
			"original_calendar": "thai_buddhist",
			"review_required": False,
			"review_reason": None,
		}
	# YYYY/MM/DD with BE year
	if 2400 <= a <= 2700 and 1 <= b <= 12 and 1 <= c <= 31:
		return {
			"normalised_form": f"{a - 543:04d}-{b:02d}-{c:02d}",
			"original_calendar": "thai_buddhist",
			"review_required": False,
			"review_reason": None,
		}
	return None


def _detect_minguo_date(text: str) -> dict | None:
	"""Detect Minguo date strings and convert to Gregorian."""
	match = _MINGUO_DATE_RE.match(text)
	if not match:
		return None

	year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
	if not (1 <= month <= 12 and 1 <= day <= 31):
		return None

	return {
		"normalised_form": f"{year + 1911:04d}-{month:02d}-{day:02d}",
		"original_calendar": "minguo",
		"review_required": False,
		"review_reason": None,
	}


def _detect_solar_hijri_date(text: str) -> dict | None:
	"""Detect Solar Hijri date strings and convert with convertdate."""
	match = _SOLAR_HIJRI_RE.match(text)
	if not match:
		return None

	year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
	if not (1 <= month <= 12 and 1 <= day <= 31):
		return None

	g_year, g_month, g_day = persian.to_gregorian(year, month, day)
	return {
		"normalised_form": f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
		"original_calendar": "solar_hijri",
		"review_required": False,
		"review_reason": None,
	}


def _detect_hebrew_date(text: str) -> dict | None:
	"""Detect Hebrew date text and convert with convertdate."""
	match = _HEBREW_TISHREI_RE.match(text)
	if match:
		day, year = int(match.group(1)), int(match.group(2))
		g_year, g_month, g_day = hebrew.to_gregorian(year, 7, day)
		return {
			"normalised_form": f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
			"original_calendar": "hebrew",
			"review_required": False,
			"review_reason": None,
		}

	match = _HEBREW_NUMERIC_RE.match(text)
	if not match:
		return None

	year, civil_month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
	if not (1 <= civil_month <= 13 and 1 <= day <= 30):
		return None

	biblical_month = _hebrew_civil_to_biblical_month(year, civil_month)
	g_year, g_month, g_day = hebrew.to_gregorian(year, biblical_month, day)
	return {
		"normalised_form": f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
		"original_calendar": "hebrew",
		"review_required": False,
		"review_reason": None,
	}


def _hebrew_civil_to_biblical_month(year: int, civil_month: int) -> int:
	"""Map civil Hebrew month index (Tishrei=1) to convertdate month numbering."""
	leap = hebrew.leap(year)
	if leap:
		mapping = {1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 13: 6}
	else:
		mapping = {1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6}
	return mapping[civil_month]


def _extract_currency(text: str, language: str, country: str) -> tuple[str, str]:
	"""Extract currency symbol from text and resolve to ISO code."""
	working = text.strip()
	for symbol, code in _CURRENCY_SYMBOLS.items():
		if symbol in working:
			amount = working.replace(symbol, "").strip()
			return amount, code

	if "¥" in working:
		amount = working.replace("¥", "").strip()
		if country == "CN" or language == "zh":
			return amount, "CNY"
		return amount, "JPY"

	if "﷼" in working:
		amount = working.replace("﷼", "").strip()
		return amount, "SAR"

	return working, ""


def _normalise_number_text(text: str) -> str:
	"""Normalise separators to English numeric format without grouping."""
	working = text.strip().replace(" ", "").replace("'", "")

	negative = working.startswith("-")
	if negative:
		working = working[1:]

	last_comma = working.rfind(",")
	last_dot = working.rfind(".")

	if "," in working and "." in working:
		if last_comma > last_dot:
			working = working.replace(".", "")
			working = working.replace(",", ".")
		else:
			working = working.replace(",", "")
	elif "," in working:
		parts = working.split(",")
		if len(parts) == 2 and len(parts[1]) <= 2:
			working = f"{parts[0]}.{parts[1]}"
		else:
			working = "".join(parts)
	elif "." in working:
		parts = working.split(".")
		if len(parts) == 2 and len(parts[1]) <= 2:
			working = f"{parts[0]}.{parts[1]}"
		else:
			working = "".join(parts)

	if working.startswith("."):
		working = "0" + working

	if negative and not working.startswith("-"):
		working = "-" + working

	return working
