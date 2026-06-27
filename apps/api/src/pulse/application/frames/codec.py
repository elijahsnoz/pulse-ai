"""Frame codec — canonical, versioned serialization of ``MatchFrame``.

Purpose
    Turn a frame into stable bytes for the tape and back again. This is the
    "serializable" leg of the replay contract; ``canonical_bytes`` is the basis
    for deterministic storage and comparison.

Inputs / Outputs
    encode_frame(MatchFrame) -> dict          (JSON-safe, stamped schema_version)
    decode_frame(dict)       -> MatchFrame
    canonical_bytes(MatchFrame) -> bytes       (UTF-8, sorted keys, no whitespace)

Invariants
    * Round-trip identity: ``decode_frame(encode_frame(f)) == f``.
    * Canonical bytes are independent of dict insertion order (sorted keys),
      so equal frames always serialize to identical bytes.
    * Every encoded frame carries ``schema_version``; decoding rejects versions
      it does not understand (forward-safety for tapes).
"""
from __future__ import annotations

import json
from typing import Any

from .event_codec import decode_event, encode_event
from .frame import FrameKind, MatchFrame

# Bump only on a breaking change to the on-tape frame shape. Tapes record this.
SCHEMA_VERSION = 1

_MINUTE_DECIMALS = 3


class FrameDecodeError(ValueError):
    """Raised when a serialized frame cannot be decoded."""


def encode_frame(frame: MatchFrame) -> dict[str, Any]:
    """Serialize a frame to a stable, JSON-safe dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "sequence": frame.sequence,
        "match_minute": round(frame.match_minute, _MINUTE_DECIMALS),
        "kind": frame.kind.value,
        "provider_event_id": frame.provider_event_id,
        "event": encode_event(frame.event) if frame.event is not None else None,
    }


def decode_frame(data: dict[str, Any]) -> MatchFrame:
    """Reconstruct a frame from a dict produced by ``encode_frame``."""
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise FrameDecodeError(
            f"unsupported schema_version: {version!r} (expected {SCHEMA_VERSION})"
        )
    try:
        kind = FrameKind(data["kind"])
    except ValueError as exc:
        raise FrameDecodeError(f"unknown frame kind: {data.get('kind')!r}") from exc

    event_data = data.get("event")
    event = decode_event(event_data) if event_data is not None else None
    return MatchFrame(
        sequence=data["sequence"],
        match_minute=data["match_minute"],
        kind=kind,
        event=event,
        provider_event_id=data.get("provider_event_id"),
    )


def canonical_bytes(frame: MatchFrame) -> bytes:
    """Deterministic byte encoding of a frame (sorted keys, compact)."""
    return json.dumps(
        encode_frame(frame),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
