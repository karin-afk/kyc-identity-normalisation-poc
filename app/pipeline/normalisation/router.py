"""Normalisation router (minimal): Strategy A plus unresolved fallback."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[3] / "src"
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))


PRESERVE_FIELDS = [
	"passport_no",
	"id_no",
	"id_number",
	"email",
	"registration_no",
	"company_no",
	"commercial_registration_no",
	"reference_no",
	"tax_id",
	"vat_number",
	"document_number",
	"licence_no",
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
]


def route_field(row: dict) -> dict:
	"""Route one field through strategies A-I, currently resolving Strategy A only."""
	text = row.get("original_text", "")
	field_type = row.get("field_type", "")
	language = row.get("language", "")
	country = row.get("country", "")

	if not field_type:
		return _unresolved(text, field_type, language, reason="Missing field_type")

	result = _try_strategy_b(text, field_type, language, country)
	if result:
		return result

	result = _try_strategy_c(text, field_type, language, country)
	if result:
		return result

	result = _try_strategy_a(text, field_type)
	if result:
		return result

	for strategy_letter, module_name in (
		("B", "calendar_rules"),
		("C", "vocabulary_lookup"),
		("D", "geographic_lookup"),
		("E", "repository_lookup"),
		("F", "transliteration"),
		("G", "character_map_normaliser"),
		("H", "nmt_translator"),
	):
		result = _try_stub(strategy_letter, module_name)
		if result:
			return result

	if os.environ.get("LLM_ENABLED", "false").lower() == "true":
		result = _try_stub("I", "llm_normalise")
		if result:
			return result

	return _unresolved(text, field_type, language)


def _try_strategy_a(text: str, field_type: str) -> dict | None:
	"""Call preserve logic from src rules engine and normalize method label."""
	if field_type not in PRESERVE_FIELDS:
		return None

	try:
		from pipeline.rules_engine import apply_rules

		result = apply_rules(field_type, text)
		if result:
			result["processing_method"] = "PRESERVE"
			return result
	except Exception:
		pass

	return {
		"original_text": text,
		"normalised_form": text,
		"allowed_variants": [],
		"processing_method": "PRESERVE",
		"confidence": 1.0,
		"review_required": False,
		"review_reason": None,
		"should_use_in_screening": True,
		"latin_transliteration": None,
		"analyst_english_rendering": text,
	}


def _try_strategy_b(text: str, field_type: str, language: str, country: str) -> dict | None:
	"""Apply Strategy B for calendar and financial numeric fields."""
	try:
		from app.pipeline.normalisation.calendar_rules import (
			apply_calendar_rules,
			apply_numeric_rules,
		)

		cal = apply_calendar_rules(field_type, text, language=language, country=country)
		if cal:
			return cal

		num = apply_numeric_rules(field_type, text, language=language, country=country)
		if num:
			return num
	except Exception:
		pass

	return None


def _try_strategy_c(text: str, field_type: str, language: str, country: str) -> dict | None:
	"""Apply Strategy C vocabulary lookup using app singleton service."""
	try:
		from flask import current_app

		service = getattr(current_app, "vocab_service", None)
		if service is None:
			from app.pipeline.normalisation.vocabulary_lookup import VocabularyLookupService
			from pathlib import Path

			tables_dir = Path(current_app.root_path).parent / "data" / "lookup_tables"
			service = VocabularyLookupService(tables_dir)

		return service.lookup(field_type, text, language=language, country=country)
	except Exception:
		return None


def _try_stub(strategy_letter: str, module_name: str) -> None:
	"""Placeholder for not-yet-implemented strategies."""
	return None


def _unresolved(
	text: str,
	field_type: str,
	language: str,
	reason: str | None = None,
) -> dict:
	"""Fallback result when no strategy resolves the field."""
	return {
		"original_text": text,
		"normalised_form": None,
		"allowed_variants": [],
		"processing_method": "UNRESOLVED",
		"confidence": 0.0,
		"review_required": True,
		"review_reason": reason
		or (
			f"No strategy resolved field_type='{field_type}' "
			f"language='{language}' - awaiting native speaker review"
		),
		"should_use_in_screening": False,
		"latin_transliteration": None,
		"analyst_english_rendering": None,
	}
