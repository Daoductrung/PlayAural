"""Mixin providing score checking actions for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
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
        - self.speak_turn_l(listener, current, buffer=...)
        - self.status_box(player, lines)
        - self.live_status_box(player, box_id, builder)
    """

    def get_score_unit_key(self) -> str:
        """Return the localization key for this game's scoreboard unit."""
        return getattr(self, "score_unit_key", "game-score-unit-points")

    def get_score_target(self) -> int | None:
        """Return the configured score target, if the game exposes one."""
        if not hasattr(self, "options"):
            return None
        if hasattr(self.options, "target_score"):
            return self.options.target_score
        if hasattr(self.options, "winning_score"):
            return self.options.winning_score
        return None

    def get_score_sort_descending(self) -> bool:
        """Return whether shared score displays should sort high scores first."""
        return getattr(self, "score_sort_descending", True)

    def supports_score_actions(self) -> bool:
        """Return whether the shared score actions have score lines to report."""
        return bool(self.team_manager.teams)

    def _sync_score_display_names(self) -> None:
        """Align score display names with active replacement-bot seat names."""
        sync = getattr(self, "_sync_replacement_team_members", None)
        if callable(sync):
            sync()

    def _action_whose_turn(self, player: "Player", action_id: str) -> None:
        """Announce whose turn it is."""
        user = self.get_user(player)
        if user:
            current = self.current_player
            if current:
                self.speak_turn_l(player, current, buffer="game")
            else:
                user.speak_l("game-no-turn", buffer="game")

    def _action_whos_at_table(self, player: "Player", action_id: str) -> None:
        """Announce who is at the table."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        host_suffix = " " + Localization.get(locale, "table-host-suffix")
        voice_suffix = " " + Localization.get(locale, "table-voice-chat-suffix")

        players = []
        for p in self.players:
            if not p.is_spectator:
                players.append(
                    self._format_table_presence_name(p, host_suffix, voice_suffix)
                )

        spectators = []
        for p in self.players:
            if p.is_spectator:
                spectators.append(
                    self._format_table_presence_name(p, host_suffix, voice_suffix)
                )

        count = len(players)
        if count == 0:
            user.speak_l("table-no-players", buffer="game")
            return
        names = Localization.format_list_and(locale, players)
        key = "table-players-one" if count == 1 else "table-players-many"
        user.speak_l(key, buffer="game", count=count, players=names)
        if spectators:
            spectator_names = Localization.format_list_and(locale, spectators)
            user.speak_l("table-spectators", buffer="game", spectators=spectator_names)

    def _format_table_presence_name(
        self,
        table_player: "Player",
        host_suffix: str,
        voice_suffix: str,
    ) -> str:
        """Format a table member for the public presence list."""
        username = table_player.name
        name = username
        if name == self.host:
            name += host_suffix
        if not table_player.is_bot and self._is_table_member_in_voice_chat(username):
            name += voice_suffix
        return name

    def _is_table_member_in_voice_chat(self, username: str) -> bool:
        """Return whether a table member currently has voice presence here."""
        table = getattr(self, "_table", None)
        if not table:
            return False
        server = getattr(table, "_server", None)
        if not server:
            return False
        voice_presence = getattr(server, "_voice_presence_by_user", {})
        presence = voice_presence.get(username)
        if not presence:
            return False
        return (
            presence.get("scope") == "table"
            and presence.get("context_id") == getattr(table, "table_id", None)
        )

    def _action_check_scores(self, player: "Player", action_id: str) -> None:
        """Announce scores briefly."""
        user = self.get_user(player)
        if not user:
            return

        self._sync_score_display_names()
        if self.supports_score_actions():
            lines = self.team_manager.format_scores_detailed(
                user.locale,
                self.get_score_target(),
                score_unit_key=self.get_score_unit_key(),
                descending=self.get_score_sort_descending(),
            )
            for line in lines:
                user.speak(line, buffer="game")
        else:
            user.speak_l("no-scores-available", buffer="game")

    def _action_check_scores_detailed(self, player: "Player", action_id: str) -> None:
        """Show detailed scores in a status box."""
        user = self.get_user(player)
        if not user:
            return

        self._sync_score_display_names()
        if self.supports_score_actions():
            self.live_status_box(
                player,
                "detailed_scores",
                lambda _player, live_user: self._detailed_score_lines(live_user.locale),
            )
        else:
            self.status_box(
                player,
                [Localization.get(user.locale, "no-scores-available")],
            )

    def _detailed_score_lines(self, locale: str) -> list[str]:
        self._sync_score_display_names()
        return self.team_manager.format_scores_detailed(
            locale,
            self.get_score_target(),
            score_unit_key=self.get_score_unit_key(),
            descending=self.get_score_sort_descending(),
        )

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
            user.speak_l("game-rules-not-available", game=game_name, buffer="game")
            return

        self.status_box(player, manager.render_markdown_lines(content))
