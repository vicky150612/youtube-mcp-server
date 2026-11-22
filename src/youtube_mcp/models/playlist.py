"""Playlist proposal and creation models (FR-05).

Proposal content is immutable. Lifecycle state is held separately by the
proposal store, never inside ``PlaylistProposal``, so the content whose digest
is verified cannot change.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from youtube_mcp.models.video import Video

__all__ = [
    "Privacy",
    "ProposalState",
    "PlaylistConstraints",
    "ConstraintCheck",
    "PlaylistProposal",
    "CreatedPlaylist",
]

Privacy = Literal["private", "unlisted", "public"]

# Lifecycle states tracked by the proposal store (not by PlaylistProposal).
ProposalState = Literal[
    "proposed",
    "creating",
    "created",
    "partially-created",
    "cancelled",
    "superseded",
    "expired",
]


@dataclass(frozen=True)
class PlaylistConstraints:
    """Ranges are enforced by input validation, not by this model."""

    topic: str  # 1..200 characters
    total_duration_s: int  # 60..43200
    max_video_s: int  # >=60 and <= total duration
    language: str | None = None
    allow_unknown_language: bool = False
    tolerance: float = 0.10
    privacy: Privacy = "private"


@dataclass(frozen=True)
class ConstraintCheck:
    name: str  # e.g. "max_video_length", "total_within_tolerance", "language"
    passed: bool
    detail: str


@dataclass(frozen=True)
class PlaylistProposal:
    proposal_id: str  # >=128 bits of randomness
    digest: str  # SHA-256 of canonical proposal content
    owner: str  # account fingerprint
    constraints: PlaylistConstraints
    videos: tuple[Video, ...]  # ordered and immutable
    total_duration_s: int
    checks: tuple[ConstraintCheck, ...]  # constraint-check report (FR-05.4)
    unknown_language: tuple[str, ...]  # video IDs allowed only via allow_unknown_language (flagged)
    write_cost: int
    expires_at: datetime  # creation time + 15 minutes


@dataclass(frozen=True)
class CreatedPlaylist:
    playlist_id: str
    url: str
    added: tuple[str, ...]  # video IDs
    failed: tuple[str, ...]  # video IDs
