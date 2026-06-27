"""Wire serialization — snapshots and timeline events for the browser.

Purpose
    Flatten the rich domain objects into compact, UI-friendly JSON. Deliberately
    fan-facing: it sends the heartbeat BPM, vibe bands, drama stars and the
    narration certainty *tier* — and NEVER the raw Confidence number (product
    rule: confidence is an internal dial, not a fan-facing figure).

Invariants
    * Pure functions; JSON-safe output.
    * No Confidence Score value is ever emitted to the client.
"""
from __future__ import annotations

from typing import Any

from pulse.application.reduction.timeline import (
    CardShown,
    EmotionChanged,
    GoalScored,
    MomentumShiftSignalled,
    PhaseChanged,
    PulseMoment,
    TimelineEvent,
)
from pulse.domain.value_objects.match_state import MatchState
from pulse.domain.value_objects.side import Side


def build_meta(home: str, away: str, match_id: str) -> dict[str, Any]:
    """The first message: match identity and team names."""
    return {"type": "meta", "match_id": match_id, "home": home, "away": away}


def snapshot_to_wire(state: MatchState) -> dict[str, Any]:
    """Flatten a snapshot into the live dashboard payload."""
    fan = state.fan_read
    return {
        "type": "snapshot",
        "minute": round(state.minute, 1),
        "score": {"home": state.scoreline.home, "away": state.scoreline.away},
        "pulse": {
            "value": round(state.pulse.value, 1),
            "band": fan.pulse_band.label,
            "bpm": fan.heartbeat_bpm,
        },
        "drama": {
            "value": round(state.drama.value, 1),
            "band": fan.drama_band.label,
            "stars": fan.drama_stars,
        },
        "momentum": {
            "value": round(state.momentum.value, 1),
            "direction": state.momentum.direction.value,
            "band": fan.momentum_band.label,
        },
        "pressure": {
            "home": round(state.pressure_home.value, 1),
            "away": round(state.pressure_away.value, 1),
        },
        "phase": state.phase.label,
        "emotion": state.emotion.label,
        "certainty": fan.narration_certainty.label,  # tier, never the number
    }


def _team(side: Side, home: str, away: str) -> str:
    if side is Side.HOME:
        return home
    if side is Side.AWAY:
        return away
    return ""


def timeline_to_wire(event: TimelineEvent, home: str, away: str) -> dict[str, Any]:
    """Render a timeline event into an icon + human line for the feed."""
    icon, text = _describe(event, home, away)
    return {
        "type": "timeline",
        "kind": event.kind.value,
        "sequence": event.sequence,
        "minute": round(event.minute, 1),
        "icon": icon,
        "text": text,
    }


def _describe(event: TimelineEvent, home: str, away: str) -> tuple[str, str]:
    if isinstance(event, GoalScored):
        return "⚽", f"GOAL! {_team(event.side, home, away)} — {event.home}-{event.away}"
    if isinstance(event, CardShown):
        kind = "Red" if event.is_red else "Yellow"
        icon = "🟥" if event.is_red else "🟨"
        return icon, f"{kind} card — {_team(event.side, home, away)}"
    if isinstance(event, MomentumShiftSignalled):
        return "🔄", f"Momentum shifts to {_team(event.toward, home, away)}"
    if isinstance(event, PulseMoment):
        return "🔥", f"{event.band.label} intensity"
    if isinstance(event, PhaseChanged):
        return "⏱️", event.to_phase.label
    if isinstance(event, EmotionChanged):
        return "🎭", f"Mood: {event.to_state.label}"
    raise TypeError(f"unknown timeline event: {type(event).__name__}")  # pragma: no cover
