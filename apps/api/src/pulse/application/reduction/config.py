"""TimelineConfig — tuning for timeline-event derivation.

Purpose
    Application-layer thresholds for which transitions become TimelineEvents.
    Kept OUT of the frozen Module 1 ``MetricConfig`` so the v1.0 domain contract
    is untouched; timeline framing is an application concern.

Invariants
    * Frozen / immutable.
    * No magic numbers in the reducer — they live here.
"""
from __future__ import annotations

from dataclasses import dataclass

from pulse.domain.value_objects.intensity_band import IntensityBand


@dataclass(frozen=True)
class TimelineConfig:
    """Thresholds governing TimelineEvent emission."""

    # A Pulse Moment fires when the pulse band crosses UP into this band or higher.
    pulse_moment_band: IntensityBand = IntensityBand.ELECTRIC


DEFAULT_TIMELINE_CONFIG = TimelineConfig()
