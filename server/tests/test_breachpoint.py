"""Tests for the Breach Point tactical board game."""

import hashlib
import json
import math
from dataclasses import replace
from itertools import pairwise
from pathlib import Path, PurePath, PurePosixPath

from ..audio import distance_attenuation_gain
from ..game_utils.actions import Visibility
from ..game_utils.reaction_window import ReactionWindow
from ..game_utils.stats_helpers import RatingHelper
from ..games.breachpoint.arsenal import (
    AK47,
    AWP,
    DEFUSE_KIT,
    DESERT_EAGLE,
    FAMAS,
    FLASHBANG,
    GALIL_AR,
    GLOCK,
    HE_GRENADE,
    INCENDIARY_GRENADE,
    M4,
    MAC10,
    MOLOTOV,
    MP9,
    NOVA,
    PURCHASE_ROLE_ANTI_ECO,
    PURCHASE_ROLE_BUDGET,
    PURCHASE_ROLE_PRECISION,
    PURCHASE_ROLE_STANDARD,
    SMOKE_GRENADE,
    SSG08,
    STANDARD_ECONOMY,
    USP_S,
    UTILITY_EFFECT_FIRE,
    UTILITY_EFFECT_SMOKE,
    WEAPON_SLOT_PRIMARY,
    WEAPON_SLOT_SIDEARM,
    UtilityProfile,
    get_default_sidearm,
    get_purchasable_equipment,
    get_purchasable_utilities,
    get_purchasable_weapons,
)
from ..games.breachpoint.audio import (
    BODY_FALL_ASSETS_BY_SURFACE,
    BOMB_ARM_ASSET,
    BOMB_ARM_START_RATIO,
    BOMB_BEEP_ASSETS,
    BOMB_EXPLOSION_ASSET,
    BOMB_EXPLOSION_HANDLE,
    BOMB_KEYPAD_ASSETS,
    BOMB_NVG_ON_ASSET,
    BOMB_PICKUP_BEEP_ASSETS,
    BOMB_PLANT_INITIATE_ASSET,
    BOMB_PLANT_QUIET_ASSET,
    BREACHPOINT_ASSET_PATHS,
    BUY_COUNTDOWN_ASSET,
    BUY_ITEM_HOVER_ASSETS,
    CASING_FAMILIES_BY_CALIBER_AND_SURFACE,
    DEATH_VOICE_ASSETS,
    DISTANT_ATTENUATION,
    FINAL_ROUND_STINGER_ASSET,
    FIRE_ATTENUATION,
    FIRE_DAMAGE_FAMILY,
    FIRE_EXTINGUISH_ASSET,
    FIRE_IGNITE_FAMILY,
    FIRE_LOOP_ASSET,
    FIRE_OUTRO_ASSET,
    FLASH_TINNITUS_ASSET,
    FOOTSTEP_ASSETS_BY_SURFACE,
    FOOTSTEP_ATTENUATION,
    FOOTSTEP_SOURCE_HEIGHT_METERS,
    HEADSHOT_ASSETS_BY_ARMOR,
    IMPACT_FLESH_ASSETS,
    MAP_AMBIENCE_ASSET,
    MAP_AMBIENCE_HANDLE,
    MAP_ZONE_AMBIENCE_HANDLE,
    MATCH_VICTORY_ASSET,
    MOLOTOV_IDLE_ASSET,
    MOVEMENT_AUDIO_SEQUENCE_TAG,
    MOVEMENT_AUDIO_SPEED_PERCENT,
    MUSIC_ACTION_START_ASSETS,
    MUSIC_ACTION_STOP_SEQUENCE_TAG,
    MUSIC_BOMB_PLANTED_ASSET,
    MUSIC_CONTEXT_HANDLE,
    MUSIC_MATCH_START_ASSET,
    MUSIC_RESULT_HANDLE,
    MUSIC_ROUND_LOST_ASSET,
    MUSIC_ROUND_START_ASSET,
    MUSIC_ROUND_WON_ASSET,
    PICKUP_ASSETS,
    PICKUP_DEFUSE_KIT_ASSET,
    PICKUP_FAMILIES,
    POSITIONAL_ATTENUATION,
    RADIO_BOMB_DEFUSED_ASSET,
    RADIO_BOMB_PLANTED_ASSET,
    RADIO_COUNTER_TERRORISTS_WIN_ASSET,
    RADIO_CUE_HANDLE,
    RADIO_TERRORISTS_WIN_ASSET,
    ROUND_STINGER_HANDLE,
    TICKS_PER_SECOND,
    TURN_NOTIFICATION_ASSET,
    UTILITY_AUDIO_PROFILES,
    UTILITY_AUDIO_SEQUENCE_TAG,
    UTILITY_SOURCE_HEIGHT_METERS,
    WEAPON_AUDIO_PROFILES,
    WEAPON_AUDIO_SEQUENCE_TAG,
    WEAPON_PROJECTILE_PRIORITY,
    WEAPON_SOURCE_HEIGHT_METERS,
    bomb_detonation_warning_ticks,
    listener_relative_position,
    sound_ticks,
    utility_audio_timing,
    weapon_fire_delay_ticks,
)
from ..games.breachpoint.bot import (
    ATTACK_STRATEGY_DIRECT,
    ATTACK_STRATEGY_FAKE,
    ATTACK_STRATEGY_SPLIT,
    ROLE_ANCHOR,
    ROLE_ENTRY,
    ROLE_LURKER,
    ROLE_OBJECTIVE,
    ROLE_ROTATOR,
    ROLE_SUPPORT,
)
from ..games.breachpoint.effects import AreaEffectState
from ..games.breachpoint.game import (
    BOMB_CARRIED,
    BOMB_DETONATION_SEQUENCE_TAG,
    BOMB_DROPPED,
    BOMB_PLANTED,
    BOMB_PLANTING,
    BUY_COUNTDOWN_SECONDS,
    BUY_COUNTDOWN_SEQUENCE_TAG,
    MATCH_DRAW,
    MATCH_OVERTIME,
    MATCH_REGULATION,
    MATCH_RESULT_DELAY_TICKS,
    MATCH_RESULT_SEQUENCE_TAG,
    PHASE_BUY,
    PHASE_COMBAT,
    REACTION_DEFUSE,
    REACTION_PLANT,
    REACTION_WATCHED_ENTRY,
    ROUND_TRANSITION_SEQUENCE_TAG,
    ROUND_TRANSITION_TICKS,
    TEAM_COUNTER_TERRORISTS,
    TEAM_TERRORISTS,
    WIN_DEFUSED,
    WIN_DETONATED,
    WIN_ELIMINATION,
    WIN_TIME,
    BreachPointGame,
    BreachPointOptions,
)
from ..games.breachpoint.ground import BuyTransaction, DroppedWeapon
from ..games.breachpoint.maps import (
    DUST_MAP,
    GridPoint,
    GridRect,
    TacticalMap,
    TacticalNode,
    TacticalSightline,
    _validate_map,
)
from ..games.breachpoint.player import BreachPointPlayer
from ..games.breachpoint.rules import OVERTIME_DRAW, STANDARD_RULES
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    start: bool = False,
    player_count: int = 4,
    bot_indexes: set[int] | None = None,
    touch_indexes: set[int] | None = None,
    finish_buy_phase: bool = True,
    **option_overrides,
) -> BreachPointGame:
    game = BreachPointGame(options=BreachPointOptions(**option_overrides))
    game._bot_coordinator.seed_strategy(2)
    game._gameplay_rng.seed(2)
    game._spatial_rng.seed(2)
    game.setup_keybinds()
    bot_indexes = bot_indexes or set()
    touch_indexes = touch_indexes or set()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if index in bot_indexes:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if index in touch_indexes:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
        if finish_buy_phase:
            complete_buy_phase(game)
        game.flush_menus()
    return game


def tactical_player(game: BreachPointGame, index: int) -> BreachPointPlayer:
    player = game.players[index]
    assert isinstance(player, BreachPointPlayer)
    return player


def spoken_text(game: BreachPointGame, index: int) -> list[str]:
    user = game.get_user(game.players[index])
    assert isinstance(user, MockUser)
    return user.get_spoken_messages()


def turn_menu_ids(game: BreachPointGame, index: int) -> list[str | None]:
    user = game.get_user(game.players[index])
    assert isinstance(user, MockUser)
    return [item.id for item in user.menus["turn_menu"]["items"]]


def turn_menu_item(game: BreachPointGame, index: int, item_id: str):
    user = game.get_user(game.players[index])
    assert isinstance(user, MockUser)
    return next(
        item for item in user.menus["turn_menu"]["items"] if item.id == item_id
    )


def last_turn_menu_message(game: BreachPointGame, index: int):
    user = game.get_user(game.players[index])
    assert isinstance(user, MockUser)
    return next(
        message
        for message in reversed(user.messages)
        if message.type == "show_menu"
        and message.data.get("menu_id") == "turn_menu"
    )


def clear_spoken(game: BreachPointGame) -> None:
    for player in game.players:
        user = game.get_user(player)
        if isinstance(user, MockUser):
            user.clear_messages()


def start_activation(game: BreachPointGame, player: BreachPointPlayer) -> None:
    game.current_player = player
    game._start_activation(player)


def complete_timed_action(game: BreachPointGame, tag: str) -> None:
    """Advance one measured audio action without giving bots another action."""

    for _ in range(500):
        if not game.has_active_sequence(tag=tag):
            return
        game.process_audio_automations()
        game.process_scheduled_sounds()
        game.process_sequences()
    raise AssertionError(f"Timed audio action did not complete: {tag}")


def complete_movement(game: BreachPointGame) -> None:
    complete_timed_action(game, MOVEMENT_AUDIO_SEQUENCE_TAG)


def complete_utility(game: BreachPointGame) -> None:
    complete_timed_action(game, UTILITY_AUDIO_SEQUENCE_TAG)


def complete_weapon_fire(game: BreachPointGame) -> None:
    complete_timed_action(game, WEAPON_AUDIO_SEQUENCE_TAG)


def complete_round_transition(game: BreachPointGame) -> None:
    complete_timed_action(game, ROUND_TRANSITION_SEQUENCE_TAG)


def complete_buy_countdown(game: BreachPointGame) -> None:
    complete_timed_action(game, BUY_COUNTDOWN_SEQUENCE_TAG)


def complete_match_result(game: BreachPointGame) -> None:
    complete_timed_action(game, MATCH_RESULT_SEQUENCE_TAG)


def complete_round_or_match_transition(game: BreachPointGame) -> None:
    if game.has_active_sequence(tag=MATCH_RESULT_SEQUENCE_TAG):
        complete_match_result(game)
    else:
        complete_round_transition(game)


def bot_target_nodes(
    game: BreachPointGame, player: BreachPointPlayer
) -> tuple[str, ...]:
    return game._bot_coordinator.target_nodes(game, player)


def bot_path_step(
    game: BreachPointGame,
    player: BreachPointPlayer,
    target_nodes: tuple[str, ...],
) -> str | None:
    return game._bot_coordinator.shortest_path_step(game, player, target_nodes)


def complete_buy_phase(game: BreachPointGame) -> None:
    while game.phase == PHASE_BUY:
        if game.has_active_sequence(tag=BUY_COUNTDOWN_SEQUENCE_TAG):
            complete_buy_countdown(game)
            continue
        buyer = game.current_player
        assert isinstance(buyer, BreachPointPlayer)
        game.execute_action(buyer, "finish_buy")


def set_area_effect(
    game: BreachPointGame,
    utility: UtilityProfile,
    node_id: str,
    *,
    expiration: int | None = None,
    known_team_indexes: list[int] | None = None,
    source_player_id: str | None = None,
    affected_player_rounds: dict[str, int] | None = None,
) -> AreaEffectState:
    """Install one authoritative area effect for a focused scenario."""

    state = AreaEffectState(
        effect=utility.effect,
        utility_id=utility.id,
        node_id=node_id,
        source_player_id=source_player_id or tactical_player(game, 0).id,
        expires_at_tactical_round=(
            expiration
            if expiration is not None
            else game.tactical_round + utility.duration_tactical_rounds
        ),
        known_team_indexes=list(known_team_indexes or []),
        affected_player_rounds=dict(affected_player_rounds or {}),
    )
    game.area_effects = [
        existing
        for existing in game.area_effects
        if (existing.effect, existing.node_id) != (state.effect, state.node_id)
    ]
    game.area_effects.append(state)
    return state


def test_registration_metadata_and_defaults() -> None:
    assert GameRegistry.get("breachpoint") is BreachPointGame
    assert BreachPointGame.get_name() == "Breach Point"
    assert BreachPointGame.get_type() == "breachpoint"
    assert BreachPointGame.get_category() == "board"
    assert BreachPointGame.get_min_players() == 4
    assert BreachPointGame.get_max_players() == 10
    assert BreachPointGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]
    options = BreachPointOptions()
    assert options.match_format == "mr12"
    assert options.overtime_mode == "mr3"
    assert STANDARD_RULES.weapon_pickup_cost == 1


def test_arsenal_and_economy_profiles_are_side_specific_and_data_driven() -> None:
    assert get_default_sidearm(TEAM_TERRORISTS) is GLOCK
    assert get_default_sidearm(TEAM_COUNTER_TERRORISTS) is USP_S
    assert get_purchasable_weapons(TEAM_TERRORISTS) == (
        DESERT_EAGLE,
        MAC10,
        NOVA,
        GALIL_AR,
        SSG08,
        AK47,
        AWP,
    )
    assert get_purchasable_weapons(TEAM_COUNTER_TERRORISTS) == (
        DESERT_EAGLE,
        NOVA,
        MP9,
        FAMAS,
        SSG08,
        M4,
        AWP,
    )
    assert get_purchasable_weapons(
        TEAM_TERRORISTS,
        WEAPON_SLOT_SIDEARM,
    ) == (DESERT_EAGLE,)
    assert get_purchasable_weapons(
        TEAM_COUNTER_TERRORISTS,
        WEAPON_SLOT_PRIMARY,
    ) == (NOVA, MP9, FAMAS, SSG08, M4, AWP)
    assert get_purchasable_weapons(TEAM_TERRORISTS, "invalid") == ()
    assert get_purchasable_utilities(TEAM_TERRORISTS) == (
        SMOKE_GRENADE,
        FLASHBANG,
        HE_GRENADE,
        MOLOTOV,
    )
    assert get_purchasable_utilities(TEAM_COUNTER_TERRORISTS) == (
        SMOKE_GRENADE,
        FLASHBANG,
        HE_GRENADE,
        INCENDIARY_GRENADE,
    )
    assert get_purchasable_equipment(TEAM_TERRORISTS) == ()
    assert get_purchasable_equipment(TEAM_COUNTER_TERRORISTS) == (DEFUSE_KIT,)
    assert GLOCK.rounds_per_attack == 3
    assert GLOCK.hits_by_range == (2, 1)
    assert GLOCK.damage_by_range == (38, 30)
    assert GLOCK.shots_per_activation == 2
    assert GLOCK.followup_damage_percent == 75
    assert GLOCK.hold_action_point_cost == 1
    assert GLOCK.reaction_damage_percent == 75
    assert USP_S.shots_per_activation == 2
    assert USP_S.reaction_damage_percent == 75
    assert DESERT_EAGLE.slot == WEAPON_SLOT_SIDEARM
    assert DESERT_EAGLE.allowed_sides == (
        TEAM_TERRORISTS,
        TEAM_COUNTER_TERRORISTS,
    )
    assert DESERT_EAGLE.cost == STANDARD_ECONOMY.starting_cash - 100
    assert DESERT_EAGLE.max_range == 2
    assert DESERT_EAGLE.shots_per_activation == 1
    assert DESERT_EAGLE.followup_damage_percent == 70
    assert DESERT_EAGLE.damage_by_range == (72, 58, 44)
    assert DESERT_EAGLE.armor_reduction_percent == 7
    assert MAC10.allowed_sides == (TEAM_TERRORISTS,)
    assert MAC10.cost == 1050
    assert MAC10.max_range == 1
    assert MAC10.damage_by_range == (76, 36)
    assert MAC10.shots_per_activation == 2
    assert MAC10.followup_damage_percent == 55
    assert MAC10.reaction_damage_percent == 50
    assert MAC10.purchase_role == PURCHASE_ROLE_ANTI_ECO
    assert MAC10.kill_reward == 600
    assert MP9.allowed_sides == (TEAM_COUNTER_TERRORISTS,)
    assert MP9.cost == 1250
    assert MP9.max_range == 1
    assert MP9.damage_by_range == (68, 48)
    assert MP9.shots_per_activation == 2
    assert MP9.followup_damage_percent == 60
    assert MP9.reaction_damage_percent == 65
    assert MP9.purchase_role == PURCHASE_ROLE_ANTI_ECO
    assert MP9.kill_reward == 600
    assert NOVA.allowed_sides == (
        TEAM_TERRORISTS,
        TEAM_COUNTER_TERRORISTS,
    )
    assert NOVA.cost == 1050
    assert NOVA.damage_by_range == (96, 38)
    assert NOVA.magazine_capacity == 8
    assert NOVA.reserve_units == 16
    assert NOVA.reload_units_per_action == 2
    assert not NOVA.discard_loaded_rounds_on_reload
    assert NOVA.kill_reward == 900
    assert GALIL_AR.allowed_sides == (TEAM_TERRORISTS,)
    assert GALIL_AR.cost == 1800
    assert GALIL_AR.max_range == 2
    assert GALIL_AR.damage_by_range == (74, 56, 34)
    assert GALIL_AR.shots_per_activation == 2
    assert not GALIL_AR.can_repeat_target
    assert GALIL_AR.followup_damage_percent == 55
    assert GALIL_AR.reaction_damage_percent == 65
    assert GALIL_AR.purchase_role == PURCHASE_ROLE_BUDGET
    assert FAMAS.allowed_sides == (TEAM_COUNTER_TERRORISTS,)
    assert FAMAS.cost == 1950
    assert FAMAS.max_range == 2
    assert FAMAS.rounds_per_attack == 3
    assert FAMAS.damage_by_range == (64, 50, 32)
    assert FAMAS.shots_per_activation == 2
    assert FAMAS.can_repeat_target
    assert FAMAS.followup_damage_percent == 60
    assert FAMAS.reaction_damage_percent == 65
    assert FAMAS.purchase_role == PURCHASE_ROLE_BUDGET
    assert SSG08.allowed_sides == (
        TEAM_TERRORISTS,
        TEAM_COUNTER_TERRORISTS,
    )
    assert SSG08.cost == 1700
    assert SSG08.max_range == 3
    assert SSG08.damage_by_range == (88, 84, 80, 74)
    assert SSG08.requires_aim
    assert SSG08.action_point_cost == 1
    assert SSG08.purchase_role == PURCHASE_ROLE_PRECISION
    assert AK47.rounds_per_attack == 12
    assert AK47.shots_per_activation == 1
    assert AK47.followup_damage_percent == 65
    assert AK47.reaction_damage_percent == 75
    assert AK47.purchase_role == PURCHASE_ROLE_STANDARD
    assert M4.damage_by_range == tuple(sorted(M4.damage_by_range, reverse=True))
    assert M4.followup_damage_percent == 65
    assert M4.hold_action_point_cost == 1
    assert M4.reaction_damage_percent == 75
    assert M4.can_repeat_target
    assert AWP.minimum_hits_after_evasion == 1
    assert AWP.reaction_damage_percent == 100
    assert AWP.purchase_role == PURCHASE_ROLE_PRECISION
    assert AWP.reserve_units == 2
    assert FLASHBANG.affects_thrower is False
    assert HE_GRENADE.damage == 45
    assert MOLOTOV.effect == UTILITY_EFFECT_FIRE
    assert INCENDIARY_GRENADE.cost == 500
    assert STANDARD_RULES.allow_contested_entry
    assert STANDARD_RULES.disengage_cost == STANDARD_RULES.action_points_per_activation
    assert STANDARD_RULES.maximum_utility_items == 4
    assert STANDARD_ECONOMY.maximum_armor == 100
    assert STANDARD_ECONOMY.starting_cash == 800
    assert STANDARD_ECONOMY.overtime_cash == 10_000
    assert STANDARD_ECONOMY.initial_loss_count == 1
    assert STANDARD_ECONOMY.loss_reward(1) == 1900
    assert STANDARD_ECONOMY.loss_reward(99) == 3400
    assert STANDARD_ECONOMY.win_reward(WIN_DEFUSED) == 3500
    assert STANDARD_ECONOMY.win_reward(WIN_DETONATED) == 3500
    assert STANDARD_ECONOMY.planter_reward == 300
    assert STANDARD_ECONOMY.defuser_reward == 300


def test_buy_phase_is_sequential_private_and_blocks_combat() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    assert game.phase == PHASE_BUY
    assert game.current_player is terrorist
    assert terrorist.cash == game.economy.starting_cash
    assert terrorist.action_points == 0
    assert game._is_move_enabled(terrorist, action_id="move_mid") == (
        "breachpoint-error-buy-phase-active"
    )

    game.execute_action(terrorist, "buy_armor")
    assert terrorist.armor == game.economy.maximum_armor
    assert terrorist.cash == game.economy.starting_cash - game.economy.armor_cost
    game.execute_action(terrorist, "buy_weapon_m4")
    assert terrorist.primary_weapon_id == ""
    game.execute_action(terrorist, "finish_buy")

    assert game.current_player is defender
    assert game.buy_ready_player_ids == [terrorist.id]
    assert any("Player1 is ready" in text for text in spoken_text(game, 1))
    assert all("$150" not in text for text in spoken_text(game, 1))

    complete_buy_phase(game)
    assert game.phase == PHASE_COMBAT
    assert game.current_player is terrorist
    assert terrorist.action_points == game.rules.action_points_per_activation


def test_buy_menu_uses_cs_categories_numeric_sequences_and_explicit_focus() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    user = game.get_user(buyer)
    assert isinstance(user, MockUser)

    assert turn_menu_ids(game, 0)[:11] == [
        "buy_menu_summary",
        "buy_menu_teammates",
        "buy_menu_category_equipment",
        "buy_menu_category_pistols",
        "buy_menu_category_mid_tier",
        "buy_menu_category_rifles",
        "buy_menu_category_grenades",
        "buy_menu_ground_weapons",
        "buy_menu_refunds",
        "buy_menu_donation",
        "finish_buy",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_summary"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "2"})
    assert turn_menu_ids(game, 0) == [
        "buy_weapon_desert_eagle",
        "buy_menu_back",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_weapon_desert_eagle"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "1"})
    assert buyer.sidearm_weapon_id == DESERT_EAGLE.id
    assert buyer.cash == game.economy.starting_cash - DESERT_EAGLE.cost
    assert last_turn_menu_message(game, 0).data["selection_id"] is None

    user.clear_messages()
    game.refresh_menus(buyer)
    game.flush_menus()
    assert last_turn_menu_message(game, 0).data["selection_id"] is None


def test_purchasable_buy_rows_have_stable_navigation_sounds() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_menu_category_rifles")
    game.flush_menus()

    item_ids = [
        action_id
        for action_id in turn_menu_ids(game, 0)
        if action_id and action_id.startswith("buy_weapon_")
    ]
    item_sounds = [
        turn_menu_item(game, 0, action_id).sound for action_id in item_ids
    ]
    assert item_sounds
    assert all(sound in BUY_ITEM_HOVER_ASSETS for sound in item_sounds)
    assert turn_menu_item(game, 0, "buy_menu_back").sound is None

    first_action = game.find_action(buyer, item_ids[0])
    assert first_action is not None
    first_sound = game.resolve_action(buyer, first_action).sound
    game.refresh_menus(buyer)
    game.flush_menus()
    assert game.resolve_action(buyer, first_action).sound == first_sound


def test_buy_menu_back_restores_the_parent_item_that_opened_each_submenu() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.handle_event(buyer, {"type": "keybind", "key": "4"})
    assert turn_menu_ids(game, 0)[0] == "buy_weapon_galil_ar"
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_weapon_galil_ar"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_category_rifles"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "2"})
    game.handle_event(buyer, {"type": "keybind", "key": "1"})
    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_category_pistols"
    )

    game.execute_action(buyer, "buy_menu_ground_weapons")
    game.flush_menus()
    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_ground_weapons"
    )

    game.execute_action(buyer, "buy_menu_refunds")
    game.flush_menus()
    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_refunds"
    )


def test_buy_menu_back_restores_nested_donation_openers() -> None:
    game = make_game(start=True, player_count=6, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_menu_donation")
    game.execute_action(buyer, "buy_menu_donation_target_p5")
    game.execute_action(buyer, "buy_menu_category_rifles")
    game.flush_menus()

    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_category_rifles"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_donation_target_p5"
    )

    game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_donation"
    )


def test_buy_menu_back_skips_the_auto_selected_donation_recipient() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_menu_donation")
    game.flush_menus()
    assert "buy_menu_donation_target_p3" not in turn_menu_ids(game, 0)

    game.handle_event(buyer, {"type": "keybind", "key": "x"})

    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_donation"
    )


def test_buy_ground_weapons_are_isolated_in_their_own_submenu() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_weapon_desert_eagle")
    game.execute_action(buyer, "buy_menu_ground_weapons")
    game.flush_menus()

    assert turn_menu_ids(game, 0) == ["pick_up_weapon_1", "buy_menu_back"]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "pick_up_weapon_1"
    )
    assert "refund_weapon_desert_eagle" not in turn_menu_ids(game, 0)

    game.execute_action(buyer, "pick_up_weapon_1")
    game.flush_menus()

    assert turn_menu_ids(game, 0) == ["pick_up_weapon_2", "buy_menu_back"]
    assert last_turn_menu_message(game, 0).data["selection_id"] is None


def test_buy_summary_and_teammate_info_reveal_only_same_team_loadouts() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    teammate = tactical_player(game, 2)
    enemy = tactical_player(game, 1)
    user = game.get_user(buyer)
    assert isinstance(user, MockUser)
    teammate.cash = 4321
    enemy.cash = 9876

    game.handle_event(
        buyer,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "buy_menu_summary",
        },
    )
    summary_lines = [item.text for item in user.menus["status_box"]["items"]]
    assert any("Money: $800" in line for line in summary_lines)
    assert any("Sidearm: Glock" in line for line in summary_lines)

    game.handle_event(
        buyer,
        {
            "type": "menu",
            "menu_id": "status_box",
            "selection_id": "status_box:line:0",
        },
    )
    game.handle_event(
        buyer,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "buy_menu_teammates",
        },
    )
    teammate_lines = [item.text for item in user.menus["status_box"]["items"]]
    assert any(teammate.name in line and "$4,321" in line for line in teammate_lines)
    assert all(enemy.name not in line and "$9876" not in line for line in teammate_lines)


def test_refund_submenu_retains_focus_and_shows_empty_state() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    game.execute_action(buyer, "buy_weapon_desert_eagle")
    game.execute_action(buyer, "buy_menu_refunds")
    game.flush_menus()

    assert turn_menu_ids(game, 0) == [
        "refund_weapon_desert_eagle",
        "buy_menu_back",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "refund_weapon_desert_eagle"
    )

    game.handle_event(
        buyer,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "refund_weapon_desert_eagle",
        },
    )
    assert turn_menu_ids(game, 0) == [
        "buy_menu_empty_refunds",
        "buy_menu_back",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] is None


def test_donation_auto_selects_single_teammate_and_locks_buyer_menu() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    recipient = tactical_player(game, 2)
    buyer.cash = AK47.cost

    game.execute_action(buyer, "buy_menu_donation")
    game.flush_menus()
    assert "buy_menu_donation_target_p3" not in turn_menu_ids(game, 0)
    assert turn_menu_ids(game, 0) == [
        "buy_menu_category_pistols",
        "buy_menu_category_mid_tier",
        "buy_menu_category_rifles",
        "buy_menu_back",
    ]

    game.execute_action(buyer, "buy_menu_category_rifles")
    game.execute_action(buyer, game._donate_weapon_action_id(AK47, recipient))
    game.flush_menus()

    assert game.current_player is recipient
    assert turn_menu_ids(game, 0) == [
        "buy_menu_summary",
        "buy_menu_waiting",
    ]
    assert turn_menu_ids(game, 2)[:2] == [
        "accept_weapon_donation",
        "decline_weapon_donation",
    ]
    assert game.resolve_action(
        buyer,
        game.find_action(buyer, "buy_menu_waiting"),
    ).enabled is False

    buyer_user = game.get_user(buyer)
    assert isinstance(buyer_user, MockUser)
    buyer_user.clear_messages()
    game.handle_event(
        recipient,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "accept_weapon_donation",
        },
    )
    assert recipient.primary_weapon_id == AK47.id
    assert game.current_player is buyer
    donor_repaint = last_turn_menu_message(game, 0)
    assert donor_repaint.data["selection_id"] is None


def test_donation_menu_lists_multiple_eligible_teammates_before_categories() -> None:
    game = make_game(start=True, player_count=6, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_menu_donation")
    game.flush_menus()

    assert turn_menu_ids(game, 0) == [
        "buy_menu_donation_target_p3",
        "buy_menu_donation_target_p5",
        "buy_menu_back",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "buy_menu_donation_target_p3"
    )


def test_first_round_buy_music_uses_the_same_looping_context_as_later_rounds() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)

    initial_music = next(
        message
        for message in user.messages
        if message.type == "play_music"
        and message.data.get("name") == MUSIC_MATCH_START_ASSET
    )
    assert initial_music.data.get("looping") is True
    assert initial_music.data.get("handle") == MUSIC_CONTEXT_HANDLE
    assert any(
        state.kind == "music"
        and state.handle == MUSIC_CONTEXT_HANDLE
        and state.asset == MUSIC_MATCH_START_ASSET
        and state.loop is True
        for state in game.active_audio.values()
    )


def test_buy_phase_ends_with_exactly_three_global_countdown_beeps() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)

    while not game.has_active_sequence(tag=BUY_COUNTDOWN_SEQUENCE_TAG):
        buyer = game.current_player
        assert isinstance(buyer, BreachPointPlayer)
        game.execute_action(buyer, "finish_buy")

    assert game.phase == PHASE_BUY
    wait_error = game._buy_turn_error(listener)
    assert wait_error == (
        "breachpoint-error-wait-buy-countdown",
        {"seconds": BUY_COUNTDOWN_SECONDS},
    )
    assert sum(
        message.type == "play_sound"
        and message.data.get("name") == BUY_COUNTDOWN_ASSET
        for message in user.messages
    ) == 1

    complete_buy_countdown(game)

    assert game.phase == PHASE_COMBAT
    assert sum(
        message.type == "play_sound"
        and message.data.get("name") == BUY_COUNTDOWN_ASSET
        for message in user.messages
    ) == 3


def test_bot_avoids_wasteful_duplicate_even_when_direct_rebuy_is_legal() -> None:
    game = make_game(
        start=True,
        bot_indexes={0},
        finish_buy_phase=False,
    )
    bot = tactical_player(game, 0)
    bot.primary_weapon_id = AK47.id
    bot.equipped_weapon_id = AK47.id
    bot.cash = game.economy.maximum_cash
    game._set_full_weapon_ammunition(bot, AK47)

    chosen = game._bot_coordinator.buy_action(game, bot)
    cash_before = bot.cash
    drops_before = list(game.dropped_weapons)
    game.execute_action(bot, "buy_weapon_ak47")

    assert chosen != "buy_weapon_ak47"
    assert bot.cash == cash_before - AK47.cost
    assert bot.primary_weapon_id == AK47.id
    assert len(game.dropped_weapons) == len(drops_before) + 1
    assert game.dropped_weapons[-1].weapon_id == AK47.id


def test_purchase_audio_matches_item_type_and_remains_private() -> None:
    weapon_game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(weapon_game, 0)
    observer = tactical_player(weapon_game, 1)
    buyer_user = weapon_game.get_user(buyer)
    observer_user = weapon_game.get_user(observer)
    assert isinstance(buyer_user, MockUser)
    assert isinstance(observer_user, MockUser)
    buyer_user.clear_messages()
    observer_user.clear_messages()

    weapon_game.execute_action(buyer, "buy_weapon_desert_eagle")

    purchase_chain = next(
        message
        for message in buyer_user.messages
        if message.type == "play_sound"
        and len(message.data.get("segments", [])) == 2
        and message.data["segments"][0]["asset"] in PICKUP_ASSETS["weapon"]
    )
    assert purchase_chain.data["segments"][1]["asset"] in PICKUP_ASSETS["ammo"]
    purchase_assets = {
        segment["asset"] for segment in purchase_chain.data["segments"]
    }
    assert not any(
        message.type == "play_sound"
        and (
            message.data.get("name") in purchase_assets
            or any(
                segment["asset"] in purchase_assets
                for segment in message.data.get("segments", [])
            )
        )
        for message in observer_user.messages
    )

    utility_game = make_game(start=True, finish_buy_phase=False)
    utility_buyer = tactical_player(utility_game, 0)
    utility_user = utility_game.get_user(utility_buyer)
    assert isinstance(utility_user, MockUser)
    utility_user.clear_messages()
    utility_game.execute_action(utility_buyer, "buy_utility_smoke")
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == PICKUP_FAMILIES["grenade"]
        for message in utility_user.messages
    )

    equipment_game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(equipment_game, 0)
    defender = tactical_player(equipment_game, 1)
    equipment_game.execute_action(terrorist, "finish_buy")
    defender_user = equipment_game.get_user(defender)
    assert isinstance(defender_user, MockUser)
    defender_user.clear_messages()
    equipment_game.execute_action(defender, "buy_equipment_defuse_kit")
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == PICKUP_DEFUSE_KIT_ASSET
        for message in defender_user.messages
    )


def test_ammunition_profiles_scale_partial_attacks_without_inventing_rounds() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    full = game._preview_attack(target, AK47, 0)
    partial = game._preview_attack(
        target,
        AK47,
        0,
        ammunition_used=6,
    )
    empty = game._preview_attack(
        target,
        AK47,
        0,
        ammunition_used=0,
    )

    assert (full.rounds_fired, full.rounds_on_target, full.health_damage) == (
        12,
        4,
        92,
    )
    assert (partial.rounds_fired, partial.rounds_on_target, partial.health_damage) == (
        6,
        2,
        46,
    )
    assert (empty.rounds_fired, empty.rounds_on_target, empty.health_damage) == (
        0,
        0,
        0,
    )


def test_magazine_attacks_consume_ammunition_and_reload_discards_the_old_magazine() -> (
    None
):
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.primary_weapon_id = AK47.id
    shooter.equipped_weapon_id = AK47.id
    game._set_full_weapon_ammunition(shooter, AK47)
    shooter.position_id = "mid"
    target.position_id = "mid"
    start_activation(game, shooter)

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)

    assert shooter.weapon_magazine_ammo[AK47.id] == 18
    assert shooter.weapon_reserve_units[AK47.id] == AK47.reserve_units
    assert shooter.action_points == 1
    assert game._is_reload_enabled(shooter) is None

    game.execute_action(shooter, "reload")

    assert shooter.weapon_magazine_ammo[AK47.id] == AK47.magazine_capacity
    assert shooter.weapon_reserve_units[AK47.id] == AK47.reserve_units - 1
    assert shooter.action_points == 0
    assert any(
        "discarding 18 loaded rounds" in message for message in spoken_text(game, 0)
    )


def test_reload_uses_personal_team_and_shared_enemy_vision_perspectives() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    visible_enemy = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    concealed_enemy = tactical_player(game, 3)
    shooter.primary_weapon_id = AK47.id
    shooter.equipped_weapon_id = AK47.id
    shooter.weapon_magazine_ammo[AK47.id] = 6
    shooter.weapon_reserve_units[AK47.id] = 1
    shooter.position_id = "t_spawn"
    visible_enemy.position_id = "ct_spawn"
    teammate.position_id = "t_spawn"
    concealed_enemy.position_id = "ct_spawn"
    start_activation(game, shooter)
    clear_spoken(game)

    game.execute_action(shooter, "reload")

    assert any("You reload AK-47" in message for message in spoken_text(game, 0))
    assert any("Player1 reloads AK-47" in message for message in spoken_text(game, 2))
    assert all("reloads AK-47" not in message for message in spoken_text(game, 1))
    assert all("reloads AK-47" not in message for message in spoken_text(game, 3))

    shooter.weapon_magazine_ammo[AK47.id] = 6
    shooter.weapon_reserve_units[AK47.id] = 1
    shooter.position_id = visible_enemy.position_id = "mid"
    start_activation(game, shooter)
    clear_spoken(game)
    game.execute_action(shooter, "reload")

    assert any("Player1 reloads AK-47" in message for message in spoken_text(game, 1))
    assert any("Player1 reloads AK-47" in message for message in spoken_text(game, 3))


def test_shell_reload_keeps_loaded_rounds_and_loads_bounded_individual_shells() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    shooter.primary_weapon_id = NOVA.id
    shooter.equipped_weapon_id = NOVA.id
    shooter.weapon_magazine_ammo[NOVA.id] = 5
    shooter.weapon_reserve_units[NOVA.id] = 3
    start_activation(game, shooter)

    game.execute_action(shooter, "reload")

    assert shooter.weapon_magazine_ammo[NOVA.id] == 7
    assert shooter.weapon_reserve_units[NOVA.id] == 1
    assert shooter.action_points == 1
    assert any("load 2 shells" in message for message in spoken_text(game, 0))

    game.execute_action(shooter, "reload")

    assert shooter.weapon_magazine_ammo[NOVA.id] == NOVA.magazine_capacity
    assert shooter.weapon_reserve_units[NOVA.id] == 0
    assert shooter.action_points == 0


def test_empty_weapon_requires_reload_and_cannot_prepare_a_reaction() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.primary_weapon_id = SSG08.id
    shooter.equipped_weapon_id = SSG08.id
    shooter.weapon_magazine_ammo[SSG08.id] = 0
    shooter.weapon_reserve_units[SSG08.id] = 1
    shooter.position_id = "mid"
    target.position_id = "mid"
    start_activation(game, shooter)

    shoot_error = game._is_shoot_enabled(
        shooter,
        action_id=f"shoot_{target.id}",
    )
    hold_error = game._is_hold_angle_enabled(
        shooter,
        action_id="hold_angle_mid",
    )

    assert shoot_error == (
        "breachpoint-error-weapon-empty",
        {"weapon": "SSG 08"},
    )
    assert hold_error == shoot_error
    assert game._is_reload_enabled(shooter) is None

    game.execute_action(shooter, "reload")

    assert shooter.weapon_magazine_ammo[SSG08.id] == SSG08.magazine_capacity
    assert shooter.weapon_reserve_units[SSG08.id] == 0
    assert any(
        "insert a fresh magazine into the empty SSG 08" in message
        for message in spoken_text(game, 0)
    )


def test_reload_reports_empty_reserves_without_spending_action_points() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    shooter.primary_weapon_id = NOVA.id
    shooter.equipped_weapon_id = NOVA.id
    shooter.weapon_magazine_ammo[NOVA.id] = 4
    shooter.weapon_reserve_units[NOVA.id] = 0
    start_activation(game, shooter)

    assert game._is_reload_enabled(shooter) == (
        "breachpoint-error-no-reserve-ammo",
        {"weapon": "Nova"},
    )

    game.execute_action(shooter, "reload")

    assert shooter.action_points == game.rules.action_points_per_activation
    assert shooter.weapon_magazine_ammo[NOVA.id] == 4

    shooter.weapon_magazine_ammo[NOVA.id] = 0
    no_ammunition = (
        "breachpoint-error-no-ammunition",
        {"weapon": "Nova"},
    )
    assert game._is_reload_enabled(shooter) == no_ammunition
    assert (
        game._is_hold_angle_enabled(
            shooter,
            action_id="hold_angle_mid",
        )
        == no_ammunition
    )

    target = tactical_player(game, 1)
    shooter.position_id = target.position_id = "mid"
    assert (
        game._is_shoot_enabled(
            shooter,
            action_id=f"shoot_{target.id}",
        )
        == no_ammunition
    )


def test_nova_and_ssg08_keep_distinct_close_and_long_range_roles() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    nova_close = game._preview_attack(target, NOVA, 0)
    nova_far = game._preview_attack(target, NOVA, 1)
    ssg_close = game._preview_attack(target, SSG08, 0)
    ssg_far = game._preview_attack(target, SSG08, 3)

    assert (nova_close.rounds_fired, nova_close.rounds_on_target) == (9, 6)
    assert nova_close.health_damage == 96
    assert nova_far.health_damage == 38
    assert ssg_close.health_damage == 88
    assert ssg_far.health_damage == 74

    target.armor = game.economy.maximum_armor
    armored_nova = game._preview_attack(target, NOVA, 0)
    armored_ssg = game._preview_attack(target, SSG08, 3)

    assert (armored_nova.health_damage, armored_nova.armor_absorbed) == (58, 38)
    assert (armored_ssg.health_damage, armored_ssg.armor_absorbed) == (67, 7)


def test_nova_evasion_removes_pellets_but_cannot_erase_the_close_attack() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)
    target.guard_points = game.rules.maximum_evasion_points

    outcome = game._preview_attack(target, NOVA, 0)

    assert outcome.rounds_on_target == 6
    assert outcome.rounds_evaded == 2
    assert outcome.health_damage == 64
    assert not outcome.fully_evaded


def test_weapon_purchase_and_round_setup_refill_only_owned_weapons() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = GALIL_AR.cost + NOVA.cost

    game.execute_action(buyer, "buy_weapon_nova")
    assert buyer.weapon_magazine_ammo[NOVA.id] == NOVA.magazine_capacity
    assert buyer.weapon_reserve_units[NOVA.id] == NOVA.reserve_units

    game.execute_action(buyer, "buy_weapon_galil_ar")
    assert NOVA.id not in buyer.weapon_magazine_ammo
    assert NOVA.id not in buyer.weapon_reserve_units
    buyer.weapon_magazine_ammo[GALIL_AR.id] = 1
    buyer.weapon_reserve_units[GALIL_AR.id] = 0

    game._prepare_combat_round()

    assert buyer.weapon_magazine_ammo == {
        GLOCK.id: GLOCK.magazine_capacity,
        GALIL_AR.id: GALIL_AR.magazine_capacity,
    }
    assert buyer.weapon_reserve_units == {
        GLOCK.id: GLOCK.reserve_units,
        GALIL_AR.id: GALIL_AR.reserve_units,
    }


def test_buying_side_rifles_and_armor_updates_private_loadouts() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    terrorist.cash = AK47.cost + game.economy.armor_cost

    game.execute_action(terrorist, "buy_weapon_ak47")
    game.execute_action(terrorist, "buy_armor")

    assert terrorist.primary_weapon_id == AK47.id
    assert terrorist.equipped_weapon_id == AK47.id
    assert terrorist.armor == game.economy.maximum_armor
    assert terrorist.cash == 0
    assert (
        game._is_buy_weapon_enabled(terrorist, action_id="buy_weapon_ak47")
        == (
            "breachpoint-error-not-enough-cash",
            {"cost": AK47.cost, "cash": 0},
        )
    )


def test_upgraded_sidearms_use_an_independent_slot_for_both_sides() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    assert terrorist.sidearm_weapon_id == GLOCK.id
    terrorist.cash = AK47.cost + DESERT_EAGLE.cost

    game.execute_action(terrorist, "buy_weapon_ak47")
    game.execute_action(terrorist, "buy_weapon_desert_eagle")

    assert terrorist.primary_weapon_id == AK47.id
    assert terrorist.sidearm_weapon_id == DESERT_EAGLE.id
    assert terrorist.equipped_weapon_id == DESERT_EAGLE.id
    assert terrorist.cash == 0
    assert game._is_buy_weapon_enabled(
        terrorist,
        action_id="buy_weapon_desert_eagle",
    ) == (
        "breachpoint-error-not-enough-cash",
        {"cost": DESERT_EAGLE.cost, "cash": terrorist.cash},
    )

    game.execute_action(terrorist, "finish_buy")
    defender = tactical_player(game, 1)
    assert defender.sidearm_weapon_id == USP_S.id
    defender.cash = DESERT_EAGLE.cost
    game.execute_action(defender, "buy_weapon_desert_eagle")

    assert defender.primary_weapon_id == ""
    assert defender.sidearm_weapon_id == DESERT_EAGLE.id
    assert defender.equipped_weapon_id == DESERT_EAGLE.id


def test_elimination_drops_the_primary_with_its_remaining_ammunition() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    node = game._node("mid")
    assert node is not None
    shooter.position_id = target.position_id = node.id
    target.grid_x = node.anchor.x
    target.grid_y = node.anchor.y
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    target.weapon_magazine_ammo[M4.id] = 7
    target.weapon_reserve_units[M4.id] = 2
    target.health = 1

    assert game._perform_attack(
        shooter,
        target,
        GLOCK,
        damage_percent=100,
        resume_mode="normal",
    )
    complete_weapon_fire(game)

    assert target.eliminated
    assert target.primary_weapon_id == ""
    assert M4.id not in target.weapon_magazine_ammo
    assert M4.id not in target.weapon_reserve_units
    assert game.dropped_weapons == [
        DroppedWeapon(
            drop_id=1,
            weapon_id=M4.id,
            node_id=node.id,
            grid_x=node.anchor.x,
            grid_y=node.anchor.y,
            magazine_ammo=7,
            reserve_units=2,
        )
    ]
    assert game.next_dropped_weapon_id == 2
    assert any("You drop M4 at Mid" in message for message in spoken_text(game, 1))
    assert any("Player2 drops M4 at Mid" in message for message in spoken_text(game, 3))


def test_same_area_kill_leaves_pickup_and_end_turn_choices_with_remaining_ap() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.position_id = target.position_id = "mid"
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.health = 1
    start_activation(game, shooter)

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)
    game.flush_menus()

    assert target.eliminated
    assert game.current_player is shooter
    assert shooter.action_points == 1
    dropped_m4 = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == M4.id
    )
    pickup_action = game._dropped_weapon_action_id(dropped_m4)
    assert game._is_pick_up_weapon_enabled(shooter, action_id=pickup_action) is None
    assert game._is_end_turn_enabled(shooter) is None

    game.execute_action(shooter, pickup_action)

    assert shooter.primary_weapon_id == M4.id
    assert shooter.action_points == 0
    assert game.current_player is not shooter


def test_final_elimination_waits_for_same_area_weapon_recovery_choice() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    shooter.position_id = target.position_id = "mid"
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.health = 1
    other_defender.eliminated = True
    other_defender.health = 0
    clear_spoken(game)

    assert game._perform_attack(
        shooter,
        target,
        GLOCK,
        damage_percent=100,
        resume_mode="normal",
    )
    complete_weapon_fire(game)

    dropped_m4 = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == M4.id
    )
    pickup_action = game._dropped_weapon_action_id(dropped_m4)
    assert game.round_recovery_player_id == shooter.id
    assert game.round_recovery_drop_ids == [dropped_m4.drop_id]
    assert game.pending_round_winner_side_index == TEAM_TERRORISTS
    assert game._squad_score(TEAM_TERRORISTS) == 0
    assert game.current_player is shooter
    assert game._is_pick_up_weapon_enabled(shooter, action_id=pickup_action) is None
    assert game._is_end_turn_enabled(shooter) is None
    assert game._is_move_hidden(shooter, action_id="move_t_spawn") == Visibility.HIDDEN

    game.flush_menus()
    assert turn_menu_ids(game, 0) == [
        pickup_action,
        "combat_menu_back",
        "end_turn",
    ]
    game.execute_action(shooter, pickup_action)

    assert shooter.primary_weapon_id == M4.id
    assert shooter.action_points == 0
    assert game.round_recovery_player_id == ""
    assert game._squad_score(TEAM_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_ELIMINATION
    assert game.has_active_sequence(tag=ROUND_TRANSITION_SEQUENCE_TAG)


def test_final_elimination_recovery_can_be_skipped_and_survives_restore() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    shooter.position_id = target.position_id = "mid"
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.eliminated = True
    target.health = 0
    other_defender.eliminated = True
    other_defender.health = 0

    assert game._finalize_eliminations(
        shooter,
        [target],
        source_name_key=GLOCK.name_key,
        kill_reward=GLOCK.kill_reward,
    )
    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_shooter = tactical_player(restored, 0)
    restored_shooter.reconnect_grace_ticks = 0

    assert restored.round_recovery_player_id == restored_shooter.id
    assert restored.current_player is restored_shooter
    assert restored._is_end_turn_enabled(restored_shooter) is None

    restored.flush_menus()
    restored.execute_action(restored_shooter, "end_turn")

    assert restored.round_recovery_player_id == ""
    assert restored._squad_score(TEAM_TERRORISTS) == 1
    assert restored.has_active_sequence(tag=ROUND_TRANSITION_SEQUENCE_TAG)
    assert any("skip weapon recovery" in message for message in spoken_text(restored, 0))


def test_match_point_elimination_waits_for_weapon_recovery_before_game_over() -> None:
    game = make_game(start=True, match_format="mr7")
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    winning_squad = game._squad_for_side(TEAM_TERRORISTS)
    game._team_manager.teams[winning_squad].total_score = (
        game.match_format.rounds_to_win - 1
    )
    shooter.position_id = target.position_id = "mid"
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.eliminated = True
    target.health = 0
    other_defender.eliminated = True
    other_defender.health = 0

    assert game._finalize_eliminations(
        shooter,
        [target],
        source_name_key=GLOCK.name_key,
        kill_reward=GLOCK.kill_reward,
    )

    assert game.round_recovery_player_id == shooter.id
    assert game._squad_score(winning_squad) == game.match_format.rounds_to_win - 1
    assert not game.has_active_sequence(tag=MATCH_RESULT_SEQUENCE_TAG)

    game.flush_menus()
    game.execute_action(shooter, "end_turn")

    assert game.round_recovery_player_id == ""
    assert game._squad_score(winning_squad) == game.match_format.rounds_to_win
    assert game.has_active_sequence(tag=MATCH_RESULT_SEQUENCE_TAG)
    assert game.status == "playing"


def test_final_elimination_without_pickup_ap_ends_round_immediately() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    shooter.position_id = target.position_id = "mid"
    shooter.action_points = 0
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.eliminated = True
    target.health = 0
    other_defender.eliminated = True
    other_defender.health = 0

    assert game._finalize_eliminations(
        shooter,
        [target],
        source_name_key=GLOCK.name_key,
        kill_reward=GLOCK.kill_reward,
    )

    assert game.round_recovery_player_id == ""
    assert game._squad_score(TEAM_TERRORISTS) == 1
    assert game.has_active_sequence(tag=ROUND_TRANSITION_SEQUENCE_TAG)


def test_death_drop_uses_a_purchased_sidearm_but_not_a_free_default() -> None:
    game = make_game(start=True)
    upgraded = tactical_player(game, 0)
    default_only = tactical_player(game, 2)
    upgraded.sidearm_weapon_id = DESERT_EAGLE.id
    upgraded.equipped_weapon_id = DESERT_EAGLE.id
    upgraded.weapon_magazine_ammo[DESERT_EAGLE.id] = 3
    upgraded.weapon_reserve_units[DESERT_EAGLE.id] = 1

    dropped_weapon = game._death_drop_weapon(upgraded)

    assert dropped_weapon is not None
    assert dropped_weapon.weapon_id == DESERT_EAGLE.id
    assert dropped_weapon.magazine_ammo == 3
    assert dropped_weapon.reserve_units == 1
    assert game._death_drop_weapon(default_only) is None
    assert [item.weapon_id for item in game.dropped_weapons] == [DESERT_EAGLE.id]


def test_cross_side_pickup_exchanges_slots_ammunition_and_action_points() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    defender.weapon_magazine_ammo[M4.id] = 9
    defender.weapon_reserve_units[M4.id] = 1
    start_activation(game, defender)
    point = game._player_grid_point(defender)
    dropped_ak = game._create_dropped_weapon(
        AK47,
        defender.position_id,
        point,
        magazine_ammo=5,
        reserve_units=2,
    )
    game.refresh_menus(defender)
    game.flush_menus()
    defender_user = game.get_user(defender)
    observer = tactical_player(game, 3)
    observer_user = game.get_user(observer)
    assert isinstance(defender_user, MockUser)
    assert isinstance(observer_user, MockUser)
    defender_user.clear_messages()
    observer_user.clear_messages()

    action_id = game._dropped_weapon_action_id(dropped_ak)
    game.execute_action(defender, action_id)

    assert defender.action_points == 1
    assert defender.primary_weapon_id == AK47.id
    assert defender.equipped_weapon_id == AK47.id
    assert defender.weapon_magazine_ammo == {
        USP_S.id: USP_S.magazine_capacity,
        AK47.id: 5,
    }
    assert defender.weapon_reserve_units == {
        USP_S.id: USP_S.reserve_units,
        AK47.id: 2,
    }
    assert game.dropped_weapons == [
        DroppedWeapon(
            drop_id=2,
            weapon_id=M4.id,
            node_id=defender.position_id,
            grid_x=point.x,
            grid_y=point.y,
            magazine_ammo=9,
            reserve_units=1,
        )
    ]
    assert any("exchange M4 for AK-47" in message for message in spoken_text(game, 1))
    assert any(
        "Player2 exchanges M4 for AK-47" in message for message in spoken_text(game, 3)
    )
    pickup_assets = {
        asset for item_kind in ("weapon", "ammo") for asset in PICKUP_ASSETS[item_kind]
    }
    for user in (defender_user, observer_user):
        pickup_chain = next(
            message
            for message in user.messages
            if message.type == "play_sound"
            and len(message.data.get("segments", [])) == 2
            and {
                segment["asset"] for segment in message.data["segments"]
            }.issubset(pickup_assets)
        )
        assert pickup_chain.data["segments"][0]["asset"] in PICKUP_ASSETS["weapon"]
        assert pickup_chain.data["segments"][1]["asset"] in PICKUP_ASSETS["ammo"]
    assert all(
        segment["position"] is None
        for segment in next(
            message
            for message in defender_user.messages
            if message.type == "play_sound"
            and len(message.data.get("segments", [])) == 2
            and message.data["segments"][0]["asset"] in PICKUP_ASSETS["weapon"]
        ).data["segments"]
    )
    assert all(
        segment["position"] is not None
        for segment in next(
            message
            for message in observer_user.messages
            if message.type == "play_sound"
            and len(message.data.get("segments", [])) == 2
            and message.data["segments"][0]["asset"] in PICKUP_ASSETS["weapon"]
        ).data["segments"]
    )
    assert not any("AK-47" in message for message in spoken_text(game, 0))

    state_before_stale_action = (
        defender.action_points,
        defender.primary_weapon_id,
        list(game.dropped_weapons),
    )
    game.execute_action(defender, action_id)
    assert (
        defender.action_points,
        defender.primary_weapon_id,
        game.dropped_weapons,
    ) == state_before_stale_action
    assert any("no longer available" in message for message in spoken_text(game, 1))


def test_round_setup_removes_ground_weapons_without_reusing_drop_ids() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    point = game._player_grid_point(player)
    game._create_dropped_weapon(
        AK47,
        player.position_id,
        point,
        magazine_ammo=1,
        reserve_units=0,
    )
    assert game.next_dropped_weapon_id == 2

    game._prepare_combat_round()

    assert game.dropped_weapons == []
    assert game.next_dropped_weapon_id == 2
    next_drop = game._create_dropped_weapon(
        M4,
        player.position_id,
        game._player_grid_point(player),
        magazine_ammo=1,
        reserve_units=0,
    )
    assert next_drop.drop_id == 2


def test_buying_a_different_primary_replaces_and_equips_the_old_primary() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    terrorist.cash = MAC10.cost + AK47.cost

    game.execute_action(terrorist, "buy_weapon_mac10")
    assert terrorist.primary_weapon_id == MAC10.id
    assert (
        game._is_buy_weapon_enabled(
            terrorist,
            action_id="buy_weapon_mac10",
        )
        is None
    )
    assert (
        game._is_buy_weapon_enabled(
            terrorist,
            action_id="buy_weapon_ak47",
        )
        is None
    )

    game.execute_action(terrorist, "buy_weapon_ak47")

    assert terrorist.primary_weapon_id == AK47.id
    assert terrorist.equipped_weapon_id == AK47.id
    assert terrorist.cash == 0


def test_buy_replacement_drops_and_keeps_current_turn_purchases_refundable() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = MAC10.cost + AK47.cost
    buyer_user = game.get_user(buyer)
    assert isinstance(buyer_user, MockUser)

    game.execute_action(buyer, "buy_weapon_mac10")
    buyer_user.clear_messages()
    game.execute_action(buyer, "buy_weapon_ak47")

    assert buyer.primary_weapon_id == AK47.id
    assert game.dropped_weapons == [
        DroppedWeapon(
            drop_id=1,
            weapon_id=MAC10.id,
            node_id=buyer.position_id,
            grid_x=game._player_grid_point(buyer).x,
            grid_y=game._player_grid_point(buyer).y,
            magazine_ammo=MAC10.magazine_capacity,
            reserve_units=MAC10.reserve_units,
        )
    ]
    assert game.buy_transactions == [
        BuyTransaction(
            buyer.id,
            "weapon",
            MAC10.id,
            MAC10.cost,
            dropped_weapon_id=1,
        ),
        BuyTransaction(buyer.id, "weapon", AK47.id, AK47.cost),
    ]
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == WEAPON_AUDIO_PROFILES[MAC10.id].drop_asset
        for message in buyer_user.messages
    )
    game.execute_action(buyer, "buy_menu_refunds")
    assert game._is_refund_purchase_hidden(
        buyer,
        action_id="refund_weapon_mac10",
    ) == Visibility.VISIBLE

    game.execute_action(buyer, "refund_weapon_mac10")
    assert game.dropped_weapons == []
    assert buyer.primary_weapon_id == AK47.id
    assert buyer.cash == MAC10.cost

    game.execute_action(buyer, "refund_weapon_ak47")
    assert buyer.primary_weapon_id == ""
    assert buyer.equipped_weapon_id == GLOCK.id
    assert buyer.cash == MAC10.cost + AK47.cost
    assert game.buy_transactions == []


def test_duplicate_weapon_purchases_drop_and_refund_each_exact_copy() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = game.economy.maximum_cash
    starting_cash = buyer.cash

    game.execute_action(buyer, "buy_weapon_ak47")
    game.execute_action(buyer, "buy_weapon_ak47")

    assert buyer.primary_weapon_id == AK47.id
    assert buyer.cash == starting_cash - AK47.cost * 2
    assert [dropped.weapon_id for dropped in game.dropped_weapons] == [AK47.id]
    assert game._refundable_item_count(buyer, "weapon", AK47.id) == 2

    game.execute_action(buyer, "refund_weapon_ak47")
    assert buyer.primary_weapon_id == ""
    assert len(game.dropped_weapons) == 1
    game.execute_action(buyer, "refund_weapon_ak47")
    assert not game.dropped_weapons
    assert buyer.cash == starting_cash


def test_later_buyer_can_donate_a_weapon_to_an_earlier_teammate() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    recipient = tactical_player(game, 0)
    intervening_buyer = tactical_player(game, 1)
    buyer = tactical_player(game, 2)
    game.execute_action(recipient, "finish_buy")
    game.execute_action(intervening_buyer, "finish_buy")
    assert game.current_player is buyer
    buyer.cash = AK47.cost
    action_id = game._donate_weapon_action_id(AK47, recipient)
    recipient_user = game.get_user(recipient)
    assert isinstance(recipient_user, MockUser)
    recipient_user.clear_messages()

    game.execute_action(buyer, action_id)

    assert game.current_player is recipient
    assert game.pending_weapon_donation is not None
    assert TURN_NOTIFICATION_ASSET in recipient_user.get_sounds_played()
    assert game._buy_turn_error(buyer) == (
        "breachpoint-error-donation-response-player",
        {"player": recipient.name},
    )
    assert game._is_weapon_donation_response_hidden(recipient) is Visibility.VISIBLE
    clear_spoken(game)
    game._action_whose_turn(buyer, "whose_turn")
    game._action_whose_turn(recipient, "whose_turn")
    assert spoken_text(game, 2) == [
        "Buying is waiting for Player1 to answer a weapon offer."
    ]
    assert spoken_text(game, 0) == [
        "Buying is waiting for you to accept or decline a teammate's weapon offer."
    ]
    game.execute_action(recipient, "accept_weapon_donation")

    assert game.pending_weapon_donation is None
    assert game.current_player is buyer
    assert recipient.primary_weapon_id == AK47.id
    assert buyer.primary_weapon_id == ""
    assert buyer.cash == 0
    assert not any(
        transaction.player_id == buyer.id
        for transaction in game.buy_transactions
    )


def test_weapon_donation_rejects_self_enemy_and_wrong_side_action_ids() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    buyer.cash = game.economy.maximum_cash
    initial_state = (buyer.cash, game.pending_weapon_donation)

    forged_action_ids = (
        f"donate_weapon_{AK47.id}_to_{buyer.id}",
        f"donate_weapon_{AK47.id}_to_{enemy.id}",
        f"donate_weapon_{M4.id}_to_{teammate.id}",
    )
    for action_id in forged_action_ids:
        assert game._is_donate_weapon_enabled(
            buyer,
            action_id=action_id,
        ) == "breachpoint-error-donation-unavailable"
        game._action_donate_weapon(buyer, action_id)

    assert (buyer.cash, game.pending_weapon_donation) == initial_state


def test_bot_accepts_a_donation_upgrade_but_declines_a_duplicate() -> None:
    game = make_game(
        start=True,
        bot_indexes={2},
        finish_buy_phase=False,
    )
    buyer = tactical_player(game, 0)
    recipient = tactical_player(game, 2)
    buyer.cash = AK47.cost * 2

    game.execute_action(
        buyer,
        game._donate_weapon_action_id(AK47, recipient),
    )
    assert game._bot_coordinator.choose_action(game, recipient) == (
        "accept_weapon_donation"
    )
    game.execute_action(recipient, "accept_weapon_donation")
    assert recipient.primary_weapon_id == AK47.id

    game.execute_action(
        buyer,
        game._donate_weapon_action_id(AK47, recipient),
    )
    assert game._bot_coordinator.choose_action(game, recipient) == (
        "decline_weapon_donation"
    )


def test_declined_donation_becomes_the_buyers_refundable_ground_weapon() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    recipient = tactical_player(game, 2)
    buyer.cash = AK47.cost
    action_id = game._donate_weapon_action_id(AK47, recipient)

    game.execute_action(buyer, action_id)
    game.execute_action(recipient, "decline_weapon_donation")

    assert game.current_player is buyer
    assert buyer.cash == 0
    assert len(game.dropped_weapons) == 1
    dropped_weapon = game.dropped_weapons[0]
    assert dropped_weapon.weapon_id == AK47.id
    assert dropped_weapon.node_id == buyer.position_id
    assert game._is_refund_purchase_enabled(
        buyer,
        action_id="refund_weapon_ak47",
    ) is None

    game.execute_action(buyer, "refund_weapon_ak47")

    assert buyer.cash == AK47.cost
    assert not game.dropped_weapons


def test_refunds_restore_stacked_utility_partial_armor_and_equipment() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)

    game.execute_action(terrorist, "buy_utility_flashbang")
    game.execute_action(terrorist, "buy_utility_flashbang")
    label = game._get_refund_purchase_label(
        terrorist,
        "refund_utility_flashbang",
    )
    assert "you have 2" in label

    game.execute_action(terrorist, "refund_utility_flashbang")
    assert terrorist.utility_counts == {FLASHBANG.id: 1}
    game.execute_action(terrorist, "refund_utility_flashbang")
    assert terrorist.utility_counts == {}
    assert terrorist.cash == game.economy.starting_cash

    terrorist.armor = 35
    game.execute_action(terrorist, "buy_armor")
    game.execute_action(terrorist, "refund_armor")
    assert terrorist.armor == 35
    assert terrorist.cash == game.economy.starting_cash

    game.execute_action(terrorist, "finish_buy")
    defender = tactical_player(game, 1)
    game.execute_action(defender, "buy_equipment_defuse_kit")
    game.execute_action(defender, "refund_equipment_defuse_kit")
    assert defender.equipment_counts == {}
    assert defender.cash == game.economy.starting_cash


def test_finish_buy_commits_purchases_and_closes_refunds() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    game.execute_action(buyer, "buy_weapon_desert_eagle")

    game.execute_action(buyer, "finish_buy")

    assert all(
        transaction.player_id != buyer.id for transaction in game.buy_transactions
    )
    assert game._is_refund_purchase_hidden(
        buyer,
        action_id="refund_weapon_desert_eagle",
    ) == Visibility.HIDDEN


def test_buy_zone_ground_pickup_is_free_and_preserves_combat_ap() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    game.execute_action(buyer, "buy_weapon_desert_eagle")
    dropped_glock = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == GLOCK.id
    )
    pickup_action = game._dropped_weapon_action_id(dropped_glock)
    game.flush_menus()

    assert game._is_pick_up_weapon_enabled(buyer, action_id=pickup_action) is None
    assert "free during your buy" in game._get_pick_up_weapon_label(
        buyer,
        pickup_action,
    )
    game.execute_action(buyer, "refund_weapon_desert_eagle")
    game.execute_action(buyer, pickup_action)

    assert buyer.sidearm_weapon_id == GLOCK.id
    assert buyer.equipped_weapon_id == GLOCK.id
    assert buyer.action_points == 0
    assert buyer.cash == game.economy.starting_cash
    assert game.current_player is buyer


def test_buy_zone_pickup_relinks_both_refundable_weapon_purchases() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = MAC10.cost + AK47.cost
    game.execute_action(buyer, "buy_weapon_mac10")
    game.execute_action(buyer, "buy_weapon_ak47")
    dropped_mac10 = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == MAC10.id
    )
    game.flush_menus()

    game.execute_action(buyer, game._dropped_weapon_action_id(dropped_mac10))

    dropped_ak47 = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == AK47.id
    )
    mac10_purchase = next(
        transaction
        for transaction in game.buy_transactions
        if transaction.item_id == MAC10.id
    )
    ak47_purchase = next(
        transaction
        for transaction in game.buy_transactions
        if transaction.item_id == AK47.id
    )
    assert buyer.primary_weapon_id == MAC10.id
    assert mac10_purchase.dropped_weapon_id == 0
    assert ak47_purchase.dropped_weapon_id == dropped_ak47.drop_id

    game.execute_action(buyer, "refund_weapon_mac10")
    game.execute_action(buyer, "refund_weapon_ak47")

    assert buyer.primary_weapon_id == ""
    assert game.dropped_weapons == []
    assert buyer.cash == MAC10.cost + AK47.cost


def test_buy_and_status_announcements_report_both_weapon_slots() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    terrorist.cash = AK47.cost + DESERT_EAGLE.cost
    game.execute_action(terrorist, "buy_weapon_ak47")
    game.execute_action(terrorist, "buy_weapon_desert_eagle")
    clear_spoken(game)

    game._start_buy_turn(terrorist)
    game._action_read_position(terrorist, "read_position")

    messages = spoken_text(game, 0)
    assert any("Primary: AK-47" in message for message in messages)
    assert any("Sidearm: Desert Eagle" in message for message in messages)
    assert any("Equipped: Desert Eagle" in message for message in messages)

    clear_spoken(game)
    terrorist.health = 64
    terrorist.armor = 37
    game._action_read_vitals(terrorist, "read_vitals")
    assert spoken_text(game, 0) == ["Health: 64 of 100. Armor: 37."]


def test_buying_utility_respects_cash_and_profile_carry_limits() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)

    game.execute_action(buyer, "buy_utility_flashbang")
    game.execute_action(buyer, "buy_utility_flashbang")
    assert buyer.utility_counts == {FLASHBANG.id: FLASHBANG.maximum_carry}
    assert buyer.cash == game.economy.starting_cash - 2 * FLASHBANG.cost
    assert game._is_buy_utility_enabled(
        buyer,
        action_id="buy_utility_flashbang",
    ) == ("breachpoint-error-utility-full", {"maximum": 2})

    game.execute_action(buyer, "buy_utility_smoke")
    assert buyer.utility_counts[SMOKE_GRENADE.id] == 1
    assert buyer.cash == 100
    assert game._is_buy_utility_enabled(
        buyer,
        action_id="buy_utility_smoke",
    ) == ("breachpoint-error-utility-full", {"maximum": 1})


def test_defuse_kit_is_a_private_ct_only_equipment_purchase() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    assert (
        game._is_buy_equipment_hidden(
            terrorist,
            action_id="buy_equipment_defuse_kit",
        )
        == Visibility.HIDDEN
    )
    game.execute_action(terrorist, "finish_buy")
    game.execute_action(defender, "buy_equipment_defuse_kit")

    assert defender.equipment_counts == {DEFUSE_KIT.id: 1}
    assert defender.cash == game.economy.starting_cash - DEFUSE_KIT.cost
    assert game._defuse_action_point_cost(defender) == 1


def test_weapon_range_damage_armor_and_shot_limits_are_profile_driven() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = "t_spawn"
    defender.position_id = "mid_doors"
    action_id = f"shoot_{defender.id}"

    assert game._is_shoot_enabled(terrorist, action_id=action_id)[0] == (
        "breachpoint-error-target-out-of-range"
    )
    terrorist.primary_weapon_id = AK47.id
    terrorist.equipped_weapon_id = AK47.id
    defender.armor = game.economy.maximum_armor
    game.execute_action(terrorist, action_id)
    complete_weapon_fire(game)
    assert defender.armor == 94
    assert defender.health == 60

    start_activation(game, defender)
    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    defender.position_id = "mid_doors"
    terrorist.position_id = "ct_mid"
    terrorist.health = game.rules.max_health
    terrorist.armor = 0
    second_terrorist = tactical_player(game, 2)
    second_terrorist.position_id = "b_site"
    return_fire = f"shoot_{terrorist.id}"
    game.execute_action(defender, return_fire)
    complete_weapon_fire(game)
    assert terrorist.health == 46
    assert defender.action_points == 1
    game.execute_action(defender, return_fire)
    complete_weapon_fire(game)
    assert terrorist.health == 10
    assert second_terrorist.health == game.rules.max_health
    assert defender.shots_fired_this_activation == M4.shots_per_activation


def test_ak_cannot_one_shot_and_m4_can_commit_its_followup_burst() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = "a_site"
    defender.position_id = "a_ramp"

    terrorist.primary_weapon_id = AK47.id
    terrorist.equipped_weapon_id = AK47.id
    game.execute_action(terrorist, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.health == 31
    assert not defender.eliminated

    start_activation(game, defender)
    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    game.execute_action(defender, f"shoot_{terrorist.id}")
    complete_weapon_fire(game)
    assert (
        game._is_shoot_enabled(
            defender,
            action_id=f"shoot_{terrorist.id}",
        )
        is None
    )
    game.execute_action(defender, f"shoot_{terrorist.id}")
    complete_weapon_fire(game)
    assert terrorist.health == 10
    assert not terrorist.eliminated
    assert game._is_shoot_enabled(
        defender,
        action_id=f"shoot_{terrorist.id}",
    ) == ("breachpoint-error-not-your-turn", {"player": game.current_player.name})


def test_glock_burst_rewards_point_blank_pressure_but_respects_evasion() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    close = game._preview_attack(target, GLOCK, 0)
    followup = game._preview_attack(
        target,
        GLOCK,
        0,
        damage_percent=GLOCK.followup_damage_percent,
    )
    assert close.rounds_fired == 3
    assert close.rounds_on_target == 2
    assert close.health_damage == 38
    assert followup.health_damage == 29
    assert close.health_damage + followup.health_damage < target.health

    target.guard_points = game.rules.maximum_evasion_points
    evaded_close = game._preview_attack(target, GLOCK, 0)
    assert evaded_close.rounds_evaded == 1
    assert evaded_close.health_damage == 19

    target.guard_points = game.rules.maximum_evasion_points
    evaded_at_range = game._preview_attack(target, GLOCK, 1)
    assert evaded_at_range.fully_evaded
    assert evaded_at_range.rounds_evaded == 1


def test_smgs_need_close_followup_bursts_and_remain_weak_against_armor() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    mac_close = game._preview_attack(target, MAC10, 0)
    mac_far = game._preview_attack(target, MAC10, 1)
    mp9_close = game._preview_attack(target, MP9, 0)
    mp9_far = game._preview_attack(target, MP9, 1)

    assert mac_close.health_damage == 76
    assert mac_far.health_damage == 36
    assert mp9_close.health_damage == 68
    assert mp9_far.health_damage == 48
    assert mac_close.health_damage < target.health
    assert mp9_close.health_damage < target.health

    target.armor = game.economy.maximum_armor
    armored_mac = game._preview_attack(target, MAC10, 0)
    armored_mp9 = game._preview_attack(target, MP9, 0)
    assert (armored_mac.armor_absorbed, armored_mac.health_damage) == (30, 46)
    assert (armored_mp9.armor_absorbed, armored_mp9.health_damage) == (23, 45)

    target.armor = 0
    target.guard_points = game.rules.maximum_evasion_points
    evaded_mac = game._preview_attack(target, MAC10, 0)
    evaded_mp9 = game._preview_attack(target, MP9, 0)
    assert evaded_mac.rounds_evaded == evaded_mp9.rounds_evaded == 2
    assert 0 < evaded_mac.health_damage < mac_close.health_damage
    assert 0 < evaded_mp9.health_damage < mp9_close.health_damage


def test_smg_followup_can_finish_an_unarmored_point_blank_target() -> None:
    game = make_game(start=True)
    attacker = tactical_player(game, 0)
    target = tactical_player(game, 1)
    attacker.primary_weapon_id = MAC10.id
    attacker.equipped_weapon_id = MAC10.id
    attacker.position_id = target.position_id = "mid"
    action_id = f"shoot_{target.id}"

    game.execute_action(attacker, action_id)
    complete_weapon_fire(game)
    assert target.health == game.rules.max_health - MAC10.damage_by_range[0]
    assert not target.eliminated
    game.execute_action(attacker, action_id)
    complete_weapon_fire(game)

    assert target.eliminated
    assert attacker.weapon_shots_fired_this_activation == {MAC10.id: 2}
    assert attacker.cash == game.economy.starting_cash + MAC10.kill_reward


def test_budget_rifles_trade_full_buy_power_for_distinct_attack_patterns() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    galil_close = game._preview_attack(target, GALIL_AR, 0)
    galil_far = game._preview_attack(target, GALIL_AR, 2)
    famas_close = game._preview_attack(target, FAMAS, 0)
    famas_far = game._preview_attack(target, FAMAS, 2)
    assert (galil_close.health_damage, galil_far.health_damage) == (74, 34)
    assert (famas_close.health_damage, famas_far.health_damage) == (64, 32)
    assert galil_close.health_damage < AK47.damage_by_range[0]
    assert famas_close.health_damage < M4.damage_by_range[0]

    target.armor = game.economy.maximum_armor
    armored_galil = game._preview_attack(target, GALIL_AR, 0)
    armored_famas = game._preview_attack(target, FAMAS, 0)
    assert (armored_galil.armor_absorbed, armored_galil.health_damage) == (16, 58)
    assert (armored_famas.armor_absorbed, armored_famas.health_damage) == (19, 45)

    target.armor = 0
    target.guard_points = game.rules.maximum_evasion_points
    evaded_galil = game._preview_attack(target, GALIL_AR, 0)
    evaded_famas = game._preview_attack(target, FAMAS, 0)
    assert evaded_galil.rounds_evaded == evaded_famas.rounds_evaded == 2
    assert (evaded_galil.health_damage, evaded_famas.health_damage) == (37, 22)


def test_galil_can_suppress_two_targets_but_cannot_repeat_one_target() -> None:
    game = make_game(start=True)
    attacker = tactical_player(game, 0)
    first_target = tactical_player(game, 1)
    second_target = tactical_player(game, 3)
    attacker.primary_weapon_id = GALIL_AR.id
    attacker.equipped_weapon_id = GALIL_AR.id
    attacker.position_id = first_target.position_id = second_target.position_id = "mid"

    first_action = f"shoot_{first_target.id}"
    second_action = f"shoot_{second_target.id}"
    game.execute_action(attacker, first_action)
    complete_weapon_fire(game)
    assert first_target.health == game.rules.max_health - GALIL_AR.damage_by_range[0]
    assert game._is_shoot_enabled(attacker, action_id=first_action) == (
        "breachpoint-error-target-already-fired",
        {"player": first_target.name, "weapon": "Galil AR"},
    )
    assert game._is_shoot_enabled(attacker, action_id=second_action) is None

    game.execute_action(attacker, second_action)
    complete_weapon_fire(game)
    assert second_target.health == 59
    assert attacker.weapon_shots_fired_this_activation == {GALIL_AR.id: 2}


def test_famas_followup_can_finish_unarmored_but_not_armored_close_target() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)

    first = game._preview_attack(target, FAMAS, 0)
    followup = game._preview_attack(
        target,
        FAMAS,
        0,
        damage_percent=FAMAS.followup_damage_percent,
    )
    assert first.health_damage + followup.health_damage > target.health

    target.armor = game.economy.maximum_armor
    armored_first = game._preview_attack(target, FAMAS, 0)
    target.armor -= armored_first.armor_absorbed
    target.health -= armored_first.health_damage
    armored_followup = game._preview_attack(
        target,
        FAMAS,
        0,
        damage_percent=FAMAS.followup_damage_percent,
    )
    assert target.health - armored_followup.health_damage == 27


def test_awp_requires_a_prepared_angle_and_retains_one_shot_lethality() -> None:
    game = make_game(start=True)
    sniper = tactical_player(game, 0)
    target = tactical_player(game, 1)
    sniper.position_id = "pit"
    target.position_id = "a_site"
    sniper.primary_weapon_id = AWP.id
    sniper.equipped_weapon_id = AWP.id
    target.armor = game.economy.maximum_armor
    action_id = f"shoot_{target.id}"

    assert game._is_shoot_enabled(sniper, action_id=action_id) == (
        "breachpoint-error-aim-required",
        {"player": target.name, "weapon": "AWP"},
    )
    game.execute_action(sniper, "hold_angle_a_site")
    assert sniper.held_angle_node_id == "a_site"
    assert sniper.action_points == 0
    assert sniper.guard_points == 0

    start_activation(game, sniper)
    assert game._is_shoot_enabled(sniper, action_id=action_id) is None
    game.execute_action(sniper, action_id)
    complete_weapon_fire(game)
    assert target.eliminated
    assert target.armor == 95
    assert sniper.cash == game.economy.starting_cash + AWP.kill_reward
    assert not sniper.held_angle_node_id


def test_every_firearm_can_hold_a_visible_lane_before_firing() -> None:
    game = make_game(start=True)
    holder = tactical_player(game, 1)
    holder.position_id = "a_short"
    holder.primary_weapon_id = M4.id
    holder.equipped_weapon_id = M4.id
    start_activation(game, holder)

    assert (
        game._is_hold_angle_enabled(
            holder,
            action_id="hold_angle_a_site",
        )
        is None
    )
    game.execute_action(holder, "hold_angle_a_site")

    assert holder.held_angle_origin_id == "a_short"
    assert holder.held_angle_node_id == "a_site"
    assert holder.action_points == 0
    assert holder.guard_points == 0


def test_firing_prevents_preparing_a_held_angle_in_the_same_activation() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    target = tactical_player(game, 0)
    defender.position_id = "ct_spawn"
    target.position_id = "a_site"
    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    start_activation(game, defender)

    game.execute_action(defender, f"shoot_{target.id}")
    complete_weapon_fire(game)

    assert defender.action_points == 1
    assert (
        game._is_hold_angle_enabled(
            defender,
            action_id="hold_angle_a_site",
        )
        == "breachpoint-error-hold-after-firing"
    )


def test_watched_entry_pauses_movement_for_fire_or_hold_choice() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_ramp"
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert mover.position_id == "a_site"
    assert mover.action_points == 1
    assert game.current_player is watcher
    assert game.reaction_window.kind == REACTION_WATCHED_ENTRY
    assert game.reaction_window.triggering_player_id == mover.id
    assert game._is_reaction_shoot_enabled(watcher) is None
    assert game._is_reaction_pass_enabled(watcher) is None
    assert game._turn_error(watcher) == "breachpoint-error-reaction-action-only"
    assert game._pending_menu_focus[watcher.id] == "reaction_shoot"
    turn_set = game.get_action_set(watcher, "turn")
    assert turn_set is not None
    visible_ids = [
        resolved.action.id for resolved in game.get_all_visible_actions(watcher)
    ]
    assert visible_ids[:2] == ["reaction_shoot", "reaction_pass"]
    game.flush_menus()
    assert turn_menu_ids(game, 2) == [
        "combat_menu_summary",
        "combat_menu_move",
        "combat_menu_attack",
        "combat_menu_utility",
        "combat_menu_angle",
        "combat_menu_objective",
        "combat_menu_weapons",
        "combat_menu_loot",
        "end_turn",
    ]
    clear_spoken(game)
    game.execute_action(mover, "combat_menu_attack")
    assert any(
        f"Wait for {watcher.name} to resolve the reaction" in text
        for text in spoken_text(game, 2)
    )

    game.execute_action(watcher, "reaction_pass")

    assert not game.reaction_window.is_open
    assert game.current_player is mover
    assert mover.action_points == 1
    assert watcher.held_angle_node_id == "a_site"


def test_watched_entry_shot_uses_evasion_then_resumes_surviving_mover() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_ramp"
    mover.guard_points = game.rules.maximum_evasion_points
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)
    mover.guard_points = game.rules.maximum_evasion_points

    game.execute_action(mover, "move_a_site")
    complete_movement(game)
    game.execute_action(watcher, "reaction_shoot")
    complete_weapon_fire(game)

    assert mover.health == 10
    assert mover.guard_points == 0
    assert not mover.eliminated
    assert game.current_player is mover
    assert mover.action_points == 1
    assert not watcher.held_angle_node_id
    assert not game.reaction_window.is_open


def test_rifle_watched_entry_uses_profile_reaction_damage_and_label() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_short"
    watcher.position_id = "a_ramp"
    watcher.primary_weapon_id = M4.id
    watcher.equipped_weapon_id = M4.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert game.current_player is watcher
    assert "75 percent damage" in game._get_reaction_shoot_label(
        watcher,
        "reaction_shoot",
    )
    game.execute_action(watcher, "reaction_shoot")
    complete_weapon_fire(game)

    assert mover.health == 59
    assert watcher.weapon_magazine_ammo[M4.id] == (
        M4.magazine_capacity - M4.ammunition_per_attack
    )
    assert not mover.eliminated
    assert game.current_player is mover
    assert mover.action_points == 1
    assert not watcher.held_angle_node_id
    assert not game.reaction_window.is_open


def test_lethal_watched_entry_shot_restores_order_after_the_mover() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    next_player = tactical_player(game, 3)
    game.round_acted_player_ids = [tactical_player(game, 0).id, watcher.id]
    game.bomb_carrier_id = tactical_player(game, 0).id
    mover.position_id = "a_ramp"
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)
    game.execute_action(watcher, "reaction_shoot")
    complete_weapon_fire(game)

    assert mover.eliminated
    assert mover.id in game.round_acted_player_ids
    assert game.current_player is next_player
    assert not game.reaction_window.is_open


def test_smoke_blocks_watched_entry_without_consuming_the_held_angle() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_ramp"
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert game.current_player is mover
    assert mover.action_points == 1
    assert watcher.held_angle_node_id == "a_site"
    assert not game.reaction_window.is_open


def test_smoke_does_not_hide_point_blank_entry_from_a_site_occupant() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_ramp"
    watcher.position_id = "a_site"
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = watcher.position_id
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert game.current_player is watcher
    assert game.reaction_window.kind == REACTION_WATCHED_ENTRY
    assert game.reaction_window.target_player_id == mover.id
    assert game._is_reaction_shoot_enabled(watcher) is None


def test_one_move_opens_only_the_closest_valid_watched_entry_response() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    remote_watcher = tactical_player(game, 1)
    close_watcher = tactical_player(game, 3)
    mover.position_id = "a_short"
    remote_watcher.position_id = "pit"
    close_watcher.position_id = "a_long"
    for watcher in (remote_watcher, close_watcher):
        watcher.primary_weapon_id = AWP.id
        watcher.equipped_weapon_id = AWP.id
        watcher.held_angle_origin_id = watcher.position_id
        watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)

    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert game.current_player is close_watcher
    assert game.reaction_window.responding_player_id == close_watcher.id
    game.execute_action(close_watcher, "reaction_pass")
    assert game.current_player is mover
    assert not game.reaction_window.is_open
    assert remote_watcher.held_angle_node_id == "a_site"


def test_objective_response_movement_cannot_open_a_nested_reaction() -> None:
    game = make_game(start=True)
    planter = tactical_player(game, 0)
    responder = tactical_player(game, 1)
    watcher = tactical_player(game, 2)
    planter.position_id = "b_site"
    responder.position_id = "ct_spawn"
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    game.bomb_carrier_id = planter.id
    start_activation(game, planter)
    game.execute_action(planter, "plant")

    assert game.current_player is responder
    assert game.reaction_window.kind == REACTION_PLANT
    game.execute_action(responder, "move_a_site")
    complete_movement(game)

    assert game.current_player is responder
    assert game.reaction_window.kind == REACTION_PLANT
    assert game.reaction_window.responding_player_id == responder.id
    assert watcher.held_angle_node_id == "a_site"


def test_watched_entry_window_survives_restore_and_bots_take_the_shot() -> None:
    game = make_game(start=True, bot_indexes={1})
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    mover.position_id = "a_ramp"
    watcher.position_id = "pit"
    watcher.primary_weapon_id = AWP.id
    watcher.equipped_weapon_id = AWP.id
    watcher.held_angle_origin_id = watcher.position_id
    watcher.held_angle_node_id = "a_site"
    start_activation(game, mover)
    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    restored = BreachPointGame.from_json(game.to_json())
    for restored_player in restored.players:
        user = (
            Bot(restored_player.name, uuid=restored_player.id)
            if restored_player.id == watcher.id
            else MockUser(restored_player.name, uuid=restored_player.id)
        )
        restored.attach_user(restored_player.id, user)
    restored.rebuild_runtime_state()
    restored_watcher = tactical_player(restored, 1)

    assert restored.reaction_window.kind == REACTION_WATCHED_ENTRY
    assert restored.current_player is restored_watcher
    assert restored.bot_think(restored_watcher) == "reaction_shoot"


def test_restore_discards_an_invalid_reaction_window() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    game.current_player = watcher
    game.reaction_window = ReactionWindow(
        kind=REACTION_WATCHED_ENTRY,
        triggering_player_id=mover.id,
        responding_player_id=watcher.id,
        resume_after_player_id=mover.id,
        target_player_id=mover.id,
        context={"node_id": "missing"},
    )

    game.rebuild_runtime_state()

    assert not game.reaction_window.is_open
    assert game.current_player is mover


def test_restore_recovers_an_incomplete_watched_entry_window() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 2)
    watcher = tactical_player(game, 1)
    game.current_player = watcher
    game.reaction_window = ReactionWindow(
        kind=REACTION_WATCHED_ENTRY,
        triggering_player_id=mover.id,
        resume_after_player_id=mover.id,
        target_player_id=mover.id,
        context={"node_id": mover.position_id},
    )

    game.rebuild_runtime_state()

    assert not game.reaction_window.is_open
    assert game.current_player is mover


def test_unused_ap_defense_is_consumed_and_attacking_prevents_rearming_it() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 0)
    attacker = tactical_player(game, 1)
    defender.position_id = "mid"
    attacker.position_id = "mid_doors"
    defender.action_points = 1

    game.execute_action(defender, "end_turn")
    assert defender.guard_points == 1
    game.execute_action(attacker, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.health == 76
    assert defender.guard_points == 0

    attacker.action_points = 1
    game.execute_action(attacker, "end_turn")
    assert attacker.shots_fired_this_activation == 1
    assert attacker.guard_points == 0


def test_full_evasion_dodges_a_pistol_but_only_mitigates_an_awp() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 0)
    sniper = tactical_player(game, 1)
    defender.position_id = "a_site"
    sniper.position_id = "pit"

    game.execute_action(defender, "end_turn")
    assert defender.guard_points == game.rules.maximum_evasion_points
    sniper.primary_weapon_id = AWP.id
    sniper.equipped_weapon_id = AWP.id
    sniper.held_angle_origin_id = sniper.position_id
    sniper.held_angle_node_id = defender.position_id
    game.execute_action(sniper, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.health == 10
    assert defender.guard_points == 0

    defender.guard_points = game.rules.maximum_evasion_points
    start_activation(game, defender)
    assert defender.guard_points == 0


def test_desert_eagle_extends_sidearm_range_without_replacing_awp_lethality() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 1)
    target.health = game.rules.max_health
    target.armor = game.economy.maximum_armor

    long_range = game._preview_attack(target, DESERT_EAGLE, 2)
    assert long_range.rounds_fired == 1
    assert long_range.rounds_on_target == 1
    assert long_range.armor_absorbed == 3
    assert long_range.health_damage == 41
    assert long_range.health_damage < target.health

    target.guard_points = game.rules.maximum_evasion_points
    evaded = game._preview_attack(target, DESERT_EAGLE, 0)
    assert evaded.fully_evaded
    assert evaded.rounds_evaded == 1
    assert evaded.health_damage == 0
    assert evaded.armor_absorbed == 0


def test_full_evasion_dodges_sidearm_but_not_rifle_burst() -> None:
    game = make_game(start=True)
    target = tactical_player(game, 0)
    target.guard_points = game.rules.maximum_evasion_points
    sidearm_outcome = game._resolve_attack(target, USP_S, 1)
    assert sidearm_outcome.fully_evaded
    assert sidearm_outcome.rounds_evaded == 1
    assert target.health == game.rules.max_health

    target.guard_points = game.rules.maximum_evasion_points
    rifle_outcome = game._resolve_attack(target, AK47, 1)
    assert not rifle_outcome.fully_evaded
    assert rifle_outcome.rounds_fired == 12
    assert rifle_outcome.rounds_on_target == 3
    assert rifle_outcome.rounds_evaded == 2
    assert rifle_outcome.health_damage == 23
    assert target.health == game.rules.max_health - 23

    target.health = game.rules.max_health
    target.guard_points = 1
    one_point_outcome = game._resolve_attack(target, AK47, 2)
    target.health = game.rules.max_health
    target.guard_points = 2
    two_point_outcome = game._resolve_attack(target, AK47, 2)
    assert one_point_outcome.rounds_evaded == two_point_outcome.rounds_evaded == 1
    assert 0 < two_point_outcome.health_damage < one_point_outcome.health_damage


def test_stationary_evasion_decays_until_movement_resets_it() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)

    game.execute_action(player, "end_turn")
    assert player.guard_points == 2
    start_activation(game, player)
    game.execute_action(player, "end_turn")
    assert player.guard_points == 1
    start_activation(game, player)
    game.execute_action(player, "end_turn")
    assert player.guard_points == 0

    start_activation(game, player)
    game.execute_action(player, "move_mid")
    complete_movement(game)
    game.execute_action(player, "end_turn")
    assert player.guard_points == 1


def test_end_turn_without_evasion_omits_a_zero_value_announcement() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    player.shots_fired_this_activation = 1
    clear_spoken(game)

    game.execute_action(player, "end_turn")

    assert "You end your activation." in spoken_text(game, 0)
    assert all("0 evasion" not in message for message in spoken_text(game, 0))


def test_weapon_switching_is_free_and_preserves_per_weapon_attack_limits() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.primary_weapon_id = AK47.id
    terrorist.equipped_weapon_id = AK47.id
    terrorist.position_id = "a_ramp"
    defender.position_id = "a_site"

    game.execute_action(terrorist, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.health == 31
    assert terrorist.action_points == 1
    assert terrorist.shots_fired_this_activation == 1
    assert terrorist.weapon_shots_fired_this_activation == {AK47.id: 1}
    assert (
        game._is_shoot_enabled(
            terrorist,
            action_id=f"shoot_{defender.id}",
        )
        == "breachpoint-error-already-fired"
    )

    game.execute_action(terrorist, "equip_sidearm")

    assert terrorist.equipped_weapon_id == GLOCK.id
    assert terrorist.action_points == 1
    assert terrorist.shots_fired_this_activation == 1
    assert game._is_equip_weapon_enabled(terrorist, action_id="equip_primary") is None

    game.execute_action(terrorist, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.health == 8
    assert terrorist.action_points == 0
    assert terrorist.weapon_shots_fired_this_activation == {
        AK47.id: 1,
        GLOCK.id: 1,
    }


def test_desert_eagle_is_a_recoil_limited_rifle_backup() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.sidearm_weapon_id = DESERT_EAGLE.id
    terrorist.primary_weapon_id = AK47.id
    terrorist.equipped_weapon_id = AK47.id
    terrorist.position_id = "a_ramp"
    defender.position_id = "a_site"

    game.execute_action(terrorist, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    game.execute_action(terrorist, "equip_sidearm")

    assert "recoil-limited to 70 percent damage" in game._get_shoot_label(
        terrorist,
        f"shoot_{defender.id}",
    )
    game.execute_action(terrorist, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert defender.eliminated
    assert terrorist.weapon_shots_fired_this_activation == {
        AK47.id: 1,
        DESERT_EAGLE.id: 1,
    }


def test_second_sidearm_attack_has_recoil_and_evasion_only_applies_once() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.position_id = "a_ramp"
    target.position_id = "a_site"
    target.guard_points = game.rules.maximum_evasion_points

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)
    assert target.health == game.rules.max_health
    assert target.guard_points == 0
    assert shooter.action_points == 1
    assert "recoil-limited to 75 percent damage" in game._get_shoot_label(
        shooter,
        f"shoot_{target.id}",
    )

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)
    assert target.health == 77
    assert shooter.action_points == 0
    assert shooter.weapon_shots_fired_this_activation == {GLOCK.id: 2}


def test_start_validation_requires_even_equal_team_roster() -> None:
    valid = make_game(player_count=4)
    assert valid.prestart_validate() == []
    assert valid._configured_team_mode() == "2v2"

    odd = make_game(player_count=5)
    errors = odd.prestart_validate()
    assert ("breachpoint-error-even-teams", {"players": 5}) in errors
    assert odd._configured_team_mode() == "individual"


def test_start_validation_rejects_stale_option_and_map_values() -> None:
    game = make_game()
    game.options.match_format = "mr99"
    game.options.overtime_mode = "sudden_death"
    game.map_id = "missing"

    errors = game.prestart_validate()
    assert (
        "breachpoint-error-match-format",
        {"format": "mr99"},
    ) in errors
    assert (
        "breachpoint-error-overtime-mode",
        {"mode": "sudden_death"},
    ) in errors
    assert ("breachpoint-error-map-unavailable", {"map": "missing"}) in errors


def test_map_registry_is_reciprocal_and_rejects_invalid_edges() -> None:
    _validate_map(DUST_MAP)
    invalid = TacticalMap(
        id="invalid",
        name_key="invalid-map",
        bounds=GridRect(0, 0, 9, 4),
        grid_unit_meters=1.0,
        range_band_grid_units=3.0,
        minimum_player_spacing=1,
        maximum_area_occupants=2,
        terrorist_spawn="one",
        counter_terrorist_spawn="two",
        terrorist_spawn_heading=0,
        counter_terrorist_spawn_heading=180,
        spectator_anchor=GridPoint(2, 2),
        nodes=(
            TacticalNode(
                "one",
                "one",
                "one-description",
                GridRect(0, 0, 3, 3),
                GridPoint(1, 1),
                ("two",),
                bomb_site=True,
            ),
            TacticalNode(
                "two",
                "two",
                "two-description",
                GridRect(6, 0, 9, 3),
                GridPoint(8, 1),
                (),
                bomb_site=False,
            ),
        ),
        sightlines=(TacticalSightline("one", "two"),),
    )
    try:
        _validate_map(invalid)
    except ValueError as error:
        assert "not reciprocal" in str(error)
    else:
        raise AssertionError("An asymmetric movement edge must be rejected")


def test_dust_geometry_separates_routes_sightlines_and_weapon_ranges() -> None:
    assert DUST_MAP.bounds == GridRect(0, 0, 66, 55)
    assert len(DUST_MAP.nodes) == 19
    assert DUST_MAP.get_node("mid").adjacent == (
        "t_spawn",
        "mid_doors",
        "catwalk",
        "lower_tunnels",
    )
    assert not DUST_MAP.has_sightline("mid", "lower_tunnels")
    assert DUST_MAP.combat_distance("t_spawn", "mid_doors") == 2
    assert DUST_MAP.combat_distance("t_spawn", "ct_mid") == 3
    assert DUST_MAP.combat_distance("pit", "a_site") == 3

    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    shooter.position_id = "t_spawn"
    shooter.sidearm_weapon_id = DESERT_EAGLE.id
    shooter.equipped_weapon_id = DESERT_EAGLE.id
    assert game._can_hold_angle(shooter, "mid_doors", DESERT_EAGLE)
    assert not game._can_hold_angle(shooter, "ct_mid", DESERT_EAGLE)
    shooter.primary_weapon_id = AWP.id
    shooter.equipped_weapon_id = AWP.id
    assert game._can_hold_angle(shooter, "ct_mid", AWP)


def test_round_start_assigns_unique_spaced_walkable_coordinates() -> None:
    game = make_game(start=True, player_count=10)

    for spawn_id in (
        game.tactical_map.terrorist_spawn,
        game.tactical_map.counter_terrorist_spawn,
    ):
        occupants = [
            player
            for player in game.get_active_players()
            if isinstance(player, BreachPointPlayer) and player.position_id == spawn_id
        ]
        points = [game._player_grid_point(player) for player in occupants]
        assert len(points) == len(set(points)) == 5
        assert all(game._node(spawn_id).is_walkable(point) for point in points)
        assert all(
            (first.x - second.x) ** 2 + (first.y - second.y) ** 2
            >= game.tactical_map.minimum_player_spacing**2
            for index, first in enumerate(points)
            for second in points[index + 1 :]
        )


def test_every_dust_area_can_space_the_full_roster() -> None:
    game = make_game(start=True, player_count=10)
    players = [
        player
        for player in game.get_active_players()
        if isinstance(player, BreachPointPlayer)
    ]

    for node in game.tactical_map.nodes:
        for player in players:
            player.position_id = node.id
            player.grid_x = -1
            player.grid_y = -1
        game._normalize_spatial_positions(players)
        points = [game._player_grid_point(player) for player in players]
        assert len(points) == len(set(points)) == len(players)
        assert all(game._player_has_valid_grid_point(player) for player in players)
        assert all(
            (first.x - second.x) ** 2 + (first.y - second.y) ** 2
            >= game.tactical_map.minimum_player_spacing**2
            for index, first in enumerate(points)
            for second in points[index + 1 :]
        )


def test_movement_places_player_in_destination_and_faces_travel_direction() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    origin = game._player_grid_point(player)
    source = game._node(player.position_id)
    destination = game._node("outside_long")
    assert source is not None
    assert destination is not None

    game.execute_action(player, "move_outside_long")
    complete_movement(game)

    point = game._player_grid_point(player)
    expected_heading = (
        round(
            math.degrees(
                math.atan2(
                    destination.anchor.x - source.anchor.x,
                    destination.anchor.y - source.anchor.y,
                )
            )
        )
        % 360
    )
    assert point != origin
    assert destination.is_walkable(point)
    assert player.facing_degrees == expected_heading


def test_listener_transform_uses_heading_and_spectator_cardinal_frame() -> None:
    source = GridPoint(10, 20)
    listener = GridPoint(10, 10)

    assert listener_relative_position(source, listener, 0, 1.0) == (
        0.0,
        10.0,
        -1.6,
    )
    assert listener_relative_position(source, listener, 90, 1.0) == (
        -10.0,
        0.0,
        -1.6,
    )
    assert listener_relative_position(source, listener, 180, 1.0) == (
        -0.0,
        -10.0,
        -1.6,
    )


def test_tactical_attenuation_keeps_nearby_cues_strong_and_culls_footsteps() -> None:
    assert distance_attenuation_gain(
        (0.0, 20.0, 0.0),
        POSITIONAL_ATTENUATION,
    ) >= 0.8
    assert distance_attenuation_gain(
        (0.0, 20.0, 0.0),
        FOOTSTEP_ATTENUATION,
    ) >= 0.64
    assert distance_attenuation_gain(
        (0.0, 20.0, 0.0),
        FIRE_ATTENUATION,
    ) >= 0.64
    assert distance_attenuation_gain(
        (0.0, FOOTSTEP_ATTENUATION.max_distance, 0.0),
        FOOTSTEP_ATTENUATION,
    ) == 0.0
    assert distance_attenuation_gain(
        (0.0, FIRE_ATTENUATION.max_distance, 0.0),
        FIRE_ATTENUATION,
    ) == 0.0

    placement_points = {
        node.id: node.placement_points(DUST_MAP.minimum_player_spacing)
        for node in DUST_MAP.nodes
    }
    maximum_same_area_distance = max(
        math.dist((first.x, first.y), (second.x, second.y))
        * DUST_MAP.grid_unit_meters
        for points in placement_points.values()
        for first in points
        for second in points
    )
    assert distance_attenuation_gain(
        (0.0, maximum_same_area_distance, 0.0),
        FOOTSTEP_ATTENUATION,
    ) >= 0.7

    terrorist_spawn_points = placement_points[DUST_MAP.terrorist_spawn]
    counter_terrorist_spawn_points = placement_points[
        DUST_MAP.counter_terrorist_spawn
    ]
    minimum_spawn_distance = min(
        math.dist((terrorist.x, terrorist.y), (counter.x, counter.y))
        * DUST_MAP.grid_unit_meters
        for terrorist in terrorist_spawn_points
        for counter in counter_terrorist_spawn_points
    )
    assert minimum_spawn_distance > FOOTSTEP_ATTENUATION.max_distance


def test_movement_waits_for_measured_spatial_footsteps() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    origin_node_id = mover.position_id
    mover_user = game.get_user(mover)
    observer_user = game.get_user(observer)
    assert isinstance(mover_user, MockUser)
    assert isinstance(observer_user, MockUser)
    mover_user.clear_messages()
    observer_user.clear_messages()

    game.execute_action(mover, "move_mid")

    assert mover.position_id == origin_node_id
    assert mover.action_points == 1
    assert game.has_active_sequence(tag="breachpoint-movement")
    mover_chain = next(
        message
        for message in mover_user.messages
        if message.type == "play_sound" and message.data.get("segments")
    )
    observer_chain = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound" and message.data.get("segments")
    )
    expected_onset_ratio = 10000 / (
        WEAPON_AUDIO_PROFILES[GLOCK.id].footstep_cadence_percent
        * MOVEMENT_AUDIO_SPEED_PERCENT
    )
    assert mover_chain.data["pitch"] == 100
    assert all(
        math.isclose(segment["next_start_ratio"], expected_onset_ratio)
        for segment in mover_chain.data["segments"]
    )
    assert all(
        segment["position"] is None and segment["destination_position"] is None
        for segment in mover_chain.data["segments"]
    )
    assert all(
        segment["position"] is not None
        and segment["destination_position"] is not None
        and segment["attenuation"] == FOOTSTEP_ATTENUATION.to_packet()
        for segment in observer_chain.data["segments"]
    )

    complete_movement(game)

    assert mover.position_id == "mid"
    assert not game.has_active_sequence(tag="breachpoint-movement")
    assert mover_user.get_spoken_messages()


def test_utility_unlocks_when_detonation_is_dispatched_not_after_its_tail() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    thrower.position_id = "a_ramp"
    thrower.utility_counts = {MOLOTOV.id: 1}
    start_activation(game, thrower)
    destination = game._node("a_site")
    assert destination is not None
    timing = utility_audio_timing(
        MOLOTOV.id,
        game._player_grid_point(thrower),
        destination.anchor,
    )

    game.execute_action(thrower, "throw_molotov_a_site")

    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    assert sequence.current_index == 1
    assert sequence.next_tick - game.sound_scheduler_tick == timing.handling_ticks
    assert not game._is_burning("a_site")
    assert game.is_sequence_gameplay_locked()

    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()

    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    assert sequence.current_index == 2
    assert sequence.next_tick - game.sound_scheduler_tick == timing.travel_ticks
    assert sequence.metadata["audio_stage"] == "flight"
    assert not game._is_burning("a_site")
    assert game.is_sequence_gameplay_locked()

    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()

    assert game._is_burning("a_site")
    assert not game.has_active_sequence(tag=UTILITY_AUDIO_SEQUENCE_TAG)
    assert not game.is_sequence_gameplay_locked()


def test_restored_movement_replays_its_finite_spatial_audio() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    origin_node_id = mover.position_id
    game.execute_action(mover, "move_mid")

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored_mover = tactical_player(restored, 0)
    mover_user = restored.get_user(restored_mover)
    assert isinstance(mover_user, MockUser)

    assert restored_mover.position_id == origin_node_id
    assert any(
        message.type == "play_sound" and message.data.get("segments")
        for message in mover_user.messages
    )
    complete_movement(restored)
    assert restored_mover.position_id == "mid"


def test_weapon_reports_select_close_and_distant_assets_per_listener() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    far_listener = tactical_player(game, 3)
    shooter.position_id = target.position_id = "t_spawn"
    far_listener.position_id = "b_site"
    shooter.grid_x = game._node("t_spawn").anchor.x
    shooter.grid_y = game._node("t_spawn").anchor.y
    target.grid_x = shooter.grid_x + 2
    target.grid_y = shooter.grid_y
    far_listener.grid_x = game._node("b_site").anchor.x
    far_listener.grid_y = game._node("b_site").anchor.y
    shooter_user = game.get_user(shooter)
    far_user = game.get_user(far_listener)
    assert isinstance(shooter_user, MockUser)
    assert isinstance(far_user, MockUser)
    shooter_user.clear_messages()
    far_user.clear_messages()

    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=0,
        rounds_on_target=1,
        rounds_evaded=0,
        health_damage=20,
        armor_absorbed=0,
    )

    profile = WEAPON_AUDIO_PROFILES[AK47.id]
    shooter_chain = next(
        message
        for message in shooter_user.messages
        if message.type == "play_sound"
        and any(
            segment["asset"] in profile.projectile_assets
            for segment in message.data.get("segments", [])
        )
    )
    far_chain = next(
        message
        for message in far_user.messages
        if message.type == "play_sound"
        and any(
            segment["asset"] in profile.projectile_assets
            for segment in message.data.get("segments", [])
        )
    )
    assert shooter_chain.data["segments"][0]["asset"] in profile.fire_close_assets
    assert shooter_chain.data["segments"][1]["asset"] == profile.fire_distant
    assert far_chain.data["segments"][0]["asset"] == profile.fire_distant
    assert far_chain.data["segments"][0]["attenuation"] == (
        DISTANT_ATTENUATION.to_packet()
    )
    assert not any(
        segment["asset"] in profile.fire_close_assets
        for segment in far_chain.data["segments"]
    )


def test_weapon_audio_cadence_matches_cs_fire_and_burst_intervals() -> None:
    expected_intervals = {
        GLOCK.id: 50,
        USP_S.id: 170,
        DESERT_EAGLE.id: 225,
        MAC10.id: 75,
        MP9.id: 70,
        NOVA.id: 880,
        GALIL_AR.id: 90,
        FAMAS.id: 75,
        SSG08.id: 1250,
        AK47.id: 100,
        M4.id: 90,
        AWP.id: 1455,
    }

    assert {
        weapon_id: profile.shot_interval_ms
        for weapon_id, profile in WEAPON_AUDIO_PROFILES.items()
    } == expected_intervals

    for weapon_id, interval_ms in expected_intervals.items():
        interval_count = 20
        elapsed_ticks = sum(
            weapon_fire_delay_ticks(weapon_id, shot_index)
            for shot_index in range(interval_count)
        )
        expected_ticks = math.floor(
            interval_count * interval_ms * TICKS_PER_SECOND / 1000 + 0.5
        )
        assert elapsed_ticks == max(interval_count, expected_ticks)

    assert [weapon_fire_delay_ticks(MP9.id, index) for index in range(4)] == [
        1,
        2,
        1,
        2,
    ]
    assert [weapon_fire_delay_ticks(M4.id, index) for index in range(5)] == [
        2,
        2,
        1,
        2,
        2,
    ]


def test_weapon_audio_uses_surface_casings_and_contiguous_projectile_impacts() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    game._place_player_in_node(shooter, "t_spawn")
    game._place_player_in_node(target, "t_spawn")
    shooter_user = game.get_user(shooter)
    target_user = game.get_user(target)
    assert isinstance(shooter_user, MockUser)
    assert isinstance(target_user, MockUser)
    shooter_user.clear_messages()
    target_user.clear_messages()

    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=0,
        rounds_on_target=1,
        rounds_evaded=0,
        health_damage=20,
        armor_absorbed=0,
    )

    profile = WEAPON_AUDIO_PROFILES[AK47.id]
    shooter_node = game._node(shooter.position_id)
    assert shooter_node is not None
    casing_family = CASING_FAMILIES_BY_CALIBER_AND_SURFACE[
        profile.casing_caliber
    ][shooter_node.footstep_surface]
    casing = next(
        message
        for message in target_user.messages
        if message.type == "play_sound" and message.data.get("name") == casing_family
    )
    assert casing.data["position"] == list(
        game._relative_audio_position(
            target,
            game._player_grid_point(shooter),
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
        )
    )
    projectile = next(
        message
        for message in target_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in profile.projectile_assets
            for segment in message.data["segments"]
        )
    )
    projectile_segments = projectile.data["segments"]
    projectile_index = next(
        index
        for index, segment in enumerate(projectile_segments)
        if segment["asset"] in profile.projectile_assets
    )
    assert projectile_segments[0]["next_start_ratio"] == 0.0
    assert projectile_segments[1]["next_start_ratio"] == 0.0
    assert projectile_segments[projectile_index]["next_start_ratio"] == 0.0
    assert projectile_segments[projectile_index]["destination_position"] is not None
    assert projectile_segments[projectile_index + 1]["asset"] in IMPACT_FLESH_ASSETS
    assert projectile_segments[projectile_index + 1]["position"] == list(
        game._relative_audio_position(
            target,
            game._player_grid_point(target),
            source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
        )
    )

    target_user.clear_messages()
    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=0,
        rounds_on_target=0,
        rounds_evaded=0,
        health_damage=0,
        armor_absorbed=0,
    )
    missed_projectile = next(
        message
        for message in target_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in profile.projectile_assets
            for segment in message.data["segments"]
        )
    )
    expected_pass_point = game._projectile_pass_point(
        game._player_grid_point(shooter),
        game._player_grid_point(target),
        shooter.facing_degrees,
    )
    missed_segments = missed_projectile.data["segments"]
    missed_index = next(
        index
        for index, segment in enumerate(missed_segments)
        if segment["asset"] in profile.projectile_assets
    )
    assert missed_segments[missed_index]["destination_position"] == list(
        game._relative_audio_position(
            target,
            expected_pass_point,
            source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
        )
    )
    assert (
        missed_segments[missed_index + 1]["asset"]
        in profile.projectile_impact_assets
    )
    assert missed_segments[missed_index + 1]["position"] == list(
        game._relative_audio_position(
            target,
            expected_pass_point,
            source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
        )
    )


def test_only_the_final_lethal_bullet_starts_headshot_and_death_audio() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    game._place_player_in_node(shooter, "mid")
    game._place_player_in_node(target, "mid")
    shooter_user = game.get_user(shooter)
    target_user = game.get_user(target)
    assert isinstance(shooter_user, MockUser)
    assert isinstance(target_user, MockUser)
    shooter_user.clear_messages()
    target_user.clear_messages()

    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=0,
        rounds_on_target=2,
        rounds_evaded=0,
        health_damage=target.health,
        armor_absorbed=0,
        lethal=True,
        target_had_armor=False,
    )
    assert not any(
        message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in HEADSHOT_ASSETS_BY_ARMOR[False]
            for segment in message.data["segments"]
        )
        for message in shooter_user.messages
    )
    assert not any(
        message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in DEATH_VOICE_ASSETS
            for segment in message.data["segments"]
        )
        for message in target_user.messages
    )

    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=1,
        rounds_on_target=2,
        rounds_evaded=0,
        health_damage=target.health,
        armor_absorbed=0,
        lethal=True,
        target_had_armor=False,
    )
    assert any(
        message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in HEADSHOT_ASSETS_BY_ARMOR[False]
            for segment in message.data["segments"]
        )
        for message in shooter_user.messages
    )
    headshot_chain = next(
        message
        for message in shooter_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in HEADSHOT_ASSETS_BY_ARMOR[False]
            for segment in message.data["segments"]
        )
    )
    headshot_segments = headshot_chain.data["segments"]
    profile = WEAPON_AUDIO_PROFILES[AK47.id]
    assert any(
        segment["asset"] in profile.fire_close_assets
        for segment in headshot_segments
    )
    assert any(
        segment["asset"] in profile.projectile_assets
        for segment in headshot_segments
    )
    assert headshot_chain.data["priority"] == WEAPON_PROJECTILE_PRIORITY
    target_lethal_chain = next(
        message
        for message in target_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and any(
            segment["asset"] in DEATH_VOICE_ASSETS
            for segment in message.data["segments"]
        )
    )
    target_segments = target_lethal_chain.data["segments"]
    assert any(
        segment["asset"] in profile.fire_close_assets
        for segment in target_segments
    )
    assert any(
        segment["asset"] in profile.projectile_assets
        for segment in target_segments
    )
    death_index = next(
        index
        for index, segment in enumerate(target_segments)
        if segment["asset"] in DEATH_VOICE_ASSETS
    )
    assert death_index > 0
    assert (
        target_segments[death_index - 1]["asset"]
        in HEADSHOT_ASSETS_BY_ARMOR[False]
    )
    assert target_segments[death_index - 1]["next_start_ratio"] == 0.0
    assert (
        target_segments[death_index + 1]["asset"]
        in BODY_FALL_ASSETS_BY_SURFACE["sand"]
    )
    assert target_segments[death_index]["position"] is None
    assert target_segments[death_index + 1]["position"] is None


def test_nonlethal_unarmored_hits_use_flesh_variants_for_every_listener() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    game._place_player_in_node(shooter, "mid")
    game._place_player_in_node(target, "mid")

    game._play_weapon_bullet_audio(
        shooter,
        target,
        USP_S,
        shot_index=0,
        rounds_on_target=1,
        rounds_evaded=0,
        health_damage=USP_S.damage_at_range(0),
        armor_absorbed=0,
    )

    for listener in game.players:
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        projectile_chain = next(
            message
            for message in user.messages
            if message.type == "play_sound"
            and any(
                segment["asset"] in WEAPON_AUDIO_PROFILES[USP_S.id].projectile_assets
                for segment in message.data.get("segments", [])
            )
        )
        assert any(
            segment["asset"] in IMPACT_FLESH_ASSETS
            for segment in projectile_chain.data["segments"]
        )


def test_lethal_armored_headshot_uses_headshot_variant_for_every_listener() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    game._place_player_in_node(shooter, "mid")
    game._place_player_in_node(target, "mid")
    for listener in game.players:
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.clear_messages()

    game._play_weapon_bullet_audio(
        shooter,
        target,
        AK47,
        shot_index=0,
        rounds_on_target=1,
        rounds_evaded=0,
        health_damage=target.health,
        armor_absorbed=target.armor,
        lethal=True,
        target_had_armor=True,
    )

    for listener in game.players:
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        projectile_chain = next(
            message
            for message in user.messages
            if message.type == "play_sound"
            and any(
                segment["asset"] in WEAPON_AUDIO_PROFILES[AK47.id].projectile_assets
                for segment in message.data.get("segments", [])
            )
        )
        assert any(
            segment["asset"] in HEADSHOT_ASSETS_BY_ARMOR[True]
            for segment in projectile_chain.data["segments"]
        )


def test_rifle_burst_issues_each_report_before_unlocking_without_waiting_for_tails() -> (
    None
):
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.primary_weapon_id = AK47.id
    shooter.equipped_weapon_id = AK47.id
    game._set_full_weapon_ammunition(shooter, AK47)
    shooter.position_id = target.position_id = "mid"
    shooter_user = game.get_user(shooter)
    assert isinstance(shooter_user, MockUser)
    shooter_user.clear_messages()
    start_tick = game.sound_scheduler_tick

    game.execute_action(shooter, f"shoot_{target.id}")

    sequence = next(
        state
        for state in game.active_sequences
        if state.tag == WEAPON_AUDIO_SEQUENCE_TAG
    )
    assert sequence.metadata["shots_issued"] == 1
    assert target.health == game.rules.max_health
    wait_error = game._turn_error(shooter)
    assert wait_error and wait_error[0] == "breachpoint-error-wait-weapon-you"
    target_wait_error = game._turn_error(target)
    assert target_wait_error and target_wait_error[0] == (
        "breachpoint-error-wait-weapon-player"
    )

    complete_weapon_fire(game)

    profile = WEAPON_AUDIO_PROFILES[AK47.id]
    shot_chains = [
        message
        for message in shooter_user.messages
        if message.type == "play_sound"
        and any(
            segment["asset"] in profile.projectile_assets
            for segment in message.data.get("segments", [])
        )
    ]
    assert len(shot_chains) == AK47.ammunition_per_attack
    assert all(
        chain.data["segments"][0]["asset"] in profile.fire_close_assets
        and chain.data["segments"][1]["asset"] == profile.fire_distant
        for chain in shot_chains
    )
    casing_family = CASING_FAMILIES_BY_CALIBER_AND_SURFACE[
        profile.casing_caliber
    ]["sand"]
    bullet_events = []
    for message in shooter_user.messages:
        if message.type != "play_sound":
            continue
        if (
            message.data.get("segments")
            and any(
                segment["asset"] in profile.projectile_assets
                for segment in message.data["segments"]
            )
        ):
            bullet_events.append("shot_chain")
        elif message.data.get("name") == casing_family:
            bullet_events.append("casing")
    assert bullet_events == [
        event
        for _ in range(AK47.ammunition_per_attack)
        for event in ("shot_chain", "casing")
    ]
    assert not game.has_active_sequence(tag=WEAPON_AUDIO_SEQUENCE_TAG)
    assert target.health < game.rules.max_health
    elapsed_ticks = game.sound_scheduler_tick - start_tick
    assert elapsed_ticks == sum(
        weapon_fire_delay_ticks(AK47.id, shot_index)
        for shot_index in range(AK47.ammunition_per_attack - 1)
    )
    assert elapsed_ticks < sound_ticks(profile.fire_close_assets[0])


def test_restored_rifle_burst_finishes_pending_reports_and_resolves_once() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.primary_weapon_id = AK47.id
    shooter.equipped_weapon_id = AK47.id
    game._set_full_weapon_ammunition(shooter, AK47)
    shooter.position_id = target.position_id = "mid"

    game.execute_action(shooter, f"shoot_{target.id}")
    assert target.health == game.rules.max_health

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_target = tactical_player(restored, 1)
    assert restored_target.health == restored.rules.max_health

    complete_weapon_fire(restored)

    assert restored_target.health == restored.rules.max_health - AK47.damage_by_range[0]
    assert not restored.has_active_sequence(tag=WEAPON_AUDIO_SEQUENCE_TAG)


def test_molotov_handling_stays_at_thrower_and_flight_moves_to_impact() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "a_ramp")
    thrower.utility_counts = {MOLOTOV.id: 1}
    thrower_user = game.get_user(thrower)
    assert isinstance(thrower_user, MockUser)
    thrower_user.clear_messages()
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_molotov_a_site")

    profile = UTILITY_AUDIO_PROFILES[MOLOTOV.id]
    chain = next(
        message
        for message in thrower_user.messages
        if message.type == "play_sound" and message.data.get("segments")
    )
    segments = chain.data["segments"]
    assert all(segment["asset"] != profile.release_asset for segment in segments)
    assert all(segment["asset"] != profile.flight_asset for segment in segments)

    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    flight_play = next(
        message
        for message in thrower_user.messages
        if message.type == "audio"
        and message.data.get("command") == "play"
        and message.data.get("asset") == profile.flight_asset
    )
    flight_update = next(
        message
        for message in thrower_user.messages
        if message.type == "audio"
        and message.data.get("command") == "update"
        and message.data.get("handle") == flight_play.data["handle"]
    )
    assert flight_play.data["loop"] is True
    assert flight_play.data["position"] is not None
    assert flight_update.data["motion"]["destination_position"] is not None
    release = next(
        message
        for message in thrower_user.messages
        if message.type == "play_sound"
        and message.data.get("name") == profile.release_asset
    )
    assert release.data.get("position") is None
    assert release.data.get("attenuation") is None

    complete_utility(game)

    assert any(
        message.type == "audio"
        and message.data.get("command") == "stop"
        and message.data.get("handle") == flight_play.data["handle"]
        for message in thrower_user.messages
    )

    reports = {
        message.data.get("name")
        for message in thrower_user.messages
        if message.type == "play_sound"
    }
    assert profile.detonate_close_family in reports
    assert profile.detonate_distant_family in reports
    assert set(profile.detonate_overlay_assets).issubset(reports)
    assert FIRE_IGNITE_FAMILY in reports
    assert MOLOTOV_IDLE_ASSET in reports


def test_he_grenade_bounces_progress_through_distinct_world_positions() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "t_spawn")
    thrower.utility_counts = {HE_GRENADE.id: 1}
    observer = tactical_player(game, 1)
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user.clear_messages()
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_he_grenade_mid")
    complete_utility(game)

    profile = UTILITY_AUDIO_PROFILES[HE_GRENADE.id]
    assert len(profile.detonate_close_assets) == 6
    assert len(profile.detonate_distant_assets) == 6
    bounce_asset = profile.bounce_asset
    bounce_positions = [
        tuple(message.data["position"])
        for message in observer_user.messages
        if message.type == "play_sound" and message.data.get("name") == bounce_asset
    ]
    assert len(bounce_positions) >= 2
    assert len(set(bounce_positions)) == len(bounce_positions)


def test_flashbang_impact_precedes_detonation_and_unlocks_on_dispatch() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "a_ramp")
    thrower.utility_counts = {FLASHBANG.id: 1}
    user = game.get_user(thrower)
    assert isinstance(user, MockUser)
    start_activation(game, thrower)
    destination = game._node("a_site")
    assert destination is not None
    timing = utility_audio_timing(
        FLASHBANG.id,
        game._player_grid_point(thrower),
        destination.anchor,
    )
    assert 0 < timing.impact_lead_ticks < timing.travel_ticks

    game.execute_action(thrower, "throw_flashbang_a_site")
    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    assert sequence.next_tick - game.sound_scheduler_tick == (
        timing.travel_ticks - timing.impact_lead_ticks
    )

    user.clear_messages()
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    profile = UTILITY_AUDIO_PROFILES[FLASHBANG.id]
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == profile.landing_asset
        for message in user.messages
    )
    assert not any(
        message.type == "play_sound"
        and message.data.get("name")
        in {
            profile.detonate_close_family,
            profile.detonate_distant_family,
        }
        for message in user.messages
    )
    assert game.is_sequence_gameplay_locked()

    user.clear_messages()
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    assert any(
        message.type == "play_sound"
        and message.data.get("name")
        in {
            profile.detonate_close_family,
            profile.detonate_distant_family,
        }
        for message in user.messages
    )
    assert not game.has_active_sequence(tag=UTILITY_AUDIO_SEQUENCE_TAG)
    assert not game.is_sequence_gameplay_locked()


def test_smoke_has_no_flight_or_persistent_emission_audio() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "a_ramp")
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}
    user = game.get_user(thrower)
    assert isinstance(user, MockUser)
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_smoke_a_site")
    complete_utility(game)

    profile = UTILITY_AUDIO_PROFILES[SMOKE_GRENADE.id]
    assert profile.flight_asset == ""
    reports = [
        message.data.get("name")
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert profile.detonate_close_assets[0] in reports
    assert profile.detonate_distant_assets[0] in reports
    assert set(profile.detonate_overlay_assets).issubset(reports)
    assert all(
        state.asset not in profile.detonate_overlay_assets
        for state in game.active_audio.values()
    )


def test_incendiary_grenade_combines_moving_flight_and_physical_bounces() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 1)
    game._place_player_in_node(thrower, "ct_spawn")
    thrower.utility_counts = {INCENDIARY_GRENADE.id: 1}
    observer = tactical_player(game, 0)
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user.clear_messages()
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_incendiary_grenade_a_site")
    complete_utility(game)

    profile = UTILITY_AUDIO_PROFILES[INCENDIARY_GRENADE.id]
    assert profile.flight_asset
    assert profile.bounce_asset
    assert any(
        message.type == "audio"
        and message.data.get("command") == "play"
        and message.data.get("asset") == profile.flight_asset
        and message.data.get("loop") is True
        for message in observer_user.messages
    )
    assert any(
        message.type == "audio"
        and message.data.get("command") == "update"
        and message.data.get("motion", {}).get("destination_position") is not None
        for message in observer_user.messages
    )
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == profile.bounce_asset
        for message in observer_user.messages
    )
    assert not any(
        message.type == "play_sound" and message.data.get("name") == MOLOTOV_IDLE_ASSET
        for message in observer_user.messages
    )
    assert any(
        state.handle == game._fire_audio_handle("a_site")
        and state.asset == FIRE_LOOP_ASSET
        and state.outro == FIRE_OUTRO_ASSET
        for state in game.active_audio.values()
    )


def test_restored_grenade_bounce_replays_once_for_each_listener() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "t_spawn")
    thrower.utility_counts = {HE_GRENADE.id: 1}
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_he_grenade_mid")
    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    assert sequence.metadata.get("audio_stage") == "bounce"

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))

    bounce_asset = UTILITY_AUDIO_PROFILES[HE_GRENADE.id].bounce_asset
    for player in restored.players:
        user = restored.get_user(player)
        assert isinstance(user, MockUser)
        assert (
            sum(
                message.type == "play_sound"
                and message.data.get("name") == bounce_asset
                for message in user.messages
            )
            == 1
        )


def test_restored_molotov_flight_resumes_motion_without_replaying_handling() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    game._place_player_in_node(thrower, "a_ramp")
    thrower.utility_counts = {MOLOTOV.id: 1}
    start_activation(game, thrower)

    game.execute_action(thrower, "throw_molotov_a_site")
    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()
    assert sequence.metadata["audio_stage"] == "flight"
    remaining_ticks = sequence.next_tick - game.sound_scheduler_tick

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_sequence = next(
        sequence
        for sequence in restored.active_sequences
        if sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
    )
    assert (
        restored_sequence.next_tick - restored.sound_scheduler_tick == remaining_ticks
    )
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))

    restored_thrower = tactical_player(restored, 0)
    user = restored.get_user(restored_thrower)
    assert isinstance(user, MockUser)
    profile = UTILITY_AUDIO_PROFILES[MOLOTOV.id]
    assert any(
        message.type == "audio"
        and message.data.get("command") == "play"
        and message.data.get("asset") == profile.flight_asset
        for message in user.messages
    )
    assert not any(
        message.type == "play_sound"
        and any(
            segment["asset"] == profile.draw_asset
            for segment in message.data.get("segments", [])
        )
        for message in user.messages
    )

    complete_utility(restored)

    assert restored._is_burning("a_site")


def test_ambient_stingers_are_spatial_nonblocking_and_reschedule() -> None:
    game = make_game(start=True)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    user.clear_messages()
    emitter = next(
        candidate
        for candidate in game.tactical_map.ambient_emitters
        if candidate.id == "sand_gust"
    )
    game.ambient_stinger_due_ticks = {
        candidate.id: game.sound_scheduler_tick + 10_000
        for candidate in game.tactical_map.ambient_emitters
    }
    game.ambient_stinger_due_ticks[emitter.id] = game.sound_scheduler_tick

    game._process_ambient_stingers()

    cue = next(
        message
        for message in user.messages
        if message.type == "play_sound" and message.data.get("name") == emitter.family
    )
    assert cue.data["position"] is not None
    assert cue.data["attenuation"] == POSITIONAL_ATTENUATION.to_packet()
    assert game.ambient_stinger_due_ticks[emitter.id] > game.sound_scheduler_tick
    assert not game.is_sequence_gameplay_locked()


def test_aircraft_stingers_use_open_sky_zones_and_two_to_three_minute_spacing() -> None:
    game = make_game(start=True)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    emitter = next(
        candidate
        for candidate in game.tactical_map.ambient_emitters
        if candidate.id == "aircraft"
    )
    assert emitter.minimum_interval_seconds == 120
    assert emitter.maximum_interval_seconds == 180

    game._place_player_in_node(listener, "upper_tunnels")
    user.clear_messages()
    game.ambient_stinger_due_ticks[emitter.id] = game.sound_scheduler_tick
    game._process_ambient_stingers()
    assert not any(
        message.type == "play_sound" and message.data.get("name") == emitter.family
        for message in user.messages
    )

    game._place_player_in_node(listener, "a_long")
    user.clear_messages()
    game.ambient_stinger_due_ticks[emitter.id] = game.sound_scheduler_tick
    game._process_ambient_stingers()
    assert any(
        message.type == "play_sound" and message.data.get("name") == emitter.family
        for message in user.messages
    )


def test_map_and_fire_ambience_have_replayable_lifecycles() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    thrower.position_id = "a_ramp"
    thrower.utility_counts = {MOLOTOV.id: 1, SMOKE_GRENADE.id: 1}
    start_activation(game, thrower)

    assert any(
        state.handle == MAP_AMBIENCE_HANDLE and state.asset == MAP_AMBIENCE_ASSET
        for state in game.active_audio.values()
    )
    game.execute_action(thrower, "throw_molotov_a_site")
    complete_utility(game)

    fire_handle = game._fire_audio_handle("a_site")
    fire_states = [
        state for state in game.active_audio.values() if state.handle == fire_handle
    ]
    assert fire_states
    assert {
        recipient for state in fire_states for recipient in state.recipient_ids
    } == {player.id for player in game.players}
    assert all(
        state.asset == FIRE_LOOP_ASSET
        and state.outro == FIRE_OUTRO_ASSET
        and state.position is not None
        for state in fire_states
    )

    spectator_user = MockUser("Spectator", uuid="spectator")
    spectator = game.add_spectator("Spectator", spectator_user)
    assert any(
        state.handle == fire_handle and spectator.id in state.recipient_ids
        for state in game.active_audio.values()
    )
    assert any(
        message.type == "audio"
        and message.data.get("command") == "play"
        and message.data.get("kind") == "ambience"
        and message.data.get("handle") == fire_handle
        for message in spectator_user.messages
    )

    game.execute_action(thrower, "throw_smoke_a_site")
    complete_utility(game)

    assert not any(state.handle == fire_handle for state in game.active_audio.values())
    smoke_profile = UTILITY_AUDIO_PROFILES[SMOKE_GRENADE.id]
    for listener in game.players:
        user = game.get_user(listener)
        if not isinstance(user, MockUser):
            continue
        assert any(
            message.type in {"audio", "stop_ambience"}
            and message.data["command"] == "stop"
            and message.data["kind"] == "ambience"
            and message.data["handle"] == fire_handle
            and message.data.get("play_outro", True) is False
            for message in user.messages
        )
        assert any(
            message.type == "play_sound"
            and message.data.get("name") == FIRE_EXTINGUISH_ASSET
            for message in user.messages
        )
        smoke_reports = [
            message.data.get("name")
            for message in user.messages
            if message.type == "play_sound"
        ]
        assert smoke_profile.detonate_distant_assets[0] in smoke_reports
        assert set(smoke_profile.detonate_overlay_assets).issubset(smoke_reports)
    users = [game.get_user(listener) for listener in game.players]
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == smoke_profile.detonate_close_assets[0]
        for user in users
        if isinstance(user, MockUser)
        for message in user.messages
    )
    assert all(
        state.asset not in smoke_profile.detonate_overlay_assets
        for state in game.active_audio.values()
    )


def test_area_ambience_replaces_the_base_track_across_zone_boundaries() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    player.position_id = "outside_tunnels"
    player.grid_x = game._node("outside_tunnels").anchor.x
    player.grid_y = game._node("outside_tunnels").anchor.y
    game._sync_listener_environment_audio(player)
    sand_asset = next(
        layer.asset
        for layer in game.tactical_map.zone_ambience
        if layer.id == "sand_wind"
    )
    assert any(
        state.handle == MAP_ZONE_AMBIENCE_HANDLE
        and state.asset == sand_asset
        and player.id in state.recipient_ids
        for state in game.active_audio.values()
    )
    assert not any(
        state.handle == MAP_AMBIENCE_HANDLE and player.id in state.recipient_ids
        for state in game.active_audio.values()
    )

    start_activation(game, player)
    game.execute_action(player, "move_upper_tunnels")
    player_user = game.get_user(player)
    assert isinstance(player_user, MockUser)
    movement_chain = next(
        message
        for message in reversed(player_user.messages)
        if message.type == "play_sound" and message.data.get("segments")
    )
    assert {segment["asset"] for segment in movement_chain.data["segments"]}.issubset(
        set(FOOTSTEP_ASSETS_BY_SURFACE["concrete"])
    )
    complete_movement(game)

    tunnel_asset = game.tactical_map.zone_ambience[0].asset
    assert any(
        state.handle == MAP_ZONE_AMBIENCE_HANDLE
        and state.asset == tunnel_asset
        and player.id in state.recipient_ids
        for state in game.active_audio.values()
    )

    start_activation(game, player)
    game.execute_action(player, "move_lower_tunnels")
    complete_movement(game)
    start_activation(game, player)
    game.execute_action(player, "move_mid")
    complete_movement(game)

    assert not any(
        state.handle == MAP_ZONE_AMBIENCE_HANDLE and player.id in state.recipient_ids
        for state in game.active_audio.values()
    )
    assert any(
        state.handle == MAP_AMBIENCE_HANDLE
        and state.asset == MAP_AMBIENCE_ASSET
        and player.id in state.recipient_ids
        for state in game.active_audio.values()
    )


def test_breachpoint_audio_assets_are_complete_and_identical_across_clients() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    expected = {
        PurePath(*PurePosixPath(asset).parts) for asset in BREACHPOINT_ASSET_PATHS
    }
    discovered_by_pack: dict[str, set[PurePath]] = {}
    for pack in ("client", "web_client", "mobile_client"):
        sound_root = repository_root / pack / "sounds"
        discovered_by_pack[pack] = {
            path.relative_to(sound_root)
            for path in (sound_root / "game_breachpoint").rglob("*")
            if path.is_file()
        }
        assert discovered_by_pack[pack] == expected

    for asset in expected:
        paths = tuple(
            repository_root / pack / "sounds" / asset
            for pack in ("client", "web_client", "mobile_client")
        )
        assert all(path.stat().st_size > 0 for path in paths)
        assert len({hashlib.sha256(path.read_bytes()).digest() for path in paths}) == 1
        if asset.suffix == ".ogg":
            assert sound_ticks(PurePosixPath(*asset.parts).as_posix()) > 0


def test_restore_preserves_valid_spatial_state_and_repairs_collisions() -> None:
    game = make_game(start=True)
    first = tactical_player(game, 0)
    second = tactical_player(game, 2)
    first_point = game._player_grid_point(first)
    first_heading = first.facing_degrees

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_first = tactical_player(restored, 0)
    assert restored._player_grid_point(restored_first) == first_point
    assert restored_first.facing_degrees == first_heading

    second.grid_x = first.grid_x
    second.grid_y = first.grid_y
    collided = BreachPointGame.from_json(game.to_json())
    collided.rebuild_runtime_state()
    repaired_first = tactical_player(collided, 0)
    repaired_second = tactical_player(collided, 2)
    assert collided._player_grid_point(repaired_first) != collided._player_grid_point(
        repaired_second
    )
    assert collided._player_has_valid_grid_point(repaired_first)
    assert collided._player_has_valid_grid_point(repaired_second)


def test_start_assigns_fixed_sides_random_bomb_carrier_and_balanced_turn_order() -> None:
    game = make_game(start=True, player_count=6)

    assert [player.squad_index for player in game.players] == [0, 1, 0, 1, 0, 1]
    assert [player.team_index for player in game.players] == [0, 1, 0, 1, 0, 1]
    assert [player.id for player in game.turn_players] == [
        "p1",
        "p2",
        "p3",
        "p4",
        "p5",
        "p6",
    ]
    assert all(
        tactical_player(game, index).position_id
        == ("t_spawn" if index % 2 == 0 else "ct_spawn")
        for index in range(6)
    )
    assert game.bomb_state == BOMB_CARRIED
    assert game.bomb_carrier_id == "p1"
    assert game.bomb_carrier_id == tactical_player(game, 0).id
    assert game.current_player is tactical_player(game, 0)
    assert tactical_player(game, 0).action_points == 2
    assert game.round == 1
    assert game.tactical_round == 1


def test_round_bomb_carrier_is_randomly_selected_from_all_terrorists() -> None:
    game = make_game(player_count=6)
    selected_pools: list[tuple[str, ...]] = []

    class SelectLastTerrorist:
        @staticmethod
        def choice(players):
            selected_pools.append(tuple(player.id for player in players))
            return players[-1]

    game._gameplay_rng = SelectLastTerrorist()
    game.on_start()

    assert selected_pools == [("p1", "p3", "p5")]
    assert game.bomb_carrier_id == "p5"
    assignment = game._bot_coordinator.assignment_for("p5")
    assert assignment is not None
    assert assignment.role == ROLE_OBJECTIVE


def test_round_bomb_assignment_is_announced_only_to_terrorists() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    carrier = game._breach_player_by_id(game.bomb_carrier_id)
    assert carrier is not None
    terrorists = game._players_on_team(TEAM_TERRORISTS, alive_only=True)
    defenders = game._players_on_team(TEAM_COUNTER_TERRORISTS, alive_only=True)
    clear_spoken(game)

    game._announce_combat_round_start()

    for terrorist in terrorists:
        messages = spoken_text(game, game.players.index(terrorist))
        expected = (
            "You carry the bomb this combat round."
            if terrorist.id == carrier.id
            else f"{carrier.name} carries the bomb this combat round."
        )
        assert expected in messages
    for defender in defenders:
        messages = spoken_text(game, game.players.index(defender))
        assert all("carries the bomb this combat round" not in text for text in messages)


def test_team_arrangement_uses_t_and_ct_names() -> None:
    game = make_game()
    game._begin_team_arrangement()

    lines = game._team_arrangement_lines("en")
    assert lines[0].startswith("T:")
    assert lines[1].startswith("CT:")
    host_label = game._team_arrangement_member_label(game.players[0], "p1")
    assert "T" in host_label


def test_normal_start_action_enters_arrangement_then_begins_match() -> None:
    game = make_game()
    host = tactical_player(game, 0)

    game.execute_action(host, "start_game")
    assert game.status == "waiting"
    assert game.team_arrangement_active

    game.execute_action(host, "start_game")
    assert game.status == "playing"
    assert not game.team_arrangement_active
    assert game.current_player is not None
    assert game.current_player.team_index == TEAM_TERRORISTS


def test_manual_team_swap_still_gives_terrorists_first_activation() -> None:
    game = make_game()
    game._begin_team_arrangement()
    assert game._team_manager.swap_members("Player1", "Player2")
    game._apply_team_indexes_from_manager()
    game.on_start()
    complete_buy_phase(game)

    assert game.current_player is not None
    assert game.current_player.team_index == TEAM_TERRORISTS
    assert game.bomb_carrier_id == game.current_player.id


def test_legal_movement_spends_ap_and_last_ap_advances_turn() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)

    game.execute_action(player, "move_outside_long")
    complete_movement(game)
    assert player.position_id == "outside_long"
    assert player.action_points == 1
    assert game.current_player is player

    game.execute_action(player, "move_long_doors")
    complete_movement(game)
    assert player.position_id == "long_doors"
    assert player.action_points == 0
    assert game.current_player is tactical_player(game, 1)


def test_illegal_movement_cannot_change_state() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)

    game.execute_action(player, "move_a_site")
    assert player.position_id == "t_spawn"
    assert player.action_points == 2


def test_contested_entry_enables_point_blank_attack_and_costly_disengagement() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = "b_tunnels"
    defender.position_id = "b_site"
    set_area_effect(game, SMOKE_GRENADE, "b_tunnels")
    clear_spoken(game)

    assert game._is_move_enabled(terrorist, action_id="move_b_site") is None
    assert all(defender.name not in text for text in spoken_text(game, 0))
    game.execute_action(terrorist, "move_b_site")
    complete_movement(game)

    assert terrorist.position_id == defender.position_id == "b_site"
    assert game._can_see(terrorist, defender)
    assert "Contact: Player2 at Bombsite B." in spoken_text(game, 0)
    assert "Contact: Player2 at Bombsite B." in spoken_text(game, 2)
    assert game._is_move_enabled(terrorist, action_id="move_b_doors") == (
        "breachpoint-error-not-enough-ap",
        {"needed": game.rules.disengage_cost, "remaining": 1},
    )
    game.execute_action(terrorist, "move_b_doors")
    complete_movement(game)
    assert terrorist.position_id == "b_site"
    assert terrorist.action_points == 1

    start_activation(game, terrorist)
    assert game._is_move_enabled(terrorist, action_id="move_b_doors") is None
    assert game._get_move_label(terrorist, "move_b_doors") == (
        "Disengage to B Doors (2 AP; ends activation)"
    )
    game.execute_action(terrorist, "move_b_doors")
    complete_movement(game)

    assert terrorist.position_id == "b_doors"
    assert terrorist.action_points == 0
    assert terrorist.guard_points == 0
    assert game.current_player is defender
    assert game._can_see(defender, terrorist)


def test_last_ap_contested_entry_yields_a_point_blank_counterattack() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    defender.position_id = "b_site"

    terrorist.position_id = "b_tunnels"
    terrorist.action_points = 1

    game.execute_action(terrorist, "move_b_site")
    complete_movement(game)

    assert terrorist.position_id == defender.position_id == "b_site"
    assert terrorist.action_points == 0
    assert game.current_player is defender
    assert game._is_shoot_enabled(defender, action_id=f"shoot_{terrorist.id}") is None


def test_sidearm_followup_requires_line_of_sight_and_uses_remaining_ap() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.position_id = "a_ramp"
    target.position_id = "a_site"

    action_id = f"shoot_{target.id}"
    game.execute_action(shooter, action_id)
    complete_weapon_fire(game)
    assert target.health == 70
    assert shooter.action_points == 1
    assert shooter.shots_fired_this_activation == 1
    assert game._is_shoot_enabled(shooter, action_id=action_id) is None

    game.execute_action(shooter, action_id)
    complete_weapon_fire(game)
    assert target.health == 47
    assert shooter.action_points == 0
    start_activation(game, shooter)
    target.position_id = "outside_tunnels"
    assert game._is_shoot_enabled(shooter, action_id=action_id) == (
        "breachpoint-error-no-line-of-sight",
        {"player": target.name},
    )


def test_forged_friendly_fire_and_off_turn_actions_are_rejected() -> None:
    game = make_game(start=True)
    current = tactical_player(game, 0)
    teammate = tactical_player(game, 2)
    off_turn_enemy = tactical_player(game, 1)
    current.position_id = "mid"
    teammate.position_id = "mid_doors"

    friendly_action = f"shoot_{teammate.id}"
    assert game._is_shoot_enabled(current, action_id=friendly_action) == (
        "breachpoint-error-friendly-fire"
    )
    game.execute_action(current, friendly_action)
    assert teammate.health == game.rules.max_health

    assert game._is_move_enabled(off_turn_enemy, action_id="move_a_short") == (
        "breachpoint-error-not-your-turn",
        {"player": current.name},
    )
    game.execute_action(off_turn_enemy, "move_a_short")
    assert off_turn_enemy.position_id == "ct_spawn"


def test_shot_announcements_use_actor_target_and_observer_perspectives() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.position_id = "mid"
    target.position_id = "mid_doors"
    clear_spoken(game)

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)

    assert any(text.startswith("You fire at Player2") for text in spoken_text(game, 0))
    assert any(text.startswith("Player1 fires at you") for text in spoken_text(game, 1))
    assert any(
        text.startswith("Player1 fires at Player2") for text in spoken_text(game, 2)
    )
    for player in game.players:
        user = game.get_user(player)
        if isinstance(user, MockUser):
            assert all(
                message.data.get("buffer") == "game"
                for message in user.messages
                if message.type == "speak"
            )


def test_eliminated_bomb_carrier_drops_bomb_for_teammate_pickup() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    shooter = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    game._place_player_in_node(carrier, "mid")
    dropped_point = game._player_grid_point(carrier)
    carrier.health = 1
    shooter.position_id = "mid_doors"
    start_activation(game, shooter)

    game.execute_action(shooter, f"shoot_{carrier.id}")
    complete_weapon_fire(game)
    assert carrier.eliminated
    assert game.bomb_state == BOMB_DROPPED
    assert game.bomb_location_id == "mid"
    assert game._bomb_grid_point() == dropped_point

    teammate.position_id = "mid"
    start_activation(game, teammate)
    game.execute_action(teammate, "pick_up_bomb")
    assert game.bomb_state == BOMB_CARRIED
    assert game.bomb_carrier_id == teammate.id
    assert teammate.action_points == 1


def test_bomb_pickup_layers_world_foley_with_quiet_c4_beep() -> None:
    game = make_game(start=True)
    picker = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    game._place_player_in_node(picker, "mid")
    game.bomb_state = BOMB_DROPPED
    game.bomb_carrier_id = ""
    game.bomb_location_id = picker.position_id
    game._set_bomb_grid_point(game._player_grid_point(picker))
    picker_user = game.get_user(picker)
    observer_user = game.get_user(observer)
    assert isinstance(picker_user, MockUser)
    assert isinstance(observer_user, MockUser)
    picker_user.clear_messages()
    observer_user.clear_messages()
    start_activation(game, picker)

    game.execute_action(picker, "pick_up_bomb")

    assert any(
        message.type == "play_sound"
        and message.data.get("name") == PICKUP_FAMILIES["weapon"]
        for message in picker_user.messages
    )
    picker_beep = next(
        message
        for message in picker_user.messages
        if message.type == "play_sound"
        and message.data.get("name") in BOMB_PICKUP_BEEP_ASSETS
    )
    observer_beep = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and message.data.get("name") == picker_beep.data["name"]
    )
    assert picker_beep.data.get("position") is None
    assert picker_beep.data["volume"] == 3
    assert observer_beep.data["position"] == list(
        game._relative_audio_position(
            observer,
            game._player_grid_point(picker),
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
        )
    )


def test_bomb_normalization_reassigns_an_inactive_carrier() -> None:
    game = make_game(start=True)
    inactive_carrier = tactical_player(game, 0)
    replacement = tactical_player(game, 2)

    active_players = [
        player
        for player in game.players
        if isinstance(player, BreachPointPlayer) and player.id != inactive_carrier.id
    ]
    game._normalize_bomb_state(active_players)

    assert game.bomb_state == BOMB_CARRIED
    assert game.bomb_carrier_id == replacement.id


def test_counter_terrorists_can_guard_but_never_pick_up_a_dropped_bomb() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_DROPPED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "mid"
    defender.position_id = "mid"
    start_activation(game, defender)

    assert game._is_pick_up_bomb_hidden(defender) == Visibility.HIDDEN
    assert (
        game._is_pick_up_bomb_enabled(defender) == "breachpoint-error-terrorists-only"
    )
    game.execute_action(defender, "pick_up_bomb")
    assert game.bomb_state == BOMB_DROPPED
    assert game.bomb_location_id == "mid"
    assert not game.bomb_carrier_id


def test_ct_objective_logic_knows_bomb_carrier_only_after_visual_contact() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    assert "concealed" in game._bomb_status_line(defender, "en")
    assert bot_target_nodes(game, defender) == ("a_site",)

    carrier.position_id = "ct_mid"
    assert "Player1" in game._bomb_status_line(defender, "en")
    assert bot_target_nodes(game, defender) == ("ct_mid",)


def test_bomb_recovery_identifies_carrier_to_ct_only_with_team_vision() -> None:
    game = make_game(start=True)
    recovering = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_DROPPED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "t_spawn"
    recovering.position_id = "t_spawn"
    start_activation(game, recovering)
    clear_spoken(game)

    game.execute_action(recovering, "pick_up_bomb")
    assert all("recovers the dropped bomb" not in text for text in spoken_text(game, 1))

    game.bomb_state = BOMB_DROPPED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "ct_mid"
    recovering.position_id = "ct_mid"
    defender.position_id = "ct_spawn"
    start_activation(game, recovering)
    clear_spoken(game)
    game.execute_action(recovering, "pick_up_bomb")
    assert "Player3 recovers the dropped bomb at CT Mid." in spoken_text(game, 1)


def test_plant_completes_after_one_ct_response_then_defuse_scores_round() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._place_player_in_node(carrier, "a_site")
    planted_point = game._player_grid_point(carrier)

    game.execute_action(carrier, "plant")
    assert game.bomb_state == BOMB_PLANTING
    assert game.planting_player_id == carrier.id
    assert carrier.action_points == 0
    assert game.current_player is defender
    game.flush_menus()
    assert turn_menu_ids(game, 0) == [
        "combat_menu_summary",
        "combat_menu_move",
        "combat_menu_attack",
        "combat_menu_utility",
        "combat_menu_angle",
        "combat_menu_objective",
        "combat_menu_weapons",
        "combat_menu_loot",
        "end_turn",
    ]
    assert turn_menu_ids(game, 1)[0] == "combat_menu_summary"
    clear_spoken(game)
    game.execute_action(carrier, "combat_menu_attack")
    assert any(
        f"Wait for {defender.name} to resolve the reaction" in text
        for text in spoken_text(game, 0)
    )

    game.execute_action(defender, "end_turn")
    assert game.bomb_state == BOMB_PLANTED
    assert game.bomb_location_id == "a_site"
    assert game._bomb_grid_point() == planted_point
    assert game.bomb_fuse_remaining == game.rules.bomb_fuse_tactical_rounds
    assert game.bomb_planted_tactical_round == 1
    assert carrier.cash == game.economy.starting_cash + game.economy.planter_reward

    defender.position_id = "a_site"
    start_activation(game, defender)
    game.execute_action(defender, "defuse")
    responder = game.current_player
    assert isinstance(responder, BreachPointPlayer)
    assert responder.team_index == TEAM_TERRORISTS
    game.execute_action(responder, "end_turn")
    assert game.status == "playing"
    assert game._squad_score(TEAM_COUNTER_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_DEFUSED
    assert game.round == 2
    assert defender.cash == (
        game.economy.starting_cash
        + game.economy.defuser_reward
        + game.economy.win_reward(WIN_DEFUSED)
    )
    assert any("Defuse reward: $300" in text for text in spoken_text(game, 1))


def test_bomb_audio_uses_the_persisted_ground_coordinate() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    game._place_player_in_node(carrier, "a_site")
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = carrier.position_id
    game._set_bomb_grid_point(game._player_grid_point(carrier))
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user.clear_messages()

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored._bomb_grid_point() == game._bomb_grid_point()

    game._play_bomb_audio(
        BOMB_BEEP_ASSETS[0],
        game.bomb_location_id,
        source=game._bomb_grid_point(),
    )

    message = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and message.data.get("name") == BOMB_BEEP_ASSETS[0]
    )
    assert message.data["position"] == list(
        game._relative_audio_position(
            observer,
            game._bomb_grid_point(),
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
        )
    )


def test_plant_uses_initiation_foley_and_spatial_keypad_sequence() -> None:
    game = make_game(start=True)
    planter = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    game._place_player_in_node(planter, "a_site")
    planter_user = game.get_user(planter)
    observer_user = game.get_user(observer)
    assert isinstance(planter_user, MockUser)
    assert isinstance(observer_user, MockUser)
    planter_user.clear_messages()
    observer_user.clear_messages()

    game.execute_action(planter, "plant")

    for user in (planter_user, observer_user):
        assert any(
            message.type == "play_sound"
            and message.data.get("name") == BOMB_PLANT_INITIATE_ASSET
            for message in user.messages
        )
        assert not any(
            message.type == "play_sound"
            and message.data.get("name") == BOMB_PLANT_QUIET_ASSET
            for message in user.messages
        )
    keypad_chain = next(
        message
        for message in planter_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and all(
            segment["asset"] in BOMB_KEYPAD_ASSETS
            for segment in message.data["segments"]
        )
    )
    assert len(keypad_chain.data["segments"]) in {5, 6}
    assert all(
        first["asset"] != second["asset"]
        for first, second in pairwise(keypad_chain.data["segments"])
    )
    assert all(
        segment["position"] is None for segment in keypad_chain.data["segments"]
    )
    observer_keypad_chain = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and all(
            segment["asset"] in BOMB_KEYPAD_ASSETS
            for segment in message.data["segments"]
        )
    )
    assert [
        segment["asset"] for segment in observer_keypad_chain.data["segments"]
    ] == [segment["asset"] for segment in keypad_chain.data["segments"]]
    assert all(
        segment["position"]
        == list(
            game._relative_audio_position(
                observer,
                game._player_grid_point(planter),
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            )
        )
        for segment in observer_keypad_chain.data["segments"]
    )
    assert observer_keypad_chain.data["volume"] == 30

    planter_user.clear_messages()
    observer_user.clear_messages()
    assert game._complete_pending_plant()
    for user in (planter_user, observer_user):
        completion = next(
            message
            for message in user.messages
            if message.type == "play_sound"
            and message.data.get("name") == BOMB_PLANT_QUIET_ASSET
        )
        assert completion.data["priority"] == 76
        assert not any(
            message.data.get("name") in {BOMB_NVG_ON_ASSET, BOMB_ARM_ASSET}
            or any(
                segment["asset"] in {BOMB_NVG_ON_ASSET, BOMB_ARM_ASSET}
                for segment in message.data.get("segments", [])
            )
            for message in user.messages
            if message.type == "play_sound"
        )
        assert any(
            message.type == "play_sound"
            and [segment["asset"] for segment in message.data.get("segments", [])]
            == [RADIO_BOMB_PLANTED_ASSET]
            for message in user.messages
        )
    planter_completion = next(
        message
        for message in planter_user.messages
        if message.data.get("name") == BOMB_PLANT_QUIET_ASSET
    )
    assert planter_completion.data.get("position") is None
    observer_completion = next(
        message
        for message in observer_user.messages
        if message.data.get("name") == BOMB_PLANT_QUIET_ASSET
    )
    assert observer_completion.data["position"] == list(
        game._relative_audio_position(
            observer,
            game._bomb_grid_point(),
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
        )
    )
    for user in (planter_user, observer_user):
        assert any(
            message.type == "play_music"
            and message.data.get("name") == MUSIC_BOMB_PLANTED_ASSET
            and message.data.get("kind") == "music"
            and message.data.get("looping") is True
            and message.data.get("handle") == MUSIC_CONTEXT_HANDLE
            for message in user.messages
        )
    assert any(
        state.kind == "music"
        and state.handle == MUSIC_CONTEXT_HANDLE
        and state.asset == MUSIC_BOMB_PLANTED_ASSET
        and state.loop is True
        for state in game.active_audio.values()
    )


def test_defuse_is_locked_until_the_bomb_is_officially_planted() -> None:
    for bomb_state in (BOMB_CARRIED, BOMB_DROPPED, BOMB_PLANTING):
        game = make_game(start=True)
        defender = tactical_player(game, 1)
        carrier = tactical_player(game, 0)
        defender.position_id = "a_site"
        game.bomb_state = bomb_state
        game.bomb_location_id = "a_site"
        if bomb_state == BOMB_PLANTING:
            carrier.position_id = "a_site"
            game.bomb_carrier_id = carrier.id
            game.planting_player_id = carrier.id
            game.planting_location_id = "a_site"
        start_activation(game, defender)
        starting_action_points = defender.action_points

        assert game._is_defuse_hidden(defender) is Visibility.HIDDEN
        assert game._is_defuse_enabled(defender) == (
            "breachpoint-error-bomb-not-planted"
        )

        game._action_defuse(defender, "defuse")

        assert game.bomb_state == bomb_state
        assert game.defusing_player_id == ""
        assert game.defusing_location_id == ""
        assert defender.action_points == starting_action_points


def test_final_bomb_warning_overlaps_arm_then_triggers_global_explosion() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    game._place_player_in_node(carrier, "a_site")
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = carrier.position_id
    game._set_bomb_grid_point(game._player_grid_point(carrier))
    game.bomb_fuse_remaining = 1
    game.bomb_planted_tactical_round = 1
    game.tactical_round = 2
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user.clear_messages()

    assert game._complete_tactical_round()

    assert game.bomb_fuse_remaining == 0
    assert game.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
    assert game._squad_score(TEAM_TERRORISTS) == 0
    warning = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and [segment["asset"] for segment in message.data.get("segments", [])]
        == [BOMB_NVG_ON_ASSET, BOMB_ARM_ASSET]
    )
    assert warning.data["segments"][0]["next_start_ratio"] == (
        BOMB_ARM_START_RATIO
    )
    assert warning.data["segments"][0]["position"] == list(
        game._relative_audio_position(
            observer,
            game._bomb_grid_point(),
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
        )
    )
    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == BOMB_DETONATION_SEQUENCE_TAG
    )
    assert sequence.next_tick - game.sound_scheduler_tick == (
        bomb_detonation_warning_ticks()
    )
    assert not any(
        message.data.get("name") == BOMB_EXPLOSION_ASSET
        for message in observer_user.messages
    )

    complete_timed_action(game, BOMB_DETONATION_SEQUENCE_TAG)

    assert game._squad_score(TEAM_TERRORISTS) == 1
    explosion = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and message.data.get("name") == BOMB_EXPLOSION_ASSET
    )
    assert explosion.data.get("position") is None
    assert explosion.data.get("attenuation") is None


def test_opposite_site_ct_can_rotate_then_defuse_with_the_fixed_fuse() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round
    defender.position_id = "a_site"
    start_activation(game, defender)

    assert game._node_distance("a_site", "b_site") == 3
    game.execute_action(defender, "move_ct_spawn")
    complete_movement(game)
    game.execute_action(defender, "move_b_doors")
    complete_movement(game)
    assert defender.position_id == "b_doors"
    assert game.bomb_fuse_remaining == game.rules.bomb_fuse_tactical_rounds

    start_activation(game, defender)
    game.execute_action(defender, "move_b_site")
    complete_movement(game)
    assert defender.position_id == "b_site"
    assert game._is_defuse_enabled(defender) == (
        "breachpoint-error-not-enough-ap",
        {"needed": game.rules.defuse_cost, "remaining": 1},
    )
    assert game.bomb_fuse_remaining == game.rules.bomb_fuse_tactical_rounds

    start_activation(game, defender)
    game.execute_action(defender, "defuse")
    responder = game.current_player
    assert isinstance(responder, BreachPointPlayer)
    game.execute_action(responder, "end_turn")
    assert game.last_round_win_reason == WIN_DEFUSED
    assert game._squad_score(TEAM_COUNTER_TERRORISTS) == 1


def test_defuse_kit_allows_move_then_interruptible_defuse() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round
    defender.position_id = "ct_spawn"
    defender.equipment_counts = {DEFUSE_KIT.id: 1}
    terrorist.position_id = "b_site"
    start_activation(game, defender)

    game.execute_action(defender, "move_a_site")
    complete_movement(game)
    assert defender.action_points == 1
    game.execute_action(defender, "defuse")

    assert game.defusing_player_id == defender.id
    responder = game.current_player
    assert isinstance(responder, BreachPointPlayer)
    assert responder.team_index == TEAM_TERRORISTS
    responder.position_id = "a_ramp"
    assert game._squad_score(TEAM_COUNTER_TERRORISTS) == 0

    game.execute_action(responder, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert not game.defusing_player_id
    assert defender.health < game.rules.max_health
    assert game.last_round_win_reason == ""


def test_fully_evaded_pistol_does_not_interrupt_defuse() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round
    defender.position_id = "a_site"
    defender.guard_points = game.rules.maximum_evasion_points
    start_activation(game, defender)
    defender.guard_points = game.rules.maximum_evasion_points

    game.execute_action(defender, "defuse")
    responder = game.current_player
    assert isinstance(responder, BreachPointPlayer)
    responder.position_id = "ct_mid"
    game.execute_action(responder, f"shoot_{defender.id}")
    complete_weapon_fire(game)

    assert defender.health == game.rules.max_health
    assert game.defusing_player_id == defender.id
    game.execute_action(responder, "end_turn")
    assert game.last_round_win_reason == WIN_DEFUSED


def test_damage_interrupts_pending_plant_without_dropping_bomb() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    carrier.position_id = "a_site"
    defender.position_id = "a_ramp"

    game.execute_action(carrier, "plant")
    assert game.current_player is defender
    game.execute_action(defender, f"shoot_{carrier.id}")
    complete_weapon_fire(game)

    assert game.bomb_state == BOMB_CARRIED
    assert game.bomb_carrier_id == carrier.id
    assert game.planting_player_id == ""
    assert carrier.health == 68


def test_pending_plant_limits_an_already_acted_ct_response_to_one_ap() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 2)
    responder = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    other_defender.eliminated = True
    other_defender.health = 0
    game.round_acted_player_ids = ["p1", responder.id]
    game.bomb_carrier_id = carrier.id
    carrier.position_id = "b_site"
    start_activation(game, carrier)
    clear_spoken(game)

    game.execute_action(carrier, "plant")

    assert game.bomb_state == BOMB_PLANTING
    assert game.current_player is responder
    assert responder.action_points == game.rules.repeat_objective_response_action_points
    assert game.reaction_window.kind == REACTION_PLANT
    assert not game.reaction_window.consumes_activation
    assert "Your plant response. You have 1 AP." in spoken_text(game, 1)
    assert "Player2 begins a plant response." in spoken_text(game, 0)


def test_plant_response_resumes_after_the_planter_without_reordering_players() -> None:
    game = make_game(start=True, player_count=8)
    planter = tactical_player(game, 2)
    remote_next_player = tactical_player(game, 3)
    responder = tactical_player(game, 5)
    later_player = tactical_player(game, 6)
    planter.position_id = responder.position_id = "a_site"
    for defender in game._players_on_team(TEAM_COUNTER_TERRORISTS):
        if defender.id != responder.id:
            defender.position_id = "b_site"
    game.bomb_carrier_id = planter.id
    game.round_acted_player_ids = [
        tactical_player(game, 0).id,
        tactical_player(game, 1).id,
    ]
    original_turn_order = list(game.turn_player_ids)
    start_activation(game, planter)

    game.execute_action(planter, "plant")

    assert game.current_player is responder
    assert game.reaction_window.resume_after_player_id == planter.id
    assert game.reaction_window.consumes_activation
    game.execute_action(responder, "end_turn")

    assert game.bomb_state == BOMB_PLANTED
    assert game.turn_player_ids == original_turn_order
    assert game.current_player is remote_next_player
    game.execute_action(remote_next_player, "end_turn")
    assert game.current_player is tactical_player(game, 4)
    assert game.current_player is not later_player


def test_interrupted_plant_response_restores_the_suspended_turn_order() -> None:
    game = make_game(start=True, player_count=8)
    planter = tactical_player(game, 2)
    remote_next_player = tactical_player(game, 3)
    responder = tactical_player(game, 5)
    planter.position_id = responder.position_id = "a_site"
    for defender in game._players_on_team(TEAM_COUNTER_TERRORISTS):
        if defender.id != responder.id:
            defender.position_id = "b_site"
    game.bomb_carrier_id = planter.id
    game.round_acted_player_ids = [
        tactical_player(game, 0).id,
        tactical_player(game, 1).id,
    ]
    start_activation(game, planter)

    game.execute_action(planter, "plant")
    game.execute_action(responder, f"shoot_{planter.id}")
    complete_weapon_fire(game)

    assert game.bomb_state == BOMB_CARRIED
    assert game.current_player is responder
    assert game.reaction_window.resume_after_player_id == planter.id

    restored = BreachPointGame.from_json(game.to_json())
    for restored_player in restored.players:
        restored.attach_user(
            restored_player.id,
            MockUser(restored_player.name, uuid=restored_player.id),
        )
    restored.rebuild_runtime_state()
    restored_responder = tactical_player(restored, 5)

    assert restored.current_player is restored_responder
    assert (
        restored.reaction_window.resume_after_player_id
        == tactical_player(restored, 2).id
    )
    restored_responder.reconnect_grace_ticks = 0
    restored.execute_action(restored_responder, "end_turn")
    assert restored.current_player is tactical_player(restored, 3)
    assert restored.current_player.id == remote_next_player.id
    assert not restored.reaction_window.is_open


def test_interrupted_defuse_response_restores_the_suspended_turn_order() -> None:
    game = make_game(start=True, player_count=8)
    defuser = tactical_player(game, 3)
    remote_next_player = tactical_player(game, 4)
    responder = tactical_player(game, 6)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round
    defuser.position_id = responder.position_id = "a_site"
    for terrorist in game._players_on_team(TEAM_TERRORISTS):
        if terrorist.id != responder.id:
            terrorist.position_id = "b_site"
    game.round_acted_player_ids = [
        tactical_player(game, 0).id,
        tactical_player(game, 1).id,
        tactical_player(game, 2).id,
    ]
    start_activation(game, defuser)

    game.execute_action(defuser, "defuse")
    game.execute_action(responder, f"shoot_{defuser.id}")
    complete_weapon_fire(game)

    assert game.defusing_player_id == ""
    assert game.current_player is responder
    assert game.reaction_window.resume_after_player_id == defuser.id
    game.execute_action(responder, "end_turn")
    assert game.current_player is remote_next_player
    assert not game.reaction_window.is_open


def test_objective_responses_prioritize_a_co_located_enemy() -> None:
    plant_game = make_game(start=True, player_count=6)
    planter = tactical_player(plant_game, 2)
    local_defender = tactical_player(plant_game, 1)
    remote_defender = tactical_player(plant_game, 3)
    planter.position_id = local_defender.position_id = "a_site"
    remote_defender.position_id = "b_site"
    plant_game.bomb_carrier_id = planter.id
    plant_game.round_acted_player_ids = [
        tactical_player(plant_game, 0).id,
        local_defender.id,
    ]
    start_activation(plant_game, planter)

    plant_game.execute_action(planter, "plant")

    assert plant_game.current_player is local_defender
    assert plant_game.reaction_window.kind == REACTION_PLANT
    assert plant_game.reaction_window.responding_player_id == local_defender.id
    plant_game.execute_action(local_defender, "end_turn")
    assert plant_game.bomb_state == BOMB_PLANTED
    assert not plant_game.reaction_window.is_open
    assert plant_game.current_player is remote_defender

    defuse_game = make_game(start=True, player_count=6)
    defuser = tactical_player(defuse_game, 3)
    local_terrorist = tactical_player(defuse_game, 0)
    remote_terrorist = tactical_player(defuse_game, 4)
    defuser.position_id = local_terrorist.position_id = "a_site"
    remote_terrorist.position_id = "b_site"
    defuse_game.bomb_state = BOMB_PLANTED
    defuse_game.bomb_carrier_id = ""
    defuse_game.bomb_location_id = "a_site"
    defuse_game.bomb_fuse_remaining = defuse_game.rules.bomb_fuse_tactical_rounds
    defuse_game.bomb_planted_tactical_round = defuse_game.tactical_round
    defuse_game.round_acted_player_ids = [local_terrorist.id]
    start_activation(defuse_game, defuser)

    defuse_game.execute_action(defuser, "defuse")

    assert defuse_game.current_player is local_terrorist
    assert defuse_game.reaction_window.kind == REACTION_DEFUSE
    assert defuse_game.reaction_window.responding_player_id == local_terrorist.id


def test_hidden_plant_warns_ct_without_revealing_planter_or_site() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    carrier.position_id = "b_site"
    clear_spoken(game)

    game.execute_action(carrier, "plant")

    for defender_index in (1, 3):
        messages = spoken_text(game, defender_index)
        assert "Plant attempt detected. CT has one response." in messages
        assert all(
            "Player1" not in text and "Bombsite B" not in text for text in messages
        )
    assert any("Bombsite B" in text for text in spoken_text(game, 2))


def test_planting_round_does_not_consume_fuse_but_later_rounds_do() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    carrier.position_id = "b_site"
    game.execute_action(carrier, "plant")
    game._complete_pending_plant()

    assert not game._complete_tactical_round()
    assert game.bomb_fuse_remaining == 3
    game.tactical_round = 2
    assert not game._complete_tactical_round()
    assert game.bomb_fuse_remaining == 2
    game.tactical_round = 3
    assert not game._complete_tactical_round()
    assert game.bomb_fuse_remaining == 1
    clear_spoken(game)
    game.tactical_round = 4
    assert game._complete_tactical_round()
    assert game.status == "playing"
    assert game.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
    assert game._squad_score(TEAM_TERRORISTS) == 0
    complete_timed_action(game, BOMB_DETONATION_SEQUENCE_TAG)
    assert game._squad_score(TEAM_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_DETONATED
    assert game.round == 2
    for player in game.players:
        user = game.get_user(player)
        assert isinstance(user, MockUser)
        explosion = next(
            message
            for message in user.messages
            if message.type == "play_sound"
            and message.data.get("name") == BOMB_EXPLOSION_ASSET
        )
        assert explosion.data.get("position") is None
        assert explosion.data.get("attenuation") is None


def test_postplant_phase_labels_replace_the_expired_preplant_counter() -> None:
    game = make_game(start=True)
    game.tactical_round = game.rules.preplant_tactical_round_limit + 1
    game.bomb_state = BOMB_PLANTED
    game.bomb_location_id = "b_site"
    game.bomb_carrier_id = ""
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round

    assert game._round_phase_label("en") == (
        "Bomb planted; 3 full tactical rounds remain"
    )
    clear_spoken(game)
    game._announce_tactical_round_start()
    assert "Bomb planted; 3 full tactical rounds remain." in spoken_text(game, 0)
    assert all("7 of 6" not in text for text in spoken_text(game, 0))

    game.tactical_round += 1
    assert game._round_phase_label("en") == "Bomb planted 1 of 3"
    clear_spoken(game)
    start_activation(game, tactical_player(game, 0))
    assert spoken_text(game, 0) == ["Your turn. You have 2 AP."]
    assert all("of 6" not in text for text in spoken_text(game, 0))
    game.bomb_fuse_remaining = 1
    assert game._round_phase_label("en") == "Bomb planted 3 of 3"


def test_last_second_plant_receives_the_full_post_plant_fuse() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    responder = tactical_player(game, 1)
    carrier.position_id = "a_site"
    for player_index in (2, 3):
        eliminated = tactical_player(game, player_index)
        eliminated.eliminated = True
        eliminated.health = 0
    game.tactical_round = game.rules.preplant_tactical_round_limit

    game.execute_action(carrier, "plant")
    game.execute_action(responder, "end_turn")

    assert game.bomb_state == BOMB_PLANTED
    assert game.bomb_fuse_remaining == game.rules.bomb_fuse_tactical_rounds
    assert game.tactical_round == game.rules.preplant_tactical_round_limit + 1
    assert game.round == 1

    for expected_fuse in (2, 1, 0):
        game.execute_action(carrier, "end_turn")
        game.execute_action(responder, "end_turn")
        if expected_fuse:
            assert game.bomb_fuse_remaining == expected_fuse
            assert game.round == 1

    assert game.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
    complete_timed_action(game, BOMB_DETONATION_SEQUENCE_TAG)
    assert game._squad_score(TEAM_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_DETONATED
    assert game.round == 2


def test_preplant_round_limit_finishes_for_counter_terrorists() -> None:
    game = make_game(start=True)
    game.tactical_round = game.rules.preplant_tactical_round_limit

    assert game._complete_tactical_round()
    assert game.status == "playing"
    assert game._squad_score(TEAM_COUNTER_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_TIME
    assert game.round == 2


def test_round_transition_cleans_round_audio_and_waits_nine_seconds() -> None:
    game = make_game(start=True)
    winner = tactical_player(game, 0)
    loser = tactical_player(game, 1)
    spectator_user = MockUser("Spectator", uuid="spectator")
    game.add_spectator("Spectator", spectator_user)
    fire = set_area_effect(game, MOLOTOV, "a_site")
    game._start_fire_audio(fire.node_id)
    fire_handle = game._fire_audio_handle(fire.node_id)
    assert any(state.handle == fire_handle for state in game.active_audio.values())
    for player in game.players:
        user = game.get_user(player)
        if isinstance(user, MockUser):
            user.clear_messages()


    game._play_global_asset(
        BOMB_EXPLOSION_ASSET,
        handle=BOMB_EXPLOSION_HANDLE,
    )
    start_tick = game.sound_scheduler_tick

    game._finish_combat_round(TEAM_TERRORISTS, WIN_ELIMINATION)

    assert ROUND_TRANSITION_TICKS == 9 * TICKS_PER_SECOND
    assert game.phase == PHASE_COMBAT
    assert game.has_active_sequence(tag=ROUND_TRANSITION_SEQUENCE_TAG)
    assert game.is_sequence_gameplay_locked()
    assert game.is_sequence_bot_paused()
    assert not any(state.handle == fire_handle for state in game.active_audio.values())
    winner_user = game.get_user(winner)
    loser_user = game.get_user(loser)
    assert isinstance(winner_user, MockUser)
    assert isinstance(loser_user, MockUser)
    assert any(
        message.type == "play_sound"
        and [segment["asset"] for segment in message.data.get("segments", [])]
        == [RADIO_TERRORISTS_WIN_ASSET]
        for message in winner_user.messages
    )
    assert any(
        message.type == "play_music"
        and message.data.get("name") == MUSIC_ROUND_WON_ASSET
        and message.data.get("kind") == "music"
        and message.data.get("looping") is False
        and message.data.get("handle") == MUSIC_RESULT_HANDLE
        for message in winner_user.messages
    )
    assert any(
        message.type == "play_music"
        and message.data.get("name") == MUSIC_ROUND_LOST_ASSET
        and message.data.get("kind") == "music"
        and message.data.get("looping") is False
        and message.data.get("handle") == MUSIC_RESULT_HANDLE
        for message in loser_user.messages
    )
    assert any(
        message.type == "play_music"
        and message.data.get("name") == MUSIC_ROUND_WON_ASSET
        and message.data.get("kind") == "music"
        and message.data.get("looping") is False
        and message.data.get("handle") == MUSIC_RESULT_HANDLE
        for message in spectator_user.messages
    )

    complete_round_transition(game)

    assert game.sound_scheduler_tick - start_tick == ROUND_TRANSITION_TICKS
    assert game.phase == PHASE_BUY
    assert not game.has_active_sequence(tag=ROUND_TRANSITION_SEQUENCE_TAG)
    assert not game.area_effects
    stopped_handles = {
        message.data.get("handle")
        for message in winner_user.messages
        if message.type in {"audio", "stop_music"}
        and message.data.get("command") == "stop"
    }
    assert {
        BOMB_EXPLOSION_HANDLE,
        MUSIC_CONTEXT_HANDLE,
        MUSIC_RESULT_HANDLE,
        ROUND_STINGER_HANDLE,
        RADIO_CUE_HANDLE,
    } <= stopped_handles
    assert any(
        message.type == "play_music"
        and message.data.get("name") == MUSIC_ROUND_START_ASSET
        and message.data.get("kind") == "music"
        and message.data.get("looping") is True
        and message.data.get("handle") == MUSIC_CONTEXT_HANDLE
        for message in winner_user.messages
    )


def test_action_music_uses_bgm_loop_and_stops_after_cs_ten_second_window() -> None:
    game = make_game(start=True)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)

    action_music = [
        message
        for message in user.messages
        if message.type == "play_music"
        and message.data.get("name") in MUSIC_ACTION_START_ASSETS
    ]
    assert action_music
    assert action_music[-1].data.get("kind") == "music"
    assert action_music[-1].data.get("looping") is True
    assert action_music[-1].data.get("handle") == MUSIC_CONTEXT_HANDLE
    assert game.has_active_sequence(tag=MUSIC_ACTION_STOP_SEQUENCE_TAG)
    assert any(
        state.kind == "music"
        and state.handle == MUSIC_CONTEXT_HANDLE
        and state.loop is True
        for state in game.active_audio.values()
    )

    complete_timed_action(game, MUSIC_ACTION_STOP_SEQUENCE_TAG)

    assert any(
        message.type == "stop_music"
        and message.data.get("handle") == MUSIC_CONTEXT_HANDLE
        for message in user.messages
    )
    assert not any(
        state.kind == "music" and state.handle == MUSIC_CONTEXT_HANDLE
        for state in game.active_audio.values()
    )


def test_final_round_and_match_point_stinger_follow_cs_triggers() -> None:
    game = make_game(start=True, match_format="mr7")
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    game.cancel_sequences_by_tag(MUSIC_ACTION_STOP_SEQUENCE_TAG)

    user.clear_messages()
    game.round = game.match_format.rounds_per_half
    game._announce_combat_round_start()
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == FINAL_ROUND_STINGER_ASSET
        and message.data.get("kind") == "sfx"
        and message.data.get("handle") == ROUND_STINGER_HANDLE
        and message.data.get("volume") == 60
        for message in user.messages
    )

    user.clear_messages()
    game.round = game.match_format.rounds_per_half + 1
    game._announce_combat_round_start()
    assert not any(
        message.type == "play_sound"
        and message.data.get("name") == FINAL_ROUND_STINGER_ASSET
        for message in user.messages
    )

    user.clear_messages()
    game.round += 1
    game._team_manager.teams[0].total_score = game.match_format.rounds_to_win - 1
    game._announce_combat_round_start()
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == FINAL_ROUND_STINGER_ASSET
        and message.data.get("handle") == ROUND_STINGER_HANDLE
        for message in user.messages
    )


def test_defuse_result_radio_chains_objective_and_team_announcements() -> None:
    game = make_game(start=True)
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game._finish_combat_round(TEAM_COUNTER_TERRORISTS, WIN_DEFUSED)

    assert any(
        message.type == "play_sound"
        and [segment["asset"] for segment in message.data.get("segments", [])]
        == [RADIO_BOMB_DEFUSED_ASSET, RADIO_COUNTER_TERRORISTS_WIN_ASSET]
        for message in user.messages
    )


def test_final_match_result_waits_nine_seconds_then_plays_victory_with_game_over() -> None:
    game = make_game(start=True, match_format="mr7")
    listener = tactical_player(game, 0)
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    winning_squad = game._squad_for_side(TEAM_TERRORISTS)
    game._team_manager.teams[winning_squad].total_score = (
        game.match_format.rounds_to_win - 1
    )
    user.clear_messages()
    start_tick = game.sound_scheduler_tick

    game._finish_combat_round(TEAM_TERRORISTS, WIN_ELIMINATION)

    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == MATCH_RESULT_SEQUENCE_TAG
    )
    assert sequence.next_tick - start_tick == MATCH_RESULT_DELAY_TICKS
    assert game.status == "playing"
    assert any(
        message.type == "play_sound"
        and [segment["asset"] for segment in message.data.get("segments", [])]
        == [RADIO_TERRORISTS_WIN_ASSET]
        for message in user.messages
    )
    assert not any(
        message.type == "play_sound"
        and message.data.get("name") == MATCH_VICTORY_ASSET
        for message in user.messages
    )

    for _ in range(MATCH_RESULT_DELAY_TICKS - 1):
        game.process_scheduled_sounds()
        game.process_sequences()
    assert game.status == "playing"

    game.process_scheduled_sounds()
    game.process_sequences()

    assert game.status == "finished"
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == MATCH_VICTORY_ASSET
        for message in user.messages
    )


def test_round_income_loss_bonus_and_equipment_retention_follow_squads() -> None:
    game = make_game(start=True)
    terrorist_survivor = tactical_player(game, 0)
    defender_casualty = tactical_player(game, 1)
    terrorist_survivor.sidearm_weapon_id = DESERT_EAGLE.id
    terrorist_survivor.primary_weapon_id = AK47.id
    terrorist_survivor.equipped_weapon_id = AK47.id
    terrorist_survivor.armor = 1
    defender_casualty.sidearm_weapon_id = DESERT_EAGLE.id
    defender_casualty.primary_weapon_id = M4.id
    defender_casualty.equipped_weapon_id = M4.id
    defender_casualty.armor = 1
    defender_casualty.eliminated = True
    defender_casualty.health = 0

    game._finish_combat_round(TEAM_TERRORISTS, WIN_ELIMINATION)
    complete_round_transition(game)

    assert game.phase == PHASE_BUY
    assert terrorist_survivor.cash == 800 + game.economy.win_reward(WIN_ELIMINATION)
    assert terrorist_survivor.sidearm_weapon_id == DESERT_EAGLE.id
    assert terrorist_survivor.primary_weapon_id == AK47.id
    assert terrorist_survivor.armor == 1
    assert defender_casualty.cash == 800 + game.economy.loss_reward(1)
    assert defender_casualty.sidearm_weapon_id == USP_S.id
    assert defender_casualty.primary_weapon_id == ""
    assert defender_casualty.armor == 0
    assert game.squad_loss_streaks == [0, 2]


def test_round_income_follows_persistent_squads_after_side_swap() -> None:
    game = make_game(start=True)
    original_terrorists = [
        player for player in game.players if player.squad_index == TEAM_TERRORISTS
    ]
    original_counter_terrorists = [
        player
        for player in game.players
        if player.squad_index == TEAM_COUNTER_TERRORISTS
    ]
    game._swap_sides()
    for player in game.players:
        player.cash = 0

    game._settle_round_economy(TEAM_TERRORISTS, WIN_ELIMINATION)

    assert all(
        player.cash == game.economy.win_reward(WIN_ELIMINATION)
        for player in original_counter_terrorists
    )
    assert all(
        player.cash == game.economy.loss_reward(game.economy.initial_loss_count)
        for player in original_terrorists
    )


def test_defuse_income_includes_plant_loss_bonus_and_objective_reward() -> None:
    game = make_game(start=True)
    for player in game.players:
        tactical = game._breach_player(player)
        assert tactical is not None
        tactical.cash = 0

    game._settle_round_economy(TEAM_COUNTER_TERRORISTS, WIN_DEFUSED)

    for terrorist in game._players_on_team(TEAM_TERRORISTS):
        assert terrorist.cash == (
            game.economy.loss_reward(1) + game.economy.plant_team_bonus
        )
    for defender in game._players_on_team(TEAM_COUNTER_TERRORISTS):
        assert defender.cash == game.economy.win_reward(WIN_DEFUSED)


def test_round_income_updates_a_reserved_player_without_an_attached_user() -> None:
    game = make_game(start=True)
    reserved_player = tactical_player(game, 2)
    reserved_player.cash = 0
    game._users.pop(reserved_player.id)

    game._settle_round_economy(TEAM_TERRORISTS, WIN_ELIMINATION)

    assert reserved_player.cash == game.economy.win_reward(WIN_ELIMINATION)


def test_win_steps_loss_counter_down_instead_of_resetting_it() -> None:
    game = make_game(start=True)
    game.squad_loss_streaks = [game.economy.maximum_loss_count, 0]

    game._settle_round_economy(TEAM_TERRORISTS, WIN_ELIMINATION)

    assert game.squad_loss_streaks == [game.economy.maximum_loss_count - 1, 1]


def test_halftime_and_overtime_start_fresh_side_appropriate_economies() -> None:
    halftime = make_game(start=True, match_format="mr7")
    halftime.round = halftime.match_format.rounds_per_half
    for player in halftime.players:
        tactical = halftime._breach_player(player)
        assert tactical is not None
        tactical.cash = 9_000
        tactical.sidearm_weapon_id = DESERT_EAGLE.id
        tactical.primary_weapon_id = (
            AK47.id if tactical.team_index == TEAM_TERRORISTS else M4.id
        )
        tactical.armor = 1

    halftime._finish_combat_round(TEAM_TERRORISTS, WIN_ELIMINATION)
    complete_round_transition(halftime)

    assert halftime.side_squad_indexes == [1, 0]
    assert all(
        player.cash == halftime.economy.starting_cash for player in halftime.players
    )
    assert all(player.primary_weapon_id == "" for player in halftime.players)
    assert all(
        player.sidearm_weapon_id == get_default_sidearm(player.team_index).id
        for player in halftime.players
    )
    assert all(
        player.equipped_weapon_id == get_default_sidearm(player.team_index).id
        for player in halftime.players
    )

    overtime = make_game(start=True, match_format="mr7")
    overtime._team_manager.teams[0].total_score = 7
    overtime._team_manager.teams[1].total_score = 6
    overtime.round = overtime.match_format.regulation_rounds
    overtime._finish_combat_round(overtime._side_for_squad(1), WIN_DEFUSED)
    complete_round_transition(overtime)
    assert overtime.overtime_period == 1
    assert all(
        player.cash == overtime.economy.overtime_cash for player in overtime.players
    )


def test_elimination_rules_change_after_bomb_is_planted() -> None:
    game = make_game(start=True)
    terrorist_one = tactical_player(game, 0)
    terrorist_two = tactical_player(game, 2)
    terrorist_one.eliminated = True
    terrorist_one.health = 0
    terrorist_two.eliminated = True
    terrorist_two.health = 0

    game.bomb_state = BOMB_PLANTED
    assert not game._check_elimination_victory()
    assert game.status == "playing"

    game.bomb_state = BOMB_DROPPED
    assert game._check_elimination_victory()
    assert game._squad_score(TEAM_COUNTER_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_ELIMINATION


def test_eliminating_all_counter_terrorists_finishes_for_terrorists() -> None:
    game = make_game(start=True)
    for defender in game._players_on_team(TEAM_COUNTER_TERRORISTS):
        defender.eliminated = True
        defender.health = 0

    assert game._check_elimination_victory()
    assert game._squad_score(TEAM_TERRORISTS) == 1
    assert game.last_round_win_reason == WIN_ELIMINATION


def test_mr7_halftime_swap_and_regulation_victory_follow_squads() -> None:
    game = make_game(start=True, match_format="mr7")

    for squad_index in (0, 1, 0, 1, 0, 1, 0):
        game._finish_combat_round(game._side_for_squad(squad_index), WIN_ELIMINATION)
        complete_round_transition(game)

    assert game.round == 8
    assert game._squad_score(0) == 4
    assert game._squad_score(1) == 3
    assert game.side_squad_indexes == [1, 0]
    assert tactical_player(game, 0).squad_index == 0
    assert tactical_player(game, 0).team_index == TEAM_COUNTER_TERRORISTS

    for _ in range(4):
        game._finish_combat_round(game._side_for_squad(0), WIN_ELIMINATION)
        if game.status == "playing":
            complete_round_or_match_transition(game)

    assert game.status == "finished"
    assert game.winning_team_index == 0
    assert game.win_reason == MATCH_REGULATION
    assert game._squad_score(0) == 8


def test_regulation_tie_can_end_as_draw() -> None:
    game = make_game(
        start=True,
        match_format="mr7",
        overtime_mode=OVERTIME_DRAW,
    )
    game._team_manager.teams[0].total_score = 7
    game._team_manager.teams[1].total_score = 6
    game.round = game.match_format.regulation_rounds
    game.side_squad_indexes = [1, 0]
    game._apply_current_sides(
        [player for player in game.players if isinstance(player, BreachPointPlayer)]
    )

    game._finish_combat_round(game._side_for_squad(1), WIN_DEFUSED)
    complete_match_result(game)

    assert game.status == "finished"
    assert game.winning_team_index == -1
    assert game.win_reason == MATCH_DRAW
    result = game.build_game_result()
    assert result.custom_data["winner_ids"] == []


def test_tied_mr12_enters_mr3_overtime_and_requires_four_rounds() -> None:
    game = make_game(start=True, match_format="mr12")
    game._team_manager.teams[0].total_score = 12
    game._team_manager.teams[1].total_score = 11
    game.round = game.match_format.regulation_rounds
    game.side_squad_indexes = [1, 0]
    game._apply_current_sides(
        [player for player in game.players if isinstance(player, BreachPointPlayer)]
    )

    game._finish_combat_round(game._side_for_squad(1), WIN_DEFUSED)
    complete_round_transition(game)
    assert game.status == "playing"
    assert game.overtime_period == 1
    assert game.overtime_round == 1
    assert game.side_squad_indexes == [0, 1]

    for _ in range(4):
        game._finish_combat_round(game._side_for_squad(0), WIN_ELIMINATION)
        if game.status == "playing":
            complete_round_or_match_transition(game)

    assert game.status == "finished"
    assert game.winning_team_index == 0
    assert game.win_reason == MATCH_OVERTIME
    assert game._squad_score(0) == 16


def test_tied_mr3_period_restarts_overtime_without_losing_score() -> None:
    game = make_game(start=True, match_format="mr7")
    game._team_manager.teams[0].total_score = 7
    game._team_manager.teams[1].total_score = 7
    game.round = game.match_format.regulation_rounds + 1
    game.overtime_period = 1
    game.overtime_round = 1
    game.overtime_start_scores = [7, 7]

    for squad_index in (0, 1, 0, 1, 0, 1):
        game._finish_combat_round(game._side_for_squad(squad_index), WIN_ELIMINATION)
        complete_round_transition(game)

    assert game.status == "playing"
    assert game.overtime_period == 2
    assert game.overtime_round == 1
    assert game.overtime_start_scores == [10, 10]
    assert game.side_squad_indexes == [0, 1]
    assert [
        game._squad_score(index) for index in (TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS)
    ] == [10, 10]


def test_touch_menu_exposes_gameplay_and_status_actions_in_stable_order() -> None:
    game = make_game(start=True, touch_indexes={0})
    player = tactical_player(game, 0)
    turn_set = game.get_action_set(player, "turn")
    standard_set = game.get_action_set(player, "standard")
    assert turn_set is not None
    assert standard_set is not None

    visible_turn_ids = [
        action.action.id for action in turn_set.get_visible_actions(game, player)
    ]
    assert visible_turn_ids == [
        "combat_menu_summary",
        "combat_menu_move",
        "combat_menu_attack",
        "combat_menu_utility",
        "combat_menu_angle",
        "combat_menu_objective",
        "combat_menu_weapons",
        "combat_menu_loot",
        "end_turn",
    ]
    visible_standard_ids = [
        action.action.id for action in standard_set.get_visible_actions(game, player)
    ]
    assert visible_standard_ids[-9:] == [
        "read_vitals",
        "read_position",
        "read_map",
        "read_teammates",
        "read_enemies",
        "read_bomb",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]


def test_combat_submenus_isolate_actions_and_restore_their_parent_focus() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    player.primary_weapon_id = AWP.id
    player.equipped_weapon_id = AWP.id
    game._set_full_weapon_ammunition(player, AWP)
    player.utility_counts = {SMOKE_GRENADE.id: 1, FLASHBANG.id: 1}

    game.execute_action(player, "combat_menu_weapons")
    game.flush_menus()
    assert turn_menu_ids(game, 0) == [
        "equip_primary",
        "equip_sidearm",
        "reload",
        "combat_menu_back",
    ]

    game.handle_event(player, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "combat_menu_weapons"
    )

    game.execute_action(player, "combat_menu_utility")
    game.execute_action(player, "combat_menu_utility_smoke")
    game.flush_menus()
    assert turn_menu_ids(game, 0) == [
        "throw_smoke_t_spawn",
        "throw_smoke_outside_long",
        "throw_smoke_mid",
        "throw_smoke_outside_tunnels",
        "combat_menu_back",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "throw_smoke_t_spawn"
    )

    game.handle_event(player, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "combat_menu_utility_smoke"
    )
    game.handle_event(player, {"type": "keybind", "key": "x"})
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "combat_menu_utility"
    )


def test_move_menu_leads_with_spatial_context_and_private_visible_contacts() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    enemy.position_id = teammate.position_id = "mid"

    game.execute_action(mover, "combat_menu_move")
    game.flush_menus()

    assert turn_menu_ids(game, 0)[0] == "combat_menu_location"
    assert "You are at T Spawn" in turn_menu_item(
        game,
        0,
        "combat_menu_location",
    ).text
    move_label = turn_menu_item(game, 0, "move_mid").text
    assert f"{enemy.name}, enemy" in move_label
    assert f"{teammate.name}, teammate" in move_label

    set_area_effect(game, SMOKE_GRENADE, "mid")
    game.refresh_menus(mover)
    game.flush_menus()
    smoked_label = turn_menu_item(game, 0, "move_mid").text
    assert enemy.name not in smoked_label
    assert teammate.name not in smoked_label

    game.area_effects = []
    mover.flash_penalty = FLASHBANG.activation_penalty
    game.refresh_menus(mover)
    game.flush_menus()
    blinded_label = turn_menu_item(game, 0, "move_mid").text
    assert enemy.name not in blinded_label
    assert teammate.name not in blinded_label


def test_combat_root_leads_with_concise_health_weapon_and_los_summary() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    enemy.position_id = teammate.position_id = "mid"
    player.health = 73

    game.refresh_menus(player)
    game.flush_menus()

    assert turn_menu_ids(game, 0)[0] == "combat_menu_summary"
    summary = turn_menu_item(game, 0, "combat_menu_summary")
    summary_action = game.find_action(player, "combat_menu_summary")
    assert summary_action is not None
    assert not game.resolve_action(player, summary_action).enabled
    assert "HP 73" in summary.text
    assert "equipped Glock" in summary.text
    assert f"{enemy.name} at Mid, enemy" in summary.text
    assert f"{teammate.name} at Mid, teammate" in summary.text

    set_area_effect(game, SMOKE_GRENADE, "mid")
    game.refresh_menus(player)
    game.flush_menus()
    obscured_summary = turn_menu_item(game, 0, "combat_menu_summary").text
    assert enemy.name not in obscured_summary
    assert teammate.name not in obscured_summary


def test_utility_and_angle_targets_mark_position_and_obey_personal_los() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    enemy.position_id = "mid"
    player.utility_counts = {SMOKE_GRENADE.id: 1}
    player.primary_weapon_id = AWP.id
    player.equipped_weapon_id = AWP.id
    game._set_full_weapon_ammunition(player, AWP)

    game.execute_action(player, "combat_menu_utility")
    game.execute_action(player, "combat_menu_utility_smoke")
    game.flush_menus()
    assert "current location" in turn_menu_item(
        game,
        0,
        "throw_smoke_t_spawn",
    ).text
    assert f"{enemy.name}, enemy" in turn_menu_item(
        game,
        0,
        "throw_smoke_mid",
    ).text

    game.execute_action(player, "combat_menu_back")
    game.execute_action(player, "combat_menu_back")
    game.execute_action(player, "combat_menu_angle")
    game.flush_menus()
    assert f"{enemy.name}, enemy" in turn_menu_item(
        game,
        0,
        "hold_angle_mid",
    ).text

    set_area_effect(game, SMOKE_GRENADE, "mid")
    game.refresh_menus(player)
    game.flush_menus()
    assert enemy.name not in turn_menu_item(
        game,
        0,
        "hold_angle_mid",
    ).text


def test_movement_keeps_locked_combat_root_visible_and_restores_move_focus() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    user = game.get_user(mover)
    assert isinstance(user, MockUser)

    game.execute_action(mover, "combat_menu_move")
    game.execute_action(mover, "move_mid")
    game.flush_menus()

    assert game.has_active_sequence(tag=MOVEMENT_AUDIO_SEQUENCE_TAG)
    assert turn_menu_ids(game, 0) == [
        "combat_menu_summary",
        "combat_menu_move",
        "combat_menu_attack",
        "combat_menu_utility",
        "combat_menu_angle",
        "combat_menu_objective",
        "combat_menu_weapons",
        "combat_menu_loot",
        "end_turn",
    ]
    assert last_turn_menu_message(game, 0).data["selection_id"] == (
        "combat_menu_move"
    )
    clear_spoken(game)
    game.execute_action(mover, "combat_menu_move")
    assert any("You are moving to Mid" in text for text in spoken_text(game, 0))

    complete_movement(game)
    game.flush_menus()
    assert game.current_player is mover
    assert mover.position_id == "mid"
    assert turn_menu_ids(game, 0)[0] == "combat_menu_summary"


def test_desktop_status_actions_remain_available_in_actions_menu() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    standard_set = game.get_action_set(player, "standard")
    assert standard_set is not None

    assert game._is_read_map_hidden(player) == Visibility.HIDDEN
    enabled_ids = [
        action.action.id for action in standard_set.get_enabled_actions(game, player)
    ]
    assert "read_map" in enabled_ids
    assert "read_vitals" in enabled_ids
    assert "read_position" in enabled_ids
    assert "read_teammates" in enabled_ids
    assert "read_enemies" in enabled_ids
    assert "check_scores" in enabled_ids
    assert "check_scores_detailed" in enabled_ids


def test_game_keybinds_use_active_scope_without_base_collisions() -> None:
    game = make_game()
    expected = {
        "h": "read_vitals",
        "m": "read_map",
        "p": "read_position",
        "o": "read_bomb",
        "v": "read_teammates",
        "w": "read_enemies",
        "e": "context_finish_or_end",
        "r": "reload",
        "x": "context_menu_back",
    }
    for key, action_id in expected.items():
        bindings = [
            binding for binding in game._keybinds[key] if action_id in binding.actions
        ]
        assert len(bindings) == 1
        assert bindings[0].state == KeybindState.ACTIVE
    assert any(
        binding.actions == ["context_finish_or_end"]
        for binding in game._keybinds["e"]
    )
    assert any(
        binding.actions == ["context_menu_back"] for binding in game._keybinds["x"]
    )
    for digit in map(str, range(1, 10)):
        bindings = [
            binding
            for binding in game._keybinds[digit]
            if binding.actions == [f"buy_shortcut_{digit}"]
        ]
        assert len(bindings) == 1
        assert bindings[0].state == KeybindState.ACTIVE
    for key, action_id in (("s", "check_scores"), ("shift+s", "check_scores_detailed")):
        bindings = [
            binding for binding in game._keybinds[key] if action_id in binding.actions
        ]
        assert len(bindings) == 1
        assert bindings[0].state == KeybindState.ACTIVE


def test_finish_and_back_hotkeys_dispatch_only_within_the_current_phase() -> None:
    buy_game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(buy_game, 0)
    clear_spoken(buy_game)

    buy_game.handle_event(buyer, {"type": "keybind", "key": "x"})
    assert spoken_text(buy_game, 0) == []

    buy_game.handle_event(buyer, {"type": "keybind", "key": "e"})
    assert buyer.id in buy_game.buy_ready_player_ids
    assert not any(
        "buy phase is still active" in text.lower()
        for text in spoken_text(buy_game, 0)
    )

    combat_game = make_game(start=True)
    actor = tactical_player(combat_game, 0)
    clear_spoken(combat_game)

    combat_game.handle_event(actor, {"type": "keybind", "key": "x"})
    assert spoken_text(combat_game, 0) == []

    combat_game.handle_event(actor, {"type": "keybind", "key": "e"})
    assert combat_game.current_player is not actor
    assert not any(
        "buying is closed" in text.lower()
        for text in spoken_text(combat_game, 0)
    )


def test_turn_announcements_are_public_and_report_the_actors_ap() -> None:
    game = make_game(start=True)
    actor = tactical_player(game, 0)
    hidden_enemy = tactical_player(game, 1)
    clear_spoken(game)

    game._start_activation(actor)

    assert spoken_text(game, 0) == ["Your turn. You have 2 AP."]
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    assert actor_user.get_sounds_played() == [TURN_NOTIFICATION_ASSET]
    assert spoken_text(game, 2) == [f"{actor.name}'s turn."]
    assert spoken_text(game, 1) == [f"{actor.name}'s turn."]
    assert spoken_text(game, 3) == [f"{actor.name}'s turn."]

    hidden_enemy.position_id = "mid"
    clear_spoken(game)
    game._start_activation(actor, action_point_limit=1)
    assert spoken_text(game, 0) == ["Your turn. You have 1 AP."]
    assert spoken_text(game, 1) == [f"{actor.name}'s turn."]

    clear_spoken(game)
    actor_user.preferences.play_turn_sound = False
    game._start_activation(actor)
    assert actor_user.get_sounds_played() == []


def test_turn_status_reports_reaction_decision_owner() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    responder = tactical_player(game, 1)
    game.reaction_window = ReactionWindow(
        kind=REACTION_WATCHED_ENTRY,
        triggering_player_id=mover.id,
        responding_player_id=responder.id,
        resume_after_player_id=mover.id,
        target_player_id=mover.id,
        context={"node_id": "mid"},
    )
    game.current_player = responder
    clear_spoken(game)

    game._action_whose_turn(mover, "whose_turn")
    game._action_whose_turn(responder, "whose_turn")

    assert spoken_text(game, 0) == [
        "The game is waiting for Player2's response."
    ]
    assert spoken_text(game, 1) == ["The game is waiting for your response."]


def test_brief_score_reports_current_side_scores_in_one_line() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    game._team_manager.teams[0].total_score = 4
    game._team_manager.teams[1].total_score = 7
    game.side_squad_indexes = [1, 0]
    clear_spoken(game)

    game._action_check_scores(player, "check_scores")

    assert spoken_text(game, 0) == [f"Round {game.round}: T 7, CT 4."]


def test_live_map_uses_stable_ids_and_reports_exits_sightlines_and_occupants() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    items = game._build_map_status(player, user)
    assert items[0].id == "breachpoint_map_header"
    assert items[1].id == "breachpoint_map_spatial_context"
    assert "You are at T Spawn" in items[1].text
    assert "stacked supply crates" in items[1].text
    mid_doors = next(
        item for item in items if item.id == "breachpoint_map_node_mid_doors"
    )
    assert "Connected areas: Mid and CT Mid" in mid_doors.text
    assert "CT Spawn, range 2" in mid_doors.text
    t_spawn = next(item for item in items if item.id == "breachpoint_map_node_t_spawn")
    assert "Player1" in t_spawn.text
    assert "Player3" in t_spawn.text


def test_live_map_uses_the_postplant_phase_instead_of_an_expired_round_limit() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    game.tactical_round = game.rules.preplant_tactical_round_limit + 1
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round

    header = game._build_map_status(player, user)[0].text

    assert "Bomb planted; 3 full tactical rounds remain" in header
    assert "7 of 6" not in header


def test_fog_of_war_hides_enemy_positions_health_and_unseen_bomb() -> None:
    game = make_game(start=True)
    viewer = tactical_player(game, 0)
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)

    map_text = "\n".join(item.text for item in game._build_map_status(viewer, user))
    assert "Player1" in map_text
    assert "Player3" in map_text
    assert "Player2" not in map_text
    assert "Player4" not in map_text

    teammate_text = "\n".join(
        item.text for item in game._build_teammate_status(viewer, user)
    )
    assert "Player3" in teammate_text
    assert "Player2" not in teammate_text
    assert "Player4" not in teammate_text

    enemy_items = game._build_enemy_status(viewer, user)
    assert [item.id for item in enemy_items] == [
        "breachpoint_enemies_header",
        "breachpoint_enemies_empty",
    ]
    assert "No enemy position is currently known" in enemy_items[1].text

    defender = tactical_player(game, 1)
    assert "concealed" in game._bomb_status_line(defender, "en")
    assert "Player1" in game._bomb_status_line(viewer, "en")

    defender.position_id = "mid"
    visible_enemy_items = game._build_enemy_status(viewer, user)
    assert any(item.id == "breachpoint_enemy_p2" for item in visible_enemy_items)
    assert all("Player3" not in item.text for item in visible_enemy_items)

    set_area_effect(game, SMOKE_GRENADE, "mid")
    hidden_enemy_items = game._build_enemy_status(viewer, user)
    assert all(item.id != "breachpoint_enemy_p2" for item in hidden_enemy_items)

    defender.eliminated = True
    defender.health = 0
    defender.armor = 73
    eliminated_enemy = next(
        item
        for item in game._build_enemy_status(viewer, user)
        if item.id == "breachpoint_enemy_p2"
    )
    assert "last seen at Mid" in eliminated_enemy.text
    assert "eliminated this combat round" in eliminated_enemy.text
    assert "73 armor" not in eliminated_enemy.text


def test_team_shared_los_reveals_contacts_without_granting_remote_shots() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    scout = tactical_player(game, 2)
    enemy = tactical_player(game, 1)
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)

    scout.position_id = "ct_mid"
    enemy.position_id = "ct_spawn"
    map_text = "\n".join(item.text for item in game._build_map_status(shooter, user))
    assert "Player2" in map_text
    assert (
        game._is_shoot_hidden(shooter, action_id=f"shoot_{enemy.id}")
        == Visibility.HIDDEN
    )


def test_smoke_blocks_endpoint_sightlines_for_two_tactical_rounds() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    user = game.get_user(thrower)
    assert isinstance(user, MockUser)
    thrower.position_id = "ct_spawn"
    target.position_id = "a_site"
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}

    assert game._can_see(thrower, target)
    game.execute_action(thrower, "throw_smoke_a_site")
    complete_utility(game)
    smoke = game._area_effect(UTILITY_EFFECT_SMOKE, "a_site")
    assert smoke is not None
    assert smoke.expires_at_tactical_round == 3
    assert not game._can_see(thrower, target)
    map_text = "\n".join(item.text for item in game._build_map_status(thrower, user))
    assert "Bombsite A, bombsite, active effects: smoke" in map_text

    game.tactical_round = 2
    game._prune_expired_area_effects()
    assert game._is_smoked("a_site")
    game.tactical_round = 3
    game._prune_expired_area_effects()
    assert not game._is_smoked("a_site")
    assert not game.area_effects
    assert game._can_see(thrower, target)


def test_utility_callouts_are_teamwide_but_enemy_visibility_limited() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    hidden_enemy = tactical_player(game, 1)
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}
    clear_spoken(game)

    game.execute_action(thrower, "throw_smoke_t_spawn")
    complete_utility(game)

    assert "You throw Smoke Grenade at T Spawn." in spoken_text(game, 0)
    assert "Player1 throws Smoke Grenade at T Spawn." in spoken_text(game, 2)
    assert all("Smoke Grenade" not in text for text in spoken_text(game, 1))
    assert all("Smoke Grenade" not in text for text in spoken_text(game, 3))

    thrower.utility_counts = {FLASHBANG.id: 1}
    thrower.position_id = "ct_spawn"
    hidden_enemy.position_id = "a_site"
    start_activation(game, thrower)
    clear_spoken(game)
    game.execute_action(thrower, "throw_flashbang_a_site")
    complete_utility(game)

    assert "Enemy utility: Player1 throws Flashbang at Bombsite A." in spoken_text(
        game, 1
    )
    assert hidden_enemy.flash_penalty == FLASHBANG.activation_penalty


def test_visible_utility_impact_does_not_reveal_concealed_thrower() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    observer.position_id = "upper_tunnels"
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}
    clear_spoken(game)

    game.execute_action(thrower, "throw_smoke_outside_tunnels")
    complete_utility(game)

    assert "Enemy Smoke Grenade at Outside Tunnels." in spoken_text(game, 1)
    assert all("Player1" not in text for text in spoken_text(game, 1))


def test_hidden_smoke_is_not_leaked_to_enemy_map_status() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}

    game.execute_action(thrower, "throw_smoke_t_spawn")
    complete_utility(game)

    thrower_user = game.get_user(thrower)
    enemy_user = game.get_user(enemy)
    assert isinstance(thrower_user, MockUser)
    assert isinstance(enemy_user, MockUser)
    friendly_map = "\n".join(
        item.text for item in game._build_map_status(thrower, thrower_user)
    )
    enemy_map = "\n".join(
        item.text for item in game._build_map_status(enemy, enemy_user)
    )
    assert "T Spawn, normal area, active effects: smoke" in friendly_map
    assert "T Spawn, normal area, active effects: smoke" not in enemy_map
    assert "T Spawn, normal area, no confirmed smoke or fire" in enemy_map


def test_unknown_smoke_overlap_does_not_leak_through_action_validation() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    teammate = tactical_player(game, 2)
    thrower.position_id = teammate.position_id = "t_spawn"
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}
    start_activation(game, thrower)
    existing_expiration = game.tactical_round + 1
    set_area_effect(
        game,
        SMOKE_GRENADE,
        "t_spawn",
        expiration=existing_expiration,
        known_team_indexes=[TEAM_TERRORISTS],
    )
    set_area_effect(
        game,
        SMOKE_GRENADE,
        "mid",
        expiration=existing_expiration,
    )

    assert not game._team_knows_smoke(TEAM_TERRORISTS, "mid")
    assert (
        game._is_throw_utility_enabled(
            thrower,
            action_id="throw_smoke_t_spawn",
        )
        == "breachpoint-error-smoke-active"
    )
    assert (
        game._is_throw_utility_enabled(
            thrower,
            action_id="throw_smoke_mid",
        )
        is None
    )

    game.execute_action(thrower, "throw_smoke_mid")
    complete_utility(game)

    assert thrower.utility_counts == {}
    smoke = game._area_effect(UTILITY_EFFECT_SMOKE, "mid")
    assert smoke is not None
    assert smoke.expires_at_tactical_round == (
        game.tactical_round + SMOKE_GRENADE.duration_tactical_rounds
    )
    assert game._team_knows_smoke(TEAM_TERRORISTS, "mid")


def test_team_discovers_hidden_smoke_when_movement_reveals_its_boundary() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    observer_teammate = tactical_player(game, 3)
    thrower.position_id = "b_tunnels"
    observer.position_id = observer_teammate.position_id = "ct_mid"
    thrower.utility_counts = {SMOKE_GRENADE.id: 1}

    game.execute_action(thrower, "throw_smoke_b_site")
    complete_utility(game)
    assert not game._team_knows_smoke(TEAM_COUNTER_TERRORISTS, "b_site")

    start_activation(game, observer)
    game.execute_action(observer, "move_b_doors")
    complete_movement(game)

    assert game._team_knows_smoke(TEAM_COUNTER_TERRORISTS, "b_site")
    smoke = game._area_effect(UTILITY_EFFECT_SMOKE, "b_site")
    assert smoke is not None
    assert TEAM_COUNTER_TERRORISTS in smoke.known_team_indexes
    user = game.get_user(observer)
    assert isinstance(user, MockUser)
    map_text = "\n".join(item.text for item in game._build_map_status(observer, user))
    assert "Bombsite B, bombsite, active effects: smoke" in map_text


def test_smoke_does_not_hide_opponents_sharing_the_same_area() -> None:
    game = make_game(start=True)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = "a_site"
    defender.position_id = "a_site"
    set_area_effect(game, SMOKE_GRENADE, "a_site")

    assert game._can_see(terrorist, defender)
    assert game._team_can_see_player(TEAM_TERRORISTS, defender)


def test_flashbang_spares_thrower_but_affects_teammates_and_enemies() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    thrower.position_id = "a_site"
    defender.position_id = "a_site"
    teammate.position_id = "a_site"
    thrower.utility_counts = {FLASHBANG.id: 1}
    defender.held_angle_origin_id = defender.position_id
    defender.held_angle_node_id = "ct_mid"
    teammate.held_angle_origin_id = teammate.position_id
    teammate.held_angle_node_id = "ct_mid"
    users = {
        player.id: game.get_user(player) for player in (thrower, defender, teammate)
    }
    for user in users.values():
        assert isinstance(user, MockUser)
        user.clear_messages()

    game.execute_action(thrower, "throw_flashbang_a_site")
    complete_utility(game)
    assert thrower.flash_penalty == 0
    assert defender.flash_penalty == FLASHBANG.activation_penalty
    assert teammate.flash_penalty == FLASHBANG.activation_penalty
    assert not defender.held_angle_node_id
    assert not teammate.held_angle_node_id
    for player in (defender, teammate):
        user = users[player.id]
        assert isinstance(user, MockUser)
        assert any(
            message.type == "play_sound"
            and message.data.get("name") == FLASH_TINNITUS_ASSET
            for message in user.messages
        )
    thrower_user = users[thrower.id]
    assert isinstance(thrower_user, MockUser)
    assert not any(
        message.type == "play_sound"
        and message.data.get("name") == FLASH_TINNITUS_ASSET
        for message in thrower_user.messages
    )

    start_activation(game, defender)
    assert defender.action_points == (
        game.rules.action_points_per_activation - FLASHBANG.activation_penalty
    )
    assert defender.flash_penalty == 0
    assert teammate.flash_penalty == FLASHBANG.activation_penalty


def test_using_utility_breaks_a_prepared_angle() -> None:
    game = make_game(start=True)
    sniper = tactical_player(game, 0)
    sniper.position_id = "ct_mid"
    sniper.primary_weapon_id = AWP.id
    sniper.equipped_weapon_id = AWP.id
    sniper.utility_counts = {SMOKE_GRENADE.id: 1}
    sniper.held_angle_origin_id = "ct_mid"
    sniper.held_angle_node_id = "a_site"

    game.execute_action(sniper, "throw_smoke_b_doors")
    complete_utility(game)
    assert not sniper.held_angle_origin_id
    assert not sniper.held_angle_node_id


def test_utility_inventory_enforces_type_and_total_carry_limits() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = game.economy.maximum_cash

    for action_id in (
        "buy_utility_smoke",
        "buy_utility_flashbang",
        "buy_utility_flashbang",
        "buy_utility_he_grenade",
    ):
        game.execute_action(buyer, action_id)

    assert sum(buyer.utility_counts.values()) == game.rules.maximum_utility_items
    assert game._is_buy_utility_enabled(
        buyer,
        action_id="buy_utility_molotov",
    ) == (
        "breachpoint-error-utility-total-full",
        {"maximum": game.rules.maximum_utility_items},
    )

    buyer.utility_counts[MOLOTOV.id] = 1
    game._normalize_utility_counts(buyer)
    assert buyer.utility_counts == {
        SMOKE_GRENADE.id: 1,
        FLASHBANG.id: 2,
        HE_GRENADE.id: 1,
    }


def test_area_effect_normalization_merges_valid_state_and_rejects_bad_data() -> None:
    game = make_game(start=True)
    source = tactical_player(game, 0)
    replacement_source = tactical_player(game, 2)
    affected = tactical_player(game, 1)
    game.area_effects = [
        AreaEffectState(
            effect=UTILITY_EFFECT_SMOKE,
            utility_id=SMOKE_GRENADE.id,
            node_id="a_site",
            source_player_id=source.id,
            expires_at_tactical_round=game.tactical_round + 1,
            known_team_indexes=[TEAM_TERRORISTS, TEAM_TERRORISTS, True, 9],
            affected_player_rounds={
                affected.id: game.tactical_round - 1,
                "missing-player": game.tactical_round,
            },
        ),
        AreaEffectState(
            effect=UTILITY_EFFECT_SMOKE,
            utility_id=SMOKE_GRENADE.id,
            node_id="a_site",
            source_player_id=replacement_source.id,
            expires_at_tactical_round=game.tactical_round + 2,
            known_team_indexes=[TEAM_COUNTER_TERRORISTS],
            affected_player_rounds={affected.id: game.tactical_round},
        ),
        AreaEffectState(
            effect=UTILITY_EFFECT_FIRE,
            utility_id=FLASHBANG.id,
            node_id="b_site",
            source_player_id=source.id,
            expires_at_tactical_round=game.tactical_round + 2,
        ),
        AreaEffectState(
            effect=UTILITY_EFFECT_FIRE,
            utility_id=MOLOTOV.id,
            node_id="not-a-node",
            source_player_id=source.id,
            expires_at_tactical_round=game.tactical_round + 2,
        ),
    ]

    game._normalize_area_effects(
        game.tactical_map.node_map(),
        {player.id for player in game.get_active_players()},
    )

    assert len(game.area_effects) == 1
    smoke = game.area_effects[0]
    assert smoke.effect == UTILITY_EFFECT_SMOKE
    assert smoke.utility_id == SMOKE_GRENADE.id
    assert smoke.node_id == "a_site"
    assert smoke.source_player_id == replacement_source.id
    assert smoke.expires_at_tactical_round == game.tactical_round + 2
    assert smoke.known_team_indexes == [
        TEAM_TERRORISTS,
        TEAM_COUNTER_TERRORISTS,
    ]
    assert smoke.affected_player_rounds == {affected.id: game.tactical_round}


def test_he_grenade_resolves_evasion_armor_and_friendly_damage() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    thrower.position_id = "a_ramp"
    target.position_id = teammate.position_id = "a_site"
    target.armor = 100
    target.guard_points = 2
    thrower.utility_counts = {HE_GRENADE.id: 1}

    game.execute_action(thrower, "throw_he_grenade_a_site")
    complete_utility(game)

    assert target.health == 76
    assert target.armor == 91
    assert target.guard_points == 0
    assert teammate.health == 77
    assert not game.area_effects
    assert any("Your HE Grenade hits Player2" in text for text in spoken_text(game, 0))
    assert any("HE Grenade hits you" in text for text in spoken_text(game, 1))


def test_blind_he_damage_does_not_confirm_a_surviving_concealed_target() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    thrower.position_id = "a_ramp"
    target.position_id = "a_site"
    thrower.utility_counts = {HE_GRENADE.id: 1}
    set_area_effect(
        game,
        SMOKE_GRENADE,
        "a_site",
        known_team_indexes=[TEAM_TERRORISTS],
    )
    clear_spoken(game)

    game.execute_action(thrower, "throw_he_grenade_a_site")
    complete_utility(game)

    assert target.health == 55
    assert all("hits Player2" not in text for text in spoken_text(game, 0))
    assert any("HE Grenade hits you" in text for text in spoken_text(game, 1))


def test_damaging_utility_elimination_uses_the_public_kill_feed() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    thrower.position_id = "a_ramp"
    target.position_id = "a_site"
    target.health = 20
    thrower.utility_counts = {HE_GRENADE.id: 1}
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    clear_spoken(game)

    game.execute_action(thrower, "throw_he_grenade_a_site")
    complete_utility(game)

    assert target.eliminated
    expected = "Player1 eliminates Player2 with HE Grenade at Bombsite A."
    assert expected in spoken_text(game, 2)
    assert expected in spoken_text(game, 3)


def test_simultaneous_utility_team_wipe_awards_the_acting_side() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    thrower.position_id = target.position_id = "a_site"
    thrower.health = target.health = 20
    thrower.utility_counts = {HE_GRENADE.id: 1}
    for eliminated in (tactical_player(game, 2), tactical_player(game, 3)):
        eliminated.health = 0
        eliminated.eliminated = True

    game.execute_action(thrower, "throw_he_grenade_a_site")
    complete_utility(game)

    assert game.last_round_win_reason == WIN_ELIMINATION
    assert game._squad_score(thrower.squad_index) == 1


def test_self_lethal_he_finishes_the_throwers_activation_with_ap_remaining() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    next_player = tactical_player(game, 1)
    teammate = tactical_player(game, 2)
    game._place_player_in_node(thrower, "a_site")
    game._place_player_in_node(teammate, "t_spawn")
    thrower.health = 1
    thrower.utility_counts = {HE_GRENADE.id: 1}
    assert thrower.action_points == game.rules.action_points_per_activation

    game.execute_action(thrower, "throw_he_grenade_a_site")
    assert thrower.action_points == game.rules.action_points_per_activation - 1
    complete_utility(game)

    assert thrower.eliminated
    assert thrower.action_points == 0
    assert game.current_player is next_player
    assert game.status == "playing"
    assert not game.has_active_sequence(tag=UTILITY_AUDIO_SEQUENCE_TAG)


def test_fatal_utility_starts_spatial_death_and_surface_body_fall_audio() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    observer = tactical_player(game, 3)
    game._place_player_in_node(target, "a_site")
    target.health = 1
    target_user = game.get_user(target)
    observer_user = game.get_user(observer)
    assert isinstance(target_user, MockUser)
    assert isinstance(observer_user, MockUser)
    target_user.clear_messages()
    observer_user.clear_messages()

    game._damage_players_with_utility(thrower, HE_GRENADE, [target])

    target_chain = next(
        message
        for message in target_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and message.data["segments"][0]["asset"] in DEATH_VOICE_ASSETS
    )
    observer_chain = next(
        message
        for message in observer_user.messages
        if message.type == "play_sound"
        and message.data.get("segments")
        and message.data["segments"][0]["asset"] in DEATH_VOICE_ASSETS
    )
    assert target_chain.data["segments"][1]["asset"] in BODY_FALL_ASSETS_BY_SURFACE[
        "concrete"
    ]
    assert all(
        segment["position"] is None for segment in target_chain.data["segments"]
    )
    assert all(
        segment["position"] is not None for segment in observer_chain.data["segments"]
    )


def test_fire_damages_once_per_tactical_round_and_then_burns_out() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    thrower.position_id = "a_ramp"
    target.position_id = "a_site"
    thrower.utility_counts = {MOLOTOV.id: 1}
    target_user = game.get_user(target)
    assert isinstance(target_user, MockUser)
    target_user.clear_messages()

    game.execute_action(thrower, "throw_molotov_a_site")
    complete_utility(game)

    fire = game._area_effect(UTILITY_EFFECT_FIRE, "a_site")
    assert fire is not None
    assert target.health == 80
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == FIRE_DAMAGE_FAMILY
        and message.data.get("position") is None
        for message in target_user.messages
    )
    assert fire.affected_player_rounds == {target.id: game.tactical_round}
    assert not game._process_fire_contact(target)
    assert target.health == 80

    game.tactical_round += 1
    game._prune_expired_area_effects()
    start_activation(game, target)
    assert target.health == 60
    assert target.action_points == game.rules.action_points_per_activation

    game.tactical_round += 1
    game._prune_expired_area_effects()
    assert not game._is_burning("a_site")


def test_entering_known_fire_warns_and_applies_one_damage_tick() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 1)
    source = tactical_player(game, 0)
    mover.position_id = "a_ramp"
    set_area_effect(
        game,
        MOLOTOV,
        "a_site",
        source_player_id=source.id,
        known_team_indexes=[TEAM_COUNTER_TERRORISTS],
    )
    start_activation(game, mover)

    assert "Move into fire" in game._get_move_label(mover, "move_a_site")
    game.execute_action(mover, "move_a_site")
    complete_movement(game)

    assert mover.health == 80
    fire = game._area_effect(UTILITY_EFFECT_FIRE, "a_site")
    assert fire is not None
    assert fire.affected_player_rounds[mover.id] == game.tactical_round


def test_smoke_extinguishes_fire_and_fire_cannot_ignite_in_smoke() -> None:
    game = make_game(start=True)
    thrower = tactical_player(game, 0)
    target = tactical_player(game, 1)
    thrower.position_id = "a_ramp"
    target.position_id = "ct_spawn"
    thrower.utility_counts = {
        MOLOTOV.id: 1,
        SMOKE_GRENADE.id: 1,
    }

    game.execute_action(thrower, "throw_molotov_a_site")
    complete_utility(game)
    assert game._is_burning("a_site")
    game.execute_action(thrower, "throw_smoke_a_site")
    complete_utility(game)

    assert not game._is_burning("a_site")
    assert game._is_smoked("a_site")
    assert any("Smoke extinguishes the fire" in text for text in spoken_text(game, 0))

    start_activation(game, thrower)
    thrower.utility_counts = {MOLOTOV.id: 1}
    clear_spoken(game)
    game.execute_action(thrower, "throw_molotov_a_site")
    complete_utility(game)

    assert not game._is_burning("a_site")
    assert game._is_smoked("a_site")
    assert any(
        "Smoke prevents the fire from igniting" in text for text in spoken_text(game, 0)
    )
    user = game.get_user(thrower)
    assert isinstance(user, MockUser)
    assert any(
        message.type == "play_sound"
        and message.data.get("name") == FIRE_EXTINGUISH_ASSET
        for message in user.messages
    )


def test_fire_damage_interrupts_a_pending_plant_before_completion() -> None:
    game = make_game(start=True)
    planter = tactical_player(game, 0)
    source = tactical_player(game, 1)
    planter.position_id = "a_site"
    game.bomb_state = BOMB_PLANTING
    game.bomb_carrier_id = planter.id
    game.planting_player_id = planter.id
    game.planting_location_id = planter.position_id
    set_area_effect(
        game,
        INCENDIARY_GRENADE,
        "a_site",
        source_player_id=source.id,
    )

    start_activation(game, planter)

    assert planter.health == 80
    assert game.bomb_state == BOMB_CARRIED
    assert not game.planting_player_id


def test_enemy_movement_conceals_destination_until_team_los_detects_it() -> None:
    game = make_game(start=True)
    mover = tactical_player(game, 0)
    observing_enemy = tactical_player(game, 1)
    observing_teammate = tactical_player(game, 3)
    observing_enemy.position_id = observing_teammate.position_id = "a_short"
    clear_spoken(game)

    game.execute_action(mover, "move_mid")
    complete_movement(game)
    assert spoken_text(game, 1) == ["Player1 moved."]
    assert spoken_text(game, 3) == ["Player1 moved."]

    game.execute_action(mover, "move_catwalk")
    complete_movement(game)
    assert any("Contact: Player1 at Catwalk" in text for text in spoken_text(game, 1))
    assert any("Contact: Player1 at Catwalk" in text for text in spoken_text(game, 3))


def test_spectator_status_and_shot_feed_do_not_reveal_positions() -> None:
    game = make_game()
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher = game.add_spectator("Watcher", watcher_user)
    game.on_start()
    complete_buy_phase(game)
    game.flush_menus()
    watcher_user.clear_messages()

    map_text = "\n".join(
        item.text for item in game._build_map_status(watcher, watcher_user)
    )
    assert all(player.name not in map_text for player in game.get_active_players())
    assert "concealed" in game._bomb_status_line(watcher, "en")

    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    game.execute_action(shooter, "move_mid")
    complete_movement(game)
    assert "Player1 moved." in watcher_user.get_spoken_messages()
    target.position_id = "mid_doors"
    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)

    shot_messages = [
        text for text in watcher_user.get_spoken_messages() if "fires at" in text
    ]
    assert shot_messages == [
        "Player1 fires at Player2 with Glock: 30 damage; shots landed: 1."
    ]
    assert all("Mid Doors" not in text for text in shot_messages)


def test_kill_feed_is_public_and_includes_shooter_target_and_location() -> None:
    game = make_game()
    watcher_user = MockUser("Watcher", uuid="watcher")
    game.add_spectator("Watcher", watcher_user)
    game.on_start()
    complete_buy_phase(game)
    game.flush_menus()
    clear_spoken(game)
    watcher_user.clear_messages()
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.position_id = "mid"
    target.position_id = "mid_doors"
    target.health = 1

    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)

    assert shooter.cash == game.economy.starting_cash + GLOCK.kill_reward
    assert "You eliminate Player2 with Glock at Mid Doors." in spoken_text(game, 0)
    assert "Player1 eliminates you with Glock at Mid Doors." in spoken_text(game, 1)
    assert "Player1 eliminates Player2 with Glock at Mid Doors." in spoken_text(game, 2)
    assert "Player1 eliminates Player2 with Glock at Mid Doors." in spoken_text(game, 3)
    assert (
        "Player1 eliminates Player2 with Glock at Mid Doors."
        in watcher_user.get_spoken_messages()
    )

    for viewer in game.players:
        user = game.get_user(viewer)
        assert isinstance(user, MockUser)
        map_line = next(
            item.text
            for item in game._build_map_status(viewer, user)
            if item.id == "breachpoint_map_node_mid_doors"
        )
        assert "Player2" in map_line
        if not viewer.is_spectator and viewer.id != target.id:
            if viewer.squad_index == target.squad_index:
                casualty_id = f"breachpoint_teammate_{target.id}"
                status_items = game._build_teammate_status(viewer, user)
            else:
                casualty_id = f"breachpoint_enemy_{target.id}"
                status_items = game._build_enemy_status(viewer, user)
            casualty_line = next(
                item.text for item in status_items if item.id == casualty_id
            )
            assert "Player2" in casualty_line
            assert "Mid Doors" in casualty_line
            assert "eliminated this combat round" in casualty_line


def test_ground_weapons_are_visible_only_in_team_observed_areas() -> None:
    game = make_game(start=True)
    viewer = tactical_player(game, 0)
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)
    friendly_node = game._node(viewer.position_id)
    hidden_node = game._node("ct_spawn")
    assert friendly_node is not None
    assert hidden_node is not None
    game._create_dropped_weapon(
        AK47,
        friendly_node.id,
        friendly_node.anchor,
        magazine_ammo=4,
        reserve_units=1,
    )
    game._create_dropped_weapon(
        M4,
        hidden_node.id,
        hidden_node.anchor,
        magazine_ammo=5,
        reserve_units=1,
    )

    items = game._build_map_status(viewer, user)
    friendly_line = next(
        item.text
        for item in items
        if item.id == f"breachpoint_map_node_{friendly_node.id}"
    )
    hidden_line = next(
        item.text for item in items if item.id == "breachpoint_map_node_ct_spawn"
    )

    assert "Ground weapons: AK-47" in friendly_line
    assert "4 of 30 loaded; 1 reserve magazine" in friendly_line
    assert "Ground weapons: unconfirmed" in hidden_line
    assert "M4" not in hidden_line


def test_result_records_true_team_ranking_and_winner_ids() -> None:
    game = make_game(start=True)
    game.winning_team_index = TEAM_TERRORISTS
    game.win_reason = MATCH_REGULATION
    game._team_manager.teams[TEAM_TERRORISTS].total_score = 8
    game._team_manager.teams[TEAM_COUNTER_TERRORISTS].total_score = 4

    result = game.build_game_result()
    assert result.custom_data["winner_ids"] == ["p1", "p3"]
    assert result.custom_data["team_rankings"][0]["members"] == [
        "Player1",
        "Player3",
    ]
    teams, ranks = RatingHelper.extract_teams_and_ranks(result)
    assert teams == [["p1", "p3"], ["p2", "p4"]]
    assert ranks == [0, 1]


def test_save_restore_preserves_match_state_and_rebuilds_derived_actions() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    carrier.position_id = "a_site"
    game.execute_action(carrier, "plant")
    current_id = game.current_player.id if game.current_player else ""

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
        turn_set = restored.get_action_set(player, "turn")
        assert turn_set is not None
        turn_set.remove("end_turn")
    restored.current_player = tactical_player(restored, 2)
    restored.rebuild_runtime_state()

    assert restored.bomb_state == BOMB_PLANTING
    assert restored.planting_location_id == "a_site"
    assert restored.planting_player_id == carrier.id
    assert restored.reaction_window.kind == REACTION_PLANT
    assert restored.reaction_window.responding_player_id == current_id
    assert restored.reaction_window.resume_after_player_id == carrier.id
    assert restored.current_player is not None
    assert restored.current_player.id == current_id
    assert all(
        restored.find_action(player, "end_turn") is not None
        for player in restored.players
    )


def test_save_restore_preserves_utility_effects_guard_and_generic_held_angle() -> None:
    game = make_game(start=True)
    guarded = tactical_player(game, 0)
    holder = tactical_player(game, 1)
    guarded.utility_counts = {SMOKE_GRENADE.id: 1, FLASHBANG.id: 2}
    guarded.guard_anchor_node_id = guarded.position_id
    guarded.stationary_guard_activations = 1
    guarded.guard_points = 1
    holder.equipment_counts = {DEFUSE_KIT.id: 1}
    holder.position_id = "a_site"
    holder.primary_weapon_id = M4.id
    holder.equipped_weapon_id = M4.id
    holder.held_angle_origin_id = "a_site"
    holder.held_angle_node_id = "a_site"
    set_area_effect(
        game,
        SMOKE_GRENADE,
        "b_site",
        expiration=game.tactical_round + 2,
        known_team_indexes=[TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS],
    )
    burning = set_area_effect(
        game,
        MOLOTOV,
        "a_site",
        expiration=game.tactical_round + 2,
        known_team_indexes=[TEAM_TERRORISTS],
        source_player_id=guarded.id,
        affected_player_rounds={holder.id: game.tactical_round},
    )

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()

    restored_guarded = tactical_player(restored, 0)
    restored_holder = tactical_player(restored, 1)
    assert restored_guarded.utility_counts == {
        SMOKE_GRENADE.id: 1,
        FLASHBANG.id: 2,
    }
    assert restored_guarded.guard_points == 1
    assert restored_guarded.guard_anchor_node_id == guarded.position_id
    assert restored_guarded.stationary_guard_activations == 1
    restored_smoke = restored._area_effect(UTILITY_EFFECT_SMOKE, "b_site")
    assert restored_smoke is not None
    assert restored_smoke.expires_at_tactical_round == game.tactical_round + 2
    assert restored_smoke.known_team_indexes == [
        TEAM_TERRORISTS,
        TEAM_COUNTER_TERRORISTS,
    ]
    restored_fire = restored._area_effect(UTILITY_EFFECT_FIRE, "a_site")
    assert restored_fire is not None
    assert restored_fire.utility_id == MOLOTOV.id
    assert restored_fire.source_player_id == guarded.id
    assert restored_fire.expires_at_tactical_round == game.tactical_round + 2
    assert restored_fire.known_team_indexes == [TEAM_TERRORISTS]
    assert restored_fire.affected_player_rounds == {holder.id: game.tactical_round}
    assert burning.affected_player_rounds == {holder.id: game.tactical_round}
    assert restored_holder.equipment_counts == {DEFUSE_KIT.id: 1}
    assert restored_holder.held_angle_origin_id == "a_site"
    assert restored_holder.held_angle_node_id == "a_site"


def test_save_restore_preserves_per_weapon_attack_cadence_and_recoil() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 0)
    target = tactical_player(game, 1)
    shooter.primary_weapon_id = AK47.id
    shooter.equipped_weapon_id = AK47.id
    shooter.position_id = "a_ramp"
    target.position_id = "a_site"
    game.execute_action(shooter, f"shoot_{target.id}")
    complete_weapon_fire(game)

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_shooter = tactical_player(restored, 0)
    restored_target = tactical_player(restored, 1)

    assert restored_shooter.shots_fired_this_activation == 1
    assert restored_shooter.weapon_shots_fired_this_activation == {AK47.id: 1}
    assert restored_shooter.weapon_target_ids_this_activation == {
        AK47.id: [restored_target.id]
    }
    restored._action_equip_weapon(restored_shooter, "equip_sidearm")
    restored.flush_menus()
    assert "recoil-limited to 75 percent damage" in restored._get_shoot_label(
        restored_shooter,
        f"shoot_{restored_target.id}",
    )


def test_save_restore_preserves_buy_order_cash_and_equipment() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    first_buyer = tactical_player(game, 0)
    game.execute_action(first_buyer, "buy_armor")
    game.execute_action(first_buyer, "finish_buy")
    current_id = game.current_player.id if game.current_player else ""

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()

    restored_first = tactical_player(restored, 0)
    assert restored.phase == PHASE_BUY
    assert restored.buy_ready_player_ids == [first_buyer.id]
    assert restored.current_player is not None
    assert restored.current_player.id == current_id
    assert restored_first.cash == 150
    assert restored_first.armor == game.economy.maximum_armor
    assert restored_first.equipped_weapon_id == GLOCK.id


def test_save_restore_preserves_a_purchased_sidearm() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    game.execute_action(buyer, "buy_weapon_desert_eagle")

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_buyer = tactical_player(restored, 0)

    assert restored_buyer.sidearm_weapon_id == DESERT_EAGLE.id
    assert restored_buyer.primary_weapon_id == ""
    assert restored_buyer.equipped_weapon_id == DESERT_EAGLE.id
    assert restored_buyer.cash == game.economy.starting_cash - DESERT_EAGLE.cost


def test_save_restore_preserves_refundable_held_and_dropped_purchases() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    buyer.cash = MAC10.cost + AK47.cost
    game.execute_action(buyer, "buy_weapon_mac10")
    game.execute_action(buyer, "buy_weapon_ak47")

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_buyer = tactical_player(restored, 0)

    assert len(restored.buy_transactions) == 2
    assert restored._is_refund_purchase_enabled(
        restored_buyer,
        action_id="refund_weapon_mac10",
    ) is None
    assert restored._is_refund_purchase_enabled(
        restored_buyer,
        action_id="refund_weapon_ak47",
    ) is None
    restored._action_refund_purchase(restored_buyer, "refund_weapon_mac10")
    restored._action_refund_purchase(restored_buyer, "refund_weapon_ak47")
    assert restored_buyer.cash == MAC10.cost + AK47.cost
    assert restored.dropped_weapons == []


def test_save_restore_preserves_pending_weapon_donation_and_buy_turn() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    recipient = tactical_player(game, 2)
    buyer.cash = AK47.cost
    game.execute_action(
        buyer,
        game._donate_weapon_action_id(AK47, recipient),
    )

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_buyer = restored._breach_player_by_id(buyer.id)
    restored_recipient = restored._breach_player_by_id(recipient.id)
    assert restored_buyer is not None
    assert restored_recipient is not None
    assert restored.pending_weapon_donation is not None
    assert restored.current_player is restored_recipient
    assert restored._is_weapon_donation_response_enabled(restored_recipient) is None

    restored.execute_action(restored_recipient, "accept_weapon_donation")

    assert restored.pending_weapon_donation is None
    assert restored.current_player is restored_buyer
    assert restored_recipient.primary_weapon_id == AK47.id
    assert restored_buyer.cash == 0


def test_save_restore_restarts_the_irreversible_bomb_warning() -> None:
    game = make_game(start=True)
    carrier = tactical_player(game, 0)
    game._place_player_in_node(carrier, "a_site")
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = carrier.position_id
    game._set_bomb_grid_point(game._player_grid_point(carrier))
    game.bomb_fuse_remaining = 1
    game.bomb_planted_tactical_round = 1
    game.tactical_round = 2
    assert game._complete_tactical_round()

    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    listener = restored._breach_player_by_id(tactical_player(game, 1).id)
    assert listener is not None
    listener_user = MockUser(listener.name, uuid=listener.id)
    restored.attach_user(listener.id, listener_user)

    assert restored.bomb_fuse_remaining == 0
    assert restored.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
    assert "too late to defuse" in restored._bomb_status_line(listener, "en")
    warning = next(
        message
        for message in listener_user.messages
        if message.type == "play_sound"
        and [segment["asset"] for segment in message.data.get("segments", [])]
        == [BOMB_NVG_ON_ASSET, BOMB_ARM_ASSET]
    )
    assert warning.data["segments"][0]["next_start_ratio"] == (
        BOMB_ARM_START_RATIO
    )

    complete_timed_action(restored, BOMB_DETONATION_SEQUENCE_TAG)
    assert restored._squad_score(TEAM_TERRORISTS) == 1


def test_restore_discards_buy_transaction_with_noncanonical_price() -> None:
    game = make_game(start=True, finish_buy_phase=False)
    buyer = tactical_player(game, 0)
    game.execute_action(buyer, "buy_weapon_desert_eagle")
    game.buy_transactions[0].cost = game.economy.maximum_cash

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_buyer = tactical_player(restored, 0)

    assert restored.buy_transactions == []
    assert (
        restored._is_refund_purchase_hidden(
            restored_buyer,
            action_id="refund_weapon_desert_eagle",
        )
        == Visibility.HIDDEN
    )


def test_save_restore_preserves_authoritative_weapon_ammunition() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 1)
    shooter.primary_weapon_id = M4.id
    shooter.equipped_weapon_id = M4.id
    shooter.weapon_magazine_ammo = {
        USP_S.id: 4,
        M4.id: 6,
    }
    shooter.weapon_reserve_units = {
        USP_S.id: 2,
        M4.id: 1,
    }

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()
    restored_shooter = tactical_player(restored, 1)

    assert restored_shooter.weapon_magazine_ammo == {
        USP_S.id: 4,
        M4.id: 6,
    }
    assert restored_shooter.weapon_reserve_units == {
        USP_S.id: 2,
        M4.id: 1,
    }


def test_save_restore_preserves_and_normalizes_dropped_weapons() -> None:
    game = make_game(start=True)
    node = game._node("mid")
    assert node is not None
    game.dropped_weapons = [
        DroppedWeapon(4, AK47.id, node.id, -100, -100, 999, 999),
        DroppedWeapon(4, M4.id, node.id, node.anchor.x, node.anchor.y, 3, 1),
        DroppedWeapon(5, "unknown", node.id, node.anchor.x, node.anchor.y, 1, 1),
        DroppedWeapon(6, M4.id, "unknown", node.anchor.x, node.anchor.y, 1, 1),
        DroppedWeapon(0, M4.id, node.id, node.anchor.x, node.anchor.y, 1, 1),
    ]
    game.next_dropped_weapon_id = 1

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()

    assert restored.dropped_weapons == [
        DroppedWeapon(
            4,
            AK47.id,
            node.id,
            node.anchor.x,
            node.anchor.y,
            AK47.magazine_capacity,
            AK47.reserve_units,
        )
    ]
    assert restored.next_dropped_weapon_id == 5
    assert all(
        restored.find_action(player, "pick_up_weapon_4") is not None
        for player in restored.players
    )


def test_save_restore_preserves_a_valid_defuse_response_window() -> None:
    game = make_game(start=True)
    defender = tactical_player(game, 1)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    game.bomb_planted_tactical_round = game.tactical_round
    defender.position_id = "a_site"
    start_activation(game, defender)
    game.execute_action(defender, "defuse")
    responder_id = game.current_player.id if game.current_player else ""

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()

    assert restored.defusing_player_id == defender.id
    assert restored.defusing_location_id == "a_site"
    assert restored.reaction_window.kind == REACTION_DEFUSE
    assert restored.reaction_window.responding_player_id == responder_id
    assert restored.reaction_window.resume_after_player_id == defender.id
    assert restored.current_player is not None
    assert restored.current_player.id == responder_id


def test_save_restore_preserves_squad_scores_and_current_sides() -> None:
    game = make_game(start=True, match_format="mr7")
    game._team_manager.teams[0].total_score = 4
    game._team_manager.teams[1].total_score = 3
    game.round = 8
    game._swap_sides()
    clear_spoken(game)

    restored = BreachPointGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored.rebuild_runtime_state()

    assert restored.round == 8
    assert restored.side_squad_indexes == [1, 0]
    assert [restored._squad_score(index) for index in (0, 1)] == [4, 3]
    restored_player = tactical_player(restored, 0)
    assert restored_player.squad_index == 0
    assert restored_player.team_index == TEAM_COUNTER_TERRORISTS


def test_restore_normalizes_invalid_match_metadata_and_scores() -> None:
    game = make_game(start=True, match_format="mr7")
    game.options.match_format = "mr99"
    game.options.overtime_mode = "sudden_death"
    game.side_squad_indexes = [0, 0]
    game.overtime_start_scores = [8, -1]
    game._team_manager.teams[0].total_score = 3
    game._team_manager.teams[0].round_score = 2
    game._team_manager.teams[1].total_score = -4
    game._team_manager.teams[1].round_score = 5
    game.phase = "invalid"
    game.squad_loss_streaks = [-5, 99]
    first_player = tactical_player(game, 0)
    first_player.cash = -20
    first_player.armor = game.economy.maximum_armor + 99
    first_player.sidearm_weapon_id = M4.id
    first_player.primary_weapon_id = M4.id
    first_player.equipped_weapon_id = "missing"
    first_player.shots_fired_this_activation = 0
    first_player.weapon_shots_fired_this_activation = {
        GLOCK.id: 1,
        M4.id: 2,
        "missing": 2,
    }
    first_player.weapon_target_ids_this_activation = {
        GLOCK.id: [tactical_player(game, 1).id, tactical_player(game, 1).id],
        "missing": [tactical_player(game, 1).id],
    }
    first_player.weapon_magazine_ammo = {
        GLOCK.id: GLOCK.magazine_capacity + 99,
        M4.id: 4,
        "missing": 1,
    }
    first_player.weapon_reserve_units = {
        GLOCK.id: -1,
        M4.id: 1,
        "missing": 1,
    }

    game.rebuild_runtime_state()

    assert game.options.match_format == "mr12"
    assert game.options.overtime_mode == "mr3"
    assert game.side_squad_indexes == [0, 1]
    assert [team.total_score for team in game._team_manager.teams] == [3, 0]
    assert [team.round_score for team in game._team_manager.teams] == [0, 0]
    assert game.overtime_start_scores == [3, 0]
    assert game.phase == PHASE_COMBAT
    assert game.squad_loss_streaks == [0, game.economy.maximum_loss_count]
    assert first_player.cash == 0
    assert first_player.armor == game.economy.maximum_armor
    assert first_player.sidearm_weapon_id == GLOCK.id
    assert first_player.primary_weapon_id == M4.id
    assert first_player.equipped_weapon_id == M4.id
    assert first_player.shots_fired_this_activation == 2
    assert first_player.weapon_shots_fired_this_activation == {
        GLOCK.id: 1,
        M4.id: 1,
    }
    assert first_player.weapon_target_ids_this_activation == {
        GLOCK.id: [tactical_player(game, 1).id]
    }
    assert first_player.weapon_magazine_ammo == {
        GLOCK.id: GLOCK.magazine_capacity,
        M4.id: 4,
    }
    assert first_player.weapon_reserve_units == {GLOCK.id: 0, M4.id: 1}


def test_restore_rejects_an_unknown_map_instead_of_migrating_it() -> None:
    game = make_game(start=True)
    game.map_id = "missing"

    try:
        game.rebuild_runtime_state()
    except ValueError as error:
        assert "Unknown Breach Point tactical map" in str(error)
    else:
        raise AssertionError("An unknown unreleased map must not be migrated")


def test_restore_caps_combined_attack_history_to_the_activation_ap_budget() -> None:
    game = make_game(start=True)
    shooter = tactical_player(game, 1)
    first_target = tactical_player(game, 0)
    second_target = tactical_player(game, 2)
    shooter.primary_weapon_id = M4.id
    shooter.equipped_weapon_id = USP_S.id
    shooter.action_points = game.rules.action_points_per_activation
    shooter.shots_fired_this_activation = 99
    shooter.weapon_shots_fired_this_activation = {
        USP_S.id: 1,
        M4.id: M4.shots_per_activation,
    }
    shooter.weapon_target_ids_this_activation = {
        USP_S.id: [first_target.id],
        M4.id: [first_target.id, second_target.id],
    }

    game.rebuild_runtime_state()

    assert shooter.shots_fired_this_activation == 2
    assert shooter.weapon_shots_fired_this_activation == {
        USP_S.id: 1,
        M4.id: 1,
    }
    assert shooter.weapon_target_ids_this_activation == {
        USP_S.id: [first_target.id],
        M4.id: [first_target.id],
    }
    assert shooter.action_points == 0


def test_bot_strategy_uses_legal_objective_and_path_actions() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    terrorist_bot = tactical_player(game, 2)
    start_activation(game, terrorist_bot)
    game.bomb_carrier_id = terrorist_bot.id

    first_action = game.bot_think(terrorist_bot)
    assert first_action in {
        "move_outside_long",
        "move_mid",
        "move_outside_tunnels",
    }
    terrorist_bot.position_id = "a_site"
    terrorist_bot.action_points = 2
    assert game.bot_think(terrorist_bot) == "plant"

    defender_bot = tactical_player(game, 1)
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    defender_bot.position_id = "a_site"
    terrorist_bot.position_id = "b_site"
    start_activation(game, defender_bot)
    assert game.bot_think(defender_bot) == "defuse"


def test_bot_recovers_a_better_ground_weapon_without_abandoning_the_bomb() -> None:
    game = make_game(start=True, bot_indexes={0, 1})
    defender = tactical_player(game, 1)
    start_activation(game, defender)
    point = game._player_grid_point(defender)
    dropped_ak = game._create_dropped_weapon(
        AK47,
        defender.position_id,
        point,
        magazine_ammo=12,
        reserve_units=1,
    )
    game.refresh_menus(defender)
    game.flush_menus()

    action_id = game._dropped_weapon_action_id(dropped_ak)
    assert game.bot_think(defender) == action_id
    game.execute_action(defender, action_id)
    assert defender.primary_weapon_id == AK47.id
    assert defender.action_points == 1

    carrier = tactical_player(game, 0)
    start_activation(game, carrier)
    game.bomb_carrier_id = carrier.id
    dropped_m4 = game._create_dropped_weapon(
        M4,
        carrier.position_id,
        game._player_grid_point(carrier),
        magazine_ammo=12,
        reserve_units=1,
    )
    assert game._bot_coordinator.pickup_weapon_action(game, carrier) is None
    assert dropped_m4 in game.dropped_weapons


def test_bot_prefers_a_loaded_recovery_to_reloading_a_more_expensive_gun() -> None:
    game = make_game(start=True, bot_indexes={1})
    defender = tactical_player(game, 1)
    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    defender.weapon_magazine_ammo[M4.id] = 0
    defender.weapon_reserve_units[M4.id] = 1
    start_activation(game, defender)
    dropped_galil = game._create_dropped_weapon(
        GALIL_AR,
        defender.position_id,
        game._player_grid_point(defender),
        magazine_ammo=GALIL_AR.ammunition_per_attack,
        reserve_units=0,
    )
    game.refresh_menus(defender)
    game.flush_menus()

    assert game.bot_think(defender) == game._dropped_weapon_action_id(dropped_galil)


def test_bot_resolves_final_elimination_recovery_without_stalling() -> None:
    game = make_game(start=True, bot_indexes={0})
    bot = tactical_player(game, 0)
    target = tactical_player(game, 1)
    other_defender = tactical_player(game, 3)
    bot.position_id = target.position_id = "mid"
    target.primary_weapon_id = M4.id
    target.equipped_weapon_id = M4.id
    game._set_full_weapon_ammunition(target, M4)
    target.eliminated = True
    target.health = 0
    other_defender.eliminated = True
    other_defender.health = 0

    assert game._finalize_eliminations(
        bot,
        [target],
        source_name_key=GLOCK.name_key,
        kill_reward=GLOCK.kill_reward,
    )
    dropped_m4 = next(
        dropped for dropped in game.dropped_weapons if dropped.weapon_id == M4.id
    )

    assert game.bot_think(bot) == game._dropped_weapon_action_id(dropped_m4)
    game.flush_menus()
    game.execute_action(bot, game._dropped_weapon_action_id(dropped_m4))
    assert bot.primary_weapon_id == M4.id
    assert game._squad_score(TEAM_TERRORISTS) == 1


def test_bomb_carrier_uses_the_final_activation_to_reach_and_plant() -> None:
    game = make_game(start=True, bot_indexes={0})
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "b_site"
    plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
    plan.strategy_committed = True
    carrier.position_id = "b_tunnels"
    defender.position_id = "b_site"
    game.tactical_round = game.rules.preplant_tactical_round_limit
    start_activation(game, carrier)

    assert game.bot_think(carrier) == "move_b_site"
    game.execute_action(carrier, "move_b_site")
    complete_movement(game)
    assert game.bot_think(carrier) == "plant"


def test_bot_pathfinding_does_not_route_around_a_concealed_enemy(
    monkeypatch,
) -> None:
    rules = replace(STANDARD_RULES, allow_contested_entry=False)
    monkeypatch.setattr(BreachPointGame, "rules", property(lambda _game: rules))
    game = make_game(start=True, bot_indexes={0})
    bot = tactical_player(game, 0)
    enemy = tactical_player(game, 1)
    bot.position_id = "t_spawn"
    enemy.position_id = "outside_long"
    set_area_effect(game, SMOKE_GRENADE, "outside_long")

    assert not game._team_can_see_player(bot.team_index, enemy)
    assert bot_path_step(game, bot, ("pit",)) == "outside_long"

    game.area_effects = []
    assert game._team_can_see_player(bot.team_index, enemy)
    assert bot_path_step(game, bot, ("a_site",)) == "mid"


def test_bots_buy_for_their_side_and_prefer_rifles_when_affordable() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3}, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)

    assert game.bot_think(terrorist) == "buy_utility_smoke"
    terrorist.cash = AK47.cost
    assert game.bot_think(terrorist) == "buy_weapon_ak47"
    game.execute_action(terrorist, "buy_weapon_ak47")
    terrorist.armor = game.economy.maximum_armor
    terrorist.cash = DESERT_EAGLE.cost
    assert game.bot_think(terrorist) == "buy_weapon_desert_eagle"
    game.execute_action(terrorist, "buy_weapon_desert_eagle")
    assert game.bot_think(terrorist) == "finish_buy"

    game.execute_action(terrorist, "finish_buy")
    defender = tactical_player(game, 1)
    defender.cash = M4.cost
    assert game.bot_think(defender) == "buy_weapon_m4"

    defender.primary_weapon_id = M4.id
    defender.equipped_weapon_id = M4.id
    defender.armor = game.economy.maximum_armor
    defender.cash = DEFUSE_KIT.cost + SMOKE_GRENADE.cost + FLASHBANG.cost
    assert game.bot_think(defender) == "buy_equipment_defuse_kit"
    game.execute_action(defender, "buy_equipment_defuse_kit")
    assert game.bot_think(defender) == "buy_utility_smoke"
    game.execute_action(defender, "buy_utility_smoke")
    assert game.bot_think(defender) == "buy_utility_flashbang"


def test_bots_reserve_close_range_primaries_for_anti_eco_rounds() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3}, finish_buy_phase=False)
    entry = next(
        player
        for player in game._turn_order_players_on_team(TEAM_TERRORISTS)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    game.current_player = entry
    entry.cash = MAC10.cost
    assert game.bot_think(entry) == "finish_buy"

    game.squad_loss_streaks[entry.squad_index] = 0
    ct_squad = game._squad_for_side(TEAM_COUNTER_TERRORISTS)
    game.squad_loss_streaks[ct_squad] = game.economy.initial_loss_count + 1
    entry.cash = AK47.cost
    assert game.bot_think(entry) == "buy_weapon_nova"

    game.current_player = carrier
    carrier.cash = AK47.cost
    assert game.bot_think(carrier) == "buy_weapon_ak47"

    entry.primary_weapon_id = MAC10.id
    entry.equipped_weapon_id = MAC10.id
    entry.cash = AK47.cost
    game.current_player = entry
    assert game._bot_coordinator._preferred_primary_weapon(game, entry) is None
    game.squad_loss_streaks[ct_squad] += 1
    assert game.bot_think(entry) == "buy_weapon_ak47"

    game.current_player = defender
    defender.cash = M4.cost
    assert game.bot_think(defender) == "buy_weapon_m4"
    game.squad_loss_streaks[defender.squad_index] = 0
    t_squad = game._squad_for_side(TEAM_TERRORISTS)
    game.squad_loss_streaks[t_squad] = game.economy.initial_loss_count + 1
    assert game.bot_think(defender) == "buy_weapon_mp9"

    game.squad_loss_streaks[t_squad] += 1
    assert game.bot_think(defender) == "buy_weapon_m4"


def test_terrorist_anti_eco_roles_split_alpha_and_sustained_weapons() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
        finish_buy_phase=False,
    )
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    entry = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )
    lurker = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_LURKER
    )
    game.squad_loss_streaks[entry.squad_index] = 0
    opposing_squad = game._squad_for_side(TEAM_COUNTER_TERRORISTS)
    game.squad_loss_streaks[opposing_squad] = game.economy.initial_loss_count + 1

    for bot, expected_action in (
        (entry, "buy_weapon_nova"),
        (lurker, "buy_weapon_mac10"),
    ):
        game.current_player = bot
        bot.cash = AK47.cost
        assert game.bot_think(bot) == expected_action


def test_bots_buy_budget_rifles_only_when_the_loadout_can_protect_them() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3}, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    terrorist.cash = GALIL_AR.cost
    assert game.bot_think(terrorist) == "finish_buy"
    terrorist.cash += game.economy.armor_cost
    assert game.bot_think(terrorist) == "buy_weapon_galil_ar"
    game.execute_action(terrorist, "buy_weapon_galil_ar")
    assert game.bot_think(terrorist) == "buy_armor"

    game.current_player = defender
    defender.cash = FAMAS.cost
    assert game.bot_think(defender) == "finish_buy"
    defender.armor = game.economy.maximum_armor
    assert game.bot_think(defender) == "buy_weapon_famas"


def test_bots_upgrade_budget_rifles_when_full_buy_weapons_are_affordable() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3}, finish_buy_phase=False)
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)

    terrorist.primary_weapon_id = GALIL_AR.id
    terrorist.equipped_weapon_id = GALIL_AR.id
    terrorist.cash = AK47.cost
    assert game.bot_think(terrorist) == "buy_weapon_ak47"

    game.current_player = defender
    defender.primary_weapon_id = FAMAS.id
    defender.equipped_weapon_id = FAMAS.id
    defender.cash = M4.cost
    assert game.bot_think(defender) == "buy_weapon_m4"


def test_bot_close_range_force_buy_count_scales_with_squad_size() -> None:
    for team_size in range(2, 6):
        game = make_game(
            start=True,
            player_count=team_size * 2,
            bot_indexes=set(range(team_size * 2)),
            finish_buy_phase=False,
        )
        expected_count = max(
            1,
            team_size // game._bot_coordinator.profile.close_range_primary_team_divisor,
        )
        for team_index in (TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS):
            teammates = game._turn_order_players_on_team(team_index)
            designated = [
                teammate
                for teammate in teammates
                if game._bot_coordinator._is_designated_close_range_user(
                    game,
                    teammate,
                )
            ]
            assert len(designated) == expected_count


def test_mobile_ct_responder_covers_squad_defuse_kit_on_fresh_economy() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3}, finish_buy_phase=False)
    first_terrorist = tactical_player(game, 0)
    game.execute_action(first_terrorist, "finish_buy")
    first_defender = tactical_player(game, 1)

    assert game.bot_think(first_defender) == "buy_armor"
    game.execute_action(first_defender, "buy_armor")
    assert game.bot_think(first_defender) == "finish_buy"

    game.execute_action(first_defender, "finish_buy")
    second_terrorist = tactical_player(game, 2)
    game.execute_action(second_terrorist, "finish_buy")
    second_defender = tactical_player(game, 3)
    assert game.bot_think(second_defender) == "buy_equipment_defuse_kit"
    game.execute_action(second_defender, "buy_equipment_defuse_kit")
    assert game.bot_think(second_defender) == "buy_utility_flashbang"


def test_terrorist_pistol_squad_assigns_utility_to_the_protected_carrier() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
        finish_buy_phase=False,
    )
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    carrier = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_OBJECTIVE
    )
    entry = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )

    assert game._bot_coordinator._pistol_round_utility(game, carrier) is SMOKE_GRENADE
    carrier.utility_counts = {SMOKE_GRENADE.id: 1}
    assert game._bot_coordinator._pistol_round_utility(game, carrier) is FLASHBANG
    carrier.utility_counts[FLASHBANG.id] = 1
    assert game._bot_coordinator._pistol_round_utility(game, carrier) is FLASHBANG
    carrier.utility_counts[FLASHBANG.id] = 2
    assert game._bot_coordinator._pistol_round_utility(game, carrier) is None
    assert game._bot_coordinator._pistol_round_utility(game, entry) is None


def test_large_terrorist_pistol_squad_keeps_its_extra_player_armored() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
        finish_buy_phase=False,
    )
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    carrier = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_OBJECTIVE
    )
    support = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    carrier.utility_counts = {
        SMOKE_GRENADE.id: 1,
        FLASHBANG.id: FLASHBANG.maximum_carry,
    }

    assert game._bot_coordinator._pistol_round_utility(game, support) is None


def test_three_player_pistol_execute_sends_one_lurker_then_commits(
    monkeypatch,
) -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    coordinator = game._bot_coordinator
    monkeypatch.setattr(
        coordinator,
        "planned_attack_strategy",
        lambda _game, _attacker_count: ATTACK_STRATEGY_SPLIT,
    )
    coordinator.begin_combat_round(game)
    plan = coordinator.team_plans[TEAM_TERRORISTS]
    attackers = game._turn_order_players_on_team(TEAM_TERRORISTS)
    lurker = next(
        attacker
        for attacker in attackers
        if coordinator.assignment_for(attacker.id).role == ROLE_LURKER
    )

    assert plan.attack_strategy_id == ATTACK_STRATEGY_DIRECT
    assert all(
        bot_target_nodes(game, attacker) == (plan.attack_site_id,)
        for attacker in attackers
        if attacker is not lurker
    )
    assert bot_target_nodes(game, lurker) == (plan.primary_staging_node_id,)

    game.tactical_round = coordinator.profile.pistol_lurker_commit_tactical_round
    assert bot_target_nodes(game, lurker) == (plan.attack_site_id,)


def test_later_low_cash_round_does_not_reuse_the_pistol_utility_plan() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
        finish_buy_phase=False,
    )
    carrier = tactical_player(game, 0)
    game.round = 2
    carrier.cash = game.economy.starting_cash

    assert game._bot_coordinator._pistol_round_utility(game, carrier) is None


def test_large_direct_execute_lurker_flanks_once_then_commits() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    coordinator = game._bot_coordinator
    plan = coordinator.team_plans[TEAM_TERRORISTS]
    lurker = next(
        player
        for player in game._turn_order_players_on_team(TEAM_TERRORISTS)
        if coordinator.assignment_for(player.id).role == ROLE_LURKER
    )

    assert plan.attack_strategy_id == ATTACK_STRATEGY_DIRECT
    assert bot_target_nodes(game, lurker) == (plan.primary_staging_node_id,)

    game.tactical_round = coordinator.profile.pistol_lurker_commit_tactical_round
    assert bot_target_nodes(game, lurker) == (plan.attack_site_id,)

    game.round = 2
    game.tactical_round = 1
    coordinator.begin_combat_round(game)
    later_plan = coordinator.team_plans[TEAM_TERRORISTS]
    later_plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
    later_plan.strategy_committed = True
    assert bot_target_nodes(game, lurker) == (
        coordinator._alternate_site(game, later_plan.attack_site_id),
    )

    game.tactical_round = coordinator.profile.lurker_commit_tactical_round
    assert bot_target_nodes(game, lurker) == (later_plan.attack_site_id,)


def test_one_designated_rotator_buys_the_squads_precision_weapon() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
        finish_buy_phase=False,
    )
    first_defender, _second_defender, rotator = game._turn_order_players_on_team(
        TEAM_COUNTER_TERRORISTS
    )
    game.current_player = rotator
    rotator.cash = AWP.cost

    assert game.bot_think(rotator) == "buy_weapon_awp"

    first_defender.primary_weapon_id = AWP.id
    first_defender.equipped_weapon_id = AWP.id
    assert game.bot_think(rotator) == "buy_weapon_m4"


def test_designated_precision_bot_protects_an_ssg08_force_buy_with_armor() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
        finish_buy_phase=False,
    )
    rotator = game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)[-1]
    game.current_player = rotator
    rotator.cash = SSG08.cost + game.economy.armor_cost

    assert game.bot_think(rotator) == "buy_weapon_ssg08"
    game.execute_action(rotator, "buy_weapon_ssg08")
    assert game.bot_think(rotator) == "buy_armor"


def test_bot_squad_limits_upgraded_sidearms_to_one_full_loadout() -> None:
    game = make_game(
        start=True,
        bot_indexes={0, 1, 2, 3},
        finish_buy_phase=False,
    )
    first_terrorist, second_terrorist = game._turn_order_players_on_team(
        TEAM_TERRORISTS
    )
    for bot in (first_terrorist, second_terrorist):
        bot.primary_weapon_id = AK47.id
        bot.equipped_weapon_id = AK47.id
        bot.armor = game.economy.maximum_armor
        bot.cash = DESERT_EAGLE.cost

    game.current_player = first_terrorist
    assert game.bot_think(first_terrorist) == "buy_weapon_desert_eagle"
    game.execute_action(first_terrorist, "buy_weapon_desert_eagle")

    game.current_player = second_terrorist
    assert game.bot_think(second_terrorist) == "buy_utility_smoke"


def test_bots_split_sites_then_rotate_to_a_public_planted_bomb() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    terrorist_a = tactical_player(game, 0)
    terrorist_b = tactical_player(game, 2)
    defender_a = tactical_player(game, 1)
    defender_b = tactical_player(game, 3)

    assert bot_target_nodes(game, defender_a) == ("a_site",)
    assert bot_target_nodes(game, defender_b) == ("b_site",)

    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    terrorist_a.position_id = "b_site"
    terrorist_b.position_id = "b_site"
    defender_a.position_id = "a_site"
    start_activation(game, defender_a)

    assert bot_target_nodes(game, defender_a) == ("b_site",)
    assert bot_path_step(game, defender_a, ("b_site",)) == "ct_spawn"
    assert game.bot_think(defender_a) == "move_ct_spawn"
    game.execute_action(defender_a, "move_ct_spawn")
    complete_movement(game)
    assert game.bot_think(defender_a) == "move_b_doors"


def test_ct_prioritizes_a_cross_site_rotation_over_a_tempo_shot() -> None:
    game = make_game(start=True, bot_indexes={1})
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = "a_site"
    defender.position_id = "ct_spawn"
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == "move_b_doors"
    assert terrorist.health == game.rules.max_health


def test_ct_bot_fights_a_shared_node_enemy_before_rotating_with_time() -> None:
    game = make_game(start=True, bot_indexes={1})
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = defender.position_id = "ct_mid"
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == f"shoot_{terrorist.id}"
    game.execute_action(defender, f"shoot_{terrorist.id}")
    complete_weapon_fire(game)

    assert defender.position_id == "ct_mid"
    assert defender.action_points == 1
    assert terrorist.health < game.rules.max_health


def test_bot_switches_to_sidearm_after_spending_its_rifle_attack() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    bot = tactical_player(game, 0)
    target = tactical_player(game, 1)
    bot.primary_weapon_id = AK47.id
    bot.equipped_weapon_id = AK47.id
    bot.position_id = "a_ramp"
    target.position_id = "a_site"
    start_activation(game, bot)

    assert game.bot_think(bot) == f"shoot_{target.id}"
    game.execute_action(bot, f"shoot_{target.id}")
    complete_weapon_fire(game)
    assert game.bot_think(bot) == "equip_sidearm"
    game.execute_action(bot, "equip_sidearm")
    assert game.bot_think(bot) == f"shoot_{target.id}"


def test_m4_bot_commits_its_followup_burst_to_a_wounded_target() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    target = tactical_player(game, 0)
    bot = tactical_player(game, 1)
    second_target = tactical_player(game, 2)
    ally = tactical_player(game, 3)
    bot.primary_weapon_id = M4.id
    bot.equipped_weapon_id = M4.id
    bot.position_id = "mid_doors"
    target.position_id = "ct_mid"
    second_target.position_id = "mid"
    ally.position_id = "mid_doors"
    start_activation(game, bot)

    assert game.bot_think(bot) == f"shoot_{target.id}"
    game.execute_action(bot, f"shoot_{target.id}")
    complete_weapon_fire(game)
    assert target.health == 46
    assert (
        game._is_shoot_enabled(
            bot,
            action_id=f"shoot_{second_target.id}",
        )
        is None
    )
    assert game.bot_think(bot) == f"shoot_{target.id}"


def test_bot_reloads_before_moving_when_the_next_full_attack_is_unavailable() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    bot = tactical_player(game, 1)
    bot.primary_weapon_id = M4.id
    bot.equipped_weapon_id = M4.id
    bot.weapon_magazine_ammo[M4.id] = M4.ammunition_per_attack - 1
    bot.weapon_reserve_units[M4.id] = 1
    start_activation(game, bot)

    assert game.bot_think(bot) == "reload"
    game.execute_action(bot, "reload")

    assert bot.weapon_magazine_ammo[M4.id] == M4.magazine_capacity
    assert bot.weapon_reserve_units[M4.id] == 0
    assert bot.action_points == 1


def test_outnumbered_ct_bot_falls_back_after_firing() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    first_target = tactical_player(game, 0)
    bot = tactical_player(game, 1)
    second_target = tactical_player(game, 2)
    third_target = tactical_player(game, 4)
    bot.primary_weapon_id = M4.id
    bot.equipped_weapon_id = M4.id
    bot.position_id = "a_short"
    first_target.position_id = "a_site"
    second_target.position_id = "catwalk"
    third_target.position_id = "a_site"
    start_activation(game, bot)

    game.execute_action(bot, f"shoot_{first_target.id}")
    complete_weapon_fire(game)

    assert game.bot_think(bot) == "move_ct_spawn"


def test_ct_pair_holds_ground_against_an_equal_visible_force() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    first_target = tactical_player(game, 0)
    bot = tactical_player(game, 1)
    second_target = tactical_player(game, 2)
    ally = tactical_player(game, 3)
    bot.primary_weapon_id = M4.id
    bot.equipped_weapon_id = M4.id
    bot.position_id = ally.position_id = "a_short"
    first_target.position_id = "a_site"
    second_target.position_id = "catwalk"
    start_activation(game, bot)

    game.execute_action(bot, f"shoot_{first_target.id}")
    complete_weapon_fire(game)

    assert game.bot_think(bot) == f"shoot_{first_target.id}"


def test_exhausted_bot_ends_activation_when_it_cannot_afford_disengagement() -> None:
    game = make_game(start=True, bot_indexes={1})
    target = tactical_player(game, 0)
    bot = tactical_player(game, 1)
    bot.primary_weapon_id = M4.id
    bot.equipped_weapon_id = M4.id
    bot.position_id = target.position_id = "a_site"
    start_activation(game, bot)
    bot.action_points = 1
    bot.shots_fired_this_activation = (
        M4.shots_per_activation + USP_S.shots_per_activation
    )
    bot.weapon_shots_fired_this_activation = {
        M4.id: M4.shots_per_activation,
        USP_S.id: USP_S.shots_per_activation,
    }

    assert bot_path_step(game, bot, ("b_site",)) == "ct_spawn"
    assert game.bot_think(bot) == "end_turn"


def test_bot_fights_before_starting_a_co_located_objective_when_ap_allows() -> None:
    game = make_game(start=True, bot_indexes={0, 1})
    planter = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    planter.position_id = defender.position_id = "a_site"
    game.bomb_carrier_id = planter.id
    start_activation(game, planter)

    assert game.bot_think(planter) == f"shoot_{defender.id}"
    game.execute_action(planter, f"shoot_{defender.id}")
    complete_weapon_fire(game)
    assert game.bot_think(planter) == "plant"

    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    defender.equipment_counts = {DEFUSE_KIT.id: 1}
    start_activation(game, defender)

    assert game.bot_think(defender) == f"shoot_{planter.id}"
    game.execute_action(defender, f"shoot_{planter.id}")
    complete_weapon_fire(game)
    assert game.bot_think(defender) == "defuse"


def test_bot_prioritizes_an_urgent_full_ap_objective_attempt() -> None:
    game = make_game(start=True, bot_indexes={1})
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = defender.position_id = "a_site"
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    game.bomb_fuse_remaining = 1
    start_activation(game, defender)

    assert game._defuse_action_point_cost(defender) == defender.action_points
    assert game.bot_think(defender) == "defuse"


def test_bot_uses_objective_when_visible_enemy_is_out_of_weapon_range() -> None:
    game = make_game(start=True, bot_indexes={0})
    planter = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    planter.position_id = "a_site"
    defender.position_id = "pit"
    game.bomb_carrier_id = planter.id
    start_activation(game, planter)

    assert game._can_see(planter, defender)
    assert not game._weapon_can_reach(planter, defender)
    assert game.bot_think(planter) == "plant"


def test_ct_roles_follow_activation_order_after_halftime_rotation() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    game._swap_sides()
    game._reset_economy(game.economy.starting_cash)
    game._prepare_combat_round()
    first_defender = tactical_player(game, 2)
    second_defender = tactical_player(game, 0)

    assert [
        defender.id
        for defender in game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
    ] == [first_defender.id, second_defender.id]
    assert game._bot_coordinator.assigned_bomb_site(game, first_defender) == "a_site"
    assert game._bot_coordinator.assigned_bomb_site(game, second_defender) == "b_site"
    assert game._bot_coordinator.team_priority_equipment(game, first_defender) is None
    assert (
        game._bot_coordinator.team_priority_equipment(game, second_defender)
        is DEFUSE_KIT
    )


def test_ct_site_assignments_rotate_between_combat_rounds() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    first_defender, second_defender, _rotator = game._turn_order_players_on_team(
        TEAM_COUNTER_TERRORISTS
    )
    assert game._bot_coordinator.assigned_bomb_site(game, first_defender) == "a_site"
    assert game._bot_coordinator.assigned_bomb_site(game, second_defender) == "b_site"

    game.round = 2
    game._bot_coordinator.begin_combat_round(game)

    assert game._bot_coordinator.assigned_bomb_site(game, first_defender) == "b_site"
    assert game._bot_coordinator.assigned_bomb_site(game, second_defender) == "a_site"


def test_ct_site_rotation_restarts_symmetrically_at_each_half() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
        match_format="mr7",
    )
    game.round = game.match_format.rounds_per_half + 1
    game._swap_sides()
    game._reset_economy(game.economy.starting_cash)
    game._prepare_combat_round()
    first_defender, second_defender, _rotator = game._turn_order_players_on_team(
        TEAM_COUNTER_TERRORISTS
    )

    assert game._bot_coordinator.assigned_bomb_site(game, first_defender) == "a_site"
    assert game._bot_coordinator.assigned_bomb_site(game, second_defender) == "b_site"


def test_bot_smokes_a_known_objective_before_entering_it() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    defender = tactical_player(game, 1)
    defender.position_id = "b_doors"
    defender.utility_counts = {SMOKE_GRENADE.id: 1}
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == "throw_smoke_b_site"
    game.execute_action(defender, "throw_smoke_b_site")
    complete_utility(game)
    assert game._is_smoked("b_site")
    assert game.bot_think(defender) == "move_b_site"


def test_terrorist_support_smokes_a_publicly_observed_crossfire() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "a_site"
    plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
    plan.strategy_committed = True
    support = next(
        player
        for player in game._players_on_team(TEAM_TERRORISTS, alive_only=True)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    first_defender, second_defender = game._players_on_team(
        TEAM_COUNTER_TERRORISTS,
        alive_only=True,
    )[:2]
    support.position_id = "a_ramp"
    support.utility_counts = {SMOKE_GRENADE.id: 1}
    first_defender.position_id = second_defender.position_id = "a_site"
    start_activation(game, support)

    assert game.bot_think(support) == "throw_smoke_a_site"


def test_terrorist_support_smokes_the_defender_lane_during_an_execute() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "a_site"
    plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
    plan.strategy_committed = True
    support = next(
        player
        for player in game._players_on_team(TEAM_TERRORISTS, alive_only=True)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    first_defender, second_defender = game._players_on_team(
        TEAM_COUNTER_TERRORISTS,
        alive_only=True,
    )[:2]
    support.position_id = "a_short"
    support.utility_counts = {SMOKE_GRENADE.id: 1}
    first_defender.position_id = second_defender.position_id = "ct_spawn"
    start_activation(game, support)

    assert game.bot_think(support) == "throw_smoke_ct_spawn"


def test_terrorist_support_escorts_without_backtracking_from_the_execute() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "a_site"
    plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
    plan.strategy_committed = True
    carrier = game._breach_player_by_id(game.bomb_carrier_id)
    support = next(
        player
        for player in game._players_on_team(TEAM_TERRORISTS, alive_only=True)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    assert carrier is not None

    carrier.position_id = "mid"
    support.position_id = "a_ramp"
    assert bot_target_nodes(game, support) == ("a_site",)

    carrier.position_id = "a_ramp"
    support.position_id = "t_spawn"
    assert bot_target_nodes(game, support) == ("a_ramp",)


def test_bot_with_kit_moves_then_defuses_instead_of_delaying_for_smoke() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    defender = tactical_player(game, 1)
    defender.position_id = "b_doors"
    defender.equipment_counts = {DEFUSE_KIT.id: 1}
    defender.utility_counts = {SMOKE_GRENADE.id: 1}
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == "move_b_site"
    game.execute_action(defender, "move_b_site")
    complete_movement(game)
    assert game.bot_think(defender) == "defuse"


def test_terrorist_bot_plan_switches_site_and_pattern_after_a_failed_execute() -> None:
    game = make_game(
        start=True,
        bot_indexes={0, 1, 2, 3},
        match_format="mr7",
    )
    carrier = tactical_player(game, 0)

    assert bot_target_nodes(game, carrier) == ("a_site",)
    assert (
        game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )
    game._bot_coordinator.record_round_result(game, TEAM_COUNTER_TERRORISTS)
    game.round = 2
    game._bot_coordinator.begin_combat_round(game)
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    assert plan.attack_site_id == "b_site"
    assert plan.attack_strategy_id == ATTACK_STRATEGY_SPLIT
    assert bot_target_nodes(game, carrier) == (plan.primary_staging_node_id,)


def test_attack_pattern_cycle_respects_squad_size() -> None:
    three_player_game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    coordinator = three_player_game._bot_coordinator
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )
    coordinator.record_round_result(three_player_game, TEAM_COUNTER_TERRORISTS)
    three_player_game.round += 1
    coordinator.begin_combat_round(three_player_game)
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_SPLIT
    )
    coordinator.record_round_result(three_player_game, TEAM_COUNTER_TERRORISTS)
    three_player_game.round += 1
    coordinator.begin_combat_round(three_player_game)
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )

    four_player_game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    coordinator = four_player_game._bot_coordinator
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )
    for expected_strategy in (ATTACK_STRATEGY_SPLIT, ATTACK_STRATEGY_DIRECT):
        coordinator.record_round_result(
            four_player_game,
            TEAM_COUNTER_TERRORISTS,
        )
        four_player_game.round += 1
        coordinator.begin_combat_round(four_player_game)
        assert (
            coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
            == expected_strategy
        )

    five_player_game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    coordinator = five_player_game._bot_coordinator
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )
    for expected_strategy in (ATTACK_STRATEGY_SPLIT, ATTACK_STRATEGY_FAKE):
        coordinator.record_round_result(
            five_player_game,
            TEAM_COUNTER_TERRORISTS,
        )
        five_player_game.round += 1
        coordinator.begin_combat_round(five_player_game)
        assert (
            coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
            == expected_strategy
        )

    two_player_game = make_game(
        start=True,
        bot_indexes={0, 1, 2, 3},
    )
    coordinator = two_player_game._bot_coordinator
    coordinator.record_round_result(two_player_game, TEAM_COUNTER_TERRORISTS)
    two_player_game.round += 1
    coordinator.begin_combat_round(two_player_game)
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_SPLIT
    )
    coordinator.record_round_result(two_player_game, TEAM_COUNTER_TERRORISTS)
    two_player_game.round += 1
    coordinator.begin_combat_round(two_player_game)
    assert (
        coordinator.team_plans[TEAM_TERRORISTS].attack_strategy_id
        == ATTACK_STRATEGY_DIRECT
    )


def test_split_execute_uses_a_map_derived_route_without_backtracking() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_strategy_id = ATTACK_STRATEGY_SPLIT
    plan.strategy_committed = False
    plan.completed_strategy_route_player_ids.clear()
    stage = plan.split_staging_node_id
    stage_node = game._node(stage)
    assert stage_node is not None
    assert stage not in {
        *game.tactical_map.bomb_site_ids(),
        game.tactical_map.terrorist_spawn,
        game.tactical_map.counter_terrorist_spawn,
    }
    route = game._bot_coordinator._topology_path(game, stage, plan.attack_site_id)
    assert route[0] == stage
    assert route[-1] == plan.attack_site_id
    assert len(route) == len(set(route))
    assert all(
        destination_id in game._node(source_id).adjacent
        for source_id, destination_id in pairwise(route)
    )
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    carrier = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_OBJECTIVE
    )
    entry = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )
    support = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    lurker = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_LURKER
    )

    assert bot_target_nodes(game, carrier) == (plan.primary_staging_node_id,)
    assert bot_target_nodes(game, support) == (stage,)
    assert bot_target_nodes(game, lurker) == (stage,)
    assert bot_target_nodes(game, entry) == (plan.primary_staging_node_id,)

    carrier.position_id = plan.primary_staging_node_id
    entry.position_id = plan.primary_staging_node_id
    support.position_id = stage
    lurker.position_id = stage
    game._bot_coordinator.observe(game)
    assert support.id in plan.completed_strategy_route_player_ids
    assert lurker.id in plan.completed_strategy_route_player_ids
    assert plan.strategy_committed
    assert bot_target_nodes(game, carrier) == (plan.attack_site_id,)
    assert bot_target_nodes(game, support) == (plan.attack_site_id,)


def test_split_execute_groups_scale_evenly_from_two_to_five_players() -> None:
    expected_route_sizes = {2: 1, 3: 1, 4: 2, 5: 2}
    for team_size, expected_route_size in expected_route_sizes.items():
        game = make_game(
            start=True,
            player_count=team_size * 2,
            bot_indexes=set(range(team_size * 2)),
        )
        plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
        route_assignments = [
            assignment
            for assignment in plan.assignments.values()
            if game._bot_coordinator._uses_split_route(plan, assignment)
        ]

        assert len(route_assignments) == expected_route_size
        assert len(plan.assignments) - len(route_assignments) >= expected_route_size


def test_split_execute_commits_on_schedule_if_one_route_is_delayed() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_strategy_id = ATTACK_STRATEGY_SPLIT
    plan.strategy_committed = False
    game.tactical_round = game._bot_coordinator.profile.split_commit_tactical_round

    game._bot_coordinator.observe(game)

    assert plan.strategy_committed
    assert all(
        bot_target_nodes(game, player) == (plan.attack_site_id,)
        for player in game._turn_order_players_on_team(TEAM_TERRORISTS)
    )


def test_attacking_sniper_advances_after_covering_a_route_for_one_activation() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_strategy_id = ATTACK_STRATEGY_SPLIT
    plan.strategy_committed = False
    plan.attack_site_id = "a_site"
    plan.split_staging_node_id = "mid_doors"
    plan.completed_strategy_route_player_ids.clear()
    support = next(
        player
        for player in game._turn_order_players_on_team(TEAM_TERRORISTS)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    support.position_id = "mid"
    support.primary_weapon_id = AWP.id
    support.equipped_weapon_id = AWP.id
    support.held_angle_origin_id = "mid"
    support.held_angle_node_id = "mid_doors"
    start_activation(game, support)

    assert game.bot_think(support) == "move_mid_doors"


def test_fake_execute_stages_bomb_sells_decoy_then_commits() -> None:
    game = make_game(
        start=True,
        player_count=8,
        bot_indexes=set(range(8)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_strategy_id = ATTACK_STRATEGY_FAKE
    plan.strategy_committed = False
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    carrier = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_OBJECTIVE
    )
    entry = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )
    lurker = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_LURKER
    )

    assert bot_target_nodes(game, carrier) == (plan.primary_staging_node_id,)
    assert bot_target_nodes(game, entry) == (plan.decoy_site_id,)
    assert bot_target_nodes(game, lurker) == (plan.decoy_site_id,)

    game.tactical_round = game._bot_coordinator.profile.fake_commit_tactical_round
    game._bot_coordinator.observe(game)
    assert plan.strategy_committed
    assert bot_target_nodes(game, carrier) == (plan.attack_site_id,)
    assert bot_target_nodes(game, entry) == (plan.attack_site_id,)
    assert bot_target_nodes(game, lurker) == (plan.attack_site_id,)


def test_fake_execute_commits_early_after_confirmed_decoy_contacts() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_strategy_id = ATTACK_STRATEGY_FAKE
    plan.strategy_committed = False
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    diversion_players = [
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role
        in {ROLE_ENTRY, ROLE_LURKER}
    ]
    defenders = game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
    for player in (*diversion_players, *defenders[:2]):
        player.position_id = plan.decoy_site_id

    game._bot_coordinator.observe(game)

    assert len(game._bot_coordinator.contacts_for_team(TEAM_TERRORISTS)) >= 2
    assert plan.strategy_committed


def test_bomb_carrier_stages_behind_the_entry_player() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    carrier = tactical_player(game, 0)
    entry = tactical_player(game, 2)
    start_activation(game, carrier)

    assert game.bot_think(carrier) == "move_mid"
    game.execute_action(carrier, "move_mid")
    complete_movement(game)

    assert carrier.position_id == "mid"
    assert entry.position_id == "t_spawn"
    assert game.bot_think(carrier) == "end_turn"


def test_bomb_carrier_preserves_smoke_for_the_site_execute() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    carrier = tactical_player(game, 0)
    carrier.utility_counts = {SMOKE_GRENADE.id: 1}
    start_activation(game, carrier)

    assert game.bot_think(carrier) == "move_mid"


def test_site_anchor_flashes_a_visible_execute_before_firing() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    carrier = tactical_player(game, 0)
    anchor = tactical_player(game, 1)
    entry = tactical_player(game, 2)
    carrier.position_id = entry.position_id = "a_ramp"
    anchor.position_id = "a_site"
    anchor.utility_counts = {FLASHBANG.id: 1}
    start_activation(game, anchor)

    assert game.bot_think(anchor) == "throw_flashbang_a_ramp"


def test_entry_flashes_a_visible_site_defender_without_private_angle_knowledge() -> (
    None
):
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = "a_ramp"
    entry.utility_counts = {FLASHBANG.id: 1}
    defender.position_id = "a_site"
    defender.held_angle_origin_id = ""
    defender.held_angle_node_id = ""
    start_activation(game, entry)

    assert game._bot_coordinator.assignment_for(entry.id).role == ROLE_ENTRY
    assert game.bot_think(entry) == "throw_flashbang_a_site"


def test_bot_uses_he_against_grouped_visible_enemies() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    thrower = tactical_player(game, 0)
    first_enemy = tactical_player(game, 1)
    second_enemy = tactical_player(game, 3)
    thrower.position_id = "a_ramp"
    first_enemy.position_id = second_enemy.position_id = "a_site"
    thrower.utility_counts = {HE_GRENADE.id: 1}
    start_activation(game, thrower)

    assert game.bot_think(thrower) == "throw_he_grenade_a_site"


def test_bot_uses_fire_to_deny_a_visible_bombsite() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    thrower = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    thrower.position_id = "a_ramp"
    defender.position_id = "a_site"
    thrower.utility_counts = {MOLOTOV.id: 1}
    start_activation(game, thrower)

    assert game.bot_think(thrower) == "throw_molotov_a_site"


def test_bot_path_avoids_known_fire_when_a_safe_route_exists() -> None:
    game = make_game(start=True, bot_indexes={0})
    bot = tactical_player(game, 0)
    set_area_effect(
        game,
        INCENDIARY_GRENADE,
        "outside_long",
        source_player_id=tactical_player(game, 1).id,
        known_team_indexes=[TEAM_TERRORISTS],
    )

    assert bot_path_step(game, bot, ("a_site",)) == "mid"


def test_bomb_carrier_uses_the_squad_flash_to_support_a_site_execute() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    carrier.position_id = "a_ramp"
    carrier.utility_counts = {FLASHBANG.id: 1}
    defender.position_id = "a_site"
    start_activation(game, carrier)

    assert game._bot_coordinator.assignment_for(carrier.id).role == ROLE_OBJECTIVE
    assert game.bot_think(carrier) == "throw_flashbang_a_site"


def test_bomb_carrier_can_flash_the_execute_after_moving_into_throw_range() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    carrier.position_id = "a_ramp"
    carrier.action_points = FLASHBANG.action_point_cost
    carrier.utility_counts = {FLASHBANG.id: 1}
    defender.position_id = "a_site"
    game.current_player = carrier

    assert game.bot_think(carrier) == "throw_flashbang_a_site"


def test_bomb_carrier_flashes_a_visible_site_approach_during_the_execute() -> None:
    game = make_game(start=True, bot_indexes={0, 1, 2, 3})
    carrier = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    carrier.position_id = "a_site"
    carrier.utility_counts = {FLASHBANG.id: 1}
    defender.position_id = "a_short"
    start_activation(game, carrier)

    assert game.bot_think(carrier) == "throw_flashbang_a_short"


def test_entry_holds_the_captured_site_for_the_incoming_carrier() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    entry = tactical_player(game, 2)
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "a_site"
    plan.strategy_committed = True
    entry.position_id = "a_site"
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, entry)
    entry.action_points = GLOCK.hold_action_point_cost

    assert game.bot_think(entry) == "hold_angle_a_site"


def test_entry_takes_a_site_while_its_visible_defender_is_flashed() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = "a_ramp"
    defender.position_id = "a_site"
    defender.flash_penalty = FLASHBANG.activation_penalty
    start_activation(game, entry)
    entry.action_points = game.rules.move_cost

    assert game.bot_think(entry) == "move_a_site"


def test_entry_does_not_rush_an_unflashed_site_defender() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = "a_ramp"
    defender.position_id = "a_site"
    start_activation(game, entry)
    entry.action_points = game.rules.move_cost

    assert game.bot_think(entry) == f"shoot_{defender.id}"


def test_support_trades_the_entry_by_taking_contested_site_space() -> None:
    game = make_game(start=True, player_count=8, bot_indexes=set(range(8)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    support = tactical_player(game, 4)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = defender.position_id = "a_site"
    support.position_id = "a_ramp"
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, support)
    support.action_points = game.rules.move_cost

    assert not game._can_see(support, defender)
    assert game._bot_coordinator.assignment_for(support.id).role == ROLE_SUPPORT
    assert game.bot_think(support) == "move_a_site"


def test_support_takes_a_lethal_trade_shot_before_moving_onto_site() -> None:
    game = make_game(start=True, player_count=8, bot_indexes=set(range(8)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    support = tactical_player(game, 4)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = defender.position_id = "a_site"
    support.position_id = "a_ramp"
    defender.health = GLOCK.damage_at_range(1)
    start_activation(game, support)

    assert game.bot_think(support) == f"shoot_{defender.id}"


def test_support_trades_a_recently_eliminated_entry_without_chasing_stale_contact() -> (
    None
):
    game = make_game(start=True, player_count=8, bot_indexes=set(range(8)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    support = tactical_player(game, 4)
    plan = game._bot_coordinator.team_plans[TEAM_TERRORISTS]
    plan.attack_site_id = "a_site"
    entry.position_id = defender.position_id = "a_site"
    support.position_id = "a_ramp"
    game._bot_coordinator.observe(game)
    entry.health = 0
    entry.eliminated = True
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, support)

    assert game.bot_think(support) == "move_a_site"

    support.position_id = "a_ramp"
    game.tactical_round += 1
    start_activation(game, support)

    assert game._bot_coordinator._trade_entry_action(game, support) is None


def test_support_trades_an_entry_eliminated_during_a_watched_move() -> None:
    game = make_game(start=True, player_count=8, bot_indexes=set(range(8)))
    entry = tactical_player(game, 2)
    defender = tactical_player(game, 1)
    support = tactical_player(game, 4)
    game._bot_coordinator.team_plans[TEAM_TERRORISTS].attack_site_id = "a_site"
    entry.position_id = support.position_id = "a_ramp"
    entry.health = 20
    defender.position_id = "a_site"
    defender.held_angle_origin_id = "a_site"
    defender.held_angle_node_id = "a_site"
    set_area_effect(game, SMOKE_GRENADE, "a_site")
    start_activation(game, entry)
    entry.action_points = game.rules.move_cost

    game.execute_action(entry, "move_a_site")
    complete_movement(game)

    assert game.reaction_window.is_open
    assert game.current_player is defender
    game.execute_action(defender, "reaction_shoot")
    complete_weapon_fire(game)
    assert entry.eliminated

    support.position_id = "a_ramp"
    start_activation(game, support)
    assert game.bot_think(support) == "move_a_site"


def test_small_ct_squad_fully_rotates_after_confirming_the_execute() -> None:
    game = make_game(start=True, player_count=6, bot_indexes=set(range(6)))
    carrier = tactical_player(game, 0)
    a_anchor = tactical_player(game, 1)
    entry = tactical_player(game, 2)
    b_anchor = tactical_player(game, 3)
    carrier.position_id = entry.position_id = "a_long"
    a_anchor.position_id = "a_site"
    b_anchor.position_id = "b_site"

    game._bot_coordinator.observe(game)

    assert bot_target_nodes(game, b_anchor) == ("a_long",)


def test_bot_with_awp_prepares_then_uses_a_visible_angle() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    sniper = tactical_player(game, 1)
    target = tactical_player(game, 0)
    sniper.position_id = "pit"
    target.position_id = "a_site"
    sniper.primary_weapon_id = AWP.id
    sniper.equipped_weapon_id = AWP.id
    start_activation(game, sniper)

    assert game.bot_think(sniper) == "hold_angle_a_site"
    game.execute_action(sniper, "hold_angle_a_site")
    start_activation(game, sniper)
    assert game.bot_think(sniper) == f"shoot_{target.id}"


def test_awp_bot_prepares_a_likely_ingress_angle_after_deploying() -> None:
    game = make_game(start=True, bot_indexes={1})
    sniper = tactical_player(game, 1)
    sniper.position_id = "a_site"
    sniper.primary_weapon_id = AWP.id
    sniper.equipped_weapon_id = AWP.id
    start_activation(game, sniper)

    assert game._bot_coordinator.assigned_bomb_site(game, sniper) == "a_site"
    assert game.bot_think(sniper) == "hold_angle_pit"


def test_rifle_anchor_occupies_its_site_and_holds_point_blank_entry() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    anchor = tactical_player(game, 1)
    anchor.primary_weapon_id = M4.id
    anchor.equipped_weapon_id = M4.id
    start_activation(game, anchor)

    assert game._bot_coordinator.assigned_bomb_site(game, anchor) == "a_site"
    assert game.bot_think(anchor) == "move_a_site"
    game.execute_action(anchor, "move_a_site")
    complete_movement(game)

    start_activation(game, anchor)
    assert game.bot_think(anchor) == "hold_angle_a_site"
    game.execute_action(anchor, "hold_angle_a_site")

    start_activation(game, anchor)
    assert game.bot_think(anchor) == "end_turn"
    assert anchor.held_angle_origin_id == "a_site"
    assert anchor.held_angle_node_id == "a_site"


def test_terrorist_entry_leads_the_carrier_and_then_defends_postplant() -> None:
    game = make_game(start=True, bot_indexes={1, 2, 3})
    escort = tactical_player(game, 2)
    carrier = tactical_player(game, 0)
    carrier.position_id = "a_long"
    escort.position_id = "t_spawn"

    assert bot_target_nodes(game, escort) == ("a_site",)
    assert bot_path_step(game, escort, ("a_site",)) == "mid"

    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    assert bot_target_nodes(game, escort) == ("b_doors",)


def test_large_terrorist_squad_spreads_specialists_after_planting() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    carrier, entry, first_support, second_support, lurker = (
        game._turn_order_players_on_team(TEAM_TERRORISTS)
    )
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"

    assert bot_target_nodes(game, carrier) == ("a_site",)
    assert bot_target_nodes(game, entry) == ("ct_spawn",)
    assert bot_target_nodes(game, first_support) == ("a_site",)
    assert bot_target_nodes(game, second_support) == ("a_site",)
    assert bot_target_nodes(game, lurker) == ("a_short",)


def test_postplant_site_support_holds_the_bomb_while_specialists_spread() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
    support = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_SUPPORT
    )
    entry = next(
        player
        for player in terrorists
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ENTRY
    )
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "a_site"
    support.position_id = entry.position_id = "a_site"
    start_activation(game, support)

    assert (
        game._bot_coordinator._proactive_angle_action(game, support)
        == "hold_angle_a_site"
    )
    start_activation(game, entry)
    assert game._bot_coordinator._proactive_angle_action(game, entry) is None


def test_bot_memory_records_only_team_visible_contacts_and_expires() -> None:
    game = make_game(start=True, bot_indexes={1})
    carrier = tactical_player(game, 0)
    observer = tactical_player(game, 1)

    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS) == ()

    observer.position_id = "ct_spawn"
    carrier.position_id = "a_site"
    game._bot_coordinator.observe(game)
    contacts = game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)
    assert [(contact.player_id, contact.node_id) for contact in contacts] == [
        (carrier.id, "a_site")
    ]

    observer.position_id = tactical_player(game, 3).position_id = "b_doors"
    game.tactical_round += game._bot_coordinator.profile.contact_memory_tactical_rounds
    game._bot_coordinator.observe(game)
    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)

    game.tactical_round += 1
    game._bot_coordinator.observe(game)
    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS) == ()


def test_completed_actions_feed_visible_contacts_into_bot_memory() -> None:
    game = make_game(start=True, bot_indexes={1})
    mover = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    observer.position_id = tactical_player(game, 3).position_id = "a_short"

    game.execute_action(mover, "move_mid")
    complete_movement(game)
    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS) == ()

    game.execute_action(mover, "move_catwalk")
    complete_movement(game)
    contacts = game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)
    assert [(contact.player_id, contact.node_id) for contact in contacts] == [
        (mover.id, "catwalk")
    ]


def test_rotator_uses_a_teammates_last_known_contact_without_hidden_vision() -> None:
    game = make_game(start=True, player_count=6, bot_indexes={5})
    enemy = tactical_player(game, 0)
    spotter = tactical_player(game, 1)
    rotator = tactical_player(game, 5)
    enemy.position_id = "a_long"
    spotter.position_id = "a_site"
    rotator.position_id = "ct_spawn"

    assert not game._can_see(rotator, enemy)
    game._bot_coordinator.observe(game)
    assignment = game._bot_coordinator.assignment_for(rotator.id)
    assert assignment is not None
    assert assignment.role == ROLE_ROTATOR
    assert bot_target_nodes(game, rotator) == ("b_doors",)

    start_activation(game, rotator)
    assert game.bot_think(rotator) == "move_b_doors"
    game.execute_action(rotator, "move_b_doors")
    complete_movement(game)
    assert bot_target_nodes(game, rotator) == ("a_long",)
    assert game.bot_think(rotator) == "move_ct_spawn"


def test_large_defense_does_not_overrotate_to_an_unconfirmed_decoy() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    attackers = game._turn_order_players_on_team(TEAM_TERRORISTS)
    defenders = game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
    rotator = next(
        player
        for player in defenders
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ROTATOR
    )
    rotator.position_id = "b_doors"
    for attacker in attackers[1:3]:
        attacker.position_id = "b_site"

    game._bot_coordinator.observe(game)

    assert len(game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)) == 2
    assert bot_target_nodes(game, rotator) == ("b_doors",)

    carrier = next(player for player in attackers if player.id == game.bomb_carrier_id)
    carrier.position_id = "b_site"
    game._bot_coordinator.observe(game)

    assert bot_target_nodes(game, rotator) == ("b_site",)


def test_small_defense_rotates_when_visible_contacts_are_a_majority() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    attackers = game._turn_order_players_on_team(TEAM_TERRORISTS)
    rotator = next(
        player
        for player in game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
        if game._bot_coordinator.assignment_for(player.id).role == ROLE_ROTATOR
    )
    rotator.position_id = "b_doors"
    for attacker in attackers[1:]:
        attacker.position_id = "b_site"

    game._bot_coordinator.observe(game)

    assert len(game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)) == 2
    assert bot_target_nodes(game, rotator) == ("b_site",)


def test_bot_memory_is_runtime_only_and_cleared_at_lifecycle_boundaries() -> None:
    game = make_game(start=True, bot_indexes={1})
    enemy = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    observer.position_id = "ct_mid"
    enemy.position_id = "a_site"
    game._bot_coordinator.observe(game)
    game._bot_coordinator.record_round_result(game, TEAM_TERRORISTS)
    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)
    assert game._bot_coordinator.squad_memories

    observer.position_id = tactical_player(game, 3).position_id = "b_doors"
    payload = json.loads(game.to_json())
    assert "_bot_coordinator" not in payload
    restored = BreachPointGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS) == ()
    assert restored._bot_coordinator.squad_memories == {}

    game.on_discard()
    assert game._bot_coordinator.team_plans == {}
    assert game._bot_coordinator.squad_memories == {}
    game.on_discard()
    assert game._bot_coordinator.team_plans == {}
    assert game._bot_coordinator.squad_memories == {}


def test_match_completion_immediately_releases_bot_memory() -> None:
    game = make_game(start=True, bot_indexes={1})
    enemy = tactical_player(game, 0)
    observer = tactical_player(game, 1)
    observer.position_id = "ct_mid"
    enemy.position_id = "a_site"
    game._bot_coordinator.observe(game)
    game._bot_coordinator.record_round_result(game, TEAM_TERRORISTS)
    player = tactical_player(game, 0)
    game._create_dropped_weapon(
        AK47,
        player.position_id,
        game._player_grid_point(player),
        magazine_ammo=1,
        reserve_units=0,
    )
    set_area_effect(
        game,
        MOLOTOV,
        player.position_id,
        known_team_indexes=[TEAM_TERRORISTS],
        source_player_id=player.id,
    )
    assert game._bot_coordinator.contacts_for_team(TEAM_COUNTER_TERRORISTS)
    assert game._bot_coordinator.squad_memories
    assert game.dropped_weapons
    assert game.area_effects

    game._finish_match(TEAM_TERRORISTS, MATCH_REGULATION)

    assert game.status == "finished"
    assert game.dropped_weapons == []
    assert game.next_dropped_weapon_id == 1
    assert game.area_effects == []
    assert game._bot_coordinator.team_plans == {}
    assert game._bot_coordinator.squad_memories == {}


def test_bot_round_roles_scale_from_two_to_five_players_per_side() -> None:
    expected_terrorist_roles = {
        2: [ROLE_OBJECTIVE, ROLE_ENTRY],
        3: [ROLE_OBJECTIVE, ROLE_ENTRY, ROLE_LURKER],
        4: [ROLE_OBJECTIVE, ROLE_ENTRY, ROLE_SUPPORT, ROLE_LURKER],
        5: [
            ROLE_OBJECTIVE,
            ROLE_ENTRY,
            ROLE_SUPPORT,
            ROLE_SUPPORT,
            ROLE_LURKER,
        ],
    }
    expected_counter_terrorist_roles = {
        2: [ROLE_ANCHOR, ROLE_ANCHOR],
        3: [ROLE_ANCHOR, ROLE_ANCHOR, ROLE_ROTATOR],
        4: [ROLE_ANCHOR, ROLE_ANCHOR, ROLE_ROTATOR, ROLE_ROTATOR],
        5: [
            ROLE_ANCHOR,
            ROLE_ANCHOR,
            ROLE_ROTATOR,
            ROLE_ANCHOR,
            ROLE_ANCHOR,
        ],
    }
    for team_size in range(2, 6):
        game = make_game(
            start=True,
            player_count=team_size * 2,
            bot_indexes=set(range(team_size * 2)),
        )
        terrorists = game._turn_order_players_on_team(TEAM_TERRORISTS)
        defenders = game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
        assert [
            game._bot_coordinator.assignment_for(player.id).role
            for player in terrorists
        ] == expected_terrorist_roles[team_size]
        assert [
            game._bot_coordinator.assignment_for(player.id).role for player in defenders
        ] == expected_counter_terrorist_roles[team_size]
        if team_size == 4:
            assert [
                game._bot_coordinator.assignment_for(player.id).anchor_node_id
                for player in defenders[2:]
            ] == ["b_doors", "ct_mid"]


def test_surplus_five_player_anchors_form_defender_side_crossfires() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    defenders = game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
    primary_a, primary_b, rotator, secondary_a, secondary_b = defenders

    assert bot_target_nodes(game, primary_a) == ("a_site",)
    assert bot_target_nodes(game, primary_b) == ("b_site",)
    assert bot_target_nodes(game, rotator) == ("b_doors",)
    assert bot_target_nodes(game, secondary_a) == ("ct_spawn",)
    assert bot_target_nodes(game, secondary_b) == ("b_doors",)

    secondary_a.position_id = game.tactical_map.counter_terrorist_spawn
    secondary_a.primary_weapon_id = M4.id
    secondary_a.equipped_weapon_id = M4.id
    start_activation(game, secondary_a)
    assert game.bot_think(secondary_a) == "hold_angle_a_site"


def test_surplus_anchor_collapses_to_the_site_after_primary_is_eliminated() -> None:
    game = make_game(
        start=True,
        player_count=10,
        bot_indexes=set(range(10)),
    )
    primary_a, _primary_b, _rotator, secondary_a, _secondary_b = (
        game._turn_order_players_on_team(TEAM_COUNTER_TERRORISTS)
    )
    assert bot_target_nodes(game, secondary_a) == ("ct_spawn",)

    primary_a.eliminated = True
    primary_a.health = 0
    game._bot_coordinator.observe(game)

    assert bot_target_nodes(game, secondary_a) == ("a_site",)


def test_postplant_bot_takes_a_route_opening_kill_then_rotates() -> None:
    game = make_game(start=True, bot_indexes={1})
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    terrorist.position_id = defender.position_id = "ct_mid"
    terrorist.health = 30
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == f"shoot_{terrorist.id}"
    game.execute_action(defender, f"shoot_{terrorist.id}")
    complete_weapon_fire(game)
    assert terrorist.eliminated
    assert game.bot_think(defender) == "move_b_doors"


def test_postplant_bot_keeps_rotation_tempo_after_opening_its_route() -> None:
    game = make_game(start=True, bot_indexes={1})
    close_terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    distant_terrorist = tactical_player(game, 2)
    close_terrorist.position_id = defender.position_id = "ct_mid"
    close_terrorist.health = 30
    distant_terrorist.position_id = "mid"
    distant_terrorist.health = 1
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    game.execute_action(defender, f"shoot_{close_terrorist.id}")
    complete_weapon_fire(game)

    assert close_terrorist.eliminated
    assert game._can_see(defender, distant_terrorist)
    assert game.bot_think(defender) == "move_b_doors"


def test_postplant_bot_does_not_mistake_one_of_two_kills_for_an_open_route() -> None:
    game = make_game(start=True, bot_indexes={1})
    first_terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    second_terrorist = tactical_player(game, 2)
    first_terrorist.position_id = defender.position_id = "ct_mid"
    second_terrorist.position_id = "ct_mid"
    first_terrorist.health = 1
    game.bomb_state = BOMB_PLANTED
    game.bomb_carrier_id = ""
    game.bomb_location_id = "b_site"
    game.bomb_fuse_remaining = game.rules.bomb_fuse_tactical_rounds
    start_activation(game, defender)

    assert game.bot_think(defender) == f"shoot_{first_terrorist.id}"
    game.execute_action(defender, f"shoot_{first_terrorist.id}")
    complete_weapon_fire(game)
    assert first_terrorist.eliminated
    assert game.bot_think(defender) == f"shoot_{second_terrorist.id}"


def test_surviving_ct_anchors_keep_their_sites_after_a_teammate_is_eliminated() -> None:
    game = make_game(
        start=True,
        player_count=6,
        bot_indexes=set(range(6)),
    )
    first_anchor, second_anchor, rotator = game._turn_order_players_on_team(
        TEAM_COUNTER_TERRORISTS
    )
    before = {
        player.id: game._bot_coordinator.assignment_for(player.id)
        for player in (second_anchor, rotator)
    }

    first_anchor.eliminated = True
    first_anchor.health = 0
    game._bot_coordinator.observe(game)

    assert (
        game._bot_coordinator.assignment_for(second_anchor.id)
        == before[second_anchor.id]
    )
    assert game._bot_coordinator.assignment_for(rotator.id) == before[rotator.id]


def test_terrorist_objective_role_follows_a_new_bomb_carrier() -> None:
    game = make_game(start=True, bot_indexes={0, 2})
    original_carrier, teammate = game._turn_order_players_on_team(TEAM_TERRORISTS)
    assert (
        game._bot_coordinator.assignment_for(original_carrier.id).role == ROLE_OBJECTIVE
    )

    game.bomb_state = BOMB_DROPPED
    game.bomb_carrier_id = ""
    game.bomb_location_id = original_carrier.position_id
    game._bot_coordinator.observe(game)
    game.bomb_state = BOMB_CARRIED
    game.bomb_carrier_id = teammate.id
    game.bomb_location_id = ""
    game._bot_coordinator.observe(game)

    assert game._bot_coordinator.assignment_for(teammate.id).role == ROLE_OBJECTIVE
    assert game._bot_coordinator.assignment_for(original_carrier.id).role == ROLE_ENTRY


def test_bot_angles_cover_spawn_exits_instead_of_the_spawn_itself() -> None:
    game = make_game(start=True, bot_indexes={0})
    terrorist = tactical_player(game, 0)
    defender = tactical_player(game, 1)
    game._place_player_in_node(terrorist, "mid")
    game._place_player_in_node(defender, game.tactical_map.counter_terrorist_spawn)
    terrorist.primary_weapon_id = AWP.id
    terrorist.equipped_weapon_id = AWP.id
    game._set_full_weapon_ammunition(terrorist, AWP)
    start_activation(game, terrorist)

    assert game._can_see(terrorist, defender)
    assert game._bot_coordinator._angle_action(
        game,
        terrorist,
        [defender],
    ) is None
    predicted = game._bot_coordinator._predictive_angle_nodes(
        game,
        terrorist,
        terrorist.position_id,
    )

    assert game.tactical_map.counter_terrorist_spawn not in predicted
    assert game.tactical_map.terrorist_spawn not in predicted
    assert predicted
    assert predicted[0] == "ct_mid"


def test_bot_squad_does_not_duplicate_existing_objective_equipment() -> None:
    game = make_game(
        start=True,
        bot_indexes={0, 1, 2, 3},
        finish_buy_phase=False,
    )
    game.execute_action(tactical_player(game, 0), "finish_buy")
    first_defender = tactical_player(game, 1)
    second_defender = tactical_player(game, 3)
    second_defender.equipment_counts = {DEFUSE_KIT.id: 1}

    assert game.bot_think(first_defender) == "buy_armor"


def test_movement_uses_spatial_audio_then_announces_arrival() -> None:
    game = make_game(start=True)
    player = tactical_player(game, 0)
    clear_spoken(game)

    game.execute_action(player, "move_mid")
    complete_movement(game)

    for table_player in game.players:
        user = game.get_user(table_player)
        if not isinstance(user, MockUser):
            continue
        assert user.get_spoken_messages()
        assert any(
            message.type == "play_sound" and message.data.get("segments")
            for message in user.messages
        )


def test_bots_can_complete_matches_at_every_supported_roster_size() -> None:
    for player_count in (4, 6, 8, 10):
        game = make_game(
            start=True,
            player_count=player_count,
            bot_indexes=set(range(player_count)),
            match_format="mr7",
            overtime_mode=OVERTIME_DRAW,
        )

        for _ in range(20_000):
            if game.status == "finished":
                break
            timed_sequences = [
                sequence
                for sequence in game.active_sequences
                if sequence.tag
                in {
                    MOVEMENT_AUDIO_SEQUENCE_TAG,
                    UTILITY_AUDIO_SEQUENCE_TAG,
                    WEAPON_AUDIO_SEQUENCE_TAG,
                }
            ]
            if timed_sequences:
                game.sound_scheduler_tick = max(
                    sequence.next_tick for sequence in timed_sequences
                )
                game.process_sequences()
            else:
                game.on_tick()
            game.flush_menus()

        assert game.status == "finished"
        assert game.winning_team_index in {
            TEAM_TERRORISTS,
            TEAM_COUNTER_TERRORISTS,
            -1,
        }
        assert game.win_reason in {MATCH_REGULATION, MATCH_DRAW}
