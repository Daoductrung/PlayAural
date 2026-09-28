"""
1-4-24 (Midnight) Game Implementation.

Dice game where players roll 6 dice trying to get a 1 and a 4.
The other 4 dice are summed for points (max 24). Highest score wins the round.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import DiceSet, random_dice_throw_sound
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


QUALIFIER_ONE = 1
QUALIFIER_FOUR = 4


@dataclass
class MidnightPlayer(Player):
    """Player state for 1-4-24 (Midnight) game."""

    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=6, sides=6))
    round_score: int = 0  # Score for current round (0 if disqualified)
    round_wins: int = 0  # Number of rounds won
    qualified: bool = False  # Whether player has 1 and 4


@dataclass
class MidnightOptions(GameOptions):
    """Options for 1-4-24 (Midnight) game."""

    rounds: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=20,
            value_key="rounds",
            label="midnight-set-rounds",
            prompt="midnight-enter-rounds",
            change_msg="midnight-option-changed-rounds",
        )
    )


@dataclass
@register_game
class MidnightGame(Game, DiceGameMixin):
    """
    1-4-24 (Midnight) dice game.

    Players roll 6 dice and must keep at least one die after each roll.
    Once kept, dice are locked and can't be changed.
    To score, you need a 1 and a 4. The other 4 dice sum for points (max 24).
    Highest score wins the round. First to win the most rounds wins the game.
    """

    relevant_preferences = ["brief_announcements", "dice_keeping_style"]
    score_unit_key = "midnight-score-unit-round-wins"

    # Game-specific state
    players: list[MidnightPlayer] = field(default_factory=list)
    options: MidnightOptions = field(default_factory=MidnightOptions)
    last_turn_player_id: str = ""
    last_turn_dice: list[int] = field(default_factory=list)
    last_turn_score: int = 0
    last_turn_qualified: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "1-4-24"

    @classmethod
    def get_type(cls) -> str:
        return "midnight"

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
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> MidnightPlayer:
        """Create a new player with Midnight-specific state."""
        return MidnightPlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            dice=DiceSet(num_dice=6, sides=6),
            round_score=0,
            round_wins=0,
            qualified=False,
        )

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: MidnightPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener is actor
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
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _format_dice_values(self, values: list[int], locale: str) -> str:
        return Localization.format_list(locale, [str(value) for value in values])

    def _format_missing_qualifiers(self, values: list[int], locale: str) -> str:
        missing = []
        if QUALIFIER_ONE not in values:
            missing.append(str(QUALIFIER_ONE))
        if QUALIFIER_FOUR not in values:
            missing.append(str(QUALIFIER_FOUR))
        return Localization.format_list_and(locale, missing)

    def _evaluate_dice(self, values: list[int]) -> tuple[bool, int, list[int]]:
        if QUALIFIER_ONE not in values or QUALIFIER_FOUR not in values:
            return False, 0, []
        scoring_values = list(values)
        scoring_values.remove(QUALIFIER_ONE)
        scoring_values.remove(QUALIFIER_FOUR)
        return True, sum(scoring_values), scoring_values

    def _format_player_dice_status(self, player: MidnightPlayer, locale: str) -> str:
        if not player.dice.has_rolled:
            return Localization.get(locale, "midnight-status-dice-not-rolled")

        parts = []
        for index, value in enumerate(player.dice.values):
            if player.dice.is_locked(index):
                parts.append(
                    Localization.get(locale, "midnight-die-locked", value=value)
                )
            elif player.dice.is_kept(index):
                parts.append(
                    Localization.get(locale, "midnight-die-kept", value=value)
                )
            else:
                parts.append(str(value))
        return Localization.format_list(locale, parts)

    def _current_turn_snapshot_kwargs(self, player: MidnightPlayer, locale: str) -> dict:
        dice_text = self._format_player_dice_status(player, locale)
        locked_count = len(player.dice.locked)
        kept_count = player.dice.kept_unlocked_count
        remaining = player.dice.unlocked_count
        qualified, score, scoring_values = self._evaluate_dice(player.dice.values)
        scoring_dice = (
            self._format_dice_values(scoring_values, locale)
            if scoring_values
            else ""
        )
        missing = self._format_missing_qualifiers(player.dice.values, locale)
        return self._resolve_broadcast_kwargs(
            locale,
            {
                "player": player,
                "dice": dice_text,
                "locked": locked_count,
                "kept": kept_count,
                "remaining": remaining,
                "score": score,
                "scoring_dice": scoring_dice,
                "missing": missing,
                "qualified": "yes" if qualified else "no",
            },
        )

    def _sync_team_scores(self) -> None:
        for player in self.get_active_players():
            team = self.team_manager.get_team(player.name)
            if team:
                team.total_score = getattr(player, "round_wins", 0)

    # ==========================================================================
    # Dice toggle methods (required by DiceGameMixin)
    # ==========================================================================

    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        midnight_player: MidnightPlayer = player  # type: ignore
        if not midnight_player.dice.has_rolled:
            return "midnight-need-to-roll"
        if midnight_player.dice.is_locked(die_index):
            return "dice-locked"
        # Allow toggling (keeping/unkeeping) until dice are locked
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Dice toggles are visible when dice are rolled and die is not locked/kept."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        midnight_player: MidnightPlayer = player  # type: ignore
        if not midnight_player.dice.has_rolled:
            return Visibility.HIDDEN
        # Hide only locked dice (kept dice are still toggleable)
        if midnight_player.dice.is_locked(die_index):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_dice_toggle_label(self, player: Player, die_index: int) -> str:
        """Get label for dice toggle action."""
        midnight_player: MidnightPlayer = player  # type: ignore

        # Safety check - if dice haven't been rolled or index out of range
        if not midnight_player.dice.has_rolled or die_index >= len(midnight_player.dice.values):
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return Localization.get(locale, "midnight-die-index", index=die_index + 1)

        die_val = midnight_player.dice.values[die_index]
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if midnight_player.dice.is_locked(die_index):
            return Localization.get(locale, "midnight-die-locked", value=die_val)
        if midnight_player.dice.is_kept(die_index):
            return Localization.get(locale, "midnight-die-kept", value=die_val)
        return Localization.get(locale, "midnight-die-value", value=die_val)

    def _toggle_die(self, player: Player, die_index: int) -> None:
        """Toggle a die and broadcast the public keep state."""
        if not isinstance(player, MidnightPlayer):
            return

        user = self.get_user(player)
        if die_index < 0 or die_index >= player.dice.num_dice:
            if user:
                user.speak_l("midnight-invalid-die-index", buffer="game")
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
                "midnight-you-keep",
                "midnight-player-keeps",
                brief_personal_key="midnight-you-keep-brief",
                brief_others_key="midnight-player-keeps-brief",
                **kwargs,
            )
        else:
            self._broadcast_actor_l(
                player,
                "midnight-you-unkeep",
                "midnight-player-unkeeps",
                brief_personal_key="midnight-you-unkeep-brief",
                brief_others_key="midnight-player-unkeeps-brief",
                **kwargs,
            )

        self.refresh_menus(player)

    # ==========================================================================
    # Roll action
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        midnight_player: MidnightPlayer = player  # type: ignore
        # Must keep at least one die per roll (except first roll)
        if midnight_player.dice.has_rolled and midnight_player.dice.kept_unlocked_count == 0:
            return "midnight-must-keep-one"
        if midnight_player.dice.unlocked_count == 0:
            return "midnight-no-dice-to-keep"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Roll is visible during play for current player."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        midnight_player: MidnightPlayer = player  # type: ignore
        if midnight_player.dice.unlocked_count == 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _first_visible_dice_toggle_action_id(self, player: Player) -> str | None:
        return next(
            (
                resolved.action.id
                for resolved in self.get_all_visible_actions(player)
                if resolved.action.id.startswith("toggle_die_")
            ),
            None,
        )

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        midnight_player: MidnightPlayer = player  # type: ignore

        self.play_sound(random_dice_throw_sound())

        # Roll dice (locks kept dice)
        midnight_player.dice.roll(lock_kept=True, clear_kept=True)
        self._apply_dice_values_defaults(midnight_player)

        # Announce results in each listener's locale so list conjunctions
        # render correctly for English, Vietnamese, and future locales.
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            dice_text = self._format_dice_values(
                midnight_player.dice.values, user.locale
            )
            is_actor = listener is midnight_player
            if is_actor:
                key = (
                    "midnight-you-rolled-brief"
                    if self._wants_brief(user)
                    else "midnight-you-rolled"
                )
                user.speak_l(key, buffer="game", dice=dice_text)
            else:
                key = (
                    "midnight-player-rolled-brief"
                    if self._wants_brief(user)
                    else "midnight-player-rolled"
                )
                user.speak_l(
                    key, buffer="game", player=midnight_player.name, dice=dice_text
                )

        # Check if auto-score needed (all locked or only 1 unlocked)
        if midnight_player.dice.unlocked_count <= 1:
            self._score_turn(midnight_player)
            return

        # Give bot time to think about next action
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        focus = self._first_visible_dice_toggle_action_id(midnight_player)
        if focus:
            self.request_menu_focus(midnight_player, focus)
        self.refresh_menus(midnight_player)

    # ==========================================================================
    # Bank action
    # ==========================================================================

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        midnight_player: MidnightPlayer = player  # type: ignore
        if not midnight_player.dice.has_rolled:
            return "midnight-must-roll-first"
        if not midnight_player.dice.all_decided:
            return "midnight-keep-all-first"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank is visible during play for current player after first roll."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        midnight_player: MidnightPlayer = player  # type: ignore
        if not midnight_player.dice.has_rolled:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Bank score and end turn."""
        midnight_player: MidnightPlayer = player  # type: ignore
        self._score_turn(midnight_player)

    def _score_turn(self, player: MidnightPlayer) -> None:
        """Calculate and apply turn score."""
        qualified, score, scoring_values = self._evaluate_dice(player.dice.values)

        self.last_turn_player_id = player.id
        self.last_turn_dice = list(player.dice.values)
        self.last_turn_score = score
        self.last_turn_qualified = qualified

        if qualified:
            player.round_score = score
            player.qualified = True

            self.play_sound("game_pig/bank.ogg")
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                scoring_dice = self._format_dice_values(scoring_values, user.locale)
                is_actor = listener is player
                if is_actor:
                    key = (
                        "midnight-you-scored-brief"
                        if self._wants_brief(user)
                        else "midnight-you-scored"
                    )
                    user.speak_l(
                        key,
                        buffer="game",
                        score=player.round_score,
                        scoring_dice=scoring_dice,
                    )
                else:
                    key = (
                        "midnight-scored-brief"
                        if self._wants_brief(user)
                        else "midnight-scored"
                    )
                    user.speak_l(
                        key,
                        buffer="game",
                        player=player.name,
                        score=player.round_score,
                        scoring_dice=scoring_dice,
                    )
        else:
            # Disqualified
            player.round_score = 0
            player.qualified = False

            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                missing = self._format_missing_qualifiers(
                    player.dice.values, user.locale
                )
                is_actor = listener is player
                if is_actor:
                    key = (
                        "midnight-you-disqualified-brief"
                        if self._wants_brief(user)
                        else "midnight-you-disqualified"
                    )
                    user.speak_l(key, buffer="game", missing=missing)
                else:
                    key = (
                        "midnight-player-disqualified-brief"
                        if self._wants_brief(user)
                        else "midnight-player-disqualified"
                    )
                    user.speak_l(
                        key, buffer="game", player=player.name, missing=missing
                    )

        # Jolt all bots to pause for the turn change
        BotHelper.jolt_bots(self, ticks=random.randint(20, 30))

        user = self.get_user(player)
        if self.is_touch_client(user):
            self.request_menu_focus(player, "roll")

        self._on_turn_end()

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: MidnightPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Add dice toggle actions from mixin (handles 1-6 keys and menu items)
        self.add_dice_toggle_actions(action_set, num_dice=6)

        # Roll action
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "midnight-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                show_in_actions_menu=False,
            )
        )

        # Bank action (end turn voluntarily)
        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "midnight-bank"),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    web_target_order = [
        "check_dice",
        "check_round_status",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)

        action_set.add(
            Action(
                id="check_dice",
                label=Localization.get(locale, "midnight-check-dice"),
                handler="_action_check_dice",
                is_enabled="_is_check_dice_enabled",
                is_hidden="_is_check_dice_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_round_status",
                label=Localization.get(locale, "midnight-check-round-status"),
                handler="_action_check_round_status",
                is_enabled="_is_check_round_status_enabled",
                is_hidden="_is_check_round_status_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)

        return action_set

    # WEB-SPECIFIC: Override visibility for standard actions
    # accessible in the Standard Action Set (displayed at bottom of menu)

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
            # Only visible when playing
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_dice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_dice_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_check_round_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_round_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        # Call parent for lobby/standard keybinds
        super().setup_keybinds()

        # Dice keybinds from mixin (1-6 keys)
        self.setup_dice_keybinds(num_dice=6)

        # Roll action keybind
        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player_by_name(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        self.define_keybind(
            "r",
            Localization.get(locale, "midnight-roll"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )

        # Bank action keybind
        self.define_keybind(
            "b",
            Localization.get(locale, "midnight-bank"),
            ["bank"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "h",
            Localization.get(locale, "midnight-check-dice"),
            ["check_dice"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            Localization.get(locale, "midnight-check-round-status"),
            ["check_round_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_check_dice(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        current = self.current_player
        if not isinstance(current, MidnightPlayer):
            user.speak_l("game-no-turn", buffer="game")
            return

        if not current.dice.has_rolled:
            if current is player:
                user.speak_l("midnight-your-dice-not-rolled", buffer="game")
            else:
                user.speak_l(
                    "midnight-player-dice-not-rolled",
                    buffer="game",
                    player=current.name,
                )
            return

        kwargs = self._current_turn_snapshot_kwargs(current, user.locale)
        if current is player:
            user.speak_l("midnight-your-dice-status", buffer="game", **kwargs)
        else:
            user.speak_l("midnight-player-dice-status", buffer="game", **kwargs)

    def _status_items(self, player: Player, user) -> list[MenuItem]:
        locale = user.locale
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "midnight-status-round",
                    round=self.round,
                    total=self.options.rounds,
                ),
                id="round",
            )
        ]

        current = self.current_player
        if isinstance(current, MidnightPlayer):
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "midnight-status-current-player",
                        player=current.name,
                    ),
                    id="current-player",
                )
            )
            if current.dice.has_rolled:
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "midnight-status-current-dice",
                            **self._current_turn_snapshot_kwargs(current, locale),
                        ),
                        id=f"current-dice:{current.id}",
                    )
                )
            else:
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "midnight-status-current-not-rolled",
                            player=current.name,
                        ),
                        id=f"current-dice:{current.id}",
                    )
                )

        if self.last_turn_player_id:
            last_player = self.get_player_by_id(self.last_turn_player_id)
            if last_player:
                dice = self._format_dice_values(self.last_turn_dice, locale)
                key = (
                    "midnight-status-last-qualified"
                    if self.last_turn_qualified
                    else "midnight-status-last-disqualified"
                )
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            key,
                            player=last_player.name,
                            dice=dice,
                            score=self.last_turn_score,
                        ),
                        id=f"last-turn:{self.last_turn_player_id}",
                    )
                )

        for standing_index, midnight_player in enumerate(
            self._sorted_players_by_standing(), 1
        ):
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "midnight-status-standing-line",
                        rank=standing_index,
                        player=midnight_player.name,
                        wins=midnight_player.round_wins,
                        current=midnight_player.round_score,
                        qualified="yes" if midnight_player.qualified else "no",
                    ),
                    id=f"standing:{midnight_player.id}",
                )
            )
        return items

    def _action_check_round_status(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "midnight_round_status",
            lambda _player, live_user: self._status_items(_player, live_user),
        )

    def _sorted_players_by_standing(self) -> list[MidnightPlayer]:
        active_players = [
            player for player in self.get_active_players() if isinstance(player, MidnightPlayer)
        ]
        return sorted(
            active_players,
            key=lambda p: (p.round_wins, p.round_score, p.qualified),
            reverse=True,
        )

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 1 <= self.options.rounds <= 20:
            errors.append(
                (
                    "midnight-error-rounds-out-of-range",
                    {"rounds": self.options.rounds, "min": 1, "max": 20},
                )
            )
        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)
        self.team_manager.team_mode = "individual"
        self.team_manager.setup_teams([player.name for player in active_players])
        self.team_manager.reset_all_scores()
        self.last_turn_player_id = ""
        self.last_turn_dice = []
        self.last_turn_score = 0
        self.last_turn_qualified = False

        # Reset player state
        for player in active_players:
            player.dice.reset()
            player.round_score = 0
            player.round_wins = 0
            player.qualified = False
        self._sync_team_scores()

        # Play intro music
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Reset turn order for new round
        self.set_turn_players(self.get_active_players())

        self.play_sound("game_pig/roundstart.ogg")
        self._broadcast_global_l(
            "midnight-round-start",
            "midnight-round-start-brief",
            round=self.round,
            total=self.options.rounds,
        )

        # Reset all players for new round
        for player in self.get_active_players():
            player.dice.reset()
            player.round_score = 0
            player.qualified = False

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        midnight_player: MidnightPlayer = player  # type: ignore
        midnight_player.dice.reset()
        midnight_player.round_score = 0
        midnight_player.qualified = False

        # Announce turn
        self.announce_turn()

        # Set up bot if this is a bot's turn
        if player.is_bot:
            BotHelper.set_target(player, 24)

        # Rebuild menus to reflect new turn
        self.refresh_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()

        if not self.game_active:
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: MidnightPlayer) -> str | None:
        """Bot AI decision making. Called by BotHelper."""
        if not player.dice.has_rolled:
            return "roll"

        if player.dice.all_decided:
            return "bank"

        keep_index = self._bot_pick_die_to_keep(player)
        if keep_index is not None:
            return f"toggle_die_{keep_index}"

        if player.dice.kept_unlocked_count > 0:
            return "roll"

        return "bank"

    def _bot_pick_die_to_keep(self, player: MidnightPlayer) -> int | None:
        available = [
            index
            for index in range(player.dice.num_dice)
            if not player.dice.is_locked(index) and not player.dice.is_kept(index)
        ]
        if not available:
            return None

        kept_values = [
            player.dice.values[index]
            for index in range(player.dice.num_dice)
            if player.dice.is_locked(index) or player.dice.is_kept(index)
        ]
        has_one = QUALIFIER_ONE in kept_values
        has_four = QUALIFIER_FOUR in kept_values

        if not has_one:
            one_index = self._find_available_die(player, available, QUALIFIER_ONE)
            if one_index is not None:
                return one_index

        if not has_four:
            four_index = self._find_available_die(player, available, QUALIFIER_FOUR)
            if four_index is not None:
                return four_index

        if has_one and has_four:
            for target in (6, 5):
                index = self._find_available_die(player, available, target)
                if index is not None:
                    return index

        if player.dice.kept_unlocked_count == 0:
            return max(available, key=lambda index: player.dice.values[index])

        return None

    def _find_available_die(
        self, player: MidnightPlayer, available: list[int], value: int
    ) -> int | None:
        for index in available:
            if player.dice.values[index] == value:
                return index
        return None

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
        active_players = self.get_active_players()

        # Find highest score among qualified players
        qualified_players = [p for p in active_players if p.qualified]

        if not qualified_players:
            # No one qualified
            self._broadcast_global_l(
                "midnight-all-disqualified",
                "midnight-all-disqualified-brief",
            )
        else:
            high_score = max(p.round_score for p in qualified_players)
            winners = [p for p in qualified_players if p.round_score == high_score]

            if len(winners) == 1:
                # Single round winner
                winner = winners[0]
                winner.round_wins += 1
                self._sync_team_scores()
                self.play_sound("game_pig/bank.ogg")
                self._broadcast_actor_l(
                    winner,
                    "midnight-you-win-round",
                    "midnight-round-winner",
                    brief_personal_key="midnight-you-win-round-brief",
                    brief_others_key="midnight-round-winner-brief",
                    round=self.round,
                    score=winner.round_score,
                )
            else:
                # Tie
                names = [w.name for w in winners]
                for player in self.players:
                    user = self.get_user(player)
                    if user:
                        names_str = Localization.format_list_and(user.locale, names)
                        user.speak_l(
                            "midnight-round-tie",
                            buffer="game",
                            players=names_str,
                            score=high_score,
                        )

        # Check if game is over
        if self.round >= self.options.rounds:
            self._end_game()
        else:
            # Next round
            self._start_round()

    def _end_game(self) -> None:
        """End the game and determine overall winner."""
        active_players = self.get_active_players()

        # Find highest round wins
        max_wins = max(p.round_wins for p in active_players)
        winners = [p for p in active_players if p.round_wins == max_wins]

        if len(winners) == 1:
            # Single game winner
            winner = winners[0]
            self.play_sound("game_pig/win.ogg")
            self._broadcast_actor_l(
                winner,
                "midnight-you-win-game",
                "midnight-game-winner",
                brief_personal_key="midnight-you-win-game-brief",
                brief_others_key="midnight-game-winner-brief",
                wins=max_wins,
            )
        else:
            # Game tie
            names = [w.name for w in winners]
            for player in self.players:
                user = self.get_user(player)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l(
                        "midnight-game-tie",
                        buffer="game",
                        players=names_str,
                        wins=max_wins,
                    )

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Midnight-specific data."""
        active_players = self.get_active_players()
        sorted_players = self._sorted_players_by_standing()
        max_wins = sorted_players[0].round_wins if sorted_players else 0
        winner_candidates = [
            player for player in sorted_players if player.round_wins == max_wins
        ]
        winner = winner_candidates[0] if len(winner_candidates) == 1 else None

        # Build final standings
        final_standings = {}
        for player in sorted_players:
            final_standings[player.name] = player.round_wins

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_rounds": max_wins,
                "final_standings": final_standings,
                "rounds_played": self.round,
                "total_rounds": self.options.rounds,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Midnight game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_standings = result.custom_data.get("final_standings", {})
        for i, (name, wins) in enumerate(final_standings.items(), 1):
            lines.append(
                Localization.get(
                    locale, "midnight-end-score", rank=i, player=name, wins=wins
                )
            )

        return lines
