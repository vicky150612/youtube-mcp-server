# Architecture overview

**Status:** Logical architecture only. Provider contracts, OAuth scopes/storage,
algorithms, quota implementation, and runtime technology remain undecided.

The design follows the approved boundary: the MCP adapter routes requests to focused
services; services use an isolated YouTube provider; provider work must pass quota
pre-checks. The YouTube Data API v3 is the only YouTube data/operation source. No
related-video, related-channel, or watch-history endpoint is assumed.

## Components and interactions

```mermaid
flowchart LR
    User[Authorised user] --> Client[MCP-compatible AI client]
    Client -->|tool requests| Server[MCP server and request adapter]
    Skills[Agent Skills] -->|guide user-approved workflows| Client
    Server --> Video[Video similarity service]
    Server --> Channel[Channel similarity service]
    Server --> Recommendations[Recommendations service]
    Server --> Engagement[Engagement analysis service]
    Server --> Playlist[Playlist planning and creation service]
    Video -->|estimate before API access| Quota[Quota management]
    Channel -->|estimate before API access| Quota
    Recommendations -->|estimate before API access| Quota
    Engagement -->|estimate before API access| Quota
    Playlist -->|estimate before API access| Quota
    Quota -->|reject if budget is insufficient| Server
    Video -->|only after quota approval| Provider[YouTube provider interface]
    Channel -->|only after quota approval| Provider
    Recommendations -->|only after quota approval| Provider
    Engagement -->|only after quota approval| Provider
    Playlist -->|only after quota approval| Provider
    Playlist -->|show proposal; await explicit confirmation| Client
    Provider --> Auth[OAuth authentication and credential handling]
    Provider -->|official API calls only| API[YouTube Data API v3]
    API -->|available metadata and user library data| Provider
    Provider -->|provider-neutral results| Video
    Provider -->|provider-neutral results| Channel
    Provider -->|provider-neutral results| Recommendations
    Provider -->|provider-neutral results| Engagement
    Provider -->|create only after confirmation| Playlist
```

The diagram shows responsibilities and required boundaries, not finalized class names or
method signatures. Candidate discovery, supported languages, summary input, cache policy,
and provider/service contracts remain open. The quota values and method-specific examples
are owned by the [SRS quota requirements and appendix](../srs.md#appendix-a--reference-youtube-api-quota-verified-2026-11-07-against-googles-pages);
verify them against Google's current quota documentation and the project's Quotas page
before implementation.

## Module responsibilities

| Module | Responsibility and constraints |
|---|---|
| MCP server | Register tools/resources and adapt protocol requests/responses; do not contain provider-specific API calls or core ranking logic. |
| YouTube provider | Isolate official YouTube Data API v3 operations behind a provider interface. Keep provider results separate from MCP response adaptation. |
| Authentication | Obtain and handle authorised credentials for the operation with least-privilege OAuth scopes; store tokens securely outside the repository/logs, refresh valid access tokens, detect expired/revoked credentials, and provide clear re-authorisation. Google's Testing-mode refresh tokens expire after seven days. Exact scopes and storage are open. |
| Quota management | Estimate each planned provider operation from its current documented method cost; track general units and every applicable method-specific bucket separately. Include list-page calls and playlist writes. Check the complete workflow before the first API call and reject if any applicable remaining budget is insufficient. Never assume a uniform cost or fall back to an unknown/optimistic cost. The estimator, counter, and cache design are open. |
| Metadata retrieval | Retrieve and normalize video/channel candidates and their available metadata through the provider. It does not rank candidates. Search calls and list-page calls count against their applicable quota budgets. |
| Video similarity | Consume normalized metadata and calculate rankings separately from API retrieval. Weighted feature scores or TF-IDF with cosine similarity are suitable explainable candidates; feature selection, candidate discovery, weights, and final method remain open. |
| Channel similarity | Consume normalized channel metadata and calculate rankings separately from API retrieval. Weighted metadata scoring or TF-IDF/cosine similarity over text features are candidate approaches; the final method and candidate discovery remain open. |
| Recommendations | Use the authorised user's liked videos, subscriptions, and playlists; never infer or claim watch-history access. |
| Engagement analysis | Compute the required channel/category, time, duration, and period comparisons from the supported library sources. Exact metric definitions are open. |
| Playlist planning and creation | Validate topic, total duration, maximum video length, and language constraints; show the proposal and require explicit user confirmation before a write; handle accounts without a channel. Matching/tolerance behavior is open. |
| Agent Skills | Guide workflows through the MCP-compatible client and tools. Skill instructions or tool output are not user confirmation. Skill implementations remain pending. |
| Video summary input | Open for SK-05: consider available video metadata, a transcript explicitly supplied by the user, or another team-approved compliant input. Do not scrape video pages or assume unofficial transcript APIs. Do not implement a summary source until OD-04 is decided. |

For CI and validator implementation evidence, see the existing Brain note [[CI Pipeline]].

## Request boundaries

- Every service workflow that needs YouTube data checks its estimated quota before calling
  the provider. Insufficient budget means no API request.
- Similarity uses project-computed metadata ranking, not an undocumented related-content
  endpoint.
- The provider retrieves/normalizes metadata; similarity services score that data without
  making provider calls. Metadata retrieval and ranking are separate responsibilities.
- Quota estimates use operation-specific costs and all applicable quota buckets; pagination
  and writes are included. Reject the whole workflow before making any API call if a bucket
  would be exceeded.
- Personalisation and analysis use only liked videos, subscriptions, and playlists.
- A playlist write is gated by explicit user confirmation of the displayed proposal.
- Titles, descriptions, tags, and other external metadata remain untrusted input.
- Ordinary CI uses mocks or recorded fixtures. Any future live API tests are separate,
  opt-in/scheduled, and quota-limited.

## Pending interfaces

No application language, framework, MCP SDK, provider method signatures, data-model
contracts, OAuth storage mechanism, or service API has been approved. Define and review
those contracts before implementation rather than inferring them from this diagram.
