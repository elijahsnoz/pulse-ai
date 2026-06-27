"""EmotionalState — the deterministic emotional read of a match.

Purpose
    Pulse's storytelling differentiator: a single word capturing how the match
    *feels*. Derived deterministically from Pulse Score, Momentum Vector and
    Drama Index — never from a model and never random.

Invariants
    * A total enumeration: the resolver always returns exactly one state.
    * Pure function of the three input metrics + config thresholds.
"""
from __future__ import annotations

from enum import Enum


class EmotionalState(Enum):
    """The deterministic emotional tone of the current match state."""

    CALM = "calm"
    BALANCED = "balanced"
    BUILDING = "building"
    DOMINANT = "dominant"
    EXPLOSIVE = "explosive"
    CHAOTIC = "chaotic"
    DESPERATE = "desperate"

    @property
    def label(self) -> str:
        """Human-friendly title-case label (e.g. ``"Explosive"``)."""
        return self.value.title()
