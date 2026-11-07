---
title: YouTube API Quota Management
type: research
aliases:
  - YouTube API Quota Management
tags:
  - research
  - youtube-mcp
  - youtube-api
  - quota
sources:
  - "https://developers.google.com/youtube/v3/determine_quota_cost"
  - "https://developers.google.com/youtube/v3/docs/errors"
author: Person 3
created: 2026-11-07
---

# YouTube API Quota Management

## Overview

The YouTube Data API v3 assigns quota to API requests. Each Google Cloud project has daily limits, and methods do not all have the same cost. Estimating and tracking the applicable quota before a workflow starts helps prevent avoidable API calls and quota exhaustion.

## Key Concepts

- **Quota unit:** A cost charged to a project for an API method call. The method determines the cost; it is not a uniform per-request price.
- **Separate method buckets:** `search.list` and `videos.insert` have their own daily call limits in addition to the general daily quota pool.
- **Pagination:** Each request for an additional result page is another API call and incurs quota.
- **`quotaExceeded`:** The YouTube Data API reports this as a `403` error when the request cannot be completed because the quota has been exceeded.
- **Caching:** Reusing eligible cached responses avoids making duplicate API calls. Cache freshness and identity rules are application design choices, not a guarantee of quota savings stated by the quota table.

## Important Findings

- The quota documentation gives defaults of **10,000 units per day** for endpoints in the general pool, **100 `search.list` calls per day**, and **100 `videos.insert` calls per day**. The two method-specific buckets are separate; each call costs one quota in its respective bucket. Daily quotas reset at midnight Pacific Time. Project-specific limits and the current quota table should be checked in Google Cloud Console because defaults can change.
- Common list methods, including `channels.list`, `videos.list`, `playlists.list` and `playlistItems.list`, cost **1 unit per call** in the published table. `playlists.insert` and `playlistItems.insert` each cost **50 units per call**. Additional pages are separate calls with their method's cost.
- All API requests, including invalid requests, incur at least one quota point. Validate parameters before making a request.

## Relevance to Our Project

The points below are project recommendations, not additional guarantees from Google's quota documentation:

- Before any workflow makes an API call, estimate all planned operations, pages and writes; track the cost in every applicable bucket. Reject the workflow before its first call if any bucket is insufficient or a required cost is unknown. This project rule is captured by [NFR-02.1 and NFR-02.2](../../docs/srs.md) and [TQ-06](../../docs/srs.md).
- Cache eligible reads using keys that include the request parameters and, for private/user data, the appropriate user context. Choose explicit freshness rules. Do not assume a conditional request or `304 Not Modified` is quota-free unless the current API documentation confirms it.
- Convert `quotaExceeded` to a clear user-facing error and stop the affected workflow; retrying the same call without a quota change does not resolve the exhausted-budget condition.
- Similar-video/channel search, personal-library reads and playlist writes draw on different methods and possibly different quota buckets. Estimate each method separately; a single aggregate request count is not sufficient.

## Related Requirements

- [FR-01 — Similar Videos](../../docs/srs.md), [FR-02 — Similar Channels](../../docs/srs.md), [FR-03 — Recommendations](../../docs/srs.md), [FR-04 — Engagement Analysis](../../docs/srs.md), and [FR-05 — Playlist Creation](../../docs/srs.md).
- [NFR-02 — Quota and caching](../../docs/srs.md), especially NFR-02.1 and NFR-02.2; [TQ-04 — Negative tests](../../docs/srs.md); [TQ-06 — Quota pre-check](../../docs/srs.md).

## Sources

- **Quota costs for API requests** — YouTube Data API, Google for Developers. https://developers.google.com/youtube/v3/determine_quota_cost (redirects to Google's current quota-cost page; accessed 2026-11-07).
- **YouTube Data API — Errors** — Google for Developers. https://developers.google.com/youtube/v3/docs/errors (redirects to the REST API errors reference; accessed 2026-11-07; publication/update date not stated on the page).

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube Playlist Resource]]
- [[OAuth-Authentication|OAuth 2.0 Authentication]]
- [[TF-IDF-and-Cosine-Similarity|TF-IDF and Cosine Similarity]]
