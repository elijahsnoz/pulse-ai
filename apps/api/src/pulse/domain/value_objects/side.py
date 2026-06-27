"""Side — the sport-agnostic notion of a competing party.

Purpose
    Identify which competitor an event belongs to without assuming football,
    teams, or any sport-specific vocabulary. Two contesting sides plus a
    neutral option cover the overwhelming majority of timed team sports.

Invariants
    * ``sign`` is +1 for HOME, -1 for AWAY, 0 for NEUTRAL — used to convert
      one-sided event weights into a signed, directional quantity.
"""
from __future__ import annotations

from enum import Enum


class Side(Enum):
    """A competitor in a match (or NEUTRAL for un-attributed events)."""

    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"

    @property
    def sign(self) -> int:
        """Directional multiplier: +1 home, -1 away, 0 neutral."""
        return {Side.HOME: 1, Side.AWAY: -1, Side.NEUTRAL: 0}[self]

    @property
    def opponent(self) -> "Side":
        """The opposing side; NEUTRAL is its own opponent."""
        if self is Side.HOME:
            return Side.AWAY
        if self is Side.AWAY:
            return Side.HOME
        return Side.NEUTRAL
