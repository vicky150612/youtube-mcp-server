# Defect log

Record confirmed defects with a reproducible description and a regression-test reference
(`TQ-08`). Link the related GitHub issue and PR only when those identifiers exist. Do not use this
file as evidence that untested product behaviour is defect-free. No product code exists yet, so
all defects below are in repository tooling or content.

| ID | Summary | Severity | Regression test | Status |
|---|---|---|---|---|
| DEF-001 | Skill validation passed vacuously: `scripts/validate_skills.py` scanned only `skills/`, so the real skill in `.claude/skills/` was never validated (audit C3). | High | `test_empty_skills_directory_fails`, `test_missing_skills_directory_fails`, `test_repository_skill_is_discovered_and_valid` (`tests/test_ci_validators.py`) | Fixed on `fix/stage-1-audit-consistency` |
| DEF-002 | Three incompatible note schemas; notes written from the `brain-ingest` template failed validation (audit C1). | High | `test_brain_ingest_template_produces_a_valid_note` and the schema tests in `tests/test_ci_validators.py` | Fixed on `fix/stage-1-audit-consistency`; 4 notes still await contributor metadata |
| DEF-003 | 33 broken wikilinks in the Brain; wikilinks in code were counted as links (audit C2). | Medium | `test_wikilinks_in_code_are_literal_text`, `test_heading_links_are_checked`, `test_frontmatter_alias_is_not_a_link_target` | Fixed on `fix/stage-1-audit-consistency` |
| DEF-004 | `scripts/frontmatter.py` crashed with an unhandled `ValueError` on an impossible unquoted date such as `2026-13-01`, because PyYAML raises `ValueError` rather than a `YAMLError` (found while testing the C1 schema). | Medium | `test_impossible_unquoted_date_is_reported_not_raised` | Fixed on `fix/stage-1-audit-consistency` |
| DEF-005 | Obsidian wikilinks in `docs/` render as plain text on GitHub; nothing validated documentation links (audit I-6). | Low | `tests/test_validate_docs.py` | Fixed on `fix/stage-1-audit-consistency` |
| DEF-006 | CI build job failed on every checkout because the empty `src/` directory is not tracked (audit C4). | High | `tests/test_ci_build.py` (on the PR-3 worktree) | Fixed on `ci/build-structure-formatting` (uncommitted worktree); not integrated |
| DEF-007 | `ruff format --check` failed on four files formatted at a narrower width than `ruff.toml` (audit C4). | Medium | CI Lint job (`ruff format --check`) | Fixed on `ci/build-structure-formatting`; the files rewritten on this branch are formatted; `scripts/ci_build.py` and any untouched file depend on integration |
| DEF-008 | `.gitignore` did not protect credential files (audit I-13). | High | `tests/test_repository_hygiene.py` (on `fix/gitignore-credential-protection`) | Fixed in local commit `63acd08`; not integrated |
| DEF-009 | The hygiene test failed on Windows because text-mode pipes added carriage returns to `git check-ignore` input (found while implementing DEF-008). | Low | The same test, now using NUL-separated input | Fixed in `63acd08` |
