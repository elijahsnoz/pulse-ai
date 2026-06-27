"""Application ports — the interfaces the pipeline depends on.

Purpose
    Define the seams that keep the pipeline source- and storage-agnostic.
    Infrastructure provides the implementations; the pipeline only ever sees
    these Protocols. This is what makes "one pipeline, swappable edges" real.

Invariants
    * Structural (``typing.Protocol``) — any object with the right methods fits.
    * No behaviour here; contracts only.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from .frames.frame import MatchFrame


@runtime_checkable
class SportsDataProvider(Protocol):
    """A source of ordered ``MatchFrame``s for a single match.

    Implemented by ``TxLineProvider`` (live), ``RecordedProvider`` (replay) and
    the ``Recorder`` tee. The pipeline cannot tell which one it is holding.
    """

    def frames(self) -> Iterator[MatchFrame]:
        """Yield the match's frames in canonical sequence order."""
        ...


@runtime_checkable
class TapeStore(Protocol):
    """Append-only persistence for a match's frame tape."""

    def append(self, match_id: str, frame: MatchFrame) -> None:
        """Append one frame (idempotent on ``frame.sequence``)."""
        ...

    def read(self, match_id: str) -> list[MatchFrame]:
        """Return all stored frames for a match, in sequence order."""
        ...
