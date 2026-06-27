"""Tests for the PhaseResolver and EmotionResolver (deterministic mappings)."""
from __future__ import annotations

import pytest

from pulse.domain.services.emotion import EmotionResolver
from pulse.domain.services.phase import PhaseResolver
from pulse.domain.value_objects.emotional_state import EmotionalState
from pulse.domain.value_objects.explanation import Explanation
from pulse.domain.value_objects.match_phase import MatchPhase
from pulse.domain.value_objects.metrics import (
    DramaIndex,
    MomentumVector,
    PulseScore,
)
from pulse.domain.value_objects.side import Side


def _exp(metric, value):
    return Explanation(metric=metric, value=value, raw_value=value, contributors=())


def momentum(value):
    direction = Side.HOME if value > 12 else Side.AWAY if value < -12 else Side.NEUTRAL
    return MomentumVector(value=value, direction=direction, explanation=_exp("m", value))


def drama(value):
    return DramaIndex(value=value, explanation=_exp("d", value))


def pulse(value):
    return PulseScore(value=value, explanation=_exp("p", value))


# ---- Phase -----------------------------------------------------------------

@pytest.mark.parametrize(
    "minute,mom,dram,expected",
    [
        (5.0, 0.0, 0.0, MatchPhase.OPENING),
        (18.0, 0.0, 0.0, MatchPhase.SETTLING),
        (45.0, 0.0, 0.0, MatchPhase.MID_GAME),
        (45.0, 60.0, 0.0, MatchPhase.MOMENTUM_WINDOW),       # metric override mid-game
        (82.0, 0.0, 10.0, MatchPhase.FINAL_PUSH),
        (72.0, 0.0, 80.0, MatchPhase.CRITICAL_PHASE),        # late + high drama
        (92.0, 90.0, 90.0, MatchPhase.STOPPAGE_TIME),        # stoppage wins over all
        (8.0, 70.0, 0.0, MatchPhase.MOMENTUM_WINDOW),        # surge in opening minutes
    ],
)
def test_phase_resolution(minute, mom, dram, expected):
    resolver = PhaseResolver()
    assert resolver.resolve(minute, momentum(mom), drama(dram)) is expected


def test_critical_requires_both_late_and_high_drama():
    resolver = PhaseResolver()
    # high drama but too early => not critical
    assert resolver.resolve(50.0, momentum(0.0), drama(90.0)) is MatchPhase.MID_GAME


# ---- Emotion ---------------------------------------------------------------

@pytest.mark.parametrize(
    "p,mom,dram,expected",
    [
        (10.0, 0.0, 10.0, EmotionalState.CALM),
        (90.0, 20.0, 90.0, EmotionalState.EXPLOSIVE),
        (60.0, 70.0, 80.0, EmotionalState.DESPERATE),     # high drama + directional siege
        (70.0, 5.0, 50.0, EmotionalState.CHAOTIC),         # high pulse, balanced
        (50.0, 70.0, 40.0, EmotionalState.DOMINANT),       # one side controlling
        (50.0, 10.0, 40.0, EmotionalState.BUILDING),       # pulse rising
        (33.0, 10.0, 30.0, EmotionalState.BALANCED),       # the residual case
    ],
)
def test_emotion_resolution(p, mom, dram, expected):
    resolver = EmotionResolver()
    assert resolver.resolve(pulse(p), momentum(mom), drama(dram)) is expected


def test_emotion_is_total_over_a_grid():
    """Every combination must resolve to some state (never raises / None)."""
    resolver = EmotionResolver()
    for p in range(0, 101, 10):
        for m in range(0, 101, 10):
            for d in range(0, 101, 10):
                result = resolver.resolve(pulse(p), momentum(m), drama(d))
                assert isinstance(result, EmotionalState)
