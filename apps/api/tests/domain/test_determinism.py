"""Determinism suite — the core guarantee that makes Replay reproducible.

Same inputs (in any order) must yield byte-identical derived state.
"""
from __future__ import annotations

from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.match_state import MatchState
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from .conftest import corner, dangerous, goal, shot


def _state_signature(state: MatchState) -> tuple:
    """A fully-comparable signature of every derived number/enum."""
    return (
        state.pulse.value,
        state.pressure_home.value,
        state.pressure_away.value,
        state.momentum.value,
        state.momentum.direction,
        state.drama.value,
        state.confidence.value,
        state.phase,
        state.emotion,
        state.fan_read.pulse_band,
        state.fan_read.heartbeat_bpm,
        state.fan_read.drama_stars,
        state.fan_read.momentum_band,
        state.fan_read.narration_certainty,
        tuple((c.label, c.value) for c in state.momentum.explanation.contributors),
        tuple((c.label, c.value) for c in state.drama.explanation.contributors),
    )


def _build_match():
    return [
        shot(76.0, Side.HOME, on_target=True, seq=1),
        corner(77.0, Side.HOME, seq=2),
        dangerous(78.0, Side.AWAY, seq=3),
        goal(79.0, Side.HOME, seq=4),
        shot(80.0, Side.AWAY, on_target=True, seq=5),
        shot(81.0, Side.HOME, seq=6),
    ]


def test_repeated_evaluation_is_identical():
    engine = MetricEngine()
    events = _build_match()
    a = engine.evaluate(events=events, minute=82.0, scoreline=Scoreline(2, 1))
    b = engine.evaluate(events=events, minute=82.0, scoreline=Scoreline(2, 1))
    assert _state_signature(a) == _state_signature(b)


def test_input_order_does_not_change_output():
    engine = MetricEngine()
    events = _build_match()
    shuffled = list(reversed(events))
    a = engine.evaluate(events=events, minute=82.0, scoreline=Scoreline(2, 1))
    b = engine.evaluate(events=shuffled, minute=82.0, scoreline=Scoreline(2, 1))
    assert _state_signature(a) == _state_signature(b)


def test_two_independent_engines_agree():
    events = _build_match()
    a = MetricEngine().evaluate(events=events, minute=82.0, scoreline=Scoreline(2, 1))
    b = MetricEngine().evaluate(events=events, minute=82.0, scoreline=Scoreline(2, 1))
    assert _state_signature(a) == _state_signature(b)


def test_replay_sequence_is_reproducible():
    """Replaying the same minute-by-minute tape twice yields identical states."""
    events = _build_match()

    def run() -> list[tuple]:
        engine = MetricEngine()
        previous = None
        signatures = []
        for minute in range(76, 90):
            state = engine.evaluate(
                events=events, minute=float(minute),
                scoreline=Scoreline(2, 1), previous=previous,
            )
            signatures.append(_state_signature(state))
            previous = state
        return signatures

    assert run() == run()
