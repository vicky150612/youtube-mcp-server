---
title: Agent Skills format
created: 2026-11-22
source:
  - "Agent Skills Specification, https://agentskills.io/specification (checked 2026-11-22)"
  - "YT-MCP-SRS.pdf v1.0, §6.1"
requirements:
  - SK-00
  - SK-01
  - SK-02
  - SK-03
  - SK-04
  - SK-05
  - SB-03
issues: []
---

# Summary

An Agent Skill is a folder containing a `SKILL.md` with YAML frontmatter and
Markdown instructions. The YouTube MCP SRS adds project-specific skill names,
Brain-note references, and evaluation requirements.

# Key findings

## Source-grounded findings

- The format requires `name` and `description` frontmatter. `name` is
  1 to 64 lowercase letters, digits, or hyphens; it must match the parent
  directory and cannot start/end with a hyphen or contain consecutive
  hyphens. `description` is 1 to 1024 characters and explains purpose and when
  to use the skill.
- Optional directories include `scripts/`, `references/`, and `assets/`.
  File links in `SKILL.md` should be relative to the skill folder.
- The specification recommends concise instructions (under 500 lines and
  around 5,000 tokens) and progressive disclosure for additional references.
  It identifies `skills-ref validate` as a reference validator, not a
  requirement to adopt that command.
- The SRS names five skills: `brain-ingest`, `brain-refine`, `brain-query`,
  `local-check`, and `video-to-playlist`. It requires skill evaluations before
  each stage submission, references to Brain notes, and no bypass of quota or
  confirmation safeguards.

## Interpretation for YouTube MCP

Treat Agent Skills format rules as the portable file contract; treat the SRS
skill list and evaluation rules as additional project requirements. Keep each
skill focused and link deeper guidance instead of copying large references
into every `SKILL.md`.

# Relevance to YouTube MCP

These conventions apply to all five planned skills. This note supports writing
and validating skills such as [[skills/brain-ingest/SKILL|brain-ingest]] and
helps keep their folder names, metadata, references, and reviews consistent.

# Decisions or implications

- Match each directory and frontmatter `name` exactly, using the required
  lowercase kebab-case form.
- Include a useful description that says both what the skill does and when it
  should activate.
- Keep project-required Brain note links and evaluation evidence, even though
  they are additional to the generic file format.
- Confirm with the team before adopting any validator as a canonical
  development command.

# Related notes

- [[brain/index|Second Brain index]]
- [[brain/resources/mcp/mcp-tools-and-elicitation|MCP tools and elicitation]]
- [[skills/brain-ingest/SKILL|brain-ingest skill]]

# Open questions

- Which Agent Skills validator and evaluation workflow will the team adopt?
- How will dated skill evaluations be stored for each stage?

## Sources

- [Agent Skills Specification](https://agentskills.io/specification), checked 2026-11-22.
- `YT-MCP-SRS.pdf` v1.0, §6.1; locally supplied and ignored by Git.
- Related implementation: [PR #24](https://github.com/vicky150612/youtube-mcp-server/pull/24).
