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
from .teams import TeamManager
from ..messages.localization import Localization

if TYPE_CHECKING:
    from ..games.base import Game
    from .player import Player


@dataclass
class OptionMeta:
    """Metadata for a game option."""

    default: Any
    label: str  # Localization key for the option label
    change_msg: str  # Localization key for the change announcement
    prompt: str = ""  # Localization key for input prompt (if applicable)
    description: str = ""  # Localization key for a longer description (spoken on demand)

    def get_label(self, locale: str, value: Any) -> str:
        """Get the localized label with current value interpolated.

        Subclasses must override this.
        """
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

    def _format_default(self, locale: str) -> str:
        """Return the option's default value in player-facing form."""
        return str(self.default)

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        """Return explicit or generated help text for this option."""
        if self.description:
            return Localization.get(locale, self.description)
        return Localization.get(
            locale,
            "option-desc-generic",
            label=self.get_label(locale, current_value),
            default=self._format_default(locale),
        )


@dataclass
class IntOption(OptionMeta):
    """Integer option with min/max validation."""

    min_val: int = 0
    max_val: int = 100
    value_key: str = (
        "score"  # Key used in localization (e.g., "score", "points", "sides")
    )

    def get_label(self, locale: str, value: Any) -> str:
        return Localization.get(locale, self.label, **self.get_label_kwargs(value))

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

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        if self.description:
            return Localization.get(locale, self.description)
        return Localization.get(
            locale,
            "option-desc-integer",
            label=self.get_label(locale, current_value),
            min=self.min_val,
            max=self.max_val,
            default=self._format_default(locale),
        )


@dataclass
class FloatOption(OptionMeta):
    """Float option with min/max validation and decimal rounding."""

    min_val: float = 0.0
    max_val: float = 100.0
    decimal_places: int = 1  # Round to this many decimal places
    value_key: str = (
        "value"  # Key used in localization (e.g., "value", "amount", "rate")
    )

    def get_label(self, locale: str, value: Any) -> str:
        return Localization.get(locale, self.label, **self.get_label_kwargs(value))

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

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        if self.description:
            return Localization.get(locale, self.description)
        return Localization.get(
            locale,
            "option-desc-number",
            label=self.get_label(locale, current_value),
            min=self.min_val,
            max=self.max_val,
            default=self._format_default(locale),
        )


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

    def get_label(self, locale: str, value: Any) -> str:
        return Localization.get(
            locale, self.label, **self.get_label_kwargs_localized(value, locale)
        )

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

    def _format_default(self, locale: str) -> str:
        return self.get_localized_choice(str(self.default), locale)

    def _localized_choices_for_description(
        self,
        locale: str,
        game: "Game | None",
        player: "Player | None",
    ) -> str:
        try:
            choices = (
                self.get_choices(game, player)
                if game is not None
                else list(self.choices)
            )
        except TypeError:
            choices = list(self.choices) if not callable(self.choices) else []
        localized = [
            self.get_localized_choice(str(choice), locale) for choice in choices
        ]
        if not localized:
            return Localization.get(locale, "option-desc-no-choices")
        return Localization.format_list_or(locale, localized)

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        if self.description:
            return Localization.get(locale, self.description)
        return Localization.get(
            locale,
            "option-desc-menu",
            label=self.get_label(locale, current_value),
            choices=self._localized_choices_for_description(locale, game, player),
            default=self._format_default(locale),
        )


@dataclass
class TeamModeOption(MenuOption):
    """
    Menu option specifically for team modes.

    Stores team modes in internal format ("individual", "2v2", "2v2v2")
    but displays them in localized format ("Individual", "2 teams of 2").
    """

    def get_localized_choice(self, value: str, locale: str) -> str:
        """Convert internal team mode format to localized display format."""
        return TeamManager.format_team_mode_for_display(value, locale)


@dataclass
class BoolOption(OptionMeta):
    """Boolean toggle option."""

    value_key: str = "enabled"  # Key used in localization

    def __post_init__(self):
        # Bool options don't need a prompt - they just toggle
        self.prompt = ""

    def get_label(self, locale: str, value: Any) -> str:
        on_off_key = "option-on" if value else "option-off"
        on_off = Localization.get(locale, on_off_key)
        return Localization.get(locale, self.label, **{self.value_key: on_off})

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: "on" if value else "off"}

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        return {self.value_key: "on" if value else "off"}

    def get_change_kwargs_localized(self, value: Any, locale: str) -> dict[str, Any]:
        """Get kwargs with localized on/off value for change message."""
        on_off_key = "option-on" if value else "option-off"
        return {self.value_key: Localization.get(locale, on_off_key)}

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

    def _format_default(self, locale: str) -> str:
        return Localization.get(locale, "option-on" if self.default else "option-off")

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        if self.description:
            return Localization.get(locale, self.description)
        return Localization.get(
            locale,
            "option-desc-bool",
            label=self.get_label(locale, current_value),
            default=self._format_default(locale),
        )


@dataclass
class MultiSelectOption(OptionMeta):
    """Multi-select option where multiple choices can be toggled on/off.

    Stores a list of selected choice strings. Presented as a path-aware
    sub-menu of boolean toggles (optionally grouped), with optional
    "Select all" / "Deselect all" bulk actions.

    Attributes:
        choices: Static list or no-arg callable returning available choices.
        min_selected: Minimum number of choices that must remain selected.
        max_selected: Maximum number of choices that can be selected (0 = no limit).
        choice_labels: Optional mapping of choice -> localization key for display.
        show_bulk_actions: If True, show "Select all" / "Deselect all" in the toggle list.
        groups: Optional grouping of choices. When set, the top-level multi-select
            shows group names as navigable sub-menus instead of individual choices.
            Maps group name -> list of choice strings in that group. May be a no-arg
            callable returning such a mapping.
    """

    choices: list[str] | Callable[[], list[str]] = field(default_factory=list)
    min_selected: int = 1
    max_selected: int = 0  # 0 = no limit (all choices can be selected)
    choice_labels: dict[str, str] | None = None
    show_bulk_actions: bool = False
    groups: dict[str, list[str]] | Callable[[], dict[str, list[str]]] | None = None

    def get_choices(self) -> list[str]:
        """Get the list of available choices."""
        if callable(self.choices):
            return self.choices()
        return list(self.choices)

    def get_groups(self) -> dict[str, list[str]] | None:
        """Get the group mapping, if any."""
        if self.groups is None:
            return None
        if callable(self.groups):
            return self.groups()
        return dict(self.groups)

    def get_localized_choice(self, value: str, locale: str) -> str:
        """Get the localized display text for a choice value."""
        if self.choice_labels and value in self.choice_labels:
            return Localization.get(locale, self.choice_labels[value])
        return value

    def get_label(self, locale: str, value: Any) -> str:
        return Localization.get(locale, self.label, **self.get_label_kwargs(value))

    def get_label_kwargs(self, value: Any) -> dict[str, Any]:
        """Return label formatting kwargs for the current value (a list)."""
        return {
            "count": len(value) if isinstance(value, list) else 0,
            "total": len(self.get_choices()),
        }

    def get_change_kwargs(self, value: Any) -> dict[str, Any]:
        """Return change-message kwargs for the current value."""
        return {
            "count": len(value) if isinstance(value, list) else 0,
            "total": len(self.get_choices()),
        }

    def create_action(
        self,
        option_name: str,
        game: "Game",
        player: "Player",
        current_value: Any,
        locale: str,
    ) -> Action:
        """Create an action that opens the multi-select sub-menu."""
        label = Localization.get(
            locale, self.label, **self.get_label_kwargs(current_value)
        )
        return Action(
            id=f"multiselect_{option_name}",
            label=label,
            handler="_action_open_multiselect",
            is_enabled="_is_option_enabled",
            is_hidden="_is_option_hidden",
            show_in_actions_menu=False,
        )

    def validate_and_convert(self, value: str) -> tuple[bool, Any]:
        """Not used for multi-select (toggles are handled individually)."""
        return True, value

    def _format_choice_list(self, locale: str, values: list[str]) -> str:
        localized = [self.get_localized_choice(str(value), locale) for value in values]
        if not localized:
            return Localization.get(locale, "option-desc-none-selected")
        return Localization.format_list_and(locale, localized)

    def _format_default(self, locale: str) -> str:
        default_values = list(self.default) if isinstance(self.default, list) else []
        return self._format_choice_list(locale, default_values)

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: "Game | None" = None,
        player: "Player | None" = None,
    ) -> str:
        if self.description:
            return Localization.get(locale, self.description)
        selected = list(current_value) if isinstance(current_value, list) else []
        max_text = (
            Localization.get(locale, "option-desc-no-maximum")
            if self.max_selected <= 0
            else str(self.max_selected)
        )
        return Localization.get(
            locale,
            "option-desc-multiselect",
            label=self.get_label(locale, current_value),
            selected=self._format_choice_list(locale, selected),
            default=self._format_default(locale),
            min=self.min_selected,
            max=max_text,
        )


def option_field(
    meta: OptionMeta,
    *,
    visible_when: (
        tuple[str, Callable[[Any], bool]]
        | list[tuple[str, Callable[[Any], bool]]]
        | None
    ) = None,
) -> Any:
    """Create a dataclass field with option metadata attached.

    Usage:
        target_score: int = option_field(IntOption(default=50, ...))

    Args:
        meta: Option metadata instance.
        visible_when: One or more (option_name, predicate) tuples. The option is
            hidden unless every predicate returns True for its referenced
            option's current value (AND logic). Use for mode-conditional options.
    """
    metadata: dict[str, Any] = {"option_meta": meta}
    if visible_when is not None:
        if isinstance(visible_when, tuple):
            visible_when = [visible_when]
        metadata["visible_when"] = visible_when
    return field(default=meta.default, metadata=metadata)


def multi_select_field(meta: MultiSelectOption) -> Any:
    """Create a dataclass field for a multi-select option.

    The field stores a ``list[str]`` of selected choices. Each instance gets
    an independent copy of the default list.

    Args:
        meta: MultiSelectOption metadata instance.

    Returns:
        Dataclass field configured for multi-select options.
    """
    default_val = list(meta.default) if isinstance(meta.default, list) else []
    return field(
        default_factory=lambda d=default_val: list(d),
        metadata={"option_meta": meta},
    )


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


def get_visibility_conditions(
    options_class: type, field_name: str
) -> list[tuple[str, Callable[[Any], bool]]] | None:
    """Get the visible_when conditions for an option field, if any."""
    for f in fields(options_class):
        if f.name == field_name:
            return f.metadata.get("visible_when")
    return None


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

    def is_option_visible(self, name: str) -> bool:
        """Whether an option passes all its visible_when conditions (AND logic).

        Options without conditions are always visible. Used to hide
        mode-conditional options from the lobby until they are relevant.
        """
        conditions = get_visibility_conditions(type(self), name)
        if not conditions:
            return True
        for ref_name, predicate in conditions:
            if not predicate(getattr(self, ref_name, None)):
                return False
        return True

    def format_options_summary(self, locale: str) -> list[str]:
        """Return a list of localized label strings for all current option values."""
        lines = []
        for name, meta in self.get_option_metas().items():
            if not self.is_option_visible(name):
                continue
            current_value = getattr(self, name)
            lines.append(meta.get_label(locale, current_value))
        return lines

    def _get_options_path(self, game: "Game", player: "Player") -> list[str]:
        """Get the current options navigation path for a player.

        Returns an empty list when the player is at the top level (or when the
        game does not track navigation, e.g. games without multi-select options).
        """
        if hasattr(game, "_options_path"):
            return game._options_path.get(player.id, [])
        return []

    def _populate_action_set(
        self, action_set: ActionSet, game: "Game", player: "Player", locale: str
    ) -> None:
        """Populate an action set with options for the player's current path.

        At the top level this renders one action per visible option (honoring
        visible_when). When the player has navigated into a MultiSelectOption it
        renders the relevant toggles, optional bulk actions, and a back action.
        PlayAural has no option groups, so there are no group headers here.
        """
        path = self._get_options_path(game, player)
        options_class = type(self)

        if path:
            current_level = path[-1]

            # Inside a group of a grouped MultiSelectOption.
            # Path pattern: [..., "option_name", "group:GroupName"]
            if current_level.startswith("group:") and len(path) >= 2:
                option_name = path[-2]
                group_name = current_level.removeprefix("group:")
                meta = get_option_meta(options_class, option_name)
                if meta and isinstance(meta, MultiSelectOption):
                    groups = meta.get_groups()
                    if groups and group_name in groups:
                        self._add_multiselect_toggles(
                            action_set, meta, option_name,
                            groups[group_name], getattr(self, option_name, []),
                            locale,
                        )
                        if meta.show_bulk_actions:
                            self._add_multiselect_bulk_actions(
                                action_set, option_name, locale
                            )
                        self._add_options_back_action(
                            action_set, locale, handler="_action_options_back"
                        )
                        return

            # At a MultiSelectOption's top level.
            meta = get_option_meta(options_class, current_level)
            if meta and isinstance(meta, MultiSelectOption):
                current_selections = getattr(self, current_level, [])
                groups = meta.get_groups()

                if groups:
                    # Show group names as navigable sub-menus.
                    for group_name, group_choices in groups.items():
                        selected_count = sum(
                            1 for c in group_choices if c in current_selections
                        )
                        total_count = len(group_choices)
                        label = (
                            f"{group_name} "
                            f"({selected_count} of {total_count} selected)"
                        )
                        action_set.add(
                            Action(
                                id=f"msgroup_{current_level}_{group_name}",
                                label=label,
                                handler="_action_open_ms_group",
                                is_enabled="_is_option_enabled",
                                is_hidden="_is_option_hidden",
                                show_in_actions_menu=False,
                            )
                        )
                else:
                    self._add_multiselect_toggles(
                        action_set, meta, current_level,
                        meta.get_choices(), current_selections, locale,
                    )
                    if meta.show_bulk_actions:
                        self._add_multiselect_bulk_actions(
                            action_set, current_level, locale
                        )

                self._add_options_back_action(
                    action_set, locale, handler="_action_options_back_multiselect"
                )
                return

        # Top level: every visible option (PlayAural has no option groups).
        for name, meta in self.get_option_metas().items():
            if not self.is_option_visible(name):
                continue
            current_value = getattr(self, name)
            action = meta.create_action(name, game, player, current_value, locale)
            action_set.add(action)

    @staticmethod
    def _add_multiselect_toggles(
        action_set: ActionSet,
        meta: "MultiSelectOption",
        option_name: str,
        choices: list[str],
        current_selections: list[str],
        locale: str,
    ) -> None:
        """Add one on/off toggle action per choice."""
        for choice in choices:
            selected = choice in current_selections
            on_off_key = "option-on" if selected else "option-off"
            on_off = Localization.get(locale, on_off_key)
            display = meta.get_localized_choice(choice, locale)
            action_set.add(
                Action(
                    id=f"mstoggle_{option_name}_{choice}",
                    label=f"{display}: {on_off}",
                    handler="_action_toggle_multiselect",
                    is_enabled="_is_option_enabled",
                    is_hidden="_is_option_hidden",
                    show_in_actions_menu=False,
                )
            )

    @staticmethod
    def _add_multiselect_bulk_actions(
        action_set: ActionSet, option_name: str, locale: str
    ) -> None:
        """Add Select all / Deselect all actions for the current view."""
        action_set.add(
            Action(
                id=f"mselectall_{option_name}",
                label=Localization.get(locale, "option-select-all"),
                handler="_action_select_all_multiselect",
                is_enabled="_is_option_enabled",
                is_hidden="_is_option_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id=f"mdeselectall_{option_name}",
                label=Localization.get(locale, "option-deselect-all"),
                handler="_action_deselect_all_multiselect",
                is_enabled="_is_option_enabled",
                is_hidden="_is_option_hidden",
                show_in_actions_menu=False,
            )
        )

    @staticmethod
    def _add_options_back_action(
        action_set: ActionSet, locale: str, *, handler: str
    ) -> None:
        """Add a Back action that pops one level of options navigation."""
        action_set.add(
            Action(
                id="options_back",
                label=Localization.get(locale, "option-back"),
                handler=handler,
                is_enabled="_is_option_enabled",
                is_hidden="_is_option_hidden",
                show_in_actions_menu=False,
            )
        )

    def create_options_action_set(self, game: "Game", player: "Player") -> ActionSet:
        """Create an ActionSet for the player's current options navigation level."""
        user = game.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="options")
        self._populate_action_set(action_set, game, player, locale)
        return action_set

    def update_options_labels(self, game: "Game") -> None:
        """Update options action sets for all players to reflect current values.

        Updates the existing action set in-place to avoid duplicates.
        """
        for player in game.players:
            existing_set = game.get_action_set(player, "options")
            if existing_set:
                existing_set._actions.clear()
                existing_set._order.clear()
                user = game.get_user(player)
                locale = user.locale if user else "en"
                self._populate_action_set(existing_set, game, player, locale)
            else:
                # Fallback: create and add new action set if it doesn't exist
                new_options_set = self.create_options_action_set(game, player)
                game.add_action_set(player, new_options_set)


class OptionsHandlerMixin:
    """Mixin providing declarative options handling for games.

    Expects on the Game class:
        - self.options: GameOptions (subclass with option_field declarations)
        - self.get_user(player) -> User | None
        - self.refresh_menus()
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

    def _is_in_options_submenu(self, player: "Player") -> bool:
        """Whether a player is navigated into an options sub-menu (multi-select)."""
        if hasattr(self, "_options_path"):
            return bool(self._options_path.get(player.id))
        return False

    def get_all_visible_actions(self, player: "Player") -> list:
        """Show only the options action set while inside an options sub-menu.

        When a player has navigated into a multi-select option, the lobby/turn
        actions are suppressed so the toggle list is uncluttered. At the top
        level this defers to the normal action-set composition.
        """
        if self._is_in_options_submenu(player):
            options_set = self.get_action_set(player, "options")
            if options_set:
                return options_set.get_visible_actions(self, player)
            return []
        return super().get_all_visible_actions(player)

    def _speak_option_description(self, player: "Player", menu_item_id: str) -> bool:
        """Speak an option's description when space is pressed on it.

        Extracts the option name from the focused menu item id (e.g. set_X /
        toggle_X) and speaks explicit option help or a code-derived fallback.
        Returns True if help was spoken.
        """
        if not hasattr(self, "options"):
            return False
        option_name = None
        for prefix in ("set_", "toggle_", "group_", "multiselect_"):
            if menu_item_id.startswith(prefix):
                option_name = menu_item_id[len(prefix):]
                break
        if option_name is None:
            return False
        meta = get_option_meta(type(self.options), option_name)
        if meta is None:
            return False
        user = self.get_user(player)
        if not user:
            return False
        current_value = getattr(self.options, option_name, meta.default)
        if meta.description:
            user.speak_l(meta.description, buffer="system")
        else:
            user.speak(
                meta.get_description(
                    user.locale,
                    current_value,
                    game=self,
                    player=player,
                ),
                buffer="system",
            )
        return True

    def _handle_option_change(self, option_name: str, value: str) -> None:
        """Handle a declarative option change (for int/menu options).

        This is called by auto-generated option actions.
        """
        meta = get_option_meta(type(self.options), option_name)
        if not meta:
            return

        success, converted = meta.validate_and_convert(value)
        if not success:
            return

        # Set the option value
        setattr(self.options, option_name, converted)

        # Broadcast change to all players
        self._broadcast_option_change(meta, converted)

        # Update labels and rebuild menus
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        self.refresh_menus()

    def _handle_option_toggle(self, option_name: str) -> None:
        """Handle a declarative boolean option toggle.

        This is called by auto-generated toggle actions.
        """
        meta = get_option_meta(type(self.options), option_name)
        if not meta:
            return

        # Toggle the value
        current = getattr(self.options, option_name)
        new_value = not current
        setattr(self.options, option_name, new_value)

        # Broadcast change to all players
        self._broadcast_option_change(meta, new_value)

        # Update labels and rebuild menus
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        self.refresh_menus()

    def _broadcast_option_change(self, meta: OptionMeta, value: Any) -> None:
        """Broadcast an option change announcement to all players."""
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            if hasattr(meta, "get_change_kwargs_localized"):
                kwargs = meta.get_change_kwargs_localized(value, user.locale)
            else:
                kwargs = meta.get_change_kwargs(value)
            user.speak_l(meta.change_msg, buffer="system", **kwargs)

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

    # Navigation handlers for multi-select options.

    def _first_visible_options_action_id(self, player: "Player") -> str | None:
        """Return the first visible action in the current options view."""
        options_set = self.get_action_set(player, "options")
        if not options_set:
            return None
        visible = options_set.get_visible_actions(self, player)
        if not visible:
            return None
        return visible[0].action.id

    def _options_focus_target_or_first(
        self,
        player: "Player",
        focus_action_id: str | None,
    ) -> str | None:
        """Return a valid options focus target, falling back to the first item."""
        options_set = self.get_action_set(player, "options")
        if not options_set:
            return None
        if focus_action_id:
            for resolved in options_set.get_visible_actions(self, player):
                if resolved.action.id == focus_action_id:
                    return focus_action_id
        return self._first_visible_options_action_id(player)

    def _refresh_options_menus(
        self,
        player: "Player | None" = None,
        *,
        focus_action_id: str | None = None,
        focus_first: bool = False,
    ) -> None:
        """Re-render options and optionally queue an action-driven focus jump."""
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        if player is not None and (focus_action_id or focus_first):
            focus = self._options_focus_target_or_first(player, focus_action_id)
            if focus:
                self.request_menu_focus(player, focus)
        self.refresh_menus()

    def _action_open_multiselect(self, player: "Player", action_id: str) -> None:
        """Open a multi-select option's sub-menu.

        Pushes the option name onto the player's options path and rebuilds menus.
        """
        option_name = action_id.removeprefix("multiselect_")
        if not hasattr(self, "_options_path"):
            self._options_path = {}
        path = self._options_path.setdefault(player.id, [])
        path.append(option_name)
        self._refresh_options_menus(player, focus_first=True)

    def _action_options_back(self, player: "Player", action_id: str) -> None:
        """Go back one level in the options navigation (no validation)."""
        focus_action_id = None
        if hasattr(self, "_options_path"):
            path = self._options_path.get(player.id, [])
            if path:
                current = path.pop()
                if current.startswith("group:") and path:
                    option_name = path[-1]
                    group_name = current.removeprefix("group:")
                    focus_action_id = f"msgroup_{option_name}_{group_name}"
                elif current:
                    focus_action_id = f"multiselect_{current}"
        self._refresh_options_menus(player, focus_action_id=focus_action_id)

    def _action_open_ms_group(self, player: "Player", action_id: str) -> None:
        """Open a multi-select group's sub-menu.

        Action ID format: msgroup_{option_name}_{group_name}.
        Pushes 'group:{group_name}' onto the player's options path.
        """
        remainder = action_id.removeprefix("msgroup_")
        for name, meta in self.options.get_option_metas().items():
            if isinstance(meta, MultiSelectOption) and remainder.startswith(name + "_"):
                group_name = remainder[len(name) + 1 :]
                if not hasattr(self, "_options_path"):
                    self._options_path = {}
                path = self._options_path.setdefault(player.id, [])
                path.append(f"group:{group_name}")
                self._refresh_options_menus(player, focus_first=True)
                return

    def _get_scoped_choices(
        self, player: "Player", option_name: str, meta: "MultiSelectOption"
    ) -> list[str]:
        """Get the choices scoped to the current view (group or all)."""
        if hasattr(self, "_options_path"):
            path = self._options_path.get(player.id, [])
            if path and path[-1].startswith("group:"):
                group_name = path[-1].removeprefix("group:")
                groups = meta.get_groups()
                if groups and group_name in groups:
                    return groups[group_name]
        return meta.get_choices()

    def _action_select_all_multiselect(self, player: "Player", action_id: str) -> None:
        """Select all choices in the current multi-select view."""
        option_name = action_id.removeprefix("mselectall_")
        meta = get_option_meta(type(self.options), option_name)
        if not meta or not isinstance(meta, MultiSelectOption):
            return

        current_list = list(getattr(self.options, option_name, []))
        choices = self._get_scoped_choices(player, option_name, meta)

        added = 0
        for choice in choices:
            if choice not in current_list:
                current_list.append(choice)
                added += 1

        setattr(self.options, option_name, current_list)

        if added > 0:
            user = self.get_user(player)
            if user:
                user.speak_l("option-selected-count", buffer="system", count=added)

        self._refresh_options_menus()

    def _action_deselect_all_multiselect(self, player: "Player", action_id: str) -> None:
        """Deselect all choices in the current multi-select view."""
        option_name = action_id.removeprefix("mdeselectall_")
        meta = get_option_meta(type(self.options), option_name)
        if not meta or not isinstance(meta, MultiSelectOption):
            return

        current_list = list(getattr(self.options, option_name, []))
        choices = self._get_scoped_choices(player, option_name, meta)

        removed = 0
        for choice in choices:
            if choice in current_list:
                current_list.remove(choice)
                removed += 1

        setattr(self.options, option_name, current_list)

        if removed > 0:
            user = self.get_user(player)
            if user:
                user.speak_l("option-deselected-count", buffer="system", count=removed)

        self._refresh_options_menus()

    def _action_options_back_multiselect(self, player: "Player", action_id: str) -> None:
        """Go back from a multi-select menu, validating min/max selection count."""
        if hasattr(self, "_options_path"):
            path = self._options_path.get(player.id, [])
            if path:
                current = path[-1]
                # Going back from a group level just pops the group.
                if current.startswith("group:"):
                    group_name = current.removeprefix("group:")
                    path.pop()
                    option_name = path[-1] if path else ""
                    focus_action_id = (
                        f"msgroup_{option_name}_{group_name}"
                        if option_name
                        else None
                    )
                    self._refresh_options_menus(
                        player,
                        focus_action_id=focus_action_id,
                    )
                    return
                # Going back from the option level validates selection count.
                meta = get_option_meta(type(self.options), current)
                if meta and isinstance(meta, MultiSelectOption):
                    current_list = getattr(self.options, current, [])
                    if len(current_list) < meta.min_selected:
                        user = self.get_user(player)
                        if user:
                            user.speak_l(
                                "option-min-selected",
                                buffer="system",
                                count=meta.min_selected,
                            )
                        return
                    if meta.max_selected > 0 and len(current_list) > meta.max_selected:
                        user = self.get_user(player)
                        if user:
                            user.speak_l(
                                "option-max-selected",
                                buffer="system",
                                count=meta.max_selected,
                            )
                        return
                path.pop()
                self._refresh_options_menus(
                    player,
                    focus_action_id=f"multiselect_{current}",
                )
                return
        self._refresh_options_menus(player)

    def _action_toggle_multiselect(self, player: "Player", action_id: str) -> None:
        """Toggle a single choice in a multi-select option.

        Action ID format: mstoggle_{option_name}_{choice}. The choice may itself
        contain underscores, so the option name is matched by prefix.
        """
        remainder = action_id.removeprefix("mstoggle_")
        option_name = None
        choice = None
        for name, meta in self.options.get_option_metas().items():
            if isinstance(meta, MultiSelectOption) and remainder.startswith(name + "_"):
                option_name = name
                choice = remainder[len(name) + 1 :]
                break
        if not option_name or choice is None:
            return

        meta = get_option_meta(type(self.options), option_name)
        if not meta or not isinstance(meta, MultiSelectOption):
            return

        current_list = list(getattr(self.options, option_name, []))
        if choice in current_list:
            current_list.remove(choice)
        else:
            current_list.append(choice)

        setattr(self.options, option_name, current_list)
        self._refresh_options_menus()
