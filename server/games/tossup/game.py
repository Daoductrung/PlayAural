"""Toss Up push-your-luck dice game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import random_dice_throw_sound
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


RISK_CONFIRM_TICKS = 200
RISK_CONFIRM_SECONDS = 10


@dataclass
class TossUpPlayer(Player):
    """Player state for Toss Up game."""

    turn_points: int = 0  # Points accumulated this turn (lost on bust)
    dice_count: int = 0  # Number of dice remaining this turn
    last_roll: dict[str, int] = field(
        default_factory=dict
    )  # Last roll results {green, yellow, red}
    pending_risky_action: str = ""
    risky_confirm_ticks: int = 0


@dataclass
class TossUpOptions(GameOptions):
    """Options for Toss Up game using declarative option system."""

    target_score: int = option_field(
        IntOption(
            default=100,
            min_val=20,
            max_val=500,
            value_key="score",
            label="game-set-target-score",
            prompt="game-enter-target-score",
            change_msg="game-option-changed-target",
            description="tossup-desc-target-score",
        )
    )
    starting_dice: int = option_field(
        IntOption(
            default=10,
            min_val=5,
            max_val=20,
            value_key="count",
            label="tossup-set-starting-dice",
            prompt="tossup-enter-starting-dice",
            change_msg="tossup-option-changed-dice",
            description="tossup-desc-starting-dice",
        )
    )
    rules_variant: str = option_field(
        MenuOption(
            default="Standard",
            value_key="variant",
            choices=lambda g, p: ["Standard", "PlayAural"],
            choice_labels={
                "Standard": "tossup-rules-standard",
                "PlayAural": "tossup-rules-PlayAural",
            },
            label="tossup-set-rules-variant",
            prompt="tossup-select-rules-variant",
            change_msg="tossup-option-changed-rules",
            description="tossup-desc-rules-variant",
        )
    )


@dataclass
@register_game
class TossUpGame(Game):
    """Traffic-light dice game with classic and forgiving rules."""

    relevant_preferences = [
        "brief_announcements",
        "confirm_destructive_actions",
    ]

    # Game-specific state
    players: list[TossUpPlayer] = field(default_factory=list)
    options: TossUpOptions = field(default_factory=TossUpOptions)
    tiebreaker_player_names: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Toss Up"

    @classmethod
    def get_type(cls) -> str:
        return "tossup"

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
    ) -> TossUpPlayer:
        """Create a new player with TossUp-specific state."""
        return TossUpPlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            turn_points=0,
            dice_count=0,
            last_roll={},
            pending_risky_action="",
            risky_confirm_ticks=0,
        )

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: TossUpPlayer,
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

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _round_players(self) -> list[TossUpPlayer]:
        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, TossUpPlayer)
        ]
        if not self.tiebreaker_player_names:
            return active
        finalists = set(self.tiebreaker_player_names)
        return [player for player in active if player.name in finalists]

    def _clear_risky_confirmation(self, player: TossUpPlayer) -> None:
        player.pending_risky_action = ""
        player.risky_confirm_ticks = 0

    def _focus_roll_after_action(self, player: TossUpPlayer) -> None:
        """Return a touch player's completed action to the persistent Roll anchor."""
        if self.is_touch_client(self.get_user(player)):
            self.request_menu_focus(player, "roll")

    def _is_classic_rules(self) -> bool:
        """Unknown legacy values fall back to the safer classic rules."""
        return self.options.rules_variant != "PlayAural"

    def _has_crossed_target(self, score: int) -> bool:
        return score > self.options.target_score

    def _bust_probability(self, dice_count: int) -> float:
        dice_count = max(1, dice_count)
        if self._is_classic_rules():
            # No green, with at least one red: P(no green) - P(all yellow).
            return (0.5**dice_count) - ((1 / 3) ** dice_count)
        return (1 / 3) ** dice_count

    def _score_to_beat(self, player: TossUpPlayer) -> int:
        scores = [
            self.get_player_score(other)
            for other in self._round_players()
            if other.id != player.id
        ]
        return max([self.options.target_score, *scores])

    def _should_confirm_risky_roll(self, player: TossUpPlayer) -> bool:
        if player.is_bot or not player.last_roll or player.turn_points <= 0:
            self._clear_risky_confirmation(player)
            return False

        banked = self.get_player_score(player)
        potential_total = banked + player.turn_points
        winning_bank = potential_total > self._score_to_beat(player)
        risk = self._bust_probability(player.dice_count)
        meaningful = player.turn_points >= max(
            5, min(15, self.options.target_score // 10)
        )
        high_stakes = meaningful and risk >= 0.05
        if not winning_bank and not high_stakes:
            self._clear_risky_confirmation(player)
            return False

        user = self.get_user(player)
        if not user or not user.preferences.get_effective(
            "confirm_destructive_actions", game_type=self.get_type()
        ):
            self._clear_risky_confirmation(player)
            return False

        signature = (
            f"roll:{self.round}:{banked}:{player.turn_points}:"
            f"{player.dice_count}:{self.options.rules_variant}"
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
            "tossup-confirm-risky-roll",
            buffer="game",
            points=player.turn_points,
            dice=player.dice_count,
            risk=round(risk * 100, 1),
            total=potential_total,
            target=self.options.target_score,
            winning="yes" if winning_bank else "no",
            seconds=RISK_CONFIRM_SECONDS,
        )
        return True

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label methods for turn actions
    # ==========================================================================

    def _turn_action_disabled_reason(
        self, player: Player, action: str
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return f"tossup-error-{action}-not-playing"
        if player.is_spectator:
            return "tossup-error-spectator-action"
        current = self.current_player
        if current is None:
            return f"tossup-error-{action}-no-turn"
        if current != player:
            return (
                f"tossup-error-{action}-not-your-turn",
                {"player": current.name},
            )
        if not isinstance(player, TossUpPlayer):
            return "action-not-available"
        return None

    def _is_roll_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        """Check if roll action is enabled."""
        return self._turn_action_disabled_reason(player, "roll")

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Keep Roll visible during play as a stable menu focus anchor."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for roll action showing dice count."""
        tossup_player: TossUpPlayer = player  # type: ignore[assignment]
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if not tossup_player.last_roll:
            # First roll of turn
            return Localization.get(
                locale, "tossup-roll-first", count=tossup_player.dice_count
            )
        else:
            # Subsequent rolls
            return Localization.get(
                locale, "tossup-roll-remaining", count=tossup_player.dice_count
            )

    def _is_bank_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        """Check if bank action is enabled."""
        reason = self._turn_action_disabled_reason(player, "bank")
        if reason:
            return reason
        tossup_player: TossUpPlayer = player  # type: ignore[assignment]
        if not tossup_player.last_roll:
            return "tossup-error-bank-roll-first"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Keep Bank present during play as a stable menu focus anchor."""
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for bank action showing current points."""
        tossup_player: TossUpPlayer = player  # type: ignore[assignment]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "tossup-bank", points=tossup_player.turn_points)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: TossUpPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "tossup-roll-first", count=10),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "tossup-bank", points=0),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                get_label="_get_bank_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    touch_standard_order = [
        "check_turn_status",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_turn_status",
                label=Localization.get(locale, "tossup-check-turn-status"),
                handler="_action_check_turn_status",
                is_enabled="_is_check_turn_status_enabled",
                is_hidden="_is_check_turn_status_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.touch_standard_order)

        return action_set

    # Touch visibility overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Keep the table roster available to touch clients."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Keep turn information available to touch clients during play."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Keep scores available to touch clients during play."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_turn_status_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "tossup-error-status-not-playing"
        if not isinstance(self.current_player, TossUpPlayer):
            return "tossup-error-status-no-turn"
        return None

    def _is_check_turn_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        # Call parent for lobby/standard keybinds (includes t, s, shift+s)
        super().setup_keybinds()

        # Turn action keybinds
        self.define_keybind(
            "r",
            Localization.get("en", "tossup-roll-first", count=10),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "b",
            Localization.get("en", "tossup-bank", points=0),
            ["bank"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "h",
            Localization.get("en", "tossup-check-turn-status"),
            ["check_turn_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        if not isinstance(player, TossUpPlayer):
            return
        tossup_player = player

        if self._should_confirm_risky_roll(tossup_player):
            self._focus_roll_after_action(tossup_player)
            return
        self._clear_risky_confirmation(tossup_player)

        self.play_sound(random_dice_throw_sound())

        # Roll the dice
        green = 0
        yellow = 0
        red = 0

        is_classic = self._is_classic_rules()
        dice_to_roll = tossup_player.dice_count
        if not 1 <= dice_to_roll <= self.options.starting_dice:
            dice_to_roll = self.options.starting_dice
            tossup_player.dice_count = dice_to_roll

        for _ in range(dice_to_roll):
            if is_classic:
                # Classic: 3 green, 2 yellow, 1 red on each six-sided die.
                roll = random.randint(1, 6)
                if roll <= 3:
                    green += 1
                elif roll <= 5:
                    yellow += 1
                else:
                    red += 1
            else:
                # Forgiving variant: equal color distribution.
                roll = random.randint(1, 3)
                if roll == 1:
                    green += 1
                elif roll == 2:
                    yellow += 1
                else:
                    red += 1

        tossup_player.last_roll = {"green": green, "yellow": yellow, "red": red}

        is_bust = (
            green == 0 and red > 0
            if is_classic
            else green == 0 and yellow == 0
        )

        if is_bust:
            self.play_sound("game_pig/lose.ogg")
            lost = tossup_player.turn_points
            self._announce_roll_resolution(
                tossup_player,
                green=green,
                yellow=yellow,
                red=red,
                busted=True,
                lost=lost,
            )
            tossup_player.turn_points = 0
            self._focus_roll_after_action(tossup_player)
            self.end_turn()
            return

        # Add green dice to turn points
        tossup_player.turn_points += green
        remaining = yellow + red
        fresh = remaining == 0
        tossup_player.dice_count = remaining
        if fresh:
            tossup_player.dice_count = self.options.starting_dice

        self._announce_roll_resolution(
            tossup_player,
            green=green,
            yellow=yellow,
            red=red,
            busted=False,
            gained=green,
            remaining=remaining,
            fresh=fresh,
        )

        if tossup_player.is_bot:
            BotHelper.jolt_bot(tossup_player, ticks=random.randint(10, 20))
        self._focus_roll_after_action(tossup_player)
        self.refresh_menus()

    def _announce_roll_resolution(
        self,
        actor: TossUpPlayer,
        *,
        green: int,
        yellow: int,
        red: int,
        busted: bool,
        lost: int = 0,
        gained: int = 0,
        remaining: int = 0,
        fresh: bool = False,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == actor.id
            results = self._format_roll_results(user.locale, green, yellow, red)
            if self._wants_brief(user):
                key = (
                    "tossup-you-bust-brief"
                    if busted and is_actor
                    else "tossup-player-busts-brief"
                    if busted
                    else "tossup-you-roll-safe-brief"
                    if is_actor
                    else "tossup-player-rolls-safe-brief"
                )
                payload = {
                    "results": results,
                    "points": lost,
                    "turn_points": actor.turn_points,
                    "dice_count": actor.dice_count,
                    "fresh": "yes" if fresh else "no",
                }
                if not is_actor:
                    payload["player"] = actor.name
                user.speak_l(key, buffer="game", **payload)
                continue

            roll_key = "tossup-you-roll" if is_actor else "tossup-player-rolls"
            roll_payload = {"results": results}
            if not is_actor:
                roll_payload["player"] = actor.name
            user.speak_l(roll_key, buffer="game", **roll_payload)

            if busted:
                key = "tossup-you-bust" if is_actor else "tossup-player-busts"
                payload = {
                    "points": lost,
                    "variant": self.options.rules_variant,
                }
            else:
                key = (
                    "tossup-you-have-points"
                    if is_actor
                    else "tossup-player-has-points"
                )
                payload = {
                    "gained": gained,
                    "turn_points": actor.turn_points,
                    "dice_count": remaining,
                }
            if not is_actor:
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

            if not busted and fresh:
                key = "tossup-you-get-fresh" if is_actor else "tossup-player-gets-fresh"
                payload = {"count": actor.dice_count}
                if not is_actor:
                    payload["player"] = actor.name
                user.speak_l(key, buffer="game", **payload)

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Handle bank action."""
        if not isinstance(player, TossUpPlayer):
            return
        tossup_player = player

        self.play_sound("game_pig/bank.ogg")
        banked = tossup_player.turn_points
        threshold_was_crossed = any(
            self._has_crossed_target(self.get_player_score(other))
            for other in self._round_players()
        )

        # Add to team score via TeamManager
        self._team_manager.add_to_team_score(player.name, banked)
        team = self._team_manager.get_team(player.name)
        total = team.total_score if team else 0

        tossup_player.turn_points = 0
        self._clear_risky_confirmation(tossup_player)

        self._broadcast_actor_l(
            tossup_player,
            "tossup-you-bank",
            "tossup-player-banks",
            brief_personal_key="tossup-you-bank-brief",
            brief_others_key="tossup-player-banks-brief",
            points=banked,
            total=total,
        )

        if (
            not self.tiebreaker_player_names
            and not threshold_was_crossed
            and self._has_crossed_target(total)
        ):
            remaining_turns = len(self.turn_players) - self.turn_index - 1
            if remaining_turns > 0:
                self._broadcast_actor_l(
                    tossup_player,
                    "tossup-you-trigger-final-turns",
                    "tossup-player-triggers-final-turns",
                    brief_personal_key="tossup-you-trigger-final-turns-brief",
                    brief_others_key="tossup-player-triggers-final-turns-brief",
                    score=total,
                    target=self.options.target_score,
                    count=remaining_turns,
                )

        self._focus_roll_after_action(tossup_player)
        self.end_turn()

    def _action_check_turn_status(self, player: Player, action_id: str) -> None:
        current = self.current_player
        user = self.get_user(player)
        if not isinstance(current, TossUpPlayer) or not user:
            return

        score = self.get_player_score(current)
        is_actor = current.id == player.id
        if current.last_roll:
            results = self._format_roll_results(
                user.locale,
                current.last_roll.get("green", 0),
                current.last_roll.get("yellow", 0),
                current.last_roll.get("red", 0),
            )
            key = (
                "tossup-your-turn-status"
                if is_actor
                else "tossup-player-turn-status"
            )
            payload = {
                "score": score,
                "turn_points": current.turn_points,
                "dice_count": current.dice_count,
                "results": results,
            }
        else:
            key = (
                "tossup-your-turn-awaiting-roll"
                if is_actor
                else "tossup-player-turn-awaiting-roll"
            )
            payload = {
                "score": score,
                "dice_count": current.dice_count,
            }
        if not is_actor:
            payload["player"] = current
        payload = self._resolve_broadcast_kwargs(user.locale, payload)
        user.speak_l(key, buffer="game", **payload)

    def get_player_score(self, player: TossUpPlayer) -> int:
        """Get a player's total score from TeamManager."""
        team = self._team_manager.get_team(player.name)
        return team.total_score if team else 0

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        """Validate every setup value, including directly restored options."""
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 20 <= self.options.target_score <= 500:
            errors.append(
                (
                    "tossup-error-target-out-of-range",
                    {"value": self.options.target_score, "min": 20, "max": 500},
                )
            )
        if not 5 <= self.options.starting_dice <= 20:
            errors.append(
                (
                    "tossup-error-dice-out-of-range",
                    {"value": self.options.starting_dice, "min": 5, "max": 20},
                )
            )
        if self.options.rules_variant not in {"Standard", "PlayAural"}:
            errors.append(
                (
                    "tossup-error-rules-variant",
                    {"variant": self.options.rules_variant},
                )
            )
        return errors

    def _announce_game_start(self) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            rules_key = (
                "tossup-rules-standard"
                if self._is_classic_rules()
                else "tossup-rules-PlayAural"
            )
            rules = Localization.get(user.locale, rules_key)
            key = (
                "tossup-game-start-brief"
                if self._wants_brief(user)
                else "tossup-game-start"
            )
            user.speak_l(
                key,
                buffer="game",
                target=self.options.target_score,
                dice=self.options.starting_dice,
                rules=rules,
            )

    def _finish_with_winner(self, winner: TossUpPlayer) -> None:
        self.tiebreaker_player_names = []
        for player in self.players:
            self._clear_risky_confirmation(player)
        self.play_sound("game_pig/win.ogg")
        self._broadcast_actor_l(
            winner,
            "tossup-you-win",
            "tossup-winner",
            brief_personal_key="tossup-you-win-brief",
            brief_others_key="tossup-winner-brief",
            score=self.get_player_score(winner),
        )
        self.finish_game()

    def rebuild_runtime_state(self) -> None:
        """Repair legacy tiebreaker saves that changed players into spectators."""
        super().rebuild_runtime_state()
        if self.tiebreaker_player_names or self.status != "playing":
            return

        team_members = {
            member
            for team in self._team_manager.teams
            for member in team.members
        }
        legacy_nonfinalists = [
            player
            for player in self.players
            if player.is_spectator and player.name in team_members
        ]
        if not legacy_nonfinalists:
            return

        finalists = [
            player
            for player in self.players
            if not player.is_spectator
            and player.name in team_members
            and self._has_crossed_target(self.get_player_score(player))
        ]
        if len(finalists) < 2:
            return

        self.tiebreaker_player_names = [player.name for player in finalists]
        for player in legacy_nonfinalists:
            player.is_spectator = False

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.tiebreaker_player_names = []

        # Set up teams (individual mode only for now)
        active_players = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Initialize turn order
        self.set_turn_players(active_players)

        # Reset player state
        for player in active_players:
            player.turn_points = 0
            player.dice_count = self.options.starting_dice
            player.last_roll = {}
            self._clear_risky_confirmation(player)

        # Play intro music
        self.play_music("game_pig/mus.ogg")
        self._announce_game_start()

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        round_players = self._round_players()
        if not round_players:
            return
        if len(round_players) == 1 and self.tiebreaker_player_names:
            self._finish_with_winner(round_players[0])
            return

        self.round += 1

        self.set_turn_players(round_players)

        self.play_sound("game_pig/roundstart.ogg")
        if self.tiebreaker_player_names:
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                players = Localization.format_list_and(
                    user.locale, [p.name for p in round_players]
                )
                key = (
                    "tossup-tiebreaker-round-start-brief"
                    if self._wants_brief(user)
                    else "tossup-tiebreaker-round-start"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    round=self.round,
                    players=players,
                )
        else:
            self._broadcast_global_l(
                "tossup-round-start", "tossup-round-start-brief", round=self.round
            )

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        tossup_player: TossUpPlayer = player  # type: ignore[assignment]
        tossup_player.turn_points = 0
        tossup_player.dice_count = self.options.starting_dice
        tossup_player.last_roll = {}
        self._clear_risky_confirmation(tossup_player)

        # Get current score
        current_score = self.get_player_score(tossup_player)

        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("turn.ogg")
        self._broadcast_actor_l(
            tossup_player,
            "tossup-your-turn",
            "tossup-player-turn",
            brief_personal_key="tossup-your-turn-brief",
            brief_others_key="tossup-player-turn-brief",
            score=current_score,
            dice=tossup_player.dice_count,
        )

        # Set up bot target if this is a bot's turn
        if player.is_bot:
            self._setup_bot_target(player)

        self.refresh_menus()

    def _setup_bot_target(self, player: Player) -> None:
        """Set up the bot's target score for this turn."""
        tossup_player: TossUpPlayer = player  # type: ignore

        target = random.randint(8, 16)
        round_players = self._round_players()
        my_score = self.get_player_score(tossup_player)
        opponent_scores = [
            self.get_player_score(other)
            for other in round_players
            if other.id != player.id
        ]
        leader_score = max(opponent_scores, default=0)

        if self._has_crossed_target(leader_score):
            target = leader_score + 1 - my_score
        else:
            points_needed = self.options.target_score + 1 - my_score
            if leader_score >= self.options.target_score - 15 or points_needed <= target:
                target = max(1, points_needed)

        BotHelper.set_target(player, max(1, target))

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if not self.game_active:
            return

        for tossup_player in self.players:
            if tossup_player.risky_confirm_ticks > 0:
                tossup_player.risky_confirm_ticks -= 1
                if tossup_player.risky_confirm_ticks <= 0:
                    self._clear_risky_confirmation(tossup_player)

        # Ensure bot target is set up (needed after reload)
        player = self.current_player
        if player and player.is_bot and BotHelper.get_target(player) is None:
            self._setup_bot_target(player)

        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: TossUpPlayer) -> str | None:
        """Bot AI decision making. Called by BotHelper."""
        target = BotHelper.get_target(player)
        if target is None:
            target = 15  # Default fallback

        my_score = self.get_player_score(player)
        potential_total = my_score + player.turn_points
        score_to_beat = self._score_to_beat(player)
        if potential_total > score_to_beat:
            return "bank"

        # Decide based on dice count and target
        dice_count = player.dice_count

        if not player.last_roll:
            return "roll"

        if player.turn_points == 0:
            return "roll"

        bust_risk = self._bust_probability(dice_count)
        green_probability = 0.5 if self._is_classic_rules() else 1 / 3
        expected_gain = dice_count * green_probability
        expected_loss = player.turn_points * bust_risk

        if self._has_crossed_target(score_to_beat):
            return "roll"

        if expected_loss >= expected_gain and player.turn_points >= max(
            5, self.options.target_score // 12
        ):
            return "bank"

        # If we've hit our target, consider banking based on dice count
        if player.turn_points >= target:
            bank_chance = min(
                0.95,
                0.10 + (bust_risk * 2.5) + min(0.35, player.turn_points / 100),
            )
            if random.random() < bank_chance:
                return "bank"
            return "roll"
        return "roll"

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check if round is over (all active players have gone)
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            # Next player
            self.advance_turn(announce=False)
            self._start_turn()

    def _on_round_end(self) -> None:
        """Handle end of a round."""
        round_players = self._round_players()
        winners: list[TossUpPlayer] = []
        high_score = 0

        for player in round_players:
            score = self.get_player_score(player)
            if self._has_crossed_target(score):
                if score > high_score:
                    winners = [player]
                    high_score = score
                elif score == high_score:
                    winners.append(player)

        if len(winners) == 1:
            self._finish_with_winner(winners[0])
        elif len(winners) > 1:
            names = [w.name for w in winners]
            for player in self.players:
                user = self.get_user(player)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    key = (
                        "tossup-tie-tiebreaker-brief"
                        if self._wants_brief(user)
                        else "tossup-tie-tiebreaker"
                    )
                    user.speak_l(key, buffer="game", players=names_str)

            self.tiebreaker_player_names = names
            self._start_round()
        else:
            self._start_round()

    def build_game_result(self) -> GameResult:
        """Build the game result with TossUp-specific data."""
        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )
        winner = sorted_teams[0] if sorted_teams else None

        # Build final scores dict
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
                "winner_name": self._team_manager.get_team_name(winner)
                if winner
                else None,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "rules_variant": self.options.rules_variant,
                "starting_dice": self.options.starting_dice,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Toss Up game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(locale, "tossup-line-format", rank=i, player=name, points=points_str)
            )

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """Override to use TossUp's turn advancement logic."""
        # Jolt all bots to pause for the turn change
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))
        self._on_turn_end()

    def _format_roll_results(self, locale: str, green: int, yellow: int, red: int) -> str:
        """Format roll results list for a specific locale."""
        parts = []
        if green > 0:
            parts.append(Localization.get(locale, "tossup-result-green", count=green))
        if yellow > 0:
            parts.append(Localization.get(locale, "tossup-result-yellow", count=yellow))
        if red > 0:
            parts.append(Localization.get(locale, "tossup-result-red", count=red))
        return Localization.format_list_and(locale, parts)
