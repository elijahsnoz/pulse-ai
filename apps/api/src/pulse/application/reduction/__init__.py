"""Reduction — the source-agnostic pipeline core.

``MatchReducer`` folds ``MatchFrame``s into ``MatchSnapshot``s plus a deterministic
``TimelineEvent`` stream. Live, replay and tests all flow through this one path.
"""
from .config import DEFAULT_TIMELINE_CONFIG, TimelineConfig
from .reducer import MatchReducer, ReductionResult, ReductionStep, reduce_frames
from .timeline import (
    CardShown,
    EmotionChanged,
    GoalScored,
    MomentumShiftSignalled,
    PhaseChanged,
    PulseMoment,
    TimelineEvent,
    TimelineKind,
)

__all__ = [
    "DEFAULT_TIMELINE_CONFIG",
    "TimelineConfig",
    "MatchReducer",
    "ReductionResult",
    "ReductionStep",
    "reduce_frames",
    "CardShown",
    "EmotionChanged",
    "GoalScored",
    "MomentumShiftSignalled",
    "PhaseChanged",
    "PulseMoment",
    "TimelineEvent",
    "TimelineKind",
]
