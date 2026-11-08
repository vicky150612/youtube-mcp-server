---
sources:
  - "https://developers.google.com/youtube/data/reference/rest/v3/videos"
  - "https://developers.google.com/youtube/data/guides/implementation/ratings"
  - "https://developers.google.com/youtube/data/getting-started"
title: YouTube Video Resource
tags:
  - youtube
  - api
  - metadata
  - similarity
type: research
author: Person 1
status: draft-pending-brain-ingest
created: 2026-11-07
---

# YouTube Video Resource

## Overview
A `video` resource represents one YouTube video. Its metadata is the raw material for our **metadata-based similarity** (`FR-01`), our duration and language checks (`FR-05`) and our category analysis (`FR-04`). Fetched with `videos.list` (1 quota unit per call).

## Key Concepts
- **`snippet`**: `publishedAt`, `channelId`, `channelTitle`, `title`, `description`, `tags[]`, `categoryId`, `defaultLanguage`, `defaultAudioLanguage`, `liveBroadcastContent`, thumbnails.
- **`contentDetails.duration`**: an **ISO 8601 duration** (for example `PT15M51S`; videos of a day or more use the `P#DT#H#M#S` form). We must parse this into `duration_seconds`.
- **`statistics`**: view, like and comment counts (some can be hidden).
- **`status`** and **`topicDetails`** parts also exist.
- `snippet.tags[]` is optional; tags may contain spaces and have a combined length limit.
- Titles are limited to 100 characters, and the text fields are **untrusted input** from our point of view.

## Important Findings
- Tags, description and language fields can be **missing**. The similarity code must degrade gracefully (`TQ-04`, `AC-01.3`).
- `defaultLanguage` and `defaultAudioLanguage` are optional, so a language constraint in `FR-05` must handle "unknown" explicitly (`OD-06`).
- Duration arrives as a string, not seconds. Parsing is one of the unit-test targets named in the brief (`TQ-01`).
- Search results do not carry duration or category; they need a follow-up `videos.list`.
- `snippet.categoryId` is a numeric string; human-readable names come from `videoCategories.list` (1 unit).
- Likes by the user can be listed with `videos.list` and `myRating=like` (authorised request); this returns video resources but no "time liked".

## Relevance to Our Project
- Maps onto the shared internal `Video` model: `video_id`, `title`, `description`, `tags`, `channel_id`, `channel_title`, `duration_seconds`, `category_id`, `language`, `published_at`.
- Feature candidates for TF-IDF/weighted scoring: title, description, tags, category, channel, duration band.
- Prompt-injection surface: title, description and tags are attacker-controllable text and must never trigger actions (`NFR-04.2`).

## Related Requirements
`FR-01`, `FR-03`, `FR-04`, `FR-05`, `NFR-04.1`, `NFR-04.2`, `NFR-06.2`, `TQ-01`, `TQ-04`.

## Sources
- Videos resource reference: https://developers.google.com/youtube/data/reference/rest/v3/videos (accessed 2026-11-07)
- Ratings implementation guide (`myRating`): https://developers.google.com/youtube/data/guides/implementation/ratings (accessed 2026-11-07)
- Overview and `part` parameter: https://developers.google.com/youtube/data/getting-started (accessed 2026-11-07)

## Related Notes
- [[YouTube Data API Overview]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- Planned (other members): Cosine Similarity and TF-IDF
