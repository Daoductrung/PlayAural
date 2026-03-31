"""Backgammon for PlayAural."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_think as _bot_think
from .bot import bot_respond_to_double as _bot_respond_to_double

if TYPE_CHECKING:
    from ...users.base import User


COLOR_RED = "red"
COLOR_WHITE = "white"
COLORS = [COLOR_RED, COLOR_WHITE]

TURN_PHASE_MOVING = "moving"
TURN_PHASE_PRE_ROLL = "pre_roll"
TURN_PHASE_DOUBLING = "doubling_response"

MUSIC_PATH = "game_ninetynine/mus.ogg"
SOUND_DICE = "game_squares/diceroll{index}.ogg"
SOUND_STEP = "game_squares/step{index}.ogg"
SOUND_HIT = "game_chess/capture{index}.ogg"
SOUND_BEAR_OFF = "mention.ogg"
SOUND_WIN = "game_pig/win.ogg"
SOUND_MATCH_WIN = "game_pig/wingame.ogg"
SOUND_MATCH_LOSE = "game_pig/lose.ogg"
SOUND_TURN = "game_squares/begin turn.ogg"

INITIAL_POINTS = [0] * 24
INITIAL_POINTS[23] = 2
INITIAL_POINTS[12] = 5
INITIAL_POINTS[7] = 3
INITIAL_POINTS[5] = 5
INITIAL_POINTS[0] = -2
INITIAL_POINTS[11] = -5
INITIAL_POINTS[16] = -3
INITIAL_POINTS[18] = -5

BOT_STRATEGY_CHOICES = ["simple", "smart", "random"]
BOT_STRATEGY_LABELS = {
    "simple": "backgammon-bot-simple",
    "smart": "backgammon-bot-smart",
    "random": "backgammon-bot-random",
}

WEB_STANDARD_ORDER = [
    "read_board",
    "check_status",
    "check_pip",
    "check_cube",
    "check_dice",
    "check_scores",
    "whose_turn",
    "whos_at_table",
]


@dataclass
class BackgammonBoard(DataClassJSONMixin):
    points: list[int] = field(default_factory=lambda: list(INITIAL_POINTS))
    bar_red: int = 0
    bar_white: int = 0
    off_red: int = 0
    off_white: int = 0


@dataclass(frozen=True)
class BackgammonMove(DataClassJSONMixin):
    source: int
    destination: int
    die_value: int
    is_hit: bool = False
    is_bear_off: bool = False


@dataclass
class BackgammonSmartSearchNode(DataClassJSONMixin):
    prefix: list[BackgammonMove] = field(default_factory=list)
    remaining_dice: list[int] = field(default_factory=list)


@dataclass
class BackgammonSmartSearchState(DataClassJSONMixin):
    player_id: str = ""
    player_color: str = ""
    root_dice: list[int] = field(default_factory=list)
    root_board: BackgammonBoard = field(default_factory=BackgammonBoard)
    stack: list[BackgammonSmartSearchNode] = field(default_factory=list)
    best_sequence: list[BackgammonMove] = field(default_factory=list)
    best_score: int = -100_000
    best_length: int = -1
    evaluated_sequences: int = 0
    completed: bool = False


@dataclass
class BackgammonPlayer(Player):
    color: str = ""


@dataclass
class BackgammonOptions(GameOptions):
    match_length: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=25,
            value_key="points",
            label="backgammon-set-match-length",
            prompt="backgammon-enter-match-length",
            change_msg="backgammon-option-changed-match-length",
        )
    )
    bot_strategy: str = option_field(
        MenuOption(
            default="simple",
            choices=BOT_STRATEGY_CHOICES,
            value_key="strategy",
            label="backgammon-set-bot-strategy",
            prompt="backgammon-select-bot-strategy",
            change_msg="backgammon-option-changed-bot-strategy",
            choice_labels=BOT_STRATEGY_LABELS,
        )
    )


@register_game
@dataclass
class BackgammonGame(Game):
    players: list[BackgammonPlayer] = field(default_factory=list)
    options: BackgammonOptions = field(default_factory=BackgammonOptions)

    board: BackgammonBoard = field(default_factory=BackgammonBoard)
    turn_phase: str = TURN_PHASE_PRE_ROLL
    remaining_dice: list[int] = field(default_factory=list)
    moves_this_turn: list[BackgammonMove] = field(default_factory=list)
    pending_double_to: str = ""

    score_red: int = 0
    score_white: int = 0
    cube_value: int = 1
    cube_owner: str = ""
    is_crawford: bool = False
    crawford_used: bool = False
    game_number: int = 1

    match_winner_color: str = ""
    smart_bot_search: BackgammonSmartSearchState | None = None

    @classmethod
    def get_name(cls) -> str:
        return "Backgammon"

    @classmethod
    def get_type(cls) -> str:
        return "backgammon"

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

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> BackgammonPlayer:
        return BackgammonPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        return super().prestart_validate()

    def create_turn_action_set(self, player: BackgammonPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "backgammon-roll-dice"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="offer_double",
                label=Localization.get(locale, "backgammon-offer-double"),
                handler="_action_offer_double",
                is_enabled="_is_offer_double_enabled",
                is_hidden="_is_offer_double_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="accept_double",
                label=Localization.get(locale, "backgammon-accept-double"),
                handler="_action_accept_double",
                is_enabled="_is_accept_double_enabled",
                is_hidden="_is_accept_double_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="drop_double",
                label=Localization.get(locale, "backgammon-drop-double"),
                handler="_action_drop_double",
                is_enabled="_is_drop_double_enabled",
                is_hidden="_is_drop_double_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="undo_move",
                label=Localization.get(locale, "backgammon-undo-move"),
                handler="_action_undo_move",
                is_enabled="_is_undo_move_enabled",
                is_hidden="_is_undo_move_hidden",
                show_in_actions_menu=False,
            )
        )
        self._sync_turn_actions(player, action_set)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        for action in [
            Action(
                id="read_board",
                label=Localization.get(locale, "backgammon-read-board"),
                handler="_action_read_board",
                is_enabled="_is_info_enabled",
                is_hidden="_is_read_board_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_status",
                label=Localization.get(locale, "backgammon-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_pip",
                label=Localization.get(locale, "backgammon-check-pip"),
                handler="_action_check_pip",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_pip_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_cube",
                label=Localization.get(locale, "backgammon-check-cube"),
                handler="_action_check_cube",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_cube_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_dice",
                label=Localization.get(locale, "backgammon-check-dice"),
                handler="_action_check_dice",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_dice_hidden",
                include_spectators=True,
            ),
        ]:
            action_set.add(action)
        self._apply_standard_action_order(action_set, user)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll_dice"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "shift+d", "Offer double", ["offer_double"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "y", "Accept double", ["accept_double"], state=KeybindState.ACTIVE
        )
        self.define_keybind("n", "Drop double", ["drop_double"], state=KeybindState.ACTIVE)
        self.define_keybind("u", "Undo move", ["undo_move"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "v",
            "Read board",
            ["read_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "p",
            "Check pip count",
            ["check_pip"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            "Check cube",
            ["check_cube"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "x",
            "Check dice",
            ["check_dice"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
            self._sync_standard_actions(player)
        super().rebuild_all_menus()

    def on_start(self) -> None:
        active = self.get_active_players()
        for index, player in enumerate(active):
            player.color = COLORS[index]
        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        self.play_music(MUSIC_PATH)
        self.score_red = 0
        self.score_white = 0
        self.cube_value = 1
        self.cube_owner = ""
        self.is_crawford = False
        self.crawford_used = False
        self.game_number = 1
        self.match_winner_color = ""
        self._reset_smart_bot_search()
        self._start_new_game(initial=True)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active or self.status != "playing":
            return

        if self.turn_phase == TURN_PHASE_DOUBLING:
            responder = self._get_double_responder()
            if responder and responder.is_bot:
                BotHelper.process_bot_action(
                    responder,
                    lambda: _bot_respond_to_double(self, responder),
                    lambda action_id: self.execute_action(responder, action_id),
                )
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: BackgammonPlayer) -> str | None:
        if self.options.bot_strategy == "random" and self.turn_phase == TURN_PHASE_MOVING:
            moves = self._get_legal_submoves(player.color)
            if moves:
                return self.action_id_for_move(random.choice(moves))  # nosec B311
        return _bot_think(self, player)

    def action_id_for_move(self, move: BackgammonMove) -> str:
        source = "bar" if move.source == -1 else f"p{move.source}"
        destination = "off" if move.is_bear_off else f"p{move.destination}"
        return f"move_{source}_{destination}_{move.die_value}"

    def _clone_board(self, board: BackgammonBoard | None = None) -> BackgammonBoard:
        source = board or self.board
        return BackgammonBoard(
            points=list(source.points),
            bar_red=source.bar_red,
            bar_white=source.bar_white,
            off_red=source.off_red,
            off_white=source.off_white,
        )

    def _reset_smart_bot_search(self) -> None:
        self.smart_bot_search = None

    def _new_smart_bot_search_state(
        self, player: BackgammonPlayer
    ) -> BackgammonSmartSearchState:
        return BackgammonSmartSearchState(
            player_id=player.id,
            player_color=player.color,
            root_dice=list(self.remaining_dice),
            root_board=self._clone_board(),
            stack=[
                BackgammonSmartSearchNode(
                    prefix=[],
                    remaining_dice=list(self.remaining_dice),
                )
            ],
        )

    def _is_smart_bot_search_valid(self, player: BackgammonPlayer) -> bool:
        search = self.smart_bot_search
        return bool(
            search
            and self.current_player == player
            and self.turn_phase == TURN_PHASE_MOVING
            and search.player_id == player.id
            and search.player_color == player.color
            and search.root_dice == list(self.remaining_dice)
            and search.root_board == self.board
        )

    def _sync_turn_actions(self, player: Player, action_set: ActionSet | None = None) -> None:
        turn_set = action_set or self.get_action_set(player, "turn")
        if not turn_set:
            return
        turn_set.remove_by_prefix("move_")

        if (
            self.status == "playing"
            and self.turn_phase == TURN_PHASE_MOVING
            and isinstance(player, BackgammonPlayer)
            and not player.is_spectator
            and self.current_player == player
        ):
            for move in self._get_legal_submoves(player.color):
                turn_set.add(
                    Action(
                        id=self.action_id_for_move(move),
                        label="",
                        handler="_action_move_option",
                        is_enabled="_is_move_option_enabled",
                        is_hidden="_is_move_option_hidden",
                        get_label="_get_move_option_label",
                        show_in_actions_menu=False,
                    )
                )

        move_ids = [aid for aid in turn_set._order if aid.startswith("move_")]
        ordered = []
        for aid in ("accept_double", "drop_double", "offer_double", "roll_dice"):
            if turn_set.get_action(aid):
                ordered.append(aid)
        ordered.extend(move_ids)
        if turn_set.get_action("undo_move"):
            ordered.append("undo_move")
        turn_set._order = ordered

    def _sync_standard_actions(self, player: Player) -> None:
        standard_set = self.get_action_set(player, "standard")
        if standard_set:
            self._apply_standard_action_order(standard_set, self.get_user(player))

    def _apply_standard_action_order(self, action_set: ActionSet, user: "User | None") -> None:
        local_ids = ["read_board", "check_status", "check_pip", "check_cube", "check_dice"]
        action_set._order = [aid for aid in action_set._order if aid not in local_ids] + [
            aid for aid in local_ids if action_set.get_action(aid)
        ]
        if user and getattr(user, "client_type", "") == "web":
            new_order = [aid for aid in action_set._order if aid not in WEB_STANDARD_ORDER]
            for aid in WEB_STANDARD_ORDER:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

    def _start_new_game(self, *, initial: bool = False) -> None:
        self.board = BackgammonBoard(points=list(INITIAL_POINTS))
        self.turn_phase = TURN_PHASE_PRE_ROLL
        self.remaining_dice = []
        self.moves_this_turn = []
        self.pending_double_to = ""
        self.cube_value = 1
        self.cube_owner = ""
        self._reset_smart_bot_search()
        if not initial:
            self.broadcast_l(
                "backgammon-new-game",
                buffer="game",
                number=self.game_number,
            )
        if self.is_crawford:
            self.broadcast_l("backgammon-crawford", buffer="game")
        self._perform_opening_roll()

    def _perform_opening_roll(self) -> None:
        self._reset_smart_bot_search()
        red_player = self._get_player_by_color(COLOR_RED)
        white_player = self._get_player_by_color(COLOR_WHITE)
        if not red_player or not white_player:
            return

        while True:
            red_die = random.randint(1, 6)  # nosec B311
            white_die = random.randint(1, 6)  # nosec B311
            self.broadcast_l(
                "backgammon-opening-roll",
                buffer="game",
                red=red_player.name,
                white=white_player.name,
                red_die=red_die,
                white_die=white_die,
            )
            if red_die != white_die:
                break
            self.broadcast_l("backgammon-opening-tie", buffer="game", die=red_die)

        opener = red_player if red_die > white_die else white_player
        other = white_player if opener is red_player else red_player
        self.set_turn_players([opener, other])
        self.turn_phase = TURN_PHASE_MOVING
        self.remaining_dice = [max(red_die, white_die), min(red_die, white_die)]
        self.moves_this_turn = []
        self.pending_double_to = ""
        self.play_sound(SOUND_DICE.format(index=random.randint(1, 3)))  # nosec B311
        self.broadcast_l(
            "backgammon-opening-winner",
            buffer="game",
            player=opener.name,
            die1=self.remaining_dice[0],
            die2=self.remaining_dice[1],
        )
        self._handle_post_roll_state()
        self.rebuild_all_menus()
        self._jolt_relevant_bots()

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        if player != self.current_player:
            return
        self._reset_smart_bot_search()
        die1 = random.randint(1, 6)  # nosec B311
        die2 = random.randint(1, 6)  # nosec B311
        self.remaining_dice = [die1, die2] if die1 != die2 else [die1, die1, die1, die1]
        self.turn_phase = TURN_PHASE_MOVING
        self.moves_this_turn = []
        self.play_sound(SOUND_DICE.format(index=random.randint(1, 3)))  # nosec B311
        self.broadcast_l(
            "backgammon-roll",
            buffer="game",
            player=player.name,
            die1=die1,
            die2=die2,
        )
        self._handle_post_roll_state()
        self.rebuild_all_menus()
        self._jolt_relevant_bots()

    def _handle_post_roll_state(self) -> None:
        current = self._as_backgammon_player(self.current_player)
        if not current:
            return
        if not self._get_legal_submoves(current.color):
            self.broadcast_l("backgammon-no-moves", buffer="game", player=current.name)
            self._advance_to_next_turn()

    def _action_offer_double(self, player: Player, action_id: str) -> None:
        bg_player = self._as_backgammon_player(player)
        if not bg_player or not self._can_offer_double(bg_player):
            return
        self._reset_smart_bot_search()
        self.turn_phase = TURN_PHASE_DOUBLING
        self.pending_double_to = self._opponent_color(bg_player.color)
        self.broadcast_l(
            "backgammon-double-offered",
            buffer="game",
            player=bg_player.name,
            value=self.cube_value * 2,
        )
        self.rebuild_all_menus()
        self._jolt_relevant_bots()

    def _action_accept_double(self, player: Player, action_id: str) -> None:
        bg_player = self._as_backgammon_player(player)
        if not bg_player or bg_player.color != self.pending_double_to:
            return
        self._reset_smart_bot_search()
        self.cube_value *= 2
        self.cube_owner = bg_player.color
        self.turn_phase = TURN_PHASE_PRE_ROLL
        self.pending_double_to = ""
        self.broadcast_l(
            "backgammon-double-accepted",
            buffer="game",
            player=bg_player.name,
            value=self.cube_value,
        )
        self.rebuild_all_menus()
        self._jolt_relevant_bots()

    def _action_drop_double(self, player: Player, action_id: str) -> None:
        bg_player = self._as_backgammon_player(player)
        proposer = self._as_backgammon_player(self.current_player)
        if not bg_player or not proposer or bg_player.color != self.pending_double_to:
            return
        self._reset_smart_bot_search()
        self.broadcast_l(
            "backgammon-double-dropped",
            buffer="game",
            player=bg_player.name,
        )
        self._award_game(proposer.color, self.cube_value)

    def _action_move_option(self, player: Player, action_id: str) -> None:
        bg_player = self._as_backgammon_player(player)
        move = self._decode_move_action(action_id)
        if not bg_player or not move:
            return
        legal_moves = self._get_legal_submoves(bg_player.color)
        if move not in legal_moves:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-illegal-move", buffer="system")
            return

        self._reset_smart_bot_search()
        self._apply_move(move, bg_player.color)
        self.moves_this_turn.append(move)
        self.remaining_dice.remove(move.die_value)
        self._play_move_sound(move)
        self._announce_move(bg_player, move)

        if self._off_count(bg_player.color) >= 15:
            self._award_game(bg_player.color, self._game_points_for_winner(bg_player.color))
            return

        if not self._get_legal_submoves(bg_player.color):
            self._advance_to_next_turn()
        else:
            self.rebuild_all_menus()
            self._jolt_relevant_bots()

    def _action_undo_move(self, player: Player, action_id: str) -> None:
        bg_player = self._as_backgammon_player(player)
        if not bg_player or not self.moves_this_turn:
            return
        self._reset_smart_bot_search()
        move = self.moves_this_turn.pop()
        self._undo_move(move, bg_player.color)
        self.remaining_dice.append(move.die_value)
        self.remaining_dice.sort(reverse=True)
        user = self.get_user(player)
        if user:
            user.speak_l("backgammon-move-undone", buffer="game")
        self.rebuild_all_menus()

    def _action_read_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        viewer_color = self._viewer_color(player)
        lines = [Localization.get(user.locale, "backgammon-board-header")]
        lines.append(self._status_line(user.locale))
        lines.append(self._cube_line(user.locale))
        lines.append(self._score_line(user.locale))
        for point_index in range(23, -1, -1):
            point_number = self._point_number_for_player(point_index, viewer_color)
            lines.append(
                Localization.get(
                    user.locale,
                    "backgammon-board-point",
                    point=point_number,
                    state=self._describe_point_for_locale(point_index, user.locale),
                )
            )
        self.status_box(player, lines)

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(self._status_line(user.locale), buffer="game")

    def _action_check_pip(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        red = self._get_player_by_color(COLOR_RED)
        white = self._get_player_by_color(COLOR_WHITE)
        if user and red and white:
            user.speak_l(
                "backgammon-pip-line",
                buffer="game",
                red=red.name,
                red_pip=self._pip_count(COLOR_RED),
                white=white.name,
                white_pip=self._pip_count(COLOR_WHITE),
            )

    def _action_check_cube(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(self._cube_line(user.locale), buffer="game")

    def _action_check_dice(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not self.remaining_dice:
            user.speak_l("backgammon-dice-none", buffer="game")
            return
        dice_text = Localization.format_list_and(user.locale, [str(d) for d in self.remaining_dice])
        user.speak_l("backgammon-dice-line", buffer="game", dice=dice_text)

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(self._score_line(user.locale), buffer="game")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        red = self._get_player_by_color(COLOR_RED)
        white = self._get_player_by_color(COLOR_WHITE)
        lines = [Localization.get(user.locale, "backgammon-scores-header")]
        if red and white:
            lines.append(
                Localization.get(
                    user.locale,
                    "backgammon-score-detail",
                    player=red.name,
                    score=self.score_red,
                )
            )
            lines.append(
                Localization.get(
                    user.locale,
                    "backgammon-score-detail",
                    player=white.name,
                    score=self.score_white,
                )
            )
        lines.append(
            Localization.get(
                user.locale,
                "backgammon-score-target",
                points=self.options.match_length,
            )
        )
        self.status_box(player, lines)

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        current = self._as_backgammon_player(self.current_player)
        if not user or not current:
            return
        if self.turn_phase == TURN_PHASE_DOUBLING:
            responder = self._get_double_responder()
            if responder:
                user.speak_l(
                    "backgammon-waiting-for-double-response",
                    buffer="game",
                    player=current.name,
                    responder=responder.name,
                )
                return
        if self.turn_phase == TURN_PHASE_PRE_ROLL:
            user.speak_l("backgammon-turn-preroll", buffer="game", player=current.name)
            return
        user.speak_l("game-turn-start", buffer="game", player=current.name)

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player != self.current_player:
            return "action-not-your-turn"
        if self.turn_phase != TURN_PHASE_PRE_ROLL:
            return "backgammon-cannot-roll"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_roll_dice_enabled(player) is None else Visibility.HIDDEN

    def _is_offer_double_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        bg_player = self._as_backgammon_player(player)
        if not bg_player or player != self.current_player:
            return "action-not-your-turn"
        if not self._can_offer_double(bg_player):
            return "backgammon-cannot-double"
        return None

    def _is_offer_double_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_offer_double_enabled(player) is None else Visibility.HIDDEN

    def _is_accept_double_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        bg_player = self._as_backgammon_player(player)
        if not bg_player or self.turn_phase != TURN_PHASE_DOUBLING:
            return "backgammon-no-double-pending"
        if bg_player.color != self.pending_double_to:
            return "backgammon-no-double-pending"
        return None

    def _is_accept_double_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_accept_double_enabled(player) is None else Visibility.HIDDEN

    def _is_drop_double_enabled(self, player: Player) -> str | None:
        return self._is_accept_double_enabled(player)

    def _is_drop_double_hidden(self, player: Player) -> Visibility:
        return self._is_accept_double_hidden(player)

    def _is_undo_move_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player != self.current_player:
            return "action-not-your-turn"
        if self.turn_phase != TURN_PHASE_MOVING or not self.moves_this_turn:
            return "backgammon-no-move-to-undo"
        return None

    def _is_undo_move_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_undo_move_enabled(player) is None else Visibility.HIDDEN

    def _is_move_option_enabled(self, player: Player, action_id: str = "") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player != self.current_player:
            return "action-not-your-turn"
        if self.turn_phase != TURN_PHASE_MOVING:
            return "action-not-available"
        move = self._decode_move_action(action_id)
        bg_player = self._as_backgammon_player(player)
        if not move or not bg_player or move not in self._get_legal_submoves(bg_player.color):
            return "backgammon-illegal-move"
        return None

    def _is_move_option_hidden(self, player: Player, action_id: str = "") -> Visibility:
        return Visibility.VISIBLE if self._is_move_option_enabled(player, action_id) is None else Visibility.HIDDEN

    def _get_move_option_label(self, player: Player, action_id: str) -> str:
        move = self._decode_move_action(action_id)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        viewer_color = self._viewer_color(player)
        if not move:
            return action_id
        source = Localization.get(locale, "backgammon-bar") if move.source == -1 else str(
            self._point_number_for_player(move.source, viewer_color)
        )
        if move.is_bear_off:
            return Localization.get(
                locale,
                "backgammon-move-label-bear-off",
                source=source,
                die=move.die_value,
            )
        destination = self._point_number_for_player(move.destination, viewer_color)
        key = "backgammon-move-label-hit" if move.is_hit else "backgammon-move-label"
        return Localization.get(locale, key, source=source, dest=destination, die=move.die_value)

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_read_board_hidden(self, player: Player) -> Visibility:
        return self._web_turn_info_visibility(player)

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        return self._web_turn_info_visibility(player)

    def _is_check_pip_hidden(self, player: Player) -> Visibility:
        return self._web_turn_info_visibility(player)

    def _is_check_cube_hidden(self, player: Player) -> Visibility:
        return self._web_turn_info_visibility(player)

    def _is_check_dice_hidden(self, player: Player) -> Visibility:
        return self._web_turn_info_visibility(player)

    def _web_turn_info_visibility(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if (
            self.status == "playing"
            and user
            and getattr(user, "client_type", "") == "web"
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def _advance_to_next_turn(self) -> None:
        self._reset_smart_bot_search()
        self.remaining_dice = []
        self.moves_this_turn = []
        self.turn_phase = TURN_PHASE_PRE_ROLL
        self.pending_double_to = ""
        self.advance_turn(announce=False)
        self.announce_turn(turn_sound=SOUND_TURN)
        self._jolt_relevant_bots()

    def _award_game(self, winner_color: str, points: int) -> None:
        winner = self._get_player_by_color(winner_color)
        if not winner:
            return
        self.play_sound(SOUND_WIN)
        if winner_color == COLOR_RED:
            self.score_red += points
        else:
            self.score_white += points

        self.broadcast_l(
            "backgammon-game-won",
            buffer="game",
            player=winner.name,
            points=points,
        )

        if self._score_for_color(winner_color) >= self.options.match_length:
            self._finish_match(winner_color)
            return

        if self.is_crawford:
            self.is_crawford = False
        elif not self.crawford_used and (
            self.score_red == self.options.match_length - 1
            or self.score_white == self.options.match_length - 1
        ):
            self.is_crawford = True
            self.crawford_used = True

        self.game_number += 1
        self._start_new_game()

    def _finish_match(self, winner_color: str) -> None:
        self.match_winner_color = winner_color
        winner = self._get_player_by_color(winner_color)
        loser = self._get_player_by_color(self._opponent_color(winner_color))
        if winner:
            self.broadcast_l("backgammon-match-winner", buffer="game", player=winner.name)
        for participant in self.players:
            user = self.get_user(participant)
            if not user:
                continue
            if isinstance(participant, BackgammonPlayer) and participant.color == winner_color:
                user.play_sound(SOUND_MATCH_WIN)
            elif isinstance(participant, BackgammonPlayer) and loser and participant.color == loser.color:
                user.play_sound(SOUND_MATCH_LOSE)
            else:
                user.play_sound(SOUND_MATCH_LOSE)
        self.finish_game()

    def build_game_result(self) -> GameResult:
        winner = self._get_player_by_color(self.match_winner_color) if self.match_winner_color else None
        red_player = self._get_player_by_color(COLOR_RED)
        white_player = self._get_player_by_color(COLOR_WHITE)
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
                "score_red": self.score_red,
                "score_white": self.score_white,
                "match_length": self.options.match_length,
                "red_name": red_player.name if red_player else "Red",
                "white_name": white_player.name if white_player else "White",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        data = result.custom_data
        return [
            Localization.get(
                locale,
                "backgammon-end-score",
                red=data.get("red_name", "Red"),
                red_score=data.get("score_red", 0),
                white=data.get("white_name", "White"),
                white_score=data.get("score_white", 0),
                match_length=data.get("match_length", 1),
            )
        ]

    def _announce_move(self, mover: BackgammonPlayer, move: BackgammonMove) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            viewer_color = self._viewer_color(player)
            source = Localization.get(user.locale, "backgammon-bar") if move.source == -1 else str(
                self._point_number_for_player(move.source, viewer_color)
            )
            if move.is_bear_off:
                user.speak_l(
                    "backgammon-announcement-bear-off",
                    buffer="game",
                    player=mover.name,
                    source=source,
                    die=move.die_value,
                )
                continue
            destination = self._point_number_for_player(move.destination, viewer_color)
            message_key = "backgammon-announcement-hit" if move.is_hit else "backgammon-announcement-move"
            user.speak_l(
                message_key,
                buffer="game",
                player=mover.name,
                source=source,
                dest=destination,
                die=move.die_value,
            )

    def _play_move_sound(self, move: BackgammonMove) -> None:
        if move.is_bear_off:
            self.play_sound(SOUND_BEAR_OFF)
        elif move.is_hit:
            self.play_sound(SOUND_HIT.format(index=random.randint(1, 2)))  # nosec B311
        else:
            self.play_sound(SOUND_STEP.format(index=random.randint(1, 3)))  # nosec B311

    def _viewer_color(self, player: Player) -> str:
        if isinstance(player, BackgammonPlayer):
            return player.color
        return COLOR_RED

    def _status_line(self, locale: str) -> str:
        red = self._get_player_by_color(COLOR_RED)
        white = self._get_player_by_color(COLOR_WHITE)
        return Localization.get(
            locale,
            "backgammon-status-line",
            red=red.name if red else "Red",
            red_bar=self.board.bar_red,
            red_off=self.board.off_red,
            white=white.name if white else "White",
            white_bar=self.board.bar_white,
            white_off=self.board.off_white,
        )

    def _cube_line(self, locale: str) -> str:
        owner = self._get_player_by_color(self.cube_owner)
        owner_name = owner.name if owner else Localization.get(locale, "backgammon-cube-centered")
        return Localization.get(
            locale,
            "backgammon-cube-line",
            value=self.cube_value,
            owner=owner_name,
            can_double=Localization.get(
                locale,
                "backgammon-cube-yes" if self._can_anyone_double() else "backgammon-cube-no",
            ),
        )

    def _score_line(self, locale: str) -> str:
        red = self._get_player_by_color(COLOR_RED)
        white = self._get_player_by_color(COLOR_WHITE)
        return Localization.get(
            locale,
            "backgammon-score-line",
            red=red.name if red else "Red",
            red_score=self.score_red,
            white=white.name if white else "White",
            white_score=self.score_white,
            match_length=self.options.match_length,
        )

    def _describe_point_for_locale(self, point_index: int, locale: str) -> str:
        value = self.board.points[point_index]
        if value == 0:
            return Localization.get(locale, "backgammon-point-empty")
        owner_color = COLOR_RED if value > 0 else COLOR_WHITE
        owner_name = self._get_player_by_color(owner_color)
        return Localization.get(
            locale,
            "backgammon-point-occupied",
            player=owner_name.name if owner_name else owner_color.title(),
            count=abs(value),
        )

    def _get_legal_submoves(self, color: str) -> list[BackgammonMove]:
        sequences = self._generate_legal_sequences(color, list(self.remaining_dice))
        first_moves: list[BackgammonMove] = []
        for sequence in sequences:
            if sequence and sequence[0] not in first_moves:
                first_moves.append(sequence[0])
        return first_moves

    def _generate_legal_sequences(self, color: str, dice_values: list[int]) -> list[list[BackgammonMove]]:
        sequences = self._enumerate_sequences(color, dice_values)
        if not sequences:
            return []

        max_length = max(len(sequence) for sequence in sequences)
        sequences = [sequence for sequence in sequences if len(sequence) == max_length]
        if len(dice_values) == 2 and dice_values[0] != dice_values[1] and max_length == 1:
            highest = max(dice_values)
            sequences = [sequence for sequence in sequences if sequence and sequence[0].die_value == highest]
        return sequences

    def _enumerate_sequences(self, color: str, dice_values: list[int]) -> list[list[BackgammonMove]]:
        if not dice_values:
            return [[]]

        sequences: list[list[BackgammonMove]] = [[]]
        found_move = False
        tried_values: set[int] = set()

        for die_value in list(dice_values):
            if die_value in tried_values:
                continue
            tried_values.add(die_value)
            legal_moves = self._generate_moves_for_die(color, die_value)
            if not legal_moves:
                continue
            found_move = True
            remaining = list(dice_values)
            remaining.remove(die_value)
            for move in legal_moves:
                self._apply_move(move, color)
                tails = self._enumerate_sequences(color, remaining)
                self._undo_move(move, color)
                for tail in tails:
                    sequences.append([move, *tail])

        if not found_move:
            return [[]]
        return sequences

    def _generate_moves_for_die(
        self,
        color: str,
        die_value: int,
        board: BackgammonBoard | None = None,
    ) -> list[BackgammonMove]:
        sign = self._color_sign(color)
        moves: list[BackgammonMove] = []
        active_board = board or self.board

        if self._bar_count(color, active_board) > 0:
            destination = 24 - die_value if color == COLOR_RED else die_value - 1
            if self._can_land_on_point(color, destination, active_board):
                moves.append(
                    BackgammonMove(
                        source=-1,
                        destination=destination,
                        die_value=die_value,
                        is_hit=self._is_hit_point(color, destination, active_board),
                    )
                )
            return moves

        can_bear_off = self._all_checkers_in_home(color, active_board)
        for point_index, value in enumerate(active_board.points):
            if value * sign <= 0:
                continue

            destination = point_index - die_value if color == COLOR_RED else point_index + die_value
            if color == COLOR_RED and destination < 0:
                if can_bear_off and (
                    destination == -1 or self._is_furthest_checker(color, point_index, active_board)
                ):
                    moves.append(
                        BackgammonMove(
                            source=point_index,
                            destination=24,
                            die_value=die_value,
                            is_bear_off=True,
                        )
                    )
                continue
            if color == COLOR_WHITE and destination > 23:
                if can_bear_off and (
                    destination == 24 or self._is_furthest_checker(color, point_index, active_board)
                ):
                    moves.append(
                        BackgammonMove(
                            source=point_index,
                            destination=24,
                            die_value=die_value,
                            is_bear_off=True,
                        )
                    )
                continue
            if 0 <= destination <= 23 and self._can_land_on_point(color, destination, active_board):
                moves.append(
                    BackgammonMove(
                        source=point_index,
                        destination=destination,
                        die_value=die_value,
                        is_hit=self._is_hit_point(color, destination, active_board),
                    )
                )
        return moves

    def _can_land_on_point(
        self,
        color: str,
        point_index: int,
        board: BackgammonBoard | None = None,
    ) -> bool:
        sign = self._color_sign(color)
        value = (board or self.board).points[point_index]
        return value * -sign <= 1

    def _is_hit_point(
        self,
        color: str,
        point_index: int,
        board: BackgammonBoard | None = None,
    ) -> bool:
        sign = self._color_sign(color)
        value = (board or self.board).points[point_index]
        return value * -sign == 1

    def _apply_move(
        self,
        move: BackgammonMove,
        color: str,
        board: BackgammonBoard | None = None,
    ) -> None:
        sign = self._color_sign(color)
        opponent = self._opponent_color(color)
        active_board = board or self.board

        if move.source == -1:
            self._set_bar(color, self._bar_count(color, active_board) - 1, active_board)
        else:
            active_board.points[move.source] -= sign

        if move.is_bear_off:
            self._set_off(color, self._off_count(color, active_board) + 1, active_board)
            return

        if move.is_hit:
            active_board.points[move.destination] += sign
            self._set_bar(opponent, self._bar_count(opponent, active_board) + 1, active_board)
        active_board.points[move.destination] += sign

    def _undo_move(
        self,
        move: BackgammonMove,
        color: str,
        board: BackgammonBoard | None = None,
    ) -> None:
        sign = self._color_sign(color)
        opponent = self._opponent_color(color)
        active_board = board or self.board

        if move.is_bear_off:
            self._set_off(color, self._off_count(color, active_board) - 1, active_board)
        else:
            active_board.points[move.destination] -= sign
            if move.is_hit:
                active_board.points[move.destination] -= sign
                self._set_bar(opponent, self._bar_count(opponent, active_board) - 1, active_board)

        if move.source == -1:
            self._set_bar(color, self._bar_count(color, active_board) + 1, active_board)
        else:
            active_board.points[move.source] += sign

    def _game_points_for_winner(self, winner_color: str) -> int:
        loser_color = self._opponent_color(winner_color)
        multiplier = 1
        if self._off_count(loser_color) == 0:
            multiplier = 2
            if self._bar_count(loser_color) > 0 or any(
                self.board.points[index] * self._color_sign(loser_color) > 0
                for index in self._winner_home_indices(winner_color)
            ):
                multiplier = 3
        return self.cube_value * multiplier

    def _winner_home_indices(self, winner_color: str) -> range:
        return range(0, 6) if winner_color == COLOR_RED else range(18, 24)

    def _all_checkers_in_home(
        self,
        color: str,
        board: BackgammonBoard | None = None,
    ) -> bool:
        active_board = board or self.board
        if self._bar_count(color, active_board) > 0:
            return False
        sign = self._color_sign(color)
        for index, value in enumerate(active_board.points):
            if value * sign <= 0:
                continue
            if color == COLOR_RED and index > 5:
                return False
            if color == COLOR_WHITE and index < 18:
                return False
        return True

    def _is_furthest_checker(
        self,
        color: str,
        point_index: int,
        board: BackgammonBoard | None = None,
    ) -> bool:
        sign = self._color_sign(color)
        active_board = board or self.board
        if color == COLOR_RED:
            for index in range(point_index + 1, 6):
                if active_board.points[index] * sign > 0:
                    return False
        else:
            for index in range(18, point_index):
                if active_board.points[index] * sign > 0:
                    return False
        return True

    def _is_home_board_point(self, color: str, point_index: int) -> bool:
        return point_index in self._winner_home_indices(color)

    def _is_opponent_home_board_point(self, color: str, point_index: int) -> bool:
        return point_index in self._winner_home_indices(self._opponent_color(color))

    def _decode_move_action(self, action_id: str) -> BackgammonMove | None:
        if not action_id.startswith("move_"):
            return None
        try:
            _prefix, raw_source, raw_destination, raw_die = action_id.split("_", 3)
        except ValueError:
            return None
        source = -1 if raw_source == "bar" else int(raw_source.removeprefix("p"))
        is_bear_off = raw_destination == "off"
        destination = 24 if is_bear_off else int(raw_destination.removeprefix("p"))
        die_value = int(raw_die)
        current = self._as_backgammon_player(self.current_player)
        current_color = current.color if current else COLOR_RED
        return BackgammonMove(
            source=source,
            destination=destination,
            die_value=die_value,
            is_hit=(not is_bear_off and self._is_hit_point(current_color, destination)),
            is_bear_off=is_bear_off,
        )

    def _can_offer_double(self, player: BackgammonPlayer) -> bool:
        if self.options.match_length <= 1:
            return False
        if self.is_crawford:
            return False
        if self.turn_phase != TURN_PHASE_PRE_ROLL:
            return False
        if self.current_player != player:
            return False
        return self.cube_owner in ("", player.color)

    def _can_anyone_double(self) -> bool:
        if self.options.match_length <= 1 or self.is_crawford:
            return False
        current = self._as_backgammon_player(self.current_player)
        return bool(current and self._can_offer_double(current))

    def _pip_count(self, color: str, board: BackgammonBoard | None = None) -> int:
        sign = self._color_sign(color)
        active_board = board or self.board
        total = self._bar_count(color, active_board) * 25
        for index, value in enumerate(active_board.points):
            if value * sign <= 0:
                continue
            count = abs(value)
            total += count * (index + 1 if color == COLOR_RED else 24 - index)
        return total

    def _get_player_by_color(self, color: str) -> BackgammonPlayer | None:
        for player in self.players:
            if isinstance(player, BackgammonPlayer) and player.color == color:
                return player
        return None

    def _get_double_responder(self) -> BackgammonPlayer | None:
        return self._get_player_by_color(self.pending_double_to) if self.pending_double_to else None

    def _as_backgammon_player(self, player: Player | None) -> BackgammonPlayer | None:
        return player if isinstance(player, BackgammonPlayer) else None

    def _point_number_for_player(self, point_index: int, color: str) -> int:
        return point_index + 1 if color == COLOR_RED else 24 - point_index

    def _opponent_color(self, color: str) -> str:
        return COLOR_WHITE if color == COLOR_RED else COLOR_RED

    def _color_sign(self, color: str) -> int:
        return 1 if color == COLOR_RED else -1

    def _bar_count(self, color: str, board: BackgammonBoard | None = None) -> int:
        active_board = board or self.board
        return active_board.bar_red if color == COLOR_RED else active_board.bar_white

    def _off_count(self, color: str, board: BackgammonBoard | None = None) -> int:
        active_board = board or self.board
        return active_board.off_red if color == COLOR_RED else active_board.off_white

    def _set_bar(self, color: str, count: int, board: BackgammonBoard | None = None) -> None:
        active_board = board or self.board
        if color == COLOR_RED:
            active_board.bar_red = count
        else:
            active_board.bar_white = count

    def _set_off(self, color: str, count: int, board: BackgammonBoard | None = None) -> None:
        active_board = board or self.board
        if color == COLOR_RED:
            active_board.off_red = count
        else:
            active_board.off_white = count

    def _score_for_color(self, color: str) -> int:
        return self.score_red if color == COLOR_RED else self.score_white

    def _jolt_relevant_bots(self) -> None:
        if self.turn_phase == TURN_PHASE_DOUBLING:
            responder = self._get_double_responder()
            if responder and responder.is_bot:
                BotHelper.jolt_bot(responder, ticks=random.randint(8, 16))  # nosec B311
            return
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(8, 16))  # nosec B311
