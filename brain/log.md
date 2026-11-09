# Second Brain Activity Log

This file records all brain-ingest runs, note creation and maintenance activities, in
chronological order.

Conventions: wikilinks use note filenames as targets (ADR 0003). On 2026-11-08 the links in
earlier entries were normalised to the current filenames or to plain text for notes that do not
exist; quoted historical link syntax is kept in code formatting. The wording of earlier entries
is otherwise unchanged. Entries marked "recorded retrospectively" were reconstructed from Git
history because the activity was not logged when it happened.

---

## 2026-11-05

### Activity: Initial Vault Setup

**Contributor:** Person 2

**Actions performed:**
- Created Obsidian vault.
- Created PARA directory structure.
- Created index.md.
- Created log.md.

**Status:** Completed

**Next steps:**
- Create brain-ingest skill.
- Ingest research notes.
- Verify wikilinks and note structure.

---

## 2026-11-06

### Activity: CI Pipeline

- Implemented and locally verified the CI pipeline; see [[CI-Pipeline|CI Pipeline]].

(This entry was previously appended at the end of the log under a stray `# Act` heading; it was
moved here into date order on 2026-11-08. The contributor was not recorded in the original
entry; the note was committed in `cedd5a0`, merged in PR #11.)

---

## 2026-11-07

### Activity 1: Research Ingestion — YouTube Data API v3

**Topic:** YouTube Data API v3 — Overview

**Source:** YouTube Data API Overview, Google for Developers — https://developers.google.com/youtube/v3/getting-started (accessed 2026-11-07)

**Note Created:** [[YouTube-Data-API|YouTube Data API]]

**Destination:** brain/resources/YouTube-Data-API.md

**Contributor:** Person 2

**Index:** Updated the existing Resources link from `[[YouTube Data API]]` to `[[YouTube-Data-API|YouTube Data API]]` so it resolves to the new file (note also carries the alias "YouTube Data API").

**Result:** Successfully created and linked research note.

**Open issues:**
- `[[FR-1]]`–`[[FR-5]]` were unresolved references; requirement definitions did not exist in the Second Brain. (Requirements are now referenced as `FR-01`…`FR-05`, defined in the SRS.)
- Related notes "YouTube MCP Server" (still planned), [[YouTube-API-Quota-Management|YouTube API Quota Management]] and [[OAuth-Authentication|OAuth 2.0 Authentication]] were planned but not yet created at the time; the latter two were created later the same day (Activities 5 and 6).
- To verify: whether ETag-based 304 responses still consume quota (not stated in the source).

### Activity 2: Research Ingestion — MCP Architecture

**Topic:** Model Context Protocol (MCP) — Architecture (protocol version `2026-07-28`)

**Source:** Architecture overview, Model Context Protocol

https://modelcontextprotocol.io/docs/learn/architecture

(accessed 2026-11-07)

**Note Created:** [[MCP-Architecture|MCP Architecture]]

**Destination:** brain/resources/MCP-Architecture.md

**Contributor:** Person 2

**Index:** Updated the existing Resources link from `[[MCP Architecture]]` to `[[MCP-Architecture|MCP Architecture]]` (note also carries the alias "MCP Architecture").

**Result:** Successfully created and linked research note.

**Open issues:**
- No requirement IDs assigned yet; requirement definitions do not exist in the repository.
- Related notes [[MCP-Tools-and-Resources|MCP Tools and Resources]], "YouTube MCP Server" (still planned) and "OAuth Authentication" (created later the same day as [[OAuth-Authentication|OAuth 2.0 Authentication]]) were planned but not yet created.
- The note documents the stateless discovery model of protocol version `2026-07-28`; earlier protocol versions are not covered.
- Transport (stdio vs Streamable HTTP) and SDK choice are not yet decided.

### Activity 3: Research Ingestion — MCP Tools and Resources

**Topic:** MCP Tools and Resources (protocol version `2026-07-28`, inferred)

**Sources:**

Understanding MCP servers, Model Context Protocol

https://modelcontextprotocol.io/docs/learn/server-concepts

Understanding MCP clients, Model Context Protocol

https://modelcontextprotocol.io/docs/learn/client-concepts

(both accessed 2026-11-07)

**Note Created:** [[MCP-Tools-and-Resources|MCP Tools and Resources]]

**Destination:** brain/resources/MCP-Tools-and-Resources.md

**Contributor:** Person 2

**Index:** Updated the existing Resources link from `[[MCP Tools and Resources]]` to `[[MCP-Tools-and-Resources|MCP Tools and Resources]]` (note also carries the alias "MCP Tools and Resources").

**Note Updated:** [[MCP-Architecture|MCP Architecture]] — replaced its planned `[[MCP Tools and Resources]]` link with the actual link to the new note.

**Result:** Successfully created and linked research note.

**Open issues:**
- No requirement IDs assigned yet; requirement definitions do not exist in the repository.
- Related notes "YouTube MCP Server" (still planned) and "OAuth Authentication" (created later the same day) were planned but not yet created.
- Protocol version `2026-07-28` is inferred from linked specification pages; neither source page declares it explicitly.
- Not covered by the sources: exact `resources/list` / `resources/read` response formats, tool annotations, tool output schemas, and the parameter-completion method name.

### Activity 4: Research Ingestion — Agent Skills Format

**Topic:** Agent Skills format and specification

**Source:** Specification, Agent Skills

https://agentskills.io/specification

(accessed 2026-11-07)

**Note Created:** [[Agent-Skills-Format|Agent Skills Format]]

**Destination:** brain/resources/Agent-Skills-Format.md

**Contributor:** Person 2

**Index:** Updated the existing Resources link from `[[Agent Skills Format]]` to `[[Agent-Skills-Format|Agent Skills Format]]` (note also carries the alias "Agent Skills Format").

**Result:** Successfully created and linked research note.

**Open issues:**
- No requirement IDs assigned yet; requirement definitions do not exist in the repository.
- Related note "YouTube MCP Server" was planned but not yet created (still planned).
- The specification page states no version or publication date.
- `.claude/skills/brain-ingest/SKILL.md` was checked manually against the spec but not with `skills-ref validate`.

### Activity 5: Research Ingestion — OAuth 2.0 Authentication

**Topic:** OAuth 2.0 user authorization and token lifecycle for Google APIs

**Sources:** Google Identity OAuth 2.0 overview and Google server-side web application guide (accessed 2026-11-07).

**Note Created:** [[OAuth-Authentication|OAuth 2.0 Authentication]]

**Destination:** brain/resources/OAuth-Authentication.md

**Contributor:** Person 3

**Index:** Replaced the planned OAuth resource link with the created note.

**Result:** Created a research note covering authorization-code flow, scopes, access/refresh tokens, secure storage, and the project's re-authorisation requirement. The exact OAuth client type, scopes and storage design remain open.

### Activity 6: Research Ingestion — YouTube API Quota Management

**Topic:** YouTube Data API quota costs, limits, caching and pre-checks

**Sources:** YouTube Data API quota-cost and errors documentation (accessed 2026-11-07).

**Note Created:** [[YouTube-API-Quota-Management|YouTube API Quota Management]]

**Destination:** brain/resources/YouTube-API-Quota-Management.md

**Contributor:** Person 3

**Index:** Replaced the planned quota resource link with the created note.

**Result:** Created a research note distinguishing the general daily unit pool from method-specific buckets, documenting common costs and `quotaExceeded`, and separating documented facts from project recommendations.

### Activity 7: Research Ingestion — TF-IDF and Cosine Similarity

**Topic:** Text vectorization, TF-IDF weighting and cosine similarity

**Sources:** scikit-learn feature-extraction and cosine-similarity documentation (accessed 2026-11-07).

**Note Created:** [[TF-IDF-and-Cosine-Similarity|TF-IDF and Cosine Similarity]]

**Destination:** brain/resources/TF-IDF-and-Cosine-Similarity.md

**Contributor:** Person 3

**Index:** Replaced the planned video-similarity resource link with the created note.

**Result:** Created a research note explaining vectorization, TF/IDF, cosine similarity, metadata-based use, and limitations. The ranking method and feature weighting remain open.

### Activity 8: Draft research notes and AI-session note added (recorded retrospectively)

**Recorded:** 2026-11-08, from Git history (commits `48e2cb9`, `0a9fe9a` and `d58951d` of
2026-11-07, merged in PR #15).

**Notes added:** four YouTube API notes by Person 1 (`YouTube Data API Overview.md`,
`YouTube Channel Resource.md`, `YouTube Playlist Resource.md`, `YouTube Video Resource.md`) with
`status: draft-pending-brain-ingest`, and the AI-session note
[[ai-session-2026-11-07-srs-drafting|AI session — SRS drafting and API research]] (Person 1).

**Result:** The notes were added as drafts and were not run through `brain-ingest` or added to
the index at the time. Their ingestion is recorded under 2026-11-08.

---

## 2026-11-08

All activities below were carried out in one AI-assisted session (Claude Code) run by Git user
`ChadDadChag` for the Stage 1 repository audit; see
[[ai-session-2026-11-08-stage-1-audit|AI session — Stage 1 repository audit]]. The original
authors' attribution in each note is unchanged.

### Activity 1: Renames and link normalisation (audit I-8, C2)

- Renamed `CI Pipeline.md`, `YouTube Channel Resource.md`, `YouTube Playlist Resource.md` and
  `YouTube Video Resource.md` to hyphenated filenames and updated every reference.
- Fixed the 33 broken wikilinks reported by the audit: planned-note links became plain text,
  links that relied on aliases now target filenames, and requirement wikilinks became canonical
  IDs. Five links that were already in code formatting are now treated as literal text by the
  validator.

### Activity 2: Schema migration (audit C1, ADR 0002)

- Migrated every note to the canonical schema: `source` became a `sources` list, duplicate
  `source` and `protocol_version` keys were removed (the protocol version is stated in each
  note body), `author` became a list, and `tags` were added to the CI Pipeline note.
- **Not done:** `author` and `created` were not added to
  [[Agent-Skills-Format|Agent Skills Format]], [[MCP-Architecture|MCP Architecture]],
  [[MCP-Tools-and-Resources|MCP Tools and Resources]] and [[CI-Pipeline|CI Pipeline]], because
  their contributors have not confirmed the values. These notes fail validation until they do.

### Activity 3: Research Ingestion — Person 1's resource notes (audit C5)

**Sources:** the Google pages cited in each note, re-read on 2026-11-08
(`channels.list`, channels resource, videos resource, `videos.list`, `playlistItems` resource,
`playlists.insert`, `playlistItems.insert`, ratings guide, quota costs, getting started).

**Notes updated:** [[YouTube-Channel-Resource|YouTube Channel Resource]],
[[YouTube-Playlist-Resource|YouTube Playlist Resource]],
[[YouTube-Video-Resource|YouTube Video Resource]] (`brain/resources/`).

**Contributor:** Person 1 (author, unchanged); processed by `ChadDadChag`, AI-assisted.

**Result:** Processed with the `brain-ingest` workflow and set to `status: ingested`.
Corrections from source verification: full `channels.list` part list; `forHandle` accepts an
optional `@`; `tags` has a 500-character combined limit (not documented as optional);
`dislikeCount` is the only private statistic; `topicIds` is deprecated; `videos.list` with
`myRating=like` is capped at 1000 videos; `youtubeSignupRequired` is documented in the global
errors reference, not on `playlists.insert`; the likes-playlist route is documented but not yet
tested. "Planned (other members)" lines were replaced with links to the notes that now exist.

### Activity 4: Duplicate merge — YouTube Data API overview (audit D-1)

**Notes:** `YouTube Data API Overview.md` (Person 1) merged into
[[YouTube-Data-API|YouTube Data API]] (Person 2); the redundant file was removed after all links
were migrated. Both contributors are credited in `author` and in a Contributors section.
Default-allocation figures were replaced by a link to SRS Appendix A (ADR 0006).

**Attribution to confirm:** Person 2's authorship and the 2026-11-07 creation date in the merged
note are taken from Activity 1 of 2026-11-07 above and need Person 2's confirmation.

### Activity 5: Research update — OAuth installed-app flow and scopes (audit F-1)

**Sources:** Google's installed-app OAuth guide, OAuth 2.0 overview and scope list (accessed
2026-11-08).

**Note updated:** [[OAuth-Authentication|OAuth 2.0 Authentication]] (Person 3, author unchanged).

**Result:** Added verified findings on desktop clients, loopback redirect, PKCE, refresh-token
expiry reasons and YouTube scopes; the proposed project choice is ADR 0008.

### Activity 6: Research Ingestion — YouTube Data API errors (skill evaluation E1)

**Sources:** YouTube Data API — Errors — https://developers.google.com/youtube/v3/docs/errors
(accessed 2026-11-08), plus the `playlistItems.list`, `playlistItems.insert`, `playlists.insert`
and `channels.list` reference pages.

**Note created:** [[YouTube-API-Errors|YouTube Data API Errors]]
(`brain/resources/YouTube-API-Errors.md`)

**Contributor:** `ChadDadChag` (team role not recorded); AI-assisted: yes

**Result:** Created with the `brain-ingest` workflow as evaluation case E1
(`docs/testing/skill-evaluations.md`); duplicate check found no existing note covering the error
catalogue; added to the index; validated. Not stated in the source: a global rate-limit error
and the JSON error format.

### Activity 7: Duplicate check — YouTube Data API getting-started page (skill evaluation E2)

**Source:** https://developers.google.com/youtube/v3/getting-started (accessed 2026-11-08)

**Result:** No note created. The duplicate check found [[YouTube-Data-API|YouTube Data API]],
which already covers the page and was re-verified today (Activity 4), so the correct outcome was
to reuse the existing note.

### Activity 8: Contributor metadata completed from Git evidence (audit C1)

**Notes updated:** [[Agent-Skills-Format|Agent Skills Format]],
[[MCP-Architecture|MCP Architecture]], [[MCP-Tools-and-Resources|MCP Tools and Resources]] and
[[CI-Pipeline|CI Pipeline]]; this completes the item left open in Activity 2.

**Evidence:**
- The three research notes were created in commit `8e80f55` (2026-11-07). The same commit added
  their ingestion entries to this log under 2026-11-07 with "**Contributor:** Person 2"
  (2026-11-07 Activities 2–4). Recorded: `author: [Person 2]`, `created: 2026-11-07`. The same
  evidence supports Person 2's credit and date in the merged
  [[YouTube-Data-API|YouTube Data API]] note (2026-11-07 Activity 1).
- `CI-Pipeline.md` was created in commit `cedd5a0` (2026-11-07) by the Git identity that also
  committed `a5caa34`, "brain: add research notes (Person 3)", whose notes carry
  `author: Person 3`; the development plan assigns CI to Person 3. Recorded:
  `author: [Person 3]`, `created: 2026-11-07` (the date the note first appears in Git). The
  log line written in the same commit dates the CI work itself to 2026-11-06; Person 3 may
  correct `created` to that date.

**Result:** Brain validation passes with no errors.

---

## 2026-11-09

### Activity 1: Contributor role confirmed

**Notes updated:** [[YouTube-API-Errors|YouTube Data API Errors]] and
[[ai-session-2026-11-08-stage-1-audit|AI session — Stage 1 repository audit]].

**Contributor:** Person 2 (Git user `ChadDadChag`), who confirmed their team role on 2026-11-09.

**Result:** `author` changed from the Git username `ChadDadChag` to `Person 2` on both notes, as
ADR 0002 prescribes once a role is confirmed. Content, sources and `created` dates are unchanged.
Earlier entries that name `ChadDadChag` are kept as they were written.

