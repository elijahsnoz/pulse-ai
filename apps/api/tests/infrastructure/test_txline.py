"""Tests for the TxLineProvider normalization (live source parity)."""
from __future__ import annotations

import pytest

from pulse.application.frames import FrameKind
from pulse.infrastructure.providers import TxLineProvider, normalize_txline_event
from pulse.infrastructure.providers.txline import TxLineNormalizationError
from pulse.domain.events.football import CardColor, CardEvent, GoalEvent, ShotEvent
from pulse.domain.value_objects.side import Side


def test_normalize_each_type():
    assert normalize_txline_event({"id": "1", "minute": 10, "type": "goal", "team": "home"}, 1) \
        == GoalEvent("1", 1, 10.0, Side.HOME)
    shot = normalize_txline_event({"id": "2", "minute": 5, "type": "shot",
                                   "team": "away", "on_target": True}, 2)
    assert shot == ShotEvent("2", 2, 5.0, Side.AWAY, on_target=True)
    red = normalize_txline_event({"id": "3", "minute": 70, "type": "card",
                                  "team": "home", "card": "red"}, 3)
    assert red == CardEvent("3", 3, 70.0, Side.HOME, color=CardColor.RED)


@pytest.mark.parametrize(
    "raw_type,expected_kind",
    [
        ("attack", "attack"),
        ("dangerous_attack", "dangerous_attack"),
        ("corner", "corner"),
        ("free_kick", "free_kick"),
        ("substitution", "substitution"),
    ],
)
def test_normalize_covers_all_simple_types(raw_type, expected_kind):
    ev = normalize_txline_event(
        {"id": "1", "minute": 12, "type": raw_type, "team": "neutral"}, 1
    )
    assert ev.kind == expected_kind
    assert ev.side is Side.NEUTRAL


def test_normalize_yellow_card_default():
    ev = normalize_txline_event(
        {"id": "1", "minute": 30, "type": "card", "team": "home"}, 1
    )
    assert ev == CardEvent("1", 1, 30.0, Side.HOME, color=CardColor.YELLOW)


def test_normalize_unknown_type_raises():
    with pytest.raises(TxLineNormalizationError):
        normalize_txline_event({"id": "x", "minute": 1, "type": "ufo", "team": "home"}, 1)


def test_provider_dedupes_and_orders_by_minute():
    raw = [
        {"id": "b", "minute": 20.0, "type": "shot", "team": "home"},
        {"id": "a", "minute": 10.0, "type": "goal", "team": "home"},
        {"id": "a", "minute": 10.0, "type": "goal", "team": "home"},  # dup id
    ]
    frames = list(TxLineProvider(raw).frames())
    assert [f.provider_event_id for f in frames] == ["a", "b"]
    assert [f.sequence for f in frames] == [1, 2]


def test_provider_interleaves_ticks():
    raw = [{"id": "g", "minute": 2.0, "type": "goal", "team": "home"}]
    frames = list(TxLineProvider(raw, tick_interval=0.5).frames())
    kinds = [f.kind for f in frames]
    assert kinds.count(FrameKind.TICK) == 4  # ticks at 0.5,1.0,1.5,2.0
    assert FrameKind.EVENT in kinds
    # sequences are gap-free
    assert [f.sequence for f in frames] == list(range(1, len(frames) + 1))


def test_provider_without_tick_interval_emits_only_events():
    raw = [{"id": "g", "minute": 2.0, "type": "goal", "team": "home"}]
    frames = list(TxLineProvider(raw).frames())
    assert all(f.kind is FrameKind.EVENT for f in frames)
