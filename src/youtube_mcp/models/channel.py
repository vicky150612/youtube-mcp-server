"""Channel models."""

from __future__ import annotations

from dataclasses import dataclass

from youtube_mcp.models.video import Video

__all__ = ["Channel", "ScoredChannel"]


@dataclass(frozen=True)
class Channel:
    """A YouTube channel's metadata. Hidden statistics are ``None``, not ``0``."""

    channel_id: str  # UC-prefixed
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
class ScoredChannel:
    channel: Channel
    score: float  # 0..1
    reason: str
