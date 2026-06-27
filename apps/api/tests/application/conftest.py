"""Shared frame builders for the application-layer tests."""
from __future__ import annotations

from collections.abc import Sequence

from pulse.application.frames import MatchFrame
from pulse.domain.events.base import MatchEvent
from pulse.domain.events.football import CardColor, CardEvent, GoalEvent, ShotEvent
from pulse.domain.value_objects.side import Side


def event_frame(sequence: int, event: MatchEvent) -> MatchFrame:
    return MatchFrame.event_frame(
        sequence=sequence, event=event, provider_event_id=f"prov-{sequence}"
    )


def tick_frame(sequence: int, minute: float) -> MatchFrame:
    return MatchFrame.tick_frame(sequence=sequence, match_minute=minute)


def frames_from_events(events: Sequence[MatchEvent], start: int = 1) -> list[MatchFrame]:
    return [event_frame(start + i, e) for i, e in enumerate(events)]


def sample_match_frames() -> list[MatchFrame]:
    """A representative tape that triggers several distinct timeline events.

    Designed to exercise: momentum shift, a goal, a red card, phase changes
    (opening -> ... -> final push -> stoppage) and emotion changes. The frame
    ``sequence`` and the wrapped event's ``sequence`` advance together so window
    ordering is well-defined.
    """
    frames: list[MatchFrame] = []
    seq = 0

    def add_tick(minute: float) -> None:
        nonlocal seq
        seq += 1
        frames.append(tick_frame(seq, minute))

    def add_event(make_event) -> None:
        nonlocal seq
        seq += 1
        frames.append(event_frame(seq, make_event(seq)))

    # Opening: away pressing.
    add_tick(1.0)
    for minute in (4.0, 5.0, 6.0):
        add_event(lambda s, m=minute: ShotEvent(f"a{s}", s, m, Side.AWAY, on_target=True))

    # Home surges back hard -> momentum swing.
    for minute in (8.0, 8.5, 9.0, 9.5, 10.0):
        add_event(lambda s, m=minute: ShotEvent(f"h{s}", s, m, Side.HOME, on_target=True))

    # Home goal.
    add_event(lambda s: GoalEvent(f"g{s}", s, 11.0, Side.HOME))

    # Quiet ticks settle the match.
    add_tick(20.0)
    add_tick(40.0)

    # Late drama: red card and a tense finish.
    add_event(lambda s: CardEvent(f"c{s}", s, 78.0, Side.AWAY, color=CardColor.RED))
    add_event(lambda s: ShotEvent(f"h{s}", s, 88.0, Side.HOME, on_target=True))
    add_tick(91.0)  # stoppage time

    return frames
