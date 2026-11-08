---
title: Stage 1 Review
type: stage-review
stage: 1
status: draft — Person 1 section and audit section filled; reflections from Persons 2 and 3 pending
---

# Stage 1 Review (SB-02)

Format: work completed · what worked · what did not · outstanding problems · lessons · changes
for Stage 2. Each member writes their own reflections; the team agrees the summary at stage
close. Canonical location: `docs/stage-reviews/` (ADR 0004).

## Person 1 — SRS, traceability, development plan, research notes

**What worked**
- Splitting the SRS into FR / NFR / SK / TQ with source tags (`BRIEF-P`, `BRIEF-S`, `DERIVED`, `PROPOSED`) made it easy to separate fixed requirements from our own decisions.
- Checking Google's own documentation (not blog posts) before finalising quota requirements.

**What did not**
- The planning documents used two ID styles (`FR-1` vs `FR-01`) and three different research-note splits. This was resolved by following the baseline (`FR-01`; Person 1 writes the four YouTube API notes) but cost review time.
- Quota information in the original plan was out of date: `search.list` now has its own 100-calls/day bucket (SRS Appendix A). It was found only because the numbers were verified against the official page.

**What to change**
- Re-verify API quota and OAuth facts at the start of Stage 3 (Google states defaults are subject to change).
- Keep one agreed ID format and note-split in the baseline and never copy older versions.
- Convert "planned" links in `docs/traceability.md` to real wikilinks once Persons 2 and 3 merge their notes.

*Editorial notes (2026-11-08, audit):* the first "What did not" bullet originally read
"(`FR-01` vs `FR-01`)"; it was corrected to `FR-1` vs `FR-01`, the two styles described in SRS §1.4.
The last "What to change" item is superseded by ADR 0003: files under `docs/` use relative
Markdown links instead of wikilinks, and the traceability matrix was updated accordingly.
Person 1 should confirm both edits.

## Person 2 — Second Brain and `brain-ingest`

**Work completed (from repository evidence):** PARA vault, `brain/index.md` and `brain/log.md`
(log entry 2026-11-05); the `brain-ingest` skill and four research notes (MCP architecture,
MCP tools/resources, Agent Skills format, YouTube Data API) in PR #12, logged as ingestion runs on
2026-11-07.

**What worked · what did not · outstanding problems · lessons · changes for Stage 2:**
*to be written by Person 2.* Items Person 2 may want to cover: confirming the `author`/`created`
metadata of their notes (blocked until then, ADR 0002), the note-schema decision, and the
Stage 2 skills `brain-refine` and `brain-query` (proposed owner).

## Person 3 — Repository, `AGENTS.md`, CI

**Work completed (from repository evidence):** the three research notes (OAuth, quota
management, TF-IDF) in PR #17 carry `author: Person 3`. The development plan (task 6) assigns the
repository, `AGENTS.md` and CI to Person 3; the matching work is `.gitignore` and PR template
(PR #9), `AGENTS.md` (PR #10) and the six-job CI pipeline, validators, tests and workflow
documentation (PR #11). Which Git account made these commits is not mapped to a Person in the
repository; Person 3 should confirm.

**What worked · what did not · outstanding problems · lessons · changes for Stage 2:**
*to be written by Person 3.* Items Person 3 may want to cover: the CI failures on `main`
recorded in `docs/testing/results.md` (build, formatting, Brain validation), the GitHub ruleset
without required checks, and `local-check` (proposed owner).

## Stage 1 repository audit (AI-assisted session, 2026-11-08)

Carried out by Git user `ChadDadChag` with Claude Code; see the Brain note
`brain/projects/ai-session-2026-11-08-stage-1-audit.md`.

**Work completed:** eight proposed ADRs; skill, Brain and documentation validators enforcing the
skill location, note schema, link rules, requirement IDs and ADR citations; Person 1's notes
ingested and the duplicate overview merged; all broken wikilinks fixed; SRS 0.3.0 (confirmation
design, quota limits, single decision register); architecture, testing and traceability
updates; `brain-ingest` evaluation.

**What worked:** verifying every external fact against Google's and the MCP specification's
pages; recording decisions as Proposed ADRs instead of presenting them as approved; writing
tests first for new validator rules, which exposed a parser crash.

**What did not:** contributor metadata could not be completed without the contributors;
GitHub-side evidence (issues, reviews, Actions runs, rulesets) was not accessible; the original
briefs are not in the repository, so brief-level wording cannot be checked.

**Outstanding problems:** see the blockers in `docs/testing/results.md` (latest run) and the open
decisions `OD-01`…`OD-17`.

**Lessons:** keep requirement IDs, file names and link conventions enforced by CI from the start;
cheap automated checks prevent most of the drift found in this audit.

**Changes for Stage 2:** approve or amend ADRs 0001–0008; decide the "Before Stage 2" items in the
register; freeze the interface contracts; integrate the credential-protection and build/structure
branches; enable required status checks on `main`.

## Team summary

*To be agreed at stage close by all three members*, including the status of `OD-01`…`OD-17`
and their owners.
