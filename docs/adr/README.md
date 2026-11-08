# Architecture Decision Records

Record a significant choice in an ADR. An ADR stays **Proposed** until the team has reviewed
and approved it in a pull request; record the actual approval in the ADR's approval field and
never mark a decision accepted without that evidence. Open decisions are tracked in the
[SRS open-decision register](../srs.md#9-open-decisions-od).

## Workflow

1. Copy [`template.md`](template.md) to `NNNN-short-title.md`.
2. Record the actual context, decision, alternatives, consequences, owners and status.
3. Cite at least one existing, relevant, distilled Second Brain note with a relative Markdown
   link (`SB-03`). Do not invent a note.
4. Submit the ADR through a PR. Update the SRS, architecture, traceability and `AGENTS.md`
   when the decision changes them.
5. When the team approves the ADR, change its status to Accepted and record the approval
   (reviewers, date and PR).

## Index

| ADR | Title | Status | Owners |
|---|---|---|---|
| [0001](0001-agent-skill-location.md) | Agent Skill location | Proposed | Person 2, Person 3 |
| [0002](0002-brain-note-schema.md) | Canonical Second Brain note schema | Proposed | Person 2 |
| [0003](0003-linking-naming-and-requirement-references.md) | Linking, file naming and requirement references | Proposed | Person 2, Person 3 |
| [0004](0004-documentation-locations.md) | Canonical documentation locations | Proposed | All members |
| [0005](0005-repository-toolchain.md) | Repository tooling (separate from the application stack) | Proposed | Person 3 |
| [0006](0006-quota-reference-and-accounting.md) | Quota reference, accounting model and search capacity | Proposed | Person 1 |
| [0007](0007-playlist-confirmation.md) | Two-phase playlist confirmation | Proposed | Person 3 |
| [0008](0008-oauth-client-and-scopes.md) | OAuth client type, scopes and token handling | Proposed | Person 1 |

No ADR has been accepted yet.
