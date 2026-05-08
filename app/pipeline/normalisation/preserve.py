"""Strategy A: Preserve strict identifiers exactly as extracted.

This strategy applies only to strict identifiers defined in
`PRESERVE_FIELDS`. Values are returned byte-for-byte without any
normalisation, transliteration, or translation.
"""

from app.pipeline.normalisation.field_types import (
	PRESERVE_FIELDS,
	ProcessingMethod,
	STRATEGY_CONFIDENCE,
)


def apply_preserve(field_type: str, text: str) -> dict | None:
	"""Return preserve result for strict identifier fields.

	Args:
		field_type: KYC field type.
		text: Raw extracted text.

	Returns:
		Standard result payload for preserve fields, otherwise None so the
		router can continue to later strategies.
	"""
	if field_type not in PRESERVE_FIELDS:
		return None

	return {
		"original_text": text,
		"normalised_form": text,
		"allowed_variants": [],
		"processing_method": ProcessingMethod.PRESERVE,
		"confidence": STRATEGY_CONFIDENCE[ProcessingMethod.PRESERVE],
		"review_required": False,
		"review_reason": None,
		"should_use_in_screening": True,
	}
