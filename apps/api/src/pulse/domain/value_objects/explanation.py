"""Explanation — structured, additive reasoning behind every metric.

Purpose
    Every metric in Pulse exposes *why* it holds a value, not just the number.
    An ``Explanation`` is a list of named ``Contributor`` deltas plus the final
    (post-clamp) value. The Story Engine later turns these into natural language.

Inputs
    metric:       stable machine key, e.g. ``"momentum_vector"``.
    value:        final, clamped metric value shown to users.
    raw_value:    pre-clamp sum of all contributors.
    contributors: ordered, signed deltas that explain the raw value.

Invariants
    * ADDITIVE: ``sum(c.value for c in contributors) == raw_value`` (within float
      tolerance). This lets explanations be rendered as a balanced breakdown.
    * ``value`` equals ``raw_value`` after clamping to the metric's range.
    * Frozen / immutable.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Contributor:
    """A single signed component of a metric's value.

    label:  machine-stable key (e.g. ``"shots_on_target"``, ``"decay_adjustment"``).
    value:  signed contribution to the metric's raw value.
    detail: optional human-oriented note for richer narration.
    """

    label: str
    value: float
    detail: str = ""


@dataclass(frozen=True)
class Explanation:
    """Structured reasoning for one metric evaluation."""

    metric: str
    value: float
    raw_value: float
    contributors: tuple[Contributor, ...] = field(default_factory=tuple)

    def total_contribution(self) -> float:
        """Sum of contributor values; should equal ``raw_value`` (additive invariant)."""
        return sum(c.value for c in self.contributors)

    def top_contributors(self, limit: int = 3) -> tuple[Contributor, ...]:
        """The ``limit`` contributors with the largest absolute impact.

        Ordering is deterministic: by descending magnitude, then by label.
        """
        ranked = sorted(self.contributors, key=lambda c: (-abs(c.value), c.label))
        return tuple(ranked[:limit])
