from pathlib import Path

import pytest

from ..game_utils.teams import TeamManager
from ..games.blackjack.game import BlackjackGame
from ..games.fivecarddraw.game import FiveCardDrawGame
from ..games.holdem.game import HoldemGame
from ..games.leftrightcenter.game import LeftRightCenterGame
from ..games.ludo.game import LudoGame
from ..games.deadmansdeck.game import DeadMansDeckGame
from ..games.ninetynine.game import NinetyNineGame
from ..games.pusoydos.game import PusoyDosGame
from ..games.sorry.game import SorryGame
from ..games.tienlen.game import TienLenGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_team_manager() -> TeamManager:
    manager = TeamManager()
    manager.setup_teams(["Alice", "Bob"])
    manager.add_to_team_score("Alice", 5)
    manager.add_to_team_score("Bob", 2)
    return manager


def test_team_manager_defaults_to_localized_points() -> None:
    manager = make_team_manager()

    assert manager.format_scores_brief("en") == "Alice: 5 points. Bob: 2 points."
    assert manager.format_scores_detailed("en") == [
        "Alice: 5 points",
        "Bob: 2 points",
    ]


def test_team_manager_formats_custom_score_units_in_both_locales() -> None:
    manager = make_team_manager()

    assert (
        manager.format_scores_brief(
            "en",
            score_unit_key="game-score-unit-ninetynine-tokens",
        )
        == "Alice: 5 tokens. Bob: 2 tokens."
    )
    assert (
        manager.format_scores_brief(
            "vi",
            score_unit_key="game-score-unit-ninetynine-tokens",
        )
        == "Alice: 5 thẻ. Bob: 2 thẻ."
    )


def test_team_manager_uses_target_score_for_target_unit_pluralization() -> None:
    manager = TeamManager()
    manager.setup_teams(["Alice", "Bob"])
    manager.add_to_team_score("Alice", 1)

    assert (
        manager.format_scores_brief(
            "en",
            target_score=2,
            score_unit_key="game-score-unit-hand-wins",
        )
        == "Alice: 1/2 hand wins. Bob: 0/2 hand wins."
    )


@pytest.mark.parametrize(
    ("game_cls", "unit_key"),
    [
        (BlackjackGame, "game-score-unit-chips"),
        (FiveCardDrawGame, "game-score-unit-chips"),
        (HoldemGame, "game-score-unit-chips"),
        (LeftRightCenterGame, "game-score-unit-chips"),
        (LudoGame, "game-score-unit-tokens-home"),
        (NinetyNineGame, "game-score-unit-ninetynine-tokens"),
        (PusoyDosGame, "game-score-unit-coins"),
        (SorryGame, "game-score-unit-pawns-home"),
        (TienLenGame, "game-score-unit-hand-wins"),
    ],
)
def test_games_with_non_point_scores_declare_score_unit(game_cls, unit_key) -> None:
    assert game_cls().get_score_unit_key() == unit_key


def test_check_scores_uses_game_score_unit() -> None:
    game = NinetyNineGame()
    alice_user = MockUser("Alice")
    bob_user = MockUser("Bob")
    alice = game.add_player("Alice", alice_user)
    bob = game.add_player("Bob", bob_user)
    game._team_manager.team_mode = "individual"
    game._team_manager.setup_teams(["Alice", "Bob"])
    alice.tokens = 7
    bob.tokens = 3
    game._sync_team_scores()

    game._action_check_scores(alice, "check_scores")

    assert alice_user.get_spoken_messages()[-2:] == [
        "Alice: 7 tokens",
        "Bob: 3 tokens",
    ]


def test_scoreless_game_score_hotkey_is_silent() -> None:
    game = DeadMansDeckGame()
    game.setup_keybinds()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    game.status = "playing"
    game.setup_player_actions(player)

    game.handle_event(player, {"type": "keybind", "key": "s"})
    game.handle_event(player, {"type": "keybind", "key": "shift+s"})

    assert user.get_spoken_messages() == []
