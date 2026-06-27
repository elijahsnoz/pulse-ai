"""ShiftDetector — emits a MomentumShifted signal on a large swing.

Purpose
    Detect when momentum has swung by at least a configured threshold between two
    consecutive evaluations, so the Story and Notification engines can react.

Inputs
    previous: the prior ``MomentumVector`` (or ``None`` at match start).
    current:  the current ``MomentumVector``.
    minute:   current match minute (stamped onto the signal).

Outputs
    ``MomentumShifted`` when the swing meets the threshold, else ``None``.

Invariants
    * Pure & deterministic.
    * No previous value => no signal (cannot detect a swing from nothing).
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..events.signals import MomentumShifted
from ..numeric import sign
from ..value_objects.metrics import MomentumVector
from ..value_objects.side import Side


class ShiftDetector:
    """Detects momentum swings crossing the configured threshold."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def detect(
        self,
        previous: MomentumVector | None,
        current: MomentumVector,
        minute: float,
    ) -> MomentumShifted | None:
        """Return a ``MomentumShifted`` signal, or ``None`` if no large swing."""
        if previous is None:
            return None
        delta = current.value - previous.value
        if abs(delta) < self._config.shift.swing_threshold:
            return None
        toward = Side.HOME if sign(delta) > 0 else Side.AWAY
        return MomentumShifted(
            previous_value=previous.value,
            current_value=current.value,
            delta=delta,
            toward=toward,
            minute=minute,
        )
