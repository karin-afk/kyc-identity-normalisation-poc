"""Export routes providing graceful fallback responses for frontend controls."""

from flask import Blueprint, render_template

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/", methods=["GET"])
def index():
    """Export endpoint placeholder."""
    return "Export - not yet implemented", 200


@export_bp.route("/csv", methods=["GET"])
def export_csv():
    """CSV export fallback partial used by HTMX controls."""
    return render_template("partials/not_implemented.html", feature="CSV export (Epic 08)"), 200


@export_bp.route("/email", methods=["POST"])
def export_email():
    """Email export fallback partial used by HTMX controls."""
    return render_template("partials/not_implemented.html", feature="Email export (Epic 08)"), 200
