"""Tests for the Pressure Index calculator."""
from __future__ import annotations

import pytest

from pulse.domain.services.pressure import PressureCalculator
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.side import Side

from .conftest import corner, shot


def _pressure(events, side, minute=60.0):
    return PressureCalculator().calculate(build_window(events, minute), side)


def test_pressure_is_non_negative_and_side_scoped():
    events = [shot(59.0, Side.HOME, on_target=True, seq=1), corner(59.5, Side.HOME, seq=2)]
    home = _pressure(events, Side.HOME)
    away = _pressure(events, Side.AWAY)
    assert home.value > 0
    assert away.value == 0.0
    assert home.side is Side.HOME and away.side is Side.AWAY


def test_both_sides_can_have_pressure_simultaneously():
    events = [shot(59.0, Side.HOME, on_target=True, seq=1),
              shot(59.0, Side.AWAY, on_target=True, seq=2)]
    assert _pressure(events, Side.HOME).value > 0
    assert _pressure(events, Side.AWAY).value > 0


def test_pressure_clamped_to_100():
    events = [shot(59.5 + i * 0.01, Side.HOME, on_target=True, seq=i) for i in range(50)]
    assert _pressure(events, Side.HOME).value == 100.0


def test_explanation_additive_with_decay_line():
    events = [shot(59.0, Side.HOME, on_target=True, seq=1), corner(58.0, Side.HOME, seq=2)]
    p = _pressure(events, Side.HOME)
    assert p.explanation.total_contribution() == pytest.approx(p.explanation.raw_value)
    assert any(c.label == "decay_adjustment" for c in p.explanation.contributors)
