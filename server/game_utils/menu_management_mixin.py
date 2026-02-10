"""Mixin providing menu management functionality for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User
    from .actions import ResolvedAction

from ..users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization


class MenuManagementMixin:
    """Mixin providing menu rebuilding and status box functionality.

    Expects on the Game class:
        - self._destroyed: bool
        - self.status: str
        - self.players: list[Player]
        - self._status_box_open: set[str]
        - self.get_user(player) -> User | None
        - self.get_all_visible_actions(player) -> list[ResolvedAction]
    """

    def rebuild_player_menu(self, player: "Player") -> None:
        """Rebuild the turn menu for a player."""
        if self._destroyed:
            return  # Don't rebuild menus after game is destroyed
            
        if self.status == "finished":
            # BUGFIX: If game is finished, we should restore the end screen
            # instead of doing nothing (which leaves user with no menu)
            
            # Robustness: If _last_game_result is missing (e.g. after server restart),
            # try to rebuild it from current state.
            if not hasattr(self, "_last_game_result") or self._last_game_result is None:
                if hasattr(self, "build_game_result"):
                    self._last_game_result = self.build_game_result()

            if hasattr(self, "_last_game_result") and self._last_game_result:
                # We need to access _show_end_screen_to_player from GameResultMixin
                # Since Game inherits from both, this is valid
                if hasattr(self, "_show_end_screen_to_player"):
                    self._show_end_screen_to_player(player, self._last_game_result)
            return

        user = self.get_user(player)
        if not user:
            return

        items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            items.append(MenuItem(text=resolved.label, id=resolved.action.id))

        # WEB-SPECIFIC: Add static control buttons
        client_type = getattr(user, "client_type", None)
        if client_type == "web":
            # 1. Actions Menu / Context Menu (Top Left)
            items.append(MenuItem(
                text=Localization.get(user.locale, "actions-menu"),
                id="web_actions_menu"
            ))
            # 2. Leave Table (Bottom Right)
            items.append(MenuItem(
                text=Localization.get(user.locale, "game-leave"), # Use "game-leave" ("Leave" or "Leave table") 
                id="web_leave_table"
            ))

        user.show_menu(
            "turn_menu",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
        )

    def rebuild_all_menus(self) -> None:
        """Rebuild menus for all players."""
        if self._destroyed:
            return  # Don't rebuild menus after game is destroyed
        for player in self.players:
            self.rebuild_player_menu(player)

    def update_player_menu(
        self, player: "Player", selection_id: str | None = None
    ) -> None:
        """Update the turn menu for a player, preserving focus position."""
        if self._destroyed:
            return
        if self.status == "finished":
            return
        user = self.get_user(player)
        if not user:
            return

        items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            items.append(MenuItem(text=resolved.label, id=resolved.action.id))
            
        # WEB-SPECIFIC: Add static control buttons
        if user.client_type == "web":
            # 1. Actions Menu / Context Menu (Top Left)
            items.append(MenuItem(
                text=Localization.get(user.locale, "actions-menu"),
                id="web_actions_menu"
            ))
            # 2. Leave Table (Bottom Right)
            items.append(MenuItem(
                text=Localization.get(user.locale, "game-leave"),
                id="web_leave_table"
            ))

        user.update_menu("turn_menu", items, selection_id=selection_id)

    def update_all_menus(self) -> None:
        """Update menus for all players, preserving focus position."""
        if self._destroyed:
            return
        for player in self.players:
            self.update_player_menu(player)

    def status_box(self, player: "Player", lines: list[str]) -> None:
        """Show a status box (menu with text items) to a player.

        Press Enter on any item to close. No header or close button needed
        since screen readers speak list items and Enter always closes.
        """
        user = self.get_user(player)
        if user:
            items = [MenuItem(text=line, id="status_line") for line in lines]
            user.show_menu(
                "status_box",
                items,
                multiletter=False,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
            self._status_box_open.add(player.id)
