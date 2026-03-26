from openskill.models import PlackettLuce

from server.game_utils.game_result import GameResult, PlayerResult
from server.game_utils.stats_helpers import RatingHelper


class FakeRatingDB:
    def __init__(self) -> None:
        self._ratings: dict[tuple[str, str], tuple[float, float]] = {}

    def get_player_rating(self, player_id: str, game_type: str):
        return self._ratings.get((player_id, game_type))

    def set_player_rating(self, player_id: str, game_type: str, mu: float, sigma: float) -> None:
        self._ratings[(player_id, game_type)] = (mu, sigma)


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

    updated = helper.update_from_result(result)

    model = PlackettLuce()
    expected = model.rate(
        [[_default_rating(model)], [_default_rating(model)], [_default_rating(model)]],
        ranks=[0, 1, 1],
    )

    assert round(updated["alice"].mu, 8) == round(expected[0][0].mu, 8)
    assert round(updated["bob"].mu, 8) == round(expected[1][0].mu, 8)
    assert round(updated["charlie"].mu, 8) == round(expected[2][0].mu, 8)


def test_rating_helper_uses_team_rankings_for_true_team_games() -> None:
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
            "team_rankings": [
                {"members": ["Alice", "Bob"], "score": 50},
                {"members": ["Charlie", "Dana"], "score": 30},
            ]
        },
    )

    updated = helper.update_from_result(result)

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
