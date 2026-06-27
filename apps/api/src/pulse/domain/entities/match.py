"""Match — the aggregate root tying teams, status and score together.

PROVISIONAL — not part of the frozen Module 1 v1.0 contract (see entities/__init__.py).

Purpose
    Model a single fixture's identity and high-level state. The metric engine is
    intentionally decoupled from this entity (it takes primitive inputs), but the
    broader domain uses ``Match`` as the aggregate that owns a fixture.

Invariants
    * ``id`` is the stable identity; equality/hashing derive from it alone.
    * ``home`` and ``away`` are distinct teams.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..value_objects.scoreline import Scoreline
from .team import Team


class MatchStatus(Enum):
    """Lifecycle state of a fixture."""

    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"


@dataclass(eq=False)
class Match:
    """A fixture between two teams with a status, score and clock."""

    id: str
    home: Team
    away: Team
    competition: str = ""
    status: MatchStatus = MatchStatus.SCHEDULED
    scoreline: Scoreline = field(default_factory=Scoreline)
    current_minute: float = 0.0

    def __post_init__(self) -> None:
        if self.home == self.away:
            raise ValueError("home and away teams must be distinct")

    @property
    def is_live(self) -> bool:
        """True when the match is currently in play."""
        return self.status is MatchStatus.LIVE

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Match) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
