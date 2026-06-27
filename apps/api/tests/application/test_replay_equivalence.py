"""End-to-end replay equivalence — the governing principle, as a test.

Proves:

    Live Frames -> Reducer -> Fingerprint
        ==
    Serialized Frames -> Deserialized Frames -> Reducer -> Fingerprint

i.e. round-tripping every frame through its on-tape serialization changes nothing
about the resulting snapshot stream — there is one pipeline, and replay reproduces
the live path byte-for-byte.
"""
from __future__ import annotations

import json

from pulse.application.fingerprint import fingerprint
from pulse.application.frames import decode_frame, encode_frame
from pulse.application.reduction import reduce_frames

from .conftest import sample_match_frames


def _serialize_roundtrip(frames):
    """Encode each frame to JSON bytes and decode back — the tape round-trip."""
    return [decode_frame(json.loads(json.dumps(encode_frame(f)))) for f in frames]


def test_live_and_replay_fingerprints_are_identical():
    live_frames = sample_match_frames()

    # LIVE path
    live = reduce_frames(live_frames)
    live_fps = [fingerprint(s) for s in live.snapshots]

    # REPLAY path: same frames, but forced through serialize -> deserialize
    replay_frames = _serialize_roundtrip(live_frames)
    replay = reduce_frames(replay_frames)
    replay_fps = [fingerprint(s) for s in replay.snapshots]

    assert live_fps == replay_fps  # byte-for-byte snapshot identity
    assert len(live_fps) == len(live_frames)


def test_live_and_replay_timelines_are_identical():
    live_frames = sample_match_frames()
    replay_frames = _serialize_roundtrip(live_frames)
    assert reduce_frames(live_frames).timeline == reduce_frames(replay_frames).timeline


def test_deserialized_frames_equal_originals():
    live_frames = sample_match_frames()
    assert _serialize_roundtrip(live_frames) == live_frames


def test_single_combined_fingerprint_matches():
    """A digest over the whole snapshot stream is identical for both paths."""
    live_frames = sample_match_frames()
    replay_frames = _serialize_roundtrip(live_frames)

    def stream_digest(frames):
        return "|".join(fingerprint(s) for s in reduce_frames(frames).snapshots)

    assert stream_digest(live_frames) == stream_digest(replay_frames)
