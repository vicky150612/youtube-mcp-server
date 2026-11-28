# YouTube MCP Server

Python 3.12 stdio MCP server for YouTube discovery and account workflows.
See the [provider integration and live demo](docs/api/provider.md).

## Setup

Create a virtual environment using `python -m venv .venv` and activate it
with `.venv\Scripts\Activate.ps1` on Windows PowerShell or
`source .venv/bin/activate` on POSIX. Run from the repository root.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
python scripts/validate_docs.py
python scripts/local_check.py
```

Launch fixture mode with
`python -m youtube_mcp.server --fixtures tests/fixtures/provider.json`.
