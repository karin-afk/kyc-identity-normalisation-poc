"""
Admin routes - placeholder.
Full implementation in Epic 07.
"""

from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/", methods=["GET"])
def index():
    """Admin dashboard - placeholder."""
    return render_template("admin.html")
