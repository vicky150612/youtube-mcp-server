---
title: Stage 1 Review
type: stage-review
stage: 1
status: draft — Person 1 section filled; Persons 2 and 3 to add theirs
---

# Stage 1 Review (SB-02)

Format: what worked · what did not · what to change. Each member fills in their own section; the team agrees the summary at stage close.

## Person 1 — SRS, traceability, development plan, research notes

**What worked**
- Splitting the SRS into FR / NFR / SK / TQ with source tags (`BRIEF-P`, `BRIEF-S`, `DERIVED`, `PROPOSED`) made it easy to separate fixed requirements from our own decisions.
- Checking Google's own documentation (not blog posts) before finalising quota requirements.

**What did not**
- The planning documents used two ID styles (`FR-01` vs `FR-01`) and three different research-note splits. This was resolved by following the baseline (`FR-01`; Person 1 writes the four YouTube API notes) but cost review time.
- Quota information in the original plan was out of date: `search.list` now has its own 100-calls/day bucket (SRS Appendix A). It was found only because the numbers were verified against the official page.

**What to change**
- Re-verify API quota and OAuth facts at the start of Stage 3 (Google states defaults are subject to change).
- Keep one agreed ID format and note-split in the baseline and never copy older versions.
- Convert "planned" links in `docs/traceability.md` to real wikilinks once Persons 2 and 3 merge their notes.

## Person 2 — Second Brain and `brain-ingest`
*(to be completed by Person 2)*

## Person 3 — Repository, `AGENTS.md`, CI
*(to be completed by Person 3)*

## Team summary
*(to be agreed at stage close: open decisions OD-01 to OD-09 and their owners)*
