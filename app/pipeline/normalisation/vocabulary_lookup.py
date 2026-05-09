"""Strategy C vocabulary lookup service."""

from __future__ import annotations

import json
from pathlib import Path

VOCABULARY_FIELDS: set[str] = {
	"legal_form",
	"status",
	"role",
	"designation",
	"share_class",
	"capital_change_type",
	"industry_code",
	"document_type",
}

ALLOWED_STATUS_VALUES = {
	"ACTIVE",
	"INACTIVE",
	"DISSOLVED",
	"SUSPENDED",
	"IN_LIQUIDATION",
	"STRUCK_OFF",
	"DORMANT",
}

ALLOWED_DOCUMENT_TYPE_LABELS = {
	"national_id",
	"drivers_licence",
	"passport",
	"company_registry_local",
	"company_registry_foreign",
	"business_registration",
	"aoa",
	"financial_statement",
	"shareholder_table",
	"unknown",
}


class VocabularyLookupService:
	"""In-memory JSON dictionary lookup service for Strategy C."""

	def __init__(self, tables_dir: Path):
		self.tables_dir = tables_dir
		self.legal_forms = self._load(tables_dir, "legal_forms.json")
		self.status_terms = self._load(tables_dir, "status_terms.json")
		self.role_titles = self._load(tables_dir, "role_titles.json")
		self.street_types = self._load(tables_dir, "street_types.json")
		self.industry_codes = self._load(tables_dir, "industry_codes.json")
		self.issuing_authorities = self._load(tables_dir, "issuing_authorities.json")
		self.share_classes = self._load(tables_dir, "share_classes.json")
		self.capital_changes = self._load(tables_dir, "capital_change_types.json")
		self.document_types = self._load(tables_dir, "document_type_labels.json")

	def lookup(self, field_type: str, text: str, language: str = "", country: str = "") -> dict | None:
		"""Route to strategy-specific vocabulary lookup."""
		if field_type not in VOCABULARY_FIELDS:
			return None

		if not text or not text.strip():
			return None

		result = None
		if field_type == "legal_form":
			result = self.lookup_legal_form(text, country)
		elif field_type == "status":
			result = self.lookup_status(text, language)
		elif field_type in ("role", "designation"):
			result = self.lookup_role(text, language)
		elif field_type == "share_class":
			result = self.lookup_share_class(text, language)
		elif field_type == "capital_change_type":
			result = self.lookup_capital_change(text, language)
		elif field_type == "industry_code":
			result = self.lookup_industry_code(text)
		elif field_type == "document_type":
			result = self.lookup_document_type(text, language)

		if result is None:
			return None

		result["original_text"] = text
		return result

	def lookup_legal_form(self, text: str, country: str) -> dict | None:
		"""Lookup legal form by country with suffix and full-string match."""
		needle = _norm(text)
		if not needle:
			return None

		candidate_countries = [country.upper()] if country else []
		if not candidate_countries:
			candidate_countries = list(self.legal_forms.keys())

		for cc in candidate_countries:
			table = self.legal_forms.get(cc)
			if not isinstance(table, dict):
				continue
			for key, canonical in table.items():
				k = _norm(key)
				if not k:
					continue
				if needle == k or needle.endswith(k):
					return self._build_result(canonical)
		return None

	def lookup_status(self, text: str, language: str) -> dict | None:
		"""Case-insensitive status lookup with en fallback."""
		return self._lookup_language_table(self.status_terms, text, language, fallback="en")

	def lookup_role(self, text: str, language: str) -> dict | None:
		"""Case-insensitive role lookup with punctuation trimming."""
		result = self._lookup_language_table(self.role_titles, text, language, fallback="en")
		if result is not None:
			return result
		cleaned = text.strip().rstrip(".,;:，。؛")
		if cleaned != text:
			return self._lookup_language_table(self.role_titles, cleaned, language, fallback="en")
		return None

	def lookup_street_type(self, token: str, language: str) -> str | None:
		"""Lookup single street token for address enrichment use."""
		if not token:
			return None
		lang = (language or "").lower()
		table = self.street_types.get(lang, {})
		if not isinstance(table, dict):
			return None
		return table.get(_norm(token))

	def lookup_industry_code(self, code: str, scheme: str = "NACE") -> dict | None:
		"""Lookup industry code by exact, parent, or child-prefix match."""
		if not code:
			return None
		needle = code.strip().upper()
		schemes = [scheme] if scheme in self.industry_codes else list(self.industry_codes.keys())
		for sch in schemes:
			table = self.industry_codes.get(sch, {})
			if not isinstance(table, dict):
				continue

			# Industry table keys are normalized to lowercase during load;
			# use an uppercase index for code-style matching.
			upper_index = {str(k).upper(): v for k, v in table.items()}
			if needle in upper_index:
				return self._build_result(upper_index[needle])

			best_parent_key = None
			for k in upper_index.keys():
				if needle.startswith(k):
					if best_parent_key is None or len(k) > len(best_parent_key):
						best_parent_key = k
			if best_parent_key is not None:
				return self._build_result(upper_index[best_parent_key])

			child_keys = sorted([k for k in upper_index.keys() if k.startswith(needle)])
			if child_keys:
				return self._build_result(upper_index[child_keys[0]])
		return None

	def lookup_document_type(self, text: str, language: str) -> dict | None:
		"""Case-insensitive document-type label lookup."""
		return self._lookup_language_table(self.document_types, text, language, fallback="en")

	def lookup_share_class(self, text: str, language: str) -> dict | None:
		"""Case-insensitive share-class lookup."""
		return self._lookup_language_table(self.share_classes, text, language, fallback="en")

	def lookup_capital_change(self, text: str, language: str) -> dict | None:
		"""Case-insensitive capital-change lookup."""
		return self._lookup_language_table(self.capital_changes, text, language, fallback="en")

	@staticmethod
	def _build_result(normalised_form: str) -> dict:
		return {
			"normalised_form": normalised_form,
			"allowed_variants": [],
			"processing_method": "VOCABULARY",
			"confidence": 1.0,
			"review_required": False,
			"review_reason": None,
			"should_use_in_screening": True,
		}

	@staticmethod
	def _load(tables_dir: Path, filename: str) -> dict:
		"""Load JSON table and normalise key casing for O(1) lookups."""
		file_path = tables_dir / filename
		if not file_path.exists():
			raise FileNotFoundError(f"Required lookup table missing: {file_path}")

		raw = json.loads(file_path.read_text(encoding="utf-8"))
		if not isinstance(raw, dict):
			raise ValueError(f"Lookup file must contain a JSON object: {file_path}")

		normalised: dict = {}
		for top_key, top_val in raw.items():
			if top_key.startswith("_"):
				continue
			if isinstance(top_val, dict):
				inner = {}
				for inner_key, inner_val in top_val.items():
					if inner_key.startswith("_"):
						continue
					inner[_norm(inner_key)] = str(inner_val).strip()
				normalised[str(top_key).strip()] = inner
			else:
				normalised[str(top_key).strip()] = top_val
		return normalised

	def _lookup_language_table(self, table_root: dict, text: str, language: str, fallback: str = "en") -> dict | None:
		needle = _norm(text)
		if not needle:
			return None
		lang = (language or "").lower()
		for candidate in [lang, fallback]:
			if not candidate:
				continue
			table = table_root.get(candidate)
			if isinstance(table, dict) and needle in table:
				return self._build_result(table[needle])
		return None


def _norm(value: str) -> str:
	return str(value).strip().lower()
