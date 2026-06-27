"""Tests for the deterministic numeric helpers."""
from __future__ import annotations

import math

import pytest

from pulse.domain.numeric import clamp, decay_factor, mean, pstdev, sign


@pytest.mark.parametrize(
    "value,low,high,expected",
    [
        (5, 0, 10, 5),
        (-1, 0, 10, 0),
        (11, 0, 10, 10),
        (0, 0, 10, 0),
        (10, 0, 10, 10),
        (-50, -100, 100, -50),
    ],
)
def test_clamp(value, low, high, expected):
    assert clamp(value, low, high) == expected


@pytest.mark.parametrize("value,expected", [(3.2, 1), (-0.1, -1), (0, 0), (0.0, 0)])
def test_sign(value, expected):
    assert sign(value) == expected


def test_mean_and_empty():
    assert mean([2, 4, 6]) == 4
    assert mean([]) == 0.0


def test_pstdev_basic_and_degenerate():
    assert pstdev([]) == 0.0
    assert pstdev([5]) == 0.0
    assert pstdev([2, 2, 2]) == 0.0
    assert pstdev([1, 3]) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "ago,half_life,expected",
    [
        (0, 5, 1.0),
        (5, 5, 0.5),
        (10, 5, 0.25),
        (-3, 5, 1.0),  # negative clamped to 0
    ],
)
def test_decay_factor(ago, half_life, expected):
    assert decay_factor(ago, half_life) == pytest.approx(expected)


def test_decay_factor_rejects_nonpositive_half_life():
    with pytest.raises(ValueError):
        decay_factor(1.0, 0.0)
    with pytest.raises(ValueError):
        decay_factor(1.0, -2.0)


def test_decay_is_monotonic_decreasing():
    values = [decay_factor(a, 5) for a in range(0, 11)]
    assert all(earlier >= later for earlier, later in zip(values, values[1:]))
    assert math.isclose(values[0], 1.0)
