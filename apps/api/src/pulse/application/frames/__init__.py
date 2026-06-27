"""Canonical pipeline frames — the atomic, recordable unit of ingestion.

A ``MatchFrame`` is what enters the pipeline and what gets recorded. It is either
an EVENT frame (wrapping a Module 1 domain event) or a TICK frame (a clock
advance). Live and replay both emit identical frames into the same pipeline.
"""
from .frame import FrameKind, MatchFrame
from .codec import (
    SCHEMA_VERSION,
    FrameDecodeError,
    canonical_bytes,
    decode_frame,
    encode_frame,
)

__all__ = [
    "FrameKind",
    "MatchFrame",
    "SCHEMA_VERSION",
    "FrameDecodeError",
    "canonical_bytes",
    "decode_frame",
    "encode_frame",
]
