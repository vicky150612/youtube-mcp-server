"""Video models, video filters, and the shared ISO 8601 duration parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

__all__ = ["Video", "ScoredVideo", "Filters", "parse_iso8601_duration"]


@dataclass(frozen=True)
class Video:
    """A YouTube video's metadata as used inside the server.

    Metadata text (title, description, tags) is untrusted input. Unknown
    optional values are ``None``, never ``0`` or ``""``. Datetimes are
    timezone-aware UTC.
    """

    video_id: str  # 11 characters
    title: str
    channel_id: str
    tags: tuple[str, ...] = ()
    available: bool = True  # False if private/deleted/unavailable
    description: str | None = None
    duration_s: int | None = None  # None if unknown or unparseable
    category_id: str | None = None
    language: str | None = None  # BCP-47 primary subtag; never inferred from text
    published_at: datetime | None = None
    channel_title: str | None = None


@dataclass(frozen=True)
class ScoredVideo:
    video: Video
    score: float  # 0..1
    reason: str


@dataclass(frozen=True)
class Filters:
    """Optional filters for recommendations (FR-03)."""

    max_duration_s: int | None = None
    language: str | None = None


_DURATION_RE = re.compile(
    r"P"
    r"(?:(?P<weeks>\d+)W)?"
    r"(?:(?P<days>\d+)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+)H)?"
    r"(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)S)?"
    r")?"
)

_UNIT_SECONDS = {
    "weeks": 7 * 24 * 3600,
    "days": 24 * 3600,
    "hours": 3600,
    "minutes": 60,
    "seconds": 1,
}


def parse_iso8601_duration(value: object) -> int | None:
    """Parse a YouTube ISO 8601 duration (e.g. ``PT1H2M10S``) into whole seconds.

    This is the single duration parser for the project (SRS 6.3). Supported
    designators are W, D, H, M and S with integer values. Anything else —
    including years/months (ambiguous length), fractional values, an empty
    ``P``/``PT``, or a non-string — returns ``None`` so the video is treated as
    unusable for duration constraints.
    """
    if not isinstance(value, str):
        return None
    text = value.strip()
    match = _DURATION_RE.fullmatch(text)
    if match is None:
        return None
    parts = match.groupdict()
    if all(v is None for v in parts.values()):
        return None  # "P" or "PT"
    if "T" in text and all(parts[k] is None for k in ("hours", "minutes", "seconds")):
        return None  # "P1DT" — time designator with no time component
    return sum(int(v) * _UNIT_SECONDS[k] for k, v in parts.items() if v is not None)
