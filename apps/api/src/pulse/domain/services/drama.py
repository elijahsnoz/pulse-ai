"""DramaScorer — derives the Drama Index (intensity weighted by stakes).

Purpose
    Amplify the Pulse Score by what is *at stake*, in [0, 100]. A frantic spell
    at 0-0 in minute 20 is intense; the same spell at 1-1 in minute 88 with a red
    card is drama. Stakes are added as transparent, explainable bonuses.

Inputs
    pulse:      the current ``PulseScore``.
    window:     an ``EventWindow`` (for recent goals via the ``"scoring"`` tag).
    all_events: full event list (for red cards via the ``"dismissal"`` tag — a
                sending-off earlier in the match still raises the stakes).
    scoreline:  current ``Scoreline`` (for margin).
    minute:     current match minute (for lateness).

Outputs
    ``DramaIndex`` with an additive ``Explanation``.

Invariants
    * Pure & deterministic; sport-neutral (reasons over tags, not classes).
    * Contributors sum to the raw value; final value clamped to [0, 100].
"""
from __future__ import annotations

from collections.abc import Iterable

from ..config import DEFAULT_CONFIG, MetricConfig
from ..events.base import MatchEvent
from ..numeric import clamp
from ..value_objects.explanation import Contributor, Explanation
from ..value_objects.metrics import DramaIndex, PulseScore
from ..value_objects.scoreline import Scoreline
from .windowing import EventWindow

_METRIC = "drama_index"


class DramaScorer:
    """Computes the branded Drama Index from Pulse plus match stakes."""

    def __init__(self, config: MetricConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def calculate(
        self,
        pulse: PulseScore,
        window: EventWindow,
        all_events: Iterable[MatchEvent],
        scoreline: Scoreline,
        minute: float,
    ) -> DramaIndex:
        """Return the Drama Index for the current moment."""
        cfg = self._config.drama
        contributors: list[Contributor] = [
            Contributor(label="pulse_base", value=cfg.pulse_weight * pulse.value)
        ]

        if minute >= cfg.late_game_minute:
            contributors.append(
                Contributor(label="late_game", value=cfg.late_game_bonus,
                            detail=f"minute >= {cfg.late_game_minute:g}")
            )

        if scoreline.margin <= cfg.narrow_margin_max:
            contributors.append(
                Contributor(label="narrow_margin", value=cfg.narrow_margin_bonus,
                            detail=f"margin <= {cfg.narrow_margin_max}")
            )

        red_cards = min(
            sum(1 for e in all_events if "dismissal" in e.tags), cfg.red_card_cap
        )
        if red_cards:
            contributors.append(
                Contributor(label="red_cards", value=cfg.red_card_bonus * red_cards,
                            detail=f"{red_cards} dismissal(s)")
            )

        recent_goals = min(window.tag_count("scoring"), cfg.recent_goal_cap)
        if recent_goals:
            contributors.append(
                Contributor(label="recent_goals", value=cfg.recent_goal_bonus * recent_goals,
                            detail=f"{recent_goals} goal(s) in window")
            )

        raw_value = sum(c.value for c in contributors)
        value = clamp(raw_value, 0.0, 100.0)

        explanation = Explanation(
            metric=_METRIC,
            value=value,
            raw_value=raw_value,
            contributors=tuple(contributors),
        )
        return DramaIndex(value=value, explanation=explanation)
