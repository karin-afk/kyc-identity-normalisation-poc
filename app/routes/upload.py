"""Upload routes for document UI and HTMX processing endpoint."""

from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, render_template, request

from app.utils.session_trace import log_event

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")


@upload_bp.route("/", methods=["GET"])
def index():
    """Document upload form."""
    log_event("upload_page_opened", {"path": request.path}, source="frontend")
    return render_template("upload.html")


@upload_bp.route("/results/<int:document_id>", methods=["GET"])
def results(document_id: int):
    """Results view placeholder path retained for compatibility."""
    return f"Results for document {document_id} - not yet implemented", 200


@upload_bp.route("/process", methods=["POST"])
def process():
    """Receive uploaded document and return results partial via HTMX."""
    try:
        file = request.files.get("file")
        log_event(
            "upload_received",
            {
                "has_file": file is not None,
                "filename": file.filename if file is not None else "",
            },
            source="backend",
        )
        if file is None or file.filename is None or not file.filename:
            log_event("upload_rejected", {"reason": "missing_file"}, source="backend")
            return '<p class="error-inline">Error: file is required.</p>', 400

        suffix = Path(file.filename).suffix.lower()
        allowed = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".docx", ".txt"}
        if suffix not in allowed:
            log_event("upload_rejected", {"reason": "unsupported_file_type", "suffix": suffix}, source="backend")
            return '<p class="error-inline">Error: unsupported file type.</p>', 400

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 50 * 1024 * 1024:
            log_event("upload_rejected", {"reason": "file_too_large", "size_bytes": size}, source="backend")
            return '<p class="error-inline">Error: file exceeds 50 MB.</p>', 400

        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        save_path = upload_folder / f"{uuid4().hex}{suffix}"
        file.save(save_path)

        doc_type = request.form.get("document_type", "")
        language = request.form.get("language", "")
        log_event(
            "upload_metadata_collected",
            {
                "doc_type": doc_type,
                "language_hint": language,
                "size_bytes": size,
                "saved_path": str(save_path),
            },
            source="backend",
        )

        try:
            from app.pipeline.orchestrator import process_document_file

            data = process_document_file(str(save_path), doc_type, language)
            if isinstance(data, dict):
                results = data.get("results", [])
                detected_doc_type = data.get("document_type_detected", doc_type or "Auto-detect")
                detected_language = data.get("language_detected", language or "Auto-detect")
            else:
                results = data if isinstance(data, list) else []
                detected_doc_type = doc_type or "Auto-detect"
                detected_language = language or "Auto-detect"

            log_event(
                "upload_processing_completed",
                {
                    "result_count": len(results),
                    "detected_doc_type": detected_doc_type,
                    "detected_language": detected_language,
                },
                source="backend",
            )

            return render_template(
                "partials/upload_results.html",
                results=results,
                document_type_detected=detected_doc_type,
                language_detected=detected_language,
            )
        except (ImportError, NotImplementedError):
            log_event("upload_processing_not_implemented", {}, source="backend")
            return render_template(
                "partials/not_implemented.html",
                feature="Document processing pipeline (Epic 10)",
            ), 200
    except Exception as exc:
        log_event("upload_processing_error", {"error": str(exc)}, source="backend")
        return f'<p class="error-inline">Error: {exc}</p>', 400
