# ADR 0005: Repository tooling (separate from the application stack)

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 3 (repository, CI and validators, per `docs/development-plan.md`)
- **Approval record:** The tooling below was introduced and merged in PR #11 (commit
  `cedd5a0`, "Implement CI pipeline and project workflow documentation"). Whether that PR had
  a recorded review could not be verified from this checkout. This ADR records the existing
  choice; team approval of the ADR itself is pending.
- **Related requirements:** `OD-01`, `NFR-08.2`, CI requirements (SRS §6.3), `TQ-05`; Stage 1
  audit issue I-4
- **Relevant Brain notes:** [CI Pipeline](../../brain/projects/CI-Pipeline.md)

## Context

`OD-01` listed "implementation language, framework and MCP SDK; lint/test/secret-scan tools"
as one open decision, while the repository already used a fixed toolchain for CI. The README
states that the Python tooling does not select the application language. The open decision
needed to be split so that an implemented choice is not shown as undecided, and an undecided
one is not shown as made.

## Decision

The **repository tooling** is:

| Purpose | Tool and version | Where pinned |
|---|---|---|
| CI platform | GitHub Actions on `ubuntu-24.04`; actions pinned by commit SHA (`actions/checkout` v4, `actions/setup-python` v5) | `.github/workflows/ci.yml` |
| Tooling language | Python 3.12, for `scripts/` and `tests/` only | `.github/workflows/ci.yml`, `ruff.toml` |
| YAML parsing | PyYAML 6.0.3 (`yaml.safe_load` only, shared in `scripts/frontmatter.py`) | `requirements-ci.txt` |
| Lint and formatting | Ruff 0.17.4, `line-length = 100`, rules `E4,E7,E9,F` | `requirements-ci.txt`, `ruff.toml` |
| Tests | Python `unittest`, discovered from `tests/` | `.github/workflows/ci.yml` |
| Secret scanning | Gitleaks 8.30.1, release checksum verified in CI, redacted output, full history | `.github/workflows/ci.yml`, `.gitleaks.toml` |

The **application** language, framework, MCP SDK and package manager remain open as `OD-01`.
Python tooling in this repository is not evidence of, or a commitment to, a Python
application.

## Alternatives considered

- **Leave `OD-01` as one item.** Misreports the implemented tooling as undecided. Rejected.
- **Treat the tooling as choosing the application stack.** Presents an unmade decision as made.
  Rejected.

## Consequences

- SRS `OD-01` covers only the application stack; `AGENTS.md`, `README.md` and the testing docs
  describe the tooling above.
- Changing a pinned tool version is done through a pull request that updates this table.
- If the application stack is later chosen to be Python, the tooling can be reused; otherwise
  the tooling stays independent of the application build.
