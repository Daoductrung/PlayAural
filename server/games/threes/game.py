"""
Threes Game Implementation.

Low-score dice game: Roll 5 dice, keep at least one each roll.
Threes = 0 points. Lowest score wins!
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import DiceSet, random_dice_throw_sound
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


MIN_ROUNDS = 1
MAX_ROUNDS = 20


@dataclass
class ThreesPlayer(Player):
    """Player state for Threes game."""

    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=5, sides=6))
    turn_score: int = 0  # Score for current turn
    total_score: int = 0  # Total score across all rounds


@dataclass
class ThreesOptions(GameOptions):
    """Options for Threes game."""

    total_rounds: int = option_field(
        IntOption(
            default=10,
            min_val=MIN_ROUNDS,
            max_val=MAX_ROUNDS,
            value_key="rounds",
            label="threes-set-rounds",
            prompt="threes-enter-rounds",
            change_msg="threes-option-changed-rounds",
            description="threes-desc-rounds",
        )
    )


@dataclass
@register_game
class ThreesGame(Game, DiceGameMixin):
    """
    Threes dice game.

    Roll 5 dice, then keep at least one die each roll before rolling again.
    Kept dice become locked and can't be rerolled.
    Continue until all dice are locked or only 1 die remains.

    Scoring:
    - Threes = 0 points
    - All other dice = face value
    - Five sixes = "Shooting the moon" = -30 points

    Lowest score wins after all rounds.
    """

    relevant_preferences = ["brief_announcements", "dice_keeping_style"]
    score_sort_descending = False

    players: list[ThreesPlayer] = field(default_factory=list)
    options: ThreesOptions = field(default_factory=ThreesOptions)
    current_round: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Threes"

    @classmethod
    def get_type(cls) -> str:
        return "threes"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ThreesPlayer:
        """Create a new player with Threes-specific state."""
        return ThreesPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _active_threes_players(self) -> list[ThreesPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, ThreesPlayer)
        ]

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: ThreesPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast an actor event with listener-specific perspective."""
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
        self,
        full_key: str,
        brief_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast a global event with optional brief wording per listener."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _format_dice_values(self, values: list[int], locale: str) -> str:
        return Localization.format_list(locale, [str(value) for value in values])

    def _turn_score_for_values(self, values: list[int]) -> int:
        return sum(value for value in values if value != 3)

    def _focus_first_enabled_turn_action(self, player: ThreesPlayer) -> None:
        """Focus the first visible enabled item after an in-turn repaint."""
        for resolved in self.get_all_visible_actions(player):
            if resolved.enabled:
                self.request_menu_focus(player, resolved.action.id)
                return

    def _focus_touch_roll_anchor(self, player: ThreesPlayer) -> None:
        user = self.get_user(player)
        if self.is_touch_client(user):
            self.request_menu_focus(player, "roll")

    def _sync_team_scores(self) -> None:
        """Keep shared score actions aligned with Threes' low-score totals."""
        for player in self._active_threes_players():
            team = self.team_manager.get_team(player.name)
            if team:
                team.total_score = player.total_score

    def _ensure_score_teams(self) -> None:
        """Create individual score rows for starts and older restored games."""
        active_players = self._active_threes_players()
        active_names = [player.name for player in active_players]
        if (
            self.team_manager.team_mode != "individual"
            or not self.team_manager.validate_assignments(active_names)
        ):
            self.team_manager.team_mode = "individual"
            self.team_manager.setup_teams(active_names)
        else:
            self.team_manager.rebuild_player_index()
        self._sync_team_scores()

    def supports_score_actions(self) -> bool:
        if self.status == "playing" and not self.team_manager.teams:
            self._ensure_score_teams()
        return super().supports_score_actions()

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not MIN_ROUNDS <= self.options.total_rounds <= MAX_ROUNDS:
            errors.append(
                (
                    "threes-error-rounds-out-of-range",
                    {
                        "rounds": self.options.total_rounds,
                        "min": MIN_ROUNDS,
                        "max": MAX_ROUNDS,
                    },
                )
            )
        return errors

    def rebuild_runtime_state(self) -> None:
        super().rebuild_runtime_state()
        if self.status == "playing":
            self._ensure_score_teams()

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label for turn actions
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "threes-error-roll-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if not isinstance(player, ThreesPlayer):
            return "action-not-available"
        current = self.current_player
        if current is None:
            return "threes-error-roll-no-turn"
        if self.current_player != player:
            return (
                "threes-error-roll-not-your-turn",
                {"player": current.name},
            )
        if not player.dice.has_rolled:
            return None
        if player.dice.unlocked_count <= 1:
            return "threes-error-roll-last-die"
        if player.dice.kept_unlocked_count == 0:
            return "threes-error-roll-must-keep"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Roll stays visible as a touch anchor during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator or not isinstance(player, ThreesPlayer):
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE

        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_bank_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "threes-error-bank-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if not isinstance(player, ThreesPlayer):
            return "action-not-available"
        current = self.current_player
        if current is None:
            return "threes-error-bank-no-turn"
        if self.current_player != player:
            return (
                "threes-error-bank-not-your-turn",
                {"player": current.name},
            )
        if not player.dice.has_rolled:
            return "threes-error-bank-roll-first"
        if not player.dice.all_decided:
            return "threes-error-bank-keep-all"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank stays visible for active touch players as a stable control."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator or not isinstance(player, ThreesPlayer):
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE

        if self.current_player != player:
            return Visibility.HIDDEN
        if not player.dice.has_rolled:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_hand_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        """Check if check_hand action is enabled."""
        if self.status != "playing":
            return "threes-error-check-not-playing"
        current = self.current_player
        if not isinstance(current, ThreesPlayer):
            return "threes-error-check-no-turn"
        if not current.dice.has_rolled:
            if current is player:
                return "threes-error-check-your-dice-not-rolled"
            return (
                "threes-error-check-player-dice-not-rolled",
                {"player": current.name},
            )
        return None

    def _is_check_hand_hidden(self, player: Player) -> Visibility:
        """Check dice is touch-visible and keybind-only elsewhere."""
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # Override dice toggle methods from DiceGameMixin for Threes-specific logic
    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled in Threes."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if not isinstance(player, ThreesPlayer):
            return "action-not-available"
        if die_index < 0 or die_index >= player.dice.num_dice:
            return "action-not-available"
        if not player.dice.has_rolled:
            return "dice-not-rolled"
        if player.dice.is_locked(die_index):
            return "dice-locked"
        if player.dice.unlocked_count <= 1:
            return "threes-error-toggle-last-die"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Check if die toggle action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if not isinstance(player, ThreesPlayer):
            return Visibility.HIDDEN
        if die_index < 0 or die_index >= player.dice.num_dice:
            return Visibility.HIDDEN
        if not player.dice.has_rolled:
            return Visibility.HIDDEN
        if player.dice.is_locked(die_index):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_dice_toggle_label(self, player: Player, die_index: int) -> str:
        """Return localized labels for visible dice controls."""
        locale = self._player_locale(player)
        if not isinstance(player, ThreesPlayer) or not player.dice.has_rolled:
            return Localization.get(locale, "threes-die-index", index=die_index + 1)

        value = player.dice.get_value(die_index)
        if value is None:
            return Localization.get(locale, "threes-die-index", index=die_index + 1)
        if player.dice.is_locked(die_index):
            return Localization.get(locale, "threes-die-locked-label", value=value)
        if player.dice.is_kept(die_index):
            return Localization.get(locale, "threes-die-kept-label", value=value)
        return Localization.get(locale, "threes-die-value", value=value)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: ThreesPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Dice keep/unkeep actions (1-5 keys) - from mixin
        self.add_dice_toggle_actions(action_set)

        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "threes-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                show_in_actions_menu=False,
            )
        )

        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "threes-bank"),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_hand", "check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_hand",
                label=Localization.get(locale, "threes-check-hand"),
                handler="_action_check_hand",
                is_enabled="_is_check_hand_enabled",
                is_hidden="_is_check_hand_hidden",
                include_spectators=True,
            )
        )

        # WEB-SPECIFIC: Reorder for Web Clients
        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)

        return action_set

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, "host_username") and self.host_username:
            host = self.get_player_by_name(self.host_username)
            if host:
                user = self.get_user(host)
        locale = user.locale if user else "en"

        # Turn action keybinds - r/b like Pig
        self.define_keybind(
            "r",
            Localization.get(locale, "threes-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "b",
            Localization.get(locale, "threes-bank"),
            ["bank"],
            state=KeybindState.ACTIVE,
        )

        # Dice toggle keybinds (1-5) - from DiceGameMixin
        self.setup_dice_keybinds()

        # Check hand
        self.define_keybind(
            "h",
            Localization.get(locale, "threes-check-hand"),
            ["check_hand"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle rolling dice."""
        if not isinstance(player, ThreesPlayer):
            return

        disabled_reason = self._is_roll_enabled(player)
        if disabled_reason:
            self._speak_action_disabled_reason(player, disabled_reason)
            return

        # Roll dice (locks kept dice and rerolls unlocked)
        self.play_sound(random_dice_throw_sound())
        player.dice.roll()
        self._apply_dice_values_defaults(player)

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            dice_str = self._format_dice_values(player.dice.values, user.locale)
            if listener.id == player.id:
                key = (
                    "threes-you-rolled-brief"
                    if self._wants_brief(user)
                    else "threes-you-rolled"
                )
                user.speak_l(key, buffer="game", dice=dice_str)
            else:
                key = (
                    "threes-player-rolled-brief"
                    if self._wants_brief(user)
                    else "threes-player-rolled"
                )
                user.speak_l(
                    key, buffer="game", player=player.name, dice=dice_str
                )

        # Check if auto-score needed (all locked or only 1 unlocked)
        if player.dice.unlocked_count <= 1:
            self._score_turn(player)
            return

        # Give bot time to think about next action
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 30))

        self._focus_first_enabled_turn_action(player)
        self.refresh_menus(player)

    def _toggle_die(self, player: Player, die_index: int) -> None:
        """Toggle a die and broadcast the keep state with actor perspective."""
        if not isinstance(player, ThreesPlayer):
            return

        user = self.get_user(player)
        if die_index < 0 or die_index >= player.dice.num_dice:
            if user:
                user.speak_l("threes-invalid-die-index", buffer="game")
            return

        disabled_reason = self._is_dice_toggle_enabled(player, die_index)
        if disabled_reason:
            self._speak_action_disabled_reason(player, disabled_reason)
            return

        result = player.dice.toggle_keep(die_index)
        if result is None:
            if user:
                user.speak_l("dice-locked", buffer="game")
            return

        die_value = player.dice.get_value(die_index)
        kwargs = {"die": die_value, "index": die_index + 1}
        if result:
            self._broadcast_actor_l(
                player,
                "threes-you-keep",
                "threes-player-keeps",
                brief_personal_key="threes-you-keep-brief",
                brief_others_key="threes-player-keeps-brief",
                **kwargs,
            )
        else:
            self._broadcast_actor_l(
                player,
                "threes-you-unkeep",
                "threes-player-unkeeps",
                brief_personal_key="threes-you-unkeep-brief",
                brief_others_key="threes-player-unkeeps-brief",
                **kwargs,
            )

        self.refresh_menus(player)

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Bank score and end turn."""
        if not isinstance(player, ThreesPlayer):
            return

        disabled_reason = self._is_bank_enabled(player)
        if disabled_reason:
            self._speak_action_disabled_reason(player, disabled_reason)
            return

        self._score_turn(player)

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        """Check current dice."""
        user = self.get_user(player)
        if not user:
            return

        disabled_reason = self._is_check_hand_enabled(player)
        if disabled_reason:
            self._speak_action_disabled_reason(player, disabled_reason)
            return

        current = self.current_player
        if not isinstance(current, ThreesPlayer):
            user.speak_l("threes-error-check-no-turn", buffer="game")
            return

        dice_str = self._format_dice_l(current.dice, user.locale)
        score = self._turn_score_for_values(current.dice.values)
        remaining = current.dice.unlocked_count
        if current.id == player.id:
            user.speak_l(
                "threes-your-dice",
                buffer="game",
                dice=dice_str,
                score=score,
                remaining=remaining,
            )
        else:
            user.speak_l(
                "threes-player-dice",
                buffer="game",
                player=current.name,
                dice=dice_str,
                score=score,
                remaining=remaining,
            )

    def _score_turn(self, player: ThreesPlayer) -> None:
        """Calculate and apply turn score."""
        # Threes = 0 points, so sum all values excluding 3s
        score = player.dice.sum_values(exclude_value=3)
        six_count = player.dice.count_value(6)
        new_total = player.total_score + score

        # Check for shooting the moon (5 sixes)
        if six_count == 5:
            score = -30
            new_total = player.total_score + score
            self.play_sound("game_pig/win.ogg")
            self._broadcast_actor_l(
                player,
                "threes-you-shot-moon",
                "threes-shot-moon",
                brief_personal_key="threes-you-shot-moon-brief",
                brief_others_key="threes-shot-moon-brief",
                score=score,
                total=new_total,
            )
        else:
            self.play_sound("game_pig/bank.ogg")
            self._broadcast_actor_l(
                player,
                "threes-you-scored",
                "threes-scored",
                brief_personal_key="threes-you-scored-brief",
                brief_others_key="threes-scored-brief",
                score=score,
                total=new_total,
            )

        player.turn_score = score
        player.total_score = new_total
        self._sync_team_scores()

        self._focus_touch_roll_anchor(player)
        self._end_turn()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Check if round is over
        if self.turn_index >= len(self.turn_players) - 1:
            self._end_round()
        else:
            self.advance_turn(announce=False)
            self._start_turn()

    def _end_round(self) -> None:
        """End the current round."""
        # Announce round scores
        scores = [
            (p.name, p.total_score) for p in self._active_threes_players()
        ]
        scores.sort(key=lambda x: x[1])  # Sort by score (lowest first)

        for player in self.players:
            user = self.get_user(player)
            if user:
                header_key = (
                    "threes-round-scores-header-brief"
                    if self._wants_brief(user)
                    else "threes-round-scores-header"
                )
                user.speak_l(header_key, buffer="game", round=self.current_round)
                for name, score in scores:
                    user.speak_l("threes-score-pair", buffer="game", player=name, score=score)

        # Check if game is over
        if self.current_round >= self.options.total_rounds:
            self._end_game()
        else:
            # Start next round
            self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.current_round += 1
        self._broadcast_global_l(
            "threes-round-start",
            "threes-round-start-brief",
            round=self.current_round,
            total=self.options.total_rounds,
        )

        # Reset turn order to start of player list
        self.set_turn_players(self._active_threes_players())

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, ThreesPlayer):
            return

        # Reset turn state
        player.dice.reset()
        player.turn_score = 0

        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("game_3cardpoker/turn.ogg")
        self._broadcast_actor_l(
            player,
            "threes-turn-you",
            "threes-turn-other",
            brief_personal_key="threes-turn-you-brief",
            brief_others_key="threes-turn-other-brief",
            round=self.current_round,
            total=self.options.total_rounds,
            score=player.total_score,
        )

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

        self.refresh_menus()

    def _end_game(self) -> None:
        """End the game and announce winner."""
        # Find winner(s) (lowest score)
        players_with_scores = [(p, p.total_score) for p in self._active_threes_players()]
        players_with_scores.sort(key=lambda x: x[1])

        lowest_score = players_with_scores[0][1]
        winners = [p for p, s in players_with_scores if s == lowest_score]

        if len(winners) == 1:
            self.play_sound("game_pig/win.ogg")
            self._broadcast_actor_l(
                winners[0],
                "threes-winner-you",
                "threes-winner-other",
                brief_personal_key="threes-winner-you-brief",
                brief_others_key="threes-winner-other-brief",
                score=lowest_score,
            )
        else:
            winner_names_list = [w.name for w in winners]
            winner_ids = {winner.id for winner in winners}

            for player in self.players:
                user = self.get_user(player)
                if user:
                    other_names = [
                        name for name in winner_names_list if name != player.name
                    ]
                    key = (
                        "threes-tie-you"
                        if player.id in winner_ids and other_names
                        else "threes-tie"
                    )
                    if self._wants_brief(user):
                        key = (
                            "threes-tie-you-brief"
                            if key == "threes-tie-you"
                            else "threes-tie-brief"
                        )
                    names = other_names if key.startswith("threes-tie-you") else winner_names_list
                    winner_names = Localization.format_list_and(user.locale, names)
                    user.speak_l(
                        key, buffer="game", players=winner_names, score=lowest_score
                    )

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Threes-specific data."""
        # Sorted by score ascending (lowest wins)
        sorted_players = sorted(
            self._active_threes_players(),
            key=lambda p: p.total_score,
        )

        # Build final scores
        final_scores = {}
        for p in sorted_players:
            final_scores[p.name] = p.total_score

        winner = sorted_players[0] if sorted_players else None
        winner_score = winner.total_score if winner else 0
        tied_winners = [
            p for p in sorted_players if winner and p.total_score == winner_score
        ]
        single_winner = winner if len(tied_winners) == 1 else None

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in sorted_players
            ],
            custom_data={
                "winner_name": single_winner.name if single_winner else None,
                "winner_score": winner_score,
                "winner_ids": [p.id for p in tied_winners],
                "is_tie": len(tied_winners) > 1,
                "final_scores": final_scores,
                "rounds_played": self.current_round,
                "total_rounds": self.options.total_rounds,
                "scoring_mode": "lowest_wins",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Threes game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(locale, "threes-line-format", rank=i, player=name, points=points_str)
            )

        return lines

    def _format_dice_l(self, dice: DiceSet, locale: str) -> str:
        """Format dice with localized status."""
        parts = []
        for i in range(dice.num_dice):
            val = str(dice.values[i])
            status = dice.get_status(i)
            if status == "locked":
                status_str = Localization.get(locale, "threes-dice-locked")
                parts.append(Localization.get(locale, "threes-dice-format-status", value=val, status=status_str))
            elif status == "kept":
                status_str = Localization.get(locale, "threes-dice-kept")
                parts.append(Localization.get(locale, "threes-dice-format-status", value=val, status=status_str))
            else:
                parts.append(val)
        return Localization.format_list(locale, parts)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.current_round = 0

        # Reset player scores
        for player in self._active_threes_players():
            player.total_score = 0
            player.turn_score = 0
            player.dice.reset()

        # Initialize turn order
        active_players = self._active_threes_players()
        self.set_turn_players(active_players)
        self._ensure_score_teams()

        # Play music
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()

        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Bot AI decision making."""
        if not isinstance(player, ThreesPlayer):
            return None

        # If no dice, roll
        if not player.dice.has_rolled:
            return "roll"

        # If only 1 unlocked die, we must bank (auto-handled)
        if player.dice.unlocked_count <= 1:
            return "bank"

        # Check if all dice are kept/locked - then bank
        if player.dice.all_decided:
            return "bank"

        # Decide what to keep using strategy
        self._bot_decide_keepers(player)

        # If we've kept something new, roll
        if player.dice.kept_unlocked_count > 0:
            return "roll"

        # Fallback: shouldn't reach here, but keep lowest if we do
        return None

    def _bot_decide_keepers(self, player: ThreesPlayer) -> None:
        """Bot AI to decide which dice to keep."""
        dice = player.dice

        # Clear current kept dice (except locked ones)
        dice.kept = list(dice.locked)

        # Group available dice by value
        available: dict[int, list[int]] = {}  # value -> list of indices
        for i in range(5):
            if not dice.is_locked(i):
                value = dice.get_value(i)
                if value is not None:
                    if value not in available:
                        available[value] = []
                    available[value].append(i)

        # Count locked sixes for moon shot check
        locked_sixes = sum(1 for i in dice.locked if dice.get_value(i) == 6)
        available_sixes = available.get(6, [])

        # Strategy 1: finish the moon shot when every die can become a six.
        if available_sixes and locked_sixes + len(available_sixes) == dice.num_dice:
            for i in available_sixes:
                dice.keep(i)
            return

        # Strategy 2: Keep threes (0 points!)
        if 3 in available:
            for i in available[3]:
                dice.keep(i)
            return

        # Strategy 3: Keep ones (low value)
        if 1 in available:
            for i in available[1]:
                dice.keep(i)
            return

        # Strategy 4: Keep twos
        if 2 in available:
            for i in available[2]:
                dice.keep(i)
            return

        # Strategy 5: keep a six only when the moon shot is realistic.
        if locked_sixes >= 4 and available_sixes:
            for i in available_sixes:
                dice.keep(i)
            return

        # Strategy 6: Keep lowest available
        for value in [4, 5, 6]:
            if value in available:
                dice.keep(available[value][0])
                return
