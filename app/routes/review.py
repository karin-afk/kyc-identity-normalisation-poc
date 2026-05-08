"""
Review routes - placeholder.
Full implementation in Epic 07.
"""

from flask import Blueprint, render_template

review_bp = Blueprint("review", __name__, url_prefix="/review")


@review_bp.route("/", methods=["GET"])
def index():
    """Review queue - placeholder."""
    return render_template("review.html")
