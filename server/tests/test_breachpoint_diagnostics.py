"""Tests for the Breach Point full-match diagnostic runner."""

import pytest

from server.games.breachpoint.bot import (
    ATTACK_STRATEGY_DIRECT,
    ATTACK_STRATEGY_FAKE,
    ATTACK_STRATEGY_SPLIT,
)
from server.tools.breachpoint_diagnostics import run_match


def test_seeded_diagnostic_completes_without_stalling() -> None:
    diagnostic = run_match(2, seed=7)

    assert diagnostic.stalled_state == ""
    assert diagnostic.result
    assert len(diagnostic.rounds) == sum(diagnostic.final_score)
    assert diagnostic.actions["move"] > 0
    assert diagnostic.actions["shoot"] > 0
    assert diagnostic.purchases
    assert sum(diagnostic.attacks_by_weapon.values()) >= diagnostic.actions["shoot"]
    attack_strategies = {
        round_diagnostic.attack_strategy
        for round_diagnostic in diagnostic.rounds
    }
    assert attack_strategies == {ATTACK_STRATEGY_DIRECT, ATTACK_STRATEGY_SPLIT}
    assert ATTACK_STRATEGY_FAKE not in attack_strategies
    assert all(round_diagnostic.attack_site for round_diagnostic in diagnostic.rounds)
    pistol_rounds = [
        round_diagnostic
        for round_diagnostic in diagnostic.rounds
        if round_diagnostic.regulation_pistol_round
    ]
    assert [round_diagnostic.round_number for round_diagnostic in pistol_rounds] == [
        1,
        8,
    ]

    exact_length = run_match(
        2,
        seed=7,
        maximum_actions=sum(diagnostic.actions.values()),
    )
    assert exact_length.stalled_state == ""
    assert exact_length.final_score == diagnostic.final_score


@pytest.mark.parametrize(
    ("team_size", "match_format", "maximum_actions"),
    ((1, "mr7", 100), (2, "unknown", 100), (2, "mr7", 0)),
)
def test_diagnostic_rejects_invalid_configuration(
    team_size: int,
    match_format: str,
    maximum_actions: int,
) -> None:
    with pytest.raises(ValueError):
        run_match(
            team_size,
            match_format=match_format,
            maximum_actions=maximum_actions,
        )
