import pytest
from server.games.farkle.game import FarkleGame, FarklePlayer, FarkleOptions
from server.users.test_user import MockUser

@pytest.fixture
def mock_users():
    return [MockUser("player1"), MockUser("player2")]

@pytest.fixture
def farkle_game(mock_users):
    game = FarkleGame()
    game.add_player("player1", mock_users[0])
    game.add_player("player2", mock_users[1])

    game.on_start()
    return game

def test_farkle_game_initialization(farkle_game):
    assert len(farkle_game.players) == 2
    assert farkle_game.status == "playing"
    assert farkle_game.round == 1

    player1 = farkle_game.get_player_by_name("player1")
    assert isinstance(player1, FarklePlayer)
    assert player1.score == 0
    assert player1.turn_score == 0

def test_minimal_entrance_score(farkle_game):
    # Set custom entrance score
    farkle_game.options.min_entrance_score = 100

    player = farkle_game.current_player
    assert player.score == 0

    # Try to bank with 0 score (should fail - already handled by can_bank check, but we want to test our specific condition)
    player.turn_score = 50
    # Add a mock dice so has_scoring_dice check passes or len(dice.values) == 0 passes
    player.dice.values = []

    # Check if bank is enabled - should fail due to entrance score
    assert farkle_game._is_bank_enabled(player) == "farkle-must-reach-entrance-score"

    # Increase turn score to meet requirement
    player.turn_score = 100
    assert farkle_game._is_bank_enabled(player) is None

    # Increase turn score to exceed requirement
    player.turn_score = 150
    assert farkle_game._is_bank_enabled(player) is None

def test_minimal_bank_score(farkle_game):
    # Set custom scores
    farkle_game.options.min_entrance_score = 100
    farkle_game.options.min_bank_score = 30

    player = farkle_game.current_player
    # Player has already entered the game
    player.score = 200

    # Try to bank with less than bank score
    player.turn_score = 20
    player.dice.values = []

    # Should fail due to bank score
    assert farkle_game._is_bank_enabled(player) == "farkle-must-reach-bank-score"

    # Increase turn score to meet requirement
    player.turn_score = 30
    assert farkle_game._is_bank_enabled(player) is None

    # Increase turn score to exceed requirement
    player.turn_score = 50
    assert farkle_game._is_bank_enabled(player) is None

def test_bot_think_entrance_score(farkle_game):
    farkle_game.options.min_entrance_score = 100

    bot_player = farkle_game.get_player_by_name("player2")
    bot_player.is_bot = True
    bot_player.score = 0
    bot_player.turn_score = 50
    bot_player.dice.values = []

    # Bot shouldn't bank yet, hasn't reached entrance score
    action = farkle_game.bot_think(bot_player)
    # The action could be "roll" or a scoring combo, but NOT "bank"
    assert action != "bank"

def test_bot_think_bank_score(farkle_game):
    farkle_game.options.min_bank_score = 30

    bot_player = farkle_game.get_player_by_name("player2")
    bot_player.is_bot = True
    bot_player.score = 100 # Already in
    bot_player.turn_score = 20
    bot_player.dice.values = []

    # Bot shouldn't bank yet, hasn't reached bank score
    action = farkle_game.bot_think(bot_player)
    assert action != "bank"
