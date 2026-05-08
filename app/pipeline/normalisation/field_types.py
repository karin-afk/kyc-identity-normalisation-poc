"""Field type classifications for the KYC normalisation pipeline.

This module defines routing sets consumed by the normalisation router.
Do not rename `ProcessingMethod` labels once published because audit and
dashboard reporting rely on those stable values.
"""

# ---------------------------------------------------------------------------
# Strategy A -- Preserve (strict identifiers only)
# ---------------------------------------------------------------------------

PRESERVE_FIELDS: list[str] = [
	# Identity document identifiers
	"passport_no",
	"id_no",
	"id_number",
	"licence_no",
	"document_number",

	# Company identifiers
	"registration_no",
	"company_no",
	"commercial_registration_no",

	# Financial identifiers
	"reference_no",
	"tax_id",
	"vat_number",

	# Contact
	"email",
]

# Financial numeric fields are explicitly NOT preserved; Strategy B normalises
# representation (digit scripts, separators, signs) while preserving value.
FINANCIAL_NUMERIC_FIELDS: list[str] = [
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

# ---------------------------------------------------------------------------
# Strategy B -- Calendar and numeric rules
# ---------------------------------------------------------------------------

NUMERIC_FIELDS: list[str] = [
	"date_of_birth",
	"birth_date",
	"date",
	"issue_date",
	"expiry_date",
	"incorporation_date",
	"document_date",
	"registry_date",
	"financial_period",
]

# ---------------------------------------------------------------------------
# Strategy C -- Vocabulary lookup
# ---------------------------------------------------------------------------

VOCABULARY_FIELDS: list[str] = [
	"legal_form",
	"status",
	"role",
	"designation",
	"share_class",
	"capital_change_type",
	"relationship_classification",
	"industry_code",
	"document_type",
]

# ---------------------------------------------------------------------------
# Strategy D -- Geographic lookup
# ---------------------------------------------------------------------------

GEOGRAPHIC_FIELDS: list[str] = [
	"nationality",
	"country",
	"country_of_residence",
	"place_of_birth",
	"city",
]

# ---------------------------------------------------------------------------
# Strategy E -- Verified repository
# ---------------------------------------------------------------------------

REPOSITORY_CHECKED_FIELDS: list[str] = [
	"full_name",
	"person_name",
	"alias",
	"director_name",
	"officer_name",
	"shareholder_name",
	"parent_name_father",
	"parent_name_mother",
	"entity_name",
	"company_name",
	"issuing_authority",
	"address",
	"registered_address",
	"mailing_address",
	"shareholder_address",
	"office_address",
	"locality_information",
]

# ---------------------------------------------------------------------------
# Strategy F -- Transliteration libraries
# ---------------------------------------------------------------------------

NAME_FIELDS: list[str] = [
	"full_name",
	"person_name",
	"alias",
	"director_name",
	"officer_name",
	"shareholder_name",
	"parent_name_father",
	"parent_name_mother",
	"entity_name",
	"company_name",
	"issuing_authority",
]

# ---------------------------------------------------------------------------
# Strategy G -- Character mapping
# ---------------------------------------------------------------------------

ADDRESS_FIELDS: list[str] = [
	"address",
	"registered_address",
	"mailing_address",
	"shareholder_address",
	"office_address",
]

# ---------------------------------------------------------------------------
# Strategy H -- Azure Translator NMT
# ---------------------------------------------------------------------------

PROSE_FIELDS: list[str] = [
	"nature_of_business",
	"business_purpose",
	"accounting_policies",
	"locality_information",
	"capital_changes_narrative",
	"unstructured_text",
]


class ProcessingMethod:
	"""Stable processing labels written to result payloads and audit logs."""

	PRESERVE = "PRESERVE"
	CALENDAR = "CALENDAR"
	NUMERIC = "NUMERIC"
	VOCABULARY = "VOCABULARY"
	GEOGRAPHIC = "GEOGRAPHIC"
	REPOSITORY = "REPOSITORY"
	TRANSLITERATION = "TRANSLITERATION"
	CHARACTER_MAP = "CHARACTER_MAP"
	NMT = "NMT"
	NATIVE_SPEAKER = "NATIVE_SPEAKER"
	LLM = "LLM"
	UNRESOLVED = "UNRESOLVED"
	FALLBACK = "FALLBACK"


DEFAULT_OCR_CONFIDENCE_THRESHOLD: float = 0.85

STRATEGY_CONFIDENCE: dict[str, float] = {
	ProcessingMethod.PRESERVE: 1.0,
	ProcessingMethod.CALENDAR: 0.95,
	ProcessingMethod.NUMERIC: 0.95,
	ProcessingMethod.VOCABULARY: 1.0,
	ProcessingMethod.GEOGRAPHIC: 1.0,
	ProcessingMethod.REPOSITORY: 1.0,
	ProcessingMethod.TRANSLITERATION: 0.90,
	ProcessingMethod.CHARACTER_MAP: 0.95,
	ProcessingMethod.NMT: 0.80,
	ProcessingMethod.NATIVE_SPEAKER: 1.0,
	ProcessingMethod.LLM: 0.75,
	ProcessingMethod.UNRESOLVED: 0.0,
	ProcessingMethod.FALLBACK: 0.50,
}
