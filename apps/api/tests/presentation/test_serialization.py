"""Tests for wire serialization (snapshots + timeline), incl. product rules."""
from __future__ import annotations

import json

import pytest

from pulse.application.reduction.timeline import (
    CardShown,
    EmotionChanged,
    GoalScored,
    MomentumShiftSignalled,
    PhaseChanged,
    PulseMoment,
)
from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.emotional_state import EmotionalState
from pulse.domain.value_objects.intensity_band import IntensityBand
from pulse.domain.value_objects.match_phase import MatchPhase
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side
from pulse.presentation.serialization import (
    build_meta,
    snapshot_to_wire,
    timeline_to_wire,
)

from tests.domain.conftest import goal, shot


def _state():
    events = [shot(82.0, Side.HOME, on_target=True, seq=1), goal(83.0, Side.HOME, seq=2)]
    return MetricEngine().evaluate(events=events, minute=84.0, scoreline=Scoreline(1, 1))


def test_meta_shape():
    assert build_meta("Argentina", "France", "demo") == {
        "type": "meta", "match_id": "demo", "home": "Argentina", "away": "France",
    }


def test_snapshot_payload_is_json_safe_and_complete():
    wire = snapshot_to_wire(_state())
    json.dumps(wire)  # must not raise
    assert wire["type"] == "snapshot"
    for key in ("minute", "score", "pulse", "drama", "momentum", "pressure",
                "phase", "emotion", "certainty"):
        assert key in wire
    assert {"value", "band", "bpm"} <= wire["pulse"].keys()
    assert {"value", "band", "stars"} <= wire["drama"].keys()


def test_confidence_number_is_never_sent():
    # Product rule: confidence is internal; only the certainty TIER may surface.
    wire = snapshot_to_wire(_state())
    blob = json.dumps(wire).lower()
    assert "confidence" not in blob
    assert wire["certainty"] in {"Tentative", "Measured", "Confident"}


@pytest.mark.parametrize(
    "event,expected_kind,expected_icon",
    [
        (GoalScored(0, 83.0, Side.HOME, 1, 0), "goal", "⚽"),
        (CardShown(0, 66.0, Side.AWAY, True), "card", "🟥"),
        (CardShown(0, 30.0, Side.HOME, False), "card", "🟨"),
        (MomentumShiftSignalled(0, 55.0, Side.HOME, 60.0), "momentum_shift", "🔄"),
        (PulseMoment(0, 40.0, IntensityBand.ELECTRIC, 70.0), "pulse_moment", "🔥"),
        (PhaseChanged(0, 90.0, MatchPhase.FINAL_PUSH, MatchPhase.STOPPAGE_TIME),
         "phase_changed", "⏱️"),
        (EmotionChanged(0, 20.0, EmotionalState.CALM, EmotionalState.BUILDING),
         "emotion_changed", "🎭"),
    ],
)
def test_timeline_rendering(event, expected_kind, expected_icon):
    wire = timeline_to_wire(event, "Argentina", "France")
    assert wire["kind"] == expected_kind
    assert wire["icon"] == expected_icon
    assert wire["text"]
    json.dumps(wire)


def test_goal_text_uses_team_name_and_score():
    wire = timeline_to_wire(GoalScored(0, 11.0, Side.HOME, 1, 0), "Argentina", "France")
    assert "Argentina" in wire["text"] and "1-0" in wire["text"]


def test_neutral_side_renders_blank_team():
    # a side-less signal must not crash and yields an empty team name
    wire = timeline_to_wire(MomentumShiftSignalled(0, 50.0, Side.NEUTRAL, 60.0),
                            "Argentina", "France")
    assert wire["kind"] == "momentum_shift"
    assert wire["text"].endswith("to ")  # blank team
