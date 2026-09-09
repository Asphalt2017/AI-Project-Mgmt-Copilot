# AI Delivery Copilot / Project Intelligence Platform

## Purpose

Build a pragmatic project-intelligence layer that keeps product intent, engineering scope, and implementation reality aligned.

The platform should help developers understand what they are being asked to build and why, while giving managers timely, evidence-backed feedback about what is actually being built. It should connect requirements in Jira with implementation activity in GitHub, surface meaningful changes and discoveries, and make decisions explicit before scope drift becomes expensive.

This document is the durable operating guide for the project. Future contributors and AI-assisted coding sessions should read it before proposing or making changes.

## Product vision

Create a shared, trustworthy view of delivery from requirement to implementation:

`Intent -> scoped work -> implementation -> engineering findings -> human decisions -> updated intent`

The product is not an autonomous project manager. It is a copilot that organizes context, identifies gaps, summarizes evidence, and asks the right people for decisions. Jira and GitHub remain the systems where teams plan and build; this platform connects their information and makes alignment visible.

The long-term outcome is that:

- Developers can quickly answer: Why does this work matter? What is in scope? What is out of scope? What are the acceptance criteria? What changed?
- Managers can quickly answer: What is being built? What changed during implementation? What risks or blockers emerged? What decision is needed? Does the implementation still match the original intent?
- Both groups can trace important claims back to the Jira issue, pull request, review, comment, commit, or recorded decision that supports them.

## Core problems

1. **Requirements lack usable implementation context.** Jira issues often describe a request without clearly separating the goal, rationale, boundaries, acceptance criteria, dependencies, and prior decisions.
2. **Scope is interpreted differently.** Developers and managers may hold different assumptions about what is included, excluded, or required for completion.
3. **Implementation findings are buried.** Architectural constraints, unexpected dependencies, effort changes, and reduced feasibility often appear in pull requests or review comments but do not reach the people responsible for scope and priority.
4. **Requirement drift is discovered too late.** The implementation may diverge from the original intent without a visible comparison or explicit approval.
5. **Decisions lose their provenance.** Teams struggle to reconstruct why a change was accepted, who approved it, and which requirement or implementation finding caused it.
6. **Status reporting is manual and shallow.** Managers receive activity summaries instead of concise explanations of material changes, risks, blockers, and decisions.

## Target users

### Developers

Developers need a compact implementation brief for each unit of work containing:

- the user or business goal;
- the reason the work matters;
- explicit in-scope and out-of-scope boundaries;
- acceptance criteria;
- dependencies, constraints, and related decisions;
- linked Jira issues and GitHub pull requests;
- changes to the brief since work began;
- unresolved questions or decisions.

Developers should be able to report findings through their normal GitHub workflow. The platform should identify possible findings but allow developers to correct, dismiss, or clarify them.

### Managers and product/delivery owners

Managers need concise, actionable summaries showing:

- what is currently being implemented;
- what materially changed and why;
- implementation findings and their evidence;
- scope drift or acceptance-criteria gaps;
- risks, blockers, and dependencies;
- decisions required, available options, and likely impact;
- whether implementation still appears aligned with intent;
- the approval history for accepted changes.

## Initial product scope

The first version should prove the core alignment loop with one Jira project and one or more GitHub repositories.

### 1. Jira issue ingestion

- Connect to Jira using supported APIs and least-privilege credentials.
- Import selected issues and relevant fields, including description, status, issue type, labels, links, comments when authorized, and acceptance criteria when present.
- Preserve source identifiers, timestamps, URLs, and revision information.
- Support manual refresh first; add webhook-driven refresh only when justified by MVP usage.

### 2. Developer brief generation

- Convert issue context into a structured draft with goal, rationale, in scope, out of scope, acceptance criteria, dependencies, constraints, open questions, and related artifacts.
- Distinguish source facts from LLM inferences.
- Mark missing or ambiguous information instead of inventing it.
- Require human confirmation before a generated brief becomes the accepted baseline.
- Version accepted baselines so later changes can be compared.

### 3. GitHub implementation ingestion

- Link pull requests to Jira issues using explicit issue keys or deliberate manual links.
- Ingest pull-request metadata, descriptions, changed-file summaries, review comments, review status, and relevant commit metadata.
- Store provenance for every extracted finding.
- Avoid sending source code to an external model by default; begin with metadata, descriptions, summaries, and authorized review content. Any deeper code analysis must be a deliberate configuration choice.

### 4. Implementation findings

- Extract candidate findings such as architectural constraints, newly discovered dependencies, effort changes, blockers, security or reliability concerns, and scope-change proposals.
- Show the supporting GitHub evidence and confidence or uncertainty.
- Let a human confirm, edit, dismiss, or classify each candidate.
- Never silently rewrite the accepted requirement from a finding.

### 5. Requirement-to-implementation comparison

- Compare the accepted brief with linked pull-request intent and confirmed findings.
- Identify potential coverage gaps, contradictions, additions, removals, or changes to acceptance criteria.
- Present these as reviewable signals, not definitive judgments.
- Make every signal traceable to both requirement and implementation evidence.

### 6. Manager decision view

- Summarize material changes, risks, blockers, and pending decisions.
- For each decision, present the triggering evidence, affected scope, reasonable options, and estimated impact when supported by available information.
- Record the human decision, decision-maker, timestamp, rationale, and affected artifacts.
- Feed approved decisions into a new version of the baseline while retaining history.

## Non-goals for the MVP

- Replacing Jira, GitHub, or established team workflows.
- Autonomous approval, prioritization, ticket editing, merging, or project management.
- A general-purpose chat assistant over all company data.
- Fully autonomous multi-agent orchestration.
- Complex agent frameworks, self-directed planning loops, or agent-to-agent delegation.
- Perfect semantic understanding of an entire codebase.
- Automated effort estimates presented as facts.
- Organization-wide rollout, multi-tenant billing, or enterprise administration before a single-team workflow is validated.
- Real-time event streaming infrastructure before polling or manual refresh becomes inadequate.
- Broad integrations beyond Jira and GitHub during the initial validation phase.

## Architecture direction

Keep the first implementation a modular monolith with clear internal boundaries.

### Initial stack

The MVP uses a Python-first modular monolith. The accepted direction is documented in `TECH_STACK.md` and DEC-004. Prefer a small, conventional stack that supports:

- a typed application layer;
- a relational database with migrations;
- background jobs for Jira and GitHub synchronization;
- server-rendered pages or a modest web client;
- isolated provider adapters;
- automated unit and integration tests;
- local development without cloud dependencies.

Do not introduce a distributed architecture, event-streaming platform, vector database, or agent framework until a validated requirement makes it necessary.

### Internal boundaries

Organize the modular monolith around business capabilities rather than external APIs:

- **Artifacts:** normalized source records and provenance.
- **Requirements:** Jira issue context, briefs, and accepted baselines.
- **Implementation:** GitHub pull requests, reviews, commits, and findings.
- **Alignment:** comparisons, gaps, and drift signals.
- **Decisions:** review queues, approvals, rationale, and baseline updates.
- **Integrations:** Jira, GitHub, and model-provider adapters.
- **Operations:** authentication, configuration, jobs, logging, and diagnostics.

Dependencies should point toward the domain. Provider-specific payloads must not become the core data model.

## Delivery rules

When planning or implementing work:

1. Read this file and `ROADMAP.md`.
2. Select the earliest incomplete milestone unless a deliberate reprioritization is recorded.
3. Define observable acceptance criteria before implementation.
4. Preserve provenance for imported facts and label generated inference.
5. Add or update automated tests with behavior changes.
6. Record durable architectural or product choices in `DECISIONS.md`.
7. Put unresolved ideas in `THOUGHTS.md`; do not silently turn them into scope.
8. Update roadmap status as part of completing a milestone.

## Definition of done

A work item is complete when:

- its acceptance criteria are met;
- relevant tests pass;
- failure behavior is explicit and observable;
- security and data-handling implications were considered;
- user-facing or operational documentation is updated;
- provenance and audit history remain intact;
- any consequential decision is recorded.

## AI-assisted contribution rules

- Treat generated content as a draft until a human accepts it.
- Never fabricate missing requirements, evidence, confidence, or estimates.
- Keep facts, inferences, and recommendations distinguishable in data and UI.
- Prefer narrow, reversible changes over speculative infrastructure.
- Do not modify Jira issues, GitHub artifacts, baselines, or decisions without an explicit user action.
- Avoid exposing credentials, source code, or private comments to model providers unless the configured policy explicitly permits it.
- Report uncertainty and missing context directly.

## Document ownership

The `.build` directory is the project-control plane:

- `README.md` explains how the documents fit together.
- `instruction.md` contains durable product and engineering constraints.
- `ROADMAP.md` defines sequence, deliverables, and progress.
- `TECH_STACK.md` defines implementation requirements and selected technologies.
- `DECISIONS.md` records accepted choices and their rationale.
- `THOUGHTS.md` holds unresolved proposals, questions, and risks.

Keep durable rules here, implementation documentation near the code it describes, and user documentation in a future top-level `docs/` directory.
