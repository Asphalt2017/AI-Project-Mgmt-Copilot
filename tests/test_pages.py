from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from conftest import sign_in
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ai_copilot.main import create_app
from ai_copilot.operations.config import Settings, WebConfig, load_web_config


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(
        create_app(
            Settings(
                _env_file=None, database_url="sqlite:///:memory:", cookie_secure=False
            )
        )
    ) as client:
        sign_in(client)
        yield client


def test_home_and_all_configured_pages(client: TestClient) -> None:
    config = load_web_config()
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"].endswith("/overview")
    for page in config.pages:
        response = client.get(f"/{page.slug}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert page.title in response.text
        assert 'aria-current="page"' in response.text
        assert "Sample content only" in response.text
        for navigation in config.pages:
            assert f'/{navigation.slug}"' in response.text
    assert client.get("/static/app.css").status_code == 200


def test_search_status_filter_and_no_results(client: TestClient) -> None:
    response = client.get("/requirements", params={"q": "BASELINE"})
    assert "DEMO-102" in response.text
    assert "DEMO-101" not in response.text
    response = client.get("/requirements", params={"status": "Draft"})
    assert "DEMO-101" in response.text
    assert "DEMO-102" not in response.text
    response = client.get("/requirements", params={"q": "baseline", "status": "Draft"})
    assert "No matching items" in response.text
    assert "Show all items" in response.text


def test_missing_page_and_api_coexist(client: TestClient) -> None:
    response = client.get("/not-a-page")
    assert response.status_code == 404
    assert "This page isn't in your workspace." in response.text
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 200


def test_custom_yaml_controls_routes_content_and_escapes_html(tmp_path: Path) -> None:
    path = tmp_path / "custom.yaml"
    config = load_web_config().model_dump()
    config["name"] = "<script>alert(1)</script>"
    config["home"] = "backlog"
    config["pages"] = [
        {
            "slug": "backlog",
            "label": "Backlog",
            "title": "Our backlog",
            "description": "Configured without Python changes.",
            "empty_message": "Nothing scheduled yet.",
        }
    ]
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    with TestClient(
        create_app(
            Settings(
                _env_file=None,
                web_settings_file=path,
                database_url="sqlite:///:memory:",
                cookie_secure=False,
            )
        )
    ) as client:
        sign_in(client)
        response = client.get("/")
        assert response.url.path == "/backlog"
        assert "Nothing scheduled yet." in response.text
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
        assert "<script>alert(1)</script>" not in response.text
        assert client.get("/requirements").status_code == 404
        response = client.get("/backlog", params={"q": '<img src=x onerror="x">'})
        assert "<img src=x" not in response.text
        assert "&lt;img" in response.text


@pytest.mark.parametrize("slug", ["health", "docs", "redoc", "static", "../bad"])
def test_rejects_invalid_or_reserved_routes(slug: str) -> None:
    config = load_web_config().model_dump()
    config["pages"][0]["slug"] = slug
    config["home"] = slug
    with pytest.raises(ValidationError):
        WebConfig.model_validate(config)


def test_rejects_duplicate_pages_and_missing_home() -> None:
    config = load_web_config().model_dump()
    config["pages"].append(config["pages"][0])
    with pytest.raises(ValidationError, match="unique"):
        WebConfig.model_validate(config)
    config = load_web_config().model_dump()
    config["home"] = "missing"
    with pytest.raises(ValidationError, match="Home"):
        WebConfig.model_validate(config)


def test_bad_config_fails_startup(tmp_path: Path) -> None:
    path = tmp_path / "settings.yaml"
    with pytest.raises(ValueError, match="Cannot load web settings"):
        create_app(Settings(_env_file=None, web_settings_file=path))
    for content in ["pages: [", "!!python/object/apply:os.system ['false']"]:
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match="Cannot load web settings"):
            load_web_config(path)
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_web_config(path)


def test_env_file_selects_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "settings.yaml"
    env_file = tmp_path / ".env"
    config = load_web_config().model_dump()
    config["home"] = "decisions"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    env_file.write_text(f"WEB_SETTINGS_FILE={path}\n", encoding="utf-8")
    with TestClient(
        create_app(
            Settings(
                _env_file=env_file,
                database_url="sqlite:///:memory:",
                cookie_secure=False,
            )
        )
    ) as client:
        sign_in(client)
        assert client.get("/").url.path == "/decisions"


def test_default_yaml_is_derived_from_settings_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings_dir = tmp_path / "tests" / "settings"
    settings_dir.mkdir(parents=True)
    config = load_web_config().model_dump()
    config["home"] = "implementation"
    (settings_dir / "alternate.yaml").write_text(
        yaml.safe_dump(config), encoding="utf-8"
    )
    (settings_dir / "config.yaml").write_text(
        "\n".join(
            [
                "debug: false",
                "web_settings_file: alternate.yaml",
                'database_url: "sqlite:///:memory:"',
                "cookie_secure: false",
                "session_lifetime_seconds: 28800",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("APP_SETTINGS", str(settings_dir / "config.yaml"))
    assert load_web_config().home == "implementation"
