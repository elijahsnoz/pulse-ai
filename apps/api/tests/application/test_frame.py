"""Tests for the MatchFrame canonical unit and its invariants."""
from __future__ import annotations

import pytest

from pulse.application.frames import FrameKind, MatchFrame
from pulse.domain.events.football import GoalEvent
from pulse.domain.value_objects.side import Side


def _goal(minute=83.0, side=Side.HOME, seq=4):
    return GoalEvent(event_id="g1", sequence=seq, minute=minute, side=side)


def test_event_frame_defaults_minute_to_event_minute():
    frame = MatchFrame.event_frame(sequence=4, event=_goal(83.0), provider_event_id="p1")
    assert frame.kind is FrameKind.EVENT
    assert frame.is_event and not frame.is_tick
    assert frame.match_minute == 83.0
    assert frame.provider_event_id == "p1"


def test_event_frame_can_override_minute():
    frame = MatchFrame.event_frame(sequence=4, event=_goal(83.0), match_minute=84.5)
    assert frame.match_minute == 84.5


def test_tick_frame_carries_only_minute():
    frame = MatchFrame.tick_frame(sequence=10, match_minute=45.25)
    assert frame.kind is FrameKind.TICK
    assert frame.is_tick and not frame.is_event
    assert frame.event is None
    assert frame.provider_event_id is None


def test_event_frame_requires_event():
    with pytest.raises(ValueError):
        MatchFrame(sequence=1, match_minute=10.0, kind=FrameKind.EVENT, event=None)


def test_tick_frame_rejects_event():
    with pytest.raises(ValueError):
        MatchFrame(sequence=1, match_minute=10.0, kind=FrameKind.TICK, event=_goal())


def test_tick_frame_rejects_provider_id():
    with pytest.raises(ValueError):
        MatchFrame(
            sequence=1, match_minute=10.0, kind=FrameKind.TICK,
            provider_event_id="p1",
        )


def test_negative_minute_rejected():
    with pytest.raises(ValueError):
        MatchFrame.tick_frame(sequence=1, match_minute=-0.1)


def test_frames_are_value_equal():
    a = MatchFrame.event_frame(sequence=4, event=_goal(), provider_event_id="p1")
    b = MatchFrame.event_frame(sequence=4, event=_goal(), provider_event_id="p1")
    assert a == b
