from unittest.mock import patch

import pytest

from ai_copilot.main import main


@pytest.fixture(autouse=True)
def clear_launch_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DEBUG", "HOST", "PORT"):
        monkeypatch.delenv(name, raising=False)


def test_cli_overrides_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DEBUG", "HOST", "PORT", "APP_SETTINGS"):
        monkeypatch.setenv(name, "invalid")
    with patch("ai_copilot.main.uvicorn.run") as run:
        main(
            [
                "--debug",
                "--host",
                "127.0.0.1",
                "--port",
                "8123",
                "-settings",
                "tests/settings/config.yaml",
            ]
        )
    assert run.call_args.args[0].debug is True
    assert run.call_args.kwargs == {
        "host": "127.0.0.1",
        "port": 8123,
        "log_level": "debug",
    }


def test_environment_fallback_and_no_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8124")
    with patch("ai_copilot.main.uvicorn.run") as run:
        main([])
        assert run.call_args.args[0].debug is True
        main(["--no-debug"])
    assert run.call_args.args[0].debug is False
    assert run.call_args.kwargs == {
        "host": "127.0.0.1",
        "port": 8124,
        "log_level": "info",
    }


@pytest.mark.parametrize("missing", ["DEBUG", "HOST", "PORT", "APP_SETTINGS"])
def test_missing_value_fails(
    missing: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, value in (("DEBUG", "false"), ("HOST", "localhost"), ("PORT", "8000")):
        monkeypatch.setenv(name, value)
    monkeypatch.delenv(missing)
    with patch("ai_copilot.main.uvicorn.run") as run, pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert missing in capsys.readouterr().err
    run.assert_not_called()


@pytest.mark.parametrize(
    "name,value",
    [
        ("DEBUG", "invalid"),
        ("HOST", " "),
        ("PORT", "abc"),
        ("PORT", "0"),
        ("PORT", "65536"),
        ("APP_SETTINGS", "/missing.yaml"),
    ],
)
def test_invalid_value_fails(
    name: str, value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key, setting in (("DEBUG", "false"), ("HOST", "localhost"), ("PORT", "8000")):
        monkeypatch.setenv(key, setting)
    monkeypatch.setenv(name, value)
    with patch("ai_copilot.main.uvicorn.run") as run, pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    run.assert_not_called()
