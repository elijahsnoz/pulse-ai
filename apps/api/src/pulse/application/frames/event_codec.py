"""Event codec — lossless (de)serialization of Module 1 football events.

Purpose
    Convert a domain ``MatchEvent`` to/from a plain, stable dict so it can be
    recorded on the tape and replayed to reconstruct the EXACT same event (value
    equality). Football-specific knowledge lives here, not in the frame.

Inputs / Outputs
    encode_event(MatchEvent) -> dict   (JSON-safe, stable keys)
    decode_event(dict)       -> MatchEvent

Invariants
    * Round-trip identity: ``decode_event(encode_event(e)) == e`` for every
      supported event type (events are frozen dataclasses, compared by value).
    * Each type has a STABLE ``"type"`` tag decoupled from the metric ``kind``
      (e.g. a shot's tag is always ``"shot"`` whether or not it is on target).
    * Unknown tags raise — events can never silently vanish (guards TD-1).
"""
from __future__ import annotations

from typing import Any

from pulse.domain.events.base import MatchEvent
from pulse.domain.events.football import (
    AttackEvent,
    CardColor,
    CardEvent,
    CornerEvent,
    DangerousAttackEvent,
    FreeKickEvent,
    GoalEvent,
    ShotEvent,
    SubstitutionEvent,
)
from pulse.domain.value_objects.side import Side

# Stable serialization tag per concrete event type. NEVER reuse or repurpose a
# tag once tapes exist in the wild — add a new one instead.
_TAG_BY_TYPE: dict[type[MatchEvent], str] = {
    AttackEvent: "attack",
    DangerousAttackEvent: "dangerous_attack",
    ShotEvent: "shot",
    CornerEvent: "corner",
    FreeKickEvent: "free_kick",
    GoalEvent: "goal",
    CardEvent: "card",
    SubstitutionEvent: "substitution",
}
_TYPE_BY_TAG: dict[str, type[MatchEvent]] = {tag: t for t, tag in _TAG_BY_TYPE.items()}

# Minute precision recorded on the tape (canonical, language-neutral).
_MINUTE_DECIMALS = 3


class EventCodecError(ValueError):
    """Raised when an event cannot be encoded or decoded."""


def encode_event(event: MatchEvent) -> dict[str, Any]:
    """Serialize a domain event to a stable, JSON-safe dict."""
    tag = _TAG_BY_TYPE.get(type(event))
    if tag is None:
        raise EventCodecError(f"unregistered event type: {type(event).__name__}")
    data: dict[str, Any] = {
        "type": tag,
        "event_id": event.event_id,
        "sequence": event.sequence,
        "minute": round(event.minute, _MINUTE_DECIMALS),
        "side": event.side.value,
    }
    if isinstance(event, ShotEvent):
        data["on_target"] = event.on_target
    elif isinstance(event, CardEvent):
        data["color"] = event.color.value
    return data


def decode_event(data: dict[str, Any]) -> MatchEvent:
    """Reconstruct a domain event from a dict produced by ``encode_event``."""
    tag = data.get("type")
    cls = _TYPE_BY_TAG.get(tag)
    if cls is None:
        raise EventCodecError(f"unknown event type tag: {tag!r}")

    common = {
        "event_id": data["event_id"],
        "sequence": data["sequence"],
        "minute": data["minute"],
        "side": Side(data["side"]),
    }
    if cls is ShotEvent:
        return ShotEvent(**common, on_target=bool(data["on_target"]))
    if cls is CardEvent:
        return CardEvent(**common, color=CardColor(data["color"]))
    return cls(**common)
