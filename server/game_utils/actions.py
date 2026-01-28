"""Action system for games - declarative callbacks for state management."""

import copy
import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

if TYPE_CHECKING:
    from ..games.base import Game, Player


class Visibility(str, Enum):
    """Visibility state for actions."""

    VISIBLE = "visible"
    HIDDEN = "hidden"


@dataclass
class MenuInput(DataClassJSONMixin):
    """
    Request menu selection before action executes.

    The options and bot_select are method names (strings) that will be
    looked up on the game object at execution time.
    """

    prompt: str  # Localization key for menu title/prompt
    options: str  # Method name that returns list[str]
    bot_select: str | None = None  # Method name for bot auto-selection


@dataclass
class EditboxInput(DataClassJSONMixin):
    """
    Request text input before action executes.

    The bot_input is a method name (string) that will be looked up
    on the game object at execution time.
    """

    prompt: str  # Localization key for prompt
    default: str = ""  # Default value (static string only now)
    bot_input: str | None = None  # Method name for bot auto-input


@dataclass
class Action(DataClassJSONMixin):
    """
    A game action with declarative state callbacks.

    All callback fields are method names (strings) for serialization.
    Methods are looked up on the game object at resolution time.

    Callback signatures:
    - handler: (self, player, action_id) or (self, player, input_value, action_id)
    - is_enabled: (self, player, *, action_id: str = None) -> str | None
      Returns None if enabled, or a localization key (disabled reason) if disabled.
      The action_id kwarg is optional and passed if the method signature accepts it.
    - is_hidden: (self, player, *, action_id: str = None) -> Visibility
      Returns Visibility.VISIBLE or Visibility.HIDDEN.
      The action_id kwarg is optional and passed if the method signature accepts it.
    - get_label: (self, player, action_id) -> str
      Returns the dynamic label string.
    """

    id: str
    label: str  # Static label (fallback if no get_label)
    handler: str  # Method name on game object (e.g., "_action_roll")
    is_enabled: str  # Method name (e.g., "_is_roll_enabled")
    is_hidden: str  # Method name (e.g., "_is_roll_hidden")
    get_label: str | None = None  # Optional method name (e.g., "_get_roll_label")
    input_request: MenuInput | EditboxInput | None = None
    show_in_actions_menu: bool = True


@dataclass
class ResolvedAction:
    """
    An action with its state resolved for a specific player.

    This is the result of calling the declarative callbacks.
    Not serialized - created fresh when building menus.
    """

    action: Action
    label: str
    enabled: bool
    disabled_reason: str | None  # Localization key if disabled, None if enabled
    visible: bool


@dataclass
class ActionSet(DataClassJSONMixin):
    """
    A named group of actions for a player.

    Players have an ordered list of ActionSets (e.g., "turn" before "lobby").
    Action state is resolved declaratively via callbacks when building menus.
    """

    name: str  # e.g., "turn", "lobby", "hand"
    _actions: dict[str, Action] = field(default_factory=dict)
    _order: list[str] = field(default_factory=list)

    def add(self, action: Action) -> None:
        """Add an action to this set."""
        self._actions[action.id] = action
        if action.id not in self._order:
            self._order.append(action.id)

    def remove(self, action_id: str) -> None:
        """Remove an action from this set."""
        if action_id in self._actions:
            del self._actions[action_id]
        if action_id in self._order:
            self._order.remove(action_id)

    def remove_by_prefix(self, prefix: str) -> None:
        """Remove all actions whose ID starts with the given prefix."""
        to_remove = [aid for aid in self._actions if aid.startswith(prefix)]
        for aid in to_remove:
            self.remove(aid)

    def get_action(self, action_id: str) -> Action | None:
        """Get an action by ID."""
        return self._actions.get(action_id)

    def resolve_action(
        self, game: "Game", player: "Player", action: Action
    ) -> ResolvedAction:
        """Resolve a single action's state for a player."""
        # Resolve enabled state
        disabled_reason: str | None = None
        if action.is_enabled:
            method = getattr(game, action.is_enabled, None)
            if method:
                # Check if method accepts action_id kwarg
                sig = inspect.signature(method)
                if 'action_id' in sig.parameters:
                    disabled_reason = method(player, action_id=action.id)
                else:
                    disabled_reason = method(player)

        # Resolve visibility
        visible = True
        if action.is_hidden:
            method = getattr(game, action.is_hidden, None)
            if method:
                # Check if method accepts action_id kwarg
                sig = inspect.signature(method)
                if 'action_id' in sig.parameters:
                    visibility = method(player, action_id=action.id)
                else:
                    visibility = method(player)
                visible = visibility == Visibility.VISIBLE

        # Resolve label
        label = action.label
        if action.get_label:
            method = getattr(game, action.get_label, None)
            if method:
                label = method(player, action.id)

        return ResolvedAction(
            action=action,
            label=label,
            enabled=disabled_reason is None,
            disabled_reason=disabled_reason,
            visible=visible,
        )

    def resolve_actions(
        self, game: "Game", player: "Player"
    ) -> list[ResolvedAction]:
        """Resolve all actions' states for a player."""
        result = []
        for aid in self._order:
            if aid not in self._actions:
                continue
            action = self._actions[aid]
            resolved = self.resolve_action(game, player, action)
            result.append(resolved)
        return result

    def get_visible_actions(
        self, game: "Game", player: "Player"
    ) -> list[ResolvedAction]:
        """Get enabled, visible actions for the turn menu."""
        return [
            ra
            for ra in self.resolve_actions(game, player)
            if ra.enabled and ra.visible
        ]

    def get_enabled_actions(
        self, game: "Game", player: "Player"
    ) -> list[ResolvedAction]:
        """Get all enabled actions for the actions menu (includes hidden)."""
        return [
            ra
            for ra in self.resolve_actions(game, player)
            if ra.enabled and ra.action.show_in_actions_menu
        ]

    def get_all_actions(
        self, game: "Game", player: "Player"
    ) -> list[ResolvedAction]:
        """Get all actions with their resolved state."""
        return self.resolve_actions(game, player)

    def copy(self) -> "ActionSet":
        """Deep copy for templates."""
        return copy.deepcopy(self)
