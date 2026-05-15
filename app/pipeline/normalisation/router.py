"""Normalisation router (minimal): Strategy A plus unresolved fallback."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from app.utils.session_trace import log_event

SRC_DIR = Path(__file__).resolve().parents[3] / "src"
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))


# ── T3-3: Legacy field-name aliases → canonical names ─────────────────────────
# Older extracts and upstream systems sometimes use different names for the same
# concept. Canonicalise at the router boundary so every strategy sees a single
# consistent name.
_FIELD_TYPE_ALIASES: dict[str, str] = {
	# Identifier variants
	"id_card_no":          "id_number",
	"national_id_no":      "id_number",
	# Name variants — all route like person_name
	"given_name":          "person_name",
	"first_name":          "person_name",
	"family_name":         "person_name",
	"last_name":           "person_name",
	"full_name":           "person_name",
}


def _canonicalise_field_type(field_type: str) -> str:
	"""Map legacy field-type names to their canonical equivalent."""
	return _FIELD_TYPE_ALIASES.get(field_type, field_type)


# Identifiers and codes — passed through verbatim (Strategy A)
PRESERVE_FIELDS = [
	"passport_no",
	"id_no",
	"id_number",
	"iban",
	"email",
	"registration_no",
	"company_no",
	"commercial_registration_no",
	"reference_no",
	"tax_id",
	"vat_number",
	"document_number",
	"licence_no",
]

# Financial aggregates — numeric normalisation via Strategy B
# (share_capital, total_assets, etc. removed from PRESERVE so B can handle them)
# FINANCIAL_NUMERIC_FIELDS is defined in calendar_rules.py and checked there.


def route_field(row: dict) -> dict:
	"""Route one field through strategies A-I, currently resolving Strategy A only."""
	text = row.get("original_text", "")
	field_type = _canonicalise_field_type(row.get("field_type", ""))
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

	result = _try_strategy_a(text, field_type)
	if result:
		log_event("router_selected_strategy", {"strategy": "A", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_b(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "B", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_c(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "C", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_g(text, field_type, language)
	if result:
		log_event("router_selected_strategy", {"strategy": "G", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_d(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "D", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_f(text, field_type, language, country)
	if result:
		log_event("router_selected_strategy", {"strategy": "F", "method": result.get("processing_method")}, source="backend")
		return result

	result = _try_strategy_h(text, field_type, language)
	if result:
		log_event("router_selected_strategy", {"strategy": "H", "method": result.get("processing_method")}, source="backend")
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


def _try_strategy_d(text: str, field_type: str, language: str, country: str) -> dict | None:
	"""Strategy D — GeoNames geographic lookup."""
	try:
		from app.pipeline.normalisation.geographic_lookup import lookup_geographic

		result = lookup_geographic(text, field_type, language=language, country=country)
		if result:
			log_event("strategy_d_hit", {"field_type": field_type, "language": language}, source="backend")
		else:
			log_event("strategy_d_miss", {"field_type": field_type, "language": language, "text_preview": text[:180]}, source="backend")
		return result
	except Exception as exc:
		log_event("strategy_d_error", {"field_type": field_type, "language": language, "error": str(exc)}, source="backend")
		return None


def _try_strategy_f(text: str, field_type: str, language: str,
					country: str = "") -> dict | None:
	"""Strategy F — Transliteration. Wraps src/pipeline/transliteration_engine."""
	try:
		from app.pipeline.normalisation.transliteration import apply_transliteration
		return apply_transliteration(text, language, field_type, country)
	except Exception:
		return None


def _try_strategy_g(text: str, field_type: str, language: str) -> dict | None:
	try:
		from app.pipeline.normalisation.character_map_normaliser import apply_character_map
		return apply_character_map(text, language, field_type)
	except Exception:
		return None


def _try_strategy_h(text: str, field_type: str, language: str) -> dict | None:
	"""Strategy H — Azure NMT for prose fields only."""
	try:
		from app.pipeline.normalisation.nmt_translator import apply_nmt
		return apply_nmt(text, field_type, language)
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
