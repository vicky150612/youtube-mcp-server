# Project Guidelines

## General
- The SRS is the source of truth.
- Do not implement features outside the approved requirements without team agreement.
- Keep the implementation simple and modular.
- All YouTube API access must go through the provider abstraction.
- Use the official YouTube Data API v3 only.
- Do not scrape YouTube or use unofficial APIs.

## Security
- Never commit API credentials, OAuth secrets, or tokens.
- Use the minimum required OAuth scopes.
- Playlist creation must require explicit user confirmation.
- Never bypass quota checks or confirmation safeguards.

## Development
- Use Python 3.12.
- Write tests for implemented functionality.
- Prefer fixture-based tests over live API calls.
- Keep pull requests small and reviewable.
- Do not merge unreviewed AI-generated code.

## Git
- Do not commit directly to main.
- Use feature branches and pull requests.
- Every team member must contribute visible commits.