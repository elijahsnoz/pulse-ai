"""Tests for the TapeStore adapters (in-memory + JSON file)."""
from __future__ import annotations

from pulse.application.frames import MatchFrame
from pulse.infrastructure.persistence import InMemoryTapeStore, JsonFileTapeStore
from pulse.domain.events.football import GoalEvent
from pulse.domain.value_objects.side import Side


def _frames():
    return [
        MatchFrame.tick_frame(sequence=1, match_minute=1.0),
        MatchFrame.event_frame(sequence=2, event=GoalEvent("g", 2, 11.0, Side.HOME),
                               provider_event_id="p2"),
        MatchFrame.tick_frame(sequence=3, match_minute=20.0),
    ]


def test_in_memory_round_trip_and_order():
    store = InMemoryTapeStore()
    for f in reversed(_frames()):  # insert out of order
        store.append("m1", f)
    read = store.read("m1")
    assert [f.sequence for f in read] == [1, 2, 3]
    assert read == _frames()


def test_in_memory_append_is_idempotent():
    store = InMemoryTapeStore()
    f = MatchFrame.tick_frame(sequence=1, match_minute=1.0)
    store.append("m1", f)
    store.append("m1", f)
    assert len(store.read("m1")) == 1


def test_read_unknown_match_is_empty():
    assert InMemoryTapeStore().read("nope") == []


def test_json_file_round_trip(tmp_path):
    store = JsonFileTapeStore(tmp_path)
    for f in _frames():
        store.append("m1", f)
    # a fresh store reading the same directory recovers identical frames
    reopened = JsonFileTapeStore(tmp_path)
    assert reopened.read("m1") == _frames()


def test_json_file_persists_across_instances_and_is_idempotent(tmp_path):
    store = JsonFileTapeStore(tmp_path)
    f = MatchFrame.event_frame(sequence=5, event=GoalEvent("g", 5, 50.0, Side.AWAY),
                               provider_event_id="p5")
    store.append("m9", f)
    store.append("m9", f)  # idempotent
    assert JsonFileTapeStore(tmp_path).read("m9") == [f]
