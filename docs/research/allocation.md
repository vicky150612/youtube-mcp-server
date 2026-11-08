# Stage 1 research-note allocation

**Source:** The team allocation in the Stage 1 baseline (`STAGE_1_BASELINE.md`, located outside
this repository). The requested `Project Plan Division.txt` was not present in the workspace.
**Status:** Updated 2026-11-08. All assigned notes exist; contribution evidence is from Git
history and note metadata. Which Git account belongs to which Person is not recorded in the
repository, so authorship is stated per note, not per account.

Each member writes their own notes using the `brain-ingest` workflow. A file or PR is evidence of
a contribution, but does not by itself prove that a note passed the agreed ingestion/review
workflow. Research authorship is distinct from implementation ownership; see
[`docs/development-plan.md`](../development-plan.md).

| Owner | Assigned research notes | Current evidence |
|---|---|---|
| Person 1 | YouTube Data API overview; Video resource; Channel resource; Playlist resource (4) | Four notes added in PR #15 (commits `48e2cb9`, `d58951d`) as `draft-pending-brain-ingest`. On 2026-11-08 the video, channel and playlist notes were processed with `brain-ingest` (now `status: ingested`), and the overview note was merged into the shared YouTube Data API note with Person 1 credited (audit C5, D-1). |
| Person 2 | MCP architecture; MCP tools/resources; Agent Skills format (3) | The three notes plus a YouTube Data API note were added in PR #12 (commit `8e80f55`) and logged as Person 2's ingestion runs on 2026-11-07. Their `author`/`created` metadata was completed on 2026-11-08 from that commit's own log entries ("Contributor: Person 2", 2026-11-07); see `brain/log.md`. |
| Person 3 | OAuth authentication; YouTube quota management; metadata similarity (TF-IDF/cosine similarity) (3) | All three notes exist (PR #17, commit `a5caa34`) with `author: Person 3`, logged as ingestion runs on 2026-11-07. The OAuth note was extended on 2026-11-08 with installed-app findings (audit F-1). |

## Topic count

There are **11 distinct research topics** in `brain/resources/`: YouTube Data API overview,
video, channel and playlist resources, quota management, API errors, OAuth, TF-IDF/cosine
similarity, MCP architecture, MCP tools/resources and Agent Skills format. The errors note was
added on 2026-11-08 as `brain-ingest` evaluation case E1 by Git user `ChadDadChag`. Merging the
two overview notes removed a duplicate, not a topic. The AI-session and CI notes in
`brain/projects/` are not counted as research notes.

## Brain structure

The five PARA directories (`inbox`, `projects`, `areas`, `resources`, `archive`) are tracked;
the empty ones contain a `.gitkeep`, and the build check fails if any is missing.
Person 2 owns the vault navigation, log, note schema and `brain-ingest` conventions (ADR 0002).
