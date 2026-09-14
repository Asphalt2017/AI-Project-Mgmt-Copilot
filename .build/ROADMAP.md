# AI Delivery Copilot Roadmap

**Current phase:** Phase 0 — Foundation  
**Status:** In progress  
**Last reviewed:** 2026-09-09

## Product Goal

Build a project-intelligence layer that keeps Jira requirements, GitHub implementation activity, engineering findings, and human decisions aligned.

The first release should prove that one team can move from issue intent to an accepted implementation baseline, detect meaningful implementation changes, and record decisions with evidence.

## Roadmap Principles

- Jira and GitHub remain the systems of record.
- The platform connects context, highlights gaps, and records decisions.
- LLM output must distinguish source facts from inference.
- Human confirmation is required before generated briefs, findings, or baseline updates become accepted.
- Every important claim must link back to Jira, GitHub, or a recorded decision.
- The MVP should validate a single-team workflow before adding broad automation or enterprise features.

## Phase 0: Foundation

**Goal:** Establish the application skeleton, internal boundaries, and durable data model.

**Status:** In progress

### Deliverables

- [x] Repository README and project-control documentation.
- [x] Baseline `.gitignore`, `.editorconfig`, `.gitattributes`, and environment template.
- [x] MVP technology direction and architectural constraints.
- [x] Pre-commit hooks for file hygiene and Python linting/formatting.
- [x] Local PostgreSQL Docker Compose service, persistent volume, and environment template.
- [x] GitHub Actions CI for pre-commit checks and Docker Compose validation.
- [x] Modular monolith application structure with an app factory and health endpoint.
- [x] YAML-configured multi-page web preview with sample content, search, and filters (user-prioritized before persistence).
- Core domain model for:
  - source artifacts;
  - Jira issues;
  - GitHub pull requests;
  - generated briefs;
  - accepted baselines;
  - findings;
  - comparisons;
  - decisions.
- Persistence layer with migrations.
- [x] Typed environment configuration.
- [x] Basic authentication.
- Audit-friendly provenance model for source URLs, timestamps, revisions, and extraction metadata.
- [x] Initial test harness and local development workflow (pytest, mypy, Ruff, and CI).

### Exit Criteria

- A developer can run the app locally.
- The database can store imported source artifacts and versioned baselines.
- Core entities have automated tests around creation, update, and provenance behavior.

## Phase 1: Jira Issue Ingestion

**Goal:** Import selected Jira issues and preserve enough context to generate a reliable developer brief.

**Status:** Not started

### Deliverables

- Jira API integration using least-privilege credentials.
- Manual issue refresh by issue key or configured project.
- Imported fields:
  - issue key;
  - title;
  - description;
  - status;
  - issue type;
  - labels;
  - links;
  - comments when authorized;
  - acceptance criteria when present.
- Source revision and timestamp tracking.
- Import status and error reporting.

### Exit Criteria

- A user can import or refresh Jira issues from one configured Jira project.
- Imported records preserve source identifiers, URLs, timestamps, and revision information.
- Missing or unauthorized fields are represented explicitly instead of silently ignored.

## Phase 2: Developer Brief Generation

**Goal:** Convert Jira issue context into a structured, reviewable implementation brief.

**Status:** Not started

### Deliverables

- Brief sections for:
  - goal;
  - rationale;
  - in scope;
  - out of scope;
  - acceptance criteria;
  - dependencies;
  - constraints;
  - open questions;
  - related artifacts.
- Source-fact vs inference labeling.
- Ambiguity and missing-information flags.
- Human review workflow for accepting a generated brief as the baseline.
- Baseline version history.

### Exit Criteria

- A user can generate a draft brief from an imported Jira issue.
- A reviewer can accept, edit, or reject the generated brief.
- Accepted baselines are immutable versions that can be compared later.

## Phase 3: GitHub Implementation Ingestion

**Goal:** Link GitHub pull requests to Jira issues and ingest implementation context without requiring source-code analysis by default.

**Status:** Not started

### Deliverables

- GitHub API integration.
- PR linking by explicit Jira issue key and manual association.
- Imported PR metadata:
  - title;
  - description;
  - status;
  - author;
  - reviewers;
  - review status;
  - changed-file summaries;
  - review comments;
  - relevant commit metadata.
- Configuration flag for deeper code analysis, disabled by default.
- Provenance storage for all imported GitHub evidence.

### Exit Criteria

- A user can link one or more pull requests to an accepted Jira baseline.
- PR metadata and review context are visible without sending source code to an external model by default.
- Imported evidence can be traced back to specific PRs, comments, commits, or files.

## Phase 4: Implementation Findings

**Goal:** Identify meaningful implementation discoveries and route them through human confirmation.

**Status:** Not started

### Deliverables

- Candidate finding extraction for:
  - architectural constraints;
  - newly discovered dependencies;
  - effort changes;
  - blockers;
  - security or reliability concerns;
  - scope-change proposals.
- Confidence and uncertainty indicators.
- Evidence view for each candidate finding.
- Human workflow to confirm, edit, dismiss, or classify findings.
- Finding history and status tracking.

### Exit Criteria

- The system can surface candidate findings from linked PR context.
- A human can turn a candidate into a confirmed finding without altering the accepted baseline automatically.
- Confirmed findings retain evidence and reviewer action history.

## Phase 5: Requirement-To-Implementation Comparison

**Goal:** Compare accepted intent with actual implementation signals and expose reviewable alignment risks.

**Status:** Not started

### Deliverables

- Comparison engine for:
  - coverage gaps;
  - contradictions;
  - scope additions;
  - scope removals;
  - acceptance-criteria changes;
  - unresolved open questions.
- Traceability from each signal to requirement evidence and implementation evidence.
- Review workflow for dismissing or escalating comparison signals.
- Alignment summary per issue.

### Exit Criteria

- A manager or developer can see whether linked PR activity appears aligned with the accepted baseline.
- Each comparison signal includes supporting evidence and uncertainty.
- Users can distinguish material risks from informational differences.

## Phase 6: Manager Decision View

**Goal:** Give managers an actionable view of material changes, risks, blockers, and decisions needed.

**Status:** Not started

### Deliverables

- Issue-level manager summary.
- Decision queue with:
  - triggering evidence;
  - affected scope;
  - options;
  - estimated impact when supported;
  - recommendation only when evidence is sufficient.
- Decision recording with:
  - decision-maker;
  - timestamp;
  - rationale;
  - affected artifacts;
  - resulting baseline version.
- Baseline update flow for approved decisions.

### Exit Criteria

- A manager can review pending decisions for a Jira issue.
- Approved decisions create a new baseline version while preserving previous history.
- Decision provenance is visible and auditable.

## Phase 7: MVP Validation

**Goal:** Validate the end-to-end alignment loop with one Jira project and one or more GitHub repositories.

**Status:** Not started

### Deliverables

- End-to-end workflow:
  - import Jira issue;
  - generate draft brief;
  - accept baseline;
  - link PR;
  - ingest GitHub context;
  - extract candidate findings;
  - compare requirement to implementation;
  - record manager decision;
  - update baseline.
- Usability review with target developer and manager workflows.
- Operational logging and basic admin diagnostics.
- MVP documentation.

### Exit Criteria

- A pilot team can use the product for real Jira issues and GitHub PRs.
- Users can trace material summaries and decisions back to evidence.
- The product demonstrates reduced ambiguity or earlier surfacing of scope drift.
- The team has enough feedback to decide whether to add automation, broader integrations, or enterprise controls.

## Post-MVP Candidates

- Webhook-driven Jira and GitHub refresh.
- Deeper configurable code analysis.
- Multi-project and multi-repository rollout.
- Notification workflows for pending decisions.
- Role-based access controls beyond basic MVP needs.
- Dashboard-level delivery health views.
- Additional integrations beyond Jira and GitHub.
- Organization-level administration and onboarding.

## Explicit Non-Goals For The MVP

- Replacing Jira or GitHub.
- Autonomous approval, prioritization, ticket editing, merging, or project management.
- Fully autonomous multi-agent orchestration.
- Real-time event infrastructure before manual refresh or polling proves inadequate.
- Automated effort estimates presented as facts.
- Organization-wide rollout, multi-tenant billing, or enterprise administration.
