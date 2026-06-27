"""FanRead — the human-ready bundle derived from the raw metrics.

Purpose
    One immutable struct that turns engine numbers into things a fan actually
    feels: a heartbeat rate, vibe bands, a drama star rating, and the narration
    certainty tier. Every consumer surface (live screen, recap, notification)
    reads the SAME bundle, so the experience can never disagree with itself.

Invariants
    * Frozen / immutable.
    * Purely derived from a ``MatchState``'s metrics + ``FanConfig`` — deterministic.
    * Carries no raw analytics a fan shouldn't see (no confidence number, no
      contributor internals).
"""
from __future__ import annotations

from dataclasses import dataclass

from .certainty import CertaintyTier
from .intensity_band import IntensityBand


@dataclass(frozen=True)
class FanRead:
    """Fan-facing presentation primitives for one match moment."""

    pulse_band: IntensityBand
    heartbeat_bpm: int
    drama_band: IntensityBand
    drama_stars: int
    momentum_band: IntensityBand
    pressure_home_band: IntensityBand
    pressure_away_band: IntensityBand
    narration_certainty: CertaintyTier
