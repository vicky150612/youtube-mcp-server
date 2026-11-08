# ADR 0004: Canonical documentation locations

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** All three members; Person 1 maintains the SRS and traceability
- **Approval record:** Pending team review through a pull request.
- **Related requirements:** `SE-01`, `SE-03`, `SE-05`, `SB-02`; Stage 1 audit issues I-7, D-3
- **Relevant Brain notes:** [CI Pipeline](../../brain/projects/CI-Pipeline.md)

## Context

Stage reviews were described as Brain notes in some places (`AGENTS.md` §11, `SB-02`) and as
`docs/` documents in others (`AGENTS.md` §3 tree, `docs/stage-reviews/`). Two inconsistent
open-decision registers existed: SRS §9 (`OD-01`…`OD-09`) and `AGENTS.md` §16, each listing
items the other lacked.

## Decision

| Artefact | Canonical location | Notes |
|---|---|---|
| Requirements | `docs/srs.md` | Highest-precedence repository source after the original briefs |
| Open-decision register | SRS §9 | `AGENTS.md` §16 points to it. Every entry has a description, options, a recommendation, an owner (marked unconfirmed until confirmed), a target milestone, linked ADRs and a status. |
| Architecture decisions | `docs/adr/NNNN-*.md` | Each cites at least one distilled Brain note (`SB-03`) |
| Stage reviews | `docs/stage-reviews/stage-N-review.md` | Satisfies `SB-02`; the Brain index links to it |
| Traceability | `docs/traceability.md` | Requirement → issue → PR → test → skill → Brain note |
| Test results and defects | `docs/testing/results.md`, `docs/testing/defects.md` | Historical runs are kept and labelled |
| Skill evaluations | `docs/testing/skill-evaluations.md` | `TQ-07` evidence |
| Research notes and AI sessions | `brain/` | Schema in ADR 0002 |

Stage reviews stay in `docs/` because the existing review is there, they are deliverables
reviewed in pull requests like other documents, and the Brain schema (ADR 0002) has no
stage-review note type.

## Alternatives considered

- **Stage reviews as Brain notes.** Matches the wording of `SB-02` most literally, but needs a
  new note type and moving Person 1's existing review. Rejected for now; can be revisited by
  amending ADR 0002.
- **Keep two decision registers.** They had already diverged. Rejected.
- **`AGENTS.md` as the register.** `AGENTS.md` is lower precedence than the SRS. Rejected.

## Consequences

- `AGENTS.md` §11 and §16, the SRS (`SB-02` wording and §9) and the Brain index are updated to
  point to these locations.
- Items that existed only in `AGENTS.md` §16 become new SRS entries (`OD-10` onwards); no item
  is closed by the merge.
