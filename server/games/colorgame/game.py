"""Color Game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, EditboxInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


PHASE_BETTING = "betting"
PHASE_ROLLING = "rolling"
PHASE_RESOLVING = "resolving"

WIN_CONDITION_LAST_PLAYER = "last_player"
WIN_CONDITION_HIGHEST_BANKROLL = "highest_bankroll"

COLORS = ("red", "blue", "yellow", "green", "white", "orange")
ROLL_DICE_COUNT = 3
ROLL_SEQUENCE_ID = "colorgame_roll"
ROLL_SEQUENCE_TAG = "colorgame_roll"
SHAKE_TO_ROLL_DELAY_TICKS = 34
ROLL_TO_RESULT_DELAY_TICKS = 24
TICKS_PER_SECOND = 20


def roll_colors() -> list[str]:
    """Roll the three color dice."""
    return [random.choice(COLORS) for _ in range(ROLL_DICE_COUNT)]


def evaluate_color_bet(stake: int, matches: int) -> tuple[int, int]:
    """Return (total_return, net_change) for a single color bet."""
    if matches <= 0:
        return 0, -stake
    total_return = stake * (matches + 1)
    return total_return, stake * matches


@dataclass
class ColorGamePlayer(Player):
    """Per-player state for Color Game."""

    bankroll: int = 0
    current_bets: dict[str, int] = field(default_factory=dict)
    bets_locked: bool = False
    profitable_rounds: int = 0
    biggest_win: int = 0


@dataclass
class ColorGameOptions(GameOptions):
    """Host-configurable Color Game settings."""

    starting_bankroll: int = option_field(
        IntOption(
            default=100,
            min_val=10,
            max_val=1000,
            value_key="amount",
            label="colorgame-set-starting-bankroll",
            prompt="colorgame-enter-starting-bankroll",
            change_msg="colorgame-option-changed-starting-bankroll",
        )
    )
    minimum_bet: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=100,
            value_key="amount",
            label="colorgame-set-minimum-bet",
            prompt="colorgame-enter-minimum-bet",
            change_msg="colorgame-option-changed-minimum-bet",
        )
    )
    maximum_total_bet: int = option_field(
        IntOption(
            default=20,
            min_val=1,
            max_val=1000,
            value_key="amount",
            label="colorgame-set-maximum-total-bet",
            prompt="colorgame-enter-maximum-total-bet",
            change_msg="colorgame-option-changed-maximum-total-bet",
        )
    )
    betting_timer_seconds: int = option_field(
        IntOption(
            default=15,
            min_val=5,
            max_val=60,
            value_key="seconds",
            label="colorgame-set-betting-timer",
            prompt="colorgame-enter-betting-timer",
            change_msg="colorgame-option-changed-betting-timer",
        )
    )
    round_limit: int = option_field(
        IntOption(
            default=20,
            min_val=1,
            max_val=100,
            value_key="count",
            label="colorgame-set-round-limit",
            prompt="colorgame-enter-round-limit",
            change_msg="colorgame-option-changed-round-limit",
        )
    )
    win_condition: str = option_field(
        MenuOption(
            default=WIN_CONDITION_LAST_PLAYER,
            choices=[WIN_CONDITION_LAST_PLAYER, WIN_CONDITION_HIGHEST_BANKROLL],
            value_key="mode",
            label="colorgame-set-win-condition",
            prompt="colorgame-select-win-condition",
            change_msg="colorgame-option-changed-win-condition",
            choice_labels={
                WIN_CONDITION_LAST_PLAYER: "colorgame-win-condition-last-player",
                WIN_CONDITION_HIGHEST_BANKROLL: "colorgame-win-condition-highest-bankroll",
            },
        )
    )


@dataclass
@register_game
class ColorGameGame(Game):
    """Traditional Filipino Perya Color Game adaptation."""

    players: list[ColorGamePlayer] = field(default_factory=list)
    options: ColorGameOptions = field(default_factory=ColorGameOptions)
    phase: str = PHASE_BETTING
    betting_ticks_remaining: int = 0
    last_roll: list[str] = field(default_factory=list)
    last_round_bets: dict[str, dict[str, int]] = field(default_factory=dict)
    last_round_net_changes: dict[str, int] = field(default_factory=dict)
    last_round_total_returns: dict[str, int] = field(default_factory=dict)

    @classmethod
    def get_name(cls) -> str:
        return "Color Game"

    @classmethod
    def get_type(cls) -> str:
        return "colorgame"

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
        return ["wins", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ColorGamePlayer:
        return ColorGamePlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = super().prestart_validate()
        if self.options.maximum_total_bet < self.options.minimum_bet:
            errors.append("colorgame-error-max-bet-too-small")
        if self.options.maximum_total_bet > self.options.starting_bankroll:
            errors.append("colorgame-error-max-bet-too-large")
        return errors

    def _sync_team_scores(self) -> None:
        for player in self.get_active_players():
            team = self.team_manager.get_team(player.name)
            if team and isinstance(player, ColorGamePlayer):
                team.total_score = player.bankroll

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _color_name(self, locale: str, color: str) -> str:
        return Localization.get(locale, f"colorgame-color-{color}")

    def _format_color_list(self, locale: str, colors: list[str]) -> str:
        return Localization.format_list_and(
            locale, [self._color_name(locale, color) for color in colors]
        )

    def _format_bet_summary(self, locale: str, bets: dict[str, int]) -> str:
        if not bets:
            return Localization.get(locale, "colorgame-no-bets")
        parts = []
        for color in COLORS:
            amount = bets.get(color, 0)
            if amount > 0:
                parts.append(
                    Localization.get(
                        locale,
                        "colorgame-bet-entry",
                        color=self._color_name(locale, color),
                        amount=amount,
                    )
                )
        if not parts:
            return Localization.get(locale, "colorgame-no-bets")
        return Localization.format_list_and(locale, parts)

    def _player_total_bet(self, player: ColorGamePlayer) -> int:
        return sum(player.current_bets.values())

    def _player_bet_cap(self, player: ColorGamePlayer) -> int:
        return min(player.bankroll, self.options.maximum_total_bet)

    def _live_players(self) -> list[ColorGamePlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, ColorGamePlayer) and player.bankroll > 0
        ]

    def _all_betting_players_locked(self) -> bool:
        live = self._live_players()
        return bool(live) and all(player.bets_locked for player in live)

    def _remaining_betting_seconds(self) -> int:
        return max(
            0, (self.betting_ticks_remaining + (TICKS_PER_SECOND - 1)) // TICKS_PER_SECOND
        )

    def _standings_key(self, player: ColorGamePlayer) -> tuple[int, int, int]:
        return (player.bankroll, player.profitable_rounds, player.biggest_win)

    def _sorted_players_by_standing(self) -> list[ColorGamePlayer]:
        players = [
            player for player in self.get_active_players() if isinstance(player, ColorGamePlayer)
        ]
        return sorted(players, key=self._standings_key, reverse=True)

    def _announce_game_start(self) -> None:
        names = [player.name for player in self.get_active_players()]
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            players_text = Localization.format_list_and(user.locale, names)
            user.speak_l("colorgame-game-start", buffer="game", players=players_text)

    def _should_finish_now(self) -> bool:
        if self.round >= self.options.round_limit:
            return True
        return len(self._live_players()) <= 1

    def _reset_round_state(self) -> None:
        for player in self.get_active_players():
            if isinstance(player, ColorGamePlayer):
                player.current_bets.clear()
                player.bets_locked = player.bankroll <= 0

    def _queue_betting_bots(self) -> None:
        for player in self._live_players():
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(12, 30))

    def _start_betting_round(self) -> None:
        if self._should_finish_now():
            self.finish_game()
            return

        self.cancel_sequences_by_tag(ROLL_SEQUENCE_TAG)
        self.round += 1
        self.phase = PHASE_BETTING
        self.betting_ticks_remaining = self.options.betting_timer_seconds * TICKS_PER_SECOND
        self._reset_round_state()

        self.play_sound("game_bunko/roundstart.ogg")
        self.broadcast_l(
            "colorgame-round-start",
            buffer="game",
            round=self.round,
            limit=self.options.round_limit,
            seconds=self.options.betting_timer_seconds,
        )
        self._queue_betting_bots()
        self.rebuild_all_menus()

    def _start_roll_sequence(self) -> None:
        if self.phase != PHASE_BETTING:
            return
        self.phase = PHASE_ROLLING
        rolled = roll_colors()
        shake_sound = f"game_squares/diceshake{random.randint(1, 3)}.ogg"
        roll_sound = f"game_squares/diceroll{random.randint(1, 3)}.ogg"
        self.start_sequence(
            ROLL_SEQUENCE_ID,
            [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(shake_sound)],
                    delay_after_ticks=SHAKE_TO_ROLL_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(roll_sound)],
                    delay_after_ticks=ROLL_TO_RESULT_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "resolve_roll",
                            {"rolled": list(rolled)},
                        )
                    ]
                ),
            ],
            tag=ROLL_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _finalize_roll(self, rolled: list[str]) -> None:
        self.phase = PHASE_RESOLVING
        self.last_roll = list(rolled)
        self.last_round_bets = {}
        self.last_round_net_changes = {}
        self.last_round_total_returns = {}

        for player in self.get_active_players():
            if not isinstance(player, ColorGamePlayer):
                continue
            bets_snapshot = dict(player.current_bets)
            self.last_round_bets[player.id] = bets_snapshot

            total_net = 0
            total_return = 0
            for color, stake in bets_snapshot.items():
                matches = rolled.count(color)
                color_return, net_change = evaluate_color_bet(stake, matches)
                total_return += color_return
                total_net += net_change

            player.bankroll += total_net
            if total_net > 0:
                player.profitable_rounds += 1
                player.biggest_win = max(player.biggest_win, total_net)

            self.last_round_net_changes[player.id] = total_net
            self.last_round_total_returns[player.id] = total_return

        self._sync_team_scores()

        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l(
                    "colorgame-roll-result",
                    buffer="game",
                    colors=self._format_color_list(user.locale, rolled),
                )

        for player in self._sorted_players_by_standing():
            net = self.last_round_net_changes.get(player.id, 0)
            bets = self.last_round_bets.get(player.id, {})
            if not bets:
                self.broadcast_l(
                    "colorgame-player-sat-out",
                    buffer="game",
                    player=player.name,
                    bankroll=player.bankroll,
                )
            elif net > 0:
                self.broadcast_l(
                    "colorgame-player-won",
                    buffer="game",
                    player=player.name,
                    amount=net,
                    bankroll=player.bankroll,
                )
            elif net == 0:
                self.broadcast_l(
                    "colorgame-player-even",
                    buffer="game",
                    player=player.name,
                    bankroll=player.bankroll,
                )
            else:
                self.broadcast_l(
                    "colorgame-player-lost",
                    buffer="game",
                    player=player.name,
                    amount=abs(net),
                    bankroll=player.bankroll,
                )

        if self._should_finish_now():
            self.finish_game()
            return

        self._start_betting_round()

    def _lock_player_bets(self, player: ColorGamePlayer) -> None:
        if player.bets_locked:
            return
        player.bets_locked = True
        total = self._player_total_bet(player)
        if total > 0:
            self.broadcast_l(
                "colorgame-player-locked-bets",
                buffer="game",
                player=player.name,
                total=total,
            )
        else:
            self.broadcast_l("colorgame-player-sits-out", buffer="game", player=player.name)

    def _auto_lock_unconfirmed_players(self) -> None:
        for player in self._live_players():
            if not player.bets_locked:
                self._lock_player_bets(player)

    def _choose_bot_bets(self, player: ColorGamePlayer) -> dict[str, int]:
        cap = self._player_bet_cap(player)
        minimum = min(self.options.minimum_bet, cap)
        if minimum <= 0:
            return {}

        leaders = self._sorted_players_by_standing()
        leader_bankroll = leaders[0].bankroll if leaders else player.bankroll
        rounds_left = max(0, self.options.round_limit - self.round + 1)
        trailing = leader_bankroll - player.bankroll

        if player.bankroll <= minimum:
            total = minimum
            color_count = 1
        elif self.options.win_condition == WIN_CONDITION_LAST_PLAYER and player.bankroll <= (
            self.options.starting_bankroll // 4
        ):
            total = min(cap, max(minimum, player.bankroll // 3))
            color_count = 1
        elif rounds_left <= 3 or trailing > max(5, self.options.starting_bankroll // 5):
            total = min(cap, max(minimum, player.bankroll // 3))
            color_count = 2 if total >= minimum * 2 else 1
        else:
            total = min(cap, max(minimum, player.bankroll // 5))
            if total >= minimum * 3 and random.random() < 0.35:
                color_count = 3
            elif total >= minimum * 2 and random.random() < 0.6:
                color_count = 2
            else:
                color_count = 1

        color_count = max(1, min(color_count, len(COLORS), total // minimum))
        chosen = random.sample(list(COLORS), k=color_count)
        plan: dict[str, int] = {}

        remaining = total
        for index, color in enumerate(chosen):
            slots_left = color_count - index
            amount = minimum
            extra_available = remaining - minimum * slots_left
            if slots_left == 1:
                amount = remaining
            elif extra_available > 0:
                amount += random.randint(0, extra_available)
            plan[color] = amount
            remaining -= amount

        return {color: amount for color, amount in plan.items() if amount > 0}

    def _process_betting_bots(self) -> None:
        for player in self._live_players():
            if not player.is_bot or player.bets_locked:
                continue
            if player.bot_think_ticks > 0:
                player.bot_think_ticks -= 1
                continue
            player.current_bets = self._choose_bot_bets(player)
            self._lock_player_bets(player)
            self.rebuild_all_menus()
            if self._all_betting_players_locked():
                self._start_roll_sequence()
            break

    def _standings_lines(self, locale: str) -> list[str]:
        lines = []
        for index, player in enumerate(self._sorted_players_by_standing(), 1):
            status_key = "colorgame-standing-bust" if player.bankroll <= 0 else "colorgame-standing-live"
            lines.append(
                Localization.get(
                    locale,
                    "colorgame-score-line",
                    rank=index,
                    player=player.name,
                    bankroll=player.bankroll,
                    profitable_rounds=player.profitable_rounds,
                    biggest_win=player.biggest_win,
                    status=Localization.get(locale, status_key),
                )
            )
        return lines

    def _betting_lines(self, locale: str) -> list[str]:
        lines = []
        for player in self._sorted_players_by_standing():
            locked_key = (
                "colorgame-bets-locked-status"
                if player.bets_locked
                else "colorgame-bets-open-status"
            )
            lines.append(
                Localization.get(
                    locale,
                    "colorgame-bets-line",
                    player=player.name,
                    bets=self._format_bet_summary(locale, player.current_bets),
                    total=self._player_total_bet(player),
                    locked=Localization.get(locale, locked_key),
                )
            )
        return lines

    def _is_set_bet_enabled(self, player: Player, *, action_id: str) -> str | None:
        _ = action_id
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if cg_player.bankroll <= 0:
            return "colorgame-bankrupt"
        if self.phase != PHASE_BETTING:
            return "action-game-in-progress"
        if cg_player.bets_locked:
            return "colorgame-bets-already-locked"
        return None

    def _is_set_bet_hidden(self, player: Player, *, action_id: str) -> Visibility:
        _ = action_id
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_BETTING or cg_player.bankroll <= 0 or cg_player.bets_locked:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_set_bet_label(self, player: Player, action_id: str) -> str:
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        locale = self._player_locale(player)
        color = action_id.removeprefix("set_bet_")
        return Localization.get(
            locale,
            "colorgame-set-bet-color",
            color=self._color_name(locale, color),
            amount=cg_player.current_bets.get(color, 0),
        )

    def _is_clear_bets_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_BETTING:
            return "action-game-in-progress"
        if cg_player.bets_locked:
            return "colorgame-bets-already-locked"
        if not cg_player.current_bets:
            return "colorgame-no-bets-placed"
        return None

    def _is_clear_bets_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_BETTING or cg_player.bets_locked or not cg_player.current_bets:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_confirm_bets_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if cg_player.bankroll <= 0:
            return "colorgame-bankrupt"
        if self.phase != PHASE_BETTING:
            return "action-game-in-progress"
        if cg_player.bets_locked:
            return "colorgame-bets-already-locked"
        return None

    def _is_confirm_bets_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_BETTING or cg_player.bankroll <= 0 or cg_player.bets_locked:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_confirm_bets_label(self, player: Player, action_id: str) -> str:
        _ = action_id
        cg_player: ColorGamePlayer = player  # type: ignore[assignment]
        locale = self._player_locale(player)
        total = self._player_total_bet(cg_player)
        if total > 0:
            return Localization.get(locale, "colorgame-confirm-bets", total=total)
        return Localization.get(locale, "colorgame-confirm-sit-out")

    def _is_check_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_bets_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_bets_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_last_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_last_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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

    def create_turn_action_set(self, player: ColorGamePlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        for color in COLORS:
            action_set.add(
                Action(
                    id=f"set_bet_{color}",
                    label=Localization.get(
                        locale,
                        "colorgame-set-bet-color",
                        color=self._color_name(locale, color),
                        amount=0,
                    ),
                    handler="_action_set_bet",
                    is_enabled="_is_set_bet_enabled",
                    is_hidden="_is_set_bet_hidden",
                    get_label="_get_set_bet_label",
                    input_request=EditboxInput(
                        prompt="colorgame-enter-bet-amount",
                        default="",
                        bot_input="_bot_input_bet_amount",
                    ),
                    show_in_actions_menu=False,
                )
            )

        action_set.add(
            Action(
                id="clear_bets",
                label=Localization.get(locale, "colorgame-clear-bets"),
                handler="_action_clear_bets",
                is_enabled="_is_clear_bets_enabled",
                is_hidden="_is_clear_bets_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="confirm_bets",
                label=Localization.get(locale, "colorgame-confirm-bets", total=0),
                handler="_action_confirm_bets",
                is_enabled="_is_confirm_bets_enabled",
                is_hidden="_is_confirm_bets_hidden",
                get_label="_get_confirm_bets_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "colorgame-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_bets",
                label=Localization.get(locale, "colorgame-check-bets"),
                handler="_action_check_bets",
                is_enabled="_is_check_bets_enabled",
                is_hidden="_is_check_bets_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_last_roll",
                label=Localization.get(locale, "colorgame-check-last-roll"),
                handler="_action_check_last_roll",
                is_enabled="_is_check_last_roll_enabled",
                is_hidden="_is_check_last_roll_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            target_order = [
                "check_status",
                "check_bets",
                "check_last_roll",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("r", "Set red bet", ["set_bet_red"], state=KeybindState.ACTIVE)
        self.define_keybind("u", "Set blue bet", ["set_bet_blue"], state=KeybindState.ACTIVE)
        self.define_keybind("y", "Set yellow bet", ["set_bet_yellow"], state=KeybindState.ACTIVE)
        self.define_keybind("g", "Set green bet", ["set_bet_green"], state=KeybindState.ACTIVE)
        self.define_keybind("w", "Set white bet", ["set_bet_white"], state=KeybindState.ACTIVE)
        self.define_keybind("o", "Set orange bet", ["set_bet_orange"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Clear bets", ["clear_bets"], state=KeybindState.ACTIVE)
        self.define_keybind("space", "Confirm bets", ["confirm_bets"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "e",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "v",
            "Check bets",
            ["check_bets"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            "Check last roll",
            ["check_last_roll"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_set_bet(
        self, player: ColorGamePlayer, input_value: str, action_id: str
    ) -> None:
        color = action_id.removeprefix("set_bet_")
        user = self.get_user(player)
        if not user:
            return

        try:
            amount = int(input_value.strip())
        except ValueError:
            user.speak_l("colorgame-invalid-bet-amount", buffer="game")
            return

        if amount < 0:
            user.speak_l("colorgame-invalid-bet-amount", buffer="game")
            return

        proposed = dict(player.current_bets)
        if amount == 0:
            proposed.pop(color, None)
        else:
            if amount < self.options.minimum_bet:
                user.speak_l(
                    "colorgame-bet-below-minimum",
                    buffer="game",
                    amount=self.options.minimum_bet,
                )
                return
            proposed[color] = amount

        total = sum(proposed.values())
        cap = self._player_bet_cap(player)
        if total > cap:
            user.speak_l("colorgame-bet-exceeds-bankroll", buffer="game", amount=cap)
            return

        player.current_bets = proposed
        user.speak_l(
            "colorgame-bet-updated",
            buffer="game",
            color=self._color_name(user.locale, color),
            amount=player.current_bets.get(color, 0),
            total=total,
        )

    def _action_clear_bets(self, player: ColorGamePlayer, action_id: str) -> None:
        _ = action_id
        player.current_bets.clear()
        user = self.get_user(player)
        if user:
            user.speak_l("colorgame-bets-cleared", buffer="game")

    def _action_confirm_bets(self, player: ColorGamePlayer, action_id: str) -> None:
        _ = action_id
        self._lock_player_bets(player)
        self.rebuild_all_menus()
        if self._all_betting_players_locked():
            self._start_roll_sequence()

    def _action_check_status(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return

        win_mode = Localization.get(
            user.locale,
            f"colorgame-win-condition-{self.options.win_condition.replace('_', '-')}",
        )
        if self.phase == PHASE_BETTING:
            user.speak_l(
                "colorgame-status-betting",
                buffer="game",
                round=self.round,
                limit=self.options.round_limit,
                seconds=self._remaining_betting_seconds(),
                win_mode=win_mode,
            )
        elif self.phase == PHASE_ROLLING:
            user.speak_l(
                "colorgame-status-rolling",
                buffer="game",
                round=self.round,
                limit=self.options.round_limit,
                win_mode=win_mode,
            )
        else:
            user.speak_l(
                "colorgame-status-resolving",
                buffer="game",
                round=self.round,
                limit=self.options.round_limit,
                win_mode=win_mode,
            )

        if isinstance(player, ColorGamePlayer) and not player.is_spectator:
            user.speak_l(
                "colorgame-status-bankroll",
                buffer="game",
                bankroll=player.bankroll,
                total=self._player_total_bet(player),
                cap=self._player_bet_cap(player),
            )
            user.speak_l(
                "colorgame-status-bet-lock",
                buffer="game",
                state=Localization.get(
                    user.locale,
                    "colorgame-bets-locked-status"
                    if player.bets_locked
                    else "colorgame-bets-open-status",
                ),
            )

        leaders = self._sorted_players_by_standing()
        if leaders:
            user.speak_l(
                "colorgame-status-leader",
                buffer="game",
                player=leaders[0].name,
                bankroll=leaders[0].bankroll,
            )

    def _action_check_bets(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("colorgame-bets-header", buffer="game")
        for line in self._betting_lines(user.locale):
            user.speak(line, buffer="game")

    def _action_check_last_roll(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        if not self.last_roll:
            user.speak_l("colorgame-last-roll-none", buffer="game")
            return
        user.speak_l(
            "colorgame-last-roll-header",
            buffer="game",
            colors=self._format_color_list(user.locale, self.last_roll),
        )
        for standing_player in self._sorted_players_by_standing():
            net = self.last_round_net_changes.get(standing_player.id, 0)
            user.speak_l(
                "colorgame-last-roll-line",
                buffer="game",
                player=standing_player.name,
                bets=self._format_bet_summary(
                    user.locale, self.last_round_bets.get(standing_player.id, {})
                ),
                net=net,
                bankroll=standing_player.bankroll,
            )

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        if self.phase == PHASE_BETTING:
            user.speak_l(
                "colorgame-whose-turn-betting",
                buffer="game",
                seconds=self._remaining_betting_seconds(),
            )
        elif self.phase == PHASE_ROLLING:
            user.speak_l("colorgame-whose-turn-rolling", buffer="game")
        else:
            user.speak_l("colorgame-whose-turn-resolving", buffer="game")

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("colorgame-standings-header", buffer="game")
        for line in self._standings_lines(user.locale):
            user.speak(line, buffer="game")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "colorgame-standings-header")]
        lines.extend(self._standings_lines(user.locale))
        self.status_box(player, lines)

    def _bot_input_bet_amount(self, player: ColorGamePlayer) -> str:
        if player.current_bets:
            pending = self._pending_actions.get(player.id, "")
            color = pending.removeprefix("set_bet_")
            return str(player.current_bets.get(color, 0))
        return str(self.options.minimum_bet)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.phase = PHASE_BETTING
        self.round = 0
        self.last_roll = []
        self.last_round_bets = {}
        self.last_round_net_changes = {}
        self.last_round_total_returns = {}

        active_players = self.get_active_players()
        self.team_manager.team_mode = "individual"
        self.team_manager.setup_teams([player.name for player in active_players])

        for player in active_players:
            if isinstance(player, ColorGamePlayer):
                player.bankroll = self.options.starting_bankroll
                player.current_bets.clear()
                player.bets_locked = False
                player.profitable_rounds = 0
                player.biggest_win = 0

        self.set_turn_players(active_players)
        self._sync_team_scores()
        self._announce_game_start()
        self.play_music("game_pig/mus.ogg")
        self._start_betting_round()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status != "playing" or self.is_sequence_bot_paused():
            return
        if self.phase == PHASE_BETTING:
            if self.betting_ticks_remaining > 0:
                self.betting_ticks_remaining -= 1
            if self.betting_ticks_remaining <= 0:
                self._auto_lock_unconfirmed_players()
                if self.phase == PHASE_BETTING and self._all_betting_players_locked():
                    self._start_roll_sequence()
                return
            self._process_betting_bots()

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id != ROLL_SEQUENCE_ID or callback_id != "resolve_roll":
            return
        if self.status != "playing":
            return
        rolled = [str(color) for color in payload.get("rolled", [])]
        if len(rolled) != ROLL_DICE_COUNT:
            return
        self._finalize_roll(rolled)

    def build_game_result(self) -> GameResult:
        sorted_players = self._sorted_players_by_standing()
        top_key = self._standings_key(sorted_players[0]) if sorted_players else None
        winners = [
            player for player in sorted_players if self._standings_key(player) == top_key
        ]
        rankings = []
        for player in sorted_players:
            rankings.append(
                {
                    "members": [player.name],
                    "bankroll": player.bankroll,
                    "profitable_rounds": player.profitable_rounds,
                    "biggest_win": player.biggest_win,
                }
            )
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
                "winner_ids": [player.id for player in winners],
                "winner_name": winners[0].name if len(winners) == 1 else None,
                "rankings": rankings,
                "rounds_played": self.round,
                "round_limit": self.options.round_limit,
                "win_condition": self.options.win_condition,
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
                    "colorgame-score-line",
                    rank=index,
                    player=name,
                    bankroll=entry.get("bankroll", 0),
                    profitable_rounds=entry.get("profitable_rounds", 0),
                    biggest_win=entry.get("biggest_win", 0),
                    status=Localization.get(
                        locale,
                        "colorgame-standing-live"
                        if entry.get("bankroll", 0) > 0
                        else "colorgame-standing-bust",
                    ),
                )
            )
        return lines
