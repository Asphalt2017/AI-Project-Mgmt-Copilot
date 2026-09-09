"""Command-line options and environment fallbacks for the application launcher."""

import argparse
import os
from collections.abc import Sequence


def arg_parser(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse and validate launcher arguments, preferring CLI values over the environment."""
    parser = argparse.ArgumentParser(description="Run AI Delivery Copilot.")
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable debug mode (fallback: DEBUG).",
    )
    parser.add_argument(
        "--host", default=os.environ.get("HOST"), help="Bind address (fallback: HOST)."
    )
    parser.add_argument(
        "--port",
        default=os.environ.get("PORT", "8000"),
        help="TCP port, 1–65535 (fallback: PORT).",
    )
    parser.add_argument(
        "--settings",
        "-s",
        default=os.environ.get("APP_SETTINGS"),
        help="Settings YAML file (fallback: APP_SETTINGS).",
    )
    args = parser.parse_args(argv)
    resolved = {}
    for name, env in (
        ("debug", "DEBUG"),
        ("host", "HOST"),
        ("port", "PORT"),
        ("settings", "APP_SETTINGS"),
    ):
        value = getattr(args, name)
        if value is None:
            value = os.environ.get(env)
        if value is None or (isinstance(value, str) and not value.strip()):
            parser.error(f"Pass --{name} or set {env}.")
        resolved[name] = value

    debug = str(resolved["debug"]).lower()
    if debug not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
        parser.error("DEBUG must be true/false, 1/0, yes/no, or on/off.")
    try:
        port = int(resolved["port"])
    except ValueError:
        parser.error("--port / PORT must be an integer between 1 and 65535.")
    if not 1 <= port <= 65535:
        parser.error("--port / PORT must be an integer between 1 and 65535.")
    return argparse.Namespace(
        debug=debug in {"true", "1", "yes", "on"},
        host=resolved["host"],
        port=port,
        settings=resolved["settings"],
    )
