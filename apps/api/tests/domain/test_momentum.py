"""Tests for the Momentum Vector calculator."""
from __future__ import annotations

import pytest

from pulse.domain.services.momentum import MomentumCalculator
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.side import Side

from .conftest import shot, substitution


def _momentum(events, minute=60.0):
    return MomentumCalculator().calculate(build_window(events, minute))


def test_empty_window_is_balanced_zero():
    m = _momentum([])
    assert m.value == 0.0
    assert m.direction is Side.NEUTRAL
    assert m.magnitude == 0.0


def test_home_pressure_is_positive_and_home_directed():
    m = _momentum([shot(59.0, Side.HOME, on_target=True, seq=1),
                   shot(59.5, Side.HOME, on_target=True, seq=2)])
    assert m.value > 0
    assert m.direction is Side.HOME


def test_away_pressure_is_negative_and_away_directed():
    m = _momentum([shot(59.0, Side.AWAY, on_target=True, seq=1),
                   shot(59.5, Side.AWAY, on_target=True, seq=2)])
    assert m.value < 0
    assert m.direction is Side.AWAY


def test_balanced_play_stays_in_neutral_band():
    m = _momentum([shot(59.0, Side.HOME, seq=1), shot(59.0, Side.AWAY, seq=2)])
    assert m.direction is Side.NEUTRAL


def test_value_is_clamped_to_range():
    events = [shot(59.5 + i * 0.01, Side.HOME, on_target=True, seq=i) for i in range(40)]
    m = _momentum(events)
    assert m.value == 100.0


def test_explanation_is_additive():
    m = _momentum([shot(59.0, Side.HOME, on_target=True, seq=1),
                   shot(58.0, Side.AWAY, seq=2)])
    assert m.explanation.total_contribution() == pytest.approx(m.explanation.raw_value)
    labels = {c.label for c in m.explanation.contributors}
    assert "decay_adjustment" in labels


def test_zero_weight_events_do_not_contribute():
    m = _momentum([substitution(59.0, Side.HOME, seq=1)])
    assert m.value == 0.0
    # only the decay_adjustment line exists (no kind contributors)
    labels = [c.label for c in m.explanation.contributors]
    assert labels == ["decay_adjustment"]
