"""Five Field Kono game for PlayAural."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.grid_mixin import GridCursor, GridGameMixin, grid_cell_id
from ...messages.localization import Localization
from .bot import bot_think
from .moves import (
    Move,
    apply_move,
    has_any_legal_move,
    is_winner,
    legal_destinations,
)
from .state import (
    PIECES_PER_PLAYER,
    TARGET_CELLS,
    FiveFieldKonoState,
    build_initial_state,
    cell_index,
    cell_rowcol,
    opponent_num,
    player_piece_cells,
)


SOUND_PICKUP = "game_chess/pickup.ogg"
SOUND_SETDOWN = "game_chess/setdown.ogg"
SOUND_MOVE = "game_squares/step1.ogg"
SOUND_TURN = "game_squares/begin turn.ogg"
SOUND_WIN = "game_pig/win.ogg"


@dataclass
class FiveFieldKonoOptions(GameOptions):
    pass


@dataclass
class FiveFieldKonoPlayer(Player):
    player_num: int = 0  # 1 or 2


@register_game
@dataclass
class FiveFieldKonoGame(GridGameMixin, Game):
    """Five Field Kono — 5x5 diagonal race."""

    relevant_preferences = ["brief_announcements"]

    players: list[FiveFieldKonoPlayer] = field(default_factory=list)
    options: FiveFieldKonoOptions = field(default_factory=FiveFieldKonoOptions)
    state: FiveFieldKonoState = field(default_factory=FiveFieldKonoState)

    selected_square: dict[str, int] = field(default_factory=dict)
    bot_move_targets: dict[str, int] = field(default_factory=dict)
    last_move: list[int] = field(default_factory=list)
    winner_num: int = 0
    win_reason: str = ""  # "" | "completed" | "stuck"
    winner_name: str | None = None

    grid_rows: int = 5
    grid_cols: int = 5
    grid_row_labels: list[str] = field(
        default_factory=lambda: ["1", "2", "3", "4", "5"]
    )
    grid_col_labels: list[str] = field(default_factory=lambda: list("ABCDE"))
    grid_cursors: dict[str, GridCursor] = field(default_factory=dict)

    # ---- metadata ----
    @classmethod
    def get_name(cls) -> str:
        return "Five Field Kono"

    @classmethod
    def get_type(cls) -> str:
        return "fivefieldkono"

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

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> FiveFieldKonoPlayer:
        return FiveFieldKonoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ---- helpers ----
    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_player_by_num(self, num: int) -> FiveFieldKonoPlayer | None:
        for p in self.get_active_players():
            if isinstance(p, FiveFieldKonoPlayer) and p.player_num == num:
                return p
        return None

    def _as_kono_player(self, player: Player) -> FiveFieldKonoPlayer | None:
        return player if isinstance(player, FiveFieldKonoPlayer) else None

    def _coord(self, index: int) -> str:
        row, col = cell_rowcol(index)
        return self._grid_cell_coordinate(row, col)

    # ---- lifecycle ----
    def on_start(self) -> None:
        active = self.get_active_players()
        if len(active) != 2:
            return
        self.status = "playing"
        self.game_active = True
        self.round = 1
        self._init_grid()

        if random.random() < 0.5:  # nosec B311
            active[0].player_num, active[1].player_num = 1, 2
        else:
            active[0].player_num, active[1].player_num = 2, 1

        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        self.state = build_initial_state(p1.id, p2.id)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])

        self.set_turn_players([p1, p2], reset_index=True)
        self.current_player = p1
        self.state.current_player_num = 1

        self.broadcast_l(
            "ffk-game-started",
            buffer="game",
            p1=p1.name,
            p2=p2.name,
            first=p1.name,
        )
        self.refresh_menus()
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: FiveFieldKonoPlayer) -> str | None:
        return bot_think(self, player)

    # ---- grid rendering ----
    def get_cell_label(self, row: int, col: int, player: Player, locale: str) -> str:
        index = cell_index(row, col)
        coord = self._grid_cell_coordinate(row, col)
        piece = self.state.board[index]
        kp = self._as_kono_player(player)
        selected = self.selected_square.get(player.id) if kp else None

        if piece is None:
            label = Localization.get(locale, "ffk-cell-empty", coord=coord)
        elif kp and piece.owner_id == player.id:
            label = Localization.get(locale, "ffk-cell-own", coord=coord)
        else:
            owner = self._get_player_by_num(piece.owner_num)
            label = Localization.get(
                locale,
                "ffk-cell-opponent",
                coord=coord,
                owner=owner.name if owner else "?",
            )

        if selected == index:
            return Localization.get(locale, "ffk-cell-selected", label=label)
        if (
            kp
            and self.current_player is not None
            and player.id == self.current_player.id
            and selected is not None
            and piece is None
            and index in legal_destinations(self.state.board, selected, kp.player_num)
        ):
            return Localization.get(locale, "ffk-cell-move-target", coord=coord)
        return label

    def is_grid_cell_enabled(self, player: Player, row: int, col: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def is_grid_cell_hidden(self, player: Player, row: int, col: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # ---- interaction ----
    def on_grid_select(self, player: Player, row: int, col: int) -> None:
        if self.status != "playing":
            return
        kp = self._as_kono_player(player)
        index = cell_index(row, col)
        if (
            kp
            and not kp.is_spectator
            and self.winner_num == 0
            and self.current_player is not None
            and player.id == self.current_player.id
            and self.state.current_player_num == kp.player_num
        ):
            self._handle_select(kp, index)
            return
        self._announce_cell(player, index)

    def _announce_cell(self, player: Player, index: int) -> None:
        user = self.get_user(player)
        if not user:
            return
        piece = self.state.board[index]
        coord = self._coord(index)
        if piece is None:
            user.speak_l("ffk-cell-empty", buffer="game", coord=coord)
        elif piece.owner_id == player.id:
            user.speak_l("ffk-cell-own", buffer="game", coord=coord)
        else:
            owner = self._get_player_by_num(piece.owner_num)
            user.speak_l(
                "ffk-cell-opponent",
                buffer="game",
                coord=coord,
                owner=owner.name if owner else "?",
            )

    def _handle_select(self, player: FiveFieldKonoPlayer, index: int) -> None:
        user = self.get_user(player)
        if not user:
            return
        piece = self.state.board[index]
        selected = self.selected_square.get(player.id)

        # Clicking the already-selected piece clears the selection.
        if selected is not None and selected == index:
            self.selected_square.pop(player.id, None)
            user.play_sound(SOUND_SETDOWN)
            user.speak_l("ffk-selection-cleared", buffer="game")
            self.refresh_menus(player)
            return

        # Select a piece, or switch the selection to another own piece.
        if selected is None or (piece is not None and piece.owner_id == player.id):
            if piece is None or piece.owner_id != player.id:
                user.speak_l("ffk-select-own-piece", buffer="game")
                return
            dests = legal_destinations(self.state.board, index, player.player_num)
            if not dests:
                user.speak_l("ffk-piece-no-moves", buffer="game")
                return
            self.selected_square[player.id] = index
            user.play_sound(SOUND_PICKUP)
            user.speak_l(
                "ffk-piece-selected",
                buffer="game",
                coord=self._coord(index),
                count=len(dests),
            )
            row, col = cell_rowcol(index)
            self.request_menu_focus(player, grid_cell_id(row, col))
            self.refresh_menus(player)
            return

        if index not in legal_destinations(
            self.state.board, selected, player.player_num
        ):
            user.play_sound(SOUND_SETDOWN)
            user.speak_l("ffk-illegal-move", buffer="game")
            self.refresh_menus(player)
            return

        self._commit_move(player, Move(source=selected, destination=index))

    def _commit_move(self, player: FiveFieldKonoPlayer, move: Move) -> None:
        from_coord = self._coord(move.source)
        to_coord = self._coord(move.destination)
        self.last_move = [move.source, move.destination]
        apply_move(self.state, move)
        self.selected_square.pop(player.id, None)
        self.bot_move_targets.pop(player.id, None)
        self.broadcast_sound(SOUND_MOVE)
        self.broadcast_personal_l(
            player,
            "ffk-move-you",
            "ffk-move-other",
            buffer="game",
            **{"from": from_coord, "to": to_coord},
        )
        if is_winner(self.state, player.player_num):
            self.win_reason = "completed"
            self._handle_win(player)
            return
        self._end_turn(player)

    def _end_turn(self, mover: FiveFieldKonoPlayer) -> None:
        opp_num = opponent_num(mover.player_num)
        opp = self._get_player_by_num(opp_num)
        self.state.current_player_num = opp_num
        if opp:
            self.current_player = opp
        # Stuck rule: opponent with no legal move at turn start loses.
        if not has_any_legal_move(self.state, opp_num):
            self.win_reason = "stuck"
            self._handle_win(mover)
            return
        self.announce_turn(turn_sound=SOUND_TURN)
        self.refresh_menus()
        BotHelper.jolt_bots(self, ticks=random.randint(3, 6))

    def _handle_win(self, winner: FiveFieldKonoPlayer) -> None:
        self.winner_num = winner.player_num
        self.winner_name = winner.name
        if self.win_reason == "stuck":
            self.broadcast_personal_l(
                winner,
                "ffk-win-stuck-you",
                "ffk-win-stuck-other",
                buffer="game",
            )
        else:
            self.broadcast_personal_l(
                winner,
                "ffk-win-you",
                "ffk-win-other",
                buffer="game",
            )
        self.broadcast_sound(SOUND_WIN)
        self.finish_game()
