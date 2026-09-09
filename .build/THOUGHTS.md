# Thoughts, Questions, and Risks

This is a review queue for ideas that are not yet committed work. Promote an item to `ROADMAP.md` when it is prioritized, or to `DECISIONS.md` when a conclusion is accepted.

## Open questions

- Who is the human approver for a baseline: issue owner, product owner, engineering lead, or a configurable role?
- What Jira field conventions will the pilot project use for acceptance criteria?
- How should explicit Jira-to-PR links be represented when one PR serves multiple issues?
- Which GitHub review comments are authorized for ingestion, and how will deleted or edited comments be handled?
- What is the smallest useful definition of an alignment signal for the first vertical slice?
- Which model-provider data retention and regional-processing constraints apply to the pilot?
- How long should normalized source snapshots and generated drafts be retained?

## Assumptions to validate

- Issue keys in PR titles or descriptions are common enough to support automatic link suggestions.
- PR descriptions and review discussion contain sufficient evidence for useful findings without source-code ingestion.
- Versioned baselines are understandable and useful to both developers and managers.
- Earlier visibility into scope drift is valuable enough to justify a separate review workflow.

## Product risks

- Too many low-confidence signals could make the decision view noisy and untrusted.
- A generated brief could appear authoritative even when the Jira source is incomplete.
- Stale synchronization could cause comparisons against outdated intent or implementation evidence.
- Teams may perceive the product as surveillance if activity summaries lack context or agency.
- A decision workflow that duplicates Jira approvals may increase process burden instead of reducing it.

## Technical risks

- Jira installations vary substantially in field configuration and API behavior.
- GitHub rate limits and permission scopes may constrain refresh behavior.
- Provenance can become ambiguous if source content is edited or deleted after ingestion.
- Provider payloads may leak into the domain model unless adapters normalize them early.
- LLM evaluation will require representative, permission-safe examples and explicit quality criteria.

## Candidate first vertical slice

Implement one narrow path before broad infrastructure:

1. Import a single Jira issue manually.
2. Store a revisioned source snapshot with provenance.
3. Generate a structured brief that labels facts, inference, and missing information.
4. Let a human edit and accept it as baseline version 1.
5. Display the accepted baseline and its source links.

This slice exercises the essential trust model while postponing GitHub ingestion and comparison complexity.
