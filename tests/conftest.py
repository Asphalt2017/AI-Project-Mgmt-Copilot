from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolated_auth_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "APP_SETTINGS",
        str(Path(__file__).parent / "settings" / "config.yaml"),
    )


def sign_in(client: TestClient) -> None:
    client.app.state.auth_store.create_user("dev@example.com", "a long test password")  # type: ignore[union-attr]
    client.get("/login")
    response = client.post(
        "/login",
        data={
            "email": "dev@example.com",
            "password": "a long test password",
            "csrf": client.cookies["copilot_csrf"],
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
