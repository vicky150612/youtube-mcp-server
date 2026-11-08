## Description

What changed and why.

## Related issue and requirements

Closes #

Requirement IDs (canonical form, for example `FR-01`, `NFR-02.2`, `SK-01`):

## Changes made

-

## Testing performed

List the commands you ran and their results (pass/fail). Do not tick a box for a check you
did not run.

- [ ] `python -m unittest discover -s tests -v`
- [ ] `ruff check scripts tests` and `ruff format --check scripts tests`
- [ ] Validators for changed areas (`validate_skills.py --require brain-ingest`,
      `validate_brain.py`, `validate_docs.py`)
- [ ] Other (integration, manual, live test with an approved budget):

## Documentation and Second Brain

- [ ] Documentation updated (SRS, ADR, architecture, traceability, `AGENTS.md`), or not
      applicable
- [ ] Brain notes added or updated with `brain-ingest`, index and log updated, or not
      applicable

## Interfaces and compatibility

- [ ] No change to shared interfaces (`docs/api/interfaces.md`), CI job names or file
      locations, **or** the change is described here and the affected owners are reviewers

## Security and data

- [ ] No API keys, client secrets, tokens or credential files are included
- [ ] No real personal data in code, fixtures, logs or notes
- [ ] Gitleaks passes

## AI assistance

- [ ] No AI assistance, **or** AI-assisted: tool used, and a human has reviewed every changed
      line (`AIP-01`); significant sessions are recorded as `ai-session` notes (`AIP-03`)

## Known limitations and follow-up work

## Reviewer notes
