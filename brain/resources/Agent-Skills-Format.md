---
title: "Agent Skills Format and Specification"
type: research
aliases:
  - "Agent Skills Format"
tags:
  - research
  - youtube-mcp
  - agent-skills
source: "https://agentskills.io/specification"
---

# Agent Skills Format and Specification

> **Version:** the specification page does not state a version number or publication date.

## Overview

Agent Skills is an open format for packaging instructions (and optional scripts, references and assets) that AI agents can load to perform specific tasks. A skill is a directory containing, at minimum, a `SKILL.md` file made of YAML frontmatter followed by Markdown instructions.

It matters to us because our project uses skills (e.g. `.claude/skills/brain-ingest/SKILL.md`), and any skills we write should follow the specification so agents can discover and load them correctly.

## Key Concepts

- **Skill**: a directory containing, at minimum, a `SKILL.md` file.
- **`SKILL.md`**: the required file. YAML frontmatter (metadata) followed by Markdown content (instructions).
- **Frontmatter**: the YAML block at the top of `SKILL.md`. `name` and `description` are required.
- **Body content**: the Markdown instructions after the frontmatter.
- **Optional directories**: `scripts/` (executable code), `references/` (documentation), `assets/` (static resources).
- **Progressive disclosure**: agents load skill content in stages, pulling in more detail only as a task requires it.
- **Activation**: the point at which an agent decides to use a skill and loads its full `SKILL.md`.
- **`skills-ref`**: the reference library for validating skills.

## Important Findings

> This section reflects the **official Agent Skills specification**.

### Directory structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

- Only `SKILL.md` is required.
- A skill directory may contain any other files and directories. The `scripts/`, `references/` and `assets/` conventions are **recommendations**, not requirements.

### `SKILL.md` format

- `SKILL.md` **must** contain YAML frontmatter followed by Markdown content.

### Frontmatter fields

| Field           | Required | Constraints                                                                                             |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `name`          | **Yes**  | Max 64 characters. Lowercase letters, numbers and hyphens only. Must not start or end with a hyphen.    |
| `description`   | **Yes**  | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                       |
| `license`       | No       | License name or reference to a bundled license file.                                                    |
| `compatibility` | No       | Max 500 characters. Environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary map from string keys to string values.                                                        |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. **Experimental.**                       |

Minimal example:

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### `name` field

- Must be **1–64 characters**.
- May only contain lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`).
- Must **not start or end** with a hyphen.
- Must **not contain consecutive hyphens** (`--`).
- Must **match the parent directory name**.
- Valid: `pdf-processing`, `data-analysis`, `code-review`.
- Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive hyphens).

### `description` field

- Must be **1–1024 characters**.
- **Should** describe both **what the skill does** and **when to use it**.
- **Should** include specific keywords that help agents identify relevant tasks.
- Good example: "Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."
- Poor example: "Helps with PDFs."

### Optional fields

- **`license`**: the license applied to the skill. Recommended to keep it short (a license name or the name of a bundled license file).
- **`compatibility`**:
  - Must be 1–500 characters if provided.
  - Should only be included if the skill has specific environment requirements.
  - The spec notes that most skills do not need it.
  - Example: "Requires git, docker, jq, and access to the internet".
- **`metadata`**:
  - A map from string keys to string values.
  - Clients can use it to store properties not defined by the spec.
  - Key names should be reasonably unique to avoid conflicts.
- **`allowed-tools`**:
  - Space-separated string of pre-approved tools (e.g. `Bash(git:*) Bash(jq:*) Read`).
  - **Experimental**; support varies between agent implementations.

### Body content (instructions)

- The Markdown body contains the skill instructions. There are **no format restrictions**.
- Recommended sections:
  - Step-by-step instructions.
  - Examples of inputs and outputs.
  - Common edge cases.
- The agent loads the **entire file** once it decides to activate a skill, so longer content should be split into referenced files.

### Optional directories

**`scripts/`**: executable code agents can run. Scripts should:

- Be self-contained or clearly document dependencies.
- Include helpful error messages.
- Handle edge cases gracefully.
- Supported languages depend on the agent implementation (common options: Python, Bash, JavaScript).

**`references/`**: additional documentation agents read when needed:

- `REFERENCE.md`: detailed technical reference.
- `FORMS.md`: form templates or structured data formats.
- Domain-specific files (e.g. `finance.md`, `legal.md`).
- Keep individual reference files focused; agents load them on demand, so smaller files use less context.

**`assets/`**: static resources:

- Templates (document or configuration templates).
- Images (diagrams, examples).
- Data files (lookup tables, schemas).

### Progressive disclosure

| Stage           | What is loaded                                | When                        | Size guidance             |
| --------------- | --------------------------------------------- | --------------------------- | ------------------------- |
| 1. Metadata     | `name` and `description`                      | At startup, for all skills  | ~100 tokens               |
| 2. Instructions | Full `SKILL.md` body                          | When the skill is activated | < 5000 tokens recommended |
| 3. Resources    | Files in `scripts/`, `references/`, `assets/` | Only when required          | As needed                 |

- Keep the main `SKILL.md` **under 500 lines**.
- Move detailed reference material to separate files.

### File references

- Reference other files using **relative paths from the skill root** (e.g. `references/REFERENCE.md`, `scripts/extract.py`).
- Keep file references **one level deep** from `SKILL.md`. Avoid deeply nested reference chains.

### Validation

- The **`skills-ref`** reference library validates skills: `skills-ref validate ./my-skill`.
- It checks that `SKILL.md` frontmatter is valid and follows all naming conventions.

## Relevance to Our Project

> The points below are **our team's interpretation** and our own checks, not statements from the specification.

- **Our existing skill appears to conform.** A manual check of `.claude/skills/brain-ingest/SKILL.md` on 2026-11-07 found:
  - `name: brain-ingest` matches its parent directory and uses only lowercase letters and a single hyphen.
  - `description` is non-empty and well under 1024 characters, and states what the skill does.
  - The file is 286 lines, under the 500-line recommendation.
  - It has not been run through `skills-ref validate`; doing so would confirm conformance.
- **Description quality matters most for discovery.** Only `name` and `description` are loaded at startup, so the description is what lets an agent pick the skill. Our `brain-ingest` description says _what_ it does but has no explicit "Use when…" clause, which the spec recommends. Adding one is a possible improvement.
- **Keep instructions lean.** If `brain-ingest` grows (e.g. the research-note template or log format), moving that material into `references/` or `assets/` would follow the progressive-disclosure guidance.
- **Future project skills:** any additional skills (e.g. for working with the YouTube MCP server) should use the same structure, valid names that match their directory, and clear trigger-oriented descriptions.
- **Relationship to MCP:** Agent Skills (instructions loaded by an agent) and MCP Tools (functions exposed by a server) are separate mechanisms. The specification does not describe how they interact; any combination in our project would be a design decision. See [[MCP-Tools-and-Resources|MCP Tools and Resources]].
- **Portability caution:** `allowed-tools` is experimental and implementation-dependent, so we should not rely on it for consistent behaviour across agents.

## Related Requirements

None assigned yet.

## Sources

- **Specification** (Agent Skills format specification)
  - Organisation: Agent Skills (agentskills.io)
  - URL: https://agentskills.io/specification
  - Accessed: 2026-11-07
  - Note: no author, version or publication date was visible on the page.

## Related Notes

- [[MCP-Tools-and-Resources|MCP Tools and Resources]]
- [[MCP-Architecture|MCP Architecture]]
- [[YouTube MCP Server]] _(planned — not yet created)_
