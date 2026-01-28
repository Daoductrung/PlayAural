"""Mixin providing score checking actions for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User
    from .teams import TeamManager

from ..messages.localization import Localization


class GameScoresMixin:
    """Mixin providing score checking and turn announcement actions.

    Expects on the Game class:
        - self.current_player: Player | None
        - self.team_manager: TeamManager
        - self.players: list[Player]
        - self.get_user(player) -> User | None
        - self.status_box(player, lines)
    """

    def _action_whose_turn(self, player: "Player", action_id: str) -> None:
        """Announce whose turn it is."""
        user = self.get_user(player)
        if user:
            current = self.current_player
            if current:
                user.speak_l("game-turn-start", player=current.name)
            else:
                user.speak_l("game-no-turn")

    def _action_whos_at_table(self, player: "Player", action_id: str) -> None:
        """Announce who is at the table."""
        user = self.get_user(player)
        if not user:
            return
        players = [p.name for p in self.players if not p.is_spectator]
        spectators = [p.name for p in self.players if p.is_spectator]
        count = len(players)
        if count == 0:
            user.speak_l("table-no-players")
            return
        names = Localization.format_list_and(user.locale, players)
        key = "table-players-one" if count == 1 else "table-players-many"
        user.speak_l(key, count=count, players=names)
        if spectators:
            spectator_names = Localization.format_list_and(user.locale, spectators)
            user.speak_l("table-spectators", spectators=spectator_names)

    def _action_check_scores(self, player: "Player", action_id: str) -> None:
        """Announce scores briefly."""
        user = self.get_user(player)
        if not user:
            return

        if self.team_manager.teams:
            user.speak(self.team_manager.format_scores_brief(user.locale))
        else:
            user.speak_l("no-scores-available")

    def _action_check_scores_detailed(self, player: "Player", action_id: str) -> None:
        """Show detailed scores in a status box."""
        user = self.get_user(player)
        if not user:
            return

        if self.team_manager.teams:
            lines = self.team_manager.format_scores_detailed(user.locale)
            self.status_box(player, lines)
        else:
            self.status_box(player, ["No scores available."])
