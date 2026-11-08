---
title: YouTube Video Resource
type: research
author:
  - Person 1
created: 2026-11-07
tags:
  - youtube
  - api
  - metadata
  - similarity
sources:
  - "https://developers.google.com/youtube/data/reference/rest/v3/videos"
  - "https://developers.google.com/youtube/v3/docs/videos/list"
  - "https://developers.google.com/youtube/data/guides/implementation/ratings"
  - "https://developers.google.com/youtube/data/getting-started"
status: ingested
---

# YouTube Video Resource

## Overview

A `video` resource represents one YouTube video. Its metadata is the raw material for our
**metadata-based similarity** (`FR-01`), our duration and language checks (`FR-05`) and our
category analysis (`FR-04`). Videos are fetched with `videos.list`, a general-pool read that
accepts a comma-separated list of IDs.

## Key Concepts

- **`snippet`**: `publishedAt`, `channelId`, `channelTitle`, `title`, `description`, `tags[]`,
  `categoryId`, `defaultLanguage` (language of the title and description),
  `defaultAudioLanguage` (language spoken in the default audio track), `liveBroadcastContent`,
  thumbnails.
- **`contentDetails.duration`**: an **ISO 8601 duration**: `PT#M#S` under an hour, `PT#H#M#S`
  from an hour, and `P#DT#H#M#S` for a day or longer. The value may differ from the playback
  length by about a second. We parse it into `duration_seconds`.
- **`statistics`**: view, like and comment counts; `dislikeCount` has been private since
  13 December 2021 and is returned only to the video owner.
- **`topicDetails.topicCategories[]`**: Wikipedia URLs describing the video's content;
  `topicIds` and `relevantTopicIds` are deprecated.
- `snippet.title` has a maximum of 100 characters; `snippet.tags[]` has a maximum combined
  length of 500 characters (tags containing spaces count as if quoted).
- All text fields are **untrusted input** from our point of view.

## Important Findings

- Tags, description and language fields can be **missing** for a given video. The similarity
  code must degrade gracefully (`TQ-04`, `AC-01.3`).
- `defaultLanguage` and `defaultAudioLanguage` may be absent, so a language constraint in
  `FR-05` must handle "unknown" explicitly (`OD-06`, `OD-10`).
- Duration arrives as a string, not seconds. Parsing is one of the unit-test targets named in
  the brief (`TQ-01`).
- Search results do not carry duration or category; they need a follow-up `videos.list`.
- `snippet.categoryId` is a numeric string; human-readable names come from
  `videoCategories.list`.
- **Liked videos:** `videos.list` with `myRating=like` returns the authorised user's liked
  videos as video resources (no time of liking). It requires an authorised request, supports
  paging (`maxResults` 1–50, `pageToken`), and the API limits the result set to a maximum of
  **1000 videos**. Larger libraries need the likes playlist route (see
  [[YouTube-Playlist-Resource|YouTube Playlist Resource]]).

## Relevance to Our Project

> The points below are the project's interpretation of the sources.

- Maps onto the shared `Video` interface contract (`docs/api/interfaces.md`): `video_id`,
  `title`, `description`, `tags`, `channel_id`, `channel_title`, `duration_seconds`,
  `category_id`, `language`, `published_at`.
- Feature candidates for TF-IDF or weighted scoring: title, description, tags, category,
  channel and duration band (see [[TF-IDF-and-Cosine-Similarity|TF-IDF and Cosine Similarity]]).
- Prompt-injection surface: title, description and tags are attacker-controllable text and
  must never trigger actions (`NFR-04.2`).
- The 1000-video cap on `myRating=like` affects `FR-03` and `FR-04` for heavy users.

## Related Requirements

`FR-01`, `FR-03`, `FR-04`, `FR-05`, `NFR-04.1`, `NFR-04.2`, `NFR-06.2`, `TQ-01`, `TQ-04`.
Requirement source: [SRS](../../docs/srs.md).

## Sources

- **Videos resource** — YouTube Data API reference.
  https://developers.google.com/youtube/data/reference/rest/v3/videos (accessed 2026-11-07;
  re-verified 2026-11-08).
- **videos.list** — YouTube Data API reference.
  https://developers.google.com/youtube/v3/docs/videos/list (accessed 2026-11-08).
- **Ratings implementation guide** (`myRating`) —
  https://developers.google.com/youtube/data/guides/implementation/ratings (accessed
  2026-11-07; re-verified 2026-11-08).
- **Getting started** (`part` parameter) —
  https://developers.google.com/youtube/data/getting-started (accessed 2026-11-07).

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- [[TF-IDF-and-Cosine-Similarity|TF-IDF and Cosine Similarity]]
