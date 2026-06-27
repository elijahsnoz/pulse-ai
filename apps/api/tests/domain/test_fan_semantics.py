"""Tests for the deterministic fan-semantics (experience) layer."""
from __future__ import annotations

import pytest

from pulse.domain.config import DEFAULT_CONFIG, FanConfig, MetricConfig
from pulse.domain.services.fan_semantics import FanSemantics
from pulse.domain.value_objects.certainty import CertaintyTier
from pulse.domain.value_objects.explanation import Explanation
from pulse.domain.value_objects.intensity_band import IntensityBand
from pulse.domain.value_objects.metrics import (
    ConfidenceScore,
    DramaIndex,
    MomentumVector,
    PressureIndex,
    PulseScore,
)
from pulse.domain.value_objects.side import Side


def _exp(v):
    return Explanation("m", v, v, ())


def _read(pulse=0.0, drama=0.0, momentum=0.0, ph=0.0, pa=0.0, conf=0.0, config=DEFAULT_CONFIG):
    return FanSemantics(config).derive(
        PulseScore(pulse, _exp(pulse)),
        DramaIndex(drama, _exp(drama)),
        MomentumVector(momentum, Side.NEUTRAL, _exp(momentum)),
        PressureIndex(Side.HOME, ph, _exp(ph)),
        PressureIndex(Side.AWAY, pa, _exp(pa)),
        ConfidenceScore(conf, _exp(conf)),
    )


# ---- IntensityBand boundaries (defaults 20/40/60/80) -----------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        (0.0, IntensityBand.DORMANT),
        (19.9, IntensityBand.DORMANT),
        (20.0, IntensityBand.SIMMERING),
        (40.0, IntensityBand.HEATING),
        (60.0, IntensityBand.ELECTRIC),
        (79.9, IntensityBand.ELECTRIC),
        (80.0, IntensityBand.FRENZIED),
        (100.0, IntensityBand.FRENZIED),
    ],
)
def test_pulse_band_boundaries(value, expected):
    assert _read(pulse=value).pulse_band is expected


def test_band_label():
    assert IntensityBand.DORMANT.label == "Dormant"
    assert IntensityBand.FRENZIED.label == "Frenzied"


def test_band_requires_four_thresholds():
    with pytest.raises(ValueError):
        IntensityBand.from_value(50.0, (10.0, 20.0))


# ---- Heartbeat BPM ---------------------------------------------------------

@pytest.mark.parametrize(
    "pulse,expected_bpm",
    [
        (0.0, 50),     # min
        (100.0, 180),  # max
        (50.0, 115),   # midpoint of 50..180
    ],
)
def test_heartbeat_bpm_mapping(pulse, expected_bpm):
    assert _read(pulse=pulse).heartbeat_bpm == expected_bpm


def test_heartbeat_bpm_is_clamped_for_out_of_range_pulse():
    # value objects are clamped upstream, but the mapping must be safe regardless
    assert _read(pulse=130.0).heartbeat_bpm == 180


# ---- Drama stars (defaults 10/30/50/70/90) ---------------------------------

@pytest.mark.parametrize(
    "drama,stars",
    [(0.0, 0), (9.9, 0), (10.0, 1), (35.0, 2), (55.0, 3), (75.0, 4), (95.0, 5)],
)
def test_drama_stars(drama, stars):
    assert _read(drama=drama).drama_stars == stars


# ---- Certainty tier (defaults 40/70) ---------------------------------------

@pytest.mark.parametrize(
    "conf,tier",
    [
        (0.0, CertaintyTier.TENTATIVE),
        (39.9, CertaintyTier.TENTATIVE),
        (40.0, CertaintyTier.MEASURED),
        (69.9, CertaintyTier.MEASURED),
        (70.0, CertaintyTier.CONFIDENT),
        (100.0, CertaintyTier.CONFIDENT),
    ],
)
def test_certainty_tier(conf, tier):
    assert _read(conf=conf).narration_certainty is tier


def test_certainty_requires_two_thresholds():
    with pytest.raises(ValueError):
        CertaintyTier.from_confidence(50.0, (40.0,))


def test_certainty_label():
    assert CertaintyTier.MEASURED.label == "Measured"
    assert CertaintyTier.CONFIDENT.label == "Confident"


# ---- Momentum band reads magnitude (direction-agnostic) --------------------

def test_momentum_band_uses_magnitude():
    pos = _read(momentum=80.0).momentum_band
    neg = _read(momentum=-80.0).momentum_band
    assert pos is neg is IntensityBand.FRENZIED


# ---- Both pressures band independently -------------------------------------

def test_pressure_bands_are_independent():
    read = _read(ph=85.0, pa=10.0)
    assert read.pressure_home_band is IntensityBand.FRENZIED
    assert read.pressure_away_band is IntensityBand.DORMANT


# ---- Config drives the semantics -------------------------------------------

def test_custom_config_changes_bands_and_bpm():
    cfg = MetricConfig(
        fan=FanConfig(
            pulse_band_thresholds=(5.0, 10.0, 15.0, 20.0),
            heartbeat_min_bpm=60.0,
            heartbeat_max_bpm=200.0,
        )
    )
    read = _read(pulse=25.0, config=cfg)
    assert read.pulse_band is IntensityBand.FRENZIED  # 25 exceeds all custom cuts
    assert read.heartbeat_bpm == round(60 + 140 * 0.25)
