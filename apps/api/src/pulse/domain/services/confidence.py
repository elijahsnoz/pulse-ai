"""ConfidenceCalculator — derives the Confidence Score.

Purpose
    Quantify how much to trust the deterministic signal, in [0, 100]. This is NOT
    AI confidence — it is signal confidence, blended from four factors:
      * density     — enough events to be meaningful.
      * coverage    — how much of the window the match has actually filled.
      * consistency — do sub-windows agree on a direction?
      * volatility  — steadier signals are more trustworthy.

Inputs
    window: an ``EventWindow``.

Outputs
    ``ConfidenceScore`` with an additive ``Explanation`` (one contributor per factor).

Invariants
    * Pure & deterministic.
    * Each factor is normalised to [0, 1]; the weighted blend is scaled to [0, 100].
    * Contributors sum to the raw value.
"""
from __future__ import annotations

from ..config import DEFAULT_CONFIG, MetricConfig
from ..numeric import clamp, pstdev, sign
from ..value_objects.explanation import Contributor, Explanation
from ..value_objects.metrics import ConfidenceScore
from .windowing import EventWindow

_METRIC = "confidence_score"


class ConfidenceCalculator:
    """Computes the branded Confidence Score from window support statistics."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def calculate(self, window: EventWindow) -> ConfidenceScore:
        """Return the Confidence Score for ``window``."""
        cfg = self._config.confidence

        density = clamp(len(window) / cfg.expected_events_per_window, 0.0, 1.0)

        covered = min(window.current_minute, window.window_minutes)
        coverage = clamp(
            covered / window.window_minutes if window.window_minutes > 0 else 1.0,
            0.0,
            1.0,
        )

        buckets = window.signed_buckets(
            cfg.volatility_buckets, self._config.momentum.scale
        )
        consistency = self._consistency(buckets, cfg.neutral_consistency)

        volatility = pstdev(buckets)
        volatility_factor = clamp(1.0 - volatility / cfg.volatility_reference, 0.0, 1.0)

        total_weight = (
            cfg.density_weight
            + cfg.coverage_weight
            + cfg.consistency_weight
            + cfg.volatility_weight
        )

        def component(weight: float, factor: float) -> float:
            return 100.0 * weight * factor / total_weight

        contributors = (
            Contributor(label="density", value=component(cfg.density_weight, density),
                        detail="event volume vs expected"),
            Contributor(label="coverage", value=component(cfg.coverage_weight, coverage),
                        detail="window time filled"),
            Contributor(label="consistency", value=component(cfg.consistency_weight, consistency),
                        detail="directional agreement across sub-windows"),
            Contributor(label="volatility", value=component(cfg.volatility_weight, volatility_factor),
                        detail="signal steadiness"),
        )
        raw_value = sum(c.value for c in contributors)
        value = clamp(raw_value, 0.0, 100.0)

        explanation = Explanation(
            metric=_METRIC,
            value=value,
            raw_value=raw_value,
            contributors=contributors,
        )
        return ConfidenceScore(value=value, explanation=explanation)

    @staticmethod
    def _consistency(buckets: list[float], neutral: float) -> float:
        """Fraction of non-zero buckets agreeing with the overall direction.

        Returns ``neutral`` when there is no directional signal at all.
        """
        overall = sign(sum(buckets))
        directional = [b for b in buckets if sign(b) != 0]
        if overall == 0 or not directional:
            return neutral
        agreeing = sum(1 for b in directional if sign(b) == overall)
        return agreeing / len(directional)
