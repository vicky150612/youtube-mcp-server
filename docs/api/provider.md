# Provider integration and live demonstration

The feature services depend on `YouTubeProvider` in `providers/base.py`.
Use fixture mode for tests and `build_live()` for the live composition.
Provider errors carry `code`, `message` and `next_action`.

| Operation | Quota cost |
| --- | --- |
| Video or channel metadata | One general unit per batch of at most 50 IDs |
| Resolve channel | Zero for normalized ID, one general unit for lookup |
| Recent uploads | Up to three general units for up to 50 uploads |
| Categories | One general unit |
| Search | One separate search call per page |
| Library | One general unit per API page or metadata batch |
| Account fingerprint | One general unit |
| Verify write account | Two general units for the channel comparison |
| Playlist or item insertion | 50 general units for each write |

Wrap each MCP tool invocation in `with quota.tool_scope():` to enforce
the shared two-page search cap. Before calling the provider, services
must use `quota.cost_of` and `quota.check` for the full known worst-case
workflow cost, including cache misses. Include the playlist insert and
all item inserts before elicitation. A preflight is a check. The actual
reservation is per dispatch and allows concurrent local workflows to
share the ledger. Unknown library pagination is checked per page and
budget exhaustion returns an error without a partial snapshot.

The playlist service owns proposal validation, owner and lifecycle checks,
explicit elicitation, replay protection, and partial failure reporting.
Prepare the write scope and verify the proposal owner before confirmation.
Call provider mutations only after confirmed acceptance.

## Live demo

Enable YouTube Data API v3, configure an OAuth test user, and download
two Desktop clients. Set these environment variables locally.

| Variable | Purpose |
| --- | --- |
| `YOUTUBE_QUOTA_PROJECT` | Google Cloud project ID used to namespace the local ledger |
| `YOUTUBE_API_KEY` | API key restricted to YouTube Data API v3 |
| `YOUTUBE_READ_CLIENT_FILE` | Path to read Desktop client JSON outside the repo |
| `YOUTUBE_WRITE_CLIENT_FILE` | Path to separate write Desktop client JSON outside the repo |
| `YOUTUBE_TOKEN_STORE` | Optional `protected-file` on POSIX |

Run `python -m youtube_mcp.server --authorise` for read consent. Connect an
MCP stdio client to `python -m youtube_mcp.server`. Invoke `auth_status`,
`get_quota_status`, and `get_video_details` with a known public ID or watch/Shorts URL. Repeat the metadata call and compare quota status to show the cache.
Use `python -m youtube_mcp.server --sign-out` after the demo. If Testing mode
invalidates the refresh grant, run the authorization command again.

API-key public reads use the TTL cache. When no key is configured, public
reads may use read-only OAuth and bypass the cache to keep authorised
metadata out of shared entries. One retry is allowed for a rate-limited
read if quota is available. Writes are not retried.

The weekly workflow takes an API key from the repository secret
`YOUTUBE_LIVE_SMOKE_API_KEY`. It caps combined quota at 200 units and search
at two calls. Its provider is read-only and upload quota is zero.
