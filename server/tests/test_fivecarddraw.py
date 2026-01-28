import json

from server.games.fivecarddraw.game import FiveCardDrawGame, FiveCardDrawOptions
from server.users.test_user import MockUser
from server.users.bot import Bot


def test_draw_game_creation():
    game = FiveCardDrawGame()
    assert game.get_name() == "Five Card Draw"
    assert game.get_name_key() == "game-name-fivecarddraw"
    assert game.get_type() == "fivecarddraw"
    assert game.get_category() == "category-poker"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 5


def test_draw_options_defaults():
    game = FiveCardDrawGame()
    assert game.options.starting_chips == 20000
    assert game.options.ante == 100
    assert game.options.raise_mode == "no_limit"


def test_draw_serialization_round_trip():
    game = FiveCardDrawGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    json_str = game.to_json()
    data = json.loads(json_str)
    assert data["hand_number"] >= 1
    loaded = FiveCardDrawGame.from_json(json_str)
    assert loaded.hand_number == game.hand_number


def test_draw_bot_game_completes():
    options = FiveCardDrawOptions(starting_chips=200, ante=100)
    game = FiveCardDrawGame(options=options)
    for i in range(2):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()
    for _ in range(40000):
        if game.status == "finished":
            break
        game.on_tick()
    if game.status != "finished":
        current = game.current_player.name if game.current_player else None
        betting = game.betting
        active_ids = game._active_betting_ids() if hasattr(game, "_active_betting_ids") else set()
        all_in_ids = game._all_in_ids() if hasattr(game, "_all_in_ids") else set()
        raise AssertionError(
            "Game did not finish. "
            f"status={game.status}, phase={getattr(game, 'phase', None)}, "
            f"hand={getattr(game, 'hand_number', None)}, "
            f"current={current}, "
            f"active={len(active_ids)}, all_in={len(all_in_ids)}, "
            f"betting_current={getattr(betting, 'current_bet', None)}, "
            f"betting_acted={len(getattr(betting, 'acted_since_raise', [])) if betting else None}, "
            f"bets={getattr(betting, 'bets', None)}"
        )


def test_draw_raise_too_large_rejected():
    game = FiveCardDrawGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    player = game.current_player
    assert player is not None
    player.chips = 5
    pot_before = game.pot_manager.total_pot()
    bet_before = game.betting.bets.get(player.id, 0) if game.betting else 0
    game._action_raise(player, "10", "raise")
    assert game.pot_manager.total_pot() == pot_before
    assert game.betting.bets.get(player.id, 0) == bet_before


def test_draw_short_stack_raise_all_in():
    game = FiveCardDrawGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    player = game.current_player
    assert player is not None
    player.chips = 5
    if game.betting:
        game.betting.current_bet = 10
        game.betting.bets[player.id] = 0
    pot_before = game.pot_manager.total_pot()
    game._action_raise(player, "5", "raise")
    assert game.pot_manager.total_pot() == pot_before + 5
    if game.betting:
        assert game.betting.current_bet == 10


def test_draw_short_all_in_does_not_reopen_betting():
    game = FiveCardDrawGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    player = game.current_player
    assert player is not None
    player.chips = 15
    if game.betting:
        game.betting.current_bet = 10
        game.betting.last_raise_size = 10
        game.betting.bets[player.id] = 0
        game.betting.acted_since_raise = set()
    game._action_all_in(player, "all_in")
    if game.betting:
        assert game.betting.current_bet == 10
        assert game.betting.acted_since_raise == {player.id}


def test_draw_underfunded_raise_goes_all_in():
    game = FiveCardDrawGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    player = game.current_player
    assert player is not None
    player.chips = 100
    if game.betting:
        game.betting.current_bet = 90
        game.betting.last_raise_size = 20
        game.betting.bets[player.id] = 0
        game.betting.acted_since_raise = set()
    pot_before = game.pot_manager.total_pot()
    game._action_raise(player, "20", "raise")
    assert game.pot_manager.total_pot() == pot_before + 100
    assert player.all_in is True
    if game.betting:
        assert game.betting.current_bet == 90


def test_draw_all_in_still_draws():
    options = FiveCardDrawOptions(starting_chips=200, ante=100)
    game = FiveCardDrawGame(options=options)
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    game.on_start()
    players = game.get_active_players()
    assert len(players) == 2
    for p in players:
        p.chips = 0
        p.all_in = True
    if game.betting:
        game.betting.current_bet = 100
        game.betting.last_raise_size = 100
        for p in players:
            game.betting.bets[p.id] = 100
        game.betting.acted_since_raise = {p.id for p in players}
    game.current_bet_round = 1
    game._after_action()
    assert game.phase == "draw"
