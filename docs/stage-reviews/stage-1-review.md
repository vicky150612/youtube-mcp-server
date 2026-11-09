---
title: Stage 1 Review
type: stage-review
stage: 1
status: draft — Person 1, Person 2 and audit sections filled; Person 3 section is an evidence-based draft awaiting Person 3
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

*Reflection points under "What worked", "What did not" and "Lessons learned" are Person 2's own
answers (given on 2026-11-09); the other points summarise the repository record and were
reviewed by Person 2.*

**Work completed**

*Individual work (evidence: commit `8e80f55`, 2026-11-07, merged in PR #12; `brain/log.md`):*
- Set up the Obsidian Second Brain with the PARA structure, `brain/index.md` and `brain/log.md`.
  The log records the vault setup on 2026-11-05; the content was first committed on 2026-11-07
  (empty `index.md`/`log.md` placeholders already existed from the project skeleton, `edaa883`).
- Developed the `brain-ingest` Agent Skill (`.claude/skills/brain-ingest/SKILL.md`).
- Researched, wrote and ingested four notes — MCP architecture, MCP tools and resources, Agent
  Skills format and the YouTube Data API overview — logging each run with topic, source,
  destination and contributor, and updating the index for each.

*Stage 1 audit and consistency work (2026-11-08 to 2026-11-09, AI-assisted with Claude Code; all 19
commits on branch `fix/stage-1-audit-consistency`, plus `63acd08`, were made under Person 2's Git
identity; see `brain/projects/ai-session-2026-11-08-stage-1-audit.md`):*
- Directed the audit and approved its key decisions in principle (skill location, note schema,
  confirmation approach), which are recorded as Proposed ADRs 0001–0008 awaiting team review.
- Rewrote `brain-ingest` with a canonical note template, validation and pull-request steps;
  evaluated it on a new topic and a duplicate input, which created the YouTube Data API errors
  note and confirmed duplicate detection (evaluation cases E1 and E2,
  `docs/testing/skill-evaluations.md`).
- Validated Brain metadata and wikilinks with the new validators: fixed all 33 broken links,
  migrated every note to one schema, merged the duplicate API overview with both contributors
  credited, and made the activity log chronological.
- Corrected contributor attribution after confirming the Person 2 role (`a0cccaa`, 2026-11-09).

*Team work:* the research notes of Persons 1 and 3 and the SRS were integrated into the Brain
during the audit; their authorship is unchanged.

**What worked**
- Delivering my own assigned work: the `brain-ingest` skill and the Second Brain it feeds.
- *(Repository record)* Every 2026-11-07 ingestion run was logged with its source and
  contributor, which later made it possible to verify attribution from the log and Git history.

**What did not (what failed)**
- Keeping all our work consistent while it was done in parallel.
- *(Repository record)* Examples: the original skill template wrote a singular `source` field that
  the CI validator rejected (DEF-002); several of my notes linked to notes that did not exist yet
  (part of DEF-003); the skill lived in `.claude/skills/` while the CI validator scanned `skills/`,
  so skill validation passed without checking anything (DEF-001); notes did not record
  `author`/`created`, which had to be reconstructed later.

**Outstanding problems**
- ADRs 0001–0003 (skill location, note schema, linking rules) are proposed and await team review.
- The `brain-ingest` evaluation is a self-evaluation by the same AI-assisted session; an
  independent re-run by a team member is recommended.
- `brain-refine` and `brain-query` (Stage 2) are not started; Person 2 is the proposed owner.

**Lessons learned**
- Discuss more as a team and ensure a good flow of work between members.

**Changes for Stage 2**
- Agree shared conventions (schema, file locations, link rules) before parallel work starts, and
  review them together.
- Run `validate_brain.py` and `validate_skills.py` before every Brain or skill pull request.
- Record `author` and `created` in each note when it is created.
- Implement and evaluate `brain-refine` and `brain-query`.

## Person 3 — Repository, `AGENTS.md`, CI

> **Draft prepared from repository evidence on 2026-11-09 — not yet reviewed or confirmed by
> Person 3.** Person 2 identified Person 3 as the Git identity "Vicky"; commit `a5caa34` by that
> identity is also titled "(Person 3)". Person 3 should check every statement, answer the
> questions below and then remove this notice.

**Work completed**

*Assigned and completed (evidence: commits by the Git identity "Vicky"):*
- Project skeleton (`edaa883`, 2026-11-03) and `.gitignore` and PR template (`eba1a23`,
  2026-11-03; PR #9).
- `AGENTS.md` (`0f2421e`, 2026-11-06; PR #10).
- Six-job CI pipeline, the CI build check, skill and Brain validators, 21 tests, Gitleaks
  configuration and workflow, testing and traceability documentation, and the CI Pipeline
  AI-session note (`cedd5a0`, 2026-11-07; PR #11).
- Three research notes — OAuth 2.0 authentication, YouTube API quota management, TF-IDF and cosine
  similarity — with `author: Person 3`, plus updates to `AGENTS.md` (per-bucket quota and live-test
  rules), the architecture overview, research allocation, testing documentation, results and
  traceability (`a5caa34`, 2026-11-07; PR #17).

*Assigned, not yet started:* `local-check` (Stage 2; proposed owner, unconfirmed).

*Recorded by Person 3 (`docs/testing/results.md`, 2026-11-07):* on `main`, the Build, Lint (format)
and Brain validation jobs failed; the causes were later logged as DEF-006, DEF-007, DEF-002 and DEF-003.
These were fixed during the Stage 1 audit, not in Person 3's commits.

**What worked** — *to be written by Person 3.*
> *Question for Person 3:* what went well in your Stage 1 work (repository setup, AGENTS.md, CI, research notes)?

**What did not (what failed)** — *to be written by Person 3.*
> *Question for Person 3:* what was difficult or did not work? Related evidence: DEF-001, DEF-006, DEF-007 and the main ruleset without required status checks.

**Outstanding problems** *(repository record)*
- Required status checks on `main` are not configured (needs a GitHub admin).
- `local-check` is not started.
- The CI note's `created` date is recorded as 2026-11-07 (first commit); the log dates the CI work
  to 2026-11-06. *Question for Person 3: which is correct?*

**Lessons learned** — *to be written by Person 3.*
> *Question for Person 3:* what would you do differently?

**Changes for Stage 2** — *to be written by Person 3.*
> *Question for Person 3:* which changes do you propose? Do you accept the proposed local-check ownership?

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

**What did not:** contributor metadata had to be reconstructed from Git evidence afterwards;
GitHub-side evidence (issues, reviews, Actions runs, rulesets) was not accessible; the original
briefs are not in the repository, so brief-level wording cannot be checked.

**Outstanding problems:** see the blockers in `docs/testing/results.md` (latest run) and the open
decisions `OD-01`…`OD-17`.

**Lessons:** keep requirement IDs, file names and link conventions enforced by CI from the start;
cheap automated checks prevent most of the drift found in this audit.

**Changes for Stage 2:** approve or amend ADRs 0001–0008; decide the "Before Stage 2" items in the
register; freeze the interface contracts; review and merge this branch (which now integrates the
credential-protection and build/structure work); enable required status checks on `main`.

## Team summary

*To be agreed at stage close by all three members*, including the status of `OD-01`…`OD-17`
and their owners.
