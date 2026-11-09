---
title: YouTube Data API Errors
type: research
author:
  - Person 2
created: 2026-11-08
tags:
  - research
  - youtube-mcp
  - youtube-api
  - errors
sources:
  - "https://developers.google.com/youtube/v3/docs/errors"
  - "https://developers.google.com/youtube/v3/docs/playlistItems/list"
  - "https://developers.google.com/youtube/v3/docs/playlistItems/insert"
  - "https://developers.google.com/youtube/v3/docs/playlists/insert"
  - "https://developers.google.com/youtube/data/reference/rest/v3/channels/list"
status: ingested
---

# YouTube Data API Errors

## Overview

The YouTube Data API returns errors as an HTTP status plus an error "reason" (detail). Google's
errors reference lists general errors first and then per-resource, per-method errors. The
project needs this catalogue to map API failures to typed, user-readable errors (`NFR-06.2`) and
to write the negative tests required by `TQ-04`.

## Key Concepts

- **Error type and detail:** each entry has an HTTP status family (for example
  `forbidden (403)`) and a detail string (for example `quotaExceeded`) that identifies the
  specific failure.
- **General errors:** three tables — "Core API errors", "Common request errors" and "Request
  context errors" — apply to all methods.
- **Per-method errors:** every resource section has one table per method; each method can also
  return the common request errors.

## Important Findings

- **Core API errors** contain exactly two entries: `forbidden (403)` — "Access forbidden. The
  request may not be properly authorized." — and `quotaExceeded (403)` — "The request cannot be
  completed because you have exceeded your quota."
- **`youtubeSignupRequired` (401):** the user has a Google Account that is not linked to a
  YouTube channel; such users can use some authorised features but not all. The page notes it is
  commonly seen with the OAuth service-account flow because YouTube does not support service
  accounts.
- **`authorizationRequired` (401):** the request uses the `mine` parameter but is not properly
  authorised.
- **`insufficientPermissions` (403)** (common request errors): the OAuth token's scopes are not
  sufficient for the requested data.
- **Rate limiting:** `rateLimitExceeded (400)` is listed only for `videos.reportAbuse`. No global
  rate-limit error (for example `userRateLimitExceeded`) and no HTTP 429 entry appears on the
  page (checked 2026-11-08). The page also does not describe the JSON error body.
- **Errors relevant to our methods:**
  - `channels.list`: `channelNotFound (404)` for the `id` filter; more than one filter gives
    `badRequest (400)` / `invalidCriteria`.
  - `playlistItems.list`: `playlistNotFound (404)`, `playlistItemsNotAccessible (403)`,
    `watchLaterNotAccessible`, `watchHistoryNotAccessible` ("Watch history data cannot be
    retrieved through the API"), `playlistOperationUnsupported (400)`.
  - `playlists.insert`: `maxPlaylistExceeded (400)`, `playlistForbidden (403)`,
    `invalidPlaylistSnippet (400)`, `playlistTitleRequired (400)`.
  - `playlistItems.insert`: `playlistContainsMaximumNumberOfVideos (403)`, `videoNotFound (404)`,
    `playlistItemsNotAccessible (403)`, `playlistNotFound (404)`; no duplicate-item error is
    documented.

## Relevance to Our Project

> The points below are the project's interpretation of the sources, not statements from Google.

- The provider should map the detail strings above to the typed errors in the interface
  contract (`docs/api/interfaces.md`), for example `youtubeSignupRequired` →
  `channel_required`, `quotaExceeded` → `quota_exhausted` (and mark the bucket exhausted,
  ADR 0006), `authorizationRequired`/`insufficientPermissions` → `authorization_required`,
  `*NotFound` → `not_found`.
- Because rate limiting is not documented as a global error, treat HTTP 429 and any
  `rateLimitExceeded`/`userRateLimitExceeded` reason as retryable with bounded exponential
  backoff, and verify the actual behaviour in a capped live test. Retries still cost quota.
- `watchHistoryNotAccessible` confirms that no feature may depend on watch history.
- Each listed error is a candidate negative test (`TQ-04`) with a recorded fixture.

## Related Requirements

`NFR-06.1`, `NFR-06.2`, `NFR-03.3`, `NFR-02.2`, `TQ-04`, `FR-05`. Requirement source:
[SRS](../../docs/srs.md).

## Sources

- **YouTube Data API — Errors** — Google for Developers.
  https://developers.google.com/youtube/v3/docs/errors (accessed 2026-11-08; no update date
  shown in the fetched content).
- **playlistItems.list**, **playlistItems.insert**, **playlists.insert** — YouTube Data API
  reference pages (accessed 2026-11-08).
- **channels.list** — https://developers.google.com/youtube/data/reference/rest/v3/channels/list
  (accessed 2026-11-08).

## Related Notes

- [[YouTube-API-Quota-Management|YouTube API Quota Management]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[OAuth-Authentication|OAuth 2.0 Authentication]]
- [[YouTube-Data-API|YouTube Data API]]
