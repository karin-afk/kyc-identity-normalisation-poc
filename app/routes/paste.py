"""Paste tab routes for sentence normalisation UI."""

from flask import Blueprint, render_template, request

paste_bp = Blueprint("paste", __name__, url_prefix="/paste")


@paste_bp.route("/", methods=["GET"])
def index():
    """Paste tool page."""
    return render_template("paste_sentence.html")


@paste_bp.route("/translate", methods=["POST"])
def translate():
    """Translate/normalise pasted text and return an HTMX partial."""
    try:
        text = request.form.get("original_text", request.form.get("text", "")).strip()
        field_type = request.form.get("field_type", "auto")
        language = request.form.get("language", "")
        detected_field_type = None
        field_type_confidence = None

        if not text:
            return '<p class="error-inline">Error: text is required.</p>', 400
        if len(text) > 2000:
            return '<p class="error-inline">Error: text exceeds 2,000 characters.</p>', 400

        if field_type == "auto":
            from app.pipeline.normalisation.field_type_detector import detect_field_type

            detected_field_type, field_type_confidence = detect_field_type(text, language)
            field_type = detected_field_type

        try:
            from app.pipeline.orchestrator import process_field_row

            result = process_field_row({"original_text": text, "field_type": field_type, "language": language})
            if detected_field_type is not None:
                result["detected_field_type"] = detected_field_type
                result["field_type_confidence"] = field_type_confidence

            return render_template(
                "partials/paste_result.html",
                result=result,
                original=text,
                field_type=field_type,
                detected_field_type=detected_field_type,
                field_type_confidence=field_type_confidence,
            )
        except (ImportError, NotImplementedError):
            return render_template(
                "partials/not_implemented.html",
                feature="Normalisation router",
            ), 200
    except Exception as exc:
        return f'<p class="error-inline">Error: {exc}</p>', 400
