"""Citadels base-cast implementation for PlayAural."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .bot import bot_think as citadels_bot_think


PHASE_SELECTION = "selection_phase"
PHASE_RANK_RESOLUTION = "rank_resolution_phase"
PHASE_TURN = "turn_phase"
PHASE_ROUND_CLEANUP = "round_cleanup"

SUBPHASE_NORMAL = "normal"
SUBPHASE_ASSASSIN_TARGET = "assassin_target"
SUBPHASE_THIEF_TARGET = "thief_target"
SUBPHASE_DRAW_KEEP = "draw_keep"
SUBPHASE_MAGICIAN_SWAP = "magician_swap"
SUBPHASE_MAGICIAN_REDRAW = "magician_redraw"
SUBPHASE_LABORATORY = "laboratory_discard"
SUBPHASE_WARLORD_TARGET = "warlord_target"
SUBPHASE_THIEVES_DEN = "thieves_den_payment"

DISTRICT_NOBLE = "noble"
DISTRICT_RELIGIOUS = "religious"
DISTRICT_TRADE = "trade"
DISTRICT_MILITARY = "military"
DISTRICT_UNIQUE = "unique"
ALL_DISTRICT_TYPES = [
    DISTRICT_NOBLE,
    DISTRICT_RELIGIOUS,
    DISTRICT_TRADE,
    DISTRICT_MILITARY,
    DISTRICT_UNIQUE,
]

CHARACTER_ASSASSIN = 1
CHARACTER_THIEF = 2
CHARACTER_MAGICIAN = 3
CHARACTER_KING = 4
CHARACTER_BISHOP = 5
CHARACTER_MERCHANT = 6
CHARACTER_ARCHITECT = 7
CHARACTER_WARLORD = 8
CHARACTER_QUEEN = 9

WIN_DISTRICT_COUNT = 7
BOT_THINK_DELAY_MIN = 20
BOT_THINK_DELAY_MAX = 60

SOUND_MUSIC = "game_coup/music.ogg"
SOUND_CROWN = "game_citadels/take_crown.ogg"
SOUND_ASSASSINATE_DECLARE = "game_citadels/assassinate_declare.ogg"
SOUND_ASSASSINATED_SKIP = "game_citadels/assassinated_skip.ogg"
SOUND_CITY_COMPLETE = "game_citadels/city_complete.ogg"
SOUND_MAGIC_SWAP = "game_citadels/magic_swap.ogg"
SOUND_WIN = "game_citadels/wingame.ogg"
COIN_SOUNDS = {
    "small": "game_citadels/coins_small.ogg",
    "medium": "game_citadels/coins_medium.ogg",
    "large": "game_citadels/coins_large.ogg",
}
THIEF_LAUGH_SOUNDS = [
    "game_citadels/thief_laugh1.ogg",
    "game_citadels/thief_laugh2.ogg",
]
DEAL_SOUNDS = [
    "game_citadels/deal1.ogg",
    "game_citadels/deal2.ogg",
]
SHUFFLE_SOUNDS = [
    "game_citadels/shuffle1.ogg",
    "game_citadels/shuffle2.ogg",
]
BUILD_SOUNDS = [
    "game_citadels/build1.ogg",
    "game_citadels/build2.ogg",
]
COLLAPSE_SOUNDS = [
    "game_citadels/collapse1.ogg",
    "game_citadels/collapse2.ogg",
]
SOUND_WARLORD_FIRE = "game_citadels/warlord_fire.ogg"

SOUND_DELAYS = {
    SOUND_CROWN: 9,
    SOUND_ASSASSINATE_DECLARE: 8,
    SOUND_ASSASSINATED_SKIP: 8,
    SOUND_CITY_COMPLETE: 10,
    SOUND_MAGIC_SWAP: 8,
    SOUND_WARLORD_FIRE: 7,
    SOUND_WIN: 18,
    COIN_SOUNDS["small"]: 6,
    COIN_SOUNDS["medium"]: 7,
    COIN_SOUNDS["large"]: 8,
    DEAL_SOUNDS[0]: 6,
    DEAL_SOUNDS[1]: 6,
    SHUFFLE_SOUNDS[0]: 8,
    SHUFFLE_SOUNDS[1]: 8,
    BUILD_SOUNDS[0]: 7,
    BUILD_SOUNDS[1]: 7,
    COLLAPSE_SOUNDS[0]: 8,
    COLLAPSE_SOUNDS[1]: 8,
    THIEF_LAUGH_SOUNDS[0]: 8,
    THIEF_LAUGH_SOUNDS[1]: 8,
}

BASE_CHARACTER_RANKS = [
    CHARACTER_ASSASSIN,
    CHARACTER_THIEF,
    CHARACTER_MAGICIAN,
    CHARACTER_KING,
    CHARACTER_BISHOP,
    CHARACTER_MERCHANT,
    CHARACTER_ARCHITECT,
    CHARACTER_WARLORD,
]
QUEEN_CHARACTER_RANKS = BASE_CHARACTER_RANKS + [CHARACTER_QUEEN]

FACEUP_DISCARD_COUNTS_8 = {4: 2, 5: 1, 6: 0, 7: 0}
FACEUP_DISCARD_COUNTS_9 = {8: 0}

DISTRICT_DEFS = [
    ("temple", "Temple", 1, DISTRICT_RELIGIOUS, "", 3),
    ("church", "Church", 2, DISTRICT_RELIGIOUS, "", 3),
    ("monastery", "Monastery", 3, DISTRICT_RELIGIOUS, "", 3),
    ("cathedral", "Cathedral", 5, DISTRICT_RELIGIOUS, "", 2),
    ("manor", "Manor", 3, DISTRICT_NOBLE, "", 5),
    ("castle", "Castle", 4, DISTRICT_NOBLE, "", 4),
    ("palace", "Palace", 5, DISTRICT_NOBLE, "", 3),
    ("tavern", "Tavern", 1, DISTRICT_TRADE, "", 5),
    ("market", "Market", 2, DISTRICT_TRADE, "", 4),
    ("trading_post", "Trading Post", 2, DISTRICT_TRADE, "", 3),
    ("docks", "Docks", 3, DISTRICT_TRADE, "", 3),
    ("harbor", "Harbor", 4, DISTRICT_TRADE, "", 3),
    ("town_hall", "Town Hall", 5, DISTRICT_TRADE, "", 2),
    ("watchtower", "Watchtower", 1, DISTRICT_MILITARY, "", 3),
    ("prison", "Prison", 2, DISTRICT_MILITARY, "", 3),
    ("barracks", "Barracks", 3, DISTRICT_MILITARY, "", 3),
    ("fortress", "Fortress", 5, DISTRICT_MILITARY, "", 2),
    ("dragon_gate", "Dragon Gate", 6, DISTRICT_UNIQUE, "dragon_gate", 1),
    ("factory", "Factory", 5, DISTRICT_UNIQUE, "factory", 1),
    ("haunted_quarter", "Haunted Quarter", 2, DISTRICT_UNIQUE, "haunted_quarter", 1),
    ("imperial_treasury", "Imperial Treasury", 5, DISTRICT_UNIQUE, "imperial_treasury", 1),
    ("keep", "Keep", 3, DISTRICT_UNIQUE, "keep", 1),
    ("laboratory", "Laboratory", 5, DISTRICT_UNIQUE, "laboratory", 1),
    ("library", "Library", 6, DISTRICT_UNIQUE, "library", 1),
    ("map_room", "Map Room", 5, DISTRICT_UNIQUE, "map_room", 1),
    ("quarry", "Quarry", 5, DISTRICT_UNIQUE, "quarry", 1),
    ("school_of_magic", "School of Magic", 6, DISTRICT_UNIQUE, "school_of_magic", 1),
    ("smithy", "Smithy", 5, DISTRICT_UNIQUE, "smithy", 1),
    ("statue", "Statue", 3, DISTRICT_UNIQUE, "statue", 1),
    ("thieves_den", "Thieves' Den", 6, DISTRICT_UNIQUE, "thieves_den", 1),
    ("wishing_well", "Wishing Well", 5, DISTRICT_UNIQUE, "wishing_well", 1),
]


@dataclass
class DistrictCard(DataClassJSONMixin):
    id: int
    slug: str
    name: str
    cost: int
    district_type: str
    effect_key: str = ""

    @property
    def is_unique(self) -> bool:
        return self.district_type == DISTRICT_UNIQUE


@dataclass
class CitadelsPlayer(Player):
    hand: list[DistrictCard] = field(default_factory=list)
    city: list[DistrictCard] = field(default_factory=list)
    gold: int = 0
    selected_character_rank: int | None = None
    revealed_character_rank: int | None = None


@register_game
@dataclass
class CitadelsGame(Game):
    players: list[CitadelsPlayer] = field(default_factory=list)

    phase: str = PHASE_SELECTION
    turn_subphase: str = SUBPHASE_NORMAL
    district_deck: list[DistrictCard] = field(default_factory=list)
    faceup_discarded_ranks: list[int] = field(default_factory=list)
    facedown_discarded_ranks: list[int] = field(default_factory=list)
    available_character_ranks: list[int] = field(default_factory=list)
    selection_order_player_ids: list[str] = field(default_factory=list)
    selection_index: int = 0
    current_rank: int | None = None
    crown_holder_id: str | None = None
    killed_rank: int | None = None
    robbed_rank: int | None = None
    robber_player_id: str | None = None
    first_completed_city_player_id: str | None = None
    city_completion_order: list[str] = field(default_factory=list)
    pending_draw_choices: list[DistrictCard] = field(default_factory=list)
    selected_card_ids: list[int] = field(default_factory=list)
    pending_build_card_id: int | None = None
    turn_resource_taken: bool = False
    turn_income_used: bool = False
    turn_character_ability_used: bool = False
    turn_build_limit: int = 1
    turn_builds_made: int = 0
    turn_laboratory_used: bool = False
    turn_smithy_used: bool = False
    initial_facedown_rank: int | None = None
    pending_queen_bonus_player_id: str | None = None
    sequence_counter: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()

    @classmethod
    def get_name(cls) -> str:
        return "Citadels"

    @classmethod
    def get_type(cls) -> str:
        return "citadels"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 4

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> CitadelsPlayer:
        return CitadelsPlayer(id=player_id, name=name, is_bot=is_bot)

    def create_turn_action_set(self, player: CitadelsPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="take_gold",
                label=Localization.get(locale, "citadels-take-gold"),
                handler="_action_take_gold",
                is_enabled="_is_take_gold_enabled",
                is_hidden="_is_take_gold_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="draw_cards",
                label=Localization.get(locale, "citadels-draw-cards"),
                handler="_action_draw_cards",
                is_enabled="_is_draw_cards_enabled",
                is_hidden="_is_draw_cards_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="collect_income",
                label=Localization.get(locale, "citadels-collect-income"),
                handler="_action_collect_income",
                is_enabled="_is_collect_income_enabled",
                is_hidden="_is_collect_income_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="magician_swap_mode",
                label=Localization.get(locale, "citadels-magician-swap"),
                handler="_action_enter_magician_swap",
                is_enabled="_is_magician_swap_mode_enabled",
                is_hidden="_is_magician_swap_mode_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="magician_redraw",
                label=Localization.get(locale, "citadels-magician-redraw"),
                handler="_action_enter_magician_redraw",
                is_enabled="_is_magician_redraw_enabled",
                is_hidden="_is_magician_redraw_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="use_laboratory",
                label=Localization.get(locale, "citadels-use-laboratory"),
                handler="_action_enter_laboratory",
                is_enabled="_is_use_laboratory_enabled",
                is_hidden="_is_use_laboratory_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="use_smithy",
                label=Localization.get(locale, "citadels-use-smithy"),
                handler="_action_use_smithy",
                is_enabled="_is_use_smithy_enabled",
                is_hidden="_is_use_smithy_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="warlord_destroy_mode",
                label=Localization.get(locale, "citadels-warlord-destroy"),
                handler="_action_enter_warlord_destroy",
                is_enabled="_is_warlord_destroy_mode_enabled",
                is_hidden="_is_warlord_destroy_mode_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="confirm_magician_redraw",
                label=Localization.get(locale, "citadels-confirm-redraw"),
                handler="_action_confirm_magician_redraw",
                is_enabled="_is_confirm_magician_redraw_enabled",
                is_hidden="_is_confirm_magician_redraw_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="cancel_magician_redraw",
                label=Localization.get(locale, "cancel"),
                handler="_action_cancel_subphase",
                is_enabled="_is_cancel_subphase_enabled",
                is_hidden="_is_cancel_magician_redraw_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="confirm_thieves_den_payment",
                label=Localization.get(locale, "citadels-build-thieves-den"),
                handler="_action_confirm_thieves_den",
                is_enabled="_is_confirm_thieves_den_payment_enabled",
                is_hidden="_is_confirm_thieves_den_payment_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="cancel_thieves_den_payment",
                label=Localization.get(locale, "cancel"),
                handler="_action_cancel_subphase",
                is_enabled="_is_cancel_subphase_enabled",
                is_hidden="_is_cancel_thieves_den_payment_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="cancel_subphase",
                label=Localization.get(locale, "cancel"),
                handler="_action_cancel_subphase",
                is_enabled="_is_cancel_subphase_enabled",
                is_hidden="_is_cancel_subphase_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="end_turn",
                label=Localization.get(locale, "citadels-end-turn"),
                handler="_action_end_turn",
                is_enabled="_is_end_turn_enabled",
                is_hidden="_is_end_turn_hidden",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="read_status",
                label=Localization.get(locale, "citadels-read-status"),
                handler="_action_read_status",
                is_enabled="_is_read_status_enabled",
                is_hidden="_is_read_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_status_detailed",
                label=Localization.get(locale, "citadels-read-status-detailed"),
                handler="_action_read_status_detailed",
                is_enabled="_is_read_status_detailed_enabled",
                is_hidden="_is_read_status_detailed_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_character",
                label=Localization.get(locale, "citadels-read-character"),
                handler="_action_read_character",
                is_enabled="_is_read_character_enabled",
                is_hidden="_is_read_character_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "citadels-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_cities",
                label=Localization.get(locale, "citadels-read-cities"),
                handler="_action_read_cities",
                is_enabled="_is_read_cities_enabled",
                is_hidden="_is_read_cities_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_discards",
                label=Localization.get(locale, "citadels-read-discards"),
                handler="_action_read_discards",
                is_enabled="_is_read_discards_enabled",
                is_hidden="_is_read_discards_hidden",
                include_spectators=True,
            )
        )
        self._apply_standard_action_order(action_set, user)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Draw cards", ["draw_cards"], state=KeybindState.ACTIVE)
        self.define_keybind("g", "Take gold", ["take_gold"], state=KeybindState.ACTIVE)
        self.define_keybind("h", "Read hand", ["read_hand"], state=KeybindState.ACTIVE)
        self.define_keybind("v", "Read cities", ["read_cities"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("i", "Read status", ["read_status"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+i", "Read detailed status", ["read_status_detailed"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("k", "Read character", ["read_character"], state=KeybindState.ACTIVE)
        self.define_keybind("f", "Read discards", ["read_discards"], state=KeybindState.ACTIVE, include_spectators=True)

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_player_action_sets(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_player_action_sets(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_player_action_sets(player)
        super().rebuild_all_menus()

    def find_action(self, player: Player, action_id: str) -> Action | None:
        self._sync_player_action_sets(player)
        return super().find_action(player, action_id)

    def _sync_player_action_sets(self, player: Player) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)

    def _sync_standard_actions(self, player: Player) -> None:
        standard_set = self.get_action_set(player, "standard")
        if not standard_set:
            return
        self._apply_standard_action_order(standard_set, self.get_user(player))

    def _apply_standard_action_order(self, action_set: ActionSet, user) -> None:
        custom_ids = [
            "read_status",
            "read_status_detailed",
            "read_character",
            "read_hand",
            "read_cities",
            "read_discards",
        ]
        action_set._order = [aid for aid in action_set._order if aid not in custom_ids] + [
            aid for aid in custom_ids if action_set.get_action(aid)
        ]
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_status",
                    "read_status_detailed",
                    "read_character",
                    "read_hand",
                    "read_cities",
                    "read_discards",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )

    def _sync_turn_actions(self, player: Player) -> None:
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        for prefix in (
            "select_character_",
            "assassinate_target_",
            "thief_target_",
            "keep_draw_",
            "build_",
            "magician_swap_target_",
            "laboratory_discard_",
            "warlord_destroy_target_",
            "magician_redraw_toggle_",
            "thieves_den_toggle_",
        ):
            turn_set.remove_by_prefix(prefix)

        if self.status != "playing" or player.is_spectator or self.is_sequence_gameplay_locked():
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"
        dynamic_ids: list[str] = []

        if self.phase == PHASE_SELECTION and self.current_player == player:
            for rank in self._selection_options_for_player(player):
                action_id = f"select_character_{rank}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-select-character-line",
                            rank=rank,
                            character=self._character_name(rank, locale),
                        ),
                        handler="_action_select_character",
                        is_enabled="_is_select_character_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids
            return

        if self.phase != PHASE_TURN or self.current_player != player:
            return

        if self.turn_subphase == SUBPHASE_ASSASSIN_TARGET:
            for rank in self._assassin_target_ranks():
                action_id = f"assassinate_target_{rank}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-assassinate-target-line",
                            rank=rank,
                            character=self._character_name(rank, locale),
                        ),
                        handler="_action_choose_assassin_target",
                        is_enabled="_is_choose_assassin_target_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids
            return

        if self.turn_subphase == SUBPHASE_THIEF_TARGET:
            for rank in self._thief_target_ranks():
                action_id = f"thief_target_{rank}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-thief-target-line",
                            rank=rank,
                            character=self._character_name(rank, locale),
                        ),
                        handler="_action_choose_thief_target",
                        is_enabled="_is_choose_thief_target_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids
            return

        if self.turn_subphase == SUBPHASE_DRAW_KEEP:
            for card in self.pending_draw_choices:
                action_id = f"keep_draw_{card.id}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=self._district_line(card, locale),
                        handler="_action_keep_draw_card",
                        is_enabled="_is_keep_draw_card_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids
            return

        if self.turn_subphase == SUBPHASE_MAGICIAN_SWAP:
            for other in self._swap_targets():
                action_id = f"magician_swap_target_{other.id}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-magician-swap-line",
                            player=other.name,
                            cards=len(other.hand),
                        ),
                        handler="_action_magician_swap",
                        is_enabled="_is_magician_swap_target_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids + ["cancel_subphase"]
            return

        if self.turn_subphase == SUBPHASE_LABORATORY:
            cit_player = self._as_citadels_player(player)
            if cit_player:
                for card in cit_player.hand:
                    action_id = f"laboratory_discard_{card.id}"
                    turn_set.add(
                        Action(
                            id=action_id,
                            label=self._district_line(card, locale),
                            handler="_action_laboratory_discard",
                            is_enabled="_is_laboratory_discard_enabled",
                            is_hidden="_is_dynamic_turn_action_hidden",
                            show_in_actions_menu=False,
                        )
                    )
                    dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids + ["cancel_subphase"]
            return

        if self.turn_subphase == SUBPHASE_WARLORD_TARGET:
            for owner, district in self._warlord_targets():
                action_id = f"warlord_destroy_target_{owner.id}_{district.id}"
                turn_set.add(
                    Action(
                        id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-warlord-target-line",
                            player=owner.name,
                            district=self._district_name(district, locale),
                            cost=max(0, self._warlord_destroy_cost(owner, district)),
                            description=self._district_effect_description(district, locale),
                        ),
                        handler="_action_warlord_destroy",
                        is_enabled="_is_warlord_destroy_target_enabled",
                        is_hidden="_is_dynamic_turn_action_hidden",
                        show_in_actions_menu=False,
                    )
                )
                dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids + ["cancel_subphase"]
            return

        if self.turn_subphase == SUBPHASE_MAGICIAN_REDRAW:
            cit_player = self._as_citadels_player(player)
            if cit_player:
                for card in cit_player.hand:
                    selected = card.id in self.selected_card_ids
                    action_id = f"magician_redraw_toggle_{card.id}"
                    turn_set.add(
                        Action(
                            id=action_id,
                            label=self._toggle_line(locale, card, selected),
                            handler="_action_toggle_magician_redraw",
                            is_enabled="_is_toggle_magician_redraw_enabled",
                            is_hidden="_is_dynamic_turn_action_hidden",
                            show_in_actions_menu=False,
                        )
                    )
                    dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids + ["confirm_magician_redraw", "cancel_magician_redraw"]
            return

        if self.turn_subphase == SUBPHASE_THIEVES_DEN:
            cit_player = self._as_citadels_player(player)
            if cit_player:
                pending = self._find_hand_card(cit_player, self.pending_build_card_id)
                if pending:
                    for card in cit_player.hand:
                        if card.id == pending.id:
                            continue
                        selected = card.id in self.selected_card_ids
                        action_id = f"thieves_den_toggle_{card.id}"
                        turn_set.add(
                            Action(
                                id=action_id,
                                label=self._toggle_line(locale, card, selected),
                                handler="_action_toggle_thieves_den_payment",
                                is_enabled="_is_toggle_thieves_den_payment_enabled",
                                is_hidden="_is_dynamic_turn_action_hidden",
                                show_in_actions_menu=False,
                            )
                        )
                        dynamic_ids.append(action_id)
            turn_set._order = dynamic_ids + [
                "confirm_thieves_den_payment",
                "cancel_thieves_den_payment",
            ]
            return

        cit_player = self._as_citadels_player(player)
        build_ids: list[str] = []
        if cit_player and self.turn_resource_taken and self._may_build_more():
            for card in cit_player.hand:
                if self._can_attempt_build(cit_player, card):
                    action_id = f"build_{card.id}"
                    turn_set.add(
                        Action(
                            id=action_id,
                        label=Localization.get(
                            locale,
                            "citadels-build-card-line",
                            district=self._district_name(card, locale),
                            cost=self._effective_build_cost(cit_player, card),
                            description=self._district_effect_description(card, locale),
                        ),
                            handler="_action_build_card",
                            is_enabled="_is_build_card_enabled",
                            is_hidden="_is_dynamic_turn_action_hidden",
                            show_in_actions_menu=False,
                        )
                    )
                    build_ids.append(action_id)

        turn_set._order = build_ids + [
            "take_gold",
            "draw_cards",
            "collect_income",
            "magician_swap_mode",
            "magician_redraw",
            "use_laboratory",
            "use_smithy",
            "warlord_destroy_mode",
            "end_turn",
        ]

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1
        self.phase = PHASE_SELECTION
        self.turn_subphase = SUBPHASE_NORMAL
        self.faceup_discarded_ranks.clear()
        self.facedown_discarded_ranks.clear()
        self.available_character_ranks.clear()
        self.city_completion_order.clear()
        self.first_completed_city_player_id = None
        self.pending_draw_choices.clear()
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self.pending_queen_bonus_player_id = None
        self.turn_player_ids = []
        self.turn_index = 0

        active_players = self.get_active_players()
        self.crown_holder_id = active_players[0].id if active_players else None
        self.district_deck = self._build_district_deck()
        random.shuffle(self.district_deck)
        for player in active_players:
            player.hand.clear()
            player.city.clear()
            player.gold = 2
            player.selected_character_rank = None
            player.revealed_character_rank = None
            self._draw_to_hand(player, 4)

        self.play_music(SOUND_MUSIC)
        self.broadcast_l("citadels-game-start", buffer="game")
        self._start_selection_phase()

    def prestart_validate(self) -> list[str] | list[tuple[str, dict]]:
        errors = super().prestart_validate()
        active_count = len(self.get_active_players())
        if active_count < self.get_min_players():
            errors.append("action-need-more-players")
        if active_count > self.get_max_players():
            errors.append("action-table-full")
        return errors

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.is_sequence_bot_paused():
            return
        if self.status == "playing" and self.current_player and self.current_player.is_bot:
            BotHelper.on_tick(self)

    def _replace_with_bot(self, player: Player) -> None:
        was_current = self.current_player == player
        was_selection_picker = self.phase == PHASE_SELECTION and self._selection_player() == player
        super()._replace_with_bot(player)
        if self.status != "playing" or not player.is_bot:
            return
        player.bot_pending_action = None
        if was_selection_picker:
            self.set_turn_players([player])
        if was_current or was_selection_picker or self.current_player == player:
            self.rebuild_all_menus()
            self._schedule_bot_turn(player)

    def _start_selection_phase(self) -> None:
        self.phase = PHASE_SELECTION
        self.turn_subphase = SUBPHASE_NORMAL
        self.turn_player_ids = []
        self.turn_index = 0
        self.current_rank = None
        self.killed_rank = None
        self.robbed_rank = None
        self.robber_player_id = None
        self.pending_draw_choices.clear()
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self.pending_queen_bonus_player_id = None
        self.turn_resource_taken = False
        self.turn_income_used = False
        self.turn_character_ability_used = False
        self.turn_build_limit = 1
        self.turn_builds_made = 0
        self.turn_laboratory_used = False
        self.turn_smithy_used = False
        self.faceup_discarded_ranks.clear()
        self.facedown_discarded_ranks.clear()
        self.available_character_ranks = self._character_ranks_in_play()
        self.initial_facedown_rank = None

        for player in self.get_active_players():
            player.selected_character_rank = None
            player.revealed_character_rank = None

        character_pool = list(self.available_character_ranks)
        random.shuffle(character_pool)
        faceup_count = self._faceup_discard_count()
        while faceup_count > 0:
            rank = character_pool.pop()
            if rank == CHARACTER_KING:
                character_pool.insert(0, rank)
                random.shuffle(character_pool)
                continue
            self.faceup_discarded_ranks.append(rank)
            faceup_count -= 1
        if character_pool:
            self.initial_facedown_rank = character_pool.pop()
            self.facedown_discarded_ranks = [self.initial_facedown_rank]
        self.available_character_ranks = character_pool

        self.selection_order_player_ids = [p.id for p in self._players_from_crown()]
        self.selection_index = 0
        first = self._selection_player()
        if first:
            self.set_turn_players([first])
            self._announce_selection_turn(first, round_number=self.round)
            return
        self.rebuild_all_menus()

    def _finish_selection_phase(self) -> None:
        if self.available_character_ranks:
            self.facedown_discarded_ranks.extend(self.available_character_ranks)
            self.available_character_ranks.clear()
        self.phase = PHASE_RANK_RESOLUTION
        self.turn_player_ids = []
        self.turn_index = 0
        self.current_rank = CHARACTER_ASSASSIN
        self.broadcast_l("citadels-turn-phase-start", buffer="game")
        self.rebuild_all_menus()
        self._advance_rank_resolution()

    def _advance_rank_resolution(self) -> None:
        self.phase = PHASE_RANK_RESOLUTION
        self.turn_subphase = SUBPHASE_NORMAL
        self.turn_player_ids = []
        self.turn_index = 0
        while self.current_rank is not None:
            if self.current_rank > max(self._character_ranks_in_play()):
                self._start_round_cleanup()
                return
            rank = self.current_rank
            owner = self._player_with_rank(rank)
            if owner is None:
                self._broadcast_localized(
                    "citadels-rank-unclaimed",
                    buffer="game",
                    rank=rank,
                    character=lambda locale: self._character_name(rank, locale),
                )
                self.current_rank += 1
                continue
            if rank == self.killed_rank:
                self.start_sequence(
                    self._next_sequence_id("citadels_skip"),
                    [
                        SequenceBeat(
                            ops=[SequenceOperation.sound_op(SOUND_ASSASSINATED_SKIP)],
                            delay_after_ticks=self._paced_delay_ticks(SOUND_ASSASSINATED_SKIP),
                        ),
                        SequenceBeat(
                            ops=[
                                SequenceOperation.callback_op(
                                    "skip_rank",
                                    {"rank": rank, "owner_id": owner.id},
                                )
                            ]
                        ),
                    ],
                    tag="citadels_rank_skip",
                    lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                    pause_bots=True,
                )
                return

            owner.revealed_character_rank = rank
            self.set_turn_players([owner])
            self._broadcast_localized(
                "citadels-character-revealed",
                buffer="game",
                player=owner.name,
                rank=rank,
                character=lambda locale: self._character_name(rank, locale),
            )
            if rank == self.robbed_rank and self.robber_player_id:
                self._start_resolution_sequence(
                    "citadels_robbery",
                    self._build_robbery_beats(owner),
                    tag="citadels_robbery",
                )
                return
            self._begin_turn(owner, rank)
            return

    def _begin_turn(self, player: CitadelsPlayer, rank: int) -> None:
        self.phase = PHASE_TURN
        if rank == CHARACTER_ASSASSIN and self.killed_rank is None:
            self.turn_subphase = SUBPHASE_ASSASSIN_TARGET
        elif rank == CHARACTER_THIEF and self.robbed_rank is None:
            self.turn_subphase = SUBPHASE_THIEF_TARGET
        else:
            self.turn_subphase = SUBPHASE_NORMAL
        self.pending_draw_choices.clear()
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self.turn_resource_taken = False
        self.turn_income_used = False
        self.turn_character_ability_used = False
        self.turn_build_limit = 3 if rank == CHARACTER_ARCHITECT else 1
        self.turn_builds_made = 0
        self.turn_laboratory_used = False
        self.turn_smithy_used = False

        if rank == CHARACTER_KING:
            self._start_resolution_sequence(
                "citadels_take_crown",
                [
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(SOUND_CROWN)],
                        delay_after_ticks=self._paced_delay_ticks(SOUND_CROWN),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "take_crown",
                                {"player_id": player.id},
                            )
                        ]
                    ),
                ],
                tag="citadels_turn_open",
            )
            return

        if rank == CHARACTER_ARCHITECT:
            draw_sound = random.choice(SHUFFLE_SOUNDS)
            self._start_resolution_sequence(
                "citadels_architect_draw",
                [
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(draw_sound)],
                        delay_after_ticks=self._paced_delay_ticks(draw_sound),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "architect_bonus",
                                {"player_id": player.id},
                            )
                        ]
                    ),
                ],
                tag="citadels_turn_open",
            )
            return

        if rank == CHARACTER_QUEEN:
            self._apply_queen_bonus(player)

        self._announce_turn_ready(player, rank)

    def _finish_turn(self) -> None:
        self.phase = PHASE_RANK_RESOLUTION
        self.turn_subphase = SUBPHASE_NORMAL
        self.pending_draw_choices.clear()
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self.turn_player_ids = []
        self.turn_index = 0
        if self.current_rank is None:
            self._start_round_cleanup()
            return
        self.current_rank += 1
        self.rebuild_all_menus()
        self._advance_rank_resolution()

    def _start_round_cleanup(self) -> None:
        self.phase = PHASE_ROUND_CLEANUP
        self.turn_subphase = SUBPHASE_NORMAL
        self.turn_player_ids = []
        self.turn_index = 0

        king_owner = self._player_with_rank(CHARACTER_KING)
        if self.killed_rank == CHARACTER_KING and king_owner is not None:
            self._start_resolution_sequence(
                "citadels_round_cleanup",
                [
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(SOUND_CROWN)],
                        delay_after_ticks=self._paced_delay_ticks(SOUND_CROWN),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "round_cleanup_king_heir",
                                {"player_id": king_owner.id},
                            )
                        ]
                    ),
                ],
                tag="citadels_round_cleanup",
            )
            return

        self._complete_round_cleanup()

    def _complete_round_cleanup(self) -> None:
        if self._any_completed_city():
            winner = self._winner_player()
            winner_id = winner.id if winner is not None else ""
            self._start_resolution_sequence(
                "citadels_game_end",
                [
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(SOUND_WIN),
                            SequenceOperation.callback_op(
                                "announce_winner",
                                {"winner_id": winner_id},
                            ),
                        ],
                        delay_after_ticks=self._paced_delay_ticks(SOUND_WIN),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op("finish_game")
                        ],
                    ),
                ],
                tag="citadels_game_end",
            )
            return

        self.round += 1
        self._start_selection_phase()

    def _paced_delay_ticks(self, sound_path: str) -> int:
        return SOUND_DELAYS.get(sound_path, 6)

    def _next_sequence_id(self, prefix: str) -> str:
        self.sequence_counter += 1
        return f"{prefix}_{self.sequence_counter}"

    def _refresh_menus_for_focus(
        self,
        player: Player,
        *,
        selection_id: str | None = None,
    ) -> None:
        self.rebuild_all_menus()
        target_id = selection_id
        if target_id is not None and self.find_action(player, target_id) is None:
            target_id = None
        if target_id is None:
            target_id = self._preferred_focus_action_id(player)
        if target_id is not None:
            self.update_player_menu(player, selection_id=target_id)

    def _first_visible_action_id(self, player: Player) -> str | None:
        visible_actions = self.get_all_visible_actions(player)
        if not visible_actions:
            return None
        return visible_actions[0].action.id

    def _preferred_focus_action_id(self, player: Player) -> str | None:
        if self.phase == PHASE_SELECTION and self.current_player == player:
            options = self._selection_options_for_player(player)
            if options:
                return f"select_character_{options[0]}"
            return None

        if self.phase != PHASE_TURN or self.current_player != player:
            return None

        if self.turn_subphase == SUBPHASE_ASSASSIN_TARGET:
            targets = self._assassin_target_ranks()
            return f"assassinate_target_{targets[0]}" if targets else None
        if self.turn_subphase == SUBPHASE_THIEF_TARGET:
            targets = self._thief_target_ranks()
            return f"thief_target_{targets[0]}" if targets else None
        if self.turn_subphase == SUBPHASE_DRAW_KEEP:
            return f"keep_draw_{self.pending_draw_choices[0].id}" if self.pending_draw_choices else None
        if self.turn_subphase == SUBPHASE_MAGICIAN_SWAP:
            targets = self._swap_targets()
            return f"magician_swap_target_{targets[0].id}" if targets else None
        if self.turn_subphase == SUBPHASE_LABORATORY:
            cit_player = self._as_citadels_player(player)
            if cit_player and cit_player.hand:
                return f"laboratory_discard_{cit_player.hand[0].id}"
            return None
        if self.turn_subphase == SUBPHASE_WARLORD_TARGET:
            targets = self._warlord_targets()
            if targets:
                owner, district = targets[0]
                return f"warlord_destroy_target_{owner.id}_{district.id}"
            return None
        if self.turn_subphase == SUBPHASE_MAGICIAN_REDRAW:
            cit_player = self._as_citadels_player(player)
            if cit_player and cit_player.hand:
                return f"magician_redraw_toggle_{cit_player.hand[0].id}"
            return None
        if self.turn_subphase == SUBPHASE_THIEVES_DEN:
            cit_player = self._as_citadels_player(player)
            if not cit_player:
                return None
            pending = self._find_hand_card(cit_player, self.pending_build_card_id)
            if pending is None:
                return None
            for card in cit_player.hand:
                if card.id != pending.id:
                    return f"thieves_den_toggle_{card.id}"
        return self._first_visible_action_id(player)

    def _announce_selection_turn(
        self, player: CitadelsPlayer, *, round_number: int | None = None
    ) -> None:
        if round_number is not None:
            self.broadcast_l(
                "citadels-selection-start",
                buffer="game",
                round=round_number,
                player=player.name,
            )
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("turn.ogg")
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )
        if user:
            user.speak_l("citadels-selection-prompt", buffer="game")
        self._schedule_bot_turn(player)

    def _district_name(self, card: DistrictCard, locale: str) -> str:
        return Localization.get(locale, f"citadels-district-{card.slug}")

    def _district_effect_description(self, card: DistrictCard, locale: str) -> str:
        effect_key = card.effect_key or "none"
        return Localization.get(locale, f"citadels-district-effect-{effect_key}")

    def _speak_lines(self, player: Player, lines: list[str], *, buffer: str = "game") -> None:
        user = self.get_user(player)
        if not user:
            return
        for line in lines:
            user.speak(line, buffer=buffer)

    def _broadcast_localized(
        self,
        message_id: str,
        *,
        buffer: str,
        **kwargs,
    ) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            localized_kwargs = {
                key: value(user.locale) if callable(value) else value
                for key, value in kwargs.items()
            }
            user.speak_l(message_id, buffer=buffer, **localized_kwargs)

    def _schedule_bot_turn(self, player: Player) -> None:
        BotHelper.jolt_bot(
            player,
            ticks=random.randint(BOT_THINK_DELAY_MIN, BOT_THINK_DELAY_MAX),
        )

    def _announce_turn_ready(self, player: CitadelsPlayer, rank: int) -> None:
        _ = rank
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("turn.ogg")
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )
        self._schedule_bot_turn(player)

    def _start_resolution_sequence(
        self,
        prefix: str,
        beats: list[SequenceBeat],
        *,
        tag: str,
    ) -> None:
        self.start_sequence(
            self._next_sequence_id(prefix),
            beats,
            tag=tag,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _build_coin_beats(self, amount: int, *, allow_laugh: bool = False) -> list[SequenceBeat]:
        if amount <= 0:
            return []
        sound = self._coin_sound(amount)
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(sound)],
                delay_after_ticks=self._paced_delay_ticks(sound),
            )
        ]
        if allow_laugh and amount >= 5:
            laugh = random.choice(THIEF_LAUGH_SOUNDS)
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(laugh)],
                    delay_after_ticks=self._paced_delay_ticks(laugh),
                )
            )
        return beats

    def _build_magician_swap_beats(
        self, player_id: str, target_id: str
    ) -> list[SequenceBeat]:
        deal = random.choice(DEAL_SOUNDS)
        return [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(SOUND_MAGIC_SWAP)],
                delay_after_ticks=self._paced_delay_ticks(SOUND_MAGIC_SWAP),
            ),
            SequenceBeat(
                ops=[SequenceOperation.sound_op(deal)],
                delay_after_ticks=self._paced_delay_ticks(deal),
            ),
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "magician_swap",
                        {"player_id": player_id, "target_id": target_id},
                    )
                ]
            ),
        ]

    def _build_warlord_destroy_beats(
        self,
        owner_id: str,
        district_id: int,
    ) -> list[SequenceBeat]:
        collapse = random.choice(COLLAPSE_SOUNDS)
        return [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(SOUND_WARLORD_FIRE)],
                delay_after_ticks=self._paced_delay_ticks(SOUND_WARLORD_FIRE),
            ),
            SequenceBeat.pause(3),
            SequenceBeat(
                ops=[SequenceOperation.sound_op(collapse)],
                delay_after_ticks=self._paced_delay_ticks(collapse),
            ),
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "warlord_destroy",
                        {"owner_id": owner_id, "district_id": district_id},
                    )
                ]
            ),
        ]

    def _build_robbery_beats(self, target: CitadelsPlayer) -> list[SequenceBeat]:
        amount = max(0, target.gold)
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "apply_robbery",
                        {"target_id": target.id, "amount": amount},
                    )
                ]
            )
        ]
        beats.extend(self._build_coin_beats(amount, allow_laugh=True))
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "resume_turn_after_robbery",
                        {"target_id": target.id},
                    )
                ]
            )
        )
        return beats

    def _action_select_character(self, player: Player, action_id: str) -> None:
        cit_player = self._as_citadels_player(player)
        if not cit_player:
            return
        rank = self._parse_rank_action(action_id, "select_character_")
        if rank is None or rank not in self._selection_options_for_player(cit_player):
            return
        cit_player.selected_character_rank = rank
        if rank in self.available_character_ranks:
            self.available_character_ranks.remove(rank)
        elif self.initial_facedown_rank == rank:
            self.initial_facedown_rank = None
            self.facedown_discarded_ranks.clear()

        self.broadcast_l("citadels-character-chosen", buffer="game", player=cit_player.name)
        if self.selection_index >= len(self.selection_order_player_ids) - 1:
            self._finish_selection_phase()
            return
        self.selection_index += 1
        next_player = self._selection_player()
        if next_player:
            self.set_turn_players([next_player])
            self._announce_selection_turn(next_player)

    def _action_choose_assassin_target(self, player: Player, action_id: str) -> None:
        rank = self._parse_rank_action(action_id, "assassinate_target_")
        if rank is None:
            return
        self.killed_rank = rank
        self.turn_subphase = SUBPHASE_NORMAL
        self._start_resolution_sequence(
            "citadels_assassinate",
            [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_ASSASSINATE_DECLARE)],
                    delay_after_ticks=self._paced_delay_ticks(SOUND_ASSASSINATE_DECLARE),
                )
            ],
            tag="citadels_turn_action",
        )
        self._broadcast_localized(
            "citadels-assassin-targeted",
            buffer="game",
            rank=rank,
            character=lambda locale: self._character_name(rank, locale),
        )
        self._refresh_menus_for_focus(player)

    def _action_choose_thief_target(self, player: Player, action_id: str) -> None:
        rank = self._parse_rank_action(action_id, "thief_target_")
        if rank is None:
            return
        self.robbed_rank = rank
        self.robber_player_id = player.id
        self.turn_subphase = SUBPHASE_NORMAL
        user = self.get_user(player)
        if user:
            user.speak_l(
                "citadels-thief-targeted",
                buffer="game",
                rank=rank,
                character=self._character_name(rank, user.locale),
            )
        self._refresh_menus_for_focus(player)

    def _action_take_gold(self, player: Player, action_id: str) -> None:
        _ = action_id
        beats = [SequenceBeat(ops=[SequenceOperation.callback_op("apply_resource_gold", {"player_id": player.id})])]
        beats.extend(self._build_coin_beats(2))
        self._start_resolution_sequence("citadels_take_gold", beats, tag="citadels_turn_action")

    def _action_draw_cards(self, player: Player, action_id: str) -> None:
        _ = action_id
        shuffle = random.choice(SHUFFLE_SOUNDS)
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(shuffle)],
                delay_after_ticks=self._paced_delay_ticks(shuffle),
            ),
            SequenceBeat(ops=[SequenceOperation.callback_op("apply_resource_draw", {"player_id": player.id})]),
        ]
        self._start_resolution_sequence("citadels_draw_cards", beats, tag="citadels_turn_action")

    def _action_keep_draw_card(self, player: Player, action_id: str) -> None:
        cit_player = self._as_citadels_player(player)
        if not cit_player:
            return
        card_id = self._parse_card_action(action_id, "keep_draw_")
        if card_id is None:
            return
        keep = self._find_card(self.pending_draw_choices, card_id)
        if keep is None:
            return
        for card in self.pending_draw_choices:
            if card.id == keep.id:
                cit_player.hand.append(card)
            else:
                self.district_deck.append(card)
        self.pending_draw_choices.clear()
        self.turn_subphase = SUBPHASE_NORMAL
        self.turn_resource_taken = True
        self.broadcast_l("citadels-player-kept-card", buffer="game", player=cit_player.name)
        user = self.get_user(cit_player)
        if user:
            user.speak_l(
                "citadels-you-kept-card",
                buffer="game",
                district=self._district_name(keep, user.locale),
            )
        self._refresh_menus_for_focus(cit_player)
        self._schedule_bot_turn(cit_player)

    def _action_collect_income(self, player: Player, action_id: str) -> None:
        _ = action_id
        cit_player = self._as_citadels_player(player)
        if not cit_player or cit_player.revealed_character_rank is None:
            return
        amount = self._income_amount(cit_player, cit_player.revealed_character_rank)
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "collect_income",
                        {
                            "player_id": cit_player.id,
                            "rank": cit_player.revealed_character_rank,
                            "amount": amount,
                        },
                    )
                ]
            )
        ]
        beats.extend(self._build_coin_beats(amount))
        self._start_resolution_sequence("citadels_collect_income", beats, tag="citadels_turn_action")

    def _action_enter_magician_swap(self, player: Player, action_id: str) -> None:
        _ = action_id
        self.turn_subphase = SUBPHASE_MAGICIAN_SWAP
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )

    def _action_magician_swap(self, player: Player, action_id: str) -> None:
        target = self._player_from_id_action(action_id, "magician_swap_target_")
        if not isinstance(target, CitadelsPlayer):
            return
        self._start_resolution_sequence(
            "citadels_magician_swap",
            self._build_magician_swap_beats(player.id, target.id),
            tag="citadels_turn_action",
        )

    def _action_enter_magician_redraw(self, player: Player, action_id: str) -> None:
        _ = action_id
        self.selected_card_ids.clear()
        self.turn_subphase = SUBPHASE_MAGICIAN_REDRAW
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )

    def _action_toggle_magician_redraw(self, player: Player, action_id: str) -> None:
        card_id = self._parse_card_action(action_id, "magician_redraw_toggle_")
        if card_id is None:
            return
        self._toggle_selected_card(card_id)
        self._refresh_menus_for_focus(player, selection_id=action_id)

    def _action_confirm_magician_redraw(self, player: Player, action_id: str) -> None:
        _ = action_id
        shuffle = random.choice(SHUFFLE_SOUNDS)
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(shuffle)],
                delay_after_ticks=self._paced_delay_ticks(shuffle),
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("magician_redraw", {"player_id": player.id, "card_ids": list(self.selected_card_ids)})]
            ),
        ]
        self._start_resolution_sequence("citadels_magician_redraw", beats, tag="citadels_turn_action")

    def _action_enter_laboratory(self, player: Player, action_id: str) -> None:
        _ = action_id
        self.turn_subphase = SUBPHASE_LABORATORY
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )

    def _action_laboratory_discard(self, player: Player, action_id: str) -> None:
        card_id = self._parse_card_action(action_id, "laboratory_discard_")
        if card_id is None:
            return
        beats = [SequenceBeat(ops=[SequenceOperation.callback_op("laboratory", {"player_id": player.id, "card_id": card_id})])]
        beats.extend(self._build_coin_beats(2))
        self._start_resolution_sequence("citadels_laboratory", beats, tag="citadels_turn_action")

    def _action_use_smithy(self, player: Player, action_id: str) -> None:
        _ = action_id
        shuffle = random.choice(SHUFFLE_SOUNDS)
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(shuffle)],
                delay_after_ticks=self._paced_delay_ticks(shuffle),
            ),
            SequenceBeat(ops=[SequenceOperation.callback_op("smithy", {"player_id": player.id})]),
        ]
        self._start_resolution_sequence("citadels_smithy", beats, tag="citadels_turn_action")

    def _action_build_card(self, player: Player, action_id: str) -> None:
        cit_player = self._as_citadels_player(player)
        if not cit_player:
            return
        card_id = self._parse_card_action(action_id, "build_")
        if card_id is None:
            return
        card = self._find_hand_card(cit_player, card_id)
        if card is None:
            return
        if card.effect_key == "thieves_den":
            self.pending_build_card_id = card.id
            self.selected_card_ids.clear()
            self.turn_subphase = SUBPHASE_THIEVES_DEN
            self._refresh_menus_for_focus(
                player,
                selection_id=self._preferred_focus_action_id(player),
            )
            return
        beats = self._build_district_beats(cit_player, card, [], self._effective_build_cost(cit_player, card))
        self._start_resolution_sequence("citadels_build", beats, tag="citadels_turn_action")

    def _action_toggle_thieves_den_payment(self, player: Player, action_id: str) -> None:
        card_id = self._parse_card_action(action_id, "thieves_den_toggle_")
        if card_id is None:
            return
        self._toggle_selected_card(card_id)
        self._refresh_menus_for_focus(player, selection_id=action_id)

    def _action_confirm_thieves_den(self, player: Player, action_id: str) -> None:
        _ = action_id
        cit_player = self._as_citadels_player(player)
        if not cit_player:
            return
        card = self._find_hand_card(cit_player, self.pending_build_card_id)
        if card is None:
            return
        gold_cost = self._effective_build_cost(cit_player, card) - len(self.selected_card_ids)
        beats = self._build_district_beats(cit_player, card, list(self.selected_card_ids), gold_cost)
        self._start_resolution_sequence("citadels_build", beats, tag="citadels_turn_action")

    def _action_enter_warlord_destroy(self, player: Player, action_id: str) -> None:
        _ = action_id
        self.turn_subphase = SUBPHASE_WARLORD_TARGET
        self._refresh_menus_for_focus(
            player,
            selection_id=self._preferred_focus_action_id(player),
        )

    def _action_warlord_destroy(self, player: Player, action_id: str) -> None:
        parsed = self._parse_owner_card_action(action_id, "warlord_destroy_target_")
        if parsed is None:
            return
        owner_id, district_id = parsed
        self._start_resolution_sequence(
            "citadels_warlord_destroy",
            self._build_warlord_destroy_beats(owner_id, district_id),
            tag="citadels_turn_action",
        )

    def _action_cancel_subphase(self, player: Player, action_id: str) -> None:
        _ = player, action_id
        self.turn_subphase = SUBPHASE_NORMAL
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self._refresh_menus_for_focus(player)

    def _action_end_turn(self, player: Player, action_id: str) -> None:
        _ = player, action_id
        self._finish_turn()

    def _gameplay_locked_reason(self) -> str | None:
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        return None

    def _is_dynamic_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_select_character_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing" or self.phase != PHASE_SELECTION:
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        rank = self._parse_rank_action(action_id or "", "select_character_")
        if rank not in self._selection_options_for_player(player):
            return "action-not-available"
        return None

    def _is_choose_assassin_target_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_ASSASSIN_TARGET:
            return "action-not-your-turn"
        rank = self._parse_rank_action(action_id or "", "assassinate_target_")
        if rank not in self._assassin_target_ranks():
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_choose_thief_target_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_THIEF_TARGET:
            return "action-not-your-turn"
        rank = self._parse_rank_action(action_id or "", "thief_target_")
        if rank not in self._thief_target_ranks():
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_take_gold_enabled(self, player: Player) -> str | None:
        if self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or self.turn_resource_taken:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_take_gold_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_take_gold_enabled(player) is None else Visibility.HIDDEN

    def _is_draw_cards_enabled(self, player: Player) -> str | None:
        return self._is_take_gold_enabled(player)

    def _is_draw_cards_hidden(self, player: Player) -> Visibility:
        return self._is_take_gold_hidden(player)

    def _is_keep_draw_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_DRAW_KEEP:
            return "action-not-your-turn"
        card_id = self._parse_card_action(action_id or "", "keep_draw_")
        if card_id is None or self._find_card(self.pending_draw_choices, card_id) is None:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_collect_income_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        if self.turn_income_used:
            return "action-not-available"
        if cit_player.revealed_character_rank not in {
            CHARACTER_KING,
            CHARACTER_BISHOP,
            CHARACTER_MERCHANT,
            CHARACTER_WARLORD,
        }:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_collect_income_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_collect_income_enabled(player) is None else Visibility.HIDDEN

    def _is_magician_mode_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        if self.turn_character_ability_used or cit_player.revealed_character_rank != CHARACTER_MAGICIAN:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_magician_swap_mode_enabled(self, player: Player) -> str | None:
        return self._is_magician_mode_enabled(player)

    def _is_magician_swap_mode_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_magician_swap_mode_enabled(player) is None else Visibility.HIDDEN

    def _is_magician_redraw_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        result = self._is_magician_mode_enabled(player)
        if result is not None:
            return result
        if not cit_player or not cit_player.hand:
            return "action-not-available"
        return None

    def _is_magician_redraw_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_magician_redraw_enabled(player) is None else Visibility.HIDDEN

    def _is_magician_swap_target_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_MAGICIAN_SWAP:
            return "action-not-your-turn"
        target = self._player_from_id_action(action_id or "", "magician_swap_target_")
        if not isinstance(target, CitadelsPlayer) or target.id == player.id or target.is_spectator:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_toggle_magician_redraw_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_MAGICIAN_REDRAW:
            return "action-not-your-turn"
        card_id = self._parse_card_action(action_id or "", "magician_redraw_toggle_")
        cit_player = self._as_citadels_player(player)
        if card_id is None or not cit_player or self._find_hand_card(cit_player, card_id) is None:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_confirm_magician_redraw_enabled(self, player: Player) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_MAGICIAN_REDRAW:
            return "action-not-your-turn"
        if not self.selected_card_ids:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_confirm_magician_redraw_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.turn_subphase == SUBPHASE_MAGICIAN_REDRAW and self.current_player == player else Visibility.HIDDEN

    def _is_cancel_subphase_enabled(self, player: Player) -> str | None:
        if self.current_player != player:
            return "action-not-your-turn"
        if self.turn_subphase in {
            SUBPHASE_MAGICIAN_REDRAW,
            SUBPHASE_THIEVES_DEN,
            SUBPHASE_MAGICIAN_SWAP,
            SUBPHASE_LABORATORY,
            SUBPHASE_WARLORD_TARGET,
        }:
            return None
        return "action-not-available"

    def _is_cancel_magician_redraw_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.turn_subphase == SUBPHASE_MAGICIAN_REDRAW and self.current_player == player else Visibility.HIDDEN

    def _is_cancel_subphase_hidden(self, player: Player) -> Visibility:
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.turn_subphase in {
            SUBPHASE_MAGICIAN_SWAP,
            SUBPHASE_LABORATORY,
            SUBPHASE_WARLORD_TARGET,
        }:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_use_laboratory_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        if self.turn_laboratory_used or not cit_player.hand:
            return "action-not-available"
        if not self._has_city_effect(cit_player, "laboratory"):
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_use_laboratory_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_use_laboratory_enabled(player) is None else Visibility.HIDDEN

    def _is_laboratory_discard_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_LABORATORY:
            return "action-not-your-turn"
        card_id = self._parse_card_action(action_id or "", "laboratory_discard_")
        cit_player = self._as_citadels_player(player)
        if card_id is None or not cit_player or self._find_hand_card(cit_player, card_id) is None:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_use_smithy_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        if self.turn_smithy_used or cit_player.gold < 2:
            return "action-not-available"
        if not self._has_city_effect(cit_player, "smithy"):
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_use_smithy_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_use_smithy_enabled(player) is None else Visibility.HIDDEN

    def _is_build_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        card_id = self._parse_card_action(action_id or "", "build_")
        card = self._find_hand_card(cit_player, card_id)
        if card is None or not self._can_attempt_build(cit_player, card):
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_toggle_thieves_den_payment_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_THIEVES_DEN:
            return "action-not-your-turn"
        card_id = self._parse_card_action(action_id or "", "thieves_den_toggle_")
        cit_player = self._as_citadels_player(player)
        if card_id is None or not cit_player or self._find_hand_card(cit_player, card_id) is None:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_confirm_thieves_den_payment_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player or self.turn_subphase != SUBPHASE_THIEVES_DEN:
            return "action-not-your-turn"
        card = self._find_hand_card(cit_player, self.pending_build_card_id)
        if card is None:
            return "action-not-available"
        gold_cost = self._effective_build_cost(cit_player, card) - len(self.selected_card_ids)
        if gold_cost < 0 or gold_cost > cit_player.gold:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_confirm_thieves_den_payment_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.turn_subphase == SUBPHASE_THIEVES_DEN and self.current_player == player else Visibility.HIDDEN

    def _is_cancel_thieves_den_payment_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.turn_subphase == SUBPHASE_THIEVES_DEN and self.current_player == player else Visibility.HIDDEN

    def _is_warlord_destroy_mode_enabled(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        if self.turn_character_ability_used or cit_player.revealed_character_rank != CHARACTER_WARLORD:
            return "action-not-available"
        if not self._warlord_targets():
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_warlord_destroy_mode_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_warlord_destroy_mode_enabled(player) is None else Visibility.HIDDEN

    def _is_warlord_destroy_target_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.current_player != player or self.turn_subphase != SUBPHASE_WARLORD_TARGET:
            return "action-not-your-turn"
        parsed = self._parse_owner_card_action(action_id or "", "warlord_destroy_target_")
        if parsed is None:
            return "action-not-available"
        valid = {(owner.id, district.id) for owner, district in self._warlord_targets()}
        if parsed not in valid:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_end_turn_enabled(self, player: Player) -> str | None:
        if self.current_player != player:
            return "action-not-your-turn"
        if self.phase != PHASE_TURN or self.turn_subphase != SUBPHASE_NORMAL or not self.turn_resource_taken:
            return "action-not-available"
        return self._gameplay_locked_reason()

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_end_turn_enabled(player) is None else Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_read_status_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_read_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_status_detailed_enabled(self, player: Player) -> str | None:
        return self._is_read_status_enabled(player)

    def _is_read_status_detailed_hidden(self, player: Player) -> Visibility:
        return self._is_read_status_hidden(player)

    def _is_read_character_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_read_character_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing" and not player.is_spectator:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing" and not player.is_spectator:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_cities_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_read_cities_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_discards_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_read_discards_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        _ = action_id
        cit_player = self._as_citadels_player(player)
        user = self.get_user(player)
        if not cit_player or not user:
            return
        lines = [Localization.get(user.locale, "citadels-hand-header", count=len(cit_player.hand))]
        if cit_player.hand:
            for card in sorted(cit_player.hand, key=lambda c: (c.cost, c.name)):
                lines.append(self._district_line(card, user.locale))
        else:
            lines.append(Localization.get(user.locale, "citadels-hand-empty"))
        self.status_box(player, lines)

    def _action_read_cities(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "citadels-cities-header")]
        for cit_player in self.get_active_players():
            city_names = (
                ", ".join(self._district_name(card, user.locale) for card in cit_player.city)
                or Localization.get(user.locale, "citadels-city-empty")
            )
            lines.append(
                Localization.get(
                    user.locale,
                    "citadels-city-line",
                    player=cit_player.name,
                    count=len(cit_player.city),
                    gold=cit_player.gold,
                    score=self._score_city(cit_player),
                    districts=city_names,
                )
            )
        self.status_box(player, lines)

    def _action_read_character(self, player: Player, action_id: str) -> None:
        _ = action_id
        cit_player = self._as_citadels_player(player)
        user = self.get_user(player)
        if not cit_player or not user:
            return
        if cit_player.selected_character_rank is None:
            user.speak_l("citadels-character-none", buffer="game", gold=cit_player.gold)
        else:
            user.speak_l(
                "citadels-character-line",
                buffer="game",
                gold=cit_player.gold,
                rank=cit_player.selected_character_rank,
                character=self._character_name(cit_player.selected_character_rank, user.locale),
            )

    def _action_read_discards(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        faceup = (
            ", ".join(self._character_name(rank, user.locale) for rank in self.faceup_discarded_ranks)
            if self.faceup_discarded_ranks
            else Localization.get(user.locale, "citadels-discards-none")
        )
        user.speak_l("citadels-faceup-discards-line", buffer="game", characters=faceup)

    def _action_read_status(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        self._speak_lines(player, self._status_lines(user.locale, detailed=False))

    def _action_read_status_detailed(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        self.status_box(player, self._status_lines(user.locale, detailed=True))

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("citadels-standings-header", buffer="game")
        for line in self._standings_lines(user.locale):
            user.speak(line, buffer="game")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "citadels-standings-header")]
        lines.extend(self._standings_lines(user.locale))
        self.status_box(player, lines)

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        _ = sequence_id
        if callback_id == "skip_rank":
            self._handle_skipped_rank(payload)
            return
        if callback_id == "apply_robbery":
            self._apply_robbery(payload)
            return
        if callback_id == "resume_turn_after_robbery":
            target = self.get_player_by_id(payload.get("target_id", ""))
            if isinstance(target, CitadelsPlayer) and target.revealed_character_rank is not None:
                self._begin_turn(target, target.revealed_character_rank)
            return
        if callback_id == "take_crown":
            player = self.get_player_by_id(payload.get("player_id", ""))
            if isinstance(player, CitadelsPlayer):
                self.crown_holder_id = player.id
                self.broadcast_l("citadels-crown-taken", buffer="game", player=player.name)
                if player.revealed_character_rank is not None:
                    self._announce_turn_ready(player, player.revealed_character_rank)
            return
        if callback_id == "architect_bonus":
            player = self.get_player_by_id(payload.get("player_id", ""))
            if isinstance(player, CitadelsPlayer):
                self._draw_to_hand(player, 2)
                self.broadcast_l("citadels-architect-bonus", buffer="game", player=player.name, count=2)
                if player.revealed_character_rank is not None:
                    self._announce_turn_ready(player, player.revealed_character_rank)
            return
        if callback_id == "apply_resource_gold":
            self._apply_take_gold_callback(payload)
            return
        if callback_id == "apply_resource_draw":
            self._apply_draw_cards_callback(payload)
            return
        if callback_id == "collect_income":
            self._apply_collect_income_callback(payload)
            return
        if callback_id == "magician_swap":
            self._apply_magician_swap_callback(payload)
            return
        if callback_id == "magician_redraw":
            self._apply_magician_redraw_callback(payload)
            return
        if callback_id == "laboratory":
            self._apply_laboratory_callback(payload)
            return
        if callback_id == "smithy":
            self._apply_smithy_callback(payload)
            return
        if callback_id == "build_district":
            self._apply_build_callback(payload)
            return
        if callback_id == "warlord_destroy":
            self._apply_warlord_destroy_callback(payload)
            return
        if callback_id == "round_cleanup_king_heir":
            self._apply_round_cleanup_king_heir(payload)
            return
        if callback_id == "announce_winner":
            winner = self.get_player_by_id(payload.get("winner_id", ""))
            if isinstance(winner, CitadelsPlayer):
                self.broadcast_l("game-winner", buffer="game", player=winner.name)
            return
        if callback_id == "finish_game":
            self.finish_game()
            return

    def _handle_skipped_rank(self, payload: dict) -> None:
        rank = int(payload.get("rank", 0))
        self._broadcast_localized(
            "citadels-character-killed-skip",
            buffer="game",
            rank=rank,
            character=lambda locale: self._character_name(rank, locale),
        )
        self.current_rank = rank + 1
        self._advance_rank_resolution()

    def _apply_robbery(self, payload: dict) -> None:
        target = self.get_player_by_id(payload.get("target_id", ""))
        robber = self.get_player_by_id(self.robber_player_id or "")
        if not isinstance(target, CitadelsPlayer) or not isinstance(robber, CitadelsPlayer):
            return
        amount = min(target.gold, int(payload.get("amount", 0)))
        if amount <= 0:
            self.broadcast_l("citadels-thief-found-nothing", buffer="game", player=robber.name)
            return
        target.gold -= amount
        robber.gold += amount
        self.broadcast_l(
            "citadels-thief-stole-gold",
            buffer="game",
            thief=robber.name,
            amount=amount,
        )

    def _apply_take_gold_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        player.gold += 2
        self.turn_resource_taken = True
        self.broadcast_l("citadels-player-took-gold", buffer="game", player=player.name, amount=2)
        self._after_turn_state_change(player)

    def _apply_draw_cards_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        drawn = self._draw_cards(2)
        self.turn_resource_taken = True
        if self._has_city_effect(player, "library"):
            player.hand.extend(drawn)
            self.broadcast_l("citadels-library-draw", buffer="game", player=player.name, count=len(drawn))
            self._after_turn_state_change(player)
            return
        if drawn:
            self.pending_draw_choices = drawn
            self.turn_subphase = SUBPHASE_DRAW_KEEP
            self.broadcast_l("citadels-player-drew-options", buffer="game", player=player.name, count=len(drawn))
            self._refresh_menus_for_focus(
                player,
                selection_id=self._preferred_focus_action_id(player),
            )
            self._schedule_bot_turn(player)
            return
        self._after_turn_state_change(player)

    def _apply_collect_income_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        amount = max(0, int(payload.get("amount", 0)))
        rank = int(payload.get("rank", 0))
        player.gold += amount
        self.turn_income_used = True
        self._broadcast_localized(
            "citadels-income-collected",
            buffer="game",
            player=player.name,
            character=lambda locale: self._character_name(rank, locale),
            amount=amount,
        )
        self._after_turn_state_change(player)

    def _apply_magician_swap_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        target = self.get_player_by_id(payload.get("target_id", ""))
        if not isinstance(player, CitadelsPlayer) or not isinstance(target, CitadelsPlayer):
            return
        player.hand, target.hand = target.hand, player.hand
        self.turn_character_ability_used = True
        self.turn_subphase = SUBPHASE_NORMAL
        self.broadcast_l("citadels-magician-swapped", buffer="game", player=player.name, target=target.name)
        self._after_turn_state_change(player)

    def _apply_magician_redraw_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        card_ids = {int(card_id) for card_id in payload.get("card_ids", [])}
        kept: list[DistrictCard] = []
        discarded: list[DistrictCard] = []
        for card in player.hand:
            if card.id in card_ids:
                discarded.append(card)
            else:
                kept.append(card)
        if not discarded:
            return
        player.hand = kept
        self.district_deck.extend(discarded)
        player.hand.extend(self._draw_cards(len(discarded)))
        self.turn_character_ability_used = True
        self.turn_subphase = SUBPHASE_NORMAL
        self.selected_card_ids.clear()
        self.broadcast_l("citadels-magician-redrew", buffer="game", player=player.name, count=len(discarded))
        self._after_turn_state_change(player)

    def _apply_laboratory_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        card = self._remove_hand_card(player, int(payload.get("card_id", -1)))
        if card is None:
            return
        self.district_deck.append(card)
        player.gold += 2
        self.turn_laboratory_used = True
        self.turn_subphase = SUBPHASE_NORMAL
        self.broadcast_l(
            "citadels-laboratory-used",
            buffer="game",
            player=player.name,
            amount=2,
        )
        self._after_turn_state_change(player)

    def _apply_smithy_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer) or player.gold < 2:
            return
        player.gold -= 2
        drawn = self._draw_cards(3)
        player.hand.extend(drawn)
        self.turn_smithy_used = True
        self.broadcast_l("citadels-smithy-used", buffer="game", player=player.name, count=len(drawn))
        self._after_turn_state_change(player)

    def _apply_build_callback(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        card = self._remove_hand_card(player, int(payload.get("card_id", -1)))
        if card is None:
            return
        discard_card_ids = {int(card_id) for card_id in payload.get("discard_card_ids", [])}
        gold_cost = max(0, int(payload.get("gold_cost", 0)))
        discarded_cards: list[DistrictCard] = []
        if discard_card_ids:
            remaining: list[DistrictCard] = []
            for hand_card in player.hand:
                if hand_card.id in discard_card_ids:
                    self.district_deck.append(hand_card)
                    discarded_cards.append(hand_card)
                else:
                    remaining.append(hand_card)
            player.hand = remaining
        player.gold -= gold_cost
        player.city.append(card)
        self.turn_builds_made += 1
        self.turn_subphase = SUBPHASE_NORMAL
        self.selected_card_ids.clear()
        self.pending_build_card_id = None
        self._broadcast_localized(
            "citadels-district-built",
            buffer="game",
            player=player.name,
            district=lambda locale: self._district_name(card, locale),
            gold=gold_cost,
        )
        if discarded_cards:
            owner_user = self.get_user(player)
            if owner_user:
                owner_user.speak_l(
                    "citadels-thieves-den-payment",
                    buffer="game",
                    cards=Localization.format_list_and(
                        owner_user.locale,
                        [self._district_name(discarded_card, owner_user.locale) for discarded_card in discarded_cards],
                    ),
                )
        if len(player.city) >= WIN_DISTRICT_COUNT and player.id not in self.city_completion_order:
            self.city_completion_order.append(player.id)
            if self.first_completed_city_player_id is None:
                self.first_completed_city_player_id = player.id
            self.broadcast_l("citadels-city-completed", buffer="game", player=player.name, count=len(player.city))
        self._after_turn_state_change(player)

    def _apply_warlord_destroy_callback(self, payload: dict) -> None:
        owner = self.get_player_by_id(payload.get("owner_id", ""))
        current = self.current_player
        if not isinstance(owner, CitadelsPlayer) or not isinstance(current, CitadelsPlayer):
            return
        district_id = int(payload.get("district_id", -1))
        district = self._remove_city_card(owner, district_id)
        if district is None:
            return
        current.gold -= max(0, self._warlord_destroy_cost(owner, district))
        self.district_deck.append(district)
        self.turn_character_ability_used = True
        self.turn_subphase = SUBPHASE_NORMAL
        self._broadcast_localized(
            "citadels-warlord-destroyed",
            buffer="game",
            player=current.name,
            target=owner.name,
            district=lambda locale: self._district_name(district, locale),
        )
        self._after_turn_state_change(current)

    def _apply_round_cleanup_king_heir(self, payload: dict) -> None:
        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, CitadelsPlayer):
            return
        player.revealed_character_rank = CHARACTER_KING
        self.crown_holder_id = player.id
        self.broadcast_l("citadels-king-heir", buffer="game", player=player.name)
        if self.pending_queen_bonus_player_id:
            queen = self.get_player_by_id(self.pending_queen_bonus_player_id)
            if isinstance(queen, CitadelsPlayer):
                queen.gold += 3
                self.broadcast_l("citadels-queen-bonus", buffer="game", player=queen.name, amount=3)
            self.pending_queen_bonus_player_id = None
        self._complete_round_cleanup()

    def _after_turn_state_change(self, player: CitadelsPlayer) -> None:
        self._refresh_menus_for_focus(player)
        self._schedule_bot_turn(player)

    def _build_district_deck(self) -> list[DistrictCard]:
        deck: list[DistrictCard] = []
        next_id = 0
        for slug, name, cost, district_type, effect_key, count in DISTRICT_DEFS:
            for _ in range(count):
                deck.append(
                    DistrictCard(
                        id=next_id,
                        slug=slug,
                        name=name,
                        cost=cost,
                        district_type=district_type,
                        effect_key=effect_key,
                    )
                )
                next_id += 1
        return deck

    def _draw_cards(self, count: int) -> list[DistrictCard]:
        drawn: list[DistrictCard] = []
        for _ in range(count):
            if not self.district_deck:
                break
            drawn.append(self.district_deck.pop(0))
        return drawn

    def _draw_to_hand(self, player: CitadelsPlayer, count: int) -> None:
        player.hand.extend(self._draw_cards(count))

    def _character_ranks_in_play(self) -> list[int]:
        return list(QUEEN_CHARACTER_RANKS if len(self.get_active_players()) == 8 else BASE_CHARACTER_RANKS)

    def _faceup_discard_count(self) -> int:
        player_count = len(self.get_active_players())
        return FACEUP_DISCARD_COUNTS_9.get(player_count, FACEUP_DISCARD_COUNTS_8.get(player_count, 0))

    def _selection_player(self) -> CitadelsPlayer | None:
        if self.selection_index >= len(self.selection_order_player_ids):
            return None
        player = self.get_player_by_id(self.selection_order_player_ids[self.selection_index])
        return player if isinstance(player, CitadelsPlayer) else None

    def _players_from_crown(self) -> list[CitadelsPlayer]:
        active = [p for p in self.get_active_players() if isinstance(p, CitadelsPlayer)]
        if not active or self.crown_holder_id is None:
            return active
        for index, player in enumerate(active):
            if player.id == self.crown_holder_id:
                return active[index:] + active[:index]
        return active

    def _selection_options_for_player(self, player: Player) -> list[int]:
        cit_player = self._as_citadels_player(player)
        if not cit_player or self.phase != PHASE_SELECTION or self.current_player != player:
            return []
        options = list(self.available_character_ranks)
        is_last = self.selection_index == len(self.selection_order_player_ids) - 1
        if is_last and len(self.get_active_players()) in {7, 8} and self.initial_facedown_rank is not None:
            options.append(self.initial_facedown_rank)
        return options

    def _player_with_rank(self, rank: int) -> CitadelsPlayer | None:
        for player in self.get_active_players():
            if isinstance(player, CitadelsPlayer) and player.selected_character_rank == rank:
                return player
        return None

    def _character_name(self, rank: int, locale: str) -> str:
        return Localization.get(locale, f"citadels-character-{rank}")

    def _district_type_name(self, district_type: str, locale: str) -> str:
        return Localization.get(locale, f"citadels-district-type-{district_type}")

    def _district_line(self, card: DistrictCard, locale: str) -> str:
        return Localization.get(
            locale,
            "citadels-district-line",
            district=self._district_name(card, locale),
            cost=card.cost,
            type=self._district_type_name(card.district_type, locale),
            description=self._district_effect_description(card, locale),
        )

    def _toggle_line(self, locale: str, card: DistrictCard, selected: bool) -> str:
        key = "citadels-toggle-selected" if selected else "citadels-toggle-not-selected"
        return Localization.get(locale, key, district=self._district_name(card, locale), cost=card.cost)

    def _coin_sound(self, amount: int) -> str:
        if amount >= 5:
            return COIN_SOUNDS["large"]
        if amount >= 3:
            return COIN_SOUNDS["medium"]
        return COIN_SOUNDS["small"]

    def _has_city_effect(self, player: CitadelsPlayer, effect_key: str) -> bool:
        return any(card.effect_key == effect_key for card in player.city)

    def _effective_build_cost(self, player: CitadelsPlayer, card: DistrictCard) -> int:
        cost = card.cost
        if card.effect_key != "factory" and card.is_unique and self._has_city_effect(player, "factory"):
            cost = max(0, cost - 1)
        return cost

    def _can_attempt_build(self, player: CitadelsPlayer, card: DistrictCard) -> bool:
        if not self._may_build_more() or not self._can_build_duplicate(player, card):
            return False
        cost = self._effective_build_cost(player, card)
        if card.effect_key == "thieves_den":
            return player.gold + max(0, len(player.hand) - 1) >= cost
        return player.gold >= cost

    def _can_build_duplicate(self, player: CitadelsPlayer, card: DistrictCard) -> bool:
        if self._has_city_effect(player, "quarry"):
            return True
        return not any(city_card.name == card.name for city_card in player.city)

    def _may_build_more(self) -> bool:
        return self.turn_builds_made < self.turn_build_limit

    def _income_amount(self, player: CitadelsPlayer, rank: int) -> int:
        wanted_type = {
            CHARACTER_KING: DISTRICT_NOBLE,
            CHARACTER_BISHOP: DISTRICT_RELIGIOUS,
            CHARACTER_MERCHANT: DISTRICT_TRADE,
            CHARACTER_WARLORD: DISTRICT_MILITARY,
        }.get(rank)
        amount = 0
        if wanted_type is not None:
            amount = sum(1 for card in player.city if card.district_type == wanted_type)
            if self._has_city_effect(player, "school_of_magic"):
                amount += 1
        if rank == CHARACTER_MERCHANT:
            amount += 1
        return amount

    def _assassin_target_ranks(self) -> list[int]:
        return [rank for rank in self._character_ranks_in_play() if rank != CHARACTER_ASSASSIN]

    def _thief_target_ranks(self) -> list[int]:
        return [
            rank
            for rank in self._character_ranks_in_play()
            if rank not in {CHARACTER_ASSASSIN, CHARACTER_THIEF, self.killed_rank}
        ]

    def _swap_targets(self) -> list[CitadelsPlayer]:
        return [player for player in self.get_active_players() if isinstance(player, CitadelsPlayer) and player != self.current_player]

    def _warlord_targets(self) -> list[tuple[CitadelsPlayer, DistrictCard]]:
        current = self._as_citadels_player(self.current_player)
        if not current:
            return []
        targets: list[tuple[CitadelsPlayer, DistrictCard]] = []
        for owner in self.get_active_players():
            if not isinstance(owner, CitadelsPlayer) or len(owner.city) >= WIN_DISTRICT_COUNT:
                continue
            protected = owner.selected_character_rank == CHARACTER_BISHOP and self.killed_rank != CHARACTER_BISHOP and owner != current
            for district in owner.city:
                if protected or district.effect_key == "keep":
                    continue
                cost = self._warlord_destroy_cost(owner, district)
                if current.gold >= cost:
                    targets.append((owner, district))
        return targets

    def _warlord_destroy_cost(self, owner: CitadelsPlayer, district: DistrictCard) -> int:
        _ = owner
        return max(0, district.cost - 1)

    def _find_card(self, cards: list[DistrictCard], card_id: int | None) -> DistrictCard | None:
        if card_id is None:
            return None
        for card in cards:
            if card.id == card_id:
                return card
        return None

    def _find_hand_card(self, player: CitadelsPlayer, card_id: int | None) -> DistrictCard | None:
        return self._find_card(player.hand, card_id)

    def _remove_hand_card(self, player: CitadelsPlayer, card_id: int) -> DistrictCard | None:
        for index, card in enumerate(player.hand):
            if card.id == card_id:
                return player.hand.pop(index)
        return None

    def _remove_city_card(self, player: CitadelsPlayer, card_id: int) -> DistrictCard | None:
        for index, card in enumerate(player.city):
            if card.id == card_id:
                return player.city.pop(index)
        return None

    def _toggle_selected_card(self, card_id: int) -> None:
        if card_id in self.selected_card_ids:
            self.selected_card_ids.remove(card_id)
        else:
            self.selected_card_ids.append(card_id)

    def _player_from_id_action(self, action_id: str, prefix: str) -> CitadelsPlayer | None:
        if not action_id.startswith(prefix):
            return None
        player = self.get_player_by_id(action_id.removeprefix(prefix))
        return player if isinstance(player, CitadelsPlayer) else None

    def _parse_rank_action(self, action_id: str, prefix: str) -> int | None:
        if not action_id.startswith(prefix):
            return None
        raw = action_id.removeprefix(prefix)
        return int(raw) if raw.isdigit() else None

    def _parse_card_action(self, action_id: str, prefix: str) -> int | None:
        if not action_id.startswith(prefix):
            return None
        raw = action_id.removeprefix(prefix)
        return int(raw) if raw.isdigit() else None

    def _parse_owner_card_action(self, action_id: str, prefix: str) -> tuple[str, int] | None:
        if not action_id.startswith(prefix):
            return None
        owner_id, _, raw_card = action_id.removeprefix(prefix).partition("_")
        if not owner_id or not raw_card.isdigit():
            return None
        return owner_id, int(raw_card)

    def _build_district_beats(
        self,
        player: CitadelsPlayer,
        card: DistrictCard,
        discard_card_ids: list[int],
        gold_cost: int,
    ) -> list[SequenceBeat]:
        build_sound = random.choice(BUILD_SOUNDS)
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(build_sound)],
                delay_after_ticks=self._paced_delay_ticks(build_sound),
            ),
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "build_district",
                        {
                            "player_id": player.id,
                            "card_id": card.id,
                            "discard_card_ids": list(discard_card_ids),
                            "gold_cost": gold_cost,
                        },
                    )
                ]
            ),
        ]
        if len(player.city) + 1 >= WIN_DISTRICT_COUNT and player.id not in self.city_completion_order:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_CITY_COMPLETE)],
                    delay_after_ticks=self._paced_delay_ticks(SOUND_CITY_COMPLETE),
                )
            )
        return beats

    def _apply_queen_bonus(self, player: CitadelsPlayer) -> None:
        king_owner = self._player_with_rank(CHARACTER_KING)
        if king_owner is None or not self._players_are_adjacent(player, king_owner):
            return
        if self.killed_rank == CHARACTER_KING:
            self.pending_queen_bonus_player_id = player.id
            return
        player.gold += 3
        self.broadcast_l("citadels-queen-bonus", buffer="game", player=player.name, amount=3)

    def _players_are_adjacent(self, a: CitadelsPlayer, b: CitadelsPlayer) -> bool:
        seats = [p for p in self.get_active_players() if isinstance(p, CitadelsPlayer)]
        if len(seats) < 2:
            return False
        try:
            a_index = seats.index(a)
            b_index = seats.index(b)
        except ValueError:
            return False
        return (a_index - b_index) % len(seats) in {1, len(seats) - 1}

    def _as_citadels_player(self, player: Player | None) -> CitadelsPlayer | None:
        return player if isinstance(player, CitadelsPlayer) else None

    def _any_completed_city(self) -> bool:
        return any(len(player.city) >= WIN_DISTRICT_COUNT for player in self.get_active_players() if isinstance(player, CitadelsPlayer))

    def _score_city(self, player: CitadelsPlayer) -> int:
        base = sum(card.cost for card in player.city)
        best_bonus = 0
        haunted = next((card for card in player.city if card.effect_key == "haunted_quarter"), None)
        unique_count = sum(1 for card in player.city if card.district_type == DISTRICT_UNIQUE)
        wished = self._has_city_effect(player, "wishing_well")
        present_counts = {district_type: 0 for district_type in ALL_DISTRICT_TYPES}
        for card in player.city:
            present_counts[card.district_type] += 1
        choices = [DISTRICT_UNIQUE]
        if haunted:
            choices.extend([DISTRICT_NOBLE, DISTRICT_RELIGIOUS, DISTRICT_TRADE, DISTRICT_MILITARY])
        for haunted_choice in choices:
            counts = dict(present_counts)
            wishing_bonus = unique_count if wished else 0
            if haunted and haunted_choice != DISTRICT_UNIQUE:
                counts[DISTRICT_UNIQUE] -= 1
                counts[haunted_choice] += 1
                if wished:
                    wishing_bonus = max(0, wishing_bonus - 1)
            bonus = 0
            if all(counts[dtype] > 0 for dtype in ALL_DISTRICT_TYPES):
                bonus += 3
            if self.first_completed_city_player_id == player.id:
                bonus += 4
            elif len(player.city) >= WIN_DISTRICT_COUNT:
                bonus += 2
            for card in player.city:
                if card.effect_key == "dragon_gate":
                    bonus += 2
                elif card.effect_key == "imperial_treasury":
                    bonus += player.gold
                elif card.effect_key == "map_room":
                    bonus += len(player.hand)
                elif card.effect_key == "statue" and self.crown_holder_id == player.id:
                    bonus += 5
            bonus += wishing_bonus
            best_bonus = max(best_bonus, bonus)
        return base + best_bonus

    def _standings_lines(self, locale: str) -> list[str]:
        players = self._ranked_players_for_results()
        return [
            Localization.get(
                locale,
                "citadels-standing-line",
                rank=index,
                player=player.name,
                score=self._score_city(player),
                gold=player.gold,
                districts=len(player.city),
                cards=len(player.hand),
            )
            for index, player in enumerate(players, 1)
        ]

    def _final_ranking_key(self, player: CitadelsPlayer) -> tuple[int, int, int]:
        return (
            self._score_city(player),
            player.revealed_character_rank if player.revealed_character_rank is not None else -1,
            player.gold,
        )

    def _ranked_players_for_results(
        self,
        players: list[CitadelsPlayer] | None = None,
    ) -> list[CitadelsPlayer]:
        participants = (
            players
            if players is not None
            else [p for p in self.get_active_players() if isinstance(p, CitadelsPlayer)]
        )
        return sorted(participants, key=self._final_ranking_key, reverse=True)

    def _winner_player(self) -> CitadelsPlayer | None:
        ranked = self._ranked_players_for_results()
        return ranked[0] if ranked else None

    def _status_lines(self, locale: str, *, detailed: bool) -> list[str]:
        lines = [Localization.get(locale, "citadels-status-header")]
        crown_holder = self.get_player_by_id(self.crown_holder_id or "")
        if crown_holder:
            lines.append(Localization.get(locale, "citadels-status-crown", player=crown_holder.name))
        if self.phase == PHASE_SELECTION:
            current = self.current_player
            if current:
                lines.append(Localization.get(locale, "citadels-status-selection", player=current.name))
        elif self.phase == PHASE_RANK_RESOLUTION:
            rank = self.current_rank or 0
            lines.append(Localization.get(locale, "citadels-status-rank-resolution", rank=rank, character=self._character_name(rank, locale)))
        elif self.phase == PHASE_TURN:
            current = self.current_player
            if current and isinstance(current, CitadelsPlayer) and current.revealed_character_rank is not None:
                lines.append(
                    Localization.get(
                        locale,
                        "citadels-status-turn",
                        player=current.name,
                        rank=current.revealed_character_rank,
                        character=self._character_name(current.revealed_character_rank, locale),
                    )
                )
                lines.append(Localization.get(locale, "citadels-status-turn-progress", builds=self.turn_builds_made, limit=self.turn_build_limit))
        if detailed:
            if self.killed_rank is None:
                lines.append(Localization.get(locale, "citadels-status-killed-none"))
            else:
                lines.append(
                    Localization.get(
                        locale,
                        "citadels-status-killed",
                        rank=self.killed_rank,
                        character=self._character_name(self.killed_rank, locale),
                    )
                )
            if self.robbed_rank is None:
                lines.append(Localization.get(locale, "citadels-status-robbed-none"))
            else:
                lines.append(
                    Localization.get(
                        locale,
                        "citadels-status-robbed",
                        rank=self.robbed_rank,
                        character=self._character_name(self.robbed_rank, locale),
                    )
                )
            first_completed = self.get_player_by_id(self.first_completed_city_player_id or "")
            if first_completed:
                lines.append(
                    Localization.get(
                        locale,
                        "citadels-status-first-completed",
                        player=first_completed.name,
                    )
                )
        return lines

    def build_game_result(self) -> GameResult:
        players = [p for p in self.get_active_players() if isinstance(p, CitadelsPlayer)]
        sorted_players = self._ranked_players_for_results(players)
        winner = sorted_players[0] if sorted_players else None
        final_scores = {player.name: self._score_city(player) for player in players}
        team_rankings = [
            {
                "members": [player.name],
                "score": (self._score_city(player) * 100) + (player.revealed_character_rank if player.revealed_character_rank is not None else -1),
            }
            for player in sorted_players
        ]
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(player_id=player.id, player_name=player.name, is_bot=player.is_bot and not player.replaced_human)
                for player in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                "final_gold": {player.name: player.gold for player in players},
                "final_district_counts": {player.name: len(player.city) for player in players},
                "final_rank_values": {player.name: player.revealed_character_rank if player.revealed_character_rank is not None else -1 for player in players},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        rankings = sorted(
            result.custom_data.get("final_scores", {}).items(),
            key=lambda item: (item[1], result.custom_data.get("final_rank_values", {}).get(item[0], -1)),
            reverse=True,
        )
        for index, (name, score) in enumerate(rankings, 1):
            lines.append(
                Localization.get(
                    locale,
                    "citadels-end-line",
                    rank=index,
                    player=name,
                    score=score,
                    gold=result.custom_data.get("final_gold", {}).get(name, 0),
                    districts=result.custom_data.get("final_district_counts", {}).get(name, 0),
                )
            )
        return lines

    def bot_think(self, player: Player) -> str | None:
        cit_player = self._as_citadels_player(player)
        if not cit_player:
            return None
        return citadels_bot_think(self, cit_player)
