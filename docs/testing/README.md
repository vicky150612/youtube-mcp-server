# Testing and validation

## Test levels

| Level                     | Scope                                                                                                                            | Current status                                         |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Unit (TQ-01)              | Service/tool logic, including similarity, duration parsing, and playlist constraints                                             | Product tests pending; CI validator unit tests exist.  |
| Integration (TQ-02)       | Component interactions, especially the provider boundary                                                                         | Pending provider implementation.                       |
| System (TQ-03)            | FR-01 through FR-05 through the MCP interface                                                                                    | Pending application/MCP implementation.                |
| Negative/security (TQ-04) | Invalid IDs, inaccessible videos, missing metadata, quota/auth/rate errors, prompt injection, secret handling, and personal data | Product tests pending; validator negative tests exist. |
| Quota pre-check (TQ-06)   | Reject over-budget work before any provider/API call                                                                             | Pending quota implementation.                          |
| Skill evaluation (TQ-07)  | Evaluate each implemented skill before stage submission                                                                          | Pending; do not claim unevaluated skills.              |
| Regression (TQ-08)        | Add a regression test for each significant defect                                                                                | Required as defects are found.                         |

`tests/` is the current executable test location. Put synthetic fixtures under
`tests/fixtures/`; never place real user data, credentials, or live-account responses in
fixtures. Keep test design/results here and record actual runs in
[`results.md`](results.md). Record discovered defects in [`defects.md`](defects.md) without
claiming an empty log means the application has no defects.

## Required technical-constraint scenarios

These are product test cases derived from the SRS, not claims that product tests or
application modules exist. Implement them with mocks/synthetic fixtures when the relevant
components are available. Do not substitute validator tests for these cases.

| Area | Positive/negative scenario | Expected result | Status |
|---|---|---|---|
| Similarity / API limits | Fetch candidate metadata through the provider, then rank fixture metadata with weighted scoring or TF-IDF/cosine. | Ranking is deterministic; ranking performs no API calls. Do not call a related-video/channel endpoint. | Pending product implementation |
| Library data | Build recommendations/analysis from liked videos, subscriptions, and playlists; provide no watch-history fixture or provider method. | Results identify supported source data; no feature depends on watch history. | Pending product implementation |
| Quota costs | Plan distinct read, search, paginated-list, playlist-create, and playlist-item-create operations. | Use the applicable method cost and bucket for each request/page/write; do not treat all calls as equal. | Pending quota estimator |
| Quota pre-check | Planned general-unit cost exceeds remaining general units; separately, a search workflow has no remaining `search.list` calls. | Each workflow is rejected before the first provider/API call; mock provider call count is zero. | Pending quota estimator |
| Quota cache / unknown cost | Repeat an eligible cached read; separately plan an operation whose current cost is unavailable. | Cache hit makes no API call; unknown cost fails closed before any API call. | Pending quota/cache implementation |
| OAuth | Test allowed scopes, protected token storage and refresh success; simulate expired seven-day Testing-mode token, revoked token, and refresh failure. | No secrets in logs/repository; usable refresh succeeds; expired/revoked/failed refresh returns a clear re-authorisation action; no protected operation proceeds unauthorised. | Pending OAuth implementation |
| Playlist confirmation | Display a proposal and confirm that exact proposal; then test missing confirmation, explicit rejection, malformed/invalid confirmation, and confirmation after the proposal changes. | Only valid explicit confirmation for the unchanged displayed proposal permits creation; all other cases create nothing. | Pending playlist implementation |
| Untrusted metadata | Put instruction-like text in a title, description, or tag while confirmation is absent or rejected. | Metadata cannot change system behavior or cause a playlist write. | Pending playlist implementation |
| No YouTube channel | Mock `youtubeSignupRequired` for an authorised Google account without a YouTube channel. | Return a clear typed error and create no playlist or playlist items. | Pending provider/playlist implementation |
| Summary input | Supply metadata or a user-provided transcript; try an unavailable transcript source. | Use only an input approved under OD-04; do not scrape or call an unofficial transcript API. | Pending OD-04 and skill implementation |

## CI and live API separation

Ordinary CI must use mocks or reviewed, recorded fixtures and must not require the live
YouTube API or a developer account (TQ-05). A live API test must be separate, opt-in or
scheduled, use a fixed quota budget, pre-check its estimated cost, and report usage. No live
test workflow or budget has been approved or implemented yet. Do not add a YouTube
credential to ordinary CI.

Before any live-test workflow is enabled, the team must approve a numeric per-run budget
for every applicable quota bucket (including the general-unit budget and any method-specific
call bucket used by the test). The workflow must require explicit finite positive limits,
fail closed when a limit or operation cost is missing/invalid, reserve/check each operation
and page before calling the API, stop before a call that would exceed any limit, and report
the estimated and actual usage. A zero budget disables calls; it must not mean unlimited.
Scheduled/manual triggers, protected credentials, and concurrency controls do not replace
these code-level caps. Keep the live workflow separate from ordinary CI and never request
additional Google Cloud projects to evade quota limits.

The current CI workflow is not a live-test workflow. The separate live workflow, numeric
budget, operation-cost implementation, and live credentials are all pending team approval;
none is claimed to exist.

The current six-job CI workflow runs repository structural/syntax checks, Ruff, deterministic
unit tests, Gitleaks, and the skill/Brain validators. It does not claim product build,
provider integration, MCP system, or live API coverage. See [[CI Pipeline]] for the existing
CI implementation note.

## Current local commands

From the repository root, install the tooling and run:

```powershell
python -m pip install -r requirements-ci.txt
python scripts/ci_build.py
ruff check scripts tests
ruff format --check scripts tests
python -m unittest discover -s tests -v
python scripts/validate_skills.py
python scripts/validate_brain.py
gitleaks dir . --config .gitleaks.toml --redact --exit-code 1
gitleaks git . --config .gitleaks.toml --redact --exit-code 1
```

Install Gitleaks 8.30.1 separately. The repository build command is a structural and Python
syntax check only: no application build target exists yet.
