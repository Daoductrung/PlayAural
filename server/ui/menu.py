"""Menu definitions for client communication."""

from dataclasses import dataclass

# Re-export MenuItem from users.base for convenience
from ..users.base import MenuItem


@dataclass
class Menu:
    """A menu definition."""

    menu_id: str
    items: list[MenuItem]
    multiletter: bool = True
    escape_behavior: str = "keybind"
    grid_enabled: bool = False
    grid_width: int = 1


__all__ = ["Menu", "MenuItem"]
