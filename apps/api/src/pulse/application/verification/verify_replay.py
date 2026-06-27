"""VerifyReplay — assert a tape reproduces byte-for-byte through serialization.

Purpose
    Turn the replay principle into a callable guarantee: reduce a tape directly,
    then reduce it again after a full serialize -> deserialize round-trip, and
    assert the snapshot fingerprints match exactly. Runnable on any tape, in CI or
    at startup — replay fidelity is enforced, not assumed.

Inputs / Outputs
    verify_replay(frames) -> VerifyReplayResult
    verify_tape(store, match_id) -> VerifyReplayResult   (reads from a TapeStore)

Invariants
    * Pure & deterministic.
    * ``passed`` is True iff every snapshot fingerprint matches and counts agree.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pulse.application.fingerprint import fingerprint
from pulse.application.frames.codec import decode_frame, encode_frame
from pulse.application.frames.frame import MatchFrame
from pulse.application.ports import TapeStore
from pulse.application.reduction import reduce_frames
from pulse.application.reduction.config import DEFAULT_TIMELINE_CONFIG, TimelineConfig
from pulse.domain.config import DEFAULT_CONFIG, MetricConfig


@dataclass(frozen=True)
class VerifyReplayResult:
    """Outcome of a replay-fidelity check."""

    passed: bool
    snapshot_count: int
    first_mismatch: int | None


def _fingerprints(
    frames: list[MatchFrame],
    metric_config: MetricConfig,
    timeline_config: TimelineConfig,
) -> list[str]:
    result = reduce_frames(frames, metric_config, timeline_config)
    return [fingerprint(snapshot) for snapshot in result.snapshots]


def verify_replay(
    frames: Iterable[MatchFrame],
    metric_config: MetricConfig = DEFAULT_CONFIG,
    timeline_config: TimelineConfig = DEFAULT_TIMELINE_CONFIG,
) -> VerifyReplayResult:
    """Verify direct reduction == serialize/deserialize round-trip reduction."""
    frames = list(frames)
    reference = _fingerprints(frames, metric_config, timeline_config)

    roundtrip = [decode_frame(encode_frame(frame)) for frame in frames]
    actual = _fingerprints(roundtrip, metric_config, timeline_config)

    first_mismatch = next(
        (i for i, (a, b) in enumerate(zip(reference, actual)) if a != b),
        None,
    )
    passed = first_mismatch is None and len(reference) == len(actual)
    return VerifyReplayResult(
        passed=passed,
        snapshot_count=len(reference),
        first_mismatch=first_mismatch,
    )


def verify_tape(
    store: TapeStore,
    match_id: str,
    metric_config: MetricConfig = DEFAULT_CONFIG,
    timeline_config: TimelineConfig = DEFAULT_TIMELINE_CONFIG,
) -> VerifyReplayResult:
    """Verify a tape persisted in ``store`` reproduces faithfully."""
    return verify_replay(store.read(match_id), metric_config, timeline_config)
