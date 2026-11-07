---
title: YouTube Channel Resource
tags:
  - youtube
  - api
  - channel
  - similarity
type: research
author: Person 1
status: draft-pending-brain-ingest
created: 2026-11-07
---

# YouTube Channel Resource

## Overview
A `channel` resource describes one YouTube channel. It is the input for `FR-02` (similar channels) and the way to find a channel's uploaded videos and, for the authorised user, their liked-videos playlist. Fetched with `channels.list` (1 quota unit per call).

## Key Concepts
- **Lookup filters.** `channels.list` accepts exactly one of: `id`, `forHandle` (with or without `@`), `forUsername`, `mine`, `managedByMe`. Specifying more than one returns a `badRequest / invalidCriteria` error. The `categoryId` filter is **deprecated**.
- **Parts:** `snippet`, `statistics`, `topicDetails`, `brandingSettings` (includes channel keywords), `contentDetails`, `localizations`, `status`, plus owner-only parts.
- **`contentDetails.relatedPlaylists`**: playlist IDs for the channel's uploads and, for the authorised user's own channel, the liked-videos playlist.
- **`statistics`**: view, video and subscriber counts. Subscriber counts follow a YouTube display policy and may be hidden (`hiddenSubscriberCount`).

## Important Findings
- Our input formats map directly onto the API: a channel URL gives either an ID (`UC...`) or a handle; use `id` or `forHandle` after normalising the input (`FR-02`, `AC-02.1`).
- Because the category filter is deprecated and there is no related-channels endpoint, similar-channel discovery must go through our own logic: search for channels or videos on the topic, then compare channel metadata.
- Useful channel features for similarity: title, description, `brandingSettings.channel.keywords`, `topicDetails` and the metadata of recent uploads (fetched cheaply via the uploads playlist).
- Metadata can be sparse or hidden, so "insufficient metadata" must be a defined outcome (`AC-02.3`).
- A non-existent channel yields an empty result, which we must convert into a typed "not found" error (`AC-02.4`).

## Relevance to Our Project
- Maps onto the internal `Channel` model (to be frozen at kickoff).
- The uploads playlist read through `playlistItems.list` costs 1 unit, versus search calls from the limited search bucket, so it is the preferred way to sample a channel's videos (`OD-09`).
- Needed for `FR-04` top-channel analysis (channel names for aggregation).

## Related Requirements
`FR-02`, `FR-03`, `FR-04`, `NFR-02.1`, `NFR-03.2`, `NFR-06.2`, `TQ-04`.

## Sources
- channels.list reference: https://developers.google.com/youtube/data/reference/rest/v3/channels/list (accessed 2026-11-07)
- Overview: https://developers.google.com/youtube/data/getting-started (accessed 2026-11-07)

## Related Notes
- [[YouTube Data API Overview]]
- [[YouTube Video Resource]]
- [[YouTube Playlist Resource]]
