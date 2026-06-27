"""Integration tests for the MetricEngine orchestrator."""
from __future__ import annotations

from pulse.domain.config import DEFAULT_CONFIG
from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.match_state import MatchState
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from .conftest import shot


def test_evaluate_returns_fully_populated_state(home_siege):
    engine = MetricEngine()
    state = engine.evaluate(
        events=home_siege, minute=84.0, scoreline=Scoreline(1, 1)
    )
    assert isinstance(state, MatchState)
    assert state.minute == 84.0
    assert state.momentum.direction is Side.HOME
    assert state.pressure_home.value > state.pressure_away.value
    assert state.pulse.value > 0
    assert state.drama.value > 0
    assert state.confidence.value >= 0
    assert state.phase is not None
    assert state.emotion is not None
    # fan-facing experience layer is populated and consistent with the metrics
    assert state.fan_read is not None
    assert 50 <= state.fan_read.heartbeat_bpm <= 180
    assert 0 <= state.fan_read.drama_stars <= 5


def test_engine_exposes_its_config():
    engine = MetricEngine()
    assert engine.config is DEFAULT_CONFIG


def test_momentum_shift_detected_against_previous_state():
    engine = MetricEngine()
    # First tick: away pressing.
    away_events = [shot(50.0, Side.AWAY, on_target=True, seq=i) for i in range(1, 6)]
    first = engine.evaluate(events=away_events, minute=51.0, scoreline=Scoreline(0, 0))
    assert first.momentum_shift is None

    # Second tick a few minutes later: home now pressing hard => big swing.
    home_events = away_events + [
        shot(55.0 + i * 0.1, Side.HOME, on_target=True, seq=10 + i) for i in range(8)
    ]
    second = engine.evaluate(
        events=home_events, minute=56.0, scoreline=Scoreline(0, 0), previous=first
    )
    assert second.momentum_shift is not None
    assert second.momentum_shift.toward is Side.HOME


def test_accepts_generator_inputs_without_consuming_issues():
    engine = MetricEngine()
    gen = (shot(59.0, Side.HOME, on_target=True, seq=i) for i in range(1, 4))
    state = engine.evaluate(events=gen, minute=60.0, scoreline=Scoreline(0, 0))
    assert state.momentum.direction is Side.HOME
