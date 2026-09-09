# Application boundaries

`main.py` is the composition root and exposes the `create_app` factory.
`web/` owns HTTP routes and response schemas. `operations/` owns configuration
and future operational concerns. `integrations/` will implement provider adapters.

The business capability packages are `artifacts/`, `requirements/`,
`implementation/`, `alignment/`, and `decisions/`. They are intentionally empty
until their domain models and use cases are implemented. Within each capability,
add `domain.py` for framework-independent policy, `application.py` for use cases
and adapter interfaces, and `persistence.py` for SQLAlchemy mappings as needed.
Web routes call application use cases; adapters implement application-owned
interfaces. Domain code must not import FastAPI, SQLAlchemy, or provider types.

`GET /health` is a public process-liveness endpoint and performs no external I/O.
YAML-configured, read-only pages live in `web/pages.py`, with shared templates
and static assets under `web/`. The configuration schema and loader live in
`web/config.py`; see `docs/web-configuration.md`. Database readiness,
authentication, approval workflows, and provider integrations belong to subsequent
milestones.
