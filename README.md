# AI Delivery Copilot

AI Delivery Copilot is a project-intelligence layer that keeps Jira requirements, GitHub implementation activity, engineering findings, and human decisions aligned.

The product helps developers understand the intent and boundaries of their work and helps managers see material implementation changes, risks, and decisions backed by source evidence. Jira and GitHub remain the systems of record.

## Project status

The project is in **Phase 0 — Foundation**. The product direction and delivery roadmap are defined; application scaffolding is the next milestone.

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

See [`.build/TECH_STACK.md`](.build/TECH_STACK.md) for requirements and boundaries. Exact versions will be pinned when the application skeleton is created.

## Repository guide

The [`.build`](.build/README.md) directory is the project control plane:

- [`instruction.md`](.build/instruction.md) — durable product and engineering rules;
- [`ROADMAP.md`](.build/ROADMAP.md) — ordered phases, deliverables, and status;
- [`DECISIONS.md`](.build/DECISIONS.md) — accepted choices and rationale;
- [`THOUGHTS.md`](.build/THOUGHTS.md) — unresolved ideas, assumptions, and risks.

Application code lives under `ai_copilot/`, tests under `tests/`, with database migrations planned under `migrations/` and operational documentation under `docs/`.

## Local development

Application bootstrap commands will be added with the Phase 0 skeleton. Expected prerequisites are:

- Git;
- Python supported by the pinned project configuration;
- `uv`;
- PostgreSQL, either locally or through Docker.

Store local environment files in `.workspace/` and API keys or credential files in `.workspace/keys/`. The entire directory is ignored by Git. Keep only placeholder values in the tracked `.env.example`. Never commit credentials, access tokens, imported customer data, or generated model traces containing private content.

### Local database

Install Docker Engine with the Compose plugin, or Docker Desktop. Start PostgreSQL with:

```bash
mkdir -p .workspace/keys
cp -n .env.example .workspace/.env
chmod 700 .workspace .workspace/keys
chmod 600 .workspace/.env
docker compose --env-file .workspace/.env up -d --wait db
```

Skip the copy if you already have a `.workspace/.env`. The example credentials are for local development only. PostgreSQL is available at `127.0.0.1:5432`, with database `ai_delivery_copilot` and user `copilot`. Set `POSTGRES_PORT` in `.workspace/.env` if port 5432 is already in use. Application code running locally will use this host and port; a future application container will use `db:5432`.

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

The GitHub Actions workflow in `.github/workflows/ci.yaml` runs on pull requests, pushes to `main`, and manual dispatch. It runs pre-commit against all tracked files using Python 3.14 and validates Docker Compose using `.env.example`. No repository secrets are required. Hook fixes fail the check so contributors can review and commit them locally.

CI also builds the Python distribution with uv, installs the wheel, and verifies that `ai_copilot` imports from outside the checkout. Application tests, type checking, and database integration tests will be added with the application skeleton.

## License

No open-source license has been selected. Until one is added, the repository should be treated as all rights reserved.
