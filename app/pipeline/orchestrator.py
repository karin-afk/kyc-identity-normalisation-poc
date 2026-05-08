"""Pipeline orchestrator (minimal): route one field and stub document path."""


def process_field_row(row: dict) -> dict:
	"""Process one pre-extracted field through the normalisation router."""
	from app.pipeline.normalisation.router import route_field

	row = {
		"original_text": row.get("original_text", ""),
		"field_type": row.get("field_type", ""),
		"language": row.get("language", ""),
		"country": row.get("country", ""),
	}
	return route_field(row)


def process_document_file(file_path: str, doc_type: str, language: str) -> list[dict]:
	"""Stub document pipeline until document extraction epic is implemented."""
	raise NotImplementedError(
		"Document processing pipeline not yet implemented (Epic 11). "
		"The UI will show a 'not yet available' notice."
	)
