"""
Toss Up Game Implementation for PlayAural v0.1.0.

Push-your-luck dice game: roll dice with green/yellow/red sides.
Green = points + remove die. Yellow = remove die. Red = danger!
All red = bust! Bank your points or risk it all.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


@dataclass
class TossUpPlayer(Player):
    """Player state for Toss Up game."""

    turn_points: int = 0  # Points accumulated this turn (lost on bust)
    dice_count: int = 0  # Number of dice remaining this turn
    last_roll: dict[str, int] = field(
        default_factory=dict
    )  # Last roll results {green, yellow, red}


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
        )
    )


@dataclass
@register_game
class TossUpGame(Game):
    """
    Toss Up dice game.

    Roll dice with green/yellow/red sides. Green dice add points and are removed.
    Yellow dice are removed but don't add points. Red dice stay in play.
    Bust if all dice show red (PlayAural) or if you have no greens and at least
    one red (Standard). Bank your points or keep rolling - but don't bust!
    When you run out of dice, you get a fresh set. First to reach target score wins.
    """

    # Game-specific state
    players: list[TossUpPlayer] = field(default_factory=list)
    options: TossUpOptions = field(default_factory=TossUpOptions)

    @classmethod
    def get_name(cls) -> str:
        return "Toss Up"

    @classmethod
    def get_type(cls) -> str:
        return "tossup"

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
    ) -> TossUpPlayer:
        """Create a new player with TossUp-specific state."""
        return TossUpPlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            turn_points=0,
            dice_count=0,
            last_roll={},
        )

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label methods for turn actions
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Roll is visible during play for current player."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for roll action showing dice count."""
        tossup_player: TossUpPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if tossup_player.turn_points == 0:
            # First roll of turn
            return Localization.get(
                locale, "tossup-roll-first", count=tossup_player.dice_count
            )
        else:
            # Subsequent rolls
            return Localization.get(
                locale, "tossup-roll-remaining", count=tossup_player.dice_count
            )

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        tossup_player: TossUpPlayer = player  # type: ignore
        if tossup_player.turn_points <= 0:
            return "tossup-need-points"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank is hidden until player has rolled at least once."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        tossup_player: TossUpPlayer = player  # type: ignore
        if tossup_player.turn_points <= 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for bank action showing current points."""
        tossup_player: TossUpPlayer = player  # type: ignore
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

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_scores", "whose_turn", "whos_at_table"]

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

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        # Call parent for lobby/standard keybinds (includes t, s, shift+s)
        super().setup_keybinds()

        # Turn action keybinds
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Bank points", ["bank"], state=KeybindState.ACTIVE)

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        tossup_player: TossUpPlayer = player  # type: ignore

        self.play_sound("game_pig/roll.ogg")

        # Jolt the rolling player to pause before next action
        BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        # Roll the dice
        green = 0
        yellow = 0
        red = 0

        is_standard = self.options.rules_variant == "Standard"

        for _ in range(tossup_player.dice_count):
            if is_standard:
                # Standard: 3 green, 2 yellow, 1 red (6-sided die)
                roll = random.randint(1, 6)
                if roll <= 3:
                    green += 1
                elif roll <= 5:
                    yellow += 1
                else:
                    red += 1
            else:
                # PlayAural: Equal distribution (3-sided die)
                roll = random.randint(1, 3)
                if roll == 1:
                    green += 1
                elif roll == 2:
                    yellow += 1
                else:
                    red += 1

        tossup_player.last_roll = {"green": green, "yellow": yellow, "red": red}

        # Announce results
        for p in self.get_active_players():
            user = self.get_user(p)
            if not user:
                continue
            
            # Format results for this user's locale
            result_text = self._format_roll_results(user.locale, green, yellow, red)

            if p == player:
                user.speak_l("tossup-you-roll", buffer="game", results=result_text)
            else:
                user.speak_l("tossup-player-rolls", buffer="game", player=player.name, results=result_text)

        # Check for bust based on rules variant
        is_bust = False
        if is_standard:
            # Standard: Bust if you have at least one red AND no greens
            is_bust = green == 0 and red > 0
        else:
            # PlayAural: Bust if all red (no green, no yellow)
            is_bust = green == 0 and yellow == 0

        if is_bust:
            # Bust!
            self.play_sound("game_pig/lose.ogg")

            self.broadcast_personal_l(
                player,
                "tossup-you-bust",
                "tossup-player-busts",
                points=tossup_player.turn_points,
            )

            tossup_player.turn_points = 0
            self.end_turn()
            return
            
        # Add green dice to turn points
        tossup_player.turn_points += green
        
        # Remove green dice from pool (yellow and red remain)
        tossup_player.dice_count = yellow + red

        # Announce turn status
        self.broadcast_personal_l(
            player,
            "tossup-you-have-points",
            "tossup-player-has-points",
            turn_points=tossup_player.turn_points,
            dice_count=tossup_player.dice_count,
        )

        # Check if no dice left (refresh dice)
        if tossup_player.dice_count == 0:
            tossup_player.dice_count = self.options.starting_dice

            self.broadcast_personal_l(
                player,
                "tossup-you-get-fresh",
                "tossup-player-gets-fresh",
                count=tossup_player.dice_count,
            )

        # Menus will be rebuilt automatically after action execution

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Handle bank action."""
        tossup_player: TossUpPlayer = player  # type: ignore

        self.play_sound("game_pig/bank.ogg")
        banked = tossup_player.turn_points

        # Add to team score via TeamManager
        self._team_manager.add_to_team_score(player.name, banked)
        team = self._team_manager.get_team(player.name)
        total = team.total_score if team else 0

        tossup_player.turn_points = 0

        # Announce banking
        self.broadcast_personal_l(
            player,
            "tossup-you-bank",
            "tossup-player-banks",
            points=banked,
            total=total,
        )

        self.end_turn()

    def get_player_score(self, player: TossUpPlayer) -> int:
        """Get a player's total score from TeamManager."""
        team = self._team_manager.get_team(player.name)
        return team.total_score if team else 0

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

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

        # Play intro music
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Refresh turn order with current active players (handles tiebreakers)
        self.set_turn_players(self.get_active_players())

        self.play_sound("game_pig/roundstart.ogg")
        self.broadcast_l("game-round-start", round=self.round)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        tossup_player: TossUpPlayer = player  # type: ignore
        tossup_player.turn_points = 0
        tossup_player.dice_count = self.options.starting_dice
        tossup_player.last_roll = {}

        # Get current score
        current_score = self.get_player_score(tossup_player)

        # Custom turn announcement for Toss Up
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("game_pig/turn.ogg")
        self.broadcast_l("tossup-turn-start", player=player.name, score=current_score)

        # Set up bot target if this is a bot's turn
        if player.is_bot:
            self._setup_bot_target(player)

        # Rebuild menus to reflect new turn
        self.rebuild_all_menus()

    def _setup_bot_target(self, player: Player) -> None:
        """Set up the bot's target score for this turn."""
        tossup_player: TossUpPlayer = player  # type: ignore

        # Base target: random between 10-25
        target = random.randint(10, 25)

        # Check if anyone is close to winning
        active_players = self.get_active_players()
        someone_hit_threshold = False
        highest_score = 0
        my_score = self.get_player_score(tossup_player)

        for other in active_players:
            if other != player:
                other_score = self.get_player_score(other)
                if other_score >= self.options.target_score:
                    someone_hit_threshold = True
                    highest_score = max(highest_score, other_score)

        if someone_hit_threshold:
            # Need to beat the highest score
            target = highest_score + 1 - my_score
        else:
            # Check if opponent is within 20 points of winning (go desperate)
            max_opponent_score = 0
            for other in active_players:
                if other != player:
                    other_score = self.get_player_score(other)
                    max_opponent_score = max(max_opponent_score, other_score)

            if max_opponent_score >= (self.options.target_score - 20):
                # Desperate mode: never bank unless winning
                target = 999  # Very high target

        BotHelper.set_target(player, max(0, target))

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()

        if not self.game_active:
            return

        # Ensure bot target is set up (needed after reload)
        player = self.current_player
        if player and player.is_bot and BotHelper.get_target(player) is None:
            self._setup_bot_target(player)

        BotHelper.on_tick(self)

    def bot_think(self, player: TossUpPlayer) -> str | None:
        """Bot AI decision making. Called by BotHelper."""
        target = BotHelper.get_target(player)
        if target is None:
            target = 15  # Default fallback

        # If we can win this turn, bank immediately
        my_score = self.get_player_score(player)
        if my_score + player.turn_points >= self.options.target_score:
            return "bank"

        # Decide based on dice count and target
        dice_count = player.dice_count

        # If we haven't rolled yet, always roll
        if player.turn_points == 0:
            return "roll"

        # If we've hit our target, consider banking based on dice count
        if player.turn_points >= target:
            # More dice = more likely to bust, so bank more often
            if dice_count == 1:
                bank_chance = 0.55
            elif dice_count == 2:
                bank_chance = 0.30
            elif dice_count == 3:
                bank_chance = 0.10
            else:
                bank_chance = 0.02

            if random.random() < bank_chance:
                return "bank"
            else:
                return "roll"
        else:
            # Haven't hit target yet, keep rolling
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
        # Check for winners (only among active players)
        active_players = self.get_active_players()
        winners = []
        high_score = 0

        for player in active_players:
            score = self.get_player_score(player)
            if score >= self.options.target_score:
                if score > high_score:
                    winners = [player]
                    high_score = score
                elif score == high_score:
                    winners.append(player)

        if len(winners) == 1:
            # Single winner!
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l(
                "tossup-winner", player=winners[0].name, score=high_score
            )
            self.finish_game()
        elif len(winners) > 1:
            # Tiebreaker!
            names = [w.name for w in winners]
            for player in self.players:
                user = self.get_user(player)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l("tossup-tie-tiebreaker", buffer="game", players=names_str)

            # Mark non-winners as spectators for the tiebreaker
            winner_names = [w.name for w in winners]
            for p in active_players:
                if p.name not in winner_names:
                    p.is_spectator = True
            self._start_round()
        else:
            # No winner yet, continue to next round
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
                    is_bot=p.is_bot,
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
