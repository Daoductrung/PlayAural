import pytest
from server.games.coup.game import CoupGame
from server.game_utils.bot_helper import BotHelper

def test_bot_executes_all_actions():
    game = CoupGame()
    player_bot = game.create_player(player_id="b1", name="BotBob", is_bot=True)
    player_human = game.create_player(player_id="h1", name="Alice", is_bot=False)
    game.players = [player_bot, player_human]
    game.setup_player_actions(player_bot)
    game.setup_player_actions(player_human)
    game.on_start()

    game.turn_player_ids = [player_bot.id, player_human.id]
    game.turn_index = 0
    game.current_player = player_bot

    actions_to_test = ["income", "foreign_aid", "tax", "exchange", "steal", "assassinate", "coup"]

    for action in actions_to_test:
        print(f"--- TESTING ACTION: {action} ---")

        # reset state
        game.turn_phase = "main"
        player_bot.coins = 10 if action == "coup" else (6 if action == "assassinate" else 2)
        game.is_resolving = False

        # Fake pending action
        player_bot.bot_pending_action = action
        player_bot.bot_think_ticks = 0

        # execution tick
        BotHelper.on_tick(game)

        # Check if it succeeded
        print(f"Action {action} result: pending_action={player_bot.bot_pending_action}, is_resolving={game.is_resolving}, turn_phase={game.turn_phase}")
        if action == "income":
            assert game.turn_phase == "main"
            assert game.current_player == player_human # turn advanced
        elif action in ["foreign_aid", "tax", "exchange", "steal", "assassinate", "coup"]:
            assert game.turn_phase == "action_declared" or game.is_resolving or game.turn_phase == "exchanging"

        # Restore turn for next test
        game.turn_player_ids = [player_bot.id, player_human.id]
        game.turn_index = 0
