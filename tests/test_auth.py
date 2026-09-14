from collections.abc import Iterator

import pytest
from conftest import sign_in
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from ai_copilot.main import create_app
from ai_copilot.operations.auth import auth, sessions, token_hash
from ai_copilot.operations.config import Settings
from ai_copilot.tools.encription import hash_password, verify_password


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(
        create_app(
            Settings(
                _env_file=None, database_url="sqlite:///:memory:", cookie_secure=False
            )
        )
    ) as client:
        yield client


def test_password_hashes_are_salted_and_verifiable() -> None:
    password = "a long test password"
    first, second = hash_password(password), hash_password(password)
    assert first.startswith("$argon2id$")
    assert first != second
    assert password not in first
    assert verify_password(first, password)
    assert not verify_password(first, "wrong password")
    assert not verify_password("corrupt", password)
    with pytest.raises(ValueError):
        hash_password("short")


def test_workspace_requires_login(client: TestClient) -> None:
    for path in ("/", "/overview", "/requirements"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"
    assert client.get("/health").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_login_storage_logout_and_revocation(client: TestClient) -> None:
    sign_in(client)
    token = client.cookies["copilot_session"]
    response = client.get("/overview")
    assert "Log out" in response.text
    assert "dev@example.com" in response.text
    assert response.headers["cache-control"] == "no-store"
    with client.app.state.auth_store.engine.connect() as connection:
        row = connection.execute(select(auth)).mappings().one()
        assert row["password_hash"].startswith("$argon2id$")
        assert connection.execute(
            select(sessions.c.token_hash)
        ).scalar_one() == token_hash(token)
    response = client.post(
        "/logout", data={"csrf": client.cookies["copilot_csrf"]}, follow_redirects=False
    )
    assert response.status_code == 303
    assert "copilot_session" not in client.cookies
    client.cookies.set("copilot_session", token)
    assert client.get("/overview", follow_redirects=False).status_code == 303


def test_failed_login_and_csrf(client: TestClient) -> None:
    client.get("/login")
    data = {"email": "missing@example.com", "password": "incorrect", "csrf": "invalid"}
    assert client.post("/login", data=data).status_code == 403
    data["csrf"] = client.cookies["copilot_csrf"]
    assert (
        client.post(
            "/login", data=data, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    response = client.post("/login", data=data)
    assert response.status_code == 401
    assert "Invalid email or password" in response.text
    assert "copilot_session" not in client.cookies
    sign_in(client)
    assert client.post("/logout", data={"csrf": "invalid"}).status_code == 403
    assert client.get("/overview").status_code == 200
    assert client.get("/logout", follow_redirects=False).status_code != 200


def test_expired_and_forged_sessions(client: TestClient) -> None:
    sign_in(client)
    with client.app.state.auth_store.engine.begin() as connection:
        connection.execute(update(sessions).values(expires_at=0))
    assert client.get("/overview", follow_redirects=False).status_code == 303
    client.cookies.clear()
    client.cookies.set("copilot_session", "forged")
    assert client.get("/overview", follow_redirects=False).status_code == 303


def test_login_throttling(client: TestClient) -> None:
    client.get("/login")
    for _ in range(10):
        assert (
            client.post(
                "/login",
                data={
                    "email": "missing@example.com",
                    "password": "incorrect",
                    "csrf": client.cookies["copilot_csrf"],
                },
            ).status_code
            == 401
        )
    response = client.post(
        "/login",
        data={
            "email": "missing@example.com",
            "password": "incorrect",
            "csrf": client.cookies["copilot_csrf"],
        },
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "300"


def test_secure_cookies() -> None:
    with TestClient(
        create_app(
            Settings(
                _env_file=None, database_url="sqlite:///:memory:", cookie_secure=True
            )
        ),
        base_url="https://testserver",
    ) as client:
        sign_in(client)
        cookies = list(client.cookies.jar)
        assert all(cookie.secure for cookie in cookies)
        assert all(cookie.has_nonstandard_attr("HttpOnly") for cookie in cookies)
