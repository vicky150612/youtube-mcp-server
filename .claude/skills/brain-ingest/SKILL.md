---
name: brain-ingest
description: Ingest research into the project Second Brain as a sourced, schema-valid PARA note with Obsidian links, index and log updates, validation and a pull request. Use when adding research from official documentation, articles, papers or supplied text to brain/, or when processing an existing draft note into the Brain.
---

# Brain Ingest

## 1. Purpose

Convert research material into structured, verified and interconnected Markdown notes in the
project's Obsidian Second Brain (`brain/`), so that all three team members can reuse the
knowledge and cite it from ADRs and skills (`SB-01`, `SB-03`).

The note format follows the canonical schema in
[ADR 0002](../../../docs/adr/0002-brain-note-schema.md); links and requirement references
follow [ADR 0003](../../../docs/adr/0003-linking-naming-and-requirement-references.md). The
Agent Skills conventions this skill follows are summarised in the Brain note
[Agent Skills Format](../../../brain/resources/Agent-Skills-Format.md).

## 2. When to Use

- Adding research from official documentation, articles, papers or PDFs.
- Recording technical findings relevant to the YouTube MCP project.
- Processing an existing note with `status: draft` into the Brain.
- Updating an existing note with new, verified findings.

Do not use it for requirement changes (edit `docs/srs.md` through a PR), for ADRs
(`docs/adr/`) or for stage reviews (`docs/stage-reviews/`).

## 3. Required Inputs

- **Research material:** a URL, document, PDF or supplied text. If the content is not
  available to you, ask for it. Never pretend to have read a source.
- **Topic.**
- **Contributor:** the team role (for example `Person 2`) of the person the note is written
  for. If the role is unknown, ask; if it cannot be confirmed, use the contributor's Git
  username. Never invent a contributor.
- **Project context**, if available.

## 4. Workflow

### Step 1: Inspect and verify the source

- Read the supplied material in full. Record its title, organisation or author, URL, the
  access date and any "last updated" date the page actually shows.
- Prefer official and primary sources. Quote numbers, limits and error names exactly.
- Separate what the source states from your interpretation. If a fact you expected is not in
  the source, write "not stated in the source" instead of filling the gap.
- Never invent facts, quotations, dates or references.

### Step 2: Identify project relevance

Explain how the research relates to the project and list only genuinely relevant
requirements, using canonical zero-padded IDs in backticks, for example `FR-01`, `NFR-02.2`,
`SK-05`, `TQ-04`. Requirements are defined in the SRS and are never wikilinked.

### Step 3: Check for duplicates and existing notes

- Search `brain/` for notes on the same topic (filenames, titles, `aliases`, headings).
- If a note already covers the topic, **update or merge** it instead of creating a new one.
  Keep all existing correct content and add every contributor to `author`.
- Never overwrite or delete a note without the owner's approval.

### Step 4: Choose a PARA destination

- `brain/resources/`: reusable technical and research references (default for research).
- `brain/projects/`: knowledge specific to the active project, including `ai-session` notes.
- `brain/areas/`: ongoing responsibilities and disciplines.
- `brain/inbox/`: material awaiting classification.
- `brain/archive/`: inactive or completed material.

### Step 5: Write the note from the template

Copy [the note template](assets/research-note.tmpl) and fill every `{{placeholder}}`. The
frontmatter must contain exactly the schema fields:

```yaml
title: "YouTube Video Resource"
type: research            # research | ai-session
author:
  - "Person 1"            # role names; list every contributor
created: "2026-11-07"     # date the note was first created; never guessed
tags:
  - research
sources:                  # http(s) URLs or repository-relative paths that exist
  - "https://developers.google.com/youtube/v3/docs/videos"
aliases:                  # optional; display names only
  - "Video resource"
status: ingested          # optional: draft | ingested
```

- Filename: hyphen-separated words, for example `YouTube-Video-Resource.md`; AI-session notes
  use `ai-session-YYYY-MM-DD-topic.md`.
- Link existing notes with the filename as the target and the title as display text, for
  example `[[OAuth-Authentication|OAuth 2.0 Authentication]]`. Do not link planned notes;
  list them as plain text marked "(planned)".
- Link repository documents outside the Brain with relative Markdown links, for example
  `[SRS](../../docs/srs.md)`.
- When updating a note, keep its original `created` date and existing `author` entries.

### Step 6: Update the index

Add the note to `brain/index.md` under the matching section, with a short description, unless
an entry already exists.

### Step 7: Append to the activity log

Append an entry to `brain/log.md` under the actual date of the operation (keep the log in
chronological order):

```markdown
### Activity: Research Ingestion — <topic>

**Sources:** <title> — <URL> (accessed YYYY-MM-DD)

**Note created or updated:** [[File-Name|Title]] (`brain/resources/File-Name.md`)

**Contributor:** <role or Git username>; AI-assisted: yes/no

**Result:** <what was done, including anything not verified>
```

Never claim that a note, index or log was updated unless the file operation succeeded.

### Step 8: Validate

Run, from the repository root:

```text
python scripts/validate_brain.py
python scripts/validate_docs.py
```

Fix every reported error in the files you changed. Do not weaken a validator to make a note
pass. If an error concerns metadata only the contributor can confirm, report it instead of
guessing.

### Step 9: Submit through a pull request

Brain changes, including AI-generated ones, go through a pull request with at least one human
review (`SB-05`, `AIP-01`). Commit with the contributor's own Git identity so the contribution
is visible in history (`SB-06`), mention AI assistance in the PR, and link related issues and
requirement IDs.

### Step 10: Report the result

Report what was researched, the note created or updated and its path, the requirements and
notes it links to, whether the index and log were updated, the validation result, and any
unresolved questions.

## 5. Outputs (Expected Outcome)

1. A verified note in the correct PARA folder that passes `validate_brain.py`.
2. Correct wikilinks to existing notes and a relative link to the SRS.
3. An updated `brain/index.md` and a chronological `brain/log.md` entry.
4. A pull request ready for human review, and a short completion report.

## 6. Quality Rules

- Never fabricate findings, sources, dates or contributors.
- Write concise explanations in your own words; keep important terminology.
- Distinguish facts, interpretations and recommendations.
- Do not include secrets, credentials or personal user data.
- Avoid repeating content that another note already covers; link to it instead. Exact quota
  figures live in SRS Appendix A ([ADR 0006](../../../docs/adr/0006-quota-reference-and-accounting.md)).

## 7. Error Handling

- **Source unavailable:** say so, ask for the content or an alternative source, and create no
  note with invented findings.
- **Destination folder missing:** report it; the five PARA folders are required by the
  repository build check.
- **Note already exists:** update or merge (Step 3); never overwrite silently.
- **Link target missing:** check whether the note is planned; write it as plain text instead
  of creating a broken link.
- **Validation fails:** fix the note, or report the remaining error if only the contributor
  can resolve it.
- **Index or log cannot be updated:** report that the ingestion is incomplete.

## 8. Limitations

- The skill works only on material that is supplied or that the agent can actually read; it
  cannot verify paywalled or unavailable sources.
- It does not decide requirements or architecture; findings become decisions only through the
  SRS and ADR processes.
- Summaries are only as good as the source verification step; a human reviewer must check them
  in the pull request.
- The skill format has been checked by `scripts/validate_skills.py`, not by the external
  `skills-ref` tool.
