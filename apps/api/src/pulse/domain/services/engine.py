"""MetricEngine — the single deterministic entry point to all match intelligence.

Purpose
    Orchestrate every calculator/resolver in the correct dependency order and
    return one immutable ``MatchState``. This is the public face of the metric
    engine: upstream code calls ``evaluate`` once per tick and broadcasts the
    result.

Inputs (to ``evaluate``)
    events:    the full ordered list of ``MatchEvent`` so far.
    minute:    the "now" minute to evaluate at.
    scoreline: current ``Scoreline``.
    previous:  the prior ``MatchState`` (optional) for momentum-shift detection.

Outputs
    A fully-populated ``MatchState``.

Invariants
    * Pure & deterministic: identical inputs always yield an identical
      ``MatchState`` — this is what makes Historical Replay reproduce exactly.
    * Stateless across calls (any history is passed in explicitly via ``previous``).
    * Computation order respects dependencies: window -> momentum/pressure ->
      pulse -> drama -> confidence -> phase/emotion -> fan_read.
"""
from __future__ import annotations

from collections.abc import Iterable

from ..config import DEFAULT_CONFIG, MetricConfig
from ..events.base import MatchEvent
from ..value_objects.match_state import MatchState
from ..value_objects.scoreline import Scoreline
from ..value_objects.side import Side
from .confidence import ConfidenceCalculator
from .drama import DramaScorer
from .emotion import EmotionResolver
from .fan_semantics import FanSemantics
from .momentum import MomentumCalculator
from .phase import PhaseResolver
from .pressure import PressureCalculator
from .pulse import PulseScorer
from .shift import ShiftDetector
from .windowing import build_window


class MetricEngine:
    """Deterministic orchestrator producing a ``MatchState`` per evaluation."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config
        self._momentum = MomentumCalculator(config)
        self._pressure = PressureCalculator(config)
        self._pulse = PulseScorer(config)
        self._drama = DramaScorer(config)
        self._confidence = ConfidenceCalculator(config)
        self._phase = PhaseResolver(config)
        self._emotion = EmotionResolver(config)
        self._fan = FanSemantics(config)
        self._shift = ShiftDetector(config)

    @property
    def config(self) -> MetricConfig:
        """The configuration this engine was built with."""
        return self._config

    def evaluate(
        self,
        *,
        events: Iterable[MatchEvent],
        minute: float,
        scoreline: Scoreline,
        previous: MatchState | None = None,
    ) -> MatchState:
        """Compute the complete ``MatchState`` for the given moment."""
        events = list(events)
        window = build_window(events, minute, self._config)

        momentum = self._momentum.calculate(window)
        pressure_home = self._pressure.calculate(window, Side.HOME)
        pressure_away = self._pressure.calculate(window, Side.AWAY)
        pulse = self._pulse.calculate(window, scoreline)
        drama = self._drama.calculate(pulse, window, events, scoreline, minute)
        confidence = self._confidence.calculate(window)
        phase = self._phase.resolve(minute, momentum, drama)
        emotion = self._emotion.resolve(pulse, momentum, drama)
        fan_read = self._fan.derive(
            pulse, drama, momentum, pressure_home, pressure_away, confidence
        )
        shift = self._shift.detect(
            previous.momentum if previous else None, momentum, minute
        )

        return MatchState(
            minute=minute,
            scoreline=scoreline,
            pulse=pulse,
            pressure_home=pressure_home,
            pressure_away=pressure_away,
            momentum=momentum,
            drama=drama,
            confidence=confidence,
            phase=phase,
            emotion=emotion,
            fan_read=fan_read,
            momentum_shift=shift,
        )
