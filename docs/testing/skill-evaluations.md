# Skill evaluations (`TQ-07`)

Record every skill evaluation run before a stage submission. Record only runs that actually
happened, including failures. A skill is not "evaluated" until a row exists here.

## Evaluation procedure

1. Choose representative inputs: at least one new topic, one input that duplicates existing
   material, and one existing draft to process.
2. Run the skill exactly as written in its `SKILL.md`, on a branch.
3. Check each criterion below and record the evidence (file, validator output, log entry).
4. Run `python scripts/validate_skills.py --require <skill>` and the validators the skill names.
5. Record failures and follow-up actions; fix the skill through a pull request if it misled the
   operator.

Criteria for `brain-ingest`: correct frontmatter (ADR 0002), accurate summaries checked against
the sources, valid source attribution, correct PARA placement, valid requirement references,
correct wikilinks, duplicate detection, index update, log update.

## Stage 1 — `brain-ingest` (`SK-01`), 2026-11-08

- **Skill version:** `.claude/skills/brain-ingest/SKILL.md` as rewritten on branch
  `fix/stage-1-audit-consistency` (commit `5bd3bf9`).
- **Operator:** AI agent (Claude Code) in a session run by Git user `ChadDadChag`.
- **Limitation of this evaluation:** the same AI session that rewrote the skill also executed
  and scored it, so this is a self-evaluation. A team member should repeat at least case E1
  independently before the Stage 1 submission.
- **Skill format check:** `python scripts/validate_skills.py --require brain-ingest` — passed
  (see [results.md](results.md)).

| Case | Input | Expected | Actual result | Pass |
|---|---|---|---|---|
| E1 — new topic | Google's YouTube Data API errors reference and four method pages | New schema-valid note in `brain/resources/`, sourced, linked, indexed, logged | `brain/resources/YouTube-API-Errors.md` created; validator reports no errors for it; added to the index; log 2026-11-08 Activity 6 | Yes |
| E2 — duplicate | YouTube Data API getting-started page | Existing note detected; no new note | `YouTube-Data-API.md` found in Step 3; no note created; log Activity 7 | Yes |
| E3 — process drafts | Person 1's three `status: draft` resource notes (C5) | Notes verified against sources, corrected, linked, `status: ingested`, logged | Three notes updated with seven source-verified corrections; log Activity 3 | Yes, with gaps (see below) |

| Criterion | E1 | E2 | E3 | Evidence |
|---|---|---|---|---|
| Correct frontmatter | Pass | n/a | Pass | `scripts/validate_brain.py` reports no errors for these notes |
| Accurate summaries | Pass | n/a | Pass | Each finding traced to the fetched Google page on 2026-11-08; unverified points marked "not stated" |
| Source attribution | Pass | n/a | Pass | URLs and access dates in `sources` and the Sources section |
| PARA placement | Pass (`resources/`) | n/a | Pass (`resources/`) | File paths |
| Requirement references | Pass | n/a | Pass | Canonical IDs; validator checks they exist in the SRS |
| Wikilinks | Pass | n/a | Pass | Validator: zero broken wikilinks |
| Duplicate detection | Pass | Pass | Pass (D-1 duplicate merged) | Log Activities 4, 6, 7 |
| Index update | Pass | Not needed | Pass | `brain/index.md` |
| Log update | Pass | Pass | Pass | `brain/log.md` 2026-11-08 |

**Failures and gaps found**

- **Contributor role unknown:** for E1 the operator's team role is not recorded, so `author`
  uses the Git username `ChadDadChag`, as ADR 0002 allows. Replace it with the role once
  confirmed.
- **Step 9 (pull request) not yet completed:** the changes are committed on a branch; no PR has
  been opened, so `SB-05` review is outstanding for all three cases.
- **Earlier version failure (historical):** the skill as merged on 2026-11-07 wrote a singular
  `source` field that the validator rejected (audit C1). That version would have failed the
  frontmatter criterion; the rewrite fixed it, and a unit test now fills the template and
  validates it.

**Result:** `brain-ingest` meets all criteria in this self-evaluation, pending an independent
re-run by a team member and the pull-request review.

## Other skills

| Skill | Stage | Status |
|---|---|---|
| `brain-refine` (`SK-02`) | 2 | Not implemented; not evaluated |
| `brain-query` (`SK-03`) | 2 | Not implemented; not evaluated |
| `local-check` (`SK-04`) | 2 | Not implemented; not evaluated |
| `video-to-playlist` (`SK-05`) | 3 | Not implemented; not evaluated |
