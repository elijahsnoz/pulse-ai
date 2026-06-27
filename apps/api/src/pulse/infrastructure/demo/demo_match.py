"""A scripted demo match tape — deterministic, dramatic, dense enough to animate.

Purpose
    With no live TxLINE credentials, the first visual demo is driven by a recorded
    tape. This builds a believable ~95-minute match (two goals each way, a red
    card, momentum swings) with a clock tick every 0.5 match-minutes so the
    heartbeat evolves smoothly in the browser.

Invariants
    * Pure & deterministic: same frames every call (no randomness, no clock).
    * Frame ``sequence`` and wrapped event ``sequence`` advance together, so the
      window ordering is well-defined.
"""
from __future__ import annotations

from pulse.application.frames.frame import MatchFrame
from pulse.domain.events.football import (
    CardColor,
    CardEvent,
    CornerEvent,
    DangerousAttackEvent,
    GoalEvent,
    ShotEvent,
)
from pulse.domain.value_objects.side import Side

DEMO_MATCH_ID = "demo"
DEMO_HOME = "Argentina"
DEMO_AWAY = "France"

_TICK_INTERVAL = 0.5
_FINAL_MINUTE = 95.0


def _event_specs() -> list[tuple[float, str, Side, dict]]:
    """(minute, type, side, extra) — a scripted, end-to-end-dramatic match."""
    h, a = Side.HOME, Side.AWAY
    specs: list[tuple[float, str, Side, dict]] = []

    # Opening: France press.
    specs += [(3.0, "dangerous_attack", a, {}), (4.5, "shot", a, {"on_target": False}),
              (6.0, "corner", a, {}), (7.5, "shot", a, {"on_target": True})]
    # Argentina surge and score.
    specs += [(9.0, "shot", h, {"on_target": True}), (9.5, "corner", h, {}),
              (10.0, "shot", h, {"on_target": True}), (11.0, "goal", h, {})]
    # France respond, equalise before half.
    specs += [(28.0, "dangerous_attack", a, {}), (33.0, "shot", a, {"on_target": True}),
              (38.0, "goal", a, {})]
    # Second-half end-to-end.
    specs += [(52.0, "shot", h, {"on_target": True}), (57.0, "shot", a, {"on_target": True}),
              (61.0, "dangerous_attack", h, {}), (64.0, "corner", h, {})]
    # France down to ten.
    specs += [(66.0, "card", a, {"red": True})]
    # Argentina lay siege and win it late.
    specs += [(80.0, "shot", h, {"on_target": True}), (83.0, "corner", h, {}),
              (85.0, "shot", h, {"on_target": True}), (88.0, "goal", h, {}),
              (93.0, "shot", a, {"on_target": False})]
    return specs


def _make_event(minute: float, kind: str, side: Side, extra: dict, sequence: int):
    common = dict(event_id=f"demo-{sequence}", sequence=sequence, minute=minute, side=side)
    if kind == "shot":
        return ShotEvent(**common, on_target=extra.get("on_target", False))
    if kind == "corner":
        return CornerEvent(**common)
    if kind == "dangerous_attack":
        return DangerousAttackEvent(**common)
    if kind == "goal":
        return GoalEvent(**common)
    if kind == "card":
        color = CardColor.RED if extra.get("red") else CardColor.YELLOW
        return CardEvent(**common, color=color)
    raise ValueError(f"unhandled demo event kind: {kind}")  # pragma: no cover


def demo_match_frames() -> list[MatchFrame]:
    """Return the scripted demo tape (events + 0.5-minute ticks), in order."""
    events = _event_specs()

    # Tick grid.
    ticks: list[float] = []
    n = 1
    while round(_TICK_INTERVAL * n, 6) <= _FINAL_MINUTE:
        ticks.append(round(_TICK_INTERVAL * n, 6))
        n += 1

    # Merge events (order 0) and ticks (order 1) by minute.
    merged: list[tuple[float, int, tuple | None]] = [
        (m, 0, (m, k, s, x)) for (m, k, s, x) in events
    ]
    merged += [(m, 1, None) for m in ticks]
    merged.sort(key=lambda item: (item[0], item[1]))

    frames: list[MatchFrame] = []
    sequence = 0
    for minute, _order, spec in merged:
        sequence += 1
        if spec is None:
            frames.append(MatchFrame.tick_frame(sequence=sequence, match_minute=minute))
        else:
            m, k, s, x = spec
            event = _make_event(m, k, s, x, sequence)
            frames.append(
                MatchFrame.event_frame(
                    sequence=sequence, event=event, provider_event_id=f"demo-{sequence}"
                )
            )
    return frames
