# Requirement traceability

**Status:** Updated 2026-11-08 on branch `fix/stage-1-audit-consistency` (not yet merged). No
product code exists, so no functional or non-functional requirement is implemented or tested.
**Requirement source:** [`docs/srs.md`](srs.md) (version 0.3.0, not approved).

Chain: requirement → GitHub issue → pull request → test → skill → Brain note (`SE-05`).

## Evidence rules

- **PR numbers** come from merge commits in Git history: #11 (CI pipeline and workflow docs),
  #12 (Second Brain and `brain-ingest`), #14 (SRS 0.2.0), #15 (Person 1 research notes),
  #17 (Person 3 research notes). Their GitHub review records could not be verified from the
  repository.
- **Issue numbers:** only #16 is referenced in earlier documentation (a documentation task); its
  state could not be verified. No implementation issues exist yet. "None yet" means no issue has
  been filed; do not invent one.
- **Branch** means the work is on `fix/stage-1-audit-consistency`, committed but not reviewed or
  merged.
- **Tests:** tooling tests validate repository checks, not product behaviour.
- Brain-note links use the note files under `brain/`.

## Functional requirements

| Requirement | Issue | PR | Test evidence | Skill | Brain notes | Status |
|---|---|---|---|---|---|---|
| `FR-01` Similar videos | None yet | #14 (SRS) | None (product) | `video-to-playlist` (planned) | [Video](../brain/resources/YouTube-Video-Resource.md), [TF-IDF](../brain/resources/TF-IDF-and-Cosine-Similarity.md), [API](../brain/resources/YouTube-Data-API.md) | Specified |
| `FR-02` Similar channels | None yet | #14 | None | — | [Channel](../brain/resources/YouTube-Channel-Resource.md), [TF-IDF](../brain/resources/TF-IDF-and-Cosine-Similarity.md) | Specified |
| `FR-03` Recommendations | None yet | #14 | None | — | [Playlist](../brain/resources/YouTube-Playlist-Resource.md), [Video](../brain/resources/YouTube-Video-Resource.md) | Specified |
| `FR-04` Engagement analysis | None yet | #14 | None | — | [Playlist](../brain/resources/YouTube-Playlist-Resource.md), [Video](../brain/resources/YouTube-Video-Resource.md) | Specified; `OD-05` open |
| `FR-05` Playlist creation | None yet | #14; branch (two-phase confirmation, ADR 0007) | Specified only: CONF-01…15 in [testing](testing/README.md) | `video-to-playlist` (planned) | [Playlist](../brain/resources/YouTube-Playlist-Resource.md), [MCP Tools](../brain/resources/MCP-Tools-and-Resources.md) | Specified; design proposed |

## Non-functional requirements

| Requirement | Issue | PR | Test evidence | Brain notes | Status |
|---|---|---|---|---|---|
| `NFR-01` Official API only | None yet | #14 | None | [API](../brain/resources/YouTube-Data-API.md) | Specified |
| `NFR-02.1` Quota budget | None yet | #14; branch (Appendix A canonical, ADR 0006) | None | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Specified |
| `NFR-02.2` Quota tracking and pre-check | None yet | #14; branch (estimate limits) | Specified in [testing](testing/README.md) | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Specified |
| `NFR-02.3` Unknown cost fails closed | None yet | Branch (proposed) | Specified | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Proposed |
| `NFR-03.1` Minimum scopes | None yet | #14; branch (ADR 0008) | Specified | [OAuth](../brain/resources/OAuth-Authentication.md) | Specified; scopes proposed |
| `NFR-03.2` Safe token storage | None yet | #14; branch (ADR 0008) | Specified | [OAuth](../brain/resources/OAuth-Authentication.md) | Specified |
| `NFR-03.3` Re-authorisation | None yet | #14 | Specified | [OAuth](../brain/resources/OAuth-Authentication.md) | Specified |
| `NFR-04.1` Input validation | None yet | #14 | Specified | [Errors](../brain/resources/YouTube-API-Errors.md) | Specified |
| `NFR-04.2` Prompt-injection resistance | None yet | #14 | Specified (CONF-13) | [Video](../brain/resources/YouTube-Video-Resource.md) | Specified |
| `NFR-04.3` Confirmation integrity | None yet | Branch (proposed, ADR 0007) | Specified (CONF-01…15) | [MCP Tools](../brain/resources/MCP-Tools-and-Resources.md) | Proposed |
| `NFR-05.1` No secrets in repository | None yet | #11 (Gitleaks CI); branch (credential `.gitignore` rules, cherry-picked from `63acd08`) | Gitleaks CI job; `tests/test_repository_hygiene.py` | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Partly implemented (repository level) |
| `NFR-05.2` No real personal data | None yet | #14; branch (`tests/fixtures/README.md` fixture rules) | None (product fixtures do not exist yet) | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Specified |
| `NFR-06.1` Channel-less accounts | None yet | #14 | Specified | [Errors](../brain/resources/YouTube-API-Errors.md), [Playlist](../brain/resources/YouTube-Playlist-Resource.md) | Specified |
| `NFR-06.2` Graceful failure | None yet | #14; branch (typed errors in [interfaces](api/interfaces.md)) | Specified | [Errors](../brain/resources/YouTube-API-Errors.md) | Specified |
| `NFR-07` Provider isolation | None yet | #14 | None | [MCP Architecture](../brain/resources/MCP-Architecture.md) | Specified |
| `NFR-08.1` Testability | None yet | #14 | None (product) | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Specified |
| `NFR-08.2` CI isolation from live API | None yet | #11 | CI uses no YouTube credentials | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Implemented for current tooling |
| `NFR-08.3` Separate live tests | None yet | Branch (requirements documented) | None; workflow deferred (`OD-13`) | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Not implemented |
| `NFR-08.4` Live-test caps fail closed | None yet | Branch (proposed) | Specified | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Proposed |
| `NFR-09` MCP compatibility | None yet | #14; branch (wording, compatibility statement) | None | [MCP Architecture](../brain/resources/MCP-Architecture.md) | Specified |
| `NFR-10` Deterministic computation | None yet | #14 | None | [TF-IDF](../brain/resources/TF-IDF-and-Cosine-Similarity.md) | Specified |
| `NFR-11` Documentation | None yet | #11, #14; branch | `scripts/validate_docs.py` checks documentation links | [MCP Architecture](../brain/resources/MCP-Architecture.md) | Partly done (no user docs yet) |

## Skill requirements

| Requirement | Issue | PR | Test evidence | Skill | Brain notes | Status |
|---|---|---|---|---|---|---|
| `SK-01` `brain-ingest` | None yet | #12; branch (rewrite) | `scripts/validate_skills.py --require brain-ingest`; template test in `tests/test_ci_validators.py`; [evaluation](testing/skill-evaluations.md) | `.claude/skills/brain-ingest` | [Agent Skills](../brain/resources/Agent-Skills-Format.md) | Implemented; self-evaluated |
| `SK-02` `brain-refine` | None yet | — | None | Planned | [Agent Skills](../brain/resources/Agent-Skills-Format.md) | Not implemented |
| `SK-03` `brain-query` | None yet | — | None | Planned | [Agent Skills](../brain/resources/Agent-Skills-Format.md) | Not implemented |
| `SK-04` `local-check` | None yet | — | None | Planned | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Not implemented |
| `SK-05` `video-to-playlist` | None yet | — | None | Planned | [MCP Tools](../brain/resources/MCP-Tools-and-Resources.md), [Playlist](../brain/resources/YouTube-Playlist-Resource.md) | Not implemented; `OD-04` open |

## Testing requirements

| Requirement | Issue | PR | Test evidence | Brain notes | Status |
|---|---|---|---|---|---|
| `TQ-01` Unit tests | None yet | #11; branch | Tooling unit tests in `tests/`; no product unit tests | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Tooling only |
| `TQ-02` Integration tests | None yet | — | None | — | Not implemented |
| `TQ-03` MCP system tests | None yet | — | None | [MCP Architecture](../brain/resources/MCP-Architecture.md) | Not implemented |
| `TQ-04` Negative tests | None yet | Branch (scenarios) | Tooling negative tests; product scenarios specified | [Errors](../brain/resources/YouTube-API-Errors.md) | Specified |
| `TQ-05` CI/live separation | None yet | #11 | CI is fixture/local-only | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Partly implemented |
| `TQ-06` Quota pre-check | None yet | — | Specified | [Quota](../brain/resources/YouTube-API-Quota-Management.md) | Not implemented |
| `TQ-07` Skill evaluations | None yet | Branch | [skill-evaluations.md](testing/skill-evaluations.md) (`brain-ingest`) | [Agent Skills](../brain/resources/Agent-Skills-Format.md) | Started (Stage 1) |
| `TQ-08` Regression tests | None yet | Branch | Regression tests for tooling defects ([defects](testing/defects.md)) | [CI Pipeline](../brain/projects/CI-Pipeline.md) | Tooling only |

## Engineering, Second Brain and AI-policy requirements

| Requirement | PR | Evidence | Status |
|---|---|---|---|
| `SE-01` SRS | #14; branch | [`docs/srs.md`](srs.md) 0.3.0 | Draft, not approved |
| `SE-02` Architecture/UML | Branch | [Architecture overview](architecture/overview.md) (component and sequence diagrams) | Logical only; Stage 2 deliverable |
| `SE-03` ADRs | Branch | [ADR index](adr/README.md): 0001–0008, all Proposed | Proposed |
| `SE-04` Development plan | #14 (commit `c2d9f86`); branch | [`docs/development-plan.md`](development-plan.md) | Draft; owners proposed |
| `SE-05` Traceability | Branch | This document | Updated |
| `SE-06` Provider isolation (see `NFR-07`) | #14 | [Interfaces draft](api/interfaces.md) | Specified |
| `SE-07` User and API docs (see `NFR-11`) | Branch | [API docs](api/README.md) | Partly done |
| `SB-01` Wikilinks and requirement links | Branch | `scripts/validate_brain.py`; ADR 0003 | Enforced in CI |
| `SB-02` Stage review notes | #14 (commit `a1dae74`); branch | [Stage 1 review](stage-reviews/stage-1-review.md) | Incomplete (Persons 2 and 3 sections pending) |
| `SB-03` ADRs and skills cite Brain notes | Branch | `scripts/validate_docs.py` (ADRs), `scripts/validate_skills.py` (skills) | Enforced in CI |
| `SB-04` `AGENTS.md` at root | #10 | [`AGENTS.md`](../AGENTS.md) | Done |
| `SB-05` Brain changes through PRs | #12, #15, #17 | Merge history; this branch awaits a PR | Ongoing |
| `SB-06` Every member authors notes | #12, #15, #17 | Note `author` fields (counted 2026-11-08): Person 1 on 5 notes, Person 2 on 4, Person 3 on 4 (the merged API note credits Persons 1 and 2), plus 2 notes by Git user `ChadDadChag`. Git evidence links identity `Vicky` to Person 3 (`a5caa34`) and the committer of `8e80f55` to Person 2's notes; no complete account-to-Person mapping is recorded | Met by note authorship; account mapping partly verifiable |
| `AIP-01` Human review of AI changes | — | This branch awaits review | Pending |
| `AIP-02` Members can explain merged work | — | Not verifiable from the repository | Unverifiable |
| `AIP-03` AI-session notes | #15; branch | [2026-11-07](../brain/projects/ai-session-2026-11-07-srs-drafting.md), [2026-11-08](../brain/projects/ai-session-2026-11-08-stage-1-audit.md), [CI Pipeline](../brain/projects/CI-Pipeline.md) | Done for known sessions |
| `AIP-04` No secrets in AI tools | — | Stated in AI-session notes | Self-reported |

## Maintenance

Update a row when its issue, PR, test, skill evaluation or Brain note actually exists. Person 1
maintains this matrix (`docs/development-plan.md`). `scripts/validate_docs.py` checks that
every ID used here is defined in the SRS and that every link resolves.
