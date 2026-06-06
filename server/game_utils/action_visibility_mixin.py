"""Mixin providing action visibility callbacks for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from ..users.base import User
    from .teams import TeamManager

from .actions import Visibility
from ..messages.localization import Localization


class ActionVisibilityMixin:
    """Mixin providing is_enabled/is_hidden/get_label methods for base actions.

    Also provides player helper methods used by visibility checks.

    Expects on the Game class:
        - self.status: str
        - self.host: str
        - self.players: list[Player]
        - self.team_manager: TeamManager
        - self.get_user(player) -> User | None
        - self.get_min_players() -> int
        - self.get_max_players() -> int
    """

    # Player helper methods

    def _is_player_spectator(self, player: "Player") -> bool:
        """Check if a player is a spectator."""
        return player.is_spectator

    def get_active_players(self) -> list["Player"]:
        """Get list of players who are not spectators (actually playing)."""
        return [p for p in self.players if not p.is_spectator]

    def get_active_player_count(self) -> int:
        """Get the number of active (non-spectator) players."""
        return len(self.get_active_players())

    # --- Lobby actions ---

    def _is_start_game_enabled(self, player: "Player") -> str | None:
        """Check if start_game action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if self.team_arrangement_active:
            if player.name != self.host:
                return "action-not-host"
            return None
        if player.name != self.host:
            return "action-not-host"
        active_count = self.get_active_player_count()
        if active_count < self.get_min_players():
            return "action-need-more-players"
        return None

    def _is_start_game_hidden(self, player: "Player") -> Visibility:
        """Check if start_game action is hidden."""
        if self.status != "waiting" or self.team_arrangement_active:
            return Visibility.HIDDEN
        if self.get_active_player_count() < self.get_min_players():
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_confirm_team_arrangement_enabled(self, player: "Player") -> str | None:
        """Check if team arrangement can be confirmed."""
        if self.status != "waiting":
            return "action-not-available"
        if not self.team_arrangement_active:
            return "action-not-available"
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_confirm_team_arrangement_hidden(self, player: "Player") -> Visibility:
        """Show confirm only during team arrangement."""
        if self.status == "waiting" and self.team_arrangement_active:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_team_arrangement_enabled(self, player: "Player") -> str | None:
        """Check if current arranged teams can be read."""
        if not self.team_arrangement_active:
            return "team-arrangement-not-active"
        return None

    def _is_read_team_arrangement_hidden(self, player: "Player") -> Visibility:
        """Show read-teams only during team arrangement."""
        if self.status == "waiting" and self.team_arrangement_active:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_select_team_member_enabled(self, player: "Player") -> str | None:
        """Check if the host can select a team member to move."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if not self.team_arrangement_active:
            return "team-arrangement-not-active"
        if player.name != self.host:
            return "action-not-host"
        if self.get_active_player_count() < 2:
            return "action-need-more-players"
        if not self._team_arrangement_is_valid():
            return "game-error-invalid-team-mode"
        return None

    def _is_select_team_member_hidden(self, player: "Player") -> Visibility:
        """Show member selection only to the host during arrangement."""
        if (
            self.status == "waiting"
            and self.team_arrangement_active
            and player.name == self.host
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_swap_team_member_enabled(self, player: "Player") -> str | None:
        """Check if the selected member can be swapped."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if not self.team_arrangement_active:
            return "team-arrangement-not-active"
        if player.name != self.host:
            return "action-not-host"
        if not self.team_arrangement_selected_player_id:
            return "team-arrangement-select-first"
        if not self._team_arrangement_is_valid():
            return "game-error-invalid-team-mode"
        if not self._team_arrangement_swap_options(player):
            return "no-options-available"
        return None

    def _is_swap_team_member_hidden(self, player: "Player") -> Visibility:
        """Show swap action only after the host selects a member."""
        if (
            self.status == "waiting"
            and self.team_arrangement_active
            and self.team_arrangement_selected_player_id
            and player.name == self.host
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_cancel_team_arrangement_enabled(self, player: "Player") -> str | None:
        """Check if team arrangement can be cancelled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if not self.team_arrangement_active:
            return "team-arrangement-not-active"
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_cancel_team_arrangement_hidden(self, player: "Player") -> Visibility:
        """Show cancel only during team arrangement."""
        if self.status == "waiting" and self.team_arrangement_active:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_add_bot_enabled(self, player: "Player") -> str | None:
        """Check if add_bot action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if self.team_arrangement_active:
            return "team-arrangement-in-progress"
        if player.name != self.host:
            return "action-not-host"
        if self.get_active_player_count() >= self.get_max_players():
            return "action-table-full"
        return None

    def _is_add_bot_hidden(self, player: "Player") -> Visibility:
        """Add bot is always hidden (actions menu/keybind only)."""
        return Visibility.HIDDEN

    def _is_remove_bot_enabled(self, player: "Player") -> str | None:
        """Check if remove_bot action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if self.team_arrangement_active:
            return "team-arrangement-in-progress"
        if player.name != self.host:
            return "action-not-host"
        if not any(p.is_bot for p in self.players):
            return "action-no-bots"
        return None

    def _is_remove_bot_hidden(self, player: "Player") -> Visibility:
        """Remove bot is always hidden (actions menu/keybind only)."""
        return Visibility.HIDDEN

    def _is_toggle_spectator_enabled(self, player: "Player") -> str | None:
        """Check if toggle_spectator action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if self.team_arrangement_active:
            return "team-arrangement-in-progress"
        if player.is_bot:
            return "action-bots-cannot"
        return None

    def _is_toggle_spectator_hidden(self, player: "Player") -> Visibility:
        """Toggle spectator is always hidden (actions menu/keybind only)."""
        return Visibility.HIDDEN

    def _get_toggle_spectator_label(self, player: "Player", action_id: str) -> str:
        """Get dynamic label for toggle_spectator action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if player.is_spectator:
            return Localization.get(locale, "play")
        return Localization.get(locale, "spectate")

    def _is_host_management_enabled(self, player: "Player") -> str | None:
        """Host management is only available to the host."""
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_host_management_hidden(self, player: "Player") -> Visibility:
        """Host management is always hidden (actions menu / Ctrl+M only)."""
        return Visibility.HIDDEN

    def _is_leave_game_enabled(self, player: "Player") -> str | None:
        """Leave game is always enabled."""
        return None

    def _is_leave_game_hidden(self, player: "Player") -> Visibility:
        """Leave game is always hidden (actions menu/keybind only)."""
        return Visibility.HIDDEN

    # --- Option actions ---

    def _is_option_enabled(self, player: "Player") -> str | None:
        """Check if option actions are enabled (waiting state, host only)."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if self.team_arrangement_active:
            return "team-arrangement-in-progress"
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_option_hidden(self, player: "Player") -> Visibility:
        """Options are visible in waiting state only."""
        if self.status != "waiting" or self.team_arrangement_active:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # --- Standard actions ---

    def _is_show_actions_enabled(self, player: "Player") -> str | None:
        """Show actions menu is always enabled."""
        return None

    def _is_show_actions_hidden(self, player: "Player") -> Visibility:
        """Show actions is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_save_table_enabled(self, player: "Player") -> str | None:
        """Check if save_table action is enabled."""
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_save_table_hidden(self, player: "Player") -> Visibility:
        """Save table is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_whose_turn_enabled(self, player: "Player") -> str | None:
        """Check if whose_turn action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Whose turn is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_whos_at_table_enabled(self, player: "Player") -> str | None:
        """Check if whos_at_table action is enabled."""
        return None

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Whos at table is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_scores_enabled(self, player: "Player") -> str | None:
        """Check if check_scores action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if not self.supports_score_actions():
            return "action-not-available"
        return None

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Check scores is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_scores_detailed_enabled(self, player: "Player") -> str | None:
        """Check if check_scores_detailed action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if not self.supports_score_actions():
            return "action-not-available"
        return None

    def _is_check_scores_detailed_hidden(self, player: "Player") -> Visibility:
        """Check scores detailed is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_predict_outcomes_enabled(self, player: "Player") -> str | None:
        """Check if predict_outcomes action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if "rating" not in self.get_supported_leaderboards():
            return "action-not-available"
        # Need at least 2 human players for meaningful predictions
        human_count = sum(1 for p in self.players if not p.is_bot and not p.is_spectator)
        if human_count < 2:
            return "action-need-more-humans"
        return None

    def _is_predict_outcomes_hidden(self, player: "Player") -> Visibility:
        """Predict outcomes is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_game_info_enabled(self, player: "Player") -> str | None:
        """Game info is always enabled."""
        return None

    def _is_game_info_hidden(self, player: "Player") -> Visibility:
        """Game info is always hidden (keybind/actions menu only)."""
        return Visibility.HIDDEN

    def _is_game_rules_enabled(self, player: "Player") -> str | None:
        """Game rules is always enabled."""
        return None

    def _is_game_rules_hidden(self, player: "Player") -> Visibility:
        """Game rules is always hidden (keybind/actions menu only)."""
        return Visibility.HIDDEN
