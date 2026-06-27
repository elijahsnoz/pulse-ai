"""Tests for the Pulse Score scorer."""
from __future__ import annotations

import pytest

from pulse.domain.services.pulse import PulseScorer
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from .conftest import shot


def _pulse(events, scoreline, minute=60.0):
    return PulseScorer().calculate(build_window(events, minute), scoreline)


def test_quiet_level_match_has_low_but_positive_pulse():
    # No events, level score: only tension contributes.
    p = _pulse([], Scoreline(0, 0))
    assert 0 < p.value < 40
    contributors = {c.label: c.value for c in p.explanation.contributors}
    assert contributors["density"] == 0.0
    assert contributors["volatility"] == 0.0
    assert contributors["tension"] > 0.0


def test_busy_match_raises_pulse():
    quiet = _pulse([], Scoreline(0, 0)).value
    busy = _pulse(
        [shot(59.0 + i * 0.1, Side.HOME, on_target=True, seq=i) for i in range(6)],
        Scoreline(0, 0),
    ).value
    assert busy > quiet


def test_tighter_scoreline_increases_tension_component():
    level = _pulse([], Scoreline(1, 1))
    blowout = _pulse([], Scoreline(4, 0))
    level_tension = next(c.value for c in level.explanation.contributors if c.label == "tension")
    blowout_tension = next(c.value for c in blowout.explanation.contributors if c.label == "tension")
    assert level_tension > blowout_tension


def test_end_to_end_play_adds_volatility():
    # Alternating sides across the window swings momentum => volatility > 0.
    events = []
    for i in range(6):
        side = Side.HOME if i % 2 == 0 else Side.AWAY
        events.append(shot(52.0 + i, side, on_target=True, seq=i))
    p = _pulse(events, Scoreline(1, 1))
    volatility = next(c.value for c in p.explanation.contributors if c.label == "volatility")
    assert volatility > 0


def test_explanation_additive_and_clamped():
    p = _pulse([shot(59.0, Side.HOME, on_target=True, seq=1)], Scoreline(1, 1))
    assert p.explanation.total_contribution() == pytest.approx(p.explanation.raw_value)
    assert 0.0 <= p.value <= 100.0
