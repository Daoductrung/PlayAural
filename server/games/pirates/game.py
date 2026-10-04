"""
Pirates of the Lost Seas - Main Game Class.

A complex RPG adventure with sailing, combat, and leveling.
Players sail across four oceans, collecting gems and battling other pirates.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, FloatOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem

from .player import PiratesPlayer
from . import gems
from . import combat
from . import skills
from . import bot as bot_ai

# Ocean names for random selection
OCEAN_NAMES = [
    "pirates-ocean-rory",
    "pirates-ocean-dev",
    "pirates-ocean-par",
    "pirates-ocean-pal",
    "pirates-ocean-sil",
    "pirates-ocean-kai",
    "pirates-ocean-gam",
    "pirates-ocean-ser",
    "pirates-ocean-bat",
    "pirates-ocean-cod",
]

MAP_SIZE = 40
OCEAN_SIZE = 10
TOTAL_GEMS = 18
VALID_STEALING_MODES = {"with_roll_bonus", "no_roll_bonus", "disabled"}


@dataclass
class PiratesOptions(GameOptions):
    """Game options for Pirates of the Lost Seas."""

    combat_xp_multiplier: float = option_field(
        FloatOption(
            default=1.0,
            min_val=0.1,
            max_val=3.0,
            decimal_places=2,
            value_key="combat_multiplier",
            label="pirates-set-combat-xp-multiplier",
            prompt="pirates-enter-combat-xp-multiplier",
            change_msg="pirates-option-changed-combat-xp",
            description="pirates-desc-combat-xp-multiplier",
        )
    )

    find_gem_xp_multiplier: float = option_field(
        FloatOption(
            default=1.0,
            min_val=0.1,
            max_val=3.0,
            decimal_places=2,
            value_key="find_gem_multiplier",
            label="pirates-set-find-gem-xp-multiplier",
            prompt="pirates-enter-find-gem-xp-multiplier",
            change_msg="pirates-option-changed-find-gem-xp",
            description="pirates-desc-find-gem-xp-multiplier",
        )
    )

    gem_stealing: str = option_field(
        MenuOption(
            default="with_roll_bonus",
            value_key="mode",
            choices=["with_roll_bonus", "no_roll_bonus", "disabled"],
            choice_labels={
                "with_roll_bonus": "pirates-stealing-with-bonus",
                "no_roll_bonus": "pirates-stealing-no-bonus",
                "disabled": "pirates-stealing-disabled",
            },
            label="pirates-set-gem-stealing",
            prompt="pirates-select-gem-stealing",
            change_msg="pirates-option-changed-stealing",
            description="pirates-desc-gem-stealing",
        )
    )


@dataclass
@register_game
class PiratesGame(Game):
    """
    Pirates of the Lost Seas - A complex RPG adventure.

    Features:
    - 40-tile map across 4 oceans
    - 18 gems to collect
    - Skill system that unlocks as players level up
    - Combat with cannonballs, buffs, and gem stealing
    - Golden Moon event every 3rd round (3x XP)
    """

    relevant_preferences = ["brief_announcements"]

    players: list[PiratesPlayer] = field(default_factory=list)
    options: PiratesOptions = field(default_factory=PiratesOptions)

    # Game state
    selected_oceans: list[str] = field(default_factory=list)
    charted_tiles: dict[int, bool] = field(default_factory=dict)
    gem_positions: dict[int, int] = field(default_factory=dict)
    gems_collected: int = 0
    total_gems: int = TOTAL_GEMS
    golden_moon_active: bool = False
    winner_ids: list[str] = field(default_factory=list)
    winner_names: list[str] = field(default_factory=list)
    pending_boarding_attacker_id: str = ""
    pending_boarding_defender_id: str = ""
    pending_boarding_attack_bonus: int = 0
    pending_boarding_defense_bonus: int = 0
    pending_portal_player_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Pirates of the Lost Seas"

    @classmethod
    def get_type(cls) -> str:
        return "pirates"

    @classmethod
    def get_category(cls) -> str:
        return "arcade"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def __post_init__(self):
        """Initialize non-serialized state."""
        super().__post_init__()

    def rebuild_runtime_state(self) -> None:
        """Rebuild runtime state after deserialization."""
        super().rebuild_runtime_state()
        if self.gem_positions:
            self.gem_positions = {int(k): v for k, v in self.gem_positions.items()}
        if self.charted_tiles:
            self.charted_tiles = {int(k): v for k, v in self.charted_tiles.items()}
        # Cannonball was once duplicated as a skill but never had mutable state.
        for player in self.players:
            player.skill_cooldowns.pop("cannonball", None)
            player.skill_active.pop("cannonball", None)
            player.skill_uses.pop("cannonball", None)
        self._prune_pending_choices()

    def before_menu_build(self, player: Player) -> None:
        """Clear impossible pending choices before action menus are resolved."""
        self._prune_pending_choices()

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> PiratesPlayer:
        """Create a new Pirates player."""
        # Skills are initialized in PiratesPlayer.__post_init__
        return PiratesPlayer(id=player_id, name=name, is_bot=is_bot)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: PiratesPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast an actor event with per-listener perspective and verbosity."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == actor.id
            key = personal_key if is_actor else others_key
            if self._wants_brief(user):
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key
            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _clear_pending_boarding(self) -> None:
        self.pending_boarding_attacker_id = ""
        self.pending_boarding_defender_id = ""
        self.pending_boarding_attack_bonus = 0
        self.pending_boarding_defense_bonus = 0

    def _has_pending_boarding(self, player: Player | None = None) -> bool:
        if not self.pending_boarding_attacker_id:
            return False
        return player is None or player.id == self.pending_boarding_attacker_id

    def _clear_pending_portal(self) -> None:
        self.pending_portal_player_id = ""

    def _has_pending_portal(self, player: Player | None = None) -> bool:
        if not self.pending_portal_player_id:
            return False
        return player is None or player.id == self.pending_portal_player_id

    def _has_pending_choice(self, player: Player | None = None) -> bool:
        return self._has_pending_boarding(player) or self._has_pending_portal(player)

    def _is_active_pirate(self, player: Player | None) -> bool:
        return (
            isinstance(player, PiratesPlayer)
            and player in self.get_active_players()
        )

    def _prune_pending_choices(self) -> None:
        """Drop serialized pending choices that can no longer be resolved."""
        if self.pending_boarding_attacker_id:
            attacker, defender = self._pending_boarding_players()
            if (
                not self._is_active_pirate(attacker)
                or not self._is_active_pirate(defender)
            ):
                self._clear_pending_boarding()

        if self.pending_portal_player_id:
            player = self.get_player_by_id(self.pending_portal_player_id)
            if not self._is_active_pirate(player):
                self._clear_pending_portal()

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: Player) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Movement actions
        action_set.add(
            Action(
                id="move_left",
                label=Localization.get(locale, "pirates-move-left"),
                handler="_action_move_left",
                is_enabled="_is_move_enabled",
                is_hidden="_is_move_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_right",
                label=Localization.get(locale, "pirates-move-right"),
                handler="_action_move_right",
                is_enabled="_is_move_enabled",
                is_hidden="_is_move_hidden",
                show_in_actions_menu=False,
            )
        )

        # Level 15+ movements
        action_set.add(
            Action(
                id="move_2_left",
                label=Localization.get(locale, "pirates-move-2-left"),
                handler="_action_move_2_left",
                is_enabled="_is_move_2_enabled",
                is_hidden="_is_move_2_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_2_right",
                label=Localization.get(locale, "pirates-move-2-right"),
                handler="_action_move_2_right",
                is_enabled="_is_move_2_enabled",
                is_hidden="_is_move_2_hidden",
                show_in_actions_menu=False,
            )
        )

        # Level 150+ movements
        action_set.add(
            Action(
                id="move_3_left",
                label=Localization.get(locale, "pirates-move-3-left"),
                handler="_action_move_3_left",
                is_enabled="_is_move_3_enabled",
                is_hidden="_is_move_3_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_3_right",
                label=Localization.get(locale, "pirates-move-3-right"),
                handler="_action_move_3_right",
                is_enabled="_is_move_3_enabled",
                is_hidden="_is_move_3_hidden",
                show_in_actions_menu=False,
            )
        )

        action_set.add(
            Action(
                id="cannonball",
                label=Localization.get(locale, "pirates-cannonball"),
                handler="_action_cannonball",
                is_enabled="_is_cannonball_enabled",
                is_hidden="_is_cannonball_hidden",
                show_in_actions_menu=False,
                input_request=MenuInput(
                    options="_get_cannonball_target_options",
                    prompt="pirates-select-cannon-target",
                    bot_select="_bot_select_cannonball_target",
                    pre_input_check="_precheck_cannonball_input",
                    option_label="_get_cannonball_target_label",
                ),
            )
        )

        # Skill menu
        action_set.add(
            Action(
                id="use_skill",
                label=Localization.get(locale, "pirates-use-skill"),
                handler="_action_use_skill",
                is_enabled="_is_skill_enabled",
                is_hidden="_is_skill_hidden",
                show_in_actions_menu=False,
                input_request=MenuInput(
                    options="_get_skill_options",
                    prompt="pirates-select-skill",
                    bot_select="_bot_select_skill",
                    option_label="_get_skill_option_label",
                ),
            )
        )
        action_set.add(
            Action(
                id="resolve_boarding",
                label=Localization.get(locale, "pirates-resolve-boarding"),
                handler="_action_resolve_boarding",
                is_enabled="_is_boarding_enabled",
                is_hidden="_is_boarding_hidden",
                show_in_actions_menu=False,
                input_request=MenuInput(
                    options="_get_boarding_options",
                    prompt="pirates-select-boarding-action",
                    bot_select="_bot_select_boarding_option",
                    pre_input_check="_precheck_boarding_input",
                    option_label="_get_boarding_option_label",
                ),
            )
        )
        action_set.add(
            Action(
                id="resolve_portal",
                label=Localization.get(locale, "pirates-resolve-portal"),
                handler="_action_resolve_portal",
                is_enabled="_is_portal_choice_enabled",
                is_hidden="_is_portal_choice_hidden",
                show_in_actions_menu=False,
                input_request=MenuInput(
                    options="_get_portal_options",
                    prompt="pirates-select-portal-ocean",
                    bot_select="_bot_select_portal_ocean",
                    pre_input_check="_precheck_portal_choice_input",
                    option_label="_get_portal_option_label",
                    initial_selection="_get_portal_initial_selection",
                ),
            )
        )

        return action_set

    # Touch clients need desktop-keybind utility actions as visible buttons.
    touch_standard_action_order = [
        "check_position",
        "check_moon",
        "check_status",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Remove default score actions to prevent "No scores available yet"
        if action_set.get_action("check_scores"):
            action_set.remove("check_scores")
        if action_set.get_action("check_scores_detailed"):
            action_set.remove("check_scores_detailed")

        action_set.add(
            Action(
                id="check_moon",
                label=Localization.get(locale, "pirates-check-moon"),
                handler="_action_check_moon",
                is_enabled="_is_moon_check_enabled",
                is_hidden="_is_moon_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_position",
                label=Localization.get(locale, "pirates-check-position"),
                handler="_action_check_position",
                is_enabled="_is_status_enabled",
                is_hidden="_is_check_position_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "pirates-check-status"),
                handler="_action_check_status",
                is_enabled="_is_status_enabled",
                is_hidden="_is_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_status_detailed",
                label=Localization.get(locale, "pirates-check-status-detailed"),
                handler="_action_check_status_detailed",
                is_enabled="_is_status_enabled",
                is_hidden="_is_detailed_status_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set, self.touch_standard_action_order
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        self.define_keybind(
            "p",
            "Check position",
            ["check_position"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "m",
            "Check moon brightness",
            ["check_moon"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        self.define_keybind(
            "s",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        self.define_keybind(
            "shift+s",
            "Detailed status",
            ["check_status_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _turn_action_disabled_reason(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self._has_pending_boarding(player):
            return "pirates-must-resolve-boarding"
        if self._has_pending_portal(player):
            return "pirates-must-resolve-portal"
        return None

    def _is_move_enabled(self, player: Player) -> str | None:
        return self._turn_action_disabled_reason(player)

    def _is_move_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_2_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        reason = self._turn_action_disabled_reason(player)
        if reason:
            return reason
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return (
                "pirates-requires-level",
                {"action": "move_2", "current": p.level if p else 0, "required": 15},
            )
        return None

    def _is_move_2_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_3_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        reason = self._turn_action_disabled_reason(player)
        if reason:
            return reason
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return (
                "pirates-requires-level",
                {
                    "action": "move_3",
                    "current": p.level if p else 0,
                    "required": 150,
                },
            )
        return None

    def _is_move_3_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_cannonball_enabled(self, player: Player) -> str | None:
        return self._turn_action_disabled_reason(player)

    def _is_cannonball_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_skill_enabled(self, player: Player) -> str | None:
        return self._turn_action_disabled_reason(player)

    def _is_skill_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_skill_options(self, player: Player) -> list[str]:
        """Return stable skill IDs for unlocked activated skills."""
        if not isinstance(player, PiratesPlayer):
            return []
        return [
            skill.skill_id
            for skill in skills.get_available_skills(player)
        ]

    def _get_skill_option_label(self, player: Player, skill_id: str) -> str:
        if not isinstance(player, PiratesPlayer):
            return ""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        skill = skills.SKILLS_BY_ID.get(skill_id)
        if not skill:
            return Localization.get(locale, "pirates-unknown-skill")
        return skill.get_menu_label(player, locale)

    def _bot_select_skill(
        self, player: Player, skill_options: list[str]
    ) -> str:
        if not isinstance(player, PiratesPlayer):
            return skill_options[0]
        return bot_ai.bot_select_skill_choice(self, player, skill_options)

    def _get_cannonball_target_options(self, player: Player) -> list[str]:
        if not isinstance(player, PiratesPlayer):
            return []
        return [target.id for target in self.get_targets_in_range(player)]

    def _get_cannonball_target_label(self, player: Player, target_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target = self.get_player_by_id(target_id)
        if not isinstance(player, PiratesPlayer) or not isinstance(target, PiratesPlayer):
            return Localization.get(locale, "pirates-target-unavailable")
        return Localization.get(
            locale,
            "pirates-target-option",
            player=target.name,
            distance=combat.get_distance(player, target),
            score=target.score,
            gems=len(target.gems),
        )

    def _precheck_cannonball_input(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        reason = self._is_cannonball_enabled(player)
        if reason:
            return reason
        if not isinstance(player, PiratesPlayer):
            return "action-disabled"
        if not self.get_targets_in_range(player):
            return (
                "pirates-no-targets",
                {"range": skills.get_attack_range(player)},
            )
        return None

    def _bot_select_cannonball_target(
        self, player: Player, target_ids: list[str]
    ) -> str:
        if not isinstance(player, PiratesPlayer):
            return target_ids[0]
        targets = [
            target
            for target_id in target_ids
            if isinstance(
                (target := self.get_player_by_id(target_id)), PiratesPlayer
            )
        ]
        target = bot_ai.bot_select_target(self, player, targets)
        return target.id if target else target_ids[0]

    def _is_boarding_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.id != self.pending_boarding_attacker_id:
            return "pirates-no-pending-boarding"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_boarding_hidden(self, player: Player) -> Visibility:
        if (
            self.status == "playing"
            and not player.is_spectator
            and player.id == self.pending_boarding_attacker_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _pending_boarding_players(
        self,
    ) -> tuple[PiratesPlayer | None, PiratesPlayer | None]:
        attacker = self.get_player_by_id(self.pending_boarding_attacker_id)
        defender = self.get_player_by_id(self.pending_boarding_defender_id)
        return (
            attacker if isinstance(attacker, PiratesPlayer) else None,
            defender if isinstance(defender, PiratesPlayer) else None,
        )

    def _get_boarding_options(self, player: Player) -> list[str]:
        attacker, defender = self._pending_boarding_players()
        if attacker is not player or defender is None:
            return []
        options = ["push_left", "push_right"]
        if self.options.gem_stealing != "disabled" and defender.has_gems():
            options.insert(0, "steal")
        return options

    def _get_boarding_option_label(self, player: Player, option: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        key = {
            "steal": "pirates-boarding-steal",
            "push_left": "pirates-boarding-push-left",
            "push_right": "pirates-boarding-push-right",
        }.get(option, "pirates-boarding-option-unknown")
        return Localization.get(locale, key)

    def _bot_select_boarding_option(
        self, player: Player, options: list[str]
    ) -> str:
        attacker, defender = self._pending_boarding_players()
        if not isinstance(attacker, PiratesPlayer) or defender is None:
            return options[0]
        choice = bot_ai.bot_select_boarding_action(
            self, attacker, defender, "steal" in options
        )
        return "push_left" if choice == "left" else (
            "push_right" if choice == "right" else choice
        )

    def _precheck_boarding_input(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        reason = self._is_boarding_enabled(player)
        if reason:
            return reason
        attacker, defender = self._pending_boarding_players()
        if attacker is not player or defender is None:
            self._clear_pending_boarding()
            return "pirates-boarding-stale"
        return None

    def _is_portal_choice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.id != self.pending_portal_player_id:
            return "pirates-no-pending-portal"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_portal_choice_hidden(self, player: Player) -> Visibility:
        if (
            self.status == "playing"
            and not player.is_spectator
            and player.id == self.pending_portal_player_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _occupied_portal_oceans(self, player: PiratesPlayer) -> list[int]:
        current_ocean = (player.position - 1) // OCEAN_SIZE
        oceans: set[int] = set()
        for other in self.get_active_players():
            if other.id == player.id:
                continue
            other_ocean = (other.position - 1) // OCEAN_SIZE
            if other_ocean != current_ocean:
                oceans.add(other_ocean)
        return sorted(oceans)

    def _get_portal_options(self, player: Player) -> list[str]:
        if not isinstance(player, PiratesPlayer):
            return []
        if player.id != self.pending_portal_player_id:
            return []
        ocean_options = [str(ocean) for ocean in self._occupied_portal_oceans(player)]
        ocean_options.append("random")
        return ocean_options

    def _get_portal_option_label(self, player: Player, ocean_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if ocean_id == "random":
            return Localization.get(locale, "pirates-portal-option-random")
        if not isinstance(player, PiratesPlayer):
            return Localization.get(locale, "pirates-portal-option-unavailable")
        try:
            ocean = int(ocean_id)
        except ValueError:
            return Localization.get(locale, "pirates-portal-option-unavailable")
        if ocean not in self._occupied_portal_oceans(player):
            return Localization.get(locale, "pirates-portal-option-unavailable")
        start = ocean * OCEAN_SIZE + 1
        end = start + OCEAN_SIZE - 1
        ship_names = [
            other.name
            for other in self.get_active_players()
            if other.id != player.id and start <= other.position <= end
        ]
        gem_count = sum(
            gem_type != -1
            for position, gem_type in self.gem_positions.items()
            if start <= position <= end
        )
        ocean_key = (
            self.selected_oceans[ocean]
            if 0 <= ocean < len(self.selected_oceans)
            else "pirates-ocean-unknown"
        )
        return Localization.get(
            locale,
            "pirates-portal-option",
            ocean=Localization.get(locale, ocean_key),
            ships=Localization.format_list_and(locale, ship_names),
            gems=gem_count,
        )

    def _bot_select_portal_ocean(
        self, player: Player, ocean_ids: list[str]
    ) -> str:
        if not isinstance(player, PiratesPlayer):
            return ocean_ids[0]
        selectable_oceans = [
            ocean_id for ocean_id in ocean_ids if ocean_id != "random"
        ]
        if not selectable_oceans:
            return "random"
        options = [
            (int(ocean_id), self.selected_oceans[int(ocean_id)])
            for ocean_id in selectable_oceans
        ]
        selected = bot_ai.bot_select_portal_ocean(self, player, options)
        if selected == "random":
            return "random"
        return str(selected) if selected is not None else selectable_oceans[0]

    def _get_portal_initial_selection(
        self, player: Player, options: list[str]
    ) -> str | None:
        for option in options:
            if option != "random":
                return option
        return options[0] if options else None

    def _precheck_portal_choice_input(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        reason = self._is_portal_choice_enabled(player)
        if reason:
            return reason
        if not isinstance(player, PiratesPlayer):
            return "action-disabled"
        return None

    def _is_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_status_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_detailed_status_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_moon_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_moon_check_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        return (
            Visibility.VISIBLE
            if self.is_touch_client(user)
            else Visibility.HIDDEN
        )

    def _is_always_hidden(self, player: Player) -> Visibility:
        """Always return hidden - for keybind-only actions."""
        return Visibility.HIDDEN

    # Touch-specific visibility overrides.

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_position_hidden(self, player: "Player") -> Visibility:
        """Show the position check as a touch utility during active play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 0.1 <= self.options.combat_xp_multiplier <= 3.0:
            errors.append(
                (
                    "pirates-error-combat-xp-range",
                    {
                        "value": self.options.combat_xp_multiplier,
                        "min": 0.1,
                        "max": 3.0,
                    },
                )
            )
        if not 0.1 <= self.options.find_gem_xp_multiplier <= 3.0:
            errors.append(
                (
                    "pirates-error-gem-xp-range",
                    {
                        "value": self.options.find_gem_xp_multiplier,
                        "min": 0.1,
                        "max": 3.0,
                    },
                )
            )
        if self.options.gem_stealing not in VALID_STEALING_MODES:
            errors.append(
                (
                    "pirates-error-stealing-mode",
                    {"mode": self.options.gem_stealing},
                )
            )
        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Play music and ambience
        self.play_music("game_pirates/mus.ogg")
        self.play_ambience(
            "game_pirates/amloop.ogg",
            intro="game_pirates/am_intro.ogg",
            outro="game_pirates/am_outro.ogg",
        )

        self._clear_pending_boarding()
        self._clear_pending_portal()
        self.winner_ids = []
        self.winner_names = []
        self.golden_moon_active = False

        self._broadcast_global_l("pirates-welcome", "pirates-welcome-brief")

        # Select 4 random oceans
        available = list(OCEAN_NAMES)
        random.shuffle(available)
        self.selected_oceans = available[:4]

        for p in self.players:
            u = self.get_user(p)
            if u:
                oceans_str = Localization.format_list_and(
                    u.locale,
                    [Localization.get(u.locale, key) for key in self.selected_oceans],
                )
                u.speak_l("pirates-oceans", buffer="game", oceans=oceans_str)

        # Initialize charted tiles
        self.charted_tiles = {i: False for i in range(1, MAP_SIZE + 1)}

        # Place gems
        self.gem_positions = gems.place_gems(MAP_SIZE)
        self.total_gems = sum(
            gem_type != -1 for gem_type in self.gem_positions.values()
        )
        self.gems_collected = 0

        # Start ships on distinct empty tiles so no treasure is silently skipped.
        empty_positions = [
            position
            for position, gem_type in self.gem_positions.items()
            if gem_type == -1
        ]
        random.shuffle(empty_positions)
        for player, position in zip(
            self.get_active_players(), empty_positions, strict=False
        ):
            player.position = position
            player.score = 0
            player.gems = []
            player.leveling.level = 0
            player.leveling.xp = 0
            player.skill_cooldowns.clear()
            player.skill_active.clear()
            player.skill_uses.clear()
            player.skill_activated_this_turn = False
            self.charted_tiles[position] = True

        self._broadcast_global_l(
            "pirates-gems-placed",
            "pirates-gems-placed-brief",
            total=self.total_gems,
        )

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Rebuild menus and start first turn
        self.refresh_menus()
        self._start_round()

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(10, 30))

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Check for Golden Moon (every 3rd round)
        self.golden_moon_active = (self.round % 3 == 0)
        if self.golden_moon_active:
            self.play_sound("game_pirates/goldenmoon.ogg")
            self._broadcast_global_l(
                "pirates-golden-moon",
                "pirates-golden-moon-brief",
                round=self.round,
            )

        # Announce first turn
        self._announce_turn()

    def _announce_turn(self) -> None:
        """Announce whose turn it is."""
        player = self.current_player
        if not player or not isinstance(player, PiratesPlayer):
            return

        # Update skill timers
        skills.on_turn_start(self, player)
        player.skill_activated_this_turn = False

        # Play turn sound
        if not player.is_bot:
            user = self.get_user(player)
            if user and user.preferences.play_turn_sound:
                user.play_sound("turn.ogg")

        ocean_name_by_locale = {}
        ocean_key = self._ocean_key_for_position(player.position)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            ocean_name = ocean_name_by_locale.setdefault(
                user.locale, Localization.get(user.locale, ocean_key)
            )
            is_actor = listener.id == player.id
            key = "pirates-turn-you" if is_actor else "pirates-turn"
            if self._wants_brief(user):
                key += "-brief"
            user.speak_l(
                key,
                buffer="game",
                player=player.name,
                position=player.position,
                ocean=ocean_name,
                round=self.round,
            )

    def on_tick(self) -> None:
        """Called every game tick."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if self.status != "playing":
            return

        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Determine what action a bot should take."""
        if not isinstance(player, PiratesPlayer):
            return None
        return bot_ai.bot_think(self, player)

    def end_turn(self) -> None:
        """End the current player's turn."""
        current = self.current_player
        if not current or not isinstance(current, PiratesPlayer):
            return
        if self._has_pending_choice(current):
            return

        # Check for gem at current position
        self._check_gem_collection(current)

        # Check for win condition
        if self.total_gems <= 0:
            self._end_game()
            return

        # Advance to next player
        self.advance_turn(announce=False)

        # Check if we've completed a round
        if self.turn_index == 0:
            self._start_round()
        else:
            self._announce_turn()

        self.refresh_menus()

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(80, 120))

    def _check_gem_collection(self, player: PiratesPlayer) -> None:
        """Check if player is on a gem and collect it."""
        gem_type = self.gem_positions.get(player.position, -1)
        if gem_type == -1:
            return

        gem_value = gems.get_gem_value(gem_type)
        gem_name = gems.get_gem_name(gem_type)

        # Play collection sound
        sound_num = random.randint(1, 3)
        self.play_sound(f"game_pirates/grabgem{sound_num}.ogg", volume=70)

        # Add gem to player
        player.add_gem(gem_type, gem_value)

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == player.id
            if is_actor:
                key = (
                    "pirates-gem-found-you-brief"
                    if self._wants_brief(user)
                    else "pirates-gem-found-you"
                )
            else:
                key = (
                    "pirates-gem-found-brief"
                    if self._wants_brief(user)
                    else "pirates-gem-found"
                )
            user.speak_l(
                key,
                buffer="game",
                player=player.name,
                gem=Localization.get(user.locale, gem_name),
                value=gem_value,
                score=player.score,
                remaining=self.total_gems - 1,
            )

        # Give XP for finding gem
        xp_gain = random.randint(150, 300)
        moon_mult = 3.0 if self.golden_moon_active else 1.0
        player.leveling.give_xp(
            self,
            player.name,
            xp_gain,
            moon_mult,
            self.options.find_gem_xp_multiplier,
            reason="gem",
        )

        # Mark gem as collected
        self.gem_positions[player.position] = -1
        self.total_gems -= 1
        self.gems_collected += 1
        self.charted_tiles[player.position] = True

    def _end_game(self) -> None:
        """End the game and determine winner."""
        if self.status != "playing":
            return
        self._clear_pending_boarding()
        self._clear_pending_portal()
        self._broadcast_global_l(
            "pirates-all-gems-collected",
            "pirates-all-gems-collected-brief",
        )

        # Find winner by highest score
        active_players = self.get_active_players()
        if not active_players:
            return

        highest_score = max(p.score for p in active_players)
        winners = [p for p in active_players if p.score == highest_score]

        self.play_sound("game_pig/win.ogg", volume=80)
        self.winner_ids = [winner.id for winner in winners]
        self.winner_names = [winner.name for winner in winners]
        winner_ids = set(self.winner_ids)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            listener_won = listener.id in winner_ids
            if len(winners) == 1:
                key = (
                    "pirates-you-win"
                    if listener_won
                    else "pirates-winner"
                )
                if self._wants_brief(user):
                    key += "-brief"
                user.speak_l(
                    key,
                    buffer="game",
                    player=winners[0].name,
                    score=highest_score,
                )
                continue

            if listener_won:
                other_names = [
                    winner.name
                    for winner in winners
                    if winner.id != listener.id
                ]
                key = (
                    "pirates-you-tie-brief"
                    if self._wants_brief(user)
                    else "pirates-you-tie"
                )
                names = Localization.format_list_and(user.locale, other_names)
            else:
                key = (
                    "pirates-players-tie-brief"
                    if self._wants_brief(user)
                    else "pirates-players-tie"
                )
                names = Localization.format_list_and(
                    user.locale, self.winner_names
                )
            user.speak_l(key, buffer="game", players=names, score=highest_score)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Pirates-specific data."""
        active_players = self.get_active_players()
        sorted_players = sorted(active_players, key=lambda p: p.score, reverse=True)

        # Build final scores and levels
        final_scores = {}
        final_levels = {}
        final_gems = {}
        for p in sorted_players:
            final_scores[p.name] = p.score
            final_levels[p.name] = p.level
            final_gems[p.name] = list(p.gems)

        winner_name = self.winner_names[0] if len(self.winner_names) == 1 else None
        winner_score = sorted_players[0].score if sorted_players else 0

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner_name,
                "winner_names": list(self.winner_names),
                "winner_ids": list(self.winner_ids),
                "winner_score": winner_score,
                "final_scores": final_scores,
                "final_levels": final_levels,
                "final_gems": final_gems,
                "rounds_played": self.round,
                "gems_collected": self.gems_collected,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Pirates game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        final_levels = result.custom_data.get("final_levels", {})

        rank = 0
        previous_score = None
        for index, (name, score) in enumerate(final_scores.items(), 1):
            if score != previous_score:
                rank = index
                previous_score = score
            level = final_levels.get(name, 0)
            points_str = Localization.get(locale, "game-points", count=score)
            line = Localization.get(
                locale,
                "pirates-end-score-line",
                rank=rank,
                player=name,
                points=points_str,
                level=level,
            )
            lines.append(line)

        return lines

    # ==========================================================================
    # Movement Actions
    # ==========================================================================

    def _ocean_key_for_position(self, position: int) -> str:
        ocean_index = max(0, position - 1) // OCEAN_SIZE
        if 0 <= ocean_index < len(self.selected_oceans):
            return self.selected_oceans[ocean_index]
        return "pirates-ocean-unknown"

    def _move_player(self, player: PiratesPlayer, amount: int) -> bool:
        """
        Move a player by the specified amount.

        Returns:
            True if move was successful, False if blocked by map edge
        """
        old_position = player.position

        if amount > 0:
            new_position = min(MAP_SIZE, player.position + amount)
        else:
            new_position = max(1, player.position + amount)

        if new_position == old_position:
            # Blocked by map edge
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-map-edge", buffer="game", position=old_position)
            return False

        player.position = new_position
        actual_amount = new_position - old_position

        # Play movement sound
        abs_amount = abs(actual_amount)
        if abs_amount == 1:
            sound_num = random.randint(1, 3)
            self.play_sound(f"game_pirates/move{sound_num}.ogg", volume=60)
        elif abs_amount == 2:
            sound_num = random.randint(1, 3)
            self.play_sound(f"game_pirates/boat{sound_num}.ogg", volume=60)
        elif abs_amount == 3:
            sound_num = random.randint(1, 2)
            self.play_sound(f"game_pirates/future{sound_num}.ogg", volume=60)

        direction_key = (
            "pirates-dir-right" if actual_amount > 0 else "pirates-dir-left"
        )
        ocean_key = self._ocean_key_for_position(player.position)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == player.id
            if is_actor:
                key = (
                    "pirates-move-you-brief"
                    if self._wants_brief(user)
                    else "pirates-move-you"
                )
            else:
                key = (
                    "pirates-move-brief"
                    if self._wants_brief(user)
                    else "pirates-move"
                )
            user.speak_l(
                key,
                buffer="game",
                player=player.name,
                tiles=abs_amount,
                direction=Localization.get(user.locale, direction_key),
                position=player.position,
                ocean=Localization.get(user.locale, ocean_key),
            )

        self.charted_tiles[player.position] = True
        return True

    def _action_move_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -1):
            self.end_turn()

    def _action_move_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 1):
            self.end_turn()

    def _action_move_2_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -2):
            self.end_turn()

    def _action_move_2_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 2):
            self.end_turn()

    def _action_move_3_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -3):
            self.end_turn()

    def _action_move_3_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 3):
            self.end_turn()

    def _action_cannonball(
        self, player: Player, target_id: str, action_id: str
    ) -> None:
        """Fire a cannonball at a target in range."""
        if not isinstance(player, PiratesPlayer):
            return
        if self.current_player != player:
            return

        result = self.handle_cannonball_attack(player, target_id)
        if result == "end_turn":
            self.end_turn()

    # ==========================================================================
    # Skill Actions
    # ==========================================================================

    def _action_use_skill(
        self, player: Player, skill_id: str, action_id: str
    ) -> None:
        """Handle skill menu selection."""
        if not isinstance(player, PiratesPlayer):
            return

        user = self.get_user(player)
        skill = skills.SKILLS_BY_ID.get(skill_id)
        if (
            not skill
            or not skill.is_unlocked(player)
        ):
            if user:
                user.speak_l(
                    "pirates-skill-selection-stale",
                    buffer="game",
                    skill=skill_id,
                )
            return

        can_use, reason = skill.can_perform(self, player)
        if can_use:
            result = skill.do_action(self, player)
            if result == "end_turn":
                self.end_turn()
        elif user and reason:
            user.speak_l("pirates-skill-error", buffer="game", message=reason)

    def _action_resolve_boarding(
        self, player: Player, choice: str, action_id: str
    ) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        attacker, defender = self._pending_boarding_players()
        if attacker is not player:
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-no-pending-boarding", buffer="game")
            return
        if defender is None:
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-boarding-stale", buffer="game")
            self._clear_pending_boarding()
            return

        valid_options = self._get_boarding_options(player)
        if choice not in valid_options:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "pirates-boarding-option-unavailable",
                    buffer="game",
                    action=self._get_boarding_option_label(player, choice),
                    defender=defender.name,
                )
            return

        attack_bonus = self.pending_boarding_attack_bonus
        defense_bonus = self.pending_boarding_defense_bonus
        self._clear_pending_boarding()
        if choice == "steal":
            use_bonuses = self.options.gem_stealing == "with_roll_bonus"
            combat.attempt_gem_steal(
                self,
                attacker,
                defender,
                attack_bonus if use_bonuses else 0,
                defense_bonus if use_bonuses else 0,
            )
        else:
            direction = "left" if choice == "push_left" else "right"
            combat.push_defender(self, attacker, defender, direction)
        self.end_turn()

    def _action_resolve_portal(
        self, player: Player, ocean_id: str, action_id: str
    ) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        user = self.get_user(player)
        if player.id != self.pending_portal_player_id:
            if user:
                user.speak_l("pirates-no-pending-portal", buffer="game")
            return
        if ocean_id == "random":
            new_position = random.randint(1, MAP_SIZE)
            ocean = (new_position - 1) // OCEAN_SIZE
        else:
            try:
                ocean = int(ocean_id)
            except ValueError:
                ocean = -1
            valid_oceans = self._occupied_portal_oceans(player)
            if ocean not in valid_oceans:
                if user:
                    user.speak_l(
                        "pirates-portal-option-unavailable",
                        buffer="game",
                        ocean=ocean_id,
                    )
                return
            ocean_start = ocean * OCEAN_SIZE + 1
            new_position = random.randint(ocean_start, ocean_start + OCEAN_SIZE - 1)

        self._clear_pending_portal()
        player.position = new_position
        skills.PORTAL.start_cooldown(player)
        self.play_sound(f"game_pirates/portal{random.randint(1, 2)}.ogg", volume=60)
        ocean_key = (
            self.selected_oceans[ocean]
            if ocean < len(self.selected_oceans)
            else "pirates-ocean-unknown"
        )
        for listener in self.players:
            listener_user = self.get_user(listener)
            if not listener_user:
                continue
            is_actor = listener.id == player.id
            key = "pirates-portal-success-you" if is_actor else "pirates-portal-success"
            if self._wants_brief(listener_user):
                key += "-brief"
            listener_user.speak_l(
                key,
                buffer="game",
                player=player.name,
                ocean=Localization.get(listener_user.locale, ocean_key),
                position=new_position,
            )
        self.charted_tiles[new_position] = True
        self.end_turn()

    # ==========================================================================
    # Status Actions
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show game status (speech only)."""
        if not isinstance(player, PiratesPlayer) and not player.is_spectator:
            return

        user = self.get_user(player)
        if not user:
            return
            
        locale = user.locale

        # Speak status for each active player individually
        for p in self.get_active_players():
            user.speak_l(
                "pirates-status-line",
                buffer="game",
                **self._status_kwargs(p, locale, detailed=False),
            )

    def _action_check_status_detailed(self, player: Player, action_id: str) -> None:
        """Show full game status list."""
        if not isinstance(player, PiratesPlayer) and not player.is_spectator:
            return

        self.live_status_box(
            player,
            "pirates_status",
            lambda _player, live_user: self._detailed_status_lines(live_user.locale),
        )

    def _status_kwargs(
        self, player: PiratesPlayer, locale: str, *, detailed: bool
    ) -> dict:
        progress, needed = player.leveling.get_xp_progress()
        return {
            "player": player.name,
            "level": player.level,
            "xp": player.xp,
            "progress": progress,
            "needed": needed,
            "points": Localization.get(
                locale, "game-points", count=player.score
            ),
            "gem_count": len(player.gems),
            "gems": gems.format_gem_list(player.gems, locale),
            "position": player.position,
            "ocean": Localization.get(
                locale, self._ocean_key_for_position(player.position)
            ),
            "skills": skills.format_active_skills(player, locale),
            "detail": "yes" if detailed else "no",
        }

    def _detailed_status_lines(self, locale: str) -> list[MenuItem]:
        lines: list[MenuItem] = []
        for p in self.get_active_players():
            lines.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "pirates-status-line",
                        **self._status_kwargs(p, locale, detailed=True),
                    ),
                    id=f"player:{p.id}",
                )
            )

        return lines

    def _action_check_position(self, player: Player, action_id: str) -> None:
        """Announce player's current position."""
        if not isinstance(player, PiratesPlayer) or player.is_spectator:
            return

        user = self.get_user(player)
        if user:
            ocean_key = self._ocean_key_for_position(player.position)
            user.speak_l(
                "pirates-your-position",
                buffer="game",
                position=player.position,
                ocean=Localization.get(user.locale, ocean_key),
                sector=((player.position - 1) // 5) + 1,
            )

    def _action_check_moon(self, player: Player, action_id: str) -> None:
        """Check moon brightness (gems collected percentage)."""
        user = self.get_user(player)
        if user:
            rounds_until = (3 - (self.round % 3)) % 3
            key = (
                "pirates-moon-active"
                if self.golden_moon_active
                else "pirates-moon-inactive"
            )
            user.speak_l(
                key,
                buffer="game",
                round=self.round,
                rounds=rounds_until or 3,
                collected=self.gems_collected,
                remaining=self.total_gems,
                total=TOTAL_GEMS,
            )

    # ==========================================================================
    # Combat Helpers
    # ==========================================================================

    def get_targets_in_range(self, attacker: PiratesPlayer) -> list[PiratesPlayer]:
        """Get all valid targets within attack range."""
        return combat.get_targets_in_range(self, attacker)

    def handle_cannonball_attack(
        self, player: PiratesPlayer, target_id: str
    ) -> str:
        """Handle a cannonball attack action."""
        targets = self.get_targets_in_range(player)

        if not targets:
            max_range = skills.get_attack_range(player)
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-no-targets", buffer="game", range=max_range)
            return "continue"

        target = self.get_player_by_id(target_id)
        if not isinstance(target, PiratesPlayer) or target not in targets:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "pirates-target-out-of-range",
                    buffer="game",
                    target=target.name if isinstance(target, PiratesPlayer) else target_id,
                    range=skills.get_attack_range(player),
                    position=player.position,
                )
            return "continue"

        result = combat.do_attack(
            self,
            player,
            target,
            self.golden_moon_active,
            self.options.combat_xp_multiplier,
        )
        if result.boarding_pending:
            return "continue"
        return "end_turn"

    def begin_boarding(
        self,
        attacker: PiratesPlayer,
        defender: PiratesPlayer,
        attack_bonus: int,
        defense_bonus: int,
    ) -> bool:
        """Enter the framework-owned boarding choice flow after a direct hit."""
        self.pending_boarding_attacker_id = attacker.id
        self.pending_boarding_defender_id = defender.id
        self.pending_boarding_attack_bonus = attack_bonus
        self.pending_boarding_defense_bonus = defense_bonus
        self.refresh_menus(attacker)
        self.execute_action(attacker, "resolve_boarding")
        # The boarding flow owns turn completion for both humans and bots.
        return True

    def handle_portal(self, player: PiratesPlayer) -> str:
        """Open a persistent ocean choice for the Portal skill."""
        self.pending_portal_player_id = player.id
        self.refresh_menus(player)
        self.execute_action(player, "resolve_portal")
        return "continue"

    def handle_battleship(self, player: PiratesPlayer) -> str:
        """Handle the battleship skill (two attacks)."""
        self.play_sound("game_pirates/battleship.ogg", volume=60)

        self._broadcast_actor_l(
            player,
            "pirates-battleship-activated",
            "pirates-battleship-activated-player",
            brief_personal_key="pirates-battleship-activated-brief",
            brief_others_key="pirates-battleship-activated-player-brief",
            shots=2,
            cooldown=skills.BATTLESHIP.max_cooldown,
        )

        for shot in range(1, 3):
            targets = self.get_targets_in_range(player)
            if not targets:
                self._broadcast_actor_l(
                    player,
                    "pirates-battleship-no-targets",
                    "pirates-battleship-no-targets-player",
                    brief_personal_key="pirates-battleship-no-targets-brief",
                    brief_others_key="pirates-battleship-no-targets-player-brief",
                    shot=shot,
                    range=skills.get_attack_range(player),
                )
                break

            target = bot_ai.bot_select_target(self, player, targets)
            if target:
                self._broadcast_actor_l(
                    player,
                    "pirates-battleship-shot",
                    "pirates-battleship-shot-player",
                    brief_personal_key="pirates-battleship-shot-brief",
                    brief_others_key="pirates-battleship-shot-player-brief",
                    shot=shot,
                    target=target.name,
                )
                combat.do_attack(
                    self,
                    player,
                    target,
                    self.golden_moon_active,
                    self.options.combat_xp_multiplier,
                    allow_boarding=False,
                    announce_fire=False,
                )

        return "end_turn"
