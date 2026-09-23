"""Breach Point - an audio-first turn-based tactical shooter."""

from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult
from ...game_utils.options import MenuOption, option_field
from ...game_utils.reaction_window import ReactionWindow
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, GameOptions, Player
from ..registry import register_game
from .arsenal import (
    BUY_CATEGORIES,
    BUY_CATEGORY_EQUIPMENT,
    BUY_CATEGORY_GRENADES,
    BUY_CATEGORY_MID_TIER,
    BUY_CATEGORY_PISTOLS,
    BUY_CATEGORY_RIFLES,
    SIDE_COUNTER_TERRORISTS,
    SIDE_INDEXES,
    SIDE_TERRORISTS,
    STANDARD_ECONOMY,
    UTILITY_EFFECT_EXPLOSIVE,
    UTILITY_EFFECT_FIRE,
    UTILITY_EFFECT_FLASH,
    UTILITY_EFFECT_SMOKE,
    WEAPON_BUY_CATEGORIES,
    WEAPON_SLOT_PRIMARY,
    WEAPON_SLOT_SIDEARM,
    EconomyProfile,
    EquipmentProfile,
    UtilityProfile,
    WeaponProfile,
    get_default_sidearm,
    get_equipment,
    get_purchasable_equipment,
    get_purchasable_utilities,
    get_purchasable_weapons,
    get_utilities,
    get_utility,
    get_weapon,
)
from .audio import (
    BOMB_BEEP_ASSETS,
    BOMB_DEFUSE_START_ASSET,
    BOMB_DEFUSED_ASSET,
    BOMB_DETONATION_AUDIO_SEQUENCE_TAG,
    BOMB_EXPLOSION_ASSET,
    BOMB_EXPLOSION_HANDLE,
    BUY_COUNTDOWN_ASSET,
    BUY_ITEM_HOVER_ASSETS,
    FINAL_ROUND_STINGER_ASSET,
    LAST_ROUND_HALF_ASSET,
    MATCH_VICTORY_ASSET,
    MOVEMENT_AUDIO_SEQUENCE_TAG,
    MUSIC_ACTION_STOP_SEQUENCE_TAG,
    MUSIC_BOMB_PLANTED_ASSET,
    MUSIC_BOMB_TEN_SECOND_ASSET,
    MUSIC_CONTEXT_HANDLE,
    MUSIC_CROSSFADE_MS,
    MUSIC_MATCH_START_ASSET,
    MUSIC_ROUND_START_ASSET,
    MUSIC_ROUND_TEN_SECOND_ASSET,
    RADIO_BOMB_DEFUSED_ASSET,
    RADIO_BOMB_PLANTED_ASSET,
    RADIO_COUNTER_TERRORISTS_WIN_ASSET,
    RADIO_TERRORISTS_WIN_ASSET,
    TICKS_PER_SECOND,
    TURN_NOTIFICATION_ASSET,
    UTILITY_AUDIO_SEQUENCE_TAG,
    WEAPON_AUDIO_SEQUENCE_TAG,
    BreachPointAudioMixin,
    bomb_detonation_warning_ticks,
    movement_audio_plan,
    utility_audio_timing,
    weapon_fire_delay_ticks,
)
from .bot import BreachPointBotCoordinator
from .effects import AreaEffectState
from .ground import BuyTransaction, DroppedWeapon, PendingWeaponDonation
from .maps import (
    DEFAULT_MAP_ID,
    GridPoint,
    TacticalMap,
    TacticalNode,
    get_tactical_map,
)
from .player import BreachPointPlayer
from .rules import (
    DEFAULT_MATCH_FORMAT_ID,
    DEFAULT_OVERTIME_MODE,
    MATCH_FORMATS,
    OVERTIME_DRAW,
    OVERTIME_MODES,
    OVERTIME_MR3,
    STANDARD_RULES,
    BreachPointRules,
    MatchFormat,
    get_match_format,
)
from .state import (
    BOMB_CARRIED,
    BOMB_DROPPED,
    BOMB_PLANTED,
    BOMB_PLANTING,
    BOMB_STATES,
    MATCH_DRAW,
    MATCH_OVERTIME,
    MATCH_REGULATION,
    MATCH_RESULTS,
    PHASE_BUY,
    PHASE_COMBAT,
    PHASES,
    REACTION_DEFUSE,
    REACTION_KINDS,
    REACTION_PLANT,
    REACTION_WATCHED_ENTRY,
    WIN_DEFUSED,
    WIN_DETONATED,
    WIN_ELIMINATION,
    WIN_REASONS,
    WIN_TIME,
)

if TYPE_CHECKING:
    from ...users.base import User


TEAM_TERRORISTS = SIDE_TERRORISTS
TEAM_COUNTER_TERRORISTS = SIDE_COUNTER_TERRORISTS
TEAM_INDEXES = SIDE_INDEXES

MIN_TEAM_SIZE = 2
MAX_TEAM_SIZE = 5
PICK_UP_WEAPON_ACTION_PREFIX = "pick_up_weapon_"
DONATE_WEAPON_ACTION_PREFIX = "donate_weapon_"
REFUND_ACTION_PREFIX = "refund_"
BUY_MENU_CATEGORY_ACTION_PREFIX = "buy_menu_category_"
BUY_MENU_DONATION_TARGET_PREFIX = "buy_menu_donation_target_"
BUY_MENU_SHORTCUT_PREFIX = "buy_shortcut_"
BUY_MENU_ROOT = "root"
BUY_MENU_GROUND = "ground"
BUY_MENU_REFUNDS = "refunds"
BUY_MENU_DONATION_TARGETS = "donation_targets"
BUY_MENU_CATEGORY = "category"
BUY_MENU_DONATION_CATEGORIES = "donation_categories"
BUY_MENU_DONATION_ITEMS = "donation_items"
BUY_MENU_SHORTCUT_DIGITS = tuple(str(number) for number in range(1, 10))
BUY_CATEGORY_LABEL_KEYS = {
    BUY_CATEGORY_EQUIPMENT: "breachpoint-buy-category-equipment",
    BUY_CATEGORY_PISTOLS: "breachpoint-buy-category-pistols",
    BUY_CATEGORY_MID_TIER: "breachpoint-buy-category-mid-tier",
    BUY_CATEGORY_RIFLES: "breachpoint-buy-category-rifles",
    BUY_CATEGORY_GRENADES: "breachpoint-buy-category-grenades",
}
COMBAT_MENU_ROOT = "root"
COMBAT_MENU_MOVE = "move"
COMBAT_MENU_ATTACK = "attack"
COMBAT_MENU_UTILITY = "utility"
COMBAT_MENU_UTILITY_TARGETS = "utility_targets"
COMBAT_MENU_ANGLE = "angle"
COMBAT_MENU_OBJECTIVE = "objective"
COMBAT_MENU_WEAPONS = "weapons"
COMBAT_MENU_LOOT = "loot"
COMBAT_MENU_VIEWS = frozenset(
    {
        COMBAT_MENU_ROOT,
        COMBAT_MENU_MOVE,
        COMBAT_MENU_ATTACK,
        COMBAT_MENU_UTILITY,
        COMBAT_MENU_UTILITY_TARGETS,
        COMBAT_MENU_ANGLE,
        COMBAT_MENU_OBJECTIVE,
        COMBAT_MENU_WEAPONS,
        COMBAT_MENU_LOOT,
    }
)
COMBAT_MENU_UTILITY_ACTION_PREFIX = "combat_menu_utility_"
COMBAT_MENU_ROOT_ACTION_IDS = (
    "combat_menu_move",
    "combat_menu_attack",
    "combat_menu_utility",
    "combat_menu_angle",
    "combat_menu_objective",
    "combat_menu_weapons",
    "combat_menu_loot",
)
COMBAT_MENU_SUMMARY_ACTION_ID = "combat_menu_summary"
COMBAT_MENU_ACTION_VIEWS = {
    "combat_menu_move": COMBAT_MENU_MOVE,
    "combat_menu_attack": COMBAT_MENU_ATTACK,
    "combat_menu_utility": COMBAT_MENU_UTILITY,
    "combat_menu_angle": COMBAT_MENU_ANGLE,
    "combat_menu_objective": COMBAT_MENU_OBJECTIVE,
    "combat_menu_weapons": COMBAT_MENU_WEAPONS,
    "combat_menu_loot": COMBAT_MENU_LOOT,
}
COMBAT_MENU_VIEW_OPENERS = {
    view: action_id for action_id, view in COMBAT_MENU_ACTION_VIEWS.items()
}
PURCHASE_KIND_WEAPON = "weapon"
PURCHASE_KIND_UTILITY = "utility"
PURCHASE_KIND_EQUIPMENT = "equipment"
PURCHASE_KIND_ARMOR = "armor"
PURCHASE_KINDS = frozenset(
    {
        PURCHASE_KIND_WEAPON,
        PURCHASE_KIND_UTILITY,
        PURCHASE_KIND_EQUIPMENT,
        PURCHASE_KIND_ARMOR,
    }
)
MOVEMENT_SEQUENCE_TAG = MOVEMENT_AUDIO_SEQUENCE_TAG
MOVEMENT_START_CALLBACK = "breachpoint-movement-start"
MOVEMENT_ARRIVE_CALLBACK = "breachpoint-movement-arrive"
UTILITY_SEQUENCE_TAG = UTILITY_AUDIO_SEQUENCE_TAG
UTILITY_START_CALLBACK = "breachpoint-utility-start"
UTILITY_FLIGHT_CALLBACK = "breachpoint-utility-flight"
UTILITY_BOUNCE_CALLBACK = "breachpoint-utility-bounce"
UTILITY_IMPACT_CALLBACK = "breachpoint-utility-impact"
UTILITY_RESOLVE_CALLBACK = "breachpoint-utility-resolve"
UTILITY_FINISH_CALLBACK = "breachpoint-utility-finish"
WEAPON_SEQUENCE_TAG = WEAPON_AUDIO_SEQUENCE_TAG
WEAPON_FIRE_CALLBACK = "breachpoint-weapon-fire"
WEAPON_RESOLVE_CALLBACK = "breachpoint-weapon-resolve"
ROUND_TRANSITION_SEQUENCE_TAG = "breachpoint-round-transition"
ROUND_TRANSITION_CALLBACK = "breachpoint-round-transition-finish"
ROUND_TRANSITION_SECONDS = 9
ROUND_TRANSITION_TICKS = ROUND_TRANSITION_SECONDS * TICKS_PER_SECOND
BUY_COUNTDOWN_SEQUENCE_TAG = "breachpoint-buy-countdown"
BUY_COUNTDOWN_BEEP_CALLBACK = "breachpoint-buy-countdown-beep"
BUY_COUNTDOWN_FINISH_CALLBACK = "breachpoint-buy-countdown-finish"
BUY_COUNTDOWN_SECONDS = 3
MATCH_RESULT_SEQUENCE_TAG = "breachpoint-match-result"
MATCH_RESULT_FINISH_CALLBACK = "breachpoint-match-result-finish"
MATCH_RESULT_DELAY_SECONDS = 9
MATCH_RESULT_DELAY_TICKS = MATCH_RESULT_DELAY_SECONDS * TICKS_PER_SECOND
MUSIC_ACTION_STOP_CALLBACK = "breachpoint-music-action-stop"
MUSIC_ACTION_DURATION_SECONDS = 10
MUSIC_ACTION_DURATION_TICKS = MUSIC_ACTION_DURATION_SECONDS * TICKS_PER_SECOND
BOMB_DETONATION_SEQUENCE_TAG = BOMB_DETONATION_AUDIO_SEQUENCE_TAG
BOMB_DETONATION_START_CALLBACK = "breachpoint-bomb-detonation-start"
BOMB_DETONATION_FINISH_CALLBACK = "breachpoint-bomb-detonation-finish"


@dataclass(frozen=True)
class AttackOutcome:
    """Resolved deterministic defenses for one successful shot."""

    rounds_fired: int
    rounds_on_target: int
    rounds_evaded: int
    health_damage: int
    armor_absorbed: int
    fully_evaded: bool


@dataclass(frozen=True)
class UtilityDamageOutcome:
    """Resolved health, armor, and evasion impact from damaging utility."""

    health_damage: int
    armor_absorbed: int
    evasion_mitigation: int


@dataclass(frozen=True)
class BuyMenuState:
    """Runtime-only navigation state for one player's buy menu."""

    view: str = BUY_MENU_ROOT
    category_id: str = ""
    recipient_id: str = ""


@dataclass(frozen=True)
class CombatMenuState:
    """Runtime-only navigation state for one player's combat menu."""

    view: str = COMBAT_MENU_ROOT
    utility_id: str = ""


@dataclass
class BreachPointOptions(GameOptions):
    """Host-configurable match structure."""

    match_format: str = option_field(
        MenuOption(
            default=DEFAULT_MATCH_FORMAT_ID,
            choices=list(MATCH_FORMATS),
            value_key="format",
            label="breachpoint-set-match-format",
            prompt="breachpoint-select-match-format",
            change_msg="breachpoint-option-changed-match-format",
            choice_labels={
                match_format_id: f"breachpoint-match-format-{match_format_id}"
                for match_format_id in MATCH_FORMATS
            },
        )
    )
    overtime_mode: str = option_field(
        MenuOption(
            default=DEFAULT_OVERTIME_MODE,
            choices=list(OVERTIME_MODES),
            value_key="mode",
            label="breachpoint-set-overtime-mode",
            prompt="breachpoint-select-overtime-mode",
            change_msg="breachpoint-option-changed-overtime-mode",
            choice_labels={
                OVERTIME_DRAW: "breachpoint-overtime-draw",
                OVERTIME_MR3: "breachpoint-overtime-mr3",
            },
        )
    )


@register_game
@dataclass
class BreachPointGame(BreachPointAudioMixin, Game):
    """A deterministic bomb-defusal game on a spatial tactical map."""

    _turn_action_templates: ClassVar[dict[tuple[type, str], ActionSet]] = {}
    visibility_first_action_sets: ClassVar[frozenset[str]] = frozenset({"turn"})

    players: list[BreachPointPlayer] = field(default_factory=list)
    options: BreachPointOptions = field(default_factory=BreachPointOptions)

    map_id: str = DEFAULT_MAP_ID
    phase: str = PHASE_COMBAT
    buy_ready_player_ids: list[str] = field(default_factory=list)
    buy_transactions: list[BuyTransaction] = field(default_factory=list)
    pending_weapon_donation: PendingWeaponDonation | None = None
    squad_loss_streaks: list[int] = field(
        default_factory=lambda: [
            STANDARD_ECONOMY.initial_loss_count for _ in TEAM_INDEXES
        ]
    )
    area_effects: list[AreaEffectState] = field(default_factory=list)
    ambient_stinger_due_ticks: dict[str, int] = field(default_factory=dict)
    dropped_weapons: list[DroppedWeapon] = field(default_factory=list)
    next_dropped_weapon_id: int = 1
    tactical_round: int = 1
    round_acted_player_ids: list[str] = field(default_factory=list)
    bomb_state: str = BOMB_CARRIED
    bomb_carrier_id: str = ""
    bomb_location_id: str = ""
    bomb_grid_x: int = -1
    bomb_grid_y: int = -1
    bomb_fuse_remaining: int = 0
    bomb_planted_tactical_round: int = 0
    planting_player_id: str = ""
    planting_location_id: str = ""
    defusing_player_id: str = ""
    defusing_location_id: str = ""
    reaction_window: ReactionWindow = field(default_factory=ReactionWindow)
    side_squad_indexes: list[int] = field(
        default_factory=lambda: [TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS]
    )
    overtime_period: int = 0
    overtime_round: int = 0
    overtime_start_scores: list[int] = field(default_factory=lambda: [0, 0])
    winning_team_index: int = -1
    last_round_win_reason: str = ""
    win_reason: str = ""
    round_recovery_player_id: str = ""
    round_recovery_drop_ids: list[int] = field(default_factory=list)
    pending_round_winner_side_index: int = -1
    pending_round_win_reason: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self._bot_coordinator = BreachPointBotCoordinator()
        self._gameplay_rng = random.Random()  # nosec B311 - non-security game state
        self._spatial_rng = random.Random()  # nosec B311 - cosmetic placement
        self._restored_finite_audio_sequence_ids: set[str] = set()
        self._buy_menu_views: dict[str, BuyMenuState] = {}
        self._combat_menu_views: dict[str, CombatMenuState] = {}

    def on_discard(self) -> None:
        """Release runtime-only tactical observations with the game instance."""

        self._bot_coordinator.clear()
        self._restored_finite_audio_sequence_ids.clear()
        self._buy_menu_views.clear()
        self._combat_menu_views.clear()
        super().on_discard()

    @classmethod
    def get_name(cls) -> str:
        return "Breach Point"

    @classmethod
    def get_type(cls) -> str:
        return "breachpoint"

    @classmethod
    def get_category(cls) -> str:
        return "board"

    @classmethod
    def get_min_players(cls) -> int:
        return MIN_TEAM_SIZE * len(TEAM_INDEXES)

    @classmethod
    def get_max_players(cls) -> int:
        return MAX_TEAM_SIZE * len(TEAM_INDEXES)

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    @property
    def rules(self) -> BreachPointRules:
        """Return the active rules profile."""

        return STANDARD_RULES

    @property
    def economy(self) -> EconomyProfile:
        """Return the active economy profile."""

        return STANDARD_ECONOMY

    @property
    def match_format(self) -> MatchFormat:
        """Return the selected validated match profile."""

        match_format = get_match_format(self.options.match_format)
        if match_format is None:
            match_format = get_match_format(DEFAULT_MATCH_FORMAT_ID)
        if match_format is None:
            raise RuntimeError("Breach Point has no registered match format")
        return match_format

    @property
    def tactical_map(self) -> TacticalMap:
        """Return the active validated map definition."""

        tactical_map = get_tactical_map(self.map_id)
        if tactical_map is None:
            raise RuntimeError(f"Unknown Breach Point tactical map: {self.map_id}")
        return tactical_map

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> BreachPointPlayer:
        return BreachPointPlayer(id=player_id, name=name, is_bot=is_bot)

    def supports_score_actions(self) -> bool:
        """Round wins are tracked for the two persistent squads."""

        return bool(self._team_manager.teams)

    def _configured_team_mode(self) -> str:
        """Derive the fixed two-side layout from the current even roster."""

        player_count = self.get_active_player_count()
        if player_count < self.get_min_players() or player_count % 2:
            return "individual"
        team_size = player_count // len(TEAM_INDEXES)
        return "v".join(str(team_size) for _ in TEAM_INDEXES)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        player_count = self.get_active_player_count()
        if player_count % len(TEAM_INDEXES):
            errors.append(
                (
                    "breachpoint-error-even-teams",
                    {"players": player_count},
                )
            )
        if get_match_format(self.options.match_format) is None:
            errors.append(
                (
                    "breachpoint-error-match-format",
                    {"format": self.options.match_format},
                )
            )
        if self.options.overtime_mode not in OVERTIME_MODES:
            errors.append(
                (
                    "breachpoint-error-overtime-mode",
                    {"mode": self.options.overtime_mode},
                )
            )
        if get_tactical_map(self.map_id) is None:
            errors.append(("breachpoint-error-map-unavailable", {"map": self.map_id}))
        return errors

    # ------------------------------------------------------------------
    # Team names and arrangement
    # ------------------------------------------------------------------

    @staticmethod
    def _team_name_key(team_index: int) -> str:
        if team_index == TEAM_TERRORISTS:
            return "breachpoint-team-terrorists"
        return "breachpoint-team-counter-terrorists"

    def _team_name(self, locale: str, team_index: int) -> str:
        return Localization.get(locale, self._team_name_key(team_index))

    def _squad_for_side(self, side_index: int) -> int:
        if side_index not in TEAM_INDEXES or len(self.side_squad_indexes) != 2:
            return -1
        return self.side_squad_indexes[side_index]

    def _side_for_squad(self, squad_index: int) -> int:
        try:
            return self.side_squad_indexes.index(squad_index)
        except ValueError:
            return -1

    def _squad_name(self, locale: str, squad_index: int) -> str:
        team = next(
            (team for team in self._team_manager.teams if team.index == squad_index),
            None,
        )
        if team:
            return self._team_manager.get_team_name(team, locale)
        return Localization.get(locale, "game-team-name", index=squad_index + 1)

    def _squad_score(self, squad_index: int) -> int:
        team = next(
            (team for team in self._team_manager.teams if team.index == squad_index),
            None,
        )
        return team.total_score if team else 0

    def _apply_current_sides(self, active_players: list[BreachPointPlayer]) -> None:
        for player in active_players:
            player.team_index = self._side_for_squad(player.squad_index)

    def _swap_sides(self) -> None:
        self.side_squad_indexes.reverse()
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        self._apply_current_sides(active_players)
        self.broadcast_l(
            "breachpoint-sides-swapped",
            buffer="game",
            terrorists=lambda locale: self._squad_name(
                locale, self._squad_for_side(TEAM_TERRORISTS)
            ),
            counter_terrorists=lambda locale: self._squad_name(
                locale, self._squad_for_side(TEAM_COUNTER_TERRORISTS)
            ),
        )

    def _team_arrangement_lines(self, locale: str) -> list[str]:
        lines: list[str] = []
        for team in sorted(self._team_manager.teams, key=lambda item: item.index):
            members = Localization.format_list_and(locale, team.members)
            lines.append(
                Localization.get(
                    locale,
                    "team-arrangement-line",
                    team=self._team_name(locale, team.index),
                    members=members,
                )
            )
        turn_order = [player.name for player in self._get_team_turn_players()]
        if turn_order:
            lines.append(
                Localization.get(
                    locale,
                    "team-arrangement-turn-order",
                    players=Localization.format_list_and(locale, turn_order),
                )
            )
        return lines

    def _get_team_turn_players(
        self, active_players: list[Player] | None = None
    ) -> list[Player]:
        """Balance the sides while guaranteeing that T takes first activation."""

        ordered = super()._get_team_turn_players(active_players)
        first_terrorist = next(
            (
                index
                for index, player in enumerate(ordered)
                if getattr(player, "team_index", -1) == TEAM_TERRORISTS
            ),
            None,
        )
        if first_terrorist is None:
            return ordered
        return ordered[first_terrorist:] + ordered[:first_terrorist]

    def _team_arrangement_member_label(self, player: Player, target_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target = self._find_team_arrangement_player(target_id)
        if not target:
            return target_id
        team = self._team_manager.get_team(target.name)
        team_index = team.index if team else TEAM_TERRORISTS
        selected_key = (
            "team-arrangement-selected"
            if target.id == self.team_arrangement_selected_player_id
            else "team-arrangement-not-selected"
        )
        return Localization.get(
            locale,
            "team-arrangement-member-option",
            player=target.name,
            team=self._team_name(locale, team_index),
            selected=Localization.get(locale, selected_key),
        )

    # ------------------------------------------------------------------
    # Action construction and ordering
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: Player) -> ActionSet:
        template_key = (type(self), self.map_id)
        template = type(self)._turn_action_templates.get(template_key)
        if template is None:
            template = self._create_turn_action_template()
            type(self)._turn_action_templates[template_key] = template
        action_set = template.copy_shared_actions()
        self._sync_donation_actions(action_set, player)
        self._sync_dropped_weapon_actions(action_set)
        self._sync_shoot_actions(action_set, player)
        self._apply_turn_action_order(action_set)
        return action_set

    def _create_turn_action_template(self) -> ActionSet:
        """Build immutable map/catalog actions shared by every player set."""

        action_set = ActionSet(name="turn")
        self._add_reaction_actions(action_set)
        self._add_buy_actions(action_set)
        self._add_combat_menu_actions(action_set)
        self._add_objective_actions(action_set)
        self._add_weapon_actions(action_set)
        self._sync_hold_angle_actions(action_set)
        self._sync_utility_actions(action_set)
        for node in self.tactical_map.nodes:
            action_set.add(
                Action(
                    id=f"move_{node.id}",
                    label="",
                    handler="_action_move",
                    is_enabled="_is_move_enabled",
                    is_hidden="_is_move_hidden",
                    get_label="_get_move_label",
                    show_in_actions_menu=False,
                )
            )
        self._add_end_activation_action(action_set)
        self._apply_turn_action_order(action_set)
        return action_set

    def _add_combat_menu_actions(self, action_set: ActionSet) -> None:
        """Add stable navigation rows for the nested combat menu."""

        for action_id in COMBAT_MENU_ROOT_ACTION_IDS:
            action_set.add(
                Action(
                    id=action_id,
                    label="",
                    handler="_action_open_combat_menu",
                    is_enabled="_is_combat_menu_navigation_enabled",
                    is_hidden="_is_combat_root_action_hidden",
                    get_label="_get_combat_menu_label",
                    show_in_actions_menu=False,
                )
            )
        for action_id, get_label, hidden_callback, enabled_callback in (
            (
                COMBAT_MENU_SUMMARY_ACTION_ID,
                "_get_combat_summary_label",
                "_is_combat_summary_hidden",
                "_is_combat_menu_info_enabled",
            ),
            (
                "combat_menu_location",
                "_get_combat_location_label",
                "_is_combat_location_hidden",
                "_is_combat_menu_info_enabled",
            ),
            (
                "combat_menu_empty",
                "_get_combat_empty_label",
                "_is_combat_empty_hidden",
                "_is_combat_menu_info_enabled",
            ),
            (
                "combat_menu_back",
                "_get_combat_menu_back_label",
                "_is_combat_menu_back_hidden",
                "_is_combat_menu_navigation_enabled",
            ),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label="",
                    handler=(
                        "_action_combat_menu_back"
                        if action_id == "combat_menu_back"
                        else "_action_combat_menu_noop"
                    ),
                    is_enabled=enabled_callback,
                    is_hidden=hidden_callback,
                    get_label=get_label,
                    show_in_actions_menu=False,
                )
            )
        for utility in get_utilities():
            action_set.add(
                Action(
                    id=f"{COMBAT_MENU_UTILITY_ACTION_PREFIX}{utility.id}",
                    label="",
                    handler="_action_open_combat_utility_targets",
                    is_enabled="_is_combat_utility_choice_enabled",
                    is_hidden="_is_combat_utility_choice_hidden",
                    get_label="_get_combat_utility_choice_label",
                    show_in_actions_menu=False,
                )
            )

    def _add_reaction_actions(self, action_set: ActionSet) -> None:
        action_set.add(
            Action(
                id="reaction_shoot",
                label="",
                handler="_action_reaction_shoot",
                is_enabled="_is_reaction_shoot_enabled",
                is_hidden="_is_reaction_action_hidden",
                get_label="_get_reaction_shoot_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="reaction_pass",
                label="",
                handler="_action_reaction_pass",
                is_enabled="_is_reaction_pass_enabled",
                is_hidden="_is_reaction_action_hidden",
                get_label="_get_reaction_pass_label",
                show_in_actions_menu=False,
            )
        )

    def _add_buy_actions(self, action_set: ActionSet) -> None:
        self._add_buy_menu_actions(action_set)
        action_set.add(
            Action(
                id="accept_weapon_donation",
                label="",
                handler="_action_accept_weapon_donation",
                is_enabled="_is_weapon_donation_response_enabled",
                is_hidden="_is_weapon_donation_response_hidden",
                get_label="_get_weapon_donation_response_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="decline_weapon_donation",
                label="",
                handler="_action_decline_weapon_donation",
                is_enabled="_is_weapon_donation_response_enabled",
                is_hidden="_is_weapon_donation_response_hidden",
                get_label="_get_weapon_donation_response_label",
                show_in_actions_menu=False,
            )
        )
        for weapon in get_purchasable_weapons(
            TEAM_TERRORISTS
        ) + get_purchasable_weapons(TEAM_COUNTER_TERRORISTS):
            if action_set.get_action(f"buy_weapon_{weapon.id}"):
                continue
            action_set.add(
                Action(
                    id=f"buy_weapon_{weapon.id}",
                    label="",
                    handler="_action_buy_weapon",
                    is_enabled="_is_buy_weapon_enabled",
                    is_hidden="_is_buy_weapon_hidden",
                    get_label="_get_buy_weapon_label",
                    get_sound="_get_buy_item_hover_sound",
                    show_in_actions_menu=False,
                )
            )
        for utility in get_utilities():
            action_set.add(
                Action(
                    id=f"buy_utility_{utility.id}",
                    label="",
                    handler="_action_buy_utility",
                    is_enabled="_is_buy_utility_enabled",
                    is_hidden="_is_buy_utility_hidden",
                    get_label="_get_buy_utility_label",
                    get_sound="_get_buy_item_hover_sound",
                    show_in_actions_menu=False,
                )
            )
        for equipment in get_purchasable_equipment(
            TEAM_TERRORISTS
        ) + get_purchasable_equipment(TEAM_COUNTER_TERRORISTS):
            if action_set.get_action(f"buy_equipment_{equipment.id}"):
                continue
            action_set.add(
                Action(
                    id=f"buy_equipment_{equipment.id}",
                    label="",
                    handler="_action_buy_equipment",
                    is_enabled="_is_buy_equipment_enabled",
                    is_hidden="_is_buy_equipment_hidden",
                    get_label="_get_buy_equipment_label",
                    get_sound="_get_buy_item_hover_sound",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="buy_armor",
                label="",
                handler="_action_buy_armor",
                is_enabled="_is_buy_armor_enabled",
                is_hidden="_is_buy_armor_hidden",
                get_label="_get_buy_armor_label",
                get_sound="_get_buy_item_hover_sound",
                show_in_actions_menu=False,
            )
        )
        refund_item_ids = {
            PURCHASE_KIND_WEAPON: tuple(
                dict.fromkeys(
                    weapon.id
                    for side in TEAM_INDEXES
                    for weapon in get_purchasable_weapons(side)
                )
            ),
            PURCHASE_KIND_UTILITY: tuple(
                utility.id for utility in get_utilities()
            ),
            PURCHASE_KIND_EQUIPMENT: tuple(
                dict.fromkeys(
                    equipment.id
                    for side in TEAM_INDEXES
                    for equipment in get_purchasable_equipment(side)
                )
            ),
        }
        for item_kind, item_ids in refund_item_ids.items():
            for item_id in item_ids:
                action_set.add(
                    Action(
                        id=f"{REFUND_ACTION_PREFIX}{item_kind}_{item_id}",
                        label="",
                        handler="_action_refund_purchase",
                        is_enabled="_is_refund_purchase_enabled",
                        is_hidden="_is_refund_purchase_hidden",
                        get_label="_get_refund_purchase_label",
                        show_in_actions_menu=False,
                    )
                )
        action_set.add(
            Action(
                id=f"{REFUND_ACTION_PREFIX}{PURCHASE_KIND_ARMOR}",
                label="",
                handler="_action_refund_purchase",
                is_enabled="_is_refund_purchase_enabled",
                is_hidden="_is_refund_purchase_hidden",
                get_label="_get_refund_purchase_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="finish_buy",
                label="",
                handler="_action_finish_buy",
                is_enabled="_is_finish_buy_enabled",
                is_hidden="_is_finish_buy_hidden",
                get_label="_get_finish_buy_label",
                show_in_actions_menu=False,
            )
        )

    def _add_buy_menu_actions(self, action_set: ActionSet) -> None:
        """Add stable navigation rows for the nested CS-style buy menu."""

        definitions = (
            (
                "buy_menu_summary",
                "_action_show_buy_summary",
                "_is_buy_summary_enabled",
                "_is_buy_summary_hidden",
                "_get_buy_summary_label",
            ),
            (
                "buy_menu_teammates",
                "_action_show_teammate_buy_info",
                "_is_buy_navigation_enabled",
                "_is_buy_root_action_hidden",
                "_get_buy_teammates_label",
            ),
            (
                "buy_menu_ground_weapons",
                "_action_open_ground_weapons",
                "_is_ground_weapon_menu_enabled",
                "_is_buy_root_action_hidden",
                "_get_buy_ground_weapons_label",
            ),
            (
                "buy_menu_refunds",
                "_action_open_refunds",
                "_is_refund_menu_enabled",
                "_is_buy_root_action_hidden",
                "_get_buy_refunds_label",
            ),
            (
                "buy_menu_donation",
                "_action_open_donation",
                "_is_donation_menu_enabled",
                "_is_buy_root_action_hidden",
                "_get_buy_donation_label",
            ),
            (
                "buy_menu_empty_refunds",
                "_action_buy_menu_noop",
                "_is_empty_refund_row_enabled",
                "_is_empty_refund_row_hidden",
                "_get_empty_refund_row_label",
            ),
            (
                "buy_menu_waiting",
                "_action_buy_menu_noop",
                "_is_donation_waiting_enabled",
                "_is_donation_waiting_hidden",
                "_get_donation_waiting_label",
            ),
            (
                "buy_menu_back",
                "_action_buy_menu_back",
                "_is_buy_navigation_enabled",
                "_is_buy_menu_back_hidden",
                "_get_buy_menu_back_label",
            ),
        )
        for action_id, handler, enabled, hidden, get_label in definitions:
            action_set.add(
                Action(
                    id=action_id,
                    label="",
                    handler=handler,
                    is_enabled=enabled,
                    is_hidden=hidden,
                    get_label=get_label,
                    show_in_actions_menu=False,
                )
            )
        for category_id in BUY_CATEGORIES:
            action_set.add(
                Action(
                    id=f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{category_id}",
                    label="",
                    handler="_action_open_buy_category",
                    is_enabled="_is_buy_category_enabled",
                    is_hidden="_is_buy_category_hidden",
                    get_label="_get_buy_category_label",
                    show_in_actions_menu=False,
                )
            )
        for digit in BUY_MENU_SHORTCUT_DIGITS:
            action_set.add(
                Action(
                    id=f"{BUY_MENU_SHORTCUT_PREFIX}{digit}",
                    label="",
                    handler="_action_buy_shortcut",
                    is_enabled="_is_buy_shortcut_enabled",
                    is_hidden="_is_buy_shortcut_hidden",
                    show_in_actions_menu=False,
                )
            )

    def _sync_donation_actions(
        self,
        action_set: ActionSet,
        player: Player,
    ) -> bool:
        """Expose side-legal firearm donations to every active teammate."""

        donor = self._breach_player(player)
        teammates = self._eligible_donation_recipients(donor) if donor else []
        weapons = get_purchasable_weapons(donor.team_index) if donor else []
        desired_ids = [
            *(
                f"{BUY_MENU_DONATION_TARGET_PREFIX}{teammate.id}"
                for teammate in teammates
            ),
            *(
                self._donate_weapon_action_id(weapon, teammate)
                for teammate in teammates
                for weapon in weapons
            ),
        ]
        if not self._dynamic_action_ids_changed(
            action_set,
            (BUY_MENU_DONATION_TARGET_PREFIX, DONATE_WEAPON_ACTION_PREFIX),
            desired_ids,
        ):
            return False

        action_set.remove_by_prefix(DONATE_WEAPON_ACTION_PREFIX)
        action_set.remove_by_prefix(BUY_MENU_DONATION_TARGET_PREFIX)
        for teammate in teammates:
            action_set.add(
                Action(
                    id=f"{BUY_MENU_DONATION_TARGET_PREFIX}{teammate.id}",
                    label="",
                    handler="_action_open_donation_target",
                    is_enabled="_is_buy_navigation_enabled",
                    is_hidden="_is_donation_target_hidden",
                    get_label="_get_donation_target_label",
                    show_in_actions_menu=False,
                )
            )
        for teammate in teammates:
            for weapon in weapons:
                action_set.add(
                    Action(
                        id=self._donate_weapon_action_id(weapon, teammate),
                        label="",
                        handler="_action_donate_weapon",
                        is_enabled="_is_donate_weapon_enabled",
                        is_hidden="_is_donate_weapon_hidden",
                        get_label="_get_donate_weapon_label",
                        get_sound="_get_buy_item_hover_sound",
                        show_in_actions_menu=False,
                    )
                )
        return True

    def _add_objective_actions(self, action_set: ActionSet) -> None:
        action_set.add(
            Action(
                id="plant",
                label="",
                handler="_action_plant",
                is_enabled="_is_plant_enabled",
                is_hidden="_is_plant_hidden",
                get_label="_get_objective_action_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="defuse",
                label="",
                handler="_action_defuse",
                is_enabled="_is_defuse_enabled",
                is_hidden="_is_defuse_hidden",
                get_label="_get_objective_action_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pick_up_bomb",
                label="",
                handler="_action_pick_up_bomb",
                is_enabled="_is_pick_up_bomb_enabled",
                is_hidden="_is_pick_up_bomb_hidden",
                get_label="_get_objective_action_label",
                show_in_actions_menu=False,
            )
        )

    def _add_weapon_actions(self, action_set: ActionSet) -> None:
        for action_id in ("equip_primary", "equip_sidearm"):
            action_set.add(
                Action(
                    id=action_id,
                    label="",
                    handler="_action_equip_weapon",
                    is_enabled="_is_equip_weapon_enabled",
                    is_hidden="_is_equip_weapon_hidden",
                    get_label="_get_equip_weapon_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="reload",
                label="",
                handler="_action_reload",
                is_enabled="_is_reload_enabled",
                is_hidden="_is_reload_hidden",
                get_label="_get_reload_label",
                show_in_actions_menu=False,
            )
        )

    @staticmethod
    def _dynamic_action_ids_changed(
        action_set: ActionSet,
        prefixes: tuple[str, ...],
        desired_ids: list[str],
    ) -> bool:
        """Whether a prefixed dynamic action collection needs rebuilding."""

        current_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith(prefixes)
        ]
        return current_ids != desired_ids

    def _sync_dropped_weapon_actions(self, action_set: ActionSet) -> bool:
        """Keep stable pickup actions aligned with authoritative ground state."""

        desired_ids = [
            self._dropped_weapon_action_id(dropped_weapon)
            for dropped_weapon in self.dropped_weapons
        ]
        if not self._dynamic_action_ids_changed(
            action_set,
            (PICK_UP_WEAPON_ACTION_PREFIX,),
            desired_ids,
        ):
            return False

        action_set.remove_by_prefix(PICK_UP_WEAPON_ACTION_PREFIX)
        for dropped_weapon in self.dropped_weapons:
            action_set.add(
                Action(
                    id=self._dropped_weapon_action_id(dropped_weapon),
                    label="",
                    handler="_action_pick_up_weapon",
                    is_enabled="_is_pick_up_weapon_enabled",
                    is_hidden="_is_pick_up_weapon_hidden",
                    get_label="_get_pick_up_weapon_label",
                    show_in_actions_menu=False,
                )
            )
        return True

    def _sync_hold_angle_actions(self, action_set: ActionSet) -> None:
        action_set.remove_by_prefix("hold_angle_")
        for node in self.tactical_map.nodes:
            action_set.add(
                Action(
                    id=f"hold_angle_{node.id}",
                    label="",
                    handler="_action_hold_angle",
                    is_enabled="_is_hold_angle_enabled",
                    is_hidden="_is_hold_angle_hidden",
                    get_label="_get_hold_angle_label",
                    show_in_actions_menu=False,
                )
            )

    def _sync_utility_actions(self, action_set: ActionSet) -> None:
        action_set.remove_by_prefix("throw_")
        for utility in get_utilities():
            for node in self.tactical_map.nodes:
                action_set.add(
                    Action(
                        id=f"throw_{utility.id}_{node.id}",
                        label="",
                        handler="_action_throw_utility",
                        is_enabled="_is_throw_utility_enabled",
                        is_hidden="_is_throw_utility_hidden",
                        get_label="_get_throw_utility_label",
                        show_in_actions_menu=False,
                    )
                )

    def _add_end_activation_action(self, action_set: ActionSet) -> None:
        for action in (
            Action(
                id="end_turn",
                label="",
                handler="_action_end_turn",
                is_enabled="_is_end_turn_enabled",
                is_hidden="_is_end_turn_hidden",
                get_label="_get_end_turn_label",
                show_in_actions_menu=False,
            ),
            Action(
                id="context_finish_or_end",
                label="",
                handler="_action_context_finish_or_end",
                is_enabled="_is_context_finish_or_end_enabled",
                is_hidden="_is_context_hotkey_hidden",
                show_in_actions_menu=False,
            ),
            Action(
                id="context_menu_back",
                label="",
                handler="_action_context_menu_back",
                is_enabled="_is_context_menu_back_enabled",
                is_hidden="_is_context_hotkey_hidden",
                show_in_actions_menu=False,
            ),
        ):
            action_set.add(action)

    def _sync_shoot_actions(self, action_set: ActionSet, player: Player) -> bool:
        targets = [
            target for target in self.get_active_players() if target.id != player.id
        ]
        desired_ids = [f"shoot_{target.id}" for target in targets]
        if not self._dynamic_action_ids_changed(
            action_set,
            ("shoot_",),
            desired_ids,
        ):
            return False

        action_set.remove_by_prefix("shoot_")
        for target in targets:
            action_set.add(
                Action(
                    id=f"shoot_{target.id}",
                    label="",
                    handler="_action_shoot",
                    is_enabled="_is_shoot_enabled",
                    is_hidden="_is_shoot_hidden",
                    get_label="_get_shoot_label",
                    show_in_actions_menu=False,
                )
            )
        return True

    @staticmethod
    def _apply_turn_action_order(action_set: ActionSet) -> None:
        reaction_ids = [
            action_id
            for action_id in (
                "accept_weapon_donation",
                "decline_weapon_donation",
                "reaction_shoot",
                "reaction_pass",
            )
            if action_set.get_action(action_id)
        ]
        buy_navigation_ids = [
            action_id
            for action_id in (
                "buy_menu_summary",
                "buy_menu_teammates",
                *(
                    f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{category_id}"
                    for category_id in BUY_CATEGORIES
                ),
            )
            if action_set.get_action(action_id)
        ]
        buy_item_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_weapon_")
        ]
        buy_item_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_utility_")
        )
        buy_item_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_equipment_")
        )
        buy_item_ids.extend(
            action_id
            for action_id in ("buy_armor",)
            if action_set.get_action(action_id)
        )
        combat_root_ids = [
            action_id
            for action_id in (
                COMBAT_MENU_SUMMARY_ACTION_ID,
                *COMBAT_MENU_ROOT_ACTION_IDS,
            )
            if action_set.get_action(action_id)
        ]
        combat_utility_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith(COMBAT_MENU_UTILITY_ACTION_PREFIX)
        ]
        buy_item_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith(REFUND_ACTION_PREFIX)
        )
        buy_item_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith(BUY_MENU_DONATION_TARGET_PREFIX)
        )
        buy_item_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith(DONATE_WEAPON_ACTION_PREFIX)
        )
        buy_item_ids.extend(
            action_id
            for action_id in (
                "buy_menu_empty_refunds",
                "buy_menu_waiting",
                "buy_menu_ground_weapons",
                "buy_menu_refunds",
                "buy_menu_donation",
                "finish_buy",
            )
            if action_set.get_action(action_id)
        )
        objective_ids = [
            "plant",
            "defuse",
            "pick_up_bomb",
        ]
        weapon_ids = [
            action_id
            for action_id in ("equip_primary", "equip_sidearm", "reload")
            if action_set.get_action(action_id)
        ]
        pickup_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith(PICK_UP_WEAPON_ACTION_PREFIX)
        ]
        hold_angle_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("hold_angle_")
        ]
        shoot_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("shoot_")
        ]
        move_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("move_")
        ]
        utility_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("throw_")
        ]
        action_set._order = (
            reaction_ids
            + buy_navigation_ids
            + buy_item_ids
            + combat_root_ids
            + [
                action_id
                for action_id in ("combat_menu_location",)
                if action_set.get_action(action_id)
            ]
            + [
                action_id
                for action_id in objective_ids
                if action_set.get_action(action_id)
            ]
        )
        action_set._order.extend(pickup_ids)
        action_set._order.extend(weapon_ids)
        action_set._order.extend(hold_angle_ids)
        action_set._order.extend(shoot_ids)
        action_set._order.extend(combat_utility_ids)
        action_set._order.extend(utility_ids)
        action_set._order.extend(move_ids)
        for action_id in (
            "combat_menu_empty",
            "buy_menu_back",
            "combat_menu_back",
        ):
            if action_set.get_action(action_id):
                action_set._order.append(action_id)
        if action_set.get_action("end_turn"):
            action_set._order.append("end_turn")

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        for (
            action_id,
            label_key,
            handler,
            enabled_callback,
            hidden_callback,
            include_spectators,
        ) in (
            (
                "read_vitals",
                "breachpoint-action-read-vitals",
                "_action_read_vitals",
                "_is_read_vitals_enabled",
                "_is_read_vitals_hidden",
                False,
            ),
            (
                "read_position",
                "breachpoint-action-read-position",
                "_action_read_position",
                "_is_read_position_enabled",
                "_is_read_position_hidden",
                False,
            ),
            (
                "read_map",
                "breachpoint-action-read-map",
                "_action_read_map",
                "_is_read_map_enabled",
                "_is_read_map_hidden",
                True,
            ),
            (
                "read_teammates",
                "breachpoint-action-read-teammates",
                "_action_read_teammates",
                "_is_read_teammates_enabled",
                "_is_read_teammates_hidden",
                False,
            ),
            (
                "read_enemies",
                "breachpoint-action-read-enemies",
                "_action_read_enemies",
                "_is_read_enemies_enabled",
                "_is_read_enemies_hidden",
                False,
            ),
            (
                "read_bomb",
                "breachpoint-action-read-bomb",
                "_action_read_bomb",
                "_is_read_bomb_enabled",
                "_is_read_bomb_hidden",
                True,
            ),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label_key),
                    handler=handler,
                    is_enabled=enabled_callback,
                    is_hidden=hidden_callback,
                    include_spectators=include_spectators,
                )
            )
        self._apply_standard_action_order(action_set, user)
        return action_set

    def _apply_standard_action_order(
        self, action_set: ActionSet, user: User | None
    ) -> None:
        custom_ids = [
            "read_vitals",
            "read_position",
            "read_map",
            "read_teammates",
            "read_enemies",
            "read_bomb",
        ]
        action_set._order = [
            action_id for action_id in action_set._order if action_id not in custom_ids
        ] + [action_id for action_id in custom_ids if action_set.get_action(action_id)]
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                custom_ids
                + [
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )

    def before_menu_build(self, player: Player) -> None:
        turn_set = self.get_action_set(player, "turn")
        if turn_set:
            sync_results = (
                self._sync_shoot_actions(turn_set, player),
                self._sync_dropped_weapon_actions(turn_set),
                self._sync_donation_actions(turn_set, player),
            )
            if any(sync_results):
                self._apply_turn_action_order(turn_set)
        standard_set = self.get_action_set(player, "standard")
        if standard_set:
            self._apply_standard_action_order(standard_set, self.get_user(player))

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "h",
            Localization.get("en", "breachpoint-action-read-vitals"),
            ["read_vitals"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "m",
            Localization.get("en", "breachpoint-action-read-map"),
            ["read_map"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "p",
            Localization.get("en", "breachpoint-action-read-position"),
            ["read_position"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "o",
            Localization.get("en", "breachpoint-action-read-bomb"),
            ["read_bomb"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "v",
            Localization.get("en", "breachpoint-action-read-teammates"),
            ["read_teammates"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "w",
            Localization.get("en", "breachpoint-action-read-enemies"),
            ["read_enemies"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "e",
            Localization.get("en", "breachpoint-keybind-finish-or-end"),
            ["context_finish_or_end"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "x",
            Localization.get("en", "breachpoint-keybind-menu-back"),
            ["context_menu_back"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "r",
            Localization.get("en", "breachpoint-action-reload-keybind"),
            ["reload"],
            state=KeybindState.ACTIVE,
        )
        for digit in BUY_MENU_SHORTCUT_DIGITS:
            self.define_keybind(
                digit,
                Localization.get(
                    "en",
                    "breachpoint-keybind-buy-shortcut",
                    number=digit,
                ),
                [f"{BUY_MENU_SHORTCUT_PREFIX}{digit}"],
                state=KeybindState.ACTIVE,
            )

    # ------------------------------------------------------------------
    # Lifecycle and restoration
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        team_mode = self._configured_team_mode()
        self._setup_team_manager_for_start(team_mode, active_players)
        for player in active_players:
            player.squad_index = player.team_index
        self._team_manager.reset_all_scores()
        self.side_squad_indexes = [TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS]

        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        self.round = 1
        self.tactical_round = 1
        self.overtime_period = 0
        self.overtime_round = 0
        self.overtime_start_scores = [0, 0]
        self.winning_team_index = -1
        self.last_round_win_reason = ""
        self.win_reason = ""
        self._clear_round_recovery()
        self._bot_coordinator.clear()
        self.ambient_stinger_due_ticks = {}
        self._reset_dropped_weapons()
        self._apply_current_sides(active_players)
        self._reset_economy(self.economy.starting_cash, active_players)
        self._prepare_combat_round(active_players)
        self._start_map_ambience()
        self._play_music_cue(
            MUSIC_MATCH_START_ASSET,
            looping=True,
            priority=30,
        )
        self._announce_match_start()
        self._announce_combat_round_start()
        self._start_buy_phase()

    def _prepare_combat_round(
        self, active_players: list[BreachPointPlayer] | None = None
    ) -> None:
        self._stop_all_utility_flight_audio()
        self.cancel_sequences_by_tag(MOVEMENT_SEQUENCE_TAG)
        self.cancel_sequences_by_tag(UTILITY_SEQUENCE_TAG)
        self.cancel_sequences_by_tag(WEAPON_SEQUENCE_TAG)
        active_players = active_players or [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        self.tactical_round = 1
        self.round_acted_player_ids = []
        self.bomb_state = BOMB_CARRIED
        self.bomb_location_id = ""
        self._clear_bomb_grid_point()
        self.bomb_fuse_remaining = 0
        self.bomb_planted_tactical_round = 0
        self.planting_player_id = ""
        self.planting_location_id = ""
        self.defusing_player_id = ""
        self.defusing_location_id = ""
        self.reaction_window = ReactionWindow()
        self._clear_round_recovery()
        self.buy_transactions = []
        self._buy_menu_views.clear()
        self._combat_menu_views.clear()
        for effect in self.area_effects:
            if effect.effect == UTILITY_EFFECT_FIRE:
                self._stop_fire_audio(effect.node_id)
        self.area_effects = []
        self._clear_dropped_weapons()

        for player in active_players:
            if player.eliminated:
                player.sidearm_weapon_id = ""
                player.primary_weapon_id = ""
                player.armor = 0
                player.utility_counts = {}
                player.equipment_counts = {}
            primary = self._primary_weapon(player)
            if not primary:
                player.primary_weapon_id = ""
            sidearm = self._sidearm(player)
            if not sidearm:
                sidearm = get_default_sidearm(player.team_index)
                player.sidearm_weapon_id = sidearm.id if sidearm else ""
            player.equipped_weapon_id = (
                primary.id if primary else sidearm.id if sidearm else ""
            )
            self._refill_owned_weapon_ammunition(player)
            player.position_id = self._spawn_for_team(player.team_index)
            player.grid_x = -1
            player.grid_y = -1
            player.facing_degrees = self._spawn_heading_for_team(player.team_index)
            player.health = self.rules.max_health
            player.eliminated = False
            player.action_points = 0
            player.shots_fired_this_activation = 0
            player.weapon_shots_fired_this_activation = {}
            player.weapon_target_ids_this_activation = {}
            player.guard_points = 0
            self._reset_stationary_evasion(player)
            player.flash_penalty = 0
            player.held_angle_node_id = ""
            player.held_angle_origin_id = ""
            self._normalize_utility_counts(player)
            self._normalize_equipment_counts(player)

        self._normalize_spatial_positions(active_players)
        self._sync_all_listener_environment_audio()

        turn_players = self._get_team_turn_players(active_players)
        self.set_turn_players(turn_players)
        terrorists = tuple(
            player
            for player in turn_players
            if isinstance(player, BreachPointPlayer)
            and player.team_index == TEAM_TERRORISTS
        )
        carrier = self._gameplay_rng.choice(terrorists) if terrorists else None
        self.bomb_carrier_id = carrier.id if carrier else ""
        self._bot_coordinator.begin_combat_round(self)

    def _reset_economy(
        self,
        cash: int,
        active_players: list[BreachPointPlayer] | None = None,
    ) -> None:
        """Reset cash and equipment at a regulation or overtime side boundary."""

        players = active_players or [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        starting_cash = max(0, min(self.economy.maximum_cash, cash))
        self.squad_loss_streaks = [
            self.economy.initial_loss_count for _ in TEAM_INDEXES
        ]
        for player in players:
            player.cash = starting_cash
            sidearm = get_default_sidearm(player.team_index)
            player.sidearm_weapon_id = sidearm.id if sidearm else ""
            player.primary_weapon_id = ""
            player.armor = 0
            player.utility_counts = {}
            player.equipment_counts = {}
            player.guard_points = 0
            player.shots_fired_this_activation = 0
            player.weapon_shots_fired_this_activation = {}
            player.weapon_target_ids_this_activation = {}
            self._reset_stationary_evasion(player)
            player.flash_penalty = 0
            player.held_angle_node_id = ""
            player.held_angle_origin_id = ""
            player.equipped_weapon_id = sidearm.id if sidearm else ""
            self._refill_owned_weapon_ammunition(player)

    def _start_buy_phase(self) -> None:
        """Begin private sequential purchases for the new combat round."""

        self.phase = PHASE_BUY
        self.buy_ready_player_ids = []
        self.buy_transactions = []
        self.pending_weapon_donation = None
        self._buy_menu_views.clear()
        self._combat_menu_views.clear()
        buyer = next(
            (
                player
                for player in self.turn_players
                if isinstance(player, BreachPointPlayer) and not player.eliminated
            ),
            None,
        )
        if not buyer:
            return
        self.current_player = buyer
        self.broadcast_l(
            "breachpoint-buy-phase-start",
            buffer="game",
            round=self.round,
        )
        self._start_buy_turn(buyer)
        self.refresh_menus()
        BotHelper.jolt_bot(buyer)

    def _start_buy_turn(self, player: BreachPointPlayer) -> None:
        self._buy_menu_views[player.id] = BuyMenuState()
        self._focus_buy_menu_first(player)
        self._play_turn_notification(player)
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "breachpoint-buy-turn",
            buffer="game",
            cash=player.cash,
        )

    def _play_turn_notification(self, player: BreachPointPlayer) -> None:
        """Play the optional local cue whenever this player owes a new choice."""

        if player.is_bot:
            return
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound(TURN_NOTIFICATION_ASSET, buffer="game")

    def _start_combat_phase(self) -> None:
        """Leave preparation and start the first tactical activation."""

        self.phase = PHASE_COMBAT
        self.buy_transactions = []
        self.pending_weapon_donation = None
        self._play_action_start_music()
        self.start_sequence(
            MUSIC_ACTION_STOP_SEQUENCE_TAG,
            [
                SequenceBeat.pause(MUSIC_ACTION_DURATION_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            MUSIC_ACTION_STOP_CALLBACK,
                        )
                    ]
                ),
            ],
            tag=MUSIC_ACTION_STOP_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_NONE,
            pause_bots=False,
        )
        self.buy_ready_player_ids = []
        self.round_acted_player_ids = []
        first_player = next(
            (
                player
                for player in self.turn_players
                if isinstance(player, BreachPointPlayer) and not player.eliminated
            ),
            None,
        )
        if not first_player:
            return
        self.current_player = first_player
        self._announce_tactical_round_start()
        self._start_activation(first_player)
        self.refresh_menus()
        BotHelper.jolt_bot(first_player)

    def _queue_combat_start_countdown(self) -> None:
        """Lock preparation for three audible beats before combat begins."""

        if self.has_active_sequence(tag=BUY_COUNTDOWN_SEQUENCE_TAG):
            return
        self.broadcast_l(
            "breachpoint-buy-countdown-start",
            buffer="game",
        )
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(BUY_COUNTDOWN_BEEP_CALLBACK)
                ],
                delay_after_ticks=TICKS_PER_SECOND,
            )
            for _ in range(BUY_COUNTDOWN_SECONDS)
        ]
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(BUY_COUNTDOWN_FINISH_CALLBACK)
                ]
            )
        )
        self.start_sequence(
            BUY_COUNTDOWN_SEQUENCE_TAG,
            beats,
            tag=BUY_COUNTDOWN_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"seconds": BUY_COUNTDOWN_SECONDS},
        )
        self.refresh_menus()

    def rebuild_runtime_state(self) -> None:
        super().rebuild_runtime_state()
        self._bot_coordinator.clear()
        if get_tactical_map(self.map_id) is None:
            raise ValueError(f"Unknown Breach Point tactical map: {self.map_id}")
        if get_match_format(self.options.match_format) is None:
            self.options.match_format = DEFAULT_MATCH_FORMAT_ID
        if self.options.overtime_mode not in OVERTIME_MODES:
            self.options.overtime_mode = DEFAULT_OVERTIME_MODE

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        valid_player_ids = {player.id for player in active_players}
        previous_current_id = self.current_player.id if self.current_player else ""
        self.turn_player_ids = list(
            dict.fromkeys(
                player_id
                for player_id in self.turn_player_ids
                if player_id in valid_player_ids
            )
        )
        self.turn_player_ids.extend(
            player.id
            for player in active_players
            if player.id not in self.turn_player_ids
        )
        self.round_acted_player_ids = list(
            dict.fromkeys(
                player_id
                for player_id in self.round_acted_player_ids
                if player_id in valid_player_ids
            )
        )
        self.buy_ready_player_ids = list(
            dict.fromkeys(
                player_id
                for player_id in self.buy_ready_player_ids
                if player_id in valid_player_ids
            )
        )
        if previous_current_id in self.turn_player_ids:
            self.turn_index = self.turn_player_ids.index(previous_current_id)
        elif self.turn_player_ids:
            self.turn_index %= len(self.turn_player_ids)
        else:
            self.turn_index = 0

        active_names = [player.name for player in active_players]
        expected_team_mode = self._configured_team_mode()
        if expected_team_mode != "individual" and (
            self._team_manager.team_mode != expected_team_mode
            or not self._team_manager.validate_assignments(active_names)
        ):
            self._team_manager.team_mode = expected_team_mode
            self._team_manager.setup_teams(active_names)
        else:
            self._team_manager.rebuild_player_index()
        for team in self._team_manager.teams:
            team.total_score = max(0, team.total_score)
            team.round_score = 0
        for player in active_players:
            team = self._team_manager.get_team(player.name)
            player.squad_index = team.index if team else TEAM_TERRORISTS
        if sorted(self.side_squad_indexes) != list(TEAM_INDEXES):
            self.side_squad_indexes = list(TEAM_INDEXES)
        self._apply_current_sides(active_players)
        if self.status == "playing":
            self._normalize_dropped_weapons()
        else:
            self._reset_dropped_weapons()
        if self.status == "playing" and self.phase == PHASE_BUY:
            self._normalize_buy_transactions(valid_player_ids)
        else:
            self.buy_transactions = []
            self.pending_weapon_donation = None
        valid_emitter_ids = {
            emitter.id for emitter in self.tactical_map.ambient_emitters
        }
        self.ambient_stinger_due_ticks = {
            emitter_id: due_tick
            for emitter_id, due_tick in self.ambient_stinger_due_ticks.items()
            if emitter_id in valid_emitter_ids
            and isinstance(due_tick, int)
            and not isinstance(due_tick, bool)
            and due_tick >= 0
        }
        self._rebuild_turn_action_sets()
        if self.status == "waiting":
            return
        self.round = max(1, self.round)
        self.tactical_round = max(1, self.tactical_round)
        if self.phase not in PHASES:
            self.phase = PHASE_COMBAT
        self.overtime_period = max(0, self.overtime_period)
        self.overtime_round = max(0, self.overtime_round)
        if len(self.squad_loss_streaks) != len(TEAM_INDEXES):
            self.squad_loss_streaks = [
                self.economy.initial_loss_count for _ in TEAM_INDEXES
            ]
        else:
            self.squad_loss_streaks = [
                max(0, min(self.economy.maximum_loss_count, streak))
                for streak in self.squad_loss_streaks
            ]
        if len(self.overtime_start_scores) != len(TEAM_INDEXES):
            self.overtime_start_scores = [0, 0]
        else:
            self.overtime_start_scores = [
                min(self._squad_score(squad_index), max(0, score))
                for squad_index, score in zip(
                    TEAM_INDEXES, self.overtime_start_scores, strict=True
                )
            ]
        valid_nodes = self.tactical_map.node_map()
        self._normalize_area_effects(valid_nodes, valid_player_ids)
        for player in active_players:
            if player.team_index not in TEAM_INDEXES:
                player.team_index = TEAM_TERRORISTS
            if player.position_id not in valid_nodes:
                player.position_id = self._spawn_for_team(player.team_index)
            player.cash = max(0, min(self.economy.maximum_cash, player.cash))
            player.armor = max(0, min(self.economy.maximum_armor, player.armor))
            primary = self._primary_weapon(player)
            if not primary:
                player.primary_weapon_id = ""
            sidearm = self._sidearm(player)
            if not sidearm:
                sidearm = get_default_sidearm(player.team_index)
                player.sidearm_weapon_id = sidearm.id if sidearm else ""
            valid_equipped_ids = {
                weapon.id for weapon in (primary, sidearm) if weapon is not None
            }
            if player.equipped_weapon_id not in valid_equipped_ids:
                player.equipped_weapon_id = (
                    primary.id if primary else sidearm.id if sidearm else ""
                )
            owned_weapon_ids = valid_equipped_ids
            self._normalize_weapon_ammunition(player, owned_weapon_ids)
            equipped = self._equipped_weapon(player)
            self._normalize_utility_counts(player)
            self._normalize_equipment_counts(player)
            player.guard_points = max(
                0,
                min(self.rules.maximum_evasion_points, player.guard_points),
            )
            if player.guard_anchor_node_id not in valid_nodes:
                self._reset_stationary_evasion(player)
            else:
                player.stationary_guard_activations = max(
                    0,
                    min(
                        self.rules.maximum_evasion_points,
                        player.stationary_guard_activations,
                    ),
                )
            player.flash_penalty = max(
                0,
                min(self.rules.action_points_per_activation, player.flash_penalty),
            )
            spent_attack_action_points = self._normalize_activation_attack_ledger(
                player,
                owned_weapon_ids,
                valid_player_ids,
            )
            if (
                not equipped
                or equipped.hold_action_point_cost <= 0
                or player.held_angle_origin_id != player.position_id
                or player.held_angle_node_id not in valid_nodes
                or not self._can_hold_angle(player, player.held_angle_node_id, equipped)
            ):
                self._clear_held_angle(player)
            if player.held_angle_node_id or player.shots_fired_this_activation:
                player.guard_points = 0
            player.health = max(0, min(self.rules.max_health, player.health))
            if player.eliminated or player.health == 0:
                player.eliminated = True
                player.health = 0
                player.action_points = 0
                player.shots_fired_this_activation = (
                    self.rules.action_points_per_activation
                )
                player.weapon_shots_fired_this_activation = {}
                player.weapon_target_ids_this_activation = {}
                player.guard_points = 0
                self._reset_stationary_evasion(player)
                player.flash_penalty = 0
                self._clear_held_angle(player)
            else:
                player.health = max(1, player.health)
                if self.phase == PHASE_BUY:
                    player.action_points = 0
                    player.shots_fired_this_activation = 0
                    player.weapon_shots_fired_this_activation = {}
                    player.weapon_target_ids_this_activation = {}
                    player.guard_points = 0
                    self._reset_stationary_evasion(player)
                else:
                    player.action_points = max(
                        0,
                        min(
                            self.rules.action_points_per_activation
                            - spent_attack_action_points,
                            player.action_points,
                        ),
                    )

        self._normalize_spatial_positions(active_players)
        self._normalize_pending_weapon_donation(active_players)
        self._normalize_bomb_state(active_players)
        self._normalize_defuse_state(active_players)
        self._normalize_round_recovery(active_players)
        self._normalize_reaction_window(active_players)
        if self.round_recovery_player_id:
            recovery_player = self._breach_player_by_id(
                self.round_recovery_player_id
            )
            if recovery_player:
                self.current_player = recovery_player
        if self.reaction_window.is_open:
            responder = self._breach_player_by_id(
                self.reaction_window.responding_player_id
            )
            if responder:
                self.current_player = responder
        if self.last_round_win_reason not in WIN_REASONS:
            self.last_round_win_reason = ""
        if self.win_reason not in MATCH_RESULTS:
            self.win_reason = ""
        if self.winning_team_index not in (*TEAM_INDEXES, -1):
            self.winning_team_index = -1
        current = self._breach_player(self.current_player)
        acted_ids = (
            self.buy_ready_player_ids
            if self.phase == PHASE_BUY
            else self.round_acted_player_ids
        )
        if self.status == "playing" and (
            not current
            or current.eliminated
            or (
                self.phase == PHASE_BUY
                and current.id in acted_ids
                and not self.pending_weapon_donation
            )
        ):
            replacement = next(
                (
                    player
                    for player in self.turn_players
                    if isinstance(player, BreachPointPlayer)
                    and not player.eliminated
                    and player.id not in acted_ids
                ),
                None,
            ) or next(
                (
                    player
                    for player in self.turn_players
                    if isinstance(player, BreachPointPlayer) and not player.eliminated
                ),
                None,
            )
            if replacement:
                self.current_player = replacement
        if self.status == "playing":
            self._bot_coordinator.begin_combat_round(self)
            self._sync_all_listener_environment_audio()
            self._prepare_restored_finite_audio_sequences()

    def _normalize_pending_weapon_donation(
        self,
        active_players: list[BreachPointPlayer],
    ) -> None:
        """Restore one coherent buy response or safely return its purchase."""

        donation = self.pending_weapon_donation
        if not donation:
            return
        if not isinstance(donation, PendingWeaponDonation):
            self.pending_weapon_donation = None
            return
        buyer = self._breach_player_by_id(donation.buyer_id)
        recipient = self._breach_player_by_id(donation.recipient_id)
        weapon = get_weapon(donation.weapon_id)
        is_valid = bool(
            self.status == "playing"
            and self.phase == PHASE_BUY
            and buyer in active_players
            and recipient in active_players
            and buyer
            and recipient
            and buyer.id != recipient.id
            and not buyer.eliminated
            and not recipient.eliminated
            and buyer.team_index == recipient.team_index
            and buyer.id not in self.buy_ready_player_ids
            and weapon
            and weapon.cost > 0
            and weapon.cost == donation.cost
            and buyer.team_index in weapon.allowed_sides
        )
        if is_valid and recipient:
            self.current_player = recipient
            return
        if (
            buyer
            and weapon
            and weapon.cost == donation.cost
            and donation.cost > 0
        ):
            self._add_cash(buyer, donation.cost)
        self.pending_weapon_donation = None

    def _normalize_bomb_state(self, active_players: list[BreachPointPlayer]) -> None:
        if self.bomb_state not in BOMB_STATES:
            self.bomb_state = BOMB_CARRIED

        active_player_ids = {player.id for player in active_players}
        carrier = self._breach_player_by_id(self.bomb_carrier_id)
        if (
            self.bomb_state in {BOMB_CARRIED, BOMB_PLANTING}
            and carrier
            and carrier.id in active_player_ids
            and not carrier.eliminated
            and carrier.team_index == TEAM_TERRORISTS
        ):
            self.bomb_location_id = ""
            self._clear_bomb_grid_point()
            self.bomb_fuse_remaining = 0
            self.bomb_planted_tactical_round = 0
            if self.bomb_state == BOMB_PLANTING:
                if (
                    self.planting_player_id != carrier.id
                    or self.planting_location_id
                    not in self.tactical_map.bomb_site_ids()
                    or carrier.position_id != self.planting_location_id
                ):
                    self.bomb_state = BOMB_CARRIED
                    self.planting_player_id = ""
                    self.planting_location_id = ""
            else:
                self.planting_player_id = ""
                self.planting_location_id = ""
            return

        if self.bomb_state == BOMB_PLANTED:
            if self.bomb_location_id not in self.tactical_map.bomb_site_ids():
                self.bomb_location_id = self.tactical_map.bomb_site_ids()[0]
            self._normalize_bomb_grid_point()
            self.bomb_carrier_id = ""
            self.bomb_fuse_remaining = max(
                0
                if self.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
                else 1,
                min(
                    self.rules.bomb_fuse_tactical_rounds,
                    self.bomb_fuse_remaining,
                ),
            )
            self.bomb_planted_tactical_round = max(
                1,
                min(
                    self.tactical_round,
                    self.bomb_planted_tactical_round or self.tactical_round,
                ),
            )
            self.planting_player_id = ""
            self.planting_location_id = ""
            return

        if (
            self.bomb_state == BOMB_DROPPED
            and self.bomb_location_id in self.tactical_map.node_map()
        ):
            self._normalize_bomb_grid_point()
            self.bomb_carrier_id = ""
            self.bomb_fuse_remaining = 0
            self.bomb_planted_tactical_round = 0
            self.planting_player_id = ""
            self.planting_location_id = ""
            return

        replacement = next(
            (
                player
                for player in active_players
                if player.team_index == TEAM_TERRORISTS and not player.eliminated
            ),
            None,
        )
        if replacement:
            self.bomb_state = BOMB_CARRIED
            self.bomb_carrier_id = replacement.id
            self.bomb_location_id = ""
            self._clear_bomb_grid_point()
            self.bomb_fuse_remaining = 0
            self.bomb_planted_tactical_round = 0
            self.planting_player_id = ""
            self.planting_location_id = ""
        else:
            self.bomb_state = BOMB_DROPPED
            self.bomb_carrier_id = ""
            self.bomb_location_id = self.tactical_map.terrorist_spawn
            self._normalize_bomb_grid_point()
            self.bomb_fuse_remaining = 0
            self.bomb_planted_tactical_round = 0
            self.planting_player_id = ""
            self.planting_location_id = ""

    def _normalize_defuse_state(self, active_players: list[BreachPointPlayer]) -> None:
        """Retain only a live, coherent post-plant defuse attempt."""

        active_player_ids = {player.id for player in active_players}
        defuser = self._breach_player_by_id(self.defusing_player_id)
        if (
            self.bomb_state != BOMB_PLANTED
            or self.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG)
            or not defuser
            or defuser.id not in active_player_ids
            or defuser.eliminated
            or defuser.team_index != TEAM_COUNTER_TERRORISTS
            or defuser.position_id != self.bomb_location_id
            or self.defusing_location_id != self.bomb_location_id
        ):
            self._clear_pending_defuse()

    def _clear_pending_defuse(self) -> None:
        self.defusing_player_id = ""
        self.defusing_location_id = ""

    def _clear_round_recovery(self) -> None:
        """Clear the serialized one-choice post-elimination recovery window."""

        self.round_recovery_player_id = ""
        self.round_recovery_drop_ids = []
        self.pending_round_winner_side_index = -1
        self.pending_round_win_reason = ""

    def _normalize_round_recovery(
        self,
        active_players: list[BreachPointPlayer],
    ) -> None:
        """Restore only a live survivor with an eligible final-elimination drop."""

        if not self.round_recovery_player_id:
            self._clear_round_recovery()
            return
        survivor = self._breach_player_by_id(self.round_recovery_player_id)
        valid_drop_ids = {
            dropped_weapon.drop_id
            for dropped_weapon in self._dropped_weapons_at(
                survivor.position_id if survivor else ""
            )
        }
        self.round_recovery_drop_ids = list(
            dict.fromkeys(
                drop_id
                for drop_id in self.round_recovery_drop_ids
                if drop_id in valid_drop_ids
            )
        )
        if (
            survivor
            and survivor in active_players
            and not survivor.eliminated
            and survivor.action_points >= self.rules.weapon_pickup_cost
            and self.round_recovery_drop_ids
            and self.pending_round_winner_side_index in TEAM_INDEXES
            and self.pending_round_win_reason in WIN_REASONS
        ):
            self.reaction_window = ReactionWindow()
            self.current_player = survivor
            return

        winner = self.pending_round_winner_side_index
        reason = self.pending_round_win_reason
        self._clear_round_recovery()
        if winner in TEAM_INDEXES and reason in WIN_REASONS:
            self._finish_combat_round(winner, reason)

    def _normalize_reaction_window(
        self,
        active_players: list[BreachPointPlayer],
    ) -> None:
        """Discard any reaction whose actors or trigger state are no longer valid."""

        window = self.reaction_window
        active_player_ids = {player.id for player in active_players}
        if not window.is_open:
            self.reaction_window = ReactionWindow()
            if self.defusing_player_id:
                self._clear_pending_defuse()
            if window.kind in REACTION_KINDS:
                self._recover_from_invalid_reaction(window, active_player_ids)
            return
        trigger = self._breach_player_by_id(window.triggering_player_id)
        responder = self._breach_player_by_id(window.responding_player_id)
        target = self._breach_player_by_id(window.target_player_id)
        common_valid = bool(
            self.status == "playing"
            and self.phase == PHASE_COMBAT
            and window.kind in REACTION_KINDS
            and trigger
            and responder
            and trigger.id in active_player_ids
            and responder.id in active_player_ids
            and not responder.eliminated
            and trigger.id != responder.id
            and window.resume_after_player_id == trigger.id
            and target
            and target.id == trigger.id
            and window.context.get("node_id", "") == trigger.position_id
        )
        responder_was_unacted = bool(
            responder and responder.id not in self.round_acted_player_ids
        )
        expected_response_action_points = (
            self.rules.action_points_per_activation
            if responder_was_unacted
            else self.rules.repeat_objective_response_action_points
        )
        kind_valid = False
        if common_valid and window.kind == REACTION_PLANT:
            kind_valid = bool(
                trigger.team_index == TEAM_TERRORISTS
                and responder.team_index == TEAM_COUNTER_TERRORISTS
                and (
                    self.bomb_state == BOMB_PLANTING
                    and trigger.id == self.planting_player_id
                    or self.bomb_state in {BOMB_CARRIED, BOMB_DROPPED}
                    and not self.planting_player_id
                )
                and window.response_action_points == expected_response_action_points
                and window.consumes_activation == responder_was_unacted
            )
        elif common_valid and window.kind == REACTION_DEFUSE:
            kind_valid = bool(
                self.bomb_state == BOMB_PLANTED
                and trigger.team_index == TEAM_COUNTER_TERRORISTS
                and responder.team_index == TEAM_TERRORISTS
                and self.defusing_player_id in {"", trigger.id}
                and window.response_action_points == expected_response_action_points
                and window.consumes_activation == responder_was_unacted
            )
        elif common_valid and window.kind == REACTION_WATCHED_ENTRY:
            weapon = self._equipped_weapon(responder)
            node_id = window.context.get("node_id", "")
            kind_valid = bool(
                target
                and target.id == trigger.id
                and not target.eliminated
                and target.team_index != responder.team_index
                and target.position_id == node_id
                and responder.held_angle_origin_id == responder.position_id
                and responder.held_angle_node_id == node_id
                and self._can_hold_angle(responder, node_id, weapon)
                and self._can_see(responder, target)
                and window.response_action_points == 0
                and not window.consumes_activation
            )
        if kind_valid:
            if window.kind in {REACTION_PLANT, REACTION_DEFUSE} and responder:
                responder.action_points = min(
                    responder.action_points,
                    window.response_action_points,
                )
            return
        if window.kind == REACTION_DEFUSE:
            self._clear_pending_defuse()
        self.reaction_window = ReactionWindow()
        self._recover_from_invalid_reaction(window, active_player_ids)

    def _recover_from_invalid_reaction(
        self,
        window: ReactionWindow,
        active_player_ids: set[str],
    ) -> None:
        """Restore playable turn ownership after discarding a stale reaction."""

        if (
            self.status != "playing"
            or self.phase != PHASE_COMBAT
            or window.kind not in REACTION_KINDS
        ):
            return
        trigger = self._breach_player_by_id(window.triggering_player_id)
        if (
            window.kind == REACTION_WATCHED_ENTRY
            and trigger
            and trigger.id in active_player_ids
            and not trigger.eliminated
        ):
            self.current_player = trigger
            return
        if window.kind == REACTION_PLANT and self.bomb_state == BOMB_PLANTING:
            self._complete_pending_plant()
        if self.status == "playing":
            self._continue_after_activation(window.resume_after_player_id)

    def _rebuild_turn_action_sets(self) -> None:
        for player in self.players:
            self.remove_action_set(player, "turn")
            sets = self.player_action_sets.setdefault(player.id, [])
            sets.insert(0, self.create_turn_action_set(player))

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        self._process_ambient_stingers()
        if self.status != "playing":
            return
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict[str, Any],
    ) -> None:
        if callback_id == MOVEMENT_START_CALLBACK:
            self._start_movement_sequence(sequence_id, payload)
            return
        if callback_id == MOVEMENT_ARRIVE_CALLBACK:
            self._complete_movement_sequence(payload)
            return
        if callback_id == UTILITY_START_CALLBACK:
            self._start_utility_sequence(sequence_id, payload)
            return
        if callback_id == UTILITY_FLIGHT_CALLBACK:
            self._start_utility_flight_sequence(sequence_id, payload)
            return
        if callback_id == UTILITY_BOUNCE_CALLBACK:
            self._bounce_utility_sequence(sequence_id, payload)
            return
        if callback_id == UTILITY_IMPACT_CALLBACK:
            self._impact_utility_sequence(sequence_id, payload)
            return
        if callback_id == UTILITY_RESOLVE_CALLBACK:
            self._resolve_utility_sequence(sequence_id, payload)
            return
        if callback_id == UTILITY_FINISH_CALLBACK:
            self._finish_utility_sequence(sequence_id, payload)
            return
        if callback_id == WEAPON_FIRE_CALLBACK:
            self._fire_weapon_sequence(sequence_id, payload)
            return
        if callback_id == WEAPON_RESOLVE_CALLBACK:
            self._resolve_weapon_sequence(sequence_id, payload)
            return
        if callback_id == ROUND_TRANSITION_CALLBACK:
            self._start_next_combat_round()
            return
        if callback_id == BUY_COUNTDOWN_BEEP_CALLBACK:
            self._play_global_asset(
                BUY_COUNTDOWN_ASSET,
                priority=80,
                max_instances=3,
            )
            return
        if callback_id == BUY_COUNTDOWN_FINISH_CALLBACK:
            self._start_combat_phase()
            return
        if callback_id == BOMB_DETONATION_START_CALLBACK:
            self._play_bomb_detonation_warning_audio(self._bomb_grid_point())
            return
        if callback_id == BOMB_DETONATION_FINISH_CALLBACK:
            self._complete_bomb_detonation(sequence_id)
            return
        if callback_id == MATCH_RESULT_FINISH_CALLBACK:
            self._finish_match(
                int(payload.get("squad_index", -1)),
                str(payload.get("reason", "")),
            )
            return
        if callback_id == MUSIC_ACTION_STOP_CALLBACK:
            self.stop_music(
                handle=MUSIC_CONTEXT_HANDLE,
                fade_ms=MUSIC_CROSSFADE_MS,
            )
            return
        super().on_sequence_callback(sequence_id, callback_id, payload)

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _breach_player(self, player: Player | None) -> BreachPointPlayer | None:
        return player if isinstance(player, BreachPointPlayer) else None

    def _breach_player_by_id(self, player_id: str) -> BreachPointPlayer | None:
        return self._breach_player(self.get_player_by_id(player_id))

    def _players_on_team(
        self, team_index: int, *, alive_only: bool = False
    ) -> list[BreachPointPlayer]:
        players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer) and player.team_index == team_index
        ]
        if alive_only:
            players = [player for player in players if not player.eliminated]
        return players

    def _turn_order_players_on_team(
        self, team_index: int, *, alive_only: bool = False
    ) -> list[BreachPointPlayer]:
        """Return one side in its current activation order."""

        players = [
            player
            for player in self.turn_players
            if isinstance(player, BreachPointPlayer) and player.team_index == team_index
        ]
        if alive_only:
            players = [player for player in players if not player.eliminated]
        return players

    def _spawn_for_team(self, team_index: int) -> str:
        if team_index == TEAM_COUNTER_TERRORISTS:
            return self.tactical_map.counter_terrorist_spawn
        return self.tactical_map.terrorist_spawn

    def _spawn_heading_for_team(self, team_index: int) -> int:
        if team_index == TEAM_COUNTER_TERRORISTS:
            return self.tactical_map.counter_terrorist_spawn_heading
        return self.tactical_map.terrorist_spawn_heading

    @staticmethod
    def _player_grid_point(player: BreachPointPlayer) -> GridPoint:
        return GridPoint(player.grid_x, player.grid_y)

    def _bomb_grid_point(self) -> GridPoint:
        """Return the bomb's exact valid ground coordinate or its area anchor."""

        point = GridPoint(self.bomb_grid_x, self.bomb_grid_y)
        node = self._node(self.bomb_location_id)
        if node and node.is_walkable(point):
            return point
        return node.anchor if node else point

    def _set_bomb_grid_point(self, point: GridPoint) -> None:
        self.bomb_grid_x = point.x
        self.bomb_grid_y = point.y

    def _clear_bomb_grid_point(self) -> None:
        self.bomb_grid_x = -1
        self.bomb_grid_y = -1

    def _normalize_bomb_grid_point(self) -> None:
        point = self._bomb_grid_point()
        node = self._node(self.bomb_location_id)
        if node and node.is_walkable(point):
            self._set_bomb_grid_point(point)
        else:
            self._clear_bomb_grid_point()

    def _player_has_valid_grid_point(self, player: BreachPointPlayer) -> bool:
        node = self._node(player.position_id)
        return bool(
            node
            and self._player_grid_point(player)
            in node.placement_points(self.tactical_map.minimum_player_spacing)
        )

    def _choose_grid_point(
        self,
        node: TacticalNode,
        occupied: set[GridPoint],
    ) -> GridPoint:
        candidates = [
            point
            for point in node.placement_points(self.tactical_map.minimum_player_spacing)
            if point not in occupied
        ]
        if not candidates:
            raise RuntimeError(f"Tactical area {node.id} has no free placement cell")
        if not occupied:
            return self._spatial_rng.choice(candidates)
        distances = {
            point: min(
                (point.x - other.x) ** 2 + (point.y - other.y) ** 2
                for other in occupied
            )
            for point in candidates
        }
        farthest_distance = max(distances.values())
        farthest = [
            point for point in candidates if distances[point] == farthest_distance
        ]
        return self._spatial_rng.choice(farthest)

    def _place_player_in_node(
        self,
        player: BreachPointPlayer,
        node_id: str,
        *,
        occupied: set[GridPoint] | None = None,
        heading: int | None = None,
    ) -> None:
        """Place one player on a free cell and derive travel orientation."""

        node = self._node(node_id)
        if not node:
            raise RuntimeError(f"Unknown tactical area {node_id}")
        previous_node = self._node(player.position_id)
        if occupied is None:
            occupied = {
                self._player_grid_point(other)
                for other in self.get_active_players()
                if isinstance(other, BreachPointPlayer)
                and other.id != player.id
                and other.position_id == node_id
                and self._player_has_valid_grid_point(other)
            }
        destination = self._choose_grid_point(node, occupied)
        player.position_id = node_id
        player.grid_x = destination.x
        player.grid_y = destination.y
        if heading is not None:
            player.facing_degrees = heading % 360
        elif previous_node and previous_node.id != node.id:
            delta_x = node.anchor.x - previous_node.anchor.x
            delta_y = node.anchor.y - previous_node.anchor.y
            player.facing_degrees = (
                round(math.degrees(math.atan2(delta_x, delta_y))) % 360
            )

    def _normalize_spatial_positions(
        self,
        players: list[BreachPointPlayer],
    ) -> None:
        """Keep restored/new occupants on unique walkable coordinates."""

        occupied_by_node: dict[str, set[GridPoint]] = {}
        for player in players:
            player.facing_degrees %= 360
            occupied = occupied_by_node.setdefault(player.position_id, set())
            point = self._player_grid_point(player)
            if not self._player_has_valid_grid_point(player) or point in occupied:
                self._place_player_in_node(
                    player,
                    player.position_id,
                    occupied=occupied,
                    heading=player.facing_degrees,
                )
                point = self._player_grid_point(player)
            occupied.add(point)

    def _node(self, node_id: str) -> TacticalNode | None:
        return self.tactical_map.get_node(node_id)

    def _node_name(self, locale: str, node_id: str) -> str:
        node = self._node(node_id)
        key = node.name_key if node else "breachpoint-node-unknown"
        return Localization.get(locale, key)

    def _spatial_context(self, locale: str, node_id: str) -> str:
        """Describe an area's physical setting and deliberate firing lanes."""

        node = self._node(node_id)
        if not node:
            return Localization.get(locale, "breachpoint-node-unknown")
        terrain = Localization.format_list_and(
            locale,
            [Localization.get(locale, feature.name_key) for feature in node.terrain],
        )
        sightlines = Localization.format_list_and(
            locale,
            [
                Localization.get(
                    locale,
                    "breachpoint-map-sightline-entry",
                    location=self._node_name(locale, visible_id),
                    range=self._combat_distance(node.id, visible_id),
                )
                for visible_id in self.tactical_map.visible_node_ids(node.id)
            ],
        )
        return Localization.get(
            locale,
            "breachpoint-map-spatial-context",
            location=self._node_name(locale, node.id),
            description=Localization.get(locale, node.description_key),
            terrain=terrain,
            sightlines=sightlines,
        )

    @staticmethod
    def _weapon_from_buy_action(action_id: str) -> WeaponProfile | None:
        prefix = "buy_weapon_"
        if not action_id.startswith(prefix):
            return None
        return get_weapon(action_id[len(prefix) :])

    @staticmethod
    def _donate_weapon_action_id(
        weapon: WeaponProfile,
        recipient: BreachPointPlayer,
    ) -> str:
        return f"{DONATE_WEAPON_ACTION_PREFIX}{weapon.id}_to_{recipient.id}"

    def _donation_action_details(
        self,
        donor: BreachPointPlayer,
        action_id: str,
    ) -> tuple[WeaponProfile, BreachPointPlayer] | None:
        """Resolve only a currently generated same-team donation action."""

        for recipient in self.get_active_players():
            if (
                not isinstance(recipient, BreachPointPlayer)
                or recipient.id == donor.id
                or recipient.team_index != donor.team_index
                or recipient.eliminated
            ):
                continue
            for weapon in get_purchasable_weapons(donor.team_index):
                if action_id == self._donate_weapon_action_id(weapon, recipient):
                    return weapon, recipient
        return None

    @staticmethod
    def _utility_from_buy_action(action_id: str) -> UtilityProfile | None:
        prefix = "buy_utility_"
        if not action_id.startswith(prefix):
            return None
        return get_utility(action_id[len(prefix) :])

    @staticmethod
    def _equipment_from_buy_action(action_id: str) -> EquipmentProfile | None:
        prefix = "buy_equipment_"
        if not action_id.startswith(prefix):
            return None
        return get_equipment(action_id[len(prefix) :])

    @staticmethod
    def _refund_action_details(action_id: str) -> tuple[str, str] | None:
        """Parse a server-created refund action without trusting arbitrary ids."""

        if action_id == f"{REFUND_ACTION_PREFIX}{PURCHASE_KIND_ARMOR}":
            return PURCHASE_KIND_ARMOR, PURCHASE_KIND_ARMOR
        for item_kind in (
            PURCHASE_KIND_WEAPON,
            PURCHASE_KIND_UTILITY,
            PURCHASE_KIND_EQUIPMENT,
        ):
            prefix = f"{REFUND_ACTION_PREFIX}{item_kind}_"
            if action_id.startswith(prefix):
                return item_kind, action_id[len(prefix) :]
        return None

    @staticmethod
    def _dropped_weapon_action_id(dropped_weapon: DroppedWeapon) -> str:
        return f"{PICK_UP_WEAPON_ACTION_PREFIX}{dropped_weapon.drop_id}"

    def _dropped_weapon_from_action(
        self,
        action_id: str,
    ) -> DroppedWeapon | None:
        """Resolve a generated action without trusting client-supplied indexes."""

        return next(
            (
                dropped_weapon
                for dropped_weapon in self.dropped_weapons
                if self._dropped_weapon_action_id(dropped_weapon) == action_id
            ),
            None,
        )

    @staticmethod
    def _node_from_hold_action(action_id: str) -> str:
        prefix = "hold_angle_"
        return action_id[len(prefix) :] if action_id.startswith(prefix) else ""

    @staticmethod
    def _throw_action_details(
        action_id: str,
    ) -> tuple[UtilityProfile, str] | None:
        prefix = "throw_"
        if not action_id.startswith(prefix):
            return None
        payload = action_id[len(prefix) :]
        for utility in sorted(
            get_utilities(), key=lambda item: len(item.id), reverse=True
        ):
            utility_prefix = f"{utility.id}_"
            if payload.startswith(utility_prefix):
                return utility, payload[len(utility_prefix) :]
        return None

    @staticmethod
    def _weapon_name(locale: str, weapon: WeaponProfile | None) -> str:
        key = weapon.name_key if weapon else "breachpoint-weapon-none"
        return Localization.get(locale, key)

    def _armor_name(self, locale: str) -> str:
        return Localization.get(locale, self.economy.armor_name_key)

    @staticmethod
    def _utility_name(locale: str, utility: UtilityProfile) -> str:
        return Localization.get(locale, utility.name_key)

    @staticmethod
    def _equipment_name(locale: str, equipment: EquipmentProfile) -> str:
        return Localization.get(locale, equipment.name_key)

    def _utility_summary(self, locale: str, player: BreachPointPlayer) -> str:
        entries = [
            (utility.id, self._utility_name(locale, utility), count)
            for utility in get_utilities()
            if (count := player.utility_counts.get(utility.id, 0)) > 0
        ]
        if not entries:
            return Localization.get(locale, "breachpoint-utility-none")
        return Localization.format_list_and(
            locale,
            [
                Localization.get(
                    locale,
                    "breachpoint-utility-count",
                    utility=name,
                    count=count,
                )
                for _utility_id, name, count in entries
            ],
        )

    def _equipment_summary(self, locale: str, player: BreachPointPlayer) -> str:
        entries = [
            self._equipment_name(locale, equipment)
            for equipment in get_purchasable_equipment(player.team_index)
            if player.equipment_counts.get(equipment.id, 0) > 0
        ]
        if not entries:
            return Localization.get(locale, "breachpoint-equipment-none")
        return Localization.format_list_and(locale, entries)

    def _dropped_weapons_at(self, node_id: str) -> tuple[DroppedWeapon, ...]:
        """Return ground weapons in stable drop order for one named area."""

        return tuple(
            dropped_weapon
            for dropped_weapon in self.dropped_weapons
            if dropped_weapon.node_id == node_id
        )

    def _reset_dropped_weapons(self) -> None:
        """Retire ground weapons and restart ids for a new match lifecycle."""

        self._clear_dropped_weapons()
        self.next_dropped_weapon_id = 1

    def _clear_dropped_weapons(self) -> None:
        """Retire round-scoped items without reusing match-scoped action ids."""

        self.dropped_weapons = []

    def _ground_weapon_summary(self, locale: str, node_id: str) -> str:
        entries = []
        for dropped_weapon in self._dropped_weapons_at(node_id):
            weapon = get_weapon(dropped_weapon.weapon_id)
            if not weapon:
                continue
            entries.append(
                Localization.get(
                    locale,
                    "breachpoint-ground-weapon-entry",
                    weapon=self._weapon_name(locale, weapon),
                    ammunition=self._dropped_weapon_ammunition_summary(
                        locale,
                        dropped_weapon,
                        weapon,
                    ),
                )
            )
        if not entries:
            return Localization.get(locale, "breachpoint-ground-weapons-none")
        return Localization.format_list_and(locale, entries)

    def _normalize_dropped_weapons(self) -> None:
        """Keep restored ground weapons valid, unique, and spatially coherent."""

        normalized: list[DroppedWeapon] = []
        seen_ids: set[int] = set()
        for dropped_weapon in self.dropped_weapons:
            if not isinstance(dropped_weapon, DroppedWeapon):
                continue
            weapon = get_weapon(dropped_weapon.weapon_id)
            node = self._node(dropped_weapon.node_id)
            integer_values = (
                dropped_weapon.drop_id,
                dropped_weapon.grid_x,
                dropped_weapon.grid_y,
                dropped_weapon.magazine_ammo,
                dropped_weapon.reserve_units,
            )
            has_invalid_integer = any(
                not isinstance(value, int) or isinstance(value, bool)
                for value in integer_values
            )
            if (
                not weapon
                or not node
                or has_invalid_integer
                or (
                    isinstance(dropped_weapon.drop_id, int)
                    and dropped_weapon.drop_id <= 0
                )
                or dropped_weapon.drop_id in seen_ids
            ):
                continue
            point = GridPoint(dropped_weapon.grid_x, dropped_weapon.grid_y)
            if not node.is_walkable(point):
                point = node.anchor
            normalized.append(
                DroppedWeapon(
                    drop_id=dropped_weapon.drop_id,
                    weapon_id=weapon.id,
                    node_id=node.id,
                    grid_x=point.x,
                    grid_y=point.y,
                    magazine_ammo=max(
                        0,
                        min(weapon.magazine_capacity, dropped_weapon.magazine_ammo),
                    ),
                    reserve_units=max(
                        0,
                        min(weapon.reserve_units, dropped_weapon.reserve_units),
                    ),
                )
            )
            seen_ids.add(dropped_weapon.drop_id)
        self.dropped_weapons = normalized
        minimum_next_id = max(seen_ids, default=0) + 1
        if not isinstance(self.next_dropped_weapon_id, int) or isinstance(
            self.next_dropped_weapon_id, bool
        ):
            self.next_dropped_weapon_id = minimum_next_id
        else:
            self.next_dropped_weapon_id = max(
                minimum_next_id,
                self.next_dropped_weapon_id,
            )

    def _normalize_buy_transactions(self, valid_player_ids: set[str]) -> None:
        """Discard malformed or no-longer-reversible current buy records."""

        normalized: list[BuyTransaction] = []
        for transaction in self.buy_transactions:
            if (
                not isinstance(transaction, BuyTransaction)
                or transaction.player_id not in valid_player_ids
                or transaction.item_kind not in PURCHASE_KINDS
                or not isinstance(transaction.cost, int)
                or isinstance(transaction.cost, bool)
                or transaction.cost < 0
                or not isinstance(transaction.previous_amount, int)
                or isinstance(transaction.previous_amount, bool)
                or transaction.previous_amount < 0
                or not isinstance(transaction.dropped_weapon_id, int)
                or isinstance(transaction.dropped_weapon_id, bool)
                or transaction.dropped_weapon_id < 0
            ):
                continue
            buyer = self._breach_player_by_id(transaction.player_id)
            if (
                buyer
                and self._transaction_profile_is_valid(buyer, transaction)
                and self._transaction_is_refundable(buyer, transaction)
            ):
                normalized.append(transaction)
        self.buy_transactions = normalized

    def _transaction_profile_is_valid(
        self,
        buyer: BreachPointPlayer,
        transaction: BuyTransaction,
    ) -> bool:
        if transaction.item_kind == PURCHASE_KIND_WEAPON:
            item = get_weapon(transaction.item_id)
            return bool(
                item
                and item.cost > 0
                and item.cost == transaction.cost
                and buyer.team_index in item.allowed_sides
                and transaction.previous_amount == 0
            )
        if transaction.item_kind == PURCHASE_KIND_UTILITY:
            item = get_utility(transaction.item_id)
            return bool(
                item
                and item.cost == transaction.cost
                and buyer.team_index in item.allowed_sides
                and transaction.previous_amount < item.maximum_carry
                and transaction.dropped_weapon_id == 0
            )
        if transaction.item_kind == PURCHASE_KIND_EQUIPMENT:
            item = get_equipment(transaction.item_id)
            return bool(
                item
                and item.cost == transaction.cost
                and buyer.team_index in item.allowed_sides
                and transaction.previous_amount < item.maximum_carry
                and transaction.dropped_weapon_id == 0
            )
        return bool(
            transaction.item_kind == PURCHASE_KIND_ARMOR
            and transaction.item_id == PURCHASE_KIND_ARMOR
            and transaction.cost == self.economy.armor_cost
            and transaction.previous_amount < self.economy.maximum_armor
            and transaction.dropped_weapon_id == 0
        )

    def _transaction_is_refundable(
        self,
        buyer: BreachPointPlayer,
        transaction: BuyTransaction,
    ) -> bool:
        """Return whether the exact purchased item still exists unused."""

        if transaction.player_id != buyer.id:
            return False
        if transaction.item_kind == PURCHASE_KIND_WEAPON:
            weapon = get_weapon(transaction.item_id)
            if not weapon:
                return False
            if transaction.dropped_weapon_id:
                return any(
                    dropped.drop_id == transaction.dropped_weapon_id
                    and dropped.weapon_id == weapon.id
                    for dropped in self.dropped_weapons
                )
            owned = (
                self._primary_weapon(buyer)
                if weapon.slot == WEAPON_SLOT_PRIMARY
                else self._sidearm(buyer)
            )
            return bool(owned and owned.id == weapon.id)
        if transaction.item_kind == PURCHASE_KIND_UTILITY:
            return (
                buyer.utility_counts.get(transaction.item_id, 0)
                > transaction.previous_amount
            )
        if transaction.item_kind == PURCHASE_KIND_EQUIPMENT:
            return (
                buyer.equipment_counts.get(transaction.item_id, 0)
                > transaction.previous_amount
            )
        if transaction.item_kind == PURCHASE_KIND_ARMOR:
            return buyer.armor > transaction.previous_amount
        return False

    def _refundable_transaction(
        self,
        buyer: BreachPointPlayer,
        item_kind: str,
        item_id: str,
    ) -> BuyTransaction | None:
        """Find the newest still-owned purchase matching one refund button."""

        return next(
            (
                transaction
                for transaction in reversed(self.buy_transactions)
                if transaction.player_id == buyer.id
                and transaction.item_kind == item_kind
                and transaction.item_id == item_id
                and self._transaction_is_refundable(buyer, transaction)
            ),
            None,
        )

    def _record_buy_transaction(
        self,
        buyer: BreachPointPlayer,
        item_kind: str,
        item_id: str,
        cost: int,
        *,
        previous_amount: int = 0,
        dropped_weapon_id: int = 0,
    ) -> None:
        self.buy_transactions.append(
            BuyTransaction(
                player_id=buyer.id,
                item_kind=item_kind,
                item_id=item_id,
                cost=cost,
                previous_amount=previous_amount,
                dropped_weapon_id=dropped_weapon_id,
            )
        )

    def _link_purchased_weapon_drop(
        self,
        buyer: BreachPointPlayer,
        weapon: WeaponProfile,
        dropped_weapon: DroppedWeapon,
    ) -> None:
        """Keep a purchased gun refundable after a later buy drops it."""

        transaction = next(
            (
                candidate
                for candidate in reversed(self.buy_transactions)
                if candidate.player_id == buyer.id
                and candidate.item_kind == PURCHASE_KIND_WEAPON
                and candidate.item_id == weapon.id
                and candidate.dropped_weapon_id == 0
            ),
            None,
        )
        if transaction:
            transaction.dropped_weapon_id = dropped_weapon.drop_id

    def _link_purchased_weapon_pickup(
        self,
        buyer: BreachPointPlayer,
        dropped_weapon: DroppedWeapon,
    ) -> None:
        """Move the buyer's exact purchase record back into their held slot."""

        transaction = next(
            (
                candidate
                for candidate in reversed(self.buy_transactions)
                if candidate.player_id == buyer.id
                and candidate.item_kind == PURCHASE_KIND_WEAPON
                and candidate.item_id == dropped_weapon.weapon_id
                and candidate.dropped_weapon_id == dropped_weapon.drop_id
            ),
            None,
        )
        if transaction:
            transaction.dropped_weapon_id = 0

    def _normalize_utility_counts(self, player: BreachPointPlayer) -> None:
        normalized: dict[str, int] = {}
        remaining_capacity = self.rules.maximum_utility_items
        for utility in get_purchasable_utilities(player.team_index):
            if remaining_capacity <= 0:
                break
            count = player.utility_counts.get(utility.id, 0)
            if isinstance(count, int) and not isinstance(count, bool) and count > 0:
                retained = min(
                    utility.maximum_carry,
                    count,
                    remaining_capacity,
                )
                normalized[utility.id] = retained
                remaining_capacity -= retained
        player.utility_counts = normalized

    def _normalize_equipment_counts(self, player: BreachPointPlayer) -> None:
        normalized: dict[str, int] = {}
        for equipment in get_purchasable_equipment(player.team_index):
            count = player.equipment_counts.get(equipment.id, 0)
            if isinstance(count, int) and count > 0:
                normalized[equipment.id] = min(equipment.maximum_carry, count)
        player.equipment_counts = normalized

    def _owned_weapons(self, player: BreachPointPlayer) -> tuple[WeaponProfile, ...]:
        """Return the player's valid weapon slots without duplicates."""

        return tuple(
            {
                weapon.id: weapon
                for weapon in (self._sidearm(player), self._primary_weapon(player))
                if weapon
            }.values()
        )

    @staticmethod
    def _set_full_weapon_ammunition(
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> None:
        player.weapon_magazine_ammo[weapon.id] = weapon.magazine_capacity
        player.weapon_reserve_units[weapon.id] = weapon.reserve_units

    def _refill_owned_weapon_ammunition(self, player: BreachPointPlayer) -> None:
        """Start a combat round with full ammunition for every retained weapon."""

        player.weapon_magazine_ammo = {}
        player.weapon_reserve_units = {}
        for weapon in self._owned_weapons(player):
            self._set_full_weapon_ammunition(player, weapon)

    def _normalize_weapon_ammunition(
        self,
        player: BreachPointPlayer,
        owned_weapon_ids: set[str],
    ) -> None:
        """Clamp serialized ammunition to the currently owned weapon profiles."""

        player.weapon_magazine_ammo = {
            weapon_id: max(0, min(weapon.magazine_capacity, ammunition))
            for weapon_id, ammunition in player.weapon_magazine_ammo.items()
            if weapon_id in owned_weapon_ids
            and (weapon := get_weapon(weapon_id)) is not None
            and isinstance(ammunition, int)
            and not isinstance(ammunition, bool)
        }
        player.weapon_reserve_units = {
            weapon_id: max(0, min(weapon.reserve_units, reserve_units))
            for weapon_id, reserve_units in player.weapon_reserve_units.items()
            if weapon_id in owned_weapon_ids
            and (weapon := get_weapon(weapon_id)) is not None
            and isinstance(reserve_units, int)
            and not isinstance(reserve_units, bool)
        }
        for weapon in self._owned_weapons(player):
            player.weapon_magazine_ammo.setdefault(weapon.id, weapon.magazine_capacity)
            player.weapon_reserve_units.setdefault(weapon.id, weapon.reserve_units)

    @staticmethod
    def _loaded_ammunition(
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> int:
        return max(
            0,
            min(
                weapon.magazine_capacity,
                player.weapon_magazine_ammo.get(weapon.id, weapon.magazine_capacity),
            ),
        )

    @staticmethod
    def _reserve_ammunition_units(
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> int:
        return max(
            0,
            min(
                weapon.reserve_units,
                player.weapon_reserve_units.get(weapon.id, weapon.reserve_units),
            ),
        )

    def _consume_attack_ammunition(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> int:
        """Consume and return the rounds or shells used by one attack."""

        loaded = self._loaded_ammunition(player, weapon)
        ammunition = min(weapon.ammunition_per_attack, loaded)
        player.weapon_magazine_ammo[weapon.id] = loaded - ammunition
        return ammunition

    def _reload_weapon(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> tuple[int, int, int]:
        """Reload from profile data and return loaded, discarded, and used units."""

        loaded = self._loaded_ammunition(player, weapon)
        reserve_units = self._reserve_ammunition_units(player, weapon)
        needed_rounds = weapon.magazine_capacity - loaded
        if needed_rounds <= 0 or reserve_units <= 0:
            return 0, 0, 0
        if weapon.discard_loaded_rounds_on_reload:
            used_units = 1
            discarded = loaded
            new_loaded = weapon.magazine_capacity
        else:
            maximum_needed_units = (
                needed_rounds + weapon.reload_rounds_per_unit - 1
            ) // weapon.reload_rounds_per_unit
            used_units = min(
                reserve_units,
                weapon.reload_units_per_action,
                maximum_needed_units,
            )
            discarded = 0
            new_loaded = min(
                weapon.magazine_capacity,
                loaded + used_units * weapon.reload_rounds_per_unit,
            )
        player.weapon_magazine_ammo[weapon.id] = new_loaded
        player.weapon_reserve_units[weapon.id] = reserve_units - used_units
        return new_loaded - loaded, discarded, used_units

    def _ammunition_summary(
        self,
        locale: str,
        player: BreachPointPlayer,
        weapon: WeaponProfile | None,
    ) -> str:
        if not weapon:
            return Localization.get(locale, "breachpoint-ammo-none")
        reserve_units = self._reserve_ammunition_units(player, weapon)
        return Localization.get(
            locale,
            "breachpoint-ammo-status",
            loaded=self._loaded_ammunition(player, weapon),
            capacity=weapon.magazine_capacity,
            reserve=reserve_units,
            unit=Localization.get(
                locale,
                weapon.reserve_unit_name_key,
                count=reserve_units,
            ),
        )

    @staticmethod
    def _dropped_weapon_ammunition_summary(
        locale: str,
        dropped_weapon: DroppedWeapon,
        weapon: WeaponProfile,
    ) -> str:
        return Localization.get(
            locale,
            "breachpoint-ammo-status",
            loaded=dropped_weapon.magazine_ammo,
            capacity=weapon.magazine_capacity,
            reserve=dropped_weapon.reserve_units,
            unit=Localization.get(
                locale,
                weapon.reserve_unit_name_key,
                count=dropped_weapon.reserve_units,
            ),
        )

    def _create_dropped_weapon(
        self,
        weapon: WeaponProfile,
        node_id: str,
        point: GridPoint,
        magazine_ammo: int,
        reserve_units: int,
    ) -> DroppedWeapon:
        """Place one physical firearm on the ground with its remaining ammo."""

        dropped_weapon = DroppedWeapon(
            drop_id=self.next_dropped_weapon_id,
            weapon_id=weapon.id,
            node_id=node_id,
            grid_x=point.x,
            grid_y=point.y,
            magazine_ammo=max(0, min(weapon.magazine_capacity, magazine_ammo)),
            reserve_units=max(0, min(weapon.reserve_units, reserve_units)),
        )
        self.next_dropped_weapon_id += 1
        self.dropped_weapons.append(dropped_weapon)
        return dropped_weapon

    def _detach_owned_weapon(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> tuple[int, int]:
        """Remove one slot weapon and return its authoritative ammunition."""

        magazine_ammo = self._loaded_ammunition(player, weapon)
        reserve_units = self._reserve_ammunition_units(player, weapon)
        if weapon.slot == WEAPON_SLOT_PRIMARY:
            player.primary_weapon_id = ""
        else:
            player.sidearm_weapon_id = ""
        player.weapon_magazine_ammo.pop(weapon.id, None)
        player.weapon_reserve_units.pop(weapon.id, None)
        if player.equipped_weapon_id == weapon.id:
            replacement = self._primary_weapon(player) or self._sidearm(player)
            player.equipped_weapon_id = replacement.id if replacement else ""
        return magazine_ammo, reserve_units

    def _drop_owned_weapon(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> DroppedWeapon:
        """Detach and spatially place one weapon carried by a player."""

        magazine_ammo, reserve_units = self._detach_owned_weapon(player, weapon)
        point = self._player_grid_point(player)
        node = self._node(player.position_id)
        if not node:
            raise RuntimeError(f"Unknown tactical area {player.position_id}")
        if not node.is_walkable(point):
            point = node.anchor
        dropped_weapon = self._create_dropped_weapon(
            weapon,
            player.position_id,
            point,
            magazine_ammo,
            reserve_units,
        )
        self._play_weapon_drop_audio(player, weapon, dropped_weapon)
        return dropped_weapon

    def _death_drop_weapon(
        self,
        player: BreachPointPlayer,
    ) -> DroppedWeapon | None:
        """Drop one valuable firearm without flooding the map with free pistols."""

        weapon = self._primary_weapon(player)
        if not weapon:
            sidearm = self._sidearm(player)
            weapon = sidearm if sidearm and sidearm.cost > 0 else None
        if not weapon:
            return None
        return self._drop_owned_weapon(player, weapon)

    def _empty_weapon_error(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> tuple[str, dict] | None:
        """Explain whether an empty weapon can still be reloaded."""

        if self._loaded_ammunition(player, weapon) > 0:
            return None
        user = self.get_user(player)
        locale = user.locale if user else "en"
        error_key = (
            "breachpoint-error-weapon-empty"
            if self._reserve_ammunition_units(player, weapon) > 0
            else "breachpoint-error-no-ammunition"
        )
        return error_key, {"weapon": self._weapon_name(locale, weapon)}

    def _normalize_activation_attack_ledger(
        self,
        player: BreachPointPlayer,
        owned_weapon_ids: set[str],
        valid_player_ids: set[str],
    ) -> int:
        """Bound restored attacks by weapon capacity and the activation AP budget."""

        remaining_action_points = self.rules.action_points_per_activation
        normalized_shots: dict[str, int] = {}
        for weapon_id, shot_count in player.weapon_shots_fired_this_activation.items():
            weapon = get_weapon(weapon_id)
            if (
                weapon_id not in owned_weapon_ids
                or not weapon
                or not isinstance(shot_count, int)
                or isinstance(shot_count, bool)
                or shot_count <= 0
            ):
                continue
            normalized_count = min(
                weapon.shots_per_activation,
                shot_count,
                remaining_action_points // weapon.action_point_cost,
            )
            if normalized_count <= 0:
                continue
            normalized_shots[weapon_id] = normalized_count
            remaining_action_points -= normalized_count * weapon.action_point_cost

        player.weapon_shots_fired_this_activation = normalized_shots
        player.weapon_target_ids_this_activation = {
            weapon_id: list(
                dict.fromkeys(
                    target_id
                    for target_id in target_ids
                    if target_id in valid_player_ids and target_id != player.id
                )
            )[: normalized_shots[weapon_id]]
            for weapon_id, target_ids in player.weapon_target_ids_this_activation.items()
            if weapon_id in normalized_shots and isinstance(target_ids, list)
        }
        player.shots_fired_this_activation = sum(normalized_shots.values())
        return self.rules.action_points_per_activation - remaining_action_points

    def _modified_action_point_cost(
        self,
        player: BreachPointPlayer,
        action_id: str,
        base_cost: int,
    ) -> int:
        modifier = sum(
            equipment.action_point_modifier(action_id)
            * player.equipment_counts.get(equipment.id, 0)
            for equipment in get_purchasable_equipment(player.team_index)
        )
        return max(1, base_cost + modifier)

    def _defuse_action_point_cost(self, player: BreachPointPlayer) -> int:
        return self._modified_action_point_cost(
            player,
            "defuse",
            self.rules.defuse_cost,
        )

    def _held_angle_status(self, locale: str, player: BreachPointPlayer) -> str:
        if not player.held_angle_node_id:
            return Localization.get(locale, "breachpoint-angle-none")
        return Localization.get(
            locale,
            "breachpoint-angle-held",
            location=self._node_name(locale, player.held_angle_node_id),
        )

    @staticmethod
    def _clear_held_angle(player: BreachPointPlayer) -> None:
        player.held_angle_node_id = ""
        player.held_angle_origin_id = ""

    def _available_guard_points(self, player: BreachPointPlayer) -> int:
        """Return defense earned by ending without making an attack."""

        if player.held_angle_node_id or player.shots_fired_this_activation:
            return 0
        saved_points = min(
            self.rules.maximum_evasion_points,
            player.action_points,
        )
        repeated_activations = (
            player.stationary_guard_activations + 1
            if player.guard_anchor_node_id == player.position_id
            else 0
        )
        return max(
            0,
            saved_points
            - repeated_activations * self.rules.stationary_evasion_decay_per_activation,
        )

    @staticmethod
    def _reset_stationary_evasion(player: BreachPointPlayer) -> None:
        player.guard_anchor_node_id = ""
        player.stationary_guard_activations = 0

    def _sidearm(self, player: BreachPointPlayer) -> WeaponProfile | None:
        weapon = get_weapon(player.sidearm_weapon_id)
        if weapon and weapon.slot == WEAPON_SLOT_SIDEARM:
            return weapon
        return None

    def _primary_weapon(self, player: BreachPointPlayer) -> WeaponProfile | None:
        weapon = get_weapon(player.primary_weapon_id)
        if weapon and weapon.slot == WEAPON_SLOT_PRIMARY:
            return weapon
        return None

    def _equipped_weapon(self, player: BreachPointPlayer) -> WeaponProfile | None:
        weapon = get_weapon(player.equipped_weapon_id)
        valid_ids = {
            candidate.id
            for candidate in (self._sidearm(player), self._primary_weapon(player))
            if candidate
        }
        return weapon if weapon and weapon.id in valid_ids else None

    def _can_hold_angle(
        self,
        player: BreachPointPlayer,
        node_id: str,
        weapon: WeaponProfile | None = None,
    ) -> bool:
        weapon = weapon or self._equipped_weapon(player)
        distance = self._combat_distance(player.position_id, node_id)
        return bool(
            weapon
            and self._loaded_ammunition(player, weapon) > 0
            and weapon.hold_action_point_cost > 0
            and distance is not None
            and distance <= weapon.max_range
        )

    def _normalize_area_effects(
        self,
        valid_nodes: dict[str, TacticalNode],
        valid_player_ids: set[str],
    ) -> None:
        """Validate restored area effects and merge duplicate effect/node pairs."""

        normalized: dict[tuple[str, str], AreaEffectState] = {}
        for state in self.area_effects:
            if not isinstance(state, AreaEffectState):
                continue
            if not all(
                isinstance(value, str)
                for value in (
                    state.effect,
                    state.utility_id,
                    state.node_id,
                    state.source_player_id,
                )
            ):
                continue
            utility = get_utility(state.utility_id)
            if (
                not utility
                or utility.effect != state.effect
                or state.effect not in {UTILITY_EFFECT_SMOKE, UTILITY_EFFECT_FIRE}
                or state.node_id not in valid_nodes
                or state.source_player_id not in valid_player_ids
                or not isinstance(state.expires_at_tactical_round, int)
                or isinstance(state.expires_at_tactical_round, bool)
                or state.expires_at_tactical_round <= self.tactical_round
            ):
                continue
            stored_team_indexes = (
                state.known_team_indexes
                if isinstance(state.known_team_indexes, list)
                else []
            )
            known_team_indexes = sorted(
                {
                    team_index
                    for team_index in stored_team_indexes
                    if isinstance(team_index, int)
                    and not isinstance(team_index, bool)
                    and team_index in TEAM_INDEXES
                }
            )
            stored_player_rounds = (
                state.affected_player_rounds
                if isinstance(state.affected_player_rounds, dict)
                else {}
            )
            affected_player_rounds = {
                player_id: round_number
                for player_id, round_number in stored_player_rounds.items()
                if isinstance(player_id, str)
                and player_id in valid_player_ids
                and isinstance(round_number, int)
                and not isinstance(round_number, bool)
                and round_number == self.tactical_round
            }
            key = (state.effect, state.node_id)
            existing = normalized.get(key)
            if not existing:
                normalized[key] = AreaEffectState(
                    effect=state.effect,
                    utility_id=state.utility_id,
                    node_id=state.node_id,
                    source_player_id=state.source_player_id,
                    expires_at_tactical_round=state.expires_at_tactical_round,
                    known_team_indexes=known_team_indexes,
                    affected_player_rounds=affected_player_rounds,
                )
                continue
            existing.known_team_indexes = sorted(
                set(existing.known_team_indexes) | set(known_team_indexes)
            )
            existing.affected_player_rounds.update(affected_player_rounds)
            if state.expires_at_tactical_round >= existing.expires_at_tactical_round:
                existing.utility_id = state.utility_id
                existing.source_player_id = state.source_player_id
                existing.expires_at_tactical_round = state.expires_at_tactical_round
        self.area_effects = list(normalized.values())

    def _area_effect(
        self,
        effect: str,
        node_id: str,
    ) -> AreaEffectState | None:
        return next(
            (
                state
                for state in self.area_effects
                if state.effect == effect
                and state.node_id == node_id
                and state.expires_at_tactical_round > self.tactical_round
            ),
            None,
        )

    def _deploy_area_effect(
        self,
        utility: UtilityProfile,
        node_id: str,
        source_player_id: str,
        visible_team_indexes: set[int],
    ) -> AreaEffectState:
        """Create or refresh one non-stacking spatial effect."""

        state = self._area_effect(utility.effect, node_id)
        expiration = self.tactical_round + utility.duration_tactical_rounds
        if not state:
            state = AreaEffectState(
                effect=utility.effect,
                utility_id=utility.id,
                node_id=node_id,
                source_player_id=source_player_id,
                expires_at_tactical_round=expiration,
            )
            self.area_effects.append(state)
        else:
            state.utility_id = utility.id
            state.source_player_id = source_player_id
            state.expires_at_tactical_round = max(
                state.expires_at_tactical_round,
                expiration,
            )
        for team_index in visible_team_indexes:
            self._remember_area_effect_for_team(state, team_index)
        return state

    def _remove_area_effect(
        self,
        effect: str,
        node_id: str,
        *,
        extinguished: bool = False,
    ) -> AreaEffectState | None:
        state = self._area_effect(effect, node_id)
        if state:
            self.area_effects.remove(state)
            if state.effect == UTILITY_EFFECT_FIRE:
                self._stop_fire_audio(state.node_id, extinguished=extinguished)
        return state

    def _is_smoked(self, node_id: str) -> bool:
        return self._area_effect(UTILITY_EFFECT_SMOKE, node_id) is not None

    def _is_burning(self, node_id: str) -> bool:
        return self._area_effect(UTILITY_EFFECT_FIRE, node_id) is not None

    @staticmethod
    def _remember_area_effect_for_team(
        state: AreaEffectState,
        team_index: int,
    ) -> None:
        if team_index not in TEAM_INDEXES:
            return
        if team_index not in state.known_team_indexes:
            state.known_team_indexes.append(team_index)
            state.known_team_indexes.sort()

    def _team_knows_area_effect(
        self,
        team_index: int,
        effect: str,
        node_id: str,
    ) -> bool:
        state = self._area_effect(effect, node_id)
        return bool(
            state
            and (
                team_index in state.known_team_indexes
                or self._team_can_observe_node_effect(team_index, node_id)
            )
        )

    def _team_knows_smoke(self, team_index: int, node_id: str) -> bool:
        return self._team_knows_area_effect(
            team_index,
            UTILITY_EFFECT_SMOKE,
            node_id,
        )

    def _team_can_observe_node_effect(self, team_index: int, node_id: str) -> bool:
        """Return whether a team can see an area's effect, not through the effect."""

        if not self._node(node_id):
            return False
        for observer in self._players_on_team(team_index, alive_only=True):
            if observer.position_id == node_id:
                return True
            if self._is_smoked(observer.position_id):
                continue
            if self.tactical_map.has_sightline(observer.position_id, node_id):
                return True
        return False

    def _remember_observable_area_effects_for_team(self, team_index: int) -> None:
        """Persist spatial-effect contacts discovered as a team moves."""

        for state in self.area_effects:
            if (
                state.expires_at_tactical_round > self.tactical_round
                and self._team_can_observe_node_effect(team_index, state.node_id)
            ):
                self._remember_area_effect_for_team(state, team_index)

    def _utility_visible_team_indexes(
        self, thrower: BreachPointPlayer, node_id: str
    ) -> set[int]:
        visible_team_indexes = {thrower.team_index}
        visible_team_indexes.update(
            team_index
            for team_index in TEAM_INDEXES
            if team_index != thrower.team_index
            and (
                self._team_can_see_player(team_index, thrower)
                or self._team_can_see_node(team_index, node_id)
            )
        )
        return visible_team_indexes

    def _prune_expired_area_effects(self) -> None:
        expired_states = [
            state
            for state in self.area_effects
            if state.expires_at_tactical_round <= self.tactical_round
        ]
        for state in expired_states:
            self.area_effects.remove(state)
            if state.effect == UTILITY_EFFECT_FIRE:
                self._stop_fire_audio(state.node_id)
            message_key = (
                "breachpoint-smoke-clears"
                if state.effect == UTILITY_EFFECT_SMOKE
                else "breachpoint-fire-burns-out"
            )
            for listener in self.players:
                tactical_listener = self._breach_player(listener)
                user = self.get_user(listener)
                if (
                    not tactical_listener
                    or not user
                    or tactical_listener.is_spectator
                    or tactical_listener.team_index not in state.known_team_indexes
                ):
                    continue
                user.speak_l(
                    message_key,
                    buffer="game",
                    location=self._node_name(user.locale, state.node_id),
                )
        for state in self.area_effects:
            state.affected_player_rounds = {
                player_id: round_number
                for player_id, round_number in state.affected_player_rounds.items()
                if round_number == self.tactical_round
            }

    def _known_area_effect_status(
        self,
        locale: str,
        viewer: BreachPointPlayer | None,
        node_id: str,
    ) -> str:
        if not viewer or viewer.is_spectator:
            return Localization.get(locale, "breachpoint-map-effects-unconfirmed")
        known_effects = []
        for effect, name_key in (
            (UTILITY_EFFECT_SMOKE, "breachpoint-effect-smoke"),
            (UTILITY_EFFECT_FIRE, "breachpoint-effect-fire"),
        ):
            if self._team_knows_area_effect(viewer.team_index, effect, node_id):
                known_effects.append(Localization.get(locale, name_key))
        if known_effects:
            return Localization.get(
                locale,
                "breachpoint-map-effects-active",
                effects=Localization.format_list_and(locale, known_effects),
            )
        if self._team_can_see_node(viewer.team_index, node_id):
            return Localization.get(locale, "breachpoint-map-effects-clear")
        return Localization.get(locale, "breachpoint-map-effects-unconfirmed")

    def _announce_fire_extinguished(
        self,
        node_id: str,
        visible_team_indexes: set[int],
        *,
        message_key: str = "breachpoint-fire-extinguished",
    ) -> None:
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or tactical_listener.team_index not in visible_team_indexes
            ):
                continue
            user.speak_l(
                message_key,
                buffer="game",
                location=self._node_name(user.locale, node_id),
            )

    def _process_fire_contact(self, player: BreachPointPlayer) -> bool:
        """Apply at most one fire tick per player and tactical round."""

        fire = self._area_effect(UTILITY_EFFECT_FIRE, player.position_id)
        if not fire:
            return False
        utility = get_utility(fire.utility_id)
        source = self._breach_player_by_id(fire.source_player_id)
        if not utility or utility.effect != UTILITY_EFFECT_FIRE or not source:
            self.area_effects.remove(fire)
            self._stop_fire_audio(fire.node_id)
            return False
        round_finished = self._damage_players_with_utility(
            source,
            utility,
            [player],
            area_effect=fire,
        )
        if round_finished:
            return True
        if player.eliminated:
            self._end_activation(player)
            return True
        return False

    def _node_distance(self, source_id: str, target_id: str) -> int | None:
        """Return shortest movement distance between two map nodes."""

        if source_id == target_id and self._node(source_id):
            return 0
        if not self._node(source_id) or not self._node(target_id):
            return None
        queue: deque[tuple[str, int]] = deque([(source_id, 0)])
        visited = {source_id}
        while queue:
            node_id, distance = queue.popleft()
            node = self._node(node_id)
            if not node:
                continue
            for neighbor_id in node.adjacent:
                if neighbor_id in visited:
                    continue
                if neighbor_id == target_id:
                    return distance + 1
                visited.add(neighbor_id)
                queue.append((neighbor_id, distance + 1))
        return None

    def _combat_distance(self, source_id: str, target_id: str) -> int | None:
        """Return the coordinate-derived range band for a clear firing lane."""

        return self.tactical_map.combat_distance(source_id, target_id)

    def _weapon_can_reach(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile | None = None,
    ) -> bool:
        weapon = weapon or self._equipped_weapon(shooter)
        distance = self._combat_distance(shooter.position_id, target.position_id)
        return bool(
            weapon
            and distance is not None
            and distance <= weapon.max_range
            and self._can_see(shooter, target)
        )

    def _add_cash(self, player: BreachPointPlayer, amount: int) -> int:
        """Add bounded cash and return the amount actually credited."""

        previous = player.cash
        player.cash = max(
            0,
            min(self.economy.maximum_cash, player.cash + max(0, amount)),
        )
        return player.cash - previous

    def _living_enemy_at(
        self, player: BreachPointPlayer, node_id: str
    ) -> BreachPointPlayer | None:
        return next(
            (
                other
                for other in self.get_active_players()
                if isinstance(other, BreachPointPlayer)
                and not other.eliminated
                and other.team_index != player.team_index
                and other.position_id == node_id
            ),
            None,
        )

    def _is_engaged(self, player: BreachPointPlayer) -> bool:
        """Return whether a living enemy currently shares the player's area."""

        return self._living_enemy_at(player, player.position_id) is not None

    def _movement_action_point_cost(self, player: BreachPointPlayer) -> int:
        """Return the movement cost for the player's current engagement state."""

        return (
            self.rules.disengage_cost
            if self._is_engaged(player)
            else self.rules.move_cost
        )

    def _can_see(self, source: BreachPointPlayer, target: BreachPointPlayer) -> bool:
        if source.eliminated or target.eliminated:
            return False
        if source.position_id == target.position_id:
            return True
        if self._is_smoked(source.position_id) or self._is_smoked(target.position_id):
            return False
        return self.tactical_map.has_sightline(
            source.position_id,
            target.position_id,
        )

    def _team_can_see_node(self, team_index: int, node_id: str) -> bool:
        target_node = self._node(node_id)
        if not target_node:
            return False
        for observer in self._players_on_team(team_index, alive_only=True):
            if observer.position_id == node_id:
                return True
            if self._is_smoked(observer.position_id) or self._is_smoked(node_id):
                continue
            if self.tactical_map.has_sightline(observer.position_id, node_id):
                return True
        return False

    def _team_can_see_player(self, team_index: int, target: BreachPointPlayer) -> bool:
        if target.eliminated:
            return False
        if target.team_index == team_index:
            return True
        return self._team_can_see_node(team_index, target.position_id)

    def _viewer_can_see_player(self, viewer: Player, target: BreachPointPlayer) -> bool:
        tactical_viewer = self._breach_player(viewer)
        if not tactical_viewer or tactical_viewer.is_spectator:
            return False
        return self._team_can_see_player(tactical_viewer.team_index, target)

    def _viewer_knows_player_location(
        self,
        viewer: Player,
        target: BreachPointPlayer,
    ) -> bool:
        """Return whether a status view may show one player's current area.

        Living enemies remain governed by fog of war. Eliminated players stay
        at the area already disclosed by the public kill feed, so hiding that
        same location from later map and roster checks would make the two
        public information surfaces contradict each other.
        """

        return target.eliminated or self._viewer_can_see_player(viewer, target)

    def _target_from_action(self, action_id: str) -> BreachPointPlayer | None:
        prefix = "shoot_"
        if not action_id.startswith(prefix):
            return None
        return self._breach_player_by_id(action_id[len(prefix) :])

    def _node_from_action(self, action_id: str) -> TacticalNode | None:
        prefix = "move_"
        if not action_id.startswith(prefix):
            return None
        return self._node(action_id[len(prefix) :])

    def _is_watched_entry_reaction(self) -> bool:
        return bool(
            self.reaction_window.is_open
            and self.reaction_window.kind == REACTION_WATCHED_ENTRY
        )

    def _reaction_turn_error(self, player: Player) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        if self.status != "playing":
            return "action-not-playing"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        if tactical_player.eliminated:
            return "breachpoint-error-eliminated-action"
        if not self._is_watched_entry_reaction():
            return "breachpoint-error-reaction-unavailable"
        if (
            tactical_player.id != self.reaction_window.responding_player_id
            or not self.current_player
            or self.current_player.id != tactical_player.id
        ):
            responder = self._breach_player_by_id(
                self.reaction_window.responding_player_id
            )
            return (
                "breachpoint-error-reaction-player",
                {"player": responder.name if responder else ""},
            )
        return None

    def _turn_error(self, player: Player) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        if self.status != "playing":
            return "action-not-playing"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        if tactical_player.eliminated:
            return "breachpoint-error-eliminated-action"
        if self.phase != PHASE_COMBAT:
            return "breachpoint-error-buy-phase-active"
        wait_error = self._sequence_wait_error(player)
        if wait_error:
            return wait_error
        if self.round_recovery_player_id:
            recovery_error = self._round_recovery_error(player)
            return recovery_error or "breachpoint-error-round-recovery-only"
        current = self.current_player
        if not current or current.id != tactical_player.id:
            return (
                "breachpoint-error-not-your-turn",
                {"player": current.name if current else ""},
            )
        if self._is_watched_entry_reaction():
            return "breachpoint-error-reaction-action-only"
        return None

    def _sequence_wait_error(
        self,
        player: Player,
    ) -> tuple[str, dict] | None:
        """Describe the gameplay event currently holding the action queue."""

        if not self.is_sequence_gameplay_locked():
            return None
        user = self.get_user(player)
        locale = user.locale if user else "en"
        sequence = next(
            (
                candidate
                for candidate in self.active_sequences
                if candidate.lock_scope
                in {self.SEQUENCE_LOCK_GAMEPLAY, self.SEQUENCE_LOCK_ALL}
            ),
            None,
        )
        if not sequence:
            return None
        payload = sequence.metadata.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        actor = self._breach_player_by_id(str(payload.get("player_id", "")))
        viewer = self._breach_player(player)
        if sequence.tag == MOVEMENT_SEQUENCE_TAG:
            if not actor or not viewer:
                return ("breachpoint-error-wait-event", {})
            if actor.id != viewer.id and actor.team_index != viewer.team_index:
                return (
                    "breachpoint-error-wait-movement-hidden",
                    {"player": actor.name},
                )
            return (
                (
                    "breachpoint-error-wait-movement-you"
                    if actor.id == player.id
                    else "breachpoint-error-wait-movement-player"
                ),
                {
                    "player": actor.name,
                    "location": self._node_name(
                        locale,
                        str(payload.get("destination_node_id", "")),
                    ),
                },
            )
        if sequence.tag == UTILITY_SEQUENCE_TAG:
            if (
                not actor
                or not viewer
                or (
                    actor.id != viewer.id
                    and actor.team_index != viewer.team_index
                )
            ):
                return ("breachpoint-error-wait-event", {})
            utility = get_utility(str(payload.get("utility_id", "")))
            return (
                (
                    "breachpoint-error-wait-utility-you"
                    if actor.id == player.id
                    else "breachpoint-error-wait-utility-player"
                ),
                {
                    "player": actor.name,
                    "utility": (self._utility_name(locale, utility) if utility else ""),
                },
            )
        if sequence.tag == WEAPON_SEQUENCE_TAG:
            weapon = get_weapon(str(payload.get("weapon_id", "")))
            return (
                (
                    "breachpoint-error-wait-weapon-you"
                    if actor and actor.id == player.id
                    else "breachpoint-error-wait-weapon-player"
                ),
                {
                    "player": actor.name if actor else "",
                    "weapon": self._weapon_name(locale, weapon),
                },
            )
        if sequence.tag == ROUND_TRANSITION_SEQUENCE_TAG:
            ticks_remaining = max(
                1,
                sequence.next_tick - self.sound_scheduler_tick,
            )
            return (
                "breachpoint-error-wait-next-round",
                {
                    "seconds": math.ceil(ticks_remaining / TICKS_PER_SECOND),
                },
            )
        if sequence.tag == BUY_COUNTDOWN_SEQUENCE_TAG:
            ticks_remaining = max(
                1,
                sequence.next_tick
                - self.sound_scheduler_tick
                + sum(
                    beat.delay_after_ticks
                    for beat in sequence.beats[sequence.current_index :]
                ),
            )
            return (
                "breachpoint-error-wait-buy-countdown",
                {
                    "seconds": math.ceil(ticks_remaining / TICKS_PER_SECOND),
                },
            )
        if sequence.tag == BOMB_DETONATION_SEQUENCE_TAG:
            ticks_remaining = max(
                1,
                sequence.next_tick - self.sound_scheduler_tick,
            )
            return (
                "breachpoint-error-wait-bomb-detonation",
                {
                    "seconds": math.ceil(ticks_remaining / TICKS_PER_SECOND),
                },
            )
        if sequence.tag == MATCH_RESULT_SEQUENCE_TAG:
            ticks_remaining = max(
                1,
                sequence.next_tick - self.sound_scheduler_tick,
            )
            return (
                "breachpoint-error-wait-match-result",
                {
                    "seconds": math.ceil(ticks_remaining / TICKS_PER_SECOND),
                },
            )
        return ("breachpoint-error-wait-event", {})

    def _buy_turn_error(self, player: Player) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        if self.status != "playing":
            return "action-not-playing"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        if self.phase != PHASE_BUY:
            return "breachpoint-error-buy-phase-ended"
        wait_error = self._sequence_wait_error(player)
        if wait_error:
            return wait_error
        if self.pending_weapon_donation:
            recipient = self._breach_player_by_id(
                self.pending_weapon_donation.recipient_id
            )
            if recipient and recipient.id == tactical_player.id:
                return "breachpoint-error-donation-response-only"
            return (
                "breachpoint-error-donation-response-player",
                {"player": recipient.name if recipient else ""},
            )
        current = self.current_player
        if not current or current.id != tactical_player.id:
            return (
                "breachpoint-error-not-your-buy-turn",
                {"player": current.name if current else ""},
            )
        return None

    def _donation_response_error(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        donation = self.pending_weapon_donation
        if (
            self.status != "playing"
            or self.phase != PHASE_BUY
            or not donation
        ):
            return "breachpoint-error-donation-unavailable"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        recipient = self._breach_player_by_id(donation.recipient_id)
        if (
            not recipient
            or tactical_player.id != recipient.id
            or not self.current_player
            or self.current_player.id != recipient.id
        ):
            return (
                "breachpoint-error-donation-response-player",
                {"player": recipient.name if recipient else ""},
            )
        return None

    def _round_recovery_error(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        """Authorize only the designated survivor during post-elimination recovery."""

        tactical_player = self._breach_player(player)
        if self.status != "playing":
            return "action-not-playing"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        if not self.round_recovery_player_id:
            return "breachpoint-error-round-recovery-unavailable"
        if (
            tactical_player.id != self.round_recovery_player_id
            or not self.current_player
            or self.current_player.id != tactical_player.id
        ):
            survivor = self._breach_player_by_id(self.round_recovery_player_id)
            return (
                "breachpoint-error-round-recovery-player",
                {"player": survivor.name if survivor else ""},
            )
        if tactical_player.eliminated:
            return "breachpoint-error-eliminated-action"
        return None

    def _spend_action_points(self, player: BreachPointPlayer, amount: int) -> bool:
        if amount < 0 or player.action_points < amount:
            return False
        player.action_points -= amount
        return True

    def _resolve_attack(
        self,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        distance: int,
        *,
        damage_percent: int = 100,
        ammunition_used: int | None = None,
    ) -> AttackOutcome:
        """Apply a deterministic projectile group through evasion and armor."""

        outcome = self._preview_attack(
            target,
            weapon,
            distance,
            damage_percent=damage_percent,
            ammunition_used=ammunition_used,
        )
        target.guard_points = 0
        target.armor = max(0, target.armor - outcome.armor_absorbed)
        target.health = max(0, target.health - outcome.health_damage)
        return outcome

    def _preview_attack(
        self,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        distance: int,
        *,
        damage_percent: int = 100,
        ammunition_used: int | None = None,
    ) -> AttackOutcome:
        """Calculate one attack without mutating authoritative player state."""

        distance = max(0, min(weapon.max_range, distance))
        ammunition_used = (
            weapon.ammunition_per_attack
            if ammunition_used is None
            else max(0, min(weapon.ammunition_per_attack, ammunition_used))
        )
        rounds_fired = weapon.projectiles_for_ammunition(ammunition_used)
        full_rounds_on_target = weapon.hits_at_range(distance)
        rounds_on_target = (
            (full_rounds_on_target * rounds_fired + weapon.rounds_per_attack - 1)
            // weapon.rounds_per_attack
            if rounds_fired
            else 0
        )
        damage_percent = max(1, min(100, damage_percent))
        base_damage = (weapon.damage_at_range(distance) * damage_percent + 99) // 100
        guard_points = min(
            self.rules.maximum_evasion_points,
            target.guard_points,
        )
        maximum_evaded_rounds = max(
            0,
            rounds_on_target - weapon.minimum_hits_after_evasion,
        )
        rounds_evaded = min(
            maximum_evaded_rounds,
            guard_points // weapon.evasion_points_per_hit,
        )
        spent_guard_points = rounds_evaded * weapon.evasion_points_per_hit
        remaining_guard_points = guard_points - spent_guard_points
        damaging_rounds = rounds_on_target - rounds_evaded
        projectile_damage = (
            (base_damage * damaging_rounds + full_rounds_on_target - 1)
            // full_rounds_on_target
            if full_rounds_on_target
            else 0
        )
        remaining_damage = max(
            0,
            projectile_damage
            - remaining_guard_points * weapon.evasion_damage_reduction_per_point,
        )
        fully_evaded = remaining_damage == 0

        armor_absorbed = min(
            target.armor,
            remaining_damage * weapon.armor_reduction_percent // 100,
        )
        remaining_damage -= armor_absorbed
        health_damage = min(target.health, remaining_damage)
        return AttackOutcome(
            rounds_fired=rounds_fired,
            rounds_on_target=rounds_on_target,
            rounds_evaded=rounds_evaded,
            health_damage=health_damage,
            armor_absorbed=armor_absorbed,
            fully_evaded=fully_evaded,
        )

    @staticmethod
    def _attack_result(locale: str, outcome: AttackOutcome) -> str:
        if outcome.fully_evaded:
            key = "breachpoint-shot-result-evaded"
        elif outcome.armor_absorbed and outcome.rounds_evaded:
            key = "breachpoint-shot-result-damage-armor-evasion"
        elif outcome.armor_absorbed:
            key = "breachpoint-shot-result-damage-armor"
        elif outcome.rounds_evaded:
            key = "breachpoint-shot-result-damage-evasion"
        else:
            key = "breachpoint-shot-result-damage"
        return Localization.get(
            locale,
            key,
            hits=max(0, outcome.rounds_on_target - outcome.rounds_evaded),
            health_damage=outcome.health_damage,
            armor_absorbed=outcome.armor_absorbed,
            rounds_evaded=outcome.rounds_evaded,
        )

    @staticmethod
    def _utility_damage_result(
        locale: str,
        outcome: UtilityDamageOutcome,
    ) -> str:
        if outcome.armor_absorbed and outcome.evasion_mitigation:
            key = "breachpoint-utility-result-damage-armor-evasion"
        elif outcome.armor_absorbed:
            key = "breachpoint-utility-result-damage-armor"
        elif outcome.evasion_mitigation:
            key = "breachpoint-utility-result-damage-evasion"
        else:
            key = "breachpoint-utility-result-damage"
        return Localization.get(
            locale,
            key,
            health_damage=outcome.health_damage,
            armor_absorbed=outcome.armor_absorbed,
            evasion_mitigation=outcome.evasion_mitigation,
        )

    # ------------------------------------------------------------------
    # Action visibility, validation, and labels
    # ------------------------------------------------------------------

    def _is_reaction_action_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._reaction_turn_error(player) is None
            else Visibility.HIDDEN
        )

    def _is_reaction_shoot_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        error = self._reaction_turn_error(player)
        if error:
            return error
        responder = self._breach_player(player)
        target = self._breach_player_by_id(self.reaction_window.target_player_id)
        node_id = self.reaction_window.context.get("node_id", "")
        weapon = self._equipped_weapon(responder) if responder else None
        if (
            not responder
            or not target
            or target.eliminated
            or target.position_id != node_id
            or responder.held_angle_origin_id != responder.position_id
            or responder.held_angle_node_id != node_id
            or not self._can_hold_angle(responder, node_id, weapon)
            or not self._can_see(responder, target)
        ):
            return "breachpoint-error-reaction-expired"
        return None

    def _is_reaction_pass_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        return self._reaction_turn_error(player)

    def _get_reaction_shoot_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        responder = self._breach_player(player)
        target = self._breach_player_by_id(self.reaction_window.target_player_id)
        weapon = self._equipped_weapon(responder) if responder else None
        return Localization.get(
            locale,
            "breachpoint-action-reaction-shoot",
            player=target.name if target else "",
            weapon=self._weapon_name(locale, weapon),
            location=self._node_name(
                locale, self.reaction_window.context.get("node_id", "")
            ),
            percent=weapon.reaction_damage_percent if weapon else 0,
        )

    def _get_reaction_pass_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "breachpoint-action-reaction-pass")

    def _buy_menu_state(self, player: Player) -> BuyMenuState:
        return self._buy_menu_views.get(player.id, BuyMenuState())

    def _combat_menu_state(self, player: Player) -> CombatMenuState:
        state = self._combat_menu_views.get(player.id, CombatMenuState())
        if state.view not in COMBAT_MENU_VIEWS:
            return CombatMenuState()
        return state

    def _combat_menu_owner(self, player: Player) -> bool:
        """Keep an activation's menu mounted while its action is resolving."""

        tactical_player = self._breach_player(player)
        if (
            self.status != "playing"
            or self.phase != PHASE_COMBAT
            or not tactical_player
            or tactical_player.is_spectator
            or tactical_player.eliminated
            or any(
                self.has_active_sequence(tag=tag)
                for tag in (
                    ROUND_TRANSITION_SEQUENCE_TAG,
                    MATCH_RESULT_SEQUENCE_TAG,
                    BOMB_DETONATION_SEQUENCE_TAG,
                )
            )
        ):
            return False
        if self.round_recovery_player_id:
            return tactical_player.id == self.round_recovery_player_id
        if self.reaction_window.is_open:
            if self.reaction_window.kind == REACTION_WATCHED_ENTRY:
                return tactical_player.id == self.reaction_window.triggering_player_id
            return tactical_player.id in {
                self.reaction_window.triggering_player_id,
                self.reaction_window.responding_player_id,
            }
        return bool(
            self.current_player and self.current_player.id == tactical_player.id
        )

    def _combat_menu_navigation_error(
        self,
        player: Player,
        *,
        action_id: str = "",
    ) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        if not self._combat_menu_owner(player):
            if self.round_recovery_player_id:
                return self._round_recovery_error(player)
            return self._turn_error(player)
        if (
            tactical_player
            and self.reaction_window.is_open
            and tactical_player.id == self.reaction_window.triggering_player_id
        ):
            responder = self._breach_player_by_id(
                self.reaction_window.responding_player_id
            )
            return (
                "breachpoint-error-wait-reaction-response",
                {"player": responder.name if responder else ""},
            )
        state = self._combat_menu_state(player)
        if (
            action_id in COMBAT_MENU_ACTION_VIEWS
            and state.view != COMBAT_MENU_ROOT
        ) or (
            action_id == "combat_menu_back" and state.view == COMBAT_MENU_ROOT
        ) or (
            action_id.startswith(COMBAT_MENU_UTILITY_ACTION_PREFIX)
            and state.view != COMBAT_MENU_UTILITY
        ):
            return "action-not-available"
        if self.round_recovery_player_id:
            if action_id in {"combat_menu_loot", "combat_menu_back"}:
                return self._round_recovery_error(player)
            return "breachpoint-error-round-recovery-only"
        return self._turn_error(player)

    @staticmethod
    def _combat_utility_from_action(action_id: str) -> UtilityProfile | None:
        if not action_id.startswith(COMBAT_MENU_UTILITY_ACTION_PREFIX):
            return None
        return get_utility(action_id.removeprefix(COMBAT_MENU_UTILITY_ACTION_PREFIX))

    def _combat_menu_view_action_ids(
        self,
        player: BreachPointPlayer,
        state: CombatMenuState | None = None,
    ) -> list[str]:
        """Return the semantic leaf rows for one combat submenu."""

        state = state or self._combat_menu_state(player)
        if state.view == COMBAT_MENU_MOVE:
            node = self._node(player.position_id)
            return [f"move_{node_id}" for node_id in node.adjacent] if node else []
        if state.view == COMBAT_MENU_ATTACK:
            return [
                f"shoot_{target.id}"
                for target in self.get_active_players()
                if isinstance(target, BreachPointPlayer)
                and target.team_index != player.team_index
                and self._personally_sees_contact(player, target)
            ]
        if state.view == COMBAT_MENU_UTILITY:
            return [
                f"{COMBAT_MENU_UTILITY_ACTION_PREFIX}{utility.id}"
                for utility in get_purchasable_utilities(player.team_index)
                if player.utility_counts.get(utility.id, 0) > 0
            ]
        if state.view == COMBAT_MENU_UTILITY_TARGETS:
            utility = get_utility(state.utility_id)
            if (
                not utility
                or player.team_index not in utility.allowed_sides
                or player.utility_counts.get(utility.id, 0) <= 0
            ):
                return []
            targets = [
                (
                    self._node_distance(player.position_id, node.id),
                    index,
                    f"throw_{utility.id}_{node.id}",
                )
                for index, node in enumerate(self.tactical_map.nodes)
            ]
            return [
                action_id
                for distance, _, action_id in sorted(
                    targets,
                    key=lambda entry: (
                        entry[0] is None,
                        entry[0] if entry[0] is not None else math.inf,
                        entry[1],
                    ),
                )
                if distance is not None and distance <= utility.throw_range
            ]
        if state.view == COMBAT_MENU_ANGLE:
            weapon = self._equipped_weapon(player)
            if not weapon or weapon.hold_action_point_cost <= 0:
                return []
            return [
                f"hold_angle_{node.id}"
                for node in self.tactical_map.nodes
                if (
                    (distance := self._combat_distance(player.position_id, node.id))
                    is not None
                    and distance <= weapon.max_range
                )
            ]
        if state.view == COMBAT_MENU_OBJECTIVE:
            return (
                ["plant", "pick_up_bomb"]
                if player.team_index == TEAM_TERRORISTS
                else ["defuse"]
            )
        if state.view == COMBAT_MENU_WEAPONS:
            return [
                *(
                    ["equip_primary", "equip_sidearm"]
                    if self._primary_weapon(player)
                    else []
                ),
                "reload",
            ]
        if state.view == COMBAT_MENU_LOOT:
            return [
                self._dropped_weapon_action_id(dropped_weapon)
                for dropped_weapon in self.dropped_weapons
                if dropped_weapon.node_id == player.position_id
                and get_weapon(dropped_weapon.weapon_id)
                and (
                    not self.round_recovery_player_id
                    or dropped_weapon.drop_id in self.round_recovery_drop_ids
                )
            ]
        return []

    def _combat_menu_first_action_id(self, player: BreachPointPlayer) -> str:
        state = self._combat_menu_state(player)
        if state.view == COMBAT_MENU_ROOT:
            if self.round_recovery_player_id:
                return "combat_menu_loot"
            return COMBAT_MENU_SUMMARY_ACTION_ID
        if state.view == COMBAT_MENU_MOVE:
            return "combat_menu_location"
        action_ids = self._combat_menu_view_action_ids(player, state)
        return action_ids[0] if action_ids else "combat_menu_empty"

    def _set_combat_menu_state(
        self,
        player: BreachPointPlayer,
        state: CombatMenuState,
        *,
        return_focus_action_id: str = "",
    ) -> None:
        self._combat_menu_views[player.id] = state
        if player.is_bot:
            return
        self.request_menu_focus(
            player,
            return_focus_action_id or self._combat_menu_first_action_id(player),
        )
        self.refresh_menus(player)

    def _return_to_combat_root(
        self,
        player: BreachPointPlayer,
        opener_action_id: str,
    ) -> None:
        """Restore the parent row before a leaf action starts resolving."""

        self._set_combat_menu_state(
            player,
            CombatMenuState(),
            return_focus_action_id=opener_action_id,
        )

    def _personally_sees_contact(
        self,
        viewer: BreachPointPlayer,
        target: BreachPointPlayer,
    ) -> bool:
        """Apply private menu visibility without borrowing team-shared vision."""

        return bool(
            not viewer.eliminated
            and not target.eliminated
            and viewer.flash_penalty <= 0
            and self._can_see(viewer, target)
        )

    def _visible_contact_details(
        self,
        viewer: BreachPointPlayer,
        node_id: str,
        locale: str,
    ) -> list[str]:
        return [
            Localization.get(
                locale,
                (
                    "breachpoint-visible-contact-teammate"
                    if target.team_index == viewer.team_index
                    else "breachpoint-visible-contact-enemy"
                ),
                player=target.name,
            )
            for target in self.get_active_players()
            if isinstance(target, BreachPointPlayer)
            and target.id != viewer.id
            and target.position_id == node_id
            and self._personally_sees_contact(viewer, target)
        ]

    def _spatial_action_label(
        self,
        player: BreachPointPlayer | None,
        locale: str,
        node_id: str,
        action_label: str,
    ) -> str:
        if not player:
            return action_label
        details: list[str] = []
        if node_id == player.position_id:
            details.append(Localization.get(locale, "breachpoint-current-location"))
        contacts = self._visible_contact_details(player, node_id, locale)
        if contacts:
            details.append(
                Localization.get(
                    locale,
                    "breachpoint-visible-contacts",
                    contacts=Localization.format_list_and(locale, contacts),
                )
            )
        if not details:
            return action_label
        return Localization.get(
            locale,
            "breachpoint-action-spatial-details",
            action=action_label,
            details=Localization.format_list_and(locale, details),
        )

    @staticmethod
    def _buy_category_from_action(action_id: str) -> str:
        return (
            action_id.removeprefix(BUY_MENU_CATEGORY_ACTION_PREFIX)
            if action_id.startswith(BUY_MENU_CATEGORY_ACTION_PREFIX)
            else ""
        )

    def _eligible_donation_recipients(
        self,
        donor: BreachPointPlayer,
    ) -> list[BreachPointPlayer]:
        """Return eligible teammates in stable activation order."""

        return [
            teammate
            for teammate in self.turn_players
            if isinstance(teammate, BreachPointPlayer)
            and teammate.id != donor.id
            and teammate.team_index == donor.team_index
            and not teammate.eliminated
        ]

    def _buy_category_action_ids(
        self,
        player: BreachPointPlayer,
        category_id: str,
    ) -> list[str]:
        if category_id == BUY_CATEGORY_EQUIPMENT:
            return [
                "buy_armor",
                *(
                    f"buy_equipment_{equipment.id}"
                    for equipment in get_purchasable_equipment(player.team_index)
                ),
            ]
        if category_id == BUY_CATEGORY_GRENADES:
            return [
                f"buy_utility_{utility.id}"
                for utility in get_purchasable_utilities(player.team_index)
            ]
        if category_id in WEAPON_BUY_CATEGORIES:
            return [
                f"buy_weapon_{weapon.id}"
                for weapon in get_purchasable_weapons(
                    player.team_index,
                    buy_category=category_id,
                )
            ]
        return []

    def _donation_category_action_ids(
        self,
        donor: BreachPointPlayer,
        recipient_id: str,
        category_id: str,
    ) -> list[str]:
        recipient = self._breach_player_by_id(recipient_id)
        if (
            not recipient
            or recipient.eliminated
            or recipient.team_index != donor.team_index
            or recipient.id == donor.id
            or category_id not in WEAPON_BUY_CATEGORIES
        ):
            return []
        return [
            self._donate_weapon_action_id(weapon, recipient)
            for weapon in get_purchasable_weapons(
                donor.team_index,
                buy_category=category_id,
            )
        ]

    def _buy_menu_shortcuts(self, player: Player) -> dict[str, str]:
        tactical_player = self._breach_player(player)
        if not tactical_player or self._buy_turn_error(player) is not None:
            return {}
        state = self._buy_menu_state(player)
        action_ids: list[str]
        if state.view == BUY_MENU_ROOT:
            action_ids = [
                f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{category_id}"
                for category_id in BUY_CATEGORIES
            ]
        elif state.view == BUY_MENU_CATEGORY:
            action_ids = self._buy_category_action_ids(
                tactical_player,
                state.category_id,
            )
        elif state.view == BUY_MENU_DONATION_CATEGORIES:
            action_ids = [
                f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{category_id}"
                for category_id in BUY_CATEGORIES
                if self._donation_category_action_ids(
                    tactical_player,
                    state.recipient_id,
                    category_id,
                )
            ]
        elif state.view == BUY_MENU_DONATION_ITEMS:
            action_ids = self._donation_category_action_ids(
                tactical_player,
                state.recipient_id,
                state.category_id,
            )
        else:
            action_ids = []
        return dict(zip(BUY_MENU_SHORTCUT_DIGITS, action_ids, strict=False))

    def _numbered_buy_label(
        self,
        player: Player,
        action_id: str,
        label: str,
    ) -> str:
        digit = next(
            (
                shortcut
                for shortcut, target_action_id in self._buy_menu_shortcuts(
                    player
                ).items()
                if target_action_id == action_id
            ),
            "",
        )
        if not digit:
            return label
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(
            locale,
            "breachpoint-buy-shortcut-label",
            number=digit,
            item=label,
        )

    def _is_buy_summary_hidden(self, player: Player) -> Visibility:
        donation = self.pending_weapon_donation
        state = self._buy_menu_state(player)
        waiting_buyer = bool(donation and donation.buyer_id == player.id)
        return (
            Visibility.VISIBLE
            if waiting_buyer
            or self._buy_turn_error(player) is None
            and state.view == BUY_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _is_buy_summary_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        donation = self.pending_weapon_donation
        if donation and donation.buyer_id == player.id:
            recipient = self._breach_player_by_id(donation.recipient_id)
            return (
                "breachpoint-error-donation-response-player",
                {"player": recipient.name if recipient else ""},
            )
        return self._buy_turn_error(player)

    def _is_buy_root_action_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            and self._buy_menu_state(player).view == BUY_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _is_buy_navigation_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        if action_id == "buy_menu_back":
            return (
                None
                if self._is_buy_menu_back_hidden(player) == Visibility.VISIBLE
                else "action-not-available"
            )
        if (action_id or "").startswith(BUY_MENU_DONATION_TARGET_PREFIX):
            return (
                None
                if self._is_donation_target_hidden(
                    player,
                    action_id=action_id,
                )
                == Visibility.VISIBLE
                else "breachpoint-error-donation-unavailable"
            )
        return (
            None
            if self._is_buy_root_action_hidden(player) == Visibility.VISIBLE
            else "action-not-available"
        )

    def _is_refund_menu_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        buyer = self._breach_player(player)
        if buyer and any(
            transaction.player_id == buyer.id
            and self._transaction_is_refundable(buyer, transaction)
            for transaction in self.buy_transactions
        ):
            return None
        return "breachpoint-error-no-refundable-purchases"

    def _is_ground_weapon_menu_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        buyer = self._breach_player(player)
        if buyer and any(
            dropped_weapon.node_id == buyer.position_id
            and get_weapon(dropped_weapon.weapon_id)
            for dropped_weapon in self.dropped_weapons
        ):
            return None
        return "breachpoint-error-no-ground-weapons"

    def _is_donation_menu_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        donor = self._breach_player(player)
        return (
            None
            if donor and self._eligible_donation_recipients(donor)
            else "breachpoint-error-no-eligible-donation-teammates"
        )

    def _is_buy_category_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        category_id = self._buy_category_from_action(action_id or "")
        if self._buy_turn_error(player) is not None or not tactical_player:
            return Visibility.HIDDEN
        state = self._buy_menu_state(player)
        if state.view == BUY_MENU_ROOT:
            return (
                Visibility.VISIBLE
                if category_id in BUY_CATEGORIES
                else Visibility.HIDDEN
            )
        if state.view == BUY_MENU_DONATION_CATEGORIES:
            return (
                Visibility.VISIBLE
                if self._donation_category_action_ids(
                    tactical_player,
                    state.recipient_id,
                    category_id,
                )
                else Visibility.HIDDEN
            )
        return Visibility.HIDDEN

    def _is_buy_category_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        category_id = self._buy_category_from_action(action_id or "")
        if category_id not in BUY_CATEGORIES:
            return "breachpoint-error-buy-category-unavailable"
        return (
            None
            if self._is_buy_category_hidden(player, action_id=action_id)
            == Visibility.VISIBLE
            else "breachpoint-error-buy-category-unavailable"
        )

    def _is_buy_menu_back_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            and self._buy_menu_state(player).view != BUY_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _is_donation_target_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        donor = self._breach_player(player)
        if (
            not donor
            or self._buy_turn_error(player) is not None
            or self._buy_menu_state(player).view != BUY_MENU_DONATION_TARGETS
        ):
            return Visibility.HIDDEN
        target_id = (action_id or "").removeprefix(
            BUY_MENU_DONATION_TARGET_PREFIX
        )
        return (
            Visibility.VISIBLE
            if any(
                teammate.id == target_id
                for teammate in self._eligible_donation_recipients(donor)
            )
            else Visibility.HIDDEN
        )

    def _is_empty_refund_row_hidden(self, player: Player) -> Visibility:
        buyer = self._breach_player(player)
        has_refund = bool(
            buyer
            and any(
                transaction.player_id == buyer.id
                and self._transaction_is_refundable(buyer, transaction)
                for transaction in self.buy_transactions
            )
        )
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            and self._buy_menu_state(player).view == BUY_MENU_REFUNDS
            and not has_refund
            else Visibility.HIDDEN
        )

    def _is_empty_refund_row_enabled(self, player: Player) -> str:
        return "breachpoint-error-no-refundable-purchases"

    def _is_donation_waiting_hidden(self, player: Player) -> Visibility:
        donation = self.pending_weapon_donation
        return (
            Visibility.VISIBLE
            if donation and donation.buyer_id == player.id
            else Visibility.HIDDEN
        )

    def _is_donation_waiting_enabled(
        self,
        player: Player,
    ) -> tuple[str, dict]:
        donation = self.pending_weapon_donation
        recipient = (
            self._breach_player_by_id(donation.recipient_id) if donation else None
        )
        return (
            "breachpoint-error-donation-response-player",
            {"player": recipient.name if recipient else ""},
        )

    def _is_buy_shortcut_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_buy_shortcut_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        digit = (action_id or "").removeprefix(BUY_MENU_SHORTCUT_PREFIX)
        return (
            None
            if digit in self._buy_menu_shortcuts(player)
            else "action-not-available"
        )

    def _get_buy_summary_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        buyer = self._breach_player(player)
        return Localization.get(
            locale,
            "breachpoint-buy-summary",
            cash=buyer.cash if buyer else 0,
            equipped=self._weapon_name(
                locale,
                self._equipped_weapon(buyer) if buyer else None,
            ),
            primary=self._weapon_name(
                locale,
                self._primary_weapon(buyer) if buyer else None,
            ),
            armor=buyer.armor if buyer else 0,
            utility=sum(buyer.utility_counts.values()) if buyer else 0,
        )

    def _get_buy_teammates_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-check-teammates",
        )

    def _get_buy_refunds_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-refunds",
        )

    def _get_buy_ground_weapons_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-ground-weapons",
        )

    def _get_buy_donation_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-for-teammate",
        )

    def _get_buy_category_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        category_id = self._buy_category_from_action(action_id)
        label = Localization.get(
            locale,
            BUY_CATEGORY_LABEL_KEYS.get(
                category_id,
                "breachpoint-buy-category-unknown",
            ),
        )
        return self._numbered_buy_label(player, action_id, label)

    def _get_donation_target_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target_id = action_id.removeprefix(BUY_MENU_DONATION_TARGET_PREFIX)
        target = self._breach_player_by_id(target_id)
        return Localization.get(
            locale,
            "breachpoint-buy-donation-target",
            player=target.name if target else "",
        )

    def _get_empty_refund_row_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-no-refunds",
        )

    def _get_donation_waiting_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        donation = self.pending_weapon_donation
        recipient = (
            self._breach_player_by_id(donation.recipient_id) if donation else None
        )
        weapon = get_weapon(donation.weapon_id) if donation else None
        return Localization.get(
            locale,
            "breachpoint-buy-donation-waiting",
            player=recipient.name if recipient else "",
            weapon=self._weapon_name(locale, weapon),
        )

    def _get_buy_menu_back_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        return Localization.get(
            user.locale if user else "en",
            "breachpoint-buy-back",
        )

    def _is_buy_weapon_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        weapon = self._weapon_from_buy_action(action_id or "")
        if (
            self._buy_turn_error(player) is None
            and tactical_player
            and weapon
            and tactical_player.team_index in weapon.allowed_sides
            and self._buy_menu_state(player)
            == BuyMenuState(BUY_MENU_CATEGORY, weapon.buy_category)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_buy_weapon_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        weapon = self._weapon_from_buy_action(action_id or "")
        if (
            not tactical_player
            or not weapon
            or weapon.cost <= 0
            or tactical_player.team_index not in weapon.allowed_sides
        ):
            return "breachpoint-error-weapon-unavailable"
        if tactical_player.cash < weapon.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": weapon.cost, "cash": tactical_player.cash},
            )
        return None

    def _is_donate_weapon_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        donor = self._breach_player(player)
        details = (
            self._donation_action_details(donor, action_id or "") if donor else None
        )
        weapon, recipient = details if details else (None, None)
        state = self._buy_menu_state(player)
        return (
            Visibility.VISIBLE
            if donor
            and self._buy_turn_error(player) is None
            and weapon
            and recipient
            and state
            == BuyMenuState(
                BUY_MENU_DONATION_ITEMS,
                weapon.buy_category,
                recipient.id,
            )
            else Visibility.HIDDEN
        )

    def _is_donate_weapon_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        donor = self._breach_player(player)
        details = (
            self._donation_action_details(donor, action_id or "") if donor else None
        )
        if not donor or not details:
            return "breachpoint-error-donation-unavailable"
        weapon, _recipient = details
        if donor.cash < weapon.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": weapon.cost, "cash": donor.cash},
            )
        return None

    def _is_weapon_donation_response_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._donation_response_error(player) is None
            else Visibility.HIDDEN
        )

    def _is_weapon_donation_response_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        return self._donation_response_error(player)

    def _is_buy_utility_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        utility = self._utility_from_buy_action(action_id or "")
        if (
            self._buy_turn_error(player) is None
            and tactical_player
            and utility
            and tactical_player.team_index in utility.allowed_sides
            and self._buy_menu_state(player)
            == BuyMenuState(BUY_MENU_CATEGORY, BUY_CATEGORY_GRENADES)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_buy_utility_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        utility = self._utility_from_buy_action(action_id or "")
        if (
            not tactical_player
            or not utility
            or tactical_player.team_index not in utility.allowed_sides
        ):
            return "breachpoint-error-utility-unavailable"
        count = tactical_player.utility_counts.get(utility.id, 0)
        if count >= utility.maximum_carry:
            return (
                "breachpoint-error-utility-full",
                {"maximum": utility.maximum_carry},
            )
        carried = sum(tactical_player.utility_counts.values())
        if carried >= self.rules.maximum_utility_items:
            return (
                "breachpoint-error-utility-total-full",
                {"maximum": self.rules.maximum_utility_items},
            )
        if tactical_player.cash < utility.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": utility.cost, "cash": tactical_player.cash},
            )
        return None

    def _get_buy_item_hover_sound(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | None:
        """Give each purchasable row a stable CS-style navigation cue."""

        del player
        if not action_id or not BUY_ITEM_HOVER_ASSETS:
            return None
        checksum = sum(
            index * byte
            for index, byte in enumerate(action_id.encode("utf-8"), start=1)
        )
        return BUY_ITEM_HOVER_ASSETS[checksum % len(BUY_ITEM_HOVER_ASSETS)]

    def _get_buy_weapon_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        weapon = self._weapon_from_buy_action(action_id)
        label = Localization.get(
            locale,
            "breachpoint-action-buy-weapon",
            weapon=self._weapon_name(locale, weapon),
            cost=weapon.cost if weapon else 0,
            cash=tactical_player.cash if tactical_player else 0,
        )
        return self._numbered_buy_label(player, action_id, label)

    def _get_donate_weapon_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        donor = self._breach_player(player)
        details = self._donation_action_details(donor, action_id) if donor else None
        weapon, recipient = details if details else (None, None)
        label = Localization.get(
            locale,
            "breachpoint-action-donate-weapon",
            weapon=self._weapon_name(locale, weapon),
            player=recipient.name if recipient else "",
            cost=weapon.cost if weapon else 0,
            cash=donor.cash if donor else 0,
        )
        return self._numbered_buy_label(player, action_id, label)

    def _get_weapon_donation_response_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        donation = self.pending_weapon_donation
        buyer = self._breach_player_by_id(donation.buyer_id) if donation else None
        weapon = get_weapon(donation.weapon_id) if donation else None
        key = (
            "breachpoint-action-accept-donation"
            if action_id == "accept_weapon_donation"
            else "breachpoint-action-decline-donation"
        )
        return Localization.get(
            locale,
            key,
            weapon=self._weapon_name(locale, weapon),
            player=buyer.name if buyer else "",
        )

    def _get_buy_utility_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        utility = self._utility_from_buy_action(action_id)
        label = Localization.get(
            locale,
            "breachpoint-action-buy-utility",
            utility=(
                self._utility_name(locale, utility)
                if utility
                else Localization.get(locale, "breachpoint-utility-none")
            ),
            cost=utility.cost if utility else 0,
            count=(
                tactical_player.utility_counts.get(utility.id, 0)
                if tactical_player and utility
                else 0
            ),
            maximum=utility.maximum_carry if utility else 0,
            cash=tactical_player.cash if tactical_player else 0,
        )
        return self._numbered_buy_label(player, action_id, label)

    def _is_buy_equipment_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        equipment = self._equipment_from_buy_action(action_id or "")
        if (
            self._buy_turn_error(player) is None
            and tactical_player
            and equipment
            and tactical_player.team_index in equipment.allowed_sides
            and self._buy_menu_state(player)
            == BuyMenuState(BUY_MENU_CATEGORY, BUY_CATEGORY_EQUIPMENT)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_buy_equipment_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        equipment = self._equipment_from_buy_action(action_id or "")
        if (
            not tactical_player
            or not equipment
            or tactical_player.team_index not in equipment.allowed_sides
        ):
            return "breachpoint-error-equipment-unavailable"
        count = tactical_player.equipment_counts.get(equipment.id, 0)
        if count >= equipment.maximum_carry:
            return (
                "breachpoint-error-equipment-full",
                {"maximum": equipment.maximum_carry},
            )
        if tactical_player.cash < equipment.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": equipment.cost, "cash": tactical_player.cash},
            )
        return None

    def _get_buy_equipment_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        equipment = self._equipment_from_buy_action(action_id)
        label = Localization.get(
            locale,
            "breachpoint-action-buy-equipment",
            equipment=(
                self._equipment_name(locale, equipment)
                if equipment
                else Localization.get(locale, "breachpoint-equipment-none")
            ),
            cost=equipment.cost if equipment else 0,
            cash=tactical_player.cash if tactical_player else 0,
        )
        return self._numbered_buy_label(player, action_id, label)

    def _is_buy_armor_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            and self._buy_menu_state(player)
            == BuyMenuState(BUY_MENU_CATEGORY, BUY_CATEGORY_EQUIPMENT)
            else Visibility.HIDDEN
        )

    def _is_buy_armor_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        if not tactical_player:
            return "breachpoint-error-weapon-unavailable"
        if tactical_player.armor >= self.economy.maximum_armor:
            return "breachpoint-error-armor-owned"
        if tactical_player.cash < self.economy.armor_cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": self.economy.armor_cost, "cash": tactical_player.cash},
            )
        return None

    def _get_buy_armor_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        label = Localization.get(
            locale,
            "breachpoint-action-buy-armor",
            armor=self._armor_name(locale),
            cost=self.economy.armor_cost,
            cash=tactical_player.cash if tactical_player else 0,
        )
        return self._numbered_buy_label(player, action_id, label)

    def _refund_item_name(self, locale: str, item_kind: str, item_id: str) -> str:
        if item_kind == PURCHASE_KIND_WEAPON:
            return self._weapon_name(locale, get_weapon(item_id))
        if item_kind == PURCHASE_KIND_UTILITY:
            utility = get_utility(item_id)
            return (
                self._utility_name(locale, utility)
                if utility
                else Localization.get(locale, "breachpoint-utility-none")
            )
        if item_kind == PURCHASE_KIND_EQUIPMENT:
            equipment = get_equipment(item_id)
            return (
                self._equipment_name(locale, equipment)
                if equipment
                else Localization.get(locale, "breachpoint-equipment-none")
            )
        return self._armor_name(locale)

    def _refundable_item_count(
        self,
        buyer: BreachPointPlayer,
        item_kind: str,
        item_id: str,
    ) -> int:
        if item_kind == PURCHASE_KIND_UTILITY:
            return buyer.utility_counts.get(item_id, 0)
        if item_kind == PURCHASE_KIND_EQUIPMENT:
            return buyer.equipment_counts.get(item_id, 0)
        if item_kind == PURCHASE_KIND_ARMOR:
            return 1
        return sum(
            1
            for transaction in self.buy_transactions
            if transaction.player_id == buyer.id
            and transaction.item_kind == item_kind
            and transaction.item_id == item_id
            and self._transaction_is_refundable(buyer, transaction)
        )

    def _is_refund_purchase_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        buyer = self._breach_player(player)
        details = self._refund_action_details(action_id or "")
        if (
            self._buy_turn_error(player) is not None
            or self._buy_menu_state(player).view != BUY_MENU_REFUNDS
            or not buyer
            or not details
        ):
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self._refundable_transaction(buyer, *details)
            else Visibility.HIDDEN
        )

    def _is_refund_purchase_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._buy_turn_error(player)
        if error:
            return error
        buyer = self._breach_player(player)
        details = self._refund_action_details(action_id or "")
        if buyer and details and self._refundable_transaction(buyer, *details):
            return None
        user = self.get_user(player)
        locale = user.locale if user else "en"
        item_kind, item_id = details or (PURCHASE_KIND_WEAPON, "")
        return (
            "breachpoint-error-refund-unavailable",
            {"item": self._refund_item_name(locale, item_kind, item_id)},
        )

    def _get_refund_purchase_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        buyer = self._breach_player(player)
        details = self._refund_action_details(action_id)
        transaction = (
            self._refundable_transaction(buyer, *details)
            if buyer and details
            else None
        )
        item_kind, item_id = details or (PURCHASE_KIND_WEAPON, "")
        return Localization.get(
            locale,
            "breachpoint-action-refund-item",
            item=self._refund_item_name(locale, item_kind, item_id),
            count=(
                self._refundable_item_count(buyer, item_kind, item_id)
                if buyer
                else 0
            ),
            amount=transaction.cost if transaction else 0,
            cash=buyer.cash if buyer else 0,
        )

    def _is_finish_buy_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        return self._buy_turn_error(player)

    def _is_context_hotkey_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_context_finish_or_end_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        if self.phase == PHASE_BUY:
            return self._is_finish_buy_enabled(player)
        if self.phase == PHASE_COMBAT:
            return self._is_end_turn_enabled(player)
        return "action-not-playing" if self.status != "playing" else None

    def _is_context_menu_back_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        if self.phase == PHASE_BUY:
            if self._buy_menu_state(player).view == BUY_MENU_ROOT:
                return None
            return self._is_buy_navigation_enabled(
                player,
                action_id="buy_menu_back",
            )
        if self.phase == PHASE_COMBAT:
            if (
                not self._combat_menu_owner(player)
                or self._combat_menu_state(player).view == COMBAT_MENU_ROOT
            ):
                return None
            return self._is_combat_menu_navigation_enabled(
                player,
                action_id="combat_menu_back",
            )
        return None

    def _is_finish_buy_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            and self._buy_menu_state(player).view == BUY_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _get_finish_buy_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        return Localization.get(
            locale,
            "breachpoint-action-finish-buy",
            cash=tactical_player.cash if tactical_player else 0,
        )

    def _is_combat_menu_navigation_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        return self._combat_menu_navigation_error(
            player,
            action_id=action_id or "",
        )

    def _is_combat_menu_info_enabled(self, player: Player) -> str:
        return "action-not-available"

    def _is_combat_root_action_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        if (
            not self._combat_menu_owner(player)
            or self._combat_menu_state(player).view != COMBAT_MENU_ROOT
            or action_id not in COMBAT_MENU_ACTION_VIEWS
        ):
            return Visibility.HIDDEN
        if self.round_recovery_player_id and action_id != "combat_menu_loot":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_combat_summary_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and not self.round_recovery_player_id
            and self._combat_menu_state(player).view == COMBAT_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _is_combat_location_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and self._combat_menu_state(player).view == COMBAT_MENU_MOVE
            else Visibility.HIDDEN
        )

    def _is_combat_menu_back_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and self._combat_menu_state(player).view != COMBAT_MENU_ROOT
            else Visibility.HIDDEN
        )

    def _is_combat_empty_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        state = self._combat_menu_state(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and state.view != COMBAT_MENU_ROOT
            and not self._combat_menu_view_action_ids(tactical_player, state)
            else Visibility.HIDDEN
        )

    def _get_combat_menu_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        if not tactical_player:
            return Localization.get(locale, "breachpoint-combat-menu-unavailable")
        labels = {
            "combat_menu_move": "breachpoint-combat-menu-move",
            "combat_menu_attack": "breachpoint-combat-menu-attack",
            "combat_menu_utility": "breachpoint-combat-menu-utility",
            "combat_menu_angle": "breachpoint-combat-menu-angle",
            "combat_menu_objective": "breachpoint-combat-menu-objective",
            "combat_menu_weapons": "breachpoint-combat-menu-weapons",
            "combat_menu_loot": "breachpoint-combat-menu-loot",
        }
        key = labels.get(action_id, "breachpoint-combat-menu-unavailable")
        kwargs: dict[str, int] = {}
        if action_id == "combat_menu_attack":
            kwargs["count"] = sum(
                1
                for target in self.get_active_players()
                if isinstance(target, BreachPointPlayer)
                and target.team_index != tactical_player.team_index
                and self._personally_sees_contact(tactical_player, target)
            )
        elif action_id == "combat_menu_utility":
            kwargs["count"] = sum(tactical_player.utility_counts.values())
        elif action_id == "combat_menu_loot":
            kwargs["count"] = len(
                self._combat_menu_view_action_ids(
                    tactical_player,
                    CombatMenuState(COMBAT_MENU_LOOT),
                )
            )
        return Localization.get(locale, key, **kwargs)

    def _get_combat_summary_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        if not tactical_player:
            return Localization.get(locale, "breachpoint-combat-menu-unavailable")
        contacts = [
            Localization.get(
                locale,
                (
                    "breachpoint-combat-summary-teammate"
                    if target.team_index == tactical_player.team_index
                    else "breachpoint-combat-summary-enemy"
                ),
                player=target.name,
                location=self._node_name(locale, target.position_id),
            )
            for target in self.get_active_players()
            if isinstance(target, BreachPointPlayer)
            and target.id != tactical_player.id
            and self._personally_sees_contact(tactical_player, target)
        ]
        sight = (
            Localization.format_list_and(locale, contacts)
            if contacts
            else Localization.get(locale, "breachpoint-combat-summary-no-contacts")
        )
        return Localization.get(
            locale,
            "breachpoint-combat-summary",
            health=tactical_player.health,
            weapon=self._weapon_name(locale, self._equipped_weapon(tactical_player)),
            sight=sight,
        )

    def _get_combat_location_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        return self._spatial_context(
            locale,
            tactical_player.position_id if tactical_player else "",
        )

    def _get_combat_empty_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        state = self._combat_menu_state(player)
        key = {
            COMBAT_MENU_MOVE: "breachpoint-combat-menu-empty-move",
            COMBAT_MENU_ATTACK: "breachpoint-combat-menu-empty-attack",
            COMBAT_MENU_UTILITY: "breachpoint-combat-menu-empty-utility",
            COMBAT_MENU_UTILITY_TARGETS: "breachpoint-combat-menu-empty-targets",
            COMBAT_MENU_ANGLE: "breachpoint-combat-menu-empty-angle",
            COMBAT_MENU_OBJECTIVE: "breachpoint-combat-menu-empty-objective",
            COMBAT_MENU_WEAPONS: "breachpoint-combat-menu-empty-weapons",
            COMBAT_MENU_LOOT: "breachpoint-combat-menu-empty-loot",
        }.get(state.view, "breachpoint-combat-menu-unavailable")
        return Localization.get(locale, key)

    def _get_combat_menu_back_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "breachpoint-combat-menu-back")

    def _is_combat_utility_choice_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        state = self._combat_menu_state(player)
        if (
            not self._combat_menu_owner(player)
            or not tactical_player
            or state.view != COMBAT_MENU_UTILITY
        ):
            return Visibility.HIDDEN
        utility = self._combat_utility_from_action(action_id or "")
        return (
            Visibility.VISIBLE
            if utility
            and utility in get_purchasable_utilities(tactical_player.team_index)
            and tactical_player.utility_counts.get(utility.id, 0) > 0
            else Visibility.HIDDEN
        )

    def _is_combat_utility_choice_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = self._combat_menu_navigation_error(
            player,
            action_id=action_id or "",
        )
        if error:
            return error
        tactical_player = self._breach_player(player)
        utility = self._combat_utility_from_action(action_id or "")
        if (
            not tactical_player
            or not utility
            or tactical_player.team_index not in utility.allowed_sides
        ):
            return "breachpoint-error-utility-unavailable"
        if tactical_player.utility_counts.get(utility.id, 0) <= 0:
            return "breachpoint-error-utility-empty"
        return None

    def _get_combat_utility_choice_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        utility = self._combat_utility_from_action(action_id)
        return Localization.get(
            locale,
            "breachpoint-combat-menu-utility-choice",
            utility=(
                self._utility_name(locale, utility)
                if utility
                else Localization.get(locale, "breachpoint-utility-none")
            ),
            count=(
                tactical_player.utility_counts.get(utility.id, 0)
                if tactical_player and utility
                else 0
            ),
        )

    def _is_equip_weapon_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and self._combat_menu_state(player).view == COMBAT_MENU_WEAPONS
            and self._primary_weapon(tactical_player)
            else Visibility.HIDDEN
        )

    def _is_equip_weapon_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        if not tactical_player or not self._primary_weapon(tactical_player):
            return "breachpoint-error-no-primary"
        weapon = (
            self._primary_weapon(tactical_player)
            if action_id == "equip_primary"
            else (
                self._sidearm(tactical_player) if action_id == "equip_sidearm" else None
            )
        )
        if not weapon:
            return "breachpoint-error-weapon-unavailable"
        if tactical_player.equipped_weapon_id == weapon.id:
            return "breachpoint-error-weapon-equipped"
        return None

    def _is_reload_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and weapon
            and self._combat_menu_state(player).view == COMBAT_MENU_WEAPONS
            else Visibility.HIDDEN
        )

    def _is_reload_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        if not tactical_player or not weapon:
            return "breachpoint-error-weapon-unavailable"
        user = self.get_user(player)
        locale = user.locale if user else "en"
        weapon_name = self._weapon_name(locale, weapon)
        if self._loaded_ammunition(tactical_player, weapon) >= weapon.magazine_capacity:
            return (
                "breachpoint-error-magazine-full",
                {"weapon": weapon_name},
            )
        if self._reserve_ammunition_units(tactical_player, weapon) <= 0:
            return (
                (
                    "breachpoint-error-no-ammunition"
                    if self._loaded_ammunition(tactical_player, weapon) <= 0
                    else "breachpoint-error-no-reserve-ammo"
                ),
                {"weapon": weapon_name},
            )
        if tactical_player.action_points < weapon.reload_action_point_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": weapon.reload_action_point_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _get_reload_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        return Localization.get(
            locale,
            "breachpoint-action-reload",
            weapon=self._weapon_name(locale, weapon),
            ammunition=self._ammunition_summary(locale, tactical_player, weapon)
            if tactical_player
            else Localization.get(locale, "breachpoint-ammo-none"),
            cost=weapon.reload_action_point_cost if weapon else 0,
        )

    def _get_equip_weapon_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        weapon = None
        if tactical_player:
            weapon = (
                self._primary_weapon(tactical_player)
                if action_id == "equip_primary"
                else self._sidearm(tactical_player)
            )
        return Localization.get(
            locale,
            "breachpoint-action-equip-weapon",
            weapon=self._weapon_name(locale, weapon),
        )

    def _living_players_at_node(self, node_id: str) -> list[BreachPointPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
            and not player.eliminated
            and player.position_id == node_id
        ]

    def _is_pick_up_weapon_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        dropped_weapon = self._dropped_weapon_from_action(action_id or "")
        if (
            self.phase == PHASE_BUY
            and self._buy_menu_state(player).view != BUY_MENU_GROUND
        ):
            return Visibility.HIDDEN
        if self.phase == PHASE_BUY:
            action_visible = self._buy_turn_error(player) is None
        else:
            action_visible = bool(
                self._combat_menu_owner(player)
                and self._combat_menu_state(player).view == COMBAT_MENU_LOOT
            )
        if (
            action_visible
            and tactical_player
            and dropped_weapon
            and dropped_weapon.node_id == tactical_player.position_id
            and (
                not self.round_recovery_player_id
                or dropped_weapon.drop_id in self.round_recovery_drop_ids
            )
            and get_weapon(dropped_weapon.weapon_id)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_pick_up_weapon_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        error = (
            self._buy_turn_error(player)
            if self.phase == PHASE_BUY
            else self._round_recovery_error(player)
            if self.round_recovery_player_id
            else self._turn_error(player)
        )
        if error:
            return error
        tactical_player = self._breach_player(player)
        dropped_weapon = self._dropped_weapon_from_action(action_id or "")
        if (
            not tactical_player
            or not dropped_weapon
            or dropped_weapon.node_id != tactical_player.position_id
            or (
                self.round_recovery_player_id
                and dropped_weapon.drop_id not in self.round_recovery_drop_ids
            )
            or not get_weapon(dropped_weapon.weapon_id)
        ):
            return "breachpoint-error-dropped-weapon-unavailable"
        if (
            self.phase == PHASE_COMBAT
            and tactical_player.action_points < self.rules.weapon_pickup_cost
        ):
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": self.rules.weapon_pickup_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _get_pick_up_weapon_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        dropped_weapon = self._dropped_weapon_from_action(action_id)
        weapon = get_weapon(dropped_weapon.weapon_id) if dropped_weapon else None
        replacement = None
        if tactical_player and weapon:
            replacement = (
                self._primary_weapon(tactical_player)
                if weapon.slot == WEAPON_SLOT_PRIMARY
                else self._sidearm(tactical_player)
            )
        return Localization.get(
            locale,
            (
                (
                    "breachpoint-action-buy-exchange-weapon"
                    if replacement
                    else "breachpoint-action-buy-pick-up-weapon"
                )
                if self.phase == PHASE_BUY
                else (
                    "breachpoint-action-exchange-weapon"
                    if replacement
                    else "breachpoint-action-pick-up-weapon"
                )
            ),
            weapon=self._weapon_name(locale, weapon),
            replaced=self._weapon_name(locale, replacement),
            ammunition=(
                self._dropped_weapon_ammunition_summary(
                    locale,
                    dropped_weapon,
                    weapon,
                )
                if dropped_weapon and weapon
                else Localization.get(locale, "breachpoint-ammo-none")
            ),
            cost=(
                0 if self.phase == PHASE_BUY else self.rules.weapon_pickup_cost
            ),
        )

    def _is_hold_angle_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        state = self._combat_menu_state(player)
        if (
            not self._combat_menu_owner(player)
            or not tactical_player
            or state.view != COMBAT_MENU_ANGLE
        ):
            return Visibility.HIDDEN
        weapon = self._equipped_weapon(tactical_player)
        node_id = self._node_from_hold_action(action_id or "")
        distance = (
            self._combat_distance(tactical_player.position_id, node_id)
            if node_id
            else None
        )
        return (
            Visibility.VISIBLE
            if weapon
            and weapon.hold_action_point_cost > 0
            and distance is not None
            and distance <= weapon.max_range
            else Visibility.HIDDEN
        )

    def _is_hold_angle_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        node_id = self._node_from_hold_action(action_id or "")
        if not tactical_player or not weapon or weapon.hold_action_point_cost <= 0:
            return "breachpoint-error-hold-unavailable"
        if ammunition_error := self._empty_weapon_error(tactical_player, weapon):
            return ammunition_error
        if not self._can_hold_angle(tactical_player, node_id, weapon):
            return "breachpoint-error-illegal-angle"
        if (
            tactical_player.held_angle_origin_id == tactical_player.position_id
            and tactical_player.held_angle_node_id == node_id
        ):
            return "breachpoint-error-angle-held"
        if tactical_player.shots_fired_this_activation:
            return "breachpoint-error-hold-after-firing"
        if tactical_player.action_points < weapon.hold_action_point_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": weapon.hold_action_point_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _get_hold_angle_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        node_id = self._node_from_hold_action(action_id)
        label = Localization.get(
            locale,
            "breachpoint-action-hold-angle",
            weapon=self._weapon_name(locale, weapon),
            location=self._node_name(locale, node_id),
            cost=weapon.hold_action_point_cost if weapon else 0,
        )
        return self._spatial_action_label(
            tactical_player,
            locale,
            node_id,
            label,
        )

    def _is_throw_utility_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        state = self._combat_menu_state(player)
        if (
            not self._combat_menu_owner(player)
            or not tactical_player
            or state.view != COMBAT_MENU_UTILITY_TARGETS
        ):
            return Visibility.HIDDEN
        details = self._throw_action_details(action_id or "")
        utility, node_id = details if details else (None, "")
        if (
            not utility
            or utility.id != state.utility_id
            or tactical_player.team_index not in utility.allowed_sides
            or tactical_player.utility_counts.get(utility.id, 0) <= 0
        ):
            return Visibility.HIDDEN
        distance = self._node_distance(tactical_player.position_id, node_id)
        return (
            Visibility.VISIBLE
            if distance is not None
            and distance <= utility.throw_range
            else Visibility.HIDDEN
        )

    def _is_throw_utility_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        details = self._throw_action_details(action_id or "")
        if not tactical_player or not details:
            return "breachpoint-error-utility-unavailable"
        utility, node_id = details
        if tactical_player.team_index not in utility.allowed_sides:
            return "breachpoint-error-utility-unavailable"
        if tactical_player.utility_counts.get(utility.id, 0) <= 0:
            return "breachpoint-error-utility-empty"
        distance = self._node_distance(tactical_player.position_id, node_id)
        if distance is None or distance > utility.throw_range:
            return (
                "breachpoint-error-utility-range",
                {"range": utility.throw_range},
            )
        if (
            utility.effect == UTILITY_EFFECT_SMOKE
            and self._is_smoked(node_id)
            and self._team_knows_smoke(tactical_player.team_index, node_id)
        ):
            return "breachpoint-error-smoke-active"
        if (
            utility.effect == UTILITY_EFFECT_FIRE
            and self._is_burning(node_id)
            and self._team_knows_area_effect(
                tactical_player.team_index,
                UTILITY_EFFECT_FIRE,
                node_id,
            )
        ):
            return "breachpoint-error-fire-active"
        if tactical_player.action_points < utility.action_point_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": utility.action_point_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _get_throw_utility_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        details = self._throw_action_details(action_id)
        utility, node_id = details if details else (None, "")
        label = Localization.get(
            locale,
            "breachpoint-action-throw-utility",
            utility=(
                self._utility_name(locale, utility)
                if utility
                else Localization.get(locale, "breachpoint-utility-none")
            ),
            location=self._node_name(locale, node_id),
            cost=utility.action_point_cost if utility else 0,
            count=(
                tactical_player.utility_counts.get(utility.id, 0)
                if tactical_player and utility
                else 0
            ),
        )
        return self._spatial_action_label(
            tactical_player,
            locale,
            node_id,
            label,
        )

    def _get_end_turn_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if self.round_recovery_player_id:
            return Localization.get(locale, "breachpoint-action-skip-round-recovery")
        tactical_player = self._breach_player(player)
        guard = self._available_guard_points(tactical_player) if tactical_player else 0
        return Localization.get(
            locale,
            "breachpoint-action-end-turn",
            guard=min(self.rules.maximum_evasion_points, guard),
        )

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        state = self._combat_menu_state(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and (
                state.view == COMBAT_MENU_ROOT
                or self.round_recovery_player_id
                and state.view == COMBAT_MENU_LOOT
            )
            else Visibility.HIDDEN
        )

    def _is_move_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        node = self._node_from_action(action_id or "")
        state = self._combat_menu_state(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and node
            and state.view == COMBAT_MENU_MOVE
            and action_id in self._combat_menu_view_action_ids(tactical_player, state)
            else Visibility.HIDDEN
        )

    def _is_move_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        node = self._node_from_action(action_id or "")
        current_node = (
            self._node(tactical_player.position_id) if tactical_player else None
        )
        if (
            not tactical_player
            or not node
            or not current_node
            or node.id not in current_node.adjacent
        ):
            return "breachpoint-error-illegal-move"
        movement_cost = self._movement_action_point_cost(tactical_player)
        if tactical_player.action_points < movement_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": movement_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        enemy = self._living_enemy_at(tactical_player, node.id)
        if enemy and not self.rules.allow_contested_entry:
            if not self._team_can_see_player(tactical_player.team_index, enemy):
                return "breachpoint-error-concealed-blocks-move"
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return (
                "breachpoint-error-enemy-blocks-move",
                {"player": enemy.name, "location": self._node_name(locale, node.id)},
            )
        return None

    def _get_move_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        node = self._node_from_action(action_id)
        fire_known = bool(
            tactical_player
            and node
            and self._team_knows_area_effect(
                tactical_player.team_index,
                UTILITY_EFFECT_FIRE,
                node.id,
            )
        )
        engaged = bool(tactical_player and self._is_engaged(tactical_player))
        label = Localization.get(
            locale,
            (
                "breachpoint-action-disengage-fire"
                if engaged and fire_known
                else "breachpoint-action-disengage"
                if engaged
                else "breachpoint-action-move-fire"
                if fire_known
                else "breachpoint-action-move"
            ),
            location=self._node_name(locale, node.id if node else ""),
            cost=(
                self._movement_action_point_cost(tactical_player)
                if tactical_player
                else self.rules.move_cost
            ),
        )
        return self._spatial_action_label(
            tactical_player,
            locale,
            node.id if node else "",
            label,
        )

    def _is_shoot_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        target = self._target_from_action(action_id or "")
        state = self._combat_menu_state(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and target
            and state.view == COMBAT_MENU_ATTACK
            and action_id in self._combat_menu_view_action_ids(tactical_player, state)
            else Visibility.HIDDEN
        )

    def _is_shoot_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        target = self._target_from_action(action_id or "")
        if not tactical_player or not target or target.is_spectator:
            return "breachpoint-error-target-unavailable"
        if target.team_index == tactical_player.team_index:
            return "breachpoint-error-friendly-fire"
        if target.eliminated:
            return ("breachpoint-error-target-eliminated", {"player": target.name})
        if not self._can_see(tactical_player, target):
            return ("breachpoint-error-no-line-of-sight", {"player": target.name})
        weapon = self._equipped_weapon(tactical_player)
        if not weapon:
            return "breachpoint-error-weapon-unavailable"
        if ammunition_error := self._empty_weapon_error(tactical_player, weapon):
            return ammunition_error
        distance = self._combat_distance(
            tactical_player.position_id,
            target.position_id,
        )
        if distance is None or distance > weapon.max_range:
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return (
                "breachpoint-error-target-out-of-range",
                {
                    "player": target.name,
                    "weapon": self._weapon_name(locale, weapon),
                    "range": weapon.max_range,
                },
            )
        if weapon.requires_aim and (
            tactical_player.held_angle_origin_id != tactical_player.position_id
            or tactical_player.held_angle_node_id != target.position_id
        ):
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return (
                "breachpoint-error-aim-required",
                {
                    "player": target.name,
                    "weapon": self._weapon_name(locale, weapon),
                },
            )
        if (
            not weapon.can_repeat_target
            and target.id
            in tactical_player.weapon_target_ids_this_activation.get(weapon.id, [])
        ):
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return (
                "breachpoint-error-target-already-fired",
                {
                    "player": target.name,
                    "weapon": self._weapon_name(locale, weapon),
                },
            )
        if (
            tactical_player.weapon_shots_fired_this_activation.get(weapon.id, 0)
            >= weapon.shots_per_activation
        ):
            return "breachpoint-error-already-fired"
        if tactical_player.action_points < weapon.action_point_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": weapon.action_point_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _get_shoot_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target = self._target_from_action(action_id)
        if not target:
            return Localization.get(locale, "breachpoint-action-shoot-unavailable")
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        return Localization.get(
            locale,
            "breachpoint-action-shoot",
            player=target.name,
            location=self._node_name(locale, target.position_id),
            health=target.health,
            armor=target.armor,
            guard=target.guard_points,
            weapon=self._weapon_name(locale, weapon),
            ammunition=self._ammunition_summary(locale, tactical_player, weapon)
            if tactical_player
            else Localization.get(locale, "breachpoint-ammo-none"),
            strength=Localization.get(
                locale,
                (
                    "breachpoint-shot-strength-full"
                    if not tactical_player
                    or tactical_player.shots_fired_this_activation == 0
                    else "breachpoint-shot-strength-followup"
                ),
                percent=weapon.followup_damage_percent if weapon else 100,
            ),
            cost=weapon.action_point_cost if weapon else 0,
        )

    def _get_objective_action_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        action_data = {
            "plant": (
                "breachpoint-action-plant",
                self.rules.plant_cost,
            ),
            "defuse": (
                "breachpoint-action-defuse",
                (
                    self._defuse_action_point_cost(tactical_player)
                    if tactical_player
                    else self.rules.defuse_cost
                ),
            ),
            "pick_up_bomb": (
                "breachpoint-action-pickup",
                self.rules.bomb_pickup_cost,
            ),
        }
        key, cost = action_data.get(
            action_id,
            ("breachpoint-action-shoot-unavailable", 0),
        )
        return Localization.get(locale, key, cost=cost)

    def _is_plant_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and tactical_player.team_index == TEAM_TERRORISTS
            and self._combat_menu_state(player).view == COMBAT_MENU_OBJECTIVE
            else Visibility.HIDDEN
        )

    def _is_plant_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        if not tactical_player or tactical_player.team_index != TEAM_TERRORISTS:
            return "breachpoint-error-terrorists-only"
        if (
            self.bomb_state != BOMB_CARRIED
            or tactical_player.id != self.bomb_carrier_id
        ):
            return "breachpoint-error-not-carrying-bomb"
        node = self._node(tactical_player.position_id)
        if not node or not node.bomb_site:
            return "breachpoint-error-not-at-bomb-site"
        if tactical_player.action_points < self.rules.plant_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": self.rules.plant_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _is_defuse_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and tactical_player.team_index == TEAM_COUNTER_TERRORISTS
            and self._combat_menu_state(player).view == COMBAT_MENU_OBJECTIVE
            else Visibility.HIDDEN
        )

    def _is_defuse_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        if not tactical_player or tactical_player.team_index != TEAM_COUNTER_TERRORISTS:
            return "breachpoint-error-counter-terrorists-only"
        if self.bomb_state != BOMB_PLANTED:
            return "breachpoint-error-bomb-not-planted"
        if self.defusing_player_id:
            return "breachpoint-error-defuse-in-progress"
        if tactical_player.position_id != self.bomb_location_id:
            return "breachpoint-error-not-at-planted-bomb"
        defuse_cost = self._defuse_action_point_cost(tactical_player)
        if tactical_player.action_points < defuse_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": defuse_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _is_pick_up_bomb_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        return (
            Visibility.VISIBLE
            if self._combat_menu_owner(player)
            and tactical_player
            and tactical_player.team_index == TEAM_TERRORISTS
            and self._combat_menu_state(player).view == COMBAT_MENU_OBJECTIVE
            else Visibility.HIDDEN
        )

    def _is_pick_up_bomb_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        if not tactical_player or tactical_player.team_index != TEAM_TERRORISTS:
            return "breachpoint-error-terrorists-only"
        if self.bomb_state != BOMB_DROPPED:
            return "breachpoint-error-bomb-not-dropped"
        if tactical_player.position_id != self.bomb_location_id:
            return "breachpoint-error-not-at-dropped-bomb"
        if tactical_player.action_points < self.rules.bomb_pickup_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": self.rules.bomb_pickup_cost,
                    "remaining": tactical_player.action_points,
                },
            )
        return None

    def _is_end_turn_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if self.round_recovery_player_id:
            return self._round_recovery_error(player)
        return self._turn_error(player)

    def _information_action_error(self) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _information_action_visibility(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.is_touch_player(player) else Visibility.HIDDEN

    def _is_read_position_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_position_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_vitals_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_vitals_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_map_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_map_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_teammates_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_teammates_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_enemies_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_enemies_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_bomb_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_bomb_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        if self.status == "playing" and self.is_touch_player(player):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        if self.is_touch_player(player):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        if self.status == "playing" and self.is_touch_player(player):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    # ------------------------------------------------------------------
    # Gameplay actions
    # ------------------------------------------------------------------

    def _focus_buy_menu_first(self, player: BreachPointPlayer) -> None:
        """Focus the first row when entering a buy menu or submenu."""

        if player.is_bot:
            return
        donation = self.pending_weapon_donation
        if donation and donation.buyer_id == player.id:
            self.request_menu_focus(player, "buy_menu_summary")
            return
        state = self._buy_menu_state(player)
        action_id = ""
        if state.view == BUY_MENU_ROOT:
            action_id = "buy_menu_summary"
        elif state.view == BUY_MENU_CATEGORY:
            action_ids = self._buy_category_action_ids(player, state.category_id)
            action_id = action_ids[0] if action_ids else "buy_menu_back"
        elif state.view == BUY_MENU_GROUND:
            ground_weapon = next(
                (
                    dropped_weapon
                    for dropped_weapon in self.dropped_weapons
                    if dropped_weapon.node_id == player.position_id
                    and get_weapon(dropped_weapon.weapon_id)
                ),
                None,
            )
            action_id = (
                self._dropped_weapon_action_id(ground_weapon)
                if ground_weapon
                else "buy_menu_back"
            )
        elif state.view == BUY_MENU_REFUNDS:
            turn_set = self.get_action_set(player, "turn")
            refund_ids = (
                [
                    candidate_id
                    for candidate_id in turn_set._order
                    if candidate_id.startswith(REFUND_ACTION_PREFIX)
                    and self._is_refund_purchase_hidden(
                        player,
                        action_id=candidate_id,
                    )
                    == Visibility.VISIBLE
                ]
                if turn_set
                else []
            )
            action_id = refund_ids[0] if refund_ids else "buy_menu_empty_refunds"
        elif state.view == BUY_MENU_DONATION_TARGETS:
            recipients = self._eligible_donation_recipients(player)
            action_id = (
                f"{BUY_MENU_DONATION_TARGET_PREFIX}{recipients[0].id}"
                if recipients
                else "buy_menu_back"
            )
        elif state.view == BUY_MENU_DONATION_CATEGORIES:
            action_id = next(
                (
                    f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{category_id}"
                    for category_id in BUY_CATEGORIES
                    if self._donation_category_action_ids(
                        player,
                        state.recipient_id,
                        category_id,
                    )
                ),
                "buy_menu_back",
            )
        elif state.view == BUY_MENU_DONATION_ITEMS:
            action_ids = self._donation_category_action_ids(
                player,
                state.recipient_id,
                state.category_id,
            )
            action_id = action_ids[0] if action_ids else "buy_menu_back"
        if action_id:
            self.request_menu_focus(player, action_id)

    def _set_buy_menu_state(
        self,
        player: BreachPointPlayer,
        state: BuyMenuState,
        *,
        return_focus_action_id: str = "",
    ) -> None:
        self._buy_menu_views[player.id] = state
        if return_focus_action_id and not player.is_bot:
            self.request_menu_focus(player, return_focus_action_id)
        else:
            self._focus_buy_menu_first(player)

    def _buy_menu_parent(
        self,
        player: BreachPointPlayer,
        state: BuyMenuState,
    ) -> tuple[BuyMenuState, str]:
        """Return a submenu's parent and the row that opened it."""

        if state.view == BUY_MENU_CATEGORY:
            return (
                BuyMenuState(),
                f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{state.category_id}",
            )
        if state.view == BUY_MENU_GROUND:
            return BuyMenuState(), "buy_menu_ground_weapons"
        if state.view == BUY_MENU_REFUNDS:
            return BuyMenuState(), "buy_menu_refunds"
        if state.view == BUY_MENU_DONATION_TARGETS:
            return BuyMenuState(), "buy_menu_donation"
        if state.view == BUY_MENU_DONATION_ITEMS:
            return (
                BuyMenuState(
                    BUY_MENU_DONATION_CATEGORIES,
                    recipient_id=state.recipient_id,
                ),
                f"{BUY_MENU_CATEGORY_ACTION_PREFIX}{state.category_id}",
            )
        if state.view == BUY_MENU_DONATION_CATEGORIES:
            recipients = self._eligible_donation_recipients(player)
            if len(recipients) > 1:
                return (
                    BuyMenuState(BUY_MENU_DONATION_TARGETS),
                    f"{BUY_MENU_DONATION_TARGET_PREFIX}{state.recipient_id}",
                )
            return BuyMenuState(), "buy_menu_donation"
        return BuyMenuState(), "buy_menu_summary"

    def _buy_summary_lines(
        self,
        player: BreachPointPlayer,
        locale: str,
    ) -> list[str]:
        primary = self._primary_weapon(player)
        sidearm = self._sidearm(player)
        return [
            Localization.get(
                locale,
                "breachpoint-buy-detail-cash",
                cash=player.cash,
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-primary",
                weapon=self._weapon_name(locale, primary),
                ammunition=self._ammunition_summary(locale, player, primary),
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-sidearm",
                weapon=self._weapon_name(locale, sidearm),
                ammunition=self._ammunition_summary(locale, player, sidearm),
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-equipped",
                weapon=self._weapon_name(locale, self._equipped_weapon(player)),
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-armor",
                armor=player.armor,
                maximum=self.economy.maximum_armor,
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-equipment",
                equipment=self._equipment_summary(locale, player),
            ),
            Localization.get(
                locale,
                "breachpoint-buy-detail-utility",
                utility=self._utility_summary(locale, player),
            ),
        ]

    def _action_show_buy_summary(self, player: Player, action_id: str) -> None:
        if self._is_buy_summary_enabled(player):
            return
        buyer = self._breach_player(player)
        user = self.get_user(player)
        if buyer and user:
            self.status_box(buyer, self._buy_summary_lines(buyer, user.locale))

    def _action_show_teammate_buy_info(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_buy_navigation_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        user = self.get_user(player)
        if not buyer or not user:
            return
        teammates = [
            teammate
            for teammate in self.turn_players
            if isinstance(teammate, BreachPointPlayer)
            and teammate.id != buyer.id
            and teammate.team_index == buyer.team_index
        ]
        lines = [
            Localization.get(
                user.locale,
                "breachpoint-buy-teammate-line",
                player=teammate.name,
                cash=teammate.cash,
                primary=self._weapon_name(
                    user.locale,
                    self._primary_weapon(teammate),
                ),
                sidearm=self._weapon_name(
                    user.locale,
                    self._sidearm(teammate),
                ),
                armor=teammate.armor,
                equipment=self._equipment_summary(user.locale, teammate),
                utility=self._utility_summary(user.locale, teammate),
            )
            for teammate in teammates
        ]
        if not lines:
            lines.append(
                Localization.get(
                    user.locale,
                    "breachpoint-buy-no-teammates",
                )
            )
        self.status_box(buyer, lines)

    def _action_open_buy_category(self, player: Player, action_id: str) -> None:
        if self._is_buy_category_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        if not buyer:
            return
        category_id = self._buy_category_from_action(action_id)
        state = self._buy_menu_state(player)
        if state.view == BUY_MENU_DONATION_CATEGORIES:
            self._set_buy_menu_state(
                buyer,
                BuyMenuState(
                    BUY_MENU_DONATION_ITEMS,
                    category_id,
                    state.recipient_id,
                ),
            )
        else:
            self._set_buy_menu_state(
                buyer,
                BuyMenuState(BUY_MENU_CATEGORY, category_id),
            )

    def _action_open_refunds(self, player: Player, action_id: str) -> None:
        if self._is_refund_menu_enabled(player):
            return
        buyer = self._breach_player(player)
        if buyer:
            self._set_buy_menu_state(buyer, BuyMenuState(BUY_MENU_REFUNDS))

    def _action_open_ground_weapons(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_ground_weapon_menu_enabled(player):
            return
        buyer = self._breach_player(player)
        if buyer:
            self._set_buy_menu_state(buyer, BuyMenuState(BUY_MENU_GROUND))

    def _action_open_donation(self, player: Player, action_id: str) -> None:
        if self._is_donation_menu_enabled(player):
            return
        donor = self._breach_player(player)
        if not donor:
            return
        recipients = self._eligible_donation_recipients(donor)
        if len(recipients) == 1:
            state = BuyMenuState(
                BUY_MENU_DONATION_CATEGORIES,
                recipient_id=recipients[0].id,
            )
        else:
            state = BuyMenuState(BUY_MENU_DONATION_TARGETS)
        self._set_buy_menu_state(donor, state)

    def _action_open_donation_target(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_buy_navigation_enabled(player, action_id=action_id):
            return
        donor = self._breach_player(player)
        if not donor:
            return
        recipient_id = action_id.removeprefix(BUY_MENU_DONATION_TARGET_PREFIX)
        self._set_buy_menu_state(
            donor,
            BuyMenuState(
                BUY_MENU_DONATION_CATEGORIES,
                recipient_id=recipient_id,
            ),
        )

    def _action_buy_menu_back(self, player: Player, action_id: str) -> None:
        if self._is_buy_navigation_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        if not buyer:
            return
        target_state, return_focus_action_id = self._buy_menu_parent(
            buyer,
            self._buy_menu_state(player),
        )
        self._set_buy_menu_state(
            buyer,
            target_state,
            return_focus_action_id=return_focus_action_id,
        )

    def _action_context_menu_back(self, player: Player, action_id: str) -> None:
        if self.phase == PHASE_BUY:
            if self._buy_menu_state(player).view != BUY_MENU_ROOT:
                self._action_buy_menu_back(player, "buy_menu_back")
            return
        if (
            self.phase == PHASE_COMBAT
            and self._combat_menu_owner(player)
            and self._combat_menu_state(player).view != COMBAT_MENU_ROOT
        ):
            self._action_combat_menu_back(player, "combat_menu_back")

    def _action_buy_shortcut(self, player: Player, action_id: str) -> None:
        if self._is_buy_shortcut_enabled(player, action_id=action_id):
            return
        digit = action_id.removeprefix(BUY_MENU_SHORTCUT_PREFIX)
        target_action_id = self._buy_menu_shortcuts(player).get(digit)
        if target_action_id:
            self.execute_action(player, target_action_id)

    @staticmethod
    def _action_buy_menu_noop(player: Player, action_id: str) -> None:
        return

    def _action_open_combat_menu(self, player: Player, action_id: str) -> None:
        if self._is_combat_menu_navigation_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        view = COMBAT_MENU_ACTION_VIEWS.get(action_id)
        if tactical_player and view:
            self._set_combat_menu_state(
                tactical_player,
                CombatMenuState(view),
            )

    def _action_open_combat_utility_targets(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_combat_utility_choice_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        utility = self._combat_utility_from_action(action_id)
        if tactical_player and utility:
            self._set_combat_menu_state(
                tactical_player,
                CombatMenuState(COMBAT_MENU_UTILITY_TARGETS, utility.id),
            )

    def _action_combat_menu_back(self, player: Player, action_id: str) -> None:
        if self._is_combat_menu_navigation_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        if not tactical_player:
            return
        state = self._combat_menu_state(player)
        if state.view == COMBAT_MENU_UTILITY_TARGETS:
            target_state = CombatMenuState(COMBAT_MENU_UTILITY)
            return_focus_action_id = (
                f"{COMBAT_MENU_UTILITY_ACTION_PREFIX}{state.utility_id}"
            )
        else:
            target_state = CombatMenuState()
            return_focus_action_id = COMBAT_MENU_VIEW_OPENERS.get(
                state.view,
                COMBAT_MENU_ROOT_ACTION_IDS[0],
            )
        self._set_combat_menu_state(
            tactical_player,
            target_state,
            return_focus_action_id=return_focus_action_id,
        )

    @staticmethod
    def _action_combat_menu_noop(player: Player, action_id: str) -> None:
        return

    def _action_reaction_shoot(self, player: Player, action_id: str) -> None:
        if self._is_reaction_shoot_enabled(player):
            return
        responder = self._breach_player(player)
        target = self._breach_player_by_id(self.reaction_window.target_player_id)
        weapon = self._equipped_weapon(responder) if responder else None
        if not responder or not target or not weapon:
            return
        if not self._perform_attack(
            responder,
            target,
            weapon,
            damage_percent=weapon.reaction_damage_percent,
            resume_mode="reaction",
        ):
            self._finish_watched_entry_reaction()

    def _action_reaction_pass(self, player: Player, action_id: str) -> None:
        if self._is_reaction_pass_enabled(player):
            return
        responder = self._breach_player(player)
        target = self._breach_player_by_id(self.reaction_window.target_player_id)
        if not responder:
            return
        for listener in (responder, target):
            if not listener:
                continue
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                (
                    "breachpoint-reaction-pass-you"
                    if listener.id == responder.id
                    else "breachpoint-reaction-pass-target"
                ),
                buffer="game",
                player=responder.name,
            )
        self._finish_watched_entry_reaction()

    def _action_buy_weapon(self, player: Player, action_id: str) -> None:
        if self._is_buy_weapon_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        weapon = self._weapon_from_buy_action(action_id)
        user = self.get_user(player)
        if not buyer or not weapon or not user:
            return
        buyer.cash -= weapon.cost
        replacement = (
            self._primary_weapon(buyer)
            if weapon.slot == WEAPON_SLOT_PRIMARY
            else self._sidearm(buyer)
        )
        if replacement:
            dropped_weapon = self._drop_owned_weapon(buyer, replacement)
            self._link_purchased_weapon_drop(buyer, replacement, dropped_weapon)
            self._announce_weapon_drop(buyer, dropped_weapon)
        if weapon.slot == WEAPON_SLOT_PRIMARY:
            buyer.primary_weapon_id = weapon.id
        elif weapon.slot == WEAPON_SLOT_SIDEARM:
            buyer.sidearm_weapon_id = weapon.id
        buyer.equipped_weapon_id = weapon.id
        owned_weapon_ids = {owned.id for owned in self._owned_weapons(buyer)}
        self._normalize_weapon_ammunition(buyer, owned_weapon_ids)
        self._set_full_weapon_ammunition(buyer, weapon)
        self._record_buy_transaction(
            buyer,
            PURCHASE_KIND_WEAPON,
            weapon.id,
            weapon.cost,
        )
        self._play_item_pickup_audio(buyer, "weapon", "ammo", local_only=True)
        user.speak_l(
            "breachpoint-buy-weapon-complete",
            buffer="game",
            weapon=self._weapon_name(user.locale, weapon),
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
        BotHelper.jolt_bot(buyer)

    def _action_donate_weapon(self, player: Player, action_id: str) -> None:
        if self._is_donate_weapon_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        details = self._donation_action_details(buyer, action_id) if buyer else None
        if not buyer or not details:
            return
        weapon, recipient = details
        buyer.cash -= weapon.cost
        self.pending_weapon_donation = PendingWeaponDonation(
            buyer_id=buyer.id,
            recipient_id=recipient.id,
            weapon_id=weapon.id,
            cost=weapon.cost,
        )
        self.current_player = recipient
        self._play_turn_notification(recipient)
        self._play_item_pickup_audio(buyer, "weapon", local_only=True)
        buyer_user = self.get_user(buyer)
        if buyer_user:
            buyer_user.speak_l(
                "breachpoint-donation-offered-buyer",
                buffer="game",
                weapon=self._weapon_name(buyer_user.locale, weapon),
                player=recipient.name,
                cash=buyer.cash,
            )
        recipient_user = self.get_user(recipient)
        if recipient_user:
            recipient_user.speak_l(
                "breachpoint-donation-offered-recipient",
                buffer="game",
                player=buyer.name,
                weapon=self._weapon_name(recipient_user.locale, weapon),
            )
        self.request_menu_focus(recipient, "accept_weapon_donation")
        self.refresh_menus()
        BotHelper.jolt_bot(recipient)

    def _action_accept_weapon_donation(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_weapon_donation_response_enabled(player):
            return
        donation = self.pending_weapon_donation
        recipient = self._breach_player(player)
        buyer = self._breach_player_by_id(donation.buyer_id) if donation else None
        weapon = get_weapon(donation.weapon_id) if donation else None
        if not donation or not recipient or not buyer or not weapon:
            return

        replacement = (
            self._primary_weapon(recipient)
            if weapon.slot == WEAPON_SLOT_PRIMARY
            else self._sidearm(recipient)
        )
        if replacement:
            dropped_weapon = self._drop_owned_weapon(recipient, replacement)
            self._link_purchased_weapon_drop(
                recipient,
                replacement,
                dropped_weapon,
            )
            self._announce_weapon_drop(recipient, dropped_weapon)
        if weapon.slot == WEAPON_SLOT_PRIMARY:
            recipient.primary_weapon_id = weapon.id
        else:
            recipient.sidearm_weapon_id = weapon.id
        recipient.equipped_weapon_id = weapon.id
        self._normalize_weapon_ammunition(
            recipient,
            {owned.id for owned in self._owned_weapons(recipient)},
        )
        self._set_full_weapon_ammunition(recipient, weapon)
        self.pending_weapon_donation = None
        self.current_player = buyer
        self._play_item_pickup_audio(
            recipient,
            "weapon",
            "ammo",
            local_only=False,
        )

        recipient_user = self.get_user(recipient)
        if recipient_user:
            recipient_user.speak_l(
                "breachpoint-donation-accepted-recipient",
                buffer="game",
                weapon=self._weapon_name(recipient_user.locale, weapon),
                player=buyer.name,
            )
        buyer_user = self.get_user(buyer)
        if buyer_user:
            buyer_user.speak_l(
                "breachpoint-donation-accepted-buyer",
                buffer="game",
                player=recipient.name,
                weapon=self._weapon_name(buyer_user.locale, weapon),
            )
        self.refresh_menus()
        BotHelper.jolt_bot(buyer)

    def _action_decline_weapon_donation(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self._is_weapon_donation_response_enabled(player):
            return
        donation = self.pending_weapon_donation
        recipient = self._breach_player(player)
        buyer = self._breach_player_by_id(donation.buyer_id) if donation else None
        weapon = get_weapon(donation.weapon_id) if donation else None
        if not donation or not recipient or not buyer or not weapon:
            return

        dropped_weapon = self._create_dropped_weapon(
            weapon,
            buyer.position_id,
            self._player_grid_point(buyer),
            weapon.magazine_capacity,
            weapon.reserve_units,
        )
        self._record_buy_transaction(
            buyer,
            PURCHASE_KIND_WEAPON,
            weapon.id,
            donation.cost,
            dropped_weapon_id=dropped_weapon.drop_id,
        )
        self.pending_weapon_donation = None
        self.current_player = buyer
        self._play_weapon_drop_audio(buyer, weapon, dropped_weapon)

        recipient_user = self.get_user(recipient)
        if recipient_user:
            recipient_user.speak_l(
                "breachpoint-donation-declined-recipient",
                buffer="game",
                weapon=self._weapon_name(recipient_user.locale, weapon),
                player=buyer.name,
            )
        buyer_user = self.get_user(buyer)
        if buyer_user:
            buyer_user.speak_l(
                "breachpoint-donation-declined-buyer",
                buffer="game",
                player=recipient.name,
                weapon=self._weapon_name(buyer_user.locale, weapon),
            )
        self.refresh_menus()
        BotHelper.jolt_bot(buyer)

    def _action_buy_utility(self, player: Player, action_id: str) -> None:
        if self._is_buy_utility_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        utility = self._utility_from_buy_action(action_id)
        user = self.get_user(player)
        if not buyer or not utility or not user:
            return
        buyer.cash -= utility.cost
        previous_count = buyer.utility_counts.get(utility.id, 0)
        buyer.utility_counts[utility.id] = previous_count + 1
        self._record_buy_transaction(
            buyer,
            PURCHASE_KIND_UTILITY,
            utility.id,
            utility.cost,
            previous_amount=previous_count,
        )
        self._play_utility_purchase_audio(buyer, utility)
        user.speak_l(
            "breachpoint-buy-utility-complete",
            buffer="game",
            utility=self._utility_name(user.locale, utility),
            count=buyer.utility_counts[utility.id],
            maximum=utility.maximum_carry,
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
        BotHelper.jolt_bot(buyer)

    def _action_buy_equipment(self, player: Player, action_id: str) -> None:
        if self._is_buy_equipment_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        equipment = self._equipment_from_buy_action(action_id)
        user = self.get_user(player)
        if not buyer or not equipment or not user:
            return
        buyer.cash -= equipment.cost
        previous_count = buyer.equipment_counts.get(equipment.id, 0)
        buyer.equipment_counts[equipment.id] = (
            previous_count + 1
        )
        self._record_buy_transaction(
            buyer,
            PURCHASE_KIND_EQUIPMENT,
            equipment.id,
            equipment.cost,
            previous_amount=previous_count,
        )
        self._play_equipment_purchase_audio(buyer, equipment)
        user.speak_l(
            "breachpoint-buy-equipment-complete",
            buffer="game",
            equipment=self._equipment_name(user.locale, equipment),
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
        BotHelper.jolt_bot(buyer)

    def _action_buy_armor(self, player: Player, action_id: str) -> None:
        if self._is_buy_armor_enabled(player):
            return
        buyer = self._breach_player(player)
        user = self.get_user(player)
        if not buyer or not user:
            return
        buyer.cash -= self.economy.armor_cost
        previous_armor = buyer.armor
        buyer.armor = self.economy.maximum_armor
        self._record_buy_transaction(
            buyer,
            PURCHASE_KIND_ARMOR,
            PURCHASE_KIND_ARMOR,
            self.economy.armor_cost,
            previous_amount=previous_armor,
        )
        self._play_item_pickup_audio(buyer, "armor", local_only=True)
        user.speak_l(
            "breachpoint-buy-armor-complete",
            buffer="game",
            armor_name=self._armor_name(user.locale),
            armor=buyer.armor,
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
        BotHelper.jolt_bot(buyer)

    def _action_refund_purchase(self, player: Player, action_id: str) -> None:
        if self._is_refund_purchase_enabled(player, action_id=action_id):
            return
        buyer = self._breach_player(player)
        user = self.get_user(player)
        details = self._refund_action_details(action_id)
        transaction = (
            self._refundable_transaction(buyer, *details)
            if buyer and details
            else None
        )
        if not buyer or not user or not details or not transaction:
            return

        item_kind, item_id = details
        if item_kind == PURCHASE_KIND_WEAPON:
            weapon = get_weapon(item_id)
            if not weapon:
                return
            if transaction.dropped_weapon_id:
                dropped_weapon = next(
                    (
                        dropped
                        for dropped in self.dropped_weapons
                        if dropped.drop_id == transaction.dropped_weapon_id
                        and dropped.weapon_id == weapon.id
                    ),
                    None,
                )
                if not dropped_weapon:
                    return
                self.dropped_weapons.remove(dropped_weapon)
            else:
                owned = (
                    self._primary_weapon(buyer)
                    if weapon.slot == WEAPON_SLOT_PRIMARY
                    else self._sidearm(buyer)
                )
                if not owned or owned.id != weapon.id:
                    return
                self._detach_owned_weapon(buyer, weapon)
        elif item_kind == PURCHASE_KIND_UTILITY:
            buyer.utility_counts[item_id] = transaction.previous_amount
            if transaction.previous_amount == 0:
                buyer.utility_counts.pop(item_id, None)
        elif item_kind == PURCHASE_KIND_EQUIPMENT:
            buyer.equipment_counts[item_id] = transaction.previous_amount
            if transaction.previous_amount == 0:
                buyer.equipment_counts.pop(item_id, None)
        else:
            buyer.armor = transaction.previous_amount

        self.buy_transactions.remove(transaction)
        credited = self._add_cash(buyer, transaction.cost)
        user.speak_l(
            "breachpoint-refund-complete",
            buffer="game",
            item=self._refund_item_name(user.locale, item_kind, item_id),
            amount=credited,
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
        BotHelper.jolt_bot(buyer)

    def _action_finish_buy(self, player: Player, action_id: str) -> None:
        if self._is_finish_buy_enabled(player):
            return
        buyer = self._breach_player(player)
        if not buyer:
            return
        self.buy_ready_player_ids.append(buyer.id)
        self.buy_transactions = [
            transaction
            for transaction in self.buy_transactions
            if transaction.player_id != buyer.id
        ]
        self.broadcast_personal_l(
            buyer,
            "breachpoint-buy-finished-you",
            "breachpoint-buy-finished-player",
            buffer="game",
            cash=buyer.cash,
        )
        next_buyer = next(
            (
                candidate
                for candidate in self.turn_players
                if isinstance(candidate, BreachPointPlayer)
                and not candidate.eliminated
                and candidate.id not in self.buy_ready_player_ids
            ),
            None,
        )
        if not next_buyer:
            self._queue_combat_start_countdown()
            return
        self.current_player = next_buyer
        self._start_buy_turn(next_buyer)
        self.refresh_menus()
        BotHelper.jolt_bot(next_buyer)

    def _action_context_finish_or_end(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        if self.phase == PHASE_BUY:
            self._action_finish_buy(player, "finish_buy")
        elif self.phase == PHASE_COMBAT:
            self._action_end_turn(player, "end_turn")

    def _action_equip_weapon(self, player: Player, action_id: str) -> None:
        if self._is_equip_weapon_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        user = self.get_user(player)
        if not tactical_player or not user:
            return
        weapon = (
            self._primary_weapon(tactical_player)
            if action_id == "equip_primary"
            else self._sidearm(tactical_player)
        )
        if not weapon:
            return
        self._return_to_combat_root(tactical_player, "combat_menu_weapons")
        tactical_player.equipped_weapon_id = weapon.id
        self._clear_held_angle(tactical_player)
        self._play_weapon_equip_audio(tactical_player, weapon)
        user.speak_l(
            "breachpoint-weapon-equipped",
            buffer="game",
            weapon=self._weapon_name(user.locale, weapon),
        )
        self.refresh_menus(tactical_player)
        BotHelper.jolt_bot(tactical_player)

    def _action_pick_up_weapon(self, player: Player, action_id: str) -> None:
        if self._is_pick_up_weapon_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        dropped_weapon = self._dropped_weapon_from_action(action_id)
        weapon = get_weapon(dropped_weapon.weapon_id) if dropped_weapon else None
        if (
            not tactical_player
            or not dropped_weapon
            or not weapon
        ):
            return
        is_buy_pickup = self.phase == PHASE_BUY
        if not is_buy_pickup and not self.round_recovery_player_id:
            self._return_to_combat_root(tactical_player, "combat_menu_loot")
        if not is_buy_pickup and not self._spend_action_points(
            tactical_player,
            self.rules.weapon_pickup_cost,
        ):
            return

        replacement = (
            self._primary_weapon(tactical_player)
            if weapon.slot == WEAPON_SLOT_PRIMARY
            else self._sidearm(tactical_player)
        )
        self.dropped_weapons.remove(dropped_weapon)
        if replacement:
            replacement_drop = self._drop_owned_weapon(tactical_player, replacement)
            if is_buy_pickup:
                self._link_purchased_weapon_drop(
                    tactical_player,
                    replacement,
                    replacement_drop,
                )
        if weapon.slot == WEAPON_SLOT_PRIMARY:
            tactical_player.primary_weapon_id = weapon.id
        else:
            tactical_player.sidearm_weapon_id = weapon.id
        tactical_player.weapon_magazine_ammo[weapon.id] = dropped_weapon.magazine_ammo
        tactical_player.weapon_reserve_units[weapon.id] = dropped_weapon.reserve_units
        tactical_player.equipped_weapon_id = weapon.id
        if is_buy_pickup:
            self._link_purchased_weapon_pickup(tactical_player, dropped_weapon)
        self._clear_held_angle(tactical_player)
        pickup_kinds = ["weapon"]
        if dropped_weapon.magazine_ammo or dropped_weapon.reserve_units:
            pickup_kinds.append("ammo")
        self._play_item_pickup_audio(
            tactical_player,
            *pickup_kinds,
            local_only=False,
        )
        self._announce_weapon_pickup(tactical_player, weapon, replacement)
        if is_buy_pickup:
            self.refresh_menus(tactical_player)
            BotHelper.jolt_bot(tactical_player)
        elif self.round_recovery_player_id == tactical_player.id:
            self._complete_round_recovery(tactical_player)
        else:
            self._finish_action(tactical_player)

    def _action_reload(self, player: Player, action_id: str) -> None:
        if self._is_reload_enabled(player):
            return
        tactical_player = self._breach_player(player)
        user = self.get_user(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        if (
            not tactical_player
            or not user
            or not weapon
            or not self._spend_action_points(
                tactical_player,
                weapon.reload_action_point_cost,
            )
        ):
            return
        self._return_to_combat_root(tactical_player, "combat_menu_weapons")
        self._clear_held_angle(tactical_player)
        loaded, discarded, used_units = self._reload_weapon(
            tactical_player,
            weapon,
        )
        if not used_units:
            tactical_player.action_points += weapon.reload_action_point_cost
            return
        self._play_weapon_reload_audio(tactical_player, weapon, loaded)
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            listener_user = self.get_user(listener)
            if (
                not tactical_listener
                or not listener_user
                or tactical_listener.is_spectator
                or (
                    listener.id != tactical_player.id
                    and tactical_listener.team_index != tactical_player.team_index
                    and not self._viewer_can_see_player(listener, tactical_player)
                )
            ):
                continue
            listener_user.speak_l(
                (
                    (
                        (
                            "breachpoint-reload-magazine-you"
                            if discarded
                            else "breachpoint-reload-empty-magazine-you"
                        )
                        if weapon.discard_loaded_rounds_on_reload
                        else "breachpoint-reload-shells-you"
                    )
                    if listener.id == tactical_player.id
                    else "breachpoint-reload-player"
                ),
                buffer="game",
                player=tactical_player.name,
                weapon=self._weapon_name(listener_user.locale, weapon),
                loaded=loaded,
                discarded=discarded,
                ammunition=self._ammunition_summary(
                    listener_user.locale,
                    tactical_player,
                    weapon,
                ),
            )
        self._finish_action(tactical_player)

    def _action_hold_angle(self, player: Player, action_id: str) -> None:
        if self._is_hold_angle_enabled(player, action_id=action_id):
            return
        holder = self._breach_player(player)
        weapon = self._equipped_weapon(holder) if holder else None
        node_id = self._node_from_hold_action(action_id)
        if (
            not holder
            or not weapon
            or not self._spend_action_points(holder, weapon.hold_action_point_cost)
        ):
            return
        self._return_to_combat_root(holder, "combat_menu_angle")
        holder.held_angle_origin_id = holder.position_id
        holder.held_angle_node_id = node_id
        self._play_hold_angle_audio(holder, weapon)
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or tactical_listener.team_index != holder.team_index
            ):
                continue
            user.speak_l(
                (
                    "breachpoint-hold-angle-you"
                    if listener.id == holder.id
                    else "breachpoint-hold-angle-player"
                ),
                buffer="game",
                player=holder.name,
                weapon=self._weapon_name(user.locale, weapon),
                location=self._node_name(user.locale, node_id),
            )
        holder.action_points = 0
        self._end_activation(holder)

    def _action_throw_utility(self, player: Player, action_id: str) -> None:
        if self._is_throw_utility_enabled(player, action_id=action_id):
            return
        thrower = self._breach_player(player)
        details = self._throw_action_details(action_id)
        if not thrower or not details:
            return
        utility, node_id = details
        visible_team_indexes = self._utility_visible_team_indexes(thrower, node_id)
        destination = self._node(node_id)
        if not destination:
            return
        self._return_to_combat_root(thrower, "combat_menu_utility")
        timing = utility_audio_timing(
            utility.id,
            self._player_grid_point(thrower),
            destination.anchor,
        )
        payload = {
            "player_id": thrower.id,
            "utility_id": utility.id,
            "node_id": node_id,
            "travel_ticks": timing.travel_ticks,
            "visible_team_indexes": sorted(visible_team_indexes),
        }
        beats = [
            SequenceBeat.after_audio(
                timing.handling_ticks,
                ops=[
                    SequenceOperation.callback_op(
                        UTILITY_START_CALLBACK,
                        payload,
                    )
                ],
            )
        ]
        timeline_ops: dict[int, list[SequenceOperation]] = {
            0: [
                SequenceOperation.callback_op(
                    UTILITY_FLIGHT_CALLBACK,
                    payload,
                )
            ]
        }
        for index, point in enumerate(timing.bounce_points):
            bounce_payload = {**payload, "bounce_x": point.x, "bounce_y": point.y}
            event_tick = round(
                timing.travel_ticks * (index + 1) / (len(timing.bounce_points) + 1)
            )
            timeline_ops.setdefault(event_tick, []).append(
                SequenceOperation.callback_op(
                    UTILITY_BOUNCE_CALLBACK,
                    bounce_payload,
                )
            )
        if timing.impact_lead_ticks:
            impact_tick = timing.travel_ticks - timing.impact_lead_ticks
            timeline_ops.setdefault(impact_tick, []).append(
                SequenceOperation.callback_op(
                    UTILITY_IMPACT_CALLBACK,
                    payload,
                )
            )
        timeline_ops.setdefault(timing.travel_ticks, []).append(
            SequenceOperation.callback_op(
                UTILITY_RESOLVE_CALLBACK,
                payload,
            )
        )
        event_ticks = sorted(timeline_ops)
        beats.extend(
            SequenceBeat(
                ops=timeline_ops[event_tick],
                delay_after_ticks=(
                    event_ticks[index + 1] - event_tick
                    if index + 1 < len(event_ticks)
                    else 0
                ),
            )
            for index, event_tick in enumerate(event_ticks)
        )
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        UTILITY_FINISH_CALLBACK,
                        payload,
                    )
                ]
            )
        )
        sequence_id = f"{UTILITY_SEQUENCE_TAG}.{thrower.id}"
        self.start_sequence(
            sequence_id,
            beats,
            tag=UTILITY_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"payload": payload, "audio_stage": "handling"},
            replace_existing=False,
        )
        self.refresh_menus()

    def _start_utility_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        thrower = self._breach_player_by_id(str(payload.get("player_id", "")))
        utility = get_utility(str(payload.get("utility_id", "")))
        node_id = str(payload.get("node_id", ""))
        if (
            not thrower
            or not utility
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or self.current_player is not thrower
            or thrower.eliminated
            or not self._node(node_id)
            or thrower.utility_counts.get(utility.id, 0) <= 0
            or not self._spend_action_points(thrower, utility.action_point_cost)
        ):
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        self._clear_held_angle(thrower)
        thrower.utility_counts[utility.id] -= 1
        if not thrower.utility_counts[utility.id]:
            del thrower.utility_counts[utility.id]
        self._play_utility_audio(thrower, utility, node_id)
        self._announce_utility_throw(
            thrower,
            utility,
            node_id,
            {int(index) for index in payload.get("visible_team_indexes", [])},
        )

    def _start_utility_flight_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        sequence = self._get_sequence(sequence_id)
        thrower = self._breach_player_by_id(str(payload.get("player_id", "")))
        utility = get_utility(str(payload.get("utility_id", "")))
        node_id = str(payload.get("node_id", ""))
        travel_ticks = int(payload.get("travel_ticks", 0))
        if (
            not sequence
            or not thrower
            or not utility
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or thrower.eliminated
            or not self._node(node_id)
            or travel_ticks <= 0
        ):
            self._stop_utility_flight_audio(sequence_id)
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        sequence.metadata["audio_stage"] = "flight"
        self._play_utility_release(thrower, utility)
        self._start_utility_flight_audio(
            sequence_id,
            thrower,
            utility,
            node_id,
            travel_ticks,
        )

    def _bounce_utility_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        sequence = self._get_sequence(sequence_id)
        utility = get_utility(str(payload.get("utility_id", "")))
        if not sequence or not utility or self.status != "playing":
            self._stop_utility_flight_audio(sequence_id)
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        point = GridPoint(
            int(payload.get("bounce_x", -1)),
            int(payload.get("bounce_y", -1)),
        )
        if not self.tactical_map.bounds.contains(point):
            self._stop_utility_flight_audio(sequence_id)
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        sequence.metadata["audio_stage"] = "bounce"
        sequence.metadata["audio_x"] = point.x
        sequence.metadata["audio_y"] = point.y
        self._play_utility_bounce(utility.id, point)

    def _impact_utility_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        sequence = self._get_sequence(sequence_id)
        utility = get_utility(str(payload.get("utility_id", "")))
        node = self._node(str(payload.get("node_id", "")))
        if not sequence or not utility or not node or self.status != "playing":
            self._stop_utility_flight_audio(sequence_id)
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        sequence.metadata["audio_stage"] = "impact"
        self._play_utility_impact(utility.id, node.id)

    def _resolve_utility_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        self._stop_utility_flight_audio(sequence_id)
        thrower = self._breach_player_by_id(str(payload.get("player_id", "")))
        utility = get_utility(str(payload.get("utility_id", "")))
        node_id = str(payload.get("node_id", ""))
        if (
            not thrower
            or not utility
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or thrower.eliminated
            or not self._node(node_id)
        ):
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        visible_team_indexes = {
            int(index)
            for index in payload.get("visible_team_indexes", [])
            if int(index) in TEAM_INDEXES
        }
        self._play_utility_detonation(utility.id, node_id)
        round_finished = False
        if utility.effect == UTILITY_EFFECT_SMOKE:
            self._deploy_area_effect(
                utility,
                node_id,
                thrower.id,
                visible_team_indexes,
            )
            extinguished_fire = self._remove_area_effect(
                UTILITY_EFFECT_FIRE,
                node_id,
                extinguished=True,
            )
            if extinguished_fire:
                visible_team_indexes.update(extinguished_fire.known_team_indexes)
                self._announce_fire_extinguished(node_id, visible_team_indexes)
        elif utility.effect == UTILITY_EFFECT_FLASH:
            for target in self.get_active_players():
                tactical_target = self._breach_player(target)
                target_user = self.get_user(target)
                if (
                    not tactical_target
                    or tactical_target.eliminated
                    or tactical_target.position_id != node_id
                    or (
                        tactical_target.id == thrower.id and not utility.affects_thrower
                    )
                ):
                    continue
                tactical_target.flash_penalty = max(
                    tactical_target.flash_penalty,
                    utility.activation_penalty,
                )
                self._clear_held_angle(tactical_target)
                self._play_flash_tinnitus_audio(tactical_target)
                if target_user:
                    target_user.speak_l(
                        "breachpoint-flashed",
                        buffer="game",
                        penalty=tactical_target.flash_penalty,
                    )
        elif utility.effect == UTILITY_EFFECT_EXPLOSIVE:
            round_finished = self._damage_players_with_utility(
                thrower,
                utility,
                self._living_players_at_node(node_id),
            )
        elif utility.effect == UTILITY_EFFECT_FIRE:
            smoke = self._area_effect(UTILITY_EFFECT_SMOKE, node_id)
            if smoke:
                self._remember_area_effect_for_team(smoke, thrower.team_index)
                visible_team_indexes.update(smoke.known_team_indexes)
                self._play_fire_extinguish_audio(node_id)
                self._announce_fire_extinguished(
                    node_id,
                    visible_team_indexes,
                    message_key="breachpoint-fire-suppressed",
                )
            else:
                fire_was_active = (
                    self._area_effect(
                        UTILITY_EFFECT_FIRE,
                        node_id,
                    )
                    is not None
                )
                fire = self._deploy_area_effect(
                    utility,
                    node_id,
                    thrower.id,
                    visible_team_indexes,
                )
                if not fire_was_active:
                    self._start_fire_audio(node_id)
                round_finished = self._damage_players_with_utility(
                    thrower,
                    utility,
                    self._living_players_at_node(node_id),
                    area_effect=fire,
                )
        if round_finished:
            self.cancel_sequence(sequence_id)
            return

    def _finish_utility_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        self._stop_utility_flight_audio(sequence_id)
        thrower = self._breach_player_by_id(str(payload.get("player_id", "")))
        self.cancel_sequence(sequence_id)
        if (
            not thrower
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or self.current_player is not thrower
        ):
            self.refresh_menus()
            return
        self._finish_action(thrower)

    def _action_move(self, player: Player, action_id: str) -> None:
        if self._is_move_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        destination = self._node_from_action(action_id)
        if not tactical_player or not destination:
            return
        origin = self._player_grid_point(tactical_player)
        occupied = {
            self._player_grid_point(other)
            for other in self.get_active_players()
            if isinstance(other, BreachPointPlayer)
            and other.id != tactical_player.id
            and other.position_id == destination.id
            and self._player_has_valid_grid_point(other)
        }
        destination_point = self._choose_grid_point(destination, occupied)
        origin_node = self._node(tactical_player.position_id)
        if not origin_node:
            return
        self._return_to_combat_root(tactical_player, "combat_menu_move")
        delta_x = destination.anchor.x - origin_node.anchor.x
        delta_y = destination.anchor.y - origin_node.anchor.y
        destination_heading = round(math.degrees(math.atan2(delta_x, delta_y))) % 360
        movement_cost = self._movement_action_point_cost(tactical_player)
        enemy_visibility_before = {
            str(team_index): self._team_can_see_player(team_index, tactical_player)
            for team_index in TEAM_INDEXES
            if team_index != tactical_player.team_index
        }
        friendly_contact_visibility_before = {
            enemy.id: [
                self._can_see(tactical_player, enemy),
                self._team_can_see_player(tactical_player.team_index, enemy),
            ]
            for enemy in self._players_on_team(
                next(
                    team_index
                    for team_index in TEAM_INDEXES
                    if team_index != tactical_player.team_index
                ),
                alive_only=True,
            )
        }
        weapon = self._equipped_weapon(tactical_player)
        assets, next_start_ratio, duration_ticks, duration_ms = movement_audio_plan(
            origin,
            destination_point,
            weapon.id if weapon else "",
            surface_id=destination.footstep_surface,
            variant_offset=self.sound_scheduler_tick
            + sum(map(ord, tactical_player.id)),
        )
        sequence_id = f"{MOVEMENT_SEQUENCE_TAG}.{tactical_player.id}"
        payload = {
            "player_id": tactical_player.id,
            "origin_node_id": tactical_player.position_id,
            "origin_x": origin.x,
            "origin_y": origin.y,
            "destination_node_id": destination.id,
            "destination_x": destination_point.x,
            "destination_y": destination_point.y,
            "destination_heading": destination_heading,
            "movement_cost": movement_cost,
            "assets": list(assets),
            "next_start_ratio": next_start_ratio,
            "duration_ms": duration_ms,
            "enemy_visibility_before": enemy_visibility_before,
            "friendly_contact_visibility_before": friendly_contact_visibility_before,
        }
        self.start_sequence(
            sequence_id,
            [
                SequenceBeat.after_audio(
                    duration_ticks,
                    ops=[
                        SequenceOperation.callback_op(
                            MOVEMENT_START_CALLBACK,
                            payload,
                        )
                    ],
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            MOVEMENT_ARRIVE_CALLBACK,
                            payload,
                        )
                    ]
                ),
            ],
            tag=MOVEMENT_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"payload": payload},
            replace_existing=False,
        )
        self.refresh_menus()

    def _start_movement_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        mover = self._breach_player_by_id(str(payload.get("player_id", "")))
        if (
            not mover
            or mover.eliminated
            or mover.position_id != payload.get("origin_node_id")
            or self._player_grid_point(mover)
            != GridPoint(
                int(payload.get("origin_x", -1)),
                int(payload.get("origin_y", -1)),
            )
            or not self._spend_action_points(
                mover,
                int(payload.get("movement_cost", 0)),
            )
        ):
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        destination = GridPoint(
            int(payload["destination_x"]),
            int(payload["destination_y"]),
        )
        heading = int(payload["destination_heading"]) % 360
        self._clear_held_angle(mover)
        self._play_movement_audio(
            mover,
            self._player_grid_point(mover),
            destination,
            tuple(str(asset) for asset in payload.get("assets", [])),
            float(payload["next_start_ratio"]),
        )
        self._move_area_effect_audio_for_listener(
            mover,
            destination,
            heading,
            int(payload.get("duration_ms", 1)),
        )

    def _complete_movement_sequence(self, payload: dict[str, Any]) -> None:
        mover = self._breach_player_by_id(str(payload.get("player_id", "")))
        destination_node_id = str(payload.get("destination_node_id", ""))
        destination_node = self._node(destination_node_id)
        if not mover or mover.eliminated or not destination_node:
            return
        destination = GridPoint(
            int(payload.get("destination_x", -1)),
            int(payload.get("destination_y", -1)),
        )
        if not destination_node.is_walkable(destination):
            raise RuntimeError(
                f"Invalid movement destination {destination} in {destination_node_id}"
            )
        if any(
            other.id != mover.id
            and not other.eliminated
            and self._player_grid_point(other) == destination
            for other in self.get_active_players()
            if isinstance(other, BreachPointPlayer)
        ):
            raise RuntimeError(f"Occupied movement destination {destination}")
        mover.position_id = destination_node_id
        mover.grid_x = destination.x
        mover.grid_y = destination.y
        mover.facing_degrees = int(payload.get("destination_heading", 0)) % 360
        self._sync_listener_environment_audio(mover)
        self._reset_stationary_evasion(mover)
        self._remember_observable_area_effects_for_team(mover.team_index)
        enemy_visibility_before = {
            int(team_index): bool(visible)
            for team_index, visible in dict(
                payload.get("enemy_visibility_before", {})
            ).items()
        }
        self._announce_movement(
            mover,
            destination_node_id,
            enemy_visibility_before,
        )
        friendly_contact_visibility_before = {
            player_id: (bool(values[0]), bool(values[1]))
            for player_id, values in dict(
                payload.get("friendly_contact_visibility_before", {})
            ).items()
            if isinstance(values, list) and len(values) == 2
        }
        self._announce_new_movement_contacts(
            mover,
            friendly_contact_visibility_before,
        )
        if self._process_fire_contact(mover):
            return
        if self._open_watched_entry_reaction(mover, destination_node_id):
            self._bot_coordinator.observe(self)
            return
        self._finish_action(mover)

    def _action_shoot(self, player: Player, action_id: str) -> None:
        if self._is_shoot_enabled(player, action_id=action_id):
            return
        shooter = self._breach_player(player)
        target = self._target_from_action(action_id)
        if not shooter or not target:
            return
        weapon = self._equipped_weapon(shooter)
        if not weapon or not self._spend_action_points(
            shooter, weapon.action_point_cost
        ):
            return
        self._return_to_combat_root(shooter, "combat_menu_attack")
        shooter.shots_fired_this_activation += 1
        shooter.weapon_shots_fired_this_activation[weapon.id] = (
            shooter.weapon_shots_fired_this_activation.get(weapon.id, 0) + 1
        )
        shooter.weapon_target_ids_this_activation.setdefault(weapon.id, []).append(
            target.id
        )
        damage_percent = (
            100
            if shooter.shots_fired_this_activation == 1
            else weapon.followup_damage_percent
        )
        if not self._perform_attack(
            shooter,
            target,
            weapon,
            damage_percent=damage_percent,
            resume_mode="normal",
        ):
            self._finish_action(shooter)

    def _perform_attack(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        *,
        damage_percent: int,
        resume_mode: str,
    ) -> bool:
        """Start an audible attack; resolve damage with the final report."""

        self._clear_held_angle(shooter)
        distance = self._combat_distance(shooter.position_id, target.position_id)
        if distance is None:
            return False
        ammunition_used = self._consume_attack_ammunition(
            shooter,
            weapon,
        )
        if ammunition_used <= 0:
            return False
        outcome = self._preview_attack(
            target,
            weapon,
            distance,
            damage_percent=damage_percent,
            ammunition_used=ammunition_used,
        )
        shot_count = ammunition_used
        payload = {
            "player_id": shooter.id,
            "target_id": target.id,
            "weapon_id": weapon.id,
            "shot_count": shot_count,
            "rounds_fired": outcome.rounds_fired,
            "rounds_on_target": outcome.rounds_on_target,
            "rounds_evaded": outcome.rounds_evaded,
            "health_damage": outcome.health_damage,
            "armor_absorbed": outcome.armor_absorbed,
            "fully_evaded": outcome.fully_evaded,
            "lethal": bool(outcome.health_damage and outcome.health_damage >= target.health),
            "target_had_armor": target.armor > 0,
            "resume_mode": resume_mode,
        }
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        WEAPON_FIRE_CALLBACK,
                        {**payload, "shot_index": shot_index},
                    )
                ],
                delay_after_ticks=(
                    weapon_fire_delay_ticks(weapon.id, shot_index)
                    if shot_index < shot_count - 1
                    else 0
                ),
            )
            for shot_index in range(shot_count)
        ]
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        WEAPON_RESOLVE_CALLBACK,
                        payload,
                    )
                ]
            )
        )
        self.start_sequence(
            f"{WEAPON_SEQUENCE_TAG}.{shooter.id}",
            beats,
            tag=WEAPON_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"payload": payload, "shots_issued": 0},
            replace_existing=False,
        )
        self.refresh_menus()
        return True

    def _fire_weapon_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        sequence = self._get_sequence(sequence_id)
        shooter = self._breach_player_by_id(str(payload.get("player_id", "")))
        target = self._breach_player_by_id(str(payload.get("target_id", "")))
        weapon = get_weapon(str(payload.get("weapon_id", "")))
        if (
            not sequence
            or not shooter
            or not target
            or not weapon
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or shooter.eliminated
            or target.eliminated
        ):
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        shot_index = int(payload.get("shot_index", -1))
        shot_count = int(payload.get("shot_count", 0))
        if not 0 <= shot_index < shot_count:
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        sequence.metadata["shots_issued"] = shot_index + 1
        self._play_weapon_bullet_audio(
            shooter,
            target,
            weapon,
            shot_index=shot_index,
            rounds_on_target=int(payload.get("rounds_on_target", 0)),
            rounds_evaded=int(payload.get("rounds_evaded", 0)),
            health_damage=int(payload.get("health_damage", 0)),
            armor_absorbed=int(payload.get("armor_absorbed", 0)),
            lethal=bool(payload.get("lethal", False)),
            target_had_armor=bool(payload.get("target_had_armor", False)),
        )

    def _resolve_weapon_sequence(
        self,
        sequence_id: str,
        payload: dict[str, Any],
    ) -> None:
        shooter = self._breach_player_by_id(str(payload.get("player_id", "")))
        target = self._breach_player_by_id(str(payload.get("target_id", "")))
        weapon = get_weapon(str(payload.get("weapon_id", "")))
        if (
            not shooter
            or not target
            or not weapon
            or self.status != "playing"
            or self.phase != PHASE_COMBAT
            or shooter.eliminated
            or target.eliminated
        ):
            self.cancel_sequence(sequence_id)
            self.refresh_menus()
            return
        outcome = AttackOutcome(
            rounds_fired=max(0, int(payload.get("rounds_fired", 0))),
            rounds_on_target=max(0, int(payload.get("rounds_on_target", 0))),
            rounds_evaded=min(
                max(0, int(payload.get("rounds_on_target", 0))),
                max(0, int(payload.get("rounds_evaded", 0))),
            ),
            health_damage=min(
                target.health,
                max(0, int(payload.get("health_damage", 0))),
            ),
            armor_absorbed=min(
                target.armor,
                max(0, int(payload.get("armor_absorbed", 0))),
            ),
            fully_evaded=bool(payload.get("fully_evaded", False)),
        )
        target.guard_points = 0
        target.armor -= outcome.armor_absorbed
        target.health -= outcome.health_damage
        if target.health == 0:
            target.eliminated = True
            target.action_points = 0
            target.guard_points = 0
            self._clear_held_angle(target)
        elif outcome.health_damage or outcome.armor_absorbed:
            self._clear_held_angle(target)
        self._announce_shot(shooter, target, weapon, outcome)
        if (
            target.id == self.planting_player_id
            and not target.eliminated
            and (outcome.health_damage or outcome.armor_absorbed)
        ):
            self._interrupt_plant(target, shooter)
        if target.id == self.defusing_player_id and (
            outcome.health_damage or outcome.armor_absorbed
        ):
            self._interrupt_defuse(target, shooter)
        if target.eliminated and self._finalize_eliminations(
            shooter,
            [target],
            source_name_key=weapon.name_key,
            kill_reward=weapon.kill_reward,
        ):
            return
        if str(payload.get("resume_mode", "")) == "reaction":
            self._finish_watched_entry_reaction()
        else:
            self._finish_action(shooter)

    def _resolve_utility_damage(
        self,
        target: BreachPointPlayer,
        utility: UtilityProfile,
        *,
        damage_percent: int = 100,
    ) -> UtilityDamageOutcome:
        """Apply deterministic utility damage through evasion and armor."""

        outcome = self._preview_utility_damage(
            target,
            utility,
            damage_percent=damage_percent,
        )
        if utility.evasion_damage_reduction_per_point:
            target.guard_points = 0
        target.armor = max(0, target.armor - outcome.armor_absorbed)
        target.health = max(0, target.health - outcome.health_damage)
        if target.health == 0:
            target.eliminated = True
            target.action_points = 0
            target.guard_points = 0
        if outcome.health_damage or outcome.armor_absorbed:
            self._clear_held_angle(target)
        return outcome

    def _preview_utility_damage(
        self,
        target: BreachPointPlayer,
        utility: UtilityProfile,
        *,
        damage_percent: int = 100,
    ) -> UtilityDamageOutcome:
        """Calculate deterministic utility damage without mutating state."""

        damage_percent = max(1, min(100, damage_percent))
        base_damage = (utility.damage * damage_percent + 99) // 100
        guard_points = min(self.rules.maximum_evasion_points, target.guard_points)
        evasion_mitigation = min(
            base_damage,
            guard_points * utility.evasion_damage_reduction_per_point,
        )
        remaining_damage = base_damage - evasion_mitigation
        armor_absorbed = min(
            target.armor,
            remaining_damage * utility.armor_reduction_percent // 100,
        )
        health_damage = min(target.health, remaining_damage - armor_absorbed)
        return UtilityDamageOutcome(
            health_damage=health_damage,
            armor_absorbed=armor_absorbed,
            evasion_mitigation=evasion_mitigation,
        )

    def _damage_players_with_utility(
        self,
        source: BreachPointPlayer,
        utility: UtilityProfile,
        targets: list[BreachPointPlayer],
        *,
        area_effect: AreaEffectState | None = None,
    ) -> bool:
        """Damage occupants once and resolve simultaneous utility eliminations."""

        eliminated_targets: list[BreachPointPlayer] = []
        for target in targets:
            if target.eliminated or (
                target.id == source.id and not utility.affects_thrower
            ):
                continue
            if (
                area_effect
                and area_effect.affected_player_rounds.get(target.id)
                == self.tactical_round
            ):
                continue
            if area_effect:
                area_effect.affected_player_rounds[target.id] = self.tactical_round
                self._remember_area_effect_for_team(
                    area_effect,
                    target.team_index,
                )
            target_was_visible = self._viewer_can_see_player(source, target)
            damage_percent = (
                100
                if target.team_index != source.team_index
                else utility.friendly_damage_percent
            )
            outcome = self._resolve_utility_damage(
                target,
                utility,
                damage_percent=damage_percent,
            )
            if utility.effect == UTILITY_EFFECT_FIRE and (
                outcome.health_damage or outcome.armor_absorbed
            ):
                self._play_fire_damage_audio(target)
            if target.eliminated:
                self._play_death_audio(target)
            self._announce_utility_damage(
                source,
                target,
                utility,
                outcome,
                source_saw_target=target_was_visible,
            )
            if target.id == self.planting_player_id and (
                outcome.health_damage or outcome.armor_absorbed
            ):
                self._interrupt_plant(target, source)
            if target.id == self.defusing_player_id and (
                outcome.health_damage or outcome.armor_absorbed
            ):
                self._interrupt_defuse(target, source)
            if target.eliminated:
                eliminated_targets.append(target)
        if not eliminated_targets:
            return False
        return self._finalize_eliminations(
            source,
            eliminated_targets,
            source_name_key=utility.name_key,
            kill_reward=utility.kill_reward,
        )

    def _finalize_eliminations(
        self,
        source: BreachPointPlayer,
        targets: list[BreachPointPlayer],
        *,
        source_name_key: str,
        kill_reward: int,
    ) -> bool:
        """Publish kills, settle rewards, and apply shared death consequences."""

        for target in targets:
            credited = (
                self._add_cash(source, kill_reward)
                if target.team_index != source.team_index
                else 0
            )
            self._announce_elimination(
                source,
                target,
                source_name_key=source_name_key,
            )
            source_user = self.get_user(source)
            if source_user and credited:
                source_user.speak_l(
                    "breachpoint-kill-reward",
                    buffer="game",
                    amount=credited,
                    cash=source.cash,
                )
        recovery_drop_ids: list[int] = []
        for target in targets:
            dropped_weapon = self._death_drop_weapon(target)
            if dropped_weapon:
                self._announce_weapon_drop(target, dropped_weapon)
                if dropped_weapon.node_id == source.position_id:
                    recovery_drop_ids.append(dropped_weapon.drop_id)
            self._drop_bomb_from_eliminated_carrier(target)
        winning_side_index = self._elimination_victory_side(
            simultaneous_winner_team_index=source.team_index,
        )
        if winning_side_index is None:
            return False
        if self._begin_round_recovery(
            source,
            recovery_drop_ids,
            winning_side_index=winning_side_index,
            reason=WIN_ELIMINATION,
        ):
            return True
        self._finish_combat_round(winning_side_index, WIN_ELIMINATION)
        return True

    def _begin_round_recovery(
        self,
        survivor: BreachPointPlayer,
        drop_ids: list[int],
        *,
        winning_side_index: int,
        reason: str,
    ) -> bool:
        """Offer one same-area weapon recovery before committing the round result."""

        eligible_ids = list(
            dict.fromkeys(
                drop_id
                for drop_id in drop_ids
                if any(
                    dropped_weapon.drop_id == drop_id
                    and dropped_weapon.node_id == survivor.position_id
                    for dropped_weapon in self.dropped_weapons
                )
            )
        )
        if (
            survivor.eliminated
            or survivor.action_points < self.rules.weapon_pickup_cost
            or not eligible_ids
        ):
            return False
        self.reaction_window = ReactionWindow()
        self.round_recovery_player_id = survivor.id
        self.round_recovery_drop_ids = eligible_ids
        self.pending_round_winner_side_index = winning_side_index
        self.pending_round_win_reason = reason
        self.current_player = survivor
        self._play_turn_notification(survivor)
        self._combat_menu_views[survivor.id] = CombatMenuState(COMBAT_MENU_LOOT)
        self.broadcast_personal_l(
            survivor,
            "breachpoint-round-recovery-you",
            "breachpoint-round-recovery-player",
            buffer="game",
            count=len(eligible_ids),
        )
        self.refresh_menus()
        first_drop = next(
            (
                dropped_weapon
                for dropped_weapon in self.dropped_weapons
                if dropped_weapon.drop_id in eligible_ids
            ),
            None,
        )
        if first_drop:
            self.request_menu_focus(
                survivor,
                self._dropped_weapon_action_id(first_drop),
            )
        BotHelper.jolt_bot(survivor)
        return True

    def _complete_round_recovery(self, survivor: BreachPointPlayer) -> None:
        """Resolve the one-choice recovery window and commit the held round result."""

        winning_side_index = self.pending_round_winner_side_index
        reason = self.pending_round_win_reason
        survivor.action_points = 0
        self._clear_round_recovery()
        if winning_side_index in TEAM_INDEXES and reason in WIN_REASONS:
            self._finish_combat_round(winning_side_index, reason)

    def _action_plant(self, player: Player, action_id: str) -> None:
        if self._is_plant_enabled(player):
            return
        terrorist = self._breach_player(player)
        if not terrorist or not self._spend_action_points(
            terrorist, self.rules.plant_cost
        ):
            return
        self._return_to_combat_root(terrorist, "combat_menu_objective")
        self._clear_held_angle(terrorist)
        self.bomb_state = BOMB_PLANTING
        self.planting_player_id = terrorist.id
        self.planting_location_id = terrorist.position_id
        self._play_bomb_plant_audio(terrorist)
        self._announce_plant_started(terrorist)
        terrorist.action_points = 0
        self._end_activation(terrorist)

    def _action_defuse(self, player: Player, action_id: str) -> None:
        if self._is_defuse_enabled(player):
            return
        counter_terrorist = self._breach_player(player)
        if not counter_terrorist:
            return
        defuse_cost = self._defuse_action_point_cost(counter_terrorist)
        if not self._spend_action_points(counter_terrorist, defuse_cost):
            return
        self._return_to_combat_root(
            counter_terrorist,
            "combat_menu_objective",
        )
        self._clear_held_angle(counter_terrorist)
        self.defusing_player_id = counter_terrorist.id
        self.defusing_location_id = self.bomb_location_id
        self._play_bomb_audio(
            BOMB_DEFUSE_START_ASSET,
            self.bomb_location_id,
            actor_id=counter_terrorist.id,
            source=self._bomb_grid_point(),
        )
        self.broadcast_personal_l(
            counter_terrorist,
            "breachpoint-defuse-start-you",
            "breachpoint-defuse-start-player",
            buffer="game",
            location=lambda locale: self._node_name(locale, self.bomb_location_id),
            cost=defuse_cost,
        )
        counter_terrorist.action_points = 0
        self._end_activation(counter_terrorist)

    def _action_pick_up_bomb(self, player: Player, action_id: str) -> None:
        if self._is_pick_up_bomb_enabled(player):
            return
        terrorist = self._breach_player(player)
        if not terrorist or not self._spend_action_points(
            terrorist, self.rules.bomb_pickup_cost
        ):
            return
        self._return_to_combat_root(terrorist, "combat_menu_objective")
        self._clear_held_angle(terrorist)
        self.bomb_state = BOMB_CARRIED
        self.bomb_carrier_id = terrorist.id
        self.bomb_location_id = ""
        self._clear_bomb_grid_point()
        self._play_bomb_pickup_audio(terrorist)
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if not tactical_listener or not user or tactical_listener.is_spectator:
                continue
            if tactical_listener.team_index == TEAM_TERRORISTS:
                key = (
                    "breachpoint-pickup-you"
                    if tactical_listener.id == terrorist.id
                    else "breachpoint-pickup-player"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    player=terrorist.name,
                    ap=terrorist.action_points,
                )
            elif self._team_can_see_node(
                tactical_listener.team_index,
                terrorist.position_id,
            ):
                user.speak_l(
                    "breachpoint-pickup-enemy",
                    buffer="game",
                    player=terrorist.name,
                    location=self._node_name(user.locale, terrorist.position_id),
                )
        self._finish_action(terrorist)

    def _action_end_turn(self, player: Player, action_id: str) -> None:
        if self._is_end_turn_enabled(player):
            return
        tactical_player = self._breach_player(player)
        if not tactical_player:
            return
        if self.round_recovery_player_id == tactical_player.id:
            self.broadcast_personal_l(
                tactical_player,
                "breachpoint-round-recovery-skipped-you",
                "breachpoint-round-recovery-skipped-player",
                buffer="game",
            )
            self._complete_round_recovery(tactical_player)
            return
        guard = self._available_guard_points(tactical_player)
        can_prepare_guard = bool(
            tactical_player.action_points
            and not tactical_player.held_angle_node_id
            and not tactical_player.shots_fired_this_activation
        )
        if can_prepare_guard:
            tactical_player.stationary_guard_activations = (
                tactical_player.stationary_guard_activations + 1
                if tactical_player.guard_anchor_node_id == tactical_player.position_id
                else 0
            )
            tactical_player.guard_anchor_node_id = tactical_player.position_id
        tactical_player.guard_points = guard
        personal_key = (
            "breachpoint-end-turn-you"
            if guard
            else "breachpoint-end-turn-no-evasion-you"
        )
        public_key = (
            "breachpoint-end-turn-player"
            if guard
            else "breachpoint-end-turn-no-evasion-player"
        )
        self.broadcast_personal_l(
            tactical_player,
            personal_key,
            public_key,
            buffer="game",
            guard=guard,
        )
        tactical_player.action_points = 0
        self._end_activation(tactical_player)

    def _finish_action(self, player: BreachPointPlayer) -> None:
        if player.eliminated:
            player.action_points = 0
        if player.action_points == 0:
            self._end_activation(player)
        else:
            self._bot_coordinator.observe(self)
            self.refresh_menus()
            BotHelper.jolt_bot(player)

    # ------------------------------------------------------------------
    # Turn and round flow
    # ------------------------------------------------------------------

    def _start_activation(
        self,
        player: Player | None,
        *,
        action_point_limit: int | None = None,
    ) -> None:
        tactical_player = self._breach_player(player)
        if not tactical_player or tactical_player.eliminated:
            return
        if self._process_fire_contact(tactical_player):
            return
        if (
            self.bomb_state == BOMB_PLANTING
            and tactical_player.team_index == TEAM_TERRORISTS
            and not self.reaction_window.is_open
        ):
            self._complete_pending_plant()
        available_action_points = self.rules.action_points_per_activation
        if action_point_limit is not None:
            available_action_points = max(
                0,
                min(available_action_points, action_point_limit),
            )
        flash_penalty = min(
            available_action_points,
            tactical_player.flash_penalty,
        )
        tactical_player.guard_points = 0
        tactical_player.action_points = max(
            0,
            available_action_points - flash_penalty,
        )
        tactical_player.flash_penalty = 0
        tactical_player.shots_fired_this_activation = 0
        tactical_player.weapon_shots_fired_this_activation = {}
        tactical_player.weapon_target_ids_this_activation = {}
        self._combat_menu_views[tactical_player.id] = CombatMenuState()
        if not tactical_player.is_bot:
            self.request_menu_focus(
                tactical_player,
                COMBAT_MENU_SUMMARY_ACTION_ID,
            )
        self._play_turn_notification(tactical_player)
        if flash_penalty:
            user = self.get_user(tactical_player)
            if user:
                user.speak_l(
                    "breachpoint-flash-penalty-ap",
                    buffer="game",
                    penalty=flash_penalty,
                    ap=tactical_player.action_points,
                )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == tactical_player.id
            objective_response = bool(
                self.reaction_window.is_open
                and self.reaction_window.kind in {REACTION_PLANT, REACTION_DEFUSE}
                and self.reaction_window.responding_player_id == tactical_player.id
            )
            if objective_response:
                key = (
                    "breachpoint-response-turn-you"
                    if is_actor
                    else "breachpoint-response-turn-player"
                )
            else:
                key = (
                    "breachpoint-turn-you"
                    if is_actor
                    else "breachpoint-turn-player"
                )
            user.speak_l(
                key,
                buffer="game",
                player=tactical_player.name,
                ap=tactical_player.action_points,
                response=Localization.get(
                    user.locale,
                    f"breachpoint-response-{self.reaction_window.kind}",
                )
                if objective_response
                else "",
            )
        self.refresh_menus()

    def _end_activation(self, player: BreachPointPlayer) -> None:
        if self.status != "playing" or self.current_player is not player:
            return
        reaction = self.reaction_window
        objective_response = bool(
            reaction.is_open
            and reaction.kind in {REACTION_PLANT, REACTION_DEFUSE}
            and reaction.responding_player_id == player.id
        )
        self._bot_coordinator.observe(self)
        if player.id not in self.round_acted_player_ids:
            self.round_acted_player_ids.append(player.id)

        if objective_response:
            self.reaction_window = ReactionWindow()
            if reaction.kind == REACTION_PLANT:
                self._complete_pending_plant()
            elif self._complete_pending_defuse():
                return
            if self.status != "playing":
                return
            self._continue_after_activation(reaction.resume_after_player_id)
            return

        if self.defusing_player_id and player.id == self.defusing_player_id:
            if self._open_objective_reaction(
                REACTION_DEFUSE,
                player,
                TEAM_TERRORISTS,
            ):
                return
            if self._complete_pending_defuse():
                return
        if self.bomb_state == BOMB_PLANTING and player.id == self.planting_player_id:
            if self._open_objective_reaction(
                REACTION_PLANT,
                player,
                TEAM_COUNTER_TERRORISTS,
            ):
                return
            self._complete_pending_plant()
        self._continue_after_activation(player.id)

    def _continue_after_activation(self, after_player_id: str) -> None:
        """Resume stable turn order after an activation or temporary response."""

        next_player = self._next_unacted_living_player(
            after_player_id=after_player_id,
        )
        if next_player:
            self.current_player = next_player
            self._start_activation(next_player)
            BotHelper.jolt_bot(next_player)
            return

        if self.bomb_state == BOMB_PLANTING:
            self._complete_pending_plant()
        if self._complete_tactical_round():
            return
        self.tactical_round += 1
        self.round_acted_player_ids = []
        next_player = next(
            (
                player
                for player in self.turn_players
                if not getattr(player, "eliminated", False)
            ),
            None,
        )
        if not next_player:
            return
        self.current_player = next_player
        self._announce_tactical_round_start()
        self._start_activation(next_player)
        BotHelper.jolt_bot(next_player)

    def _open_objective_reaction(
        self,
        kind: str,
        objective_actor: BreachPointPlayer,
        responding_team_index: int,
    ) -> bool:
        """Suspend turn order for one objective response activation."""

        if self.reaction_window.is_open or kind not in {
            REACTION_PLANT,
            REACTION_DEFUSE,
        }:
            return False
        responder = self._next_objective_response_player(
            responding_team_index,
            objective_actor,
        )
        if not responder:
            return False
        consumes_activation = responder.id not in self.round_acted_player_ids
        response_action_points = (
            self.rules.action_points_per_activation
            if consumes_activation
            else self.rules.repeat_objective_response_action_points
        )
        self.reaction_window = ReactionWindow(
            kind=kind,
            triggering_player_id=objective_actor.id,
            responding_player_id=responder.id,
            resume_after_player_id=objective_actor.id,
            target_player_id=objective_actor.id,
            context={"node_id": objective_actor.position_id},
            response_action_points=response_action_points,
            consumes_activation=consumes_activation,
        )
        self.current_player = responder
        self._start_activation(
            responder,
            action_point_limit=response_action_points,
        )
        BotHelper.jolt_bot(responder)
        return True

    def _open_watched_entry_reaction(
        self,
        mover: BreachPointPlayer,
        destination_id: str,
    ) -> bool:
        """Offer one held-angle shot before a mover spends more AP."""

        if self.reaction_window.is_open:
            return False
        turn_order = {
            player_id: index for index, player_id in enumerate(self.turn_player_ids)
        }
        candidates: list[tuple[int, int, BreachPointPlayer]] = []
        for candidate in self.get_active_players():
            watcher = self._breach_player(candidate)
            weapon = self._equipped_weapon(watcher) if watcher else None
            if (
                not watcher
                or watcher.eliminated
                or watcher.team_index == mover.team_index
                or watcher.held_angle_origin_id != watcher.position_id
                or watcher.held_angle_node_id != destination_id
                or not self._can_hold_angle(watcher, destination_id, weapon)
                or not self._can_see(watcher, mover)
            ):
                continue
            distance = self._combat_distance(watcher.position_id, destination_id)
            if distance is None:
                continue
            candidates.append(
                (
                    distance,
                    turn_order.get(watcher.id, len(turn_order)),
                    watcher,
                )
            )
        if not candidates:
            return False
        watcher = min(candidates, key=lambda candidate: candidate[:2])[2]
        self.reaction_window = ReactionWindow(
            kind=REACTION_WATCHED_ENTRY,
            triggering_player_id=mover.id,
            responding_player_id=watcher.id,
            resume_after_player_id=mover.id,
            target_player_id=mover.id,
            context={"node_id": destination_id},
        )
        self.current_player = watcher
        self._play_turn_notification(watcher)
        for listener in (watcher, mover):
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                (
                    "breachpoint-watched-entry-you"
                    if listener.id == watcher.id
                    else "breachpoint-watched-entry-target"
                ),
                buffer="game",
                player=watcher.name,
                enemy=mover.name,
                location=self._node_name(user.locale, destination_id),
            )
        self.request_menu_focus(watcher, "reaction_shoot")
        self.refresh_menus()
        BotHelper.jolt_bot(watcher)
        return True

    def _finish_watched_entry_reaction(self) -> None:
        """Close a held-angle choice and return control to the interrupted mover."""

        reaction = self.reaction_window
        if not reaction.is_open or reaction.kind != REACTION_WATCHED_ENTRY:
            return
        mover = self._breach_player_by_id(reaction.triggering_player_id)
        self.reaction_window = ReactionWindow()
        if self.status != "playing" or not mover:
            return
        self.current_player = mover
        if not mover.eliminated and mover.action_points:
            user = self.get_user(mover)
            if user:
                user.speak_l(
                    "breachpoint-watched-entry-resume",
                    buffer="game",
                    ap=mover.action_points,
                )
        self._finish_action(mover)

    def _next_unacted_living_player(
        self,
        *,
        after_player_id: str = "",
    ) -> BreachPointPlayer | None:
        """Continue stable turn order after an ordinary or response activation."""

        if not self.turn_player_ids:
            return None
        anchor_index = self.turn_index
        if after_player_id in self.turn_player_ids:
            anchor_index = self.turn_player_ids.index(after_player_id)
        for offset in range(1, len(self.turn_player_ids) + 1):
            index = (anchor_index + offset) % len(self.turn_player_ids)
            candidate = self._breach_player_by_id(self.turn_player_ids[index])
            if (
                candidate
                and not candidate.eliminated
                and candidate.id not in self.round_acted_player_ids
            ):
                return candidate
        return None

    def _next_objective_response_player(
        self,
        team_index: int,
        objective_actor: BreachPointPlayer | None,
    ) -> BreachPointPlayer | None:
        """Choose the best-positioned living responder in stable turn order."""

        if not self.turn_player_ids:
            return None
        candidates: list[BreachPointPlayer] = []
        for offset in range(1, len(self.turn_player_ids) + 1):
            index = (self.turn_index + offset) % len(self.turn_player_ids)
            candidate = self._breach_player_by_id(self.turn_player_ids[index])
            if (
                candidate
                and not candidate.eliminated
                and candidate.team_index == team_index
            ):
                candidates.append(candidate)
        if not candidates:
            return None

        def response_priority(candidate: BreachPointPlayer) -> tuple[int, bool]:
            if objective_actor and candidate.position_id == objective_actor.position_id:
                position_priority = 0
            elif objective_actor and self._can_see(candidate, objective_actor):
                position_priority = 1
            else:
                position_priority = 2
            return (
                position_priority,
                candidate.id in self.round_acted_player_ids,
            )

        return min(candidates, key=response_priority)

    def _complete_tactical_round(self) -> bool:
        if self.bomb_state == BOMB_PLANTED:
            if self.bomb_planted_tactical_round < self.tactical_round:
                self.bomb_fuse_remaining = max(0, self.bomb_fuse_remaining - 1)
                if self.bomb_fuse_remaining == 0:
                    self._queue_bomb_detonation()
                    return True
                beep_index = min(
                    len(BOMB_BEEP_ASSETS) - 1,
                    max(
                        0,
                        self.rules.bomb_fuse_tactical_rounds - self.bomb_fuse_remaining,
                    ),
                )
                self._play_bomb_audio(
                    BOMB_BEEP_ASSETS[beep_index],
                    self.bomb_location_id,
                    priority=45,
                    source=self._bomb_grid_point(),
                )
                self.broadcast_l(
                    "breachpoint-bomb-countdown",
                    buffer="game",
                    rounds=self.bomb_fuse_remaining,
                )
                if self.bomb_fuse_remaining == 1:
                    self._play_music_cue(
                        MUSIC_BOMB_TEN_SECOND_ASSET,
                        looping=False,
                        priority=36,
                    )
        elif self.tactical_round >= self.rules.preplant_tactical_round_limit:
            self._finish_combat_round(TEAM_COUNTER_TERRORISTS, WIN_TIME)
            return True
        return False

    def _queue_bomb_detonation(self) -> None:
        """Enter the irreversible measured warning window before explosion."""

        if self.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG):
            return
        self._clear_pending_defuse()
        self.reaction_window = ReactionWindow()
        warning_ticks = max(1, bomb_detonation_warning_ticks())
        payload = {
            "node_id": self.bomb_location_id,
            "x": self.bomb_grid_x,
            "y": self.bomb_grid_y,
        }
        self.broadcast_l(
            "breachpoint-bomb-detonation-locked",
            buffer="game",
        )
        self.start_sequence(
            BOMB_DETONATION_SEQUENCE_TAG,
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            BOMB_DETONATION_START_CALLBACK,
                            payload,
                        )
                    ],
                    delay_after_ticks=warning_ticks,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            BOMB_DETONATION_FINISH_CALLBACK,
                            payload,
                        )
                    ]
                ),
            ],
            tag=BOMB_DETONATION_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"payload": payload},
        )
        self.refresh_menus()

    def _complete_bomb_detonation(self, sequence_id: str) -> None:
        sequence = next(
            (
                candidate
                for candidate in self.active_sequences
                if candidate.sequence_id == sequence_id
                and candidate.tag == BOMB_DETONATION_SEQUENCE_TAG
            ),
            None,
        )
        if not sequence or self.bomb_state != BOMB_PLANTED:
            self.cancel_sequence(sequence_id)
            return
        self.cancel_sequence(sequence_id)
        self._play_global_asset(
            BOMB_EXPLOSION_ASSET,
            handle=BOMB_EXPLOSION_HANDLE,
            priority=90,
            max_instances=1,
        )
        self.broadcast_l(
            "breachpoint-bomb-detonates",
            buffer="game",
            location=lambda locale: self._node_name(
                locale, self.bomb_location_id
            ),
        )
        self._finish_combat_round(TEAM_TERRORISTS, WIN_DETONATED)

    def _announce_match_start(self) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            if player.is_spectator:
                user.speak_l(
                    "breachpoint-match-start-spectator",
                    buffer="game",
                    map=Localization.get(user.locale, self.tactical_map.name_key),
                    format=Localization.get(
                        user.locale,
                        f"breachpoint-match-format-{self.match_format.id}",
                    ),
                    tactical_rounds=self.rules.preplant_tactical_round_limit,
                )
                continue
            tactical_player = self._breach_player(player)
            if not tactical_player:
                continue
            user.speak_l(
                "breachpoint-match-start-player",
                buffer="game",
                team=self._team_name(user.locale, tactical_player.team_index),
                map=Localization.get(user.locale, self.tactical_map.name_key),
                location=self._node_name(user.locale, tactical_player.position_id),
                format=Localization.get(
                    user.locale,
                    f"breachpoint-match-format-{self.match_format.id}",
                ),
                tactical_rounds=self.rules.preplant_tactical_round_limit,
            )

    def _announce_combat_round_start(self) -> None:
        if self.round > 1:
            self._play_music_cue(
                MUSIC_ROUND_START_ASSET,
                looping=True,
                priority=28,
            )
        final_round_of_first_half = (
            not self.overtime_period
            and self.round == self.match_format.rounds_per_half
        )
        regulation_match_point = (
            not self.overtime_period
            and max(
                self._squad_score(squad_index)
                for squad_index in TEAM_INDEXES
            )
            == self.match_format.rounds_to_win - 1
        )
        if final_round_of_first_half:
            self._play_global_audio_chain(
                (LAST_ROUND_HALF_ASSET,),
                priority=88,
            )
        if final_round_of_first_half or regulation_match_point:
            self._play_round_stinger(
                FINAL_ROUND_STINGER_ASSET,
                priority=45,
            )
        self.broadcast_l(
            "breachpoint-combat-round-start",
            buffer="game",
            round=self.round,
            team_one=lambda locale: self._squad_name(locale, TEAM_TERRORISTS),
            team_one_score=self._squad_score(TEAM_TERRORISTS),
            team_two=lambda locale: self._squad_name(locale, TEAM_COUNTER_TERRORISTS),
            team_two_score=self._squad_score(TEAM_COUNTER_TERRORISTS),
        )
        self._announce_bomb_assignment()

    def _announce_bomb_assignment(self) -> None:
        """Tell only T players who received the randomly assigned bomb."""

        carrier = self._breach_player_by_id(self.bomb_carrier_id)
        if not carrier:
            return
        for terrorist in self._players_on_team(TEAM_TERRORISTS, alive_only=True):
            user = self.get_user(terrorist)
            if not user:
                continue
            user.speak_l(
                (
                    "breachpoint-bomb-assigned-you"
                    if terrorist.id == carrier.id
                    else "breachpoint-bomb-assigned-teammate"
                ),
                buffer="game",
                player=carrier.name,
            )

    def _round_phase_label(self, locale: str) -> str:
        if self.bomb_state == BOMB_PLANTED:
            total = self.rules.bomb_fuse_tactical_rounds
            if self.bomb_planted_tactical_round >= self.tactical_round:
                return Localization.get(
                    locale,
                    "breachpoint-phase-postplant-armed",
                    total=total,
                )
            postplant_round = max(
                1,
                min(total, total - self.bomb_fuse_remaining + 1),
            )
            return Localization.get(
                locale,
                "breachpoint-phase-postplant",
                round=postplant_round,
                total=total,
            )
        return Localization.get(
            locale,
            "breachpoint-phase-preplant",
            round=self.tactical_round,
            limit=self.rules.preplant_tactical_round_limit,
        )

    def _announce_tactical_round_start(self) -> None:
        self._prune_expired_area_effects()
        if (
            self.bomb_state != BOMB_PLANTED
            and self.tactical_round == self.rules.preplant_tactical_round_limit
        ):
            self._play_music_cue(
                MUSIC_ROUND_TEN_SECOND_ASSET,
                looping=False,
                priority=34,
            )
        self.broadcast_l(
            "breachpoint-tactical-round-start",
            buffer="game",
            phase=lambda locale: self._round_phase_label(locale),
        )

    def _announce_utility_throw(
        self,
        thrower: BreachPointPlayer,
        utility: UtilityProfile,
        node_id: str,
        visible_team_indexes: set[int],
    ) -> None:
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or tactical_listener.team_index not in visible_team_indexes
            ):
                continue
            if listener.id == thrower.id:
                key = "breachpoint-utility-throw-you"
            elif tactical_listener.team_index == thrower.team_index:
                key = "breachpoint-utility-throw-ally"
            elif self._team_can_see_player(tactical_listener.team_index, thrower):
                key = "breachpoint-utility-throw-enemy"
            else:
                key = "breachpoint-utility-throw-enemy-concealed"
            user.speak_l(
                key,
                buffer="game",
                player=thrower.name,
                utility=self._utility_name(user.locale, utility),
                location=self._node_name(user.locale, node_id),
            )

    def _announce_weapon_drop(
        self,
        owner: BreachPointPlayer,
        dropped_weapon: DroppedWeapon,
    ) -> None:
        weapon = get_weapon(dropped_weapon.weapon_id)
        if not weapon:
            return
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or (
                    tactical_listener.team_index != owner.team_index
                    and not self._team_can_see_node(
                        tactical_listener.team_index,
                        dropped_weapon.node_id,
                    )
                )
            ):
                continue
            user.speak_l(
                (
                    "breachpoint-weapon-dropped-you"
                    if listener.id == owner.id
                    else "breachpoint-weapon-dropped-player"
                ),
                buffer="game",
                player=owner.name,
                weapon=self._weapon_name(user.locale, weapon),
                location=self._node_name(user.locale, dropped_weapon.node_id),
            )

    def _announce_weapon_pickup(
        self,
        picker: BreachPointPlayer,
        weapon: WeaponProfile,
        replacement: WeaponProfile | None,
    ) -> None:
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or (
                    tactical_listener.team_index != picker.team_index
                    and not self._viewer_can_see_player(listener, picker)
                )
            ):
                continue
            is_picker = listener.id == picker.id
            if replacement:
                key = (
                    (
                        "breachpoint-buy-weapon-exchanged-you"
                        if self.phase == PHASE_BUY
                        else "breachpoint-weapon-exchanged-you"
                    )
                    if is_picker
                    else "breachpoint-weapon-exchanged-player"
                )
            else:
                key = (
                    (
                        "breachpoint-buy-weapon-picked-up-you"
                        if self.phase == PHASE_BUY
                        else "breachpoint-weapon-picked-up-you"
                    )
                    if is_picker
                    else "breachpoint-weapon-picked-up-player"
                )
            user.speak_l(
                key,
                buffer="game",
                player=picker.name,
                weapon=self._weapon_name(user.locale, weapon),
                replaced=self._weapon_name(user.locale, replacement),
                location=self._node_name(user.locale, picker.position_id),
                ammunition=self._ammunition_summary(user.locale, picker, weapon),
                ap=picker.action_points,
            )

    def _announce_movement(
        self,
        mover: BreachPointPlayer,
        destination_id: str,
        enemy_visibility_before: dict[int, bool],
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            tactical_listener = self._breach_player(listener)
            if not user or not tactical_listener:
                continue
            if tactical_listener.is_spectator:
                user.speak_l(
                    "breachpoint-enemy-moves-hidden",
                    buffer="game",
                    player=mover.name,
                )
                continue
            if tactical_listener.team_index == mover.team_index:
                key = (
                    "breachpoint-move-you"
                    if listener.id == mover.id
                    else "breachpoint-move-player"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    player=mover.name,
                    destination=self._node_name(user.locale, destination_id),
                    ap=mover.action_points,
                )
                continue

            was_visible = enemy_visibility_before.get(
                tactical_listener.team_index, False
            )
            is_visible = self._team_can_see_player(tactical_listener.team_index, mover)
            if is_visible:
                user.speak_l(
                    (
                        "breachpoint-enemy-moves-visible"
                        if was_visible
                        else "breachpoint-enemy-spotted"
                    ),
                    buffer="game",
                    player=mover.name,
                    location=self._node_name(user.locale, destination_id),
                )
            elif was_visible:
                user.speak_l(
                    "breachpoint-enemy-lost",
                    buffer="game",
                    player=mover.name,
                )
            else:
                user.speak_l(
                    "breachpoint-enemy-moves-hidden",
                    buffer="game",
                    player=mover.name,
                )

    def _announce_new_movement_contacts(
        self,
        mover: BreachPointPlayer,
        visibility_before: dict[str, tuple[bool, bool]],
    ) -> None:
        """Announce enemies newly revealed by movement without leaking fog state."""

        for enemy_id, (
            mover_saw_before,
            team_saw_before,
        ) in visibility_before.items():
            enemy = self._breach_player_by_id(enemy_id)
            if not enemy or enemy.eliminated:
                continue
            mover_sees_now = self._can_see(mover, enemy)
            if not mover_sees_now:
                continue
            for listener in self._players_on_team(mover.team_index):
                user = self.get_user(listener)
                if not user or listener.is_spectator:
                    continue
                personally_revealed = listener.id == mover.id and not mover_saw_before
                newly_shared = listener.id != mover.id and not team_saw_before
                if not (personally_revealed or newly_shared):
                    continue
                user.speak_l(
                    "breachpoint-enemy-spotted",
                    buffer="game",
                    player=enemy.name,
                    location=self._node_name(user.locale, enemy.position_id),
                )

    def _announce_plant_started(self, planter: BreachPointPlayer) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            tactical_listener = self._breach_player(listener)
            if not user or not tactical_listener or tactical_listener.is_spectator:
                continue
            if tactical_listener.team_index == TEAM_TERRORISTS:
                key = (
                    "breachpoint-plant-start-you"
                    if tactical_listener.id == planter.id
                    else "breachpoint-plant-start-ally"
                )
            elif self._team_can_see_node(
                tactical_listener.team_index, planter.position_id
            ):
                key = "breachpoint-plant-start-enemy"
            else:
                key = "breachpoint-plant-start-concealed"
            user.speak_l(
                key,
                buffer="game",
                player=planter.name,
                location=self._node_name(user.locale, planter.position_id),
            )

    def _complete_pending_plant(self) -> bool:
        if self.bomb_state != BOMB_PLANTING:
            return False
        planter = self._breach_player_by_id(self.planting_player_id)
        if (
            not planter
            or planter.eliminated
            or planter.team_index != TEAM_TERRORISTS
            or planter.position_id != self.planting_location_id
            or planter.position_id not in self.tactical_map.bomb_site_ids()
        ):
            self._normalize_bomb_state(
                [
                    player
                    for player in self.get_active_players()
                    if isinstance(player, BreachPointPlayer)
                ]
            )
            return False

        self.bomb_state = BOMB_PLANTED
        self.bomb_carrier_id = ""
        self.bomb_location_id = planter.position_id
        self._set_bomb_grid_point(self._player_grid_point(planter))
        self._normalize_bomb_grid_point()
        self.bomb_fuse_remaining = self.rules.bomb_fuse_tactical_rounds
        self.bomb_planted_tactical_round = self.tactical_round
        self.planting_player_id = ""
        self.planting_location_id = ""
        reward = self._add_cash(planter, self.economy.planter_reward)
        self._play_bomb_planted_audio(
            planter,
            self._bomb_grid_point(),
        )
        self._play_global_audio_chain(
            (RADIO_BOMB_PLANTED_ASSET,),
            priority=92,
        )
        self._play_music_cue(
            MUSIC_BOMB_PLANTED_ASSET,
            looping=True,
            priority=35,
        )
        self.broadcast_personal_l(
            planter,
            "breachpoint-plant-completes-you",
            "breachpoint-plant-completes-player",
            buffer="game",
            location=lambda locale: self._node_name(locale, planter.position_id),
            rounds=self.bomb_fuse_remaining,
            reward=reward,
            cash=planter.cash,
        )
        self.refresh_menus()
        return True

    def _interrupt_plant(
        self, planter: BreachPointPlayer, attacker: BreachPointPlayer
    ) -> None:
        if self.bomb_state != BOMB_PLANTING or planter.id != self.planting_player_id:
            return
        self.bomb_state = BOMB_CARRIED
        self._clear_bomb_grid_point()
        self.planting_player_id = ""
        self.planting_location_id = ""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == attacker.id:
                key = "breachpoint-plant-interrupted-you"
            elif listener.id == planter.id:
                key = "breachpoint-plant-interrupted-target"
            else:
                key = "breachpoint-plant-interrupted-player"
            user.speak_l(
                key,
                buffer="game",
                player=attacker.name,
                planter=planter.name,
            )

    def _complete_pending_defuse(self) -> bool:
        if not self.defusing_player_id:
            return False
        defuser = self._breach_player_by_id(self.defusing_player_id)
        location_id = self.defusing_location_id
        if (
            not defuser
            or defuser.eliminated
            or defuser.team_index != TEAM_COUNTER_TERRORISTS
            or self.bomb_state != BOMB_PLANTED
            or location_id != self.bomb_location_id
            or defuser.position_id != location_id
        ):
            self._clear_pending_defuse()
            return False
        self._clear_pending_defuse()
        reward = self._add_cash(defuser, self.economy.defuser_reward)
        self._play_bomb_audio(
            BOMB_DEFUSED_ASSET,
            location_id,
            actor_id=defuser.id,
            source=self._bomb_grid_point(),
        )
        self.broadcast_personal_l(
            defuser,
            "breachpoint-defuse-complete-you",
            "breachpoint-defuse-complete-player",
            buffer="game",
            location=lambda locale: self._node_name(locale, location_id),
            reward=reward,
            cash=defuser.cash,
        )
        self._finish_combat_round(TEAM_COUNTER_TERRORISTS, WIN_DEFUSED)
        return True

    def _interrupt_defuse(
        self, defuser: BreachPointPlayer, attacker: BreachPointPlayer
    ) -> None:
        if defuser.id != self.defusing_player_id:
            return
        self._clear_pending_defuse()
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == attacker.id:
                key = "breachpoint-defuse-interrupted-you"
            elif listener.id == defuser.id:
                key = "breachpoint-defuse-interrupted-target"
            else:
                key = "breachpoint-defuse-interrupted-player"
            user.speak_l(
                key,
                buffer="game",
                player=attacker.name,
                defuser=defuser.name,
            )

    def _announce_shot(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        outcome: AttackOutcome,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.is_spectator:
                user.speak_l(
                    "breachpoint-shot-spectator",
                    buffer="game",
                    shooter=shooter.name,
                    target=target.name,
                    weapon=self._weapon_name(user.locale, weapon),
                    result=self._attack_result(user.locale, outcome),
                )
                continue
            kwargs = {
                "shooter": shooter.name,
                "target": target.name,
                "location": self._node_name(user.locale, target.position_id),
                "weapon": self._weapon_name(user.locale, weapon),
                "result": self._attack_result(user.locale, outcome),
            }
            if listener.id == shooter.id:
                key = "breachpoint-shot-you"
            elif listener.id == target.id:
                key = "breachpoint-shot-target"
            else:
                key = "breachpoint-shot-observer"
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_elimination(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        *,
        source_name_key: str,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if shooter.id == target.id:
                key = (
                    "breachpoint-elimination-self-you"
                    if listener.id == target.id
                    else "breachpoint-elimination-self-observer"
                )
            elif listener.id == shooter.id:
                key = "breachpoint-elimination-you"
            elif listener.id == target.id:
                key = "breachpoint-elimination-target"
            else:
                key = "breachpoint-elimination-observer"
            user.speak_l(
                key,
                buffer="game",
                shooter=shooter.name,
                target=target.name,
                location=self._node_name(user.locale, target.position_id),
                weapon=Localization.get(user.locale, source_name_key),
            )

    def _announce_utility_damage(
        self,
        source: BreachPointPlayer,
        target: BreachPointPlayer,
        utility: UtilityProfile,
        outcome: UtilityDamageOutcome,
        *,
        source_saw_target: bool,
    ) -> None:
        """Report damage without revealing a surviving concealed target."""

        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if not tactical_listener or not user or tactical_listener.is_spectator:
                continue
            if listener.id == target.id:
                key = "breachpoint-utility-damage-target"
            elif listener.id == source.id:
                if not source_saw_target:
                    continue
                key = "breachpoint-utility-damage-you"
            elif (
                tactical_listener.team_index == target.team_index
                or self._viewer_can_see_player(listener, target)
            ):
                key = "breachpoint-utility-damage-observer"
            else:
                continue
            user.speak_l(
                key,
                buffer="game",
                target=target.name,
                utility=self._utility_name(user.locale, utility),
                location=self._node_name(user.locale, target.position_id),
                result=self._utility_damage_result(user.locale, outcome),
            )

    def _drop_bomb_from_eliminated_carrier(self, player: BreachPointPlayer) -> None:
        if (
            self.bomb_state not in {BOMB_CARRIED, BOMB_PLANTING}
            or player.id != self.bomb_carrier_id
        ):
            return
        self.bomb_state = BOMB_DROPPED
        self.bomb_carrier_id = ""
        self.bomb_location_id = player.position_id
        self._set_bomb_grid_point(self._player_grid_point(player))
        self._normalize_bomb_grid_point()
        self.planting_player_id = ""
        self.planting_location_id = ""
        for listener in self.players:
            user = self.get_user(listener)
            tactical_listener = self._breach_player(listener)
            if not user or not tactical_listener or tactical_listener.is_spectator:
                continue
            if (
                tactical_listener.team_index == TEAM_TERRORISTS
                or self._team_can_see_node(
                    tactical_listener.team_index, player.position_id
                )
            ):
                user.speak_l(
                    "breachpoint-bomb-dropped",
                    buffer="game",
                    location=self._node_name(user.locale, player.position_id),
                )

    def _check_elimination_victory(
        self,
        *,
        simultaneous_winner_team_index: int = -1,
    ) -> bool:
        winner = self._elimination_victory_side(
            simultaneous_winner_team_index=simultaneous_winner_team_index,
        )
        if winner is None:
            return False
        self._finish_combat_round(winner, WIN_ELIMINATION)
        return True

    def _elimination_victory_side(
        self,
        *,
        simultaneous_winner_team_index: int = -1,
    ) -> int | None:
        """Return the elimination winner without committing round side effects."""

        terrorists_alive = bool(self._players_on_team(TEAM_TERRORISTS, alive_only=True))
        counter_terrorists_alive = bool(
            self._players_on_team(TEAM_COUNTER_TERRORISTS, alive_only=True)
        )
        if not terrorists_alive and not counter_terrorists_alive:
            return (
                TEAM_TERRORISTS
                if self.bomb_state == BOMB_PLANTED
                else simultaneous_winner_team_index
                if simultaneous_winner_team_index in TEAM_INDEXES
                else TEAM_COUNTER_TERRORISTS
            )
        if not counter_terrorists_alive:
            return TEAM_TERRORISTS
        if self.bomb_state != BOMB_PLANTED and not terrorists_alive:
            return TEAM_COUNTER_TERRORISTS
        return None

    def _finish_combat_round(self, winning_side_index: int, reason: str) -> None:
        if self.status != "playing" or any(
            self.has_active_sequence(tag=tag)
            for tag in (
                ROUND_TRANSITION_SEQUENCE_TAG,
                MATCH_RESULT_SEQUENCE_TAG,
            )
        ):
            return
        self._clear_round_recovery()
        self._retire_round_audio()
        self._bot_coordinator.record_round_result(self, winning_side_index)
        self.reaction_window = ReactionWindow()
        winning_squad_index = self._squad_for_side(winning_side_index)
        winning_team = next(
            (
                team
                for team in self._team_manager.teams
                if team.index == winning_squad_index
            ),
            None,
        )
        if not winning_team:
            return
        winning_team.total_score += 1
        self.last_round_win_reason = reason
        radio_assets = (
            (RADIO_BOMB_DEFUSED_ASSET, RADIO_COUNTER_TERRORISTS_WIN_ASSET)
            if reason == WIN_DEFUSED
            else (RADIO_TERRORISTS_WIN_ASSET,)
            if winning_side_index == TEAM_TERRORISTS
            else (RADIO_COUNTER_TERRORISTS_WIN_ASSET,)
        )
        self._play_global_audio_chain(radio_assets, priority=94)
        self._play_round_result_music(winning_squad_index)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            tactical_listener = self._breach_player(listener)
            key = (
                "breachpoint-combat-round-won-you"
                if tactical_listener
                and not tactical_listener.is_spectator
                and tactical_listener.squad_index == winning_squad_index
                else "breachpoint-combat-round-won-other"
            )
            user.speak_l(
                key,
                buffer="game",
                round=self.round,
                squad=self._squad_name(user.locale, winning_squad_index),
                side=self._team_name(user.locale, winning_side_index),
                reason=Localization.get(
                    user.locale, f"breachpoint-win-reason-{reason}"
                ),
                score=self._score_summary(user.locale),
            )

        if self.overtime_period:
            score_delta = (
                self._squad_score(winning_squad_index)
                - self.overtime_start_scores[winning_squad_index]
            )
            if score_delta >= self.rules.overtime_half_rounds + 1:
                self._queue_match_finish(winning_squad_index, MATCH_OVERTIME)
                return
            if self.overtime_round >= self.rules.overtime_half_rounds * 2:
                self.overtime_period += 1
                self.overtime_round = 1
                self.overtime_start_scores = [
                    self._squad_score(squad_index) for squad_index in TEAM_INDEXES
                ]
                self._swap_sides()
                self._reset_economy(self.economy.overtime_cash)
                self.broadcast_l(
                    "breachpoint-overtime-restarts",
                    buffer="game",
                    period=self.overtime_period,
                )
            else:
                if self.overtime_round == self.rules.overtime_half_rounds:
                    self._swap_sides()
                    self._reset_economy(self.economy.overtime_cash)
                else:
                    self._settle_round_economy(winning_side_index, reason)
                self.overtime_round += 1
            self.round += 1
            self._queue_next_combat_round()
            return

        if winning_team.total_score >= self.match_format.rounds_to_win:
            self._queue_match_finish(winning_squad_index, MATCH_REGULATION)
            return
        if self.round >= self.match_format.regulation_rounds:
            if self.options.overtime_mode == OVERTIME_DRAW:
                self._queue_match_finish(-1, MATCH_DRAW)
                return
            self.overtime_period = 1
            self.overtime_round = 1
            self.overtime_start_scores = [
                self._squad_score(squad_index) for squad_index in TEAM_INDEXES
            ]
            self._swap_sides()
            self._reset_economy(self.economy.overtime_cash)
            self.broadcast_l(
                "breachpoint-overtime-starts",
                buffer="game",
                period=self.overtime_period,
            )
        elif self.round == self.match_format.rounds_per_half:
            self._swap_sides()
            self._reset_economy(self.economy.starting_cash)
            self.broadcast_l("breachpoint-halftime", buffer="game")
        else:
            self._settle_round_economy(winning_side_index, reason)

        self.round += 1
        self._queue_next_combat_round()

    def _queue_match_finish(self, squad_index: int, reason: str) -> None:
        """Hold the final scoreboard for the CS-style result interval."""

        payload = {"squad_index": squad_index, "reason": reason}
        self.start_sequence(
            MATCH_RESULT_SEQUENCE_TAG,
            [
                SequenceBeat.pause(MATCH_RESULT_DELAY_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            MATCH_RESULT_FINISH_CALLBACK,
                            payload,
                        )
                    ]
                ),
            ],
            tag=MATCH_RESULT_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"seconds": MATCH_RESULT_DELAY_SECONDS, "payload": payload},
        )
        self.refresh_menus()

    def _retire_round_audio(self) -> None:
        """Stop replayable round sources and abandon unfinished action flows."""

        self._stop_all_utility_flight_audio()
        for effect in self.area_effects:
            if effect.effect == UTILITY_EFFECT_FIRE:
                self._stop_fire_audio(effect.node_id)
        self.cancel_sequences_by_tag(MOVEMENT_SEQUENCE_TAG)
        self.cancel_sequences_by_tag(UTILITY_SEQUENCE_TAG)
        self.cancel_sequences_by_tag(WEAPON_SEQUENCE_TAG)
        self.cancel_sequences_by_tag(BOMB_DETONATION_SEQUENCE_TAG)

    def _queue_next_combat_round(self) -> None:
        """Hold a clean post-round boundary before preparing the next round."""

        self.start_sequence(
            ROUND_TRANSITION_SEQUENCE_TAG,
            [
                SequenceBeat.pause(ROUND_TRANSITION_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            ROUND_TRANSITION_CALLBACK,
                        )
                    ]
                ),
            ],
            tag=ROUND_TRANSITION_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"seconds": ROUND_TRANSITION_SECONDS},
        )
        self.refresh_menus()

    def _start_next_combat_round(self) -> None:
        self._stop_round_tail_audio()
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        self._prepare_combat_round(active_players)
        self._announce_combat_round_start()
        self._start_buy_phase()

    def _settle_round_economy(self, winning_side_index: int, reason: str) -> None:
        """Pay both persistent squads after a non-boundary combat round."""

        winning_squad_index = self._squad_for_side(winning_side_index)
        losing_side_index = next(
            side_index
            for side_index in TEAM_INDEXES
            if side_index != winning_side_index
        )
        losing_squad_index = self._squad_for_side(losing_side_index)
        self.squad_loss_streaks[winning_squad_index] = max(
            0,
            self.squad_loss_streaks[winning_squad_index] - 1,
        )
        losing_loss_count = self.squad_loss_streaks[losing_squad_index]
        loss_reward = self.economy.loss_reward(losing_loss_count)
        self.squad_loss_streaks[losing_squad_index] = min(
            self.economy.maximum_loss_count,
            losing_loss_count + 1,
        )
        win_reward = self.economy.win_reward(reason)
        planted_loss_bonus = (
            self.economy.plant_team_bonus
            if losing_side_index == TEAM_TERRORISTS and reason == WIN_DEFUSED
            else 0
        )
        for active_player in self.get_active_players():
            tactical_player = self._breach_player(active_player)
            user = self.get_user(active_player)
            if not tactical_player or tactical_player.is_spectator:
                continue
            if tactical_player.squad_index == winning_squad_index:
                reward = win_reward
            elif tactical_player.squad_index == losing_squad_index:
                reward = loss_reward + planted_loss_bonus
            else:
                continue
            credited = self._add_cash(tactical_player, reward)
            if user:
                user.speak_l(
                    "breachpoint-round-income",
                    buffer="game",
                    amount=credited,
                    cash=tactical_player.cash,
                )

    def _score_summary(self, locale: str) -> str:
        return Localization.get(
            locale,
            "breachpoint-score-summary",
            team_one=self._squad_name(locale, TEAM_TERRORISTS),
            team_one_score=self._squad_score(TEAM_TERRORISTS),
            team_two=self._squad_name(locale, TEAM_COUNTER_TERRORISTS),
            team_two_score=self._squad_score(TEAM_COUNTER_TERRORISTS),
        )

    def _squad_scoreboard(self) -> list[tuple[int, int, int]]:
        """Return persistent squad scores paired with their current sides."""

        return [
            (
                squad_index,
                self._squad_score(squad_index),
                self._side_for_squad(squad_index),
            )
            for squad_index in TEAM_INDEXES
        ]

    def _finish_match(self, squad_index: int, reason: str) -> None:
        if self.status != "playing":
            return
        self.reaction_window = ReactionWindow()
        self._clear_round_recovery()
        self._reset_dropped_weapons()
        self.area_effects = []
        self.winning_team_index = squad_index
        self.win_reason = reason
        if reason != MATCH_DRAW:
            self._play_global_asset(
                MATCH_VICTORY_ASSET,
                priority=100,
                max_instances=1,
            )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            tactical_listener = self._breach_player(listener)
            if reason == MATCH_DRAW:
                key = "breachpoint-match-draw"
            elif (
                tactical_listener
                and not tactical_listener.is_spectator
                and tactical_listener.squad_index == squad_index
            ):
                key = "breachpoint-victory-you"
            else:
                key = "breachpoint-victory-other"
            user.speak_l(
                key,
                buffer="game",
                team=self._squad_name(user.locale, squad_index),
                reason=Localization.get(
                    user.locale, f"breachpoint-win-reason-{reason}"
                ),
                score=self._score_summary(user.locale),
            )
        self._bot_coordinator.clear()
        self.finish_game()

    # ------------------------------------------------------------------
    # Information actions
    # ------------------------------------------------------------------

    def _action_read_vitals(self, player: Player, action_id: str) -> None:
        tactical_player = self._breach_player(player)
        user = self.get_user(player)
        if not tactical_player or not user or tactical_player.is_spectator:
            return
        user.speak_l(
            "breachpoint-vitals-status",
            buffer="game",
            health=tactical_player.health,
            max_health=self.rules.max_health,
            armor=tactical_player.armor,
        )

    def _action_read_position(self, player: Player, action_id: str) -> None:
        tactical_player = self._breach_player(player)
        user = self.get_user(player)
        if not tactical_player or not user or tactical_player.is_spectator:
            return
        user.speak_l(
            "breachpoint-position-status",
            buffer="game",
            location=self._node_name(user.locale, tactical_player.position_id),
            team=self._team_name(user.locale, tactical_player.team_index),
            ap=tactical_player.action_points,
            primary=self._weapon_name(
                user.locale, self._primary_weapon(tactical_player)
            ),
            sidearm=self._weapon_name(user.locale, self._sidearm(tactical_player)),
            equipped=self._weapon_name(
                user.locale, self._equipped_weapon(tactical_player)
            ),
            ammunition=self._ammunition_summary(
                user.locale,
                tactical_player,
                self._equipped_weapon(tactical_player),
            ),
            ground=self._ground_weapon_summary(
                user.locale,
                tactical_player.position_id,
            ),
            utility=self._utility_summary(user.locale, tactical_player),
            equipment=self._equipment_summary(user.locale, tactical_player),
            cash=tactical_player.cash,
            guard=tactical_player.guard_points,
            angle=self._held_angle_status(user.locale, tactical_player),
            effects=self._known_area_effect_status(
                user.locale,
                tactical_player,
                tactical_player.position_id,
            ),
        )

    def _action_read_map(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "breachpoint_map",
            self._build_map_status,
        )

    def _build_map_status(self, player: Player, user: User) -> list[MenuItem]:
        tactical_viewer = self._breach_player(player)
        items = [
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "breachpoint-map-header",
                    map=Localization.get(user.locale, self.tactical_map.name_key),
                    round=self.round,
                    phase=self._round_phase_label(user.locale),
                ),
                id="breachpoint_map_header",
            )
        ]
        if tactical_viewer and not tactical_viewer.is_spectator:
            items.append(
                MenuItem(
                    text=self._spatial_context(
                        user.locale,
                        tactical_viewer.position_id,
                    ),
                    id="breachpoint_map_spatial_context",
                )
            )
        for node in self.tactical_map.nodes:
            effect_status = self._known_area_effect_status(
                user.locale,
                tactical_viewer,
                node.id,
            )
            occupants = [
                tactical_player
                for tactical_player in self.get_active_players()
                if isinstance(tactical_player, BreachPointPlayer)
                and tactical_player.position_id == node.id
                and self._viewer_knows_player_location(player, tactical_player)
            ]
            occupant_text = self._format_node_occupants(user.locale, occupants)
            ground_visible = bool(
                tactical_viewer
                and not tactical_viewer.is_spectator
                and self._team_can_see_node(tactical_viewer.team_index, node.id)
            )
            ground_text = (
                self._ground_weapon_summary(user.locale, node.id)
                if ground_visible
                else Localization.get(
                    user.locale,
                    "breachpoint-ground-weapons-unconfirmed",
                )
            )
            site = (
                Localization.get(user.locale, "breachpoint-map-bomb-site")
                if node.bomb_site
                else Localization.get(user.locale, "breachpoint-map-normal-area")
            )
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "breachpoint-map-node-line",
                        location=self._node_name(user.locale, node.id),
                        site=site,
                        occupants=occupant_text,
                        ground=ground_text,
                        exits=Localization.format_list_and(
                            user.locale,
                            [
                                self._node_name(user.locale, neighbor_id)
                                for neighbor_id in node.adjacent
                            ],
                        ),
                        sightlines=Localization.format_list_and(
                            user.locale,
                            [
                                Localization.get(
                                    user.locale,
                                    "breachpoint-map-sightline-entry",
                                    location=self._node_name(user.locale, visible_id),
                                    range=self._combat_distance(node.id, visible_id),
                                )
                                for visible_id in self.tactical_map.visible_node_ids(
                                    node.id
                                )
                            ],
                        ),
                        effect=effect_status,
                    ),
                    id=f"breachpoint_map_node_{node.id}",
                )
            )
        return items

    def _format_node_occupants(
        self, locale: str, occupants: list[BreachPointPlayer]
    ) -> str:
        if not occupants:
            return Localization.get(locale, "breachpoint-map-empty")
        labels = []
        for occupant in occupants:
            state_key = (
                "breachpoint-player-eliminated"
                if occupant.eliminated
                else "breachpoint-player-active"
            )
            labels.append(
                Localization.get(
                    locale,
                    "breachpoint-map-occupant",
                    player=occupant.name,
                    team=self._team_name(locale, occupant.team_index),
                    health=occupant.health,
                    state=Localization.get(locale, state_key),
                )
            )
        return Localization.format_list_and(locale, labels)

    def _action_read_teammates(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "breachpoint_teammates",
            self._build_teammate_status,
        )

    def _build_teammate_status(
        self,
        player: Player,
        user: User,
    ) -> list[MenuItem]:
        tactical_viewer = self._breach_player(player)
        if not tactical_viewer or tactical_viewer.is_spectator:
            return []
        teammates = [
            teammate
            for teammate in self.get_active_players()
            if isinstance(teammate, BreachPointPlayer)
            and teammate.id != tactical_viewer.id
            and teammate.squad_index == tactical_viewer.squad_index
        ]
        if not teammates:
            return [
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "breachpoint-teammate-none",
                    ),
                    id="breachpoint_teammates_empty",
                )
            ]
        items = [
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "breachpoint-teammate-header",
                    team=self._team_name(user.locale, tactical_viewer.team_index),
                    alive=sum(not teammate.eliminated for teammate in teammates),
                    total=len(teammates),
                ),
                id="breachpoint_teammates_header",
            )
        ]
        for teammate in teammates:
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "breachpoint-teammate-line",
                        player=teammate.name,
                        location=self._node_name(user.locale, teammate.position_id),
                        health=teammate.health,
                        armor=teammate.armor,
                        weapon=self._weapon_name(
                            user.locale,
                            self._equipped_weapon(teammate),
                        ),
                        cash=teammate.cash,
                        state=Localization.get(
                            user.locale,
                            (
                                "breachpoint-player-eliminated"
                                if teammate.eliminated
                                else "breachpoint-player-active"
                            ),
                        ),
                    ),
                    id=f"breachpoint_teammate_{teammate.id}",
                )
            )
        return items

    def _action_read_enemies(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "breachpoint_enemies",
            self._build_enemy_status,
        )

    def _build_enemy_status(
        self,
        player: Player,
        user: User,
    ) -> list[MenuItem]:
        tactical_viewer = self._breach_player(player)
        if not tactical_viewer or tactical_viewer.is_spectator:
            return []
        enemies = [
            enemy
            for enemy in self.get_active_players()
            if isinstance(enemy, BreachPointPlayer)
            and enemy.squad_index != tactical_viewer.squad_index
        ]
        known_enemies = [
            enemy
            for enemy in enemies
            if self._viewer_knows_player_location(player, enemy)
        ]
        items = [
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "breachpoint-enemy-header",
                    known=len(known_enemies),
                    total=len(enemies),
                ),
                id="breachpoint_enemies_header",
            )
        ]
        if not known_enemies:
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "breachpoint-enemy-none",
                    ),
                    id="breachpoint_enemies_empty",
                )
            )
            return items
        for enemy in known_enemies:
            if enemy.eliminated:
                text = Localization.get(
                    user.locale,
                    "breachpoint-enemy-line-eliminated",
                    player=enemy.name,
                    location=self._node_name(user.locale, enemy.position_id),
                )
            else:
                text = Localization.get(
                    user.locale,
                    "breachpoint-enemy-line",
                    player=enemy.name,
                    location=self._node_name(user.locale, enemy.position_id),
                    health=enemy.health,
                    armor=enemy.armor,
                    state=Localization.get(
                        user.locale,
                        "breachpoint-player-active",
                    ),
                )
            items.append(
                MenuItem(
                    text=text,
                    id=f"breachpoint_enemy_{enemy.id}",
                )
            )
        return items

    def _action_read_bomb(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(self._bomb_status_line(player, user.locale), buffer="game")

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        """Report decision ownership instead of only the suspended turn owner."""

        del action_id
        user = self.get_user(player)
        if not user:
            return
        if self.pending_weapon_donation:
            recipient = self._breach_player_by_id(
                self.pending_weapon_donation.recipient_id
            )
            if recipient:
                user.speak_l(
                    (
                        "breachpoint-whose-turn-donation-you"
                        if recipient.id == player.id
                        else "breachpoint-whose-turn-donation-player"
                    ),
                    buffer="game",
                    player=recipient.name,
                )
                return
        if self.reaction_window.is_open:
            responder = self._breach_player_by_id(
                self.reaction_window.responding_player_id
            )
            if responder:
                user.speak_l(
                    (
                        "breachpoint-whose-turn-reaction-you"
                        if responder.id == player.id
                        else "breachpoint-whose-turn-reaction-player"
                    ),
                    buffer="game",
                    player=responder.name,
                )
                return
        recovery_player = self._breach_player_by_id(self.round_recovery_player_id)
        if recovery_player:
            user.speak_l(
                (
                    "breachpoint-whose-turn-recovery-you"
                    if recovery_player.id == player.id
                    else "breachpoint-whose-turn-recovery-player"
                ),
                buffer="game",
                player=recovery_player.name,
            )
            return
        super()._action_whose_turn(player, "whose_turn")

    def _bomb_status_line(self, viewer: Player, locale: str) -> str:
        if self.bomb_state == BOMB_PLANTED:
            if self.has_active_sequence(tag=BOMB_DETONATION_SEQUENCE_TAG):
                return Localization.get(
                    locale,
                    "breachpoint-bomb-status-detonating",
                    location=self._node_name(locale, self.bomb_location_id),
                )
            defuser = self._breach_player_by_id(self.defusing_player_id)
            if defuser:
                return Localization.get(
                    locale,
                    "breachpoint-bomb-status-defusing",
                    player=defuser.name,
                    location=self._node_name(locale, self.bomb_location_id),
                    rounds=self.bomb_fuse_remaining,
                )
            return Localization.get(
                locale,
                "breachpoint-bomb-status-planted",
                location=self._node_name(locale, self.bomb_location_id),
                rounds=self.bomb_fuse_remaining,
            )
        tactical_viewer = self._breach_player(viewer)
        if tactical_viewer and tactical_viewer.is_spectator:
            return Localization.get(
                locale,
                "breachpoint-bomb-status-spectator-concealed",
            )
        if not tactical_viewer:
            return Localization.get(locale, "breachpoint-bomb-status-concealed")
        viewer_is_terrorist = tactical_viewer.team_index == TEAM_TERRORISTS
        if self.bomb_state == BOMB_PLANTING:
            planter = self._breach_player_by_id(self.planting_player_id)
            if planter and (
                viewer_is_terrorist
                or self._team_can_see_node(
                    tactical_viewer.team_index, planter.position_id
                )
            ):
                return Localization.get(
                    locale,
                    "breachpoint-bomb-status-planting",
                    player=planter.name,
                    location=self._node_name(locale, planter.position_id),
                )
            return Localization.get(locale, "breachpoint-bomb-status-concealed")
        if self.bomb_state == BOMB_DROPPED:
            if not viewer_is_terrorist and not self._team_can_see_node(
                tactical_viewer.team_index, self.bomb_location_id
            ):
                return Localization.get(locale, "breachpoint-bomb-status-concealed")
            return Localization.get(
                locale,
                "breachpoint-bomb-status-dropped",
                location=self._node_name(locale, self.bomb_location_id),
            )
        carrier = self._breach_player_by_id(self.bomb_carrier_id)
        if carrier and (
            viewer_is_terrorist
            or self._team_can_see_player(tactical_viewer.team_index, carrier)
        ):
            return Localization.get(
                locale,
                "breachpoint-bomb-status-carried",
                player=carrier.name,
                location=self._node_name(locale, carrier.position_id),
            )
        if carrier:
            return Localization.get(locale, "breachpoint-bomb-status-concealed")
        return Localization.get(locale, "breachpoint-bomb-status-unavailable")

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        for squad_index, score, side_index in self._squad_scoreboard():
            user.speak_l(
                "breachpoint-score-brief",
                buffer="game",
                round=self.round,
                squad=self._squad_name(user.locale, squad_index),
                score=score,
                side=self._team_name(user.locale, side_index),
            )

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "breachpoint_scores",
            lambda _player, user: self._score_status_lines(user.locale),
        )

    def _score_status_lines(self, locale: str) -> list[str]:
        lines = [
            Localization.get(
                locale,
                "breachpoint-score-header",
                round=self.round,
                format=Localization.get(
                    locale, f"breachpoint-match-format-{self.match_format.id}"
                ),
            )
        ]
        for squad_index, score, side_index in self._squad_scoreboard():
            lines.append(
                Localization.get(
                    locale,
                    "breachpoint-score-line",
                    squad=self._squad_name(locale, squad_index),
                    score=score,
                    side=self._team_name(locale, side_index),
                )
            )
        if self.overtime_period:
            lines.append(
                Localization.get(
                    locale,
                    "breachpoint-score-overtime",
                    period=self.overtime_period,
                    round=self.overtime_round,
                    half=self.rules.overtime_half_rounds,
                )
            )
        else:
            lines.append(
                Localization.get(
                    locale,
                    "breachpoint-score-regulation",
                    round=self.round,
                    half=self.match_format.rounds_per_half,
                    target=self.match_format.rounds_to_win,
                )
            )
        return lines

    # ------------------------------------------------------------------
    # Bot strategy
    # ------------------------------------------------------------------

    def bot_think(self, player: Player) -> str | None:
        bot = self._breach_player(player)
        if not bot:
            return None
        return self._bot_coordinator.choose_action(self, bot)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        winner_ids = [
            player.id
            for player in active_players
            if player.squad_index == self.winning_team_index
        ]
        team_rankings = []
        for squad_index in TEAM_INDEXES:
            team_rankings.append(
                {
                    "team_index": squad_index,
                    "members": [
                        player.name
                        for player in active_players
                        if player.squad_index == squad_index
                    ],
                    "score": self._squad_score(squad_index),
                }
            )
        team_rankings.sort(key=lambda entry: entry["score"], reverse=True)
        return GameResult.create(
            game_type=self.get_type(),
            duration_ticks=self.sound_scheduler_tick,
            players=[
                (
                    player.id,
                    player.name,
                    player.is_bot and not player.replaced_human,
                )
                for player in active_players
            ],
            custom_data={
                "winner_ids": winner_ids,
                "winning_team_index": self.winning_team_index,
                "win_reason": self.win_reason,
                "rounds_played": self.round,
                "overtime_periods": self.overtime_period,
                "team_rankings": team_rankings,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        team_index = int(result.custom_data.get("winning_team_index", -1))
        reason = str(result.custom_data.get("win_reason", ""))
        rounds = int(result.custom_data.get("rounds_played", 0))
        team_rankings = result.custom_data.get("team_rankings", [])
        score_by_team = {
            int(entry.get("team_index", -1)): int(entry.get("score", 0))
            for entry in team_rankings
            if isinstance(entry, dict)
        }
        lines = [
            Localization.get(locale, "breachpoint-end-header"),
            Localization.get(
                locale,
                (
                    "breachpoint-end-draw"
                    if reason == MATCH_DRAW
                    else "breachpoint-end-winner"
                ),
                team=self._squad_name(locale, team_index),
            ),
            Localization.get(
                locale,
                "breachpoint-end-reason",
                reason=Localization.get(locale, f"breachpoint-win-reason-{reason}"),
            ),
            Localization.get(
                locale,
                "breachpoint-end-score",
                team_one=self._squad_name(locale, TEAM_TERRORISTS),
                team_one_score=score_by_team.get(TEAM_TERRORISTS, 0),
                team_two=self._squad_name(locale, TEAM_COUNTER_TERRORISTS),
                team_two_score=score_by_team.get(TEAM_COUNTER_TERRORISTS, 0),
            ),
            Localization.get(locale, "breachpoint-end-rounds", rounds=rounds),
        ]
        return lines
