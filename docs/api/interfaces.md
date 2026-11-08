# Shared interface contracts (draft)

- **Status:** Draft for review — **not frozen**. Freezing requires agreement from all three
  members in a pull request (`OD-17`; the plan's Day-1 freeze did not happen, and a freeze before Stage 2 design work is proposed in `docs/development-plan.md`).
- **Owners (unconfirmed):** Person 1 (provider, `Video`, `Channel`, `UserLibrarySnapshot`),
  Person 3 (`PlaylistConstraints`, proposal and MCP tool shapes), Person 2 (consumer review for
  similarity, recommendations and analysis).
- **Language:** contracts are language-neutral because the application stack is undecided
  (`OD-01`). Map them to typed models (for example classes or interfaces) once it is chosen.

Field types: `string`, `integer` (non-negative unless stated), `datetime` (ISO 8601, UTC),
`date`, `list<T>`, `enum`, `T?` (optional; absent means "unknown", never an invented default).
Source fields refer to the YouTube Data API v3 resources described in the Brain notes
[YouTube Video Resource](../../brain/resources/YouTube-Video-Resource.md),
[YouTube Channel Resource](../../brain/resources/YouTube-Channel-Resource.md) and
[YouTube Playlist Resource](../../brain/resources/YouTube-Playlist-Resource.md).

## `Video`

| Field | Type | Required | Source / rule |
|---|---|---|---|
| `video_id` | string | Yes | `id`; validated 11-character ID |
| `title` | string | Yes | `snippet.title` (untrusted text) |
| `description` | string? | No | `snippet.description` (untrusted text) |
| `tags` | list<string> | Yes (may be empty) | `snippet.tags[]`; empty list when absent |
| `channel_id` | string | Yes | `snippet.channelId` |
| `channel_title` | string? | No | `snippet.channelTitle` |
| `duration_seconds` | integer? | No | parsed from `contentDetails.duration` (ISO 8601); absent if unparseable |
| `category_id` | string? | No | `snippet.categoryId` |
| `language` | string? | No | BCP-47 code from `snippet.defaultAudioLanguage`, else `snippet.defaultLanguage` (`OD-10`) |
| `published_at` | datetime? | No | `snippet.publishedAt` |
| `availability` | enum `public`, `unlisted`, `private_or_deleted` | Yes | derived from presence and `status`; private/deleted videos are not returned as normal results (`AC-01.5`) |

## `Channel`

| Field | Type | Required | Source / rule |
|---|---|---|---|
| `channel_id` | string | Yes | `id` (`UC…`) |
| `title` | string | Yes | `snippet.title` |
| `description` | string? | No | `snippet.description` |
| `handle` | string? | No | `snippet.customUrl` if present |
| `keywords` | list<string> | Yes (may be empty) | `brandingSettings.channel.keywords` split on spaces |
| `topic_categories` | list<string> | Yes (may be empty) | `topicDetails.topicCategories[]` |
| `subscriber_count` | integer? | No | `statistics.subscriberCount`; absent when `hiddenSubscriberCount` is true |
| `video_count` | integer? | No | `statistics.videoCount` |
| `uploads_playlist_id` | string? | No | `contentDetails.relatedPlaylists.uploads` |

## `PlaylistConstraints`

| Field | Type | Required | Rule |
|---|---|---|---|
| `topic` | string | Yes | Non-empty, at most 200 characters, treated as untrusted search text |
| `total_duration_seconds` | integer | Yes | 60 … 43,200 (12 hours) **[PROPOSED range]** |
| `max_video_seconds` | integer? | No | ≥ 60 and ≤ `total_duration_seconds` when present |
| `language` | string? | No | BCP-47 primary subtag (`OD-10`) |
| `allow_unknown_language` | boolean | Yes (default false) | `OD-06` |
| `duration_tolerance_ratio` | number | Yes | Default 0.10 **[PROPOSED, `OD-06`]** |
| `title` | string? | No | Playlist title; generated from the topic if absent |
| `privacy` | enum `private`, `unlisted`, `public` | Yes (default `private`) | **[PROPOSED]** |

## `UserLibrarySnapshot`

| Field | Type | Required | Rule |
|---|---|---|---|
| `retrieved_at` | datetime | Yes | When the snapshot was taken |
| `liked_videos` | list<`LibraryItem`> | Yes (may be empty) | From the likes playlist, else `videos.list?myRating=like` (at most 1000) |
| `liked_videos_source` | enum `likes_playlist`, `my_rating`, `unavailable` | Yes | Records which route was used (F-4) |
| `subscriptions` | list<`Subscription`> | Yes (may be empty) | `subscriptions.list?mine=true` |
| `playlists` | list<`PlaylistSummary`> | Yes (may be empty) | `playlists.list?mine=true` with items via `playlistItems.list` |
| `truncated` | boolean | Yes | True if a cap (for example the 1000-video limit or a quota budget) cut the data |

`LibraryItem`: `video_id` (string), `added_at` (datetime?, the like or playlist-add time),
`video` (`Video`?). `Subscription`: `channel_id` (string), `title` (string?), `subscribed_at`
(datetime?, `snippet.publishedAt`). `PlaylistSummary`: `playlist_id` (string), `title`
(string), `items` (list<`LibraryItem`>). No field holds watch history.

## `PlaylistProposal`

`proposal_id` (string, ≥ 128 random bits), `digest` (string, SHA-256 of the canonical content),
`fingerprint` (string, short display form of the digest), `constraints` (`PlaylistConstraints`),
`videos` (ordered list<`Video`>), `total_duration_seconds` (integer), `constraint_report`
(list of per-constraint pass/fail with reasons), `estimated_write_units` (integer), `expires_at`
(datetime), `state` (enum `proposed`, `creating`, `created`, `partially_created`, `cancelled`,
`superseded`, `expired`). See [ADR 0007](../adr/0007-playlist-confirmation.md).

## `YouTubeProvider` operations

Every operation declares its quota cost per bucket so the quota manager can pre-check a
workflow (`NFR-02.2`); an operation without a declared cost cannot be planned (proposed
`NFR-02.3`). Costs come from [SRS Appendix A](../srs.md#appendix-a--reference-youtube-api-quota).

| Operation | Returns | API methods | Auth | Cost per call |
|---|---|---|---|---|
| `get_videos(ids)` | list<`Video`> | `videos.list` (batched IDs) | API key or OAuth | 1 unit per call |
| `get_channel(channel_ref)` | `Channel` | `channels.list` (`id` or `forHandle`) | API key or OAuth | 1 unit |
| `list_channel_uploads(channel_id, max_items)` | list<`video_id`> | `playlistItems.list` (paged) | API key or OAuth | 1 unit per page |
| `search_videos(query, max_results)` | list<`video_id`> | `search.list` | API key or OAuth | 1 search call per page |
| `search_channels(query, max_results)` | list<`channel_id`> | `search.list` | API key or OAuth | 1 search call per page |
| `get_library_snapshot(limits)` | `UserLibrarySnapshot` | `channels.list?mine`, `playlistItems.list`, `videos.list?myRating`, `subscriptions.list?mine`, `playlists.list?mine` | OAuth `youtube.readonly` | 1 unit per call/page |
| `create_playlist(title, description, privacy)` | `playlist_id` | `playlists.insert` | OAuth `youtube` | 50 units |
| `add_playlist_item(playlist_id, video_id)` | `playlist_item_id` | `playlistItems.insert` | OAuth `youtube` | 50 units |

Only the playlist module's confirmed creation path may call `create_playlist` and
`add_playlist_item` (ADR 0007).

## Typed errors

All operations return results or one of these typed errors, never raw API responses or stack
traces (`NFR-06.2`):

| Error | When |
|---|---|
| `invalid_input` | Validation failed before any API call (`NFR-04.1`) |
| `not_found` | Video, channel or playlist does not exist |
| `unavailable` | Private or deleted video (`AC-01.5`) |
| `insufficient_metadata` | Not enough metadata to compute a result (`AC-02.3`) |
| `insufficient_data` | Empty library (`AC-03.3`) |
| `quota_budget_insufficient` | Pre-check rejected the workflow before any call (`NFR-02.2`) |
| `quota_exhausted` | Google returned `quotaExceeded`; bucket marked exhausted until reset |
| `rate_limited` | Rate limiting after bounded retries |
| `authorization_required` | Missing, expired or revoked credentials, or insufficient scope; includes re-authorisation instructions (`NFR-03.3`) |
| `channel_required` | `youtubeSignupRequired` (`NFR-06.1`) |
| `proposal_not_found`, `proposal_expired`, `proposal_invalid` | Confirmation checks (`AC-05.11`) |
| `confirmation_unavailable` | Client cannot provide elicitation (`AC-05.12`) |
| `confirmation_declined` | User declined (`AC-05.14`) |
| `partial_failure` | Playlist created but some items failed; lists added and failed items (`AC-05.8`) |
| `upstream_error` | Any other API failure, with a sanitised message |

## Authentication assumptions

Local stdio deployment with a desktop OAuth client (proposed, [ADR 0008](../adr/0008-oauth-client-and-scopes.md));
one authorised user per server process; public reads may use the OAuth token; the provider
never logs tokens or returns them in results.
