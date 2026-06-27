"""TapeStore implementations — where the recorded tape lives.

Purpose
    Two minimal ``TapeStore`` adapters: an in-memory one (tests, ephemeral runs)
    and a JSON-file one (the demo's durable tape). Both store canonical frames via
    the frame codec, so what is persisted is exactly what the pipeline consumed.

Invariants
    * Append is idempotent on ``frame.sequence`` (re-recording is safe).
    * ``read`` returns frames in ascending ``sequence`` order.
    * No external dependencies — stdlib JSON only.
"""
from __future__ import annotations

import json
from pathlib import Path

from pulse.application.frames.codec import decode_frame, encode_frame
from pulse.application.frames.frame import MatchFrame


class InMemoryTapeStore:
    """A dict-backed tape store for tests and ephemeral runs."""

    def __init__(self) -> None:
        self._tapes: dict[str, dict[int, MatchFrame]] = {}

    def append(self, match_id: str, frame: MatchFrame) -> None:
        self._tapes.setdefault(match_id, {})[frame.sequence] = frame

    def read(self, match_id: str) -> list[MatchFrame]:
        by_seq = self._tapes.get(match_id, {})
        return [by_seq[seq] for seq in sorted(by_seq)]


class JsonFileTapeStore:
    """A JSON-file tape store: one ``{match_id}.json`` file per match.

    Frames are cached in memory and the whole file is rewritten on append. This
    is intentionally simple — adequate for demo-scale tapes, no extra machinery.
    """

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[int, MatchFrame]] = {}

    def _path(self, match_id: str) -> Path:
        return self._dir / f"{match_id}.json"

    def _load(self, match_id: str) -> dict[int, MatchFrame]:
        if match_id not in self._cache:
            path = self._path(match_id)
            frames: dict[int, MatchFrame] = {}
            if path.exists():
                raw = json.loads(path.read_text(encoding="utf-8"))
                for item in raw:
                    frame = decode_frame(item)
                    frames[frame.sequence] = frame
            self._cache[match_id] = frames
        return self._cache[match_id]

    def _flush(self, match_id: str) -> None:
        frames = self._load(match_id)
        payload = [encode_frame(frames[seq]) for seq in sorted(frames)]
        self._path(match_id).write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def append(self, match_id: str, frame: MatchFrame) -> None:
        self._load(match_id)[frame.sequence] = frame
        self._flush(match_id)

    def read(self, match_id: str) -> list[MatchFrame]:
        frames = self._load(match_id)
        return [frames[seq] for seq in sorted(frames)]
