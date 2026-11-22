---
title: Engagement analysis data
created: 2026-11-22
source:
  - "YT-MCP-SRS.pdf v1.0, FR-04 and §6.3"
  - "Architecture and Interface Plan, §§1 and 3"
requirements:
  - FR-04
  - NFR-05.2
issues:
  - 12
---

# Summary

Engagement analysis uses a temporary snapshot of the user's likes,
subscriptions, and playlists. Counts and trends must preserve source
distinctions and handle missing timestamps explicitly.

# Key findings

## Source-grounded findings

- The shared `Library` model contains likes, subscriptions, playlists, and
  playlist items. The architecture plan specifies it as an in-memory snapshot
  that is neither persisted nor cached.
- FR-04 reports top channels/categories, trends, duration preferences, and
  optional period comparisons. Counts use distinct library items and retain
  separate likes, subscriptions, and playlist-item source counts.
- Trends use the applicable like, subscription, or playlist-add time.
  Unreliable or missing timestamps belong in an explicit unknown-time bucket;
  they are excluded from period summaries and must not be assigned invented
  dates.
- Duration buckets and their boundaries must be consistent and explained in
  the report definition. The architecture plan places their constants in the
  analysis service.

## Interpretation for YouTube MCP

Model absent timestamps as unknown data, not as zero, a current date, or an
estimated date. This preserves trustworthy period comparisons and makes the
limitations visible to users.

# Relevance to YouTube MCP

This note supports [issue #12](https://github.com/vicky150612/youtube-mcp-server/issues/12)
and helps keep the FR-04 report shape, privacy behavior, and analysis rules
consistent during implementation.

# Decisions or implications

- Do not persist or cache the user's library snapshot.
- Count distinct items while retaining each source's contribution.
- Exclude unknown-time items from dated period summaries while preserving
  their presence in the overall trend.
- State the metric meaning, data sources, and duration boundaries in the
  report's definition.

# Related notes

- [[brain/projects/youtube-mcp/overview|Project overview]]
- [[brain/projects/youtube-mcp/playlist-confirmation-safety|Playlist confirmation safety]]
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and interface plan]]

# Open questions

- What exact duration thresholds does the approved SRS specify for each
  bucket? Use those values rather than choosing new ones.
- Which YouTube library sources may omit reliable event timestamps in
  practice, and how will the provider represent them?

## Sources

- `YT-MCP-SRS.pdf` v1.0, FR-04 and §6.3; locally supplied and ignored by Git.
- [[docs/architecture/Architecture_and_Interface_Plan|Architecture and Interface Plan]], `Library`, `EngagementReport`, and FR-04 contracts.
- Related pull requests: [#20](https://github.com/vicky150612/youtube-mcp-server/pull/20) and [#21](https://github.com/vicky150612/youtube-mcp-server/pull/21).
