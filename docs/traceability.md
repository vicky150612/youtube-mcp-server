# Requirement traceability

**Status:** Initial inventory; links not evidenced in GitHub remain pending.
**Requirement source:** [`docs/srs.md`](srs.md) and [`AGENTS.md`](../AGENTS.md).

`Pending` means no verified issue, PR, product test, implementation skill, or matching
research note is recorded yet. Do not replace it with an assumed identifier or a future
test. The CI tooling tests do not demonstrate product FR/NFR behaviour.

| Requirement                                  | GitHub issue | PR      | Test evidence                                                                  | Skill                                                          | Brain note                                             |
| -------------------------------------------- | ------------ | ------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------- | ------------------------------------------------------ |
| FR-01 Similar videos                         | Pending      | Pending | Pending: product ranking tests                                                 | Pending                                                        | Pending: allocated research note not found             |
| FR-02 Similar channels                       | Pending      | Pending | Pending: product ranking tests                                                 | Pending                                                        | Pending: allocated research note not found             |
| FR-03 Recommendations                        | Pending      | Pending | Pending: recommendation tests                                                  | Pending                                                        | Pending: allocated research note not found             |
| FR-04 Engagement analysis                    | Pending      | Pending | Pending: analysis tests                                                        | Pending                                                        | Pending: allocated research note not found             |
| FR-05 Playlist creation                      | Pending      | Pending | Pending: constraint, confirmation, and creation tests                          | `video-to-playlist` planned; implementation/evaluation pending | Pending: allocated research note not found             |
| NFR-01 Official API only                     | Pending      | Pending | Pending: provider/API compliance tests                                         | N/A                                                            | Pending: allocated YouTube API research note not found |
| NFR-02 Quota and caching                     | Pending      | Pending | Pending: quota pre-check tests                                                 | N/A                                                            | Pending: allocated quota research note not found       |
| NFR-03 OAuth and re-authorisation            | Pending      | Pending | Pending: OAuth scope/storage/expiry tests                                      | N/A                                                            | Pending: allocated OAuth research note not found       |
| NFR-04 Validation and untrusted metadata     | Pending      | Pending | Pending: validation and prompt-injection tests                                 | `video-to-playlist` planned                                    | Pending                                                |
| NFR-05 Secrets and personal data             | Pending      | Pending | Pending: security/privacy tests                                                | N/A                                                            | Pending                                                |
| NFR-06 Errors and capability reporting       | Pending      | Pending | Pending: negative tests                                                        | N/A                                                            | Pending                                                |
| NFR-07 Provider/service boundaries           | Pending      | Pending | Pending: provider integration tests                                            | N/A                                                            | Pending: allocated MCP architecture note not found     |
| NFR-08 Deterministic CI/live-test separation | Pending      | Pending | CI workflow and validator tests exist; product test separation remains pending | `local-check` planned; implementation pending                  | [[CI Pipeline]]                                        |
| TQ-01 Unit tests                             | Pending      | Pending | CI validator unit tests exist; product unit tests pending                      | N/A                                                            | [[CI Pipeline]]                                        |
| TQ-02 Integration tests                      | Pending      | Pending | Pending                                                                        | N/A                                                            | Pending                                                |
| TQ-03 MCP system tests                       | Pending      | Pending | Pending                                                                        | N/A                                                            | Pending                                                |
| TQ-04 Negative tests                         | Pending      | Pending | CI validator negatives exist; listed product negatives pending                 | N/A                                                            | [[CI Pipeline]]                                        |
| TQ-05 CI/live-test separation                | Pending      | Pending | Workflow is fixture/local-only; live test workflow and quota budget pending    | N/A                                                            | [[CI Pipeline]]                                        |
| TQ-06 Quota pre-check                        | Pending      | Pending | Pending                                                                        | N/A                                                            | Pending                                                |
| TQ-07 Skill evaluations                      | Pending      | Pending | Pending; no product skills currently exist                                     | All planned skills                                             | Pending                                                |
| TQ-08 Regression tests                       | Pending      | Pending | CI validator regressions exist; product regression coverage pending            | N/A                                                            | [[CI Pipeline]]                                        |
| SK-01 `brain-ingest`                         | Pending      | Pending | Pending: skill evaluation                                                      | `brain-ingest` planned; implementation/evaluation pending      | Pending                                                |
| SK-02 `brain-refine`                         | Pending      | Pending | Pending: skill evaluation                                                      | `brain-refine` planned; implementation/evaluation pending      | Pending                                                |
| SK-03 `brain-query`                          | Pending      | Pending | Pending: skill evaluation                                                      | `brain-query` planned; implementation/evaluation pending       | Pending                                                |
| SK-04 `local-check`                          | Pending      | Pending | Pending: skill evaluation                                                      | `local-check` planned; implementation/evaluation pending       | [[CI Pipeline]]                                        |
| SK-05 `video-to-playlist`                    | Pending      | Pending | Pending: skill evaluation                                                      | `video-to-playlist` planned; implementation/evaluation pending | Pending                                                |

## Status and maintenance

- The Stage 1 baseline is outside this repository; it documents the initial requirement
  and ownership allocation. See [`docs/research/allocation.md`](research/allocation.md).
- GitHub currently contains issue #8 (“Initialize repository structure”) and merged PRs #9
  and #10 for repository setup and `AGENTS.md`. They are not mapped above because the
  available titles do not establish that they implement a specific product requirement.
- Add verified issue, PR, test, skill-evaluation, and Brain-note references as work is
  completed. Keep pending items pending until evidence exists.
