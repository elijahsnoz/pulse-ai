"""Tests for the Drama Index scorer."""
from __future__ import annotations

import pytest

from pulse.domain.services.drama import DramaScorer
from pulse.domain.services.pulse import PulseScorer
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from .conftest import goal, red_card, shot


def _drama(events, scoreline, minute, all_events=None):
    window = build_window(events, minute)
    pulse = PulseScorer().calculate(window, scoreline)
    return DramaScorer().calculate(pulse, window, all_events or events, scoreline, minute)


def _labels(drama):
    return {c.label for c in drama.explanation.contributors}


def test_late_game_adds_bonus():
    early = _drama([], Scoreline(1, 1), minute=30.0)
    late = _drama([], Scoreline(1, 1), minute=85.0)
    assert "late_game" not in _labels(early)
    assert "late_game" in _labels(late)
    assert late.value > early.value


def test_narrow_margin_bonus_applies_for_draw_and_one_goal():
    assert "narrow_margin" in _labels(_drama([], Scoreline(0, 0), 50.0))
    assert "narrow_margin" in _labels(_drama([], Scoreline(2, 1), 50.0))
    assert "narrow_margin" not in _labels(_drama([], Scoreline(3, 0), 50.0))


def test_red_card_amplifies_even_when_old():
    # Red card at minute 20 still counts via full-match scan at minute 85.
    rc = red_card(20.0, Side.HOME, seq=1)
    drama = _drama([shot(84.0, Side.HOME, seq=2)], Scoreline(1, 1), 85.0,
                   all_events=[rc, shot(84.0, Side.HOME, seq=2)])
    assert "red_cards" in _labels(drama)


def test_recent_goal_bonus_from_window_only():
    drama = _drama([goal(84.0, Side.HOME, seq=1)], Scoreline(2, 1), 85.0)
    assert "recent_goals" in _labels(drama)


def test_bonuses_are_capped():
    cards = [red_card(10.0 + i, Side.HOME, seq=i) for i in range(5)]
    drama = _drama([], Scoreline(1, 1), 85.0, all_events=cards)
    red_contribution = next(c.value for c in drama.explanation.contributors if c.label == "red_cards")
    # cap is 2 * 14.0 = 28.0 by default config
    assert red_contribution == pytest.approx(28.0)


def test_explanation_additive_and_clamped():
    drama = _drama([goal(84.0, Side.HOME, seq=1)], Scoreline(1, 1), 88.0)
    assert drama.explanation.total_contribution() == pytest.approx(drama.explanation.raw_value)
    assert 0.0 <= drama.value <= 100.0
    assert "pulse_base" in _labels(drama)
