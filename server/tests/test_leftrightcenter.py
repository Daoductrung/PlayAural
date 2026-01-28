"""
Tests for the Left Right Center game.
"""

import json

from server.games.leftrightcenter.game import (
    LeftRightCenterGame,
    LeftRightCenterOptions,
)
from server.users.test_user import MockUser
from server.users.bot import Bot


def test_game_creation():
    game = LeftRightCenterGame()
    assert game.get_name() == "Left Right Center"
    assert game.get_type() == "leftrightcenter"
    assert game.get_category() == "category-dice-games"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 20


def test_options_defaults():
    game = LeftRightCenterGame()
    assert game.options.starting_chips == 3


def test_player_creation():
    game = LeftRightCenterGame()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    assert player.name == "Alice"
    assert player.chips == 0
    assert player.is_bot is False


def test_serialization_round_trip():
    game = LeftRightCenterGame(options=LeftRightCenterOptions(starting_chips=5))
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()

    game.center_pot = 2
    game.players[0].chips = 4
    game.players[1].chips = 1
    game.turn_index = 1

    json_str = game.to_json()
    data = json.loads(json_str)
    assert data["center_pot"] == 2
    assert data["players"][0]["chips"] == 4

    loaded = LeftRightCenterGame.from_json(json_str)
    assert loaded.center_pot == 2
    assert loaded.players[0].chips == 4
    assert loaded.options.starting_chips == 5


def test_roll_transfers(monkeypatch):
    game = LeftRightCenterGame()
    users = [MockUser("Alice"), MockUser("Bob"), MockUser("Cara")]
    for user in users:
        game.add_player(user.username, user)
    game.on_start()

    sequence = iter(["left", "right", "center"])

    def fake_choice(_):
        return next(sequence)

    monkeypatch.setattr("server.games.leftrightcenter.game.random.choice", fake_choice)

    current = game.current_player
    assert current is not None
    current.chips = 3

    game.execute_action(current, "roll")

    for _ in range(15):
        game.on_tick()

    # Alice passed one chip to Bob, one to Cara, one to center
    assert game.center_pot == 1
    chips = {p.name: p.chips for p in game.players}
    assert chips["Bob"] == 4
    assert chips["Cara"] == 4
    assert chips["Alice"] == 0


def test_winner_detection():
    game = LeftRightCenterGame()
    users = [MockUser("Alice"), MockUser("Bob")]
    for user in users:
        game.add_player(user.username, user)
    game.on_start()

    game.players[0].chips = 0
    game.players[1].chips = 2

    assert game.game_active is True
    assert game._check_for_winner() is True
    assert game.game_active is False


def test_pre_turn_winner_ends_before_roll():
    game = LeftRightCenterGame()
    users = [MockUser("Alice"), MockUser("Bob"), MockUser("Cara")]
    for user in users:
        game.add_player(user.username, user)
    game.on_start()

    # Only Alice has chips before the next turn starts
    game.players[0].chips = 2
    game.players[1].chips = 0
    game.players[2].chips = 0

    assert game.game_active is True
    game._start_turn()
    assert game.game_active is False


def test_bot_game_completes():
    game = LeftRightCenterGame()
    bots = [Bot("Bot1"), Bot("Bot2"), Bot("Bot3")]
    for bot in bots:
        game.add_player(bot.username, bot)
    game.on_start()

    max_ticks = 3000
    for _ in range(max_ticks):
        if not game.game_active:
            break
        game.on_tick()

    assert not game.game_active


def test_team_scores_sync(monkeypatch):
    game = LeftRightCenterGame()
    users = [MockUser("Alice"), MockUser("Bob"), MockUser("Cara")]
    for user in users:
        game.add_player(user.username, user)
    game.on_start()

    sequence = iter(["left", "right", "center"])

    def fake_choice(_):
        return next(sequence)

    monkeypatch.setattr("server.games.leftrightcenter.game.random.choice", fake_choice)

    current = game.current_player
    assert current is not None
    current.chips = 3

    game.execute_action(current, "roll")

    for _ in range(15):
        game.on_tick()

    for p in game.players:
        team = game._team_manager.get_team(p.name)
        assert team is not None
        assert team.total_score == p.chips
