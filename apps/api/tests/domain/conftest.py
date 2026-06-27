"""Shared fixtures and deterministic event factories for the domain tests."""
from __future__ import annotations

import itertools
from collections.abc import Iterable

import pytest

from pulse.domain.events.base import MatchEvent
from pulse.domain.events.football import (
    AttackEvent,
    CardColor,
    CardEvent,
    CornerEvent,
    DangerousAttackEvent,
    GoalEvent,
    ShotEvent,
    SubstitutionEvent,
)
from pulse.domain.services.windowing import build_window
from pulse.domain.value_objects.side import Side

_counter = itertools.count(1)


def _next_id() -> str:
    return f"e{next(_counter)}"


def shot(minute: float, side: Side, *, on_target: bool = False, seq: int | None = None) -> ShotEvent:
    return ShotEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                     minute=minute, side=side, on_target=on_target)


def goal(minute: float, side: Side, *, seq: int | None = None) -> GoalEvent:
    return GoalEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                     minute=minute, side=side)


def corner(minute: float, side: Side, *, seq: int | None = None) -> CornerEvent:
    return CornerEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                       minute=minute, side=side)


def dangerous(minute: float, side: Side, *, seq: int | None = None) -> DangerousAttackEvent:
    return DangerousAttackEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                                minute=minute, side=side)


def attack(minute: float, side: Side, *, seq: int | None = None) -> AttackEvent:
    return AttackEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                       minute=minute, side=side)


def red_card(minute: float, side: Side, *, seq: int | None = None) -> CardEvent:
    return CardEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                     minute=minute, side=side, color=CardColor.RED)


def yellow_card(minute: float, side: Side, *, seq: int | None = None) -> CardEvent:
    return CardEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                     minute=minute, side=side, color=CardColor.YELLOW)


def substitution(minute: float, side: Side, *, seq: int | None = None) -> SubstitutionEvent:
    return SubstitutionEvent(event_id=_next_id(), sequence=seq if seq is not None else next(_counter),
                             minute=minute, side=side)


def window_at(events: Iterable[MatchEvent], minute: float):
    """Convenience: build a default-config window at ``minute``."""
    return build_window(list(events), minute)


@pytest.fixture
def home_siege() -> list[MatchEvent]:
    """A late, one-sided home onslaught (strong +home momentum/pressure)."""
    return [
        shot(80.0, Side.HOME, on_target=True, seq=1),
        shot(81.0, Side.HOME, on_target=True, seq=2),
        corner(82.0, Side.HOME, seq=3),
        dangerous(82.5, Side.HOME, seq=4),
        shot(83.0, Side.HOME, on_target=True, seq=5),
    ]
