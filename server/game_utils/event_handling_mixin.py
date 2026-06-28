"""Mixin providing event handling for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player

from .action_context import ActionContext


class EventHandlingMixin:
    """Mixin providing event handling (menu, editbox, keybind events).

    Expects on the Game class:
        - self._actions_menu_open: set[str]
        - self._pending_actions: dict[str, str]
        - self._status_box_open: set[str]
        - self._live_status_boxes: dict[str, LiveStatusBoxState]
        - self._keybinds: dict[str, list[Keybind]]
        - self.get_user(player) -> User | None
        - self.find_action(player, action_id) -> Action | None
        - self.resolve_action(player, action) -> ResolvedAction
        - self.execute_action(player, action_id, input_value?, context?)
        - self.get_all_visible_actions(player) -> list[ResolvedAction]
        - self.refresh_menus(player?), self.flush_menus()
        - self._is_player_spectator(player) -> bool
    """

    def handle_event(self, player: "Player", event: dict) -> None:
        """Handle an event from a player.

        This is the single entry point for player-driven events, so it ends
        with the framework menu flush: every menu refresh recorded while
        handling the event is built and sent here, synchronously with the
        event. (Refreshes recorded outside an event — bots, sequences,
        timers — are flushed once per server tick instead.)
        """
        event_type = event.get("type")

        if event_type == "menu":
            self._handle_menu_event(player, event)

        elif event_type == "escape":
            self._handle_menu_event(
                player,
                {**event, "type": "menu", "selection_id": "back"},
            )

        elif event_type == "editbox":
            self._handle_editbox_event(player, event)

        elif event_type == "keybind":
            self._handle_keybind_event(player, event)

        elif event_type == "action":
            self._handle_action_event(player, event)

        self.flush_menus()

    def _handle_action_event(self, player: "Player", event: dict) -> None:
        """Handle a direct action execution event."""
        action_id = event.get("action")
        if not action_id:
            return

        # Check if action is available (can verify existence)
        action = self.find_action(player, action_id)
        if not action:
            return

        # Extract context
        context_data = event.get("context", {})
        menu_item_id = context_data.get("menu_item_id")
        
        context = ActionContext(
            menu_item_id=menu_item_id,
            # We could add more context if needed
        )

        resolved = self.resolve_action(player, action)
        if resolved.enabled:
            self.execute_action(player, action_id, context=context)
            if player.id not in self._pending_actions:
                self.refresh_menus()
        elif resolved.disabled_reason:
            self._speak_action_disabled_reason(player, resolved.disabled_reason)

    def _handle_menu_event(self, player: "Player", event: dict) -> None:
        """Handle a menu selection event."""
        menu_id = event.get("menu_id")
        selection_id = event.get("selection_id", "")
        


        if menu_id == "turn_menu":
            # WEB-SPECIFIC: Intercept specific button IDs
            if selection_id == "web_actions_menu":
                self.execute_action(
                    player,
                    "show_actions",
                    context=ActionContext(menu_item_id="web_actions_menu"),
                )
                return
            elif selection_id == "web_leave_table":
                self.execute_action(
                    player,
                    "leave_game",
                    context=ActionContext(menu_item_id="web_leave_table"),
                )
                return

            # If interacting with turn_menu, actions menu is no longer open
            self._actions_menu_open.discard(player.id)
            self._actions_menu_return_focus.pop(player.id, None)
            # Try by ID first, then by index
            action = (
                self.find_action(player, selection_id) if selection_id else None
            )
            if action:
                resolved = self.resolve_action(player, action)
                if resolved.enabled:
                    self.execute_action(
                        player,
                        selection_id,
                        context=ActionContext(menu_item_id=selection_id),
                    )
                    if player.id not in self._pending_actions:
                        self.refresh_menus()
                elif resolved.disabled_reason:
                    self._speak_action_disabled_reason(player, resolved.disabled_reason)
            else:
                # Fallback to index-based selection - use visible actions only
                selection = event.get("selection", 1) - 1  # Convert to 0-based
                visible = self.get_all_visible_actions(player)
                if 0 <= selection < len(visible):
                    resolved = visible[selection]
                    self.execute_action(
                        player,
                        resolved.action.id,
                        context=ActionContext(menu_item_id=resolved.action.id),
                    )
                    if player.id not in self._pending_actions:
                        self.refresh_menus()

        elif menu_id == "actions_menu":
            # Actions menu - use selection_id directly
            if selection_id:
                self._handle_actions_menu_selection(player, selection_id)

        elif menu_id == "status_box":
            user = self.get_user(player)
            if user:
                user.remove_menu("status_box")
                user.speak_l("status-box-closed", buffer="game")
                self._status_box_open.discard(player.id)
                self._live_status_boxes.pop(player.id, None)
                focus = self._status_box_return_focus.pop(player.id, None)
                if focus:
                    self.request_menu_focus(player, focus)
                else:
                    self.refresh_menus(player)

        elif menu_id == "game_over":
            # Handle the local post-game overlay. After a normal finish, `self`
            # is the fresh lobby game, so end-screen state is tracked per player.
            dismiss = getattr(self, "_dismiss_end_screen_for_player", None)
            if selection_id in ("return_to_table", "return_to_lobby"):
                if dismiss:
                    dismiss(player)
                self.refresh_menus(player)
            elif selection_id == "leave_game":
                if dismiss:
                    dismiss(player)
                self.execute_action(player, "leave_game")
            else:
                return

        elif menu_id == "action_input_menu":
            # Handle action input menu selection
            cancelled = selection_id in ("_cancel", "back")
            return_focus = None
            if player.id in self._pending_actions:
                action_id = self._pending_actions.pop(player.id)
                return_focus = self._pending_action_return_focus.pop(player.id, None)
                if cancelled:
                    cancel_hook = getattr(self, "_on_action_input_cancelled", None)
                    if cancel_hook:
                        cancel_hook(player, action_id)
                else:
                    # Execute the action with the selected input
                    context = (
                        ActionContext(menu_item_id=return_focus)
                        if return_focus
                        else None
                    )
                    self.execute_action(
                        player,
                        action_id,
                        selection_id,
                        context=context,
                    )
            if cancelled and return_focus:
                self.request_menu_focus(player, return_focus)
            else:
                self.refresh_menus(player)
        elif menu_id == "action_input_editbox":
            self._pending_actions.pop(player.id, None)
            focus = self._pending_action_return_focus.pop(player.id, None)
            if focus:
                self.request_menu_focus(player, focus)
            else:
                self.refresh_menus(player)
        elif menu_id == "leave_game_confirm":
            user = self.get_user(player)
            if user:
                user.remove_menu("leave_game_confirm")
            if player.id in self._pending_actions:
                self._pending_actions.pop(player.id, None)
            return_focus = self._pending_action_return_focus.pop(player.id, None)
            choice = selection_id
            if not choice:
                selection = event.get("selection", 1) - 1
                choice = "yes" if selection == 0 else "no"
            if choice == "yes":
                handler = getattr(self, "_perform_leave_game", None)
                if handler:
                    handler(player)
            elif return_focus:
                self.request_menu_focus(player, return_focus)
            else:
                self.refresh_menus(player)

    def _handle_editbox_event(self, player: "Player", event: dict) -> None:
        """Handle an editbox submission event."""
        input_id = event.get("input_id", "")
        text = event.get("text", "")

        if input_id == "action_input_editbox":
            # Handle action input editbox submission
            if player.id in self._pending_actions:
                action_id = self._pending_actions.pop(player.id)
                return_focus = self._pending_action_return_focus.pop(player.id, None)
                if text and not event.get("cancelled") and not event.get("cancel"):
                    context = (
                        ActionContext(menu_item_id=return_focus)
                        if return_focus
                        else None
                    )
                    self.execute_action(player, action_id, text, context=context)
                elif return_focus:
                    self.request_menu_focus(player, return_focus)
                    return
            self.refresh_menus(player)

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

        # In the lobby/options menu, space speaks the focused option's
        # description (when one exists) instead of acting as a game keybind.
        if (
            key == "space"
            and getattr(self, "status", "playing") != "playing"
            and menu_item_id
        ):
            handler = getattr(self, "_speak_option_description", None)
            if handler and handler(player, menu_item_id):
                return

        # Look up keybinds for this key
        keybinds = self._keybinds.get(key)
        if keybinds is None:
            return

        # Check if player is a spectator
        is_spectator = self._is_player_spectator(player)

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
                        self._actions_menu_open.discard(player.id)
                        self._actions_menu_return_focus.pop(player.id, None)
                        self.execute_action(player, action_id, context=context)
                        executed_any = True
                    elif resolved.disabled_reason:
                        self._speak_action_disabled_reason(player, resolved.disabled_reason)

        # Any executed action may have changed shared state; mark everyone
        # except when the action opened a pending input flow. Pending inputs
        # already refresh the acting player explicitly, and the flush guards
        # (status box, actions menu, system overlays) protect each player
        # individually at paint time.
        if executed_any:
            if player.id not in self._pending_actions:
                self.refresh_menus()

    def _handle_actions_menu_selection(self, player: "Player", action_id: str) -> None:
        """Handle selection from the actions menu."""
        # Actions menu is no longer open
        self._actions_menu_open.discard(player.id)
        return_focus = self._actions_menu_return_focus.pop(player.id, None)
        # Handle "go back" - just return to turn menu
        if action_id == "go_back":
            if return_focus:
                self.request_menu_focus(player, return_focus)
            else:
                self.refresh_menus(player)
            return
        action = self.find_action(player, action_id)
        if action:
            resolved = self.resolve_action(player, action)
            if resolved.enabled:
                self.execute_action(
                    player,
                    action_id,
                    context=ActionContext(menu_item_id=return_focus or action_id),
                )
            elif resolved.disabled_reason:
                self._speak_action_disabled_reason(player, resolved.disabled_reason)
        user = self.get_user(player)
        if (
            return_focus
            and user is not None
            and not self._destroyed
            and player.id not in self._pending_actions
            and player.id not in self._status_box_open
            and player.id not in self._pending_menu_focus
            and not self._is_menu_refresh_blocked(player, user)
        ):
            self.request_menu_focus(player, return_focus)
        else:
            self.refresh_menus(player)
