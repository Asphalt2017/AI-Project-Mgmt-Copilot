from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_copilot.main import create_app
from ai_copilot.operations.config import (
    Settings,
    load_config_defaults,
)


def test_defaults_without_environment_file(monkeypatch: pytest.MonkeyPatch) -> None:
    defaults = load_config_defaults()
    settings = Settings(_env_file=None)
    assert settings.debug is defaults.debug
    assert settings.web_settings_file == defaults.web_settings_file
    assert (
        settings.database_url.get_secret_value()
        == defaults.database_url.get_secret_value()
    )


def test_settings_require_explicit_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_SETTINGS", raising=False)
    with pytest.raises(ValueError, match="APP_SETTINGS"):
        Settings(_env_file=None)


def test_environment_overrides_local_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / ".workspace"
    workspace.mkdir()
    (workspace / ".env").write_text("DEBUG=true\nPOSTGRES_USER=copilot\n")
    assert create_app(Settings(_env_file=workspace / ".env")).debug is True
    assert create_app(Settings(_env_file=None)).debug is load_config_defaults().debug


def test_invalid_configuration_fails_startup(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DEBUG=invalid\n")
    with pytest.raises(ValidationError):
        create_app(Settings(_env_file=env_file))
