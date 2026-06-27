"""Windowing — turn a raw event stream into a weighted, time-decayed window.

Purpose
    Every metric reads from the same sliding window so they stay mutually
    consistent. This module selects in-window events, applies danger weights and
    exponential time-decay, and exposes deterministic aggregation helpers.

Inputs
    events:          any iterable of ``MatchEvent``.
    current_minute:  the "now" minute the window is anchored to.
    config:          ``MetricConfig`` providing weights and window/decay params.

Outputs
    ``EventWindow`` — an immutable, order-stable collection of ``WeightedEvent``.

Invariants
    * Future events (minute > current_minute) and events older than the window
      are excluded.
    * Deterministic ordering by (sequence, event_id) regardless of input order.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..config import DEFAULT_CONFIG, MetricConfig
from ..events.base import MatchEvent
from ..numeric import decay_factor


@dataclass(frozen=True)
class WeightedEvent:
    """A match event paired with its base danger weight and decay factor."""

    event: MatchEvent
    base_weight: float
    decay: float

    @property
    def effective(self) -> float:
        """Decayed danger weight (unsigned), ``base_weight * decay``."""
        return self.base_weight * self.decay

    @property
    def signed_base(self) -> float:
        """Undecayed weight, signed by side (+home / -away / 0 neutral)."""
        return self.base_weight * self.event.side.sign

    @property
    def signed_effective(self) -> float:
        """Decayed weight, signed by side."""
        return self.effective * self.event.side.sign


@dataclass(frozen=True)
class EventWindow:
    """An immutable window of weighted events anchored at ``current_minute``."""

    current_minute: float
    window_minutes: float
    events: tuple[WeightedEvent, ...]

    def __len__(self) -> int:
        return len(self.events)

    def total_danger(self) -> float:
        """Sum of unsigned effective weights across both sides."""
        return sum(we.effective for we in self.events)

    def tag_count(self, tag: str) -> int:
        """Number of in-window events carrying ``tag``."""
        return sum(1 for we in self.events if tag in we.event.tags)

    def signed_buckets(self, n_buckets: int, scale: float) -> list[float]:
        """Partition the window into ``n_buckets`` equal time slices.

        Returns the scaled net signed momentum per slice (oldest first). Used by
        Pulse (volatility) and Confidence (trend consistency). Deterministic.
        """
        if n_buckets < 1:
            raise ValueError("n_buckets must be >= 1")
        buckets = [0.0] * n_buckets
        span = self.window_minutes
        low = self.current_minute - span
        for we in self.events:
            if span > 0:
                frac = (we.event.minute - low) / span
                index = min(int(frac * n_buckets), n_buckets - 1)
                index = max(index, 0)
            else:
                index = n_buckets - 1
            buckets[index] += we.signed_effective * scale
        return buckets


def build_window(
    events: Iterable[MatchEvent],
    current_minute: float,
    config: MetricConfig = DEFAULT_CONFIG,
) -> EventWindow:
    """Build an ``EventWindow`` from raw events at ``current_minute``."""
    window_minutes = config.window.window_minutes
    half_life = config.window.half_life_minutes

    weighted: list[WeightedEvent] = []
    for event in events:
        if event.minute > current_minute:
            continue  # not yet occurred
        minutes_ago = current_minute - event.minute
        if minutes_ago > window_minutes:
            continue  # fallen out of the window
        weight = config.weight_for(event.kind)
        decay = decay_factor(minutes_ago, half_life)
        weighted.append(WeightedEvent(event=event, base_weight=weight, decay=decay))

    # Deterministic order independent of input ordering.
    weighted.sort(key=lambda we: (we.event.sequence, we.event.event_id))
    return EventWindow(
        current_minute=current_minute,
        window_minutes=window_minutes,
        events=tuple(weighted),
    )
