"""PressureCalculator — derives a side's Pressure Index.

Purpose
    Measure one side's sustained attacking pressure as an unsigned value in
    [0, 100]. Both sides are scored independently, so an end-to-end match can
    show high pressure for both.

Inputs
    window: an ``EventWindow``.
    side:   the ``Side`` to score (HOME or AWAY).

Outputs
    ``PressureIndex`` with an additive ``Explanation``.

Invariants
    * Pure & deterministic.
    * Contributors (per-kind base + decay_adjustment) sum to the raw value.
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..numeric import clamp
from ..value_objects.explanation import Contributor, Explanation
from ..value_objects.metrics import PressureIndex
from ..value_objects.side import Side
from .windowing import EventWindow

_METRIC = "pressure_index"


class PressureCalculator:
    """Computes the branded Pressure Index for a single side."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def calculate(self, window: EventWindow, side: Side) -> PressureIndex:
        """Return the Pressure Index for ``side`` within ``window``."""
        scale = self._config.pressure.scale

        base_by_kind: dict[str, float] = {}
        decayed_total = 0.0
        base_total = 0.0
        for we in window.events:
            if we.event.side is not side or we.base_weight == 0.0:
                continue
            base_by_kind[we.event.kind] = (
                base_by_kind.get(we.event.kind, 0.0) + we.base_weight
            )
            decayed_total += we.effective
            base_total += we.base_weight

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
        value = clamp(raw_value, 0.0, 100.0)

        explanation = Explanation(
            metric=_METRIC,
            value=value,
            raw_value=raw_value,
            contributors=tuple(contributors),
        )
        return PressureIndex(side=side, value=value, explanation=explanation)
