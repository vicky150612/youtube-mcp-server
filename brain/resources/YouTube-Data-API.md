---
title: "YouTube Data API v3 — Overview"
type: research
aliases:
  - "YouTube Data API"
tags:
  - research
  - youtube-mcp
  - youtube-api
source: "https://developers.google.com/youtube/v3/getting-started"
---

# YouTube Data API v3 — Overview

## Overview

The YouTube Data API v3 is Google's official API for building applications that interact with YouTube. It exposes YouTube data (videos, channels, playlists, comments, search results and more) as **resources** that applications can read and, with user authorisation, create, modify or delete.

It matters to us because it is the primary official data source for retrieving YouTube video information in our YouTube MCP server.

## Key Concepts

- **Resource** — an individual data entity with a unique identifier (e.g. a `video`, `channel` or `playlist`).
- **Resource types** listed in the overview: `activity`, `channel`, `channelBanner`, `channelSection`, `guideCategory`, `i18nLanguage`, `i18nRegion`, `playlist`, `playlistItem`, `search result`, `subscription`, `thumbnail`, `video`, `videoCategory`, `watermark`. The supported-operations table also covers `caption`, `comment` and `commentThread`.
- **Resource references** — resources often point to other resources, e.g. a `playlistItem` identifies its video through `snippet.resourceId.videoId`.
- **Methods** — the four standard operations:
  - `list` — retrieve (GET) zero or more resources.
  - `insert` — create (POST) a resource.
  - `update` — modify (PUT) a resource.
  - `delete` — remove (DELETE) a resource.
  - Some resources have extra methods, e.g. `videos.rate` and `thumbnails.set`.
- **API key** — a project credential obtained in the Google Cloud console and passed as the `key` request parameter.
- **OAuth 2.0** — the authorisation mechanism required for methods that act on behalf of a user.
- **Quota units** — the cost accounting system Google uses to limit each project's API usage.
- **`part` parameter** — selects which top-level property groups of a resource to return (e.g. `snippet`, `contentDetails`, `statistics`, `status` for a video).
- **`fields` parameter** — filters the response down to specific (including nested) properties within the requested parts.
- **ETag** — an HTTP version identifier for a resource, used for caching and safe updates.

## Important Findings

### Getting started

1. Obtain a Google Account (to use the Google Cloud console, request an API key and register the application).
2. Create a project and obtain authorisation credentials.
3. Ensure the YouTube Data API is enabled for the project in the API Library.
4. Implement OAuth 2.0 if the application uses methods that require user authorisation.
5. Optionally choose a client library to simplify implementation.
6. Understand JSON, the API's data format.

### Authentication and authorisation

- All `insert`, `update` and `delete` operations **always require user authorisation** (OAuth 2.0).
- Some `list` methods support both authorised and unauthorised requests. Unauthorised requests only retrieve **public data**; authorised requests can also retrieve information about, or private to, the currently authenticated user.

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
- `guideCategory`, `thumbnail` and `watermark` support none of the four standard methods; `channelBanner` supports only `insert`.

### Quota

- **Every request costs quota** — "All API requests, including invalid requests, incur at least a one-point quota cost."
- **Default daily allocation per project:**
  - `search.list` — separate limit of **100 calls per day**.
  - `videos.insert` — separate limit of **100 calls per day**.
  - **All other endpoints** — share a combined **10,000 units per day**.
- The default quota is **subject to change**.
- **Typical costs** (exact per-method costs are in Google's "Quota costs for API requests" table):
  - Read operation retrieving a list of resources (channels, videos, playlists): usually **1 unit**.
  - Write operation (create, update, delete): usually **50 units**.
  - Search query (`search.list`): **1 unit**.
  - Video upload (`videos.insert`): **1 unit**.
- Usage is visible on the **Quotas** page in the API Console.
- Additional quota can be requested via the **Quota extension request form for YouTube API Services**.

### Partial resources and response size

- `part` is **required** for any request that retrieves or returns a resource. It cannot filter nested properties.
- `fields` filters within the requested parts using an XPath-like syntax:
  - `fields=a,b` — multiple fields.
  - `fields=*` — all fields.
  - `fields=a(b,c)` — group nested properties.
  - `fields=a/b` — select a nested property.
  - Values must be URL-encoded.

### ETags

- **Caching:** send the stored ETag with a repeat request; if the resource is unchanged the API returns **HTTP 304 Not Modified** and the cached copy can be reused.
- **Overwrite protection:** include the ETag when updating or deleting; the request fails if the resource has changed since.
- The JavaScript client library supports `If-Match` / `If-None-Match`; the Obj-C client library does not support ETags.

### Gzip compression

- Set the `Accept-Encoding: gzip` header **and** include `gzip` in the User-Agent string to receive compressed responses (less bandwidth, some extra CPU to decompress).

## Relevance to Our Project

> The points below are our team's interpretation of the source, not statements from Google.

- **Primary data source:** the `video`, `channel`, `playlist`, `playlistItem`, `commentThread` and `search` resources cover the core information a YouTube video-intelligence MCP server would expose as tools.
- **Read-only features can avoid OAuth:** public video and channel data is available through unauthorised `list` / `search` requests using an API key. OAuth 2.0 becomes necessary only if we add features that act on a user's account or read private data.
- **Search is the tightest constraint:** `search.list` has its own 100-calls-per-day default limit, so search-based tools need caching, result reuse, and clear error handling when the limit is reached. Fetching details by known video ID via `videos.list` draws from the separate 10,000-unit pool.
- **Invalid requests still cost quota:** we should validate tool inputs (e.g. video IDs, parameters) before calling the API.
- **Keep payloads small:** request only the needed `part` values and use `fields` to trim responses — useful both for efficiency and for keeping MCP tool output concise for the agent.
- **Caching:** ETag-based conditional requests can reduce repeat data transfer for frequently requested resources. Whether a 304 response still consumes quota is not stated in this source and needs verification.
- **Secrets handling:** the API key is a credential and must not be committed to the repository.

## Related Requirements

> Requirement definitions do not yet exist in the Second Brain. These links are unresolved references supplied by the contributor; their definitions have not been documented here.

- [[FR-1]]
- [[FR-2]]
- [[FR-3]]
- [[FR-4]]
- [[FR-5]]

## Sources

- **YouTube Data API Overview** ("Getting started")
  - Organisation: Google for Developers
  - URL: https://developers.google.com/youtube/v3/getting-started
  - Accessed: 2026-11-07
  - Note: no author or last-updated date was visible on the page.

## Related Notes

> The notes below are **planned / not yet created**. They are listed in [[index]] but do not exist yet.

- [[YouTube MCP Server]] *(planned — not yet created)*
- [[YouTube API Quota Management]] *(planned — not yet created)*
- [[OAuth Authentication]] *(planned — not yet created)*
