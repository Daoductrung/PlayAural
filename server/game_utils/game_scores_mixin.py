"""Mixin providing score checking actions for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User
    from .teams import TeamManager

from ..documentation.manager import DocumentationManager
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

        host_suffix = " " + Localization.get(user.locale, "table-host-suffix")

        players = []
        for p in self.players:
            if not p.is_spectator:
                name = p.name
                if name == self.host:
                    name += host_suffix
                players.append(name)

        spectators = []
        for p in self.players:
            if p.is_spectator:
                name = p.name
                if name == self.host:
                    name += host_suffix
                spectators.append(name)

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
            # Check for target score in options
            target_score = None
            if hasattr(self, "options"):
                if hasattr(self.options, "target_score"):
                    target_score = self.options.target_score
                elif hasattr(self.options, "winning_score"):
                    target_score = self.options.winning_score

            user.speak(self.team_manager.format_scores_brief(user.locale, target_score))
        else:
            user.speak_l("no-scores-available")

    def _action_check_scores_detailed(self, player: "Player", action_id: str) -> None:
        """Show detailed scores in a status box."""
        user = self.get_user(player)
        if not user:
            return

        if self.team_manager.teams:
            # Check for target score in options
            target_score = None
            if hasattr(self, "options"):
                if hasattr(self.options, "target_score"):
                    target_score = self.options.target_score
                elif hasattr(self.options, "winning_score"):
                    target_score = self.options.winning_score

            lines = self.team_manager.format_scores_detailed(user.locale, target_score)
            self.status_box(player, lines)
        else:
            self.status_box(player, ["No scores available."])

    def _action_game_info(self, player: "Player", action_id: str) -> None:
        """Show current game settings/options to the player."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        lines = [Localization.get(locale, "game-info-header")]

        # Game name
        game_name = Localization.get(locale, self.get_name_key())
        lines.append(Localization.get(locale, "game-info-name", game=game_name))

        # Player count
        active = [p for p in self.players if not p.is_spectator]
        lines.append(
            Localization.get(locale, "game-info-players", count=len(active))
        )

        # Host
        lines.append(Localization.get(locale, "game-info-host", host=self.host))

        # Status
        status_text = Localization.get(locale, f"game-info-status-{self.status}")
        lines.append(
            Localization.get(locale, "game-info-status", status=status_text)
        )

        # Options
        if hasattr(self, "options") and self.options.get_option_metas():
            lines.append(Localization.get(locale, "game-info-options-header"))
            for option_line in self.options.format_options_summary(locale):
                lines.append(f"  {option_line}")
        else:
            lines.append(Localization.get(locale, "game-info-no-options"))

        self.status_box(player, lines)

    def _action_game_rules(self, player: "Player", action_id: str) -> None:
        """Show the current game's rules/documentation to the player."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        doc_id = f"games/{self.get_type()}"
        manager = DocumentationManager.get_instance()
        content = manager.get_document(doc_id, locale)

        if not content:
            game_name = Localization.get(locale, self.get_name_key())
            user.speak_l("game-rules-not-available", game=game_name, buffer="system")
            return

        # Parse markdown into status_box lines (same logic as server.py doc viewer)
        lines = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            clean = (
                line.replace("**", "")
                .replace("__", "")
                .replace("*", "")
                .replace("`", "")
                .replace("&nbsp;", "")
            )
            if clean.startswith("#"):
                clean = clean.lstrip("#").strip()
            elif clean.startswith("-") or clean.startswith("•"):
                clean = clean.lstrip("-• ").strip()
            lines.append(clean)

        self.status_box(player, lines)
