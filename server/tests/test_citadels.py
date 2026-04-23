"""Tests for Citadels."""

from pathlib import Path
import random

from ..games.citadels.game import (
    BASE_CHARACTER_RANKS,
    BUILD_SOUNDS,
    CHARACTER_ARCHITECT,
    CHARACTER_ASSASSIN,
    CHARACTER_BISHOP,
    CHARACTER_KING,
    CHARACTER_MAGICIAN,
    CHARACTER_MERCHANT,
    CHARACTER_QUEEN,
    CHARACTER_THIEF,
    CHARACTER_WARLORD,
    CitadelsGame,
    COIN_SOUNDS,
    COLLAPSE_SOUNDS,
    DEAL_SOUNDS,
    DISTRICT_NOBLE,
    DISTRICT_RELIGIOUS,
    DISTRICT_MILITARY,
    DISTRICT_TRADE,
    DISTRICT_UNIQUE,
    DistrictCard,
    PHASE_RANK_RESOLUTION,
    SOUND_ASSASSINATED_SKIP,
    SOUND_ASSASSINATE_DECLARE,
    SOUND_CITY_COMPLETE,
    SOUND_CROWN,
    SOUND_MAGIC_SWAP,
    SOUND_WARLORD_FIRE,
    SOUND_WIN,
    SUBPHASE_ASSASSIN_TARGET,
    SUBPHASE_THIEF_TARGET,
    THIEF_LAUGH_SOUNDS,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 4,
    start: bool = False,
    bot_all: bool = False,
    touch_first: bool = False,
) -> CitadelsGame:
    game = CitadelsGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if touch_first and index == 0:
                user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def advance_ticks(game: CitadelsGame, ticks: int) -> None:
    for _ in range(ticks):
        game.on_tick()


def advance_until(game: CitadelsGame, condition, max_ticks: int = 400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def reset_turn_state(game: CitadelsGame) -> None:
    game.phase = "turn_phase"
    game.turn_subphase = "normal"
    game.pending_draw_choices.clear()
    game.selected_card_ids.clear()
    game.pending_build_card_id = None
    game.turn_resource_taken = False
    game.turn_income_used = False
    game.turn_character_ability_used = False
    game.turn_build_limit = 1
    game.turn_builds_made = 0
    game.turn_laboratory_used = False
    game.turn_smithy_used = False


def begin_turn(game: CitadelsGame, player, rank: int) -> None:
    reset_turn_state(game)
    game.current_rank = rank
    game.set_turn_players([player])
    player.selected_character_rank = rank
    player.revealed_character_rank = rank
    game._begin_turn(player, rank)
    advance_until(game, lambda: not game.has_active_sequence(), max_ticks=100)


def make_card(card_id: int, name: str, cost: int, district_type: str, effect_key: str = "") -> DistrictCard:
    return DistrictCard(
        id=card_id,
        slug=name.lower().replace(" ", "_").replace("'", ""),
        name=name,
        cost=cost,
        district_type=district_type,
        effect_key=effect_key,
    )


def test_game_registered_and_defaults() -> None:
    assert GameRegistry.get("citadels") is CitadelsGame
    game = CitadelsGame()
    assert game.get_name() == "Citadels"
    assert game.get_type() == "citadels"
    assert game.get_min_players() == 4
    assert game.get_max_players() == 8
    assert game.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]


def test_prestart_validation_enforces_four_to_eight_players() -> None:
    assert "action-need-more-players" in make_game(player_count=2).prestart_validate()
    assert "action-need-more-players" in make_game(player_count=3).prestart_validate()
    assert make_game(player_count=4).prestart_validate() == []


def test_selection_setup_uses_correct_discard_counts_and_queen_only_at_eight() -> None:
    game4 = make_game(player_count=4, start=True)
    assert len(game4.faceup_discarded_ranks) == 2
    assert len(game4.facedown_discarded_ranks) == 1
    assert CHARACTER_QUEEN not in game4._character_ranks_in_play()

    game5 = make_game(player_count=5, start=True)
    assert len(game5.faceup_discarded_ranks) == 1
    assert len(game5.facedown_discarded_ranks) == 1

    game7 = make_game(player_count=7, start=True)
    assert len(game7.faceup_discarded_ranks) == 0
    assert len(game7.facedown_discarded_ranks) == 1
    assert game7._character_ranks_in_play() == BASE_CHARACTER_RANKS

    game8 = make_game(player_count=8, start=True)
    assert len(game8.faceup_discarded_ranks) == 0
    assert len(game8.facedown_discarded_ranks) == 1
    assert CHARACTER_QUEEN in game8._character_ranks_in_play()


def test_selection_phase_plays_turn_sound_and_prompts_the_current_picker() -> None:
    game = make_game(start=True)
    first = game.players[0]
    second = game.players[1]
    first_user = game.get_user(first)
    second_user = game.get_user(second)
    assert first_user is not None
    assert second_user is not None

    assert "turn.ogg" in first_user.get_sounds_played()
    assert "Choose a character now." in first_user.get_spoken_messages()
    first_selection_updates = [
        message for message in first_user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert first_selection_updates
    assert first_selection_updates[-1].data.get("selection_id", "").startswith("select_character_")

    second_user.clear_messages()
    available_rank = game._selection_options_for_player(first)[0]
    game.execute_action(first, f"select_character_{available_rank}")

    assert game.current_player == second
    assert second_user.get_sounds_played() == ["turn.ogg"]
    assert second_user.get_last_spoken() == "Choose a character now."
    second_selection_updates = [
        message for message in second_user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert second_selection_updates
    assert second_selection_updates[-1].data.get("selection_id", "").startswith("select_character_")


def test_seven_player_last_picker_can_choose_the_initial_facedown_rank() -> None:
    game = make_game(player_count=7, start=True)
    game.available_character_ranks = [CHARACTER_WARLORD]
    game.selection_index = len(game.selection_order_player_ids) - 1
    last = game._selection_player()
    assert last is not None
    game.set_turn_players([last])

    options = game._selection_options_for_player(last)
    assert set(options) == {CHARACTER_WARLORD, game.initial_facedown_rank}


def test_replaced_player_bot_auto_selects_character_during_selection() -> None:
    random.seed(7)
    game = make_game(start=True)
    replaced = game.current_player
    assert replaced is not None

    game._replace_with_bot(replaced)

    assert replaced.is_bot is True
    assert advance_until(
        game,
        lambda: isinstance(replaced.selected_character_rank, int) and game.selection_index >= 1,
        max_ticks=200,
    )


def test_assassin_target_skips_the_rank_with_sequence_sound() -> None:
    game = make_game(start=True)
    assassin, victim, next_player = game.players[:3]
    assassin.selected_character_rank = CHARACTER_ASSASSIN
    victim.selected_character_rank = CHARACTER_MERCHANT
    next_player.selected_character_rank = CHARACTER_ARCHITECT
    game.current_rank = CHARACTER_ASSASSIN
    game.phase = PHASE_RANK_RESOLUTION

    user = game.get_user(assassin)
    assert user is not None
    user.clear_messages()

    game._advance_rank_resolution()
    assert game.current_player == assassin
    assert game.turn_subphase == SUBPHASE_ASSASSIN_TARGET

    game.execute_action(assassin, f"assassinate_target_{CHARACTER_MERCHANT}")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=80)

    game._finish_turn()
    assert advance_until(
        game,
        lambda: victim.revealed_character_rank is None and next_player.revealed_character_rank == CHARACTER_ARCHITECT,
        max_ticks=200,
    )

    sounds = user.get_sounds_played()
    assert SOUND_ASSASSINATE_DECLARE in sounds
    assert SOUND_ASSASSINATED_SKIP in sounds


def test_thief_steals_on_reveal_and_large_thefts_trigger_laugh() -> None:
    game = make_game(start=True)
    thief, victim = game.players[:2]
    thief.selected_character_rank = CHARACTER_THIEF
    victim.selected_character_rank = CHARACTER_MERCHANT
    thief.gold = 0
    victim.gold = 6
    game.current_rank = CHARACTER_THIEF
    game.phase = PHASE_RANK_RESOLUTION

    user = game.get_user(thief)
    assert user is not None
    user.clear_messages()

    game._advance_rank_resolution()
    assert game.turn_subphase == SUBPHASE_THIEF_TARGET

    game.execute_action(thief, f"thief_target_{CHARACTER_MERCHANT}")
    game._finish_turn()

    assert advance_until(
        game,
        lambda: game.current_player == victim
        and thief.gold == 6
        and victim.gold == 0
        and not game.has_active_sequence(),
        max_ticks=240,
    )

    sounds = user.get_sounds_played()
    assert COIN_SOUNDS["large"] in sounds
    assert any(sound in THIEF_LAUGH_SOUNDS for sound in sounds)


def test_thief_cannot_target_the_thief_rank_itself() -> None:
    game = make_game(start=True)
    thief = game.players[0]
    begin_turn(game, thief, CHARACTER_THIEF)

    assert CHARACTER_THIEF not in game._thief_target_ranks()


def test_magician_swap_sequence_plays_magic_then_deal_and_swaps_hands() -> None:
    game = make_game(start=True)
    magician, target = game.players[:2]
    magician.hand = [make_card(500, "Temple", 1, DISTRICT_TRADE)]
    target.hand = [
        make_card(501, "Palace", 5, DISTRICT_TRADE),
        make_card(502, "Castle", 4, DISTRICT_TRADE),
    ]
    begin_turn(game, magician, CHARACTER_MAGICIAN)
    game.turn_resource_taken = True

    user = game.get_user(magician)
    assert user is not None
    user.clear_messages()

    game.execute_action(magician, "magician_swap_mode")
    game.execute_action(magician, f"magician_swap_target_{target.id}")

    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert [card.name for card in magician.hand] == ["Palace", "Castle"]
    assert [card.name for card in target.hand] == ["Temple"]

    sounds = user.get_sounds_played()
    assert sounds[:2][0] == SOUND_MAGIC_SWAP
    assert sounds[:2][1] in DEAL_SOUNDS


def test_magician_redraw_replaces_selected_cards() -> None:
    game = make_game(start=True)
    magician = game.players[0]
    magician.hand = [
        make_card(510, "Temple", 1, DISTRICT_TRADE),
        make_card(511, "Palace", 5, DISTRICT_TRADE),
        make_card(512, "Castle", 4, DISTRICT_TRADE),
    ]
    game.district_deck = [
        make_card(513, "Market", 2, DISTRICT_TRADE),
        make_card(514, "Harbor", 4, DISTRICT_TRADE),
    ]
    begin_turn(game, magician, CHARACTER_MAGICIAN)
    game.turn_resource_taken = True

    game.execute_action(magician, "magician_redraw")
    game.execute_action(magician, "magician_redraw_toggle_510")
    game.execute_action(magician, "confirm_magician_redraw")

    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert {card.id for card in magician.hand} == {511, 512, 513}
    assert game.turn_character_ability_used is True


def test_king_takes_the_crown_and_queen_bonus_is_adjacent_only() -> None:
    king_game = make_game(start=True)
    king = king_game.players[0]
    king_game.crown_holder_id = king_game.players[1].id
    king.selected_character_rank = CHARACTER_KING
    king_game.current_rank = CHARACTER_KING
    king_game.phase = PHASE_RANK_RESOLUTION

    king_user = king_game.get_user(king)
    assert king_user is not None
    king_user.clear_messages()

    king_game._advance_rank_resolution()
    assert king_game.has_active_sequence() is True
    assert SOUND_CROWN in king_user.get_sounds_played()
    assert advance_until(king_game, lambda: not king_game.has_active_sequence(), max_ticks=120)
    assert king_game.crown_holder_id == king.id

    queen_game = make_game(player_count=8, start=True)
    king = queen_game.players[0]
    queen = queen_game.players[1]
    king.selected_character_rank = CHARACTER_KING
    queen.selected_character_rank = CHARACTER_QUEEN
    queen.gold = 2
    queen_user = queen_game.get_user(queen)
    assert queen_user is not None
    queen_user.clear_messages()

    begin_turn(queen_game, queen, CHARACTER_QUEEN)
    assert queen.gold == 5
    assert queen_user.get_sounds_played() == ["turn.ogg"]


def test_killed_king_still_takes_the_crown_at_end_of_round() -> None:
    game = make_game(start=True)
    king = game.players[0]
    prior_holder = game.players[1]
    king.selected_character_rank = CHARACTER_KING
    game.crown_holder_id = prior_holder.id
    game.killed_rank = CHARACTER_KING

    game._start_round_cleanup()
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert game.crown_holder_id == king.id


def test_unique_district_cost_duplicate_and_income_rules_work() -> None:
    game = make_game(start=True)
    player = game.players[0]

    factory = make_card(600, "Factory", 5, DISTRICT_UNIQUE, "factory")
    dragon_gate = make_card(601, "Dragon Gate", 6, DISTRICT_UNIQUE, "dragon_gate")
    market = make_card(602, "Market", 2, DISTRICT_TRADE)
    quarry = make_card(603, "Quarry", 5, DISTRICT_UNIQUE, "quarry")
    school = make_card(604, "School of Magic", 6, DISTRICT_UNIQUE, "school_of_magic")

    player.city = [factory]
    assert game._effective_build_cost(player, dragon_gate) == 5
    assert game._effective_build_cost(player, factory) == 5
    assert game._effective_build_cost(player, market) == 2

    player.city = [market]
    assert game._can_build_duplicate(player, make_card(605, "Market", 2, DISTRICT_TRADE)) is False
    player.city = [quarry]
    assert game._can_build_duplicate(player, make_card(606, "Market", 2, DISTRICT_TRADE)) is True

    player.city = [market, school]
    assert game._income_amount(player, CHARACTER_MERCHANT) == 3
    assert game._income_amount(player, CHARACTER_KING) == 1


def test_unique_district_action_effects_work() -> None:
    game = make_game(start=True)
    player = game.players[0]

    player.city = [make_card(610, "Library", 6, DISTRICT_UNIQUE, "library")]
    game.district_deck = [
        make_card(611, "Temple", 1, DISTRICT_RELIGIOUS),
        make_card(612, "Market", 2, DISTRICT_TRADE),
    ]
    begin_turn(game, player, CHARACTER_MERCHANT)
    game.execute_action(player, "draw_cards")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert game.turn_subphase == "normal"
    assert game.pending_draw_choices == []
    assert {card.id for card in player.hand} >= {611, 612}

    player.city = [make_card(613, "Laboratory", 5, DISTRICT_UNIQUE, "laboratory")]
    player.hand = [make_card(614, "Church", 2, DISTRICT_RELIGIOUS)]
    player.gold = 0
    begin_turn(game, player, CHARACTER_MERCHANT)
    game.turn_resource_taken = True
    game.execute_action(player, "use_laboratory")
    game.execute_action(player, "laboratory_discard_614")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert player.gold == 2
    assert player.hand == []
    assert game.turn_laboratory_used is True

    player.city = [make_card(615, "Smithy", 5, DISTRICT_UNIQUE, "smithy")]
    player.hand = []
    player.gold = 2
    game.district_deck = [
        make_card(616, "Temple", 1, DISTRICT_RELIGIOUS),
        make_card(617, "Market", 2, DISTRICT_TRADE),
        make_card(618, "Manor", 3, DISTRICT_NOBLE),
    ]
    begin_turn(game, player, CHARACTER_MERCHANT)
    game.turn_resource_taken = True
    game.execute_action(player, "use_smithy")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert player.gold == 0
    assert len(player.hand) == 3
    assert game.turn_smithy_used is True

    player.city = []
    player.hand = [
        make_card(619, "Thieves' Den", 6, DISTRICT_UNIQUE, "thieves_den"),
        make_card(620, "Temple", 1, DISTRICT_RELIGIOUS),
        make_card(621, "Market", 2, DISTRICT_TRADE),
    ]
    player.gold = 4
    begin_turn(game, player, CHARACTER_MERCHANT)
    game.turn_resource_taken = True
    game.execute_action(player, "build_619")
    game.execute_action(player, "thieves_den_toggle_620")
    game.execute_action(player, "thieves_den_toggle_621")
    game.execute_action(player, "confirm_thieves_den_payment")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert [card.effect_key for card in player.city] == ["thieves_den"]
    assert player.gold == 0
    assert player.hand == []


def test_unique_district_scoring_and_keep_protection_work() -> None:
    game = make_game(start=True)
    player = game.players[0]
    warlord = game.players[1]

    keep = make_card(630, "Keep", 3, DISTRICT_UNIQUE, "keep")
    warlord.gold = 10
    warlord.city = []
    player.city = [keep]
    begin_turn(game, warlord, CHARACTER_WARLORD)
    game.turn_resource_taken = True
    assert game._warlord_targets() == []

    dragon_gate = make_card(631, "Dragon Gate", 6, DISTRICT_UNIQUE, "dragon_gate")
    player.city = [dragon_gate]
    assert game._score_city(player) == 8

    imperial = make_card(632, "Imperial Treasury", 5, DISTRICT_UNIQUE, "imperial_treasury")
    player.city = [imperial]
    player.gold = 4
    assert game._score_city(player) == 9

    map_room = make_card(633, "Map Room", 5, DISTRICT_UNIQUE, "map_room")
    player.city = [map_room]
    player.hand = [
        make_card(634, "Temple", 1, DISTRICT_RELIGIOUS),
        make_card(635, "Market", 2, DISTRICT_TRADE),
        make_card(636, "Manor", 3, DISTRICT_NOBLE),
    ]
    assert game._score_city(player) == 8

    statue = make_card(637, "Statue", 3, DISTRICT_UNIQUE, "statue")
    player.city = [statue]
    game.crown_holder_id = player.id
    assert game._score_city(player) == 8

    player.city = [
        make_card(638, "Wishing Well", 5, DISTRICT_UNIQUE, "wishing_well"),
        make_card(639, "Keep", 3, DISTRICT_UNIQUE, "keep"),
        make_card(640, "Quarry", 5, DISTRICT_UNIQUE, "quarry"),
    ]
    assert game._score_city(player) == 16

    player.city = [
        make_card(641, "Haunted Quarter", 2, DISTRICT_UNIQUE, "haunted_quarter"),
        make_card(642, "Keep", 3, DISTRICT_UNIQUE, "keep"),
        make_card(643, "Manor", 3, DISTRICT_NOBLE),
        make_card(644, "Temple", 1, DISTRICT_RELIGIOUS),
        make_card(645, "Market", 2, DISTRICT_TRADE),
    ]
    assert game._score_city(player) == 14


def test_district_descriptions_appear_in_hand_build_and_warlord_labels() -> None:
    game = make_game(start=True)
    player = game.players[0]
    target = game.players[1]
    laboratory = make_card(650, "Laboratory", 5, DISTRICT_UNIQUE, "laboratory")

    district_line = game._district_line(laboratory, "en")
    assert "Once per turn, discard a card from your hand to gain 2 gold." in district_line

    player.hand = [laboratory]
    player.gold = 5
    begin_turn(game, player, CHARACTER_MERCHANT)
    game.turn_resource_taken = True
    build_action = game.find_action(player, "build_650")
    assert build_action is not None
    assert "Once per turn, discard a card from your hand to gain 2 gold." in build_action.label

    target.city = [laboratory]
    begin_turn(game, player, CHARACTER_WARLORD)
    player.gold = 10
    game.turn_resource_taken = True
    game.execute_action(player, "warlord_destroy_mode")
    destroy_action = game.find_action(player, f"warlord_destroy_target_{target.id}_650")
    assert destroy_action is not None
    assert "Once per turn, discard a card from your hand to gain 2 gold." in destroy_action.label


def test_dynamic_target_and_toggle_menus_focus_the_expected_item() -> None:
    game = make_game(start=True)
    player = game.players[0]
    target = game.players[1]
    user = game.get_user(player)
    assert user is not None

    player.hand = [
        make_card(660, "Laboratory", 5, DISTRICT_UNIQUE, "laboratory"),
        make_card(661, "Temple", 1, DISTRICT_RELIGIOUS),
    ]
    player.gold = 5
    target.hand = [make_card(662, "Market", 2, DISTRICT_TRADE)]

    begin_turn(game, player, CHARACTER_MAGICIAN)
    game.turn_resource_taken = True
    user.clear_messages()
    game.execute_action(player, "magician_swap_mode")
    swap_updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert swap_updates[-1].data.get("selection_id") == f"magician_swap_target_{target.id}"

    begin_turn(game, player, CHARACTER_MAGICIAN)
    game.turn_resource_taken = True
    user.clear_messages()
    game.execute_action(player, "magician_redraw")
    redraw_updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert redraw_updates[-1].data.get("selection_id") == "magician_redraw_toggle_660"

    user.clear_messages()
    game.execute_action(player, "magician_redraw_toggle_661")
    toggle_updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert toggle_updates[-1].data.get("selection_id") == "magician_redraw_toggle_661"

    target.city = [make_card(663, "Laboratory", 5, DISTRICT_UNIQUE, "laboratory")]
    begin_turn(game, player, CHARACTER_WARLORD)
    player.gold = 10
    game.turn_resource_taken = True
    user.clear_messages()
    game.execute_action(player, "warlord_destroy_mode")
    warlord_updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert warlord_updates[-1].data.get("selection_id") == f"warlord_destroy_target_{target.id}_663"


def test_read_character_announces_character_and_current_gold() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    player.selected_character_rank = CHARACTER_KING
    player.gold = 6
    user.clear_messages()

    game.execute_action(player, "read_character")

    assert user.get_spoken_messages()[-1] == "Rank 4: King. You have 6 gold."


def test_canceling_swap_submenu_restores_focus_to_parent_menu_top_action() -> None:
    game = make_game(start=True)
    player = game.players[0]
    target = game.players[1]
    user = game.get_user(player)
    assert user is not None

    player.hand = [make_card(670, "Palace", 5, DISTRICT_NOBLE)]
    player.gold = 0
    target.hand = [make_card(671, "Market", 2, DISTRICT_TRADE)]

    begin_turn(game, player, CHARACTER_MAGICIAN)
    game.turn_resource_taken = True
    game.execute_action(player, "magician_swap_mode")

    user.clear_messages()
    game.execute_action(player, "cancel_subphase")
    updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert updates
    assert updates[-1].data.get("selection_id") == "magician_swap_mode"


def test_assassin_target_selection_restores_focus_to_main_turn_menu_top_action() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    begin_turn(game, player, CHARACTER_ASSASSIN)
    user.clear_messages()
    game.execute_action(player, f"assassinate_target_{CHARACTER_KING}")
    updates = [
        message for message in user.messages
        if message.type == "update_menu" and message.data.get("menu_id") == "turn_menu"
    ]
    assert updates
    assert updates[-1].data.get("selection_id") == "take_gold"


def test_merchant_income_adds_trade_gold_plus_bonus() -> None:
    game = make_game(start=True)
    merchant = game.players[0]
    merchant.gold = 0
    merchant.city = [make_card(520, "Market", 2, DISTRICT_TRADE)]
    begin_turn(game, merchant, CHARACTER_MERCHANT)
    game.turn_resource_taken = True

    game.execute_action(merchant, "collect_income")
    assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)
    assert merchant.gold == 2
    assert game.turn_income_used is True


def test_architect_bonus_draws_two_and_allows_three_builds() -> None:
    game = make_game(start=True)
    architect = game.players[0]
    architect.gold = 10
    architect.hand = [
        make_card(530, "Temple", 1, DISTRICT_TRADE),
        make_card(531, "Market", 2, DISTRICT_TRADE),
        make_card(532, "Watchtower", 1, DISTRICT_MILITARY),
    ]
    game.district_deck = [
        make_card(533, "Harbor", 4, DISTRICT_TRADE),
        make_card(534, "Castle", 4, DISTRICT_TRADE),
    ]

    begin_turn(game, architect, CHARACTER_ARCHITECT)
    assert len(architect.hand) == 5
    assert game.turn_build_limit == 3

    game.turn_resource_taken = True
    for action_id in ("build_530", "build_531", "build_532"):
        game.execute_action(architect, action_id)
        assert advance_until(game, lambda: not game.has_active_sequence(), max_ticks=120)

    assert len(architect.city) == 3
    assert game.turn_builds_made == 3
    assert game._may_build_more() is False


def test_bishop_blocks_warlord_targets_until_the_bishop_is_killed() -> None:
    game = make_game(start=True)
    warlord, bishop = game.players[:2]
    warlord.gold = 5
    warlord.selected_character_rank = CHARACTER_WARLORD
    warlord.revealed_character_rank = CHARACTER_WARLORD
    bishop.selected_character_rank = CHARACTER_BISHOP
    bishop.city = [make_card(540, "Watchtower", 1, DISTRICT_MILITARY)]

    begin_turn(game, warlord, CHARACTER_WARLORD)
    game.turn_resource_taken = True

    assert bishop not in [owner for owner, _ in game._warlord_targets()]

    game.killed_rank = CHARACTER_BISHOP
    assert bishop in [owner for owner, _ in game._warlord_targets()]


def test_warlord_destroy_sequence_plays_fire_then_collapse_before_removing_the_district() -> None:
    game = make_game(start=True)
    warlord, victim = game.players[:2]
    warlord.gold = 5
    victim.city = [make_card(550, "Prison", 2, DISTRICT_MILITARY)]
    begin_turn(game, warlord, CHARACTER_WARLORD)
    game.turn_resource_taken = True

    user = game.get_user(warlord)
    assert user is not None
    user.clear_messages()

    target_owner, target_card = game._warlord_targets()[0]
    assert target_owner == victim
    game.execute_action(warlord, "warlord_destroy_mode")
    game.execute_action(warlord, f"warlord_destroy_target_{victim.id}_{target_card.id}")

    assert user.get_sounds_played() == [SOUND_WARLORD_FIRE]
    assert advance_until(game, lambda: len(user.get_sounds_played()) >= 2, max_ticks=120)
    assert user.get_sounds_played()[1] in COLLAPSE_SOUNDS
    assert advance_until(game, lambda: not victim.city and not game.has_active_sequence(), max_ticks=120)


def test_coin_beats_use_the_expected_tiers_and_optional_laugh() -> None:
    game = make_game()
    assert game._build_coin_beats(2)[0].ops[0].sound == COIN_SOUNDS["small"]
    assert game._build_coin_beats(3)[0].ops[0].sound == COIN_SOUNDS["medium"]
    assert game._build_coin_beats(5)[0].ops[0].sound == COIN_SOUNDS["large"]
    assert len(game._build_coin_beats(5, allow_laugh=False)) == 1

    large_theft = game._build_coin_beats(5, allow_laugh=True)
    assert len(large_theft) == 2
    assert large_theft[1].ops[0].sound in THIEF_LAUGH_SOUNDS


def test_city_completion_sound_only_triggers_on_threshold_and_final_win_waits_for_sequence() -> None:
    game = make_game(start=True)
    player = game.players[0]
    card = make_card(560, "Temple", 1, DISTRICT_TRADE)

    player.city = [make_card(561 + index, f"Card{index}", 1, DISTRICT_TRADE) for index in range(5)]
    beats = game._build_district_beats(player, card, [], 1)
    assert SOUND_CITY_COMPLETE not in [op.sound for beat in beats for op in beat.ops if op.kind == "sound"]

    player.city = [make_card(570 + index, f"Card{index}", 1, DISTRICT_TRADE) for index in range(6)]
    beats = game._build_district_beats(player, card, [], 1)
    assert SOUND_CITY_COMPLETE in [op.sound for beat in beats for op in beat.ops if op.kind == "sound"]

    player.city = [make_card(580 + index, f"Built{index}", 1, DISTRICT_TRADE) for index in range(7)]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game._complete_round_cleanup()
    assert game.has_active_sequence() is True
    assert user.get_sounds_played() == [SOUND_WIN]
    assert game.status != "finished"
    assert advance_until(game, lambda: game.status == "finished", max_ticks=200)
    assert user.get_last_spoken() == "Player1 wins!"


def test_touch_standard_actions_follow_the_shared_touch_order() -> None:
    game = make_game(start=True, touch_first=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    action_set = game.create_standard_action_set(player)
    order = action_set._order
    assert order.index("read_status") < order.index("read_status_detailed")
    assert order.index("read_status_detailed") < order.index("read_character")
    assert order.index("read_status") < order.index("read_character")
    assert order.index("read_character") < order.index("read_hand")
    assert order.index("read_hand") < order.index("read_cities")
    assert order.index("read_cities") < order.index("read_discards")
    assert order.index("read_discards") < order.index("check_scores")
    assert order.index("check_scores") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")

    game.rebuild_player_menu(player)
    visible_ids = [item.id for item in user.menus["turn_menu"]["items"] if getattr(item, "id", None)]
    assert visible_ids.index("read_status") < visible_ids.index("check_scores")
    assert visible_ids.index("read_status_detailed") < visible_ids.index("check_scores")
    assert visible_ids.index("check_scores") < visible_ids.index("whose_turn")
    assert visible_ids.index("whose_turn") < visible_ids.index("whos_at_table")


def test_info_actions_remain_visible_while_gameplay_sequences_lock_the_turn() -> None:
    game = make_game(start=True, touch_first=True)
    player = game.players[0]
    begin_turn(game, player, CHARACTER_MERCHANT)

    game.execute_action(player, "draw_cards")
    assert game.has_active_sequence() is True

    visible_ids = [entry.action.id for entry in game.get_all_visible_actions(player)]
    assert "take_gold" not in visible_ids
    assert "draw_cards" not in visible_ids
    for action_id in (
        "read_status",
        "read_status_detailed",
        "read_character",
        "read_hand",
        "read_cities",
        "read_discards",
    ):
        assert action_id in visible_ids


def test_status_character_and_discards_use_tts_while_detailed_status_opens_a_status_box() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    begin_turn(game, player, CHARACTER_ASSASSIN)
    game.faceup_discarded_ranks = [CHARACTER_KING, CHARACTER_BISHOP]
    user.clear_messages()

    game.execute_action(player, "read_status")
    game.execute_action(player, "read_character")
    game.execute_action(player, "read_discards")

    message_types = [message.type for message in user.messages]
    assert "show_menu" not in message_types
    assert any(message.type == "speak" for message in user.messages)

    user.clear_messages()
    game.execute_action(player, "read_status_detailed")
    assert any(message.type == "show_menu" and message.data.get("menu_id") == "status_box" for message in user.messages)
    detailed_lines = game._status_lines("en", detailed=True)
    assert not any("Faceup discarded characters:" in line for line in detailed_lines)
    assert not any("Current standings" in line for line in detailed_lines)


def test_bot_game_completes_without_deadlock() -> None:
    random.seed(0)
    game = make_game(player_count=4, start=True, bot_all=True)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=20000)


def test_assassin_bot_targeting_is_not_locked_to_warlord() -> None:
    game = make_game(start=True)
    assassin, king, merchant, warlord = game.players[:4]
    assassin.is_bot = True
    assassin.selected_character_rank = CHARACTER_ASSASSIN
    assassin.revealed_character_rank = CHARACTER_ASSASSIN
    king.selected_character_rank = CHARACTER_KING
    king.city = [make_card(900 + index, "Castle", 4, DISTRICT_NOBLE) for index in range(6)]
    king.gold = 5
    merchant.selected_character_rank = CHARACTER_MERCHANT
    merchant.gold = 7
    warlord.selected_character_rank = CHARACTER_WARLORD
    warlord.gold = 2
    game.phase = "turn_phase"
    game.turn_subphase = SUBPHASE_ASSASSIN_TARGET
    game.set_turn_players([assassin])

    picks: set[str] = set()
    for seed in range(20):
        random.seed(seed)
        action_id = game.bot_think(assassin)
        assert action_id is not None
        picks.add(action_id)

    assert len(picks) >= 2
    assert any(not action_id.endswith(str(CHARACTER_WARLORD)) for action_id in picks)
