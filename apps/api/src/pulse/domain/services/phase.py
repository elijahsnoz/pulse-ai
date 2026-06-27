"""PhaseResolver — derives the current MatchPhase.

Purpose
    Map the moment to a narrative phase using clock position AND live metrics, so
    commentary can adapt (a surge opens a "Momentum Window"; a tense finish is a
    "Critical Phase").

Inputs
    minute:   current match minute.
    momentum: the current ``MomentumVector`` (for the momentum-window override).
    drama:    the current ``DramaIndex`` (for the critical-phase override).

Outputs
    Exactly one ``MatchPhase``.

Precedence (first match wins, deterministic)
    1. Stoppage Time   — minute >= stoppage_start.
    2. Critical Phase  — late enough AND drama >= threshold.
    3. Final Push      — minute >= final_push_start.
    4. Momentum Window — |momentum| >= threshold.
    5. Opening         — minute < opening_end.
    6. Settling        — minute < settling_end.
    7. Mid Game        — otherwise.

Invariants
    * Pure & deterministic; total (always returns a phase).
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..value_objects.match_phase import MatchPhase
from ..value_objects.metrics import DramaIndex, MomentumVector


class PhaseResolver:
    """Resolves the narrative ``MatchPhase`` from minute and live metrics."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def resolve(
        self, minute: float, momentum: MomentumVector, drama: DramaIndex
    ) -> MatchPhase:
        """Return the current ``MatchPhase`` (see module precedence)."""
        cfg = self._config.phase

        if minute >= cfg.stoppage_start:
            return MatchPhase.STOPPAGE_TIME
        if minute >= cfg.critical_min_minute and drama.value >= cfg.critical_drama_threshold:
            return MatchPhase.CRITICAL_PHASE
        if minute >= cfg.final_push_start:
            return MatchPhase.FINAL_PUSH
        if momentum.magnitude >= cfg.momentum_window_threshold:
            return MatchPhase.MOMENTUM_WINDOW
        if minute < cfg.opening_end:
            return MatchPhase.OPENING
        if minute < cfg.settling_end:
            return MatchPhase.SETTLING
        return MatchPhase.MID_GAME
