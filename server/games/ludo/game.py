"""
Ludo Game Implementation.

Classic board game: race four tokens from yard, around the track, and into home.
Roll a 6 to enter, capture opponents on unsafe squares, consecutive-6 penalty.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, IntOption, BoolOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_think


# Board constants
TRACK_LENGTH = 52
HOME_COLUMN_LENGTH = 6
SAFE_SQUARES = [9, 22, 35, 48]
COLOR_STARTS = {"red": 1, "blue": 14, "green": 27, "yellow": 40}
COLOR_ENTRIES = {"red": 51, "blue": 12, "green": 25, "yellow": 38}
ALL_START_POSITIONS = set(COLOR_STARTS.values())
PLAYER_COLORS = ["red", "blue", "green", "yellow"]

# Sound constants
NUM_STEP_SOUNDS = 3
NUM_DICE_SOUNDS = 3
NUM_TOKEN_SOUNDS = 10
NUM_CAPTURE_SOUNDS = 2

# Timing constants (20 ticks = 1 second)
STEP_DELAY_START = 3   # 150ms before first step
STEP_INTERVAL = 2      # 100ms between steps


@dataclass
class LudoToken:
    """A single Ludo token."""

    state: str = "yard"  # yard | track | home_column | finished
    position: int = 0
    token_number: int = 1


@dataclass
class LudoPlayer(Player):
    """Player state for Ludo."""

    color: str = ""
    tokens: list[LudoToken] = field(default_factory=list)
    finished_count: int = 0
    move_options: dict[int, str] = field(default_factory=dict)


@dataclass
class LudoOptions(GameOptions):
    """Options for Ludo."""

    max_consecutive_sixes: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=5,
            value_key="max_consecutive_sixes",
            label="ludo-set-max-sixes",
            prompt="ludo-enter-max-sixes",
            change_msg="ludo-option-changed-max-sixes",
        )
    )
    safe_start_squares: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="ludo-set-safe-start-squares",
            change_msg="ludo-option-changed-safe-start-squares",
        )
    )


@dataclass
@register_game
class LudoGame(Game):
    """Ludo: race four tokens around the board and into home."""

    players: list[LudoPlayer] = field(default_factory=list)
    options: LudoOptions = field(default_factory=LudoOptions)

    last_roll: int = 0
    consecutive_sixes: int = 0
    extra_turn: bool = False
    turn_start_state: dict | None = None
    is_rolling: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Ludo"

    @classmethod
    def get_type(cls) -> str:
        return "ludo"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> LudoPlayer:
        return LudoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ======================================================================
    # Action sets
    # ======================================================================

    def create_turn_action_set(self, player: LudoPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "ludo-roll-die"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
                show_in_actions_menu=False,
            )
        )
        for token_number in range(1, 5):
            action_set.add(
                Action(
                    id=f"move_token_{token_number}",
                    label=Localization.get(locale, "ludo-move-token"),
                    handler="_action_move_token",
                    is_enabled=f"_is_move_token_{token_number}_enabled",
                    is_hidden=f"_is_move_token_{token_number}_hidden",
                    get_label="_get_move_token_label",
                    show_in_actions_menu=False,
                )
            )
        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_board", "check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: LudoPlayer) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action = Action(
            id="check_board",
            label=Localization.get(locale, "ludo-check-board"),
            handler="_action_check_board",
            is_enabled="_is_check_board_enabled",
            is_hidden="_is_check_board_hidden",
            include_spectators=True,
        )
        action_set.add(action)

        # WEB-SPECIFIC: Reorder for Web Clients
        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)
        else:
            # Desktop: put check_board last in standard actions
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.append(action.id)

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        user = None
        if hasattr(self, "host_username") and self.host_username:
            player = self.get_player_by_name(self.host_username)
            if player:
                user = self.get_user(player)
        locale = user.locale if user else "en"

        self.define_keybind(
            "r",
            Localization.get(locale, "ludo-roll-die"),
            ["roll_dice"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "v",
            Localization.get(locale, "ludo-check-board"),
            ["check_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        for token_number in range(1, 5):
            self.define_keybind(
                str(token_number),
                Localization.get(locale, "ludo-move-token-n", token=token_number),
                [f"move_token_{token_number}"],
                state=KeybindState.ACTIVE,
            )

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_board_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ======================================================================
    # Game lifecycle
    # ======================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.last_roll = 0
        self.cancel_all_sequences()

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Individual scoring via TeamManager
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])
        self._team_manager.reset_all_scores()

        # Assign colors and initialize tokens
        for i, player in enumerate(active_players):
            player.color = PLAYER_COLORS[i]
            player.tokens = [
                LudoToken(state="yard", position=0, token_number=j + 1)
                for j in range(4)
            ]
            player.finished_count = 0
            player.move_options = {}

        self.play_music("game_pig/mus.ogg")
        self._start_turn(new_turn=True)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.game_active:
            return
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        return bot_think(self, player)  # type: ignore[arg-type]

    def _find_player_by_id(self, player_id: str) -> LudoPlayer | None:
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        _ = sequence_id
        if callback_id == "move":
            player = self._find_player_by_id(payload["player_id"])
            if not player:
                return
            token = player.tokens[payload["token_number"] - 1]
            self._move_token(player, token, self.last_roll)
            return

        if callback_id == "after_move":
            self.is_rolling = False
            player = self._find_player_by_id(payload["player_id"])
            if player:
                self._after_move(player)
            return

        if callback_id == "no_moves":
            self.is_rolling = False
            player = self._find_player_by_id(payload["player_id"])
            if player:
                self.broadcast_personal_l(
                    player,
                    "ludo-you-no-moves",
                    "ludo-no-moves",
                    buffer="game",
                )
            self._end_turn()

    # ======================================================================
    # Turn flow
    # ======================================================================

    def _start_turn(self, new_turn: bool) -> None:
        player = self.current_player
        self.cancel_sequences_by_tag("turn_flow")
        self.is_rolling = False
        if isinstance(player, LudoPlayer):
            player.move_options = {}
        if new_turn:
            self.consecutive_sixes = 0
            self.turn_start_state = self._save_turn_state()
        self.extra_turn = False
        if player and player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))  # nosec B311
        self.announce_turn()
        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        self.cancel_sequences_by_tag("turn_flow")
        if self.extra_turn:
            self._start_turn(new_turn=False)
            return
        self.turn_start_state = None
        self.advance_turn(announce=False)
        self._start_turn(new_turn=True)

    # ======================================================================
    # Turn state save/restore (for consecutive-6 rollback)
    # ======================================================================

    def _save_turn_state(self) -> dict:
        state: dict = {}
        for player in self.get_active_players():
            state[player.id] = {
                "finished_count": player.finished_count,
                "tokens": [
                    {
                        "state": t.state,
                        "position": t.position,
                        "token_number": t.token_number,
                    }
                    for t in player.tokens
                ],
            }
        return state

    def _restore_turn_state(self, state: dict) -> None:
        for player in self.get_active_players():
            saved = state.get(player.id)
            if not saved:
                continue
            player.finished_count = saved["finished_count"]
            for i, saved_token in enumerate(saved["tokens"]):
                token = player.tokens[i]
                token.state = saved_token["state"]
                token.position = saved_token["position"]
                token.token_number = saved_token["token_number"]
        self._sync_team_scores()

    def _sync_team_scores(self) -> None:
        self._team_manager.reset_all_scores()
        for player in self.get_active_players():
            self._team_manager.add_to_team_score(player.name, player.finished_count)

    # ======================================================================
    # Board helpers
    # ======================================================================

    def _get_start_position(self, player: LudoPlayer) -> int:
        return COLOR_STARTS[player.color]

    def _get_home_entry_position(self, player: LudoPlayer) -> int:
        return COLOR_ENTRIES[player.color]

    def _is_safe_square(self, position: int, player: LudoPlayer) -> bool:
        if position in SAFE_SQUARES:
            return True
        if self.options.safe_start_squares and position in ALL_START_POSITIONS:
            return True
        return False

    def _get_token_at_position(
        self, position: int, exclude_player: LudoPlayer
    ) -> tuple[LudoToken | None, LudoPlayer | None]:
        tokens_at_position = self._get_tokens_at_position(position, exclude_player)
        if tokens_at_position:
            return tokens_at_position[0]
        return None, None

    def _get_tokens_at_position(
        self, position: int, exclude_player: LudoPlayer
    ) -> list[tuple[LudoToken, LudoPlayer]]:
        tokens_at_position: list[tuple[LudoToken, LudoPlayer]] = []
        for player in self.get_active_players():
            if player == exclude_player:
                continue
            for token in player.tokens:
                if token.state == "track" and token.position == position:
                    tokens_at_position.append((token, player))
        return tokens_at_position

    def _can_token_move(self, token: LudoToken, roll: int) -> bool:
        if token.state == "finished":
            return False
        if token.state == "yard":
            return roll == 6
        if token.state == "track":
            return True
        if token.state == "home_column":
            return token.position + roll <= HOME_COLUMN_LENGTH
        return False

    def _get_moveable_tokens(self, player: LudoPlayer, roll: int) -> list[tuple[int, LudoToken]]:
        moveable = []
        for i, token in enumerate(player.tokens):
            if self._can_token_move(token, roll):
                moveable.append((i, token))
        return moveable

    def _describe_token(self, token: LudoToken, locale: str) -> str:
        if token.state == "yard":
            return Localization.get(locale, "ludo-token-yard", token=token.token_number)
        if token.state == "track":
            return Localization.get(
                locale, "ludo-token-track", token=token.token_number, position=token.position
            )
        if token.state == "home_column":
            return Localization.get(
                locale,
                "ludo-token-home",
                token=token.token_number,
                position=token.position,
                total=HOME_COLUMN_LENGTH,
            )
        return Localization.get(locale, "ludo-token-finished", token=token.token_number)

    def _token_index_from_action(self, action_id: str) -> int | None:
        if action_id.startswith("move_token_"):
            try:
                token_number = int(action_id.split("_")[-1])
            except ValueError:
                return None
            if 1 <= token_number <= 4:
                return token_number - 1
        return None

    # ======================================================================
    # Capture logic
    # ======================================================================

    def _check_capture(self, player: LudoPlayer, token: LudoToken) -> None:
        if token.state != "track":
            return
        if self._is_safe_square(token.position, player):
            return
        captured_entries = self._get_tokens_at_position(token.position, player)
        if captured_entries:
            captured_by_player: dict[str, tuple[LudoPlayer, list[LudoToken]]] = {}
            for captured_token, captured_player in captured_entries:
                player_entry = captured_by_player.setdefault(
                    captured_player.id,
                    (captured_player, []),
                )
                player_entry[1].append(captured_token)

            for captured_player, captured_tokens in captured_by_player.values():
                for captured_token in captured_tokens:
                    captured_token.state = "yard"
                    captured_token.position = 0

                self.broadcast_l(
                    "ludo-captures",
                    buffer="game",
                    player=player.name,
                    color=player.color,
                    captured_player=captured_player.name,
                    captured_color=captured_player.color,
                    count=len(captured_tokens),
                )
                self.play_sound(
                    f"game_chess/capture{random.randint(1, NUM_CAPTURE_SOUNDS)}.ogg"  # nosec B311
                )

    # ======================================================================
    # is_enabled / is_hidden callbacks
    # ======================================================================

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        if self.is_rolling:
            return "action-not-available"
        ludo_player: LudoPlayer = player  # type: ignore
        if ludo_player.move_options:
            return "action-not-available"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        if self.is_rolling:
            return Visibility.HIDDEN
        ludo_player: LudoPlayer = player  # type: ignore
        if ludo_player.move_options:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_token_enabled(self, player: Player, token_index: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        if self.is_rolling:
            return "action-not-available"
        ludo_player: LudoPlayer = player  # type: ignore
        if token_index not in ludo_player.move_options:
            return "action-not-available"
        return None

    def _is_move_token_1_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 0)

    def _is_move_token_2_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 1)

    def _is_move_token_3_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 2)

    def _is_move_token_4_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 3)

    def _is_move_token_hidden(self, player: Player, token_index: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        if self.is_rolling:
            return Visibility.HIDDEN
        ludo_player: LudoPlayer = player  # type: ignore
        if token_index not in ludo_player.move_options:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_token_1_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 0)

    def _is_move_token_2_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 1)

    def _is_move_token_3_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 2)

    def _is_move_token_4_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 3)

    def _get_move_token_label(self, player: Player, action_id: str) -> str:
        ludo_player: LudoPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        token_index = self._token_index_from_action(action_id)
        if token_index is None:
            return Localization.get(locale, "ludo-move-token")
        label = ludo_player.move_options.get(token_index)
        if label:
            return label
        return Localization.get(locale, "ludo-move-token")

    def _is_check_board_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "not-started"
        return None

    # ======================================================================
    # Action handlers
    # ======================================================================

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        ludo_player: LudoPlayer = player  # type: ignore

        self.last_roll = random.randint(1, 6)  # nosec B311
        self.is_rolling = True
        dice_sound = f"game_squares/diceroll{random.randint(1, NUM_DICE_SOUNDS)}.ogg"  # nosec B311
        self.broadcast_personal_l(
            player,
            "ludo-you-roll",
            "ludo-roll",
            buffer="game",
            roll=self.last_roll,
        )

        moveable = self._get_moveable_tokens(ludo_player, self.last_roll)
        if not moveable:
            # Queue no-moves event after a brief pause for the dice sound
            self.start_sequence(
                "turn_flow",
                [
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(dice_sound)],
                        delay_after_ticks=10,
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "no_moves",
                                {"player_id": player.id},
                            )
                        ]
                    ),
                ],
                tag="turn_flow",
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            self.rebuild_all_menus()
            return

        if len(moveable) == 1:
            self._start_move_sequence(
                ludo_player,
                moveable[0][1],
                include_dice_sound=dice_sound,
            )
            self.rebuild_all_menus()
            return

        # Multiple tokens can move — present choice (is_rolling stays True
        # but we clear it so player can interact with move_options)
        self.is_rolling = False
        self.play_sound(dice_sound)
        user = self.get_user(ludo_player)
        locale = user.locale if user else "en"
        ludo_player.move_options = {
            idx: self._describe_token(token, locale) for idx, token in moveable
        }
        if user:
            user.speak_l("ludo-select-token", buffer="game")
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))  # nosec B311
        self.rebuild_all_menus()

    def _action_move_token(self, player: Player, action_id: str) -> None:
        ludo_player: LudoPlayer = player  # type: ignore
        token_index = self._token_index_from_action(action_id)
        if token_index is None or token_index not in ludo_player.move_options:
            return
        ludo_player.move_options = {}
        self.is_rolling = True
        token = ludo_player.tokens[token_index]
        self._start_move_sequence(ludo_player, token)
        self.rebuild_all_menus()

    def _schedule_move(self, player: LudoPlayer, token: LudoToken) -> None:
        """Backward-compatible wrapper around the shared sequence runner."""
        self._start_move_sequence(player, token)

    def _build_move_sequence(
        self,
        player: LudoPlayer,
        token: LudoToken,
        *,
        include_dice_sound: str | None = None,
    ) -> list[SequenceBeat]:
        beats: list[SequenceBeat] = []
        if include_dice_sound:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(include_dice_sound)],
                    delay_after_ticks=STEP_DELAY_START,
                )
            )
        else:
            beats.append(SequenceBeat.pause(STEP_DELAY_START))

        if token.state == "yard":
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            f"game_squares/token{random.randint(1, NUM_TOKEN_SOUNDS)}.ogg"  # nosec B311
                        )
                    ],
                    delay_after_ticks=4,
                )
            )
        else:
            for _ in range(self.last_roll):
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(
                                f"game_squares/step{random.randint(1, NUM_STEP_SOUNDS)}.ogg"  # nosec B311
                            )
                        ],
                        delay_after_ticks=STEP_INTERVAL,
                    )
                )

        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "move",
                        {"player_id": player.id, "token_number": token.token_number},
                    )
                ],
                delay_after_ticks=2,
            )
        )
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "after_move",
                        {"player_id": player.id},
                    )
                ]
            )
        )
        return beats

    def _start_move_sequence(
        self,
        player: LudoPlayer,
        token: LudoToken,
        *,
        include_dice_sound: str | None = None,
    ) -> None:
        self.start_sequence(
            "turn_flow",
            self._build_move_sequence(player, token, include_dice_sound=include_dice_sound),
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_check_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale

        lines: list[str] = []
        for p in self.get_active_players():
            lines.append(
                Localization.get(
                    locale,
                    "ludo-board-player",
                    player=p.name,
                    color=p.color,
                    finished=p.finished_count,
                )
            )
            for token in p.tokens:
                lines.append(self._describe_token(token, locale))
        if self.last_roll > 0:
            lines.append(Localization.get(locale, "ludo-last-roll", roll=self.last_roll))

        self.status_box(player, lines)

    # ======================================================================
    # Movement / resolution
    # ======================================================================

    def _move_token(self, player: LudoPlayer, token: LudoToken, spaces: int) -> None:
        if token.state == "yard":
            token.state = "track"
            token.position = self._get_start_position(player)
            self.broadcast_l(
                "ludo-enter-board",
                buffer="game",
                player=player.name,
                color=player.color,
                token=token.token_number,
            )
            self._check_capture(player, token)
            return

        if token.state == "track":
            home_entry = self._get_home_entry_position(player)
            new_pos = token.position + spaces
            if token.position <= home_entry and new_pos > home_entry:
                overshoot = new_pos - home_entry
                if overshoot >= HOME_COLUMN_LENGTH:
                    self._finish_token(player, token)
                else:
                    token.state = "home_column"
                    token.position = overshoot
                    self.broadcast_l(
                        "ludo-enter-home",
                        buffer="game",
                        player=player.name,
                        color=player.color,
                        token=token.token_number,
                    )
                    self.play_sound(
                        f"game_squares/token{random.randint(1, NUM_TOKEN_SOUNDS)}.ogg"  # nosec B311
                    )
                return

            token.position = ((new_pos - 1) % TRACK_LENGTH) + 1
            self.broadcast_l(
                "ludo-move-track",
                buffer="game",
                player=player.name,
                color=player.color,
                token=token.token_number,
                position=token.position,
            )
            self.play_sound(
                f"game_squares/token{random.randint(1, NUM_TOKEN_SOUNDS)}.ogg"  # nosec B311
            )
            self._check_capture(player, token)
            return

        if token.state == "home_column":
            token.position += spaces
            if token.position >= HOME_COLUMN_LENGTH:
                self._finish_token(player, token)
            else:
                self.broadcast_l(
                    "ludo-move-home",
                    buffer="game",
                    player=player.name,
                    color=player.color,
                    token=token.token_number,
                    position=token.position,
                    total=HOME_COLUMN_LENGTH,
                )
                self.play_sound(
                    f"game_squares/token{random.randint(1, NUM_TOKEN_SOUNDS)}.ogg"  # nosec B311
                )

    def _finish_token(self, player: LudoPlayer, token: LudoToken) -> None:
        token.state = "finished"
        token.position = HOME_COLUMN_LENGTH
        player.finished_count += 1
        self._team_manager.add_to_team_score(player.name, 1)
        self.broadcast_l(
            "ludo-home-finish",
            buffer="game",
            player=player.name,
            color=player.color,
            token=token.token_number,
            finished=player.finished_count,
        )
        self.play_sound("game_pig/win.ogg")

    def _after_move(self, player: LudoPlayer) -> None:
        if player.finished_count >= 4:
            self.play_sound("game_pig/wingame.ogg")
            self.broadcast_l("ludo-winner", buffer="game", player=player.name, color=player.color)
            self.finish_game()
            return

        if self.last_roll == 6:
            self.consecutive_sixes += 1
            max_sixes = self.options.max_consecutive_sixes
            if max_sixes > 0 and self.consecutive_sixes >= max_sixes:
                self.broadcast_l(
                    "ludo-too-many-sixes",
                    buffer="game",
                    player=player.name,
                    count=self.consecutive_sixes,
                )
                if self.turn_start_state:
                    self._restore_turn_state(self.turn_start_state)
                    self.play_sound("game_pig/lose.ogg")
                self.consecutive_sixes = 0
                self._end_turn()
                return

            self.broadcast_personal_l(
                player,
                "ludo-you-extra-turn",
                "ludo-extra-turn",
                buffer="game",
            )
            self.extra_turn = True
            self._end_turn()
            return

        self._end_turn()

    # ======================================================================
    # End screen / results
    # ======================================================================

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        sorted_teams = self._team_manager.get_sorted_teams(by_score=True, descending=True)
        for index, team in enumerate(sorted_teams, 1):
            name = self._team_manager.get_team_name(team, locale)
            points = Localization.get(locale, "game-points", count=team.total_score)
            lines.append(f"{index}. {name}: {points}")
        return lines

    def build_game_result(self) -> GameResult:
        sorted_teams = self._team_manager.get_sorted_teams(by_score=True, descending=True)
        winner = sorted_teams[0] if sorted_teams else None

        final_scores = {}
        for team in sorted_teams:
            name = self._team_manager.get_team_name(team)
            final_scores[name] = team.total_score

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
                "winner_name": self._team_manager.get_team_name(winner) if winner else None,
                "final_scores": final_scores,
            },
        )
