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
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, FloatOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

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

    players: list[PiratesPlayer] = field(default_factory=list)
    options: PiratesOptions = field(default_factory=PiratesOptions)

    # Game state
    selected_oceans: list[str] = field(default_factory=list)
    charted_tiles: dict[int, bool] = field(default_factory=dict)
    gem_positions: dict[int, int] = field(default_factory=dict)
    gems_collected: int = 0
    total_gems: int = 18
    golden_moon_active: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Pirates of the Lost Seas"

    @classmethod
    def get_type(cls) -> str:
        return "pirates"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    def __post_init__(self):
        """Initialize non-serialized state."""
        super().__post_init__()

    def rebuild_runtime_state(self) -> None:
        """Rebuild runtime state after deserialization."""
        super().rebuild_runtime_state()
        # Skills are now on each player, no need to rebuild here

        # Fix dict keys that became strings after JSON deserialization
        if self.gem_positions:
            self.gem_positions = {int(k): v for k, v in self.gem_positions.items()}
        if self.charted_tiles:
            self.charted_tiles = {int(k): v for k, v in self.charted_tiles.items()}

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> PiratesPlayer:
        """Create a new Pirates player."""
        # Skills are initialized in PiratesPlayer.__post_init__
        return PiratesPlayer(id=player_id, name=name, is_bot=is_bot)

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
            )
        )
        action_set.add(
            Action(
                id="move_right",
                label=Localization.get(locale, "pirates-move-right"),
                handler="_action_move_right",
                is_enabled="_is_move_enabled",
                is_hidden="_is_move_hidden",
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
            )
        )
        action_set.add(
            Action(
                id="move_2_right",
                label=Localization.get(locale, "pirates-move-2-right"),
                handler="_action_move_2_right",
                is_enabled="_is_move_2_enabled",
                is_hidden="_is_move_2_hidden",
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
            )
        )
        action_set.add(
            Action(
                id="move_3_right",
                label=Localization.get(locale, "pirates-move-3-right"),
                handler="_action_move_3_right",
                is_enabled="_is_move_3_enabled",
                is_hidden="_is_move_3_hidden",
            )
        )

        """# Cannonball attack (always available)
        action_set.add(
            Action(
                id="cannonball",
                label=Localization.get(locale, "pirates-cannonball"),
                handler="_action_cannonball",
                is_enabled="_is_cannonball_enabled",
                is_hidden="_is_cannonball_hidden",
            )
        )"""

        # Skill menu
        action_set.add(
            Action(
                id="use_skill",
                label=Localization.get(locale, "pirates-use-skill"),
                handler="_action_use_skill",
                is_enabled="_is_skill_enabled",
                is_hidden="_is_skill_hidden",
                input_request=MenuInput(
                    options="_get_skill_options",
                    prompt="pirates-select-skill",
                ),
            )
        )

        # Status actions
        action_set.add(
            Action(
                id="check_moon",
                label=Localization.get(locale, "pirates-check-moon"),
                handler="_action_check_moon",
                is_enabled="_is_moon_check_enabled",
                is_hidden="_is_moon_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_moon",
                label=Localization.get(locale, "pirates-check-moon"),
                handler="_action_check_moon",
                is_enabled="_is_moon_check_enabled",
                is_hidden="_is_moon_check_hidden",
            )
        )
        
        # WEB-SPECIFIC: Moved to Standard Action Set for Web
        is_web = user and getattr(user, "client_type", "") == "web"
        if not is_web:
            action_set.add(
                Action(
                    id="check_position",
                    label=Localization.get(locale, "pirates-check-position"),
                    handler="_action_check_position",
                    is_enabled="_is_status_enabled",
                    is_hidden="_is_always_hidden",  # Always hidden, keybind only
                )
            )

        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "pirates-check-status"),
                handler="_action_check_status",
                is_enabled="_is_status_enabled",
                is_hidden="_is_status_hidden",
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_position", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            locale = user.locale

            # Ensure 'check_position' is in standard set (moved from turn set for web)
            if not action_set.get_action("check_position"):
                 action_set.add(
                    Action(
                        id="check_position",
                        label=Localization.get(locale, "pirates-check-position"),
                        handler="_action_check_position",
                        is_enabled="_is_status_enabled",
                        is_hidden="_is_check_position_hidden", # Use new visibility method
                    )
                )

            # Reordering Logic
            final_order = []
            for aid in self.web_target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)
            
            for aid in action_set._order:
                if aid not in self.web_target_order:
                    final_order.append(aid)
            
            action_set._order = final_order

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        self.define_keybind(
            "p",
            "Check position",
            ["check_position"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "m",
            "Check moon brightness",
            ["check_moon"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_move_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_move_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_2_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return "pirates-requires-level-15"
        return None

    def _is_move_2_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_3_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return "pirates-requires-level-150"
        return None

    def _is_move_3_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_cannonball_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_cannonball_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_skill_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_skill_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_skill_options(self, player: Player) -> list[str]:
        """Get available skills for the skill menu."""
        if not isinstance(player, PiratesPlayer):
             # We can't easily get locale safely here without player, but let's try
             # Actually if player is not valid, we probably just return empty or default english
             return ["Back"]

        user = self.get_user(player)
        locale = user.locale if user else "en"

        options = []
        for skill in skills.get_available_skills(player):
            options.append(skill.get_menu_label(player, locale))

        options.append(Localization.get(locale, "pirates-menu-back"))
        return options

    def _is_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_status_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_moon_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not self.golden_moon_active:
            return "pirates-no-golden-moon"
        return None

    def _is_moon_check_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if not self.golden_moon_active:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_always_hidden(self, player: Player) -> Visibility:
        """Always return hidden - for keybind-only actions."""
        return Visibility.HIDDEN

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_position_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web, hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Play music and ambience
        self.play_music("game_pirates/mus.ogg")
        self.play_ambience("game_pirates/amloop.ogg", intro="game_pirates/am_intro.ogg")

        self.broadcast_l("pirates-welcome")

        # Select 4 random oceans
        available = list(OCEAN_NAMES)
        random.shuffle(available)
        self.selected_oceans = available[:4]

        # self.broadcast_l("pirates-oceans", oceans=", ".join(self.selected_oceans))
        # Manual broadcast to localize ocean names
        for p in self.get_active_players():
            u = self.get_user(p)
            if u:
                oceans_str = ", ".join(Localization.get(u.locale, key) for key in self.selected_oceans)
                u.speak_l("pirates-oceans", buffer="game", oceans=oceans_str)

        # Initialize player positions randomly
        for player in self.get_active_players():
            player.position = random.randint(1, 40)

        # Initialize charted tiles
        self.charted_tiles = {i: False for i in range(1, 41)}

        # Place gems
        self.gem_positions = gems.place_gems(40)
        self.total_gems = 18
        self.gems_collected = 0

        self.broadcast_l("pirates-gems-placed", total=self.total_gems)

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Rebuild menus and start first turn
        self.rebuild_all_menus()
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
            self.broadcast_l("pirates-golden-moon")

        # Announce first turn
        self._announce_turn()

    def _announce_turn(self) -> None:
        """Announce whose turn it is."""
        player = self.current_player
        if not player or not isinstance(player, PiratesPlayer):
            return

        # Update skill timers
        skills.on_turn_start(self, player)

        # Play turn sound
        if not player.is_bot:
            user = self.get_user(player)
            if user and user.preferences.play_turn_sound:
                user.play_sound("game_pig/turn.ogg")

        self.broadcast_l(
            "pirates-turn",
            player=player.name,
            position=player.position
        )

    def on_tick(self) -> None:
        """Called every game tick."""
        super().on_tick()
        self.process_scheduled_sounds()

        if self.status != "playing":
            return

        # Process bot thinking
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

        self.rebuild_all_menus()

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

        user = self.get_user(player)
        if user:
            gem_local = Localization.get(user.locale, gem_name)
            user.speak_l("pirates-gem-found-you", buffer="game", gem=gem_local, value=gem_value)
        
        # Manual broadcast
        for p in self.get_active_players():
            if p.id == player.id: continue
            u = self.get_user(p)
            if u:
                gem_local = Localization.get(u.locale, gem_name)
                u.speak_l(
                    "pirates-gem-found",
                    player=player.name,
                    gem=gem_local,
                    value=gem_value
                )

        # Give XP for finding gem
        xp_gain = random.randint(150, 300)
        moon_mult = 3.0 if self.golden_moon_active else 1.0
        player.leveling.give_xp(
            self, player.name, xp_gain, moon_mult, self.options.find_gem_xp_multiplier
        )

        # Mark gem as collected
        self.gem_positions[player.position] = -1
        self.total_gems -= 1
        self.gems_collected += 1
        self.charted_tiles[player.position] = True

    def _end_game(self) -> None:
        """End the game and determine winner."""
        self.broadcast_l("pirates-all-gems-collected")

        # Find winner by highest score
        active_players = self.get_active_players()
        if not active_players:
            return

        highest_score = max(p.score for p in active_players)
        winners = [p for p in active_players if p.score == highest_score]

        # If tie, pick random winner
        winner = random.choice(winners)

        self.play_sound("game_pig/win.ogg", volume=80)
        self.broadcast_l("pirates-winner", player=winner.name, score=winner.score)

        # Store winner info for result
        self._winner_name = winner.name
        self._winner_score = winner.score

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
            final_gems[p.name] = gems.format_gem_list(p.gems)

        winner_name = getattr(self, "_winner_name", None)
        winner_score = getattr(self, "_winner_score", 0)

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                )
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner_name,
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

        for i, (name, score) in enumerate(final_scores.items(), 1):
            level = final_levels.get(name, 0)
            points_str = Localization.get(locale, "game-points", count=score)
            line = Localization.get(
                locale,
                "pirates-end-score-line",
                rank=i,
                player=name,
                points=points_str,
                level=level
            )
            lines.append(line)

        return lines

    # ==========================================================================
    # Movement Actions
    # ==========================================================================

    def _move_player(self, player: PiratesPlayer, amount: int) -> bool:
        """
        Move a player by the specified amount.

        Returns:
            True if move was successful, False if blocked by map edge
        """
        old_position = player.position

        if amount > 0:
            new_position = min(40, player.position + amount)
        else:
            new_position = max(1, player.position + amount)

        if new_position == old_position:
            # Blocked by map edge
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-map-edge", buffer="game", position=old_position)
            return False

        player.position = new_position

        # Play movement sound
        abs_amount = abs(amount)
        if abs_amount == 1:
            sound_num = random.randint(1, 3)
            self.play_sound(f"game_pirates/move{sound_num}.ogg", volume=60)
        elif abs_amount == 2:
            sound_num = random.randint(1, 3)
            self.play_sound(f"game_pirates/boat{sound_num}.ogg", volume=60)
        elif abs_amount == 3:
            sound_num = random.randint(1, 2)
            self.play_sound(f"game_pirates/future{sound_num}.ogg", volume=60)

        direction_key = "pirates-dir-right" if amount > 0 else "pirates-dir-left"
        user = self.get_user(player)
        if user:
            direction_local = Localization.get(user.locale, direction_key)
            if abs_amount == 1:
                user.speak_l("pirates-move-you", buffer="game", direction=direction_local, position=player.position)
            else:
                user.speak_l("pirates-move-you-tiles", buffer="game", tiles=abs_amount, direction=direction_local, position=player.position)

        # Manual broadcast
        for p in self.get_active_players():
            if p.id == player.id: continue
            u = self.get_user(p)
            if u:
                direction_local = Localization.get(u.locale, direction_key)
                u.speak_l(
                    "pirates-move",
                    player=player.name,
                    direction=direction_local,
                    position=player.position
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

    def _action_cannonball(self, player: Player, action_id: str) -> None:
        """Fire a cannonball at a target in range."""
        if not isinstance(player, PiratesPlayer):
            return
        if self.current_player != player:
            return

        result = self.handle_cannonball_attack(player)
        if result == "end_turn":
            self.end_turn()

    # ==========================================================================
    # Skill Actions
    # ==========================================================================

    def _action_use_skill(self, player: Player, skill_choice: str, action_id: str) -> None:
        """Handle skill menu selection."""
        if not isinstance(player, PiratesPlayer):
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"
        back_label = Localization.get(locale, "pirates-menu-back")

        if skill_choice == back_label:
            return

        # Find the skill by matching the label
        for skill in skills.get_available_skills(player):
            if skill.get_menu_label(player, locale) == skill_choice:
                can_use, reason = skill.can_perform(self, player)
                if can_use:
                    result = skill.do_action(self, player)
                    if result == "end_turn":
                        self.end_turn()
                else:
                    user = self.get_user(player)
                    if user and reason:
                        user.speak(reason, buffer="game")
                return

    # ==========================================================================
    # Status Actions
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show game status to the player."""
        if not isinstance(player, PiratesPlayer):
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"

        lines = []
        for p in self.get_active_players():
            gem_str = gems.format_gem_list(p.gems, locale)
            points_str = Localization.get(locale, "game-points", count=p.score)
            status_line = Localization.get(
                locale, 
                "pirates-status-line",
                player=p.name,
                level=p.level,
                xp=p.xp,
                points=points_str,
                gems=gem_str
            )
            lines.append(status_line)

        self.status_box(player, lines)

    def _action_check_position(self, player: Player, action_id: str) -> None:
        """Announce player's current position."""
        if not isinstance(player, PiratesPlayer):
            return

        ocean_index = (player.position - 1) // 10
        ocean_key = self.selected_oceans[ocean_index] if ocean_index < len(self.selected_oceans) else "Unknown"
        
        user = self.get_user(player)
        if user:
            ocean_name = Localization.get(user.locale, ocean_key) if ocean_key != "Unknown" else "Unknown"
            user.speak_l("pirates-your-position", buffer="game", position=player.position, ocean=ocean_name)

    def _action_check_moon(self, player: Player, action_id: str) -> None:
        """Check moon brightness (gems collected percentage)."""
        brightness = (self.gems_collected * 100) // 18

        user = self.get_user(player)
        if user:
            user.speak_l(
                "pirates-moon-brightness",
                brightness=brightness,
                collected=self.gems_collected,
                total=18
            )

    # ==========================================================================
    # Combat Helpers
    # ==========================================================================

    def get_targets_in_range(self, attacker: PiratesPlayer) -> list[PiratesPlayer]:
        """Get all valid targets within attack range."""
        return combat.get_targets_in_range(self, attacker)

    def handle_cannonball_attack(self, player: PiratesPlayer) -> str:
        """Handle a cannonball attack action."""
        targets = self.get_targets_in_range(player)

        if not targets:
            max_range = skills.get_attack_range(player)
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-no-targets", buffer="game", range=max_range)
            return "continue"

        # For human players, show target selection menu
        if not player.is_bot:
            # This would need to be handled via the action input system
            # For now, simplified to auto-select first target
            pass

        # Select target (bot or simplified)
        target = bot_ai.bot_select_target(self, player, targets)
        if target:
            combat.do_attack(
                self, player, target,
                self.golden_moon_active,
                self.options.combat_xp_multiplier,
                self.options.gem_stealing
            )
            return "end_turn"

        return "continue"

    def handle_portal(self, player: PiratesPlayer, skill) -> str:
        """Handle the portal skill."""
        # Find oceans with other players
        occupied_oceans: list[tuple[int, str]] = []
        for p in self.get_active_players():
            if p.id == player.id:
                continue
            ocean_num = (p.position - 1) // 10
            ocean_name = self.selected_oceans[ocean_num] if ocean_num < len(self.selected_oceans) else "Unknown"
            if not any(o[0] == ocean_num for o in occupied_oceans):
                occupied_oceans.append((ocean_num, ocean_name))

        if not occupied_oceans:
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-portal-no-ships", buffer="game")
            self.broadcast_l("pirates-portal-fizzle", player=player.name, exclude=player)
            return "continue"

        # Select ocean (bot or human)
        if player.is_bot:
            chosen_ocean = bot_ai.bot_select_portal_ocean(self, player, occupied_oceans)
        else:
            # For now, simplified to random selection
            chosen_ocean = random.choice(occupied_oceans)[0]

        if chosen_ocean is None:
            return "continue"

        # Teleport to random position in chosen ocean
        ocean_start = chosen_ocean * 10 + 1
        ocean_end = (chosen_ocean + 1) * 10
        new_pos = random.randint(ocean_start, ocean_end)

        player.position = new_pos
        skill.start_cooldown(player)

        sound_num = random.randint(1, 2)
        self.play_sound(f"game_pirates/portal{sound_num}.ogg", volume=60)

        ocean_key = self.selected_oceans[chosen_ocean] if chosen_ocean < len(self.selected_oceans) else "Unknown"
        
        # Manual broadcast
        for p in self.get_active_players():
            u = self.get_user(p)
            if u:
                ocean_local = Localization.get(u.locale, ocean_key) if ocean_key != "Unknown" else "Unknown"
                u.speak_l(
                    "pirates-portal-success",
                    player=player.name,
                    ocean=ocean_local,
                    position=new_pos
                )

        self.charted_tiles[new_pos] = True
        return "end_turn"

    def handle_battleship(self, player: PiratesPlayer) -> str:
        """Handle the battleship skill (two attacks)."""
        self.play_sound("game_pirates/battleship.ogg", volume=60)

        user = self.get_user(player)
        if user:
            user.speak_l("pirates-battleship-activated", buffer="game")
            
        # Manual broadcast
        for p in self.get_active_players():
            if p.id == player.id: continue
            u = self.get_user(p)
            if u:
                skill_name = Localization.get(u.locale, skills.BATTLESHIP.name)
                u.speak_l("pirates-skill-activated", buffer="game", player=player.name, skill=skill_name)

        for shot in range(1, 3):
            targets = self.get_targets_in_range(player)
            if not targets:
                if user:
                    user.speak_l("pirates-battleship-no-targets", buffer="game", shot=shot)
                break

            if user:
                user.speak_l("pirates-battleship-shot", buffer="game", shot=shot)

            target = bot_ai.bot_select_target(self, player, targets)
            if target:
                combat.do_attack(
                    self, player, target,
                    self.golden_moon_active,
                    self.options.combat_xp_multiplier,
                    self.options.gem_stealing
                )

        return "end_turn"

    def request_boarding_choice(self, attacker: PiratesPlayer, defender: PiratesPlayer) -> str:
        """Request boarding action choice from player (simplified for bot/default)."""
        can_steal = self.options.gem_stealing != "disabled" and defender.has_gems()
        return bot_ai.bot_select_boarding_action(self, attacker, defender, can_steal)
