"""Frontend UI epic integration tests for routes, nav, and HTMX fallbacks."""

from io import BytesIO

import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app("testing")


@pytest.fixture()
def client(app):
    return app.test_client()


def test_tab_pages_return_200(client) -> None:
    for path in ("/upload/", "/paste/", "/review/"):
        response = client.get(path)
        assert response.status_code == 200


def test_active_tab_changes_by_route(client) -> None:
    upload_html = client.get("/upload/").get_data(as_text=True)
    paste_html = client.get("/paste/").get_data(as_text=True)

    assert "Document</a>" in upload_html
    assert "tab tab-active\" href=\"/upload/\"" in upload_html
    assert "tab tab-active\" href=\"/paste/\"" in paste_html


def test_review_tab_hidden_when_context_flag_false() -> None:
    app = create_app("testing")

    @app.context_processor
    def _force_non_native_user():
        return {"current_user_is_native_speaker": False}

    client = app.test_client()
    html = client.get("/upload/").get_data(as_text=True)
    assert "Review</a>" not in html


def test_upload_process_returns_not_implemented_partial(client) -> None:
    response = client.post(
        "/upload/process",
        data={
            "file": (BytesIO(b"demo"), "document.pdf"),
            "document_type": "Passport",
            "language": "ar",
        },
        content_type="multipart/form-data",
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "This feature is not yet available" in html


def test_paste_translate_returns_result_partial(client, monkeypatch) -> None:
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(field_type_detector, "detect_field_type", lambda text, language="": ("passport_no", 0.93, "en"))

    response = client.post(
        "/paste/translate",
        data={"original_text": "TK1234567"},
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Language:" in html
    assert "Field type:" in html
    assert "Method:" in html
    assert "PRESERVE" in html


def test_paste_page_has_no_dropdowns(client) -> None:
    html = client.get("/paste/").get_data(as_text=True)
    assert "id=\"field-type\"" not in html
    assert "id=\"paste-language\"" not in html


def test_paste_translate_missing_key_degrades_gracefully(client, monkeypatch) -> None:
    from app.pipeline.normalisation import field_type_detector

    monkeypatch.setattr(
        field_type_detector,
        "detect_field_type",
        lambda text, language="": ("unstructured_text", 0.5, "en"),
    )

    response = client.post(
        "/paste/translate",
        data={"original_text": "random unknown content"},
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Awaiting native speaker review" in html


def test_review_detail_returns_not_implemented_partial(client) -> None:
    response = client.get("/review/1")
    assert response.status_code == 200
    assert "This feature is not yet available" in response.get_data(as_text=True)


def test_review_submit_returns_not_implemented_partial(client) -> None:
    response = client.post("/review/1/submit", data={"confirmed_form": "ABC"})
    assert response.status_code == 200
    assert "This feature is not yet available" in response.get_data(as_text=True)


def test_escalate_returns_not_implemented_partial(client) -> None:
    response = client.post(
        "/review/escalate-paste",
        data={"original_text": "株式会社", "field_type": "company_name", "normalised_suggestion": "KABUSHIKI KAISHA"},
    )
    assert response.status_code == 200
    assert "This feature is not yet available" in response.get_data(as_text=True)


def test_export_endpoints_return_not_implemented_partial(client) -> None:
    csv_response = client.get("/export/csv")
    email_response = client.post("/export/email")

    assert csv_response.status_code == 200
    assert email_response.status_code == 200
    assert "This feature is not yet available" in csv_response.get_data(as_text=True)
    assert "This feature is not yet available" in email_response.get_data(as_text=True)
