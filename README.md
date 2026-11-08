# YouTube Video Intelligence MCP Server

The project is in requirements/design work. The application language, framework, MCP SDK and
provider/service contracts are not yet approved (`OD-01`); the current Python checks support
repository tooling only and do not imply that the application is implemented in Python
([ADR 0005](docs/adr/0005-repository-toolchain.md)).

## Project documentation

- [Draft SRS](docs/srs.md) (version 0.3.0, approval pending), including the
  [open-decision register](docs/srs.md#9-open-decisions-od), and
  [requirement traceability](docs/traceability.md)
- [Logical architecture](docs/architecture/overview.md), [interface contracts (draft)](docs/api/interfaces.md)
  and [Architecture Decision Records](docs/adr/README.md) (all Proposed)
- [Testing strategy](docs/testing/README.md), [results](docs/testing/results.md),
  [defects](docs/testing/defects.md) and [skill evaluations](docs/testing/skill-evaluations.md)
- [GitHub development workflow](docs/development/github-workflow.md) and
  [development plan](docs/development-plan.md)
- [Stage reviews](docs/stage-reviews/README.md) and [research allocation](docs/research/allocation.md)
- [Second Brain index](brain/index.md) and the [`brain-ingest` skill](.claude/skills/brain-ingest/SKILL.md)
- [CI workflow](.github/workflows/ci.yml) and [contributor rules](AGENTS.md)

## Google Cloud project and quota

The SRS currently assumes that each developer uses their own Google Cloud project in OAuth
Testing mode with the default quota. This is a **proposal, not a decision** (`OD-14`). The
default quota includes a separate, small daily bucket for `search.list` calls
([SRS Appendix A](docs/srs.md#appendix-a--reference-youtube-api-quota)), and refresh tokens in
Testing mode expire after seven days. Never create extra Cloud projects to obtain more quota.

## Local repository checks

Install the CI tooling and run the same checks as CI:

```powershell
python -m pip install -r requirements-ci.txt
python scripts/ci_build.py
ruff check scripts tests
ruff format --check scripts tests
python -m unittest discover -s tests -v
python scripts/validate_skills.py --require brain-ingest
python scripts/validate_brain.py
python scripts/validate_docs.py
```

For secret scanning, install Gitleaks 8.30.1 and run both working-tree and history scans:

```powershell
gitleaks dir . --config .gitleaks.toml --redact --exit-code 1
gitleaks git . --config .gitleaks.toml --redact --exit-code 1
```

The build check is structural/syntax-only until an application build target is approved.
CI uses mocks/fixtures and does not call the live YouTube API.
