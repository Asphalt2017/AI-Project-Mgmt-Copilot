# Decision Log

Record product and engineering decisions that constrain future work. Use sequential IDs and preserve superseded entries.

## Decision template

### DEC-000: Short title

- **Status:** Proposed | Accepted | Superseded
- **Date:** YYYY-MM-DD
- **Owners:** Names or roles
- **Related:** Roadmap phase, issue, pull request, or prior decision

**Context:** What prompted the decision and which constraints matter?

**Decision:** What was chosen?

**Consequences:** What becomes easier, harder, required, or explicitly excluded?

---

## Accepted decisions

### DEC-001: Use a modular monolith for the MVP

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** Roadmap Phase 0

**Context:** The MVP must validate the alignment workflow for one team before investing in operational complexity.

**Decision:** Build the initial application as a modular monolith with explicit internal capability boundaries and provider adapters.

**Consequences:** Deployment and local development remain simple. Module boundaries must still be enforced so integrations or workloads can be extracted later if evidence supports it.

### DEC-002: Keep Jira and GitHub as systems of record

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** Product scope

**Context:** The product is intended to improve alignment, not replace established planning and implementation workflows.

**Decision:** Preserve links and provenance to Jira and GitHub. Store normalized copies and derived artifacts only as needed for comparison, review, history, and auditability.

**Consequences:** Synchronization and revision handling are core concerns. The product must make stale or missing source data visible.

### DEC-003: Require human acceptance for generated artifacts

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** Roadmap Phases 2, 4, 5, and 6

**Context:** Model-generated briefs, findings, and comparisons may be incomplete or wrong.

**Decision:** Generated outputs remain drafts or signals until a human confirms, edits, dismisses, or accepts them. Accepted baselines are immutable versions.

**Consequences:** Review states and audit history are required in the domain model and user experience.

### DEC-004: Use a Python-first web stack for the MVP

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** Roadmap Phase 0; `TECH_STACK.md`

**Context:** The MVP needs strong API integration and AI tooling, transactional workflows, a modest interactive UI, and a simple deployment model.

**Decision:** Use Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Jinja, and HTMX in a modular monolith. Use `uv` for dependency management and pytest, Ruff, and mypy as quality gates. Begin with database-backed jobs rather than a message broker.

**Consequences:** The team operates one primary application runtime and can deliver server-rendered workflows quickly. A separate frontend or distributed job system may be introduced later only when product or scaling evidence justifies it.

### DEC-005: Bootstrap capability packages with an application factory

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** Roadmap Phase 0; DEC-001; DEC-004

**Context:** The first runnable slice needs explicit boundaries and isolated configuration before persistence and integrations are introduced.

**Decision:** Keep Python 3.14, commit `.python-version` and `uv.lock`, and assemble FastAPI through `ai_copilot.main:create_app`. Organize business code by the capabilities in the operating guide, with domain policy and application use cases added within each capability. Load typed `COPILOT_` settings at app creation. Provide a public `/health` liveness route without external dependencies.

**Consequences:** Tests can construct independent apps. The skeleton runs without credentials or a database; health does not imply dependency readiness. Authentication and persistence remain separate milestones.

### DEC-006: Configure the first multi-page web preview in YAML

- **Status:** Accepted
- **Date:** 2026-09-09
- **Owners:** Project team
- **Related:** User-requested Phase 0 web preview; DEC-004; DEC-005

**Context:** The user prioritized a usable multi-page web interface and explicitly requested `tests/settings/settings.yaml`, with Overview, Requirements, Implementation, and Decisions pages.

**Decision:** Render the pages with Jinja and local CSS in the existing FastAPI app. A validated YAML schema controls branding, navigation, page types, and sample records. Use the requested file as the single default source and copy it into the wheel at build time. Allow a runtime `COPILOT_WEB_SETTINGS_FILE` override. Use ordinary GET forms and native disclosure elements for search, filters, and details.

**Consequences:** Pages can be added without Python changes; configuration changes require a restart. Sample data is explicitly labeled, and no approvals or source mutations are simulated. This preview precedes domain persistence and authentication; it does not complete the end-to-end product MVP.

## Proposed decisions

- Authentication approach for the pilot.
- Model provider and data-retention policy.
- Jira and GitHub credential model for local development and deployment.
