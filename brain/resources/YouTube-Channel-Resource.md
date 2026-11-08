---
title: YouTube Channel Resource
type: research
author:
  - Person 1
created: 2026-11-07
tags:
  - youtube
  - api
  - channel
  - similarity
sources:
  - "https://developers.google.com/youtube/data/reference/rest/v3/channels/list"
  - "https://developers.google.com/youtube/data/reference/rest/v3/channels"
  - "https://developers.google.com/youtube/data/getting-started"
status: ingested
---

# YouTube Channel Resource

## Overview

A `channel` resource describes one YouTube channel. It is the input for `FR-02` (similar
channels) and the way to find a channel's uploaded videos and, for the authorised user, their
liked-videos playlist. Channels are fetched with `channels.list`, a general-pool read (exact
cost in [SRS Appendix A](../../docs/srs.md#appendix-a--reference-youtube-api-quota)).

## Key Concepts

- **Lookup filters.** `channels.list` takes one filter: `id`, `forHandle` (the value may be
  prefixed with `@`), `forUsername`, `mine` or `managedByMe`. Giving more than one returns
  `badRequest (400)` with `invalidCriteria`. The `categoryId` filter is deprecated.
- **Parts:** `auditDetails`, `brandingSettings`, `contentDetails`, `contentOwnerDetails`, `id`,
  `localizations`, `snippet`, `statistics`, `status`, `topicDetails`.
- **`contentDetails.relatedPlaylists`**: playlist IDs associated with the channel, including
  `uploads` and `likes` (the playlist of the channel's liked videos).
- **`statistics`**: view, video and subscriber counts. `subscriberCount` is rounded down to
  three significant figures, and `hiddenSubscriberCount` indicates whether the count is
  publicly visible.
- **`brandingSettings.channel.keywords`**: a space-separated list of keywords with a 500-character
  total limit; **`topicDetails.topicCategories[]`**: Wikipedia URLs describing the channel's
  content.

## Important Findings

- Our input formats map onto the API: a channel URL gives either an ID (`UC…`) or a handle; use
  `id` or `forHandle` after normalising the input (`FR-02`, `AC-02.1`).
- Because the category filter is deprecated and there is no related-channels endpoint, similar-
  channel discovery must use our own logic: find candidate channels or videos on the topic,
  then compare channel metadata.
- Useful channel features for similarity: title, description, keywords, topic categories and
  the metadata of recent uploads (read through the uploads playlist).
- Metadata can be sparse or hidden, so "insufficient metadata" must be a defined outcome
  (`AC-02.3`).
- The `channels.list` page does not state what is returned when no channel matches a handle;
  `channelNotFound (404)` is documented for the `id` filter. Treat both an error and an empty
  `items` list as "not found" (`AC-02.4`) and confirm the behaviour in a capped live test.

## Relevance to Our Project

> The points below are the project's interpretation of the sources.

- Maps onto the shared `Channel` interface contract (see `docs/api/interfaces.md`).
- Reading a channel's uploads through `playlistItems.list` uses the general quota pool, whereas
  search calls use the scarce search bucket, so the uploads playlist is the preferred way to
  sample a channel's videos (`OD-09`).
- Needed for `FR-04` top-channel analysis (channel names for aggregation).

## Related Requirements

`FR-02`, `FR-03`, `FR-04`, `NFR-02.1`, `NFR-06.2`, `TQ-04`. Requirement source:
[SRS](../../docs/srs.md).

## Sources

- **channels.list** — YouTube Data API reference, Google for Developers.
  https://developers.google.com/youtube/data/reference/rest/v3/channels/list (accessed
  2026-11-07; re-verified 2026-11-08).
- **Channels resource** — YouTube Data API reference.
  https://developers.google.com/youtube/data/reference/rest/v3/channels (accessed 2026-11-08).
- **Getting started** — YouTube Data API. https://developers.google.com/youtube/data/getting-started
  (accessed 2026-11-07).

The older `https://developers.google.com/youtube/v3/docs/...` URLs redirect to these pages.

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube-Video-Resource|YouTube Video Resource]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- [[TF-IDF-and-Cosine-Similarity|TF-IDF and Cosine Similarity]]
