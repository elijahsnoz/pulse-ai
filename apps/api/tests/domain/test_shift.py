"""Tests for the momentum ShiftDetector."""
from __future__ import annotations

from pulse.domain.services.shift import ShiftDetector
from pulse.domain.value_objects.explanation import Explanation
from pulse.domain.value_objects.metrics import MomentumVector
from pulse.domain.value_objects.side import Side


def _mom(value):
    return MomentumVector(value=value, direction=Side.NEUTRAL,
                          explanation=Explanation("m", value, value, ()))


def test_no_previous_yields_no_signal():
    assert ShiftDetector().detect(None, _mom(60.0), minute=70.0) is None


def test_small_swing_is_ignored():
    # default ShiftConfig.swing_threshold = 55.0
    assert ShiftDetector().detect(_mom(10.0), _mom(40.0), minute=70.0) is None


def test_large_swing_toward_home():
    signal = ShiftDetector().detect(_mom(-30.0), _mom(40.0), minute=70.0)
    assert signal is not None
    assert signal.toward is Side.HOME
    assert signal.delta == 70.0
    assert signal.minute == 70.0


def test_large_swing_toward_away():
    signal = ShiftDetector().detect(_mom(40.0), _mom(-30.0), minute=66.0)
    assert signal is not None
    assert signal.toward is Side.AWAY
    assert signal.delta == -70.0
