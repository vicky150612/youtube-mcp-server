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
  models/
    __init__.py
    video.py
    channel.py
    library.py
    playlist.py
    analysis.py
    quota.py
  providers/
    __init__.py
    base.py       # YouTubeProvider Protocol
    live.py       # official YouTube API implementation
    fixture.py    # fixture-backed implementation
  services/
    __init__.py
    similarity.py
    recommendations.py
    analysis.py
    playlist.py
    validation.py
  auth/
    __init__.py
  quota/
    __init__.py
    manager.py
    ledger.py
  cache/
    __init__.py
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

**Rule:** Only `providers/live.py` communicates with Google/YouTube. Services receive internal models and never process raw API JSON.

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
    playlist_items: tuple[PlaylistItem, ...]
```

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
class PeriodSummary:
    period: Period
    item_count: int
    top_channels: tuple[tuple[str, int], ...]
    top_categories: tuple[tuple[str, int], ...]
    duration_buckets: DurationBucket

@dataclass(frozen=True)
class EngagementReport:
    overall: PeriodSummary
    periods: tuple[PeriodSummary, ...]  # zero, one, or two requested periods
    comparison: str | None             # summary when two periods supplied
    definition: str                   # explains what engagement means here
```

Counts must be based on distinct library items and must preserve the separate sources (likes, subscriptions, playlist items) as required by the SRS. Unknown timestamps belong in an unknown bucket, not an invented date.

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
class PlaylistProposal:
    proposal_id: str                  # >=128 bits of randomness
    digest: str                       # SHA-256 of canonical proposal content
    owner: str                        # account fingerprint
    constraints: PlaylistConstraints
    videos: tuple[Video, ...]         # ordered and immutable
    total_duration_s: int
    write_cost: int
    expires_at: datetime              # creation time + 15 minutes

@dataclass(frozen=True)
class CreatedPlaylist:
    playlist_id: str
    url: str
    added: tuple[str, ...]            # video IDs
    failed: tuple[str, ...]           # video IDs
```

**Proposal state:** Proposal content is immutable. Mutable lifecycle state (`proposed`, `creating`, `created`, `partially-created`, `cancelled`, `superseded`, `expired`) is held separately by the proposal store, not inside the frozen `PlaylistProposal`. This avoids changing the proposal whose digest is being verified.

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
    def auth_status(self) -> Literal["ok", "needs_authorisation", "expired"]: ...
```

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
    def cost_of(self, op: str, **args) -> QuotaCost: ...
    def check(self, cost: QuotaCost) -> None: ...
    def record(self, cost: QuotaCost) -> None: ...
    def status(self) -> QuotaStatus: ...
```

The provider itself is quota-unaware.

## 3. Service Interfaces

Services depend on the provider and quota manager only, except for the explicitly shared scoring function. Services do not call each other except where stated.

```python
class SimilarityService:
    # FR-01 and FR-02
    def similar_videos(self, video_ref: str, n: int = 10) -> list[ScoredVideo]: ...
    def similar_channels(self, channel_ref: str, n: int = 10) -> list[ScoredChannel]: ...

    # Shared by FR-01, FR-03 and FR-05; one implementation only.
    def score_video(self, source: Video, candidate: Video) -> tuple[float, str]: ...

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

**Shared similarity implementation:** Put reusable text/category scoring and the FR-01 video score in `services/similarity.py` (or a small `services/similarity/scoring.py` submodule if the team later agrees). FR-02 channel scoring and FR-03/FR-05 video candidate scoring must use shared utilities where applicable; do not duplicate scoring logic. Use the SRS weights and missing-feature weight renormalization.

### Playlist creation order

`create()` must perform these steps in order:

1. Load proposal and lifecycle state.
2. Reject unknown, expired, modified, foreign-owner, cancelled, superseded, or consumed proposals.
3. Verify the proposal's canonical content digest.
4. Pre-check the full write quota before elicitation or writes.
5. Invoke `confirm(proposal)` through MCP elicitation.
6. If confirmation is declined or elicitation is unsupported, fail closed and make no writes.
7. Only then create the playlist and add items; report partial failure accurately.

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
| `propose_playlist`              | `topic,total_duration_s,max_video_s,language?,allow_unknown_language?` | `proposal: {proposal_id,videos[],total_duration_s,checks,write_cost,expires_at}` | Playlist             | Yes (no writes) |
| `create_playlist_from_proposal` | `proposal_id: str`                                                     | `playlist_id,url,added[],failed[]`                                               | Playlist             | **No**          |
| `cancel_playlist_proposal`      | `proposal_id: str`                                                     | `cancelled: true`                                                                | Playlist             | Yes             |
| `get_video_details`             | `video_ref: str`                                                       | `video`                                                                          | Provider via service | Yes             |
| `auth_status`                   | None                                                                   | `status,scopes`                                                                  | Provider             | Yes             |
| `get_quota_status`              | None                                                                   | `general_remaining,search_remaining,resets_at`                                   | Quota                | Yes             |

Input rules: `video_ref` accepts YouTube watch, `youtu.be`, Shorts URLs, or an 11-character ID. `channel_ref` accepts a channel URL, `@handle`, or UC-prefixed ID. Validate in the MCP layer/shared validation helper before provider calls.

## 5. Error Handling

One base class in `errors.py`. Each application error contains `code`, a user-readable `message`, and `next_action`. The MCP layer maps `AppError` to the error envelope. Any unexpected exception becomes `internal_error`; details go to safe logs, never tokens or secrets.

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

### Change Process

- Changes to Sections 1–5 require a PR and at least one reviewer.
- Record each agreed change in the table above.
- Significant architectural decisions should also have an ADR in `docs/adr/`.
- This document must be reviewed and agreed upon by all three team members before feature implementation begins.
