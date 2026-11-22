"""User library models (FR-03 and FR-04).

A ``Library`` is an in-memory snapshot only; it is never persisted or cached
(SRS 6.3 Retention). A ``None`` timestamp means "unknown" and belongs in the
unknown bucket — never substitute an invented date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from youtube_mcp.models.video import Video

__all__ = ["LikedVideo", "Subscription", "PlaylistItem", "UserPlaylist", "Library"]


@dataclass(frozen=True)
class LikedVideo:
    video: Video
    added_at: datetime | None  # None => unknown timestamp bucket


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
    playlist_items: tuple[PlaylistItem, ...]  # items of the playlists above
