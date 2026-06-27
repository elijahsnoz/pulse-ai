"""Tests for the event hierarchy and core value objects."""
from __future__ import annotations

import pytest

from pulse.domain.events.base import MatchEvent
from pulse.domain.events.football import (
    AttackEvent,
    CardColor,
    CardEvent,
    CornerEvent,
    DangerousAttackEvent,
    FreeKickEvent,
    GoalEvent,
    ShotEvent,
    SubstitutionEvent,
)
from pulse.domain.value_objects.emotional_state import EmotionalState
from pulse.domain.value_objects.explanation import Contributor, Explanation
from pulse.domain.value_objects.match_phase import MatchPhase
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side


def test_base_event_is_abstract():
    with pytest.raises(TypeError):
        MatchEvent(event_id="x", sequence=1, minute=1.0)  # type: ignore[abstract]


@pytest.mark.parametrize(
    "event,expected_kind",
    [
        (AttackEvent("a", 1, 1.0, Side.HOME), "attack"),
        (DangerousAttackEvent("a", 1, 1.0, Side.HOME), "dangerous_attack"),
        (ShotEvent("a", 1, 1.0, Side.HOME, on_target=False), "shot"),
        (ShotEvent("a", 1, 1.0, Side.HOME, on_target=True), "shot_on_target"),
        (CornerEvent("a", 1, 1.0, Side.HOME), "corner"),
        (FreeKickEvent("a", 1, 1.0, Side.HOME), "free_kick"),
        (GoalEvent("a", 1, 1.0, Side.HOME), "goal"),
        (CardEvent("a", 1, 1.0, Side.HOME), "card"),
        (SubstitutionEvent("a", 1, 1.0, Side.HOME), "substitution"),
    ],
)
def test_event_kinds(event, expected_kind):
    assert event.kind == expected_kind


def test_goal_is_tagged_scoring():
    assert "scoring" in GoalEvent("a", 1, 1.0, Side.HOME).tags


def test_red_card_is_dismissal_yellow_is_not():
    assert "dismissal" in CardEvent("a", 1, 1.0, Side.HOME, color=CardColor.RED).tags
    assert CardEvent("a", 1, 1.0, Side.HOME, color=CardColor.YELLOW).tags == frozenset()


def test_default_side_is_neutral_and_no_tags():
    e = AttackEvent("a", 1, 1.0)
    assert e.side is Side.NEUTRAL
    assert e.tags == frozenset()


def test_events_are_frozen():
    e = GoalEvent("a", 1, 1.0, Side.HOME)
    with pytest.raises(Exception):
        e.minute = 2.0  # type: ignore[misc]


@pytest.mark.parametrize(
    "side,expected_sign,expected_opponent",
    [
        (Side.HOME, 1, Side.AWAY),
        (Side.AWAY, -1, Side.HOME),
        (Side.NEUTRAL, 0, Side.NEUTRAL),
    ],
)
def test_side_sign_and_opponent(side, expected_sign, expected_opponent):
    assert side.sign == expected_sign
    assert side.opponent is expected_opponent


@pytest.mark.parametrize(
    "home,away,margin,is_draw,leader",
    [
        (0, 0, 0, True, Side.NEUTRAL),
        (2, 1, 1, False, Side.HOME),
        (1, 3, 2, False, Side.AWAY),
    ],
)
def test_scoreline(home, away, margin, is_draw, leader):
    s = Scoreline(home, away)
    assert s.margin == margin
    assert s.is_draw is is_draw
    assert s.leader is leader


def test_scoreline_rejects_negative():
    with pytest.raises(ValueError):
        Scoreline(-1, 0)


def test_explanation_additive_helpers():
    contribs = (
        Contributor("a", 10.0),
        Contributor("b", -4.0),
        Contributor("c", 2.0),
    )
    exp = Explanation("demo", value=8.0, raw_value=8.0, contributors=contribs)
    assert exp.total_contribution() == pytest.approx(8.0)
    top = exp.top_contributors(2)
    assert [c.label for c in top] == ["a", "b"]  # by descending magnitude


def test_phase_and_emotion_labels():
    assert MatchPhase.MOMENTUM_WINDOW.label == "Momentum Window"
    assert MatchPhase.STOPPAGE_TIME.label == "Stoppage Time"
    assert EmotionalState.EXPLOSIVE.label == "Explosive"
