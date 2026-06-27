"""EmotionResolver — derives the deterministic EmotionalState.

Purpose
    Translate three metrics — Pulse Score, Momentum Vector and Drama Index — into
    a single emotional word that captures how the match feels. Deterministic and
    rule-based; never a model, never random.

Inputs
    pulse:    the current ``PulseScore``.
    momentum: the current ``MomentumVector`` (uses ``magnitude``).
    drama:    the current ``DramaIndex``.

Outputs
    Exactly one ``EmotionalState``.

Precedence (first match wins, deterministic)
    1. Calm      — pulse and drama both low.
    2. Explosive — pulse and drama both very high.
    3. Desperate — very high drama with a strongly directional siege.
    4. Chaotic   — high pulse but balanced momentum (end-to-end mayhem).
    5. Dominant  — one side strongly controlling.
    6. Building  — pulse rising above the building threshold.
    7. Balanced  — otherwise.

Note
    Lateness/closeness flow in via the Drama Index (which already amplifies for
    late, narrow-margin situations), keeping this a pure function of the three
    metrics as specified.

Invariants
    * Pure & deterministic; total (always returns a state).
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..value_objects.emotional_state import EmotionalState
from ..value_objects.metrics import DramaIndex, MomentumVector, PulseScore


class EmotionResolver:
    """Resolves the ``EmotionalState`` from Pulse, Momentum and Drama."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def resolve(
        self, pulse: PulseScore, momentum: MomentumVector, drama: DramaIndex
    ) -> EmotionalState:
        """Return the current ``EmotionalState`` (see module precedence)."""
        cfg = self._config.emotion
        p = pulse.value
        d = drama.value
        m = momentum.magnitude

        if p <= cfg.calm_pulse_max and d <= cfg.calm_drama_max:
            return EmotionalState.CALM
        if p >= cfg.explosive_pulse_min and d >= cfg.explosive_drama_min:
            return EmotionalState.EXPLOSIVE
        if d >= cfg.desperate_drama_min and m >= cfg.dominant_momentum_min:
            return EmotionalState.DESPERATE
        if p >= cfg.chaotic_pulse_min and m <= cfg.chaotic_momentum_max:
            return EmotionalState.CHAOTIC
        if m >= cfg.dominant_momentum_min:
            return EmotionalState.DOMINANT
        if p >= cfg.building_pulse_min:
            return EmotionalState.BUILDING
        return EmotionalState.BALANCED
