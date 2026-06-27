"""Branded metric value objects — the public intelligence vocabulary of Pulse.

Purpose
    These are the consumer-facing, branded outputs of the engine:
    Pulse Score, Pressure Index, Momentum Vector, Drama Index and Confidence
    Score. Each pairs a final value with its ``Explanation`` so no number ever
    travels without its reasoning.

Invariants
    * Frozen / immutable value objects.
    * ``value`` lies in the metric's documented range.
    * ``explanation.value == value`` and the explanation is additive.
"""
from __future__ import annotations

from dataclasses import dataclass

from .explanation import Explanation
from .side import Side


@dataclass(frozen=True)
class MomentumVector:
    """Momentum Vector — who is on top, right now.

    value:     signed intensity in [-100, 100] (+home / -away).
    direction: HOME, AWAY, or NEUTRAL when within the balanced band.
    """

    value: float
    direction: Side
    explanation: Explanation

    @property
    def magnitude(self) -> float:
        """Unsigned strength of the swing, in [0, 100]."""
        return abs(self.value)


@dataclass(frozen=True)
class PressureIndex:
    """Pressure Index — one side's sustained attacking pressure, in [0, 100]."""

    side: Side
    value: float
    explanation: Explanation


@dataclass(frozen=True)
class PulseScore:
    """Pulse Score — overall match intensity in [0, 100]; drives the heartbeat."""

    value: float
    explanation: Explanation


@dataclass(frozen=True)
class DramaIndex:
    """Drama Index — match intensity amplified by stakes, in [0, 100]."""

    value: float
    explanation: Explanation


@dataclass(frozen=True)
class ConfidenceScore:
    """Confidence Score — trust in the deterministic signal, in [0, 100].

    This is NOT model/AI confidence. It reflects how well-supported the metrics
    are by the underlying data: event density, trend consistency, volatility and
    how much of the time window is actually covered.
    """

    value: float
    explanation: Explanation
