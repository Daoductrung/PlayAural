"""Chess for PlayAural."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.grid_mixin import GridCursor, GridGameMixin, grid_cell_id
from ...game_utils.options import BoolOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_think as _bot_think

if TYPE_CHECKING:
    from ...users.base import User


COLOR_WHITE = "white"
COLOR_BLACK = "black"
PIECE_TYPES = ("pawn", "knight", "bishop", "rook", "queen", "king")

MUSIC_PATH = "game_coup/music.ogg"
SOUND_TURN = "game_squares/begin turn.ogg"
SOUND_CAPTURE = "game_chess/capture{index}.ogg"
SOUND_PAWN = "game_chess/movepawn{index}.ogg"
SOUND_KNIGHT = "game_chess/moveknight.ogg"
SOUND_BISHOP = "game_chess/movebishop.ogg"
SOUND_ROOK = "game_chess/moverook.ogg"
SOUND_QUEEN = "game_chess/movequeen.ogg"
SOUND_KING = "game_chess/moveking.ogg"
SOUND_PICKUP = "game_chess/pickup.ogg"
SOUND_SETDOWN = "game_chess/setdown.ogg"
TICKS_PER_SECOND = 20
TIME_CONTROL_CHOICES = [
    "untimed",
    "bullet_1_0",
    "bullet_2_1",
    "blitz_3_0",
    "blitz_3_2",
    "blitz_5_0",
    "rapid_10_0",
    "rapid_10_5",
    "classical_30_0",
]
TIME_CONTROL_LABELS = {
    "untimed": "chess-time-untimed",
    "bullet_1_0": "chess-time-bullet-1-0",
    "bullet_2_1": "chess-time-bullet-2-1",
    "blitz_3_0": "chess-time-blitz-3-0",
    "blitz_3_2": "chess-time-blitz-3-2",
    "blitz_5_0": "chess-time-blitz-5-0",
    "rapid_10_0": "chess-time-rapid-10-0",
    "rapid_10_5": "chess-time-rapid-10-5",
    "classical_30_0": "chess-time-classical-30-0",
}
TIME_CONTROL_SETTINGS = {
    "untimed": (0, 0),
    "bullet_1_0": (60, 0),
    "bullet_2_1": (120, 1),
    "blitz_3_0": (180, 0),
    "blitz_3_2": (180, 2),
    "blitz_5_0": (300, 0),
    "rapid_10_0": (600, 0),
    "rapid_10_5": (600, 5),
    "classical_30_0": (1800, 0),
}
DRAW_HANDLING_CHOICES = ["automatic", "claim_required"]
DRAW_HANDLING_LABELS = {
    "automatic": "chess-draw-handling-automatic",
    "claim_required": "chess-draw-handling-claim-required",
}


def index_to_notation(index: int) -> str:
    file_name = "abcdefgh"[index % 8]
    rank_name = str(index // 8 + 1)
    return f"{file_name}{rank_name}"


def notation_to_index(value: str) -> int | None:
    if len(value) != 2:
        return None
    file_name = value[0].lower()
    rank_name = value[1]
    if file_name not in "abcdefgh" or rank_name not in "12345678":
        return None
    return (int(rank_name) - 1) * 8 + "abcdefgh".index(file_name)


@dataclass
class ChessPiece(DataClassJSONMixin):
    kind: str
    color: str
    has_moved: bool = False


@dataclass
class ChessMoveRecord(DataClassJSONMixin):
    from_square: int
    to_square: int
    color: str
    piece: str
    captured: str = ""
    captured_color: str = ""
    promotion: str = ""
    special: str = ""


@dataclass
class ChessUndoSnapshot(DataClassJSONMixin):
    board: list[ChessPiece | None]
    current_color: str
    halfmove_clock: int
    en_passant_target: int
    castle_white_kingside: bool
    castle_white_queenside: bool
    castle_black_kingside: bool
    castle_black_queenside: bool
    move_history: list[ChessMoveRecord]
    position_history: list[str]
    white_clock_ticks: int
    black_clock_ticks: int
    promotion_pending: bool = False
    promotion_player_id: str = ""
    promotion_square: int = -1
    pending_promotion_from: int = -1
    pending_promotion_capture: str = ""
    pending_promotion_capture_color: str = ""
    pending_promotion_special: str = ""


@dataclass
class ChessPlayer(Player):
    color: str = ""


@dataclass
class ChessOptions(GameOptions):
    time_control: str = option_field(
        MenuOption(
            default="untimed",
            choices=TIME_CONTROL_CHOICES,
            value_key="control",
            label="chess-set-time-control",
            prompt="chess-select-time-control",
            change_msg="chess-option-changed-time-control",
            choice_labels=TIME_CONTROL_LABELS,
        )
    )
    draw_handling: str = option_field(
        MenuOption(
            default="automatic",
            choices=DRAW_HANDLING_CHOICES,
            value_key="mode",
            label="chess-set-draw-handling",
            prompt="chess-select-draw-handling",
            change_msg="chess-option-changed-draw-handling",
            choice_labels=DRAW_HANDLING_LABELS,
        )
    )
    allow_draw_offers: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="chess-toggle-draw-offers",
            change_msg="chess-option-changed-draw-offers",
        )
    )
    allow_undo_requests: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="chess-toggle-undo-requests",
            change_msg="chess-option-changed-undo-requests",
        )
    )


@register_game
@dataclass
class ChessGame(GridGameMixin, Game):
    players: list[ChessPlayer] = field(default_factory=list)
    options: ChessOptions = field(default_factory=ChessOptions)

    board: list[ChessPiece | None] = field(default_factory=lambda: [None] * 64)
    current_color: str = COLOR_WHITE
    winner_color: str = ""
    draw_reason: str = ""
    selected_square: dict[str, int] = field(default_factory=dict)
    board_flipped: dict[str, bool] = field(default_factory=dict)
    move_history: list[ChessMoveRecord] = field(default_factory=list)
    position_history: list[str] = field(default_factory=list)
    halfmove_clock: int = 0
    en_passant_target: int = -1
    castle_white_kingside: bool = True
    castle_white_queenside: bool = True
    castle_black_kingside: bool = True
    castle_black_queenside: bool = True

    promotion_pending: bool = False
    promotion_player_id: str = ""
    promotion_square: int = -1
    pending_promotion_from: int = -1
    pending_promotion_capture: str = ""
    pending_promotion_capture_color: str = ""
    pending_promotion_special: str = ""

    bot_move_targets: dict[str, int] = field(default_factory=dict)
    draw_offer_from: str = ""
    undo_request_from: str = ""
    white_clock_ticks: int = 0
    black_clock_ticks: int = 0
    clock_increment_ticks: int = 0
    undo_history: list[ChessUndoSnapshot] = field(default_factory=list)
    pending_undo_snapshot: ChessUndoSnapshot | None = None

    grid_rows: int = 8
    grid_cols: int = 8
    grid_row_labels: list[str] = field(
        default_factory=lambda: ["8", "7", "6", "5", "4", "3", "2", "1"]
    )
    grid_col_labels: list[str] = field(default_factory=lambda: list("ABCDEFGH"))
    grid_cursors: dict[str, GridCursor] = field(default_factory=dict)

    @classmethod
    def get_name(cls) -> str:
        return "Chess"

    @classmethod
    def get_type(cls) -> str:
        return "chess"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ChessPlayer:
        return ChessPlayer(id=player_id, name=name, is_bot=is_bot)

    def create_turn_action_set(self, player: ChessPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        for piece_type in ("queen", "rook", "bishop", "knight"):
            action_set.add(
                Action(
                    id=f"promote_{piece_type}",
                    label=Localization.get(locale, f"chess-promote-{piece_type}"),
                    handler="_action_promote",
                    is_enabled="_is_promote_enabled",
                    is_hidden="_is_promote_hidden",
                    show_in_actions_menu=False,
                )
            )

        for action in self.build_grid_actions(player):
            action_set.add(action)
        for action in self.build_grid_nav_actions():
            action_set.add(action)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="read_board",
                label=Localization.get(locale, "chess-read-board"),
                handler="_action_read_board",
                is_enabled="_is_info_enabled",
                is_hidden="_is_read_board_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "chess-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="flip_board",
                label=Localization.get(locale, "chess-flip-board"),
                handler="_action_flip_board",
                is_enabled="_is_info_enabled",
                is_hidden="_is_flip_board_hidden",
                include_spectators=False,
            )
        )
        action_set.add(
            Action(
                id="check_clock",
                label=Localization.get(locale, "chess-check-clock"),
                handler="_action_check_clock",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_clock_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="claim_draw",
                label=Localization.get(locale, "chess-claim-draw"),
                handler="_action_claim_draw",
                is_enabled="_is_claim_draw_enabled",
                is_hidden="_is_claim_draw_hidden",
            )
        )
        action_set.add(
            Action(
                id="offer_draw",
                label=Localization.get(locale, "chess-offer-draw"),
                handler="_action_offer_draw",
                is_enabled="_is_offer_draw_enabled",
                is_hidden="_is_offer_draw_hidden",
            )
        )
        action_set.add(
            Action(
                id="accept_draw",
                label=Localization.get(locale, "chess-accept-draw"),
                handler="_action_accept_draw",
                is_enabled="_is_draw_response_enabled",
                is_hidden="_is_draw_response_hidden",
            )
        )
        action_set.add(
            Action(
                id="decline_draw",
                label=Localization.get(locale, "chess-decline-draw"),
                handler="_action_decline_draw",
                is_enabled="_is_draw_response_enabled",
                is_hidden="_is_draw_response_hidden",
            )
        )
        action_set.add(
            Action(
                id="request_undo",
                label=Localization.get(locale, "chess-request-undo"),
                handler="_action_request_undo",
                is_enabled="_is_request_undo_enabled",
                is_hidden="_is_request_undo_hidden",
            )
        )
        action_set.add(
            Action(
                id="accept_undo",
                label=Localization.get(locale, "chess-accept-undo"),
                handler="_action_accept_undo",
                is_enabled="_is_undo_response_enabled",
                is_hidden="_is_undo_response_hidden",
            )
        )
        action_set.add(
            Action(
                id="decline_undo",
                label=Localization.get(locale, "chess-decline-undo"),
                handler="_action_decline_undo",
                is_enabled="_is_undo_response_enabled",
                is_hidden="_is_undo_response_hidden",
            )
        )
        self._apply_standard_action_order(action_set, user)
        return action_set

    def _apply_standard_action_order(self, action_set: ActionSet, user: "User | None") -> None:
        custom_ids = [
            "read_board",
            "check_status",
            "flip_board",
            "check_clock",
            "claim_draw",
            "offer_draw",
            "request_undo",
            "accept_draw",
            "decline_draw",
            "accept_undo",
            "decline_undo",
        ]
        action_set._order = [
            aid for aid in action_set._order if aid not in custom_ids
        ] + [aid for aid in custom_ids if action_set.get_action(aid)]
        if self.is_touch_client(user):
            target_order = [
                "read_board",
                "check_status",
                "flip_board",
                "check_clock",
                "claim_draw",
                "offer_draw",
                "request_undo",
                "accept_draw",
                "decline_draw",
                "accept_undo",
                "decline_undo",
                "whose_turn",
                "whos_at_table",
            ]
            action_set._order = [
                aid for aid in action_set._order if aid not in target_order
            ] + [aid for aid in target_order if action_set.get_action(aid)]

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.setup_grid_keybinds()
        self.define_keybind(
            "v",
            "Read board",
            ["read_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "f",
            "Flip board",
            ["flip_board"],
            state=KeybindState.ACTIVE,
            include_spectators=False,
        )
        self.define_keybind(
            "shift+t",
            "Check clock",
            ["check_clock"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+d",
            "Offer draw",
            ["offer_draw"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "shift+u",
            "Request undo",
            ["request_undo"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "shift+c",
            "Claim draw",
            ["claim_draw"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "y",
            "Accept draw or undo",
            ["accept_draw", "accept_undo"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "n",
            "Decline draw or undo",
            ["decline_draw", "decline_undo"],
            state=KeybindState.ACTIVE,
        )

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_standard_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_standard_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_standard_actions(player)
        super().rebuild_all_menus()

    def _sync_standard_actions(self, player: Player) -> None:
        action_set = self.get_action_set(player, "standard")
        if action_set:
            self._apply_standard_action_order(action_set, self.get_user(player))

    def on_start(self) -> None:
        active_players = self.get_active_players()
        white_player = self._as_chess_player(active_players[0]) if active_players else None
        black_player = self._as_chess_player(active_players[1]) if len(active_players) > 1 else None
        if not white_player or not black_player:
            return

        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1
        self._init_grid()
        self._init_board()

        white_player.color = COLOR_WHITE
        black_player.color = COLOR_BLACK
        self.board_flipped = {
            white_player.id: False,
            black_player.id: True,
        }

        self.play_music(MUSIC_PATH)
        self._init_clocks()
        self.set_turn_players([white_player, black_player])
        self.current_player = white_player
        self.current_color = COLOR_WHITE
        self.broadcast_l(
            "chess-game-started",
            buffer="game",
            white=white_player.name,
            black=black_player.name,
        )
        self.announce_turn(turn_sound=SOUND_TURN)
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if self.status != "playing":
            return
        if self._tick_clock():
            return
        responder = self._get_pending_response_player()
        if responder and responder.is_bot:
            BotHelper.process_bot_action(
                responder,
                lambda: self.bot_think(responder),
                lambda action_id: self.execute_action(responder, action_id),
            )
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: ChessPlayer) -> str | None:
        return _bot_think(self, player)

    def _init_clocks(self) -> None:
        base_seconds, increment_seconds = TIME_CONTROL_SETTINGS.get(
            self.options.time_control,
            TIME_CONTROL_SETTINGS["untimed"],
        )
        self.white_clock_ticks = base_seconds * TICKS_PER_SECOND
        self.black_clock_ticks = base_seconds * TICKS_PER_SECOND
        self.clock_increment_ticks = increment_seconds * TICKS_PER_SECOND

    def _has_clock(self) -> bool:
        return self.white_clock_ticks > 0 or self.black_clock_ticks > 0

    def _clock_ticks_for_color(self, color: str) -> int:
        return self.white_clock_ticks if color == COLOR_WHITE else self.black_clock_ticks

    def _set_clock_ticks_for_color(self, color: str, ticks: int) -> None:
        if color == COLOR_WHITE:
            self.white_clock_ticks = max(0, ticks)
        else:
            self.black_clock_ticks = max(0, ticks)

    def _add_increment(self, color: str) -> None:
        if self.clock_increment_ticks <= 0:
            return
        self._set_clock_ticks_for_color(
            color,
            self._clock_ticks_for_color(color) + self.clock_increment_ticks,
        )

    def _tick_clock(self) -> bool:
        if not self._has_clock() or self.promotion_pending or self._has_pending_response():
            return False
        current = self._as_chess_player(self.current_player)
        if current is None:
            return False
        remaining = self._clock_ticks_for_color(current.color) - 1
        self._set_clock_ticks_for_color(current.color, remaining)
        if remaining <= 0:
            self._handle_time_expiry(current)
            return True
        return False

    def _has_pending_response(self) -> bool:
        return bool(self.draw_offer_from or self.undo_request_from)

    def _get_pending_response_player(self) -> ChessPlayer | None:
        requester_id = self.draw_offer_from or self.undo_request_from
        if not requester_id:
            return None
        requester = self.get_player_by_id(requester_id)
        requester_color = getattr(requester, "color", "")
        if not requester_color:
            return None
        responder_color = COLOR_BLACK if requester_color == COLOR_WHITE else COLOR_WHITE
        return self._get_player_by_color(responder_color)

    def _format_clock_value(self, ticks: int) -> str:
        total_seconds = (max(0, ticks) + TICKS_PER_SECOND - 1) // TICKS_PER_SECOND
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def _get_clock_label(self, locale: str, color: str) -> str:
        time_text = self._format_clock_value(self._clock_ticks_for_color(color))
        if not self._has_clock():
            time_text = Localization.get(locale, "chess-clock-untimed")
        return Localization.get(
            locale,
            "chess-clock-line",
            color=Localization.get(locale, f"chess-color-{color}"),
            time=time_text,
        )

    def _handle_time_expiry(self, player: ChessPlayer) -> None:
        opponent_color = COLOR_BLACK if player.color == COLOR_WHITE else COLOR_WHITE
        opponent = self._get_player_by_color(opponent_color)
        if self._has_mating_material(opponent_color):
            self.winner_color = opponent_color
            self.broadcast_l(
                "chess-timeout-loss",
                buffer="game",
                player=player.name,
                winner=opponent.name if opponent else "?",
            )
        else:
            self.draw_reason = "timeout_insufficient_material"
            self.broadcast_l("chess-draw-timeout-insufficient", buffer="game")
        self.finish_game()

    def _has_mating_material(self, color: str) -> bool:
        bishops = 0
        knights = 0
        for piece in self.board:
            if piece is None or piece.color != color:
                continue
            if piece.kind in {"pawn", "rook", "queen"}:
                return True
            if piece.kind == "bishop":
                bishops += 1
            elif piece.kind == "knight":
                knights += 1
        if bishops >= 2 or knights >= 2:
            return True
        if bishops >= 1 and knights >= 1:
            return True
        return False

    def _queue_bot_turn(self) -> None:
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(10, 22))

    def _init_board(self) -> None:
        self.board = [None] * 64
        self.selected_square.clear()
        self.bot_move_targets.clear()
        back_rank = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for file_index, piece_type in enumerate(back_rank):
            self.board[file_index] = ChessPiece(piece_type, COLOR_WHITE, has_moved=False)
            self.board[56 + file_index] = ChessPiece(piece_type, COLOR_BLACK, has_moved=False)
        for square in range(8, 16):
            self.board[square] = ChessPiece("pawn", COLOR_WHITE, has_moved=False)
        for square in range(48, 56):
            self.board[square] = ChessPiece("pawn", COLOR_BLACK, has_moved=False)

        self.winner_color = ""
        self.draw_reason = ""
        self.current_color = COLOR_WHITE
        self.halfmove_clock = 0
        self.en_passant_target = -1
        self.castle_white_kingside = True
        self.castle_white_queenside = True
        self.castle_black_kingside = True
        self.castle_black_queenside = True
        self.promotion_pending = False
        self.promotion_player_id = ""
        self.promotion_square = -1
        self.pending_promotion_from = -1
        self.pending_promotion_capture = ""
        self.pending_promotion_capture_color = ""
        self.pending_promotion_special = ""
        self.move_history = []
        self.position_history = [self._get_position_hash()]
        self.draw_offer_from = ""
        self.undo_request_from = ""
        self.undo_history = []
        self.pending_undo_snapshot = None

    def _clone_piece(self, piece: ChessPiece | None) -> ChessPiece | None:
        if piece is None:
            return None
        return ChessPiece(piece.kind, piece.color, piece.has_moved)

    def save_position(self) -> dict:
        return {
            "board": [self._clone_piece(piece) for piece in self.board],
            "current_color": self.current_color,
            "halfmove_clock": self.halfmove_clock,
            "en_passant_target": self.en_passant_target,
            "castle_white_kingside": self.castle_white_kingside,
            "castle_white_queenside": self.castle_white_queenside,
            "castle_black_kingside": self.castle_black_kingside,
            "castle_black_queenside": self.castle_black_queenside,
        }

    def restore_position(self, saved: dict) -> None:
        self.board = [self._clone_piece(piece) for piece in saved["board"]]
        self.current_color = saved["current_color"]
        self.halfmove_clock = saved["halfmove_clock"]
        self.en_passant_target = saved["en_passant_target"]
        self.castle_white_kingside = saved["castle_white_kingside"]
        self.castle_white_queenside = saved["castle_white_queenside"]
        self.castle_black_kingside = saved["castle_black_kingside"]
        self.castle_black_queenside = saved["castle_black_queenside"]

    def _make_undo_snapshot(self) -> ChessUndoSnapshot:
        return ChessUndoSnapshot(
            board=[self._clone_piece(piece) for piece in self.board],
            current_color=self.current_color,
            halfmove_clock=self.halfmove_clock,
            en_passant_target=self.en_passant_target,
            castle_white_kingside=self.castle_white_kingside,
            castle_white_queenside=self.castle_white_queenside,
            castle_black_kingside=self.castle_black_kingside,
            castle_black_queenside=self.castle_black_queenside,
            move_history=[ChessMoveRecord(**record.to_dict()) for record in self.move_history],
            position_history=list(self.position_history),
            white_clock_ticks=self.white_clock_ticks,
            black_clock_ticks=self.black_clock_ticks,
            promotion_pending=self.promotion_pending,
            promotion_player_id=self.promotion_player_id,
            promotion_square=self.promotion_square,
            pending_promotion_from=self.pending_promotion_from,
            pending_promotion_capture=self.pending_promotion_capture,
            pending_promotion_capture_color=self.pending_promotion_capture_color,
            pending_promotion_special=self.pending_promotion_special,
        )

    def _restore_undo_snapshot(self, snapshot: ChessUndoSnapshot) -> None:
        self.board = [self._clone_piece(piece) for piece in snapshot.board]
        self.current_color = snapshot.current_color
        self.halfmove_clock = snapshot.halfmove_clock
        self.en_passant_target = snapshot.en_passant_target
        self.castle_white_kingside = snapshot.castle_white_kingside
        self.castle_white_queenside = snapshot.castle_white_queenside
        self.castle_black_kingside = snapshot.castle_black_kingside
        self.castle_black_queenside = snapshot.castle_black_queenside
        self.move_history = [ChessMoveRecord(**record.to_dict()) for record in snapshot.move_history]
        self.position_history = list(snapshot.position_history)
        self.white_clock_ticks = snapshot.white_clock_ticks
        self.black_clock_ticks = snapshot.black_clock_ticks
        self.promotion_pending = snapshot.promotion_pending
        self.promotion_player_id = snapshot.promotion_player_id
        self.promotion_square = snapshot.promotion_square
        self.pending_promotion_from = snapshot.pending_promotion_from
        self.pending_promotion_capture = snapshot.pending_promotion_capture
        self.pending_promotion_capture_color = snapshot.pending_promotion_capture_color
        self.pending_promotion_special = snapshot.pending_promotion_special
        self.selected_square.clear()
        self.bot_move_targets.clear()
        self.draw_offer_from = ""
        self.undo_request_from = ""
        self.pending_undo_snapshot = None
        player = self._get_player_by_color(self.current_color)
        if player and player.id in self.turn_player_ids:
            self.turn_index = self.turn_player_ids.index(player.id)

    def _piece_name(self, piece: ChessPiece, locale: str) -> str:
        color = Localization.get(locale, f"chess-color-{piece.color}")
        kind = Localization.get(locale, f"chess-piece-{piece.kind}")
        return f"{color} {kind}"

    def _piece_on_square(self, square: int) -> ChessPiece | None:
        if 0 <= square < len(self.board):
            return self.board[square]
        return None

    def _as_chess_player(self, player: Player | None) -> ChessPlayer | None:
        if isinstance(player, ChessPlayer):
            return player
        return None

    def _get_player_by_color(self, color: str) -> ChessPlayer | None:
        for player in self.get_active_players():
            chess_player = self._as_chess_player(player)
            if chess_player and chess_player.color == color:
                return chess_player
        return None

    def square_to_view(self, player: ChessPlayer | Player, square: int) -> tuple[int, int]:
        flipped = self.board_flipped.get(player.id, False)
        file_index = square % 8
        rank_index = square // 8
        if flipped:
            return rank_index, 7 - file_index
        return 7 - rank_index, file_index

    def _view_to_square(self, player: ChessPlayer | Player, row: int, col: int) -> int:
        flipped = self.board_flipped.get(player.id, False)
        if flipped:
            rank_index = row
            file_index = 7 - col
        else:
            rank_index = 7 - row
            file_index = col
        return rank_index * 8 + file_index

    def grid_cell_action_id(self, row: int, col: int) -> str:
        return grid_cell_id(row, col)

    def get_cell_label(self, row: int, col: int, player: Player, locale: str) -> str:
        square = self._view_to_square(player, row, col)
        if self.status != "playing" or len(self.board) != 64:
            return Localization.get(
                locale,
                "chess-square-empty-label",
                square=index_to_notation(square),
            )
        notation = index_to_notation(square)
        piece = self._piece_on_square(square)
        selected = self.selected_square.get(player.id)
        label = notation

        if piece is None:
            label = Localization.get(locale, "chess-square-empty-label", square=notation)
        else:
            label = Localization.get(
                locale,
                "chess-square-piece-label",
                square=notation,
                piece=self._piece_name(piece, locale),
            )

        if selected == square:
            return Localization.get(locale, "chess-square-selected-label", label=label)

        if (
            self.status == "playing"
            and not self.promotion_pending
            and isinstance(player, ChessPlayer)
            and player.id == getattr(self.current_player, "id", "")
            and player.color == self.current_color
            and selected is not None
        ):
            legal_targets = {to_sq for _, to_sq in self.get_legal_moves_from(selected, player.color)}
            if square in legal_targets:
                if piece is None:
                    return Localization.get(locale, "chess-square-move-target", square=notation)
                return Localization.get(
                    locale,
                    "chess-square-capture-target",
                    square=notation,
                    piece=self._piece_name(piece, locale),
                )

        return label

    def is_grid_cell_enabled(self, player: Player, row: int, col: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self._has_pending_response():
            return "action-not-available"
        if self.promotion_pending and player.id == self.promotion_player_id:
            return "chess-promotion-pending"
        return None

    def is_grid_cell_hidden(self, player: Player, row: int, col: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self._has_pending_response():
            return Visibility.HIDDEN
        if self.promotion_pending and player.id == self.promotion_player_id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def on_grid_select(self, player: Player, row: int, col: int) -> None:
        if self.status != "playing":
            return
        square = self._view_to_square(player, row, col)
        chess_player = self._as_chess_player(player)
        if (
            chess_player
            and self.current_player == chess_player
            and chess_player.color == self.current_color
            and not chess_player.is_spectator
            and not self.promotion_pending
        ):
            self._handle_turn_square_select(chess_player, square)
            return
        self._announce_square(player, square)

    def _announce_square(self, player: Player, square: int) -> None:
        user = self.get_user(player)
        if not user:
            return
        piece = self._piece_on_square(square)
        notation = index_to_notation(square)
        if piece is None:
            user.speak_l("chess-square-empty", buffer="game", square=notation)
            return
        user.speak_l(
            "chess-square-occupied",
            buffer="game",
            square=notation,
            piece=self._piece_name(piece, user.locale),
        )

    def _handle_turn_square_select(self, player: ChessPlayer, square: int) -> None:
        user = self.get_user(player)
        if not user:
            return
        piece = self._piece_on_square(square)
        selected = self.selected_square.get(player.id)

        if selected is None:
            if piece is None or piece.color != player.color:
                user.speak_l("chess-select-own-piece", buffer="game")
                return
            legal_moves = self.get_legal_moves_from(square, player.color)
            if not legal_moves:
                user.speak_l("chess-piece-no-legal-moves", buffer="game")
                return
            self.selected_square[player.id] = square
            user.play_sound(SOUND_PICKUP)
            user.speak_l(
                "chess-piece-selected",
                buffer="game",
                piece=self._piece_name(piece, user.locale),
                square=index_to_notation(square),
                count=len(legal_moves),
            )
            self.update_player_menu(
                player,
                selection_id=self.grid_cell_action_id(*self.square_to_view(player, square)),
            )
            return

        if selected == square:
            self.selected_square.pop(player.id, None)
            self.bot_move_targets.pop(player.id, None)
            user.play_sound(SOUND_SETDOWN)
            user.speak_l("chess-selection-cleared", buffer="game")
            self.update_player_menu(player)
            return

        if piece is not None and piece.color == player.color:
            legal_moves = self.get_legal_moves_from(square, player.color)
            if not legal_moves:
                user.speak_l("chess-piece-no-legal-moves", buffer="game")
                return
            self.selected_square[player.id] = square
            user.play_sound(SOUND_PICKUP)
            user.speak_l(
                "chess-piece-selected",
                buffer="game",
                piece=self._piece_name(piece, user.locale),
                square=index_to_notation(square),
                count=len(legal_moves),
            )
            self.update_player_menu(
                player,
                selection_id=self.grid_cell_action_id(*self.square_to_view(player, square)),
            )
            return

        legal, _ = self._is_legal_move(selected, square, player.color)
        if not legal:
            user.play_sound(SOUND_SETDOWN)
            user.speak_l("chess-illegal-move", buffer="game")
            self.update_player_menu(player)
            return

        self._execute_move_full(player, selected, square)

    def _play_piece_sound(self, piece_type: str) -> None:
        if piece_type == "pawn":
            self.play_sound(SOUND_PAWN.format(index=random.randint(1, 3)))
        elif piece_type == "knight":
            self.play_sound(SOUND_KNIGHT)
        elif piece_type == "bishop":
            self.play_sound(SOUND_BISHOP)
        elif piece_type == "rook":
            self.play_sound(SOUND_ROOK)
        elif piece_type == "queen":
            self.play_sound(SOUND_QUEEN)
        else:
            self.play_sound(SOUND_KING)

    def _find_king(self, color: str) -> int | None:
        for square, piece in enumerate(self.board):
            if piece and piece.color == color and piece.kind == "king":
                return square
        return None

    def _is_path_clear(self, from_sq: int, to_sq: int) -> bool:
        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8
        file_step = 0 if from_file == to_file else (1 if to_file > from_file else -1)
        rank_step = 0 if from_rank == to_rank else (1 if to_rank > from_rank else -1)
        current_file = from_file + file_step
        current_rank = from_rank + rank_step
        while current_file != to_file or current_rank != to_rank:
            if self.board[current_rank * 8 + current_file] is not None:
                return False
            current_file += file_step
            current_rank += rank_step
        return True

    def _is_valid_pawn_move(self, from_sq: int, to_sq: int, piece: ChessPiece) -> bool:
        direction = 1 if piece.color == COLOR_WHITE else -1
        from_file = from_sq % 8
        to_file = to_sq % 8
        from_rank = from_sq // 8
        to_rank = to_sq // 8
        target = self.board[to_sq]

        if to_file == from_file:
            if to_rank == from_rank + direction and target is None:
                return True
            start_rank = 1 if piece.color == COLOR_WHITE else 6
            if from_rank == start_rank and to_rank == from_rank + 2 * direction:
                middle_sq = from_sq + 8 * direction
                return self.board[middle_sq] is None and target is None

        if abs(to_file - from_file) == 1 and to_rank == from_rank + direction:
            if target is not None and target.color != piece.color:
                return True
            if target is None and to_sq == self.en_passant_target:
                return True

        return False

    def _is_valid_piece_move(self, from_sq: int, to_sq: int, piece: ChessPiece) -> bool:
        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)

        if piece.kind == "pawn":
            return self._is_valid_pawn_move(from_sq, to_sq, piece)
        if piece.kind == "knight":
            return (file_diff, rank_diff) in {(1, 2), (2, 1)}
        if piece.kind == "bishop":
            return file_diff == rank_diff and file_diff > 0 and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "rook":
            return (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0) and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "queen":
            straight = (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0)
            diagonal = file_diff == rank_diff and file_diff > 0
            return (straight or diagonal) and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "king":
            return file_diff <= 1 and rank_diff <= 1 and (file_diff + rank_diff > 0)
        return False

    def _can_piece_attack(self, from_sq: int, to_sq: int, piece: ChessPiece) -> bool:
        if from_sq == to_sq:
            return False
        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)

        if piece.kind == "pawn":
            direction = 1 if piece.color == COLOR_WHITE else -1
            return file_diff == 1 and to_rank == from_rank + direction
        if piece.kind == "knight":
            return (file_diff, rank_diff) in {(1, 2), (2, 1)}
        if piece.kind == "bishop":
            return file_diff == rank_diff and file_diff > 0 and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "rook":
            return (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0) and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "queen":
            straight = (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0)
            diagonal = file_diff == rank_diff and file_diff > 0
            return (straight or diagonal) and self._is_path_clear(from_sq, to_sq)
        if piece.kind == "king":
            return file_diff <= 1 and rank_diff <= 1
        return False

    def _is_square_attacked(self, square: int, by_color: str) -> bool:
        for from_sq, piece in enumerate(self.board):
            if piece and piece.color == by_color and self._can_piece_attack(from_sq, square, piece):
                return True
        return False

    def is_in_check(self, color: str) -> bool:
        king_square = self._find_king(color)
        if king_square is None:
            return False
        attacker = COLOR_BLACK if color == COLOR_WHITE else COLOR_WHITE
        return self._is_square_attacked(king_square, attacker)

    def _is_castling_move(self, from_sq: int, to_sq: int, piece: ChessPiece | None = None) -> tuple[bool, str]:
        mover = piece or self.board[from_sq]
        if mover is None or mover.kind != "king":
            return False, ""
        diff = (to_sq % 8) - (from_sq % 8)
        if diff == 2:
            return True, "kingside"
        if diff == -2:
            return True, "queenside"
        return False, ""

    def _is_castling_legal(self, color: str, side: str) -> tuple[bool, str]:
        rank = 0 if color == COLOR_WHITE else 7
        king_square = rank * 8 + 4
        rook_square = rank * 8 + (7 if side == "kingside" else 0)
        king = self.board[king_square]
        rook = self.board[rook_square]
        if king is None or king.kind != "king" or king.color != color:
            return False, "chess-invalid-castle"
        if rook is None or rook.kind != "rook" or rook.color != color:
            return False, "chess-invalid-castle"
        if king.has_moved or rook.has_moved:
            return False, "chess-invalid-castle"

        if side == "kingside":
            rights = self.castle_white_kingside if color == COLOR_WHITE else self.castle_black_kingside
            between = [rank * 8 + 5, rank * 8 + 6]
            path = [rank * 8 + 5, rank * 8 + 6]
        else:
            rights = self.castle_white_queenside if color == COLOR_WHITE else self.castle_black_queenside
            between = [rank * 8 + 1, rank * 8 + 2, rank * 8 + 3]
            path = [rank * 8 + 3, rank * 8 + 2]
        if not rights:
            return False, "chess-invalid-castle"
        if any(self.board[square] is not None for square in between):
            return False, "chess-invalid-castle"
        if self.is_in_check(color):
            return False, "chess-invalid-castle"
        attacker = COLOR_BLACK if color == COLOR_WHITE else COLOR_WHITE
        if any(self._is_square_attacked(square, attacker) for square in path):
            return False, "chess-invalid-castle"
        return True, ""

    def _update_castling_rights_after_move(
        self,
        from_sq: int,
        to_sq: int,
        piece: ChessPiece,
        captured_piece: ChessPiece | None,
    ) -> None:
        if piece.kind == "king":
            if piece.color == COLOR_WHITE:
                self.castle_white_kingside = False
                self.castle_white_queenside = False
            else:
                self.castle_black_kingside = False
                self.castle_black_queenside = False
        elif piece.kind == "rook":
            if from_sq == 0:
                self.castle_white_queenside = False
            elif from_sq == 7:
                self.castle_white_kingside = False
            elif from_sq == 56:
                self.castle_black_queenside = False
            elif from_sq == 63:
                self.castle_black_kingside = False

        if captured_piece and captured_piece.kind == "rook":
            if to_sq == 0:
                self.castle_white_queenside = False
            elif to_sq == 7:
                self.castle_white_kingside = False
            elif to_sq == 56:
                self.castle_black_queenside = False
            elif to_sq == 63:
                self.castle_black_kingside = False

    def _apply_move_core(
        self,
        from_sq: int,
        to_sq: int,
        *,
        promotion: str | None = None,
        auto_promote_to_queen: bool = False,
    ) -> dict:
        piece = self.board[from_sq]
        if piece is None:
            return {}
        target = self.board[to_sq]
        outcome = {
            "piece": piece.kind,
            "color": piece.color,
            "captured_kind": target.kind if target else "",
            "captured_color": target.color if target else "",
            "special": "",
            "promotion": "",
            "needs_promotion": False,
        }

        is_castle, castle_side = self._is_castling_move(from_sq, to_sq, piece)
        if is_castle:
            rank = 0 if piece.color == COLOR_WHITE else 7
            rook_from = rank * 8 + (7 if castle_side == "kingside" else 0)
            rook_to = rank * 8 + (5 if castle_side == "kingside" else 3)
            self.board[to_sq] = ChessPiece("king", piece.color, has_moved=True)
            self.board[from_sq] = None
            self.board[rook_to] = ChessPiece("rook", piece.color, has_moved=True)
            self.board[rook_from] = None
            self.en_passant_target = -1
            self.halfmove_clock += 1
            if piece.color == COLOR_WHITE:
                self.castle_white_kingside = False
                self.castle_white_queenside = False
            else:
                self.castle_black_kingside = False
                self.castle_black_queenside = False
            outcome["special"] = f"castle_{castle_side}"
            return outcome

        captured_piece = target
        if piece.kind == "pawn" and target is None and to_sq == self.en_passant_target and (from_sq % 8) != (to_sq % 8):
            capture_square = to_sq - (8 if piece.color == COLOR_WHITE else -8)
            captured_piece = self.board[capture_square]
            self.board[capture_square] = None
            outcome["captured_kind"] = captured_piece.kind if captured_piece else ""
            outcome["captured_color"] = captured_piece.color if captured_piece else ""
            outcome["special"] = "en_passant"

        self._update_castling_rights_after_move(from_sq, to_sq, piece, captured_piece)

        self.board[from_sq] = None
        moved_piece = ChessPiece(piece.kind, piece.color, has_moved=True)
        self.board[to_sq] = moved_piece

        self.en_passant_target = -1
        if piece.kind == "pawn":
            from_rank = from_sq // 8
            to_rank = to_sq // 8
            if abs(to_rank - from_rank) == 2:
                self.en_passant_target = from_sq + (8 if piece.color == COLOR_WHITE else -8)

        back_rank = 7 if piece.color == COLOR_WHITE else 0
        if piece.kind == "pawn" and (to_sq // 8) == back_rank:
            if promotion:
                self.board[to_sq] = ChessPiece(promotion, piece.color, has_moved=True)
                outcome["promotion"] = promotion
            elif auto_promote_to_queen:
                self.board[to_sq] = ChessPiece("queen", piece.color, has_moved=True)
                outcome["promotion"] = "queen"
            else:
                outcome["needs_promotion"] = True

        if piece.kind == "pawn" or captured_piece is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        return outcome

    def _is_legal_move(self, from_sq: int, to_sq: int, color: str) -> tuple[bool, str]:
        piece = self.board[from_sq]
        if piece is None:
            return False, "chess-illegal-move"
        if piece.color != color:
            return False, "chess-illegal-move"
        target = self.board[to_sq]
        if target is not None and target.color == color:
            return False, "chess-illegal-move"

        is_castle, castle_side = self._is_castling_move(from_sq, to_sq, piece)
        if is_castle:
            return self._is_castling_legal(color, castle_side)

        if not self._is_valid_piece_move(from_sq, to_sq, piece):
            return False, "chess-illegal-move"

        saved = self.save_position()
        self._apply_move_core(from_sq, to_sq, auto_promote_to_queen=True)
        illegal = self.is_in_check(color)
        self.restore_position(saved)
        if illegal:
            return False, "chess-illegal-move"
        return True, ""

    def _get_candidate_squares(self, from_sq: int, piece: ChessPiece) -> list[int]:
        file_index = from_sq % 8
        rank_index = from_sq // 8
        candidates: list[int] = []

        if piece.kind == "pawn":
            direction = 1 if piece.color == COLOR_WHITE else -1
            one_step_rank = rank_index + direction
            if 0 <= one_step_rank < 8:
                candidates.append(one_step_rank * 8 + file_index)
                for offset in (-1, 1):
                    target_file = file_index + offset
                    if 0 <= target_file < 8:
                        candidates.append(one_step_rank * 8 + target_file)
            start_rank = 1 if piece.color == COLOR_WHITE else 6
            if rank_index == start_rank:
                two_step_rank = rank_index + 2 * direction
                if 0 <= two_step_rank < 8:
                    candidates.append(two_step_rank * 8 + file_index)
        elif piece.kind == "knight":
            for rank_step, file_step in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                new_rank = rank_index + rank_step
                new_file = file_index + file_step
                if 0 <= new_rank < 8 and 0 <= new_file < 8:
                    candidates.append(new_rank * 8 + new_file)
        elif piece.kind in {"bishop", "rook", "queen"}:
            directions: list[tuple[int, int]] = []
            if piece.kind in {"bishop", "queen"}:
                directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
            if piece.kind in {"rook", "queen"}:
                directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
            for rank_step, file_step in directions:
                new_rank = rank_index + rank_step
                new_file = file_index + file_step
                while 0 <= new_rank < 8 and 0 <= new_file < 8:
                    square = new_rank * 8 + new_file
                    candidates.append(square)
                    if self.board[square] is not None:
                        break
                    new_rank += rank_step
                    new_file += file_step
        elif piece.kind == "king":
            for rank_step in (-1, 0, 1):
                for file_step in (-1, 0, 1):
                    if rank_step == 0 and file_step == 0:
                        continue
                    new_rank = rank_index + rank_step
                    new_file = file_index + file_step
                    if 0 <= new_rank < 8 and 0 <= new_file < 8:
                        candidates.append(new_rank * 8 + new_file)
            candidates.append(from_sq + 2)
            candidates.append(from_sq - 2)

        return [square for square in candidates if 0 <= square < 64]

    def get_legal_moves(self, color: str) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for from_sq, piece in enumerate(self.board):
            if piece is None or piece.color != color:
                continue
            for to_sq in self._get_candidate_squares(from_sq, piece):
                legal, _ = self._is_legal_move(from_sq, to_sq, color)
                if legal:
                    moves.append((from_sq, to_sq))
        return moves

    def get_legal_moves_from(self, from_sq: int, color: str) -> list[tuple[int, int]]:
        piece = self.board[from_sq]
        if piece is None or piece.color != color:
            return []
        moves: list[tuple[int, int]] = []
        for to_sq in self._get_candidate_squares(from_sq, piece):
            legal, _ = self._is_legal_move(from_sq, to_sq, color)
            if legal:
                moves.append((from_sq, to_sq))
        return moves

    def is_checkmate(self, color: str) -> bool:
        return self.is_in_check(color) and not self.get_legal_moves(color)

    def is_stalemate(self, color: str) -> bool:
        return not self.is_in_check(color) and not self.get_legal_moves(color)

    def _is_insufficient_material(self) -> bool:
        non_kings: list[tuple[int, ChessPiece]] = [
            (square, piece)
            for square, piece in enumerate(self.board)
            if piece is not None and piece.kind != "king"
        ]
        if not non_kings:
            return True
        if len(non_kings) == 1:
            return non_kings[0][1].kind in {"bishop", "knight"}
        if len(non_kings) == 2:
            first_square, first_piece = non_kings[0]
            second_square, second_piece = non_kings[1]
            if first_piece.kind == "bishop" and second_piece.kind == "bishop":
                # Same-colored bishops are insufficient regardless of whether they
                # belong to one side or are split across both sides.
                first_color = (first_square // 8 + first_square % 8) % 2
                second_color = (second_square // 8 + second_square % 8) % 2
                return first_color == second_color
        return False

    def _get_position_hash(self) -> str:
        piece_codes = {
            "pawn": "p",
            "knight": "n",
            "bishop": "b",
            "rook": "r",
            "queen": "q",
            "king": "k",
        }
        parts: list[str] = []
        for square, piece in enumerate(self.board):
            if piece is None:
                continue
            parts.append(
                f"{square}:{piece.color[0]}{piece_codes[piece.kind]}"
            )
        castling = ""
        if self.castle_white_kingside:
            castling += "K"
        if self.castle_white_queenside:
            castling += "Q"
        if self.castle_black_kingside:
            castling += "k"
        if self.castle_black_queenside:
            castling += "q"
        parts.append(f"c:{castling or '-'}")
        parts.append(f"ep:{self.en_passant_target}")
        parts.append(f"turn:{self.current_color}")
        return "|".join(parts)

    def _complete_move(
        self,
        player: ChessPlayer,
        from_sq: int,
        to_sq: int,
        outcome: dict,
        snapshot: ChessUndoSnapshot,
    ) -> None:
        self.selected_square.pop(player.id, None)
        self.bot_move_targets.pop(player.id, None)

        if outcome.get("needs_promotion"):
            self.pending_undo_snapshot = snapshot
            self.promotion_pending = True
            self.promotion_player_id = player.id
            self.promotion_square = to_sq
            self.pending_promotion_from = from_sq
            self.pending_promotion_capture = outcome.get("captured_kind", "")
            self.pending_promotion_capture_color = outcome.get("captured_color", "")
            self.pending_promotion_special = outcome.get("special", "")
            user = self.get_user(player)
            if user:
                user.speak_l("chess-choose-promotion", buffer="game")
            self.rebuild_all_menus()
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(6, 12))
            return

        self._finalize_turn(player, from_sq, to_sq, outcome, snapshot)

    def _finalize_turn(
        self,
        player: ChessPlayer,
        from_sq: int,
        to_sq: int,
        outcome: dict,
        snapshot: ChessUndoSnapshot,
    ) -> None:
        opponent_color = COLOR_BLACK if player.color == COLOR_WHITE else COLOR_WHITE
        self._add_increment(player.color)
        self.current_color = opponent_color
        self.move_history.append(
            ChessMoveRecord(
                from_square=from_sq,
                to_square=to_sq,
                color=player.color,
                piece=outcome.get("piece", ""),
                captured=outcome.get("captured_kind", ""),
                captured_color=outcome.get("captured_color", ""),
                promotion=outcome.get("promotion", ""),
                special=outcome.get("special", ""),
            )
        )
        self.position_history.append(self._get_position_hash())
        self.undo_history.append(snapshot)
        self.pending_undo_snapshot = None

        opponent = self._get_player_by_color(opponent_color)
        if self.is_checkmate(opponent_color):
            self.winner_color = player.color
            self.broadcast_personal_l(
                player,
                "chess-you-win-checkmate",
                "chess-player-wins-checkmate",
                buffer="game",
            )
            self.finish_game()
            return

        if self.is_stalemate(opponent_color):
            self.draw_reason = "stalemate"
            self.broadcast_l("chess-draw-stalemate", buffer="game")
            self.finish_game()
            return

        current_hash = self.position_history[-1]
        if self.options.draw_handling == "automatic":
            if self.halfmove_clock >= 100:
                self.draw_reason = "fifty_move_rule"
                self.broadcast_l("chess-draw-fifty-move", buffer="game")
                self.finish_game()
                return
            if self.position_history.count(current_hash) >= 3:
                self.draw_reason = "threefold_repetition"
                self.broadcast_l("chess-draw-threefold", buffer="game")
                self.finish_game()
                return
        if self._is_insufficient_material():
            self.draw_reason = "insufficient_material"
            self.broadcast_l("chess-draw-insufficient-material", buffer="game")
            self.finish_game()
            return

        if opponent and self.is_in_check(opponent_color):
            self.broadcast_l("chess-check", buffer="game", player=opponent.name)

        self._advance_to_next_turn()

    def _advance_to_next_turn(self) -> None:
        if not self.turn_player_ids:
            return
        self.turn_index = (self.turn_index + 1) % len(self.turn_player_ids)
        self.selected_square.clear()
        self.bot_move_targets.clear()
        self.draw_offer_from = ""
        self.undo_request_from = ""
        next_player = self._as_chess_player(self.current_player)
        if next_player:
            self.current_color = next_player.color
        self.announce_turn(turn_sound=SOUND_TURN)
        self._announce_claim_available(next_player)
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def _execute_move_full(self, player: ChessPlayer, from_sq: int, to_sq: int) -> None:
        piece = self.board[from_sq]
        if piece is None:
            return
        snapshot = self._make_undo_snapshot()
        from_square = index_to_notation(from_sq)
        to_square = index_to_notation(to_sq)
        outcome = self._apply_move_core(from_sq, to_sq)

        if outcome.get("captured_kind"):
            self.play_sound(SOUND_CAPTURE.format(index=random.randint(1, 2)))
            if outcome.get("special") == "en_passant":
                self.broadcast_personal_l(
                    player,
                    "chess-you-en-passant",
                    "chess-player-en-passant",
                    buffer="game",
                    from_square=from_square,
                    to_square=to_square,
                )
            else:
                self.broadcast_personal_l(
                    player,
                    "chess-you-capture",
                    "chess-player-captures",
                    buffer="game",
                    from_square=from_square,
                    to_square=to_square,
                )
        elif outcome.get("special") == "castle_kingside":
            self.play_sound(SOUND_KING)
            self.broadcast_personal_l(
                player,
                "chess-you-castle-kingside",
                "chess-player-castles-kingside",
                buffer="game",
            )
        elif outcome.get("special") == "castle_queenside":
            self.play_sound(SOUND_KING)
            self.broadcast_personal_l(
                player,
                "chess-you-castle-queenside",
                "chess-player-castles-queenside",
                buffer="game",
            )
        else:
            self._play_piece_sound(piece.kind)
            self.broadcast_personal_l(
                player,
                "chess-you-move",
                "chess-player-moves",
                buffer="game",
                from_square=from_square,
                to_square=to_square,
            )

        self._complete_move(player, from_sq, to_sq, outcome, snapshot)

    def _action_promote(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None:
            return
        if not self.promotion_pending or chess_player.id != self.promotion_player_id:
            return
        piece_type = action_id.removeprefix("promote_")
        if piece_type not in PIECE_TYPES or piece_type in {"pawn", "king"}:
            return
        piece = self.board[self.promotion_square]
        if piece is None:
            return

        self.board[self.promotion_square] = ChessPiece(piece_type, piece.color, has_moved=True)
        self.broadcast_personal_l(
            chess_player,
            "chess-you-promote",
            "chess-player-promotes",
            buffer="game",
            square=index_to_notation(self.promotion_square),
        )

        from_sq = self.pending_promotion_from
        to_sq = self.promotion_square
        outcome = {
            "piece": "pawn",
            "color": chess_player.color,
            "captured_kind": self.pending_promotion_capture,
            "captured_color": self.pending_promotion_capture_color,
            "special": self.pending_promotion_special,
            "promotion": piece_type,
        }

        self.promotion_pending = False
        self.promotion_player_id = ""
        self.pending_promotion_from = -1
        self.pending_promotion_capture = ""
        self.pending_promotion_capture_color = ""
        self.pending_promotion_special = ""
        self.promotion_square = -1
        snapshot = self.pending_undo_snapshot or self._make_undo_snapshot()
        self._finalize_turn(chess_player, from_sq, to_sq, outcome, snapshot)

    def _is_promote_enabled(self, player: Player) -> str | None:
        if not self.promotion_pending:
            return "action-not-available"
        if player.id != self.promotion_player_id:
            return "action-not-your-turn"
        return None

    def _is_promote_hidden(self, player: Player) -> Visibility:
        if not self.promotion_pending or player.id != self.promotion_player_id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _can_claim_draw_reason(self) -> str | None:
        if self.options.draw_handling != "claim_required":
            return None
        if self.halfmove_clock >= 100:
            return "fifty_move_rule"
        if self.position_history and self.position_history.count(self.position_history[-1]) >= 3:
            return "threefold_repetition"
        return None

    def _announce_claim_available(self, player: ChessPlayer | None) -> None:
        if player is None:
            return
        reason = self._can_claim_draw_reason()
        if reason is None:
            return
        user = self.get_user(player)
        if not user:
            return
        reason_key = "chess-claim-available-fifty-move"
        if reason == "threefold_repetition":
            reason_key = "chess-claim-available-threefold"
        user.speak_l(reason_key, buffer="game")

    def _is_web_client(self, player: Player) -> bool:
        user = self.get_user(player)
        return self.is_touch_client(user)

    def _is_read_board_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_flip_board_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self._is_web_client(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_clock_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self._is_web_client(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_offer_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not self.options.allow_draw_offers or self.promotion_pending or self._has_pending_response():
            return "action-not-available"
        if player != self.current_player:
            return "action-not-your-turn"
        return None

    def _is_offer_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self._is_web_client(player) and self._is_offer_draw_enabled(player) is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_draw_response_enabled(self, player: Player) -> str | None:
        responder = self._get_pending_response_player()
        if responder is None:
            return "action-not-available"
        if player.id != responder.id:
            return "action-not-your-turn"
        return None

    def _is_draw_response_hidden(self, player: Player) -> Visibility:
        if not self.draw_offer_from or player.is_spectator:
            return Visibility.HIDDEN
        responder = self._get_pending_response_player()
        if responder and player.id == responder.id and self._is_web_client(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_request_undo_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if (
            not self.options.allow_undo_requests
            or self.promotion_pending
            or self._has_pending_response()
            or not self.undo_history
        ):
            return "action-not-available"
        if player != self.current_player:
            return "action-not-your-turn"
        return None

    def _is_request_undo_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self._is_web_client(player) and self._is_request_undo_enabled(player) is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_undo_response_enabled(self, player: Player) -> str | None:
        responder = self._get_pending_response_player()
        if responder is None or not self.undo_request_from:
            return "action-not-available"
        if player.id != responder.id:
            return "action-not-your-turn"
        return None

    def _is_undo_response_hidden(self, player: Player) -> Visibility:
        if not self.undo_request_from or player.is_spectator:
            return Visibility.HIDDEN
        responder = self._get_pending_response_player()
        if responder and player.id == responder.id and self._is_web_client(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_claim_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.promotion_pending or self._has_pending_response():
            return "action-not-available"
        if player != self.current_player:
            return "action-not-your-turn"
        if self._can_claim_draw_reason() is None:
            return "action-not-available"
        return None

    def _is_claim_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self._is_web_client(player) and self._is_claim_draw_enabled(player) is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _action_read_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines: list[str] = []
        for row in range(8):
            labels: list[str] = []
            for col in range(8):
                square = self._view_to_square(player, row, col)
                piece = self.board[square]
                if piece is None:
                    labels.append(Localization.get(user.locale, "chess-empty"))
                else:
                    labels.append(self._piece_name(piece, user.locale))
            lines.append(
                Localization.get(
                    user.locale,
                    "chess-board-rank-line",
                    rank=index_to_notation(self._view_to_square(player, row, 0))[1],
                    pieces=", ".join(labels),
                )
            )
        self.status_box(player, lines)

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        white_player = self._get_player_by_color(COLOR_WHITE)
        black_player = self._get_player_by_color(COLOR_BLACK)
        current_player = self._get_player_by_color(self.current_color)
        lines = [
            Localization.get(user.locale, "chess-status-white", player=white_player.name if white_player else "?"),
            Localization.get(user.locale, "chess-status-black", player=black_player.name if black_player else "?"),
            Localization.get(
                user.locale,
                "chess-status-turn",
                color=Localization.get(user.locale, f"chess-color-{self.current_color}"),
                player=current_player.name if current_player else "?",
            ),
            Localization.get(user.locale, "chess-status-move-count", count=len(self.move_history)),
            self._get_clock_label(user.locale, COLOR_WHITE),
            self._get_clock_label(user.locale, COLOR_BLACK),
            Localization.get(
                user.locale,
                "chess-status-time-control",
                control=Localization.get(user.locale, TIME_CONTROL_LABELS[self.options.time_control]),
            ),
        ]
        if self.promotion_pending:
            lines.append(Localization.get(user.locale, "chess-status-promotion-pending"))
        elif self.is_in_check(self.current_color):
            lines.append(Localization.get(user.locale, "chess-status-check"))
        claim_reason = self._can_claim_draw_reason()
        if claim_reason == "fifty_move_rule":
            lines.append(Localization.get(user.locale, "chess-claim-available-fifty-move"))
        elif claim_reason == "threefold_repetition":
            lines.append(Localization.get(user.locale, "chess-claim-available-threefold"))
        if self.draw_offer_from:
            requester = self.get_player_by_id(self.draw_offer_from)
            lines.append(
                Localization.get(
                    user.locale,
                    "chess-status-draw-offer",
                    player=requester.name if requester else "?",
                )
            )
        if self.undo_request_from:
            requester = self.get_player_by_id(self.undo_request_from)
            lines.append(
                Localization.get(
                    user.locale,
                    "chess-status-undo-request",
                    player=requester.name if requester else "?",
                )
            )
        self.status_box(player, lines)

    def _action_check_clock(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not self._has_clock():
            user.speak_l("chess-clock-announcement-untimed", buffer="game")
            return
        user.speak_l(
            "chess-clock-announcement",
            buffer="game",
            white=self._format_clock_value(self.white_clock_ticks),
            black=self._format_clock_value(self.black_clock_ticks),
        )

    def _action_claim_draw(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None:
            return
        reason = self._can_claim_draw_reason()
        if reason is None:
            return
        self.draw_reason = reason
        key = "chess-draw-claimed-fifty-move"
        if reason == "threefold_repetition":
            key = "chess-draw-claimed-threefold"
        self.broadcast_l(key, buffer="game", player=chess_player.name)
        self.finish_game()

    def _action_offer_draw(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_offer_draw_enabled(player) is not None:
            return
        self.draw_offer_from = chess_player.id
        self.broadcast_personal_l(
            chess_player,
            "chess-you-offer-draw",
            "chess-player-offers-draw",
            buffer="game",
        )
        responder = self._get_pending_response_player()
        if responder and responder.is_bot:
            BotHelper.jolt_bot(responder, ticks=random.randint(6, 12))
        self.rebuild_all_menus()

    def _action_accept_draw(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_draw_response_enabled(player) is not None:
            return
        self.draw_reason = "agreement"
        self.broadcast_personal_l(
            chess_player,
            "chess-you-accept-draw",
            "chess-player-accepts-draw",
            buffer="game",
        )
        self.broadcast_l("chess-draw-agreement", buffer="game")
        self.finish_game()

    def _action_decline_draw(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_draw_response_enabled(player) is not None:
            return
        self.draw_offer_from = ""
        self.broadcast_personal_l(
            chess_player,
            "chess-you-decline-draw",
            "chess-player-declines-draw",
            buffer="game",
        )
        self.rebuild_all_menus()

    def _action_request_undo(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_request_undo_enabled(player) is not None:
            return
        self.undo_request_from = chess_player.id
        self.broadcast_personal_l(
            chess_player,
            "chess-you-request-undo",
            "chess-player-requests-undo",
            buffer="game",
        )
        responder = self._get_pending_response_player()
        if responder and responder.is_bot:
            BotHelper.jolt_bot(responder, ticks=random.randint(6, 12))
        self.rebuild_all_menus()

    def _action_accept_undo(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_undo_response_enabled(player) is not None:
            return
        if not self.undo_history:
            return
        snapshot = self.undo_history.pop()
        self._restore_undo_snapshot(snapshot)
        self.broadcast_personal_l(
            chess_player,
            "chess-you-accept-undo",
            "chess-player-accepts-undo",
            buffer="game",
        )
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def _action_decline_undo(self, player: Player, action_id: str) -> None:
        chess_player = self._as_chess_player(player)
        if chess_player is None or self._is_undo_response_enabled(player) is not None:
            return
        self.undo_request_from = ""
        self.broadcast_personal_l(
            chess_player,
            "chess-you-decline-undo",
            "chess-player-declines-undo",
            buffer="game",
        )
        self.rebuild_all_menus()

    def _action_flip_board(self, player: Player, action_id: str) -> None:
        self.board_flipped[player.id] = not self.board_flipped.get(player.id, False)
        user = self.get_user(player)
        if user:
            perspective = "black" if self.board_flipped[player.id] else "white"
            user.speak_l(
                "chess-board-flipped",
                buffer="game",
                color=Localization.get(user.locale, f"chess-color-{perspective}"),
            )
        self.rebuild_player_menu(player)

    def _build_grid_menu_kwargs(self) -> dict:
        if self.status != "playing" or self.promotion_pending or self._has_pending_response():
            return {}
        return super()._build_grid_menu_kwargs()

    def build_game_result(self) -> GameResult:
        winner = self._get_player_by_color(self.winner_color) if self.winner_color else None
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_color": self.winner_color,
                "draw_reason": self.draw_reason,
                "move_count": len(self.move_history),
                "time_control": self.options.time_control,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines: list[str] = []
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(
                Localization.get(
                    locale,
                    "chess-end-winner",
                    player=winner_name,
                    color=Localization.get(locale, f"chess-color-{result.custom_data.get('winner_color', COLOR_WHITE)}"),
                )
            )
        else:
            reason = result.custom_data.get("draw_reason", "")
            reason_key = {
                "stalemate": "chess-draw-stalemate",
                "fifty_move_rule": "chess-draw-fifty-move",
                "threefold_repetition": "chess-draw-threefold",
                "insufficient_material": "chess-draw-insufficient-material",
                "agreement": "chess-draw-agreement",
                "timeout_insufficient_material": "chess-draw-timeout-insufficient",
            }.get(reason, "chess-draw")
            lines.append(Localization.get(locale, reason_key))
        lines.append(
            Localization.get(
                locale,
                "chess-end-move-count",
                count=result.custom_data.get("move_count", 0),
            )
        )
        return lines
