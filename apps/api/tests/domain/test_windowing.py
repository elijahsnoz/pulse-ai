"""Tests for the windowing service (selection, decay, bucketing, ordering)."""
from __future__ import annotations

import pytest

from pulse.domain.config import MetricConfig, WindowConfig
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.side import Side

from .conftest import attack, goal, shot


def test_future_events_are_excluded():
    events = [shot(50.0, Side.HOME, seq=1), shot(70.0, Side.HOME, seq=2)]
    window = build_window(events, current_minute=60.0)
    assert len(window) == 1


def test_events_older_than_window_excluded():
    events = [shot(40.0, Side.HOME, seq=1), shot(58.0, Side.HOME, seq=2)]
    window = build_window(events, current_minute=60.0)  # default window 10 min
    assert len(window) == 1


def test_boundary_event_exactly_on_window_edge_included():
    events = [shot(50.0, Side.HOME, seq=1)]
    window = build_window(events, current_minute=60.0)
    assert len(window) == 1


def test_unknown_kind_gets_zero_weight():
    # substitution has weight 0 in default config
    from .conftest import substitution

    window = build_window([substitution(59.0, Side.HOME, seq=1)], 60.0)
    assert window.events[0].base_weight == 0.0
    assert window.total_danger() == 0.0


def test_decay_applied_to_effective_weight():
    # event 5 minutes ago with half-life 5 => decay 0.5
    window = build_window([shot(55.0, Side.HOME, on_target=True, seq=1)], 60.0)
    we = window.events[0]
    assert we.decay == pytest.approx(0.5)
    assert we.effective == pytest.approx(we.base_weight * 0.5)


def test_ordering_is_deterministic_regardless_of_input_order():
    a = shot(59.0, Side.HOME, seq=2)
    b = shot(58.0, Side.AWAY, seq=1)
    w1 = build_window([a, b], 60.0)
    w2 = build_window([b, a], 60.0)
    assert [e.event.sequence for e in w1.events] == [1, 2]
    assert [e.event.sequence for e in w2.events] == [1, 2]


def test_tag_count():
    window = build_window([goal(59.0, Side.HOME, seq=1), shot(59.5, Side.AWAY, seq=2)], 60.0)
    assert window.tag_count("scoring") == 1
    assert window.tag_count("dismissal") == 0


def test_signed_buckets_partition_and_sign():
    # home events early, away events late within a 10-min window
    events = [attack(51.0, Side.HOME, seq=1), attack(59.0, Side.AWAY, seq=2)]
    window = build_window(events, 60.0)
    buckets = window.signed_buckets(2, scale=10.0)
    assert len(buckets) == 2
    assert buckets[0] > 0  # home in older bucket
    assert buckets[1] < 0  # away in newer bucket


def test_signed_buckets_rejects_bad_bucket_count():
    window = build_window([attack(59.0, Side.HOME, seq=1)], 60.0)
    with pytest.raises(ValueError):
        window.signed_buckets(0, scale=1.0)


def test_zero_span_window_routes_to_last_bucket():
    cfg = MetricConfig(window=WindowConfig(window_minutes=0.0, half_life_minutes=5.0))
    window = build_window([attack(60.0, Side.HOME, seq=1)], 60.0, cfg)
    buckets = window.signed_buckets(3, scale=10.0)
    assert buckets[0] == 0.0 and buckets[1] == 0.0
    assert buckets[2] > 0.0
