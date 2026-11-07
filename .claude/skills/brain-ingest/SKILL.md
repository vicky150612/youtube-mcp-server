---
name: brain-ingest
description: Ingest research into the project Second Brain by creating sourced PARA notes, adding Obsidian links, and updating the index and activity log.
---

# Brain Ingest

## 1. Purpose

Convert research material into useful, structured and interconnected Markdown notes in the project's Obsidian Second Brain.

The goal is to transform raw information into reusable knowledge that all team members can understand and reference.

## 2. When to Use

Use this skill when:

- Adding research from official documentation, articles, papers or PDFs.
- Recording technical findings relevant to the YouTube MCP project.
- Turning supplied research material into reusable knowledge notes.
- Organising technical knowledge into the Second Brain.

## 3. Required Inputs

Obtain the following:

- Research material: URL, document, PDF or supplied text.
- Topic or subject.
- Project context, if available.
- Contributor name, if available.

If the source content is unavailable, ask the user to provide it.

Never pretend to have read a source.

## 4. Workflow

### Step 1: Inspect the Source

- Read the supplied research material.
- Identify its title, author or organisation, publication date if available, and source URL.
- Extract relevant facts, concepts, constraints and technical findings.
- Identify important technical terminology.
- Distinguish source-supported facts from your own interpretation.
- Never invent facts, quotations, dates or references.
- Prefer official and primary sources.

### Step 2: Identify Project Relevance

Explain how the research relates to the YouTube MCP project.

Identify relevant requirement IDs where applicable:

- FR: Functional Requirements.
- NFR: Non-Functional Requirements.
- SK: Skill Requirements.
- TQ: Testing Requirements.

Do not force a connection if the research is unrelated.

Explain whether the research:

- Helps implement a project feature.
- Explains an API or technical constraint.
- Helps with architecture or design.
- Supports security or testing.
- Provides general technical background.

### Step 3: Choose a PARA Destination

Choose the appropriate destination:

- `brain/inbox/`: Material awaiting review or classification.
- `brain/projects/`: Knowledge specific to the active YouTube MCP project.
- `brain/areas/`: Ongoing responsibilities and disciplines.
- `brain/resources/`: Reusable technical and research references.
- `brain/archive/`: Inactive or completed material.

Prefer `resources/` for reusable technical research and `projects/` for project-specific implementation knowledge.

### Step 4: Check for Duplicates

Before creating a note:

- Search for an existing note on the same subject.
- Check whether the information already exists.
- If a similar note exists, inform the user and propose updating it.
- Do not silently overwrite existing research.
- Preserve useful existing content.

### Step 5: Create the Research Note

Every research note must follow this structure:

    ---
    title: "Research Topic"
    type: research
    tags:
      - research
      - youtube-mcp
    source: "https://example.com"
    ---

    # Research Topic

    ## Overview

    Provide a brief explanation of the subject.

    Explain what the technology, concept or topic is and why it matters.

    ## Key Concepts

    Explain the important concepts.

    Include relevant technical terminology and definitions.

    ## Important Findings

    List the verified findings from the source.

    Include:
    - Important technical details.
    - Relevant API behaviour.
    - Limitations and constraints.
    - Important specifications.
    - Findings that may influence implementation.

    Do not include unsupported claims.

    ## Relevance to Our Project

    Explain how the findings affect our YouTube MCP project.

    Mention practical applications and potential implementation implications.

    ## Related Requirements

    Link relevant requirements where applicable.

    Examples:
    - [[FR-1]]
    - [[FR-2]]
    - [[NFR-1]]
    - [[NFR-2]]

    Only include genuinely relevant requirements.

    ## Sources

    For each source include:
    - Source title.
    - Organisation or author.
    - URL.
    - Access date.

    ## Related Notes

    Add relevant existing Obsidian wikilinks.

    Only link notes that actually exist or are being created as part of the same approved task.

### Step 6: Save the Note

- Save the note in the selected PARA folder.
- Use a clear, descriptive filename.
- Avoid duplicate filenames.
- Use Markdown formatting.
- Use valid Obsidian wikilinks.
- Ensure the note has the required metadata.
- Do not overwrite existing files without approval.

### Step 7: Update the Index

When a note is an important reusable reference:

- Open `brain/index.md`.
- Add its wikilink under the appropriate section.
- Place it under Resources, Projects or Areas as appropriate.
- Do not add duplicate links.
- Preserve the existing index structure.

Not every minor note needs to appear in the main index.

### Step 8: Update the Activity Log

Append an entry to `brain/log.md`.

Each entry must contain:

- Actual date of the operation.
- Research topic.
- Source used.
- Note created or updated.
- Destination path.
- Contributor, if known.
- Result and any issues.

Example:

    ## YYYY-MM-DD

    ### Activity: Research Ingestion

    **Topic:** YouTube Data API v3

    **Source:** Official Google documentation

    **Note Created:** [[YouTube Data API]]

    **Destination:** brain/resources/

    **Contributor:** Person 2

    **Result:** Successfully created and linked research note.

Never claim a note was created or updated unless the file operation succeeded.

### Step 9: Report the Result

After ingestion, report:

1. What was researched.
2. Which note was created or updated.
3. Where the note was saved.
4. Which requirements it references.
5. Which related notes it links to.
6. Whether index.md was updated.
7. Whether log.md was updated.
8. Any unresolved questions or problems.

## 5. Quality Rules

- Never fabricate research findings or sources.
- Prefer official and primary sources.
- Write concise, understandable explanations in your own words.
- Preserve important technical terminology.
- Distinguish facts, interpretations and recommendations.
- Use valid Obsidian wikilinks.
- Never silently delete or overwrite notes.
- Do not include secrets, credentials or personal user data.
- Include source URLs for factual research.
- Ensure notes are useful to all three project members.
- Avoid unnecessary repetition.
- Maintain consistent formatting across the Second Brain.

## 6. Error Handling

If a source cannot be accessed:

- Inform the user.
- Ask for the source content or an alternative source.
- Do not create a note containing invented findings.

If the destination folder does not exist:

- Inform the user.
- Ask for permission before creating missing folders if necessary.

If a note already exists:

- Do not overwrite it.
- Offer to update or merge the existing note.

If a wikilink points to a missing note:

- Check whether the target note is planned or genuinely missing.
- Avoid creating misleading links.

If the index or activity log cannot be updated:

- Report the failure.
- Do not claim the ingestion was completely successful.

## 7. Expected Outcome

A successful run produces:

1. A verified, structured Markdown research note.
2. A note saved in the correct PARA location.
3. Relevant Obsidian wikilinks.
4. An updated index when appropriate.
5. An updated activity log.
6. A concise completion report.

The final note must preserve the important knowledge from the original research and explain its relevance to the YouTube MCP project.
