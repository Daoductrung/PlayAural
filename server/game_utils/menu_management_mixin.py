"""Mixin providing menu management functionality for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User
    from .actions import ResolvedAction

from ..users.base import MenuItem, EscapeBehavior


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
            return  # Don't rebuild turn menu after game has ended
        user = self.get_user(player)
        if not user:
            return

        items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            items.append(MenuItem(text=resolved.label, id=resolved.action.id))

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
