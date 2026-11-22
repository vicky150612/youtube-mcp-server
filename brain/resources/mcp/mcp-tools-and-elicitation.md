---
title: MCP tools and elicitation
created: 2026-11-22
source:
  - "YT-MCP-SRS.pdf v1.0, §§2.4, 3.3, 5.2"
  - "MCP Server Tools, revision 2025-11-25"
  - "MCP Client Elicitation, revision 2025-11-25"
requirements:
  - FR-01
  - FR-02
  - FR-03
  - FR-04
  - FR-05
  - NFR-04.3
issues:
  - 8
  - 15
---

# Summary

MCP defines tool discovery, invocation, and result transport. YouTube MCP adds
an application-level response contract and uses elicitation for user-mediated
playlist confirmation.

# Key findings

## Source-grounded findings

- The MCP server advertises tools, clients discover them with `tools/list`, and
  invoke them with `tools/call`. Tool definitions include a name, description,
  and JSON Schema input; an output schema is optional.
- MCP results use protocol fields such as `content`, optional
  `structuredContent`, and `isError`. The architecture plan separately defines
  the YouTube MCP payload envelope (`ok`, `data`, `summary` on success).
- MCP elicitation supports structured form input and out-of-band URL
  interaction. Clients must support the mode they advertise and provide
  review/decline controls. Form mode must not collect passwords, tokens, or
  other sensitive credentials.
- The SRS specifies local stdio transport and an MCP protocol revision of
  `2026-07-28`. The official pages cited here are for revision `2025-11-25`;
  confirm the required revision and SDK behavior before implementation.

## Interpretation for YouTube MCP

Keep the MCP protocol result separate from the application's JSON envelope;
serialize the latter within the tool result according to the agreed contract.
Use elicitation for the user's explicit acceptance of a specific playlist
proposal, never as a route to collect OAuth credentials.

# Relevance to YouTube MCP

This note supports the MCP server skeleton and service-tool integration tracked
by [issue #8](https://github.com/vicky150612/youtube-mcp-server/issues/8) and
[issue #15](https://github.com/vicky150612/youtube-mcp-server/issues/15).
It also informs all five feature tools and the playlist write-confirmation
path.

# Decisions or implications

- Keep tool schemas and descriptions in the MCP layer, with service execution
  and provider access behind the boundaries in the architecture plan.
- Treat clients without the elicitation capability as unable to confirm
  playlist writes; fail closed as required by the SRS.
- Reconcile the SRS protocol revision with the chosen MCP SDK before freezing
  implementation details.

# Related notes

- [[brain/projects/youtube-mcp/playlist-confirmation-safety|Playlist confirmation safety]]
- [[brain/resources/agent-skills/agent-skills-format|Agent Skills format]]
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and interface plan]]

# Open questions

- Which MCP SDK revision will implement protocol revision `2026-07-28`?
- Which client/runtime combinations will be used to verify elicitation behavior?

## Sources

- [MCP Server Tools, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [MCP Client Elicitation, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)
- `YT-MCP-SRS.pdf` v1.0, §§2.4, 3.3, 5.2; locally supplied and ignored by Git.
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and Interface Plan]], §4.
- Related pull request: [#20](https://github.com/vicky150612/youtube-mcp-server/pull/20).
