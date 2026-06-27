"""Derived signals — domain events produced BY the engine, not ingested.

Purpose
    Distinguish raw ingested ``MatchEvent`` inputs from signals the engine
    derives, such as a momentum swing crossing a threshold. Downstream modules
    (Story Engine, Notification Engine) subscribe to these.

Invariants
    * Frozen / immutable.
    * Purely derived: reproducible from the same metric inputs.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..value_objects.side import Side


@dataclass(frozen=True)
class MomentumShifted:
    """Emitted when momentum swings by at least the configured threshold.

    previous_value/current_value: signed momentum before and after.
    delta:      ``current_value - previous_value`` (signed swing size).
    toward:     the side the momentum moved toward.
    minute:     game minute at which the shift was detected.
    """

    previous_value: float
    current_value: float
    delta: float
    toward: Side
    minute: float
