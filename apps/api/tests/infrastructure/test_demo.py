"""Tests for the scripted demo match tape."""
from __future__ import annotations

from pulse.application.frames import FrameKind
from pulse.application.reduction import GoalScored, reduce_frames
from pulse.infrastructure.demo import demo_match_frames


def test_demo_is_deterministic():
    assert demo_match_frames() == demo_match_frames()


def test_demo_has_dense_ticks_and_events():
    frames = demo_match_frames()
    ticks = [f for f in frames if f.kind is FrameKind.TICK]
    events = [f for f in frames if f.kind is FrameKind.EVENT]
    assert len(ticks) > 150  # 0.5-min cadence over ~95'
    assert len(events) >= 15


def test_demo_sequences_are_gap_free_and_sorted_by_minute():
    frames = demo_match_frames()
    assert [f.sequence for f in frames] == list(range(1, len(frames) + 1))
    minutes = [f.match_minute for f in frames]
    assert minutes == sorted(minutes)


def test_demo_produces_a_dramatic_scoreline():
    result = reduce_frames(demo_match_frames())
    final = result.snapshots[-1].scoreline
    # script: Argentina 2 - 1 France (goals at 11', 38', 88')
    assert (final.home, final.away) == (2, 1)
    goals = [e for e in result.timeline if isinstance(e, GoalScored)]
    assert len(goals) == 3
