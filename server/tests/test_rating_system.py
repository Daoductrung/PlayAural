from openskill.models import PlackettLuce

from server.game_utils.game_result import GameResult, PlayerResult
import pytest

from server.game_utils.stats_helpers import (
    RatingHelper,
    rating_competitors_from_scores,
)


class FakeRatingDB:
    def __init__(self) -> None:
        self._ratings: dict[tuple[str, str], tuple[float, float]] = {}

    def get_player_rating(self, player_id: str, game_type: str):
        return self._ratings.get((player_id, game_type))

def _default_rating(model: PlackettLuce):
    return model.rating(mu=RatingHelper.DEFAULT_MU, sigma=RatingHelper.DEFAULT_SIGMA)


def test_rating_helper_treats_tied_players_as_separate_competitors() -> None:
    db = FakeRatingDB()
    helper = RatingHelper(db, "testgame")

    result = GameResult(
        game_type="testgame",
        timestamp="2026-03-26T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Alice", False),
            PlayerResult("bob", "Bob", False),
            PlayerResult("charlie", "Charlie", False),
        ],
        custom_data={"winner_ids": ["alice"]},
    )

    teams, ranks = helper.extract_teams_and_ranks(result)
    updated = helper.calculate_updates(teams, ranks)

    model = PlackettLuce()
    expected = model.rate(
        [[_default_rating(model)], [_default_rating(model)], [_default_rating(model)]],
        ranks=[0, 1, 1],
    )

    assert round(updated["alice"].mu, 8) == round(expected[0][0].mu, 8)
    assert round(updated["bob"].mu, 8) == round(expected[1][0].mu, 8)
    assert round(updated["charlie"].mu, 8) == round(expected[2][0].mu, 8)


def test_rating_helper_uses_uuid_competitors_for_true_team_games() -> None:
    db = FakeRatingDB()
    helper = RatingHelper(db, "teamgame")

    result = GameResult(
        game_type="teamgame",
        timestamp="2026-03-26T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Alice", False),
            PlayerResult("bob", "Bob", False),
            PlayerResult("charlie", "Charlie", False),
            PlayerResult("dana", "Dana", False),
        ],
        custom_data={
            "rating_competitors": rating_competitors_from_scores(
                [(["alice", "bob"], 50), (["charlie", "dana"], 30)]
            )
        },
    )

    teams, ranks = helper.extract_teams_and_ranks(result)
    updated = helper.calculate_updates(teams, ranks)

    model = PlackettLuce()
    expected = model.rate(
        [
            [_default_rating(model), _default_rating(model)],
            [_default_rating(model), _default_rating(model)],
        ],
        ranks=[0, 1],
    )

    assert round(updated["alice"].mu, 8) == round(expected[0][0].mu, 8)
    assert round(updated["bob"].mu, 8) == round(expected[0][1].mu, 8)
    assert round(updated["charlie"].mu, 8) == round(expected[1][0].mu, 8)
    assert round(updated["dana"].mu, 8) == round(expected[1][1].mu, 8)


def test_rating_competitors_reject_spoofed_or_duplicate_ids() -> None:
    result = GameResult(
        game_type="teamgame",
        timestamp="2026-03-26T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Alice", False),
            PlayerResult("bob", "Bob", False),
        ],
        custom_data={
            "rating_competitors": [
                {"player_ids": ["alice"], "rank": 0},
                {"player_ids": ["mallory"], "rank": 1},
            ]
        },
    )

    with pytest.raises(ValueError, match="unknown player"):
        RatingHelper.extract_teams_and_ranks(result)


def test_name_only_winner_cannot_route_a_rating_update() -> None:
    result = GameResult(
        game_type="testgame",
        timestamp="2026-03-26T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Shared", False),
            PlayerResult("bob", "Shared", False),
        ],
        custom_data={"winner_name": "Shared"},
    )

    with pytest.raises(ValueError, match="immutable winner ids"):
        RatingHelper.extract_teams_and_ranks(result)


def test_draw_keeps_players_as_separate_tied_competitors() -> None:
    result = GameResult(
        game_type="testgame",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Alice", False),
            PlayerResult("bob", "Bob", False),
        ],
        custom_data={"winner_ids": []},
    )

    assert RatingHelper.extract_teams_and_ranks(result) == (
        [["alice"], ["bob"]],
        [0, 0],
    )


def test_bot_only_competitor_is_removed_without_splitting_human_team() -> None:
    result = GameResult(
        game_type="teamgame",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice", "Alice", False),
            PlayerResult("carol", "Carol", False),
            PlayerResult("ally-bot", "Ally", True),
            PlayerResult("bob", "Bob", False),
            PlayerResult("enemy-bot", "Enemy", True),
        ],
        custom_data={
            "rating_competitors": rating_competitors_from_scores(
                [
                    (["alice", "carol", "ally-bot"], 2),
                    (["bob", "enemy-bot"], 1),
                ]
            )
        },
    )

    assert RatingHelper.extract_teams_and_ranks(result) == (
        [["alice", "carol"], ["bob"]],
        [0, 1],
    )
