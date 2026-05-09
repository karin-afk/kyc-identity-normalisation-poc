"""Paste tab routes for sentence normalisation UI."""

from flask import Blueprint, render_template, request

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
    return render_template("paste_sentence.html")


@paste_bp.route("/translate", methods=["POST"])
def translate():
    """Translate/normalise pasted text and return an HTMX partial."""
    try:
        text = request.form.get("original_text", request.form.get("text", "")).strip()

        if not text:
            return '<p class="notice notice-flag">Please enter some text.</p>', 400
        if len(text) > 2000:
            return '<p class="notice notice-flag">Text exceeds 2,000 characters. Please upload as a file instead.</p>', 400

        from app.pipeline.normalisation.field_type_detector import detect_field_type

        field_type, classification_confidence, language = detect_field_type(text)

        try:
            from app.pipeline.orchestrator import process_field_row

            result = process_field_row({"original_text": text, "field_type": field_type, "language": language})
            result["detected_field_type"] = field_type
            result["detected_language"] = language
            result["detected_language_label"] = _LANGUAGE_LABELS.get(language, language)
            result["classification_confidence"] = classification_confidence

            return render_template(
                "partials/paste_result.html",
                result=result,
                original=text,
                field_type=field_type,
            )
        except (ImportError, NotImplementedError):
            return render_template(
                "partials/not_implemented.html",
                feature="Normalisation router",
            ), 200
    except Exception as exc:
        return f'<p class="error-inline">Error: {exc}</p>', 400
