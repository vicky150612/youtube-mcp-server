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

## CI and live API separation

Ordinary CI must use mocks or reviewed, recorded fixtures and must not require the live
YouTube API or a developer account (TQ-05). A live API test must be separate, opt-in or
scheduled, use a fixed quota budget, pre-check its estimated cost, and report usage. No live
test workflow or budget has been approved or implemented yet. Do not add a YouTube
credential to ordinary CI.

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
