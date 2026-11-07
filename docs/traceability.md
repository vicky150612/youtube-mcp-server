# Requirement traceability

**Status:** Initial inventory; product implementation and product tests remain pending.
**Requirement source:** [`docs/srs.md`](srs.md) and [`AGENTS.md`](../AGENTS.md).

Issue and PR references below are real documentation work, not evidence that the related
product requirement is implemented. `#14` added the SRS; `#15` added Person 1's API research
notes; `#16` tracks this Part 7 documentation task. PR for #16 is pending. Do not treat
validator tests as product behavior tests.

| Requirement | GitHub issue | PR | Test evidence | Skill | Brain note |
|---|---|---|---|---|---|
| FR-01 Similar videos | Pending: implementation issue | #14 (SRS only) | Pending: product ranking tests | Pending | [[YouTube Video Resource]], [[YouTube Data API Overview]] |
| FR-02 Similar channels | Pending: implementation issue | #14 (SRS only) | Pending: product ranking tests | Pending | [[YouTube Channel Resource]], [[YouTube Data API Overview]] |
| FR-03 Recommendations | Pending: implementation issue | #14 (SRS only) | Pending: recommendation tests | Pending | [[YouTube Data API Overview]], [[YouTube Playlist Resource]] |
| FR-04 Engagement analysis | Pending: implementation issue | #14 (SRS only) | Pending: analysis tests | Pending | [[YouTube Video Resource]], [[YouTube Playlist Resource]] |
| FR-05 Playlist creation | Pending: implementation issue | #14 (SRS only) | Pending: constraints, confirmation, and creation tests | `video-to-playlist` planned; implementation/evaluation pending | [[YouTube Playlist Resource]], [[YouTube Video Resource]] |
| NFR-01 Official API only | Pending: implementation issue | #14 (SRS only) | Pending: provider/API compliance tests | N/A | [[YouTube Data API Overview]] |
| NFR-02 Quota and caching | #16 (documentation only) | #14 (SRS); #16 PR pending | Pending: operation-cost, cache, and pre-check product tests | N/A | [[YouTube Data API Overview]], [[YouTube Playlist Resource]] |
| NFR-03 OAuth and re-authorisation | #16 (documentation only) | #14 (SRS); #16 PR pending | Pending: scope, storage, refresh, expiry, and re-authorisation tests | N/A | Pending: OAuth research note |
| NFR-04 Validation and untrusted metadata | #16 (documentation only) | #14 (SRS); #16 PR pending | Pending: validation and prompt-injection tests | `video-to-playlist` planned | [[YouTube Video Resource]] |
| NFR-05 Secrets and personal data | Pending: implementation issue | #14 (SRS only) | Pending: security/privacy product tests | N/A | [[CI Pipeline]] |
| NFR-06 Errors and capability reporting | #16 (documentation only) | #14 (SRS); #16 PR pending | Pending: negative tests, including no-channel account | N/A | [[YouTube Playlist Resource]], [[YouTube Channel Resource]] |
| NFR-07 Provider/service boundaries | Pending: implementation issue | #14 (SRS only) | Pending: provider integration tests | N/A | [[MCP-Architecture]], [[YouTube Data API Overview]] |
| NFR-08 Deterministic CI/live-test separation | #16 (documentation only) | #16 PR pending | Repository CI exists; product coverage and capped live workflow pending | `local-check` planned; implementation pending | [[CI Pipeline]] |
| NFR-09 MCP compatibility | Pending: implementation issue | #14 (SRS only) | Pending: MCP contract and system tests | N/A | [[MCP-Architecture]], [[MCP-Tools-and-Resources]] |
| NFR-10 Deterministic computation | Pending: implementation issue | #14 (SRS only) | Pending: repeatability tests for similarity and analytics | N/A | Pending: metadata similarity research note |
| NFR-11 Documentation | #16 (documentation only) | #14 (SRS); #16 PR pending | Architecture and developer workflow docs exist; product API reference pending implementation | N/A | [[MCP-Architecture]] |
| TQ-01 Unit tests | Pending: product tests | #14 (test requirement only) | Validator unit tests exist; product unit tests pending | N/A | [[CI Pipeline]] |
| TQ-02 Integration tests | Pending | Pending | Pending: provider/service integration tests | N/A | Pending |
| TQ-03 MCP system tests | Pending | Pending | Pending: FR-01 through FR-05 system tests | N/A | Pending |
| TQ-04 Negative tests | #16 (scenarios documented) | #16 PR pending | Validator negatives exist; product quota/OAuth/confirmation/channel-less tests pending | N/A | [[CI Pipeline]], [[YouTube Playlist Resource]] |
| TQ-05 CI/live-test separation | #16 (scenarios documented) | #16 PR pending | CI is fixture/local-only; capped live-test workflow pending | N/A | [[CI Pipeline]], [[YouTube Data API Overview]] |
| TQ-06 Quota pre-check | #16 (scenarios documented) | #16 PR pending | Pending: reject before any API call for each applicable bucket | N/A | [[YouTube Data API Overview]], [[YouTube Playlist Resource]] |
| TQ-07 Skill evaluations | Pending | Pending | Pending; evaluate each skill before stage submission | All planned skills | Pending |
| TQ-08 Regression tests | Pending | Pending | Validator regressions exist; product regression coverage pending | N/A | [[CI Pipeline]] |
| SK-01 `brain-ingest` | Pending | Pending | Pending: skill evaluation | `brain-ingest` implementation/evaluation not verified here | Pending |
| SK-02 `brain-refine` | Pending | Pending | Pending: skill evaluation | `brain-refine` planned; implementation/evaluation pending | Pending |
| SK-03 `brain-query` | Pending | Pending | Pending: skill evaluation | `brain-query` planned; implementation/evaluation pending | Pending |
| SK-04 `local-check` | Pending | Pending | Pending: skill evaluation | `local-check` planned; implementation/evaluation pending | [[CI Pipeline]] |
| SK-05 `video-to-playlist` | Pending | Pending | Pending: skill evaluation | `video-to-playlist` planned; implementation/evaluation pending | Pending |

## Status and maintenance

- The Stage 1 baseline is outside this repository; see
  [`docs/research/allocation.md`](research/allocation.md) for the documented assignment.
- GitHub issue #16 is the current documentation issue. Existing issues/PRs that concern
  repository setup are not presented as product implementation evidence.
- Person 1's API research notes were merged in #15. OAuth and quota-management notes
  assigned to another member remain pending.
- Add implementation issue, PR, product test, skill-evaluation, and Brain-note references
  only when their evidence exists.
