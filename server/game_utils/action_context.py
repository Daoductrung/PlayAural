"""Action execution context shared by game action handlers."""

from dataclasses import dataclass


@dataclass
class ActionContext:
    """Context passed to action handlers when triggered by keybinds or menus."""

    menu_item_id: str | None = None
    menu_index: int | None = None
    from_keybind: bool = False
