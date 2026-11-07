---
title: YouTube Playlist Resource
tags:
  - youtube
  - api
  - playlist
  - write-operations
type: research
author: Person 1
status: draft-pending-brain-ingest
created: 2026-11-07
---

# YouTube Playlist Resource

## Overview
The `playlist` and `playlistItem` resources cover everything `FR-05` writes and everything `FR-03`/`FR-04` reads from the user's playlists. Creating a playlist is a **two-step write**: `playlists.insert` creates the empty playlist, then one `playlistItems.insert` per video adds it. Both are authorised, quota-costly operations.

## Key Concepts
- **`playlists.insert`**: 50 quota units. Requires the `snippet.title`; optional `snippet.description`, `snippet.defaultLanguage`, `status.privacyStatus`. Authorisation scopes include `youtube` and `youtube.force-ssl`.
- **`playlistItems.insert`**: 50 units per video added.
- **`playlistItems.list`**: 1 unit; returns the items of a playlist.
- **`playlistItem.snippet.publishedAt`**: the time the item was **added to the playlist**. `contentDetails.videoPublishedAt` is when the video itself was published.
- **`playlistItem.snippet.resourceId.videoId`** links an item to a video resource.
- Special lists (uploads, liked videos) are exposed as playlist IDs on the channel resource (see the channel note) and read with `playlistItems.list`.
- Known error: creating a playlist can fail with `maxPlaylistExceeded` if the channel is at its playlist limit.

## Important Findings
- **Cost of `FR-05`:** a 10-video playlist costs 50 + 10 × 50 = **550 units** in writes, before any read or search calls. This must be included in the quota pre-check, and a failed batch halfway must be reported honestly (`AC-05.7`, `AC-05.8`).
- A Google account **without a YouTube channel** cannot create playlists (project brief; surfaces as `youtubeSignupRequired`). Handle it explicitly and create nothing (`NFR-06.1`, `AC-05.5`).
- Liked videos can be read as playlist items, whose `publishedAt` gives a usable time dimension for period analysis in `FR-04`, which `videos.list?myRating=like` does not provide (`OD-05`).
- Playlists default behaviour should be decided by us; proposal: create new playlists **private** unless the user asks otherwise (`[PROPOSED]`).

## Relevance to Our Project
- Defines the provider methods `create_playlist(title, description)` and `add_videos_to_playlist(playlist_id, video_ids)`.
- Because writes are expensive and visible to the user, they sit behind the explicit confirmation gate (`NFR-04.2`).
- The user's own playlists (read via `playlists.list` and `playlistItems.list`, 1 unit each) feed `FR-03` and `FR-04`.

## Related Requirements
`FR-03`, `FR-04`, `FR-05`, `NFR-02.2`, `NFR-04.2`, `NFR-06.1`, `TQ-04`, `TQ-06`.

## Sources
- playlists.insert reference: https://developers.google.com/youtube/data/reference/rest/v3/playlists/insert (accessed 2026-11-07)
- playlistItems resource: https://developers.google.com/youtube/data/reference/rest/v3/playlistItems (accessed 2026-11-07)
- Quota costs: https://developers.google.com/youtube/data/determine_quota_cost (accessed 2026-11-07)
- Ratings guide (liked videos via playlist): https://developers.google.com/youtube/data/guides/implementation/ratings (accessed 2026-11-07)

## Related Notes
- [[YouTube Data API Overview]]
- [[YouTube Video Resource]]
- [[YouTube Channel Resource]]
- Planned (other members): YouTube OAuth Authentication, YouTube Quota Management
