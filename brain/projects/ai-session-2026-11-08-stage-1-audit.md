---
title: AI session — Stage 1 repository audit
type: ai-session
author:
  - ChadDadChag
created: 2026-11-08
tags:
  - ai-session
  - audit
  - stage-1
sources:
  - "docs/adr/README.md"
  - "docs/testing/results.md"
  - "AGENTS.md"
---

# AI session — Stage 1 repository audit

## Goal

Carry out the Stage 1 repository audit and consistency specification (issues C1–C6, I-1–I-13,
N-1–N-5, D-1–D-3, F-1–F-7 and the missing deliverables) on branch
`fix/stage-1-audit-consistency`, without inventing approvals, authorship, dates or results.

## Tool

Claude Code (model Claude Opus 5.5), run by Git user `ChadDadChag`, whose team role is not
recorded in the repository. No secrets, tokens or credentials were shared (`AIP-04`). The
pinned CI tools (PyYAML 6.0.3, Ruff 0.17.4, Gitleaks 8.30.1) were installed in an isolated
environment outside the repository.

## What worked

- Recording each significant decision as a **Proposed** ADR with named owners kept proposals
  separate from approvals.
- Re-reading Google's and the MCP specification's pages found facts the notes lacked: the
  1000-video cap on `myRating=like`, the dated June 2026 search-bucket change, PKCE and
  loopback requirements for desktop OAuth clients, and the MCP elicitation rules that shape
  the playlist-confirmation design.
- Writing tests for the new validators exposed a real defect: `scripts/frontmatter.py` crashed
  on impossible dates instead of reporting them.

## What failed or needed correction

- A broad `git add -A brain` staged the untracked local `brain/.obsidian/` folder; it was
  unstaged before committing and the files were not modified. Later commits stage explicit
  paths only.
- A bulk-edit script ran its replacements in the wrong order and stopped on an assertion
  before writing anything; it was rerun in the correct order.
- An earlier test harness (credential-protection branch) failed on Windows because text-mode
  pipes add carriage returns; it now uses NUL-separated input.
- Some required metadata could not be completed: `author`/`created` for four notes wait for
  their contributors' confirmation, so Brain validation still fails on those notes.

## Outcome

Ten commits on `fix/stage-1-audit-consistency` (not pushed). On a fresh clone, Ruff, all 63
unit tests, skill and documentation validation and both Gitleaks scans pass. The build check
fails until the separate build/structure change is integrated, and Brain validation fails only
on the eight `author`/`created` fields awaiting contributor confirmation. An integration
simulation with the credential-protection and build/structure changes passed everything except
those same eight fields. Results: `docs/testing/results.md`.

## Human review

All changes must be reviewed in a pull request before merging (`AIP-01`, `SB-05`). Reviewer:
pending.

## Related

[[CI-Pipeline|CI Pipeline]], [[ai-session-2026-11-07-srs-drafting|AI session — SRS drafting and API research]],
[[log|Activity log]]
