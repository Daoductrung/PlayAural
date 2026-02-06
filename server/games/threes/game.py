"""
Threes Game Implementation for PlayAural v0.1.0.

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
from ...game_utils.dice import DiceSet
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field, GameOptions
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


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
            min_val=1,
            max_val=20,
            value_key="rounds",
            label="threes-set-rounds",
            prompt="threes-enter-rounds",
            change_msg="threes-option-changed-rounds",
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
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ThreesPlayer:
        """Create a new player with Threes-specific state."""
        return ThreesPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label for turn actions
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            # First roll is always allowed
            return None
        if threes_player.dice.unlocked_count <= 1:
            # Only 1 die left, can't roll (must bank)
            return "threes-must-bank"
        if threes_player.dice.kept_unlocked_count == 0:
            # Must keep at least one die
            return "threes-must-keep"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Roll is visible during play for current player."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "threes-roll-first"
        if not threes_player.dice.all_decided:
            return "threes-keep-all-first"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank is hidden until dice are rolled."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_hand_enabled(self, player: Player) -> str | None:
        """Check if check_hand action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "threes-no-dice-yet"
        return None

    def _is_check_hand_hidden(self, player: Player) -> Visibility:
        """Check hand is always hidden (keybind only)."""
        return Visibility.HIDDEN

    # Override dice toggle methods from DiceGameMixin for Threes-specific logic
    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled in Threes."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "dice-not-rolled"
        if threes_player.dice.is_locked(die_index):
            return "dice-locked"
        if threes_player.dice.unlocked_count <= 1:
            # Only 1 unlocked die left - can't toggle
            return "threes-last-die"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Check if die toggle action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

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
            )
        )

        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "threes-bank"),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
            )
        )

        # Check hand action
        action_set.add(
            Action(
                id="check_hand",
                label=Localization.get(locale, "threes-check-hand"),
                handler="_action_check_hand",
                is_enabled="_is_check_hand_enabled",
                is_hidden="_is_check_hand_hidden",
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            # Reordering Logic
            final_order = []
            for aid in self.web_target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)
            
            for aid in action_set._order:
                if aid not in self.web_target_order:
                    final_order.append(aid)
            
            action_set._order = final_order

        return action_set

    # WEB-SPECIFIC: Visibility Overrides

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
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Turn action keybinds - r/b like Pig
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "b", "Bank and end turn", ["bank"], state=KeybindState.ACTIVE
        )

        # Dice toggle keybinds (1-5) - from DiceGameMixin
        self.setup_dice_keybinds()

        # Check hand
        self.define_keybind(
            "h", "Check hand", ["check_hand"], state=KeybindState.ACTIVE
        )

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle rolling dice."""
        if not isinstance(player, ThreesPlayer):
            return

        # If not first roll, must keep at least one unlocked die
        if player.dice.has_rolled:
            if player.dice.kept_unlocked_count == 0:
                user = self.get_user(player)
                if user:
                    user.speak_l("threes-must-keep", buffer="game")
                return

        # Roll dice (locks kept dice and rerolls unlocked)
        self.play_sound("game_pig/roll.ogg")
        player.dice.roll()
        self._apply_dice_values_defaults(player)

        # Announce roll
        # dice_str = player.dice.format_values_only()
        # Use localized list format for values
        for p in self.get_active_players():
            user = self.get_user(p)
            if not user:
                continue
            
            # Simple list of numbers
            parts = [str(v) for v in player.dice.values]
            dice_str = Localization.format_list(user.locale, parts)

            if p == player:
                user.speak_l("threes-you-rolled", buffer="game", dice=dice_str)
            else:
                user.speak_l("threes-player-rolled", buffer="game", player=player.name, dice=dice_str)

        # Check if auto-score needed (all locked or only 1 unlocked)
        if player.dice.unlocked_count <= 1:
            self._score_turn(player)
            return

        # Give bot time to think about next action
        if player.is_bot:
            import random

            BotHelper.jolt_bot(player, ticks=random.randint(15, 30))

        self.rebuild_all_menus()

    # Dice toggle handlers provided by DiceGameMixin

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Bank score and end turn."""
        if not isinstance(player, ThreesPlayer):
            return
        self._score_turn(player)

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        """Check current dice."""
        if not isinstance(player, ThreesPlayer):
            return

        user = self.get_user(player)
        if not user:
            return

        if not player.dice.has_rolled:
            user.speak_l("threes-no-dice-yet", buffer="game")
            return

        dice_str = self._format_dice_l(player.dice, user.locale)
        user.speak_l("threes-your-dice", buffer="game", dice=dice_str)

    def _score_turn(self, player: ThreesPlayer) -> None:
        """Calculate and apply turn score."""
        # Threes = 0 points, so sum all values excluding 3s
        score = player.dice.sum_values(exclude_value=3)
        six_count = player.dice.count_value(6)

        # Check for shooting the moon (5 sixes)
        if six_count == 5:
            score = -30
            self.play_sound("game_pig/win.ogg")
            self.broadcast_personal_l(player, "threes-you-shot-moon", "threes-shot-moon")
        else:
            self.play_sound("game_pig/bank.ogg")
            self.broadcast_personal_l(
                player, "threes-you-scored", "threes-scored", score=score
            )

        player.turn_score = score
        player.total_score += score

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
            (p.name, p.total_score) for p in self.players if isinstance(p, ThreesPlayer)
        ]
        scores.sort(key=lambda x: x[1])  # Sort by score (lowest first)
        
        # scores_str = ", ".join(f"{name}: {score}" for name, score in scores)
        
        for player in self.players:
            user = self.get_user(player)
            if user:
                parts = []
                for name, score in scores:
                    parts.append(Localization.get(user.locale, "threes-score-pair", player=name, score=score))
                
                scores_str = Localization.format_list(user.locale, parts)
                user.speak_l("threes-round-scores", buffer="game", round=self.current_round, scores=scores_str)

        # Check if game is over
        if self.current_round >= self.options.total_rounds:
            self._end_game()
        else:
            # Start next round
            self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.current_round += 1
        self.broadcast_l(
            "threes-round-start",
            round=self.current_round,
            total=self.options.total_rounds,
        )

        # Reset turn order to start of player list
        self.set_turn_players(self.get_active_players())

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, ThreesPlayer):
            return

        # Reset turn state
        player.dice.reset()
        player.turn_score = 0

        # Announce turn (plays sound and broadcasts message)
        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")

        if player.is_bot:
            import random

            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

        self.rebuild_all_menus()

    def _end_game(self) -> None:
        """End the game and announce winner."""
        # Find winner(s) (lowest score)
        players_with_scores = [
            (p, p.total_score) for p in self.players if isinstance(p, ThreesPlayer)
        ]
        players_with_scores.sort(key=lambda x: x[1])

        lowest_score = players_with_scores[0][1]
        winners = [p for p, s in players_with_scores if s == lowest_score]

        if len(winners) == 1:
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l(
                "threes-winner", player=winners[0].name, score=lowest_score
            )
        else:
            # winner_names = " and ".join(w.name for w in winners)
            winner_names_list = [w.name for w in winners]
            
            for player in self.players:
                user = self.get_user(player)
                if user:
                    winner_names = Localization.format_list_and(user.locale, winner_names_list)
                    user.speak_l("threes-tie", buffer="game", players=winner_names, score=lowest_score)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Threes-specific data."""
        # Sorted by score ascending (lowest wins)
        sorted_players = sorted(
            [p for p in self.players if isinstance(p, ThreesPlayer)],
            key=lambda p: p.total_score,
        )

        # Build final scores
        final_scores = {}
        for p in sorted_players:
            final_scores[p.name] = p.total_score

        winner = sorted_players[0] if sorted_players else None

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
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.total_score if winner else 0,
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
        for player in self.players:
            if isinstance(player, ThreesPlayer):
                player.total_score = 0
                player.dice.reset()

        # Initialize turn order
        self.set_turn_players(self.get_active_players())

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

        # Strategy 1: Go for moon shot if 3+ sixes locked or 4+ total sixes
        if locked_sixes >= 3 or (len(available_sixes) + locked_sixes >= 4):
            for i in available_sixes:
                dice.keep(i)
            if available_sixes:
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

        # Strategy 5: Keep lowest available
        for value in [4, 5, 6]:
            if value in available:
                dice.keep(available[value][0])
                return
