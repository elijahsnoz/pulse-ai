"""MatchEvent — the sport-agnostic base for any in-match occurrence.

Purpose
    Define the minimal, sport-neutral contract every event satisfies so the
    metric engine can score *any* timed team sport. There is deliberately NOTHING
    football-specific here: no goals, cards or substitutions. Concrete sports add
    those as subclasses (see ``events/football.py``).

Inputs (fields)
    event_id: stable unique id (used for idempotent de-duplication upstream).
    sequence: monotonically increasing order key within a match.
    minute:   game-clock minute at which the event occurred (>= 0).
    side:     which competitor the event belongs to (``Side``).

Outputs (contract)
    kind: a stable string key the engine maps to a danger weight via config.
    tags: sport-neutral semantic markers (e.g. ``"scoring"``, ``"dismissal"``)
          so higher-level metrics can reason without importing concrete classes.

Invariants
    * Frozen / immutable and order-stable via ``sequence``.
    * Abstract: cannot be instantiated directly — forces sport subclasses.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..value_objects.side import Side


@dataclass(frozen=True)
class MatchEvent(ABC):
    """Abstract, sport-agnostic match event."""

    event_id: str
    sequence: int
    minute: float
    side: Side = Side.NEUTRAL

    @property
    @abstractmethod
    def kind(self) -> str:
        """Stable kind key resolved to a danger weight by ``MetricConfig``."""
        raise NotImplementedError

    @property
    def tags(self) -> frozenset[str]:
        """Sport-neutral semantic markers; empty by default."""
        return frozenset()
