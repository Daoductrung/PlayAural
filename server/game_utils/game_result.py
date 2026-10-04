"""
Game result dataclass for unified game end handling and statistics.

Provides a structured way to capture game results, enabling:
- Consistent end screen presentation
- Database persistence for statistics
- Helper utilities for leaderboards and ratings
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .player import Player

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class PlayerResult(DataClassJSONMixin):
    """
    A player's result in a completed game.

    Contains minimal required fields. Game-specific data goes in
    GameResult.custom_data.
    """

    player_id: str
    player_name: str
    is_bot: bool

    @classmethod
    def from_player(cls, player: "Player") -> "PlayerResult":
        """Snapshot one seat with its canonical result ownership.

        A disconnected human's replacement bot still owns that account's seat,
        so the account remains eligible for the eventual result. Dedicated bots
        have no account owner and are excluded from durable player statistics.
        """
        return cls(
            player_id=player.id,
            player_name=player.name,
            is_bot=player.is_bot and not player.replaced_human,
        )


@dataclass
class GameResult(DataClassJSONMixin):
    """
    Structured result of a completed game.

    Games put their specific data in custom_data, allowing full flexibility:
    - Pig: {"winner": "Alice", "final_scores": {"Alice": 105, "Bob": 89}}
    - Yahtzee: {"winner": "Bob", "yahtzees_rolled": 2, "bonus_achieved": True}
    - Cooperative: {"success": True, "rounds_survived": 12}
    """

    game_type: str
    timestamp: str  # ISO format
    duration_ticks: int
    player_results: list[PlayerResult] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)

    def has_human_players(self) -> bool:
        """Check if any human players participated."""
        return any(not p.is_bot for p in self.player_results)
