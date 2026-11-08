---
title: YouTube Playlist Resource
type: research
author:
  - Person 1
created: 2026-11-07
tags:
  - youtube
  - api
  - playlist
  - write-operations
sources:
  - "https://developers.google.com/youtube/data/reference/rest/v3/playlists/insert"
  - "https://developers.google.com/youtube/data/reference/rest/v3/playlistItems"
  - "https://developers.google.com/youtube/v3/docs/playlistItems/insert"
  - "https://developers.google.com/youtube/data/determine_quota_cost"
  - "https://developers.google.com/youtube/data/guides/implementation/ratings"
status: ingested
---

# YouTube Playlist Resource

## Overview

The `playlist` and `playlistItem` resources cover everything `FR-05` writes and everything
`FR-03`/`FR-04` reads from the user's playlists. Creating a playlist is a **two-step write**:
`playlists.insert` creates the empty playlist, then one `playlistItems.insert` per video adds
it. Both are authorised, expensive write operations (costs in
[SRS Appendix A](../../docs/srs.md#appendix-a--reference-youtube-api-quota)).

## Key Concepts

- **`playlists.insert`**: requires `snippet.title`; optional `snippet.description`,
  `snippet.defaultLanguage`, `status.privacyStatus`. Requires one of the scopes `youtube`,
  `youtube.force-ssl` or `youtubepartner`.
- **`playlistItems.insert`**: one call per video added; requires the same scope set.
- **`playlistItems.list`**: returns the items of a playlist, up to 50 per page.
- **`playlistItem.snippet.publishedAt`**: "the date and time that the item was added to the
  playlist". `contentDetails.videoPublishedAt` is when the video itself was published.
- **`playlistItem.snippet.resourceId.videoId`** links an item to a video resource.
- Special lists (uploads, liked videos) are exposed as playlist IDs on the channel resource
  (`contentDetails.relatedPlaylists`) and read with `playlistItems.list`.
- **Errors:** `playlists.insert` can fail with `maxPlaylistExceeded` (the channel already has
  the maximum number of playlists); `playlistItems.insert` can fail with
  `playlistContainsMaximumNumberOfVideos`, `videoNotFound` or `playlistItemsNotAccessible`.
  No duplicate-item error is documented.

## Important Findings

- **Cost of `FR-05`:** a 10-video playlist needs 1 `playlists.insert` and 10
  `playlistItems.insert` calls, which is 550 units at the documented write cost, before any
  read or search calls. The quota pre-check must include it, and a batch that fails part-way
  must be reported honestly (`AC-05.7`, `AC-05.8`).
- A Google account **without a YouTube channel** cannot create playlists (project brief). The
  global errors reference documents `youtubeSignupRequired (401)` for an unlinked Google
  account; it is not listed on the `playlists.insert` page itself. Handle it explicitly and
  create nothing (`NFR-06.1`, `AC-05.5`).
- **Liked videos via the likes playlist:** Google's ratings guide documents retrieving the
  user's liked videos (not disliked) by reading the playlist ID in
  `contentDetails.relatedPlaylists.likes` and listing it with `playlistItems.list`. Each item's
  `publishedAt` gives a time dimension for period analysis in `FR-04` that
  `videos.list?myRating=like` does not provide (`OD-05`). The route is documented and not
  deprecated in the revision history (checked 2026-11-08), but it has **not been tested** in
  this project; see the empirical test plan in `docs/testing/README.md`.
- Default privacy for created playlists is a project decision; the proposal is to create
  playlists **private** unless the user asks otherwise (`[PROPOSED]`).

## Relevance to Our Project

> The points below are the project's interpretation of the sources.

- Defines provider operations to create a playlist and add videos to it (see the
  `YouTubeProvider` contract in `docs/api/interfaces.md`).
- Because writes are expensive and visible to the user, they sit behind the two-phase
  confirmation gate (`NFR-04.2`, `NFR-04.3`; project ADR 0007).
- The user's own playlists (read via `playlists.list` and `playlistItems.list`) feed `FR-03`
  and `FR-04`.

## Related Requirements

`FR-03`, `FR-04`, `FR-05`, `NFR-02.2`, `NFR-04.2`, `NFR-06.1`, `TQ-04`, `TQ-06`. Requirement
source: [SRS](../../docs/srs.md).

## Sources

- **playlists.insert** — YouTube Data API reference.
  https://developers.google.com/youtube/data/reference/rest/v3/playlists/insert (accessed
  2026-11-07; scopes and errors re-verified 2026-11-08).
- **PlaylistItems resource** — YouTube Data API reference.
  https://developers.google.com/youtube/data/reference/rest/v3/playlistItems (accessed
  2026-11-07; re-verified 2026-11-08).
- **playlistItems.insert** — YouTube Data API reference.
  https://developers.google.com/youtube/v3/docs/playlistItems/insert (accessed 2026-11-08).
- **Quota costs** — https://developers.google.com/youtube/data/determine_quota_cost (accessed
  2026-11-07; re-verified 2026-11-08).
- **Ratings implementation guide** (liked videos via playlist) —
  https://developers.google.com/youtube/data/guides/implementation/ratings (accessed
  2026-11-07; re-verified 2026-11-08).

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube-Video-Resource|YouTube Video Resource]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[YouTube-API-Quota-Management|YouTube API Quota Management]]
- [[OAuth-Authentication|OAuth 2.0 Authentication]]
