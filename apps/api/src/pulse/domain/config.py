"""MetricConfig — the single home for every tunable constant in the engine.

Purpose
    Centralise ALL weights, scales and thresholds so no service contains a magic
    number. Tuning the product's feel (how twitchy the heartbeat is, when a
    "Critical Phase" begins) is a config change, never a code change.

Inputs
    Construct ``MetricConfig()`` for defaults, or override any nested section,
    e.g. ``MetricConfig(window=WindowConfig(window_minutes=15))``.

Invariants
    * Frozen / immutable — a config instance is a stable, shareable value.
    * Pure data. No behaviour beyond ``weight_for`` lookups.
    * Two engines built from equal configs produce identical outputs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping

# Attacking "danger weight" per event kind. Keys are sport-agnostic ``kind``
# strings emitted by event subclasses; unknown kinds resolve to 0.0 (no impact).
DEFAULT_DANGER_WEIGHTS: Mapping[str, float] = {
    "goal": 1.0,
    "penalty_won": 0.9,
    "shot_on_target": 0.7,
    "shot": 0.4,
    "dangerous_attack": 0.3,
    "corner": 0.25,
    "free_kick": 0.15,
    "attack": 0.1,
    # Non-attacking events contribute no momentum (listed for clarity).
    "card": 0.0,
    "substitution": 0.0,
}


@dataclass(frozen=True)
class WindowConfig:
    """Sliding-window and time-decay parameters."""

    window_minutes: float = 10.0
    half_life_minutes: float = 5.0


@dataclass(frozen=True)
class MomentumConfig:
    """Momentum Vector tuning. ``scale`` maps net weight-units to [-100, 100]."""

    scale: float = 14.0
    balanced_band: float = 12.0  # |value| <= band => no clear direction


@dataclass(frozen=True)
class PressureConfig:
    """Pressure Index tuning. ``scale`` maps one side's danger to [0, 100]."""

    scale: float = 22.0


@dataclass(frozen=True)
class PulseConfig:
    """Pulse Score tuning — a blend of density, volatility and scoreline tension."""

    density_weight: float = 7.0
    volatility_weight: float = 0.6
    tension_weight: float = 30.0
    volatility_buckets: int = 4


@dataclass(frozen=True)
class DramaConfig:
    """Drama Index tuning — Pulse amplified by match stakes (additive bonuses)."""

    pulse_weight: float = 0.7
    late_game_minute: float = 75.0
    late_game_bonus: float = 12.0
    narrow_margin_max: int = 1
    narrow_margin_bonus: float = 10.0
    red_card_bonus: float = 14.0
    red_card_cap: int = 2
    recent_goal_bonus: float = 16.0
    recent_goal_cap: int = 2


@dataclass(frozen=True)
class ConfidenceConfig:
    """Confidence Score tuning — confidence in the deterministic signal itself."""

    expected_events_per_window: float = 12.0
    density_weight: float = 0.3
    coverage_weight: float = 0.2
    consistency_weight: float = 0.3
    volatility_weight: float = 0.2
    volatility_buckets: int = 4
    volatility_reference: float = 50.0  # bucket-momentum stdev mapping to 0 contribution
    neutral_consistency: float = 0.5  # used when there is no directional signal


@dataclass(frozen=True)
class PhaseConfig:
    """Match Phase boundaries (minute-based plus metric-aware overrides)."""

    opening_end: float = 10.0
    settling_end: float = 25.0
    final_push_start: float = 80.0
    stoppage_start: float = 90.0
    critical_min_minute: float = 70.0
    critical_drama_threshold: float = 65.0
    momentum_window_threshold: float = 55.0


@dataclass(frozen=True)
class ShiftConfig:
    """Momentum-shift detection tuning.

    Independent of ``PhaseConfig`` so shift sensitivity can be tuned without
    moving phase boundaries. ``swing_threshold`` is the minimum absolute change
    in Momentum Vector value (between two evaluations) that emits a signal.
    """

    swing_threshold: float = 55.0


@dataclass(frozen=True)
class EmotionConfig:
    """Emotional State thresholds, evaluated in a fixed precedence (see resolver)."""

    calm_pulse_max: float = 25.0
    calm_drama_max: float = 25.0
    explosive_pulse_min: float = 75.0
    explosive_drama_min: float = 70.0
    desperate_drama_min: float = 72.0
    dominant_momentum_min: float = 55.0
    chaotic_pulse_min: float = 65.0
    chaotic_momentum_max: float = 30.0
    building_pulse_min: float = 40.0


@dataclass(frozen=True)
class FanConfig:
    """Experience-layer tuning — turns raw metric values into fan-felt semantics.

    Band thresholds are ascending 4-tuples mapping a 0-100 value onto the five
    ``IntensityBand`` members (Dormant -> Frenzied). Momentum bands read the
    unsigned magnitude. Everything here is presentation *meaning*, not styling.
    """

    pulse_band_thresholds: tuple[float, float, float, float] = (20.0, 40.0, 60.0, 80.0)
    pressure_band_thresholds: tuple[float, float, float, float] = (20.0, 40.0, 60.0, 80.0)
    drama_band_thresholds: tuple[float, float, float, float] = (20.0, 40.0, 60.0, 80.0)
    momentum_band_thresholds: tuple[float, float, float, float] = (15.0, 30.0, 50.0, 70.0)
    heartbeat_min_bpm: float = 50.0
    heartbeat_max_bpm: float = 180.0
    drama_star_thresholds: tuple[float, float, float, float, float] = (10.0, 30.0, 50.0, 70.0, 90.0)
    # Confidence below the first => Tentative, below the second => Measured, else Confident.
    certainty_thresholds: tuple[float, float] = (40.0, 70.0)


@dataclass(frozen=True)
class MetricConfig:
    """Aggregate configuration for the entire metric engine."""

    window: WindowConfig = field(default_factory=WindowConfig)
    momentum: MomentumConfig = field(default_factory=MomentumConfig)
    pressure: PressureConfig = field(default_factory=PressureConfig)
    pulse: PulseConfig = field(default_factory=PulseConfig)
    drama: DramaConfig = field(default_factory=DramaConfig)
    confidence: ConfidenceConfig = field(default_factory=ConfidenceConfig)
    phase: PhaseConfig = field(default_factory=PhaseConfig)
    emotion: EmotionConfig = field(default_factory=EmotionConfig)
    fan: FanConfig = field(default_factory=FanConfig)
    shift: ShiftConfig = field(default_factory=ShiftConfig)
    danger_weights: Mapping[str, float] = field(
        default_factory=lambda: dict(DEFAULT_DANGER_WEIGHTS)
    )

    def __post_init__(self) -> None:
        # Coerce danger_weights into a read-only mapping so a frozen config is
        # immutable all the way down (a plain dict would still be mutable, which
        # could silently corrupt the shared DEFAULT_CONFIG).
        if not isinstance(self.danger_weights, MappingProxyType):
            object.__setattr__(
                self, "danger_weights", MappingProxyType(dict(self.danger_weights))
            )

    def weight_for(self, kind: str) -> float:
        """Danger weight for an event ``kind``; unknown kinds resolve to 0.0."""
        return self.danger_weights.get(kind, 0.0)


# Shared default instance. Treat as immutable; build a new MetricConfig to tune.
DEFAULT_CONFIG = MetricConfig()
