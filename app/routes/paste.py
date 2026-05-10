"""Paste tab routes for sentence normalisation UI."""

from flask import Blueprint, render_template, request

from app.utils.session_trace import log_event

paste_bp = Blueprint("paste", __name__, url_prefix="/paste")

_LANGUAGE_LABELS = {
    "ar": "Arabic",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fa": "Farsi / Persian",
    "fr": "French",
    "he": "Hebrew",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "zh": "Chinese",
}


@paste_bp.route("/", methods=["GET"])
def index():
    """Paste tool page."""
    log_event("paste_page_opened", {"path": request.path}, source="frontend")
    return render_template("paste_sentence.html")


@paste_bp.route("/translate", methods=["POST"])
def translate():
    """Translate/normalise pasted text and return an HTMX partial."""
    try:
        text = request.form.get("original_text", request.form.get("text", "")).strip()
        language_hint = request.form.get("language_hint", "").strip()
        log_event(
            "paste_translate_received",
            {
                "text_length": len(text),
                "text_preview": text[:120],
                "language_hint": language_hint or None,
            },
            source="backend",
        )

        if not text:
            log_event("paste_translate_rejected", {"reason": "empty_text"}, source="backend")
            return '<p class="notice notice-flag">Please enter some text.</p>', 400
        if len(text) > 2000:
            log_event("paste_translate_rejected", {"reason": "text_too_long", "text_length": len(text)}, source="backend")
            return '<p class="notice notice-flag">Text exceeds 2,000 characters. Please upload as a file instead.</p>', 400

        from app.pipeline.normalisation.field_type_detector import detect_field_type

        field_type, classification_confidence, language = detect_field_type(text, language_hint=language_hint)
        log_event(
            "field_type_detected",
            {
                "field_type": field_type,
                "language": language,
                "classification_confidence": classification_confidence,
            },
            source="backend",
        )

        try:
            from app.pipeline.orchestrator import process_field_row

            result = process_field_row({"original_text": text, "field_type": field_type, "language": language})
            result["detected_field_type"] = field_type
            result["detected_language"] = language
            result["detected_language_label"] = _LANGUAGE_LABELS.get(language, language)
            result["classification_confidence"] = classification_confidence
            log_event(
                "paste_translate_completed",
                {
                    "processing_method": result.get("processing_method"),
                    "normalised_form": result.get("normalised_form"),
                    "review_required": result.get("review_required"),
                },
                source="backend",
            )

            return render_template(
                "partials/paste_result.html",
                result=result,
                original=text,
                field_type=field_type,
            )
        except (ImportError, NotImplementedError):
            log_event("paste_translate_not_implemented", {"feature": "Normalisation router"}, source="backend")
            return render_template(
                "partials/not_implemented.html",
                feature="Normalisation router",
            ), 200
    except Exception as exc:
        log_event("paste_translate_error", {"error": str(exc)}, source="backend")
        return f'<p class="error-inline">Error: {exc}</p>', 400
