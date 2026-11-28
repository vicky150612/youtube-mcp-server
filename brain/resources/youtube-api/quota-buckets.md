---
title: YouTube quota buckets and reset
created: 2026-11-28
source: https://developers.google.com/youtube/data/determine_quota_cost
requirements: [CON-02, NFR-02, TQ-06]
issues: [18]
author: Jithamanyu404
---

# YouTube quota buckets and reset

The combined default budget is 10,000 units per day. Search and video
upload each have a separate 100-call daily bucket. Every page counts as
a request. Playlist and playlist item inserts each cost 50 combined
units. Daily counters reset at midnight Pacific, including DST.

[[brain/projects/youtube-mcp/overview]]
