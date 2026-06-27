"""Scoreline — the current goals/points for each side.

Purpose
    Carry the match score as an immutable value used by tension-sensitive
    metrics (Pulse, Drama) and phase/emotion derivation.

Inputs
    home, away: non-negative integer tallies.

Invariants
    * Immutable (frozen).
    * ``margin`` is always >= 0.
"""
from __future__ import annotations

from dataclasses import dataclass

from .side import Side


@dataclass(frozen=True)
class Scoreline:
    """Immutable snapshot of the score for both sides."""

    home: int = 0
    away: int = 0

    def __post_init__(self) -> None:
        if self.home < 0 or self.away < 0:
            raise ValueError("scores must be non-negative")

    @property
    def margin(self) -> int:
        """Absolute goal/point difference between the sides."""
        return abs(self.home - self.away)

    @property
    def is_draw(self) -> bool:
        """True when the sides are level."""
        return self.home == self.away

    @property
    def leader(self) -> Side:
        """Side currently ahead, or ``Side.NEUTRAL`` when level."""
        if self.home > self.away:
            return Side.HOME
        if self.away > self.home:
            return Side.AWAY
        return Side.NEUTRAL
