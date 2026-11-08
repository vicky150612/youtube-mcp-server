# Second Brain Activity Log

This file records all brain-ingest runs,
note creation and maintenance activities.

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
- [[FR-1]]–[[FR-5]] are unresolved references; requirement definitions do not yet exist in the Second Brain.
- Related notes [[YouTube MCP Server]], [[YouTube API Quota Management]] and [[OAuth Authentication]] are planned but not yet created.
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
- Related notes [[MCP-Tools-and-Resources|MCP Tools and Resources]], [[YouTube MCP Server]] and [[OAuth Authentication]] are planned but not yet created.
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
- Related notes [[YouTube MCP Server]] and [[OAuth Authentication]] are planned but not yet created.
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
- Related note [[YouTube MCP Server]] is planned but not yet created.
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
# Act

- 2026-11-06: Implemented and locally verified the CI pipeline; see [[CI-Pipeline|CI Pipeline]].
