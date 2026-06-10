"""Senet game for PlayAural."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.options import MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import User, MenuItem, EscapeBehavior
from .bot import bot_think
from .moves import generate_legal_moves, apply_move, has_any_legal_move
from .state import (
    SenetGameState,
    PIECES_PER_PLAYER,
    SPECIAL_SQUARE_NAMES,
    HOUSE_WATER,
    HOUSE_HAPPINESS,
    HOUSE_HORUS,
    build_initial_state,
    opponent_num,
    pieces_remaining,
    throw_sticks,
)


BOT_DIFFICULTY_CHOICES = ["random", "simple"]
BOT_DIFFICULTY_LABELS = {
    "random": "senet-difficulty-random",
    "simple": "senet-difficulty-simple",
}


@dataclass
class SenetOptions(GameOptions):
    bot_difficulty: str = option_field(
        MenuOption(
            default="simple",
            choices=BOT_DIFFICULTY_CHOICES,
            choice_labels=BOT_DIFFICULTY_LABELS,
            value_key="bot_difficulty",
            label="senet-option-bot-difficulty",
            prompt="senet-option-select-bot-difficulty",
            change_msg="senet-option-changed-bot-difficulty",
        )
    )


@dataclass
class SenetPlayer(Player):
    player_num: int = 0  # 1 or 2


@register_game
@dataclass
class SenetGame(Game):
    """Senet - ancient Egyptian board game."""

    players: list[SenetPlayer] = field(default_factory=list)
    options: SenetOptions = field(default_factory=SenetOptions)
    game_state: SenetGameState = field(default_factory=SenetGameState)

    winner_name: str | None = None
    _nav_cursor: int | None = None
    _nav_skip_rebuild: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Senet"

    @classmethod
    def get_type(cls) -> str:
        return "senet"

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

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> SenetPlayer:
        return SenetPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        active_count = self.get_active_player_count()
        if active_count != 2:
            errors.append(("senet-error-exactly-two-players", {"count": active_count}))
        return errors

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_player_by_num(self, num: int) -> SenetPlayer | None:
        for p in self.get_active_players():
            if isinstance(p, SenetPlayer) and p.player_num == num:
                return p
        return None

    def _current_senet_player(self) -> SenetPlayer | None:
        return self._get_player_by_num(self.game_state.current_player_num)

    # ======================================================================
    # Action sets
    # ======================================================================

    def create_turn_action_set(self, player: SenetPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        for idx in self._grid_indices():
            action_set.add(
                Action(
                    id=f"sq_{idx}",
                    label="",
                    handler="_action_square_click",
                    is_enabled="_is_square_enabled",
                    is_hidden="_is_square_hidden",
                    get_label="_get_square_label",
                    show_in_actions_menu=False,
                )
            )

        # Navigation (keybind-only)
        action_set.add(
            Action(
                id="navigate_next",
                label=Localization.get(locale, "senet-next-piece"),
                handler="_action_navigate_next",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_navigate_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="navigate_prev",
                label=Localization.get(locale, "senet-previous-piece"),
                handler="_action_navigate_prev",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_navigate_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        """Create standard info actions for Senet."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        info_actions = [
            Action(
                id="check_status",
                label=Localization.get(locale, "senet-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_sticks",
                label=Localization.get(locale, "senet-check-sticks"),
                handler="_action_check_sticks",
                is_enabled="_is_info_enabled",
                is_hidden="_is_touch_info_hidden",
                include_spectators=True,
            ),
        ]
        for action in info_actions:
            action_set.add(action)

        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_status",
                    "check_sticks",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        self.define_keybind(
            "e",
            Localization.get("en", "senet-check-status"),
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "senet-check-sticks"),
            ["check_sticks"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+down",
            Localization.get("en", "senet-next-piece"),
            ["navigate_next"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+right",
            Localization.get("en", "senet-next-piece"),
            ["navigate_next"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+up",
            Localization.get("en", "senet-previous-piece"),
            ["navigate_prev"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "ctrl+left",
            Localization.get("en", "senet-previous-piece"),
            ["navigate_prev"],
            state=KeybindState.ACTIVE,
        )

    # ======================================================================
    # Grid helpers
    # ======================================================================

    def _grid_indices(self) -> list[int]:
        """Return square indices in physical grid order (3 rows x 10 cols).

        Row 1: squares 1-10  (indices 0-9, L to R)
        Row 2: squares 20-11 (indices 19-10, L to R visually = R to L on path)
        Row 3: squares 21-30 (indices 20-29, L to R)
        """
        row1 = list(range(0, 10))
        row2 = list(range(19, 9, -1))
        row3 = list(range(20, 30))
        return row1 + row2 + row3

    # ======================================================================
    # Navigation (ctrl+up/down)
    # ======================================================================

    def _action_navigate_next(self, player: Player, action_id: str) -> None:
        if isinstance(player, SenetPlayer):
            self._navigate(player, direction=1)

    def _action_navigate_prev(self, player: Player, action_id: str) -> None:
        if isinstance(player, SenetPlayer):
            self._navigate(player, direction=-1)

    def _navigate(self, player: SenetPlayer, direction: int) -> None:
        """Cycle through squares with movable pieces."""
        gs = self.game_state
        if gs.turn_phase != "moving" or gs.current_player_num != player.player_num:
            return

        targets = self._get_movable_squares(player.player_num)
        if not targets:
            return

        if self._nav_cursor is not None and self._nav_cursor in targets:
            idx = targets.index(self._nav_cursor)
            idx = (idx + direction) % len(targets)
        else:
            idx = 0 if direction == 1 else len(targets) - 1

        self._nav_cursor = targets[idx]
        self._nav_skip_rebuild = True
        self.update_player_menu(player, selection_id=f"sq_{targets[idx]}")

    def _should_rebuild_after_keybind(self, player: Player, executed_any: bool) -> bool:
        if self._nav_skip_rebuild:
            self._nav_skip_rebuild = False
            return False
        return super()._should_rebuild_after_keybind(player, executed_any)

    def _get_movable_squares(self, player_num: int) -> list[int]:
        gs = self.game_state
        sources: set[int] = set()
        for move in generate_legal_moves(gs, player_num, gs.current_roll):
            sources.add(move.source)
        return sorted(sources)

    # ======================================================================
    # Menu overrides (grid mode)
    # ======================================================================

    def rebuild_player_menu(self, player: Player, *, position: int | None = None) -> None:
        if self._destroyed or self.status == "finished":
            # Defer to base behaviour for the finished/end-screen case.
            if self.status == "finished":
                super().rebuild_player_menu(player)
            return
        if player.id in self._status_box_open or player.id in self._actions_menu_open:
            return
        user = self.get_user(player)
        if not user:
            return

        grid_items, other_items = self._build_menu_items(player, user)
        use_grid = len(grid_items) == 30

        user.show_menu(
            "turn_menu",
            grid_items + other_items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            position=position,
            grid_enabled=use_grid,
            grid_width=10 if use_grid else 1,
            grid_height=3 if use_grid else 0,
        )

    def update_player_menu(
        self,
        player: Player,
        selection_id: str | None = None,
    ) -> None:
        if self._destroyed or self.status == "finished":
            return
        if player.id in self._status_box_open or player.id in self._actions_menu_open:
            return
        user = self.get_user(player)
        if not user:
            return

        grid_items, other_items = self._build_menu_items(player, user)
        use_grid = len(grid_items) == 30

        user.update_menu(
            "turn_menu",
            grid_items + other_items,
            selection_id=selection_id,
            grid_enabled=use_grid,
            grid_width=10 if use_grid else 1,
            grid_height=3 if use_grid else 0,
        )

    def _build_menu_items(
        self, player: Player, user
    ) -> tuple[list[MenuItem], list[MenuItem]]:
        grid_items: list[MenuItem] = []
        other_items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            label = resolved.label
            item = MenuItem(text=label, id=resolved.action.id)
            if resolved.action.id.startswith("sq_"):
                grid_items.append(item)
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
        return grid_items, other_items

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        active_players = self.get_active_players()
        if len(active_players) != 2:
            self.broadcast_l(
                "senet-error-exactly-two-players",
                buffer="game",
                count=len(active_players),
            )
            return

        self.status = "playing"
        self.game_active = True
        self.round = 1

        self.set_turn_players(active_players, reset_index=True)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Assign player numbers randomly
        if random.random() < 0.5:  # nosec B311
            active_players[0].player_num = 1
            active_players[1].player_num = 2
        else:
            active_players[0].player_num = 2
            active_players[1].player_num = 1

        self.game_state = build_initial_state()

        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        first = p1  # Player 1 always goes first
        if first:
            self.current_player = first

        self.broadcast_l(
            "senet-game-started",
            buffer="game",
            p1=p1.name if p1 else "?",
            p2=p2.name if p2 else "?",
            first=first.name if first else "?",
        )

        self.play_music("game_pig/mus.ogg")
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: SenetPlayer) -> str | None:
        return bot_think(self, player)

    # ======================================================================
    # Square click handler
    # ======================================================================

    def _action_square_click(self, player: Player, action_id: str) -> None:
        if not isinstance(player, SenetPlayer):
            return
        gs = self.game_state
        if gs.current_player_num != player.player_num:
            user = self.get_user(player)
            if user:
                user.speak_l("action-not-your-turn", buffer="game")
            return

        # Throwing phase: any click throws sticks
        if gs.turn_phase == "throwing":
            self._do_throw(player)
            return

        if gs.turn_phase != "moving" or gs.current_roll <= 0:
            user = self.get_user(player)
            if user:
                user.speak_l("senet-need-throw-first", buffer="game")
            return

        try:
            sq_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return

        board = gs.board
        user = self.get_user(player)

        if board[sq_idx] == 0:
            if user:
                user.speak_l("senet-no-piece-there", buffer="game")
            return

        if board[sq_idx] != player.player_num:
            if user:
                user.speak_l("senet-not-your-piece", buffer="game")
            return

        # Auto-move: find the legal move from this square and apply it
        moves = [
            m
            for m in generate_legal_moves(gs, player.player_num, gs.current_roll)
            if m.source == sq_idx
        ]

        if not moves:
            if user:
                user.speak_l("senet-no-moves-from-here", buffer="game")
            return

        self._apply_and_announce(player, moves[0])

    # ======================================================================
    # Throwing sticks
    # ======================================================================

    def _do_throw(self, player: SenetPlayer) -> None:
        gs = self.game_state
        value, bonus = throw_sticks()
        gs.current_roll = value
        gs.bonus_turn = bonus
        gs.throws_this_turn += 1

        self._play_dice_sound()
        self.broadcast_personal_l(
            player,
            "senet-throw-you",
            "senet-throw-other",
            buffer="game",
            result=value,
            bonus="yes" if bonus else "no",
        )

        gs.turn_phase = "moving"

        if not has_any_legal_move(gs, player.player_num, value):
            self.broadcast_personal_l(
                player,
                "senet-no-moves-you",
                "senet-no-moves-other",
                buffer="game",
            )
            self._after_move_or_skip(player)
            return

        self.rebuild_all_menus()

    def _play_dice_sound(self) -> None:
        self.broadcast_sound(f"game_squares/diceroll{random.randint(1, 3)}.ogg")

    # ======================================================================
    # Move application and announcements
    # ======================================================================

    def _apply_and_announce(self, player: SenetPlayer, move) -> None:
        gs = self.game_state
        pnum = player.player_num
        opp_num = opponent_num(pnum)
        opp_player = self._get_player_by_num(opp_num)
        opp_name = opp_player.name if opp_player else "?"

        # Square numbers are 1-indexed for display
        from_sq = move.source + 1

        apply_move(gs, move, pnum)

        if move.is_bear_off:
            remaining = pieces_remaining(gs, pnum)
            self.broadcast_personal_l(
                player,
                "senet-bearoff-you",
                "senet-bearoff-other",
                buffer="game",
                **{"from": from_sq, "remaining": remaining},
            )
            self.broadcast_sound("mention.ogg", volume=50)
        elif move.is_swap:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-swap-you",
                "senet-swap-other",
                buffer="game",
                opponent=opp_name,
                **{"from": from_sq, "to": to_sq},
            )
            self.broadcast_sound("game_chess/capture1.ogg")
            if move.water_dest is not None:
                dest_sq = move.water_dest + 1
                self.broadcast_personal_l(
                    player,
                    "senet-water-you",
                    "senet-water-other",
                    buffer="game",
                    dest=dest_sq,
                )
                self.broadcast_sound("game_squares/step1.ogg")
        elif move.water_dest is not None:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-move-you",
                "senet-move-other",
                buffer="game",
                **{"from": from_sq, "to": to_sq},
            )
            dest_sq = move.water_dest + 1
            self.broadcast_personal_l(
                player,
                "senet-water-you",
                "senet-water-other",
                buffer="game",
                dest=dest_sq,
            )
            self.broadcast_sound("game_squares/step1.ogg")
        else:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-move-you",
                "senet-move-other",
                buffer="game",
                **{"from": from_sq, "to": to_sq},
            )
            self.broadcast_sound("game_squares/step1.ogg")

            # Announce reaching House of Happiness
            if move.destination == HOUSE_HAPPINESS:
                self.broadcast_personal_l(
                    player,
                    "senet-happiness-you",
                    "senet-happiness-other",
                    buffer="game",
                )

        # Check win
        if gs.off[pnum] >= PIECES_PER_PLAYER:
            self._handle_win(player)
            return

        self._after_move_or_skip(player)

    def _after_move_or_skip(self, player: SenetPlayer) -> None:
        """Handle post-move: bonus throw or switch turns."""
        gs = self.game_state

        if gs.bonus_turn:
            gs.turn_phase = "throwing"
            gs.current_roll = 0
            gs.bonus_turn = False
            self._nav_cursor = None
            if self._score_horus_if_ready(player):
                return
            BotHelper.jolt_bots(self, ticks=random.randint(3, 6))
            self.rebuild_all_menus()
        else:
            self._end_turn()

    def _score_horus_if_ready(self, player: SenetPlayer) -> bool:
        """Auto-score House of Horus when ready; return True if that ends the game."""
        gs = self.game_state
        pnum = player.player_num
        if gs.board[HOUSE_HORUS] != pnum:
            return False
        if any(square == pnum for square in gs.board[:10]):
            return False

        gs.board[HOUSE_HORUS] = 0
        gs.off[pnum] += 1
        remaining = pieces_remaining(gs, pnum)
        self.broadcast_personal_l(
            player,
            "senet-horus-auto-you",
            "senet-horus-auto-other",
            buffer="game",
            remaining=remaining,
        )
        self.broadcast_sound("mention.ogg", volume=50)
        if gs.off[pnum] >= PIECES_PER_PLAYER:
            self._handle_win(player)
            return True
        return False

    def _end_turn(self) -> None:
        gs = self.game_state
        opp = opponent_num(gs.current_player_num)
        gs.current_player_num = opp
        gs.turn_phase = "throwing"
        gs.current_roll = 0
        gs.bonus_turn = False
        gs.throws_this_turn = 0
        self._nav_cursor = None

        opp_player = self._get_player_by_num(opp)
        if opp_player:
            self.current_player = opp_player
        self.announce_turn()
        if opp_player and self._score_horus_if_ready(opp_player):
            return
        BotHelper.jolt_bots(self, ticks=random.randint(3, 6))
        self.rebuild_all_menus()

    # ======================================================================
    # Win
    # ======================================================================

    def _handle_win(self, winner: SenetPlayer) -> None:
        self.broadcast_personal_l(
            winner,
            "senet-wins-you",
            "senet-wins-other",
            buffer="game",
        )
        self.broadcast_sound("game_pig/win.ogg")
        self.winner_name = winner.name
        self.finish_game()

    def build_game_result(self) -> GameResult:
        from datetime import datetime

        gs = self.game_state
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": self.winner_name,
                "p1_name": p1.name if p1 else "?",
                "p2_name": p2.name if p2 else "?",
                "p1_off": gs.off[1],
                "p2_off": gs.off[2],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        d = result.custom_data
        return [
            Localization.get(
                locale,
                "senet-score",
                p1=d.get("p1_name", "?"),
                off1=d.get("p1_off", 0),
                p2=d.get("p2_name", "?"),
                off2=d.get("p2_off", 0),
            )
        ]

    # ======================================================================
    # Info actions
    # ======================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        user.speak_l(
            "senet-status",
            buffer="game",
            p1=p1.name if p1 else "?",
            off1=gs.off[1],
            p2=p2.name if p2 else "?",
            off2=gs.off[2],
            phase=gs.turn_phase,
            roll=gs.current_roll,
        )

    def _action_check_sticks(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        if gs.current_roll > 0:
            user.speak_l("senet-sticks", buffer="game", result=gs.current_roll)
        else:
            user.speak_l("senet-sticks-none", buffer="game")

    def _score_kwargs(self) -> dict:
        gs = self.game_state
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        return {
            "p1": p1.name if p1 else "?",
            "off1": gs.off[1],
            "p2": p2.name if p2 else "?",
            "off2": gs.off[2],
        }

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("senet-score", buffer="game", **self._score_kwargs())

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.status_box(
            player,
            [
                Localization.get(
                    user.locale,
                    "senet-score",
                    **self._score_kwargs(),
                )
            ],
        )

    # ======================================================================
    # Score actions: Senet uses standard score action IDs with custom output.
    # ======================================================================

    def supports_score_actions(self) -> bool:
        return False

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        return self._is_info_enabled(player)

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        return self._is_info_enabled(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    # ======================================================================
    # Leave handling
    # ======================================================================

    def _perform_leave_game(self, player: Player) -> None:
        super()._perform_leave_game(player)

    # ======================================================================
    # Visibility / enabled / label callbacks
    # ======================================================================

    def _is_square_enabled(self, player: Player, action_id: str) -> str | None:
        # Squares are always enabled so the full 3x10 grid renders; the actual
        # turn/phase/ownership checks happen inside the click handler.
        return None

    def _is_square_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_square_label(self, player: Player, action_id: str) -> str:
        try:
            sq_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return ""

        gs = self.game_state
        locale = self._player_locale(player)
        sq_num = sq_idx + 1
        occupant = gs.board[sq_idx]
        special_key = SPECIAL_SQUARE_NAMES.get(sq_idx)

        if special_key:
            special_name = Localization.get(locale, special_key)
            if occupant == 0:
                return Localization.get(locale, "senet-sq-empty-special", sq=sq_num, name=special_name)
            elif isinstance(player, SenetPlayer) and occupant == player.player_num:
                return Localization.get(locale, "senet-sq-own-special", sq=sq_num, name=special_name)
            else:
                owner = self._get_player_by_num(occupant)
                return Localization.get(
                    locale, "senet-sq-opponent-special",
                    sq=sq_num, name=special_name, owner=owner.name if owner else "?",
                )
        else:
            if occupant == 0:
                return Localization.get(locale, "senet-sq-empty", sq=sq_num)
            elif isinstance(player, SenetPlayer) and occupant == player.player_num:
                return Localization.get(locale, "senet-sq-own", sq=sq_num)
            else:
                owner = self._get_player_by_num(occupant)
                return Localization.get(
                    locale, "senet-sq-opponent", sq=sq_num, owner=owner.name if owner else "?",
                )

    def _is_navigate_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, SenetPlayer) or player.is_spectator:
            return "action-not-available"
        gs = self.game_state
        if gs.current_player_num != player.player_num:
            return "action-not-your-turn"
        if gs.turn_phase == "throwing" or gs.current_roll <= 0:
            return "senet-need-throw-first"
        if gs.turn_phase != "moving":
            return "action-not-available"
        if not self._get_movable_squares(player.player_num):
            return "senet-no-movable-pieces"
        return None

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_navigate_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self._is_navigate_enabled(player) is None and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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
