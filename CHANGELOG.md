# Changelog

## Unreleased

### Added

- Added the six-job GitHub Actions CI pipeline, secret scanning, and local skill/Brain
  validators with deterministic tests.
- Added proposed ADRs 0001–0008 (skill location, note schema, linking conventions,
  documentation locations, repository tooling, quota model, playlist confirmation, OAuth).
- Added a documentation validator and CI job (no wikilinks outside the Brain, relative links and
  anchors, canonical requirement IDs, ADR Brain citations).
- Added draft shared interface contracts (`docs/api/interfaces.md`), the `brain-ingest` note
  template, a YouTube Data API errors research note, a skill-evaluation record and a defect log.

### Changed

- Skill validation now covers `.claude/skills/` and fails when skills are missing; Brain
  validation enforces one note schema and checks heading links, relative links and requirement
  IDs.
- Rewrote the `brain-ingest` skill; processed Person 1's notes; merged the duplicate YouTube Data
  API overview notes; renamed spaced note files; fixed all broken wikilinks; rebuilt the Brain
  index and made the log chronological.
- SRS 0.3.0 (draft, not approved): two-phase playlist confirmation, quota-estimate limits, search
  capacity, external-fact tagging, corrected `NFR-09`, single open-decision register.
- Updated architecture, testing, traceability, development plan, research allocation, stage
  review, PR template, `AGENTS.md` and `README.md` to match.

### Fixed

- `scripts/frontmatter.py` no longer crashes on impossible dates (DEF-004).
