---
name: local-check
description: Build and test YouTube MCP, launch a local fixture server, and verify a read-only tool.
---

# Local check

Run `python scripts/local_check.py` from the repository root in the Python
3.12 virtual environment with the dev extra installed.

Report PASS or FAIL for the build, automated tests, and read-only fixture MCP
invocation. Record the date and observed results in the team's evaluation log.
The fixture server requires no Google credentials.

[[brain/resources/youtube-api/api-methods]]
