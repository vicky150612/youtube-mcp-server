# ADR 0003: Linking, file naming and requirement references

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 2 (Brain conventions) and Person 3 (documentation tooling and CI)
- **Approval record:** Pending team review through a pull request.
- **Related requirements:** `SB-01`, `SE-05`, `NFR-11`; Stage 1 audit issues C2, I-6, I-8, N-3
- **Relevant Brain notes:** [Agent Skills Format](../../brain/resources/Agent-Skills-Format.md),
  [CI Pipeline](../../brain/projects/CI-Pipeline.md)

## Context

The audit found 33 broken wikilinks, Obsidian wikilinks inside `docs/` (which GitHub renders
as plain text), three styles of requirement reference (backtick IDs, `[[FR-1]]` wikilinks and
relative links to `../../docs/srs.md`), unpadded IDs (`FR-1`) that differ from the canonical
`FR-01`, links that relied on frontmatter aliases as targets, and a mix of spaced and
hyphenated note filenames. There were two local Obsidian configurations (repository root and
`brain/`), so the vault root was ambiguous.

## Decision

### Vault root

`brain/` is the Obsidian vault. Wikilinks resolve only to notes inside `brain/`. Obsidian
workspace configuration (`.obsidian/`) is per-user and is not committed.

### Inside the Brain (`brain/`)

1. Link notes with wikilinks whose **target is the note's filename** without `.md`. Use the
   alias form only for display text: `[[OAuth-Authentication|OAuth 2.0 Authentication]]`.
   Frontmatter `aliases` are never link targets.
2. A heading link (`[[Note#Heading]]`) must name a heading that exists in the target note.
3. **Planned notes are not linked.** List them as plain text, for example
   "YouTube MCP Server project note (planned, not yet created)". Do not create empty notes to
   make a link resolve.
4. Wikilink syntax inside inline code or fenced code blocks is literal text, not a link. Use
   code formatting when quoting a historical or example link.
5. Links from a Brain note to repository documents outside the vault use relative Markdown
   links, for example `[SRS](../../docs/srs.md)`.

### Outside the Brain (`docs/`, `README.md`, `AGENTS.md`, other repository Markdown)

1. Use relative Markdown links. Obsidian wikilinks are not allowed outside code formatting.
2. Link targets must exist, and a `#anchor` on a Markdown target must match a heading in that
   file (GitHub heading-anchor rules).
3. Refer to Brain notes with relative links to the note file.

### Requirement references (everywhere)

1. Write requirement IDs in canonical zero-padded form, normally in backticks: `FR-01`,
   `NFR-02.1`, `TQ-06`, `SK-05`, `SE-06`, `SB-03`, `AIP-01`, `OD-09`, `AC-05.3`.
2. The SRS (`docs/srs.md`) is the requirement index. Requirements are not Brain notes, so they
   are never wikilinked. A Brain note's "Related Requirements" section lists IDs and links once
   to the SRS with a relative link.
3. An unpadded ID (for example `FR-1`) outside code formatting is an error. Every canonical ID,
   in or out of code formatting, must be defined in the SRS.

### File naming

New notes use hyphen-separated filenames (`YouTube-Video-Resource.md`); AI-session notes use
`ai-session-YYYY-MM-DD-topic.md`. Existing spaced filenames are renamed with every reference
updated in the same change: `CI Pipeline.md`, `YouTube Channel Resource.md`,
`YouTube Playlist Resource.md` and `YouTube Video Resource.md`. `YouTube Data API Overview.md`
is merged into `YouTube-Data-API.md` (audit issue D-1).

### Enforcement

`scripts/validate_brain.py` checks Brain wikilinks, heading links, relative links and
requirement IDs. `scripts/validate_docs.py` checks the same rules for repository Markdown
outside the Brain. Both run in CI and print the file, line and offending link or ID.

## Alternatives considered

- **Create one Brain note per requirement** so `[[FR-01]]` resolves. Duplicates the SRS and
  creates near-empty notes. Rejected.
- **Resolve aliases as link targets in the validator.** Obsidian does not do this, so links
  would pass CI but break in the vault. Rejected.
- **Repository root as the vault.** Would let Obsidian open `docs/`, but mixes per-user
  configuration with the repository and widens link resolution beyond the Brain. Rejected.
- **Keep spaced filenames.** Works in Obsidian but is error-prone in shells and URLs. Rejected
  for consistency; renames are done once with all references updated.

## Consequences

- Historical log entries that used old link targets are rewritten to the current targets or to
  code-formatted text; the log records that this normalisation happened.
- Contributors need the relative-link rule when writing in `docs/`; CI enforces it.
- The `.obsidian/` ignore rule was added to `.gitignore` on 2026-11-08, after the
  credential-protection change was integrated, with a hygiene test.
