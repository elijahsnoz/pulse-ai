"""MatchState — the complete derived intelligence snapshot for one moment.

Purpose
    Bundle everything the engine derives at a given minute into one immutable
    value: the branded metrics, phase, emotional state and any momentum-shift
    signal. This is the payload every later subsystem (WebSocket, Story Engine,
    Recap) consumes.

Invariants
    * Frozen / immutable.
    * Fully determined by (events, minute, scoreline, config) — reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..events.signals import MomentumShifted
from .emotional_state import EmotionalState
from .fan_read import FanRead
from .match_phase import MatchPhase
from .metrics import (
    ConfidenceScore,
    DramaIndex,
    MomentumVector,
    PressureIndex,
    PulseScore,
)
from .scoreline import Scoreline


@dataclass(frozen=True)
class MatchState:
    """Immutable snapshot of all derived match intelligence at one minute."""

    minute: float
    scoreline: Scoreline
    pulse: PulseScore
    pressure_home: PressureIndex
    pressure_away: PressureIndex
    momentum: MomentumVector
    drama: DramaIndex
    confidence: ConfidenceScore
    phase: MatchPhase
    emotion: EmotionalState
    fan_read: FanRead
    momentum_shift: MomentumShifted | None = None
