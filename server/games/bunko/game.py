"""Bunko dice game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


ROLL_SEQUENCE_ID = "bunko_roll"
ROLL_SEQUENCE_TAG = "bunko_roll"
ROUND_TARGET_SCORE = 21
TARGET_NUMBERS = 6
ROLL_DICE_COUNT = 3
WINNING_MODE_ROUND_WINS = "round_wins"
WINNING_MODE_TOTAL_SCORE = "total_score"
SHAKE_TO_ROLL_DELAY_TICKS = 34
ROLL_TO_RESULT_DELAY_TICKS = 24


def evaluate_roll(values: list[int], target_number: int) -> tuple[str, int]:
    """Score a Bunko roll."""
    if len(values) != ROLL_DICE_COUNT:
        raise ValueError("Bunko rolls must contain exactly 3 dice.")

    if all(value == target_number for value in values):
        return "bunko", ROUND_TARGET_SCORE

    if len(set(values)) == 1:
        return "mini_bunko", 5

    matches = sum(1 for value in values if value == target_number)
    if matches > 0:
        return "match", matches

    return "no_score", 0


@dataclass
class BunkoPlayer(Player):
    """Per-player Bunko state."""

    total_score: int = 0
    round_score: int = 0
    rounds_won: int = 0
    bunkos: int = 0
    mini_bunkos: int = 0


@dataclass
class BunkoOptions(GameOptions):
    """Host-configurable Bunko settings."""

    round_count: int = option_field(
        IntOption(
            default=6,
            min_val=1,
            max_val=12,
            value_key="count",
            label="bunko-set-round-count",
            prompt="bunko-enter-round-count",
            change_msg="bunko-option-changed-round-count",
        )
    )
    winning_mode: str = option_field(
        MenuOption(
            default=WINNING_MODE_ROUND_WINS,
            choices=[WINNING_MODE_ROUND_WINS, WINNING_MODE_TOTAL_SCORE],
            value_key="mode",
            label="bunko-set-winning-mode",
            prompt="bunko-select-winning-mode",
            change_msg="bunko-option-changed-winning-mode",
            choice_labels={
                WINNING_MODE_ROUND_WINS: "bunko-winning-mode-round-wins",
                WINNING_MODE_TOTAL_SCORE: "bunko-winning-mode-total-score",
            },
        )
    )


@dataclass
@register_game
class BunkoGame(Game):
    """Single-table Bunko adaptation for PlayAural."""

    players: list[BunkoPlayer] = field(default_factory=list)
    options: BunkoOptions = field(default_factory=BunkoOptions)
    current_target_number: int = 1
    last_roll: list[int] = field(default_factory=list)
    last_roll_player_id: str = ""
    last_roll_outcome: str = ""
    last_roll_points: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Bunko"

    @classmethod
    def get_type(cls) -> str:
        return "bunko"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> BunkoPlayer:
        return BunkoPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _current_round_limit(self) -> int:
        return max(1, self.options.round_count)

    def _target_for_round(self, round_number: int) -> int:
        return ((round_number - 1) % TARGET_NUMBERS) + 1

    def _ordered_players_from(
        self, starting_player: BunkoPlayer | None
    ) -> list[BunkoPlayer]:
        active_players = [
            player for player in self.get_active_players() if isinstance(player, BunkoPlayer)
        ]
        if not active_players:
            return []
        if starting_player is None or starting_player not in active_players:
            return active_players
        start_index = active_players.index(starting_player)
        return active_players[start_index:] + active_players[:start_index]

    def _queue_bot_turn(self) -> None:
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(12, 24))

    def _sync_team_scores(self) -> None:
        for player in self.get_active_players():
            team = self.team_manager.get_team(player.name)
            if team:
                team.total_score = getattr(player, "total_score", 0)

    def _ranking_key(self, player: BunkoPlayer) -> tuple[int, int, int, int]:
        if self.options.winning_mode == WINNING_MODE_TOTAL_SCORE:
            return (
                player.total_score,
                player.rounds_won,
                player.bunkos,
                player.mini_bunkos,
            )
        return (
            player.rounds_won,
            player.total_score,
            player.bunkos,
            player.mini_bunkos,
        )

    def _ranking_score_value(self, player: BunkoPlayer) -> list[int]:
        return list(self._ranking_key(player))

    def _sorted_players_by_standing(self) -> list[BunkoPlayer]:
        players = [
            player for player in self.get_active_players() if isinstance(player, BunkoPlayer)
        ]
        return sorted(players, key=self._ranking_key, reverse=True)

    def _format_roll_values(self, values: list[int]) -> str:
        return ", ".join(str(value) for value in values)

    def _announce_game_start(self) -> None:
        names = [player.name for player in self.get_active_players()]
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            players_text = Localization.format_list_and(user.locale, names)
            user.speak_l("bunko-game-start", buffer="game", players=players_text)

    def _start_turn(self) -> None:
        current = self.current_player
        if not current:
            return
        self.announce_turn(turn_sound="game_squares/begin turn.ogg")
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def _start_round(self, starter: BunkoPlayer | None = None) -> None:
        self.cancel_sequences_by_tag(ROLL_SEQUENCE_TAG)
        self.last_roll = []
        self.last_roll_player_id = ""
        self.last_roll_outcome = ""
        self.last_roll_points = 0

        self.round += 1
        self.current_target_number = self._target_for_round(self.round)

        for player in self.get_active_players():
            if isinstance(player, BunkoPlayer):
                player.round_score = 0

        ordered_players = self._ordered_players_from(starter)
        self.set_turn_players(ordered_players)

        self.play_sound("game_bunko/roundstart.ogg")
        self.broadcast_l(
            "bunko-round-start",
            buffer="game",
            round=self.round,
            total_rounds=self._current_round_limit(),
            target=self.current_target_number,
        )
        self._start_turn()

    def _finish_current_round(self, winner: BunkoPlayer) -> None:
        winner.rounds_won += 1
        self.play_sound("game_pig/win.ogg")
        self.broadcast_l(
            "bunko-round-winner",
            buffer="game",
            player=winner.name,
            round=self.round,
            score=winner.round_score,
        )

        if self.round >= self._current_round_limit():
            self.play_sound("game_pig/wingame.ogg")
            self.finish_game()
            return

        active_players = [
            player for player in self.get_active_players() if isinstance(player, BunkoPlayer)
        ]
        if not active_players:
            self.finish_game()
            return

        winner_index = active_players.index(winner)
        next_starter = active_players[(winner_index + 1) % len(active_players)]
        self._start_round(next_starter)

    def _end_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    def _standings_lines(self, locale: str) -> list[str]:
        lines = []
        for index, player in enumerate(self._sorted_players_by_standing(), 1):
            lines.append(
                Localization.get(
                    locale,
                    "bunko-score-line",
                    rank=index,
                    player=player.name,
                    rounds=player.rounds_won,
                    total=player.total_score,
                    current=player.round_score,
                    bunkos=player.bunkos,
                    mini_bunkos=player.mini_bunkos,
                )
            )
        return lines

    # ======================================================================
    # Visibility / enabled callbacks
    # ======================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_check_last_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_last_roll_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

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

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    # ======================================================================
    # Actions / keybinds
    # ======================================================================

    def create_turn_action_set(self, player: BunkoPlayer) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "bunko-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                show_in_actions_menu=False,
            )
        )
        return action_set

    web_target_order = [
        "check_status",
        "check_last_roll",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "bunko-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_last_roll",
                label=Localization.get(locale, "bunko-check-last-roll"),
                handler="_action_check_last_roll",
                is_enabled="_is_check_last_roll_enabled",
                is_hidden="_is_check_last_roll_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        host_user = None
        if self.host:
            host_player = self.get_player_by_name(self.host)
            if host_player:
                host_user = self.get_user(host_player)
        locale = host_user.locale if host_user else "en"

        self.define_keybind(
            "r",
            Localization.get(locale, "bunko-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "e",
            Localization.get(locale, "bunko-check-status"),
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            Localization.get(locale, "bunko-check-last-roll"),
            ["check_last_roll"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_roll(self, player: Player, action_id: str) -> None:
        if self.status != "playing":
            return

        values = [random.randint(1, 6) for _ in range(ROLL_DICE_COUNT)]
        self.start_sequence(
            ROLL_SEQUENCE_ID,
            [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op("game_squares/diceshake1.ogg")],
                    delay_after_ticks=SHAKE_TO_ROLL_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.sound_op("game_squares/diceroll1.ogg")],
                    delay_after_ticks=ROLL_TO_RESULT_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "resolve_roll",
                            {"player_id": player.id, "values": values},
                        )
                    ]
                ),
            ],
            tag=ROLL_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        user.speak_l(
            "bunko-status-round",
            buffer="game",
            round=self.round,
            total_rounds=self._current_round_limit(),
            target=self.current_target_number,
        )

        current = self.current_player
        if current:
            user.speak_l("bunko-status-turn", buffer="game", player=current.name)

        leader = self._sorted_players_by_standing()
        if leader:
            user.speak_l(
                "bunko-status-leader",
                buffer="game",
                player=leader[0].name,
                rounds=leader[0].rounds_won,
                total=leader[0].total_score,
            )

    def _action_check_last_roll(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        if not self.last_roll_player_id or not self.last_roll:
            user.speak_l("bunko-last-roll-none", buffer="game")
            return

        roller = self.get_player_by_id(self.last_roll_player_id)
        if not roller:
            user.speak_l("bunko-last-roll-none", buffer="game")
            return

        user.speak_l(
            f"bunko-last-roll-{self.last_roll_outcome}",
            buffer="game",
            player=roller.name,
            dice=self._format_roll_values(self.last_roll),
            points=self.last_roll_points,
        )

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        mode_key = f"bunko-winning-mode-{self.options.winning_mode.replace('_', '-')}"
        user.speak_l(
            "bunko-standings-header",
            buffer="game",
            mode=Localization.get(user.locale, mode_key),
        )
        for line in self._standings_lines(user.locale):
            user.speak(line, buffer="game")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        mode_key = f"bunko-winning-mode-{self.options.winning_mode.replace('_', '-')}"
        lines = [
            Localization.get(
                user.locale,
                "bunko-standings-header",
                mode=Localization.get(user.locale, mode_key),
            )
        ]
        lines.extend(self._standings_lines(user.locale))
        self.status_box(player, lines)

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.current_target_number = 1
        self.last_roll = []
        self.last_roll_player_id = ""
        self.last_roll_outcome = ""
        self.last_roll_points = 0

        active_players = self.get_active_players()
        self.team_manager.team_mode = "individual"
        self.team_manager.setup_teams([player.name for player in active_players])

        for player in active_players:
            if isinstance(player, BunkoPlayer):
                player.total_score = 0
                player.round_score = 0
                player.rounds_won = 0
                player.bunkos = 0
                player.mini_bunkos = 0

        self._sync_team_scores()
        self._announce_game_start()
        self.play_music("game_pig/mus.ogg")
        starter = self.players[0] if self.players else None
        self._start_round(starter if isinstance(starter, BunkoPlayer) else None)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if callback_id != "resolve_roll" or self.status != "playing":
            return

        player = self.get_player_by_id(payload.get("player_id", ""))
        if not isinstance(player, BunkoPlayer):
            return

        values = [int(value) for value in payload.get("values", [])]
        if len(values) != ROLL_DICE_COUNT:
            return

        outcome, points = evaluate_roll(values, self.current_target_number)

        player.total_score += points
        player.round_score += points
        if outcome == "bunko":
            player.bunkos += 1
            self.play_sound("game_bunko/bunko.ogg")
        elif outcome == "mini_bunko":
            player.mini_bunkos += 1
            self.play_sound("game_bunko/minibunko.ogg")
        elif outcome == "match":
            self.play_sound("game_bunko/matchdice.ogg")
        else:
            self.play_sound("game_squares/skip.ogg")

        self.last_roll = list(values)
        self.last_roll_player_id = player.id
        self.last_roll_outcome = outcome
        self.last_roll_points = points
        self._sync_team_scores()

        self.broadcast_l(
            f"bunko-roll-{outcome}",
            buffer="game",
            player=player.name,
            dice=self._format_roll_values(values),
            points=points,
            total=player.total_score,
            round_total=player.round_score,
        )

        if outcome == "no_score":
            self._end_turn()
            return

        if outcome == "bunko" or player.round_score >= ROUND_TARGET_SCORE:
            self._finish_current_round(player)
            return

        if self.current_player == player:
            self._queue_bot_turn()

    def bot_think(self, player: BunkoPlayer) -> str | None:
        return "roll"

    # ======================================================================
    # Results
    # ======================================================================

    def build_game_result(self) -> GameResult:
        sorted_players = self._sorted_players_by_standing()
        top_key = self._ranking_key(sorted_players[0]) if sorted_players else None
        winners = [
            player for player in sorted_players if self._ranking_key(player) == top_key
        ]
        winner_ids = [player.id for player in winners]

        rankings = []
        for player in sorted_players:
            rankings.append(
                {
                    "members": [player.name],
                    "score": self._ranking_score_value(player),
                    "rounds_won": player.rounds_won,
                    "total_score": player.total_score,
                    "bunkos": player.bunkos,
                    "mini_bunkos": player.mini_bunkos,
                }
            )

        final_scores = {player.name: player.total_score for player in sorted_players}

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
                for player in sorted_players
            ],
            custom_data={
                "winner_name": winners[0].name if len(winners) == 1 else None,
                "winner_ids": winner_ids,
                "final_scores": final_scores,
                "rankings": rankings,
                "team_rankings": rankings,
                "rounds_played": self.round,
                "round_count": self._current_round_limit(),
                "winning_mode": self.options.winning_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        rankings = result.custom_data.get("rankings", [])
        for index, entry in enumerate(rankings, 1):
            members = entry.get("members", [])
            name = members[0] if members else Localization.get(locale, "unknown-player")
            lines.append(
                Localization.get(
                    locale,
                    "bunko-score-line",
                    rank=index,
                    player=name,
                    rounds=entry.get("rounds_won", 0),
                    total=entry.get("total_score", 0),
                    current=0,
                    bunkos=entry.get("bunkos", 0),
                    mini_bunkos=entry.get("mini_bunkos", 0),
                )
            )
        return lines
