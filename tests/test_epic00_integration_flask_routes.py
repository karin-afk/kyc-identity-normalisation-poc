"""Integration tests for Flask route placeholders in Epic 00."""

import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app("testing")


@pytest.fixture()
def client(app):
    return app.test_client()


def test_root_redirects_to_upload(client) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 308)
    assert "/upload/" in response.headers["Location"]


def test_upload_route_returns_200(client) -> None:
    response = client.get("/upload/")
    assert response.status_code == 200


def test_paste_route_returns_200(client) -> None:
    response = client.get("/paste/")
    assert response.status_code == 200


def test_review_route_returns_200(client) -> None:
    response = client.get("/review/")
    assert response.status_code == 200


def test_admin_route_returns_200(client) -> None:
    response = client.get("/admin/")
    assert response.status_code == 200


def test_export_route_returns_200(client) -> None:
    response = client.get("/export/")
    assert response.status_code == 200
