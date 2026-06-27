"""PulseScorer — derives the Pulse Score (overall match intensity).

Purpose
    Produce the single number that drives the visual heartbeat, in [0, 100].
    Pulse blends three deterministic components:
      * density   — total decayed attacking danger in the window.
      * volatility — how much momentum swings across the window (end-to-end play).
      * tension   — scoreline closeness (a one-goal game runs hotter).

Inputs
    window:    an ``EventWindow``.
    scoreline: current ``Scoreline`` (for tension).

Outputs
    ``PulseScore`` with an additive ``Explanation`` (density + volatility + tension).

Invariants
    * Pure & deterministic.
    * Contributors sum to the raw value; final value clamped to [0, 100].
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..numeric import clamp, pstdev
from ..value_objects.explanation import Contributor, Explanation
from ..value_objects.metrics import PulseScore
from ..value_objects.scoreline import Scoreline
from .windowing import EventWindow

_METRIC = "pulse_score"


class PulseScorer:
    """Computes the branded Pulse Score from a window and the current scoreline."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def calculate(self, window: EventWindow, scoreline: Scoreline) -> PulseScore:
        """Return the Pulse Score for ``window`` given ``scoreline``."""
        cfg = self._config.pulse

        density = window.total_danger()
        density_component = cfg.density_weight * density

        bucket_values = window.signed_buckets(
            cfg.volatility_buckets, self._config.momentum.scale
        )
        volatility = pstdev(bucket_values)
        volatility_component = cfg.volatility_weight * volatility

        # Tension peaks at a level scoreline and decays as the margin widens.
        tension_component = cfg.tension_weight / (1 + scoreline.margin)

        contributors = (
            Contributor(label="density", value=density_component,
                        detail="attacking danger in the window"),
            Contributor(label="volatility", value=volatility_component,
                        detail="momentum swing across the window"),
            Contributor(label="tension", value=tension_component,
                        detail="scoreline closeness"),
        )
        raw_value = density_component + volatility_component + tension_component
        value = clamp(raw_value, 0.0, 100.0)

        explanation = Explanation(
            metric=_METRIC,
            value=value,
            raw_value=raw_value,
            contributors=contributors,
        )
        return PulseScore(value=value, explanation=explanation)
