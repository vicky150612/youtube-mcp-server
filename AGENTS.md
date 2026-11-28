# YouTube MCP Server Contributor Guide

These instructions apply to contributors and AI coding assistants. The approved
requirements are defined by the project SRS; implementation decisions must not
silently change that baseline.

## Project purpose and approved baseline

The project is the YouTube Video Intelligence MCP Server described in
`YT-MCP-SRS.pdf`, Version 1.0. It provides YouTube video and channel discovery,
personalized recommendations, engagement analysis, and playlist planning and
creation through MCP.

The SRS is the source of truth for functional requirements (FR), non-functional
requirements (NFR), and skill requirements (SK). The supporting
`Project_1_YouTube_MCP.pdf` and `SDLC_and_Workflow.pdf` provide product and
team-process detail. The PDFs are currently excluded from Git by `.gitignore`;
do not remove those ignore rules or add the documents to a commit without team
approval. If a local copy is unavailable, ask the team for the approved source
before making requirements decisions.

Use the official YouTube Data API v3 only. Scraping, unofficial APIs, and
watch-history access are out of scope. Preserve the SRS's quota and confirmation
safeguards.

## Repository structure

```text
src/youtube_mcp/       Python MCP server package
  auth/                OAuth and token handling
  cache/               Cache implementation
  mcp/                 MCP tools and schemas
  models/              Shared data models
  providers/            YouTube provider interface and implementations
  quota/               Quota management
  services/            Product and analysis services
tests/
  unit/                Isolated behavior tests
  integration/         Component tests using fixtures
  e2e/                 MCP client workflows
  fixtures/            Synthetic test data only
skills/                One directory per Agent Skill
brain/                 PARA knowledge base
docs/
  adr/                 Architecture Decision Records
  api/                 User and developer API documentation
  architecture/        Architecture and interface documents
  stage-reviews/        Stage review notes
.github/workflows/     CI workflows
```

Keep new files in the appropriate existing package or documentation area. Do
not create a second Python package for the same application.

## Python environment and development commands

Use Python 3.12, `pip`, a virtual environment, the official MCP Python SDK, and
local stdio transport as specified by the SRS. The existing setup guide
documents this bootstrap command:

```text
python -m venv .venv
```

Install the project and dev tools with `python -m pip install -e ".[dev]"`.
Run `python -m pytest -q`, `ruff check .`, and `python scripts/local_check.py`.
See the README for activation and fixture-mode startup.

## Branching, commits, and pull requests

- Never work directly on `main`; use a task-specific branch.
- Before starting, check for an existing branch related to the task. Ask before
  creating a new branch or reusing another contributor's branch.
- Do not push unless the task explicitly requests a push.
- Keep commits meaningful and incremental, and make each member's contribution
  visible in Git history.
- Track work and defects with GitHub Issues and link relevant issues and PRs.
- Submit every change to code, skills, or Brain notes through a pull request.
- Keep PRs small and reviewable. Do not merge an AI-generated change without
  human review.

## Mandatory review

Every pull request must receive at least one review before merge. A human must
review AI-generated changes, and the team remains responsible for every merged
line. Contributors must be able to explain their changes.

## Testing conventions

- Add unit tests for focused functions, services, and MCP tools.
- Test service/provider interactions with fixtures or mocks.
- Add an MCP-client end-to-end test for each implemented FR-01 through FR-05
  workflow and negative tests for applicable failure cases.
- Keep ordinary CI deterministic and offline: use fixtures/mocks, not live
  YouTube API calls. Live API checks belong only in a separately approved,
  quota-bounded scheduled workflow.
- Test that over-budget or unknown-cost workflows make no provider calls.
- Add a regression test for every significant defect.
- Record dated Agent Skill evaluation results for each skill at every stage.
- Use the commands in the Python environment section above.

Never put real user data in fixtures or logs.

## Provider, service, and MCP boundaries

- All YouTube API access goes through the provider abstraction. The live
  provider uses only the official YouTube Data API v3; services must not call
  Google APIs directly or process raw API responses.
- Services operate on internal models and depend on provider interfaces so
  they can be tested with fixture-backed or mock providers.
- The MCP layer validates inputs, invokes the appropriate service, and
  serializes structured results and errors; it must not contain product
  algorithms or direct API calls.
- Quota costs must be checked before provider calls; unknown costs fail closed.
- Playlist creation requires explicit MCP elicitation confirmation bound to
  the proposal. Missing or declined confirmation must make no writes.

Follow the detailed contracts in
`docs/architecture/Architecture_and_Interface_Plan.md` when implementing.

## Brain and Agent Skills conventions

The `brain/` directory is the team's Obsidian vault and follows PARA:
`inbox/`, `projects/`, `areas/`, `resources/`, and `archive/`. `brain/index.md`
is the entry point; `brain/log.md` records Brain skill runs. Use wikilinks and
record sources, relevant requirement IDs, and issue/PR references in notes.
Each stage ends with a short review note in `docs/stage-reviews/`. Brain
changes, including AI-generated notes, require a reviewed PR.

Each Agent Skill belongs in its own kebab-case directory under `skills/` and
contains a `SKILL.md` with YAML frontmatter whose name matches the directory
and includes a description. The five SRS skills are:

- `brain-ingest`
- `brain-refine`
- `brain-query`
- `local-check`
- `video-to-playlist`

Skills must reference at least one Brain note and be evaluated before each
stage submission. They must not bypass quota checks or playlist confirmation.

## Security restrictions

- Never commit API keys, OAuth client secrets, access tokens, or refresh tokens.
- Never paste secrets or credentials into AI tools.
- Never put real user data in fixtures or logs.
- Store tokens securely outside the repository and request only the minimum
  OAuth scopes.
- Never bypass quota checks, fail-open behavior for unknown costs, or explicit
  playlist confirmation.
- Keep credentials and local environment files excluded by `.gitignore`.

## Documentation and traceability

- Keep the SRS as the requirements authority; do not add unapproved scope.
- Preserve requirement IDs. Trace each requirement through
  `requirement -> issue -> PR -> test -> skill -> Brain note`.
- Record significant design decisions as ADRs in `docs/adr/` and cite at least
  one distilled Brain note in each ADR and skill.
- Maintain architecture/design documents and user/developer API documentation
  as they are agreed and implemented.
- Record significant AI sessions as `ai-session` notes with their goal and
  what worked or failed.
- Update relevant documentation and traceability links with behavior changes.
