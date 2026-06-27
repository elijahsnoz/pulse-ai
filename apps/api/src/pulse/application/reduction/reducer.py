"""MatchReducer — the single, source-agnostic pipeline core.

Purpose
    Fold an ordered stream of ``MatchFrame``s into the deterministic outputs every
    downstream system consumes: a ``MatchSnapshot`` per frame, plus a stream of
    ``TimelineEvent``s for the narrative transitions. This is the "one pipeline" —
    live TxLINE, replay tapes and test fixtures all flow through it identically.

Source-agnosticism (hard constraint)
    The reducer consumes ONLY ``MatchFrame`` instances. It has no knowledge of —
    and no branch on — where a frame originated. There is exactly one code path.

Determinism
    Pure fold over the frame order:
      * accumulates the domain event list,
      * derives the scoreline by folding goal events (single source of truth),
      * calls the frozen Module 1 ``MetricEngine`` for each frame,
      * derives TimelineEvents by comparing the new snapshot to the previous one.
    Same frames -> identical snapshots and identical timeline. No wall-clock, no
    randomness: ``match_minute`` comes from the frame.

Usage
    * Streaming/live: ``reducer.push(frame)`` per frame -> a ``ReductionStep``.
    * Batch/replay/tests: ``reduce_frames(frames)`` -> a ``ReductionResult``.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pulse.domain.config import DEFAULT_CONFIG, MetricConfig
from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.intensity_band import IntensityBand
from pulse.domain.value_objects.match_state import MatchState
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from ..frames.frame import MatchFrame
from .config import DEFAULT_TIMELINE_CONFIG, TimelineConfig
from .timeline import (
    CardShown,
    EmotionChanged,
    GoalScored,
    MomentumShiftSignalled,
    PhaseChanged,
    PulseMoment,
    TimelineEvent,
)

# Ascending band order for deterministic "crossed up into a high band" checks.
_BAND_ORDER = list(IntensityBand)


@dataclass(frozen=True)
class ReductionStep:
    """The output for a single frame: its snapshot and any timeline events."""

    frame: MatchFrame
    snapshot: MatchState
    timeline: tuple[TimelineEvent, ...]


@dataclass(frozen=True)
class ReductionResult:
    """The full output of reducing a frame stream."""

    steps: tuple[ReductionStep, ...]

    @property
    def snapshots(self) -> tuple[MatchState, ...]:
        """One snapshot per input frame, in order."""
        return tuple(step.snapshot for step in self.steps)

    @property
    def timeline(self) -> tuple[TimelineEvent, ...]:
        """All timeline events across every step, in emission order."""
        return tuple(event for step in self.steps for event in step.timeline)


class MatchReducer:
    """Stateful, deterministic fold of frames -> snapshots + timeline events."""

    def __init__(
        self,
        metric_config: MetricConfig = DEFAULT_CONFIG,
        timeline_config: TimelineConfig = DEFAULT_TIMELINE_CONFIG,
    ) -> None:
        self._engine = MetricEngine(metric_config)
        self._timeline_config = timeline_config
        self._events: list = []
        self._home = 0
        self._away = 0
        self._previous: MatchState | None = None
        self._timeline_seq = 0

    def push(self, frame: MatchFrame) -> ReductionStep:
        """Advance the fold by one frame and return its snapshot + timeline."""
        if frame.is_event:
            event = frame.event
            self._events.append(event)
            if "scoring" in event.tags:
                if event.side is Side.HOME:
                    self._home += 1
                elif event.side is Side.AWAY:
                    self._away += 1

        scoreline = Scoreline(self._home, self._away)
        state = self._engine.evaluate(
            events=self._events,
            minute=frame.match_minute,
            scoreline=scoreline,
            previous=self._previous,
        )
        timeline = tuple(self._derive_timeline(frame, state))
        self._previous = state
        return ReductionStep(frame=frame, snapshot=state, timeline=timeline)

    # -- internals -----------------------------------------------------------

    def _next_seq(self) -> int:
        seq = self._timeline_seq
        self._timeline_seq += 1
        return seq

    def _derive_timeline(
        self, frame: MatchFrame, state: MatchState
    ) -> list[TimelineEvent]:
        """Emit timeline events for this frame in a fixed, deterministic order."""
        out: list[TimelineEvent] = []
        minute = frame.match_minute

        if frame.is_event:
            event = frame.event
            if "scoring" in event.tags:
                out.append(
                    GoalScored(self._next_seq(), minute, event.side,
                               state.scoreline.home, state.scoreline.away)
                )
            if event.kind == "card":
                out.append(
                    CardShown(self._next_seq(), minute, event.side,
                              "dismissal" in event.tags)
                )

        if state.momentum_shift is not None:
            shift = state.momentum_shift
            out.append(
                MomentumShiftSignalled(self._next_seq(), minute, shift.toward, shift.delta)
            )

        if self._crossed_into_pulse_moment(state):
            out.append(
                PulseMoment(self._next_seq(), minute, state.fan_read.pulse_band,
                            state.pulse.value)
            )

        if self._previous is not None and state.phase is not self._previous.phase:
            out.append(
                PhaseChanged(self._next_seq(), minute, self._previous.phase, state.phase)
            )

        if self._previous is not None and state.emotion is not self._previous.emotion:
            out.append(
                EmotionChanged(self._next_seq(), minute, self._previous.emotion,
                               state.emotion)
            )

        return out

    def _crossed_into_pulse_moment(self, state: MatchState) -> bool:
        """True when the pulse band steps UP into (or within) the high zone."""
        moment_index = _BAND_ORDER.index(self._timeline_config.pulse_moment_band)
        current_index = _BAND_ORDER.index(state.fan_read.pulse_band)
        previous_index = (
            -1
            if self._previous is None
            else _BAND_ORDER.index(self._previous.fan_read.pulse_band)
        )
        return current_index >= moment_index and current_index > previous_index


def reduce_frames(
    frames: Iterable[MatchFrame],
    metric_config: MetricConfig = DEFAULT_CONFIG,
    timeline_config: TimelineConfig = DEFAULT_TIMELINE_CONFIG,
) -> ReductionResult:
    """Reduce a whole frame stream with a fresh reducer (batch/replay/tests)."""
    reducer = MatchReducer(metric_config, timeline_config)
    steps = tuple(reducer.push(frame) for frame in frames)
    return ReductionResult(steps=steps)
