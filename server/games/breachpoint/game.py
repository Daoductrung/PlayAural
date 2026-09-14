"""Breach Point - an audio-first turn-based tactical shooter."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult
from ...game_utils.options import MenuOption, option_field
from ...game_utils.reaction_window import ReactionWindow
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, GameOptions, Player
from ..registry import register_game
from .arsenal import (
    SIDE_COUNTER_TERRORISTS,
    SIDE_INDEXES,
    SIDE_TERRORISTS,
    STANDARD_ECONOMY,
    UTILITY_EFFECT_FLASH,
    UTILITY_EFFECT_SMOKE,
    WEAPON_SLOT_PRIMARY,
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
from .bot import BreachPointBotCoordinator
from .maps import DEFAULT_MAP_ID, TacticalMap, TacticalNode, get_tactical_map
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


@dataclass(frozen=True)
class AttackOutcome:
    """Resolved deterministic defenses for one successful shot."""

    rounds_fired: int
    rounds_on_target: int
    rounds_evaded: int
    health_damage: int
    armor_absorbed: int
    fully_evaded: bool


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
class BreachPointGame(Game):
    """A deterministic, graph-based bomb-defusal tactical game."""

    players: list[BreachPointPlayer] = field(default_factory=list)
    options: BreachPointOptions = field(default_factory=BreachPointOptions)

    map_id: str = DEFAULT_MAP_ID
    phase: str = PHASE_COMBAT
    buy_ready_player_ids: list[str] = field(default_factory=list)
    squad_loss_streaks: list[int] = field(
        default_factory=lambda: [
            STANDARD_ECONOMY.initial_loss_count for _ in TEAM_INDEXES
        ]
    )
    smoke_expirations: dict[str, int] = field(default_factory=dict)
    smoke_known_team_indexes: dict[str, list[int]] = field(default_factory=dict)
    tactical_round: int = 1
    round_acted_player_ids: list[str] = field(default_factory=list)
    bomb_state: str = BOMB_CARRIED
    bomb_carrier_id: str = ""
    bomb_location_id: str = ""
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

    def __post_init__(self) -> None:
        super().__post_init__()
        self._bot_coordinator = BreachPointBotCoordinator()

    def on_discard(self) -> None:
        """Release runtime-only tactical observations with the game instance."""

        self._bot_coordinator.clear()
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

        tactical_map = get_tactical_map(self.map_id) or get_tactical_map(DEFAULT_MAP_ID)
        if tactical_map is None:
            raise RuntimeError("Breach Point has no registered default map")
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
        action_set = ActionSet(name="turn")
        self._add_reaction_actions(action_set)
        self._add_buy_actions(action_set)
        self._add_objective_actions(action_set)
        self._add_weapon_actions(action_set)
        self._sync_aim_actions(action_set)
        self._sync_shoot_actions(action_set, player)
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
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="buy_armor",
                label="",
                handler="_action_buy_armor",
                is_enabled="_is_buy_armor_enabled",
                is_hidden="_is_buy_action_hidden",
                get_label="_get_buy_armor_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="finish_buy",
                label="",
                handler="_action_finish_buy",
                is_enabled="_is_finish_buy_enabled",
                is_hidden="_is_buy_action_hidden",
                get_label="_get_finish_buy_label",
                show_in_actions_menu=False,
            )
        )

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

    def _sync_aim_actions(self, action_set: ActionSet) -> None:
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
        action_set.add(
            Action(
                id="end_turn",
                label="",
                handler="_action_end_turn",
                is_enabled="_is_end_turn_enabled",
                is_hidden="_is_end_turn_hidden",
                get_label="_get_end_turn_label",
                show_in_actions_menu=False,
            )
        )

    def _sync_shoot_actions(self, action_set: ActionSet, player: Player) -> None:
        action_set.remove_by_prefix("shoot_")
        for target in self.get_active_players():
            if target.id == player.id:
                continue
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

    @staticmethod
    def _apply_turn_action_order(action_set: ActionSet) -> None:
        reaction_ids = [
            action_id
            for action_id in ("reaction_shoot", "reaction_pass")
            if action_set.get_action(action_id)
        ]
        buy_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_weapon_")
        ]
        buy_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_utility_")
        )
        buy_ids.extend(
            action_id
            for action_id in action_set._order
            if action_id.startswith("buy_equipment_")
        )
        buy_ids.extend(
            action_id
            for action_id in ("buy_armor", "finish_buy")
            if action_set.get_action(action_id)
        )
        objective_ids = [
            "plant",
            "defuse",
            "pick_up_bomb",
        ]
        weapon_ids = [
            action_id
            for action_id in ("equip_primary", "equip_sidearm")
            if action_set.get_action(action_id)
        ]
        aim_ids = [
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
        action_set._order = reaction_ids + buy_ids + [
            action_id for action_id in objective_ids if action_set.get_action(action_id)
        ]
        action_set._order.extend(weapon_ids)
        action_set._order.extend(aim_ids)
        action_set._order.extend(shoot_ids)
        action_set._order.extend(utility_ids)
        action_set._order.extend(move_ids)
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
                "read_teams",
                "breachpoint-action-read-teams",
                "_action_read_teams",
                "_is_read_teams_enabled",
                "_is_read_teams_hidden",
                True,
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
            "read_position",
            "read_map",
            "read_teams",
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
            self._sync_aim_actions(turn_set)
            self._sync_shoot_actions(turn_set, player)
            self._sync_utility_actions(turn_set)
            self._apply_turn_action_order(turn_set)
        standard_set = self.get_action_set(player, "standard")
        if standard_set:
            self._apply_standard_action_order(standard_set, self.get_user(player))

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
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
            Localization.get("en", "breachpoint-action-read-teams"),
            ["read_teams"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            Localization.get("en", "breachpoint-keybind-finish-or-end"),
            ["finish_buy", "end_turn"],
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
        self._apply_current_sides(active_players)
        self._reset_economy(self.economy.starting_cash, active_players)
        self._prepare_combat_round(active_players)
        self._announce_match_start()
        self._announce_combat_round_start()
        self._start_buy_phase()

    def _prepare_combat_round(
        self, active_players: list[BreachPointPlayer] | None = None
    ) -> None:
        active_players = active_players or [
            player
            for player in self.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ]
        self.tactical_round = 1
        self.round_acted_player_ids = []
        self.bomb_state = BOMB_CARRIED
        self.bomb_location_id = ""
        self.bomb_fuse_remaining = 0
        self.bomb_planted_tactical_round = 0
        self.planting_player_id = ""
        self.planting_location_id = ""
        self.defusing_player_id = ""
        self.defusing_location_id = ""
        self.reaction_window = ReactionWindow()
        self.smoke_expirations = {}
        self.smoke_known_team_indexes = {}

        for player in active_players:
            if player.eliminated:
                player.primary_weapon_id = ""
                player.armor = 0
                player.utility_counts = {}
                player.equipment_counts = {}
            primary = get_weapon(player.primary_weapon_id)
            if (
                not primary
                or primary.slot != WEAPON_SLOT_PRIMARY
                or player.team_index not in primary.allowed_sides
            ):
                player.primary_weapon_id = ""
            sidearm = get_default_sidearm(player.team_index)
            player.equipped_weapon_id = (
                (player.primary_weapon_id if player.primary_weapon_id else sidearm.id)
                if sidearm
                else ""
            )
            player.position_id = self._spawn_for_team(player.team_index)
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

        turn_players = self._get_team_turn_players(active_players)
        self.set_turn_players(turn_players)
        carrier = next(
            (
                player
                for player in turn_players
                if getattr(player, "team_index", -1) == TEAM_TERRORISTS
            ),
            None,
        )
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
            sidearm = get_default_sidearm(player.team_index)
            player.equipped_weapon_id = sidearm.id if sidearm else ""

    def _start_buy_phase(self) -> None:
        """Begin private sequential purchases for the new combat round."""

        self.phase = PHASE_BUY
        self.buy_ready_player_ids = []
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
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "breachpoint-buy-turn",
            buffer="game",
            cash=player.cash,
            weapon=self._weapon_name(user.locale, self._equipped_weapon(player)),
            armor=player.armor,
            utility=self._utility_summary(user.locale, player),
            equipment=self._equipment_summary(user.locale, player),
        )

    def _start_combat_phase(self) -> None:
        """Leave preparation and start the first tactical activation."""

        self.phase = PHASE_COMBAT
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

    def rebuild_runtime_state(self) -> None:
        super().rebuild_runtime_state()
        self._bot_coordinator.clear()
        if get_tactical_map(self.map_id) is None:
            self.map_id = DEFAULT_MAP_ID
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
        self.smoke_expirations = {
            node_id: max(self.tactical_round + 1, expiration)
            for node_id, expiration in self.smoke_expirations.items()
            if node_id in valid_nodes
            and isinstance(expiration, int)
            and expiration > self.tactical_round
        }
        self.smoke_known_team_indexes = {
            node_id: sorted(
                {
                    team_index
                    for team_index in team_indexes
                    if team_index in TEAM_INDEXES
                }
            )
            for node_id, team_indexes in self.smoke_known_team_indexes.items()
            if node_id in self.smoke_expirations and isinstance(team_indexes, list)
        }
        for player in active_players:
            if player.team_index not in TEAM_INDEXES:
                player.team_index = TEAM_TERRORISTS
            if player.position_id not in valid_nodes:
                player.position_id = self._spawn_for_team(player.team_index)
            player.cash = max(0, min(self.economy.maximum_cash, player.cash))
            player.armor = max(0, min(self.economy.maximum_armor, player.armor))
            primary = get_weapon(player.primary_weapon_id)
            if (
                not primary
                or primary.slot != WEAPON_SLOT_PRIMARY
                or player.team_index not in primary.allowed_sides
            ):
                player.primary_weapon_id = ""
                primary = None
            sidearm = get_default_sidearm(player.team_index)
            valid_equipped_ids = {
                weapon.id for weapon in (primary, sidearm) if weapon is not None
            }
            if player.equipped_weapon_id not in valid_equipped_ids:
                player.equipped_weapon_id = (
                    primary.id if primary else sidearm.id if sidearm else ""
                )
            owned_weapon_ids = valid_equipped_ids
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
            player.weapon_shots_fired_this_activation = {
                weapon_id: max(
                    0,
                    min(
                        weapon.shots_per_activation,
                        shot_count,
                    ),
                )
                for weapon_id, shot_count in (
                    player.weapon_shots_fired_this_activation.items()
                )
                if weapon_id in owned_weapon_ids
                and isinstance(shot_count, int)
                and (weapon := get_weapon(weapon_id)) is not None
            }
            player.weapon_target_ids_this_activation = {
                weapon_id: list(
                    dict.fromkeys(
                        target_id
                        for target_id in target_ids
                        if target_id in valid_player_ids and target_id != player.id
                    )
                )[: weapon.shots_per_activation]
                for weapon_id, target_ids in (
                    player.weapon_target_ids_this_activation.items()
                )
                if weapon_id in owned_weapon_ids
                and isinstance(target_ids, list)
                and (weapon := get_weapon(weapon_id)) is not None
            }
            if (
                not equipped
                or not equipped.requires_aim
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
                            self.rules.action_points_per_activation,
                            player.action_points,
                        ),
                    )
                    player.shots_fired_this_activation = max(
                        0,
                        min(
                            self.rules.action_points_per_activation,
                            player.shots_fired_this_activation,
                        ),
                    )

        self._normalize_bomb_state(active_players)
        self._normalize_defuse_state(active_players)
        self._normalize_reaction_window(active_players)
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
            or (self.phase == PHASE_BUY and current.id in acted_ids)
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
            self.bomb_carrier_id = ""
            self.bomb_fuse_remaining = max(
                1,
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
            self.bomb_fuse_remaining = 0
            self.bomb_planted_tactical_round = 0
            self.planting_player_id = ""
            self.planting_location_id = ""
        else:
            self.bomb_state = BOMB_DROPPED
            self.bomb_carrier_id = ""
            self.bomb_location_id = self.tactical_map.terrorist_spawn
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
                and window.response_action_points
                == expected_response_action_points
                and window.consumes_activation == responder_was_unacted
            )
        elif common_valid and window.kind == REACTION_DEFUSE:
            kind_valid = bool(
                self.bomb_state == BOMB_PLANTED
                and trigger.team_index == TEAM_COUNTER_TERRORISTS
                and responder.team_index == TEAM_TERRORISTS
                and self.defusing_player_id in {"", trigger.id}
                and window.response_action_points
                == expected_response_action_points
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
        if self.status != "playing":
            return
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

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

    def _node(self, node_id: str) -> TacticalNode | None:
        return self.tactical_map.get_node(node_id)

    def _node_name(self, locale: str, node_id: str) -> str:
        node = self._node(node_id)
        key = node.name_key if node else "breachpoint-node-unknown"
        return Localization.get(locale, key)

    @staticmethod
    def _weapon_from_buy_action(action_id: str) -> WeaponProfile | None:
        prefix = "buy_weapon_"
        if not action_id.startswith(prefix):
            return None
        return get_weapon(action_id[len(prefix) :])

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

    def _normalize_utility_counts(self, player: BreachPointPlayer) -> None:
        normalized: dict[str, int] = {}
        for utility in get_purchasable_utilities(player.team_index):
            count = player.utility_counts.get(utility.id, 0)
            if isinstance(count, int) and count > 0:
                normalized[utility.id] = min(utility.maximum_carry, count)
        player.utility_counts = normalized

    def _normalize_equipment_counts(self, player: BreachPointPlayer) -> None:
        normalized: dict[str, int] = {}
        for equipment in get_purchasable_equipment(player.team_index):
            count = player.equipment_counts.get(equipment.id, 0)
            if isinstance(count, int) and count > 0:
                normalized[equipment.id] = min(equipment.maximum_carry, count)
        player.equipment_counts = normalized

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
        return get_default_sidearm(player.team_index)

    def _primary_weapon(self, player: BreachPointPlayer) -> WeaponProfile | None:
        weapon = get_weapon(player.primary_weapon_id)
        if (
            weapon
            and weapon.slot == WEAPON_SLOT_PRIMARY
            and player.team_index in weapon.allowed_sides
        ):
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
        source = self._node(player.position_id)
        distance = self._node_distance(player.position_id, node_id)
        return bool(
            weapon
            and weapon.requires_aim
            and source
            and node_id in source.sightlines
            and distance is not None
            and distance <= weapon.max_range
        )

    def _is_smoked(self, node_id: str) -> bool:
        return self.smoke_expirations.get(node_id, 0) > self.tactical_round

    def _remember_smoke_for_team(self, node_id: str, team_index: int) -> None:
        if team_index not in TEAM_INDEXES:
            return
        known_teams = self.smoke_known_team_indexes.setdefault(node_id, [])
        if team_index not in known_teams:
            known_teams.append(team_index)
            known_teams.sort()

    def _team_knows_smoke(self, team_index: int, node_id: str) -> bool:
        return team_index in self.smoke_known_team_indexes.get(
            node_id, []
        ) or self._team_can_observe_node_effect(team_index, node_id)

    def _team_can_observe_node_effect(self, team_index: int, node_id: str) -> bool:
        """Return whether a team can see an area's effect, not through the effect."""

        if not self._node(node_id):
            return False
        for observer in self._players_on_team(team_index, alive_only=True):
            if observer.position_id == node_id:
                return True
            if self._is_smoked(observer.position_id):
                continue
            observer_node = self._node(observer.position_id)
            if observer_node and node_id in observer_node.sightlines:
                return True
        return False

    def _remember_observable_smokes_for_team(self, team_index: int) -> None:
        """Persist smoke contacts discovered as a team changes position."""

        for node_id in self.smoke_expirations:
            if self._team_can_observe_node_effect(team_index, node_id):
                self._remember_smoke_for_team(node_id, team_index)

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

    def _prune_expired_smokes(self) -> None:
        expired_node_ids = [
            node_id
            for node_id, expiration in self.smoke_expirations.items()
            if expiration <= self.tactical_round
        ]
        for node_id in expired_node_ids:
            known_team_indexes = set(self.smoke_known_team_indexes.pop(node_id, []))
            del self.smoke_expirations[node_id]
            for listener in self.players:
                tactical_listener = self._breach_player(listener)
                user = self.get_user(listener)
                if (
                    not tactical_listener
                    or not user
                    or tactical_listener.is_spectator
                    or tactical_listener.team_index not in known_team_indexes
                ):
                    continue
                user.speak_l(
                    "breachpoint-smoke-clears",
                    buffer="game",
                    location=self._node_name(user.locale, node_id),
                )

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

    def _weapon_can_reach(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile | None = None,
    ) -> bool:
        weapon = weapon or self._equipped_weapon(shooter)
        distance = self._node_distance(shooter.position_id, target.position_id)
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
        node = self._node(source.position_id)
        return bool(node and target.position_id in node.sightlines)

    def _team_can_see_node(self, team_index: int, node_id: str) -> bool:
        target_node = self._node(node_id)
        if not target_node:
            return False
        for observer in self._players_on_team(team_index, alive_only=True):
            if observer.position_id == node_id:
                return True
            if self._is_smoked(observer.position_id) or self._is_smoked(node_id):
                continue
            observer_node = self._node(observer.position_id)
            if observer_node and node_id in observer_node.sightlines:
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

    def _reaction_turn_error(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
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
        current = self.current_player
        if not current or current.id != tactical_player.id:
            return (
                "breachpoint-error-not-your-turn",
                {"player": current.name if current else ""},
            )
        if self._is_watched_entry_reaction():
            return "breachpoint-error-reaction-action-only"
        return None

    def _buy_turn_error(self, player: Player) -> str | tuple[str, dict] | None:
        tactical_player = self._breach_player(player)
        if self.status != "playing":
            return "action-not-playing"
        if not tactical_player or tactical_player.is_spectator:
            return "breachpoint-error-spectator-action"
        if self.phase != PHASE_BUY:
            return "breachpoint-error-buy-phase-ended"
        current = self.current_player
        if not current or current.id != tactical_player.id:
            return (
                "breachpoint-error-not-your-buy-turn",
                {"player": current.name if current else ""},
            )
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
    ) -> AttackOutcome:
        """Apply a deterministic projectile group through evasion and armor."""

        outcome = self._preview_attack(
            target,
            weapon,
            distance,
            damage_percent=damage_percent,
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
    ) -> AttackOutcome:
        """Calculate one attack without mutating authoritative player state."""

        distance = max(0, min(weapon.max_range, distance))
        rounds_on_target = weapon.hits_at_range(distance)
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
            base_damage * damaging_rounds + rounds_on_target - 1
        ) // rounds_on_target
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
            rounds_fired=weapon.rounds_per_attack,
            rounds_on_target=rounds_on_target,
            rounds_evaded=rounds_evaded,
            health_damage=health_damage,
            armor_absorbed=armor_absorbed,
            fully_evaded=fully_evaded,
        )

    @staticmethod
    def _attack_result(locale: str, outcome: AttackOutcome) -> str:
        key = (
            "breachpoint-shot-result-evaded"
            if outcome.fully_evaded
            else "breachpoint-shot-result-damage"
        )
        return Localization.get(
            locale,
            key,
            health_damage=outcome.health_damage,
            armor_absorbed=outcome.armor_absorbed,
            rounds_on_target=outcome.rounds_on_target,
            rounds_evaded=outcome.rounds_evaded,
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
        )

    def _get_reaction_pass_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "breachpoint-action-reaction-pass")

    def _is_buy_action_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._buy_turn_error(player) is None
            else Visibility.HIDDEN
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
        if tactical_player.primary_weapon_id:
            return "breachpoint-error-primary-owned"
        if tactical_player.cash < weapon.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": weapon.cost, "cash": tactical_player.cash},
            )
        return None

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
        if tactical_player.cash < utility.cost:
            return (
                "breachpoint-error-not-enough-cash",
                {"cost": utility.cost, "cash": tactical_player.cash},
            )
        return None

    def _get_buy_weapon_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        weapon = self._weapon_from_buy_action(action_id)
        return Localization.get(
            locale,
            "breachpoint-action-buy-weapon",
            weapon=self._weapon_name(locale, weapon),
            cost=weapon.cost if weapon else 0,
            cash=tactical_player.cash if tactical_player else 0,
        )

    def _get_buy_utility_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        utility = self._utility_from_buy_action(action_id)
        return Localization.get(
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
        return Localization.get(
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
        return Localization.get(
            locale,
            "breachpoint-action-buy-armor",
            armor=self._armor_name(locale),
            cost=self.economy.armor_cost,
            cash=tactical_player.cash if tactical_player else 0,
        )

    def _is_finish_buy_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        return self._buy_turn_error(player)

    def _get_finish_buy_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        return Localization.get(
            locale,
            "breachpoint-action-finish-buy",
            cash=tactical_player.cash if tactical_player else 0,
        )

    def _is_equip_weapon_hidden(self, player: Player) -> Visibility:
        tactical_player = self._breach_player(player)
        if self._turn_error(player) is not None or not tactical_player:
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self._primary_weapon(tactical_player)
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

    def _is_hold_angle_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        node_id = self._node_from_hold_action(action_id or "")
        if (
            self._turn_error(player) is None
            and tactical_player
            and self._can_hold_angle(tactical_player, node_id, weapon)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_hold_angle_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        error = self._turn_error(player)
        if error:
            return error
        tactical_player = self._breach_player(player)
        weapon = self._equipped_weapon(tactical_player) if tactical_player else None
        node_id = self._node_from_hold_action(action_id or "")
        if not tactical_player or not weapon or not weapon.requires_aim:
            return "breachpoint-error-aim-unavailable"
        if not self._can_hold_angle(tactical_player, node_id, weapon):
            return "breachpoint-error-illegal-angle"
        if (
            tactical_player.held_angle_origin_id == tactical_player.position_id
            and tactical_player.held_angle_node_id == node_id
        ):
            return "breachpoint-error-angle-held"
        if tactical_player.action_points < weapon.aim_action_point_cost:
            return (
                "breachpoint-error-not-enough-ap",
                {
                    "needed": weapon.aim_action_point_cost,
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
        return Localization.get(
            locale,
            "breachpoint-action-hold-angle",
            weapon=self._weapon_name(locale, weapon),
            location=self._node_name(locale, node_id),
            cost=weapon.aim_action_point_cost if weapon else 0,
        )

    def _is_throw_utility_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        details = self._throw_action_details(action_id or "")
        if not tactical_player or not details or self._turn_error(player) is not None:
            return Visibility.HIDDEN
        utility, node_id = details
        distance = self._node_distance(tactical_player.position_id, node_id)
        if (
            tactical_player.team_index in utility.allowed_sides
            and tactical_player.utility_counts.get(utility.id, 0) > 0
            and distance is not None
            and distance <= utility.throw_range
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
        if utility.effect == UTILITY_EFFECT_SMOKE and self._is_smoked(node_id):
            return "breachpoint-error-smoke-active"
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
        return Localization.get(
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

    def _get_end_turn_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        tactical_player = self._breach_player(player)
        guard = self._available_guard_points(tactical_player) if tactical_player else 0
        return Localization.get(
            locale,
            "breachpoint-action-end-turn",
            guard=min(self.rules.maximum_evasion_points, guard),
        )

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._turn_error(player) is None
            else Visibility.HIDDEN
        )

    def _is_move_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        node = self._node_from_action(action_id or "")
        current_node = (
            self._node(tactical_player.position_id) if tactical_player else None
        )
        if (
            self._turn_error(player) is None
            and node
            and current_node
            and node.id in current_node.adjacent
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
        return Localization.get(
            locale,
            (
                "breachpoint-action-disengage"
                if tactical_player and self._is_engaged(tactical_player)
                else "breachpoint-action-move"
            ),
            location=self._node_name(locale, node.id if node else ""),
            cost=(
                self._movement_action_point_cost(tactical_player)
                if tactical_player
                else self.rules.move_cost
            ),
        )

    def _is_shoot_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        tactical_player = self._breach_player(player)
        target = self._target_from_action(action_id or "")
        if (
            self._turn_error(player) is None
            and tactical_player
            and target
            and target.team_index != tactical_player.team_index
            and self._weapon_can_reach(tactical_player, target)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
        distance = self._node_distance(
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
        node = self._node(tactical_player.position_id) if tactical_player else None
        if (
            self._turn_error(player) is None
            and tactical_player
            and tactical_player.team_index == TEAM_TERRORISTS
            and tactical_player.id == self.bomb_carrier_id
            and self.bomb_state == BOMB_CARRIED
            and node
            and node.bomb_site
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
        if (
            self._turn_error(player) is None
            and tactical_player
            and tactical_player.team_index == TEAM_COUNTER_TERRORISTS
            and self.bomb_state == BOMB_PLANTED
            and tactical_player.position_id == self.bomb_location_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
        if (
            self._turn_error(player) is None
            and tactical_player
            and tactical_player.team_index == TEAM_TERRORISTS
            and self.bomb_state == BOMB_DROPPED
            and tactical_player.position_id == self.bomb_location_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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

    def _is_read_map_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_map_hidden(self, player: Player) -> Visibility:
        return self._information_action_visibility(player)

    def _is_read_teams_enabled(self, player: Player) -> str | None:
        return self._information_action_error()

    def _is_read_teams_hidden(self, player: Player) -> Visibility:
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

    def _action_reaction_shoot(self, player: Player, action_id: str) -> None:
        if self._is_reaction_shoot_enabled(player):
            return
        responder = self._breach_player(player)
        target = self._breach_player_by_id(self.reaction_window.target_player_id)
        weapon = self._equipped_weapon(responder) if responder else None
        if not responder or not target or not weapon:
            return
        round_finished = self._perform_attack(
            responder,
            target,
            weapon,
            damage_percent=100,
        )
        if round_finished:
            return
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
        buyer.primary_weapon_id = weapon.id
        buyer.equipped_weapon_id = weapon.id
        user.speak_l(
            "breachpoint-buy-weapon-complete",
            buffer="game",
            weapon=self._weapon_name(user.locale, weapon),
            cash=buyer.cash,
        )
        self.refresh_menus(buyer)
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
        buyer.utility_counts[utility.id] = buyer.utility_counts.get(utility.id, 0) + 1
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
        buyer.equipment_counts[equipment.id] = (
            buyer.equipment_counts.get(equipment.id, 0) + 1
        )
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
        buyer.armor = self.economy.maximum_armor
        user.speak_l(
            "breachpoint-buy-armor-complete",
            buffer="game",
            armor_name=self._armor_name(user.locale),
            armor=buyer.armor,
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
            self._start_combat_phase()
            return
        self.current_player = next_buyer
        self._start_buy_turn(next_buyer)
        self.refresh_menus()
        BotHelper.jolt_bot(next_buyer)

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
        tactical_player.equipped_weapon_id = weapon.id
        self._clear_held_angle(tactical_player)
        user.speak_l(
            "breachpoint-weapon-equipped",
            buffer="game",
            weapon=self._weapon_name(user.locale, weapon),
        )
        self.refresh_menus(tactical_player)
        BotHelper.jolt_bot(tactical_player)

    def _action_hold_angle(self, player: Player, action_id: str) -> None:
        if self._is_hold_angle_enabled(player, action_id=action_id):
            return
        sniper = self._breach_player(player)
        weapon = self._equipped_weapon(sniper) if sniper else None
        node_id = self._node_from_hold_action(action_id)
        if (
            not sniper
            or not weapon
            or not self._spend_action_points(sniper, weapon.aim_action_point_cost)
        ):
            return
        sniper.held_angle_origin_id = sniper.position_id
        sniper.held_angle_node_id = node_id
        for listener in self.players:
            tactical_listener = self._breach_player(listener)
            user = self.get_user(listener)
            if (
                not tactical_listener
                or not user
                or tactical_listener.is_spectator
                or tactical_listener.team_index != sniper.team_index
            ):
                continue
            user.speak_l(
                (
                    "breachpoint-hold-angle-you"
                    if listener.id == sniper.id
                    else "breachpoint-hold-angle-player"
                ),
                buffer="game",
                player=sniper.name,
                weapon=self._weapon_name(user.locale, weapon),
                location=self._node_name(user.locale, node_id),
            )
        sniper.action_points = 0
        self._end_activation(sniper)

    def _action_throw_utility(self, player: Player, action_id: str) -> None:
        if self._is_throw_utility_enabled(player, action_id=action_id):
            return
        thrower = self._breach_player(player)
        details = self._throw_action_details(action_id)
        if not thrower or not details:
            return
        utility, node_id = details
        if not self._spend_action_points(thrower, utility.action_point_cost):
            return
        self._clear_held_angle(thrower)
        thrower.utility_counts[utility.id] -= 1
        if not thrower.utility_counts[utility.id]:
            del thrower.utility_counts[utility.id]
        visible_team_indexes = self._utility_visible_team_indexes(thrower, node_id)
        self._announce_utility_throw(
            thrower,
            utility,
            node_id,
            visible_team_indexes,
        )
        if utility.effect == UTILITY_EFFECT_SMOKE:
            self.smoke_expirations[node_id] = (
                self.tactical_round + utility.duration_tactical_rounds
            )
            for team_index in visible_team_indexes:
                self._remember_smoke_for_team(node_id, team_index)
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
                if target_user:
                    target_user.speak_l(
                        "breachpoint-flashed",
                        buffer="game",
                        penalty=tactical_target.flash_penalty,
                    )
        self._finish_action(thrower)

    def _action_move(self, player: Player, action_id: str) -> None:
        if self._is_move_enabled(player, action_id=action_id):
            return
        tactical_player = self._breach_player(player)
        destination = self._node_from_action(action_id)
        if not tactical_player or not destination:
            return
        movement_cost = self._movement_action_point_cost(tactical_player)
        enemy_visibility_before = {
            team_index: self._team_can_see_player(team_index, tactical_player)
            for team_index in TEAM_INDEXES
            if team_index != tactical_player.team_index
        }
        friendly_contact_visibility_before = {
            enemy.id: (
                self._can_see(tactical_player, enemy),
                self._team_can_see_player(tactical_player.team_index, enemy),
            )
            for enemy in self._players_on_team(
                next(
                    team_index
                    for team_index in TEAM_INDEXES
                    if team_index != tactical_player.team_index
                ),
                alive_only=True,
            )
        }
        if not self._spend_action_points(tactical_player, movement_cost):
            return
        self._clear_held_angle(tactical_player)
        tactical_player.position_id = destination.id
        self._reset_stationary_evasion(tactical_player)
        self._remember_observable_smokes_for_team(tactical_player.team_index)
        self._announce_movement(
            tactical_player,
            destination.id,
            enemy_visibility_before,
        )
        self._announce_new_movement_contacts(
            tactical_player,
            friendly_contact_visibility_before,
        )
        if self._open_watched_entry_reaction(tactical_player, destination.id):
            return
        self._finish_action(tactical_player)

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
        round_finished = self._perform_attack(
            shooter,
            target,
            weapon,
            damage_percent=damage_percent,
        )
        if round_finished:
            return
        self._finish_action(shooter)

    def _perform_attack(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        *,
        damage_percent: int,
    ) -> bool:
        """Resolve one normal or reaction attack and all shared consequences."""

        self._clear_held_angle(shooter)
        distance = self._node_distance(shooter.position_id, target.position_id)
        if distance is None:
            return False
        outcome = self._resolve_attack(
            target,
            weapon,
            distance,
            damage_percent=damage_percent,
        )
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
        if target.eliminated:
            credited = self._add_cash(shooter, weapon.kill_reward)
            self._announce_elimination(shooter, target, weapon)
            shooter_user = self.get_user(shooter)
            if shooter_user and credited:
                shooter_user.speak_l(
                    "breachpoint-kill-reward",
                    buffer="game",
                    amount=credited,
                    cash=shooter.cash,
                )
            self._drop_bomb_from_eliminated_carrier(target)
            if self._check_elimination_victory():
                return True
        return False

    def _action_plant(self, player: Player, action_id: str) -> None:
        if self._is_plant_enabled(player):
            return
        terrorist = self._breach_player(player)
        if not terrorist or not self._spend_action_points(
            terrorist, self.rules.plant_cost
        ):
            return
        self._clear_held_angle(terrorist)
        self.bomb_state = BOMB_PLANTING
        self.planting_player_id = terrorist.id
        self.planting_location_id = terrorist.position_id
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
        self._clear_held_angle(counter_terrorist)
        self.defusing_player_id = counter_terrorist.id
        self.defusing_location_id = self.bomb_location_id
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
        self._clear_held_angle(terrorist)
        self.bomb_state = BOMB_CARRIED
        self.bomb_carrier_id = terrorist.id
        self.bomb_location_id = ""
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
        self.broadcast_personal_l(
            tactical_player,
            "breachpoint-end-turn-you",
            "breachpoint-end-turn-player",
            buffer="game",
            guard=guard,
        )
        tactical_player.action_points = 0
        self._end_activation(tactical_player)

    def _finish_action(self, player: BreachPointPlayer) -> None:
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
            objective_response = bool(
                self.reaction_window.is_open
                and self.reaction_window.kind in {REACTION_PLANT, REACTION_DEFUSE}
                and self.reaction_window.responding_player_id == tactical_player.id
            )
            if objective_response:
                key = (
                    "breachpoint-response-turn-you"
                    if listener.id == tactical_player.id
                    else "breachpoint-response-turn-player"
                )
            else:
                key = (
                    "breachpoint-turn-you"
                    if listener.id == tactical_player.id
                    else "breachpoint-turn-player"
                )
            user.speak_l(
                key,
                buffer="game",
                player=tactical_player.name,
                team=self._team_name(user.locale, tactical_player.team_index),
                location=(
                    self._node_name(user.locale, tactical_player.position_id)
                    if self._viewer_can_see_player(listener, tactical_player)
                    else Localization.get(user.locale, "breachpoint-location-concealed")
                ),
                ap=tactical_player.action_points,
                round=self.round,
                phase=self._round_phase_label(user.locale),
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
            distance = self._node_distance(watcher.position_id, destination_id)
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
                    self.broadcast_l(
                        "breachpoint-bomb-detonates",
                        buffer="game",
                        location=lambda locale: self._node_name(
                            locale, self.bomb_location_id
                        ),
                    )
                    self._finish_combat_round(TEAM_TERRORISTS, WIN_DETONATED)
                    return True
                self.broadcast_l(
                    "breachpoint-bomb-countdown",
                    buffer="game",
                    rounds=self.bomb_fuse_remaining,
                )
        elif self.tactical_round >= self.rules.preplant_tactical_round_limit:
            self._finish_combat_round(TEAM_COUNTER_TERRORISTS, WIN_TIME)
            return True
        return False

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
            key = (
                "breachpoint-match-start-carrier"
                if tactical_player.id == self.bomb_carrier_id
                else "breachpoint-match-start-player"
            )
            user.speak_l(
                key,
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
        self.broadcast_l(
            "breachpoint-combat-round-start",
            buffer="game",
            round=self.round,
            team_one=lambda locale: self._squad_name(locale, TEAM_TERRORISTS),
            team_one_score=self._squad_score(TEAM_TERRORISTS),
            team_two=lambda locale: self._squad_name(locale, TEAM_COUNTER_TERRORISTS),
            team_two_score=self._squad_score(TEAM_COUNTER_TERRORISTS),
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
        self._prune_expired_smokes()
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
        self.bomb_fuse_remaining = self.rules.bomb_fuse_tactical_rounds
        self.bomb_planted_tactical_round = self.tactical_round
        self.planting_player_id = ""
        self.planting_location_id = ""
        reward = self._add_cash(planter, self.economy.planter_reward)
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
                "health": target.health,
                "armor": target.armor,
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
        weapon: WeaponProfile,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == shooter.id:
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
                weapon=self._weapon_name(user.locale, weapon),
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

    def _check_elimination_victory(self) -> bool:
        if not self._players_on_team(TEAM_COUNTER_TERRORISTS, alive_only=True):
            self._finish_combat_round(TEAM_TERRORISTS, WIN_ELIMINATION)
            return True
        if self.bomb_state != BOMB_PLANTED and not self._players_on_team(
            TEAM_TERRORISTS, alive_only=True
        ):
            self._finish_combat_round(TEAM_COUNTER_TERRORISTS, WIN_ELIMINATION)
            return True
        return False

    def _finish_combat_round(self, winning_side_index: int, reason: str) -> None:
        if self.status != "playing":
            return
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
                self._finish_match(winning_squad_index, MATCH_OVERTIME)
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
            self._start_next_combat_round()
            return

        if winning_team.total_score >= self.match_format.rounds_to_win:
            self._finish_match(winning_squad_index, MATCH_REGULATION)
            return
        if self.round >= self.match_format.regulation_rounds:
            if self.options.overtime_mode == OVERTIME_DRAW:
                self._finish_match(-1, MATCH_DRAW)
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
        self._start_next_combat_round()

    def _start_next_combat_round(self) -> None:
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

    def _finish_match(self, squad_index: int, reason: str) -> None:
        if self.status != "playing":
            return
        self.reaction_window = ReactionWindow()
        self.winning_team_index = squad_index
        self.win_reason = reason
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
            health=tactical_player.health,
            max_health=self.rules.max_health,
            ap=tactical_player.action_points,
            armor=tactical_player.armor,
            weapon=self._weapon_name(
                user.locale, self._equipped_weapon(tactical_player)
            ),
            utility=self._utility_summary(user.locale, tactical_player),
            equipment=self._equipment_summary(user.locale, tactical_player),
            cash=tactical_player.cash,
            guard=tactical_player.guard_points,
            angle=self._held_angle_status(user.locale, tactical_player),
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
        for node in self.tactical_map.nodes:
            smoke_key = "breachpoint-map-smoke-unconfirmed"
            if tactical_viewer and not tactical_viewer.is_spectator:
                team_index = tactical_viewer.team_index
                if self._is_smoked(node.id) and self._team_knows_smoke(
                    team_index, node.id
                ):
                    smoke_key = "breachpoint-map-smoke-active"
                elif self._team_can_see_node(team_index, node.id):
                    smoke_key = "breachpoint-map-smoke-clear"
            occupants = [
                tactical_player
                for tactical_player in self.get_active_players()
                if isinstance(tactical_player, BreachPointPlayer)
                and tactical_player.position_id == node.id
                and self._viewer_knows_player_location(player, tactical_player)
            ]
            occupant_text = self._format_node_occupants(user.locale, occupants)
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
                                self._node_name(user.locale, visible_id)
                                for visible_id in node.sightlines
                            ],
                        ),
                        effect=Localization.get(
                            user.locale,
                            smoke_key,
                        ),
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

    def _action_read_teams(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "breachpoint_teams",
            self._build_team_status,
        )

    def _build_team_status(self, player: Player, user: User) -> list[MenuItem]:
        items: list[MenuItem] = []
        tactical_viewer = self._breach_player(player)
        for squad_index in TEAM_INDEXES:
            side_index = self._side_for_squad(squad_index)
            team_players = [
                tactical_player
                for tactical_player in self.get_active_players()
                if isinstance(tactical_player, BreachPointPlayer)
                and tactical_player.squad_index == squad_index
            ]
            alive = sum(not team_player.eliminated for team_player in team_players)
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "breachpoint-team-header",
                        squad=self._squad_name(user.locale, squad_index),
                        team=self._team_name(user.locale, side_index),
                        score=self._squad_score(squad_index),
                        alive=alive,
                        total=len(team_players),
                    ),
                    id=f"breachpoint_squad_{squad_index}",
                )
            )
            for team_player in team_players:
                can_see = bool(
                    team_player.eliminated
                    or (
                        tactical_viewer
                        and not tactical_viewer.is_spectator
                        and (
                            tactical_viewer.squad_index == team_player.squad_index
                            or self._viewer_can_see_player(player, team_player)
                        )
                    )
                )
                if not can_see:
                    items.append(
                        MenuItem(
                            text=Localization.get(
                                user.locale,
                                "breachpoint-team-player-concealed",
                                player=team_player.name,
                            ),
                            id=f"breachpoint_team_player_{team_player.id}",
                        )
                    )
                    continue
                items.append(
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "breachpoint-team-player-line",
                            player=team_player.name,
                            location=self._node_name(
                                user.locale, team_player.position_id
                            ),
                            health=team_player.health,
                            guard=team_player.guard_points,
                            state=Localization.get(
                                user.locale,
                                (
                                    "breachpoint-player-eliminated"
                                    if team_player.eliminated
                                    else "breachpoint-player-active"
                                ),
                            ),
                        ),
                        id=f"breachpoint_team_player_{team_player.id}",
                    )
                )
        return items

    def _action_read_bomb(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(self._bomb_status_line(player, user.locale), buffer="game")

    def _bomb_status_line(self, viewer: Player, locale: str) -> str:
        if self.bomb_state == BOMB_PLANTED:
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
        if not tactical_viewer or tactical_viewer.is_spectator:
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
        if user:
            for line in self._score_status_lines(user.locale):
                user.speak(line, buffer="game")

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
        for squad_index in TEAM_INDEXES:
            lines.append(
                Localization.get(
                    locale,
                    "breachpoint-score-line",
                    squad=self._squad_name(locale, squad_index),
                    score=self._squad_score(squad_index),
                    side=self._team_name(locale, self._side_for_squad(squad_index)),
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
