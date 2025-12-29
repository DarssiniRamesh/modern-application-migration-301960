import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app_client() -> Generator[TestClient, None, None]:
    """
    Create a TestClient using a dedicated SQLite db file to isolate admin tests.
    We use a separate file name to avoid cross-test interference if run independently.
    """
    # Ensure deterministic secret and DB for this module too
    test_db = os.environ.get("DATABASE_URL")
    if not test_db:
        # default to a temp file in project data dir to allow table creation on startup
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        os.makedirs(data_dir, exist_ok=True)
        os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(data_dir, 'test_auth_admin.db')}"
    os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "TEST_SECRET_KEY_CHANGE_ME")

    from app.main import app  # noqa: WPS433

    with TestClient(app) as client:
        yield client


def admin_register(client: TestClient, username: str, password: str):
    return client.post("/admin/auth/register", json={"username": username, "password": password})


def admin_login(client: TestClient, username: str, password: str):
    return client.post("/admin/auth/login", json={"username": username, "password": password})


def admin_me(client: TestClient, token: str):
    return client.get("/admin/me", headers={"Authorization": f"Bearer {token}"})


def admin_list_admins(client: TestClient, token: str):
    return client.get("/admin/admins", headers={"Authorization": f"Bearer {token}"})


def test_admin_register_login_me_and_list(app_client: TestClient):
    # Register admin (note: seed may have created 'admin' already; use a unique one)
    reg = admin_register(app_client, "qa_admin", "qa_admin_pass")
    assert reg.status_code in (200, 400), reg.text
    # 400 if username already exists due to prior run; otherwise 200 OK
    if reg.status_code == 200:
        reg_body = reg.json()
        assert reg_body["username"] == "qa_admin"
        assert reg_body["is_active"] is True

    # Login
    login = admin_login(app_client, "qa_admin", "qa_admin_pass")
    # If register returned 400 because of duplicate, ensure login still works (seed or previous test created it)
    assert login.status_code == 200, login.text
    token_payload = login.json()
    assert "access_token" in token_payload
    token = token_payload["access_token"]

    # Me with Bearer token
    me = admin_me(app_client, token)
    assert me.status_code == 200, me.text
    me_body = me.json()
    assert me_body["username"] == "qa_admin"
    assert me_body["is_active"] is True

    # List admins requires Bearer token
    admins = admin_list_admins(app_client, token)
    assert admins.status_code == 200, admins.text
    arr = admins.json()
    assert isinstance(arr, list)
    # Should contain at least the current admin
    assert any(a["username"] == "qa_admin" for a in arr)

    # Negative: no Authorization header
    admins_unauth = app_client.get("/admin/admins")
    assert admins_unauth.status_code in (401, 403)
