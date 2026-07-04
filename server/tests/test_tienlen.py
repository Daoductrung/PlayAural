from pathlib import Path
import json
import random

from ..games.registry import GameRegistry
from ..games.tienlen.evaluator import (
    NORTHERN_VARIANT,
    SOUTHERN_VARIANT,
    evaluate_combo,
)
from ..games.tienlen.game import TienLenGame, TienLenOptions
from ..games.tienlen.rules import get_rules
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def c(card_id: int, rank: int, suit: int):
    from ..game_utils.cards import Card

    return Card(card_id, rank, suit)


def make_game(
    *,
    player_count: int = 2,
    start: bool = False,
    bot_all: bool = False,
    web_first: bool = False,
    **option_overrides,
) -> TienLenGame:
    game = TienLenGame(options=TienLenOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if web_first and index == 0:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
        for _ in range(5):
            if game.hand_wait_ticks == 0 or game.status != "playing":
                break
            game.hand_wait_ticks = 1
            game.on_tick()
    return game


def prepare_active_game(game: TienLenGame) -> TienLenGame:
    game.status = "playing"
    game.game_active = True
    game.set_turn_players(game.players)
    starting_coins = game._starting_coins()
    for index, active_player in enumerate(game.players):
        active_player.hand = [c(900 + index, 5 + index, 4)]
        active_player.coins = starting_coins
        active_player.eliminated = False
    game._team_manager.team_mode = "individual"
    game._team_manager.setup_teams([player.name for player in game.get_active_players()])
    game._sync_team_scores()
    return game


def advance_until(game: TienLenGame, condition, max_ticks: int = 600) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def test_game_registered_and_defaults() -> None:
    assert GameRegistry.get("tienlen") is TienLenGame
    game = TienLenGame()
    assert game.get_name() == "Tien Len"
    assert game.get_type() == "tienlen"
    assert game.options.variant == SOUTHERN_VARIANT
    assert game.options.match_length == "50"


def test_tienlen_match_length_sets_starting_coins_without_score_target() -> None:
    assert TienLenGame(options=TienLenOptions(match_length="20"))._starting_coins() == 20
    assert TienLenGame(options=TienLenOptions(match_length="50"))._starting_coins() == 50
    assert TienLenGame(options=TienLenOptions(match_length="100"))._starting_coins() == 100
    assert TienLenGame(options=TienLenOptions(match_length="200"))._starting_coins() == 200
    assert TienLenGame(options=TienLenOptions(match_length="1"))._starting_coins() == 50
    assert TienLenGame(options=TienLenOptions(match_length="50")).get_score_target() is None


def test_tienlen_uses_ninetynine_background_music_on_start() -> None:
    game = make_game()
    first_user = game.get_user(game.players[0])
    assert isinstance(first_user, MockUser)

    game.on_start()

    assert any(
        message.type == "play_music"
        and message.data["name"] == "game_ninetynine/mus.ogg"
        for message in first_user.messages
    )


def test_tienlen_starts_first_hand_without_intro_delay_or_intro_sound() -> None:
    game = make_game()
    first_user = game.get_user(game.players[0])
    assert isinstance(first_user, MockUser)

    game.on_start()

    assert game.round == 1
    assert game.intro_wait_ticks == 0
    assert not any(
        message.type == "play_sound"
        and message.data["name"] == "game_crazyeights/intro.ogg"
        for message in first_user.messages
    )
    assert all(player.coins == 50 for player in game.players)


def test_southern_combo_evaluation_supports_straights_and_consecutive_pairs() -> None:
    straight = evaluate_combo([c(1, 3, 4), c(2, 4, 2), c(3, 5, 1)], SOUTHERN_VARIANT)
    doi_thong = evaluate_combo(
        [c(4, 5, 4), c(5, 5, 2), c(6, 6, 4), c(7, 6, 2), c(8, 7, 4), c(9, 7, 2)],
        SOUTHERN_VARIANT,
    )
    assert straight is not None and straight.type_name == "straight"
    assert doi_thong is not None and doi_thong.type_name == "consecutive_pairs"
    assert doi_thong.pair_count == 3


def test_northern_combo_evaluation_requires_dong_mau_and_dong_chat() -> None:
    invalid_pair = evaluate_combo([c(1, 7, 4), c(2, 7, 1)], NORTHERN_VARIANT)
    valid_pair = evaluate_combo([c(3, 7, 4), c(4, 7, 2)], NORTHERN_VARIANT)
    invalid_straight = evaluate_combo([c(5, 9, 4), c(6, 10, 2), c(7, 11, 4)], NORTHERN_VARIANT)
    valid_straight = evaluate_combo([c(8, 9, 3), c(9, 10, 3), c(10, 11, 3)], NORTHERN_VARIANT)
    high_end_straight = evaluate_combo([c(11, 12, 3), c(12, 13, 3), c(13, 1, 3), c(14, 2, 3)], NORTHERN_VARIANT)

    assert invalid_pair is None
    assert valid_pair is not None and valid_pair.type_name == "pair"
    assert invalid_straight is None
    assert valid_straight is not None and valid_straight.type_name == "straight"
    assert high_end_straight is None


def test_southern_chop_matrix() -> None:
    rules = get_rules(SOUTHERN_VARIANT)
    single_two = evaluate_combo([c(1, 2, 4)], SOUTHERN_VARIANT)
    pair_twos = evaluate_combo([c(2, 2, 4), c(3, 2, 2)], SOUTHERN_VARIANT)
    tu_quy = evaluate_combo([c(4, 9, 4), c(5, 9, 2), c(6, 9, 1), c(7, 9, 3)], SOUTHERN_VARIANT)
    ba_doi_thong = evaluate_combo(
        [c(8, 5, 4), c(9, 5, 2), c(10, 6, 4), c(11, 6, 2), c(12, 7, 4), c(13, 7, 2)],
        SOUTHERN_VARIANT,
    )
    bon_doi_thong = evaluate_combo(
        [c(14, 5, 4), c(15, 5, 2), c(16, 6, 4), c(17, 6, 2), c(18, 7, 4), c(19, 7, 2), c(20, 8, 4), c(21, 8, 2)],
        SOUTHERN_VARIANT,
    )

    assert single_two and pair_twos and tu_quy and ba_doi_thong and bon_doi_thong
    assert rules.combo_beats(tu_quy, single_two) is True
    assert rules.combo_beats(ba_doi_thong, single_two) is True
    assert rules.combo_beats(tu_quy, pair_twos) is True
    assert rules.combo_beats(bon_doi_thong, pair_twos) is True
    assert rules.combo_beats(bon_doi_thong, tu_quy) is True


def test_southern_higher_hang_counts_as_chop() -> None:
    rules = get_rules(SOUTHERN_VARIANT)
    lower_ba_doi_thong = evaluate_combo(
        [c(1, 4, 4), c(2, 4, 2), c(3, 5, 4), c(4, 5, 2), c(5, 6, 4), c(6, 6, 2)],
        SOUTHERN_VARIANT,
    )
    higher_ba_doi_thong = evaluate_combo(
        [c(7, 7, 4), c(8, 7, 2), c(9, 8, 4), c(10, 8, 2), c(11, 9, 4), c(12, 9, 2)],
        SOUTHERN_VARIANT,
    )
    lower_tu_quy = evaluate_combo([c(13, 5, 4), c(14, 5, 2), c(15, 5, 1), c(16, 5, 3)], SOUTHERN_VARIANT)
    higher_tu_quy = evaluate_combo([c(17, 9, 4), c(18, 9, 2), c(19, 9, 1), c(20, 9, 3)], SOUTHERN_VARIANT)

    assert lower_ba_doi_thong and higher_ba_doi_thong and lower_tu_quy and higher_tu_quy
    assert rules.is_chop(higher_ba_doi_thong, lower_ba_doi_thong) is True
    assert rules.can_bypass_pass_lock(lower_ba_doi_thong, higher_ba_doi_thong) is True
    assert rules.is_chop(higher_tu_quy, lower_tu_quy) is True


def test_northern_single_requires_matching_structure_and_pair_of_twos_is_special() -> None:
    rules = get_rules(NORTHERN_VARIANT)
    heart_five = evaluate_combo([c(1, 5, 3)], NORTHERN_VARIANT)
    heart_eight = evaluate_combo([c(2, 8, 3)], NORTHERN_VARIANT)
    spade_eight = evaluate_combo([c(3, 8, 4)], NORTHERN_VARIANT)
    normal_pair = evaluate_combo([c(4, 10, 4), c(5, 10, 2)], NORTHERN_VARIANT)
    pair_twos = evaluate_combo([c(6, 2, 3), c(7, 2, 4)], NORTHERN_VARIANT)
    lower_pair_twos = evaluate_combo([c(8, 2, 4), c(9, 2, 2)], NORTHERN_VARIANT)

    assert heart_five and heart_eight and spade_eight and normal_pair and pair_twos and lower_pair_twos
    assert rules.combo_beats(heart_eight, heart_five) is True
    assert rules.combo_beats(spade_eight, heart_five) is False
    assert rules.combo_beats(pair_twos, normal_pair) is True
    assert rules.combo_beats(pair_twos, lower_pair_twos) is True


def test_northern_higher_tu_quy_counts_as_chop_without_pass_bypass() -> None:
    rules = get_rules(NORTHERN_VARIANT)
    lower_tu_quy = evaluate_combo([c(1, 5, 4), c(2, 5, 2), c(3, 5, 1), c(4, 5, 3)], NORTHERN_VARIANT)
    higher_tu_quy = evaluate_combo([c(5, 9, 4), c(6, 9, 2), c(7, 9, 1), c(8, 9, 3)], NORTHERN_VARIANT)

    assert lower_tu_quy and higher_tu_quy
    assert rules.is_chop(higher_tu_quy, lower_tu_quy) is True
    assert rules.can_bypass_pass_lock(lower_tu_quy, higher_tu_quy) is False


def test_northern_cannot_finish_on_two() -> None:
    rules = get_rules(NORTHERN_VARIANT)
    hand = [c(1, 2, 3)]
    selected = hand[:]
    is_valid, error_key, _ = rules.validate_play(hand, selected, None, False, False)
    assert is_valid is False
    assert error_key == "tienlen-error-cannot-finish-on-two"


def test_first_hand_opening_play_must_include_lowest_opening_card() -> None:
    game = make_game(start=True, variant=SOUTHERN_VARIANT)
    opener = game.current_player
    assert opener is not None
    other = next(player for player in game.players if player.id != opener.id)
    game.set_turn_players([opener, other])
    game.turn_index = 0
    game.hand_winner_id = None
    game.current_combo = None
    game.is_first_turn = True
    opener.hand = [c(1, 3, 4), c(2, 4, 4), c(3, 5, 4)]
    other.hand = [c(4, 7, 4)]
    opener.selected_cards = {2}

    game.execute_action(opener, "play_selected")

    user = game.get_user(opener)
    assert isinstance(user, MockUser)
    assert "opening play must include" in (user.get_last_spoken() or "")

    opener.selected_cards = {1, 2, 3}
    game.execute_action(opener, "play_selected")

    assert game.trick_winner_id == opener.id


def test_southern_three_consecutive_pairs_can_open_trick() -> None:
    rules = get_rules(SOUTHERN_VARIANT)
    hand = [
        c(1, 5, 4), c(2, 5, 2),
        c(3, 6, 4), c(4, 6, 2),
        c(5, 7, 4), c(6, 7, 2),
    ]

    is_valid, error_key, _ = rules.validate_play(hand, hand[:], None, False, False)

    assert is_valid is True
    assert error_key is None


def test_southern_passed_player_can_still_act_to_chop_two() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, _ = game.players
    game.current_combo = evaluate_combo([c(1, 2, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    player2.passed_this_trick = True
    player2.hand = [
        c(2, 5, 4), c(3, 5, 2),
        c(4, 6, 4), c(5, 6, 2),
        c(6, 7, 4), c(7, 7, 2),
    ]
    game.turn_index = game.turn_player_ids.index(player2.id)

    game._start_turn()

    assert game.current_player == player2
    player2.selected_cards = {card.id for card in player2.hand}
    game.execute_action(player2, "play_selected")
    assert game.trick_winner_id == player2.id


def test_northern_game_rejects_finishing_on_two() -> None:
    game = make_game(start=True, variant=NORTHERN_VARIANT)
    current = game.current_player
    assert current is not None
    game.is_first_turn = False
    current.hand = [c(1, 2, 3)]
    current.selected_cards = {1}

    game.execute_action(current, "play_selected")

    user = game.get_user(current)
    assert isinstance(user, MockUser)
    assert "cannot finish the hand with 2s" in (user.get_last_spoken() or "")


def test_northern_structure_mismatch_reports_specific_error() -> None:
    game = make_game(start=True, variant=NORTHERN_VARIANT)
    current = game.current_player
    assert current is not None
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(10, 5, 3)], NORTHERN_VARIANT)
    current.hand = [c(1, 8, 4)]
    current.selected_cards = {1}

    game.execute_action(current, "play_selected")

    user = game.get_user(current)
    assert isinstance(user, MockUser)
    assert user.get_last_spoken() == (
        "In Northern Tien Len, your play must match the suit or color structure of the current trick."
    )


def test_trick_resets_after_all_other_players_pass() -> None:
    game = make_game(player_count=2, start=True)
    leader = game.players[0]
    follower = game.players[1]
    game.set_turn_players([leader, follower])
    game.turn_index = 0
    game.is_first_turn = False
    leader.hand = [c(1, 5, 4), c(3, 9, 4)]
    follower.hand = [c(2, 3, 4)]
    leader.selected_cards = {1}
    game.execute_action(leader, "play_selected")
    follower_user = game.get_user(follower)
    assert isinstance(follower_user, MockUser)
    follower_user._preferences.confirm_destructive_actions = False

    game.execute_action(follower, "pass")

    assert game.current_player == leader
    assert game.current_combo is None


def test_passed_player_does_not_steal_lead_when_straight_goes_unbeaten() -> None:
    game = make_game(player_count=4, start=True, variant=SOUTHERN_VARIANT)
    player_a, player_b, player_c, player_d = game.players
    game.set_turn_players([player_b, player_a, player_d, player_c])
    game.turn_index = 0
    game.is_first_turn = False
    game.current_combo = None
    game.trick_winner_id = None
    game.trick_cards = []
    game.trick_play_id = 0
    game.trick_lead_fallback_id = None

    for player in (player_a, player_d, player_c):
        user = game.get_user(player)
        assert isinstance(user, MockUser)
        user._preferences.confirm_destructive_actions = False

    player_b.hand = [
        c(1, 3, 4),
        c(2, 4, 4),
        c(3, 5, 4),
        c(4, 6, 4),
        c(5, 7, 4),
        c(6, 8, 4),
        c(7, 9, 4),
    ]
    player_b.selected_cards = {1, 2, 3, 4, 5, 6}
    player_a.hand = [c(8, 10, 4)]
    player_d.hand = [c(9, 11, 4)]
    player_c.hand = [c(10, 12, 4)]
    player_c.passed_this_trick = True

    game.execute_action(player_b, "play_selected")
    assert game.current_player == player_a

    game.execute_action(player_a, "pass")
    assert game.current_player == player_d

    game.execute_action(player_d, "pass")

    assert game.current_player == player_b
    assert game.current_combo is None
    assert all(not player.passed_this_trick for player in (player_a, player_b, player_c, player_d))


def test_unpassed_player_must_act_before_straight_resolves() -> None:
    game = make_game(player_count=4, start=True, variant=SOUTHERN_VARIANT)
    player_a, player_b, player_c, player_d = game.players
    game.set_turn_players([player_b, player_a, player_d, player_c])
    game.turn_index = 0
    game.is_first_turn = False
    game.current_combo = None
    game.trick_winner_id = None
    game.trick_cards = []
    game.trick_play_id = 0
    game.trick_lead_fallback_id = None

    for player in (player_a, player_d):
        user = game.get_user(player)
        assert isinstance(user, MockUser)
        user._preferences.confirm_destructive_actions = False

    player_b.hand = [
        c(1, 3, 4),
        c(2, 4, 4),
        c(3, 5, 4),
        c(4, 6, 4),
        c(5, 7, 4),
        c(6, 8, 4),
        c(7, 9, 4),
    ]
    player_b.selected_cards = {1, 2, 3, 4, 5, 6}
    player_a.hand = [c(8, 10, 4)]
    player_d.hand = [c(9, 11, 4)]
    player_c.hand = [c(10, 12, 4)]

    game.execute_action(player_b, "play_selected")
    game.execute_action(player_a, "pass")
    game.execute_action(player_d, "pass")

    assert game.current_player == player_c
    assert game.current_combo is not None


def test_next_active_player_leads_when_unbeaten_player_finished() -> None:
    game = make_game(player_count=4, start=True, variant=SOUTHERN_VARIANT)
    player_a, player_b, player_c, player_d = game.players
    game.set_turn_players([player_b, player_a, player_d, player_c])
    game.turn_index = 0
    game.is_first_turn = False
    game.current_combo = None
    game.trick_winner_id = None
    game.trick_cards = []
    game.trick_play_id = 0
    game.trick_lead_fallback_id = None

    for player in (player_a, player_d, player_c):
        user = game.get_user(player)
        assert isinstance(user, MockUser)
        user._preferences.confirm_destructive_actions = False

    player_b.hand = [
        c(1, 3, 4),
        c(2, 4, 4),
        c(3, 5, 4),
        c(4, 6, 4),
        c(5, 7, 4),
        c(6, 8, 4),
    ]
    player_b.selected_cards = {1, 2, 3, 4, 5, 6}
    player_a.hand = [c(8, 10, 4)]
    player_d.hand = [c(9, 11, 4)]
    player_c.hand = [c(10, 12, 4)]
    player_c.passed_this_trick = True

    game.execute_action(player_b, "play_selected")
    assert game.finishing_order_ids == [player_b.id]
    assert game.current_player == player_a

    game.execute_action(player_a, "pass")
    game.execute_action(player_d, "pass")

    assert game.current_player == player_a
    assert game.current_combo is None


def test_passed_player_gets_current_chop_window_before_two_resolves() -> None:
    game = make_game(player_count=4, start=True, variant=SOUTHERN_VARIANT)
    player_a, player_b, player_c, player_d = game.players
    game.set_turn_players([player_b, player_a, player_d, player_c])
    game.turn_index = 0
    game.is_first_turn = False
    game.current_combo = None
    game.trick_winner_id = None
    game.trick_cards = []
    game.trick_play_id = 0
    game.trick_lead_fallback_id = None

    for player in (player_a, player_d, player_c):
        user = game.get_user(player)
        assert isinstance(user, MockUser)
        user._preferences.confirm_destructive_actions = False

    player_b.hand = [c(1, 2, 4), c(2, 9, 4)]
    player_b.selected_cards = {1}
    player_a.hand = [c(3, 10, 4)]
    player_d.hand = [c(4, 11, 4)]
    player_c.hand = [
        c(5, 6, 4),
        c(6, 6, 2),
        c(7, 6, 1),
        c(8, 6, 3),
    ]
    player_c.passed_this_trick = True

    game.execute_action(player_b, "play_selected")
    game.execute_action(player_a, "pass")
    game.execute_action(player_d, "pass")

    assert game.current_player == player_c
    assert game.current_combo is not None

    game.execute_action(player_c, "pass")

    assert game.current_player == player_b
    assert game.current_combo is None


def test_southern_pass_lock_reports_chop_specific_error() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, _ = game.players
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(50, 2, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    game.set_turn_players([player1, player2, game.players[2]])
    game.turn_index = game.turn_player_ids.index(player2.id)
    player2.passed_this_trick = True
    player2.hand = [c(1, 5, 4)]
    player2.selected_cards = {1}

    game._action_play_selected(player2, "play_selected")

    user = game.get_user(player2)
    assert isinstance(user, MockUser)
    assert user.get_last_spoken() == (
        "You already passed on this trick. You may only return with a legal chop against the current 2s or chopping combination."
    )


def test_pass_respects_confirm_risky_actions_preference() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, current, player3 = game.players
    game.set_turn_players([player1, current, player3])
    game.turn_index = 1
    player1.hand = [c(80, 5, 4)]
    current.hand = [c(81, 6, 4)]
    player3.hand = [c(82, 7, 4)]
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(99, 5, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(current, "pass")

    user = game.get_user(current)
    assert isinstance(user, MockUser)
    assert current.pass_confirm_ticks == 200
    assert current.passed_this_trick is False
    assert user.get_last_spoken() == (
        "Passing locks you out of the current trick. Press Pass again within 10 seconds to confirm."
    )

    game.execute_action(current, "pass")

    assert current.pass_confirm_ticks == 0
    assert current.passed_this_trick is True


def test_pass_confirmation_can_be_disabled() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, current, player3 = game.players
    game.set_turn_players([player1, current, player3])
    game.turn_index = 1
    player1.hand = [c(80, 5, 4)]
    current.hand = [c(81, 6, 4)]
    player3.hand = [c(82, 7, 4)]
    user = game.get_user(current)
    assert isinstance(user, MockUser)
    user._preferences.confirm_destructive_actions = False
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(99, 5, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(current, "pass")

    assert current.pass_confirm_ticks == 0
    assert current.passed_this_trick is True


def test_pass_confirmation_expires() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, current, player3 = game.players
    game.set_turn_players([player1, current, player3])
    game.turn_index = 1
    player1.hand = [c(80, 5, 4)]
    current.hand = [c(81, 6, 4)]
    player3.hand = [c(82, 7, 4)]
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(99, 5, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(current, "pass")
    current.pass_confirm_ticks = 1
    game.on_tick()

    assert current.pass_confirm_ticks == 0
    assert current.passed_this_trick is False


def test_hand_sorting_rebuilds_in_tien_len_order() -> None:
    game = make_game(start=True)
    current = game.current_player
    assert current is not None
    current.hand = [
        c(1, 2, 3),
        c(2, 3, 2),
        c(3, 1, 1),
        c(4, 3, 4),
        c(5, 2, 4),
        c(6, 3, 3),
    ]

    game.refresh_menus(current)
    game.flush_menus()

    assert [(card.rank, card.suit) for card in current.hand] == [
        (3, 4),
        (3, 2),
        (3, 3),
        (1, 1),
        (2, 4),
        (2, 3),
    ]
    turn_set = game.get_action_set(current, "turn")
    assert turn_set is not None
    ordered_toggle_ids = [action_id for action_id in turn_set._order if action_id.startswith("toggle_select_")]
    assert ordered_toggle_ids == [
        "toggle_select_4",
        "toggle_select_2",
        "toggle_select_6",
        "toggle_select_3",
        "toggle_select_5",
        "toggle_select_1",
    ]


def test_web_info_actions_visible() -> None:
    waiting_game = make_game(web_first=True)
    waiting_player = waiting_game.players[0]
    waiting_actions = {entry.action.id for entry in waiting_game.get_all_visible_actions(waiting_player)}
    assert "whos_at_table" in waiting_actions

    active_game = prepare_active_game(make_game(web_first=True))
    active_player = active_game.players[0]
    active_actions = {entry.action.id for entry in active_game.get_all_visible_actions(active_player)}
    assert "check_trick" in active_actions
    assert "check_variant" in active_actions
    assert "check_scores" in active_actions


def test_touch_standard_actions_keep_game_info_before_shared_status() -> None:
    game = prepare_active_game(make_game(web_first=True))
    player = game.players[0]

    action_ids = [entry.action.id for entry in game.get_all_enabled_actions(player)]

    assert action_ids.index("check_turn_timer") < action_ids.index("check_scores")
    assert action_ids.index("check_scores") < action_ids.index("whose_turn")
    assert action_ids.index("whose_turn") < action_ids.index("whos_at_table")


def test_player_finishing_does_not_end_hand_until_places_are_known() -> None:
    game = prepare_active_game(make_game(player_count=3, variant=SOUTHERN_VARIANT))
    player1, player2, player3 = game.players
    game.set_turn_players([player1, player2, player3])
    game.turn_index = 0
    game.is_first_turn = False
    game.current_combo = None
    game.trick_winner_id = None
    player1.hand = [c(1, 5, 4)]
    player2.hand = [c(2, 6, 4), c(3, 8, 4)]
    player3.hand = [c(4, 7, 4), c(5, 9, 4)]
    player1.selected_cards = {1}

    game.execute_action(player1, "play_selected")

    assert game.status == "playing"
    assert game.hand_wait_ticks == 0
    assert game.finishing_order_ids == [player1.id]
    assert player1.hand == []
    assert game.current_player == player2


def test_two_player_hand_settles_bankroll_coins() -> None:
    game = make_game(player_count=2, start=True, variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    player1.hand = []
    player2.hand = [c(2, 6, 4)]
    game.finishing_order_ids = []

    game._player_finishes(player1)

    assert game.hand_wait_ticks > 0
    assert player1.coins == 60
    assert player2.coins == 40
    assert game.hand_winner_id == player1.id


def test_southern_instant_win_reasons_include_common_an_trang_hands() -> None:
    game = make_game(player_count=2, variant=SOUTHERN_VARIANT)
    player = game.players[0]
    player.hand = [
        c(100, 2, 4), c(101, 2, 2), c(102, 2, 1), c(103, 2, 3),
        c(104, 3, 4), c(105, 5, 2), c(106, 7, 1), c(107, 9, 3),
        c(108, 11, 4), c(109, 12, 2), c(110, 13, 1), c(111, 1, 3), c(112, 4, 4),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-four-twos"

    player.hand = [
        c(120, 3, 4), c(121, 4, 2), c(122, 5, 1), c(123, 6, 3),
        c(124, 7, 4), c(125, 8, 2), c(126, 9, 1), c(127, 10, 3),
        c(128, 11, 4), c(129, 12, 2), c(130, 13, 1), c(131, 1, 3), c(132, 9, 4),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-dragon"

    player.hand = [
        c(140, 4, 4), c(141, 4, 2), c(142, 4, 1),
        c(143, 5, 4), c(144, 5, 2), c(145, 5, 1),
        c(146, 6, 4), c(147, 6, 2), c(148, 6, 1),
        c(149, 9, 4), c(150, 11, 2), c(151, 13, 1), c(152, 1, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-three-consecutive-triples"

    player.hand = [
        c(1, 3, 4), c(2, 3, 1),
        c(3, 5, 4), c(4, 5, 3),
        c(5, 7, 4), c(6, 7, 1),
        c(7, 9, 4), c(8, 9, 3),
        c(9, 11, 4), c(10, 11, 1),
        c(11, 13, 4), c(12, 13, 3),
        c(13, 1, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-six-pairs"

    player.hand = [
        c(21, 3, 4), c(22, 3, 1),
        c(23, 4, 2), c(24, 4, 3),
        c(25, 5, 4), c(26, 5, 1),
        c(27, 6, 2), c(28, 6, 3),
        c(29, 7, 4), c(30, 7, 1),
        c(31, 9, 4), c(32, 11, 1), c(33, 1, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-five-consecutive-pairs"


def test_instant_win_settles_as_per_opponent_payment() -> None:
    game = make_game(player_count=3, variant=SOUTHERN_VARIANT)
    player1, player2, player3 = game.players
    for player in game.players:
        player.coins = 50
    player1.hand = [c(index, 3 + (index // 2), 4 if index % 2 == 0 else 2) for index in range(12)]
    player1.hand.append(c(99, 1, 3))
    player2.hand = [c(200, 5, 4)]
    player3.hand = [c(201, 6, 4)]

    game._handle_instant_win(player1, "tienlen-instant-six-pairs", [player1, player2, player3])

    assert player1.coins == 90
    assert player2.coins == 30
    assert player3.coins == 30
    assert game.hand_wait_ticks > 0


def test_additional_southern_instant_win_reasons() -> None:
    game = make_game(player_count=2, variant=SOUTHERN_VARIANT)
    player = game.players[0]

    player.hand = [
        c(1, 3, 4), c(2, 3, 2),
        c(3, 4, 4), c(4, 4, 2),
        c(5, 5, 4), c(6, 5, 2),
        c(7, 6, 4), c(8, 6, 2),
        c(9, 7, 4), c(10, 7, 2),
        c(11, 8, 4), c(12, 8, 2),
        c(13, 10, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-six-consecutive-pairs"

    player.hand = [
        c(20, 3, 4), c(21, 3, 2), c(22, 3, 1),
        c(23, 5, 4), c(24, 5, 2), c(25, 5, 1),
        c(26, 7, 4), c(27, 7, 2), c(28, 7, 1),
        c(29, 9, 4), c(30, 9, 2), c(31, 9, 1),
        c(32, 13, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-four-triples"

    player.hand = [
        c(40, 4, 4), c(41, 4, 2), c(42, 4, 1), c(43, 4, 3),
        c(44, 9, 4), c(45, 9, 2), c(46, 9, 1), c(47, 9, 3),
        c(48, 5, 4), c(49, 7, 2), c(50, 11, 1), c(51, 13, 3), c(52, 1, 4),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-two-four-of-a-kind"

    player.hand = [
        c(60, 3, 4), c(61, 4, 2), c(62, 5, 4), c(63, 6, 2), c(64, 7, 4),
        c(65, 8, 2), c(66, 9, 4), c(67, 10, 2), c(68, 11, 4), c(69, 12, 2),
        c(70, 13, 4), c(71, 13, 2), c(72, 2, 3),
    ]
    assert game._instant_win_reason(player) == "tienlen-instant-same-color"


def test_chop_payment_is_settled_with_hand() -> None:
    game = prepare_active_game(make_game(player_count=3, variant=SOUTHERN_VARIANT))
    player1, player2, player3 = game.players
    game.set_turn_players([player1, player2, player3])
    game.turn_index = 1
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(90, 2, 3)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    player1.hand = [c(91, 9, 4)]
    player2.hand = [c(92, 10, 4)]
    player3.hand = [
        c(1, 5, 4), c(2, 5, 2),
        c(3, 6, 4), c(4, 6, 2),
        c(5, 7, 4), c(6, 7, 2),
    ]
    player3.selected_cards = {card.id for card in player3.hand}

    game.execute_action(player3, "play_selected")

    assert [(payment.payer_id, payment.receiver_id, payment.amount) for payment in game.hand_payments] == [
        (player1.id, player3.id, 20)
    ]

    game.finishing_order_ids = [player3.id, player2.id, player1.id]
    player3.hand = []
    game._finish_hand()

    assert player1.coins == 10
    assert player2.coins == 40
    assert player3.coins == 100


def test_settlement_breakdown_explains_offsetting_chop_and_rank_payments() -> None:
    game = make_game(player_count=2, start=True, variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    user1 = game.get_user(player1)
    assert isinstance(user1, MockUser)
    user1.clear_messages()
    game._add_hand_payment(player2, player1, 10, "chop")
    player1.hand = [c(1, 5, 4)]
    player2.hand = []
    game.finishing_order_ids = [player2.id, player1.id]

    game._finish_hand()

    messages = user1.get_spoken_messages()
    assert "Player2 takes first place." in messages
    assert "Coin settlement follows" not in " ".join(messages)
    assert "1. Player2: placing +10; chops -10; net 0; total 50." in messages
    assert "2. Player1: placing -10; chops +10; net 0; total 50." in messages


def test_same_shape_hang_chop_payment_is_settled() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, player3 = game.players
    game.set_turn_players([player1, player2, player3])
    game.turn_index = 2
    game.is_first_turn = False
    game.current_combo = evaluate_combo(
        [c(90, 4, 4), c(91, 4, 2), c(92, 5, 4), c(93, 5, 2), c(94, 6, 4), c(95, 6, 2)],
        SOUTHERN_VARIANT,
    )
    game.trick_winner_id = player1.id
    game.trick_play_id = 1
    player1.hand = [c(96, 10, 4)]
    player2.hand = [c(97, 11, 4)]
    player3.hand = [
        c(1, 7, 4), c(2, 7, 2),
        c(3, 8, 4), c(4, 8, 2),
        c(5, 9, 4), c(6, 9, 2),
    ]
    player3.passed_this_trick = True
    player3.passed_combo_turn = 0
    player3.selected_cards = {card.id for card in player3.hand}

    game.execute_action(player3, "play_selected")

    assert [(payment.payer_id, payment.receiver_id, payment.amount) for payment in game.hand_payments] == [
        (player1.id, player3.id, 10)
    ]


def test_pending_payment_and_chop_window_state_survive_save_reload() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, player3 = game.players
    game.set_turn_players([player1, player2, player3])
    game.turn_index = 1
    game.trick_play_id = 7
    game.trick_lead_fallback_id = player2.id
    game.current_combo = evaluate_combo([c(90, 2, 3)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    player2.passed_this_trick = True
    player2.passed_combo_turn = 7
    game._add_hand_payment(player1, player3, 20)

    restored = TienLenGame.from_json(game.to_json())
    restored_player2 = restored.players[1]

    assert restored.trick_play_id == 7
    assert restored.trick_lead_fallback_id == player2.id
    assert restored_player2.passed_this_trick is True
    assert restored_player2.passed_combo_turn == 7
    assert [
        (payment.payer_id, payment.receiver_id, payment.amount)
        for payment in restored.hand_payments
    ] == [(player1.id, player3.id, 20)]


def test_legacy_pending_payment_without_reason_restores_safely() -> None:
    game = make_game(player_count=2, start=True, variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    game._add_hand_payment(player1, player2, 10)
    payload = json.loads(game.to_json())
    del payload["hand_payments"][0]["reason"]

    restored = TienLenGame.from_json(json.dumps(payload))

    assert len(restored.hand_payments) == 1
    assert restored.hand_payments[0].reason == "adjustment"


def test_leftover_twos_and_hang_pay_first_place() -> None:
    game = make_game(player_count=2, start=True, variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    player1.hand = []
    player2.hand = [
        c(1, 2, 3),
        c(2, 5, 4), c(3, 5, 2),
        c(4, 6, 4), c(5, 6, 2),
        c(6, 7, 4), c(7, 7, 2),
    ]
    game.finishing_order_ids = []

    game._player_finishes(player1)

    assert player1.coins == 90
    assert player2.coins == 10


def test_bankroll_eliminates_zero_coin_players_and_ends_at_last_standing() -> None:
    game = make_game(player_count=2, start=True, match_length="50", variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    player1.coins = 50
    player2.coins = 10
    player1.hand = []
    player2.hand = [c(2, 6, 4)]
    game.finishing_order_ids = []

    game._player_finishes(player1)

    assert player2.coins == 0
    assert player2.eliminated is True
    assert game.status == "finished"


def test_out_of_turn_southern_chop_can_override_current_two() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, player3 = game.players
    game.set_turn_players([player1, player2, player3])
    game.turn_index = 1
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(90, 2, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    player3.hand = [
        c(1, 5, 4), c(2, 5, 2),
        c(3, 6, 4), c(4, 6, 2),
        c(5, 7, 4), c(6, 7, 2),
    ]
    player3.selected_cards = {card.id for card in player3.hand}
    game.refresh_menus(player3)
    game.flush_menus()

    game.execute_action(player3, "play_selected")

    assert game.trick_winner_id == player3.id
    assert game.current_player == player1


def test_play_and_pass_broadcasts_use_first_and_third_person() -> None:
    game = make_game(player_count=2, start=True, variant=SOUTHERN_VARIANT)
    player1, player2 = game.players
    game.set_turn_players([player1, player2])
    game.turn_index = 0
    game.is_first_turn = False
    player1.hand = [c(1, 5, 4), c(2, 9, 4)]
    player1.selected_cards = {1}
    user1 = game.get_user(player1)
    user2 = game.get_user(player2)
    assert isinstance(user1, MockUser)
    assert isinstance(user2, MockUser)
    user1.clear_messages()
    user2.clear_messages()

    game.execute_action(player1, "play_selected")

    assert "You play" in (user1.get_spoken_messages()[0])
    assert "Player1 plays" in (user2.get_spoken_messages()[0])

    user2._preferences.confirm_destructive_actions = False
    user1.clear_messages()
    user2.clear_messages()
    game.execute_action(player2, "pass")

    assert "Player2 passes" in (user1.get_spoken_messages()[0])
    assert "You pass" in (user2.get_spoken_messages()[0])


def test_southern_vietnamese_card_terms_are_variant_specific() -> None:
    game = TienLenGame(options=TienLenOptions(variant=SOUTHERN_VARIANT))
    assert game._read_cards([c(1, 2, 2), c(2, 12, 2)], "vi") == "heo chuồn và đầm chuồn"

    northern = TienLenGame(options=TienLenOptions(variant=NORTHERN_VARIANT))
    assert northern._read_cards([c(1, 2, 2)], "vi") != "heo chuồn"


def test_bot_game_completes_in_southern_variant() -> None:
    random.seed(1234)
    game = make_game(player_count=3, start=True, bot_all=True, match_length="50", variant=SOUTHERN_VARIANT)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=30000)


def test_bot_game_completes_in_northern_variant() -> None:
    random.seed(4321)
    game = make_game(player_count=3, start=True, bot_all=True, match_length="50", variant=NORTHERN_VARIANT)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=30000)
