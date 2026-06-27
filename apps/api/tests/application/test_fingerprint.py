"""Tests for the snapshot fingerprint (the proof live == replay)."""
from __future__ import annotations

from pulse.application.fingerprint import canonical_content, fingerprint
from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from tests.domain.conftest import corner, goal, shot


def _state(minute=84.0, score=(1, 1)):
    events = [
        corner(80.0, Side.HOME, seq=1),
        shot(81.0, Side.HOME, on_target=True, seq=2),
        shot(82.0, Side.HOME, on_target=True, seq=3),
        goal(83.0, Side.HOME, seq=4),
    ]
    return MetricEngine().evaluate(
        events=events, minute=minute, scoreline=Scoreline(*score)
    )


def test_fingerprint_is_stable_for_identical_state():
    assert fingerprint(_state()) == fingerprint(_state())


def test_fingerprint_is_hex_sha256():
    fp = fingerprint(_state())
    assert len(fp) == 64
    int(fp, 16)  # parses as hex


def test_fingerprint_changes_with_minute():
    assert fingerprint(_state(minute=84.0)) != fingerprint(_state(minute=88.0))


def test_fingerprint_changes_with_scoreline():
    assert fingerprint(_state(score=(1, 1))) != fingerprint(_state(score=(2, 1)))


def test_canonical_content_excludes_storage_metadata():
    content = canonical_content(_state())
    blob = repr(content)
    # only semantic content — no db ids / timestamps / recorded_at
    assert "recorded_at" not in blob and "created_at" not in blob and "id" not in content


def test_canonical_content_includes_explanations_and_fan_read():
    content = canonical_content(_state())
    assert content["momentum"]["contributors"]  # additive explanation captured
    assert "heartbeat_bpm" in content["fan_read"]
    assert content["phase"] and content["emotion"]


def test_two_independent_engines_fingerprint_identically():
    a = MetricEngine().evaluate(events=[goal(83.0, Side.HOME, seq=1)],
                                minute=84.0, scoreline=Scoreline(1, 0))
    b = MetricEngine().evaluate(events=[goal(83.0, Side.HOME, seq=1)],
                                minute=84.0, scoreline=Scoreline(1, 0))
    assert fingerprint(a) == fingerprint(b)


def test_momentum_shift_is_part_of_fingerprint():
    engine = MetricEngine()
    away = [shot(50.0, Side.AWAY, on_target=True, seq=i) for i in range(1, 6)]
    first = engine.evaluate(events=away, minute=51.0, scoreline=Scoreline(0, 0))
    home = away + [shot(55.0 + i * 0.1, Side.HOME, on_target=True, seq=10 + i) for i in range(8)]
    with_shift = engine.evaluate(events=home, minute=56.0,
                                 scoreline=Scoreline(0, 0), previous=first)
    no_shift = engine.evaluate(events=home, minute=56.0, scoreline=Scoreline(0, 0))
    assert with_shift.momentum_shift is not None
    assert no_shift.momentum_shift is None
    assert fingerprint(with_shift) != fingerprint(no_shift)
