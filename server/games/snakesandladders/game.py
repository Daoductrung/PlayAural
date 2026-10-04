"""Audio-first Snakes and Ladders implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import (
    BoolOption,
    GameOptions,
    MenuOption,
    option_field,
)
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


WINNING_SQUARE = 100
STARTING_POSITION = 0
FINISH_BOUNCE_BACK = "bounce_back"
FINISH_EXACT_STAY = "exact_stay"
FINISH_RULES = (FINISH_BOUNCE_BACK, FINISH_EXACT_STAY)
FINISH_RULE_LABELS = {
    FINISH_BOUNCE_BACK: "snakes-finish-bounce-back",
    FINISH_EXACT_STAY: "snakes-finish-exact-stay",
}

STEP_DELAY_START = 8
STEP_INTERVAL = 4
NUM_STEP_SOUNDS = 3
NUM_DICE_SOUNDS = 3
NUM_LADDER_SOUNDS = 3


@dataclass
class SnakesPlayer(Player):
    """Per-player race state."""

    position: int = STARTING_POSITION
    finished: bool = False


@dataclass
class SnakesAndLaddersOptions(GameOptions):
    """Published rule variants supported by the game."""

    finish_rule: str = option_field(
        MenuOption(
            default=FINISH_BOUNCE_BACK,
            choices=list(FINISH_RULES),
            value_key="rule",
            label="snakes-set-finish-rule",
            prompt="snakes-select-finish-rule",
            change_msg="snakes-option-changed-finish-rule",
            choice_labels=FINISH_RULE_LABELS,
        )
    )
    extra_turn_on_six: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="snakes-set-extra-turn-six",
            change_msg="snakes-option-changed-extra-turn-six",
        )
    )


@dataclass
@register_game
class SnakesAndLaddersGame(Game):
    """Race from before square 1 to square 100."""

    relevant_preferences = ["brief_announcements"]

    players: list[SnakesPlayer] = field(default_factory=list)
    options: SnakesAndLaddersOptions = field(default_factory=SnakesAndLaddersOptions)
    is_rolling: bool = False
    last_roll: int = 0
    winner_id: str = ""

    WINNING_SQUARE = WINNING_SQUARE
    LADDERS = {
        1: 38,
        4: 14,
        9: 31,
        21: 42,
        28: 84,
        36: 44,
        51: 67,
        71: 91,
        80: 100,
    }
    SNAKES = {
        16: 6,
        47: 26,
        49: 11,
        56: 53,
        62: 19,
        64: 60,
        87: 24,
        93: 73,
        95: 75,
        98: 78,
    }

    @classmethod
    def get_name(cls) -> str:
        return "Snakes and Ladders"

    @classmethod
    def get_type(cls) -> str:
        return "snakesandladders"

    @classmethod
    def get_category(cls) -> str:
        return "board"

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @property
    def winner(self) -> SnakesPlayer | None:
        player = self.get_player_by_id(self.winner_id) if self.winner_id else None
        return player if isinstance(player, SnakesPlayer) else None

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> SnakesPlayer:
        return SnakesPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if self.options.finish_rule not in FINISH_RULES:
            errors.append(
                (
                    "snakes-error-invalid-finish-rule",
                    {"rule": self.options.finish_rule},
                )
            )
        return errors

    # ------------------------------------------------------------------
    # Communication helpers
    # ------------------------------------------------------------------

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: SnakesPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast with listener-specific perspective and verbosity."""
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
                payload["player"] = actor
            payload = self._resolve_broadcast_kwargs(user.locale, payload)
            user.speak_l(key, buffer="game", **payload)

    def _announce_turn(self, player: SnakesPlayer) -> None:
        user = self.get_user(player)
        if user and getattr(user.preferences, "play_turn_sound", True):
            user.play_sound("turn.ogg")

        if player.position == STARTING_POSITION:
            self._broadcast_actor_l(
                player,
                "snakes-turn-start-you",
                "snakes-turn-start-other",
            )
        else:
            self._broadcast_actor_l(
                player,
                "snakes-turn-you",
                "snakes-turn-other",
                position=player.position,
            )

    # ------------------------------------------------------------------
    # Lifecycle and turn flow
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.cancel_all_sequences()
        self.clear_scheduled_sounds()
        self.is_rolling = False
        self.last_roll = 0
        self.winner_id = ""

        active_players = self.get_active_players()
        for player in active_players:
            player.position = STARTING_POSITION
            player.finished = False

        self.set_turn_players(active_players)
        self.play_music("game_pig/mus.ogg")
        self.broadcast_l("game-snakesandladders-desc", buffer="game")
        self._start_turn(announce=True)

    def _start_turn(self, *, announce: bool) -> None:
        self.cancel_sequences_by_tag("turn_flow")
        self.is_rolling = False
        player = self.current_player
        if not isinstance(player, SnakesPlayer):
            return

        if announce:
            self._announce_turn(player)
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))  # nosec B311
        self.refresh_menus()

    def _complete_turn(self, player_id: str, extra_turn: bool) -> None:
        self.is_rolling = False
        if self.status != "playing":
            return

        player = self.get_player_by_id(player_id)
        current = self.current_player
        if not isinstance(player, SnakesPlayer) or current is not player:
            self._start_turn(announce=current is not None)
            return

        if extra_turn:
            self._broadcast_actor_l(
                player,
                "snakes-extra-turn-you",
                "snakes-extra-turn-other",
                position=player.position,
            )
            self._start_turn(announce=False)
            return

        self.advance_turn(announce=False)
        self._start_turn(announce=True)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: SnakesPlayer) -> str | None:
        return "roll"

    # ------------------------------------------------------------------
    # Sequence callbacks
    # ------------------------------------------------------------------

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        _ = sequence_id
        player_id = str(payload.get("player_id", ""))
        player = self.get_player_by_id(player_id) if player_id else None
        actor = player if isinstance(player, SnakesPlayer) else None

        # Compatibility for turn sequences saved before the polished flow.
        if callback_id == "move":
            if not actor or "pos" not in payload:
                return
            start = actor.position
            position = int(payload["pos"])
            if position > WINNING_SQUARE:
                # The legacy bounce callback carries the valid landing square.
                return
            actor.position = position
            if start == STARTING_POSITION:
                self._broadcast_actor_l(
                    actor,
                    "snakes-enter-you",
                    "snakes-enter-other",
                    brief_personal_key="snakes-enter-you-brief",
                    brief_others_key="snakes-enter-other-brief",
                    position=position,
                )
            else:
                self._broadcast_actor_l(
                    actor,
                    "snakes-move-you",
                    "snakes-move-other",
                    brief_personal_key="snakes-move-you-brief",
                    brief_others_key="snakes-move-other-brief",
                    start=start,
                    position=position,
                    roll=max(0, position - start),
                )
            self.refresh_menus()
            return

        if callback_id == "land":
            if not actor:
                return
            start = int(payload["start"])
            position = int(payload["position"])
            roll = int(payload["roll"])
            actor.position = position
            if start == STARTING_POSITION:
                self._broadcast_actor_l(
                    actor,
                    "snakes-enter-you",
                    "snakes-enter-other",
                    brief_personal_key="snakes-enter-you-brief",
                    brief_others_key="snakes-enter-other-brief",
                    position=position,
                )
            else:
                self._broadcast_actor_l(
                    actor,
                    "snakes-move-you",
                    "snakes-move-other",
                    brief_personal_key="snakes-move-you-brief",
                    brief_others_key="snakes-move-other-brief",
                    start=start,
                    position=position,
                    roll=roll,
                )
            self.refresh_menus()
            return

        if callback_id == "bounce":
            if not actor:
                return
            if "position" not in payload and "pos" in payload:
                position = int(payload["pos"])
                actor.position = position
                self._broadcast_actor_l(
                    actor,
                    "snakes-restored-bounce-you",
                    "snakes-restored-bounce-other",
                    position=position,
                )
                self.refresh_menus()
                return
            start = int(payload["start"])
            position = int(payload["position"])
            roll = int(payload["roll"])
            actor.position = position
            self._broadcast_actor_l(
                actor,
                "snakes-bounce-you",
                "snakes-bounce-other",
                brief_personal_key="snakes-bounce-you-brief",
                brief_others_key="snakes-bounce-other-brief",
                start=start,
                position=position,
                roll=roll,
                target=WINNING_SQUARE,
            )
            self.refresh_menus()
            return

        if callback_id == "exact_miss":
            if not actor:
                return
            roll = int(payload["roll"])
            needed = WINNING_SQUARE - actor.position
            self._broadcast_actor_l(
                actor,
                "snakes-exact-miss-you",
                "snakes-exact-miss-other",
                brief_personal_key="snakes-exact-miss-you-brief",
                brief_others_key="snakes-exact-miss-other-brief",
                needed=needed,
                position=actor.position,
                roll=roll,
                target=WINNING_SQUARE,
            )
            return

        if callback_id == "ladder":
            if not actor:
                return
            start = int(payload["start"])
            end = int(payload["end"])
            actor.position = end
            self._broadcast_actor_l(
                actor,
                "snakes-ladder-you",
                "snakes-ladder-other",
                brief_personal_key="snakes-ladder-you-brief",
                brief_others_key="snakes-ladder-other-brief",
                start=start,
                end=end,
                distance=end - start,
            )
            self.refresh_menus()
            return

        if callback_id == "snake":
            if not actor:
                return
            start = int(payload["start"])
            end = int(payload["end"])
            actor.position = end
            self._broadcast_actor_l(
                actor,
                "snakes-snake-you",
                "snakes-snake-other",
                brief_personal_key="snakes-snake-you-brief",
                brief_others_key="snakes-snake-other-brief",
                start=start,
                end=end,
                distance=start - end,
            )
            self.refresh_menus()
            return

        if callback_id == "win":
            if actor:
                self._handle_win(actor)
            return

        if callback_id == "end_turn":
            if not player_id and self.current_player:
                player_id = self.current_player.id
            self._complete_turn(player_id, bool(payload.get("extra_turn", False)))

    # ------------------------------------------------------------------
    # Actions and menus
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: SnakesPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "snakes-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "snakes-error-roll-not-playing"
        if self.current_player != player:
            return "snakes-error-roll-not-your-turn"
        if self.is_rolling or self.has_active_sequence(tag="turn_flow"):
            return "snakes-error-roll-resolving"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="check_positions",
                label=Localization.get(locale, "snakes-check-positions"),
                handler="_action_check_positions",
                is_enabled="_is_check_positions_enabled",
                is_hidden="_is_check_positions_hidden",
                include_spectators=True,
            )
        )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                ["check_positions", "whose_turn", "whos_at_table"],
            )
        return action_set

    def _is_check_positions_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        return Visibility.VISIBLE if self.is_touch_client(user) else Visibility.HIDDEN

    def _is_check_positions_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "snakes-error-positions-not-playing"
        return None

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        locale = "en"
        host = self.get_player_by_name(self.host) if self.host else None
        host_user = self.get_user(host) if host else None
        if host_user:
            locale = host_user.locale
        self.define_keybind(
            "r",
            Localization.get(locale, "snakes-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "space",
            Localization.get(locale, "snakes-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get(locale, "snakes-check-positions"),
            ["check_positions"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _finish_rule_label(self, locale: str) -> str:
        key = FINISH_RULE_LABELS.get(
            self.options.finish_rule, "snakes-finish-bounce-back"
        )
        return Localization.get(locale, key)

    def _position_status_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "snakes-status-goal",
                    target=WINNING_SQUARE,
                    rule=self._finish_rule_label(locale),
                ),
                id="goal",
            )
        ]
        current = self.current_player
        ordered_players = sorted(
            self.get_active_players(),
            key=lambda candidate: (candidate.finished, candidate.position),
            reverse=True,
        )
        for candidate in ordered_players:
            player = candidate
            if player.finished or player.position >= WINNING_SQUARE:
                key = "snakes-status-player-finished"
                kwargs = {"player": player.name, "position": player.position}
            elif player.position == STARTING_POSITION:
                key = (
                    "snakes-status-current-start"
                    if player is current
                    else "snakes-status-player-start"
                )
                kwargs = {"player": player.name}
            else:
                key = (
                    "snakes-status-current-position"
                    if player is current
                    else "snakes-status-player-position"
                )
                kwargs = {
                    "player": player.name,
                    "position": player.position,
                    "remaining": WINNING_SQUARE - player.position,
                }
            items.append(
                MenuItem(
                    text=Localization.get(locale, key, **kwargs),
                    id=f"player:{player.id}",
                )
            )
        return items

    def _action_check_positions(self, player: Player, action_id: str) -> None:
        current = self.current_player
        focus_id = f"player:{current.id}" if current else "goal"
        self.live_status_box(
            player,
            "snakes_positions",
            lambda _player, user: self._position_status_items(user.locale),
            focus_id=focus_id,
        )

    # ------------------------------------------------------------------
    # Roll resolution
    # ------------------------------------------------------------------

    def _append_interaction_beats(
        self,
        beats: list[SequenceBeat],
        player: SnakesPlayer,
        landing_position: int,
    ) -> int:
        final_position = landing_position
        if landing_position in self.LADDERS:
            final_position = self.LADDERS[landing_position]
            ladder_sound = (
                f"game_snakes/ladder{random.randint(1, NUM_LADDER_SOUNDS)}.ogg"  # nosec B311
            )
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(ladder_sound),
                        SequenceOperation.callback_op(
                            "ladder",
                            {
                                "player_id": player.id,
                                "start": landing_position,
                                "end": final_position,
                            },
                        ),
                    ],
                    delay_after_ticks=15,
                )
            )
        elif landing_position in self.SNAKES:
            final_position = self.SNAKES[landing_position]
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op("game_snakes/snake.ogg"),
                        SequenceOperation.callback_op(
                            "snake",
                            {
                                "player_id": player.id,
                                "start": landing_position,
                                "end": final_position,
                            },
                        ),
                    ],
                    delay_after_ticks=12,
                )
            )
        return final_position

    def _action_roll(self, player: Player, action_id: str) -> None:
        actor = player if isinstance(player, SnakesPlayer) else None
        if not actor:
            return

        self.is_rolling = True
        self.last_roll = random.randint(1, 6)  # nosec B311
        self.refresh_menus()
        self._broadcast_actor_l(
            actor,
            "snakes-roll-you",
            "snakes-roll-other",
            roll=self.last_roll,
        )

        dice_sound = (
            f"game_squares/diceroll{random.randint(1, NUM_DICE_SOUNDS)}.ogg"  # nosec B311
        )
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(dice_sound)],
                delay_after_ticks=STEP_DELAY_START,
            )
        ]

        start = actor.position
        attempted_position = start + self.last_roll
        overshoots = attempted_position > WINNING_SQUARE
        if overshoots and self.options.finish_rule == FINISH_EXACT_STAY:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "exact_miss",
                            {"player_id": actor.id, "roll": self.last_roll},
                        )
                    ],
                    delay_after_ticks=5,
                )
            )
            final_position = start
        else:
            for _ in range(self.last_roll):
                step_sound = (
                    f"game_squares/step{random.randint(1, NUM_STEP_SOUNDS)}.ogg"  # nosec B311
                )
                beats.append(
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(step_sound)],
                        delay_after_ticks=STEP_INTERVAL,
                    )
                )

            landing_position = attempted_position
            if overshoots:
                landing_position = WINNING_SQUARE - (
                    attempted_position - WINNING_SQUARE
                )
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op("game_snakes/bounce.ogg"),
                            SequenceOperation.callback_op(
                                "bounce",
                                {
                                    "player_id": actor.id,
                                    "start": start,
                                    "position": landing_position,
                                    "roll": self.last_roll,
                                },
                            ),
                        ],
                        delay_after_ticks=8,
                    )
                )
            else:
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "land",
                                {
                                    "player_id": actor.id,
                                    "start": start,
                                    "position": landing_position,
                                    "roll": self.last_roll,
                                },
                            )
                        ],
                        delay_after_ticks=2,
                    )
                )

            final_position = self._append_interaction_beats(
                beats, actor, landing_position
            )

        if final_position == WINNING_SQUARE:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "win", {"player_id": actor.id}
                        )
                    ]
                )
            )
        else:
            beats.append(SequenceBeat.pause(5))
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "end_turn",
                            {
                                "player_id": actor.id,
                                "extra_turn": bool(
                                    self.options.extra_turn_on_six
                                    and self.last_roll == 6
                                ),
                            },
                        )
                    ]
                )
            )

        self.start_sequence(
            "turn_flow",
            beats,
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _handle_win(self, winner: SnakesPlayer) -> None:
        self.is_rolling = False
        winner.position = WINNING_SQUARE
        winner.finished = True
        self.winner_id = winner.id
        self.play_sound("game_pig/win.ogg")
        self._broadcast_actor_l(
            winner,
            "snakes-win-you",
            "snakes-win-other",
            position=WINNING_SQUARE,
        )
        self.finish_game()

    def build_game_result(self) -> GameResult:
        winner = self.winner
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda player: (player.finished, player.position),
            reverse=True,
        )
        final_positions = {player.id: player.position for player in sorted_players}
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(player)
                for player in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "final_positions": final_positions,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_positions = result.custom_data.get("final_positions", {})
        for rank, player_result in enumerate(result.player_results, 1):
            position = final_positions.get(
                player_result.player_id,
                final_positions.get(player_result.player_name, STARTING_POSITION),
            )
            key = (
                "snakes-end-score-start"
                if position == STARTING_POSITION
                else "snakes-end-score"
            )
            kwargs = {
                "rank": rank,
                "player": player_result.player_name,
            }
            if position != STARTING_POSITION:
                kwargs["position"] = position
            lines.append(Localization.get(locale, key, **kwargs))
        return lines
