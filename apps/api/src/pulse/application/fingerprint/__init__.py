"""Snapshot fingerprinting — the proof that live and replay agree.

A fingerprint is a SHA-256 over a canonical serialization of a ``MatchSnapshot``'s
SEMANTIC content (metrics, derivations, fan read, explanations) — and nothing
else. Storage metadata (ids, timestamps) is deliberately excluded, so two
snapshots with identical meaning always fingerprint identically.
"""
from .snapshot_fingerprint import (
    FINGERPRINT_DECIMALS,
    canonical_content,
    fingerprint,
)

__all__ = ["FINGERPRINT_DECIMALS", "canonical_content", "fingerprint"]
