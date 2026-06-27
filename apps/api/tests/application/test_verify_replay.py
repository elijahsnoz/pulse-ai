"""Tests for the VerifyReplay use case."""
from __future__ import annotations

from pulse.application.verification import verify_replay, verify_tape
from pulse.infrastructure.demo import demo_match_frames
from pulse.infrastructure.persistence import InMemoryTapeStore


def test_demo_tape_verifies():
    result = verify_replay(demo_match_frames())
    assert result.passed
    assert result.first_mismatch is None
    assert result.snapshot_count == len(demo_match_frames())


def test_verify_tape_reads_from_store():
    store = InMemoryTapeStore()
    for f in demo_match_frames():
        store.append("demo", f)
    result = verify_tape(store, "demo")
    assert result.passed
    assert result.snapshot_count == len(demo_match_frames())


def test_empty_tape_trivially_verifies():
    result = verify_replay([])
    assert result.passed
    assert result.snapshot_count == 0
