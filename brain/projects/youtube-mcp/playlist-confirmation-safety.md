---
title: Playlist confirmation safety
created: 2026-11-22
source:
  - "YT-MCP-SRS.pdf v1.0, FR-05, §§5.2–5.3"
  - "Architecture and Interface Plan, §§1, 3"
requirements:
  - FR-05
  - NFR-04.2
  - NFR-04.3
  - BR-05
issues:
  - 13
  - 14
---

# Summary

Playlist generation is a proposal workflow. Writes are permitted only after
quota checks, authorization, and explicit user acceptance of the exact
proposal; missing, declined, or invalid confirmation must fail closed.

# Key findings

## Source-grounded findings

- The architecture plan models proposal contents as immutable and lifecycle
  state separately. The proposal has an owner, canonical SHA-256 digest,
  random ID, and a 15-minute expiry. A newer proposal can supersede an earlier
  open proposal for the same owner.
- Before writing, the service rejects unknown, expired, changed, foreign,
  cancelled, superseded, or consumed proposals and verifies the digest.
- Creation order is significant: pre-check the full write quota, ensure the
  write OAuth scope, request elicitation for that proposal, then begin writes.
  If confirmation is declined or unsupported, do not write and offer the
  documented manual-export next action.
- The SRS requires untrusted metadata not to trigger privileged actions and
  requires the confirmation to be bound to the exact stored proposal.

## Interpretation for YouTube MCP

Treat titles, descriptions, tags, and other candidate metadata as data, not
instructions. Recheck proposal identity and digest at the write boundary;
confirmation of one proposal must never authorize a modified or replacement
proposal.

# Relevance to YouTube MCP

This note supports proposal generation in
[issue #13](https://github.com/vicky150612/youtube-mcp-server/issues/13) and
confirmation/creation safety in
[issue #14](https://github.com/vicky150612/youtube-mcp-server/issues/14).
It connects the FR-05 write flow to the quota and elicitation contracts.

# Decisions or implications

- Keep quota pre-check and write-scope acquisition before elicitation and
  before any provider write.
- Make unsupported or declined elicitation a no-write outcome.
- Preserve proposal immutability and lifecycle transitions so replay,
  cancellation, expiry, and supersession can be tested explicitly.
- Report partial creation accurately; do not disguise partial failure as
  success.

# Related notes

- [[brain/resources/mcp/mcp-tools-and-elicitation|MCP tools and elicitation]]
- [[brain/projects/youtube-mcp/overview|Project overview]]
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and interface plan]]

# Open questions

- What storage implementation will retain proposal lifecycle state safely
  across server restarts?
- Which concurrency tests will prove that repeated confirmation cannot start
  duplicate writes?

## Sources

- `YT-MCP-SRS.pdf` v1.0, FR-05 and §§5.2–5.3; locally supplied and ignored by Git.
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and Interface Plan]], proposal models and playlist creation order.
- Related pull request: [#20](https://github.com/vicky150612/youtube-mcp-server/pull/20).
