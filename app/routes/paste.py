"""
Paste routes - placeholder.
Full implementation in Epic 09.
"""

from flask import Blueprint, render_template

paste_bp = Blueprint("paste", __name__, url_prefix="/paste")


@paste_bp.route("/", methods=["GET"])
def index():
    """Paste tool - placeholder."""
    return render_template("paste.html")
