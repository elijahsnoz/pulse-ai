"""Smoke tests for the FastAPI app + WebSocket stream (end-to-end)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from pulse.presentation.app import app

client = TestClient(app)


def test_index_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "PULSE" in resp.text


def test_health_reports_replay_verified():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["replay_verified"] is True


def test_websocket_streams_meta_then_live_data():
    # speed huge => negligible pacing delay
    with client.websocket_connect("/ws/match/demo?speed=100000") as ws:
        meta = ws.receive_json()
        assert meta["type"] == "meta"
        assert meta["home"] == "Argentina" and meta["away"] == "France"

        # collect a handful of messages and assert both kinds appear
        kinds = set()
        snapshot = None
        for _ in range(40):
            msg = ws.receive_json()
            kinds.add(msg["type"])
            if msg["type"] == "snapshot":
                snapshot = msg
            if {"snapshot", "timeline"} <= kinds:
                break

        assert "snapshot" in kinds
        assert snapshot is not None
        assert "bpm" in snapshot["pulse"]
        assert snapshot["score"]["home"] >= 0


def test_websocket_streams_to_completion():
    # Drain the whole match and confirm it terminates with an 'end' message.
    with client.websocket_connect("/ws/match/demo?speed=100000") as ws:
        assert ws.receive_json()["type"] == "meta"
        snapshots = 0
        last = None
        for _ in range(5000):
            msg = ws.receive_json()
            if msg["type"] == "snapshot":
                snapshots += 1
            if msg["type"] == "end":
                last = msg
                break
        assert last == {"type": "end"}
        assert snapshots > 150  # one per frame, dense tick cadence
