"""Snapshot fingerprint — canonical hash of a MatchSnapshot's meaning.

Purpose
    Provide a cheap, total equality check used by ``VerifyReplay``: re-reduce a
    tape, fingerprint each resulting snapshot, and compare to the stored
    fingerprints. Equal fingerprints == byte-for-byte identical snapshots.

Inputs / Outputs
    canonical_content(MatchState) -> dict   (deterministic, JSON-safe, no metadata)
    fingerprint(MatchState)       -> str    (SHA-256 hex)

Invariants
    * Pure & deterministic.
    * Depends ONLY on semantic content: minute, scoreline, every metric value +
      its ordered explanation, derivations (phase/emotion), the fan read, and any
      momentum-shift signal. NEVER on DB ids or timestamps.
    * Floats are rounded to ``FINGERPRINT_DECIMALS`` so the hash is robust to
      cross-machine float formatting while preserving real differences.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pulse.domain.value_objects.explanation import Explanation
from pulse.domain.value_objects.match_state import MatchState

# Precision at which metric values are frozen for hashing. Far finer than any
# product-meaningful difference; coarse enough to absorb float-format noise.
FINGERPRINT_DECIMALS = 9


def _r(value: float) -> float:
    return round(value, FINGERPRINT_DECIMALS)


def _explanation(exp: Explanation) -> dict[str, Any]:
    return {
        "metric": exp.metric,
        "value": _r(exp.value),
        "raw_value": _r(exp.raw_value),
        "contributors": [[c.label, _r(c.value)] for c in exp.contributors],
    }


def canonical_content(state: MatchState) -> dict[str, Any]:
    """Build the deterministic, metadata-free content dict for a snapshot."""
    fan = state.fan_read
    shift = state.momentum_shift
    return {
        "minute": _r(state.minute),
        "scoreline": {"home": state.scoreline.home, "away": state.scoreline.away},
        "pulse": _explanation(state.pulse.explanation),
        "pressure_home": _explanation(state.pressure_home.explanation),
        "pressure_away": _explanation(state.pressure_away.explanation),
        "momentum": {
            "direction": state.momentum.direction.value,
            **_explanation(state.momentum.explanation),
        },
        "drama": _explanation(state.drama.explanation),
        "confidence": _explanation(state.confidence.explanation),
        "phase": state.phase.value,
        "emotion": state.emotion.value,
        "fan_read": {
            "pulse_band": fan.pulse_band.value,
            "heartbeat_bpm": fan.heartbeat_bpm,
            "drama_band": fan.drama_band.value,
            "drama_stars": fan.drama_stars,
            "momentum_band": fan.momentum_band.value,
            "pressure_home_band": fan.pressure_home_band.value,
            "pressure_away_band": fan.pressure_away_band.value,
            "narration_certainty": fan.narration_certainty.value,
        },
        "momentum_shift": (
            None
            if shift is None
            else {
                "previous_value": _r(shift.previous_value),
                "current_value": _r(shift.current_value),
                "delta": _r(shift.delta),
                "toward": shift.toward.value,
                "minute": _r(shift.minute),
            }
        ),
    }


def fingerprint(state: MatchState) -> str:
    """Return the SHA-256 hex fingerprint of a snapshot's semantic content."""
    payload = json.dumps(
        canonical_content(state),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
