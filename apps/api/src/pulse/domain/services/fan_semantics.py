"""FanSemantics — derive the fan-facing ``FanRead`` from the raw metrics.

Purpose
    The deterministic "experience layer". It owns the translation from numbers to
    feeling (bands, heartbeat BPM, drama stars, certainty tier) so that the rules
    for "what is intense" live in the domain, beside the metrics, and stay
    config-driven — never duplicated in the frontend.

Inputs
    The branded metric value objects (Pulse, Drama, Momentum, both Pressures,
    Confidence).

Outputs
    A ``FanRead`` bundle.

Invariants
    * Pure & deterministic; no prose (that is the Story Engine's job).
    * All thresholds and the BPM range come from ``FanConfig`` — no magic numbers.
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..numeric import clamp
from ..value_objects.certainty import CertaintyTier
from ..value_objects.fan_read import FanRead
from ..value_objects.intensity_band import IntensityBand
from ..value_objects.metrics import (
    ConfidenceScore,
    DramaIndex,
    MomentumVector,
    PressureIndex,
    PulseScore,
)


class FanSemantics:
    """Maps raw metric values to fan-felt presentation primitives."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def derive(
        self,
        pulse: PulseScore,
        drama: DramaIndex,
        momentum: MomentumVector,
        pressure_home: PressureIndex,
        pressure_away: PressureIndex,
        confidence: ConfidenceScore,
    ) -> FanRead:
        """Return the ``FanRead`` bundle for the current metrics."""
        cfg = self._config.fan
        return FanRead(
            pulse_band=IntensityBand.from_value(pulse.value, cfg.pulse_band_thresholds),
            heartbeat_bpm=self._heartbeat_bpm(pulse),
            drama_band=IntensityBand.from_value(drama.value, cfg.drama_band_thresholds),
            drama_stars=self._drama_stars(drama),
            momentum_band=IntensityBand.from_value(
                momentum.magnitude, cfg.momentum_band_thresholds
            ),
            pressure_home_band=IntensityBand.from_value(
                pressure_home.value, cfg.pressure_band_thresholds
            ),
            pressure_away_band=IntensityBand.from_value(
                pressure_away.value, cfg.pressure_band_thresholds
            ),
            narration_certainty=CertaintyTier.from_confidence(
                confidence.value, cfg.certainty_thresholds
            ),
        )

    def _heartbeat_bpm(self, pulse: PulseScore) -> int:
        """Map Pulse [0, 100] linearly onto the configured BPM range."""
        cfg = self._config.fan
        span = cfg.heartbeat_max_bpm - cfg.heartbeat_min_bpm
        bpm = cfg.heartbeat_min_bpm + span * clamp(pulse.value, 0.0, 100.0) / 100.0
        return round(bpm)

    def _drama_stars(self, drama: DramaIndex) -> int:
        """Number of star thresholds the Drama Index meets (0-5)."""
        return sum(1 for cut in self._config.fan.drama_star_thresholds if drama.value >= cut)
