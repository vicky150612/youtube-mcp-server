---
title: YouTube API methods and batching
created: 2026-11-28
source: https://developers.google.com/youtube/data/reference/rest
requirements: [FR-01, FR-02, FR-03, FR-04, FR-05]
issues: [3, 16]
author: Jithamanyu404
---

# YouTube API methods and batching

Use the official list and search methods and playlist insert methods.
The `part` parameter selects resource sections and `fields` reduces the
payload. Deduplicate video and channel IDs and send batches of up to 50.
Prefer the likes playlist for added timestamps. When falling back to
`videos.list?myRating=like`, mark like time as unknown.

[[brain/projects/youtube-mcp/overview]]
