"""Tests for RecordedProvider and the Recorder tee."""
from __future__ import annotations

from pulse.application.ports import SportsDataProvider, TapeStore
from pulse.application.frames import MatchFrame
from pulse.infrastructure.persistence import InMemoryTapeStore
from pulse.infrastructure.providers import RecordedProvider, Recorder


def _frames():
    return [MatchFrame.tick_frame(sequence=i, match_minute=float(i)) for i in range(1, 5)]


def test_recorded_provider_yields_in_order():
    provider = RecordedProvider(_frames())
    assert list(provider.frames()) == _frames()


def test_recorded_provider_satisfies_port():
    assert isinstance(RecordedProvider(_frames()), SportsDataProvider)


def test_recorder_tees_into_store_without_altering_stream():
    store = InMemoryTapeStore()
    inner = RecordedProvider(_frames())
    recorder = Recorder(inner, store, "m1")

    streamed = list(recorder.frames())  # draining drives the tee
    assert streamed == _frames()          # stream unchanged
    assert store.read("m1") == _frames()  # and recorded faithfully


def test_recorder_satisfies_port_and_store_protocol():
    store = InMemoryTapeStore()
    assert isinstance(store, TapeStore)
    recorder = Recorder(RecordedProvider(_frames()), store, "m1")
    assert isinstance(recorder, SportsDataProvider)


def test_recorded_provider_from_store():
    store = InMemoryTapeStore()
    for f in _frames():
        store.append("m1", f)
    assert list(RecordedProvider.from_store(store, "m1").frames()) == _frames()
