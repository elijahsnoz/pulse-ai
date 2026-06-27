"""RecordedProvider — replays a stored tape through the same pipeline.

Purpose
    The replay half of "one pipeline, two sources". It yields previously-recorded
    canonical frames in order; the reducer cannot distinguish it from live.

Invariants
    * Pure source: yields exactly the frames it was given, in order.
    * No pacing here — timing is a presentation concern (the WS layer paces).
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from pulse.application.frames.frame import MatchFrame
from pulse.application.ports import TapeStore


class RecordedProvider:
    """Yields recorded frames (from a list or a ``TapeStore``)."""

    def __init__(self, frames: Iterable[MatchFrame]) -> None:
        self._frames = list(frames)

    @classmethod
    def from_store(cls, store: TapeStore, match_id: str) -> "RecordedProvider":
        """Build a provider from a tape persisted in ``store``."""
        return cls(store.read(match_id))

    def frames(self) -> Iterator[MatchFrame]:
        yield from self._frames
