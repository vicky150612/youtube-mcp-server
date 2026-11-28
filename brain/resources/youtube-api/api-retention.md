---
title: API caching and retention
created: 2026-11-28
source: https://developers.google.com/youtube/terms/developer-policies
requirements: [NFR-03]
issues: [19]
author: Jithamanyu404
---

# API caching and retention

YouTube's policies distinguish Authorized and Non-Authorized API Data.
The assignment's stronger maximum for public metadata is 24 hours.
Keep public cache entries in memory and never cache authenticated library
snapshots or authorisation state. Preflight using worst-case cache misses.

[[brain/projects/youtube-mcp/overview]]
