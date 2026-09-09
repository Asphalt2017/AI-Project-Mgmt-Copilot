"""Composition root: assemble the HTTP application and its dependencies."""

import sys
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ai_copilot.operations.auth import AuthStore, create_auth_router
from ai_copilot.operations.config import Settings, load_web_config
from ai_copilot.tools.cli import arg_parser
from ai_copilot.web.health import router as health_router
from ai_copilot.web.pages import create_pages_router


def create_app(settings: Settings) -> FastAPI:
    web_config = load_web_config(settings.web_settings_file)
    store = AuthStore(settings.database_url.get_secret_value())

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        store.initialize()
        try:
            yield
        finally:
            store.engine.dispose()

    app = FastAPI(title=web_config.name, debug=settings.debug, lifespan=lifespan)
    app.state.auth_store = store
    app.include_router(create_auth_router(web_config, settings))
    app.include_router(health_router)
    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent / "web/static"),
        name="static",
    )
    app.include_router(create_pages_router(web_config))
    return app


def create_app_from_settings_file() -> FastAPI:
    return create_app(Settings())


def main(argv: Sequence[str] | None = None) -> None:
    args = arg_parser(argv)
    try:
        app = create_app(Settings(settings_file=args.settings, debug=args.debug))
    except ValueError:
        print(
            "Cannot load application settings; check the settings and page YAML files.",
            file=sys.stderr,
        )
        raise SystemExit(2) from None
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
    )


if __name__ == "__main__":
    main()
