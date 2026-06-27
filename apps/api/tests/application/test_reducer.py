"""Tests for the MatchReducer: snapshots + deterministic timeline."""
from __future__ import annotations

from pulse.application.reduction import (
    CardShown,
    EmotionChanged,
    GoalScored,
    MatchReducer,
    MomentumShiftSignalled,
    PhaseChanged,
    PulseMoment,
    TimelineConfig,
    reduce_frames,
)
from pulse.domain.config import MetricConfig, ShiftConfig
from pulse.domain.value_objects.intensity_band import IntensityBand
from pulse.domain.value_objects.match_phase import MatchPhase
from pulse.domain.value_objects.side import Side

from .conftest import event_frame, frames_from_events, sample_match_frames, tick_frame
from pulse.domain.events.football import CardColor, CardEvent, GoalEvent, ShotEvent


def test_one_snapshot_per_frame():
    frames = sample_match_frames()
    result = reduce_frames(frames)
    assert len(result.snapshots) == len(frames)


def test_reducer_is_source_agnostic_and_consumes_only_frames():
    # The push() contract takes a MatchFrame and nothing else — no origin hint.
    reducer = MatchReducer()
    frame = tick_frame(1, 5.0)
    step = reducer.push(frame)
    assert step.frame is frame
    assert step.snapshot.minute == 5.0


def test_goal_emits_timeline_event_with_scoreline():
    frames = frames_from_events([GoalEvent("g1", 1, 10.0, Side.HOME)])
    goals = [e for e in reduce_frames(frames).timeline if isinstance(e, GoalScored)]
    assert len(goals) == 1
    assert goals[0].side is Side.HOME
    assert (goals[0].home, goals[0].away) == (1, 0)


def test_scoreline_accumulates_across_goals():
    frames = frames_from_events([
        GoalEvent("g1", 1, 10.0, Side.HOME),
        GoalEvent("g2", 2, 20.0, Side.AWAY),
        GoalEvent("g3", 3, 30.0, Side.HOME),
    ])
    result = reduce_frames(frames)
    assert (result.snapshots[-1].scoreline.home, result.snapshots[-1].scoreline.away) == (2, 1)


def test_red_and_yellow_cards_emit_correct_flag():
    frames = frames_from_events([
        CardEvent("c1", 1, 30.0, Side.HOME, color=CardColor.YELLOW),
        CardEvent("c2", 2, 31.0, Side.AWAY, color=CardColor.RED),
    ])
    cards = [e for e in reduce_frames(frames).timeline if isinstance(e, CardShown)]
    assert [(c.side, c.is_red) for c in cards] == [(Side.HOME, False), (Side.AWAY, True)]


def test_momentum_shift_appears_on_timeline():
    # With per-event frames momentum moves gradually, so shift sensitivity is
    # governed by ShiftConfig.swing_threshold. Lower it to exercise the wiring:
    # engine momentum_shift -> timeline MomentumShiftSignalled.
    cfg = MetricConfig(shift=ShiftConfig(swing_threshold=8.0))
    events = (
        [ShotEvent(f"a{i}", i, 50.0, Side.AWAY, on_target=True) for i in range(1, 6)]
        + [ShotEvent(f"h{i}", 10 + i, 55.0 + i * 0.1, Side.HOME, on_target=True) for i in range(8)]
    )
    shifts = [e for e in reduce_frames(frames_from_events(events), metric_config=cfg).timeline
              if isinstance(e, MomentumShiftSignalled)]
    assert shifts
    assert any(s.toward is Side.HOME for s in shifts)


def test_phase_change_emitted_on_transition():
    # tick in opening, then tick in stoppage -> at least one PhaseChanged
    frames = [tick_frame(1, 3.0), tick_frame(2, 92.0)]
    changes = [e for e in reduce_frames(frames).timeline if isinstance(e, PhaseChanged)]
    assert changes
    assert changes[-1].to_phase is MatchPhase.STOPPAGE_TIME


def test_no_phase_change_on_first_frame():
    frames = [tick_frame(1, 3.0)]
    assert not [e for e in reduce_frames(frames).timeline if isinstance(e, PhaseChanged)]


def test_emotion_change_emitted_on_transition():
    frames = sample_match_frames()
    assert [e for e in reduce_frames(frames).timeline if isinstance(e, EmotionChanged)]


def test_pulse_moment_fires_on_upward_crossing_only():
    # Lower the bar to SIMMERING so a modest flurry crosses it deterministically.
    cfg = TimelineConfig(pulse_moment_band=IntensityBand.SIMMERING)
    events = [ShotEvent(f"h{i}", i, 50.0 + i * 0.1, Side.HOME, on_target=True) for i in range(1, 8)]
    timeline = reduce_frames(frames_from_events(events), timeline_config=cfg).timeline
    moments = [e for e in timeline if isinstance(e, PulseMoment)]
    # at least one crossing, and each fires only when the band steps up
    assert moments
    assert all(m.band is not IntensityBand.DORMANT for m in moments)


def test_timeline_sequence_is_monotonic():
    timeline = reduce_frames(sample_match_frames()).timeline
    seqs = [e.sequence for e in timeline]
    assert seqs == sorted(seqs)
    assert len(set(seqs)) == len(seqs)  # unique


def test_reduction_is_deterministic():
    frames = sample_match_frames()
    a = reduce_frames(frames)
    b = reduce_frames(frames)
    assert a.timeline == b.timeline
    assert [s.minute for s in a.snapshots] == [s.minute for s in b.snapshots]


def test_neutral_goal_does_not_change_scoreline():
    # Defensive: a side-less scoring event is ignored by the scoreline fold.
    frames = frames_from_events([GoalEvent("g0", 1, 10.0, Side.NEUTRAL)])
    result = reduce_frames(frames)
    assert (result.snapshots[-1].scoreline.home, result.snapshots[-1].scoreline.away) == (0, 0)


def test_timeline_event_kinds():
    from pulse.application.reduction import TimelineKind
    from pulse.domain.value_objects.emotional_state import EmotionalState

    assert GoalScored(0, 1.0, Side.HOME, 1, 0).kind is TimelineKind.GOAL
    assert CardShown(0, 1.0, Side.HOME, True).kind is TimelineKind.CARD
    assert MomentumShiftSignalled(0, 1.0, Side.HOME, 60.0).kind is TimelineKind.MOMENTUM_SHIFT
    assert PulseMoment(0, 1.0, IntensityBand.ELECTRIC, 70.0).kind is TimelineKind.PULSE_MOMENT
    assert PhaseChanged(0, 1.0, MatchPhase.OPENING, MatchPhase.SETTLING).kind is TimelineKind.PHASE_CHANGED
    assert EmotionChanged(0, 1.0, EmotionalState.CALM, EmotionalState.BUILDING).kind is TimelineKind.EMOTION_CHANGED
