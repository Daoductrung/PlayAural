"""Backgammon game for PlayAural."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
import random

log = logging.getLogger(__name__)

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import User, MenuItem
from ...game_utils.menu_management_mixin import MenuBuild
from .bot import bot_think
from .moves import (
    BackgammonMove,
    apply_move,
    generate_legal_moves,
    generate_legal_turn_moves,
    has_any_legal_move,
    must_use_both_dice,
    undo_last_move,
)
from .state import (
    BackgammonGameState,
    BackgammonBoardState,
    INITIAL_BOARD,
    all_checkers_in_home,
    bar_count,
    build_initial_game_state,
    color_sign,
    game_multiplier,
    off_count,
    opponent_color,
    outside_home_count,
    pip_count,
    point_count,
    point_number_for_player,
    point_owner,
    remaining_dice,
    remaining_dice_unique,
    roll_dice,
    set_bar,
    set_off,
)


BOT_DIFFICULTY_CHOICES = [
    "random",
    "simple",
]
BOT_DIFFICULTY_LABELS = {
    "random": "backgammon-difficulty-random",
    "simple": "backgammon-difficulty-simple",
}
TICKS_PER_SECOND = 20
DROP_DOUBLE_CONFIRM_SECONDS = 10
DROP_DOUBLE_CONFIRM_TICKS = DROP_DOUBLE_CONFIRM_SECONDS * TICKS_PER_SECOND


@dataclass
class BackgammonOptions(GameOptions):
    """Configurable options for Backgammon."""

    match_length: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=25,
            value_key="match_length",
            label="backgammon-option-match-length",
            prompt="backgammon-option-select-match-length",
            change_msg="backgammon-option-changed-match-length",
        )
    )
    bot_difficulty: str = option_field(
        MenuOption(
            default="simple",
            choices=BOT_DIFFICULTY_CHOICES,
            choice_labels=BOT_DIFFICULTY_LABELS,
            value_key="bot_difficulty",
            label="backgammon-option-bot-difficulty",
            prompt="backgammon-option-select-bot-difficulty",
            change_msg="backgammon-option-changed-bot-difficulty",
        )
    )


@dataclass
class BackgammonPlayer(Player):
    """Player state for Backgammon."""

    color: str = ""  # "red" or "white"
    drop_confirm_ticks: int = 0


@register_game
@dataclass
class BackgammonGame(Game):
    """Backgammon with accessibility-first design."""

    relevant_preferences = ["brief_announcements", "confirm_destructive_actions"]

    players: list[BackgammonPlayer] = field(default_factory=list)
    options: BackgammonOptions = field(default_factory=BackgammonOptions)
    game_state: BackgammonGameState = field(default_factory=BackgammonGameState)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._forced_dice: list[int] | None = None
        self._nav_cursor: int | None = None
        self._nav_selected_source: int | None = None

    def rebuild_runtime_state(self) -> None:
        """Rebuild derived move restrictions and transient navigation state."""
        super().rebuild_runtime_state()
        self._nav_cursor = None
        self._nav_selected_source = None
        self._check_forced_dice()

    @classmethod
    def get_name(cls) -> str:
        return "Backgammon"

    @classmethod
    def get_type(cls) -> str:
        return "backgammon"

    @classmethod
    def get_category(cls) -> str:
        return "board"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> BackgammonPlayer:
        return BackgammonPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        if user:
            return user.locale
        return "en"

    @staticmethod
    def _perspective_color(color: str) -> str:
        """Use a stable Red-side board orientation for colorless spectators."""
        return color if color in {"red", "white"} else "red"

    def _get_player_by_color(self, color: str) -> BackgammonPlayer | None:
        for p in self.players:
            if isinstance(p, BackgammonPlayer) and p.color == color:
                return p
        return None

    def _broadcast_actor_l(
        self,
        player: BackgammonPlayer,
        personal_key: str,
        public_key: str,
        **kwargs,
    ) -> None:
        self.broadcast_personal_l(
            player,
            personal_key,
            public_key,
            buffer="game",
            **kwargs,
        )

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: BackgammonPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        # 24 point actions in grid order: 2 rows x 12 cols
        # Top row (L→R): points 13-24 (indices 12-23)
        # Bottom row (L→R): points 12-1 (indices 11-0)
        for idx in self._grid_indices():
            action_set.add(
                Action(
                    id=f"point_{idx}",
                    label="",
                    handler="_action_point_click",
                    is_enabled="_is_point_enabled",
                    is_hidden="_is_point_hidden",
                    get_label="_get_point_label",
                    get_sound="_get_point_sound",
                    show_in_actions_menu=False,
                )
            )

        # Offer double (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="offer_double",
                label=Localization.get(locale, "backgammon-label-double"),
                handler="_action_offer_double",
                is_enabled="_is_offer_double_enabled",
                is_hidden="_is_offer_double_hidden",
                show_in_actions_menu=False,
            )
        )

        # Doubling response (shown as modal menu items when in doubling phase)
        action_set.add(
            Action(
                id="accept_double",
                label=Localization.get(locale, "backgammon-accept"),
                handler="_action_accept_double",
                is_enabled="_is_accept_double_enabled",
                is_hidden="_is_accept_double_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="drop_double",
                label=Localization.get(locale, "backgammon-drop"),
                handler="_action_drop_double",
                is_enabled="_is_drop_double_enabled",
                is_hidden="_is_drop_double_hidden",
                show_in_actions_menu=False,
            )
        )

        # Undo (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="undo_move",
                label=Localization.get(locale, "backgammon-label-undo"),
                handler="_action_undo_move",
                is_enabled="_is_undo_enabled",
                is_hidden="_is_undo_hidden",
                show_in_actions_menu=False,
            )
        )

        # Navigation (ctrl+up/down, hidden from menu)
        action_set.add(
            Action(
                id="navigate_next",
                label=Localization.get(locale, "backgammon-label-next-destination"),
                handler="_action_navigate_next",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_navigate_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="navigate_prev",
                label=Localization.get(locale, "backgammon-label-previous-destination"),
                handler="_action_navigate_prev",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_navigate_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="deselect",
                label=Localization.get(locale, "backgammon-label-deselect"),
                handler="_action_deselect",
                is_enabled="_is_deselect_enabled",
                is_hidden="_is_deselect_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        local_actions = [
            Action(
                id="check_status",
                label=Localization.get(locale, "backgammon-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_pip",
                label=Localization.get(locale, "backgammon-check-pip"),
                handler="_action_check_pip",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_score",
                label=Localization.get(locale, "backgammon-check-score"),
                handler="_action_check_score",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_score_detailed",
                label=Localization.get(locale, "backgammon-check-score-detailed"),
                handler="_action_check_score_detailed",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_cube",
                label=Localization.get(locale, "backgammon-check-cube"),
                handler="_action_check_cube",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_dice",
                label=Localization.get(locale, "backgammon-check-dice"),
                handler="_action_check_dice",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
        ]
        for action in local_actions:
            action_set.add(action)

        # Hide base score actions — we use our own check_score
        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_status",
                    "check_pip",
                    "check_score",
                    "check_score_detailed",
                    "check_cube",
                    "check_dice",
                    "whose_turn",
                    "whos_at_table",
                ],
            )

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        # Remove base class's score keybinds — we use our own
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        # Rolling is done by pressing enter on any grid point (no dedicated key)
        self.define_keybind(
            "shift+d",
            Localization.get("en", "backgammon-label-double"),
            ["offer_double"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "y",
            Localization.get("en", "backgammon-accept"),
            ["accept_double"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "n",
            Localization.get("en", "backgammon-drop"),
            ["drop_double"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "e",
            Localization.get("en", "backgammon-check-status"),
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            Localization.get("en", "backgammon-check-cube"),
            ["check_cube"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "p",
            Localization.get("en", "backgammon-check-pip"),
            ["check_pip"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "u", Localization.get("en", "backgammon-label-undo"), ["undo_move"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "s",
            Localization.get("en", "backgammon-check-score"),
            ["check_score"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+s",
            Localization.get("en", "backgammon-check-score-detailed"),
            ["check_score_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "backgammon-check-dice"),
            ["check_dice"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+down",
            Localization.get("en", "backgammon-label-next-destination"),
            ["navigate_next"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+right",
            Localization.get("en", "backgammon-label-next-destination"),
            ["navigate_next"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+up",
            Localization.get("en", "backgammon-label-previous-destination"),
            ["navigate_prev"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+left",
            Localization.get("en", "backgammon-label-previous-destination"),
            ["navigate_prev"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+backspace",
            Localization.get("en", "backgammon-label-deselect"),
            ["deselect"],
            state=KeybindState.ACTIVE,
        )

    # ==========================================================================
    # Grid helpers
    # ==========================================================================

    def _grid_indices(self) -> list[int]:
        """Return point indices in grid order for Red's perspective.

        The board is a 1D track (points 1-24) folded into a U.
        Home board is on the RIGHT (like a physical board in front of you):
          Top row (L→R):  13 14 15 16 17 18 | 19 20 21 22 23 24
          Bottom row (L→R): 12 11 10  9  8  7 |  6  5  4  3  2  1

        Home board (1-6) is bottom-right. Opponent enters top-left.
        For White, the menu build swaps the two halves so both
        players see their own home at bottom-right.
        """
        top = list(range(12, 24))  # indices 12,13,...,23 (pts 13→24)
        bottom = list(range(11, -1, -1))  # indices 11,10,...,0  (pts 12→1)
        return top + bottom

    # ==========================================================================
    # Ctrl+Up/Down navigation
    # ==========================================================================

    def _action_navigate_next(self, player: Player, action_id: str) -> None:
        if isinstance(player, BackgammonPlayer):
            self._navigate(player, direction=1)

    def _action_navigate_prev(self, player: Player, action_id: str) -> None:
        if isinstance(player, BackgammonPlayer):
            self._navigate(player, direction=-1)

    def _action_deselect(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.selected_source is not None:
            gs.selected_source = None
            self.play_sound("game_chess/setdown.ogg")
            self.refresh_menus(player)

    def _navigate(self, player: BackgammonPlayer, direction: int) -> None:
        """Cycle through navigation targets with ctrl+up/down.

        With a piece selected: cycle destinations (blots first).
        Without selection: cycle source squares with legal moves,
        or bar entry destinations if on the bar.
        """
        gs = self.game_state
        if player.color != gs.current_color:
            return
        if gs.turn_phase == "pre_roll":
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-need-roll-first", buffer="game")
            return
        if gs.turn_phase != "moving":
            return

        color = player.color
        selected = gs.selected_source

        # Reset cursor when selection state changes
        if selected != self._nav_selected_source:
            self._nav_cursor = None
            self._nav_selected_source = selected

        if selected is not None:
            targets = self._get_navigation_destinations(color, selected)
        elif bar_count(gs, color) > 0:
            targets = self._get_navigation_destinations(color, -1)
        else:
            targets = self._get_navigation_sources(color)

        if not targets:
            return

        if self._nav_cursor is not None and self._nav_cursor in targets:
            idx = targets.index(self._nav_cursor)
            idx = (idx + direction) % len(targets)
        else:
            idx = 0 if direction == 1 else len(targets) - 1

        self._nav_cursor = targets[idx]
        self._play_navigation_sound(player, targets[idx])
        self.request_menu_focus(player, f"point_{targets[idx]}")

    def _get_navigation_destinations(self, color: str, source: int) -> list[int]:
        """Destinations for source, ordered: opponent blots, own blots, other."""
        gs = self.game_state
        sign = color_sign(color)

        destinations = {
            move.destination
            for move in self._legal_turn_moves()
            if move.source == source and not move.is_bear_off
        }

        opponent_blots: list[int] = []
        own_blots: list[int] = []
        other: list[int] = []

        for dest in destinations:
            val = gs.board.points[dest]
            if val * sign < 0:
                opponent_blots.append(dest)
            elif val * sign > 0 and abs(val) == 1:
                own_blots.append(dest)
            else:
                other.append(dest)

        key = lambda idx: point_number_for_player(idx, color)
        opponent_blots.sort(key=key)
        own_blots.sort(key=key)
        other.sort(key=key)

        return opponent_blots + own_blots + other

    def _get_navigation_sources(self, color: str) -> list[int]:
        """Source points that have legal moves, sorted by point number."""
        sources = {move.source for move in self._legal_turn_moves() if move.source >= 0}
        return sorted(sources, key=lambda idx: point_number_for_player(idx, color))

    # ==========================================================================
    # Menu hooks (grid mode)
    # ==========================================================================

    def build_menu_items(self, player: "Player", user) -> MenuBuild:
        point_items, other_items = self._build_menu_items(player, user)
        use_grid = len(point_items) == 24

        # Flip for White: swap the two 12-item row halves so both
        # players see their own home board at bottom-left.
        if use_grid and isinstance(player, BackgammonPlayer) and player.color == "white":
            point_items = point_items[12:] + point_items[:12]

        return MenuBuild(
            items=point_items + other_items,
            grid_kwargs={
                "grid_enabled": use_grid,
                "grid_width": 12 if use_grid else 1,
                "grid_height": 2 if use_grid else 0,
            },
        )

    def _build_menu_items(self, player: "Player", user) -> tuple[list[MenuItem], list[MenuItem]]:
        """Build point items and other items for the turn menu."""
        point_items: list[MenuItem] = []
        other_items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            item = resolved.to_menu_item()
            if resolved.action.id.startswith("point_"):
                point_items.append(item)
            else:
                other_items.append(item)
        if self.is_touch_client(user):
            other_items.append(
                MenuItem(
                    text=Localization.get(user.locale, "actions-menu"),
                    id="web_actions_menu",
                )
            )
            other_items.append(
                MenuItem(
                    text=Localization.get(user.locale, "game-leave"),
                    id="web_leave_table",
                )
            )
        return point_items, other_items

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.round = 1

        active_players = self.get_active_players()
        self.set_turn_players(active_players, reset_index=True)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Assign colors randomly
        if random.random() < 0.5:  # nosec B311
            active_players[0].color = "red"
            active_players[1].color = "white"
        else:
            active_players[0].color = "white"
            active_players[1].color = "red"

        self.game_state = build_initial_game_state(
            match_length=self.options.match_length,
        )

        red_player = self._get_player_by_color("red")
        white_player = self._get_player_by_color("white")
        self.broadcast_l(
            "backgammon-game-started",
            buffer="game",
            red=red_player.name if red_player else "?",
            white=white_player.name if white_player else "?",
        )

        # Opening roll
        self._do_opening_roll()
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))

    def _do_opening_roll(self) -> None:
        """Roll one die each for opening; higher goes first."""
        gs = self.game_state
        gs.opening_roll = True

        d1, d2 = roll_dice()
        while d1 == d2:
            self.broadcast_l("backgammon-opening-tie", buffer="game", die=d1)
            d1, d2 = roll_dice()

        gs.opening_die_red = d1
        gs.opening_die_white = d2

        red_player = self._get_player_by_color("red")
        white_player = self._get_player_by_color("white")

        self.broadcast_l(
            "backgammon-opening-roll",
            buffer="game",
            red=red_player.name if red_player else "Red",
            red_die=d1,
            white=white_player.name if white_player else "White",
            white_die=d2,
        )
        self._play_dice_sound()

        if d1 > d2:
            first_color = "red"
        else:
            first_color = "white"

        gs.current_color = first_color
        gs.dice = [d1, d2]
        gs.dice_used = [False, False]
        gs.opening_roll = False
        gs.turn_phase = "moving"

        first_player = self._get_player_by_color(first_color)
        if first_player:
            self.current_player = first_player

        winner_name = first_player.name if first_player else first_color
        if first_player:
            self._broadcast_actor_l(
                first_player,
                "backgammon-opening-winner-you",
                "backgammon-opening-winner-player",
                die1=d1,
                die2=d2,
            )
        else:
            self.broadcast_l(
                "backgammon-opening-winner-player",
                buffer="game",
                player=winner_name,
                die1=d1,
                die2=d2,
            )

        self._check_forced_dice()
        if not has_any_legal_move(gs, first_color):
            if first_player:
                self._broadcast_actor_l(
                    first_player,
                    "backgammon-no-moves-you",
                    "backgammon-no-moves-player",
                )
            else:
                self.broadcast_l(
                    "backgammon-no-moves-player",
                    buffer="game",
                    player=winner_name,
                )
            self._end_moving_phase()
        else:
            self.refresh_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.game_active:
            return

        for player in self.players:
            if isinstance(player, BackgammonPlayer) and player.drop_confirm_ticks > 0:
                player.drop_confirm_ticks -= 1

        # During doubling phase, the responder is the OPPONENT of current_player.
        # BotHelper.on_tick only processes current_player, so we handle this case
        # explicitly: find the opponent bot and run their think/execute cycle.
        gs = self.game_state
        if self.is_sequence_bot_paused():
            return
        if gs.turn_phase == "doubling":
            opp_color = opponent_color(gs.current_color)
            opp = self._get_player_by_color(opp_color)
            if opp and opp.is_bot:
                BotHelper.process_bot_action(
                    bot=opp,
                    think_fn=lambda: self.bot_think(opp),
                    execute_fn=lambda action_id: self.execute_action(opp, action_id),
                )
            return  # Don't run normal BotHelper — doubler shouldn't act now

        BotHelper.on_tick(self)

    def bot_think(self, player: BackgammonPlayer) -> str | None:
        return bot_think(self, player)

    def execute_action(self, player, action_id, input_value=None, context=None):
        """Override to handle bot combined move format: point_{src}_{dst}."""
        if action_id and action_id.startswith("point_") and action_id.count("_") == 2:
            if isinstance(player, BackgammonPlayer) and player.is_bot:
                self._action_point_click(player, action_id)
                return
        super().execute_action(player, action_id, input_value=input_value, context=context)

    # ==========================================================================
    # Point click handler (roll + select + move)
    # ==========================================================================

    def _action_point_click(self, player: Player, action_id: str) -> None:
        """Handle point click — roll, select source, or select destination."""
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state

        # Pre-roll: pressing enter on any point rolls
        if gs.turn_phase == "pre_roll" and player.color == gs.current_color:
            self._do_roll(player)
            return

        if gs.turn_phase != "moving":
            return
        if player.color != gs.current_color:
            return

        parts = action_id.split("_")
        # Bot combined move: point_{src}_{dst}
        if len(parts) == 3:
            try:
                src = int(parts[1])
                dst = int(parts[2])
            except ValueError:
                return
            self._try_apply_move_direct(player, src, dst)
            return

        try:
            point_idx = int(parts[1])
        except (ValueError, IndexError):
            return

        color = player.color
        selected = gs.selected_source

        if selected is None:
            # First click: select source
            self._try_select_source(player, point_idx)
        else:
            # Second click: destination
            if selected == point_idx:
                # Activating a selected home point deliberately requests bear off.
                # Deselect remains available as its own stable menu action.
                self._try_bear_off(player, point_idx)
            else:
                self._try_move_to(player, selected, point_idx)

    def _try_select_source(self, player: BackgammonPlayer, point_idx: int) -> None:
        """Try to select a point as the move source."""
        gs = self.game_state
        color = player.color
        sign = color_sign(color)

        # Check if player has checkers on bar — directly attempt bar entry
        if bar_count(gs, color) > 0:
            self._try_apply_move_direct(player, -1, point_idx)
            return

        # Check the point has our checkers
        val = gs.board.points[point_idx]
        if val == 0:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-no-checkers-there", buffer="game")
            return
        if val * sign < 0:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-not-your-checkers", buffer="game")
            return

        source_moves = [move for move in self._legal_turn_moves() if move.source == point_idx]
        if not source_moves:
            raw_source_moves = [
                move
                for die_value in remaining_dice_unique(gs)
                for move in generate_legal_moves(gs, color, die_value)
                if move.source == point_idx
            ]
            user = self.get_user(player)
            if raw_source_moves and user:
                user.speak_l("backgammon-move-would-waste-die", buffer="game")
            elif 1 <= point_number_for_player(point_idx, color) <= 6:
                self._try_bear_off(player, point_idx)
            elif user:
                user.speak_l("backgammon-no-moves-from-here", buffer="game")
            return

        # If every rule-compliant destination from this source is off the board,
        # one activation is unambiguous and can bear off immediately.  When an
        # on-board move is also available, preserve selection so the player can
        # choose it instead; bearing off is never forced merely for convenience.
        if all(move.is_bear_off for move in source_moves):
            self._try_apply_move_direct(player, point_idx, 24)
            return

        gs.selected_source = point_idx
        self.play_sound("game_chess/pickup.ogg")
        self.refresh_menus(player)

    def _try_move_to(self, player: BackgammonPlayer, source: int, dest_point: int) -> None:
        """Try to move from selected source to destination point."""
        self._try_apply_move_direct(player, source, dest_point)

    def _try_bear_off(self, player: BackgammonPlayer, point_idx: int) -> None:
        """Try to bear off from a home point and explain any rule that blocks it."""
        gs = self.game_state
        color = player.color
        user = self.get_user(player)

        # Not in bearing-off position at all
        if not all_checkers_in_home(gs, color):
            if user:
                user.speak_l(
                    "backgammon-bearoff-not-home",
                    buffer="game",
                    outside=outside_home_count(gs, color),
                    bar=bar_count(gs, color),
                )
            return

        legal_bear_off = next(
            (
                move
                for move in self._legal_turn_moves()
                if move.source == point_idx and move.is_bear_off
            ),
            None,
        )
        if legal_bear_off is not None:
            self._try_apply_move_direct(player, point_idx, 24)
            return

        raw_bear_off = any(
            move.source == point_idx and move.is_bear_off
            for die_value in remaining_dice_unique(gs)
            for move in generate_legal_moves(gs, color, die_value)
        )
        if raw_bear_off:
            if user:
                user.speak_l("backgammon-move-would-waste-die", buffer="game")
            return

        # All checkers are home but can't bear off from this specific point.
        # Give a helpful error explaining why.
        pn = point_number_for_player(point_idx, color)
        usable_dice = [
            d
            for d, u in zip(gs.dice, gs.dice_used)
            if not u and (self._forced_dice is None or d in self._forced_dice)
        ]

        if not usable_dice:
            if user:
                user.speak_l("backgammon-no-dice-remaining", buffer="game")
            return

        # The player's point number tells us the exact die needed
        exact_die = pn  # e.g. 5-point needs a 5 to bear off exactly

        # Which dice overshoot (could bear off if no higher checker)?
        overshooting = [d for d in usable_dice if d > exact_die]

        # Check: is there a higher checker blocking overshoot bear-off?
        sign = color_sign(color)
        higher_pn = None
        if color == "red":
            for i in range(point_idx + 1, 6):
                if gs.board.points[i] * sign > 0:
                    higher_pn = point_number_for_player(i, color)
                    break
        else:
            for i in range(18, point_idx):
                if gs.board.points[i] * sign > 0:
                    higher_pn = point_number_for_player(i, color)
                    break

        if overshooting and higher_pn is not None:
            # Has dice that overshoot but a higher checker blocks it
            die_str = ", ".join(str(d) for d in overshooting)
            if user:
                user.speak_l(
                    "backgammon-bearoff-blocked",
                    buffer="game",
                    point=pn,
                    die=die_str,
                    blocking_point=higher_pn,
                )
        else:
            # No die is large enough (all undershoot)
            die_str = ", ".join(str(d) for d in usable_dice)
            if user:
                user.speak_l(
                    "backgammon-bearoff-no-die",
                    buffer="game",
                    point=pn,
                    die=die_str,
                )

    def _legal_turn_moves(self) -> list[BackgammonMove]:
        """Return rule-compliant next moves for the entire remaining roll."""
        gs = self.game_state
        return generate_legal_turn_moves(gs, gs.current_color)

    def _format_die_values(self, dice: list[int]) -> str:
        if not dice:
            return "-"
        return ", ".join(str(die) for die in dice)

    def _destination_block_count(self, color: str, dest: int) -> int:
        gs = self.game_state
        if not 0 <= dest < 24:
            return 0
        if point_owner(gs, dest) != opponent_color(color):
            return 0
        count = point_count(gs, dest)
        return count if count >= 2 else 0

    def _move_exists_with_dice(
        self,
        color: str,
        source: int,
        dest: int,
        dice: list[int],
    ) -> bool:
        gs = self.game_state
        for die in dice:
            for move in generate_legal_moves(gs, color, die):
                if move.source == source and move.destination == dest:
                    return True
        return False

    def _speak_illegal_move(self, player: BackgammonPlayer, source: int, dest: int) -> None:
        """Explain why a requested checker move cannot be made right now."""
        user = self.get_user(player)
        if not user:
            return

        gs = self.game_state
        color = player.color
        unused_dice = remaining_dice_unique(gs)
        usable_dice = self._get_usable_dice()
        die_text = self._format_die_values(usable_dice or unused_dice)

        if not unused_dice:
            user.speak_l("backgammon-no-dice-remaining", buffer="game")
            return

        if bar_count(gs, color) > 0 and source != -1:
            user.speak_l("backgammon-must-enter-from-bar", buffer="game")
            return

        if source == -1:
            if bar_count(gs, color) <= 0:
                user.speak_l("backgammon-no-checkers-on-bar", buffer="game")
                return
            if not 0 <= dest < 24:
                user.speak_l("backgammon-invalid-destination", buffer="game")
                return
            dest_point = point_number_for_player(dest, color)
            blocked_count = self._destination_block_count(color, dest)
            if blocked_count:
                user.speak_l(
                    "backgammon-bar-entry-blocked",
                    buffer="game",
                    point=dest_point,
                    count=blocked_count,
                )
                return
            self._speak_forced_or_no_die_error(
                user,
                color=color,
                source=source,
                dest=dest,
                dice_text=die_text,
            )
            return

        if not 0 <= source < 24:
            user.speak_l("backgammon-illegal-move", buffer="game")
            return

        source_point = point_number_for_player(source, color)
        sign = color_sign(color)
        source_value = gs.board.points[source]
        if source_value == 0:
            user.speak_l(
                "backgammon-source-empty",
                buffer="game",
                point=source_point,
            )
            return
        if source_value * sign < 0:
            user.speak_l(
                "backgammon-source-opponent",
                buffer="game",
                point=source_point,
            )
            return

        if dest == 24:
            if not all_checkers_in_home(gs, color):
                user.speak_l(
                    "backgammon-bearoff-not-home",
                    buffer="game",
                    outside=outside_home_count(gs, color),
                    bar=bar_count(gs, color),
                )
                return
            self._speak_forced_or_no_die_error(
                user,
                color=color,
                source=source,
                dest=dest,
                dice_text=die_text,
            )
            return

        if not 0 <= dest < 24:
            user.speak_l("backgammon-invalid-destination", buffer="game")
            return

        dest_point = point_number_for_player(dest, color)
        blocked_count = self._destination_block_count(color, dest)
        if blocked_count:
            user.speak_l(
                "backgammon-destination-blocked",
                buffer="game",
                point=dest_point,
                count=blocked_count,
            )
            return

        self._speak_forced_or_no_die_error(
            user,
            color=color,
            source=source,
            dest=dest,
            dice_text=die_text,
        )

    def _speak_forced_or_no_die_error(
        self,
        user: User,
        *,
        color: str,
        source: int,
        dest: int,
        dice_text: str,
    ) -> None:
        gs = self.game_state
        unused_dice = remaining_dice_unique(gs)
        raw_move_exists = self._move_exists_with_dice(
            color,
            source,
            dest,
            unused_dice,
        )
        legal_move_exists = any(
            move.source == source and move.destination == dest
            for move in self._legal_turn_moves()
        )
        if raw_move_exists and not legal_move_exists:
            if self._forced_dice is not None:
                non_forced = [die for die in unused_dice if die not in self._forced_dice]
                if self._move_exists_with_dice(color, source, dest, non_forced):
                    user.speak_l(
                        "backgammon-must-use-forced-die",
                        buffer="game",
                        dice=self._format_die_values(self._forced_dice),
                    )
                    return
            user.speak_l("backgammon-move-would-waste-die", buffer="game")
            return

        if self._forced_dice is not None:
            non_forced = [die for die in unused_dice if die not in self._forced_dice]
            if self._move_exists_with_dice(color, source, dest, non_forced):
                user.speak_l(
                    "backgammon-must-use-forced-die",
                    buffer="game",
                    dice=self._format_die_values(self._forced_dice),
                )
                return

        if source == -1:
            dest_point = point_number_for_player(dest, color) if 0 <= dest < 24 else dest
            user.speak_l(
                "backgammon-no-die-for-bar-entry",
                buffer="game",
                point=dest_point,
                dice=dice_text,
            )
            return

        source_point = point_number_for_player(source, color)
        if dest == 24:
            user.speak_l(
                "backgammon-bearoff-no-die",
                buffer="game",
                point=source_point,
                die=dice_text,
            )
            return

        dest_point = point_number_for_player(dest, color) if 0 <= dest < 24 else dest
        user.speak_l(
            "backgammon-no-die-for-destination",
            buffer="game",
            src=source_point,
            dest=dest_point,
            dice=dice_text,
        )

    def _try_apply_move_direct(self, player: BackgammonPlayer, source: int, dest: int) -> None:
        """Try to apply a move from source to dest, finding matching die."""
        gs = self.game_state
        color = player.color

        matched_move = next(
            (
                move
                for move in self._legal_turn_moves()
                if move.source == source and move.destination == dest
            ),
            None,
        )
        matched_die_idx = None
        if matched_move is not None:
            matched_die_idx = next(
                (
                    index
                    for index, (die_value, used) in enumerate(zip(gs.dice, gs.dice_used))
                    if not used and die_value == matched_move.die_value
                ),
                None,
            )

        if matched_move is None or matched_die_idx is None:
            log.warning(
                "Illegal move: game=%s color=%s src=%s dst=%s dice=%s used=%s forced=%s",
                gs.game_number,
                color,
                source,
                dest,
                gs.dice,
                gs.dice_used,
                self._forced_dice,
            )
            gs.selected_source = None
            self.play_sound("game_chess/setdown.ogg")
            user = self.get_user(player)
            if user:
                self._speak_illegal_move(player, source, dest)
            self.refresh_menus(player)
            return

        # Apply the move
        apply_move(gs, matched_move, color)
        gs.dice_used[matched_die_idx] = True
        gs.selected_source = None

        # Announce
        self._announce_sub_move(player, matched_move)

        # Play sound
        if matched_move.is_hit:
            self.play_sound(f"game_chess/capture{random.randint(1, 2)}.ogg")  # nosec B311
        elif matched_move.is_bear_off:
            self.play_sound("mention.ogg", volume=50)
        else:
            self.play_sound("game_squares/step1.ogg")

        # Check if game won
        if off_count(gs, color) == 15:
            self._win_game(player)
            return

        # Check for more moves
        self._check_forced_dice()
        if not has_any_legal_move(gs, color):
            remaining = remaining_dice(gs)
            if remaining:
                self._broadcast_actor_l(
                    player,
                    "backgammon-no-moves-you",
                    "backgammon-no-moves-player",
                )
            self._end_moving_phase()
        elif not remaining_dice(gs):
            self._end_moving_phase()
        else:
            # The bot has another die to play this turn: pause between checkers
            # so a multi-move turn reads as distinct beats rather than a burst.
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(3, 6))  # nosec B311
            self.refresh_menus()

    def _do_roll(self, player: BackgammonPlayer) -> None:
        """Roll dice and enter moving phase."""
        gs = self.game_state
        d1, d2 = roll_dice()
        if d1 == d2:
            gs.dice = [d1, d1, d1, d1]
            gs.dice_used = [False, False, False, False]
        else:
            gs.dice = [d1, d2]
            gs.dice_used = [False, False]

        gs.moves_this_turn = []
        gs.turn_phase = "moving"

        self._play_dice_sound()
        self._broadcast_actor_l(
            player,
            "backgammon-roll-you",
            "backgammon-roll-player",
            die1=d1,
            die2=d2,
        )

        self._check_forced_dice()
        if not has_any_legal_move(gs, player.color):
            self._broadcast_actor_l(
                player,
                "backgammon-no-moves-you",
                "backgammon-no-moves-player",
            )
            self._end_moving_phase()
        else:
            # Pause a bot after the roll so it doesn't snap straight into its
            # first move — the dice deserve a beat. (_end_moving_phase already
            # paces the cross-turn handoff.)
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(4, 7))  # nosec B311
            self.refresh_menus()

    def _check_forced_dice(self) -> None:
        """Check and apply the must-use-both-dice rule."""
        gs = self.game_state
        unused = remaining_dice(gs)
        if len(unused) == 2 and unused[0] != unused[1]:
            self._forced_dice = must_use_both_dice(gs, gs.current_color, unused)
        else:
            self._forced_dice = None

    def _get_usable_dice(self) -> list[int]:
        """Get die values that can be used this sub-move."""
        return sorted({move.die_value for move in self._legal_turn_moves()})

    def _end_moving_phase(self) -> None:
        """End the moving phase and advance turn."""
        gs = self.game_state
        gs.turn_phase = "pre_roll"
        gs.selected_source = None
        gs.moves_this_turn = []
        self._forced_dice = None

        # Advance to other player
        opp_color = opponent_color(gs.current_color)
        gs.current_color = opp_color
        opp_player = self._get_player_by_color(opp_color)
        if opp_player:
            self.current_player = opp_player
            self.announce_turn()
            if opp_player.is_bot:
                BotHelper.jolt_bot(opp_player, ticks=random.randint(5, 10))  # nosec B311

        # A focus-preserving update (not a full re-show) of the already-shown
        # board. The grid persists for both players across the turn change (see
        # get_visible_actions: off-turn points disable but stay visible), so the
        # receiving player's cursor keeps its anchor instead of resetting.
        self.refresh_menus()

    # ==========================================================================
    # Doubling cube
    # ==========================================================================

    def _can_double(self, player: BackgammonPlayer) -> bool:
        """Check if player can offer the doubling cube."""
        return self._double_disabled_reason(player) is None

    def _double_disabled_reason(self, player: BackgammonPlayer) -> str | None:
        """Return a contextual reason that the doubling cube is unavailable."""
        gs = self.game_state
        if gs.match_length <= 1:
            return "backgammon-double-single-game"
        if gs.is_crawford:
            return "backgammon-double-crawford"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if gs.cube_owner and gs.cube_owner != player.color:
            return "backgammon-double-cube-owned"
        if gs.turn_phase != "pre_roll":
            return "backgammon-double-before-roll-only"
        return None

    def _action_offer_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        if not self._can_double(player):
            return
        gs = self.game_state
        gs.turn_phase = "doubling"
        new_value = gs.cube_value * 2
        for bg_player in self.players:
            if isinstance(bg_player, BackgammonPlayer):
                bg_player.drop_confirm_ticks = 0
        self._broadcast_actor_l(
            player,
            "backgammon-doubles-you",
            "backgammon-doubles-player",
            value=new_value,
        )
        # Jolt the opponent bot so they pause before responding
        opp_color = opponent_color(player.color)
        opp = self._get_player_by_color(opp_color)
        if opp and opp.is_bot:
            BotHelper.jolt_bot(opp, ticks=random.randint(3, 6))
        self.refresh_menus()

    def _action_accept_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return
        if player.color == gs.current_color:
            return  # Can't accept own double

        gs.cube_value *= 2
        gs.cube_owner = player.color
        gs.turn_phase = "pre_roll"
        player.drop_confirm_ticks = 0
        self._broadcast_actor_l(
            player,
            "backgammon-accepts-you",
            "backgammon-accepts-player",
        )
        self.refresh_menus()

    def _action_drop_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return
        if player.color == gs.current_color:
            return

        if not player.is_bot and player.drop_confirm_ticks == 0:
            user = self.get_user(player)
            if user and user.preferences.get_effective(
                "confirm_destructive_actions", game_type=self.get_type()
            ):
                player.drop_confirm_ticks = DROP_DOUBLE_CONFIRM_TICKS
                user.speak_l(
                    "backgammon-confirm-drop-double",
                    buffer="game",
                    seconds=DROP_DOUBLE_CONFIRM_SECONDS,
                )
                return

        player.drop_confirm_ticks = 0

        self._broadcast_actor_l(
            player,
            "backgammon-drops-you",
            "backgammon-drops-player",
        )
        winner = self._get_player_by_color(gs.current_color)
        if winner:
            self._score_game(winner, gs.cube_value)

    # ==========================================================================
    # Undo
    # ==========================================================================

    def _action_undo_move(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "moving":
            return
        if player.color != gs.current_color:
            return

        undone = undo_last_move(gs, player.color)
        if undone is None:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-nothing-to-undo", buffer="game")
            return

        # Unmark the die
        for i in range(len(gs.dice_used) - 1, -1, -1):
            if gs.dice_used[i] and gs.dice[i] == undone.die_value:
                gs.dice_used[i] = False
                break

        gs.selected_source = None
        self._check_forced_dice()
        self.play_sound("game_chess/setdown.ogg")
        user = self.get_user(player)
        if user:
            user.speak_l("backgammon-undone", buffer="game")
        self.refresh_menus()

    # ==========================================================================
    # Info keybinds
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        bar_r = gs.board.bar_red
        bar_w = gs.board.bar_white
        off_r = gs.board.off_red
        off_w = gs.board.off_white
        user.speak_l(
            "backgammon-status",
            buffer="game",
            bar_red=bar_r,
            bar_white=bar_w,
            outside_red=outside_home_count(gs, "red"),
            outside_white=outside_home_count(gs, "white"),
            off_red=off_r,
            off_white=off_w,
        )

    def _action_check_pip(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        user.speak_l(
            "backgammon-pip-count",
            buffer="game",
            red_pip=pip_count(gs, "red"),
            white_pip=pip_count(gs, "white"),
        )

    def _action_check_score(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        for line in self._match_score_lines(user.locale):
            user.speak(line, buffer="game")

    def _action_check_score_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "backgammon_score",
            lambda _player, live_user: self._match_score_lines(live_user.locale, detailed=True),
        )

    def _match_score_lines(self, locale: str, *, detailed: bool = False) -> list[str]:
        gs = self.game_state
        red_p = self._get_player_by_color("red")
        white_p = self._get_player_by_color("white")
        lines = [
            Localization.get(
                locale,
                "backgammon-match-score-line",
                player=red_p.name if red_p else "Red",
                score=gs.score_red,
                match_length=gs.match_length,
            ),
            Localization.get(
                locale,
                "backgammon-match-score-line",
                player=white_p.name if white_p else "White",
                score=gs.score_white,
                match_length=gs.match_length,
            ),
            Localization.get(locale, "backgammon-match-score-cube-line", cube=gs.cube_value),
        ]
        if detailed and gs.is_crawford:
            lines.append(Localization.get(locale, "backgammon-crawford"))
        return lines

    def _action_check_cube(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state

        if gs.match_length <= 1:
            user.speak_l("backgammon-cube-no-match", buffer="game")
            return

        # Who owns the cube?
        if not gs.cube_owner:
            owner_desc = "center"
        else:
            owner_p = self._get_player_by_color(gs.cube_owner)
            owner_desc = owner_p.name if owner_p else gs.cube_owner

        # Can the current player double right now?
        current_player = self._get_player_by_color(gs.current_color)
        if isinstance(current_player, BackgammonPlayer) and self._can_double(current_player):
            can_double = "yes"
        elif gs.is_crawford:
            can_double = "crawford"
        else:
            can_double = "no"

        user.speak_l(
            "backgammon-cube-status",
            buffer="game",
            value=gs.cube_value,
            owner=owner_desc,
            can_double=can_double,
        )

    def _action_check_dice(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        dice = remaining_dice(gs)
        if dice:
            user.speak_l("backgammon-dice", buffer="game", dice=" ".join(str(d) for d in dice))
        else:
            user.speak_l("backgammon-dice-none", buffer="game")

    # ==========================================================================
    # Scoring & game end
    # ==========================================================================

    def _win_game(self, winner: BackgammonPlayer) -> None:
        """Handle a player bearing off all checkers."""
        gs = self.game_state
        loser_color = opponent_color(winner.color)
        multiplier = game_multiplier(gs, loser_color)
        points = gs.cube_value * multiplier
        self._score_game(winner, points)

    def _score_game(self, winner: BackgammonPlayer, points: int) -> None:
        """Award points and check match end."""
        gs = self.game_state
        if winner.color == "red":
            gs.score_red += points
        else:
            gs.score_white += points

        self._broadcast_actor_l(
            winner,
            "backgammon-wins-game-you",
            "backgammon-wins-game-player",
            points=points,
        )

        # Check match end
        if gs.score_red >= gs.match_length:
            self._finish_match(self._get_player_by_color("red"))
        elif gs.score_white >= gs.match_length:
            self._finish_match(self._get_player_by_color("white"))
        else:
            # Crawford rule check
            if not gs.crawford_used:
                if gs.score_red == gs.match_length - 1 or gs.score_white == gs.match_length - 1:
                    gs.is_crawford = True
                    gs.crawford_used = True
                    self.broadcast_l("backgammon-crawford", buffer="game")
            elif gs.is_crawford:
                gs.is_crawford = False

            # Start new game
            gs.game_number += 1
            self._start_new_game()

    def _start_new_game(self) -> None:
        """Reset board for a new game within the match."""
        gs = self.game_state
        gs.board = BackgammonBoardState(points=list(INITIAL_BOARD))
        gs.dice = []
        gs.dice_used = []
        gs.turn_phase = "pre_roll"
        gs.selected_source = None
        gs.moves_this_turn = []
        gs.cube_value = 1
        gs.cube_owner = ""
        self._forced_dice = None
        for player in self.players:
            if isinstance(player, BackgammonPlayer):
                player.drop_confirm_ticks = 0

        self.broadcast_l("backgammon-new-game", buffer="game", number=gs.game_number)
        self._do_opening_roll()
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))

    def _finish_match(self, winner: BackgammonPlayer | None) -> None:
        """End the match."""
        self._match_winner = winner
        if winner:
            self._broadcast_actor_l(
                winner,
                "backgammon-match-winner-you",
                "backgammon-match-winner-player",
            )
        self.play_sound("game_pig/win.ogg")
        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result for the end screen."""
        from datetime import datetime

        gs = self.game_state
        winner = getattr(self, "_match_winner", None)
        red = self._get_player_by_color("red")
        white = self._get_player_by_color("white")

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
                for p in self.players
                if not p.is_spectator
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "score_red": gs.score_red,
                "score_white": gs.score_white,
                "match_length": gs.match_length,
                "red_name": red.name if red else "Red",
                "white_name": white.name if white else "White",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the match result for the end screen."""
        d = result.custom_data
        lines = []
        lines.append(
            Localization.get(
                locale,
                "backgammon-end-score",
                red=d.get("red_name", "Red"),
                red_score=d.get("score_red", 0),
                white=d.get("white_name", "White"),
                white_score=d.get("score_white", 0),
                match_length=d.get("match_length", 1),
            )
        )
        return lines

    # ==========================================================================
    # Sound helpers
    # ==========================================================================

    def _play_dice_sound(self) -> None:
        self.play_sound(f"game_squares/diceroll{random.randint(1, 3)}.ogg")  # nosec B311

    # ==========================================================================
    # Commentary / announcements
    # ==========================================================================

    def _announce_sub_move(self, player: BackgammonPlayer, move: BackgammonMove) -> None:
        """Announce a sub-move to all players with reflected point numbers."""
        gs = self.game_state
        color = player.color

        for p in self.players:
            if not isinstance(p, BackgammonPlayer):
                continue
            user = self.get_user(p)
            if not user:
                continue
            viewer_color = p.color
            self._speak_move(user, move, color, viewer_color)

    def _speak_move(
        self, user: User, move: BackgammonMove, mover_color: str, viewer_color: str
    ) -> None:
        """Speak a single sub-move to a user with point numbers in their perspective."""
        # Verbosity is a per-user preference (with optional per-game override).
        brief = bool(
            user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )
        if not brief:
            self._speak_move_verbose(user, move, mover_color, viewer_color)
            return
        if mover_color == viewer_color:
            is_self = "yes"
        elif viewer_color == "":
            is_self = "spectator"
        else:
            is_self = "no"
        mover = self._get_player_by_color(mover_color)
        opp = self._get_player_by_color(opponent_color(mover_color))
        player_name = mover.name if mover else "?"
        opponent_name = opp.name if opp else "?"

        perspective_color = self._perspective_color(viewer_color)
        if move.source == -1:
            dest_pn = point_number_for_player(move.destination, perspective_color)
            if move.is_hit:
                user.speak_l(
                    "backgammon-brief-move-bar-hit",
                    buffer="game",
                    is_self=is_self,
                    player=player_name,
                    opponent=opponent_name,
                    dest=dest_pn,
                )
            else:
                user.speak_l(
                    "backgammon-brief-move-bar",
                    buffer="game",
                    is_self=is_self,
                    player=player_name,
                    dest=dest_pn,
                )
        elif move.is_bear_off:
            src_pn = point_number_for_player(move.source, perspective_color)
            user.speak_l(
                "backgammon-brief-move-bearoff",
                buffer="game",
                is_self=is_self,
                player=player_name,
                src=src_pn,
            )
        elif move.is_hit:
            src_pn = point_number_for_player(move.source, perspective_color)
            dest_pn = point_number_for_player(move.destination, perspective_color)
            user.speak_l(
                "backgammon-brief-move-hit",
                buffer="game",
                is_self=is_self,
                player=player_name,
                opponent=opponent_name,
                src=src_pn,
                dest=dest_pn,
            )
        else:
            src_pn = point_number_for_player(move.source, perspective_color)
            dest_pn = point_number_for_player(move.destination, perspective_color)
            user.speak_l(
                "backgammon-brief-move-normal",
                buffer="game",
                is_self=is_self,
                player=player_name,
                src=src_pn,
                dest=dest_pn,
            )

    def _speak_move_verbose(
        self, user: User, move: BackgammonMove, mover_color: str, viewer_color: str
    ) -> None:
        """Speak a verbose sub-move: player name conjugation, captures, stack counts."""
        gs = self.game_state
        if mover_color == viewer_color:
            is_self = "yes"
        elif viewer_color == "":
            is_self = "spectator"
        else:
            is_self = "no"
        mover = self._get_player_by_color(mover_color)
        opp = self._get_player_by_color(opponent_color(mover_color))
        player_name = mover.name if mover else "?"
        opponent_name = opp.name if opp else "?"

        perspective_color = self._perspective_color(viewer_color)
        if move.source == -1:
            # Bar entry
            dest_pn = point_number_for_player(move.destination, perspective_color)
            dest_count = point_count(gs, move.destination)
            if move.is_hit:
                user.speak_l(
                    "backgammon-verbose-move-bar-hit",
                    buffer="game",
                    is_self=is_self,
                    player=player_name,
                    opponent=opponent_name,
                    dest=dest_pn,
                )
            else:
                user.speak_l(
                    "backgammon-verbose-move-bar",
                    buffer="game",
                    is_self=is_self,
                    player=player_name,
                    dest=dest_pn,
                    dest_count=dest_count,
                )
        elif move.is_bear_off:
            src_pn = point_number_for_player(move.source, perspective_color)
            src_count = point_count(gs, move.source)
            user.speak_l(
                "backgammon-verbose-move-bearoff",
                buffer="game",
                is_self=is_self,
                player=player_name,
                src=src_pn,
                src_count=src_count,
            )
        elif move.is_hit:
            src_pn = point_number_for_player(move.source, perspective_color)
            dest_pn = point_number_for_player(move.destination, perspective_color)
            src_count = point_count(gs, move.source)
            user.speak_l(
                "backgammon-verbose-move-hit",
                buffer="game",
                is_self=is_self,
                player=player_name,
                opponent=opponent_name,
                src=src_pn,
                dest=dest_pn,
                src_count=src_count,
            )
        else:
            src_pn = point_number_for_player(move.source, perspective_color)
            dest_pn = point_number_for_player(move.destination, perspective_color)
            src_count = point_count(gs, move.source)
            dest_count = point_count(gs, move.destination)
            user.speak_l(
                "backgammon-verbose-move-normal",
                buffer="game",
                is_self=is_self,
                player=player_name,
                src=src_pn,
                dest=dest_pn,
                src_count=src_count,
                dest_count=dest_count,
            )

    # ==========================================================================
    # Action visibility / enable callbacks
    # ==========================================================================

    def _is_point_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase == "doubling" and player.color != gs.current_color:
            return "action-not-available"
        if gs.turn_phase in ("pre_roll", "moving") and player.color != gs.current_color:
            return "action-not-your-turn"
        return None

    def _is_point_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        gs = self.game_state
        if gs.turn_phase == "doubling":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_point_label(self, player: Player, action_id: str) -> str:
        """Get label for a board point."""
        try:
            point_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return ""

        gs = self.game_state
        locale = self._player_locale(player)
        raw_color = player.color if isinstance(player, BackgammonPlayer) else ""
        color = self._perspective_color(raw_color)
        pn = point_number_for_player(point_idx, color)
        val = gs.board.points[point_idx]
        selected = (
            isinstance(player, BackgammonPlayer)
            and player.color == gs.current_color
            and gs.selected_source == point_idx
        )

        if val == 0:
            key = "backgammon-point-empty-selected" if selected else "backgammon-point-empty"
            return Localization.get(locale, key, point=pn)

        cnt = abs(val)
        owner = "red" if val > 0 else "white"
        owner_name = Localization.get(locale, f"backgammon-color-{owner}")
        selected_can_bear_off = selected and any(
            move.source == point_idx and move.is_bear_off for move in self._legal_turn_moves()
        )
        if selected_can_bear_off:
            key = "backgammon-point-occupied-selected-bearoff"
        elif selected:
            key = "backgammon-point-occupied-selected"
        else:
            key = "backgammon-point-occupied"
        return Localization.get(locale, key, point=pn, color=owner_name, count=cnt)

    def _point_sound_for(self, player: Player, point_idx: int) -> str | None:
        """Resolve the perspective-relative navigation sound for a board point.

        Sounds are "mine" vs "theirs" rather than fixed colors, so Red and
        White each hear their own checkers as the same sound. Empty points
        have no sound (None).
        """
        val = self.game_state.board.points[point_idx]
        if val == 0:
            return None

        player_color = player.color if isinstance(player, BackgammonPlayer) else ""
        perspective_color = self._perspective_color(player_color)
        is_own = (perspective_color == "red" and val > 0) or (
            perspective_color == "white" and val < 0
        )
        count = abs(val)

        if is_own:
            return "game_squares/token1.ogg" if count == 1 else "game_squares/token3.ogg"
        return "game_squares/token7.ogg" if count == 1 else "game_squares/token4.ogg"

    def _get_point_sound(self, player: Player, action_id: str) -> str | None:
        """Highlight sound for a board point, played by clients on focus.

        Wired into each point Action via ``get_sound`` so plain arrow-key
        navigation over the board grid plays each square's token sound.
        """
        try:
            point_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return None
        return self._point_sound_for(player, point_idx)

    def _play_navigation_sound(self, player: Player, point_idx: int) -> None:
        """Explicitly play a board point's navigation sound (ctrl+up/down)."""
        user = self.get_user(player)
        if not user:
            return
        sound = self._point_sound_for(player, point_idx)
        if sound:
            user.play_sound(sound)

    def _is_offer_double_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-cannot-double"
        return self._double_disabled_reason(player)

    def _is_undo_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-cannot-undo"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "backgammon-cannot-undo"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if not gs.moves_this_turn:
            return "backgammon-cannot-undo"
        return None

    def _is_accept_double_enabled(self, player: Player, action_id: str = "") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return "backgammon-not-doubling-phase"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-not-doubling-phase"
        if player.is_spectator:
            return "backgammon-not-doubling-phase"
        if player.color == gs.current_color:
            return "backgammon-not-doubling-phase"
        return None

    def _is_accept_double_hidden(self, player: Player, action_id: str = "") -> Visibility:
        if self._is_accept_double_enabled(player) is not None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_drop_double_enabled(self, player: Player, action_id: str = "") -> str | None:
        return self._is_accept_double_enabled(player)

    def _is_drop_double_hidden(self, player: Player, action_id: str = "") -> Visibility:
        return self._is_accept_double_hidden(player)

    def _touch_visible_when_enabled(self, player: Player, disabled_reason: str | None) -> Visibility:
        user = self.get_user(player)
        if disabled_reason is None and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_offer_double_hidden(self, player: Player) -> Visibility:
        return self._touch_visible_when_enabled(player, self._is_offer_double_enabled(player))

    def _is_undo_hidden(self, player: Player) -> Visibility:
        return self._touch_visible_when_enabled(player, self._is_undo_enabled(player))

    def _is_navigate_hidden(self, player: Player) -> Visibility:
        return self._touch_visible_when_enabled(player, self._is_navigate_enabled(player))

    def _is_deselect_hidden(self, player: Player) -> Visibility:
        return self._touch_visible_when_enabled(player, self._is_deselect_enabled(player))

    def _is_navigate_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if gs.turn_phase == "pre_roll":
            return "backgammon-need-roll-first"
        if gs.turn_phase != "moving":
            return "action-not-available"
        return None

    def _is_deselect_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "action-not-available"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if gs.selected_source is None:
            return "action-not-available"
        return None

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_touch_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN
