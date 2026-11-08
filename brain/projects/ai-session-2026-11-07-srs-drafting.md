---
sources:
  - "docs/srs.md"
  - "docs/development-plan.md"
  - "brain/resources/YouTube-Channel-Resource.md"
  - "brain/resources/YouTube-Data-API.md"
  - "brain/resources/YouTube-Playlist-Resource.md"
  - "brain/resources/YouTube-Video-Resource.md"
title: AI session — SRS drafting and API research
tags:
  - ai-session
  - srs
  - youtube
type: ai-session
author:
  - Person 1
created: 2026-11-07
---

# AI session — SRS drafting and API research

## Goal
Draft the Stage 1 SRS (`docs/srs.md`), the traceability matrix and development plan from the two project PDFs and the Stage 1 baseline, and draft the four YouTube API research notes.

## Tool
Claude (chat). No secrets, tokens or credentials were shared (AIP-04).

## What worked
- Producing a complete first SRS with acceptance criteria quickly.
- Web research against Google's official documentation found that `search.list` now has its own 100-calls/day bucket, which changed `NFR-02.1`, `NFR-02.2` and `OD-09`.

## What failed or needed correction
- The first draft of Appendix A used outdated quota costs from memory (`search.list` at 100 units); this was corrected after reading the official quota page.
- AI-written research notes are **drafts**: they must be read, checked against the cited sources and re-run through `brain-ingest` so the contribution is genuinely ours (AIP-01, AIP-02).

## Human review
Reviewer: Person 2 (primary reviewer for Person 1). To be recorded in the PR.

## Related
`docs/srs.md`, `docs/traceability.md`, [[YouTube-Data-API|YouTube Data API]] (Person 1's overview note from this session was merged into it on 2026-11-08), [[YouTube-Video-Resource|YouTube Video Resource]], [[YouTube-Channel-Resource|YouTube Channel Resource]], [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
