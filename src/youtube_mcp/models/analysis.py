"""Period and engagement report models (FR-04).

The report structure is shared; change it only with team agreement and an
update to docs/architecture/Architecture_and_Interface_Plan.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = [
    "Period",
    "DurationBucket",
    "SourceCounts",
    "RankedEntry",
    "TrendPoint",
    "PeriodSummary",
    "EngagementReport",
]


@dataclass(frozen=True)
class Period:
    start: date
    end: date  # inclusive; start <= end (checked by input validation)


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
    key: str  # channel ID or category ID
    label: str | None  # channel title / category name, if known
    distinct_items: int  # ranking value: distinct library items
    sources: SourceCounts  # per-source breakdown (FR-04.1)


@dataclass(frozen=True)
class TrendPoint:
    month: str | None  # "YYYY-MM"; None => unknown-timestamp bucket
    sources: SourceCounts


@dataclass(frozen=True)
class PeriodSummary:
    period: Period | None  # None => whole library (overall)
    totals: SourceCounts
    top_channels: tuple[RankedEntry, ...]
    top_categories: tuple[RankedEntry, ...]
    duration_buckets: DurationBucket
    trend: tuple[TrendPoint, ...]  # chronological; unknown bucket last, always present


@dataclass(frozen=True)
class EngagementReport:
    overall: PeriodSummary
    periods: tuple[PeriodSummary, ...]  # zero, one, or two requested periods
    comparison: str | None  # summary when two periods supplied
    definition: str  # what engagement means and which data was used (FR-04.5)
