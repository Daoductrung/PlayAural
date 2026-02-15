"""
1-4-24 (Midnight) Game Implementation for PlayAural v0.1.0.

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
from ...game_utils.dice import DiceSet
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


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

    # Game-specific state
    players: list[MidnightPlayer] = field(default_factory=list)
    options: MidnightOptions = field(default_factory=MidnightOptions)

    @classmethod
    def get_name(cls) -> str:
        return "1-4-24"

    @classmethod
    def get_type(cls) -> str:
        return "midnight"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

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

    # Dice toggle handlers provided by DiceGameMixin (no override needed)

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
        if self.current_player != player:
            return Visibility.HIDDEN
        midnight_player: MidnightPlayer = player  # type: ignore
        if midnight_player.dice.unlocked_count == 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        midnight_player: MidnightPlayer = player  # type: ignore

        self.play_sound("game_pig/roll.ogg")

        # Roll dice (locks kept dice)
        midnight_player.dice.roll(lock_kept=True, clear_kept=True)
        self._apply_dice_values_defaults(midnight_player)

        # Format roll results
        result_text = ", ".join(str(v) for v in midnight_player.dice.values)

        # Announce results
        self.broadcast_personal_l(
            player, "midnight-you-rolled", "midnight-player-rolled", dice=result_text
        )

        # Check if auto-score needed (all locked or only 1 unlocked)
        if midnight_player.dice.unlocked_count <= 1:
            self._score_turn(midnight_player)
            return

        # Give bot time to think about next action
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        self.rebuild_all_menus()

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
        # Check if player has both 1 and 4
        has_one = 1 in player.dice.values
        has_four = 4 in player.dice.values

        if has_one and has_four:
            # Qualified! Calculate score from other 4 dice
            # Remove first occurrence of 1 and first occurrence of 4
            values_copy = player.dice.values.copy()
            values_copy.remove(1)
            values_copy.remove(4)

            player.round_score = sum(values_copy)
            player.qualified = True

            self.play_sound("game_pig/bank.ogg")
            self.broadcast_personal_l(
                player,
                "midnight-you-scored",
                "midnight-scored",
                score=player.round_score,
            )
        else:
            # Disqualified
            player.round_score = 0
            player.qualified = False

            self.broadcast_personal_l(
                player, "midnight-you-disqualified", "midnight-player-disqualified"
            )

        # Jolt all bots to pause for the turn change
        BotHelper.jolt_bots(self, ticks=random.randint(20, 30))

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
            )
        )

        return action_set

    # WEB-SPECIFIC: Override visibility for standard actions
    # accessible in the Standard Action Set (displayed at bottom of menu)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            # Only visible when playing
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_always_visible(self, player: "Player") -> Visibility:
        """Helper for web-specific actions that should always be visible."""
        return Visibility.VISIBLE

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

        self.define_keybind("r", Localization.get(locale, "midnight-roll"), ["roll"], state=KeybindState.ACTIVE)

        # Bank action keybind
        self.define_keybind("b", Localization.get(locale, "midnight-bank"), ["bank"], state=KeybindState.ACTIVE)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Reset player state
        for player in active_players:
            player.dice.reset()
            player.round_score = 0
            player.round_wins = 0
            player.qualified = False

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
        self.broadcast_l("game-round-start", round=self.round)

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
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()

        if not self.game_active:
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: MidnightPlayer) -> str | None:
        """Bot AI decision making. Called by BotHelper."""
        # Strategy: Keep 1 and 4 first, then keep highest dice
        if not player.dice.has_rolled:
            return "roll"

        # If we have kept dice but haven't rolled yet to lock them, roll
        if player.dice.kept_unlocked_count > 0:
            return "roll"

        # Look for 1 if we don't have one locked yet
        if 1 not in [player.dice.values[i] for i in player.dice.locked]:
            for i in range(6):
                if not player.dice.is_locked(i) and player.dice.values[i] == 1:
                    return f"toggle_die_{i}"

        # Look for 4 if we don't have one locked yet
        if 4 not in [player.dice.values[i] for i in player.dice.locked]:
            for i in range(6):
                if not player.dice.is_locked(i) and player.dice.values[i] == 4:
                    return f"toggle_die_{i}"

        # Keep highest available die
        best_index = -1
        best_value = 0
        for i in range(6):
            if not player.dice.is_locked(i) and not player.dice.is_kept(i):
                if player.dice.values[i] > best_value:
                    best_value = player.dice.values[i]
                    best_index = i

        if best_index >= 0:
            return f"toggle_die_{best_index}"

        # No more dice to keep - decide whether to roll or stop
        # If we have both 1 and 4 locked, we can stop
        locked_values = [player.dice.values[i] for i in player.dice.locked]
        has_one = 1 in locked_values
        has_four = 4 in locked_values

        if has_one and has_four:
            # We have what we need, bank to lock in score
            return "bank"

        # Still missing 1 or 4, keep trying (but can't roll if kept_unlocked_count is 0)
        # In this case, bank anyway to avoid getting stuck
        if player.dice.kept_unlocked_count == 0:
            return "bank"

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
        active_players = self.get_active_players()

        # Find highest score among qualified players
        qualified_players = [p for p in active_players if p.qualified]

        if not qualified_players:
            # No one qualified
            self.broadcast_l("midnight-all-disqualified")
        else:
            high_score = max(p.round_score for p in qualified_players)
            winners = [p for p in qualified_players if p.round_score == high_score]

            if len(winners) == 1:
                # Single round winner
                winner = winners[0]
                winner.round_wins += 1
                self.play_sound("game_pig/bank.ogg")
                self.broadcast_l(
                    "midnight-round-winner", player=winner.name
                )
            else:
                # Tie
                names = [w.name for w in winners]
                # Each tied player gets a win
                for w in winners:
                    w.round_wins += 1
                for player in self.players:
                    user = self.get_user(player)
                    if user:
                        names_str = Localization.format_list_and(user.locale, names)
                        user.speak_l(
                            "midnight-round-tie", players=names_str
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
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l(
                "midnight-game-winner", player=winners[0].name, wins=max_wins
            )
        else:
            # Game tie
            names = [w.name for w in winners]
            for player in self.players:
                user = self.get_user(player)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l("midnight-game-tie", buffer="game", players=names_str, wins=max_wins)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Midnight-specific data."""
        active_players = self.get_active_players()
        sorted_players = sorted(
            active_players, key=lambda p: p.round_wins, reverse=True
        )
        winner = sorted_players[0] if sorted_players else None

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
                    is_bot=p.is_bot,
                )
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_rounds": winner.round_wins if winner else 0,
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
