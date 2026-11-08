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

The project specification does not prescribe a final programming language, framework, package manager or MCP SDK. The **application stack is not decided** (`OD-01` in the SRS register). The **repository tooling** is recorded in [ADR 0005](docs/adr/0005-repository-toolchain.md): Python 3.12 for CI scripts and tests only, PyYAML 6.0.3, Ruff 0.17.4, `unittest`, Gitleaks 8.30.1 and GitHub Actions. Python tooling does not select the application language. Do not invent or silently change the technology stack.

## 2. Source of Truth and Requirement Traceability

Use the following sources in this order:

1. The approved project statement and SDLC requirements (the brief PDFs, which are not stored in this repository).
2. The current approved SRS in `docs/srs.md` (version 0.3.0 is a draft; approval is pending, see its section 10).
3. Approved Architecture Decision Records (ADRs) in `docs/adr/` (index: `docs/adr/README.md`; ADRs 0001–0008 are all **Proposed**).
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

Use stable requirement IDs in canonical zero-padded form, such as `FR-01`, `NFR-02.1`, `SK-01`, `TQ-01`, `SB-01` and `OD-01`. Do not casually rename IDs after they have been referenced by issues, tests, notes or PRs. CI rejects unpadded IDs and IDs not defined in the SRS (ADR 0003).

## 3. Repository Organisation

Follow the existing repository structure. This is the tree on branch
`fix/stage-1-audit-consistency` (2026-11-08); local, untracked tool folders such as `.obsidian/`
are not part of it:

```text
.
├── .claude/
│   └── skills/
│       └── brain-ingest/          # SKILL.md and assets/research-note.tmpl (ADR 0001)
├── .github/
│   ├── ISSUE_TEMPLATE/            # bug_report.yml, task_request.yml
│   ├── workflows/ci.yml           # seven CI jobs (section 10)
│   └── PULL_REQUEST_TEMPLATE.md
├── brain/                         # Obsidian vault root (ADR 0003)
│   ├── projects/                  # project and ai-session notes
│   ├── resources/                 # research notes
│   ├── index.md
│   └── log.md
├── docs/
│   ├── adr/                       # ADRs 0001-0008, README index, template
│   ├── api/                       # interface contracts (draft), API docs
│   ├── architecture/overview.md
│   ├── development/github-workflow.md
│   ├── research/allocation.md
│   ├── stage-reviews/             # canonical stage-review location (ADR 0004)
│   ├── testing/                   # strategy, results, defects, skill evaluations
│   ├── development-plan.md
│   ├── srs.md                     # requirements and the open-decision register (section 9)
│   └── traceability.md
├── scripts/                       # CI build check and validators (Python tooling)
├── tests/                         # unit tests for the repository tooling
├── .gitignore
├── .gitleaks.toml
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── requirements-ci.txt
└── ruff.toml
```

Not yet tracked on this branch: `src/`, `tests/fixtures/` and the empty PARA folders
`brain/inbox/`, `brain/areas/` and `brain/archive/`. They are added by the separate build and
structure change (branch `ci/build-structure-formatting`), which the CI build check requires;
until it is integrated they exist only as local folders. Credential patterns in `.gitignore` are
added by branch `fix/gitignore-credential-protection`.

Do not create duplicate documentation or move files without a reason. Keep modules cohesive and
place code in the location agreed by the team once the application stack is decided (`OD-01`).

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

The system must show the proposed playlist and obtain explicit user confirmation before creating it in the user's account. A model-generated plan, tool argument or tool call, tool result, video title, description, tag or other metadata is **not** user confirmation. The proposed two-phase mechanism (immutable proposal, MCP elicitation, fail closed without it) is [ADR 0007](docs/adr/0007-playlist-confirmation.md).

Treat YouTube metadata and other externally supplied content as untrusted input. It must never alter system instructions, bypass validation or trigger playlist creation without the user's explicit confirmation.

Handle accounts that do not have a YouTube channel when playlist creation is requested.

### 4.4 Summarisation limitation

The `video-to-playlist` skill requires a video summary. The project statement does not specify a transcript acquisition mechanism. Do not scrape transcripts or assume an unofficial transcript endpoint is permitted. The team must decide and document an allowed summary input/source (for example, metadata or a transcript supplied by the user) before implementing this part (`OD-04`).

## 5. Non-Functional Requirements and Security

All contributors must preserve the following constraints:

- **API compliance:** Official YouTube Data API v3 only.
- **Quota:** Respect the default daily quota stated in the project specification (10,000 units for a new project). Do not create extra Google Cloud projects to obtain more quota.
- **Quota accounting:** Estimate and track the documented cost of each API operation in every applicable quota bucket; costs are not uniform. Count additional list pages and playlist writes. Reject a workflow that would exceed any remaining budget **before making any API call** (SRS `NFR-02.2`); fail closed if a required cost is unknown (proposed `NFR-02.3`). The remaining budget is a local estimate, never Google's figure. The canonical figures are SRS Appendix A; verify project-specific limits before implementation ([ADR 0006](docs/adr/0006-quota-reference-and-accounting.md)).
- **Caching:** Use caching and recorded fixtures where appropriate to reduce unnecessary API calls.
- **OAuth:** Request minimum necessary scopes and store credentials/tokens safely. The proposed design (desktop client with PKCE and loopback redirect, `youtube.readonly` plus incremental `youtube`, OS credential store) is [ADR 0008](docs/adr/0008-oauth-client-and-scopes.md).
- **Re-authorisation:** OAuth refresh tokens in Testing mode expire after seven days. Design for re-authorisation and handle expired or revoked credentials clearly.
- **Secrets:** Never commit API keys, client secrets, access tokens, refresh tokens, service-account files or other credentials.
- **Input validation:** Validate all external inputs and tool parameters, including IDs, URLs, filters, durations, language and playlist constraints.
- **Personal data:** Do not put real user personal data in fixtures or logs. Redact sensitive information from diagnostics.
- **Error handling:** Handle malformed IDs, private/deleted videos, missing tags, `quotaExceeded`, `youtubeSignupRequired`, expired tokens and rate limiting.
- **Live API tests:** Keep live tests separate from ordinary CI (`NFR-08.3`). Before enabling them, approve finite per-run caps for all applicable quota buckets (`OD-13`); pre-check each call/page/write and stop before a cap is exceeded. Missing caps or unknown operation costs must fail closed; a zero budget disables calls (proposed `NFR-08.4`). Requirements for the deferred workflow are in `docs/testing/README.md`.
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

GitHub Actions runs `.github/workflows/ci.yml` on every PR to `main` with seven jobs:

1. **Build** — `python scripts/ci_build.py` (structural and Python syntax check; no application build target yet).
2. **Lint** — `ruff check scripts tests` and `ruff format --check scripts tests`.
3. **Automated tests** — `python -m unittest discover -s tests -v`.
4. **Secret scanning** — Gitleaks 8.30.1 over the full Git history.
5. **Skill validation** — `python scripts/validate_skills.py --require brain-ingest` (every `SKILL.md` in `.claude/skills/`: frontmatter, naming, required sections, links, Brain citation).
6. **Brain validation** — `python scripts/validate_brain.py` (note schema, wikilinks, heading links, relative links, requirement IDs).
7. **Documentation validation** — `python scripts/validate_docs.py` (no wikilinks outside `brain/`, relative links and anchors, requirement IDs, ADR Brain citations).

These checks are not yet *required* by the `main` ruleset; see `docs/development/github-workflow.md`.

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
- `brain/log.md` — records all runs/ingestion operations, in chronological order.

Rules:

- `brain/` is the vault root. Link related notes with Obsidian `[[wikilinks]]` whose target is the note's filename; aliases are display text only, and planned notes are written as plain text, not links (ADR 0003).
- Every note has the canonical frontmatter of [ADR 0002](docs/adr/0002-brain-note-schema.md): `title`, `type` (`research` or `ai-session`), `author` (list), `created` (`YYYY-MM-DD`), `tags` (list), `sources` (list), optional `aliases` and `status` (`draft` or `ingested`). Never invent `author` or `created`; ask the contributor.
- Name new notes with hyphen-separated words (`YouTube-Video-Resource.md`).
- Outside the Brain (in `docs/`, `README.md`, this file) use relative Markdown links, never wikilinks.
- Link notes to relevant requirement IDs, GitHub Issues and PRs where applicable.
- Every team member must author notes; contributions must be visible in commit history.
- Use the agreed research-note template and include source references.
- Run `brain-ingest` when adding new research material or summaries.
- Changes to the Brain, including AI-generated changes, must go through PRs.
- At the end of every stage, write a short review note stating what worked, what did not and what should change, in `docs/stage-reviews/stage-N-review.md` (ADR 0004). Each member writes their own reflections.
- Every ADR and every Agent Skill must cite at least one distilled Second Brain note.

Do not invent research findings or citations. Verify summaries against their source material.

## 12. Agent Skills

Use the Agent Skills format and the repository's agreed naming/frontmatter conventions. Skills live in `.claude/skills/<skill-name>/SKILL.md` and nowhere else ([ADR 0001](docs/adr/0001-agent-skill-location.md)). Keep each skill focused and document its purpose, inputs, workflow, outputs and limitations in `##` sections, and cite at least one Brain note with a relative link (`SB-03`); `scripts/validate_skills.py` enforces this. Record evaluations in `docs/testing/skill-evaluations.md` (`TQ-07`).

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

Application commands depend on the team's approved language, package manager and framework (`OD-01`). The repository checks, identical to CI, are:

```text
python -m pip install -r requirements-ci.txt
python scripts/ci_build.py
ruff check scripts tests
ruff format --check scripts tests
python -m unittest discover -s tests -v
python scripts/validate_skills.py --require brain-ingest
python scripts/validate_brain.py
python scripts/validate_docs.py
gitleaks dir . --config .gitleaks.toml --redact --exit-code 1
gitleaks git . --config .gitleaks.toml --redact --exit-code 1
```

Keep this section and `README.md` updated when the application stack is chosen.

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

## 16. Open Decisions

The single open-decision register is **section 9 of [`docs/srs.md`](docs/srs.md#9-open-decisions-od)**
(ADR 0004). It lists every decision previously kept here — application stack and layout,
OAuth configuration and token storage, similarity and candidate discovery, summary input,
playlist tolerance and unknown-language handling, supported languages, quota accounting and
cache policy, note schema and link rules, CI versions and the live-test budget — together with
options, a recommendation, an unconfirmed owner, a target milestone, linked ADRs and a status
(`OD-01`…`OD-17`). Add new decisions there, not here.

Record significant architectural or technical choices as ADRs in `docs/adr/`, and ensure each ADR
cites at least one distilled Second Brain note with a relative link (CI checks this).

---

**Core rule:** Build only what the approved requirements support, use only permitted YouTube API capabilities, protect user data and credentials, require explicit confirmation for playlist creation, test with fixtures in CI, and make every change reviewable and traceable.
