"""FastAPI + WebSocket app — Pulse, live in the browser.

Purpose
    The thin presentation surface. On first use it wires the COMPLETE Module 2
    pipeline once: record the demo tape through the ``Recorder`` tee into a
    ``JsonFileTapeStore``, assert fidelity with ``VerifyReplay``, then stream it
    back through ``RecordedProvider`` -> ``MatchReducer`` over a WebSocket, paced
    in match-time so the heartbeat and timeline unfold live.

    Live (TxLINE) and replay share this exact streaming path; only the provider
    differs. Nothing here contains business logic.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from pulse.application.reduction import MatchReducer
from pulse.application.verification import verify_tape
from pulse.infrastructure.demo import (
    DEMO_AWAY,
    DEMO_HOME,
    DEMO_MATCH_ID,
    demo_match_frames,
)
from pulse.infrastructure.persistence import JsonFileTapeStore
from pulse.infrastructure.providers import RecordedProvider, Recorder
from pulse.presentation.serialization import (
    build_meta,
    snapshot_to_wire,
    timeline_to_wire,
)

_STATIC = Path(__file__).parent / "static"
# .../apps/api/src/pulse/presentation/app.py -> parents[3] == .../apps/api
_TAPE_DIR = Path(__file__).resolve().parents[3] / "var" / "tapes"

# Pacing: a large gap is capped so the stream never stalls.
_MAX_STEP_DELAY = 1.0


@dataclass(frozen=True)
class DemoPipeline:
    """The wired demo: a verified tape behind a replay provider."""

    provider: RecordedProvider
    home: str
    away: str
    match_id: str
    verified: bool


_pipeline: DemoPipeline | None = None


def build_demo_pipeline() -> DemoPipeline:
    """Record the demo tape, verify it, and return a replay provider (cached)."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    store = JsonFileTapeStore(_TAPE_DIR)
    # Record the demo through the tee so the persisted tape == what we consumed.
    source = RecordedProvider(demo_match_frames())
    recorder = Recorder(source, store, DEMO_MATCH_ID)
    for _ in recorder.frames():  # drain to persist
        pass

    result = verify_tape(store, DEMO_MATCH_ID)
    _pipeline = DemoPipeline(
        provider=RecordedProvider.from_store(store, DEMO_MATCH_ID),
        home=DEMO_HOME,
        away=DEMO_AWAY,
        match_id=DEMO_MATCH_ID,
        verified=result.passed,
    )
    return _pipeline


app = FastAPI(title="Pulse — AI Second Screen")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the single-page live visualizer."""
    return (_STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    """Liveness + replay-verification status."""
    pipeline = build_demo_pipeline()
    return {"status": "ok", "replay_verified": pipeline.verified}


@app.websocket("/ws/match/{match_id}")
async def stream_match(websocket: WebSocket, match_id: str, speed: float = 2.5) -> None:
    """Stream snapshots + timeline events for a match, paced in match-time.

    ``speed`` is match-minutes per real second (default 2.5 => ~38s for 95').
    """
    await websocket.accept()
    pipeline = build_demo_pipeline()
    await websocket.send_json(build_meta(pipeline.home, pipeline.away, match_id))

    reducer = MatchReducer()
    previous_minute = 0.0
    try:
        for frame in pipeline.provider.frames():
            delay = max(0.0, frame.match_minute - previous_minute) / max(speed, 1e-9)
            previous_minute = frame.match_minute
            if delay > 0:
                await asyncio.sleep(min(delay, _MAX_STEP_DELAY))

            step = reducer.push(frame)
            await websocket.send_json(snapshot_to_wire(step.snapshot))
            for event in step.timeline:
                await websocket.send_json(
                    timeline_to_wire(event, pipeline.home, pipeline.away)
                )
        await websocket.send_json({"type": "end"})
    except WebSocketDisconnect:  # pragma: no cover - client closed early
        return


def main() -> None:  # pragma: no cover - server entrypoint
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":  # pragma: no cover
    main()
