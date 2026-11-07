# Test results

Record only checks that were actually run. Include the date, exact command, result, and any
scope limitation. A passing validator/tooling suite is not evidence that product requirements
or live API behavior have been tested.

## 2026-11-07 — Part 5 and Part 6 documentation

| Command/check                                                                                 | Result                                                         | Scope                                                                                                                |
| --------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `python scripts/ci_build.py`                                                                  | Passed                                                         | Structural/syntax check; 5 Python files parsed. This is not an application build.                                    |
| `ruff check scripts tests`                                                                    | Passed                                                         | Repository CI scripts and tests.                                                                                     |
| `ruff format --check scripts tests`                                                           | Passed                                                         | Repository CI scripts and tests.                                                                                     |
| `python -m unittest discover -s tests -v`                                                     | Passed; 21 tests                                               | Validator tests and CI failure-propagation probes; no product behavior.                                              |
| `python scripts/validate_skills.py`                                                           | Passed                                                         | No `SKILL.md` exists; validator reports the empty state explicitly.                                                  |
| `python scripts/validate_brain.py`                                                            | Passed                                                         | One note checked; no Brain wikilinks present.                                                                        |
| `gitleaks dir . --config .gitleaks.toml --redact --no-banner --exit-code 1` (Gitleaks 8.30.1) | Passed; no leaks                                               | Working-tree scan.                                                                                                   |
| `gitleaks git . --config .gitleaks.toml --redact --no-banner --exit-code 1` (Gitleaks 8.30.1) | Passed; no leaks                                               | Four committed revisions scanned. Synthetic credential-detection fixtures passed in Part 4 validation on 2026-11-06. |
| Markdown link check                                                                           | Passed; 19 Markdown files, 20 internal links, 8 Obsidian links | Includes docs and Brain; code examples are excluded.                                                                 |
| Workflow/forms YAML, requirement-ID coverage, Mermaid flowchart syntax                        | Passed; 6 jobs, 2 issue forms, 26 unique IDs, 28 diagram edges | Static syntax/consistency check; no GitHub Actions run.                                                              |
| `git diff --check` and `git diff --cached --check`                                            | Passed                                                         | Unstaged documentation and pre-existing staged Part 4 changes.                                                       |

The first structural check found that `src/` was absent from the checkout, which would have
made the existing CI build job fail. Added `src/.gitkeep` so the expected skeleton directory
is present in Git; the subsequent build check passed.

No live YouTube API tests were run. The current repository has no application source/build
target, provider, or MCP server; product-level TQ-01 through TQ-06 tests remain pending.

GitHub Actions was not run remotely. The workflow is not present on GitHub's default branch
yet (`gh run list --workflow ci.yml` returned 404), so the documented checks were executed
locally instead.
