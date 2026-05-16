"""Pipeline orchestrator (minimal): route one field and stub document path."""

from app.utils.session_trace import log_event


def process_field_row(row: dict) -> dict:
	"""Process one pre-extracted field through the normalisation router."""
	from app.pipeline.normalisation.router import route_field

	log_event(
		"orchestrator_process_field_row_started",
		{
			"incoming": {
				"original_text": row.get("original_text", "")[:180],
				"field_type": row.get("field_type", ""),
				"language": row.get("language", ""),
				"country": row.get("country", ""),
			},
		},
		source="backend",
	)

	row = {
		"original_text": row.get("original_text", ""),
		"field_type": row.get("field_type", ""),
		"language": row.get("language", ""),
		"country": row.get("country", ""),
	}
	result = route_field(row)
	log_event(
		"orchestrator_process_field_row_completed",
		{
			"processing_method": result.get("processing_method"),
			"confidence": result.get("confidence"),
			"review_required": result.get("review_required"),
			"normalised_form": result.get("normalised_form"),
		},
		source="backend",
	)
	return result


def process_document_file(file_path: str, doc_type: str, language: str) -> list[dict]:
	"""Stub document pipeline until document extraction epic is implemented."""
	log_event(
		"orchestrator_process_document_file_called",
		{"file_path": file_path, "doc_type": doc_type, "language": language},
		source="backend",
	)
	raise NotImplementedError(
		"Document processing pipeline not yet implemented (Epic 11). "
		"The UI will show a 'not yet available' notice."
	)
