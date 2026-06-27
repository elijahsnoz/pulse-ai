"""CertaintyTier — how assertively the AI may speak about the current signal.

Purpose
    The Confidence Score is an internal trust dial; fans never see the number.
    Instead it maps to a CertaintyTier that the Story Engine uses to pick its
    phrasing ("might be edging it" vs "are taking control"). This keeps narration
    honest without exposing raw analytics.

Inputs
    A 0-100 confidence value and a 2-threshold tuple (from ``FanConfig``).

Outputs
    Exactly one tier.

Invariants
    * Pure, total, deterministic.
    * Strictly internal to narration — not a fan-facing number.
"""
from __future__ import annotations

from collections.abc import Sequence
from enum import Enum


class CertaintyTier(Enum):
    """How confident the deterministic signal is, as a narration tier."""

    TENTATIVE = "tentative"
    MEASURED = "measured"
    CONFIDENT = "confident"

    @property
    def label(self) -> str:
        """Human-friendly title-case label."""
        return self.value.title()

    @classmethod
    def from_confidence(cls, value: float, thresholds: Sequence[float]) -> "CertaintyTier":
        """Map a confidence value onto a tier using two ascending cut points."""
        if len(thresholds) != 2:
            raise ValueError(f"expected 2 thresholds, got {len(thresholds)}")
        low, high = thresholds
        if value < low:
            return cls.TENTATIVE
        if value < high:
            return cls.MEASURED
        return cls.CONFIDENT
