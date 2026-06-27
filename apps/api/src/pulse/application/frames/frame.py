"""MatchFrame — the canonical, recordable unit that enters the pipeline.

Purpose
    Represent one input to the deterministic pipeline. A frame is either:
      * EVENT — wraps a Module 1 domain ``MatchEvent`` (goal, shot, card …).
      * TICK  — a pure clock advance carrying only a ``match_minute`` so the
                heartbeat can evolve (time-decay) between events.
    Live (TxLINE) and Replay both emit identical ``MatchFrame``s; this is the
    seam that guarantees "one pipeline, two sources".

Inputs (fields)
    sequence:          monotonic, gap-free order key within a match.
    match_minute:      canonical clock position (NEVER wall-clock).
    kind:              EVENT or TICK.
    event:             the wrapped domain event (EVENT frames only; else None).
    provider_event_id: upstream id for idempotent de-duplication (EVENT frames).

Invariants
    * Frozen / immutable.
    * EVENT frames carry an ``event`` and (typically) a ``provider_event_id``.
    * TICK frames carry neither an ``event`` nor a ``provider_event_id``.
    * ``match_minute >= 0``.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pulse.domain.events.base import MatchEvent


class FrameKind(Enum):
    """Whether a frame carries a domain event or is a bare clock advance."""

    EVENT = "event"
    TICK = "tick"


@dataclass(frozen=True)
class MatchFrame:
    """An immutable, canonical pipeline input. Use the factory classmethods."""

    sequence: int
    match_minute: float
    kind: FrameKind
    event: MatchEvent | None = None
    provider_event_id: str | None = None

    def __post_init__(self) -> None:
        if self.match_minute < 0:
            raise ValueError("match_minute must be non-negative")
        if self.kind is FrameKind.EVENT:
            if self.event is None:
                raise ValueError("EVENT frames require an event")
        else:  # TICK
            if self.event is not None:
                raise ValueError("TICK frames must not carry an event")
            if self.provider_event_id is not None:
                raise ValueError("TICK frames must not carry a provider_event_id")

    @classmethod
    def event_frame(
        cls,
        *,
        sequence: int,
        event: MatchEvent,
        provider_event_id: str | None = None,
        match_minute: float | None = None,
    ) -> "MatchFrame":
        """Build an EVENT frame. ``match_minute`` defaults to the event's minute."""
        return cls(
            sequence=sequence,
            match_minute=event.minute if match_minute is None else match_minute,
            kind=FrameKind.EVENT,
            event=event,
            provider_event_id=provider_event_id,
        )

    @classmethod
    def tick_frame(cls, *, sequence: int, match_minute: float) -> "MatchFrame":
        """Build a TICK frame at ``match_minute``."""
        return cls(
            sequence=sequence,
            match_minute=match_minute,
            kind=FrameKind.TICK,
        )

    @property
    def is_event(self) -> bool:
        """True for EVENT frames."""
        return self.kind is FrameKind.EVENT

    @property
    def is_tick(self) -> bool:
        """True for TICK frames."""
        return self.kind is FrameKind.TICK
