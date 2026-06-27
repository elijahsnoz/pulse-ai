"""IntensityBand — the qualitative "vibe" tier of a metric.

Purpose
    Translate a 0-100 metric value into a fan-felt word, so the heartbeat, the
    recap and a push notification all agree on whether a moment is "Electric" or
    just "Simmering". This is shared domain knowledge, not frontend styling.

Inputs
    A metric value and an ascending 4-threshold tuple (from ``FanConfig``).

Outputs
    Exactly one of five ordered bands.

Invariants
    * Members are declared in ascending intensity order.
    * ``from_value`` is pure, total and deterministic.
"""
from __future__ import annotations

from collections.abc import Sequence
from enum import Enum


class IntensityBand(Enum):
    """Ordered intensity tiers, low to high."""

    DORMANT = "dormant"
    SIMMERING = "simmering"
    HEATING = "heating"
    ELECTRIC = "electric"
    FRENZIED = "frenzied"

    @property
    def label(self) -> str:
        """Human-friendly title-case label (e.g. ``"Electric"``)."""
        return self.value.title()

    @classmethod
    def from_value(cls, value: float, thresholds: Sequence[float]) -> "IntensityBand":
        """Map ``value`` onto a band using ascending ``thresholds``.

        ``thresholds`` must hold exactly four ascending cut points (one fewer
        than the number of bands). A value lands in the highest band whose
        threshold it meets or exceeds.
        """
        members = list(cls)
        if len(thresholds) != len(members) - 1:
            raise ValueError(
                f"expected {len(members) - 1} thresholds, got {len(thresholds)}"
            )
        index = sum(1 for cut in thresholds if value >= cut)
        return members[index]
