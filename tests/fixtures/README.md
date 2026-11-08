# Test fixtures

This directory holds recorded or synthetic data used by automated tests. It contains no
fixtures yet.

## Rules

- **Synthetic or anonymised data only.** Fixtures must not contain real users' personal data,
  including names, email addresses, channel or account identifiers that belong to real
  people, liked videos, subscriptions, playlists or other library data (SRS NFR-05.2).
- **No credentials.** Never store API keys, OAuth client secrets, access tokens, refresh
  tokens, service-account files or other secrets here (SRS NFR-05.1). CI secret scanning
  (Gitleaks) checks every change.
- **No live-account responses committed as-is.** A response recorded from the live YouTube
  Data API must have personal and account data removed or replaced before it is committed,
  and it must be reviewed in the pull request that adds it.
- **Deterministic.** Ordinary CI uses these fixtures or mocks and never calls the live YouTube
  API (TQ-05). Fixtures must not depend on the current date, network access or a developer's
  account.
- **Treat fixture content as untrusted metadata.** Prompt-injection fixtures (for example,
  instruction-like text in a video title) are expected and must be clearly labelled as such.

See the [testing strategy](../../docs/testing/README.md) and [`AGENTS.md`](../../AGENTS.md)
sections 5 and 8.
