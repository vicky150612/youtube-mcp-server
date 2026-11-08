# ADR 0002: Canonical Second Brain note schema

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 2 (owner of the Brain schema and `brain-ingest` conventions,
  per `docs/research/allocation.md`)
- **Approval record:** The schema below (decisions D-A and D-D of the Stage 1 audit) was
  approved in principle by the requesting maintainer (Git user `ChadDadChag`) on 2026-11-08
  during an AI-assisted session. Person 2's review through a pull request is pending.
- **Related requirements:** `SK-01`, `SB-01`, `SB-05`, `SB-06`, CI requirement "validation of
  brain notes (schema …)" (SRS §6.3), C1 of the Stage 1 audit
- **Relevant Brain notes:** [CI Pipeline](../../brain/projects/CI-Pipeline.md),
  [Agent Skills Format](../../brain/resources/Agent-Skills-Format.md)

## Context

Three incompatible schemas existed: the `brain-ingest` template wrote a singular `source`
field, the validator required `sources`, and contributors' notes used different field sets
(`source` and/or `sources`; `author`, `created` and `status` on some notes only;
`protocol_version` on two). Notes produced by the skill could fail validation.

## Decision

Every Markdown note under `brain/`, except `brain/index.md` and `brain/log.md`, has this YAML
frontmatter and no other keys:

| Key | Required | Type and rule |
|---|---|---|
| `title` | Yes | Non-empty string |
| `type` | Yes | `research` or `ai-session` |
| `author` | Yes | Non-empty list of strings: team role names (for example `Person 1`) or, where the role is not yet confirmed, the contributor's Git username. Never a real name or email address. |
| `created` | Yes | Date in `YYYY-MM-DD` form (the date the note was first created) |
| `tags` | Yes | Non-empty list of non-empty strings |
| `sources` | Yes | Non-empty list. Each entry is an `http(s)` URL or a repository-relative path to a file that exists. |
| `aliases` | No | List of non-empty strings. Aliases are display names only and are never used as wikilink targets (ADR 0003). |
| `status` | No | `draft` (written but not yet through the `brain-ingest` review) or `ingested`. |

- The skill's template file
  (`.claude/skills/brain-ingest/assets/research-note-template.md`) is the only template, and a
  unit test fills it in and runs the validator over it, so the skill and the validator cannot
  drift apart again.
- Unknown keys are errors. Information that previously lived in extra keys
  (`protocol_version`) is already stated in the note body, so removing the key loses nothing.
- Person 1's `status: draft-pending-brain-ingest` maps to `draft`; it becomes `ingested` only
  after the notes are actually processed with `brain-ingest`.
- **Attribution rule:** missing `author` or `created` values are never inferred or invented.
  They are added only after the contributor confirms them. Until then the validator reports
  the note, and the gap is listed as a blocker.

## Alternatives considered

- **Accept both `source` and `sources`.** Makes validation pass without fixing the
  inconsistency; the audit specification forbids competing schemas. Rejected.
- **Allow arbitrary extra keys.** Lets the schema drift again unnoticed. Rejected.
- **`author` as a single string.** A merged note (the consolidated YouTube Data API note) has
  more than one contributor; a list keeps the type consistent. Rejected.
- **Real names in `author`.** Personal data; the repository already uses role names. Rejected.

## Consequences

- All notes are migrated in the same change. Notes whose `author`/`created` values are
  missing stay invalid until their contributors confirm the values; this is reported as a
  blocker rather than hidden by loosening the validator.
- Adding a note type (for example a Brain-hosted stage review) requires amending this ADR.
