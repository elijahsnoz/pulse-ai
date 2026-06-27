"""Tests for event + frame serialization (the 'serializable' replay leg)."""
from __future__ import annotations

import pytest

from pulse.application.frames import (
    SCHEMA_VERSION,
    FrameDecodeError,
    MatchFrame,
    canonical_bytes,
    decode_frame,
    encode_frame,
)
from pulse.application.frames.event_codec import (
    EventCodecError,
    decode_event,
    encode_event,
)
from pulse.domain.events.football import (
    AttackEvent,
    CardColor,
    CardEvent,
    CornerEvent,
    DangerousAttackEvent,
    FreeKickEvent,
    GoalEvent,
    ShotEvent,
    SubstitutionEvent,
)
from pulse.domain.value_objects.side import Side

ALL_EVENTS = [
    AttackEvent("a", 1, 10.0, Side.HOME),
    DangerousAttackEvent("b", 2, 11.0, Side.AWAY),
    ShotEvent("c", 3, 12.0, Side.HOME, on_target=False),
    ShotEvent("d", 4, 13.0, Side.HOME, on_target=True),
    CornerEvent("e", 5, 14.0, Side.AWAY),
    FreeKickEvent("f", 6, 15.0, Side.HOME),
    GoalEvent("g", 7, 16.0, Side.HOME),
    CardEvent("h", 8, 17.0, Side.AWAY, color=CardColor.YELLOW),
    CardEvent("i", 9, 18.0, Side.AWAY, color=CardColor.RED),
    SubstitutionEvent("j", 10, 19.0, Side.HOME),
    AttackEvent("k", 11, 20.0, Side.NEUTRAL),
]


@pytest.mark.parametrize("event", ALL_EVENTS, ids=lambda e: type(e).__name__ + str(e.sequence))
def test_event_round_trip_is_identity(event):
    assert decode_event(encode_event(event)) == event


def test_shot_tag_is_stable_regardless_of_on_target():
    on = encode_event(ShotEvent("c", 3, 12.0, Side.HOME, on_target=True))
    off = encode_event(ShotEvent("c", 3, 12.0, Side.HOME, on_target=False))
    assert on["type"] == off["type"] == "shot"
    assert on["on_target"] is True and off["on_target"] is False


def test_unknown_event_tag_raises():
    with pytest.raises(EventCodecError):
        decode_event({"type": "teleport", "event_id": "x", "sequence": 1,
                      "minute": 1.0, "side": "home"})


def test_unregistered_event_type_raises():
    class Mystery(GoalEvent):
        pass

    with pytest.raises(EventCodecError):
        encode_event(Mystery("z", 1, 1.0, Side.HOME))


@pytest.mark.parametrize(
    "frame",
    [
        MatchFrame.event_frame(sequence=7, event=GoalEvent("g", 7, 16.0, Side.HOME),
                               provider_event_id="prov-7"),
        MatchFrame.tick_frame(sequence=8, match_minute=45.25),
    ],
    ids=["event", "tick"],
)
def test_frame_round_trip_is_identity(frame):
    assert decode_frame(encode_frame(frame)) == frame


def test_encoded_frame_stamps_schema_version():
    frame = MatchFrame.tick_frame(sequence=1, match_minute=1.0)
    assert encode_frame(frame)["schema_version"] == SCHEMA_VERSION


def test_decode_rejects_unknown_schema_version():
    frame = MatchFrame.tick_frame(sequence=1, match_minute=1.0)
    data = encode_frame(frame)
    data["schema_version"] = 999
    with pytest.raises(FrameDecodeError):
        decode_frame(data)


def test_decode_rejects_unknown_kind():
    frame = MatchFrame.tick_frame(sequence=1, match_minute=1.0)
    data = encode_frame(frame)
    data["kind"] = "wormhole"
    with pytest.raises(FrameDecodeError):
        decode_frame(data)


def test_canonical_bytes_are_stable_and_order_independent():
    frame = MatchFrame.event_frame(sequence=7, event=GoalEvent("g", 7, 16.0, Side.HOME),
                                   provider_event_id="prov-7")
    assert canonical_bytes(frame) == canonical_bytes(frame)
    # equal frames -> identical bytes
    twin = MatchFrame.event_frame(sequence=7, event=GoalEvent("g", 7, 16.0, Side.HOME),
                                  provider_event_id="prov-7")
    assert canonical_bytes(frame) == canonical_bytes(twin)


def test_canonical_bytes_differ_for_different_frames():
    a = MatchFrame.tick_frame(sequence=1, match_minute=10.0)
    b = MatchFrame.tick_frame(sequence=1, match_minute=10.25)
    assert canonical_bytes(a) != canonical_bytes(b)


def test_minute_is_recorded_at_fixed_precision():
    frame = MatchFrame.tick_frame(sequence=1, match_minute=10.123456789)
    assert encode_frame(frame)["match_minute"] == 10.123
