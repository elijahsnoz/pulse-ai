"""Deterministic numeric helpers shared across the metric engine.

Purpose
    Provide small, side-effect-free math utilities so every service derives its
    numbers identically. No randomness, no platform-variant behaviour.

Invariants
    * Every function is pure: same inputs -> same outputs, always.
    * Empty inputs degrade to neutral defaults (never raise).
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def clamp(value: float, low: float, high: float) -> float:
    """Clamp ``value`` into the closed interval ``[low, high]``."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def sign(value: float) -> int:
    """Return -1, 0 or +1 for the sign of ``value`` (0 maps to 0)."""
    return (value > 0) - (value < 0)


def mean(values: Sequence[float]) -> float:
    """Arithmetic mean; returns 0.0 for an empty sequence."""
    return sum(values) / len(values) if values else 0.0


def pstdev(values: Sequence[float]) -> float:
    """Population standard deviation; returns 0.0 for fewer than two values."""
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    variance = sum((v - mu) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def decay_factor(minutes_ago: float, half_life: float) -> float:
    """Exponential time-decay weight in ``(0, 1]``.

    A freshly occurred event (``minutes_ago == 0``) has weight ``1.0``; an event
    one half-life old has weight ``0.5``. ``half_life`` must be positive.
    """
    if half_life <= 0:
        raise ValueError("half_life must be positive")
    return 0.5 ** (max(minutes_ago, 0.0) / half_life)
