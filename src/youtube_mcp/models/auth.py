"""Authentication status model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["AuthState", "AuthStatus"]

AuthState = Literal["ok", "needs_authorisation", "expired"]


@dataclass(frozen=True)
class AuthStatus:
    state: AuthState
    scopes: tuple[str, ...]  # granted scopes; empty when not authorised
