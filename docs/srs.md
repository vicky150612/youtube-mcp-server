---
title: Software Requirements Specification — YouTube Video Intelligence MCP Server
type: srs
version: 0.2.0
status: Ready for review — awaiting approval by all three members
owner: Person 1
---

# Software Requirements Specification (SRS)
## YouTube Video Intelligence MCP Server

| Field | Value |
|---|---|
| Version | 0.2.0 (Stage 1, ready for review) |
| Owner | Person 1 |
| Reviewers | Person 2, Person 3 |
| Status | Ready for review — approve via PR (see §10) |
| Replaces | the draft SRS in `main` (same IDs; adds detail, acceptance criteria, research updates) |
| Basis | `Project_1_YouTube_MCP.pdf`, `SDLC_and_Workflow.pdf`, the team's Stage 1 baseline (`STAGE_1_BASELINE.md`) |

---

## 1. Introduction

### 1.1 Purpose
This SRS is the reference for what the system must do and the constraints it must respect. It contains **functional requirements (FR)**, **non-functional requirements (NFR)** and **skill requirements (SK)** as demanded by SE-01 of the SDLC brief, plus the testing (TQ), Second Brain (SB), engineering (SE) and AI-policy (AIP) requirements that the project is assessed against.

### 1.2 Problem and solution
YouTube's engagement algorithm tends to surface distracting content instead of focused educational material, and building a curated playlist by hand is slow. This project provides an MCP server through which an AI client can discover, analyse and curate YouTube videos for an authorised user, using objective metadata from the **official YouTube Data API v3**, and create a constrained playlist in the user's account **only after explicit confirmation**.

### 1.3 Source tags
Every requirement carries a **Source** tag so nobody mistakes a team decision for a brief requirement.

| Tag | Meaning |
|---|---|
| **[BRIEF-P]** | Stated in `Project_1_YouTube_MCP.pdf` |
| **[BRIEF-S]** | Stated in `SDLC_and_Workflow.pdf` |
| **[DERIVED]** | Logically required to satisfy a brief requirement; wording is ours |
| **[PROPOSED]** | Team default/decision proposed here; needs approval. Not a brief requirement |

Items still undecided are listed in §9 as `OD-n` and marked **OPEN** where they appear.

### 1.4 ID conventions
`FR-nn` functional · `NFR-nn` non-functional · `SK-nn` skill · `TQ-nn` testing · `SB-nn` Second Brain · `SE-nn` software engineering · `AIP-nn` AI policy · `OD-nn` open decision · `AC-nn.m` acceptance criterion *m* of `FR-nn`.

This repository uses the **zero-padded canonical IDs** from `AGENTS.md` (`FR-01`…`FR-05`, `NFR-01`…`NFR-08`, `TQ-01`…`TQ-08`, `SK-01`…`SK-05`). The Stage 1 baseline writes the same functional requirements as `FR-1`…`FR-5`. The eight **parent NFRs (`NFR-01`…`NFR-08`) are unchanged from the draft SRS already in `main`**; this version adds detailed sub-requirements (`NFR-02.1`, `NFR-02.2`, …) with acceptance criteria, and three new parents (`NFR-09` to `NFR-11`) for items the draft did not cover. IDs are never reused or renumbered once referenced by an issue, PR, test or note; retired requirements are marked **Deprecated**.

### 1.5 Definitions

| Term | Meaning |
|---|---|
| MCP | Model Context Protocol: how AI clients connect to servers exposing tools, resources and data |
| Authorised user | A Google user who has completed OAuth consent for this application |
| Library | The authorised user's liked videos, subscriptions and playlists (the only personal data sources used) |
| Provider | The module isolating all YouTube Data API v3 calls behind an interface (SE-06) |
| Quota unit | YouTube Data API cost unit; default budget 10,000 units/day |
| Fixture | Recorded or synthetic API response used for tests; contains no real user data |
| Skill | A `SKILL.md` folder following the Agent Skills format (agentskills.io) |
| Second Brain | Obsidian vault in `brain/` organised with PARA |
| Untrusted metadata | Video/channel titles, descriptions, tags and any other YouTube-supplied text |

---

## 2. Overall description

### 2.1 Product perspective
```
AI client (Claude / ChatGPT / Gemini …)
        │  MCP (tools, resources, skills)
        ▼
  MCP server ──► services (similarity, recommendations, analysis, playlist)
                        │
                        ▼
              YouTube provider interface ──► YouTube Data API v3 (official)
```
The server is client-agnostic: no behaviour may be hard-coded to a single AI product. **[DERIVED]**

### 2.2 Users
- **End user** — an authorised YouTube user who talks to an AI client.
- **Developers (team)** — the three members who build, test and review the system.

### 2.3 Fixed constraints (summary)
1. Official YouTube Data API v3 only; no scraping or unofficial APIs. **[BRIEF-P]**
2. No watch-history data exists in the API; it is out of scope. **[BRIEF-P]**
3. No related-videos or related-channels endpoint; similarity is computed by us from metadata. **[BRIEF-P]**
4. Default quota 10,000 units/day; do not create extra Google Cloud projects to obtain more. **[BRIEF-P]**
   *Research update (Google's quota page, last updated 2026-11-03): `search.list` and `videos.insert` now have their **own** buckets of 100 calls/day each (1 per call); the 10,000 units/day covers all other endpoints. See NFR-02.1/NFR-02.2 and Appendix A. [DERIVED from research — verify in your own Cloud console Quotas page]*
5. OAuth refresh tokens in Testing mode expire after 7 days. **[BRIEF-P]**
6. A Google account without a YouTube channel cannot create playlists. **[BRIEF-P]**
7. Playlist creation needs explicit user confirmation. **[BRIEF-P]**

### 2.4 Out of scope
- Watch-history ingestion or analysis.
- Scraping, unofficial APIs, or downloading video content.
- Playlist modification/deletion beyond creating a new playlist and adding items to it **[PROPOSED]**.
- Any feature requiring more quota than the default allocation.

### 2.5 Assumptions
- Each user runs against their own Google Cloud project in Testing mode with the default quota. **[DERIVED]**
- Library data (liked videos, subscriptions, playlists) is reachable through the official API with the granted scopes. Liked videos can be read with `videos.list?myRating=like` (returns video resources, no like-time) or via `playlistItems.list` on the channel's likes playlist (`contentDetails.relatedPlaylists.likes`; each item's `snippet.publishedAt` is the time the item was added). Time-based trends for likes therefore use the playlist route; see OD-05 and the research notes. **[DERIVED]**

---

## 3. Functional requirements (FR)

Common conventions for FR-01 to FR-04 **[PROPOSED]**:
- Results are returned in **descending score order** and include a score and a short, explainable reason (matching features) per item.
- The result limit `n` is a parameter; default 10 (OD-03).
- Output uses the common internal `Video` / `Channel` models (not raw API JSON).
- Errors are returned as structured, typed errors (see NFR-06.2), never raw stack traces.

### FR-01 — Similar Videos  **[BRIEF-P]**
**Description.** Given a video URL or ID, return a ranked list of similar videos.

| | |
|---|---|
| **Input** | YouTube video URL (watch/short/youtu.be forms) or 11-character video ID; optional `n` |
| **Processing** | (1) Validate/normalise input to a video ID. (2) Retrieve metadata of the source video via the provider. (3) Obtain candidate videos via provider search built from source metadata (title keywords, tags, channel). (4) Compute similarity from metadata using TF-IDF/cosine similarity or weighted scoring. (5) Rank and return. |
| **Output** | Ranked list: `video_id`, title, channel, duration, similarity score, reason. Source video itself excluded. |
| **Failure cases** | Malformed ID/URL; video private, deleted or unavailable; missing tags/description (degrade gracefully); `quotaExceeded`; rate limiting. |
| **Constraints** | No related-videos endpoint exists; similarity is computed by the team. Must pass quota pre-check (NFR-02.2). |

**Acceptance criteria**
- AC-01.1 Given a valid ID and fixture metadata, the result is non-empty, sorted by descending score, contains no duplicates and excludes the source video.
- AC-01.2 A URL and the matching bare ID yield identical results.
- AC-01.3 A video with no tags still returns results, using remaining fields.
- AC-01.4 Malformed ID returns a validation error and makes **zero** API calls.
- AC-01.5 A private/deleted video returns a typed "unavailable" error.
- AC-01.6 Scoring is deterministic: same fixtures → same ordering.

### FR-02 — Similar Channels  **[BRIEF-P]**
**Description.** Given a channel URL, handle or ID, return a ranked list of similar channels.

| | |
|---|---|
| **Input** | Channel URL, `@handle` or channel ID (`UC…`); optional `n` |
| **Processing** | Resolve to channel ID; retrieve channel metadata (title, description, topic/keywords, statistics) and a sample of recent/uploaded video metadata; find candidate channels via provider search; compute similarity from channel features; rank. |
| **Output** | Ranked list: channel ID, title, score, reason. Source channel excluded. |
| **Failure cases** | Malformed handle/ID; channel not found; hidden/missing metadata; quota and rate-limit errors. |
| **Constraints** | No related-channels endpoint exists; similarity is computed by the team. |

**Acceptance criteria**
- AC-02.1 URL, handle and ID forms of the same channel resolve to the same channel.
- AC-02.2 Output is sorted descending, deduplicated and excludes the source channel.
- AC-02.3 A channel with missing description/keywords still yields a result or a clear "insufficient metadata" error.
- AC-02.4 Non-existent channel returns a typed "not found" error.

### FR-03 — Recommendations  **[BRIEF-P]**
**Description.** Recommend videos based on the authorised user's liked videos, subscriptions and playlists.

| | |
|---|---|
| **Input** | Authorised user session; optional `n`, optional filters |
| **Processing** | Retrieve liked videos, subscriptions and playlists through the provider; build a user-interest profile from them; obtain candidates; score candidates against the profile; exclude videos already in the library; rank. |
| **Output** | Ranked list of recommended videos with score and reason (e.g. "similar to liked video X / from subscribed channel Y"). |
| **Failure cases** | Unauthorised/expired token; empty library (return a clear "not enough data" result); quota errors. |
| **Constraints** | **Must not use or promise watch history.** Only liked videos, subscriptions and playlists are valid inputs. |

**Acceptance criteria**
- AC-03.1 Given a fixture library, recommendations are ranked, contain no video already in the library, and each cites a library-based reason.
- AC-03.2 No code path or output refers to watch history.
- AC-03.3 Empty library returns a defined "insufficient data" response, not an error crash.
- AC-03.4 Expired/missing token returns an authorisation-required error with re-authorisation instructions (NFR-03.3).

### FR-04 — Engagement Analysis  **[BRIEF-P]**
**Description.** Analyse the user's liked videos, subscriptions and playlists.

| | |
|---|---|
| **Input** | Authorised user session; optional period(s) |
| **Processing** | Retrieve library data; aggregate by channel, category, time and duration. Definitions of "top" and "engagement" are **OPEN (OD-05)**; they must use only library data. |
| **Output** | Report containing all five analyses below. |

| Analysis | Output |
|---|---|
| Top channels | Channels ranked by agreed engagement measure |
| Top categories | Video categories ranked by agreed measure |
| Trends over time | How channel/category distribution changes across time buckets |
| Duration preferences | Distribution of video lengths (e.g. short / medium / long buckets) |
| Period comparison | Differences between two user-specified periods |

**Failure cases.** Library items lacking timestamps/category; empty periods; period with start after end; unauthorised user.

**Acceptance criteria**
- AC-04.1 Given a fixture library, all five analyses are produced and numerically consistent with the fixture (verified by hand-computed expected values).
- AC-04.2 Period comparison with two valid periods reports per-metric differences; an invalid period (start > end) returns a validation error.
- AC-04.3 Items with missing metadata are counted in an explicit "unknown" bucket rather than silently dropped.
- AC-04.4 The definition of "engagement" is documented and the report states what data it was computed from.

### FR-05 — Playlist Creation  **[BRIEF-P]**
**Description.** Accept a natural-language request with constraints, build a satisfying playlist, show it to the user, and create it in the user's YouTube account only after explicit confirmation.

| | |
|---|---|
| **Input** | Natural-language request, e.g. "Build me a two-hour playlist about operating systems, with no video longer than 20 minutes, preferably in English." |
| **Constraints parsed** | **Topic**, **total duration**, **maximum video length**, **language** |
| **Processing** | (1) Parse request into structured `PlaylistConstraints`. (2) Validate constraints. (3) Find candidate videos via provider. (4) Select videos satisfying the constraints. (5) Validate the resulting playlist. (6) **Present** the proposed playlist (titles, durations, total duration, constraint check). (7) Wait for explicit confirmation. (8) Create playlist and add videos via provider. |
| **Output** | Proposal (step 6) and, after confirmation, created playlist ID/URL plus final summary. |
| **Failure cases** | Missing/ambiguous/contradictory constraints; insufficient candidates to meet total duration; account without YouTube channel (`youtubeSignupRequired`); expired token; quota pre-check failure; partial failure while adding videos. |

**Acceptance criteria**
- AC-05.1 Example request above yields parsed constraints: topic = operating systems, total ≈ 120 min, max video = 20 min, language = English.
- AC-05.2 Every video in a proposed playlist is ≤ max length and matches the language constraint (or is flagged if language is unknown); total duration is within the agreed tolerance (OD-06).
- AC-05.3 **No playlist is created without an explicit confirmation action** tied to the exact proposal shown. If the proposal changes, the confirmation is invalidated.
- AC-05.4 Text inside video titles/descriptions that says e.g. "create the playlist now" does not trigger creation (NFR-04.2).
- AC-05.5 An account with no YouTube channel produces a clear, typed error and creates nothing.
- AC-05.6 Impossible constraints (e.g. 2 hours with max video 1 minute and too few candidates) produce an explanation, not a playlist that violates constraints.
- AC-05.7 Quota pre-check runs before any call; an over-budget workflow is rejected with zero API calls (NFR-02.2).
- AC-05.8 Creation failure part-way is reported honestly with what was and was not added.

---

## 4. Non-functional requirements (NFR)

> The briefs do not give a numbered NFR list. Parent IDs below are the team's draft-baseline IDs (kept unchanged); sub-requirements add testable detail.

| Parent | Topic | Sub-requirements |
|---|---|---|
| NFR-01 | Official API only | NFR-01 |
| NFR-02 | Quota and caching | NFR-02.1, NFR-02.2 |
| NFR-03 | OAuth and re-authorisation | NFR-03.1, NFR-03.2, NFR-03.3 |
| NFR-04 | Validation and untrusted metadata | NFR-04.1, NFR-04.2 |
| NFR-05 | Secrets and personal data | NFR-05.1, NFR-05.2 |
| NFR-06 | Errors and capability reporting | NFR-06.1, NFR-06.2 |
| NFR-07 | Provider/service boundaries | NFR-07 |
| NFR-08 | Deterministic CI and live-test separation | NFR-08.1, NFR-08.2, NFR-08.3 |
| NFR-09 | MCP compatibility *(new)* | NFR-09 |
| NFR-10 | Deterministic computation *(new)* | NFR-10 |
| NFR-11 | Documentation *(new)* | NFR-11 |

### 4.1 Interface and compliance

| ID | Requirement | Source | Acceptance criteria |
|---|---|---|---|
| NFR-09 | **MCP compatibility.** The system shall expose its capabilities as tools, resources and Agent Skills through an MCP-compatible server usable by any MCP client. | BRIEF-P | Server starts and lists tools for FR-01 to FR-05 to a generic MCP client; no client-specific code paths. |
| NFR-01 | **Official API only.** Only YouTube Data API v3 shall be used. No scraping, no unofficial APIs. | BRIEF-P | Code/dependency review finds no scraper or unofficial YouTube library; checked in PR review. |
| NFR-02.1 | **Quota budget.** Design shall fit the default quota using caching and fixtures; no extra Cloud projects. The default is 10,000 units/day for general endpoints **plus a separate 100-call/day bucket for `search.list`** (see Appendix A); the design must treat search calls as the scarce resource. | BRIEF-P / DERIVED | Documented cost per tool, in units and in search calls; repeated identical request served from cache without new API calls. |
| NFR-02.2 | **Quota tracking and pre-check.** Estimated quota cost shall be tracked per request, **per bucket** (general units and `search.list` calls); a workflow that would exceed the remaining budget of either bucket shall be rejected **before any API call**. Daily counters reset at midnight Pacific Time. | BRIEF-P / DERIVED | Tests: (a) general units below workflow cost → rejection, zero provider calls; (b) zero remaining search calls → rejection of any search-dependent workflow, zero provider calls. |

### 4.2 Security and privacy

| ID | Requirement | Source | Acceptance criteria |
|---|---|---|---|
| NFR-03.1 | **Minimum OAuth scopes.** Request only scopes needed for the supported reads and playlist writes. | BRIEF-P | Scope list documented and reviewed; test asserts no broader scope is requested. |
| NFR-03.2 | **Safe token storage.** Tokens shall not be stored in the repository or logged; stored outside the repo with restricted access. | BRIEF-P | Secret scan clean; test shows tokens absent from logs/output. |
| NFR-03.3 | **Re-authorisation.** Expired/revoked tokens (incl. 7-day Testing-mode expiry) shall produce a clear re-authorisation path instead of failing opaquely. | BRIEF-P | Test with expired-token mock returns authorisation-required error with instructions; completing re-auth restores operation. |
| NFR-04.1 | **Input validation.** All parameters (video/channel IDs, URLs, dates, constraints, limits) shall be validated before use. | BRIEF-P | Negative tests for malformed values; invalid input never reaches the provider. |
| NFR-04.2 | **Prompt-injection resistance.** Untrusted metadata shall never bypass or substitute for user confirmation, nor trigger privileged actions. | BRIEF-P | Test fixtures with injected instructions in titles/descriptions do not result in playlist creation or changed behaviour. |
| NFR-05.1 | **No secrets in repository.** No API keys, client secrets or tokens committed. | BRIEF-P | CI secret scanning passes; `.gitignore` covers credential files. |
| NFR-05.2 | **No real personal data** in fixtures or logs. | BRIEF-P | Fixtures reviewed as synthetic/anonymised; logging tests confirm no user identifiers or tokens. |

### 4.3 Architecture and reliability

| ID | Requirement | Source | Acceptance criteria |
|---|---|---|---|
| NFR-07 | **Provider isolation.** All YouTube API interaction shall sit behind a provider interface; services depend only on the interface. | BRIEF-S (SE-06) | Services run against a mock provider with no network access. |
| NFR-06.1 | **Channel-less accounts.** Playlist creation by an account without a YouTube channel shall be handled explicitly. | BRIEF-P | `youtubeSignupRequired` mock yields typed error; no partial state. |
| NFR-06.2 | **Graceful failure.** API errors (`quotaExceeded`, rate limiting, not found, private/deleted) shall map to typed, user-readable errors; missing optional metadata (tags, description) shall degrade gracefully. | BRIEF-P / DERIVED | One negative test per listed error class (see TQ-04). |
| NFR-10 | **Deterministic computation.** Similarity and analytics shall be deterministic for identical input data. | DERIVED | Re-running over the same fixtures gives identical output. |

### 4.4 Testability and documentation

| ID | Requirement | Source | Acceptance criteria |
|---|---|---|---|
| NFR-08.1 | **Testability.** System shall support unit, integration, system and negative testing. | BRIEF-P | All four test layers exist and run (see §7). |
| NFR-08.2 | **CI isolation from live API.** CI shall use recorded fixtures or mocks only. | BRIEF-P | CI runs pass with no network access/credentials to YouTube. |
| NFR-08.3 | **Separate live tests.** Live API tests shall run in a separate scheduled workflow with a fixed quota budget. | BRIEF-P | Separate workflow file exists; configured budget cap documented. |
| NFR-11 | **Documentation.** User documentation and developer API documentation (e.g. OpenAPI-style) shall be provided. | BRIEF-S (SE-07) | Docs exist and cover all tools and setup. |

---

## 5. Skill requirements (SK)

Skills follow the Agent Skills format (`SKILL.md` with valid frontmatter and name). Per **SB-03**, every skill shall cite at least one distilled Second Brain note. **[BRIEF-S]**

| ID | Skill | Purpose | Stage |
|---|---|---|---|
| SK-01 | `brain-ingest` | Add new material/summaries to the Second Brain | Stage 1 (create and use) |
| SK-02 | `brain-refine` | Move notes into PARA, merge duplicates, fix links | Stage 2 |
| SK-03 | `brain-query` | Answer questions from the brain; draft documents such as SRS and ADRs | Stage 2 |
| SK-04 | `local-check` | Confirm the project works on a member's machine | Stage 2 (first version) |
| SK-05 | `video-to-playlist` | Product workflow from one video to a playlist | Stage 3 (implement/test), Stage 4 (demo) |

### SK-01 `brain-ingest` **[BRIEF-S + DERIVED]**
**Behaviour.** Accepts raw research material; summarises it; extracts key concepts; chooses a PARA location; writes a structured note using the team template; adds `[[wikilinks]]` and links to requirement IDs/issues/PRs; records sources; updates `brain/index.md` if appropriate; appends a run entry to `brain/log.md`.
**Acceptance criteria**
- Valid `SKILL.md` (passes CI skill validation).
- ≥ 10 research notes produced with it, by all three members.
- Each note has sources, project relevance and ≥ 1 wikilink; each run is logged.

### SK-02 `brain-refine` **[BRIEF-S]**
**Behaviour.** Moves notes to the correct PARA folder, merges duplicates, repairs broken links.
**Acceptance criteria.** On a vault seeded with a duplicate and a broken link, the skill merges/fixes them and logs the run; result passes brain validation.

### SK-03 `brain-query` **[BRIEF-S]**
**Behaviour.** Answers questions from the vault and drafts documents (e.g. SRS sections, ADRs) with citations to notes.
**Acceptance criteria.** Given a question answered in the vault, the response cites the source notes; a drafted ADR cites ≥ 1 distilled note (SB-03).

### SK-04 `local-check` **[BRIEF-S]**
**Behaviour.** (1) Build the project; (2) run the automated test suite; (3) start the local server; (4) invoke one read-only fetch endpoint; (5) report pass/fail for each step.
**Acceptance criteria.** Produces a five-step pass/fail report on a team member's machine; a deliberately broken step is reported as FAIL; the endpoint invoked is read-only and consumes minimal quota (preferably none, via mock/fixture mode — OD-08).

### SK-05 `video-to-playlist` **[BRIEF-P]**
**Behaviour.** For one given video: (1) summarise it; (2) find similar videos (FR-01); (3) propose a playlist and ask the user to confirm; (4) create the playlist (FR-05); (5) show a short playlist analysis.
**Acceptance criteria**
- All five steps run end-to-end against fixtures in tests and live in the demo.
- Step 4 never runs without the explicit confirmation of step 3 (NFR-04.2).
- Step 1 uses a compliant source of content (metadata or user-supplied transcript — **OPEN, OD-04**); no scraping/unofficial APIs (NFR-01).
- Skill evaluation results are recorded in test documentation (TQ-07).

---

## 6. Engineering and process requirements

### 6.1 Software engineering (SE) **[BRIEF-S]**
| ID | Requirement |
|---|---|
| SE-01 | Produce and maintain this SRS (FR, NFR, SK). |
| SE-02 | Produce architecture/design documentation with UML/ER diagrams (Stage 2). |
| SE-03 | Record significant decisions as ADRs in `docs/adr/`, citing brain notes. |
| SE-04 | Produce a development plan and task breakdown (`docs/development-plan.md`). |
| SE-05 | Maintain a traceability matrix: requirement → issue → PR → test → skill → brain note (`docs/traceability.md`). |
| SE-06 | Isolate external dependencies behind a provider interface (see NFR-07). |
| SE-07 | Produce user documentation and developer API documentation (see NFR-11). |

### 6.2 Second Brain (SB) **[BRIEF-S]**
| ID | Requirement |
|---|---|
| SB-01 | Link notes with `[[wikilinks]]` and to requirement IDs, issues and PRs. |
| SB-02 | Write a short review note at the end of each stage (what worked, what did not, what to change). |
| SB-03 | Every ADR and every skill cites ≥ 1 distilled note. |
| SB-04 | Keep `AGENTS.md` at the repository root. |
| SB-05 | Changes to the brain, including AI changes, go through pull requests. |
| SB-06 | Every member authors notes; contribution visible in commit history. |

Structure: `brain/inbox`, `projects`, `areas`, `resources`, `archive`; `brain/index.md` is the entry point; `brain/log.md` records all runs.

### 6.3 Version control and CI **[BRIEF-S]**
- Meaningful incremental commits from every member; documented branching strategy.
- GitHub Issues for all work and defects.
- PR with ≥ 1 review for every change (code, skills, brain).
- Release tags and a changelog.
- CI on every PR: build, lint, automated tests, secret scanning, validation of every `SKILL.md` (frontmatter/naming), validation of brain notes (schema/broken links).

### 6.4 AI-assisted development policy (AIP) **[BRIEF-S]**
| ID | Requirement |
|---|---|
| AIP-01 | The team is responsible for every merged line; a human reviews every AI-generated change in a PR. |
| AIP-02 | Every member can explain any merged code, skill or document in project reviews. |
| AIP-03 | Significant AI sessions are recorded in the brain as `ai-session` notes (goal, what worked/failed). |
| AIP-04 | No secrets, tokens or credentials are pasted into any AI tool. |

---

## 7. Testing requirements (TQ)

| ID | Requirement | Source | Acceptance criteria |
|---|---|---|---|
| TQ-01 | Unit tests for functions, modules, services and MCP tools, including **similarity scoring, duration parsing and playlist-constraint logic**. | BRIEF-P | Each of the three named areas has dedicated unit tests; tests run in CI. |
| TQ-02 | Integration tests for interactions between components, including the YouTube provider. | BRIEF-P | Provider ↔ service tests run against recorded fixtures/mocks. |
| TQ-03 | System (end-to-end) tests for each of FR-01 to FR-05 driven through the MCP interface. | BRIEF-P | One passing E2E test per FR via an MCP client harness. |
| TQ-04 | Negative tests: invalid/malformed IDs, private/deleted videos, missing tags, `quotaExceeded`, `youtubeSignupRequired`, expired tokens, rate limiting. | BRIEF-P | At least one test per listed case, each asserting the typed error/degradation. |
| TQ-05 | CI uses recorded fixtures or mocks, not the live API; live tests run in a separate scheduled workflow with a fixed quota budget. | BRIEF-P | CI green without network access to YouTube; separate live workflow exists. |
| TQ-06 | Quota cost tracked per request; a workflow exceeding remaining budget is rejected before any API call. | BRIEF-P | Test asserts rejection and zero provider calls. |
| TQ-07 | Skill evaluations run before each stage submission; results recorded in test documentation. | BRIEF-S | `docs/testing/README.md` has an evaluation record per stage. |
| TQ-08 | Tests maintained as the system changes; every significant defect gets a regression test. | BRIEF-S | Each closed defect issue links a regression test. |

### 7.1 Security testing **[BRIEF-P]**
| Area | Verification |
|---|---|
| OAuth | Minimum scopes asserted; token storage outside repo (NFR-03.1, NFR-03.2) |
| Secrets | CI secret scan; no credentials in repo (NFR-05.1) |
| Input validation | All parameters covered by negative tests (NFR-04.1) |
| Prompt injection | Injected metadata cannot bypass confirmation (NFR-04.2) |
| Personal data | Fixtures/logs contain no real user data (NFR-05.2) |

---

## 8. Stage deliverables (from SDLC brief)

| Stage | Deliverables |
|---|---|
| 1 — Requirements | SRS (FR, NFR, SK); Obsidian PARA vault with index and log; `brain-ingest` used for ≥ 10 research notes; `AGENTS.md`; repository and CI skeleton |
| 2 — Design | Architecture/design docs and diagrams; `brain-refine`, `brain-query`; first `local-check` |
| 3 — Testing and CI | Continuous testing/CI plan and results; `video-to-playlist` with test results; defect log with regression tests; review note per stage |
| 4 — Review | Live demo of FRs in a client; run product skill end-to-end; run `local-check` and `brain-query` live; walk a requirement from brain note → ADR → code → test; final release tag |

---

## 9. Open decisions (OD)

None of these is specified by the briefs. Each needs an owner and due date; until decided they are **OPEN** and must not be treated as requirements.

| ID | Decision | Affects | Suggested owner | Status |
|---|---|---|---|---|
| OD-01 | Implementation language, framework and MCP SDK; lint/test/secret-scan tools | All, CI | All; Person 3 records | OPEN |
| OD-02 | Which MCP client is used for the demo | NFR-09, Stage 4 | Person 3 | OPEN |
| OD-03 | Default result size `n`, minimum similarity threshold | FR-01…FR-03 | Person 1 + 2 | OPEN (proposed n = 10) |
| OD-04 | Source for video summarisation: metadata only vs. user-supplied transcript | SK-05 | Person 2 + 3 | OPEN |
| OD-05 | Definition of "engagement"/"top" using only library data. *Data finding:* `playlistItem.snippet.publishedAt` = time added to a playlist; `videos.list?myRating=like` has no like-time. Still to decide: which timestamp defines "period" for likes, and subscription-date availability (verify) | FR-04, FR-03 | Person 2 | PARTLY RESOLVED (definition still OPEN) |
| OD-06 | Total-duration tolerance (e.g. ±5–10%) and handling of unknown language | FR-05 | Person 2 + 3 | OPEN |
| OD-07 | Similarity features and weights (TF-IDF/cosine vs. weighted) | FR-01, FR-02, FR-03 | Person 1 + 2 | OPEN |
| OD-08 | Token storage mechanism; whether `local-check` runs in fixture mode | NFR-03.2, SK-04 | Person 1 / Person 3 | OPEN |
| OD-09 | Candidate retrieval strategy under quota limits. `search.list` is limited to 100 calls/day per project (research update); candidate generation should prefer cheap endpoints (channel uploads via `playlistItems.list`, batched `videos.list`) and cache aggressively | NFR-02.1, FR-01…FR-05 | Person 1 | OPEN (proposal: ≤ 2 search calls per tool invocation) |

---

## 10. Approval

| Member | Role | Reviewed | Approved (PR comment/approval) |
|---|---|---|---|
| Person 1 | SRS owner | ☐ | ☐ |
| Person 2 | Reviewer | ☐ | ☐ |
| Person 3 | Reviewer | ☐ | ☐ |

**Reviewer checklist:** all five FRs match the brief · no contradiction with the PDFs · all API restrictions documented · security requirements present · all five skills covered · unique IDs · every requirement has acceptance criteria · open decisions have owners.

---

## Appendix A — Reference: YouTube API quota (verified 2026-11-07 against Google's pages)
Source: <https://developers.google.com/youtube/data/determine_quota_cost> and <https://developers.google.com/youtube/data/getting-started> (both "last updated 2026-11-03 UTC"). **Re-check before implementing; Google states default quota is subject to change.**

| Fact | Detail |
|---|---|
| Default allocation | 10,000 units/day for general endpoints, **plus** 100 `search.list` calls/day and 100 `videos.insert` calls/day (separate buckets, cost 1 per call) |
| Reset | Daily, midnight Pacific Time |
| Minimum cost | Every request, including invalid ones, costs at least 1 |
| Paging | Each extra page of a list call is charged again |
| Read calls | `videos.list`, `channels.list`, `playlists.list`, `playlistItems.list`, `subscriptions.list`, `videoCategories.list`: 1 unit |
| Write calls | `playlists.insert`, `playlistItems.insert`: 50 units each |
| Quota increase | Via Google's quota extension request form; the brief forbids extra Cloud projects |

**Worked example (FR-05, 10-video playlist):** `playlists.insert` 50 + 10 × `playlistItems.insert` 50 = **550 units**, plus the reads and the search calls used to find candidates. This is why NFR-02.1/NFR-02.2 require caching and a pre-check.

*Caution:* older blog posts and calculators still show `search.list` at 100 units and `videos.insert` at 1,600. Treat Google's own page as authoritative, and confirm the numbers shown in the team's Cloud console **Quotas** page.

## Appendix B — Change history
| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0 | 2026-11-06 | Person 1 | Initial Stage 1 draft |
| 0.2.0 | 2026-11-07 | Person 1 | Verified quota against Google docs (separate `search.list` bucket); NFR-02.1/NFR-02.2, OD-05, OD-09, Appendix A updated; data-availability notes for FR-03/FR-04 |
