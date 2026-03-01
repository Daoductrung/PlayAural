"""
Pig Game Implementation for PlayAural v0.1.0.

Classic dice game: roll or bank, but don't get a 1!
Supports individual and team modes via TeamManager.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, TeamModeOption, option_field
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


@dataclass
class PigPlayer(Player):
    """Player state for Pig game."""

    round_score: int = 0  # Score for current turn (lost on bust)


@dataclass
class PigOptions(GameOptions):
    """Options for Pig game using declarative option system."""

    target_score: int = option_field(
        IntOption(
            default=50,
            min_val=10,
            max_val=1000,
            value_key="score",
            label="game-set-target-score",
            prompt="game-enter-target-score",
            change_msg="game-option-changed-target",
        )
    )
    min_bank_points: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=50,
            value_key="points",
            label="pig-set-min-bank",
            prompt="pig-enter-min-bank",
            change_msg="pig-option-changed-min-bank",
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
        )
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=lambda g, p: TeamManager.get_all_team_modes(2, 4),
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
        )
    )


@dataclass
@register_game
class PigGame(Game):
    """
    Pig dice game.

    Players take turns rolling a die. Each roll adds to their round score,
    but rolling a 1 loses all points for that round. Players can bank their
    points at any time to add them to their total score and end their turn.
    First player to reach the target score wins.
    """

    # Game-specific state - use PigPlayer list instead of Player
    players: list[PigPlayer] = field(default_factory=list)
    options: PigOptions = field(default_factory=PigOptions)

    @classmethod
    def get_name(cls) -> str:
        return "Pig"

    @classmethod
    def get_type(cls) -> str:
        return "pig"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> PigPlayer:
        """Create a new player with Pig-specific state."""
        return PigPlayer(id=player_id, name=name, is_bot=is_bot, round_score=0)

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label methods for turn actions
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        # Always return string if it's not the player's turn
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

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        pig_player: PigPlayer = player  # type: ignore
        min_required = max(1, self.options.min_bank_points)
        if pig_player.round_score < min_required:
            return "pig-need-more-points"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank is hidden until player has enough points."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        pig_player: PigPlayer = player  # type: ignore
        min_required = max(1, self.options.min_bank_points)
        if pig_player.round_score < min_required:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for bank action showing current points."""
        pig_player: PigPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "pig-bank", points=pig_player.round_score)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: PigPlayer) -> ActionSet:
        """Create the turn action set for a player."""
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
                label=Localization.get(locale, "pig-bank", points=0),
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
        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player_by_name(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        self.define_keybind("r", Localization.get(locale, "pig-roll"), ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("b", Localization.get(locale, "pig-bank", points=0), ["bank"], state=KeybindState.ACTIVE)

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        pig_player: PigPlayer = player  # type: ignore

        self.broadcast_l("pig-rolls", player=player.name)
        self.play_sound("game_pig/roll.ogg")

        # Jolt the rolling player to pause before next action
        BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        roll = random.randint(1, self.options.dice_sides)

        if roll == 1:
            # Bust!
            self.play_sound("game_pig/lose.ogg")
            self.broadcast_l(
                "pig-bust", player=player.name, points=pig_player.round_score
            )
            pig_player.round_score = 0
            self.end_turn()
        else:
            pig_player.round_score += roll
            self.broadcast_l("pig-roll-result", roll=roll, total=pig_player.round_score)
            # Menus will be rebuilt automatically after action execution

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Handle bank action."""
        pig_player: PigPlayer = player  # type: ignore

        self.play_sound("game_pig/bank.ogg")
        banked = pig_player.round_score

        # Add to team score via TeamManager
        self._team_manager.add_to_team_score(player.name, banked)
        team = self._team_manager.get_team(player.name)
        total = team.total_score if team else 0

        pig_player.round_score = 0
        self.broadcast_l(
            "pig-bank-action", player=player.name, points=banked, total=total
        )

        self.end_turn()

    def get_player_score(self, player: PigPlayer) -> int:
        """Get a player's total score from TeamManager."""
        team = self._team_manager.get_team(player.name)
        return team.total_score if team else 0

    def prestart_validate(self) -> list[str]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        # Validate team mode for current player count
        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)

        # Ensure min_bank_points is less than target_score
        if self.options.min_bank_points >= self.options.target_score:
            errors.append("pig-error-min-bank-too-high")

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Set up teams based on active players
        active_players = self.get_active_players()
        # options.team_mode should be in internal format, but handle old display format for backwards compatibility
        team_mode = self.options.team_mode
        # If it contains spaces or uppercase (except 'v'), it's likely old display format
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)
        self._team_manager.team_mode = team_mode
        self._team_manager.setup_teams([p.name for p in active_players])

        # Initialize turn order
        self.set_turn_players(active_players)

        # Reset player round scores (total scores are in TeamManager)
        for player in active_players:
            player.round_score = 0

        # Play intro music
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Refresh turn order with current active players (handles tiebreakers)
        # and reset to first player for the new round
        self.set_turn_players(self.get_active_players())

        self.play_sound("game_pig/roundstart.ogg")
        self.broadcast_l("game-round-start", round=self.round)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        player.round_score = 0

        # Announce turn (plays sound and broadcasts message)
        self.announce_turn()

        # Set up bot target if this is a bot's turn
        if player.is_bot:
            self._setup_bot_target(player)

        # Rebuild menus to reflect new turn
        self.rebuild_all_menus()

    def _setup_bot_target(self, player: Player) -> None:
        """Set up the bot's target score for this turn."""
        # Base target: random between 10-25
        target = random.randint(10, 25)

        # Check if anyone is close to winning or has won (active players only)
        active_players = self.get_active_players()
        someone_hit_threshold = False
        highest_score = 0
        my_score = self.get_player_score(player)

        for other in active_players:
            if other != player:
                other_score = self.get_player_score(other)
                if other_score >= self.options.target_score:
                    someone_hit_threshold = True
                    highest_score = max(highest_score, other_score)
                elif other_score >= self.options.target_score - 1:
                    highest_score = max(highest_score, other_score)

        if someone_hit_threshold:
            # Need to beat the highest score
            target = highest_score + 1 - my_score
        elif highest_score > 0:
            # Someone close, try to beat them
            target = highest_score + 1 - my_score

        # If bot is close to winning, can relax
        if (my_score + player.round_score) >= (
            self.options.target_score - 1
        ) and not someone_hit_threshold:
            can_relax = True
            for other in active_players:
                if other != player:
                    other_score = self.get_player_score(other)
                    if other_score > (my_score + player.round_score - 8):
                        can_relax = False
                        break
            if can_relax:
                target = 0

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

    def bot_think(self, player: PigPlayer) -> str | None:
        """Bot AI decision making. Called by BotHelper."""
        target = BotHelper.get_target(player)
        if target is None:
            target = 15  # Default fallback

        # Decide: bank or roll?
        min_bank = max(1, self.options.min_bank_points)
        if player.round_score >= target and player.round_score >= min_bank:
            return "bank"
        else:
            return "roll"

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check if round is over (all active players have gone)
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            # Next player (don't announce yet, _start_turn will do it)
            self.advance_turn(announce=False)
            self._start_turn()

    def _on_round_end(self) -> None:
        """Handle end of a round."""
        # Check for winners by checking teams, not individual players
        # This prevents multiple teammates from all being counted as winners
        active_players = self.get_active_players()
        winning_teams = []
        high_score = 0

        # Get teams that have reached the target score
        teams_checked = set()
        for player in active_players:
            team = self._team_manager.get_team(player.name)
            if not team or team.index in teams_checked:
                continue
            teams_checked.add(team.index)

            score = team.total_score
            if score >= self.options.target_score:
                if score > high_score:
                    winning_teams = [team]
                    high_score = score
                elif score == high_score:
                    winning_teams.append(team)

        if len(winning_teams) == 1:
            # Single winning team!
            self.play_sound("game_pig/win.ogg")
            winning_team = winning_teams[0]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    team_name = self._team_manager.get_team_name(winning_team, user.locale)
                    user.speak_l("pig-winner", buffer="game", player=team_name)
            self.finish_game()
        elif len(winning_teams) > 1:
            # Tiebreaker! Start immediately (no delay)
            team_names = [self._team_manager.get_team_name(t) for t in winning_teams]
            # Format list with locale-aware "and"
            for player in self.players:
                user = self.get_user(player)
                if user:
                    names_str = Localization.format_list_and(user.locale, team_names)
                    user.speak_l("game-tiebreaker-players", buffer="game", players=names_str)

            # Mark players not on winning teams as spectators for the tiebreaker
            winning_team_indices = {t.index for t in winning_teams}
            for p in active_players:
                team = self._team_manager.get_team(p.name)
                if not team or team.index not in winning_team_indices:
                    p.is_spectator = True
            self._start_round()
        else:
            # No winner yet, continue to next round
            self._start_round()

    def build_game_result(self) -> GameResult:
        """Build the game result with Pig-specific data."""
        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )
        winner = sorted_teams[0] if sorted_teams else None

        # Build final scores dict (legacy) and rankings with metadata (new)
        final_scores = {}
        team_rankings = []
        for team in sorted_teams:
            name = self._team_manager.get_team_name(team)
            final_scores[name] = team.total_score
            
            team_rankings.append({
                "index": team.index,
                "members": team.members,
                "score": team.total_score,
                "name_legacy": name,
                "is_individual": self.options.team_mode == "individual"
            })

        winner_ids = []
        if winner:
            # Map member names to player IDs
            active_players = self.get_active_players()
            name_to_id = {p.name: p.id for p in active_players}
            for member_name in winner.members:
                if member_name in name_to_id:
                    winner_ids.append(name_to_id[member_name])

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
                "winner_name": self._team_manager.get_team_name(winner) if winner else None,
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "team_mode": self.options.team_mode,
            },
        )

        return lines

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Pig game."""
        lines = [Localization.get(locale, "game-final-scores")]

        team_rankings = result.custom_data.get("team_rankings")
        
        if team_rankings:
            for i, data in enumerate(team_rankings, 1):
                # Reconstruct localized name
                if data.get("is_individual") and data.get("members"):
                    name = data["members"][0]
                else:
                    # Team mode: "Team X" (localized)
                    # For individual mode with custom team names, this also works if we had them
                    # But for now, just handle standard team naming
                    name = Localization.get(locale, "game-team-name", index=data["index"] + 1)
                
                score = data["score"]
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(locale, "pig-line-format", rank=i, player=name, points=points_str)
                )
        else:
            # Fallback for old results
            final_scores = result.custom_data.get("final_scores", {})
            for i, (name, score) in enumerate(final_scores.items(), 1):
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(locale, "pig-line-format", rank=i, player=name, points=points_str)
                )

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """Override to use Pig's turn advancement logic."""
        # Jolt all bots to pause for the turn change
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))
        self._on_turn_end()
