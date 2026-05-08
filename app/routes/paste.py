"""Paste tab routes for sentence normalisation UI."""

from flask import Blueprint, render_template, request

paste_bp = Blueprint("paste", __name__, url_prefix="/paste")


@paste_bp.route("/", methods=["GET"])
def index():
    """Paste tool page."""
    return render_template("paste.html")


@paste_bp.route("/translate", methods=["POST"])
def translate():
    """Translate/normalise pasted text and return an HTMX partial."""
    try:
        text = request.form.get("original_text", "")
        field_type = request.form.get("field_type", "other")
        language = request.form.get("language", "")

        if not text.strip():
            return '<p class="error-inline">Error: text is required.</p>', 400
        if len(text) > 2000:
            return '<p class="error-inline">Error: text exceeds 2,000 characters.</p>', 400

        try:
            from app.pipeline.normalisation.router import route_field

            result = route_field({"original_text": text, "field_type": field_type, "language": language})
            return render_template(
                "partials/paste_result.html",
                result=result,
                original=text,
                field_type=field_type,
            )
        except (ImportError, NotImplementedError):
            return render_template(
                "partials/not_implemented.html",
                feature="Normalisation router (Epic 10)",
            ), 200
    except Exception as exc:
        return f'<p class="error-inline">Error: {exc}</p>', 400
