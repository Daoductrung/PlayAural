"""Mixin providing game result handling and persistence."""

from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .player import Player
    from ..users.base import User

from .game_result import GameResult, PlayerResult
from .stats_helpers import RatingHelper
from ..messages.localization import Localization
from ..users.base import MenuItem, EscapeBehavior


class GameResultMixin:
    """Mixin providing game result building, persistence, and end screen display.

    Expects on the Game class:
        - self.game_active: bool
        - self.status: str
        - self.players: list[Player]
        - self.sound_scheduler_tick: int
        - self._table: Any
        - self.get_user(player) -> User | None
        - self.get_type() -> str
        - self.get_active_players() -> list[Player]
        - self.destroy()
    """

    def clear_last_game_result(self) -> None:
        """Clear the stored last game result."""
        self._last_game_result = None
        self._ensure_end_screen_state()
        self._end_screen_open_player_ids.clear()

    def _ensure_end_screen_state(self) -> None:
        """Initialize runtime-only end-screen state for old restored instances."""
        if not hasattr(self, "_end_screen_open_player_ids"):
            self._end_screen_open_player_ids = set()

    def finish_game(self, show_end_screen: bool = True) -> None:
        """Mark the game as finished, persist result, and optionally show end screen.

        Call this instead of setting status directly to ensure proper cleanup.
        If no humans remain, the table is automatically destroyed.

        Args:
            show_end_screen: Whether to show the end screen (default True).
                             Set to False if you want to show it manually.
        """
        self.game_active = False
        self.status = "finished"
        self._sync_table_status()

        # Build and persist the game result
        result = self.build_game_result()
        self._last_game_result = result  # Store for menu restoration
        self._ensure_end_screen_state()
        self._end_screen_open_player_ids.clear()
        self._persist_result(result)

        # Retire every replayable game-owned source while allowing untracked
        # one-shot victory cues to finish. Ambience stems splice directly to
        # their authored outros without waiting for a long loop boundary.
        self.stop_replayable_audio(
            fade_ms=0,
            play_ambience_outros=True,
            outro_mode="immediate",
        )

        # Show end screen
        if show_end_screen:
            self._show_end_screen(result)

        # Auto-destroy if no humans remain (bot-only games), else reset table for next game
        has_humans = any(not p.is_bot for p in self.players)
        if not has_humans:
            self.destroy()
        else:
            if self._table:
                self._table.reset_game()

    def build_game_result(self) -> GameResult:
        """Build the game result. Override in subclasses for custom data.

        Returns:
            A GameResult with game-specific data in custom_data.
        """
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in self.get_active_players()
            ],
            custom_data={},
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen lines from a game result. Override for custom display.

        Args:
            result: The game result to format
            locale: The locale to use for localization

        Returns:
            List of lines to display on the end screen
        """
        # Default implementation - just show "Game Over" and player names
        lines = [Localization.get(locale, "game-over")]
        for p in result.player_results:
            lines.append(p.player_name)
        return lines

    def _persist_result(self, result: GameResult) -> None:
        """Persist one result, its derived stats, and ratings atomically."""
        # Only persist if there are human players
        if not result.has_human_players():
            return
        if result.game_type != self.get_type():
            logging.getLogger("playaural.results").error(
                "Refused mismatched result type %s from game %s",
                result.game_type,
                self.get_type(),
            )
            return

        if self._table:
            rating_updates = self._calculate_rating_updates(result)
            try:
                self._table.save_game_result(result, rating_updates=rating_updates)
            except Exception:
                # Result storage is transactional. A persistence failure must
                # never leave gameplay stuck in its finished transition.
                logging.getLogger("playaural.results").exception(
                    "Failed to persist completed %s game result",
                    self.get_type(),
                )

    def _calculate_rating_updates(
        self,
        result: GameResult,
    ) -> dict[str, tuple[float, float]]:
        """Return validated rating values for the result without persisting them."""
        if "rating" not in self.get_supported_leaderboards():
            return {}
        if result.custom_data.get("competitive") is False:
            return {}

        if not self._table or not self._table._db:
            return {}

        rating_helper = RatingHelper(self._table._db, self.get_type())
        try:
            teams, ranks = RatingHelper.extract_teams_and_ranks(result)
            updates = rating_helper.calculate_updates(teams, ranks=ranks)
        except Exception:
            # A malformed rating payload must not strand the table at game end.
            # Skip settlement and leave a diagnostic; the independent result
            # and stat validation still decides whether persistence is safe.
            logging.getLogger("playaural.ratings").exception(
                "Skipped invalid rating settlement for game %s",
                self.get_type(),
            )
            return {}
        return {
            player_id: (rating.mu, rating.sigma)
            for player_id, rating in updates.items()
        }

    def _show_end_screen(self, result: GameResult) -> None:
        """Show the end screen to all players using structured result."""
        for player in self.players:
            self._show_end_screen_to_player(player, result)

    def _set_end_screen_server_state(self, user: "User") -> None:
        """Tell the server that this user's active UI is the post-game screen."""
        server = getattr(getattr(self, "_table", None), "_server", None)
        table_id = getattr(getattr(self, "_table", None), "table_id", None)
        if server is not None and table_id and hasattr(server, "_set_game_over_state"):
            server._set_game_over_state(user, table_id)

    def _clear_end_screen_server_state(self, user: "User") -> None:
        """Clear the server's post-game UI state for this user."""
        server = getattr(getattr(self, "_table", None), "_server", None)
        table_id = getattr(getattr(self, "_table", None), "table_id", None)
        if server is not None and table_id and hasattr(server, "_clear_game_over_state"):
            server._clear_game_over_state(user, table_id)

    def _can_present_end_screen_to_user(self, user: "User") -> bool:
        """Return whether the result may replace this user's current surface."""
        table = getattr(self, "_table", None)
        server = getattr(table, "_server", None)
        table_id = getattr(table, "table_id", None)
        if server is None or not table_id:
            return True
        checker = getattr(server, "_can_present_game_over", None)
        return bool(checker and checker(user, table_id))

    def _show_end_screen_to_player(
        self,
        player: "Player",
        result: GameResult,
        *,
        mark_open: bool = True,
    ) -> None:
        """Show the end screen to a specific player."""
        user = self.get_user(player)
        if user:
            if mark_open:
                self._ensure_end_screen_state()
                self._end_screen_open_player_ids.add(player.id)

            # Global server menus and editboxes own the client surface until
            # their normal Back/submission flow returns to this table. Keep the
            # result pending without changing server UI state or dismissing any
            # active input. A later game-menu refresh restores it immediately.
            if not self._can_present_end_screen_to_user(user):
                return

            # A result can replace an action input without an intervening
            # player event (for example, when another player ends the game).
            # Dismiss that modal explicitly before painting the result so web
            # clients never retain an authoritative edit box over game_over.
            if player.id in self._pending_actions:
                self._discard_pending_action_input(player, user)
            lines = self.format_end_screen(result, user.locale)
            items = [
                MenuItem(text=line, id=f"score_line_{index}")
                for index, line in enumerate(lines)
            ]
            # Leave first, return second: Escape selects the safer return action.
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "game-leave"),
                    id="leave_game",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "return-to-table"),
                    id="return_to_table",
                )
            )
            # game_over selections are routed through EventHandlingMixin.
            user.show_menu(
                "game_over",
                items,
                multiletter=False,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )

            self._set_end_screen_server_state(user)
            self._actions_menu_open.discard(player.id)

    def _is_end_screen_open_for_player(self, player: "Player") -> bool:
        """Return whether this player's post-game screen is still active."""
        self._ensure_end_screen_state()
        return player.id in self._end_screen_open_player_ids

    def _clear_result_if_no_end_screens_remain(self) -> None:
        """Release the stored result once no player can still view it."""
        self._ensure_end_screen_state()
        if not self._end_screen_open_player_ids:
            self._last_game_result = None

    def _discard_end_screen_player_id(self, player_id: str) -> None:
        """Remove one player id from the post-game overlay state."""
        self._ensure_end_screen_state()
        self._end_screen_open_player_ids.discard(player_id)
        self._clear_result_if_no_end_screens_remain()

    def _prune_end_screen_state(self) -> None:
        """Drop post-game overlay ids that no longer belong to this game."""
        self._ensure_end_screen_state()
        valid_player_ids = {player.id for player in self.players}
        self._end_screen_open_player_ids.intersection_update(valid_player_ids)
        self._clear_result_if_no_end_screens_remain()

    def _restore_end_screen_if_open(self, player: "Player") -> bool:
        """Repaint the player's own end screen and block unrelated menu refreshes."""
        if not self._is_end_screen_open_for_player(player):
            user = self.get_user(player)
            if user:
                self._clear_end_screen_server_state(user)
            return False
        result = self._last_game_result
        if result is None:
            self._discard_end_screen_player_id(player.id)
            user = self.get_user(player)
            if user:
                self._clear_end_screen_server_state(user)
            return False
        self._show_end_screen_to_player(player, result, mark_open=False)
        return True

    def _dismiss_end_screen_for_player(self, player: "Player") -> None:
        """Dismiss only one player's post-game screen."""
        self._discard_end_screen_player_id(player.id)
        user = self.get_user(player)
        if user:
            # A replacement lobby/confirmation menu follows in the same
            # framework event. Remove the stored snapshot quietly so clients
            # never receive an empty intermediary menu that can drop focus.
            user.remove_menu("game_over", send_packet=False)
            self._clear_end_screen_server_state(user)

    def _dismiss_all_end_screens(self) -> None:
        """Dismiss every active post-game screen, used when a new game starts."""
        self._ensure_end_screen_state()
        open_player_ids = list(self._end_screen_open_player_ids)
        self._end_screen_open_player_ids.clear()
        self._last_game_result = None
        for player_id in open_player_ids:
            player = self.get_player_by_id(player_id)
            user = self.get_user(player) if player else None
            if user:
                # A pending result may never have been painted because the
                # player was using a global surface. Clearing it must therefore
                # be silent; the new game's authoritative menu follows.
                user.remove_menu("game_over", send_packet=False)
                self._clear_end_screen_server_state(user)

    def _export_end_screen_state(self) -> dict[str, Any]:
        """Return runtime end-screen state for transfer to a fresh lobby game."""
        self._prune_end_screen_state()
        return {
            "result": self._last_game_result,
            "open_player_ids": set(self._end_screen_open_player_ids),
        }

    def _import_end_screen_state(self, state: dict[str, Any] | None) -> None:
        """Import runtime end-screen state after the table creates a fresh game."""
        self._ensure_end_screen_state()
        if not state:
            self._last_game_result = None
            self._end_screen_open_player_ids.clear()
            return
        self._last_game_result = state.get("result")
        if self._last_game_result is None:
            self._end_screen_open_player_ids.clear()
            return
        self._end_screen_open_player_ids = set(state.get("open_player_ids", set()))
        self._prune_end_screen_state()

