"""Normalisation router (minimal): Strategy A plus unresolved fallback."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from app.utils.session_trace import log_event

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
	log_event(
		"router_started",
		{
			"field_type": field_type,
			"language": language,
			"country": country,
			"text_preview": text[:180],
		},
		source="backend",
	)

	if not field_type:
		log_event("router_unresolved", {"reason": "missing_field_type"}, source="backend")
		return _unresolved(text, field_type, language, reason="Missing field_type")

	result = _try_strategy_b(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "B", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_c(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "C", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_a(text, field_type)
	if result:
		log_event("router_selected_strategy", {"strategy": "A", "method": result.get("processing_method")}, source="backend")
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
			log_event("router_selected_strategy", {"strategy": "I", "method": result.get("processing_method")}, source="backend")
			return result

	log_event("router_unresolved", {"reason": "all_strategies_missed", "field_type": field_type, "language": language}, source="backend")
	return _unresolved(text, field_type, language)


def _try_strategy_a(text: str, field_type: str) -> dict | None:
	"""Call preserve logic from src rules engine and normalize method label."""
	if field_type not in PRESERVE_FIELDS:
		log_event("strategy_a_skipped", {"reason": "field_not_in_preserve", "field_type": field_type}, source="backend")
		return None

	try:
		from pipeline.rules_engine import apply_rules

		result = apply_rules(field_type, text)
		if result:
			result["processing_method"] = "PRESERVE"
			log_event("strategy_a_hit", {"field_type": field_type}, source="backend")
			return result
	except Exception:
		log_event("strategy_a_error", {"field_type": field_type}, source="backend")
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
			log_event("strategy_b_hit", {"variant": "calendar", "field_type": field_type}, source="backend")
			return cal

		num = apply_numeric_rules(field_type, text, language=language, country=country)
		if num:
			log_event("strategy_b_hit", {"variant": "numeric", "field_type": field_type}, source="backend")
			return num
	except Exception:
		log_event("strategy_b_error", {"field_type": field_type}, source="backend")
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

		result = service.lookup(field_type, text, language=language, country=country)
		if result:
			log_event("strategy_c_hit", {"field_type": field_type, "language": language}, source="backend")
		else:
			log_event("strategy_c_miss", {"field_type": field_type, "language": language, "text_preview": text[:180]}, source="backend")
		return result
	except Exception:
		log_event("strategy_c_error", {"field_type": field_type, "language": language}, source="backend")
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
