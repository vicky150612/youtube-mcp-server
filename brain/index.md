# YouTube MCP — Second Brain

## Project Overview

This Second Brain contains the research, technical knowledge, design decisions and development
notes for our YouTube Video Intelligence MCP Server. The vault root is `brain/`. Notes follow
the schema in ADR 0002 and the linking rules in ADR 0003; new notes are added with the
`brain-ingest` skill.

## PARA Navigation

### Projects

AI-session and project-specific notes (`brain/projects/`):

- [[ai-session-2026-11-07-srs-drafting|AI session — SRS drafting and API research]] (Person 1)
- [[ai-session-2026-11-08-stage-1-audit|AI session — Stage 1 repository audit]]
- [[CI-Pipeline|CI Pipeline]] — implementation record of the six-job CI pipeline and validators

Planned, not yet created: a YouTube MCP Server project overview note.

### Areas

No area notes yet (`brain/areas/`).

### Resources

Reusable research (`brain/resources/`):

| Note | Topic | Contributor |
|---|---|---|
| [[YouTube-Data-API\|YouTube Data API]] | API overview, resources, methods, quota principles | Person 2, Person 1 |
| [[YouTube-Video-Resource\|YouTube Video Resource]] | Video metadata, duration, liked videos | Person 1 |
| [[YouTube-Channel-Resource\|YouTube Channel Resource]] | Channel lookup and similarity features | Person 1 |
| [[YouTube-Playlist-Resource\|YouTube Playlist Resource]] | Playlist writes, likes playlist, errors | Person 1 |
| [[YouTube-API-Quota-Management\|YouTube API Quota Management]] | Quota buckets, costs, pre-checks | Person 3 |
| [[OAuth-Authentication\|OAuth 2.0 Authentication]] | OAuth flows, installed apps, scopes, tokens | Person 3 |
| [[TF-IDF-and-Cosine-Similarity\|TF-IDF and Cosine Similarity]] | Explainable text similarity | Person 3 |
| [[MCP-Architecture\|MCP Architecture]] | MCP participants, transports, discovery | Person 2 |
| [[MCP-Tools-and-Resources\|MCP Tools and Resources]] | Tools, resources, elicitation | Person 2 |
| [[Agent-Skills-Format\|Agent Skills Format]] | Agent Skills specification | Person 2 |

### Inbox

Unprocessed research and incoming information (`brain/inbox/`). Empty.

### Archive

Completed or inactive notes (`brain/archive/`). Empty.

## Project Documentation

These documents live outside the vault; open them in the repository or on GitHub:

- [Software Requirements Specification](../docs/srs.md), including the
  [open-decision register](../docs/srs.md#9-open-decisions-od)
- [Architecture Decision Records](../docs/adr/README.md)
- [Architecture overview](../docs/architecture/overview.md)
- [Requirement traceability](../docs/traceability.md)
- [Stage reviews](../docs/stage-reviews/README.md)
- [Testing strategy](../docs/testing/README.md) and [skill evaluations](../docs/testing/skill-evaluations.md)

## Maintenance

- [[log|Activity log]]
