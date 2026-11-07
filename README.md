# YouTube Video Intelligence MCP Server

The project is in requirements/design work; application language, framework, MCP SDK, and
provider/service contracts are not yet approved. The current Python checks support repository
tooling only and do not imply that the application is implemented in Python.

## Project documentation

- [Draft SRS](docs/srs.md) and [requirement traceability](docs/traceability.md)
- [Logical architecture](docs/architecture/overview.md) and [ADR process](docs/adr/README.md)
- [Testing strategy and results](docs/testing/README.md)
- [GitHub development workflow](docs/development/github-workflow.md)
- [Stage 1 research allocation](docs/research/allocation.md)
- [CI workflow](.github/workflows/ci.yml)

## Local repository checks

Install the CI tooling and run the same checks available for the current skeleton:

```powershell
python -m pip install -r requirements-ci.txt
python scripts/ci_build.py
ruff check scripts tests
ruff format --check scripts tests
python -m unittest discover -s tests -v
python scripts/validate_skills.py
python scripts/validate_brain.py
```

For secret scanning, install Gitleaks 8.30.1 and run both working-tree and history scans:

```powershell
gitleaks dir . --config .gitleaks.toml --redact --exit-code 1
gitleaks git . --config .gitleaks.toml --redact --exit-code 1
```

The build check is structural/syntax-only until an application build target is approved.
CI uses mocks/fixtures and does not call the live YouTube API.
