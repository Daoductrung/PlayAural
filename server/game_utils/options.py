"""
Declarative Options System for PlayAural Games.

This module provides a way to define game options declaratively, reducing
boilerplate code for option handling, validation, and UI generation.

Usage:
    @dataclass
    class MyGameOptions(GameOptions):
        target_score: int = option_field(
            IntOption(default=50, min_val=10, max_val=1000,
                      label="game-set-target-score",
                      prompt="game-enter-target-score",
                      change_msg="game-option-changed-target"))
        team_mode: str = option_field(
            MenuOption(default="individual",
                       choices=["individual", "2v2"],
                       label="game-set-team-mode",
                       prompt="game-select-team-mode",
                       change_msg="game-option-changed-team"))
        show_hints: bool = option_field(
            BoolOption(default=False,
                       label="my-game-toggle-hints",
                       change_msg="my-game-option-changed-hints"))
"""

from dataclasses import dataclass, field, fields
from typing import Any, Callable, TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from .actions import Action, ActionSet, EditboxInput, MenuInput
from ..messages.localization import Localization

if TYPE_CHECKING:
    from ..games.base import Game, Player


@dataclass
class OptionMeta:
    """Metadata for a game option."""

    default: Any
    label: str  # Localization key for the option label
    change_msg: str  # Localization key for the change announcement
    prompt: str = ""  # Localization key for input prompt (if applicable)

    def get_label(self, locale: str, value: Any) -> str:
        """Get the localized label with current value interpolated."""
        raise NotImplementedError

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        """Get kwargs for label localization."""
        raise NotImplementedError

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        """Get kwargs for change message localization."""
        raise NotImplementedError

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        """Create an Action for this option."""
        raise NotImplementedError

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        """Validate and convert input string to the option's type.

        Returns (success, converted_value). If success is False, converted_value
        is the original string.
        """
        raise NotImplementedError


@dataclass
class IntOption(OptionMeta):
    """Integer option with min/max validation."""

    min_val: int = 0
    max_val: int = 100
    value_key: str = (
        "score"  # Key used in localization (e.g., "score", "points", "sides")
    )

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        label = Localization.get(
            locale, self.label, **self.get_label_kwargs(current_value)
        )
        return Action(
            id=f"set_{option_name}",
            label=label,
            handler="_action_set_option",  # Generic handler extracts option_name from action_id
            is_enabled="_is_option_enabled",
            is_hidden="_is_option_hidden",
            input_request=EditboxInput(
                prompt=self.prompt,
                default=str(current_value),
            ),
            show_in_actions_menu=False,
        )

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        try:
            int_val = int(value)
            int_val = max(self.min_val, min(self.max_val, int_val))
            return True, int_val
        except ValueError:
            return False, value


@dataclass
class FloatOption(OptionMeta):
    """Float option with min/max validation and decimal rounding."""

    min_val: float = 0.0
    max_val: float = 100.0
    decimal_places: int = 1  # Round to this many decimal places
    value_key: str = (
        "value"  # Key used in localization (e.g., "value", "amount", "rate")
    )

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        label = Localization.get(
            locale, self.label, **self.get_label_kwargs(current_value)
        )
        return Action(
            id=f"set_{option_name}",
            label=label,
            handler="_action_set_option",  # Generic handler extracts option_name from action_id
            is_enabled="_is_option_enabled",
            is_hidden="_is_option_hidden",
            input_request=EditboxInput(
                prompt=self.prompt,
                default=str(current_value),
            ),
            show_in_actions_menu=False,
        )

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        try:
            float_val = float(value)
            float_val = max(self.min_val, min(self.max_val, float_val))
            float_val = round(float_val, self.decimal_places)
            return True, float_val
        except ValueError:
            return False, value


@dataclass
class MenuOption(OptionMeta):
    """Menu selection option."""

    choices: list[str] | Callable[["Game", "Player"], list[str]] = field(
        default_factory=list
    )
    value_key: str = "mode"  # Key used in localization
    # Map choice values to localization keys for display
    # If not provided, raw choice values are displayed
    choice_labels: dict[str, str] | None = None

    def get_localized_choice(self, value: str, locale: str) -> str:
        """Get the localized display text for a choice value."""
        if self.choice_labels and value in self.choice_labels:
            return Localization.get(locale, self.choice_labels[value])
        return value

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def get_label_kwargs_localized(self, value: Any, locale: str) -> dict[str, Any]:
        """Get kwargs with localized choice value."""
        display_value = self.get_localized_choice(value, locale)
        return {self.value_key: display_value}

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: value}

    def get_change_kwargs_localized(self, value: Any, locale: str) -> dict[str, Any]:
        """Get kwargs with localized choice value for change message."""
        display_value = self.get_localized_choice(value, locale)
        return {self.value_key: display_value}

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        # Use localized choice value in the label
        label = Localization.get(
            locale, self.label, **self.get_label_kwargs_localized(current_value, locale)
        )

        return Action(
            id=f"set_{option_name}",
            label=label,
            handler="_action_set_option",  # Generic handler extracts option_name from action_id
            is_enabled="_is_option_enabled",
            is_hidden="_is_option_hidden",
            input_request=MenuInput(
                prompt=self.prompt,
                options=f"_options_for_{option_name}",
            ),
            show_in_actions_menu=False,
        )

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        # For menu options, the value comes from a predefined list, so it's valid
        return True, value

    def get_choices(self, game: "Game", player: "Player") -> list[str]:
        """Get the list of choices for this option."""
        if callable(self.choices):
            return self.choices(game, player)
        return list(self.choices)


@dataclass
class TeamModeOption(MenuOption):
    """
    Menu option specifically for team modes.

    Stores team modes in internal format ("individual", "2v2", "2v2v2")
    but displays them in localized format ("Individual", "2 teams of 2").
    """

    def get_localized_choice(self, value: str, locale: str) -> str:
        """Convert internal team mode format to localized display format."""
        from .teams import TeamManager

        return TeamManager.format_team_mode_for_display(value, locale)


@dataclass
class BoolOption(OptionMeta):
    """Boolean toggle option."""

    value_key: str = "enabled"  # Key used in localization

    def __post_init__(self):
        # Bool options don't need a prompt - they just toggle
        self.prompt = ""

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: "on" if value else "off"}

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: "on" if value else "off"}

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        # Get localized on/off value
        on_off_key = "option-on" if current_value else "option-off"
        on_off = Localization.get(locale, on_off_key)
        label = Localization.get(locale, self.label, **{self.value_key: on_off})
        return Action(
            id=f"toggle_{option_name}",
            label=label,
            handler="_action_toggle_option",  # Generic handler extracts option_name from action_id
            is_enabled="_is_option_enabled",
            is_hidden="_is_option_hidden",
            # No input_request - toggles directly
            show_in_actions_menu=False,
        )

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        # For bool options, we just flip the value
        return True, value.lower() in ("true", "1", "yes")


def option_field(meta: OptionMeta) -> Any:
    """Create a dataclass field with option metadata attached.

    Usage:
        target_score: int = option_field(IntOption(default=50, ...))
    """
    return field(default=meta.default, metadata={"option_meta": meta})


def get_option_meta(options_class: type, field_name: str) -> OptionMeta | None:
    """Get the OptionMeta for a field, if it has one."""
    for f in fields(options_class):
        if f.name == field_name:
            return f.metadata.get("option_meta")
    return None


def get_all_option_metas(options_class: type) -> dict[str, OptionMeta]:
    """Get all OptionMeta instances from an options class."""
    result = {}
    for f in fields(options_class):
        meta = f.metadata.get("option_meta")
        if meta is not None:
            result[f.name] = meta
    return result


@dataclass
class GameOptions(DataClassJSONMixin):
    """Base class for game options with declarative option support.

    Subclasses should use option_field() for options that need auto-generated
    UI and handlers:

        @dataclass
        class MyOptions(GameOptions):
            target_score: int = option_field(IntOption(...))
            difficulty: str = option_field(MenuOption(...))

            # Regular fields without option_field work normally
            internal_state: int = 0
    """

    def get_option_metas(self) -> dict[str, OptionMeta]:
        """Get all option metadata for this options instance."""
        return get_all_option_metas(type(self))

    def create_options_action_set(self, game: "Game", player: "Player") -> ActionSet:
        """Create an ActionSet with all declared options."""
        user = game.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="options")

        for name, meta in self.get_option_metas().items():
            current_value = getattr(self, name)
            action = meta.create_action(name, game, player, current_value, locale)
            action_set.add(action)

        return action_set

    def update_options_labels(self, game: "Game") -> None:
        """Update options action sets for all players to reflect current values.

        Updates the existing action set in-place to avoid duplicates.
        """
        for player in game.players:
            # Find existing options action set
            existing_set = game.get_action_set(player, "options")
            if existing_set:
                # Clear existing actions
                existing_set._actions.clear()
                existing_set._order.clear()
                # Add updated actions with current values
                locale = game.get_user(player).locale if game.get_user(player) else "en"
                for name, meta in self.get_option_metas().items():
                    current_value = getattr(self, name)
                    action = meta.create_action(name, game, player, current_value, locale)
                    existing_set.add(action)
            else:
                # Fallback: create and add new action set if it doesn't exist
                new_options_set = self.create_options_action_set(game, player)
                game.add_action_set(player, new_options_set)


class OptionsHandlerMixin:
    """Mixin providing declarative options handling for games.

    Expects on the Game class:
        - self.options: GameOptions (subclass with option_field declarations)
        - self.get_user(player) -> User | None
        - self.rebuild_all_menus()
    """

    def create_options_action_set(self, player: "Player") -> ActionSet:
        """Create the options action set for a player.

        If the game's options class uses declarative options (option_field),
        this will auto-generate the action set. Otherwise, subclasses should
        override this method.
        """
        if hasattr(self.options, "create_options_action_set"):
            return self.options.create_options_action_set(self, player)
        # Fallback for non-declarative options
        return ActionSet(name="options")

    def _handle_option_change(self, option_name: str, value: str) -> None:
        """Handle a declarative option change (for int/menu options).

        This is called by auto-generated option actions.
        No broadcast needed - screen readers speak the updated list item.
        """
        meta = get_option_meta(type(self.options), option_name)
        if not meta:
            return

        success, converted = meta.validate_and_convert(value)
        if not success:
            return

        # Set the option value
        setattr(self.options, option_name, converted)

        # Update labels and rebuild menus
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        self.rebuild_all_menus()

    def _handle_option_toggle(self, option_name: str) -> None:
        """Handle a declarative boolean option toggle.

        This is called by auto-generated toggle actions.
        No broadcast needed - screen readers speak the updated list item.
        """
        meta = get_option_meta(type(self.options), option_name)
        if not meta:
            return

        # Toggle the value
        current = getattr(self.options, option_name)
        new_value = not current
        setattr(self.options, option_name, new_value)

        # Update labels and rebuild menus
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        self.rebuild_all_menus()

    # Generic option action handlers (extract option_name from action_id)

    def _action_set_option(self, player: "Player", value: str, action_id: str) -> None:
        """Generic handler for setting an option value.

        Extracts the option name from action_id (e.g., "set_total_rounds" -> "total_rounds")
        and delegates to _handle_option_change.
        """
        option_name = action_id.removeprefix("set_")
        self._handle_option_change(option_name, value)

    def _action_toggle_option(self, player: "Player", action_id: str) -> None:
        """Generic handler for toggling a boolean option.

        Extracts the option name from action_id (e.g., "toggle_show_hints" -> "show_hints")
        and delegates to _handle_option_toggle.
        """
        option_name = action_id.removeprefix("toggle_")
        self._handle_option_toggle(option_name)
