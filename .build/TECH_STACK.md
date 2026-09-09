# MVP Technology Stack

**Status:** Accepted direction; exact versions pending application scaffolding  
**Decision:** DEC-004  
**Last reviewed:** 2026-09-09

## Requirements

The stack must:

- support Jira, GitHub, and model-provider integrations cleanly;
- make provenance, versioning, and transactional review workflows straightforward;
- support typed domain boundaries and automated tests;
- run locally without paid cloud services;
- deploy as one application plus one relational database for the MVP;
- allow background synchronization without requiring distributed infrastructure;
- keep provider-specific payloads outside the domain model;
- provide secure configuration and structured, redacted logging.

## Selected direction

| Concern | Selection | Reason |
| --- | --- | --- |
| Language | Python | Strong integration and AI ecosystem; one primary runtime for the MVP |
| Application framework | FastAPI | Typed HTTP boundaries, dependency injection, async integration support, and OpenAPI |
| UI | Jinja templates + HTMX + minimal JavaScript | Keeps the MVP in one deployable application while supporting interactive review flows |
| Database | PostgreSQL | Transactions, relational integrity, JSON support, and mature operational tooling |
| Data access | SQLAlchemy 2.x | Explicit persistence mapping and mature PostgreSQL support |
| Migrations | Alembic | Versioned schema changes integrated with SQLAlchemy |
| HTTP clients | httpx | Async-capable adapters for Jira, GitHub, and model APIs |
| Validation/configuration | Pydantic + pydantic-settings | Typed external boundaries and environment configuration |
| Background work | Database-backed job table and worker | Reliable enough for manual refresh/polling without introducing a broker |
| Package management | uv | Fast, reproducible Python environments and lock files |
| Tests | pytest | Unit, integration, and adapter contract testing |
| Quality gates | Ruff + mypy | Formatting/linting and static type checking |
| Local infrastructure | Docker Compose | Optional reproducible PostgreSQL setup without forcing containerized app development |

## Version policy

- Pin a supported Python minor version in `pyproject.toml` and `.python-version` during scaffolding.
- Commit the generated `uv.lock` file.
- Use compatible-release bounds for direct runtime dependencies and review upgrades deliberately.
- Prefer maintained stable releases; avoid preview dependencies in the production path.
- Record any dependency that materially shapes architecture in `DECISIONS.md`.

## Architectural boundaries

- The web layer calls application use cases; it does not contain domain policy.
- Domain objects do not import FastAPI, SQLAlchemy models, or provider SDK types.
- Jira, GitHub, and model access are adapters behind application-owned interfaces.
- Generated artifacts store their sources, model metadata, timestamps, and confidence information.
- Accepted baselines and decisions are immutable records; corrections create new versions.
- Background jobs must be idempotent and expose retry/failure state.

## Deferred until evidence requires it

- React or another standalone single-page application;
- Redis, Celery, Kafka, or another message broker;
- microservices or serverless decomposition;
- vector database infrastructure;
- Kubernetes;
- autonomous agent frameworks;
- real-time event streaming.

## Decisions still required before production use

- Supported Python minor version and dependency pins.
- Authentication and authorization approach.
- Hosting platform and secret-management mechanism.
- Model provider, regional processing, retention, and redaction policy.
- Production job scheduling and concurrency limits.
- Backup, recovery, and source-data retention policies.
