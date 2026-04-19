from types import SimpleNamespace

from ..game_utils.cards import Card
from ..games.crazyeights.game import CrazyEightsGame, CrazyEightsOptions
from ..messages.localization import Localization
from ..tables.table import Table
from ..users.bot import Bot
from ..users.test_user import MockUser


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


def test_spectator_is_excluded_from_crazyeights_scores_after_start():
    game = CrazyEightsGame()
    alice_user = MockUser("Alice", uuid="p1")
    bob_user = MockUser("Bob", uuid="p2")
    watcher_user = MockUser("Watcher", uuid="p3")

    alice = game.add_player("Alice", alice_user)
    bob = game.add_player("Bob", bob_user)
    watcher = game.add_player("Watcher", watcher_user)
    watcher.is_spectator = True

    game.on_start()
    alice.score = 12
    bob.score = 4
    game._sync_team_scores()

    alice_user.clear_messages()
    game._action_check_scores(alice, "check_scores")

    spoken = alice_user.get_last_spoken()
    assert spoken is not None
    assert "Alice: 12/500" in spoken
    assert "Bob: 4/500" in spoken
    assert "Watcher" not in spoken


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


def test_resetting_crazyeights_table_does_not_replay_join_sounds():
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    table = Table(table_id="table1", game_type="crazyeights", host="Alice")
    table._server = SimpleNamespace(_users={"Alice": alice, "Bob": bob})
    table.add_member("Alice", alice)
    table.add_member("Bob", bob)

    game = CrazyEightsGame()
    game.setup_keybinds()
    game.add_player("Alice", alice)
    game.add_player("Bob", bob)
    game._table = table
    table._game = game

    alice.clear_messages()
    bob.clear_messages()

    table.reset_game()

    assert "game_crazyeights/personsit.ogg" not in alice.get_sounds_played()
    assert "game_crazyeights/personsit.ogg" not in bob.get_sounds_played()


def test_playing_eight_locks_turn_until_turn_advance():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    game.discard_pile = [Card(suit=3, rank=5, id=100)]
    first.hand = [
        Card(suit=2, rank=8, id=1),
        Card(suit=1, rank=9, id=2),
    ]
    second.hand = [Card(suit=4, rank=7, id=3)]
    game.set_turn_players([first, second])
    game.current_suit = game.top_card.suit
    game.rebuild_all_menus()

    game.execute_action(first, "play_card_1")

    assert game.awaiting_wild_suit is True
    assert [card.id for card in first.hand] == [2]

    game.execute_action(first, "suit_diamonds")

    assert game.awaiting_wild_suit is False
    assert game.wild_wait_ticks == 15

    discard_ids_before = [card.id for card in game.discard_pile]
    game.execute_action(first, "play_card_2")

    assert [card.id for card in first.hand] == [2]
    assert [card.id for card in game.discard_pile] == discard_ids_before
    assert game.current_player == first


def test_non_current_player_turn_menu_still_shows_hand_cards():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    game.discard_pile = [Card(suit=3, rank=5, id=100)]
    first.hand = [Card(id=1, rank=7, suit=3)]
    second.hand = [
        Card(id=2, rank=9, suit=1),
        Card(id=3, rank=4, suit=2),
    ]
    game.set_turn_players([first, second])
    game.current_suit = game.top_card.suit

    game.rebuild_all_menus()

    bob_menu_ids = [item.id for item in bob.menus["turn_menu"]["items"]]
    assert "play_card_2" in bob_menu_ids
    assert "play_card_3" in bob_menu_ids


def test_out_of_turn_visible_card_is_rejected_without_changing_state():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    game.discard_pile = [Card(suit=3, rank=5, id=100)]
    first.hand = [Card(id=1, rank=7, suit=3)]
    second.hand = [Card(id=2, rank=9, suit=1)]
    game.set_turn_players([first, second])
    game.current_suit = game.top_card.suit
    game.rebuild_all_menus()

    discard_ids_before = [card.id for card in game.discard_pile]
    game.execute_action(second, "play_card_2")

    assert [card.id for card in second.hand] == [2]
    assert [card.id for card in game.discard_pile] == discard_ids_before
    assert bob.get_last_spoken() == Localization.get("en", "action-not-your-turn")
