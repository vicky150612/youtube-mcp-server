# `src/` — application source (reserved)

This directory is reserved for the YouTube Video Intelligence MCP Server application code.
It contains no application code yet.

## Status

- The application programming language, framework, MCP SDK and package manager are **not
  decided**. They are open decision **OD-01** in the [SRS open decisions](../docs/srs.md#9-open-decisions-od).
- The Python files elsewhere in this repository (`scripts/`, `tests/`) are repository tooling
  for CI and validation. They do not select the application language.
- Do not add application code, package manifests or language-specific scaffolding here until
  OD-01 is decided and recorded in an ADR under [`docs/adr/`](../docs/adr/README.md).

## Expected contents once OD-01 is decided

The [logical architecture](../docs/architecture/overview.md) and [`AGENTS.md`](../AGENTS.md)
(section 6) define the boundaries the code must follow:

- MCP registration and request/response adaptation, kept separate from core service logic.
- Focused services for video/channel similarity, recommendations, engagement analysis and
  playlist planning.
- A YouTube provider interface that isolates all YouTube Data API v3 calls.
- Quota estimation and pre-checks before any provider call.

## Why this file exists

The CI build check (`scripts/ci_build.py`) requires `src/` to exist in every checkout, and Git
does not track empty directories.
