"""Tests for the Confidence Score calculator."""
from __future__ import annotations

import pytest

from pulse.domain.services.confidence import ConfidenceCalculator
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.side import Side

from .conftest import shot


def _confidence(events, minute=60.0):
    return ConfidenceCalculator().calculate(build_window(events, minute))


def test_empty_window_has_low_confidence():
    c = _confidence([], minute=60.0)
    # density 0, consistency neutral, volatility steady, coverage full
    assert 0.0 <= c.value <= 100.0
    contribs = {x.label: x.value for x in c.explanation.contributors}
    assert contribs["density"] == 0.0


def test_dense_consistent_signal_has_higher_confidence_than_sparse():
    sparse = _confidence([shot(59.0, Side.HOME, on_target=True, seq=1)])
    dense = _confidence(
        [shot(51.0 + i * 0.6, Side.HOME, on_target=True, seq=i) for i in range(14)]
    )
    assert dense.value > sparse.value


def test_early_match_has_reduced_coverage():
    # At minute 3 with a 10-min window, coverage = 3/10.
    c = _confidence([shot(2.5, Side.HOME, seq=1)], minute=3.0)
    coverage = next(x.value for x in c.explanation.contributors if x.label == "coverage")
    full = next(
        x.value
        for x in _confidence([shot(59.0, Side.HOME, seq=1)], minute=60.0).explanation.contributors
        if x.label == "coverage"
    )
    assert coverage < full


def test_consistency_neutral_when_no_direction():
    # purely neutral-side events => no directional signal => neutral consistency
    from .conftest import substitution

    c = _confidence([substitution(59.0, Side.HOME, seq=1)])
    consistency = next(x.value for x in c.explanation.contributors if x.label == "consistency")
    # neutral_consistency 0.5 * weight 0.3 * 100 / total_weight(1.0) = 15.0
    assert consistency == pytest.approx(15.0)


def test_explanation_additive_and_clamped():
    c = _confidence([shot(59.0, Side.HOME, on_target=True, seq=1)])
    assert c.explanation.total_contribution() == pytest.approx(c.explanation.raw_value)
    assert 0.0 <= c.value <= 100.0
