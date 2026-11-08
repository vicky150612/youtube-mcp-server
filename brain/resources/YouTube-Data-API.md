---
title: "YouTube Data API v3 — Overview"
type: research
author:
  - Person 2
  - Person 1
created: 2026-11-07
aliases:
  - "YouTube Data API"
  - "YouTube Data API Overview"
tags:
  - research
  - youtube-mcp
  - youtube-api
  - quota
  - oauth
sources:
  - "https://developers.google.com/youtube/v3/getting-started"
  - "https://developers.google.com/youtube/data/determine_quota_cost"
status: ingested
---

# YouTube Data API v3 — Overview

## Overview

The YouTube Data API v3 is Google's official API for building applications that interact with
YouTube. It exposes YouTube data (videos, channels, playlists, comments, search results and
more) as **resources** that applications can read and, with user authorisation, create, modify
or delete.

It matters to us because it is the only permitted data source for the YouTube MCP server
(`NFR-01`).

## Key Concepts

- **Resource** — an individual data entity with a unique identifier (e.g. a `video`, `channel`
  or `playlist`).
- **Resource types** listed in the overview: `activity`, `channel`, `channelBanner`,
  `channelSection`, `guideCategory`, `i18nLanguage`, `i18nRegion`, `playlist`, `playlistItem`,
  `search result`, `subscription`, `thumbnail`, `video`, `videoCategory`, `watermark`. The
  supported-operations table also covers `caption`, `comment` and `commentThread`.
- **Resource references** — resources often point to other resources, e.g. a `playlistItem`
  identifies its video through `snippet.resourceId.videoId`.
- **Methods** — the four standard operations:
  - `list` — retrieve (GET) zero or more resources.
  - `insert` — create (POST) a resource.
  - `update` — modify (PUT) a resource.
  - `delete` — remove (DELETE) a resource.
  - Some resources have extra methods, e.g. `videos.rate` and `thumbnails.set`.
- **API key** — a project credential obtained in the Google Cloud console and passed as the
  `key` request parameter.
- **OAuth 2.0** — the authorisation mechanism required for methods that act on behalf of a user.
- **Quota units** — the cost accounting system Google uses to limit each project's API usage.
- **`part` parameter** — selects which top-level property groups of a resource to return (e.g.
  `snippet`, `contentDetails`, `statistics`, `status` for a video).
- **`fields` parameter** — filters the response down to specific (including nested) properties
  within the requested parts.
- **ETag** — an HTTP version identifier for a resource, used for caching and safe updates.

## Important Findings

### Getting started

1. Obtain a Google Account (to use the Google Cloud console, request an API key and register
   the application).
2. Create a project and obtain authorisation credentials.
3. Ensure the YouTube Data API is enabled for the project in the API Library.
4. Implement OAuth 2.0 if the application uses methods that require user authorisation.
5. Optionally choose a client library to simplify implementation.
6. Understand JSON, the API's data format.

### Authentication and authorisation

- All `insert`, `update` and `delete` operations **always require user authorisation**
  (OAuth 2.0).
- Some `list` methods support both authorised and unauthorised requests. Unauthorised requests
  only retrieve **public data**; authorised requests can also retrieve information about, or
  private to, the currently authenticated user.

### Supported operations (selected)

| Resource | list | insert | update | delete |
|---|---|---|---|---|
| `video` | Yes | Yes | Yes | Yes |
| `channel` | Yes | No | No | No |
| `playlist` | Yes | Yes | Yes | Yes |
| `playlistItem` | Yes | Yes | Yes | Yes |
| `search result` | Yes | No | No | No |
| `comment` | Yes | Yes | Yes | Yes |
| `commentThread` | Yes | Yes | Yes | No |
| `caption` | Yes | Yes | Yes | Yes |
| `videoCategory` | Yes | No | No | No |
| `subscription` | Yes | No | No | No |
| `activity` | Yes | No | No | No |

- `search result` has no persistent data of its own and supports only `list`.
- `guideCategory`, `thumbnail` and `watermark` support none of the four standard methods;
  `channelBanner` supports only `insert`.
- **No related-videos or related-channels endpoint** exists in the resource list, which is why
  the project computes similarity itself (project brief).
- **No watch-history resource** is available: the resource list returns nothing that exposes
  watch history, and `playlistItems.list` documents `watchHistoryNotAccessible`. This matches
  the brief's statement that watch history is unavailable.

### Quota

- **Every request costs quota** — "All API requests, including invalid requests, incur at least
  a one-point quota cost."
- The default allocation has a general daily unit pool plus **separate daily call buckets for
  `search.list` and `videos.insert`**. The canonical figures, verified against Google's pages,
  are in [SRS Appendix A](../../docs/srs.md#appendix-a--reference-youtube-api-quota); this note
  does not repeat them (project ADR 0006).
- The default quota is **subject to change**.
- Read operations retrieving a list of resources usually cost little; writes (create, update,
  delete) cost much more. Exact per-method costs are in Google's "Quota costs for API requests"
  table.
- Usage is visible on the **Quotas** page in the API Console. The getting-started page does
  not describe any API method that reports remaining quota.
- Additional quota can be requested via the **Quota extension request form for YouTube API
  Services**; the project brief forbids creating extra Cloud projects to obtain more.

### Partial resources and response size

- `part` is **required** for any request that retrieves or returns a resource. It cannot filter
  nested properties.
- `fields` filters within the requested parts using an XPath-like syntax:
  - `fields=a,b` — multiple fields.
  - `fields=*` — all fields.
  - `fields=a(b,c)` — group nested properties.
  - `fields=a/b` — select a nested property.
  - Values must be URL-encoded.
- Search results give only light snippet data. Durations and categories require a follow-up
  `videos.list` call, which accepts several IDs at once and so is cheap per video.

### ETags

- **Caching:** send the stored ETag with a repeat request; if the resource is unchanged the API
  returns **HTTP 304 Not Modified** and the cached copy can be reused.
- **Overwrite protection:** include the ETag when updating or deleting; the request fails if
  the resource has changed since.
- The JavaScript client library supports `If-Match` / `If-None-Match`; the Obj-C client library
  does not support ETags.

### Gzip compression

- Set the `Accept-Encoding: gzip` header **and** include `gzip` in the User-Agent string to
  receive compressed responses (less bandwidth, some extra CPU to decompress).

## Relevance to Our Project

> The points below are our team's interpretation of the sources, not statements from Google.

- **Provider scope:** the `video`, `channel`, `playlist`, `playlistItem`, `subscription`,
  `videoCategory` and `search` resources cover what the YouTube provider (`SE-06`, `NFR-07`)
  needs for `FR-01`…`FR-05`.
- **Search is the scarcest resource:** `search.list` has its own small daily bucket, so
  candidate generation for `FR-01`, `FR-02`, `FR-03` and `FR-05` must use few searches, reuse
  results and report clearly when the bucket is exhausted (`OD-09`, project ADR 0006).
- **Batching:** `videos.list` with many IDs is the main tool for fetching duration, category,
  tags and language for many candidates cheaply.
- **Invalid requests still cost quota:** validate tool inputs (e.g. video IDs, parameters)
  before calling the API (`NFR-04.1`).
- **Keep payloads small:** request only the needed `part` values and use `fields` to trim
  responses — useful both for efficiency and for keeping MCP tool output concise.
- **Caching:** ETag-based conditional requests can reduce repeat data transfer. Whether a 304
  response still consumes quota is not stated in the source and needs verification.
- **Public reads and OAuth:** public video and channel data is available to unauthorised
  requests with an API key; personal library reads and playlist creation need OAuth 2.0 (see
  [[OAuth-Authentication|OAuth 2.0 Authentication]]).
- **Secrets handling:** the API key is a credential and must not be committed to the repository
  (`NFR-05.1`).

## Related Requirements

`FR-01`, `FR-02`, `FR-03`, `FR-04`, `FR-05`, `NFR-01`, `NFR-02.1`, `NFR-02.2`, `NFR-04.1`,
`NFR-05.1`, `SE-06`. Requirement source: [SRS](../../docs/srs.md).

## Sources

- **YouTube Data API Overview** ("Getting started") — Google for Developers.
  https://developers.google.com/youtube/v3/getting-started (accessed 2026-11-07 by both
  contributors; re-verified 2026-11-08). Person 1 recorded a "last updated 2026-11-03" date on
  2026-11-07; Person 2 saw no date, and the page content fetched on 2026-11-08 showed none.
- **Quota costs for API requests** — Google for Developers.
  https://developers.google.com/youtube/data/determine_quota_cost (accessed 2026-11-07;
  re-verified 2026-11-08).

## Contributors

This note consolidates two notes on the same topic (audit issue D-1, 2026-11-08):

- **Person 2** — the original `YouTube-Data-API.md` (ingested 2026-11-07, `brain/log.md`
  Activity 1): concepts, getting started, authorisation, supported operations, partial
  resources, ETags, gzip and most project-relevance points.
- **Person 1** — `YouTube Data API Overview.md` (merged in PR #15): the missing related-content
  and watch-history findings, search-result follow-up via `videos.list`, the quota-extension and
  extra-project constraint, and the search-capacity relevance points.

## Related Notes

- [[YouTube-Video-Resource|YouTube Video Resource]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- [[YouTube-API-Quota-Management|YouTube API Quota Management]]
- [[OAuth-Authentication|OAuth 2.0 Authentication]]
- [[MCP-Architecture|MCP Architecture]]
