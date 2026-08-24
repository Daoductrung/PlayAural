from pathlib import Path

from ..games.uno.game import UnoGame, UnoOptions
from ..games.uno import cards
from ..games.uno.cards import UnoCard
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]


def _card(cid, color, ctype, value=None):
    return UnoCard(id=cid, color=color, type=ctype, value=value)


def _locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line and not line[0].isspace()
    }


# ---------------------------------------------------------------------------
# Metadata / options
# ---------------------------------------------------------------------------


def test_uno_game_creation():
    game = UnoGame()
    assert game.get_name() == "UNO"
    assert game.get_name_key() == "game-name-uno"
    assert game.get_type() == "uno"
    assert game.get_category() == "cards"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 10


def test_uno_options_defaults():
    game = UnoGame()
    assert game.options.winning_score == 300
    assert game.options.scoring_mode == "first_to_limit"
    assert game.options.bluff is True
    assert game.options.skip_after_draw is True
    assert game.options.free_draws == 0
    assert game.options.interceptions is False


def test_uno_blocks_dependent_option_conflicts():
    game = UnoGame(
        options=UnoOptions(
            responses=False,
            advanced_responses=True,
            wait_for_draw_responses=True,
            interceptions=False,
            super_interceptions=True,
        )
    )

    assert game.prestart_validate() == [
        "uno-error-advanced-responses-require-responses",
        "uno-error-wait-responses-require-responses",
        "uno-error-super-interceptions-require-interceptions",
    ]


def test_uno_localization_and_documentation_are_present():
    en_file = ROOT / "server" / "locales" / "en" / "uno.ftl"
    vi_file = ROOT / "server" / "locales" / "vi" / "uno.ftl"
    assert en_file.exists()
    assert vi_file.exists()
    assert _locale_keys(en_file) == _locale_keys(vi_file)
    assert (ROOT / "server" / "documentation" / "content" / "en" / "games" / "uno.md").exists()
    assert (ROOT / "server" / "documentation" / "content" / "vi" / "games" / "uno.md").exists()


def test_uno_blue_color_keybind_shares_b_by_game_state():
    game = UnoGame()
    game.setup_keybinds()

    b_bindings = {(tuple(keybind.actions), keybind.state) for keybind in game._keybinds["b"]}
    assert (("add_bot",), KeybindState.IDLE) in b_bindings
    assert (("color_blue",), KeybindState.ACTIVE) in b_bindings


def test_uno_blue_hotkey_chooses_blue_during_active_color_selection():
    game, first, second = _two_player_game()
    first.hand = [_card(1, cards.WILD, cards.WILD_CARD), _card(2, cards.RED, cards.NUMBER, 5)]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.discard_pile = [_card(100, cards.YELLOW, cards.NUMBER, 5)]
    game.current_color = cards.YELLOW
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    game.handle_event(first, {"type": "keybind", "key": "b"})

    assert game.awaiting_wild_color is False
    assert game.current_color == cards.BLUE


def test_uno_deck_composition():
    deck = cards.build_deck()
    assert len(deck) == 108
    assert sum(1 for c in deck if c.type == cards.WILD_CARD) == 4
    assert sum(1 for c in deck if c.type == cards.WILD_DRAW_FOUR) == 4
    # One zero per color, two of each 1-9 per color.
    zeros = [c for c in deck if c.type == cards.NUMBER and c.value == 0]
    assert len(zeros) == 4
    fives = [c for c in deck if c.type == cards.NUMBER and c.value == 5]
    assert len(fives) == 8
    # Card ids are unique.
    assert len({c.id for c in deck}) == 108


# ---------------------------------------------------------------------------
# Scoring display
# ---------------------------------------------------------------------------


def test_spectator_excluded_from_uno_scores_after_start():
    game = UnoGame(options=UnoOptions(winning_score=500))
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
    assert any("Alice: 12/500" in m for m in spoken)
    assert any("Bob: 4/500" in m for m in spoken)
    assert all("Watcher" not in m for m in spoken)


def test_uno_score_check_omits_pending_interception_penalty_first_mode():
    game, (alice, bob) = _n_player_game(["Alice", "Bob"])
    alice_user = game.get_user(alice)
    assert alice_user is not None
    alice.score = 12
    bob.score = 4
    bob.penalty_points = 3
    alice_user.clear_messages()

    game._action_check_scores(alice, "check_scores")

    spoken = alice_user.get_spoken_messages()
    assert "Alice: 12/300 points." in spoken
    assert "Bob: 4/300 points." in spoken
    assert all("pending interception" not in message for message in spoken)


def test_uno_score_check_omits_pending_interception_penalty_elimination_mode():
    game, (alice, bob) = _n_player_game(
        ["Alice", "Bob"],
        UnoOptions(scoring_mode="elimination", winning_score=100),
    )
    alice_user = game.get_user(alice)
    assert alice_user is not None
    alice.score = 12
    bob.score = 4
    bob.penalty_points = 3
    alice_user.clear_messages()

    game._action_check_scores(alice, "check_scores")

    spoken = alice_user.get_spoken_messages()
    assert "Bob: 4/100 penalty points." in spoken
    assert "Alice: 12/100 penalty points." in spoken
    assert all("pending interception" not in message for message in spoken)


def test_uno_uses_standard_roster_audio():
    game = UnoGame()
    alice_user = MockUser("Alice", uuid="p1")
    watcher_user = MockUser("Watcher", uuid="p2")
    alice = game.add_player("Alice", alice_user)
    watcher = game.add_player("Watcher", watcher_user)
    alice_user.clear_messages()
    watcher_user.clear_messages()

    game._action_toggle_spectator(watcher, "toggle_spectator")
    assert "join_spectator.ogg" in alice_user.get_sounds_played()
    assert "join_spectator.ogg" in watcher_user.get_sounds_played()

    alice_user.clear_messages()
    watcher_user.clear_messages()

    game._action_add_bot(alice, "Botty", "add_bot")
    assert "table_join.ogg" in alice_user.get_sounds_played()
    assert "table_join.ogg" in watcher_user.get_sounds_played()


# ---------------------------------------------------------------------------
# Core mechanics (deterministic)
# ---------------------------------------------------------------------------


def _two_player_game():
    game = UnoGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="p1")
    bob = MockUser("Bob", uuid="p2")
    first = game.add_player("Alice", alice)
    second = game.add_player("Bob", bob)
    game.status = "playing"
    game.game_active = True
    return game, first, second


def test_read_counts_uses_listener_perspective() -> None:
    game, first, second = _two_player_game()
    user = game.get_user(first)
    assert user is not None
    game.set_turn_players([first, second])
    first.hand = [
        _card(1, cards.RED, cards.NUMBER, 5),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.deck = [
        _card(4, cards.YELLOW, cards.NUMBER, 1),
        _card(5, cards.YELLOW, cards.NUMBER, 2),
        _card(6, cards.YELLOW, cards.NUMBER, 3),
    ]
    user.clear_messages()

    game._action_read_counts(first, "read_counts")

    assert user.get_last_spoken() == "You 2, Bob 1, deck 3"


def test_elimination_scoring_uses_personal_and_public_context() -> None:
    game, winner, eliminated = _two_player_game()
    winner_user = game.get_user(winner)
    eliminated_user = game.get_user(eliminated)
    game.options.scoring_mode = "elimination"
    game.options.winning_score = 10
    winner.score = 3
    game.set_turn_players([winner, eliminated])
    winner_user.clear_messages()
    eliminated_user.clear_messages()

    game._score_elimination(winner, [(eliminated, 12)])

    assert eliminated.score == 12
    assert game.status == "finished"
    assert "You add 12 penalty points to your total for this round." in (
        eliminated_user.get_spoken_messages()
    )
    assert "Bob adds 12 penalty points to their total for this round." in (
        winner_user.get_spoken_messages()
    )
    assert "You have reached the 10-point elimination limit and are out of the game." in (
        eliminated_user.get_spoken_messages()
    )
    assert "Bob has reached the 10-point elimination limit and is out of the game." in (
        winner_user.get_spoken_messages()
    )
    assert winner_user.get_last_spoken() == (
        "You are the last player remaining and win with 3 penalty points."
    )
    assert eliminated_user.get_last_spoken() == (
        "Alice is the last player remaining and wins with 3 penalty points."
    )


def test_playing_wild_locks_until_color_then_advances():
    game, first, second = _two_player_game()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_CARD),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    assert game.awaiting_wild_color is True
    assert [c.id for c in first.hand] == [2]

    game.execute_action(first, "color_green")
    assert game.awaiting_wild_color is False
    assert game.current_color == cards.GREEN
    assert game.wild_wait_ticks == 15


def test_playing_wild_focuses_first_color_option_below_hand_cards():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    first_user.client_type = "mobile"
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_CARD),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()
    first_user.clear_messages()

    game.execute_action(first, "play_card_1")
    game.flush_menus()

    item_ids = [item.id for item in first_user.menus["turn_menu"]["items"]]
    assert item_ids[:6] == [
        "uno",
        "play_card_2",
        "color_red",
        "color_yellow",
        "color_green",
        "color_blue",
    ]
    turn_updates = [
        message
        for message in first_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == "color_red"


def test_choose_color_focuses_first_matching_remaining_card():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    first_user.client_type = "mobile"
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_CARD),
        _card(2, cards.GREEN, cards.NUMBER, 7),
        _card(3, cards.BLUE, cards.NUMBER, 9),
        _card(4, cards.GREEN, cards.NUMBER, 4),
    ]
    second.hand = [_card(5, cards.YELLOW, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    game.flush_menus()
    first_user.clear_messages()

    game.execute_action(first, "color_green")
    game.flush_menus()

    turn_updates = [
        message
        for message in first_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == "play_card_4"


def test_choose_color_falls_back_to_first_visible_item_without_matching_card():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    first_user.client_type = "mobile"
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_CARD),
        _card(2, cards.BLUE, cards.NUMBER, 9),
        _card(3, cards.GREEN, cards.NUMBER, 4),
    ]
    second.hand = [_card(4, cards.YELLOW, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    game.flush_menus()
    first_user.clear_messages()

    game.execute_action(first, "color_yellow")
    game.flush_menus()

    item_ids = [item.id for item in first_user.menus["turn_menu"]["items"]]
    assert item_ids[0] == "uno"
    turn_updates = [
        message
        for message in first_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == "uno"


def test_uno_button_hidden_on_desktop_turn_menu_but_hotkey_still_works():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [_card(1, cards.RED, cards.NUMBER, 1)]
    second.hand = [_card(2, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    item_ids = [item.id for item in first_user.menus["turn_menu"]["items"]]
    assert "uno" not in item_ids

    game.handle_event(first, {"type": "keybind", "key": "u"})

    assert first.said_uno is True
    assert "You say UNO!" in first_user.get_spoken_messages()


def test_uno_button_pinned_for_touch_and_reports_invalid_press():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    first_user.client_type = "mobile"
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.RED, cards.NUMBER, 1),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    item_ids = [item.id for item in first_user.menus["turn_menu"]["items"]]
    assert item_ids[0] == "uno"

    first_user.clear_messages()
    game.execute_action(first, "uno")

    assert first_user.get_last_spoken() == "No UNO call is available right now."


def _three_player_game(options=None):
    game = UnoGame(options=options or UnoOptions())
    game.setup_keybinds()
    users = [MockUser(n, uuid=f"p{i}") for i, n in enumerate(["A", "B", "C"])]
    players = [game.add_player(n, users[i]) for i, n in enumerate(["A", "B", "C"])]
    game.status = "playing"
    game.game_active = True
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    game.set_turn_players(players)
    return game, players


def test_start_card_and_color_announcements_use_listener_perspective():
    game, (dealer, left, _) = _three_player_game()
    dealer_user = game.get_user(dealer)
    left_user = game.get_user(left)
    assert dealer_user is not None
    assert left_user is not None
    game.dealer_index = 0
    dealer_user.clear_messages()
    left_user.clear_messages()

    game._broadcast_start_card(_card(101, cards.BLUE, cards.DRAW_TWO))

    assert "You turn up Blue Draw Two." in dealer_user.get_spoken_messages()
    assert "A turns up Blue Draw Two." in left_user.get_spoken_messages()

    dealer_user.clear_messages()
    left_user.clear_messages()

    game._broadcast_color_chosen(left, cards.GREEN)

    assert left_user.get_spoken_messages() == ["You choose Green."]
    assert dealer_user.get_spoken_messages() == ["B chooses Green."]


def test_opening_draw_two_draws_and_skips_player_after_dealer():
    game, (dealer, left, next_player) = _three_player_game()
    game.dealer_index = 0
    game.turn_index = 1
    game.deck = [
        _card(50, cards.BLUE, cards.NUMBER, 1),
        _card(51, cards.GREEN, cards.NUMBER, 2),
    ]
    start = _card(100, cards.RED, cards.DRAW_TWO)

    paused = game._apply_start_card_effect(start)

    assert paused is False
    assert len(left.hand) == 2
    assert game.current_player is next_player


def test_opening_skip_starts_with_player_after_skipped_seat():
    game, (dealer, left, next_player) = _three_player_game()
    game.dealer_index = 0
    game.turn_index = 1
    start = _card(100, cards.RED, cards.SKIP)

    paused = game._apply_start_card_effect(start)

    assert paused is False
    assert game.current_player is next_player


def test_opening_reverse_starts_with_dealer_and_reverses_direction():
    game, (dealer, left, next_player) = _three_player_game()
    game.dealer_index = 0
    game.turn_index = 1
    start = _card(100, cards.RED, cards.REVERSE)

    paused = game._apply_start_card_effect(start)

    assert paused is False
    assert game.turn_direction == -1
    assert game.current_player is dealer


def test_opening_wild_waits_for_first_player_to_choose_color():
    game, (dealer, left, next_player) = _three_player_game()
    left_user = game.get_user(left)
    assert left_user is not None
    game.dealer_index = 0
    game.turn_index = 1
    start = _card(100, cards.WILD, cards.WILD_CARD)

    paused = game._apply_start_card_effect(start)
    game.flush_menus()

    assert paused is True
    assert game.awaiting_wild_color is True
    assert game.opening_wild_color is True
    assert game.wild_color_player_id == left.id
    assert left_user.get_last_spoken() == "Choose the opening color."

    game.execute_action(left, "color_blue")

    assert game.awaiting_wild_color is False
    assert game.opening_wild_color is False
    assert game.current_color == cards.BLUE
    assert game.current_player is left
    assert game.wild_wait_ticks == 0


def test_opening_wild_color_choice_focuses_matching_card():
    game, (dealer, left, next_player) = _three_player_game()
    left_user = game.get_user(left)
    assert left_user is not None
    left_user.client_type = "mobile"
    game.dealer_index = 0
    game.turn_index = 1
    left.hand = [
        _card(1, cards.BLUE, cards.NUMBER, 5),
        _card(2, cards.GREEN, cards.NUMBER, 6),
    ]
    start = _card(100, cards.WILD, cards.WILD_CARD)

    game._apply_start_card_effect(start)
    game.flush_menus()
    left_user.clear_messages()

    game.execute_action(left, "color_green")
    game.flush_menus()

    turn_updates = [
        message
        for message in left_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == "play_card_2"


def test_draw_two_keeps_turn_when_skip_after_draw_off():
    # House rule: forced draw penalties can allow the target to keep their turn.
    game, (a, b, c) = _three_player_game(UnoOptions(skip_after_draw=False))
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")

    assert len(b.hand) == 3  # drew two
    assert game.current_player is b  # B keeps the turn (no skip)
    assert game.cards_to_draw == 0


def test_draw_two_skips_when_skip_after_draw_on():
    game, (a, b, c) = _three_player_game()
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")

    assert len(b.hand) == 3  # drew two
    assert game.current_player is c  # official draw penalty skips B's turn


def test_callout_forces_silent_player_to_draw_two():
    game, first, second = _two_player_game()
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [_card(1, cards.RED, cards.NUMBER, 1)]  # one card, silent
    first.said_uno = False
    first.uno_window_ticks = 10  # window open
    # second holds more than one card so its own UNO branch does not trigger.
    second.hand = [
        _card(2, cards.GREEN, cards.NUMBER, 7),
        _card(5, cards.GREEN, cards.NUMBER, 8),
    ]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(second, "uno")  # call out

    assert len(first.hand) == 3  # 1 + official 2-card penalty


def test_callout_available_after_player_drops_to_one_until_next_action():
    game, first, second = _two_player_game()
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.RED, cards.NUMBER, 1),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [
        _card(3, cards.GREEN, cards.NUMBER, 7),
        _card(5, cards.GREEN, cards.NUMBER, 8),
    ]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    assert first.uno_window_ticks > 0
    assert game.current_player is second

    game.execute_action(second, "uno")

    assert len(first.hand) == 3  # remaining card + official 2-card penalty


def test_callout_closes_after_next_player_draws():
    game, first, second = _two_player_game()
    second_user = game.get_user(second)
    assert second_user is not None
    game.deck = [_card(50, cards.GREEN, cards.NUMBER, 3)]
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.RED, cards.NUMBER, 1),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    assert first.uno_window_ticks > 0
    game.flush_menus()
    game.execute_action(second, "draw")
    assert first.uno_window_ticks == 0

    second_user.clear_messages()
    game.execute_action(second, "uno")

    assert len(first.hand) == 1
    assert second_user.get_last_spoken() == "No UNO call is available right now."


def test_desktop_uno_hotkey_reports_invalid_press():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.RED, cards.NUMBER, 1),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()
    first_user.clear_messages()

    game.handle_event(first, {"type": "keybind", "key": "u"})

    assert first_user.get_last_spoken() == "No UNO call is available right now."


def test_say_uno_protects_from_callout():
    game, first, second = _two_player_game()
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [_card(1, cards.RED, cards.NUMBER, 1)]
    first.uno_window_ticks = 10
    second.hand = [
        _card(2, cards.GREEN, cards.NUMBER, 7),
        _card(5, cards.GREEN, cards.NUMBER, 8),
    ]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "uno")  # first announces UNO
    assert first.said_uno is True

    game.execute_action(second, "uno")  # call-out should now do nothing
    assert len(first.hand) == 1


def test_stale_said_uno_cleared_when_drawing_back_above_one_card():
    # Bug A: once a player reaches one card, says UNO, and then draws back above
    # one card, the stale said_uno flag must clear so they can declare again the
    # next time they reach a single card.
    game, first, second = _two_player_game()
    first.hand = [_card(1, cards.RED, cards.NUMBER, 1)]
    first.said_uno = True
    second.hand = [_card(2, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])

    # Draw back up to two cards; a tick clears the stale declaration.
    first.hand.append(_card(3, cards.BLUE, cards.NUMBER, 4))
    game._tick_uno_window()
    assert first.said_uno is False

    # Back down to one card, the player can announce UNO again.
    first.hand = [_card(1, cards.RED, cards.NUMBER, 1)]
    game.refresh_menus()
    game.flush_menus()
    assert game._is_uno_enabled(first) is None
    game.execute_action(first, "uno")
    assert first.said_uno is True


def test_draw_hidden_during_wild_transition():
    # Bug C: after a player plays a Wild Draw Four and picks a color, the brief
    # wild_wait transition still has them as current player with a pending draw,
    # but the draw action must not appear for them during the animation.
    game, first, second = _two_player_game()
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_DRAW_FOUR),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    game.flush_menus()
    game.execute_action(first, "color_green")
    game.flush_menus()
    assert game.wild_wait_ticks > 0
    assert game.current_player is first
    assert game.cards_to_draw == 4
    # Draw stays hidden/disabled for the wild player during the transition.
    assert game._is_draw_enabled(first) == "action-not-available"
    assert game.find_action(first, "draw") is None


def test_wild_color_transition_blocks_fast_followup_play():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [
        _card(1, cards.WILD, cards.WILD_CARD),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(first, "play_card_1")
    game.execute_action(first, "color_blue")
    assert game.wild_wait_ticks > 0

    discard_ids_before = [card.id for card in game.discard_pile]
    first_user.clear_messages()
    game.execute_action(first, "play_card_2")

    assert [card.id for card in first.hand] == [2]
    assert [card.id for card in game.discard_pile] == discard_ids_before
    assert game.current_player is first
    assert "Wait for the chosen color to take effect" in first_user.get_spoken_messages()[-1]


def test_unplayable_card_reports_match_context():
    game, first, second = _two_player_game()
    first_user = game.get_user(first)
    assert first_user is not None
    game.discard_pile = [_card(100, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    first.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]
    second.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.set_turn_players([first, second])
    game.refresh_menus()
    game.flush_menus()
    first_user.clear_messages()

    game.execute_action(first, "play_card_1")

    spoken = first_user.get_spoken_messages()
    assert any("You cannot play Blue 9." in message for message in spoken)
    assert any("The top card is Red 5" in message for message in spoken)
    assert [card.id for card in first.hand] == [1]


def test_pending_draw_stack_reports_response_context():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(responses=True))
    user_b = game.get_user(b)
    assert user_b is not None
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [
        _card(3, cards.GREEN, cards.NUMBER, 7),
        _card(4, cards.RED, cards.DRAW_TWO),
    ]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    user_b.clear_messages()
    game.execute_action(b, "play_card_3")

    spoken = user_b.get_spoken_messages()
    assert any("draw stack of 2 cards" in message for message in spoken)
    assert [card.id for card in b.hand] == [3, 4]


def test_bot_play_announced_before_uno(monkeypatch):
    # Bug B: a bot dropping to one card must have its card play announced before
    # its UNO declaration, not the other way around.
    import server.games.uno.game as uno_module

    monkeypatch.setattr(uno_module.random, "random", lambda: 0.0)  # force auto-UNO
    game = UnoGame()
    game.setup_keybinds()
    observer = MockUser("Alice", uuid="p1")
    alice = game.add_player("Alice", observer)
    botb = game.add_player("BotB", Bot("BotB"))
    game.status = "playing"
    game.game_active = True
    game.deck = cards.build_deck()
    game.discard_pile = [_card(100, cards.GREEN, cards.NUMBER, 5)]
    game.current_color = cards.GREEN
    botb.hand = [
        _card(2, cards.GREEN, cards.NUMBER, 7),
        _card(3, cards.GREEN, cards.NUMBER, 8),
    ]
    alice.hand = [_card(4, cards.BLUE, cards.NUMBER, 1)]
    game.set_turn_players([botb, alice])
    game.refresh_menus()
    game.flush_menus()
    observer.clear_messages()

    game.execute_action(botb, "play_card_2")

    spoken = observer.get_spoken_messages()
    from ..messages.localization import Localization

    play_text = Localization.get(
        "en", "uno-player-plays", player="BotB",
        card=cards.format_card(_card(2, cards.GREEN, cards.NUMBER, 7), "en"),
    )
    uno_text = Localization.get("en", "uno-says-uno", player="BotB")
    assert play_text in spoken
    assert uno_text in spoken
    assert spoken.index(play_text) < spoken.index(uno_text)


# ---------------------------------------------------------------------------
# Full bot games (both scoring modes terminate)
# ---------------------------------------------------------------------------


def _run_bot_game(scoring_mode: str) -> UnoGame:
    options = UnoOptions(winning_score=30, scoring_mode=scoring_mode)
    game = UnoGame(options=options)
    for i in range(3):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    game.flush_menus()
    for _ in range(80000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()
    return game


def test_bot_game_completes_first_to_limit():
    game = _run_bot_game("first_to_limit")
    assert game.status == "finished"


def test_bot_game_completes_elimination():
    game = _run_bot_game("elimination")
    assert game.status == "finished"


# ---------------------------------------------------------------------------
# Phase 2: house rules
# ---------------------------------------------------------------------------


def _n_player_game(names, options=None):
    game = UnoGame(options=options or UnoOptions())
    game.setup_keybinds()
    players = []
    for i, n in enumerate(names):
        players.append(game.add_player(n, MockUser(n, uuid=f"p{i}")))
    game.status = "playing"
    game.game_active = True
    game.deck = cards.build_deck()
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    game.set_turn_players(players)
    return game, players


def test_draw_two_stacking_accumulates():
    game, (a, b, c) = _n_player_game(["A", "B", "C"], UnoOptions(responses=True, bluff=False))
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.RED, cards.DRAW_TWO), _card(5, cards.BLUE, cards.NUMBER, 8)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # obligation 2 -> B
    assert game.cards_to_draw == 2
    assert game.current_player is b

    game.execute_action(b, "play_card_3")  # stack -> obligation 4 -> C auto-draws 4
    assert len(c.hand) == 5  # 1 + 4
    assert game.cards_to_draw == 0


def test_winning_draw_card_carries_pending_stack():
    # A pending draw obligation the winner inherited must carry over when they
    # respond with their final draw card: d2 (obligation 2) -> B answers with a
    # winning Wild Draw Four -> C draws the full 2 + 4 = 6, not just 4.
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"],
        UnoOptions(responses=True, bluff=False, wait_for_draw_responses=False),
    )
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.WILD, cards.WILD_DRAW_FOUR)]  # last card
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # obligation 2 -> B
    assert game.cards_to_draw == 2
    assert game.current_player is b

    game.execute_action(b, "play_card_3")  # winning Wild Draw Four
    assert len(b.hand) == 0  # B emptied their hand and won the round
    assert len(c.hand) == 1 + 6  # original card + (pending 2 + this card's 4)
    assert game.cards_to_draw == 0


def test_draw_two_auto_accept_when_no_response():
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"], UnoOptions(responses=True, bluff=False, skip_after_draw=False)
    )
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]  # no response
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    assert len(b.hand) == 3  # auto-drew 2
    assert game.current_player is b  # house rule keeps the target's turn
    assert game.cards_to_draw == 0


def test_skip_response_passes_obligation_in_two_player():
    # With advanced responses, a Skip played against a Draw Two must pass the
    # obligation to the opponent, not bounce back and trap the responder. A holds
    # a second draw-two so the obligation visibly stays pending after it passes.
    opts = UnoOptions(responses=True, advanced_responses=True, bluff=False)
    game, (a, b) = _n_player_game(["A", "B"], opts)
    a.hand = [
        _card(1, cards.RED, cards.DRAW_TWO),
        _card(7, cards.RED, cards.DRAW_TWO),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    b.hand = [_card(3, cards.RED, cards.SKIP), _card(5, cards.GREEN, cards.NUMBER, 8)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # obligation 2 -> B
    assert game.current_player is b
    assert game.cards_to_draw == 2

    game.execute_action(b, "play_card_3")  # B skips defensively
    assert len(b.hand) == 1  # B did NOT draw
    assert game.current_player is a  # obligation passed to A
    assert game.cards_to_draw == 2  # still owed, now by A (who can still respond)
    assert game.draw_type == cards.DRAW_TWO


def test_reverse_response_passes_obligation_in_two_player():
    opts = UnoOptions(responses=True, advanced_responses=True, bluff=False)
    game, (a, b) = _n_player_game(["A", "B"], opts)
    a.hand = [
        _card(1, cards.RED, cards.DRAW_TWO),
        _card(7, cards.RED, cards.DRAW_TWO),
        _card(2, cards.BLUE, cards.NUMBER, 9),
    ]
    b.hand = [_card(3, cards.RED, cards.REVERSE), _card(5, cards.GREEN, cards.NUMBER, 8)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # obligation 2 -> B
    game.execute_action(b, "play_card_3")  # B reverses defensively
    assert len(b.hand) == 1  # B did NOT draw
    assert game.current_player is a  # obligation passed to A
    assert game.cards_to_draw == 2


def test_skip_response_passes_obligation_in_three_player():
    # The obligation still moves to the immediate next player with three players.
    opts = UnoOptions(
        responses=True,
        advanced_responses=True,
        bluff=False,
        skip_after_draw=False,
    )
    game, (a, b, c) = _n_player_game(["A", "B", "C"], opts)
    a.hand = [_card(1, cards.RED, cards.DRAW_TWO), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.RED, cards.SKIP), _card(5, cards.GREEN, cards.NUMBER, 8)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # obligation 2 -> B
    game.execute_action(b, "play_card_3")  # B skips
    assert len(b.hand) == 1  # B did NOT draw
    assert game.current_player is c  # obligation moved on to C
    assert len(c.hand) == 3  # C had no response and auto-drew the 2
    assert game.cards_to_draw == 0


def _advance_through_wild(game, ticks=25):
    for _ in range(ticks):
        if game.wild_wait_ticks == 0:
            break
        game.on_tick()
        game.flush_menus()


def test_bluff_challenge_catches_bluffer():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(responses=False, bluff=True))
    # A holds a red card (matching current color) yet plays Wild Draw Four -> bluff.
    a.hand = [_card(1, cards.WILD, cards.WILD_DRAW_FOUR), _card(2, cards.RED, cards.NUMBER, 5)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7), _card(6, cards.GREEN, cards.NUMBER, 8)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    assert game.awaiting_wild_color is True
    assert game.is_bluff is True
    game.execute_action(a, "color_blue")
    _advance_through_wild(game)
    assert game.current_player is b
    assert game.bluff_challenge_available is True

    game.execute_action(b, "bluff_challenge")
    assert len(a.hand) == 1 + 4  # red 5 + the illegal Wild Draw Four penalty
    assert game.cards_to_draw == 0
    assert game.current_player is b  # successful challenger keeps the turn


def test_bluff_challenge_wrong_punishes_challenger():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(responses=False, bluff=True))
    # A has no red card -> Wild Draw Four is legitimate.
    a.hand = [_card(1, cards.WILD, cards.WILD_DRAW_FOUR), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7), _card(6, cards.GREEN, cards.NUMBER, 8)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    assert game.is_bluff is False
    game.execute_action(a, "color_blue")
    _advance_through_wild(game)

    game.execute_action(b, "bluff_challenge")
    assert len(b.hand) == 2 + 6  # original 2 + (4 stack + 2 penalty)
    assert game.cards_to_draw == 0


def test_bluffer_cannot_call_own_bluff():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(responses=False, bluff=True))
    a.hand = [_card(1, cards.WILD, cards.WILD_DRAW_FOUR), _card(2, cards.RED, cards.NUMBER, 5)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7), _card(6, cards.GREEN, cards.NUMBER, 8)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.execute_action(a, "color_blue")
    # During the wild-wait window A is still current and bluff is available, but
    # A must never be offered "Call bluff" on their own Wild Draw Four.
    assert game.bluff_challenge_available is True
    assert game.current_player is a
    assert game._is_bluff_enabled(a) is not None

    _advance_through_wild(game)
    assert game.current_player is b
    assert game._is_bluff_enabled(b) is None  # B may call bluff


def test_zero_rotates_hands():
    game, (a, b, c) = _n_player_game(["A", "B", "C"], UnoOptions(zero_seven_rule=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 0), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    # Hands rotate by +1: A<-B, B<-C, C<-A(remaining blue 9).
    assert [card.id for card in c.hand] == [2]
    assert [card.id for card in a.hand] == [3]


def test_seven_swaps_with_chosen_player():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(zero_seven_rule=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 7), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 3), _card(5, cards.GREEN, cards.NUMBER, 4)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.flush_menus()
    assert game.awaiting_swap_target is True

    game.execute_action(a, f"swap_target_{b.id}")
    assert game.awaiting_swap_target is False
    assert sorted(card.id for card in a.hand) == [3, 5]
    assert [card.id for card in b.hand] == [2]


def test_seven_can_decline_swap():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(zero_seven_rule=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 7), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.flush_menus()
    assert game.awaiting_swap_target is True

    game.execute_action(a, "swap_target_none")  # keep own hand
    assert game.awaiting_swap_target is False
    assert [card.id for card in a.hand] == [2]  # unchanged
    assert [card.id for card in b.hand] == [3]  # unchanged
    assert game.current_player is b  # in-turn seven still advances the turn


def test_swap_hides_other_actions_while_choosing():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(zero_seven_rule=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 7), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 3)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.flush_menus()
    assert game.awaiting_swap_target is True

    # The remaining card and the draw must be hidden during swap selection.
    visible = {ra.action.id for ra in game.get_all_visible_actions(a)}
    assert "play_card_2" not in visible
    assert "draw" not in visible
    assert f"swap_target_{b.id}" in visible
    assert "swap_target_none" in visible


def test_straight_seven_triggers_swap():
    # A seven played as a straight continuation must still trigger the swap, and
    # because it is an out-of-turn play, the turn pointer must not move.
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(straights=True, zero_seven_rule=True))
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 6)]
    game.current_color = cards.RED
    a.hand = [
        _card(1, cards.RED, cards.NUMBER, 6),
        _card(2, cards.RED, cards.NUMBER, 7),
        _card(8, cards.BLUE, cards.NUMBER, 1),
    ]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 3), _card(5, cards.GREEN, cards.NUMBER, 4)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn red 6 -> B
    assert game.current_player is b

    game.execute_action(a, "play_card_2")  # A straights red 7 out of turn
    game.flush_menus()
    assert game.awaiting_swap_target is True
    assert game.swap_player_id == a.id

    game.execute_action(a, f"swap_target_{b.id}")
    assert game.awaiting_swap_target is False
    assert sorted(card.id for card in a.hand) == [3, 5]  # took B's hand
    assert [card.id for card in b.hand] == [8]  # A's remaining card
    assert game.current_player is b  # out-of-turn straight does not move the turn


def test_intercepted_seven_opens_swap_then_replays():
    # An intercepted seven must open the swap (freezing play), and after the swap
    # the interceptor keeps the floor and plays again (number-interception rule).
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"], UnoOptions(interceptions=True, zero_seven_rule=True)
    )
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 7)]
    game.current_color = cards.RED
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 8)]
    c.hand = [_card(4, cards.RED, cards.NUMBER, 7), _card(6, cards.BLUE, cards.NUMBER, 2)]
    game.turn_index = 0  # A current; C intercepts the red 7 out of turn
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(c, "play_card_4")  # exact-match interception of red 7
    game.flush_menus()
    assert game.awaiting_swap_target is True
    assert game.swap_player_id == c.id
    # Frozen: another player cannot play during the swap.
    game.execute_action(a, "play_card_1")
    assert game.top_card.id == 4

    game.execute_action(c, f"swap_target_{a.id}")
    assert game.awaiting_swap_target is False
    assert [card.id for card in c.hand] == [1]  # took A's hand
    assert sorted(card.id for card in a.hand) == [6]  # C's remaining card
    assert game.current_player is c  # interceptor replays after the swap


def test_straight_zero_rotates_hands():
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"], UnoOptions(straights=True, zero_seven_rule=True)
    )
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 1)]
    game.current_color = cards.RED
    a.hand = [
        _card(1, cards.RED, cards.NUMBER, 1),
        _card(2, cards.RED, cards.NUMBER, 0),
        _card(8, cards.BLUE, cards.NUMBER, 9),
    ]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 3)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 5)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn red 1 -> B
    game.execute_action(a, "play_card_2")  # A straights red 0 out of turn
    # Hands rotated by +1: A<-B, B<-C, C<-A(remaining blue 9).
    assert [card.id for card in a.hand] == [3]
    assert [card.id for card in c.hand] == [8]


def test_default_sort_is_number():
    game, (a, b) = _n_player_game(["A", "B"])
    assert a.card_sort_mode == "number"


def test_stuck_turn_auto_resolves():
    # A player who has drawn, has nothing playable, and cannot draw must have
    # their turn ended by the engine (no pass action exists). Guards against the
    # deadlock where an out-of-turn play makes a just-drawn card unplayable.
    game, a, b = _two_player_game()
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 5)]
    game.current_color = cards.RED
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]  # not playable on red 5
    a.turn_has_drawn = True
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.deck = []  # cannot draw
    game.set_turn_players([a, b])
    game.refresh_menus()
    game.flush_menus()
    assert game.current_player is a

    game.on_tick()
    game.flush_menus()
    assert game.current_player is b  # stuck turn auto-resolved


def test_free_draw_allowed_with_playable_card():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(free_draws=2))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 5)]  # playable on red top
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "draw")
    assert a.free_draws_used == 1
    assert len(a.hand) == 2
    assert game.current_player is a  # still A's turn


def test_draw_unplayable_card_auto_skips_turn():
    game, (a, b) = _n_player_game(["A", "B"])
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]  # not playable on red 5 top
    game.deck = [_card(50, cards.GREEN, cards.NUMBER, 3)]  # drawn card also unplayable
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "draw")
    assert len(a.hand) == 2  # drew the card
    assert game.current_player is b  # turn auto-skipped (no pass action)


def test_official_penalty_skip_does_not_skip_playable_ordinary_draw():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(skip_after_draw=True))
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]  # not playable on red top
    game.deck = [_card(50, cards.RED, cards.NUMBER, 3)]  # playable after drawing
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "draw")
    assert len(a.hand) == 2
    assert game.current_player is a  # ordinary draws still follow official UNO


# ---------------------------------------------------------------------------
# Phase 3: interceptions / straights
# ---------------------------------------------------------------------------


def test_interception_steals_play_and_turn():
    game, (a, b, c) = _n_player_game(["A", "B", "C"], UnoOptions(interceptions=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 5), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.RED, cards.NUMBER, 5), _card(6, cards.YELLOW, cards.NUMBER, 1)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn -> B
    assert game.current_player is b

    game.execute_action(c, "play_card_4")  # C intercepts exact red 5 out of turn
    assert game.top_card.id == 4
    assert all(card.id != 4 for card in c.hand)
    assert game.current_player is c  # the interceptor takes the floor


def test_draw_two_interception_plays_as_own_turn():
    # Action-card interceptions resolve as if played on the interceptor's turn:
    # the player to their left draws two, and this house-rule setup lets that
    # target keep the turn afterward.
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"], UnoOptions(interceptions=True, skip_after_draw=False)
    )
    game.discard_pile = [_card(900, cards.RED, cards.DRAW_TWO)]
    game.current_color = cards.RED
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(4, cards.RED, cards.DRAW_TWO), _card(5, cards.BLUE, cards.NUMBER, 8)]
    c.hand = [_card(6, cards.GREEN, cards.NUMBER, 7)]
    game.turn_index = 2  # C is the current player; B intercepts out of turn
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(b, "play_card_4")
    assert game.top_card.id == 4
    assert len(c.hand) == 3  # the player to B's left drew two
    assert game.current_player is c  # C keeps the turn (skip-after-draw off)


def test_skip_interception_plays_as_own_turn():
    game, (a, b, c) = _n_player_game(["A", "B", "C"], UnoOptions(interceptions=True))
    game.discard_pile = [_card(900, cards.RED, cards.SKIP)]
    game.current_color = cards.RED
    a.hand = [_card(1, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(4, cards.RED, cards.SKIP), _card(5, cards.BLUE, cards.NUMBER, 8)]
    c.hand = [_card(6, cards.GREEN, cards.NUMBER, 7)]
    game.turn_index = 2  # C current; B intercepts
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(b, "play_card_4")
    assert game.top_card.id == 4
    assert game.current_player is a  # C (to B's left) skipped, play moves on


def test_super_interception_ignores_color():
    game, (a, b, c) = _n_player_game(
        ["A", "B", "C"], UnoOptions(interceptions=False, super_interceptions=True)
    )
    a.hand = [_card(1, cards.RED, cards.NUMBER, 5), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.YELLOW, cards.NUMBER, 5), _card(6, cards.GREEN, cards.NUMBER, 1)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.execute_action(c, "play_card_4")  # yellow 5 onto red 5 (any color)
    assert game.top_card.id == 4
    assert game.current_color == cards.YELLOW


def test_invalid_interception_penalizes():
    game, (a, b, c) = _n_player_game(["A", "B", "C"], UnoOptions(interceptions=True))
    a.hand = [_card(1, cards.RED, cards.NUMBER, 5), _card(2, cards.BLUE, cards.NUMBER, 9)]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    c.hand = [_card(4, cards.GREEN, cards.NUMBER, 7)]  # not an exact match
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")
    game.execute_action(c, "play_card_4")  # invalid out-of-turn play
    assert c.penalty_points == 3
    assert len(c.hand) == 1  # card not played
    assert game.get_user(c).get_last_spoken() == "Invalid interception. 3 penalty points."


def test_first_to_limit_round_summary_breaks_out_interception_penalty():
    game, winner, loser = _two_player_game()
    winner_user = game.get_user(winner)
    loser_user = game.get_user(loser)
    assert winner_user is not None
    assert loser_user is not None
    game.options.winning_score = 200
    game.set_turn_players([winner, loser])
    loser.hand = [_card(1, cards.RED, cards.NUMBER, 5)]
    loser.penalty_points = 3
    winner_user.clear_messages()
    loser_user.clear_messages()

    game._score_first_to_limit(winner, [(loser, 8)])

    assert any(
        "8 from Bob (5 hand + 3 interception penalty). You gain 8." == message
        for message in winner_user.get_spoken_messages()
    )
    assert any(
        "8 from you (5 hand + 3 interception penalty). Alice gains 8." == message
        for message in loser_user.get_spoken_messages()
    )


def test_elimination_round_summary_breaks_out_interception_penalty():
    game, winner, loser = _two_player_game()
    loser_user = game.get_user(loser)
    assert loser_user is not None
    game.options.scoring_mode = "elimination"
    game.options.winning_score = 200
    game.set_turn_players([winner, loser])
    loser.penalty_points = 3
    loser_user.clear_messages()

    game._score_elimination(winner, [(loser, 8)])

    assert loser_user.get_last_spoken() == (
        "You add 8 penalty points to your total for this round "
        "(5 from your hand plus 3 interception penalty)."
    )


def test_straight_continues_same_player_same_color():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(straights=True))
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 4)]
    game.current_color = cards.RED
    a.hand = [
        _card(1, cards.RED, cards.NUMBER, 5),
        _card(2, cards.RED, cards.NUMBER, 6),
        _card(7, cards.BLUE, cards.NUMBER, 9),
    ]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn red 5 -> B
    assert game.current_player is b

    game.execute_action(a, "play_card_2")  # A straights red 6 out of turn
    assert game.top_card.id == 2
    assert all(card.id != 2 for card in a.hand)
    assert game.current_player is b  # turn pointer unchanged
    assert game.straight_dir == 1


def test_straight_wraps_nine_to_zero_ascending():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(straights=True))
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 4)]
    game.current_color = cards.RED
    a.hand = [
        _card(1, cards.RED, cards.NUMBER, 9),
        _card(2, cards.RED, cards.NUMBER, 0),
        _card(7, cards.BLUE, cards.NUMBER, 5),
    ]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn red 9 -> B
    assert game.current_player is b

    game.execute_action(a, "play_card_2")  # A straights red 0 (9 -> 0 wraps up)
    assert game.top_card.id == 2
    assert all(card.id != 2 for card in a.hand)
    assert game.current_player is b
    assert game.straight_dir == 1


def test_straight_wraps_zero_to_nine_descending():
    game, (a, b) = _n_player_game(["A", "B"], UnoOptions(straights=True))
    game.discard_pile = [_card(900, cards.RED, cards.NUMBER, 4)]
    game.current_color = cards.RED
    a.hand = [
        _card(1, cards.RED, cards.NUMBER, 0),
        _card(2, cards.RED, cards.NUMBER, 9),
        _card(7, cards.BLUE, cards.NUMBER, 5),
    ]
    b.hand = [_card(3, cards.GREEN, cards.NUMBER, 7)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(a, "play_card_1")  # in-turn red 0 -> B
    assert game.current_player is b

    game.execute_action(a, "play_card_2")  # A straights red 9 (0 -> 9 wraps down)
    assert game.top_card.id == 2
    assert all(card.id != 2 for card in a.hand)
    assert game.current_player is b
    assert game.straight_dir == -1


def test_bot_game_completes_with_interceptions_and_straights():
    options = UnoOptions(
        winning_score=30,
        interceptions=True,
        super_interceptions=True,
        straights=True,
    )
    game = UnoGame(options=options)
    for i in range(4):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    game.flush_menus()
    for _ in range(120000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()
    assert game.status == "finished"


def test_bot_game_completes_with_advanced_responses():
    # Skip/reverse draw responses must keep terminating (each response consumes a
    # card, so the exchange is finite) and never deadlock.
    options = UnoOptions(
        winning_score=30,
        responses=True,
        advanced_responses=True,
    )
    game = UnoGame(options=options)
    for i in range(3):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    game.flush_menus()
    for _ in range(120000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()
    assert game.status == "finished"


def test_bot_game_completes_with_all_advanced_rules():
    # Interceptions, straights, and zero/seven together exercise every bot-driven
    # seven-swap path (in-turn, straight, interception); must not deadlock.
    options = UnoOptions(
        winning_score=30,
        interceptions=True,
        super_interceptions=True,
        straights=True,
        zero_seven_rule=True,
    )
    game = UnoGame(options=options)
    for i in range(4):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    game.flush_menus()
    for _ in range(120000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()
    assert game.status == "finished"


def test_bot_game_completes_with_straights_and_zero_seven():
    # Exercises the out-of-turn straight-seven swap path driven by bots; must not
    # deadlock waiting for a swap chooser who never acts.
    options = UnoOptions(
        winning_score=30,
        straights=True,
        zero_seven_rule=True,
    )
    game = UnoGame(options=options)
    for i in range(4):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    game.flush_menus()
    for _ in range(120000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()
    assert game.status == "finished"
