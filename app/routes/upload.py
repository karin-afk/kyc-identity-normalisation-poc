"""
Upload routes - placeholder.
Full implementation in Epic 08.
"""

from flask import Blueprint, render_template

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")


@upload_bp.route("/", methods=["GET"])
def index():
    """Document upload form - placeholder."""
    return render_template("upload.html")


@upload_bp.route("/results/<int:document_id>", methods=["GET"])
def results(document_id: int):
    """Results view - placeholder."""
    return f"Results for document {document_id} - not yet implemented", 200
