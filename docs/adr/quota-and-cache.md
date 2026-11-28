# Quota and public metadata cache

Status. Proposed for team review on 2026-11-28.

Atomically reserve each request against a Pacific-day SQLite ledger.
Maintain three counters and reject unknown costs before dispatch. Service
preflight uses the worst-case known workflow cost. The wrapper stores
public metadata in memory for up to 24 hours. Authenticated library
snapshots are never stored.

[[brain/resources/youtube-api/api-retention]]

[[brain/resources/youtube-api/quota-buckets]]
