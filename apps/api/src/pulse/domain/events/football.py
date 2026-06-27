"""Football events — the football-specific layer of the event hierarchy.

Purpose
    Concrete ``MatchEvent`` subclasses for football. ALL football assumptions live
    here; the base class and the metric services stay sport-neutral by reasoning
    over ``kind`` (danger weight) and ``tags`` (semantics) only.

Invariants
    * Each class declares a stable ``kind`` matching a ``MetricConfig`` weight key.
    * Semantic ``tags`` (``"scoring"``, ``"dismissal"``) let metrics detect goals
      and red cards without importing these classes.
    * Frozen / immutable.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .base import MatchEvent


class CardColor(Enum):
    """A football card. RED implies a dismissal (player sent off)."""

    YELLOW = "yellow"
    RED = "red"


@dataclass(frozen=True)
class AttackEvent(MatchEvent):
    """A general attacking move into the opponent's territory."""

    @property
    def kind(self) -> str:
        return "attack"


@dataclass(frozen=True)
class DangerousAttackEvent(MatchEvent):
    """An attack that reached a threatening position."""

    @property
    def kind(self) -> str:
        return "dangerous_attack"


@dataclass(frozen=True)
class ShotEvent(MatchEvent):
    """A shot at goal; ``on_target`` raises its danger weight."""

    on_target: bool = False

    @property
    def kind(self) -> str:
        return "shot_on_target" if self.on_target else "shot"


@dataclass(frozen=True)
class CornerEvent(MatchEvent):
    """A corner kick awarded."""

    @property
    def kind(self) -> str:
        return "corner"


@dataclass(frozen=True)
class FreeKickEvent(MatchEvent):
    """A free kick in an attacking area."""

    @property
    def kind(self) -> str:
        return "free_kick"


@dataclass(frozen=True)
class GoalEvent(MatchEvent):
    """A goal scored. Tagged ``"scoring"`` for sport-neutral detection."""

    @property
    def kind(self) -> str:
        return "goal"

    @property
    def tags(self) -> frozenset[str]:
        return frozenset({"scoring"})


@dataclass(frozen=True)
class CardEvent(MatchEvent):
    """A booking. A RED card is tagged ``"dismissal"`` (stakes amplifier)."""

    color: CardColor = CardColor.YELLOW

    @property
    def kind(self) -> str:
        return "card"

    @property
    def tags(self) -> frozenset[str]:
        return frozenset({"dismissal"}) if self.color is CardColor.RED else frozenset()


@dataclass(frozen=True)
class SubstitutionEvent(MatchEvent):
    """A player substitution (no attacking danger)."""

    @property
    def kind(self) -> str:
        return "substitution"
