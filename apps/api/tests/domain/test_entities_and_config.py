"""Tests for entities and configuration behaviour."""
from __future__ import annotations

import pytest

from pulse.domain.config import (
    DEFAULT_CONFIG,
    MetricConfig,
    MomentumConfig,
)
from pulse.domain.entities.match import Match, MatchStatus
from pulse.domain.entities.team import Team
from pulse.domain.services.engine import MetricEngine
from pulse.domain.value_objects.scoreline import Scoreline
from pulse.domain.value_objects.side import Side

from .conftest import shot


def test_team_identity_equality():
    a = Team(id="t1", name="Argentina")
    b = Team(id="t1", name="Argentina (renamed)")
    c = Team(id="t2", name="France")
    assert a == b
    assert a != c
    assert hash(a) == hash(b)
    assert a != "not-a-team"


def test_match_rejects_identical_teams():
    t = Team(id="t1", name="Argentina")
    with pytest.raises(ValueError):
        Match(id="m1", home=t, away=t)


def test_match_identity_and_live_flag():
    home = Team(id="t1", name="Argentina")
    away = Team(id="t2", name="France")
    m = Match(id="m1", home=home, away=away, status=MatchStatus.LIVE)
    assert m.is_live
    assert m == Match(id="m1", home=home, away=away)
    assert m != Match(id="m2", home=home, away=away)
    assert m != "x"
    assert hash(m) == hash(Match(id="m1", home=home, away=away))


def test_default_scoreline_is_zero_zero():
    m = Match(id="m1", home=Team("t1", "A"), away=Team("t2", "B"))
    assert m.scoreline == Scoreline(0, 0)
    assert m.current_minute == 0.0


def test_weight_for_unknown_kind_is_zero():
    assert DEFAULT_CONFIG.weight_for("does_not_exist") == 0.0
    assert DEFAULT_CONFIG.weight_for("goal") == 1.0


def test_config_is_frozen():
    with pytest.raises(Exception):
        DEFAULT_CONFIG.momentum.scale = 99.0  # type: ignore[misc]


def test_danger_weights_is_read_only():
    # frozen all the way down: the weights mapping itself cannot be mutated,
    # so the shared DEFAULT_CONFIG can never be corrupted by a caller.
    with pytest.raises(TypeError):
        DEFAULT_CONFIG.danger_weights["goal"] = 5.0  # type: ignore[index]


def test_custom_danger_weights_are_coerced_to_read_only():
    cfg = MetricConfig(danger_weights={"goal": 2.0})
    assert cfg.weight_for("goal") == 2.0
    with pytest.raises(TypeError):
        cfg.danger_weights["goal"] = 9.0  # type: ignore[index]


def test_already_read_only_weights_are_accepted_as_is():
    from types import MappingProxyType

    proxy = MappingProxyType({"goal": 3.0})
    cfg = MetricConfig(danger_weights=proxy)
    assert cfg.danger_weights is proxy  # not re-wrapped
    assert cfg.weight_for("goal") == 3.0


def test_shift_threshold_is_independent_of_phase():
    # Decoupled config: tuning shift sensitivity must not touch phase boundaries.
    from pulse.domain.config import PhaseConfig, ShiftConfig

    cfg = MetricConfig(shift=ShiftConfig(swing_threshold=10.0))
    assert cfg.shift.swing_threshold == 10.0
    assert cfg.phase.momentum_window_threshold == PhaseConfig().momentum_window_threshold


def test_overriding_config_changes_output():
    events = [shot(59.0, Side.HOME, on_target=True, seq=1)]
    base = MetricEngine().evaluate(events=events, minute=60.0, scoreline=Scoreline(0, 0))
    tuned = MetricEngine(MetricConfig(momentum=MomentumConfig(scale=40.0))).evaluate(
        events=events, minute=60.0, scoreline=Scoreline(0, 0)
    )
    assert tuned.momentum.value > base.momentum.value


def test_custom_danger_weights_respected():
    cfg = MetricConfig(danger_weights={"shot_on_target": 5.0})
    assert cfg.weight_for("shot_on_target") == 5.0
    assert cfg.weight_for("goal") == 0.0  # not in the custom table
