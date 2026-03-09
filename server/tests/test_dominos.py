"""Tests for Dominos game."""

import pytest
from server.games.dominos.game import DominosGame, DominosOptions, Tile
from server.users.test_user import MockUser

def _setup_users(game: DominosGame, num_players: int = 2) -> list[MockUser]:
    users = []
    for i in range(num_players):
        pid = f"player{i}"
        user = MockUser(f"User{i}")
        user._uuid = pid
        users.append(user)
        player = game.create_player(pid, f"User{i}")
        game.players.append(player)
        game.attach_user(pid, user)
    return users

def test_tile_matching():
    tile = Tile(3, 4)
    assert tile.pips == 7
    assert tile.is_double is False
    assert tile.matches(3) is True
    assert tile.matches(4) is True
    assert tile.matches(5) is False

    double = Tile(5, 5)
    assert double.pips == 10
    assert double.is_double is True
    assert double.matches(5) is True
    assert double.matches(4) is False

def test_game_initialization():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    assert game.status == "playing"
    assert game.round == 1
    assert len(game.boneyard) == 28 - 14  # 2 players * 7 tiles
    for player in game.players:
        assert len(player.hand) == 7

def test_play_first_tile():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    player = game.current_player
    tile = player.hand[0]
    game._action_play_tile(player, f"play_tile_{tile.id}")

    assert len(player.hand) == 6
    assert len(game.board) == 1
    assert game.left_end == tile.end1
    assert game.right_end == tile.end2

def test_cannot_play_invalid_tile():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    # Set the board manually to ends that don't match our hand
    game.left_end = 99
    game.right_end = 99

    player = game.current_player
    tile = player.hand[0]

    # We changed _is_tile_enabled to return None so tiles render out-of-turn
    err = game._is_tile_enabled(player, f"play_tile_{tile.id}")
    assert err is None

    # Enforce play verification in the action handler
    game._action_play_tile(player, f"play_tile_{tile.id}")

    # The tile should still be in the hand because playing it failed
    assert len(player.hand) == 7

def test_draw_action():
    game = DominosGame()
    _setup_users(game, 2)
    game.options.game_mode = "draw"
    game.on_start()

    player = game.current_player

    # Empty hand and set board so they must draw
    player.hand = []
    game.left_end = 99
    game.right_end = 99

    err = game._is_draw_enabled(player)
    assert err is None

    initial_boneyard = len(game.boneyard)
    game._action_draw(player, "draw_tile")

    assert len(player.hand) == 1
    assert len(game.boneyard) == initial_boneyard - 1

def test_block_mode_no_draw():
    game = DominosGame()
    _setup_users(game, 2)
    game.options.game_mode = "block"
    game.on_start()

    player = game.current_player
    player.hand = []
    game.left_end = 99
    game.right_end = 99

    err = game._is_draw_enabled(player)
    assert err == "dominos-mode-no-draw"

    err_pass = game._is_pass_enabled(player)
    assert err_pass is None

def test_all_fives_scoring():
    game = DominosGame()
    _setup_users(game, 2)
    game.options.game_mode = "all_fives"
    game.on_start()

    player = game.current_player

    # Setup board
    game.board = [Tile(2, 3)]
    game.left_end = 2
    game.right_end = 3

    tile = Tile(3, 3)
    # Give player an extra tile so playing doesn't end the round
    player.hand = [tile, Tile(0, 0)]

    # Playing Double 3 on the 3. The ends will be 2 (single) and 3 (double).
    # 2 + 6 = 8. Not a multiple of 5.
    game._action_play_tile(player, f"play_tile_{tile.id}")
    assert player.score == 0
    assert game.right_is_double == True

    # Advance the turn because _action_play_tile advances the turn if played
    # The previous tile played successfully, advancing the turn.
    player2 = game.current_player

    # Now let's play a 2-4 on the Left 2.
    tile2 = Tile(2, 4)
    player2.hand = [tile2, Tile(0, 0)]
    # We must explicitly pass the side input because 2-4 only matches the left 2, so it autos.
    game._action_play_tile(player2, f"play_tile_{tile2.id}")
    # New ends: Left is 4 (single), Right is 3 (double).
    # 4 + 6 = 10. Multiple of 5! Score 10 points.
    assert player2.score == 10

def test_play_both_ends_input():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    player = game.current_player

    game.board = [Tile(1, 2)]
    game.left_end = 1
    game.right_end = 2

    tile = Tile(1, 2)
    player.hand = [tile, Tile(0, 0)]

    # Provide the localized string for Left (1)
    # The signature in action handlers is (player, input_value, action_id)
    game._action_play_tile(player, "Left (1)", f"play_tile_{tile.id}")

    # Left end was 1. We played 1-2. New left end is 2.
    assert game.left_end == 2
    assert game.right_end == 2

def test_domino_win():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    player = game.current_player
    other = [p for p in game.players if p != player][0]

    # Player plays their last tile
    player.hand = [Tile(1, 2)]
    other.hand = [Tile(5, 5)] # 10 pips

    game.left_end = 1
    game.right_end = 1

    # Play
    game._action_play_tile(player, f"play_tile_{player.hand[0].id}")

    assert player.score == 10 # Scored the 10 pips from opponent
    # Round increments and deals again
    assert game.round == 2
    assert len(player.hand) == 7

def test_blocked_game_win():
    game = DominosGame()
    _setup_users(game, 2)
    game.on_start()

    p1 = game.current_player
    p2 = [p for p in game.players if p != p1][0]

    p1.hand = [Tile(1, 1)] # 2 pips
    p2.hand = [Tile(6, 6)] # 12 pips

    game.left_end = 99
    game.right_end = 99

    game.boneyard = [] # Empty boneyard forces pass

    # P1 passes
    game._action_pass(p1, "pass_turn")
    # Turn advances to p2 (since it was just one pass)
    assert game.current_player == p2

    # P2 passes
    game._action_pass(p2, "pass_turn")

    # Game blocked. P1 wins (2 < 12).
    # Scored: opponent_pips(12) - winner_pips(2) = 10
    assert p1.score == 10
    assert game.round == 2
