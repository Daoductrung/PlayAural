import random

from server.users.bot import Bot
from server.users.test_user import MockUser
from server.game_utils.cards import Card, Deck
from server.games.blackjack.game import BlackjackGame, BlackjackOptions

BUST_SOUND_SET = {
    "game_blackjack/bust1.ogg",
    "game_blackjack/bust2.ogg",
    "game_blackjack/bust3.ogg",
}
DEAL_SOUND_SET = {
    "game_cards/draw1.ogg",
    "game_cards/draw2.ogg",
    "game_cards/draw4.ogg",
}
DISCARD_SOUND_SET = {
    "game_cards/discard1.ogg",
    "game_cards/discard2.ogg",
    "game_cards/discard3.ogg",
}
SHUFFLE_SOUND_SET = {
    "game_cards/shuffle1.ogg",
    "game_cards/shuffle2.ogg",
    "game_cards/shuffle3.ogg",
    "game_cards/small_shuffle.ogg",
}
PUSH_SOUND = "game_cards/play2.ogg"
NO_WINNER_SOUND = "game_blackjack/bust3.ogg"


def make_card(card_id: int, rank: int, suit: int) -> Card:
    return Card(id=card_id, rank=rank, suit=suit)


def create_game_with_host() -> tuple[BlackjackGame, object, MockUser]:
    game = BlackjackGame()
    host_user = MockUser("Host")
    host_player = game.add_player("Host", host_user)
    game.host = "Host"
    return game, host_player, host_user


def test_blackjack_game_creation() -> None:
    game = BlackjackGame()
    assert game.get_name() == "Blackjack"
    assert game.get_name_key() == "game-name-blackjack"
    assert game.get_type() == "blackjack"
    assert game.get_category() == "category-card-games"
    assert game.get_min_players() == 1
    assert game.get_max_players() == 7


def test_blackjack_options_defaults() -> None:
    game = BlackjackGame()
    assert game.options.rules_profile == "vegas"
    assert game.options.starting_chips == 500
    assert game.options.base_bet == 10
    assert game.options.table_min_bet == 5
    assert game.options.table_max_bet == 100
    assert game.options.deck_count == 4
    assert game.options.dealer_hits_soft_17 is True
    assert game.options.dealer_peeks_blackjack is True
    assert game.options.players_cards_face_up is True
    assert game.options.allow_insurance is True
    assert game.options.allow_late_surrender is True
    assert game.options.blackjack_payout == "3_to_2"
    assert game.options.double_down_rule == "any_two"
    assert game.options.allow_double_after_split is True
    assert game.options.split_rule == "same_rank"
    assert game.options.max_split_hands == 2
    assert game.options.split_aces_one_card_only is True
    assert game.options.split_aces_count_as_blackjack is False
    assert game.options.turn_timer == "0"


def test_blackjack_prestart_validation_rejects_large_bet() -> None:
    game = BlackjackGame(options=BlackjackOptions(starting_chips=50, base_bet=100))
    host_user = MockUser("Host")
    game.add_player("Host", host_user)
    errors = game.prestart_validate()
    assert "blackjack-error-bet-too-high" in errors


def test_blackjack_prestart_validation_rejects_invalid_table_limits() -> None:
    game = BlackjackGame(
        options=BlackjackOptions(
            starting_chips=500,
            base_bet=10,
            table_min_bet=25,
            table_max_bet=20,
        )
    )
    host_user = MockUser("Host")
    game.add_player("Host", host_user)
    errors = game.prestart_validate()
    assert "blackjack-error-table-limits-invalid" in errors
    assert "blackjack-error-bet-below-min" in errors


def test_blackjack_hand_value_handles_soft_aces() -> None:
    game = BlackjackGame()
    hand = [make_card(1, 1, 1), make_card(2, 6, 2)]
    total, soft = game.hand_value(hand)
    assert total == 17
    assert soft is True

    hand.append(make_card(3, 10, 3))
    total, soft = game.hand_value(hand)
    assert total == 17
    assert soft is False


def test_blackjack_on_start_waits_for_bets_then_deals_and_posts_bets() -> None:
    game, host_player, host_user = create_game_with_host()
    game.options = BlackjackOptions(starting_chips=100, base_bet=10, deck_count=1)
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)

    game.on_start()

    assert game.status == "playing"
    assert game.phase == "settle"
    assert game.hand_number == 0
    assert game._is_between_hands() is True
    assert host_player.bet == 0
    assert guest_player.bet == 0
    assert len(host_player.hand) == 0
    assert len(guest_player.hand) == 0
    assert len(game.dealer_hand) == 0

    game._action_set_next_bet(host_player, "10", "set_next_bet")
    assert game.phase == "settle"
    assert game.hand_number == 0

    game._action_set_next_bet(guest_player, "10", "set_next_bet")

    assert game.status == "playing"
    assert len(host_player.hand) == 2
    assert len(guest_player.hand) == 2
    assert len(game.dealer_hand) == 2
    assert game.hand_number == 1
    assert host_player.bet == 10
    assert guest_player.bet == 10
    assert host_player.chips == 90
    assert guest_player.chips == 90
    sounds = host_user.get_sounds_played()
    assert "game_3cardpoker/roundstart.ogg" in sounds
    assert "game_3cardpoker/bet.ogg" in sounds
    assert any(sound in SHUFFLE_SOUND_SET for sound in sounds)
    assert any(sound in DEAL_SOUND_SET for sound in sounds)
    spoken_messages = host_user.get_spoken_messages()
    hand_msg_index = next(i for i, msg in enumerate(spoken_messages) if "Hand 1. Place your bets." in msg)
    bet_msg_index = next(i for i, msg in enumerate(spoken_messages) if "You bet 10." in msg)
    assert hand_msg_index < bet_msg_index


def test_blackjack_on_start_single_player_does_not_end_immediately() -> None:
    game, host_player, _host_user = create_game_with_host()
    game.options = BlackjackOptions(starting_chips=100, base_bet=10, deck_count=1)

    game.on_start()

    assert game.status == "playing"
    assert game.phase == "settle"
    assert game._is_between_hands() is True
    assert game.hand_number == 0
    assert host_player.bet == 0
    assert len(host_player.hand) == 0
    assert len(game.dealer_hand) == 0


def test_blackjack_settle_single_player_continues_when_player_has_chips() -> None:
    game, host_player, _host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    host_player.chips = 90
    host_player.bet = 10
    host_player.hand = [make_card(1, 10, 1), make_card(2, 9, 2)]
    host_player.hand_done = True
    game.dealer_hand = [make_card(3, 10, 3), make_card(4, 7, 4)]  # dealer 17, player 19 wins

    game._settle_hand()

    assert game.status == "playing"
    assert game._is_between_hands() is True
    assert game.next_hand_wait_ticks == 0
    assert host_player.next_bet_entered is False
    assert host_player.chips == 110


def test_blackjack_hit_bust_advances_turn() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)

    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)
    game.deck = Deck(cards=[make_card(9, 10, 1)])
    game.dealer_hand = [make_card(10, 9, 2), make_card(11, 7, 3)]

    host_player.hand = [make_card(1, 10, 1), make_card(2, 9, 1)]
    host_player.bet = 10
    guest_player.hand = [make_card(3, 5, 1), make_card(4, 6, 1)]
    guest_player.bet = 10

    game._action_hit(host_player, "hit")

    assert host_player.busted is True
    assert host_player.hand_done is True
    assert game.current_player == guest_player
    sounds = host_user.get_sounds_played()
    assert "game_blackjack/hit.ogg" in sounds
    assert any(sound in BUST_SOUND_SET for sound in sounds)


def test_blackjack_split_creates_two_hands() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)
    game.deck = Deck(cards=[make_card(900, 3, 1), make_card(901, 4, 2)])

    host_player.hand = [make_card(1, 8, 1), make_card(2, 8, 2)]
    host_player.bet = 10
    host_player.chips = 90

    game._action_split(host_player, "split")

    assert host_player.split_bet == 10
    assert host_player.chips == 80
    assert len(host_player.hand) == 2
    assert len(host_player.split_hand) == 2
    assert host_player.active_hand_index == 0
    assert game.current_player == host_player


def test_blackjack_double_down_increases_bet_and_ends_hand() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)
    game.deck = Deck(cards=[make_card(910, 10, 1)])

    host_player.hand = [make_card(1, 5, 1), make_card(2, 6, 2)]
    host_player.bet = 10
    host_player.chips = 90

    game._action_double_down(host_player, "double_down")

    assert host_player.bet == 20
    assert host_player.chips == 80
    assert len(host_player.hand) == 3
    assert host_player.hand_done is True
    assert game.current_player == guest_player
    sounds = host_user.get_sounds_played()
    assert "game_blackjack/doubledown.ogg" in sounds
    assert "game_blackjack/hit.ogg" in sounds
    assert "game_blackjack/stand.ogg" in sounds


def test_blackjack_late_surrender_refunds_half_and_advances() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)

    host_player.hand = [make_card(1, 10, 1), make_card(2, 6, 2)]
    host_player.bet = 10
    host_player.chips = 90

    game._action_surrender(host_player, "surrender")

    assert host_player.chips == 95
    assert host_player.surrendered_main is True
    assert host_player.hand_done is True
    assert game.current_player == guest_player
    assert any(sound in DISCARD_SOUND_SET for sound in host_user.get_sounds_played())


def test_blackjack_initial_blackjack_plays_blackjack_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.deck = Deck(
        cards=[
            make_card(1, 1, 1),   # host
            make_card(2, 9, 2),   # dealer up
            make_card(3, 13, 1),  # host
            make_card(4, 7, 2),   # dealer hole
        ]
    )

    game._deal_initial_cards([host_player])

    assert host_player.has_blackjack is True
    assert "game_blackjack/blackjack.ogg" in host_user.get_sounds_played()


def test_blackjack_dealer_bust_plays_bust_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.dealer_hand = [make_card(1, 10, 1), make_card(2, 6, 2)]
    game.deck = Deck(cards=[make_card(3, 10, 3)])
    game._settle_hand = lambda: None  # type: ignore[method-assign]

    game._play_dealer_turn()

    sounds = host_user.get_sounds_played()
    assert "game_blackjack/hit.ogg" in sounds
    assert any(sound in BUST_SOUND_SET for sound in sounds)


def test_blackjack_settle_win_plays_win_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"

    host_player.chips = 90
    host_player.bet = 10
    host_player.hand = [make_card(1, 10, 1), make_card(2, 9, 2)]  # 19
    host_player.hand_done = True
    game.dealer_hand = [make_card(3, 10, 3), make_card(4, 7, 4)]  # 17

    game._settle_hand()

    assert "game_3cardpoker/winbet.ogg" in host_user.get_sounds_played()


def test_blackjack_settle_blackjack_win_plays_premium_win_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"

    host_player.chips = 90
    host_player.bet = 10
    host_player.hand = [make_card(1, 1, 1), make_card(2, 13, 2)]  # blackjack
    host_player.has_blackjack = True
    host_player.hand_done = True
    game.dealer_hand = [make_card(3, 10, 3), make_card(4, 7, 4)]  # 17

    game._settle_hand()

    assert "game_3cardpoker/win.ogg" in host_user.get_sounds_played()


def test_blackjack_end_game_winner_plays_wingame_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game._end_game(host_player)
    assert "game_3cardpoker/wingame.ogg" in host_user.get_sounds_played()


def test_blackjack_end_game_no_winner_plays_no_winner_sound() -> None:
    game, _host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game._end_game(None)
    assert NO_WINNER_SOUND in host_user.get_sounds_played()


def test_blackjack_set_next_bet_between_rounds_updates_future_posted_bet() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    game.options.table_min_bet = 5
    game.options.table_max_bet = 100

    host_player.chips = 90
    guest_player.chips = 90

    game._action_set_next_bet(host_player, "25", "set_next_bet")

    assert host_player.next_bet == 25
    assert host_player.next_bet_entered is True
    assert guest_player.next_bet_entered is False
    assert "Bet set to 25" in (host_user.get_last_spoken() or "")
    assert "game_3cardpoker/bet.ogg" in host_user.get_sounds_played()


def test_blackjack_set_next_bet_ignored_during_player_phase() -> None:
    game, host_player, _host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player], reset_index=True)

    host_player.next_bet = 10
    game._action_set_next_bet(host_player, "40", "set_next_bet")

    assert host_player.next_bet == 10


def test_blackjack_b_keybind_reads_current_bets_during_round() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.setup_keybinds()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"

    host_player.chips = 100
    host_player.bet = 10
    guest_player.chips = 80
    guest_player.bet = 20

        # Inject dummy context
    from server.games.base import ActionContext
    context = ActionContext(from_keybind=True)

    game._action_read_bets(host_player, "read_bets")

    spoken = host_user.get_last_spoken() or ""
    assert "Host" in spoken
    assert "100" in spoken
    assert "10" in spoken


def test_blackjack_b_keybind_between_hands_opens_change_bet_input() -> None:
    game, host_player, host_user = create_game_with_host()
    game.setup_keybinds()
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True

        # Normally keybind event calls change_bet
    game.execute_action(host_player, "change_bet")

    assert host_player.id in getattr(game, "_pending_actions", {})
    assert "action_input_editbox" in host_user.editboxes
    assert host_user.editboxes["action_input_editbox"]["prompt"] == "Change your bet"


def test_blackjack_actions_menu_hides_bet_previous_action() -> None:
    game, host_player, _host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    host_player.chips = 100

    standard = game.create_standard_action_set(host_player)
    enabled_ids = [ra.action.id for ra in standard.get_enabled_actions(game, host_player)]

    assert "change_bet" in enabled_ids
    assert "bet_previous" not in enabled_ids


def test_blackjack_web_standard_actions_keep_scores_above_turn_info() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    host_user.client_type = "web"

    standard = game.create_standard_action_set(host_player)
    order = standard._order

    check_scores_idx = order.index("check_scores")
    whose_turn_idx = order.index("whose_turn")
    whos_at_table_idx = order.index("whos_at_table")

    assert check_scores_idx < whose_turn_idx
    assert whose_turn_idx < whos_at_table_idx
    assert whose_turn_idx == len(order) - 2
    assert whos_at_table_idx == len(order) - 1


def test_blackjack_starts_next_hand_when_all_players_enter_bets() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    game.options.table_min_bet = 5
    game.options.table_max_bet = 100
    host_player.chips = 90
    guest_player.chips = 90

    started = {"value": False}

    def _mark_started() -> None:
        started["value"] = True

    game._start_new_hand = _mark_started  # type: ignore[method-assign]

    game._action_set_next_bet(host_player, "25", "set_next_bet")
    assert started["value"] is False

    game._action_set_next_bet(guest_player, "30", "set_next_bet")
    assert started["value"] is True


def test_blackjack_whose_turn_between_hands_reports_waiting_bettors() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    host_player.chips = 100
    guest_player.chips = 100
    host_player.next_bet_entered = True
    guest_player.next_bet_entered = False

    game._action_whose_turn(host_player, "whose_turn")

    spoken = host_user.get_last_spoken() or ""
    assert "Waiting for bets" in spoken


def test_blackjack_whose_turn_between_hands_uses_localized_waiting_message() -> None:
    game = BlackjackGame()
    host_user = MockUser("Host", locale="sr")
    host_player = game.add_player("Host", host_user)
    game.host = "Host"
    guest_user = MockUser("Guest", locale="sr")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    host_player.chips = 100
    guest_player.chips = 100
    host_player.next_bet_entered = True
    guest_player.next_bet_entered = False

    game._action_whose_turn(host_player, "whose_turn")

    spoken = host_user.get_last_spoken() or ""
    # Falls back to English when locale has no blackjack FTL
    assert "Waiting for bets" in spoken


def test_blackjack_whose_turn_between_hands_all_bets_in_uses_default_whose_turn() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.awaiting_next_bets = True
    host_player.chips = 100
    guest_player.chips = 100
    host_player.next_bet_entered = True
    guest_player.next_bet_entered = True

    game._action_whose_turn(host_player, "whose_turn")

    spoken = host_user.get_last_spoken() or ""
    assert spoken == "No one's turn right now."


def test_blackjack_between_hands_timer_timeout_uses_base_bet_for_missing_entries() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "settle"
    game.options.base_bet = 15
    game.options.table_min_bet = 5
    game.options.table_max_bet = 100
    game.options.turn_timer = "1"
    host_player.chips = 90
    guest_player.chips = 90

    started = {"value": False}

    def _mark_started() -> None:
        started["value"] = True

    game._start_new_hand = _mark_started  # type: ignore[method-assign]
    game._start_between_hands()
    game._action_set_next_bet(host_player, "40", "set_next_bet")

    for _ in range(20):
        game.on_tick()

    assert started["value"] is True
    assert host_player.next_bet == 40
    assert host_player.next_bet_entered is True
    assert guest_player.next_bet == 15
    assert guest_player.next_bet_entered is True


def test_blackjack_insurance_wins_when_dealer_has_blackjack() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.set_turn_players([host_player], reset_index=True)
    game._advance_insurance_to_next_player = lambda: None  # type: ignore[method-assign]

    host_player.hand = [make_card(1, 10, 1), make_card(2, 9, 2)]
    host_player.bet = 10
    host_player.chips = 90
    host_player.insurance_decision_done = False
    game.dealer_hand = [make_card(10, 1, 3), make_card(11, 13, 4)]

    game._action_take_insurance(host_player, "take_insurance")

    assert host_player.insurance_bet == 5
    assert host_player.chips == 85
    assert host_player.insurance_decision_done is True

    host_player.hand_done = True
    game._settle_hand()
    assert host_player.chips == 100
    assert "game_3cardpoker/winbet.ogg" in host_user.get_sounds_played()


def test_blackjack_insurance_loses_plays_discard_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.set_turn_players([host_player], reset_index=True)
    game._advance_insurance_to_next_player = lambda: None  # type: ignore[method-assign]

    host_player.hand = [make_card(1, 10, 1), make_card(2, 7, 2)]
    host_player.bet = 10
    host_player.chips = 90
    host_player.insurance_decision_done = False
    game.dealer_hand = [make_card(10, 1, 3), make_card(11, 9, 4)]

    game._action_take_insurance(host_player, "take_insurance")
    host_player.hand_done = True
    game._settle_hand()

    assert any(sound in DISCARD_SOUND_SET for sound in host_user.get_sounds_played())


def test_blackjack_even_money_pays_one_to_one() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.set_turn_players([host_player], reset_index=True)
    game._advance_insurance_to_next_player = lambda: None  # type: ignore[method-assign]

    host_player.hand = [make_card(1, 1, 1), make_card(2, 13, 2)]
    host_player.has_blackjack = True
    host_player.bet = 10
    host_player.chips = 90
    host_player.insurance_decision_done = False
    game.dealer_hand = [make_card(10, 1, 3), make_card(11, 13, 4)]

    game._action_even_money(host_player, "even_money")

    assert host_player.took_even_money is True
    assert host_player.insurance_decision_done is True
    assert "game_3cardpoker/bet.ogg" in host_user.get_sounds_played()

    host_player.hand_done = True
    game._settle_hand()
    assert host_player.chips == 110


def test_blackjack_decline_insurance_plays_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.set_turn_players([host_player], reset_index=True)
    game._advance_insurance_to_next_player = lambda: None  # type: ignore[method-assign]

    host_player.hand = [make_card(1, 10, 1), make_card(2, 7, 2)]
    host_player.bet = 10
    host_player.chips = 90
    host_player.insurance_decision_done = False
    game.dealer_hand = [make_card(10, 1, 3), make_card(11, 13, 4)]

    game._action_decline_insurance(host_player, "decline_insurance")

    assert host_player.insurance_decision_done is True
    assert "game_blackjack/stand.ogg" in host_user.get_sounds_played()


def test_blackjack_reveal_dealer_hand_plays_reveal_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.dealer_hand = [make_card(1, 10, 1), make_card(2, 7, 2)]

    game._reveal_dealer_hand()

    assert game.dealer_hole_revealed is True
    assert "game_cards/play1.ogg" in host_user.get_sounds_played()


def test_blackjack_push_result_plays_push_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"

    host_player.chips = 90
    host_player.bet = 10
    host_player.hand = [make_card(1, 10, 1), make_card(2, 7, 2)]  # 17
    host_player.hand_done = True
    game.dealer_hand = [make_card(3, 10, 3), make_card(4, 7, 4)]  # 17

    game._settle_hand()

    assert PUSH_SOUND in host_user.get_sounds_played()


def test_blackjack_player_broke_plays_bust_sound() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"

    host_player.chips = 0
    host_player.bet = 10
    host_player.hand = [make_card(1, 10, 1), make_card(2, 6, 2)]  # 16
    host_player.hand_done = True
    game.dealer_hand = [make_card(3, 10, 3), make_card(4, 8, 4)]  # 18

    game._settle_hand()

    assert any(sound in BUST_SOUND_SET for sound in host_user.get_sounds_played())


def test_blackjack_should_offer_insurance_when_dealer_shows_ace() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    host_player.bet = 10
    host_player.chips = 100
    guest_player.bet = 10
    guest_player.chips = 100
    game.dealer_hand = [make_card(10, 1, 3), make_card(11, 7, 4)]

    assert game._should_offer_insurance([host_player, guest_player]) is True

    game.options.allow_insurance = False
    assert game._should_offer_insurance([host_player, guest_player]) is False


def test_blackjack_split_limit_disables_split() -> None:
    game, host_player, _host_user = create_game_with_host()
    game.options.max_split_hands = 1
    host_player.hand = [make_card(1, 8, 1), make_card(2, 8, 2)]
    host_player.bet = 10
    host_player.chips = 100
    assert game._can_split(host_player) is False


def test_blackjack_split_aces_auto_stand_when_enabled() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)
    game.options.split_aces_one_card_only = True
    game.deck = Deck(cards=[make_card(900, 9, 1), make_card(901, 8, 2)])

    host_player.hand = [make_card(1, 1, 1), make_card(2, 1, 2)]
    host_player.bet = 10
    host_player.chips = 90

    game._action_split(host_player, "split")

    assert host_player.hand_done is True
    assert host_player.split_hand_done is True
    assert host_player.main_from_split_aces is True
    assert host_player.split_from_split_aces is True
    assert game.current_player == guest_player


def test_blackjack_split_aces_can_count_as_blackjack() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.set_turn_players([host_player, guest_player], reset_index=True)
    game.options.split_aces_one_card_only = True
    game.options.split_aces_count_as_blackjack = True
    game.deck = Deck(cards=[make_card(900, 10, 1), make_card(901, 10, 2)])

    host_player.hand = [make_card(1, 1, 1), make_card(2, 1, 2)]
    host_player.bet = 10
    host_player.chips = 90

    game._action_split(host_player, "split")

    assert host_player.has_blackjack is True
    assert host_player.split_has_blackjack is True


def test_blackjack_settle_split_hands_independently() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.dealer_hand = [make_card(100, 10, 1), make_card(101, 8, 2)]  # 18

    host_player.hand = [make_card(1, 10, 3), make_card(2, 10, 4)]  # 20, win
    host_player.bet = 10
    host_player.hand_done = True
    host_player.split_hand = [make_card(3, 10, 1), make_card(4, 9, 2), make_card(5, 5, 3)]  # bust
    host_player.split_bet = 10
    host_player.split_busted = True
    host_player.split_hand_done = True
    host_player.chips = 80

    guest_player.hand = [make_card(6, 7, 1), make_card(7, 7, 2)]
    guest_player.bet = 10
    guest_player.hand_done = True
    guest_player.chips = 90

    game._settle_hand()

    assert host_player.chips == 100


def test_blackjack_rules_profile_applies_preset() -> None:
    game = BlackjackGame()
    game._handle_option_change("rules_profile", "european")

    assert game.options.rules_profile == "european"
    assert game.options.dealer_hits_soft_17 is False
    assert game.options.dealer_peeks_blackjack is False
    assert game.options.allow_insurance is True
    assert game.options.allow_late_surrender is False
    assert game.options.blackjack_payout == "3_to_2"
    assert game.options.double_down_rule == "9_to_11"
    assert game.options.allow_double_after_split is False
    assert game.options.split_rule == "same_rank"
    assert game.options.max_split_hands == 2
    assert game.options.split_aces_one_card_only is True
    assert game.options.split_aces_count_as_blackjack is False


def test_blackjack_split_rule_controls_ten_value_splits() -> None:
    game, host_player, _host_user = create_game_with_host()
    host_player.hand = [make_card(1, 10, 1), make_card(2, 13, 2)]
    host_player.bet = 10
    host_player.chips = 100

    game.options.split_rule = "same_value"
    assert game._can_split(host_player) is True

    game.options.split_rule = "same_rank"
    assert game._can_split(host_player) is False


def test_blackjack_double_down_rules_and_das() -> None:
    game, host_player, _host_user = create_game_with_host()
    host_player.bet = 10
    host_player.chips = 100

    game.options.double_down_rule = "9_to_11"
    host_player.hand = [make_card(1, 4, 1), make_card(2, 4, 2)]  # total 8
    assert game._can_double_down(host_player) is False

    host_player.hand = [make_card(3, 5, 1), make_card(4, 5, 2)]  # total 10
    assert game._can_double_down(host_player) is True

    host_player.split_hand = [make_card(5, 5, 3), make_card(6, 5, 4)]
    host_player.split_bet = 10
    host_player.active_hand_index = 1
    game.options.allow_double_after_split = False
    assert game._can_double_down(host_player) is False

    game.options.allow_double_after_split = True
    assert game._can_double_down(host_player) is True


def test_blackjack_blackjack_payout_modes() -> None:
    game = BlackjackGame()

    game.options.blackjack_payout = "3_to_2"
    assert game._blackjack_total_payout(10) == 25

    game.options.blackjack_payout = "6_to_5"
    assert game._blackjack_total_payout(10) == 22

    game.options.blackjack_payout = "1_to_1"
    assert game._blackjack_total_payout(10) == 20


def test_blackjack_dealer_no_peek_does_not_auto_settle() -> None:
    game, host_player, _host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.options.dealer_peeks_blackjack = False
    game.options.allow_insurance = False

    events = {"settled": 0, "started_turn": 0}

    def fake_post_bets(players: list) -> None:
        for player in players:
            player.bet = 10

    def fake_deal_initial_cards(players: list) -> None:
        for player in players:
            player.hand = [make_card(1, 10, 1), make_card(2, 9, 2)]
            player.hand_done = False
        game.dealer_hand = [make_card(3, 1, 1), make_card(4, 13, 2)]

    game._ensure_deck = lambda min_cards=1: None  # type: ignore[method-assign]
    game._post_bets = fake_post_bets  # type: ignore[method-assign]
    game._deal_initial_cards = fake_deal_initial_cards  # type: ignore[method-assign]
    game._settle_hand = lambda: events.__setitem__("settled", events["settled"] + 1)  # type: ignore[method-assign]
    game._start_turn = lambda: events.__setitem__("started_turn", events["started_turn"] + 1)  # type: ignore[method-assign]

    game.on_start()
    game._action_set_next_bet(host_player, "10", "set_next_bet")
    game._action_set_next_bet(guest_player, "10", "set_next_bet")

    assert events["settled"] == 0
    assert events["started_turn"] == 1
    assert game.phase == "players"
    assert game.current_player == host_player


def test_blackjack_read_rules_action_speaks_summary() -> None:
    game, host_player, host_user = create_game_with_host()
    game._action_read_rules(host_player, "read_rules")
    spoken = host_user.get_last_spoken() or ""
    assert "Rules:" in spoken
    assert "Table limits" in spoken


def test_blackjack_pitch_style_hides_initial_cards_from_other_players() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.options.players_cards_face_up = False
    game.deck = Deck(
        cards=[
            make_card(1, 10, 1),  # host
            make_card(2, 9, 2),  # guest
            make_card(3, 6, 3),  # dealer up
            make_card(4, 7, 4),  # host
            make_card(5, 8, 1),  # guest
            make_card(6, 12, 2),  # dealer hole
        ]
    )

    game._deal_initial_cards([host_player, guest_player])

    host_spoken = " ".join(host_user.get_spoken_messages())
    guest_spoken = " ".join(guest_user.get_spoken_messages())
    assert "You have" in host_spoken
    assert "You have" in guest_spoken
    assert "Host has" not in guest_spoken
    assert "Guest has" not in host_spoken


def test_blackjack_pitch_style_hides_other_totals_in_table_status() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    game.options.players_cards_face_up = False

    host_player.chips = 100
    host_player.bet = 10
    host_player.hand = [make_card(11, 10, 1), make_card(12, 6, 2)]

    guest_player.chips = 100
    guest_player.bet = 10
    guest_player.hand = [make_card(13, 2, 1), make_card(14, 5, 2)]

    game._action_table_status(host_player, "table_status")

    spoken = host_user.get_last_spoken() or ""
    assert "Host: 100 chips, bet 10, total" in spoken
    assert "Guest: 100 chips, bet 10, total" not in spoken
    assert "Guest: 100 chips, bet 10" in spoken
    assert "Rules:" not in spoken


def test_blackjack_status_keybinds_do_not_rebuild_menus() -> None:
    game, host_player, host_user = create_game_with_host()
    game.setup_keybinds()
    game.status = "playing"
    game.game_active = True
    game.phase = "players"
    host_player.chips = 100
    host_player.bet = 10
    host_player.hand = [make_card(1, 10, 1), make_card(2, 7, 2)]
    game.dealer_hand = [make_card(3, 9, 3), make_card(4, 8, 4)]
    game.dealer_hole_revealed = True
    game.set_turn_players([host_player], reset_index=True)

    game.rebuild_all_menus()
    host_user.messages = []

    game.execute_action(host_player, "whose_turn")
    game.execute_action(host_player, "table_status")
    game.execute_action(host_player, "check_scores")
    game.execute_action(host_player, "read_bets")

    menu_events = [m for m in host_user.messages if m.type in {"show_menu", "update_menu"}]
    assert menu_events == []


def test_blackjack_dealer_reveal_supports_serbian_locale_bundle() -> None:
    game = BlackjackGame()
    host_user = MockUser("Host", locale="sr")
    game.add_player("Host", host_user)
    game.host = "Host"
    game.dealer_hand = [make_card(1, 10, 1), make_card(2, 1, 2)]

    game._reveal_dealer_hand()

    spoken = host_user.get_last_spoken() or ""
    assert spoken != "blackjack-dealer-reveals"


def test_blackjack_insurance_prompt_announced_to_player() -> None:
    game, host_player, host_user = create_game_with_host()
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.dealer_hand = [make_card(1, 1, 1), make_card(2, 9, 2)]
    host_player.bet = 10
    host_player.chips = 100
    host_player.hand = [make_card(3, 10, 1), make_card(4, 7, 2)]
    host_player.insurance_decision_done = False
    game.set_turn_players([host_player], reset_index=True)

    game._start_insurance_turn()

    spoken = " ".join(host_user.get_spoken_messages())
    assert "insurance" in spoken.lower()


def test_blackjack_dealer_hits_soft_17_when_enabled() -> None:
    game = BlackjackGame()
    game.options.dealer_hits_soft_17 = True
    game.status = "playing"
    game.dealer_hand = [make_card(1, 1, 1), make_card(2, 6, 2)]
    game.deck = Deck(cards=[make_card(3, 2, 3)])
    game._settle_hand = lambda: None  # type: ignore[method-assign]

    game._play_dealer_turn()

    assert len(game.dealer_hand) == 3


def test_blackjack_dealer_stands_soft_17_when_disabled() -> None:
    game = BlackjackGame()
    game.options.dealer_hits_soft_17 = False
    game.status = "playing"
    game.dealer_hand = [make_card(1, 1, 1), make_card(2, 6, 2)]
    game.deck = Deck(cards=[make_card(3, 2, 3)])
    game._settle_hand = lambda: None  # type: ignore[method-assign]

    game._play_dealer_turn()

    assert len(game.dealer_hand) == 2


def test_blackjack_bot_game_completes() -> None:
    random.seed(12345)
    game = BlackjackGame(
        options=BlackjackOptions(
            starting_chips=40,
            base_bet=10,
            deck_count=1,
            turn_timer="0",
        )
    )
    for index in range(3):
        bot = Bot(f"Bot{index}")
        game.add_player(f"Bot{index}", bot)

    game.on_start()

    for _ in range(120000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"


def test_blackjack_bot_game_completes_with_save_reload_cycles() -> None:
    random.seed(67890)
    game = BlackjackGame(
        options=BlackjackOptions(
            starting_chips=60,
            base_bet=10,
            table_min_bet=5,
            table_max_bet=20,
            deck_count=1,
            turn_timer="0",
        )
    )
    bots = [Bot(f"Bot{index}") for index in range(3)]
    for bot in bots:
        game.add_player(bot.username, bot)

    game.on_start()

    for tick in range(140000):
        if game.status == "finished":
            break

        if tick > 0 and tick % 75 == 0:
            saved_users = dict(game._users)
            saved_keybinds = dict(game._keybinds)
            payload = game.to_json()
            game = BlackjackGame.from_json(payload)
            game._users = saved_users
            game._keybinds = saved_keybinds
            game.rebuild_runtime_state()
            for player in game.players:
                if game.get_user(player):
                    game.setup_player_actions(player)

        game.on_tick()

    assert game.status == "finished"


def test_blackjack_persistence_round_trip_preserves_new_state_and_reconnect() -> None:
    game, host_player, host_user = create_game_with_host()
    guest_user = MockUser("Guest")
    guest_player = game.add_player("Guest", guest_user)
    game.status = "playing"
    game.game_active = True
    game.phase = "insurance"
    game.options = BlackjackOptions(
        rules_profile="friendly",
        starting_chips=900,
        base_bet=25,
        table_min_bet=10,
        table_max_bet=200,
        deck_count=2,
        dealer_hits_soft_17=False,
        dealer_peeks_blackjack=False,
        allow_insurance=True,
        allow_late_surrender=True,
        players_cards_face_up=False,
        blackjack_payout="6_to_5",
        double_down_rule="10_to_11",
        allow_double_after_split=False,
        split_rule="same_value",
        max_split_hands=2,
        split_aces_one_card_only=True,
        split_aces_count_as_blackjack=True,
        turn_timer="30",
    )
    game.dealer_hand = [make_card(20, 1, 1), make_card(21, 13, 2)]
    game.set_turn_players([host_player, guest_player], reset_index=True)

    host_player.hand = [make_card(1, 1, 1), make_card(2, 13, 2)]
    host_player.has_blackjack = True
    host_player.bet = 25
    host_player.chips = 875
    host_player.insurance_bet = 12
    host_player.insurance_decision_done = True
    host_player.took_even_money = True
    host_player.split_hand = [make_card(3, 1, 3), make_card(4, 10, 4)]
    host_player.split_bet = 25
    host_player.split_has_blackjack = True
    host_player.main_from_split_aces = True
    host_player.split_from_split_aces = True
    host_player.surrendered_main = False
    host_player.surrendered_split = False
    host_player.next_bet = 40

    payload = game.to_json()
    loaded = BlackjackGame.from_json(payload)
    loaded.rebuild_runtime_state()

    loaded_host = next(p for p in loaded.players if p.name == "Host")
    loaded_guest = next(p for p in loaded.players if p.name == "Guest")
    loaded.attach_user(loaded_host.id, host_user)
    loaded.attach_user(loaded_guest.id, guest_user)
    loaded.setup_player_actions(loaded_host)
    loaded.setup_player_actions(loaded_guest)

    assert loaded.options.table_min_bet == 10
    assert loaded.options.table_max_bet == 200
    assert loaded.options.allow_late_surrender is True
    assert loaded.options.players_cards_face_up is False
    assert loaded.options.blackjack_payout == "6_to_5"
    assert loaded.options.split_aces_count_as_blackjack is True
    assert loaded.options.double_down_rule == "10_to_11"

    assert loaded_host.insurance_bet == 12
    assert loaded_host.took_even_money is True
    assert loaded_host.main_from_split_aces is True
    assert loaded_host.split_from_split_aces is True
    assert loaded_host.split_has_blackjack is True
    assert loaded_host.next_bet == 40
    assert loaded.current_player == loaded_host

    loaded._action_read_rules(loaded_host, "read_rules")
    spoken = host_user.get_last_spoken() or ""
    assert "Rules:" in spoken
