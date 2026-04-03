import pytest
from server.games.coup.game import CoupGame
from server.game_utils.bot_helper import BotHelper
from server.messages.localization import Localization

def test_coup_target_options_format():
    game = CoupGame()
    p1 = game.create_player(player_id="p1", name="Alice")
    p2 = game.create_player(player_id="p2", name="Bob")
    p3 = game.create_player(player_id="b1", name="BotMan", is_bot=True)
    game.players = [p1, p2, p3]
    game.setup_player_actions(p1)
    game.setup_player_actions(p2)
    game.setup_player_actions(p3)
    game.on_start()

    p2.coins = 5
    options = game._target_options(p1)

    # We don't have user contexts in bare test, so it defaults to english "Bob: 5 coins"
    # Actually wait, test runs without users so `get_user` returns None
    assert len(options) == 2
    bob_opt = next(opt for opt in options if "Bob" in opt)
    assert "5" in bob_opt
    assert ":" in bob_opt

    # Test extraction
    extracted = game._extract_target_name(bob_opt)
    assert extracted == "Bob"

def test_bot_select_target_parsing():
    game = CoupGame()
    p1 = game.create_player(player_id="b1", name="BotMan", is_bot=True)
    p2 = game.create_player(player_id="p2", name="Bob")
    game.players = [p1, p2]
    game.on_start()

    p2.coins = 6 # huge threat
    options = game._target_options(p1)

    # Bot evaluates and correctly returns the full formatted string
    selected = game._bot_select_target(p1, options)
    assert selected in options
    assert game._extract_target_name(selected) == "Bob"

def test_handler_extraction():
    game = CoupGame()
    p1 = game.create_player(player_id="b1", name="BotMan", is_bot=True)
    p2 = game.create_player(player_id="p2", name="Bob")
    game.players = [p1, p2]
    game.on_start()

    # Simulate Coup
    p1.coins = 7
    options = game._target_options(p1)
    bob_opt = options[0]

    # Handler should extract "Bob" and find the target successfully, transitioning state
    game._action_coup(p1, bob_opt, "coup")

    assert game.is_resolving == True

    # The delayed lose-influence prompt now lives in the shared sequence runner.
    assert game.has_active_sequence(sequence_id="resolution")
    sequence = game.active_sequences[0]
    op = sequence.beats[0].ops[0]
    assert op.callback_id == "prompt_lose_influence"
    assert op.payload["target_id"] == p2.id
