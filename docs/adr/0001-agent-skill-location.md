# ADR 0001: Agent Skill location

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 2 (author of `brain-ingest`) and Person 3 (CI maintainer)
- **Approval record:** The recommended option was approved in principle by the requesting
  maintainer (Git user `ChadDadChag`) on 2026-11-08 during an AI-assisted session. Team
  review through a pull request is pending; this ADR is not accepted until that review exists.
- **Related requirements:** `SK-01`…`SK-05`, `SB-03`, CI requirement "validation of every
  `SKILL.md`" (SRS §6.3), C3 of the Stage 1 audit
- **Relevant Brain notes:** [Agent Skills Format](../../brain/resources/Agent-Skills-Format.md),
  [CI Pipeline](../../brain/projects/CI-Pipeline.md)

## Context

The only Agent Skill, `brain-ingest`, lives at `.claude/skills/brain-ingest/SKILL.md`.
`AGENTS.md` §3 showed a top-level `skills/` directory, and `scripts/validate_skills.py` scanned
only `skills/`. Because that directory does not exist, the validator reported "no SKILL.md
files exist" and passed while the real skill was never validated.

The Agent Skills specification requires a skill to be a directory containing `SKILL.md`
whose `name` matches the directory; it does not prescribe where skill directories live
([Agent Skills Format](../../brain/resources/Agent-Skills-Format.md)). The team's AI coding
tool (Claude Code) discovers project skills under `.claude/skills/`.

## Decision

1. `.claude/skills/<skill-name>/SKILL.md` is the single canonical location for the project's
   Agent Skills. No copies are kept elsewhere.
2. `scripts/validate_skills.py` scans `.claude/skills/`. It fails when the directory is
   missing, when it contains no skills, or when a skill named with `--require` is absent.
   CI runs it with `--require brain-ingest`; later stages add their required skills.
3. Besides the specification's frontmatter rules, the validator enforces the project rule in
   `AGENTS.md` §12 that each skill documents its purpose, inputs, workflow, outputs and
   limitations, and that relative links inside a skill point to files that exist.
4. `AGENTS.md`, `README.md` and the testing documentation refer to this location.

## Alternatives considered

- **Move skills to a top-level `skills/` directory.** Matches the old `AGENTS.md` tree and is
  tool-neutral, but Claude Code would no longer discover the skill without extra
  configuration, and the Brain note already documents the `.claude/skills/` path. Rejected.
- **Keep copies in both locations, or symlink.** Duplicates drift; Windows symlinks are
  unreliable for the team. Rejected (the audit specification forbids duplicates).
- **Scan several roots.** Adds ambiguity about which copy is authoritative. Rejected for now.

## Consequences

- CI now validates the real skill, and an empty or missing skill directory fails CI instead of
  passing silently. Two existing tests that asserted the old "empty state passes" behaviour
  are inverted.
- The location is tied to one AI tool's convention. Whether the product skill
  `video-to-playlist` (`SK-05`, Stage 3), which end users' clients load, belongs here or needs a
  distribution location is **not decided**; revisit this ADR in Stage 3.
