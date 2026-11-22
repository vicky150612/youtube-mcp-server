# Architecture and Interface Agreement

**Status:** Draft for team agreement  
**Source:** SRS v1.0  
**Language:** Python 3.12  
**Models:** Frozen dataclasses  
**Interfaces:** `typing.Protocol`

This document defines the shared interfaces and architectural decisions that all three team members must follow. The SRS is the source of truth; changes to this agreement must be reviewed and recorded.

## Project Module Layout

This layout matches the initial repository setup. Do not create a second package named `ytmcp` or use singular `provider/`.

```text
src/youtube_mcp/
  __init__.py
  server.py
  errors.py       # AppError and subclasses (Section 5)
  clock.py        # Clock Protocol + SystemClock (Section 2)
  models/
    __init__.py
    video.py
    channel.py
    library.py
    playlist.py
    analysis.py
    quota.py
    auth.py
  providers/
    __init__.py
    base.py       # YouTubeProvider Protocol
    live.py       # official YouTube API implementation
    fixture.py    # fixture-backed implementation
    cached.py     # CachingProvider wrapper (24-hour public metadata cache)
  services/
    __init__.py
    similarity.py # SimilarityService + shared pure scoring functions
    recommendations.py
    analysis.py
    playlist.py
    validation.py
  auth/
    __init__.py
    oauth.py      # PKCE flow, incremental scopes, sign-out
    tokens.py     # OS credential store (fallback: user-only file)
  quota/
    __init__.py
    manager.py
    ledger.py
  cache/
    __init__.py
    store.py      # TTL key/value store used by providers/cached.py
  mcp/
    __init__.py
    tools.py
    schemas.py

tests/
  unit/
  integration/
  e2e/
  fixtures/       # synthetic JSON only

skills/
brain/
docs/
```

**Rule:** Only `providers/live.py` (and `auth/`, for the OAuth flow) communicates with Google/YouTube. Services receive internal models and never process raw API JSON.

## 1. Common Data Models

Models are defined under `src/youtube_mcp/models/`. Use frozen dataclasses. Unknown optional values are `None`, not `0` or an empty string. Durations are seconds (`int`) and are parsed by the single tested function `parse_iso8601_duration()`. An unparseable duration produces `duration_s=None`.

### Video and Channel

```python
@dataclass(frozen=True)
class Video:
    video_id: str                 # 11 characters
    title: str
    channel_id: str
    tags: tuple[str, ...] = ()
    available: bool = True         # False if private/deleted/unavailable
    description: str | None = None
    duration_s: int | None = None
    category_id: str | None = None
    language: str | None = None   # BCP-47 primary subtag; never inferred from text
    published_at: datetime | None = None
    channel_title: str | None = None

@dataclass(frozen=True)
class Channel:
    channel_id: str                # UC-prefixed
    title: str
    description: str | None = None
    handle: str | None = None
    topics: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    subscriber_count: int | None = None  # hidden => None
    video_count: int | None = None
    uploads_playlist_id: str | None = None
    recent_uploads: tuple[Video, ...] = ()

@dataclass(frozen=True)
class ScoredVideo:
    video: Video
    score: float                   # 0..1
    reason: str

@dataclass(frozen=True)
class ScoredChannel:
    channel: Channel
    score: float                   # 0..1
    reason: str
```

### User Library Models (FR-03 and FR-04)

```python
@dataclass(frozen=True)
class LikedVideo:
    video: Video
    added_at: datetime | None      # None => unknown timestamp bucket

@dataclass(frozen=True)
class Subscription:
    channel_id: str
    channel_title: str
    subscribed_at: datetime | None

@dataclass(frozen=True)
class PlaylistItem:
    playlist_id: str
    video: Video
    added_at: datetime | None

@dataclass(frozen=True)
class UserPlaylist:
    playlist_id: str
    title: str
    item_count: int | None

@dataclass(frozen=True)
class Library:
    liked: tuple[LikedVideo, ...]
    subscriptions: tuple[Subscription, ...]
    playlists: tuple[UserPlaylist, ...]
    playlist_items: tuple[PlaylistItem, ...]   # items of the playlists above
```

`Library` is an in-memory snapshot only; it is never persisted or cached (SRS 6.3 Retention). Liked videos come from the likes playlist when available (gives `added_at`); otherwise `added_at=None`.

### Shared Filters and Period Models

```python
@dataclass(frozen=True)
class Filters:
    max_duration_s: int | None = None
    language: str | None = None

@dataclass(frozen=True)
class Period:
    start: date
    end: date                    # inclusive; start <= end
```

### Engagement Report (FR-04)

The report structure is shared. The analysis feature owner may implement its calculation, but must not change this output structure without team agreement.

```python
@dataclass(frozen=True)
class DurationBucket:
    short_count: int
    medium_count: int
    long_count: int
    unknown_count: int

@dataclass(frozen=True)
class SourceCounts:
    likes: int
    subscriptions: int
    playlist_items: int

@dataclass(frozen=True)
class RankedEntry:
    key: str                      # channel ID or category ID
    label: str | None             # channel title / category name, if known
    distinct_items: int           # ranking value: distinct library items
    sources: SourceCounts         # per-source breakdown (FR-04.1)

@dataclass(frozen=True)
class TrendPoint:
    month: str | None             # "YYYY-MM"; None => unknown-timestamp bucket
    sources: SourceCounts

@dataclass(frozen=True)
class PeriodSummary:
    period: Period | None         # None => whole library (overall)
    totals: SourceCounts
    top_channels: tuple[RankedEntry, ...]
    top_categories: tuple[RankedEntry, ...]
    duration_buckets: DurationBucket
    trend: tuple[TrendPoint, ...] # chronological; unknown bucket last, always present

@dataclass(frozen=True)
class EngagementReport:
    overall: PeriodSummary
    periods: tuple[PeriodSummary, ...]  # zero, one, or two requested periods
    comparison: str | None             # summary when two periods supplied
    definition: str                   # explains what engagement means and which data was used (FR-04.5)
```

Counts must be based on distinct library items and must preserve the separate sources (likes, subscriptions, playlist items) as required by FR-04.1. Trends use like time, playlist-add time, or subscription time as applicable (FR-04.2). Items without a reliable timestamp go in the `month=None` trend point and are excluded from period summaries, never given an invented date. Duration bucket boundaries (short/medium/long) are defined once as constants in `services/analysis.py` and stated in `definition`.

### Playlist Models (FR-05)

```python
@dataclass(frozen=True)
class PlaylistConstraints:
    topic: str                        # 1..200 characters
    total_duration_s: int             # 60..43200
    max_video_s: int                  # >=60 and <= total duration
    language: str | None = None
    allow_unknown_language: bool = False
    tolerance: float = 0.10
    privacy: Literal["private", "unlisted", "public"] = "private"

@dataclass(frozen=True)
class ConstraintCheck:
    name: str                         # e.g. "max_video_length", "total_within_tolerance", "language"
    passed: bool
    detail: str

@dataclass(frozen=True)
class PlaylistProposal:
    proposal_id: str                  # >=128 bits of randomness
    digest: str                       # SHA-256 of canonical proposal content
    owner: str                        # account fingerprint
    constraints: PlaylistConstraints
    videos: tuple[Video, ...]         # ordered and immutable
    total_duration_s: int
    checks: tuple[ConstraintCheck, ...]     # constraint-check report shown to the user (FR-05.4)
    unknown_language: tuple[str, ...]       # video IDs included only because allow_unknown_language=True (flagged)
    write_cost: int
    expires_at: datetime              # creation time + 15 minutes

@dataclass(frozen=True)
class CreatedPlaylist:
    playlist_id: str
    url: str
    added: tuple[str, ...]            # video IDs
    failed: tuple[str, ...]           # video IDs
```

**Proposal state:** Proposal content is immutable. Mutable lifecycle state (`proposed`, `creating`, `created`, `partially-created`, `cancelled`, `superseded`, `expired`) is held separately by the proposal store, not inside the frozen `PlaylistProposal`. This avoids changing the proposal whose digest is being verified. The digest covers every field except `proposal_id`, `digest`, and `expires_at`, serialized canonically (sorted keys, UTF-8 JSON). A new proposal from the same owner marks that owner's earlier open proposals `superseded`.

### Quota Models

```python
Bucket = Literal["general", "search"]

@dataclass(frozen=True)
class QuotaCost:
    general: int = 0
    search: int = 0

@dataclass(frozen=True)
class QuotaStatus:
    general_remaining: int
    search_remaining: int
    resets_at: datetime
```

## 2. YouTube Provider Interface

Services receive a `YouTubeProvider` through constructor injection. `LiveProvider` uses the official YouTube Data API. `FixtureProvider` reads synthetic data from `tests/fixtures/`. Methods return internal models and raise application errors defined in Section 5.

```python
class YouTubeProvider(Protocol):
    # Public data
    def get_videos(self, ids: Sequence[str]) -> list[Video]: ...
    # Batch IDs in groups of <=50; missing/private videos may be omitted or returned unavailable.

    def search_videos(
        self, query: str, *, max_results: int = 25, pages: int = 1
    ) -> list[str]: ...  # video IDs; at most 2 pages per tool invocation

    def get_channels(self, ids: Sequence[str]) -> list[Channel]: ...
    def resolve_channel(self, ref: str) -> str: ...  # URL, @handle, or ID -> UC channel ID
    def search_channels(self, query: str, *, max_results: int = 25) -> list[str]: ...
    def get_recent_uploads(self, channel_id: str, n: int = 10) -> list[Video]: ...
    def get_categories(self, region: str = "US") -> dict[str, str]: ...

    # User data (OAuth, youtube.readonly)
    def get_library(self) -> Library: ...
    def account_fingerprint(self) -> str: ...  # stable, non-reversible owner identifier

    # Writes (OAuth youtube scope; called only after explicit confirmation)
    def create_playlist(self, title: str, privacy: str) -> str: ...
    def add_playlist_item(self, playlist_id: str, video_id: str) -> None: ...

    # Authentication
    def auth_status(self) -> AuthStatus: ...
    def ensure_write_scope(self) -> None: ...
    # Requests the `youtube` scope incrementally; called by PlaylistService.create() only,
    # after the write-quota pre-check and before elicitation. Raises AuthRequiredError if not granted.
    def sign_out(self) -> None: ...  # revokes and deletes stored tokens
```

```python
@dataclass(frozen=True)
class AuthStatus:                    # models/auth.py
    state: Literal["ok", "needs_authorisation", "expired"]
    scopes: tuple[str, ...]          # granted scopes; empty when not authorised
```

### Clock

Every component that depends on time (quota reset, proposal expiry, cache TTL) receives a `Clock` through its constructor. Tests use a fake clock and never sleep.

```python
class Clock(Protocol):               # clock.py
    def now(self) -> datetime: ...   # timezone-aware UTC

class SystemClock:
    def now(self) -> datetime: ...
```

### Metadata cache

Caching is a wrapper, not a feature of services: `CachingProvider(inner: YouTubeProvider, store, clock)` in `providers/cached.py` implements `YouTubeProvider` and caches public metadata reads (`get_videos`, `get_channels`, `get_recent_uploads`, `get_categories`, `resolve_channel`) for at most 24 hours. It never caches `get_library`, auth, or write methods. `server.py` composes `CachingProvider(LiveProvider(...))`; services do not know whether a cache is present.

Because cache hits make no API call, workflow quota pre-checks are computed for the worst case (all misses), and cost is recorded only for real API calls (see Quota contract).

### Provider implementation rules

- All Google API calls and raw API response mapping are isolated in `providers/live.py`.
- The fixture provider implements the same Protocol and supports configurable errors and call counting.
- Any new provider method must be added to the Protocol, FixtureProvider, and LiveProvider in the same PR.
- Batch IDs in groups of at most 50.
- Limit `search.list` to at most two pages per tool invocation.

### Quota contract

`QuotaManager.cost_of(op, **args) -> QuotaCost` contains the known operation-cost table. Reads use the SRS cost; each `search.list` page consumes one search-call unit; playlist writes use the specified write cost. Before the first provider call in a workflow, the service pre-checks the full known workflow cost. If the pre-check fails, zero provider calls are made. Record cost after each actual API call. Unknown costs fail closed.

```python
class QuotaManager:
    def __init__(self, ledger: QuotaLedger, clock: Clock) -> None: ...
    def cost_of(self, op: str, **args) -> QuotaCost: ...   # raises UnknownCostError
    def check(self, cost: QuotaCost) -> None: ...          # raises OverBudgetError
    def record(self, cost: QuotaCost) -> None: ...
    def mark_exhausted(self, bucket: Bucket) -> None: ...  # after Google quotaExceeded; until next reset
    def status(self) -> QuotaStatus: ...
```

`op` names are the YouTube API method names (`videos.list`, `channels.list`, `playlistItems.list`, `playlists.list`, `subscriptions.list`, `videoCategories.list`, `search.list`, `playlists.insert`, `playlistItems.insert`). The daily reset is midnight Pacific Time.

Providers never check quota. `LiveProvider` takes an `on_api_call: Callable[[str], None]` callback at construction and calls it once per real HTTP request with the `op` name; `server.py` wires it to `quota.record(quota.cost_of(op))`. When Google returns `quotaExceeded`, `LiveProvider` calls `on_quota_exceeded(bucket)`, wired to `mark_exhausted`, before raising `QuotaExceededError`. `FixtureProvider` accepts the same callbacks so quota behaviour is testable without the network.

## 3. Service Interfaces

Services depend on the provider, quota manager, and clock only, plus the shared pure scoring functions. Services do not call each other.

**Inputs are already validated.** The MCP layer calls `services/validation.py` before any service call, so services receive normalized values: an 11-character `video_id`, and for channels either a UC-prefixed ID or an `@handle` (only handles and IDs need `provider.resolve_channel`). Services must not re-parse URLs.

```python
# services/similarity.py — shared pure functions (no provider, no I/O).
# Used by SimilarityService, RecommendationService and PlaylistService; one implementation only.
def score_video(source: Video, candidate: Video) -> tuple[float, str]: ...
def score_channel(source: Channel, candidate: Channel) -> tuple[float, str]: ...

class SimilarityService:
    # FR-01 and FR-02
    def similar_videos(self, video_id: str, n: int = 10) -> list[ScoredVideo]: ...
    def similar_channels(self, channel_ref: str, n: int = 10) -> list[ScoredChannel]: ...
    # channel_ref: UC ID or @handle (already validated)

class RecommendationService:
    # FR-03; uses SimilarityService.score_video
    def recommend(self, n: int = 10, filters: Filters | None = None) -> list[ScoredVideo]: ...

class AnalysisService:
    # FR-04; calculations over Library data
    def analyse(self, periods: Sequence[Period] = ()) -> EngagementReport: ...

class PlaylistService:
    # FR-05; uses the shared video scoring implementation for candidates
    def propose(self, constraints: PlaylistConstraints) -> PlaylistProposal: ...
    def create(self, proposal_id: str, confirm: "ConfirmFn") -> CreatedPlaylist: ...
    def cancel(self, proposal_id: str) -> None: ...

ConfirmFn = Callable[[PlaylistProposal], bool]
```

**Shared similarity implementation:** The module-level functions in `services/similarity.py` are the only scoring implementation (split into a `services/similarity/scoring.py` submodule only if the team later agrees). FR-03 and FR-05 import `score_video` directly rather than depending on a `SimilarityService` instance; do not duplicate scoring logic. Use the SRS 6.3 weights and missing-feature weight renormalization.

**Determinism (NFR-10):** Ranked results are sorted by score descending, then by ID ascending (`video_id` / `channel_id`) to break ties. Scores are rounded to 4 decimal places before sorting and output. Token normalization is fixed (lowercase, Unicode NFKC, split on non-alphanumerics) and does not depend on locale or dictionary order.

### Playlist creation order

`create()` must perform these steps in order:

1. Load proposal and lifecycle state.
2. Reject unknown, expired, modified, foreign-owner, cancelled, superseded, or consumed proposals.
3. Verify the proposal's canonical content digest.
4. Pre-check the full write quota before elicitation or writes.
5. Ensure the `youtube` write scope (`provider.ensure_write_scope()`); if not granted, fail with `AuthRequiredError` and make no writes.
6. Invoke `confirm(proposal)` through MCP elicitation.
7. If confirmation is declined or elicitation is unsupported, fail closed and make no writes; the error's `next_action` offers manual export of the proposal (FR-05.10).
8. Mark the proposal `creating` (so a replay cannot start a second creation), then create the playlist and add items; set the final state to `created` or `partially-created` and report partial failure accurately.

The confirmation function is supplied by `server.py`, which wraps MCP elicitation. A client without elicitation cannot silently proceed.

## 4. MCP Tool Contracts

Tools are thin: validate input, call one service, and serialize the result. No stack traces are returned to users.

Success envelope:

```json
{ "ok": true, "data": {}, "summary": "..." }
```

Error envelope:

```json
{
  "ok": false,
  "error": { "code": "...", "message": "...", "next_action": "..." }
}
```

| Tool                            | Input                                                                  | Success data                                                                     | Service              | `readOnlyHint`  |
| ------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------- | --------------- |
| `find_similar_videos`           | `video_ref: str`, `n: int=10` (1..50)                                  | `results: [{video_id,title,channel,duration_s,score,reason}]`                    | Similarity           | Yes             |
| `find_similar_channels`         | `channel_ref: str`, `n: int=10`                                        | `results: [{channel_id,title,score,reason}]`                                     | Similarity           | Yes             |
| `recommend_videos`              | `n: int=10`, `filters?: {max_duration_s?, language?}`                  | `results: [{video_id,title,channel,score,reason}]`                               | Recommendation       | Yes             |
| `analyse_engagement`            | `periods?: [{start,end}]` (max 2, ISO dates)                           | `report`                                                                         | Analysis             | Yes             |
| `propose_playlist`              | `topic,total_duration_s,max_video_s,language?,allow_unknown_language?` | `proposal: {proposal_id,videos[],total_duration_s,checks[],unknown_language[],write_cost,expires_at}` | Playlist             | Yes (no writes) |
| `create_playlist_from_proposal` | `proposal_id: str`                                                     | `playlist_id,url,added[],failed[]`                                               | Playlist             | **No**          |
| `cancel_playlist_proposal`      | `proposal_id: str`                                                     | `cancelled: true`                                                                | Playlist             | Yes             |
| `get_video_details`             | `video_ref: str`                                                       | `video`                                                                          | Provider via service | Yes             |
| `auth_status`                   | None                                                                   | `state,scopes`                                                                   | Provider             | Yes             |
| `get_quota_status`              | None                                                                   | `general_remaining,search_remaining,resets_at`                                   | Quota                | Yes             |

Input rules: `video_ref` accepts YouTube watch, `youtu.be`, Shorts URLs, or an 11-character ID. `channel_ref` accepts a channel URL, `@handle`, or UC-prefixed ID. Validate and normalize in the MCP layer with `services/validation.py` before any service or provider call; services receive the normalized `video_id` / `channel_ref` (Section 3).

## 5. Error Handling

One base class in `src/youtube_mcp/errors.py`. Each application error contains `code`, a user-readable `message`, and `next_action`. The MCP layer maps `AppError` to the error envelope. Any unexpected exception becomes `internal_error`; details go to safe logs, never tokens or secrets.

```python
class AppError(Exception):
    code: str
    message: str
    next_action: str
```

| Class                   | Code                      | When                                                        | Retry                                               |
| ----------------------- | ------------------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| `ValidationError`       | `invalid_input`           | Invalid ID/URL/date/constraint; before API calls            | No                                                  |
| `ConstraintError`       | `impossible_constraints`  | Contradictory or unsatisfiable playlist constraints         | No                                                  |
| `NotFoundError`         | `not_found`               | Unknown video/channel/proposal                              | No                                                  |
| `UnavailableError`      | `unavailable`             | Private/deleted/unavailable video                           | No                                                  |
| `InsufficientDataError` | `not_enough_data`         | Empty library or insufficient metadata                      | No                                                  |
| `AuthRequiredError`     | `auth_required`           | Missing/expired token or `invalid_grant`                    | After reauth                                        |
| `ChannelRequiredError`  | `youtube_signup_required` | User has no YouTube channel                                 | No                                                  |
| `QuotaExceededError`    | `quota_exceeded`          | Google quota exceeded; include reset information when known | No                                                  |
| `OverBudgetError`       | `over_budget`             | Local pre-check fails; zero provider calls                  | No                                                  |
| `UnknownCostError`      | `unknown_cost`            | Operation missing from cost table; fail closed              | No                                                  |
| `RateLimitedError`      | `rate_limited`            | HTTP 429 after limited retries                              | No                                                  |
| `ConfirmationError`     | `confirmation_failed`     | Declined/cancelled/unsupported elicitation; no writes       | No                                                  |
| `ProposalStateError`    | `proposal_invalid`        | Expired/modified/foreign/consumed/cancelled proposal        | No                                                  |
| `ProviderError`         | `provider_error`          | Other provider/API failure                                  | Depends on specific operation; no unbounded retries |

Google API reason mapping occurs only in `providers/live.py`. Services and MCP tools do not inspect HTTP status codes or Google-specific reason strings.

## 6. Testing Strategy

- **FixtureProvider:** Implements the full `YouTubeProvider` Protocol using synthetic JSON fixtures only. It can be configured to raise each application error.
- **Call counting:** `FixtureProvider.calls` records calls; tests assert zero provider calls for invalid inputs and over-budget workflows.
- **Injectable clock:** Services receive a clock for proposal expiry and quota-reset tests; tests do not wait in real time.
- **Unit tests (pytest):** Scoring, duration parsing, playlist constraints, validation, quota calculations, and model behavior.
- **Integration tests:** Each service tested with FixtureProvider.
- **End-to-end tests:** One flow for each FR-01 to FR-05 through an MCP client harness against the server, using a fake confirmation function where needed.
- **Negative/security tests:** Cover SRS TQ-04 and security requirements, including prompt-injection-like metadata titles that must never cause a write.
- **CI:** Fixture-based tests only. Live API tests run separately on a schedule within SRS NFR-08 limits.
- **Contributor rule:** Any new provider method is added to the Protocol, FixtureProvider, and LiveProvider in the same PR.

## 7. Decisions and Changes

| Date       | Decision/change                                                                                                         | Who agreed          | Issue/PR/ADR |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------ |
| 2026-11-22 | Initial interface draft: frozen dataclasses, Protocol-based provider, envelope tool responses, quota checks in services | Pending team review |              |
| 2026-11-22 | Align package structure with initial repository setup (`youtube_mcp`, plural `providers`, folder-based models)          | Pending team review |              |
| 2026-11-22 | Define shared `Filters`, `Period`, and `EngagementReport` model shapes                                                  | Pending team review |              |
| 2026-11-22 | Keep proposal content immutable and lifecycle state in the proposal store                                               | Pending team review |              |
| 2026-11-22 | Centralize reusable similarity scoring so FR-01, FR-02, FR-03, and FR-05 do not duplicate algorithms                    | Pending team review |              |
| 2026-11-22 | SRS alignment: add `errors.py`/`clock.py` to layout; `Library.playlists`; per-source counts and trend buckets in `EngagementReport`; `checks` and `unknown_language` on `PlaylistProposal` | Pending team review | #2 |
| 2026-11-22 | `AuthStatus` with scopes; `ensure_write_scope()` and `sign_out()` on the provider; write-scope step in `create()` | Pending team review | #3, #14, #17 |
| 2026-11-22 | `QuotaManager.mark_exhausted()`; providers report real API calls via `on_api_call` / `on_quota_exceeded` callbacks | Pending team review | #18 |
| 2026-11-22 | 24-hour cache as a `CachingProvider` wrapper; shared injectable `Clock` | Pending team review | #19 |
| 2026-11-22 | MCP layer normalizes refs; services take clean IDs; `score_video`/`score_channel` are module-level pure functions; deterministic tie-break by ID | Pending team review | #7, #9 |

### Change Process

- Changes to Sections 1–5 require a PR and at least one reviewer.
- Record each agreed change in the table above.
- Significant architectural decisions should also have an ADR in `docs/adr/`.
- This document must be reviewed and agreed upon by all three team members before feature implementation begins.
