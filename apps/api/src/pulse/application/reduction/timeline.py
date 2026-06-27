"""TimelineEvents — the deterministic stream of narrative moments.

Purpose
    As the reducer folds frames into snapshots it also surfaces the *transitions*
    worth telling a story about: goals, cards, momentum swings, intensity spikes,
    phase changes and mood changes. Downstream systems (Story Engine, Notification
    Engine, the animated timeline UI) consume THESE rather than re-deriving
    transitions independently — one source of truth for "what just happened".

Design
    Each event is an immutable, value-typed record carrying a monotonic
    ``sequence`` (deterministic emission order) and the ``minute`` it occurred.
    They are intentionally independent dataclasses unified by the ``TimelineEvent``
    union and a ``kind`` discriminator, so each is strongly typed yet uniformly
    switchable/serialisable later.

Invariants
    * Frozen / immutable; equality by value.
    * Produced deterministically by the reducer (same frames -> same timeline).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pulse.domain.value_objects.emotional_state import EmotionalState
from pulse.domain.value_objects.intensity_band import IntensityBand
from pulse.domain.value_objects.match_phase import MatchPhase
from pulse.domain.value_objects.side import Side


class TimelineKind(Enum):
    """Discriminator for the timeline event variants."""

    GOAL = "goal"
    CARD = "card"
    MOMENTUM_SHIFT = "momentum_shift"
    PULSE_MOMENT = "pulse_moment"
    PHASE_CHANGED = "phase_changed"
    EMOTION_CHANGED = "emotion_changed"


@dataclass(frozen=True)
class GoalScored:
    """A goal went in; carries the resulting scoreline."""

    sequence: int
    minute: float
    side: Side
    home: int
    away: int

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.GOAL


@dataclass(frozen=True)
class CardShown:
    """A booking; ``is_red`` marks a dismissal."""

    sequence: int
    minute: float
    side: Side
    is_red: bool

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.CARD


@dataclass(frozen=True)
class MomentumShiftSignalled:
    """Momentum swung past the configured threshold (mirrors the domain signal)."""

    sequence: int
    minute: float
    toward: Side
    delta: float

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.MOMENTUM_SHIFT


@dataclass(frozen=True)
class PulseMoment:
    """Match intensity crossed UP into a high band — a spike worth surfacing."""

    sequence: int
    minute: float
    band: IntensityBand
    pulse: float

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.PULSE_MOMENT


@dataclass(frozen=True)
class PhaseChanged:
    """The narrative MatchPhase transitioned."""

    sequence: int
    minute: float
    from_phase: MatchPhase
    to_phase: MatchPhase

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.PHASE_CHANGED


@dataclass(frozen=True)
class EmotionChanged:
    """The deterministic EmotionalState transitioned."""

    sequence: int
    minute: float
    from_state: EmotionalState
    to_state: EmotionalState

    @property
    def kind(self) -> TimelineKind:
        return TimelineKind.EMOTION_CHANGED


# The closed set of timeline events the reducer can emit.
TimelineEvent = (
    GoalScored
    | CardShown
    | MomentumShiftSignalled
    | PulseMoment
    | PhaseChanged
    | EmotionChanged
)
