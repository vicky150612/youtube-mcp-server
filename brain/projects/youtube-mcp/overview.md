---
title: YouTube MCP project overview
created: 2026-11-22
source: "YT-MCP-SRS.pdf v1.0; [[docs/architecture/Architecture_and_Interface_Plan]]"
requirements:
  - FR-01
  - FR-02
  - FR-03
  - FR-04
  - FR-05
  - NFR-10
issues: []
---

# YouTube MCP project overview

## Purpose

Build an MCP server for YouTube video and channel discovery, personalized
recommendations, engagement analysis, and playlist planning/creation using the
official YouTube Data API v3.

## Scope and key requirements

| Requirement | Scope |
| --- | --- |
| FR-01 | Find videos similar to a supplied video. |
| FR-02 | Find channels similar to a supplied channel. |
| FR-03 | Recommend videos using the user's YouTube library. |
| FR-04 | Analyse engagement across library data. |
| FR-05 | Propose and, after explicit user confirmation, create playlists. |
| NFR-10 | Keep ranking deterministic with stable tie-breaking. |

All YouTube API access must use the provider abstraction and the official API.
Playlist writes require explicit user confirmation, and quota safeguards must
not be bypassed. See
[[docs/architecture/Architecture_and_Interface_Plan|the architecture and interface plan]]
for the draft shared contracts.

## Status

The SRS v1.0 and supporting product/workflow briefs are available locally and
have been reviewed. The PDFs are excluded from Git by `.gitignore`; use the
team-approved copies when checking this overview. The architecture/interface
plan is available as a draft for team agreement.

## Sources and project references

- Source: `YT-MCP-SRS.pdf` v1.0 and
  [[docs/architecture/Architecture_and_Interface_Plan]].
- Supporting project/process sources: `Project_1_YouTube_MCP.pdf` and
  `SDLC_and_Workflow.pdf`.
- Related pull requests: [#20](https://github.com/vicky150612/youtube-mcp-server/pull/20)
  (architecture/interface plan) and [#21](https://github.com/vicky150612/youtube-mcp-server/pull/21)
  (common data models).
- No related issue number is recorded yet.
- [[brain/projects/youtube-mcp/stage-1|Stage 1 progress]]
