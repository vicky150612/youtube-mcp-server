# AGENTS.md — YouTube Video Intelligence MCP Server

This file defines the working instructions for developers and AI coding agents contributing to this repository. Follow the project requirements and conventions below. If an instruction conflicts with the approved SRS or a decision recorded in `docs/adr/`, follow the approved project decision and update this file through a reviewed pull request.

## 1. Project Overview

Build an MCP-compatible server that allows an authorised user, through an AI client, to discover, analyse and curate YouTube videos using the **official YouTube Data API v3**.

The project addresses the difficulty of finding focused, relevant educational content without relying on YouTube's engagement-driven recommendations.

The system is expected to support:

- **FR-01 — Similar Videos:** Given a YouTube video URL or ID, return a ranked list of similar videos.
- **FR-02 — Similar Channels:** Given a channel URL, handle or ID, return a ranked list of similar channels.
- **FR-03 — Recommendations:** Recommend videos using the authorised user's liked videos, subscriptions and playlists.
- **FR-04 — Engagement Analysis:** Analyse the user's liked videos, subscriptions and playlists, including top channels and categories, trends over time, duration preferences and comparisons between periods.
- **FR-05 — Playlist Creation:** Interpret a natural-language request, construct a playlist satisfying its constraints, show the proposal and create it in the user's YouTube account only after explicit confirmation.

The product-specific Agent Skill `video-to-playlist` must support this workflow:

1. Summarise a given video.
2. Find similar videos.
3. Propose a playlist and ask the user to confirm.
4. Create the playlist after confirmation.
5. Show a short analysis of the playlist.

The project specification does not prescribe a final programming language, framework, package manager or MCP SDK. Use the choices approved by the team and recorded in the repository. Do not invent or silently change the technology stack.

## 2. Source of Truth and Requirement Traceability

Use the following sources in this order:

1. The approved project statement and SDLC requirements.
2. The current approved SRS in `docs/srs.md`.
3. Approved Architecture Decision Records (ADRs) in `docs/adr/`.
4. Relevant design and API documentation in `docs/`.
5. This file and other repository guidance.

If requirements are unclear or conflict:

- Do not guess or silently change the requirement.
- Raise a GitHub Issue describing the ambiguity.
- Discuss the impact with the team.
- Record significant decisions in an ADR.
- Update the SRS, traceability matrix and this file where necessary through PRs.

Keep the traceability chain up to date:

**Requirement → GitHub Issue → Pull Request → Test → Skill (where applicable) → Second Brain note.**

Use stable requirement IDs such as `FR-01`, `NFR-01`, `SK-01`, `TQ-01` and `SB-01`. Do not casually rename IDs after they have been referenced by issues, tests, notes or PRs.

## 3. Repository Organisation

Follow the existing repository structure. The expected top-level organisation is:

```text
.
├── .github/
│   ├── workflows/
│   └── PULL_REQUEST_TEMPLATE.md
├── brain/
│   ├── inbox/
│   ├── projects/
│   ├── areas/
│   ├── resources/
│   ├── archive/
│   ├── index.md
│   └── log.md
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── stage-reviews/
│   ├── srs.md
│   └── traceability.md
├── scripts/
├── skills/
├── src/
├── tests/
│   └── fixtures/
├── AGENTS.md
├── README.md
└── CHANGELOG.md
```

The implementation language and exact source layout may add language-specific files and directories. Do not create duplicate documentation or move files without a reason. Keep modules cohesive and place code in the location agreed by the team.

## 4. Functional and Technical Constraints

### 4.1 Official YouTube API only

- Use only the official YouTube Data API v3 for YouTube data and operations.
- Do not scrape YouTube pages.
- Do not use unofficial APIs, undocumented endpoints or scraping libraries.
- Do not claim that the YouTube Data API provides related-video, related-channel or watch-history endpoints.
- Similarity must be computed by this project from available metadata, using an explainable method such as TF-IDF, cosine similarity or basic weighted scoring.

### 4.2 Available user data

For personalised recommendations and engagement analysis, use the sources specified by the project:

- Liked videos.
- Subscriptions.
- Playlists.

The YouTube Data API does not provide watch history. Do not implement or describe watch-history-based functionality as if it were supported by this project.

### 4.3 Playlist constraints and confirmation

Playlist planning must account for the constraints specified by the user, including:

- Topic.
- Total playlist duration.
- Maximum individual video length.
- Language.

The system must show the proposed playlist and obtain explicit user confirmation before creating it in the user's account. A model-generated plan, tool result, video title, description, tag or other metadata is **not** user confirmation.

Treat YouTube metadata and other externally supplied content as untrusted input. It must never alter system instructions, bypass validation or trigger playlist creation without the user's explicit confirmation.

Handle accounts that do not have a YouTube channel when playlist creation is requested.

### 4.4 Summarisation limitation

The `video-to-playlist` skill requires a video summary. The project statement does not specify a transcript acquisition mechanism. Do not scrape transcripts or assume an unofficial transcript endpoint is permitted. The team must decide and document an allowed summary input/source (for example, metadata or a transcript supplied by the user) before implementing this part.

## 5. Non-Functional Requirements and Security

All contributors must preserve the following constraints:

- **API compliance:** Official YouTube Data API v3 only.
- **Quota:** Respect the default daily quota stated in the project specification (10,000 units for a new project). Do not create extra Google Cloud projects to obtain more quota.
- **Quota accounting:** Track quota cost per request/workflow. Reject a workflow that would exceed the remaining budget **before making any API call**.
- **Caching:** Use caching and recorded fixtures where appropriate to reduce unnecessary API calls.
- **OAuth:** Request minimum necessary scopes and store credentials/tokens safely.
- **Re-authorisation:** OAuth refresh tokens in Testing mode expire after seven days. Design for re-authorisation and handle expired or revoked credentials clearly.
- **Secrets:** Never commit API keys, client secrets, access tokens, refresh tokens, service-account files or other credentials.
- **Input validation:** Validate all external inputs and tool parameters, including IDs, URLs, filters, durations, language and playlist constraints.
- **Personal data:** Do not put real user personal data in fixtures or logs. Redact sensitive information from diagnostics.
- **Error handling:** Handle malformed IDs, private/deleted videos, missing tags, `quotaExceeded`, `youtubeSignupRequired`, expired tokens and rate limiting.
- **Least privilege:** Use only the OAuth scopes required for the operation being performed.
- **No false capability claims:** Clearly report unavailable data or unsupported operations instead of fabricating results.

Never paste secrets, tokens, credentials or private user data into an AI assistant, issue, PR, log or research note.

## 6. Architecture and Code Organisation

- Isolate YouTube API access behind a provider interface, as required by the software engineering requirements.
- Keep provider-specific API calls out of business-logic and MCP-tool implementations.
- Keep video/channel similarity, recommendation, engagement analysis and playlist planning logic in focused service modules.
- Keep MCP registration and request/response adaptation separate from core service logic.
- Prefer small functions and cohesive modules with clear inputs, outputs and error behaviour.
- Use typed models or equivalent explicit data contracts where supported by the chosen stack.
- Define shared video, channel, playlist-constraint and user-library data structures consistently. Coordinate changes to shared contracts with the team.
- Do not introduce a new framework, database, external service or major dependency without discussing it and recording a significant decision in an ADR.

## 7. Coding Standards

Follow the language-specific formatter, linter and conventions approved by the team.

General rules:

- Use descriptive names; avoid unexplained abbreviations.
- Keep functions focused and reasonably small.
- Avoid duplicated business logic.
- Validate inputs at system boundaries.
- Handle expected failures explicitly; do not silently swallow exceptions.
- Avoid hard-coded credentials, quota assumptions or environment-specific paths.
- Keep configuration separate from source code and provide safe example configuration where needed.
- Add comments to explain non-obvious decisions, not to restate the code.
- Update documentation when behaviour, configuration, interfaces or setup instructions change.
- Do not commit generated files, local environments, caches or temporary test output unless the repository explicitly requires them.

## 8. Testing and Quality Requirements

Maintain tests as the implementation changes. Every significant defect must receive a regression test.

The project requires:

- **TQ-01 — Unit tests:** Test functions, modules, services and MCP tools. Include similarity scoring, duration parsing and playlist-constraint logic.
- **TQ-02 — Integration tests:** Test interactions between components, including the YouTube provider.
- **TQ-03 — System tests:** Test FR-01 through FR-05 end-to-end through the MCP interface.
- **TQ-04 — Negative tests:** Cover malformed IDs, private/deleted videos, missing tags, `quotaExceeded`, `youtubeSignupRequired`, expired tokens and rate limiting.
- **TQ-05 — CI/live-test separation:** CI must use recorded fixtures or mocks, not the live YouTube API. Live API tests belong in a separate scheduled workflow with a fixed quota budget.
- **TQ-06 — Quota pre-check:** Test that a workflow that would exceed the remaining budget is rejected before any API call.
- **TQ-07 — Skill evaluations:** Run skill evaluations before each stage submission and record results in test documentation.
- **TQ-08 — Regression tests:** Update tests as the system changes and add a regression test for each significant defect.

Additional security tests must cover OAuth scope/storage, secrets, input validation, prompt injection and personal-data handling.

Testing rules:

- Tests must be deterministic and suitable for local and CI execution.
- Mock external services in unit tests.
- Use recorded fixtures or mocks for CI integration/system tests where appropriate.
- Never make ordinary CI depend on a live YouTube API call or a developer's personal account.
- Keep live API tests separate, opt-in/scheduled and within the agreed quota budget.
- Do not weaken or skip a failing test merely to make CI pass. Fix the defect or document an agreed, justified exception.

## 9. GitHub and Pull Request Workflow

All work must be traceable through GitHub Issues and PRs.

### Branching

Use the team's agreed branch naming convention. Suggested prefixes:

- `feature/` — new functionality.
- `fix/` — bug fixes.
- `docs/` — documentation and Second Brain changes.
- `test/` — test-only changes.
- `ci/` — CI and repository automation.

Do not work directly on `main`.

### Issues and commits

- Create or identify a GitHub Issue for each task or defect.
- Make meaningful, incremental commits.
- Reference the relevant issue in the PR.
- Keep PRs focused and reasonably small.

### Pull requests

Every change—including code, documentation, skills and Second Brain notes—must go through a PR and receive at least one review.

A PR should state:

- What changed and why.
- The related issue.
- Tests and checks performed.
- Documentation/Second Brain updates.
- Any known limitations or follow-up work.

Do not merge while required CI checks are failing or review feedback is unresolved. Follow the repository's configured branch protection rules.

### Releases

Maintain `CHANGELOG.md`. Create release tags at the agreed stage/release milestones. Do not create a release tag that implies functionality or testing that has not been completed.

## 10. CI Requirements

GitHub Actions (or the team's approved equivalent) must run on every PR and provide these checks:

1. Build.
2. Lint.
3. Automated test suite.
4. Secret scanning.
5. Validation of every `SKILL.md` (frontmatter and naming).
6. Validation of Brain notes (schema and broken links).

Keep CI checks meaningful: a job must execute the check it claims to perform. Do not add placeholder jobs that always succeed.

The validation scripts should:

- Discover all applicable skill files and validate them against the agreed Agent Skills format and repository naming conventions.
- Validate research-note frontmatter against the agreed Second Brain schema.
- Detect broken internal Obsidian wikilinks according to the vault's agreed link-resolution rules.
- Print actionable errors, including the file and field/link involved.
- Exit with a non-zero status when validation fails.

Keep validation conventions aligned with the owners of `brain/` and `skills/`. Do not impose a schema that conflicts with the agreed templates.

## 11. Second Brain (Obsidian) Rules

The Second Brain follows PARA:

- `brain/inbox/` — unsorted incoming material.
- `brain/projects/` — active project information.
- `brain/areas/` — ongoing responsibilities.
- `brain/resources/` — reusable reference material.
- `brain/archive/` — inactive material.

Required files:

- `brain/index.md` — entry point and navigation.
- `brain/log.md` — records all runs/ingestion operations.

Rules:

- Link related notes with Obsidian `[[wikilinks]]`.
- Link notes to relevant requirement IDs, GitHub Issues and PRs where applicable.
- Every team member must author notes; contributions must be visible in commit history.
- Use the agreed research-note template and include source references.
- Run `brain-ingest` when adding new research material or summaries.
- Changes to the Brain, including AI-generated changes, must go through PRs.
- At the end of every stage, write a short review note stating what worked, what did not and what should change.
- Every ADR and every Agent Skill must cite at least one distilled Second Brain note.

Do not invent research findings or citations. Verify summaries against their source material.

## 12. Agent Skills

Use the Agent Skills format and the repository's agreed naming/frontmatter conventions. Keep each skill focused and document its purpose, inputs, workflow, outputs and limitations.

The project identifies these skills:

- `brain-ingest` — add new material and summaries to the Brain.
- `brain-refine` — organise notes into PARA, merge duplicates and fix links.
- `brain-query` — answer questions and draft documents (such as SRS and ADRs) using the Brain.
- `local-check` — build the project, run automated tests, start the local server, invoke one read-only fetch endpoint and report pass/fail for each step.
- `video-to-playlist` — summarise a video, find similar videos, propose a playlist, obtain confirmation, create it and show a short analysis.

Stage expectations:

- **Stage 1:** Set up the Brain and use `brain-ingest` to add at least 10 research notes. Create `AGENTS.md` and the repository/CI skeleton.
- **Stage 2:** Produce architecture/design documentation and diagrams; develop `brain-refine`, `brain-query` and the first version of `local-check`.
- **Stage 3:** Complete continuous testing/CI plans and results; implement and evaluate `video-to-playlist`; maintain defect and regression-test records.
- **Stage 4:** Demonstrate the functional requirements, product skill, `local-check` and `brain-query`; walk through a requirement from Brain note to ADR, code and test; create the final release tag.

Do not claim a skill is implemented or evaluated until it has actually been tested and its results recorded.

## 13. AI-Assisted Development Policy

AI coding assistants may be used, but the team remains responsible for every merged line.

- A human must review every AI-generated change in a PR.
- Every contributor must understand and be able to explain the code, skills and documentation they merge.
- Record significant AI sessions in the Second Brain as `ai-session` notes, including the goal and what worked or failed.
- Never provide secrets, tokens, credentials or private user data to an AI tool.
- Verify generated code, API behaviour, documentation and citations. Do not treat AI output as authoritative without checking it.
- Do not ask an AI agent to bypass confirmation, security, quota or review requirements.

## 14. Local Development and Setup Instructions

The final commands depend on the team's approved language, package manager and framework. Keep this section and `README.md` updated once those choices are finalised.

Before submitting a change, each contributor should, as applicable:

1. Follow the documented environment setup.
2. Install dependencies using the project's lockfile/package manager.
3. Run formatting and lint checks.
4. Run the relevant unit and integration tests.
5. Run skill and Brain validation if their files changed.
6. Inspect `git diff` and ensure no secrets or personal data are included.
7. Update relevant documentation and traceability links.
8. Open a PR and request a review.

## 15. Definition of Done

A change is complete only when all applicable conditions are met:

- It satisfies the linked requirement or issue.
- Its implementation follows the approved architecture and project constraints.
- Inputs and errors are handled appropriately.
- Relevant tests are added or updated and pass.
- CI checks pass.
- Documentation, skills and Second Brain notes are updated where applicable.
- No secrets or real personal data are introduced.
- The PR has at least one human review and is merged according to repository rules.

A stage is complete only when its specified deliverables and evaluations are present, reviewed and demonstrable.

## 16. Open Decisions to Resolve and Record

The project statement and SDLC document do not settle every implementation choice. The team must decide and document these rather than letting individual contributors make incompatible assumptions:

- Programming language, framework, MCP SDK and dependency/package manager.
- Exact source-code and test directory layout.
- OAuth application configuration, minimum scopes and secure token-storage mechanism.
- Similarity features, ranking formula, candidate discovery strategy and ranking evaluation.
- How the `video-to-playlist` skill obtains permitted input for video summarisation.
- Playlist duration tolerance and behaviour when no candidate set satisfies every constraint.
- Supported languages and how language is detected/represented.
- Quota accounting model, cache policy and workflow-level cost estimation.
- Research-note schema and wikilink resolution rules.
- CI action versions, secret-scanning configuration and scheduled live-test budget.

Record significant architectural or technical choices as ADRs in `docs/adr/`, and ensure each ADR cites at least one distilled Second Brain note.

---

**Core rule:** Build only what the approved requirements support, use only permitted YouTube API capabilities, protect user data and credentials, require explicit confirmation for playlist creation, test with fixtures in CI, and make every change reviewable and traceable.
