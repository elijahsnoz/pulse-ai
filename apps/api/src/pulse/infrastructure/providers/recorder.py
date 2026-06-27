"""Recorder — a transparent tee that records frames as they flow.

Purpose
    Recording is a cross-cutting concern, not separate logic. ``Recorder`` wraps
    any ``SportsDataProvider`` and appends each frame to a ``TapeStore`` as it
    passes through to the pipeline — so the tape is exactly what was consumed.

Invariants
    * Order-preserving and lossless: yields the inner frames unchanged.
    * Append is delegated to the store (idempotent on sequence).
"""
from __future__ import annotations

from collections.abc import Iterator

from pulse.application.frames.frame import MatchFrame
from pulse.application.ports import SportsDataProvider, TapeStore


class Recorder:
    """Tees frames from an inner provider into a tape store."""

    def __init__(
        self, inner: SportsDataProvider, store: TapeStore, match_id: str
    ) -> None:
        self._inner = inner
        self._store = store
        self._match_id = match_id

    def frames(self) -> Iterator[MatchFrame]:
        for frame in self._inner.frames():
            self._store.append(self._match_id, frame)
            yield frame
