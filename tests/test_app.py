from fastapi.testclient import TestClient

from ai_copilot.main import create_app
from ai_copilot.operations.config import Settings


def test_health_without_external_services() -> None:
    with TestClient(
        create_app(
            Settings(
                _env_file=None, database_url="sqlite:///:memory:", cookie_secure=False
            )
        )
    ) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert response.headers["content-type"] == "application/json"
        assert client.get("/unknown").status_code == 404


def test_openapi_exposes_health_contract() -> None:
    with TestClient(
        create_app(
            Settings(
                _env_file=None, database_url="sqlite:///:memory:", cookie_secure=False
            )
        )
    ) as client:
        schema = client.get("/openapi.json").json()
        assert "/health" in schema["paths"]
        assert schema["info"]["title"] == "AI Delivery Copilot"


def test_factory_isolates_configuration() -> None:
    debug_app = create_app(Settings(_env_file=None, debug=True))
    default_app = create_app(Settings(_env_file=None, debug=False))
    assert debug_app.debug is True
    assert default_app.debug is False
