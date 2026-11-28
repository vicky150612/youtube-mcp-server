"""Quota models (CON-02, NFR-02)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

__all__ = ["Bucket", "QuotaCost", "QuotaStatus"]

Bucket = Literal["general", "search", "videos_insert"]


@dataclass(frozen=True)
class QuotaCost:
    general: int = 0  # units from the 10,000/day pool
    search: int = 0  # search.list calls from the 100/day bucket
    videos_insert: int = 0


@dataclass(frozen=True)
class QuotaStatus:
    general_remaining: int
    search_remaining: int
    resets_at: datetime  # next midnight Pacific Time, timezone-aware
    videos_insert_remaining: int = 100
