# API and developer documentation

The YouTube provider must use only the official YouTube Data API v3 and remain behind a provider
interface (`NFR-07`). Supported operations, required scopes, data contracts, quota cost
assumptions and error mapping are documented together; YouTube offers no related-video,
related-channel or watch-history endpoint, and none is assumed.

- [Shared interface contracts](interfaces.md) — **draft, not frozen** (`OD-17`): `Video`,
  `Channel`, `PlaylistConstraints`, `UserLibrarySnapshot`, `PlaylistProposal`, `YouTubeProvider`
  operations, typed errors and authentication assumptions.
- The developer API reference for MCP tools (`NFR-11`) will be written when the tools exist; no
  application stack or MCP SDK has been approved yet (`OD-01`).

See the [logical architecture](../architecture/overview.md) for module boundaries.
