# Project Build Control

This directory is the working control plane for creating and managing the AI Delivery Copilot. It separates durable direction, scheduled work, accepted decisions, and ideas that are still under consideration.

## Start here

1. Read [`instruction.md`](instruction.md) for product boundaries and delivery rules.
2. Read [`ROADMAP.md`](ROADMAP.md) and work from the earliest incomplete phase.
3. Read [`TECH_STACK.md`](TECH_STACK.md) for the selected implementation direction.
4. Check [`DECISIONS.md`](DECISIONS.md) before making an architectural or product choice.
5. Review [`THOUGHTS.md`](THOUGHTS.md) for open questions relevant to the work.

## Maintenance contract

| Document | Contains | Update when |
| --- | --- | --- |
| `instruction.md` | Durable principles, scope, architecture constraints, working rules | A long-lived rule changes |
| `ROADMAP.md` | Ordered outcomes, deliverables, exit criteria, and status | Work starts, completes, or is reprioritized |
| `TECH_STACK.md` | Selected technologies, requirements, and deferred complexity | A stack constraint or selection changes |
| `DECISIONS.md` | Accepted decisions with rationale and consequences | A consequential choice is accepted or superseded |
| `THOUGHTS.md` | Unresolved ideas, risks, assumptions, and questions | Something deserves consideration but is not committed scope |

Do not use `THOUGHTS.md` as a hidden backlog. An idea becomes planned work only when it is promoted into `ROADMAP.md`; a conclusion becomes binding only when recorded in `DECISIONS.md` or `instruction.md`.

## Status vocabulary

Use one of these labels for phases and meaningful deliverables:

- `Not started`
- `In progress`
- `Blocked`
- `Done`
- `Deferred`

When marking something `Blocked`, state the blocker and the decision or dependency needed to proceed.

## Change discipline

- Keep roadmap items outcome-oriented and testable.
- Add dates in ISO format (`YYYY-MM-DD`).
- Link decisions to the roadmap phase or artifact they affect.
- Preserve superseded decisions; mark them instead of deleting history.
- Review this directory whenever a milestone closes.
