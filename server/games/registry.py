"""Game registry for registering and looking up game types."""

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Game


class GameRegistry:
    """Registry of all available game types."""

    _games: dict[str, Type["Game"]] = {}

    @classmethod
    def register(cls, game_class: Type["Game"]) -> None:
        """Register a game class."""
        game_type = game_class.get_type()
        cls._games[game_type] = game_class

    @classmethod
    def get(cls, game_type: str) -> Type["Game"] | None:
        """Get a game class by type."""
        return cls._games.get(game_type)

    @classmethod
    def get_all(cls) -> list[Type["Game"]]:
        """Get all registered game classes."""
        return list(cls._games.values())

    @classmethod
    def get_by_category(cls) -> dict[str, list[Type["Game"]]]:
        """Get games organized by category."""
        categories: dict[str, list[Type["Game"]]] = {}
        for game_class in cls._games.values():
            category = game_class.get_category()
            if category not in categories:
                categories[category] = []
            categories[category].append(game_class)
        return categories


def register_game(game_class: Type["Game"]) -> Type["Game"]:
    """Decorator to register a game class."""
    GameRegistry.register(game_class)
    return game_class


def get_game_class(game_type: str) -> Type["Game"] | None:
    """Get a game class by type."""
    return GameRegistry.get(game_type)
