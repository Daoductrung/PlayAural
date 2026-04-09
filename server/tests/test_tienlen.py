from pathlib import Path
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
        game.intro_wait_ticks = 1
        game.on_tick()
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
    assert game.options.match_length == "1"


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
    assert high_end_straight is not None and high_end_straight.type_name == "straight"


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
    assert rules.combo_beats(bon_doi_thong, pair_twos) is True
    assert rules.combo_beats(bon_doi_thong, tu_quy) is True


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


def test_northern_cannot_finish_on_two() -> None:
    rules = get_rules(NORTHERN_VARIANT)
    hand = [c(1, 2, 3)]
    selected = hand[:]
    is_valid, error_key, _ = rules.validate_play(hand, selected, None, False, False)
    assert is_valid is False
    assert error_key == "tienlen-error-cannot-finish-on-two"


def test_first_turn_requires_three_of_spades() -> None:
    game = make_game(start=True)
    current = game.current_player
    assert current is not None
    current.hand = [c(1, 3, 4), c(2, 4, 4), c(3, 5, 4)]
    current.selected_cards = {2}

    game.execute_action(current, "play_selected")

    user = game.get_user(current)
    assert isinstance(user, MockUser)
    assert user.get_last_spoken() == "You must include the 3 of Spades in the opening play."


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
        "In Northern Tien Len, your play must match the required suit or color structure of the current trick."
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

    game.execute_action(follower, "pass")

    assert game.current_player == leader
    assert game.current_combo is None


def test_southern_pass_lock_reports_chop_specific_error() -> None:
    game = make_game(player_count=3, start=True, variant=SOUTHERN_VARIANT)
    player1, player2, _ = game.players
    game.is_first_turn = False
    game.current_combo = evaluate_combo([c(50, 2, 4)], SOUTHERN_VARIANT)
    game.trick_winner_id = player1.id
    game.turn_index = game.turn_player_ids.index(player2.id)
    player2.passed_this_trick = True
    player2.hand = [c(1, 5, 4)]
    player2.selected_cards = {1}

    game._action_play_selected(player2, "play_selected")

    user = game.get_user(player2)
    assert isinstance(user, MockUser)
    assert user.get_last_spoken() == (
        "You already passed on this trick. You may only return with a legal chop against the current 2s."
    )


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

    game.rebuild_player_menu(current)

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

    active_game = make_game(web_first=True, start=True)
    active_player = active_game.players[0]
    active_actions = {entry.action.id for entry in active_game.get_all_visible_actions(active_player)}
    assert "check_trick" in active_actions
    assert "check_variant" in active_actions
    assert "check_scores" in active_actions


def test_bot_game_completes_in_southern_variant() -> None:
    random.seed(1234)
    game = make_game(player_count=3, start=True, bot_all=True, match_length="1", variant=SOUTHERN_VARIANT)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=12000)


def test_bot_game_completes_in_northern_variant() -> None:
    random.seed(4321)
    game = make_game(player_count=3, start=True, bot_all=True, match_length="1", variant=NORTHERN_VARIANT)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=12000)
