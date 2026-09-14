"""Persistent identities and revocable, opaque sessions."""

import argparse
import hashlib
import secrets
import time
from collections import defaultdict, deque
from getpass import getpass
from pathlib import Path
from threading import Lock
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.pool import StaticPool

from ai_copilot.operations.config import Settings, WebConfig
from ai_copilot.tools.encription import hash_password, needs_rehash, verify_password

SESSION_COOKIE = "copilot_session"
CSRF_COOKIE = "copilot_csrf"

metadata = MetaData(schema="user")
auth = Table(
    "auth",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(254), nullable=False, unique=True),
    Column("password_hash", String(512), nullable=False),
)
sessions = Table(
    "sessions",
    metadata,
    Column("token_hash", String(64), primary_key=True),
    Column("user_id", ForeignKey("user.auth.id"), nullable=False),
    Column("expires_at", Float, nullable=False),
)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthStore:
    def __init__(self, database_url: str) -> None:
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                **(
                    {"poolclass": StaticPool}
                    if database_url.endswith(":memory:")
                    else {}
                ),
                execution_options={"schema_translate_map": {"user": None}},
            )
        else:
            self.engine = create_engine(database_url)
        # Equivalent work for unknown accounts, avoiding a fast account lookup oracle.
        self.dummy_hash = hash_password(secrets.token_urlsafe(32))

    def initialize(self) -> None:
        with self.engine.begin() as connection:
            if self.engine.dialect.name == "postgresql":
                connection.exec_driver_sql('CREATE SCHEMA IF NOT EXISTS "user"')
            metadata.create_all(connection)

    def create_user(self, email: str, password: str) -> None:
        email = email.strip().casefold()
        if not email or len(email) > 254 or "@" not in email:
            raise ValueError("Enter a valid email address.")
        encoded = hash_password(password)
        with self.engine.begin() as connection:
            connection.execute(insert(auth).values(email=email, password_hash=encoded))

    def authenticate(self, email: str, password: str) -> int | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    select(auth).where(auth.c.email == email.strip().casefold())
                )
                .mappings()
                .first()
            )
        encoded = row["password_hash"] if row else self.dummy_hash
        valid = verify_password(encoded, password)
        if row is None or not valid:
            return None
        if needs_rehash(encoded):
            with self.engine.begin() as connection:
                connection.execute(
                    update(auth)
                    .where(auth.c.id == row["id"])
                    .values(password_hash=hash_password(password))
                )
        return int(row["id"])

    def create_session(self, user_id: int, lifetime: int) -> str:
        token = secrets.token_urlsafe(32)
        with self.engine.begin() as connection:
            connection.execute(
                delete(sessions).where(sessions.c.expires_at <= time.time())
            )
            connection.execute(
                insert(sessions).values(
                    token_hash=token_hash(token),
                    user_id=user_id,
                    expires_at=time.time() + lifetime,
                )
            )
        return token

    def user_for_session(self, token: str) -> str | None:
        with self.engine.connect() as connection:
            email = connection.execute(
                select(auth.c.email)
                .join(sessions)
                .where(
                    sessions.c.token_hash == token_hash(token),
                    sessions.c.expires_at > time.time(),
                )
            ).scalar_one_or_none()
        return str(email) if email is not None else None

    def revoke(self, token: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                delete(sessions).where(sessions.c.token_hash == token_hash(token))
            )


def require_session(request: Request) -> None:
    store: AuthStore = request.app.state.auth_store
    email = store.user_for_session(request.cookies.get(SESSION_COOKIE, ""))
    if email is None:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    request.state.email = email


def check_csrf(request: Request, csrf: str) -> None:
    expected = request.cookies.get(CSRF_COOKIE, "")
    if not expected or not secrets.compare_digest(expected, csrf):
        raise HTTPException(
            status_code=403, detail="Invalid form token. Reload the page."
        )
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(status_code=403, detail="Invalid form origin")


def create_auth_router(config: WebConfig, settings: Settings) -> APIRouter:
    router = APIRouter(include_in_schema=False)
    templates = Jinja2Templates(
        directory=Path(__file__).parents[1] / "web" / "templates"
    )
    attempts: dict[str, deque[float]] = defaultdict(deque)
    lock = Lock()

    def login_form(
        request: Request, error: str = "", status: int = 200
    ) -> HTMLResponse:
        csrf = secrets.token_urlsafe(32)
        response = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"config": config, "error": error, "csrf": csrf},
            status_code=status,
        )
        response.set_cookie(
            CSRF_COOKIE,
            csrf,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="strict",
            max_age=28800,
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @router.get("/login", response_class=HTMLResponse)
    def login_page(request: Request) -> HTMLResponse:
        return login_form(request)

    @router.post("/login", response_model=None)
    def login(
        request: Request,
        email: Annotated[str, Form(max_length=254)],
        password: Annotated[str, Form(max_length=1024)],
        csrf: Annotated[str, Form(max_length=128)],
    ) -> HTMLResponse | RedirectResponse:
        check_csrf(request, csrf)
        address = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with lock:
            for key in list(attempts):
                if not attempts[key] or attempts[key][-1] < now - 300:
                    del attempts[key]
            history = attempts[address]
            while history and history[0] < now - 300:
                history.popleft()
            if len(history) >= 10 or sum(map(len, attempts.values())) >= 1000:
                throttled_response = login_form(
                    request, "Too many attempts. Try again in five minutes.", 429
                )
                throttled_response.headers["Retry-After"] = "300"
                return throttled_response
            history.append(now)
        store: AuthStore = request.app.state.auth_store
        user_id = store.authenticate(email, password)
        if user_id is None:
            return login_form(request, "Invalid email or password.", 401)
        store.revoke(request.cookies.get(SESSION_COOKIE, ""))
        token = store.create_session(user_id, settings.session_lifetime_seconds)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            SESSION_COOKIE,
            token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=settings.session_lifetime_seconds,
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @router.post("/logout")
    def logout(
        request: Request, csrf: Annotated[str, Form(max_length=128)]
    ) -> RedirectResponse:
        check_csrf(request, csrf)
        store: AuthStore = request.app.state.auth_store
        store.revoke(request.cookies.get(SESSION_COOKIE, ""))
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(
            SESSION_COOKIE, secure=settings.cookie_secure, httponly=True, samesite="lax"
        )
        response.delete_cookie(
            CSRF_COOKIE, secure=settings.cookie_secure, httponly=True, samesite="strict"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    return router


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Copilot login account")
    parser.add_argument(
        "--settings",
        help="Path to the settings YAML file. Defaults to APP_SETTINGS.",
    )
    parser.add_argument("email")
    args = parser.parse_args()
    password = getpass("Password (15–1024 characters): ")
    if password != getpass("Confirm password: "):
        parser.error("Passwords do not match")
    store = AuthStore(
        Settings(settings_file=args.settings).database_url.get_secret_value()
    )
    try:
        store.initialize()
        store.create_user(args.email, password)
    finally:
        store.engine.dispose()
    print("Account created.")


if __name__ == "__main__":
    main()
