---
sources:
  - "https://developers.google.com/youtube/data/getting-started"
  - "https://developers.google.com/youtube/data/determine_quota_cost"
title: YouTube Data API Overview
tags:
  - youtube
  - api
  - quota
  - oauth
type: research
author: Person 1
status: draft-pending-brain-ingest
created: 2026-11-07
---

# YouTube Data API Overview

## Overview
The YouTube Data API v3 is the official way for an application to read and manage YouTube data. It is organised around **resources** (video, channel, playlist, playlistItem, subscription, search result, videoCategory and others) and **operations** (`list`, `insert`, `update`, `delete`). Write operations always need user authorisation (OAuth 2.0); some `list` calls work with only an API key but then return public data only.

## Key Concepts
- **Resources and parts.** Every request that returns a resource must name the `part`s it wants (for a video: `snippet`, `contentDetails`, `statistics`, `status`, `topicDetails` and others). The optional `fields` parameter trims the response further.
- **Quota.** Each method has a cost. Reads cost about 1 unit, writes about 50. Every request, even an invalid one, costs at least 1.
- **Default allocation (Google, page last updated 2026-11-03).** 10,000 units/day for general endpoints, plus a **separate bucket of 100 `search.list` calls/day** and 100 `videos.insert` calls/day. Resets at midnight Pacific Time.
- **ETags** allow conditional requests (HTTP 304), which helps caching.
- **No related-videos or related-channels endpoint** in the resource list, which is why we compute similarity ourselves (project brief).

## Important Findings
- The search quota rules changed relative to older guides. Many blogs still say `search.list` costs 100 units. Google's own page now describes a 100-calls/day bucket. Check the **Quotas** page of our Cloud project before designing around either number.
- Search results give only light snippet data. Durations and categories require a follow-up `videos.list` call, which accepts several IDs at once and so is cheap per video.
- The resource list contains `activity`, `playlist`, `playlistItem`, `subscription`, `video`, `videoCategory`, but nothing that returns watch history. This matches the brief's statement that watch history is unavailable.
- Quota increases exist (extension request form), but the brief forbids creating extra Cloud projects to get more.

## Relevance to Our Project
- Defines what the **YouTube provider** (SE-06) may call and what each call costs, which feeds the quota pre-check (`NFR-02.2`).
- Search calls are the scarce resource: candidate generation for `FR-01`, `FR-02` and `FR-05` must use few of them and cache results.
- `videos.list` batching is the main tool for fetching duration, category, tags and language for many candidates cheaply.

## Related Requirements
`FR-01`, `FR-02`, `FR-03`, `FR-04`, `FR-05`, `NFR-01`, `NFR-02.1`, `NFR-02.2`, `SE-06` (see `docs/srs.md`).

## Sources
- YouTube Data API Overview: https://developers.google.com/youtube/data/getting-started (last updated 2026-11-03; accessed 2026-11-07)
- Quota costs table: https://developers.google.com/youtube/data/determine_quota_cost (last updated 2026-11-03; accessed 2026-11-07)

## Related Notes
- [[YouTube Video Resource]]
- [[YouTube Channel Resource]]
- [[YouTube Playlist Resource]]
- Planned (other members): YouTube Quota Management, YouTube OAuth Authentication
