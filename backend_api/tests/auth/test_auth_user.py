import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure the app reads our test database URL before importing the FastAPI app
# We will use a temporary SQLite file DB to persist within a test run and remove after.
@pytest.fixture(scope="session")
def test_db_url(tmp_path_factory) -> str:
    tmp_dir = tmp_path_factory.mktemp("auth_tests")
    db_path = tmp_dir / "test_auth.db"
    url = f"sqlite:///{db_path}"
    # Set for the app config to pick up
    os.environ["DATABASE_URL"] = url
    # Provide a strong secret for deterministic tests
    os.environ["JWT_SECRET_KEY"] = "TEST_SECRET_KEY_CHANGE_ME"
    return url


@pytest.fixture(scope="session")
def app_client(test_db_url: str) -> Generator[TestClient, None, None]:
    """
    Create a TestClient for the FastAPI app with lifespan events enabled,
    so database tables are created and seed data is applied via startup hook.
    """
    # Import here so it picks env vars above
    from app.main import app  # noqa: WPS433

    with TestClient(app) as client:
        yield client


def register_user(client: TestClient, name: str, email: str, password: str):
    resp = client.post("/auth/register", json={"name": name, "email": email, "password": password})
    return resp


def login_user(client: TestClient, email: str, password: str):
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp


def get_me(client: TestClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return client.get("/users/me", headers=headers)


def test_user_register_and_login_and_me_flow(app_client: TestClient):
    # 1) Register
    reg = register_user(app_client, "Alice Tester", "alice@example.com", "password123")
    assert reg.status_code == 200, reg.text
    body = reg.json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice Tester"
    assert "id" in body and isinstance(body["id"], int)

    # 2) Login
    login = login_user(app_client, "alice@example.com", "password123")
    assert login.status_code == 200, login.text
    token_payload = login.json()
    assert "access_token" in token_payload
    assert token_payload.get("token_type", "bearer") == "bearer"
    token = token_payload["access_token"]

    # 3) Bearer-protected me
    me = get_me(app_client, token)
    assert me.status_code == 200, me.text
    me_body = me.json()
    assert me_body["email"] == "alice@example.com"
    # Swagger Bearer security uses Authorization header; verify also that omitting header denies access
    me_no_auth = app_client.get("/users/me")
    assert me_no_auth.status_code in (401, 403)


def test_negative_login_wrong_password(app_client: TestClient):
    # seed a user
    reg = register_user(app_client, "Bob Negative", "bob@example.com", "correct-password")
    assert reg.status_code == 200 or (reg.status_code == 400 and "already" in reg.text.lower())

    # attempt login with wrong password
    bad = login_user(app_client, "bob@example.com", "wrong-password")
    assert bad.status_code == 401
    assert "Invalid credentials" in bad.text or "invalid" in bad.text.lower()
