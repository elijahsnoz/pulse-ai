"""Public API for the Pulse domain & metric engine.

Import the engine and the vocabulary you need from here:

    from pulse.domain import MetricEngine, Scoreline
    from pulse.domain.events.football import GoalEvent

Everything exported is deterministic and dependency-free.
"""
from __future__ import annotations

# Configuration
from .config import (
    DEFAULT_CONFIG,
    ConfidenceConfig,
    DramaConfig,
    EmotionConfig,
    FanConfig,
    MetricConfig,
    MomentumConfig,
    PhaseConfig,
    PressureConfig,
    PulseConfig,
    WindowConfig,
)

# NOTE: ``Match``, ``Team`` and ``MatchStatus`` are intentionally NOT exported
# here. They are PROVISIONAL (see entities/__init__.py) and excluded from the
# frozen v1.0 public contract — their shape is finalised in Module 2 alongside
# ingestion/persistence. Import them explicitly from ``pulse.domain.entities.*``
# if needed in the interim.

# Derived signals
from .events.signals import MomentumShifted

# Engine
from .services.engine import MetricEngine

# Value objects — branded metrics & supporting types
from .value_objects.certainty import CertaintyTier
from .value_objects.emotional_state import EmotionalState
from .value_objects.explanation import Contributor, Explanation
from .value_objects.fan_read import FanRead
from .value_objects.intensity_band import IntensityBand
from .value_objects.match_phase import MatchPhase
from .value_objects.match_state import MatchState
from .value_objects.metrics import (
    ConfidenceScore,
    DramaIndex,
    MomentumVector,
    PressureIndex,
    PulseScore,
)
from .value_objects.scoreline import Scoreline
from .value_objects.side import Side

__all__ = [
    "DEFAULT_CONFIG",
    "CertaintyTier",
    "ConfidenceConfig",
    "ConfidenceScore",
    "Contributor",
    "DramaConfig",
    "DramaIndex",
    "EmotionConfig",
    "EmotionalState",
    "Explanation",
    "FanConfig",
    "FanRead",
    "IntensityBand",
    "MatchPhase",
    "MatchState",
    "MetricConfig",
    "MetricEngine",
    "MomentumConfig",
    "MomentumShifted",
    "MomentumVector",
    "PhaseConfig",
    "PressureConfig",
    "PressureIndex",
    "PulseConfig",
    "PulseScore",
    "Scoreline",
    "Side",
    "WindowConfig",
]
