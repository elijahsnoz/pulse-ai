"""MatchPhase — the narrative chapter a match is currently in.

Purpose
    Give downstream commentary a richer sense of time than a raw minute. A phase
    blends clock position with live metric state (a momentum surge can open a
    "Momentum Window" regardless of the exact minute).

Invariants
    * A total enumeration: the resolver always returns exactly one phase.
    * Order of the members reflects rough chronological/intensity progression.
"""
from __future__ import annotations

from enum import Enum


class MatchPhase(Enum):
    """The current narrative phase of a match."""

    OPENING = "opening"
    SETTLING = "settling"
    MID_GAME = "mid_game"
    MOMENTUM_WINDOW = "momentum_window"
    CRITICAL_PHASE = "critical_phase"
    FINAL_PUSH = "final_push"
    STOPPAGE_TIME = "stoppage_time"

    @property
    def label(self) -> str:
        """Human-friendly title-case label (e.g. ``"Momentum Window"``)."""
        return self.value.replace("_", " ").title()
