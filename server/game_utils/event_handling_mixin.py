"""Mixin providing event handling for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player, ActionContext


class EventHandlingMixin:
    """Mixin providing event handling (menu, editbox, keybind events).

    Expects on the Game class:
        - self._actions_menu_open: set[str]
        - self._pending_actions: dict[str, str]
        - self._status_box_open: set[str]
        - self._keybinds: dict[str, list[Keybind]]
        - self.get_user(player) -> User | None
        - self.find_action(player, action_id) -> Action | None
        - self.resolve_action(player, action) -> ResolvedAction
        - self.execute_action(player, action_id, input_value?, context?)
        - self.get_all_visible_actions(player) -> list[ResolvedAction]
        - self.rebuild_player_menu(player)
        - self.rebuild_all_menus()
        - self._is_player_spectator(player) -> bool
    """

    def handle_event(self, player: "Player", event: dict) -> None:
        """Handle an event from a player."""
        event_type = event.get("type")

        if event_type == "menu":
            self._handle_menu_event(player, event)

        elif event_type == "editbox":
            self._handle_editbox_event(player, event)

        elif event_type == "keybind":
            self._handle_keybind_event(player, event)

    def _handle_menu_event(self, player: "Player", event: dict) -> None:
        """Handle a menu selection event."""
        menu_id = event.get("menu_id")
        selection_id = event.get("selection_id", "")

        if menu_id == "turn_menu":
            # If interacting with turn_menu, actions menu is no longer open
            self._actions_menu_open.discard(player.id)
            # Try by ID first, then by index
            action = (
                self.find_action(player, selection_id) if selection_id else None
            )
            if action:
                resolved = self.resolve_action(player, action)
                if resolved.enabled:
                    self.execute_action(player, selection_id)
                    # Don't rebuild if action is waiting for input
                    if player.id not in self._pending_actions:
                        self.rebuild_all_menus()
            else:
                # Fallback to index-based selection - use visible actions only
                selection = event.get("selection", 1) - 1  # Convert to 0-based
                visible = self.get_all_visible_actions(player)
                if 0 <= selection < len(visible):
                    resolved = visible[selection]
                    self.execute_action(player, resolved.action.id)
                    # Don't rebuild if action is waiting for input
                    if player.id not in self._pending_actions:
                        self.rebuild_all_menus()

        elif menu_id == "actions_menu":
            # Actions menu - use selection_id directly
            if selection_id:
                self._handle_actions_menu_selection(player, selection_id)

        elif menu_id == "status_box":
            user = self.get_user(player)
            if user:
                user.remove_menu("status_box")
                user.speak_l("status-box-closed")
                self._status_box_open.discard(player.id)
                self.rebuild_player_menu(player)

        elif menu_id == "game_over":
            # Handle game over menu - leave_game is the only selectable action
            # It's always the last item
            if selection_id == "leave_game":
                self.execute_action(player, "leave_game")
            else:
                # Index-based - any selection triggers leave
                self.execute_action(player, "leave_game")

        elif menu_id == "action_input_menu":
            # Handle action input menu selection
            if player.id in self._pending_actions:
                action_id = self._pending_actions.pop(player.id)
                if selection_id != "_cancel":
                    # Execute the action with the selected input
                    self.execute_action(player, action_id, selection_id)
            self.rebuild_player_menu(player)
        elif menu_id == "leave_game_confirm":
            user = self.get_user(player)
            if user:
                user.remove_menu("leave_game_confirm")
            if player.id in self._pending_actions:
                self._pending_actions.pop(player.id, None)
            choice = selection_id
            if not choice:
                selection = event.get("selection", 1) - 1
                choice = "yes" if selection == 0 else "no"
            if choice == "yes":
                handler = getattr(self, "_perform_leave_game", None)
                if handler:
                    handler(player)
            self.rebuild_player_menu(player)

    def _handle_editbox_event(self, player: "Player", event: dict) -> None:
        """Handle an editbox submission event."""
        input_id = event.get("input_id", "")
        text = event.get("text", "")

        if input_id == "action_input_editbox":
            # Handle action input editbox submission
            if player.id in self._pending_actions:
                action_id = self._pending_actions.pop(player.id)
                if text:  # Non-empty input
                    self.execute_action(player, action_id, text)
            self.rebuild_player_menu(player)

    def _handle_keybind_event(self, player: "Player", event: dict) -> None:
        """Handle a keybind press event."""
        key = event.get("key", "").lower()  # Normalize to lowercase
        menu_item_id = event.get("menu_item_id")
        menu_index = event.get("menu_index")

        # Handle modifiers - reconstruct full key string
        if event.get("shift") and not key.startswith("shift+"):
            key = f"shift+{key}"
        if event.get("control") and not key.startswith("ctrl+"):
            key = f"ctrl+{key}"
        if event.get("alt") and not key.startswith("alt+"):
            key = f"alt+{key}"

        # Look up keybinds for this key
        keybinds = self._keybinds.get(key)
        if keybinds is None:
            return

        # Check if player is a spectator
        is_spectator = self._is_player_spectator(player)

        # Import here to avoid circular dependency at module level
        from ..games.base import ActionContext

        # Build context for action handlers
        context = ActionContext(
            menu_item_id=menu_item_id,
            menu_index=menu_index,
            from_keybind=True,
        )

        # Try each keybind for this key (allows same key for different states)
        executed_any = False
        for keybind in keybinds:
            # Check if keybind can be used by this player in current state
            if not keybind.can_player_use(self, player, is_spectator):
                continue

            # Check focus requirement
            if keybind.requires_focus and menu_item_id not in keybind.actions:
                continue

            # Execute all enabled actions in the keybind
            for action_id in keybind.actions:
                action = self.find_action(player, action_id)
                if action:
                    resolved = self.resolve_action(player, action)
                    if resolved.enabled:
                        self.execute_action(player, action_id, context=context)
                        executed_any = True
                    elif resolved.disabled_reason:
                        if resolved.disabled_reason != "action-not-available":
                            # Speak the disabled reason to the player
                            user = self.get_user(player)
                            if user:
                                user.speak_l(resolved.disabled_reason)

        # Don't rebuild if action is waiting for input, status box is open, or actions menu is open
        if (
            executed_any
            and player.id not in self._pending_actions
            and player.id not in self._status_box_open
            and player.id not in self._actions_menu_open
        ):
            self.rebuild_all_menus()

    def _handle_actions_menu_selection(self, player: "Player", action_id: str) -> None:
        """Handle selection from the actions menu."""
        # Actions menu is no longer open
        self._actions_menu_open.discard(player.id)
        # Handle "go back" - just return to turn menu
        if action_id == "go_back":
            self.rebuild_player_menu(player)
            return
        action = self.find_action(player, action_id)
        if action:
            resolved = self.resolve_action(player, action)
            if resolved.enabled:
                self.execute_action(player, action_id)
        # Don't rebuild if action is waiting for input
        if player.id not in self._pending_actions:
            self.rebuild_player_menu(player)
