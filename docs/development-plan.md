---
title: Development Plan and Task Breakdown
type: plan
owner: Person 1
---

# Development Plan and Task Breakdown (SE-04)

Team of 3, 15 working days. Work is split by **independent module**; interfaces and fixtures are
frozen on Day 1 so nobody waits on another member. *(Status 2026-11-08: the Day-1 freeze has not
happened; the contracts are now drafted and a freeze before Stage 2 design work, on Day 4, is
proposed — `OD-17`.)* The application stack is
open (`OD-01`); the repository tooling is recorded in ADR 0005.

> **Status of assignments:** the module ownership in the first table is from the original plan
> (merged in PR #14). Every assignment marked *(proposed)* below was added on 2026-11-08 during
> the Stage 1 audit to close gaps; it is **unconfirmed** until the named member accepts it in a
> pull-request review.

## Implementation ownership

| Member | Modules | Requirements |
|---|---|---|
| Person 1 | YouTube provider, auth, quota, video similarity | `FR-01`, `NFR-01` *(proposed)*, `NFR-02.1`–`NFR-02.3`, `NFR-03.1`–`NFR-03.3`, `NFR-06.2` *(proposed)*, `NFR-07` *(proposed)*, `NFR-10` *(proposed, with Person 2)* |
| Person 2 | Channel similarity, recommendations, engagement analysis | `FR-02`, `FR-03`, `FR-04`, `NFR-10` *(proposed, with Person 1)* |
| Person 3 | MCP server, playlist planner/creator, `video-to-playlist` | `FR-05`, `NFR-09`, `NFR-04.2`, `NFR-04.3` *(proposed)*, `NFR-06.1` *(proposed)*, `SK-05` |

The original plan listed Person 1's requirements as "FR-01, NFR-09…03, NFR-03.3". The middle
entry was garbled (it reads as a range from `NFR-09` down to `NFR-03`). Based on Person 1's
modules (provider, auth, quota), it has been interpreted as `NFR-01`–`NFR-03`; **Person 1 must
confirm this interpretation**.

### Previously unassigned requirements *(proposed)*

| Requirement | Proposed owner | Reason |
|---|---|---|
| `SK-02` `brain-refine` | Person 2 | Owns the Brain, its schema and `brain-ingest` |
| `SK-03` `brain-query` | Person 2 | Same; drafts SRS/ADR sections from the Brain |
| `SK-04` `local-check` | Person 3 | Owns the repository, CI and validators |
| `NFR-01` Official API only | Person 1 | Provider is the only module calling the API |
| `NFR-04.1` Input validation | Person 3 at the MCP boundary; each module owner for its own inputs | Validation happens where input enters |
| `NFR-05.1` No secrets | Person 3 | Owns Gitleaks, `.gitignore` and CI |
| `NFR-05.2` No real personal data | All; Person 3 reviews fixtures | Every member adds fixtures |
| `NFR-06.1` Channel-less accounts | Person 3 | Playlist creation |
| `NFR-06.2` Graceful failure | Person 1 | Provider error mapping (typed errors in `docs/api/interfaces.md`) |
| `NFR-07` Provider isolation | Person 1 | Provider interface owner |
| `NFR-10` Deterministic computation | Person 1 and Person 2 | Similarity and analytics owners |
| `NFR-11` Documentation | All; Person 3 coordinates | Each member documents their modules |

## Research authorship vs implementation ownership

Research authorship and implementation ownership are different and both are credited:

| Topic | Research note author | Implementation owner |
|---|---|---|
| YouTube Data API overview | Person 2 and Person 1 (merged note) | Person 1 (provider) |
| Video, channel, playlist resources | Person 1 | Person 1 (provider); Person 2 and Person 3 consume |
| OAuth authentication | Person 3 | Person 1 (auth module) |
| Quota management | Person 3 | Person 1 (quota module) |
| TF-IDF and cosine similarity | Person 3 | Person 1 (video similarity), Person 2 (channel similarity) |
| MCP architecture, tools and resources | Person 2 | Person 3 (MCP server) |
| Agent Skills format | Person 2 | Skill owners |
| YouTube Data API errors | Person 2 | Person 1 (error mapping) |

Person 3's research on OAuth and quota does not move those modules away from Person 1; Person 3
reviews the authentication and quota pull requests as the subject-matter researcher.

## Coordination responsibilities *(proposed)*

| Responsibility | Owner |
|---|---|
| Canonical Brain note schema (ADR 0002) | Person 2 |
| Skill location decision (ADR 0001) | Person 2 and Person 3 |
| CI and validation scripts | Person 3 |
| Approving requirement changes (SRS) | All three members by PR review; Person 1 edits the SRS |
| Traceability matrix | Person 1 |
| Approving architecture decisions (ADRs) | All three members by PR review |
| Shared interface contracts (`docs/api/interfaces.md`, `OD-17`) | Person 1 (provider models), Person 3 (MCP tool and proposal shapes); all three approve |

These do not contradict `AGENTS.md`: every change still needs a pull request with at least one
human review.

## Phases

| Stage | Days | Goal |
|---|---|---|
| 1 Requirements | 1–3 | SRS, Second Brain, `brain-ingest` + ≥10 notes, `AGENTS.md`, repo + CI skeleton |
| 2 Design | 4–7 | Architecture/UML, ADRs, `brain-refine`, `brain-query`, first `local-check`; module skeletons against mocks |
| 3 Build/Test/CI | 8–12 | All FRs implemented, integration, negative tests, `video-to-playlist`, defect log |
| 4 Review | 13–15 | Docs, live demo, release tag, changelog |

(Feature development overlaps Stages 2–3 by design; integration starts by Day 6.)

## Stage 1 tasks (each = one GitHub Issue)

| # | Task | Owner | Est. |
|---|---|---|---|
| 1 | Write `docs/srs.md` (FR/NFR/SK/TQ) | P1 | 4–5 h |
| 2 | Write `docs/development-plan.md`; update the Brain-note column of the existing `docs/traceability.md` once notes are ingested | P1 | 1 h |
| 3 | Resolve open decisions `OD-01`…`OD-17` (register in SRS §9) | All | 1 h |
| 4 | Research and ingest 4 notes (API overview, Video, Channel, Playlist) | P1 | 2 h |
| 5 | PARA vault, `index.md`, `log.md`, `brain-ingest`, 3 notes | P2 | 9–11 h |
| 6 | Repo, `AGENTS.md`, CI, validators, 3 notes | P3 | 9–12 h |
| 7 | Review each other's PRs; Stage 1 review note | All | 1–2 h |

## Day-1 interface freeze (carry into Stage 2)

Internal `Video`, `Channel`, `PlaylistConstraints`, `UserLibrarySnapshot` models; `YouTubeProvider`
interface; service function signatures for FR-01…FR-05; MCP tool list. Changes after the freeze
go through PRs.

*Status 2026-11-08:* not frozen. The models, provider operations and typed errors are drafted in
[`docs/api/interfaces.md`](api/interfaces.md); freezing them before Stage 2 design work (Day 4)
is proposed in `OD-17` and requires all three members' approval.
