"""MomentumCalculator — derives the Momentum Vector.

Purpose
    Quantify which side is on top right now as a signed, directional value in
    [-100, 100] (+home / -away), with a contributor breakdown per event kind plus
    an explicit time-decay adjustment.

Inputs
    window: an ``EventWindow`` (already weighted and decayed).

Outputs
    ``MomentumVector`` with an additive ``Explanation``.

Invariants
    * Pure & deterministic.
    * Contributors sum to the pre-clamp raw value (additive invariant):
      ``sum(per-kind base) + decay_adjustment == raw_value``.
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..numeric import clamp
from ..value_objects.explanation import Contributor, Explanation
from ..value_objects.metrics import MomentumVector
from ..value_objects.side import Side
from .windowing import EventWindow

_METRIC = "momentum_vector"


class MomentumCalculator:
    """Computes the branded Momentum Vector from a weighted event window."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def calculate(self, window: EventWindow) -> MomentumVector:
        """Return the Momentum Vector for ``window``."""
        scale = self._config.momentum.scale
        band = self._config.momentum.balanced_band

        base_by_kind: dict[str, float] = {}
        decayed_total = 0.0
        base_total = 0.0
        for we in window.events:
            if we.base_weight == 0.0:
                continue
            base_by_kind[we.event.kind] = (
                base_by_kind.get(we.event.kind, 0.0) + we.signed_base
            )
            decayed_total += we.signed_effective
            base_total += we.signed_base

        contributors: list[Contributor] = [
            Contributor(label=kind, value=scale * base_by_kind[kind])
            for kind in sorted(base_by_kind)
        ]
        decay_adjustment = scale * (decayed_total - base_total)
        contributors.append(
            Contributor(
                label="decay_adjustment",
                value=decay_adjustment,
                detail="recency weighting applied to raw event danger",
            )
        )

        raw_value = scale * decayed_total
        value = clamp(raw_value, -100.0, 100.0)

        if value > band:
            direction = Side.HOME
        elif value < -band:
            direction = Side.AWAY
        else:
            direction = Side.NEUTRAL

        explanation = Explanation(
            metric=_METRIC,
            value=value,
            raw_value=raw_value,
            contributors=tuple(contributors),
        )
        return MomentumVector(value=value, direction=direction, explanation=explanation)
