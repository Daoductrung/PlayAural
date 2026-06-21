"""Tests for shared perspective-aware turn announcements."""

from dataclasses import dataclass

from ..games.base import Game
from ..users.bot import Bot
from ..users.test_user import MockUser


@dataclass
class TurnTestGame(Game):
    """Minimal game exercising the framework-owned turn pipeline."""

    @classmethod
    def get_name(cls) -> str:
        return "Turn Test"

    @classmethod
    def get_type(cls) -> str:
        return "turntest"

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.set_turn_players(self.get_active_players())


def make_game(*, alice_locale: str = "en") -> tuple[
    TurnTestGame,
    MockUser,
    MockUser,
    MockUser,
]:
    game = TurnTestGame()
    alice = MockUser("Alice", locale=alice_locale, uuid="alice")
    bob = MockUser("Bob", uuid="bob")
    watcher = MockUser("Watcher", uuid="watcher")
    game.add_player("Alice", alice)
    game.add_player("Bob", bob)
    game.add_spectator("Watcher", watcher)
    game.on_start()
    return game, alice, bob, watcher


def test_announce_turn_uses_listener_perspective_for_players_and_spectators() -> None:
    game, alice, bob, watcher = make_game()

    game.announce_turn()

    assert alice.get_last_spoken() == "It is your turn."
    assert bob.get_last_spoken() == "It is Alice's turn."
    assert watcher.get_last_spoken() == "It is Alice's turn."
    assert alice.get_sounds_played() == ["turn.ogg"]
    assert bob.get_sounds_played() == []
    assert watcher.get_sounds_played() == []


def test_advance_turn_recomputes_perspective_for_every_listener() -> None:
    game, alice, bob, watcher = make_game()

    game.advance_turn()

    assert alice.get_last_spoken() == "It is Bob's turn."
    assert bob.get_last_spoken() == "It is your turn."
    assert watcher.get_last_spoken() == "It is Bob's turn."


def test_whose_turn_action_uses_the_same_core_perspective_logic() -> None:
    game, alice, bob, watcher = make_game()
    alice_player, bob_player = game.get_active_players()
    watcher_player = next(player for player in game.players if player.is_spectator)

    game._action_whose_turn(alice_player, "whose_turn")
    game._action_whose_turn(bob_player, "whose_turn")
    game._action_whose_turn(watcher_player, "whose_turn")

    assert alice.get_last_spoken() == "It is your turn."
    assert bob.get_last_spoken() == "It is Alice's turn."
    assert watcher.get_last_spoken() == "It is Alice's turn."


def test_bot_turn_is_announced_in_third_person_to_humans() -> None:
    game = TurnTestGame()
    game.add_player("CPU", Bot("CPU", uuid="cpu"))
    human = MockUser("Alice", uuid="alice")
    watcher = MockUser("Watcher", uuid="watcher")
    game.add_player("Alice", human)
    game.add_spectator("Watcher", watcher)
    game.on_start()

    game.announce_turn()

    assert human.get_last_spoken() == "It is CPU's turn."
    assert watcher.get_last_spoken() == "It is CPU's turn."
    assert human.get_sounds_played() == []


def test_reconnected_active_player_is_still_identified_by_player_id() -> None:
    game, alice, _, _ = make_game()
    alice_player = game.get_active_players()[0]
    reconnected_alice = MockUser("Alice", uuid="alice")

    game.attach_user(alice_player.id, reconnected_alice)
    reconnected_alice.clear_messages()
    game.speak_turn_l(alice_player, buffer="game")

    assert reconnected_alice.get_last_spoken() == "It is your turn."
    assert alice.get_last_spoken() is None


def test_turn_announcement_is_localized_per_listener() -> None:
    game, alice, bob, _ = make_game(alice_locale="vi")

    game.announce_turn()

    assert alice.get_last_spoken() == "Đến lượt bạn."
    assert bob.get_last_spoken() == "It is Alice's turn."


def test_whose_turn_reports_when_no_turn_is_active() -> None:
    game, alice, _, _ = make_game()
    alice_player = game.get_active_players()[0]
    game.turn_player_ids.clear()

    game._action_whose_turn(alice_player, "whose_turn")

    assert alice.get_last_spoken() == "No one's turn right now."
