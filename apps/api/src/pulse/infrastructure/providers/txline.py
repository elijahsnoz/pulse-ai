"""TxLineProvider — the live source, normalising TxLINE events into frames.

Purpose
    Map raw TxLINE-shaped events into canonical ``MatchFrame``s and emit them into
    the SAME pipeline the replay provider feeds. All TxLINE-specific knowledge —
    field names, dedupe, ordering, tick interleaving — is quarantined here, so the
    rest of the system stays provider-agnostic.

Scope (deliberately minimal)
    Pull-based: given an iterable of raw event dicts (one poll's worth or a whole
    match), it normalises, de-duplicates by provider id, assigns gap-free
    sequences, and interleaves clock ticks at a fixed match-minute cadence.
    Network/auth/polling live above this and are wired when credentials exist.

Raw event shape (free-tier subset)
    {"id": "tx-42", "minute": 83.0, "type": "shot", "team": "home",
     "on_target": true}                         # or "card":"red", etc.

Invariants
    * Deterministic given the same raw events + cadence.
    * Output frames are byte-identical in form to recorded frames (same codec).
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from pulse.application.frames.frame import MatchFrame
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

_SIDE_BY_NAME = {"home": Side.HOME, "away": Side.AWAY, "neutral": Side.NEUTRAL}


class TxLineNormalizationError(ValueError):
    """Raised when a raw TxLINE event cannot be normalised."""


def normalize_txline_event(raw: dict[str, Any], sequence: int) -> MatchEvent:
    """Convert one raw TxLINE event dict into a domain ``MatchEvent``."""
    kind = raw.get("type")
    side = _SIDE_BY_NAME.get(raw.get("team", "neutral"), Side.NEUTRAL)
    minute = float(raw["minute"])
    event_id = str(raw["id"])
    common = dict(event_id=event_id, sequence=sequence, minute=minute, side=side)

    if kind == "attack":
        return AttackEvent(**common)
    if kind == "dangerous_attack":
        return DangerousAttackEvent(**common)
    if kind == "shot":
        return ShotEvent(**common, on_target=bool(raw.get("on_target", False)))
    if kind == "corner":
        return CornerEvent(**common)
    if kind == "free_kick":
        return FreeKickEvent(**common)
    if kind == "goal":
        return GoalEvent(**common)
    if kind == "card":
        color = CardColor.RED if raw.get("card") == "red" else CardColor.YELLOW
        return CardEvent(**common, color=color)
    if kind == "substitution":
        return SubstitutionEvent(**common)
    raise TxLineNormalizationError(f"unknown TxLINE event type: {kind!r}")


class TxLineProvider:
    """Normalises raw TxLINE events into canonical frames (live source)."""

    def __init__(
        self,
        raw_events: Iterable[dict[str, Any]],
        *,
        tick_interval: float | None = None,
    ) -> None:
        self._raw_events = list(raw_events)
        self._tick_interval = tick_interval

    def frames(self) -> Iterator[MatchFrame]:
        # De-duplicate by provider id, keep first occurrence, order by minute.
        seen: set[str] = set()
        deduped: list[dict[str, Any]] = []
        for raw in self._raw_events:
            rid = str(raw["id"])
            if rid in seen:
                continue
            seen.add(rid)
            deduped.append(raw)
        deduped.sort(key=lambda r: float(r["minute"]))

        tick_minutes = self._tick_grid(deduped)

        # Merge events and ticks by minute (events before a tick at the same mark).
        merged: list[tuple[float, int, dict | None]] = [
            (float(r["minute"]), 0, r) for r in deduped
        ]
        merged += [(m, 1, None) for m in tick_minutes]
        merged.sort(key=lambda item: (item[0], item[1]))

        sequence = 0
        for minute, _order, raw in merged:
            sequence += 1
            if raw is None:
                yield MatchFrame.tick_frame(sequence=sequence, match_minute=minute)
            else:
                event = normalize_txline_event(raw, sequence)
                yield MatchFrame.event_frame(
                    sequence=sequence, event=event, provider_event_id=str(raw["id"])
                )

    def _tick_grid(self, deduped: list[dict[str, Any]]) -> list[float]:
        """Tick marks at the configured cadence up to the last event minute."""
        if not self._tick_interval or not deduped:
            return []
        last = float(deduped[-1]["minute"])
        marks: list[float] = []
        step = self._tick_interval
        n = 1
        while round(step * n, 6) <= last:
            marks.append(round(step * n, 6))
            n += 1
        return marks
