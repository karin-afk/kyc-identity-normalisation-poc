"""Review queue routes for human-in-the-loop workflows."""

from datetime import datetime

from flask import Blueprint, abort, render_template, request

from app.extensions import db

review_bp = Blueprint("review", __name__, url_prefix="/review")


@review_bp.route("/", methods=["GET"])
def index():
    """Render pending review tasks with graceful fallback when model unavailable."""
    try:
        from app.models.review import ReviewTask

        tasks = (
            ReviewTask.query.filter_by(status="pending")
            .order_by(ReviewTask.assigned_at.asc())
            .all()
        )
        return render_template("review.html", tasks=tasks)
    except Exception:
        return render_template("review.html", tasks=[])


@review_bp.route("/<int:task_id>", methods=["GET"])
def task_detail(task_id: int):
    """Render a single review task page or a not-implemented notice."""
    try:
        from app.models.review import ReviewTask

        task = ReviewTask.query.get(task_id)
        if task is None:
            abort(404)
        return render_template("review_task.html", task=task)
    except (ImportError, NotImplementedError):
        return render_template("partials/not_implemented.html", feature="Review task detail model (Epic 07)"), 200
    except Exception as exc:
        return f'<p class="error-inline">Error: {exc}</p>', 400


@review_bp.route("/<int:task_id>/submit", methods=["POST"])
def submit(task_id: int):
    """Persist review confirmation and attempt repository write."""
    try:
        from app.models.review import ReviewTask

        task = ReviewTask.query.get(task_id)
        if task is None:
            abort(404)

        confirmed_form = request.form.get("confirmed_form", "").strip().upper()
        variants = [
            v.strip()
            for v in request.form.get("allowed_variants", "").split(",")
            if v.strip()
        ]

        task.confirmed_form = confirmed_form
        task.confirmed_variants = variants
        suggested = (task.suggested_form or "").strip().upper() if hasattr(task, "suggested_form") else ""
        task.status = "approved" if confirmed_form == suggested and suggested else "corrected"
        task.reviewed_at = datetime.utcnow()

        repo_message = "Written to verified repository."
        try:
            from app.pipeline.normalisation.repository_lookup import RepositoryLookupService

            repo = RepositoryLookupService()
            repo.store_verified(
                task.original_text,
                task.language_code,
                task.field_type,
                confirmed_form,
                variants,
                processing_method=("LLM" if suggested else "UNRESOLVED"),
                verified_by_user_id=1,
            )
        except Exception:
            repo_message = "Repository write pending."

        db.session.commit()
        return render_template("partials/review_submitted.html", task=task, repo_message=repo_message)
    except (ImportError, NotImplementedError):
        return render_template("partials/not_implemented.html", feature="Review submission workflow (Epic 07)"), 200
    except Exception as exc:
        db.session.rollback()
        return f'<p class="error-inline">Error: {exc}</p>', 400


@review_bp.route("/escalate-paste", methods=["POST"])
def escalate_paste():
    """Create a review task from sentence-tab escalation."""
    try:
        from app.models.review import ReviewTask

        task = ReviewTask(
            original_text=request.form.get("original_text", ""),
            field_type=request.form.get("field_type", "other"),
            language_code=request.form.get("language", ""),
            suggested_form=request.form.get("normalised_suggestion", ""),
            status="pending",
            assigned_to=None,
        )
        db.session.add(task)
        db.session.commit()
        return '<p class="meta">Escalated to review queue.</p>', 200
    except (ImportError, NotImplementedError):
        return render_template("partials/not_implemented.html", feature="Review queue model (Epic 07)"), 200
    except Exception as exc:
        db.session.rollback()
        return f'<p class="error-inline">Error: {exc}</p>', 400
