"""Mixin providing action execution for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player

from .action_context import ActionContext
from .actions import Action, MenuInput, EditboxInput
from .options import get_option_meta, MenuOption
from ..users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization


class ActionExecutionMixin:
    """Mixin providing action execution and input handling.

    Expects on the Game class:
        - self._pending_actions: dict[str, str]
        - self._action_context: dict[str, ActionContext]
        - self.get_user(player) -> User | None
        - self.find_action(player, action_id) -> Action | None
        - self.resolve_action(player, action) -> ResolvedAction
        - self.advance_turn()
    """

    def execute_action(
        self,
        player: "Player",
        action_id: str,
        input_value: str | None = None,
        context: "ActionContext | None" = None,
    ) -> None:
        """Execute an action for a player, optionally with input value and context."""
        if not player.is_bot and getattr(player, "reconnect_grace_ticks", 0) > 0:
            return

        action = self.find_action(player, action_id)
        if not action:
            return

        # Defense-in-depth: block spectators from executing player-only actions,
        # regardless of how the request arrived (menu click, keybind, direct event).
        if player.is_spectator and not action.include_spectators:
            return

        # Check if action is enabled using declarative callback
        resolved = self.resolve_action(player, action)
        if not resolved.enabled:
            # Speak the reason to the player unless it's a silent block.
            self._speak_action_disabled_reason(player, resolved.disabled_reason)
            return

        # Store context for handlers that need it (e.g., keybind-triggered actions)
        self._action_context[player.id] = context or ActionContext()

        try:
            # If action requires input and we don't have it yet
            if action.input_request is not None and input_value is None:
                # For bots, get input automatically
                if player.is_bot:
                    # Set pending action so options methods can access action_id
                    self._pending_actions[player.id] = action_id
                    input_value = self._get_bot_input(action, player)
                    # Clean up pending action for bot
                    if player.id in self._pending_actions:
                        del self._pending_actions[player.id]
                    if input_value is None:
                        return  # Bot couldn't provide input
                else:
                    if not self._should_prompt_for_action_input(action, player):
                        input_value = self._get_default_action_input(action, player)
                    else:
                        # For humans, request input and store pending action
                        self._request_action_input(action, player)
                        return

            # Look up the handler method by name on this game object
            handler = getattr(self, action.handler, None)
            if not handler:
                return

            # Execute the action handler (always pass action_id for context)
            if action.input_request is not None and input_value is not None:
                # Handler expects input value: (player, input_value, action_id)
                handler(player, input_value, action_id)
            else:
                # Handler doesn't expect input: (player, action_id)
                handler(player, action_id)
        finally:
            # Clean up context
            self._action_context.pop(player.id, None)

    def _speak_action_disabled_reason(self, player: "Player", reason) -> None:
        """Speak a disabled-action reason, including parameterized locale keys."""
        if not reason or reason == "action-not-available":
            return
        user = self.get_user(player)
        if not user:
            return
        if isinstance(reason, tuple):
            key, kwargs = reason
            user.speak_l(key, buffer="game", **kwargs)
        else:
            user.speak_l(reason, buffer="game")

    def _should_prompt_for_action_input(
        self, action: Action, player: "Player"
    ) -> bool:
        """Return whether a human player should be prompted for action input."""
        req = action.input_request
        if isinstance(req, EditboxInput):
            should_prompt = req.should_prompt or f"_should_prompt_{action.id}"
            method = getattr(self, should_prompt, None)
            if method:
                return bool(method(player))
        return True

    def _get_default_action_input(
        self, action: Action, player: "Player"
    ) -> str | None:
        """Return default input for a human action when prompting is skipped."""
        req = action.input_request
        if isinstance(req, EditboxInput):
            return req.default
        if isinstance(req, MenuInput):
            options = self._get_menu_options_for_action(action, player)
            if options:
                return options[0]
        return None

    def get_action_context(self, player: "Player") -> "ActionContext":
        """Get the current action context for a player (for use in handlers)."""
        return self._action_context.get(player.id, ActionContext())

    def _get_action_return_focus_id(
        self, player: "Player", fallback_action_id: str | None
    ) -> str | None:
        """Return the menu item that should receive focus after an overlay closes."""
        context = self.get_action_context(player)
        return context.menu_item_id or fallback_action_id

    def _get_menu_options_for_action(
        self, action: Action, player: "Player"
    ) -> list[str] | None:
        """Get menu options for an action, checking method first then MenuOption metadata."""
        req = action.input_request
        if not isinstance(req, MenuInput):
            return None

        # First try the method name
        options_method = getattr(self, req.options, None)
        if options_method:
            return options_method(player)

        # Fallback: check if this is a set_* action for a MenuOption
        if action.id.startswith("set_") and hasattr(self, "options"):
            option_name = action.id[4:]  # Remove "set_" prefix
            meta = get_option_meta(type(self.options), option_name)
            if meta and isinstance(meta, MenuOption):
                choices = meta.choices
                # Choices can be a list or a callable
                if callable(choices):
                    return choices(self, player)
                return list(choices)

        return None

    def _get_bot_input(self, action: Action, player: "Player") -> str | None:
        """Get automatic input for a bot player."""
        req = action.input_request
        if isinstance(req, MenuInput):
            options = self._get_menu_options_for_action(action, player)
            if not options:
                return None
            if req.bot_select:
                # Look up bot_select method by name
                bot_select_method = getattr(self, req.bot_select, None)
                if bot_select_method:
                    return bot_select_method(player, options)
            # Default: pick first option
            return options[0]
        elif isinstance(req, EditboxInput):
            if req.bot_input:
                # Look up bot_input method by name
                bot_input_method = getattr(self, req.bot_input, None)
                if bot_input_method:
                    return bot_input_method(player)
            # Default: use default value
            return req.default
        return None

    def _gameplay_input_lock_owner(
        self,
        *,
        exclude_player_id: str | None = None,
    ) -> "Player | None":
        """Return the active player whose declarative input locks gameplay.

        Pending inputs are runtime-only UI intent. Games with interruptible
        public state can consult this helper from their actor/permission checks
        instead of coupling gameplay locks to a particular action id.
        """

        for candidate in self.get_active_players():
            if candidate.id == exclude_player_id:
                continue
            action_id = self._pending_actions.get(candidate.id)
            action = self.find_action(candidate, action_id) if action_id else None
            request = action.input_request if action else None
            if isinstance(request, MenuInput) and request.locks_gameplay:
                return candidate
        return None

    def _paint_action_menu_input(
        self,
        action: Action,
        player: "Player",
        *,
        apply_initial_selection: bool,
    ) -> bool:
        """Paint a menu input from current authoritative options and labels."""

        user = self.get_user(player)
        request = action.input_request
        if not user or not isinstance(request, MenuInput):
            return False

        options = self._get_menu_options_for_action(action, player)
        if not options:
            return False

        items = self._build_action_menu_input_items(
            action,
            player,
            user,
            options,
        )
        if not items:
            return False

        selection_id = None
        if apply_initial_selection and request.initial_selection:
            initial_selection_method = getattr(
                self,
                request.initial_selection,
                None,
            )
            if initial_selection_method:
                selection_id = initial_selection_method(player, options)
                if selection_id not in options:
                    selection_id = None

        user.show_menu(
            "action_input_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            selection_id=selection_id,
        )
        return True

    def _build_action_menu_input_items(
        self,
        action: Action,
        player: "Player",
        user,
        options: list[str],
    ) -> list[MenuItem]:
        """Build the current rows for a declarative menu input.

        Games with a specialized input surface may override this idempotent
        builder. One-time announcements and sounds belong in
        ``_on_action_menu_input_opened`` so passive refreshes remain silent.
        """

        request = action.input_request
        if not isinstance(request, MenuInput):
            return []

        menu_option_meta = None
        if action.id.startswith("set_") and hasattr(self, "options"):
            option_name = action.id[4:]
            meta = get_option_meta(type(self.options), option_name)
            if meta and isinstance(meta, MenuOption):
                menu_option_meta = meta

        option_label_method = (
            getattr(self, request.option_label, None)
            if request.option_label
            else None
        )
        option_description_method = (
            getattr(self, request.option_description, None)
            if request.option_description
            else None
        )
        items = []
        for option in options:
            if menu_option_meta:
                display_text = menu_option_meta.get_localized_choice(
                    option,
                    user.locale,
                )
            elif option_label_method:
                display_text = option_label_method(player, option)
            else:
                display_text = option
            description = (
                option_description_method(player, option)
                if option_description_method
                else None
            )
            items.append(
                MenuItem(
                    text=display_text,
                    id=option,
                    description=description,
                )
            )

        items.append(
            MenuItem(text=Localization.get(user.locale, "cancel"), id="_cancel")
        )
        return items

    def _on_action_menu_input_opened(
        self,
        action: Action,
        player: "Player",
    ) -> None:
        """Run one-time output after a menu input is opened successfully."""

    def _on_action_input_cancelled(
        self,
        player: "Player",
        action_id: str,
    ) -> None:
        """Clean game-owned draft state when an action input is dismissed."""

    def _request_action_input(self, action: Action, player: "Player") -> None:
        """Request input from a human player for an action."""
        user = self.get_user(player)
        if not user:
            return

        req = action.input_request
        if isinstance(req, MenuInput) and req.pre_input_check:
            pre_input_check = getattr(self, req.pre_input_check, None)
            if pre_input_check:
                disabled_reason = pre_input_check(player, action.id)
                if disabled_reason:
                    self._speak_action_disabled_reason(player, disabled_reason)
                    return
        self._pending_actions[player.id] = action.id
        return_focus = self._get_action_return_focus_id(player, action.id)
        if return_focus:
            self._pending_action_return_focus[player.id] = return_focus

        if isinstance(req, MenuInput):
            if not self._paint_action_menu_input(
                action,
                player,
                apply_initial_selection=True,
            ):
                # No options available
                del self._pending_actions[player.id]
                self._pending_action_return_focus.pop(player.id, None)
                user.speak_l("no-options-available", buffer="game")
                return
            self._on_action_menu_input_opened(action, player)
            self._consume_refresh_for_direct_menu_overlay(player)
            if req.locks_gameplay:
                for other in self.get_active_players():
                    if other.id != player.id:
                        self.refresh_menus(other)

        elif isinstance(req, EditboxInput):
            # Show editbox for text input
            prompt = Localization.get(user.locale, req.prompt)
            user.show_editbox("action_input_editbox", prompt, req.default)

    def end_turn(self) -> None:
        """End the current player's turn. Call this from action handlers."""
        # Default behavior - can be overridden by games
        self.advance_turn()
