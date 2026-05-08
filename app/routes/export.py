"""
Export routes - placeholder.
Full implementation in Epic 08.
"""

from flask import Blueprint

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/", methods=["GET"])
def index():
    """Export endpoint - placeholder."""
    return "Export - not yet implemented", 200
