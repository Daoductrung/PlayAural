"""Pig dice game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, TeamModeOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.teams import Team, TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


DEFAULT_TARGET_SCORE = 100
ROLL_SEQUENCE_ID = "pig_roll"
ROLL_SEQUENCE_TAG = "pig_roll"
ROLL_REVEAL_DELAY_TICKS = 8
RISK_CONFIRM_TICKS = 200
RISK_CONFIRM_SECONDS = 10


@dataclass
class PigPlayer(Player):
    """Per-player Pig state."""

    round_score: int = 0
    pending_risky_action: str = ""
    risky_confirm_ticks: int = 0


@dataclass
class PigOptions(GameOptions):
    """Host-configurable Pig settings."""

    target_score: int = option_field(
        IntOption(
            default=DEFAULT_TARGET_SCORE,
            min_val=10,
            max_val=1000,
            value_key="score",
            label="game-set-target-score",
            prompt="game-enter-target-score",
            change_msg="game-option-changed-target",
            description="pig-desc-target-score",
        )
    )
    min_bank_points: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=999,
            value_key="points",
            label="pig-set-min-bank",
            prompt="pig-enter-min-bank",
            change_msg="pig-option-changed-min-bank",
            description="pig-desc-min-bank",
        )
    )
    dice_sides: int = option_field(
        IntOption(
            default=6,
            min_val=4,
            max_val=20,
            value_key="sides",
            label="pig-set-dice-sides",
            prompt="pig-enter-dice-sides",
            change_msg="pig-option-changed-dice",
            description="pig-desc-dice-sides",
        )
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=lambda g, p: TeamManager.get_all_team_modes(2, 6),
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
            description="pig-desc-team-mode",
        )
    )


@dataclass
@register_game
class PigGame(Game):
    """Classic push-your-luck Pig with optional teams and die variants."""

    relevant_preferences = [
        "brief_announcements",
        "confirm_destructive_actions",
    ]

    players: list[PigPlayer] = field(default_factory=list)
    options: PigOptions = field(default_factory=PigOptions)
    winner_team_index: int = -1

    @classmethod
    def get_name(cls) -> str:
        return "Pig"

    @classmethod
    def get_type(cls) -> str:
        return "pig"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> PigPlayer:
        return PigPlayer(id=player_id, name=name, is_bot=is_bot)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: PigPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast an event with listener-specific perspective and verbosity."""
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
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _broadcast_hold(
        self,
        actor: PigPlayer,
        team: Team | None,
        *,
        points: int,
        total: int,
    ) -> None:
        """Announce a hold with the team name localized for each listener."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == actor.id
            if is_actor:
                key = (
                    "pig-you-hold-brief"
                    if self._wants_brief(user)
                    else "pig-you-hold"
                )
            else:
                key = (
                    "pig-player-holds-brief"
                    if self._wants_brief(user)
                    else "pig-player-holds"
                )

            payload = {
                "points": points,
                "total": total,
                "team": "yes" if self._is_team_game() else "no",
                "team_name": (
                    self._team_manager.get_team_name(team, user.locale)
                    if team
                    else actor.name
                ),
            }
            if not is_actor:
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

    def _is_team_game(self) -> bool:
        return self.options.team_mode != "individual"

    def _bank_minimum(self) -> int:
        return max(1, self.options.min_bank_points)

    def _expected_hold_threshold(self) -> int:
        """Return the one-roll expected-value break-even turn total."""
        sides = max(2, self.options.dice_sides)
        return max(1, ((sides - 1) * (sides + 2)) // 2)

    def _clear_risky_confirmation(self, player: PigPlayer) -> None:
        player.pending_risky_action = ""
        player.risky_confirm_ticks = 0

    def _should_confirm_risky_roll(self, player: PigPlayer) -> bool:
        if player.is_bot or self._is_bank_enabled(player) is not None:
            self._clear_risky_confirmation(player)
            return False

        banked_score = self.get_player_score(player)
        winning_hold = banked_score + player.round_score >= self.options.target_score
        high_stakes = player.round_score >= self._expected_hold_threshold()
        if not winning_hold and not high_stakes:
            self._clear_risky_confirmation(player)
            return False

        user = self.get_user(player)
        if not user or not user.preferences.get_effective(
            "confirm_destructive_actions", game_type=self.get_type()
        ):
            self._clear_risky_confirmation(player)
            return False

        signature = (
            f"roll:{self.round}:{banked_score}:{player.round_score}:"
            f"{self.options.dice_sides}"
        )
        if (
            player.pending_risky_action == signature
            and player.risky_confirm_ticks > 0
        ):
            self._clear_risky_confirmation(player)
            return False

        player.pending_risky_action = signature
        player.risky_confirm_ticks = RISK_CONFIRM_TICKS
        user.speak_l(
            "pig-confirm-risky-roll",
            buffer="game",
            points=player.round_score,
            risk=round(100 / self.options.dice_sides),
            total=banked_score + player.round_score,
            target=self.options.target_score,
            winning="yes" if winning_hold else "no",
            seconds=RISK_CONFIRM_SECONDS,
        )
        return True

    # ======================================================================
    # Actions and menus
    # ======================================================================

    def _turn_action_disabled_reason(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "pig-action-resolving"
        return None

    def _is_roll_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        return self._turn_action_disabled_reason(player)

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_bank_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        reason = self._turn_action_disabled_reason(player)
        if reason:
            return reason
        if not isinstance(player, PigPlayer):
            return "action-disabled"
        if player.round_score <= 0:
            return "pig-no-turn-points"
        required = self._bank_minimum()
        if player.round_score < required:
            return (
                "pig-need-more-points",
                {"current": player.round_score, "required": required},
            )
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Keep Hold stable during play so touch and screen-reader focus persists."""
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        points = player.round_score if isinstance(player, PigPlayer) else 0
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "pig-hold", points=points)

    def create_turn_action_set(self, player: PigPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "pig-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "pig-hold", points=0),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                get_label="_get_bank_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="check_turn_status",
                label=Localization.get(locale, "pig-check-turn-status"),
                handler="_action_check_turn_status",
                is_enabled="_is_check_turn_status_enabled",
                is_hidden="_is_check_turn_status_hidden",
                include_spectators=True,
            )
        )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_turn_status",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def _is_check_turn_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_turn_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def _turn_status_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(
                    locale, "pig-status-target", target=self.options.target_score
                ),
                id="target",
            ),
            MenuItem(
                text=Localization.get(locale, "pig-status-round", round=self.round),
                id="round",
            ),
        ]

        current = self.current_player
        if isinstance(current, PigPlayer):
            banked = self.get_player_score(current)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "pig-status-current-turn",
                        player=current.name,
                        banked=banked,
                        turn=current.round_score,
                        potential=banked + current.round_score,
                    ),
                    id=f"current:{current.id}",
                )
            )

        for rank, team in enumerate(
            self._team_manager.get_sorted_teams(by_score=True, descending=True), 1
        ):
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "pig-status-standing",
                        rank=rank,
                        team=self._team_manager.get_team_name(team, locale),
                        score=team.total_score,
                    ),
                    id=f"team:{team.index}",
                )
            )
        return items

    def _action_check_turn_status(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "pig_turn_status",
            lambda _player, live_user: self._turn_status_items(live_user.locale),
            focus_id="target",
        )

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "r",
            Localization.get("en", "pig-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "h",
            Localization.get("en", "pig-hold", points=0),
            ["bank"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "pig-check-turn-status"),
            ["check_turn_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ======================================================================
    # Action resolution
    # ======================================================================

    def _action_roll(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PigPlayer):
            return
        if self.has_active_sequence(tag=ROLL_SEQUENCE_TAG):
            return
        if self._should_confirm_risky_roll(player):
            return

        self._clear_risky_confirmation(player)
        roll = random.randint(1, self.options.dice_sides)
        payload = {"player_id": player.id, "roll": roll}
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op("game_pig/roll.ogg")],
                delay_after_ticks=ROLL_REVEAL_DELAY_TICKS,
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("resolve_roll", payload)]
            ),
        ]
        self.start_sequence(
            ROLL_SEQUENCE_ID,
            beats,
            tag=ROLL_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            replace_existing=False,
        )
        self.refresh_menus(player)

    def _resolve_roll(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if (
            not isinstance(player, PigPlayer)
            or player is not self.current_player
            or self.status != "playing"
        ):
            return
        try:
            roll = int(payload.get("roll", 0))
        except (TypeError, ValueError):
            return
        if not 1 <= roll <= self.options.dice_sides:
            return

        if roll == 1:
            lost = player.round_score
            player.round_score = 0
            self._clear_risky_confirmation(player)
            self.play_sound("game_pig/lose.ogg")
            self._broadcast_actor_l(
                player,
                "pig-you-bust",
                "pig-player-busts",
                brief_personal_key="pig-you-bust-brief",
                brief_others_key="pig-player-busts-brief",
                points=lost,
            )
            self.end_turn()
            return

        player.round_score += roll
        self._broadcast_actor_l(
            player,
            "pig-you-roll-result",
            "pig-player-roll-result",
            brief_personal_key="pig-you-roll-result-brief",
            brief_others_key="pig-player-roll-result-brief",
            roll=roll,
            total=player.round_score,
        )
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
        self.refresh_menus()

    def _action_bank(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PigPlayer):
            return

        self._clear_risky_confirmation(player)
        banked = player.round_score
        self._team_manager.add_to_team_score(player.name, banked)
        team = self._team_manager.get_team(player.name)
        total = team.total_score if team else 0
        player.round_score = 0

        self.play_sound("game_pig/bank.ogg")
        self._broadcast_hold(
            player,
            team,
            points=banked,
            total=total,
        )
        self.refresh_menus()

        if team and total >= self.options.target_score:
            self._finish_with_team(team)
            return
        self.end_turn()

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id == ROLL_SEQUENCE_ID and callback_id == "resolve_roll":
            self._resolve_roll(payload)

    # ======================================================================
    # Game flow and bot strategy
    # ======================================================================

    def get_player_score(self, player: PigPlayer) -> int:
        team = self._team_manager.get_team(player.name)
        return team.total_score if team else 0

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())

        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)
        if not 10 <= self.options.target_score <= 1000:
            errors.append(
                (
                    "pig-error-target-out-of-range",
                    {"value": self.options.target_score, "min": 10, "max": 1000},
                )
            )
        if not 0 <= self.options.min_bank_points <= 999:
            errors.append(
                (
                    "pig-error-min-bank-out-of-range",
                    {"value": self.options.min_bank_points, "min": 0, "max": 999},
                )
            )
        if not 4 <= self.options.dice_sides <= 20:
            errors.append(
                (
                    "pig-error-dice-sides-out-of-range",
                    {"value": self.options.dice_sides, "min": 4, "max": 20},
                )
            )
        if self.options.min_bank_points >= self.options.target_score:
            errors.append(
                (
                    "pig-error-min-bank-too-high",
                    {
                        "minimum": self.options.min_bank_points,
                        "target": self.options.target_score,
                    },
                )
            )
        return errors

    def on_start(self) -> None:
        self.cancel_sequences_by_tag(ROLL_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.winner_team_index = -1

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, PigPlayer)
        ]
        self._setup_team_manager_for_start(self.options.team_mode, active_players)
        self._team_manager.reset_all_scores()
        self.set_turn_players(self._get_team_turn_players(active_players))

        for player in self.players:
            player.round_score = 0
            self._clear_risky_confirmation(player)

        self.play_music("game_pig/mus.ogg")
        self._broadcast_global_l(
            "pig-game-start",
            "pig-game-start-brief",
            target=self.options.target_score,
            sides=self.options.dice_sides,
            minimum=self.options.min_bank_points,
            team="yes" if self._is_team_game() else "no",
        )
        self._start_round()

    def _start_round(self) -> None:
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, PigPlayer)
        ]
        if not active_players:
            return

        self.round += 1
        self.set_turn_players(self._get_team_turn_players(active_players))
        self.play_sound("game_pig/roundstart.ogg")
        self._broadcast_global_l(
            "pig-round-start",
            "pig-round-start-brief",
            round=self.round,
        )
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, PigPlayer):
            return

        player.round_score = 0
        self._clear_risky_confirmation(player)
        self.announce_turn(turn_sound="game_pig/turn.ogg")
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(12, 20))
        self.refresh_menus()

    def _on_turn_end(self) -> None:
        if self.turn_index >= len(self.turn_players) - 1:
            self._start_round()
            return
        self.advance_turn(announce=False)
        self._start_turn()

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        current = self.current_player
        if isinstance(current, PigPlayer):
            self._clear_risky_confirmation(current)
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))
        self._on_turn_end()

    def _bot_hold_threshold(self, player: PigPlayer) -> int:
        my_team = self._team_manager.get_team(player.name)
        if not my_team:
            return self._bank_minimum()

        my_score = my_team.total_score
        points_to_goal = max(1, self.options.target_score - my_score)
        base = self._expected_hold_threshold()
        threshold = base

        other_scores = [
            team.total_score
            for team in self._team_manager.teams
            if team.index != my_team.index
        ]
        leader_score = max(other_scores, default=my_score)
        gap = leader_score - my_score

        if points_to_goal <= base:
            threshold = points_to_goal
        elif leader_score >= self.options.target_score - base:
            threshold = min(points_to_goal, base + max(3, max(0, gap) // 3))
        elif gap > base:
            threshold += min(max(2, base // 2), gap // 4)
        elif gap < -base:
            threshold = max(1, (base * 3) // 4)

        return max(self._bank_minimum(), threshold)

    def bot_think(self, player: PigPlayer) -> str | None:
        if player is not self.current_player or self.is_sequence_gameplay_locked():
            return None
        if player.round_score <= 0:
            return "roll"
        if self._is_bank_enabled(player) is not None:
            return "roll"
        if (
            self.get_player_score(player) + player.round_score
            >= self.options.target_score
        ):
            return "bank"
        return (
            "bank"
            if player.round_score >= self._bot_hold_threshold(player)
            else "roll"
        )

    def _qualifying_teams(self) -> list[Team]:
        return self._team_manager.get_teams_at_or_above_score(
            self.options.target_score
        )

    def _restore_legacy_tiebreaker_players(self) -> None:
        """Undo spectator flags written by the removed equal-turn tiebreaker."""
        team_members = {
            member
            for team in self._team_manager.teams
            for member in team.members
        }
        for player in self.players:
            if player.is_spectator and player.name in team_members:
                player.is_spectator = False

    def _finish_with_team(self, winning_team: Team) -> None:
        if self.status != "playing":
            return
        self.winner_team_index = winning_team.index
        self.cancel_sequences_by_tag(ROLL_SEQUENCE_TAG)
        for player in self.players:
            self._clear_risky_confirmation(player)

        self.play_sound("game_pig/win.ogg")
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            listener_team = self._team_manager.get_team(listener.name)
            listener_won = (
                listener_team is not None
                and listener_team.index == winning_team.index
            )
            brief = self._wants_brief(user)
            if listener_won:
                key = "pig-you-win-brief" if brief else "pig-you-win"
            else:
                key = "pig-winner-brief" if brief else "pig-winner"
            user.speak_l(
                key,
                buffer="game",
                winner=self._team_manager.get_team_name(winning_team, user.locale),
                score=winning_team.total_score,
                team="yes" if self._is_team_game() else "no",
            )
        self.finish_game()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        for player in self.players:
            if player.risky_confirm_ticks > 0:
                player.risky_confirm_ticks -= 1
                if player.risky_confirm_ticks <= 0:
                    self._clear_risky_confirmation(player)

        # Older saves could be inside the removed equal-turn tiebreaker flow.
        if self.status == "playing" and not self.has_active_sequence(
            tag=ROLL_SEQUENCE_TAG
        ):
            qualifying = self._qualifying_teams()
            if qualifying:
                self._restore_legacy_tiebreaker_players()
                self._finish_with_team(
                    max(qualifying, key=lambda team: team.total_score)
                )
                return

        if (
            self.game_active
            and self.status == "playing"
            and not self.is_sequence_bot_paused()
        ):
            BotHelper.on_tick(self)

    # ======================================================================
    # Results
    # ======================================================================

    def _result_winner(self, sorted_teams: list[Team]) -> Team | None:
        for team in sorted_teams:
            if team.index == self.winner_team_index:
                return team
        return sorted_teams[0] if sorted_teams else None

    def build_game_result(self) -> GameResult:
        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )
        winner = self._result_winner(sorted_teams)

        final_scores = {}
        team_rankings = []
        for team in sorted_teams:
            name = self._team_manager.get_team_name(team)
            final_scores[name] = team.total_score
            team_rankings.append(
                {
                    "index": team.index,
                    "members": team.members,
                    "score": team.total_score,
                    "is_individual": self.options.team_mode == "individual",
                }
            )

        active_players = self.get_active_players()
        name_to_id = {player.name: player.id for player in active_players}
        winner_ids = [
            name_to_id[name]
            for name in (winner.members if winner else [])
            if name in name_to_id
        ]

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
                for player in active_players
            ],
            custom_data={
                "winner_name": (
                    self._team_manager.get_team_name(winner) if winner else None
                ),
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "team_mode": self.options.team_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        team_rankings = result.custom_data.get("team_rankings")

        if team_rankings:
            for rank, data in enumerate(team_rankings, 1):
                if data.get("is_individual") and data.get("members"):
                    name = data["members"][0]
                else:
                    name = Localization.get(
                        locale, "game-team-name", index=data["index"] + 1
                    )
                points = Localization.get(
                    locale, "game-points", count=data["score"]
                )
                lines.append(
                    Localization.get(
                        locale,
                        "pig-line-format",
                        rank=rank,
                        player=name,
                        points=points,
                    )
                )
            return lines

        for rank, (name, score) in enumerate(
            result.custom_data.get("final_scores", {}).items(), 1
        ):
            points = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(
                    locale,
                    "pig-line-format",
                    rank=rank,
                    player=name,
                    points=points,
                )
            )
        return lines
