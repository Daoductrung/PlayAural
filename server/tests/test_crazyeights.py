from server.games.crazyeights.game import CrazyEightsGame, CrazyEightsOptions
from server.users.bot import Bot


def test_crazyeights_game_creation():
    game = CrazyEightsGame()
    assert game.get_name() == "Crazy Eights"
    assert game.get_name_key() == "game-name-crazyeights"
    assert game.get_type() == "crazyeights"
    assert game.get_category() == "category-card-games"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 8


def test_crazyeights_options_defaults():
    game = CrazyEightsGame()
    assert game.options.winning_score == 500
    assert game.options.turn_timer == "0"


def test_crazyeights_bot_game_completes():
    options = CrazyEightsOptions(winning_score=50)
    game = CrazyEightsGame(options=options)
    for i in range(2):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()

    for _ in range(40000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"
