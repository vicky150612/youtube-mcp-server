# Test results

Record only checks that were actually run. Include the date, exact command, result, and any
scope limitation. A passing validator/tooling suite is not evidence that product requirements
or live API behavior have been tested. Newest results first; older sections are kept unchanged
as historical evidence.

## 2026-11-08 — Final Stage 1 completion pass (current)

Fresh clone of `fix/stage-1-audit-consistency` at `75a21e5`, after integrating the PR-3 build and
structure changes (`d1e2b17`) and the PR-2 credential-protection commit (cherry-picked from
`63acd08`), completing note metadata from Git evidence and fixing DEF-010. Same pinned tools and
environment as below; not a GitHub Actions run (nothing pushed).

| Command | Result | Notes |
|---|---|---|
| `python scripts/ci_build.py` | Passed | 11 Python files; all required directories present |
| `ruff check scripts tests` | Passed | |
| `ruff format --check scripts tests` | Passed | 12 files already formatted |
| `python -m unittest discover -s tests` | Passed; 76 tests | Skill validator 19, Brain validator 28, CI command probes 2, documentation validator 10, Markdown helpers 3, build check 8, repository hygiene 4, line endings 2 |
| `python scripts/validate_skills.py --require brain-ingest` | Passed | 1 skill (`brain-ingest`) |
| `python scripts/validate_brain.py` | Passed | 14 notes, 105 wikilinks, 0 errors |
| `python scripts/validate_docs.py` | Passed | 31 Markdown files |
| `gitleaks dir . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | |
| `gitleaks git . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | Full history |
| `git ls-files --eol` | 67 files `i/lf`, 3 empty `.gitkeep` files `i/none`; none CRLF | |
| Exact-case check of 191 relative links and path sources against `git ls-files` | 0 mismatches | Guards against Windows-only passes on case-sensitive CI runners |
| AST scan of all Python files for duplicate definitions/imports and unreachable code | 0 problems | |

**Not run / unable to verify:** GitHub Actions results and the `main` ruleset (no authenticated
GitHub access; nothing pushed); live YouTube API tests (no approved budget or test account);
product tests (no application code, `OD-01`).

## 2026-11-08 — Stage 1 audit branch, first pass (superseded by the section above)

Local runs on Windows with the project-pinned tools in an isolated environment: Python 3.12.7,
PyYAML 6.0.3, Ruff 0.17.4, Gitleaks 8.30.1 (release checksum verified). These are not GitHub
Actions runs: nothing has been pushed, so no Actions result exists for this branch.

### A. Fresh clone of the committed branch (HEAD `523655e`)

| Command | Result | Notes |
|---|---|---|
| `python scripts/ci_build.py` | **Failed** | `src/` is not tracked on this branch. Fixed by the separate build/structure change (`ci/build-structure-formatting`, DEF-006); see run B. |
| `ruff check scripts tests` | Passed | |
| `ruff format --check scripts tests` | Passed | 9 files already formatted |
| `python -m unittest discover -s tests` | Passed; 63 tests | Includes the 21 original tests (2 inverted by ADR 0001) and new validator, documentation and line-ending tests |
| `python scripts/validate_skills.py --require brain-ingest` | Passed | 1 skill validated (`brain-ingest`) |
| `python scripts/validate_brain.py` | **Failed; 8 errors** | Only missing `author`/`created` on `Agent-Skills-Format.md`, `MCP-Architecture.md`, `MCP-Tools-and-Resources.md` (Person 2) and `CI-Pipeline.md` (Person 3). These values must be confirmed by the contributors (ADR 0002); zero broken wikilinks remain. |
| `python scripts/validate_docs.py` | Passed | 29 Markdown files |
| `gitleaks dir . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | |
| `gitleaks git . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | Full history |

### B. Integration simulation (throwaway clone; no real branch changed)

The audit branch plus the credential-protection commit `63acd08` (cherry-picked; one
`CHANGELOG.md` conflict resolved by keeping both entries) plus the uncommitted PR-3 worktree
changes (conflicts in `scripts/validate_brain.py`, `scripts/validate_skills.py` and
`tests/test_ci_validators.py` resolved by keeping the audit versions, which already contain
PR-3's formatting). Run before the line-ending commit `523655e`.

| Command | Result | Notes |
|---|---|---|
| `python scripts/ci_build.py` | Passed | 10 Python files; all required directories present |
| `ruff check` / `ruff format --check scripts tests` | Passed | 11 files formatted |
| `python -m unittest discover -s tests` | Passed; 72 tests | Adds the 3 hygiene tests and 8 build tests |
| `validate_skills.py --require brain-ingest`, `validate_docs.py` | Passed | 31 Markdown files |
| `validate_brain.py` | **Failed; 8 errors** | Same pending contributor metadata as run A |
| Gitleaks working tree and history | Passed; no leaks | |

### C. Other checks

| Check | Result |
|---|---|
| `git diff --cached --ignore-cr-at-eol --stat` for the line-ending commit | Only the two new files changed content; 15 files changed line endings only |
| `python -m unittest tests.test_line_endings` after renormalisation | Passed; no tracked file stored with CRLF |
| Grep for stale filenames, top-level `skills/` paths and outdated quota statements | Only intentional historical or cautionary mentions remain |
| Duplicate note titles in `brain/` | None |

**Not run / unable to verify:** GitHub Actions runs, the `main` ruleset and PR review records
(no authenticated GitHub access); live YouTube API tests (no approved budget or test account;
none exist); product tests (no application code); an independent re-run of the `brain-ingest`
evaluation by a team member.

## 2026-11-08 — I-13 credential protection (originally commit `63acd08` on `fix/gitignore-credential-protection`; integrated into this branch by cherry-pick)

Local run on Windows with the project-pinned tools: Python 3.12.7, PyYAML 6.0.3, Ruff 0.17.4,
Gitleaks 8.30.1 (release checksum verified). Uncommitted branch; not a GitHub Actions run.

| Command/check | Result | Scope |
|---|---|---|
| `python -m unittest tests.test_repository_hygiene -v` | Passed; 3 tests | Credential paths ignored; `.env.example` and project files not ignored; no tracked file matches an ignore rule. |
| Same test module against the previous `.gitignore`, in a throwaway repository | Failed as expected (credential-ignore test) | Confirms the test detects missing credential patterns. |
| Same test module with a force-added `token.json`, in a throwaway repository | Failed as expected (tracked-file test) | Confirms the test detects a credential file that is already tracked. |
| `python -m unittest discover -s tests` | Passed; 24 tests | The 21 existing tests and the 3 new tests. |
| `ruff check scripts tests` | Passed | |
| `ruff format --check scripts tests` | Failed; 4 files would be reformatted | Pre-existing: `scripts/frontmatter.py`, `scripts/validate_brain.py`, `scripts/validate_skills.py`, `tests/test_ci_validators.py`. Addressed separately under C4. |
| `python scripts/ci_build.py` | Failed | Pre-existing: `src/` is not tracked. Addressed separately under C4. |
| `python scripts/validate_skills.py` | Passed, but vacuously | Scans only `skills/`; the real skill is not validated. Tracked as C3. |
| `python scripts/validate_brain.py` | Failed; 36 errors | Pre-existing: 33 broken wikilinks and 3 notes using `source` instead of `sources`. Tracked as C1 and C2. |
| `gitleaks dir . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | Working tree, including untracked local files. |
| `gitleaks git . --config .gitleaks.toml --redact --no-banner --exit-code 1` | Passed; no leaks | 11 commits of Git history. |

## 2026-11-07 — Part 5 and Part 6 documentation (historical)

> **Historical:** this table reflected a local working tree that contained an untracked `src/`
> directory and fewer Brain notes. The Part 7 run and the main-branch Actions run below found
> that Build, Lint (format) and Brain validation actually failed on committed `main`. Kept as
> evidence; superseded by the sections above.

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

At the time of this Part 5/6 run, the workflow had not yet run on the default branch. The
later Part 7 check below records an actual main-branch run; neither run validates this
uncommitted documentation branch.

## 2026-11-07 — Part 7 technical-constraint review (historical)

| Command/check | Result | Scope |
|---|---|---|
| `python scripts/ci_build.py` | Passed | Structural/syntax check; 5 Python files parsed. No application build target exists. |
| `ruff check scripts tests` | Passed | Repository CI scripts and tests. |
| `ruff format --check scripts tests` | Failed; 4 existing files would be reformatted | `scripts/frontmatter.py`, `scripts/validate_brain.py`, `scripts/validate_skills.py`, and `tests/test_ci_validators.py`. No product or Part 7 source code was changed. |
| `python -m unittest discover -s tests -v` | Passed; 21 tests | Validator tests and CI failure-propagation probes; no product behavior. |
| `python scripts/validate_skills.py` | Passed | No `SKILL.md` exists; the validator reports the empty state explicitly. |
| `python scripts/validate_brain.py` | Failed; 39 existing errors | Three notes have `source` where the validator requires `sources`; unresolved links occur in the Brain index, log, and existing notes. Brain-owned files were not changed. |
| Markdown link check | Passed; 31 Markdown files and 20 internal Markdown links | Relative Markdown targets resolve. Obsidian links are separately checked by the Brain validator, which has the failures listed above. |
| Requirement-ID coverage check | Passed; 29 FR/NFR/TQ/SK identifiers | Every expected ID has a row in `docs/traceability.md`. |
| Mermaid source check | Passed; 1 flowchart and 28 directed edges | Source-level header/edge check only; no Mermaid renderer was run. |
| Gitleaks working-tree/history scans | Not run | The `gitleaks` executable is not installed in this environment. |
| `git diff --check` | Reports CRLF as trailing whitespace on added lines in the pre-existing CRLF Markdown files | No other whitespace issue was observed. The repository's tracked Markdown uses CRLF; use `git -c core.whitespace=cr-at-eol diff --check` to check content while respecting those line endings. |

These are local results, not a GitHub Actions run. Technical constraints were reviewed
against the SRS and documented in the architecture and test scenarios; product behavior,
quota enforcement, OAuth handling, playlist confirmation, and live API safeguards remain
unimplemented and untested.

The latest main-branch GitHub Actions run available during this review was
[run 42382715003](https://github.com/vicky150612/youtube-mcp-server/actions/runs/42382715003)
at commit `5953462d2ba79997596ad312131eeee9ac11689c`. It completed with failures:

| Job | Result | Observed cause |
|---|---|---|
| Build | Failed | The checkout does not contain the empty `src/` directory, which the structural build script requires. The directory exists only in the local working tree and has no tracked file. |
| Lint | Failed | `ruff format --check scripts tests` reports four existing files would be reformatted. |
| Automated tests | Passed | Deterministic test suite passed. |
| Secret scanning | Passed | Gitleaks scanned Git history with redacted output. |
| Skill validation | Passed | No `SKILL.md` files exist yet; the validator reports this state. |
| Brain validation | Failed | 39 errors in existing Brain notes/index/log, as detailed above. |

This is a run on `main`, not a run for this uncommitted branch. The Brain failures require
coordination with Person 2 before changing vault conventions or notes; the build sentinel
and Ruff formatting failures are pre-existing CI follow-ups outside the Part 7 documentation
changes.
