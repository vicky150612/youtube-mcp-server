# Software Requirements Specification

**Status:** Draft baseline; team approval is pending.
**Basis:** Fixed project requirements in [`AGENTS.md`](../AGENTS.md) and the Stage 1
baseline. Implementation and design choices marked open below are not requirements.

The Stage 1 baseline writes the functional IDs as `FR-1` through `FR-5`; this repository
uses the zero-padded canonical IDs `FR-01` through `FR-05` from `AGENTS.md`. They refer to
the same five requirements.

## Functional requirements

| ID    | Requirement                                                                                                                                                                                                                                                                 |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-01 | Given a YouTube video URL or ID, return a ranked list of similar videos. Similarity must be computed from available metadata; the YouTube API has no related-videos endpoint.                                                                                               |
| FR-02 | Given a channel URL, handle, or ID, return a ranked list of similar channels. Similarity must be computed from available metadata; the YouTube API has no related-channels endpoint.                                                                                        |
| FR-03 | Recommend videos using the authorised user's liked videos, subscriptions, and playlists. Watch history is not available through the YouTube Data API and is not an input.                                                                                                   |
| FR-04 | Analyse the user's liked videos, subscriptions, and playlists, including top channels and categories, trends over time, duration preferences, and comparisons between periods.                                                                                              |
| FR-05 | Interpret playlist constraints (including topic, total duration, maximum individual video length, and language), show a proposed playlist, and create it in the authorised user's account only after explicit user confirmation. Handle accounts without a YouTube channel. |

## Non-functional requirements

These IDs organize the fixed constraints in `AGENTS.md`; they do not settle the open
implementation choices.

| ID     | Requirement                                                                                                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-01 | Use only the official YouTube Data API v3. Do not scrape YouTube, use unofficial APIs, or claim unsupported API capabilities.                                                                                       |
| NFR-02 | Account for quota per request/workflow, reject work that exceeds the remaining budget before any API call, respect the stated 10,000-unit daily default, and use caching/fixtures to limit unnecessary calls.       |
| NFR-03 | Use OAuth with minimum necessary scopes, store credentials safely, and clearly support re-authorisation for expired or revoked credentials (including seven-day Testing-mode refresh-token expiry).                 |
| NFR-04 | Validate external inputs and tool parameters. Treat titles, descriptions, tags, and other metadata as untrusted; they must not override instructions or cause playlist creation without explicit user confirmation. |
| NFR-05 | Never commit credentials or real user personal data. Redact sensitive diagnostic data and use synthetic/recorded fixtures.                                                                                          |
| NFR-06 | Handle malformed IDs, private/deleted videos, missing tags, quota errors, missing YouTube channels, expired tokens, and rate limiting explicitly; report unavailable data rather than fabricating results.          |
| NFR-07 | Isolate YouTube API access behind a provider interface. Keep MCP adaptation separate from focused business services and use consistent, explicit data contracts.                                                    |
| NFR-08 | Keep ordinary CI deterministic and independent of live YouTube and personal accounts. Run opt-in/scheduled live API tests separately under a fixed quota budget.                                                    |

## Test-quality requirements

| ID    | Requirement                                                                                                                             |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------- |
| TQ-01 | Unit-test functions, services, and MCP tools, including similarity scoring, duration parsing, and playlist-constraint logic.            |
| TQ-02 | Test component interactions, including the YouTube provider.                                                                            |
| TQ-03 | Test FR-01 through FR-05 end-to-end through the MCP interface.                                                                          |
| TQ-04 | Cover malformed IDs, private/deleted videos, missing tags, `quotaExceeded`, `youtubeSignupRequired`, expired tokens, and rate limiting. |
| TQ-05 | Use fixtures or mocks in CI; keep live API tests separate, opt-in/scheduled, and within a fixed quota budget.                           |
| TQ-06 | Prove that over-budget work is rejected before any API call.                                                                            |
| TQ-07 | Evaluate skills before stage submissions and record the results.                                                                        |
| TQ-08 | Add regression tests for significant defects; do not skip or weaken failing tests to pass CI.                                           |

Additional security tests must cover OAuth scopes/storage, secrets, input validation, prompt
injection, and personal-data handling.

## Skill requirements

| ID    | Skill               | Required outcome                                                                                                                                                                                    |
| ----- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SK-01 | `brain-ingest`      | Add source-grounded material and summaries to the Second Brain. Stage 1 requires using it to add at least ten research notes.                                                                       |
| SK-02 | `brain-refine`      | Organise notes into PARA, merge duplicates, and repair links.                                                                                                                                       |
| SK-03 | `brain-query`       | Query the Brain and draft material such as SRS and ADRs from its sources.                                                                                                                           |
| SK-04 | `local-check`       | Build and test the project, start the local server, invoke one read-only fetch endpoint, and report each result.                                                                                    |
| SK-05 | `video-to-playlist` | Summarise a video, find similar videos, propose a playlist, obtain explicit confirmation before creation, and show a short analysis. Do not use scraping or assume an unofficial transcript source. |

The Stage 1 baseline states the first four skills' stage expectations. Listing a skill here
does not claim it exists, has been implemented, or has been evaluated.

## Open decisions and approval

The programming language/framework/MCP SDK, OAuth scopes and token storage, similarity
features and ranking, summary input, playlist selection/tolerance, language support, quota
estimation/cache policy, and Brain schema/link conventions remain open. Record decisions
only after the team makes them. Confirm this draft against the approved project statement
and SDLC requirements before treating it as approved.
