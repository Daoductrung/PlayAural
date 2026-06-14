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
    assert game.get_category() == "cards"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 8


def test_crazyeights_options_defaults():
    game = CrazyEightsGame()
    assert game.options.winning_score == 500
    assert game.options.turn_timer == "0"


def test_crazyeights_standard_deal_counts_and_decks():
    two_player_game = CrazyEightsGame()
    for i in range(2):
        two_player_game.add_player(f"P{i}", MockUser(f"P{i}", uuid=f"p{i}"))
    two_player_game.status = "playing"
    two_player_game.game_active = True
    two_player_game._start_new_hand()

    assert all(len(player.hand) == 7 for player in two_player_game.turn_players)
    assert two_player_game.deck.size() == 52 - (2 * 7) - 1

    six_player_game = CrazyEightsGame()
    for i in range(6):
        six_player_game.add_player(f"P{i}", MockUser(f"P{i}", uuid=f"q{i}"))
    six_player_game.status = "playing"
    six_player_game.game_active = True
    six_player_game._start_new_hand()

    assert all(len(player.hand) == 5 for player in six_player_game.turn_players)
    assert six_player_game.deck.size() == 104 - (6 * 5) - 1


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
    game.flush_menus()
    alice.score = 12
    bob.score = 4
    game._sync_team_scores()

    alice_user.clear_messages()
    game._action_check_scores(alice, "check_scores")

    spoken = alice_user.get_spoken_messages()
    assert any("Alice: 12/500" in message for message in spoken)
    assert any("Bob: 4/500" in message for message in spoken)
    assert all("Watcher" not in message for message in spoken)


def test_crazyeights_bot_game_completes():
    options = CrazyEightsOptions(winning_score=50)
    game = CrazyEightsGame(options=options)
    for i in range(2):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()
    game.flush_menus()

    for _ in range(40000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()

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


def test_crazyeights_spectator_broadcast_uses_standard_audio():
    game = CrazyEightsGame()
    alice_user = MockUser("Alice", uuid="p1")
    watcher_user = MockUser("Watcher", uuid="p2")
    game.add_player("Alice", alice_user)
    game.add_spectator("Watcher", watcher_user)
    alice_user.clear_messages()
    watcher_user.clear_messages()

    game.broadcast_sound("join_spectator.ogg")

    assert alice_user.get_sounds_played() == ["join_spectator.ogg"]
    assert watcher_user.get_sounds_played() == ["join_spectator.ogg"]


def test_crazyeights_spectator_toggle_plays_standard_sounds():
    game = CrazyEightsGame()
    alice_user = MockUser("Alice", uuid="p1")
    watcher_user = MockUser("Watcher", uuid="p2")
    game.add_player("Alice", alice_user)
    watcher = game.add_player("Watcher", watcher_user)
    alice_user.clear_messages()
    watcher_user.clear_messages()

    game._action_toggle_spectator(watcher, "toggle_spectator")

    assert "join_spectator.ogg" in alice_user.get_sounds_played()
    assert "join_spectator.ogg" in watcher_user.get_sounds_played()

    alice_user.clear_messages()
    watcher_user.clear_messages()

    game._action_toggle_spectator(watcher, "toggle_spectator")

    assert "leave_spectator.ogg" in alice_user.get_sounds_played()
    assert "leave_spectator.ogg" in watcher_user.get_sounds_played()


def test_crazyeights_spectator_leave_plays_standard_sound():
    game = CrazyEightsGame()
    alice_user = MockUser("Alice", uuid="p1")
    watcher_user = MockUser("Watcher", uuid="p2")
    game.add_player("Alice", alice_user)
    watcher = game.add_spectator("Watcher", watcher_user)
    alice_user.clear_messages()
    watcher_user.clear_messages()

    game._perform_leave_game(watcher)

    assert alice_user.get_sounds_played() == ["leave_spectator.ogg"]
    assert watcher_user.get_sounds_played() == []


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
    game.refresh_menus()
    game.flush_menus()

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


def test_playing_eight_focuses_first_suit_below_hand_cards():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    alice.client_type = "mobile"
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
    game.refresh_menus()
    game.flush_menus()
    alice.clear_messages()

    game.execute_action(first, "play_card_1")
    game.flush_menus()

    item_ids = [item.id for item in alice.menus["turn_menu"]["items"]]
    assert item_ids[:5] == [
        "play_card_2",
        "suit_clubs",
        "suit_diamonds",
        "suit_hearts",
        "suit_spades",
    ]
    turn_updates = [
        message
        for message in alice.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == "suit_clubs"


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

    game.refresh_menus()
    game.flush_menus()

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
    game.refresh_menus()
    game.flush_menus()

    discard_ids_before = [card.id for card in game.discard_pile]
    game.execute_action(second, "play_card_2")

    assert [card.id for card in second.hand] == [2]
    assert [card.id for card in game.discard_pile] == discard_ids_before
    assert bob.get_last_spoken() == Localization.get("en", "action-not-your-turn")


def test_unplayable_card_selection_explains_exact_context():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    game.discard_pile = [Card(suit=3, rank=5, id=100)]
    first.hand = [Card(id=1, rank=9, suit=1)]
    second.hand = [Card(id=2, rank=7, suit=4)]
    game.set_turn_players([first, second])
    game.current_suit = game.top_card.suit
    game.refresh_menus()
    game.flush_menus()
    alice.clear_messages()

    game.execute_action(first, "play_card_1")

    assert [card.id for card in first.hand] == [1]
    assert [card.id for card in game.discard_pile] == [100]
    assert alice.get_last_spoken() == Localization.get(
        "en",
        "crazyeights-error-card-not-playable",
        card=game.format_card(first.hand[0], "en"),
        top=game.format_top_card("en"),
        suit=Localization.get("en", "suit-hearts"),
    )


def test_play_broadcast_uses_first_and_third_person_strings():
    game = CrazyEightsGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    game.discard_pile = [Card(suit=3, rank=5, id=100)]
    card = Card(id=1, rank=7, suit=3)
    first.hand = [card, Card(id=4, rank=9, suit=1)]
    second.hand = [Card(id=2, rank=7, suit=4)]
    game.set_turn_players([first, second])
    game.current_suit = game.top_card.suit
    game.refresh_menus()
    game.flush_menus()
    alice.clear_messages()
    bob.clear_messages()

    game.execute_action(first, "play_card_1")

    assert Localization.get(
        "en", "crazyeights-you-play", card=game.format_card(card, "en")
    ) in alice.get_spoken_messages()
    assert Localization.get(
        "en",
        "crazyeights-player-plays",
        player="Alice",
        card=game.format_card(card, "en"),
    ) in bob.get_spoken_messages()


def test_skip_and_reverse_use_matching_sounds():
    game = CrazyEightsGame()
    alice = MockUser("Alice", uuid="p1")
    game.add_player("Alice", alice)

    game._play_card_sound(Card(id=1, rank=11, suit=3))
    game._play_card_sound(Card(id=2, rank=12, suit=3))

    assert alice.get_sounds_played() == [
        "game_crazyeights/discrev.ogg",
        "game_crazyeights/discskip.ogg",
    ]
