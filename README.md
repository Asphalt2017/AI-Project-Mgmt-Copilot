# AI Delivery Copilot

AI Delivery Copilot is a project-intelligence layer that keeps Jira requirements, GitHub implementation activity, engineering findings, and human decisions aligned.

The product helps developers understand the intent and boundaries of their work and helps managers see material implementation changes, risks, and decisions backed by source evidence. Jira and GitHub remain the systems of record.

## Project status

The project is in **Phase 0 — Foundation**. A YAML-configured, multi-page web preview is implemented; the core domain model and persistence layer are next.

## MVP workflow

```text
Jira issue
  -> generated implementation brief
  -> human-accepted baseline
  -> linked GitHub pull request
  -> confirmed engineering findings
  -> requirement/implementation comparison
  -> human decision
  -> versioned baseline
```

Generated content is always reviewable. The system must distinguish source facts from inference, preserve provenance, and require human acceptance before changing an approved baseline.

## Current web app data flow

The preview loads page configuration at startup and serves read-only sample data.
Jira ingestion and GitHub ingestion are future milestones. Authentication uses durable database storage.

```mermaid
flowchart TD
    subgraph Startup[Application startup]
        Env["APP_SETTINGS"] --> Settings["Typed application settings"]
        Settings --> Source["Select page YAML from settings"]
        YAML["tests/settings/settings.yaml<br/>Packaged copy when installed from a wheel"] --> Source
        Source --> Validate["Safe YAML parsing and WebConfig validation"]
        Validate --> Config["In-memory branding, navigation, pages, and records"]
        Validate -->|Invalid configuration| Stop["Stop startup with an error"]
    end

    subgraph Requests[Page request and response]
        Browser["Browser"] -->|GET /| Home["Redirect to configured home page"]
        Home --> Browser
        Browser -->|"GET /{slug}?q=...&status=..."| Router["FastAPI page router"]
        Config --> Router
        Config --> Home
        Router -->|Known page| Filter["Select page and filter records by search and status"]
        Filter --> Templates["Jinja templates: navigation, overview, and collections"]
        Router -->|Unknown page| NotFound["Jinja page-not-found template"]
        Templates -->|Escaped HTML response| Browser
        NotFound -->|HTTP 404 HTML response| Browser
        Browser -->|GET /static/app.css| Static["Packaged stylesheet"]
        Static -->|CSS response| Browser
    end
```

Search and status filters operate on the loaded records without changing the YAML.
Expandable details work in the browser. Restart the app after editing configuration;
see [web configuration](docs/web-configuration.md) for the schema and examples.

## Technology direction

The MVP will be a Python-first modular monolith:

- Python and FastAPI for the application and HTTP interface;
- PostgreSQL for durable relational storage;
- SQLAlchemy and Alembic for persistence and migrations;
- Jinja templates, HTMX, and minimal JavaScript for the web interface;
- `httpx`-based adapters for Jira, GitHub, and model providers;
- database-backed background work initially, with no required message broker;
- pytest, Ruff, and mypy for automated verification;
- `uv` for Python dependency and environment management;
- Docker Compose for optional local infrastructure.

See [`.build/TECH_STACK.md`](.build/TECH_STACK.md) for requirements and boundaries. Application dependencies are locked in `uv.lock`; remaining stack components will be added as their milestones begin.

## Repository guide

The [`.build`](.build/README.md) directory is the project control plane:

- [`instruction.md`](.build/instruction.md) — durable product and engineering rules;
- [`ROADMAP.md`](.build/ROADMAP.md) — ordered phases, deliverables, and status;
- [`DECISIONS.md`](.build/DECISIONS.md) — accepted choices and rationale;
- [`THOUGHTS.md`](.build/THOUGHTS.md) — unresolved ideas, assumptions, and risks.

Application code lives under `ai_copilot/`, tests under `tests/`, with authentication tables initialized on startup and versioned database migrations planned under `migrations/` and operational documentation under `docs/`.

## Local development

Install Python 3.14 and `uv`, then run from the repository root:

```bash
uv sync --locked
uv run python -m ai_copilot.main --debug --port 8000 --host 127.0.0.1 --settings tests/settings/config.yaml
```

Open <http://127.0.0.1:8000/> for the web app or <http://127.0.0.1:8000/docs> for API documentation. Verify liveness with
`curl http://127.0.0.1:8000/health`, which returns `{"status":"ok"}`.
The app runs with local SQLite without PostgreSQL or provider credentials. This endpoint
checks process liveness only; it does not check database readiness.

The module launcher accepts `--debug` / `--no-debug`, `--host`, `--port`, and
`--settings` (also spelled `-settings`). Omitted options are read from `DEBUG`,
`HOST`, `PORT`, and `APP_SETTINGS`, respectively. Every launcher option must be
provided through the command line or environment; missing or invalid values stop
startup with an error. Command-line values take precedence. Debug mode enables
FastAPI debug responses and debug logging, without a reload subprocess so debugger
breakpoints stay in the launched process.

For example, launch entirely from environment variables:

```bash
DEBUG=true HOST=127.0.0.1 PORT=8000 APP_SETTINGS=tests/settings/config.yaml python -m ai_copilot.main
```

Startup requires a settings YAML file. Pass it through `APP_SETTINGS`, or use
`--settings` for commands that provide that option. Defaults such as debug mode,
the web settings file, database URL, cookie policy, and session lifetime live in
[`tests/settings/config.yaml`](tests/settings/config.yaml). Explicit env files
or constructor values can override those YAML values when tests or local tooling
pass them in.

Run the quality checks:

```bash
uv run pytest
uv run mypy
uv run ruff check .
uv run ruff format --check .
```

The web app includes Overview, Requirements, Implementation, and Decisions pages
with sample content, search, status filters, and expandable details. Configure its
branding, navigation, and pages in [`tests/settings/settings.yaml`](tests/settings/settings.yaml),
then restart the app. Set `web_settings_file` in the selected settings YAML to
use another page YAML file.
This is a read-only preview; ingestion and approval workflows remain upcoming.
See [web configuration](docs/web-configuration.md) for the schema and examples,
and [application boundaries](ai_copilot/README.md) for the package layout.

Store local environment files in `.workspace/` and API keys or credential files in `.workspace/keys/`. The entire directory is ignored by Git. Never commit credentials, access tokens, imported customer data, or generated model traces containing private content.

### Local database

Install Docker Engine with the Compose plugin, or Docker Desktop. Start PostgreSQL with:

```bash
mkdir -p .workspace/keys
touch .workspace/.env
# Set POSTGRES_PASSWORD in .workspace/.env before starting PostgreSQL.
chmod 700 .workspace .workspace/keys
chmod 600 .workspace/.env
docker compose --env-file .workspace/.env up -d --wait db
```

Set `POSTGRES_PASSWORD` in `.workspace/.env` before starting the database. PostgreSQL is available at `127.0.0.1:5432`, with database `ai_delivery_copilot` and user `copilot`. Set `POSTGRES_PORT` in `.workspace/.env` if port 5432 is already in use. Application code running locally will use this host and port; a future application container will use `db:5432`.

```bash
docker compose --env-file .workspace/.env ps
docker compose --env-file .workspace/.env exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose --env-file .workspace/.env down
```

The named volume retains database data when containers stop or are removed. Credentials and database settings initialize an empty volume only; editing `.workspace/.env` does not update an existing database. `docker compose --env-file .workspace/.env down --volumes` deletes the local database permanently.

The setup uses the [official PostgreSQL image](https://hub.docker.com/_/postgres), pinned to major version 18, with its data volume mounted at `/var/lib/postgresql`.

## Contributing

Before changing the project, read the build-control documents and work from the earliest incomplete roadmap milestone. Behavior changes require tests, durable decisions belong in the decision log, and unapproved ideas belong in the thoughts queue.

Install pre-commit and enable the hooks once per clone:

```bash
uv tool install pre-commit
pre-commit install
pre-commit run --all-files
```

The pinned hooks in `.pre-commit-config.yaml` check whitespace, file endings, YAML/JSON/TOML syntax, merge conflicts, large files, and private keys. Ruff automatically fixes lint issues where possible and formats Python files. Markdown hard line breaks are preserved. Review and stage any automatic fixes before retrying a commit. The first run downloads the hook environments and requires network access.

### Continuous integration

The GitHub Actions workflow in `.github/workflows/ci.yaml` runs on pull requests, pushes to `main`, and manual dispatch. It runs pre-commit against all tracked files using Python 3.14 and validates Docker Compose using a placeholder password supplied by CI. No repository secrets are required. Hook fixes fail the check so contributors can review and commit them locally.

CI also builds the Python distribution with uv, installs the wheel, and verifies that `ai_copilot` imports from outside the checkout. A separate job installs locked dependencies and runs pytest, mypy, and Ruff. Database integration tests will be added with persistence.

## License

No open-source license has been selected. Until one is added, the repository should be treated as all rights reserved.

### Sign in and account setup

Install dependencies with `uv sync`. For local HTTP development, set
`cookie_secure: false` in the selected settings YAML.
The default database is `sqlite:///./copilot.db`, relative to the working directory.
Create an account from the same directory and environment used to run the app:

```bash
uv run python -m ai_copilot.operations.auth --settings tests/settings/config.yaml you@example.com
uv run python -m ai_copilot.main --debug --port 8000 --host 127.0.0.1 --settings tests/settings/config.yaml
```

The account command prompts for a password and confirmation without echoing it.
Passwords must contain 15–1024 characters. Visit `http://127.0.0.1:8000/login`.
Workspace pages require login; the top bar provides a Log out button.
Health, static assets, and API documentation remain public.

To use the Compose PostgreSQL service, set `database_url` in the selected
settings YAML to
`postgresql+psycopg://copilot:YOUR_PASSWORD@127.0.0.1:5432/ai_delivery_copilot`
with your actual password (URL-encode special characters). Startup and the account
command create `"user".auth` and `"user".sessions` if absent. SQLite uses the same
logical tables without a schema prefix. The database account needs permission to
create these tables and the PostgreSQL schema on first use.

`ai_copilot/tools/encription.py` stores Argon2id password hashes with random salts;
there is no reversible password encryption. Session tokens are random, stored
only as SHA-256 hashes in the database, expire after eight hours by default, and
are revoked on logout. Forms validate CSRF tokens. Authentication responses and
workspace pages disable caching. All provisioned accounts currently share the
same workspace; project roles and password-reset flows are not implemented.

Use HTTPS and `cookie_secure: true` outside local development. Login allows ten attempts per client IP per five minutes per
worker, with an additional worker-wide cap. For multiple workers or replicas,
configure shared rate limiting at the ingress and trust forwarded IP headers
only from your proxy. Protect the database file and backups as credential data.
