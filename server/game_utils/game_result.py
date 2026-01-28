"""
Game result dataclass for unified game end handling and statistics.

Provides a structured way to capture game results, enabling:
- Consistent end screen presentation
- Database persistence for statistics
- Helper utilities for leaderboards and ratings
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

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

    @classmethod
    def create(
        cls,
        game_type: str,
        duration_ticks: int,
        players: list[tuple[str, str, bool]],  # (id, name, is_bot)
        custom_data: dict[str, Any] | None = None,
    ) -> "GameResult":
        """
        Convenience factory for creating a GameResult.

        Args:
            game_type: The game type identifier (e.g., "pig", "farkle")
            duration_ticks: Game duration in ticks
            players: List of (player_id, player_name, is_bot) tuples
            custom_data: Game-specific result data

        Returns:
            A new GameResult instance
        """
        return cls(
            game_type=game_type,
            timestamp=datetime.now().isoformat(),
            duration_ticks=duration_ticks,
            player_results=[
                PlayerResult(player_id=pid, player_name=name, is_bot=is_bot)
                for pid, name, is_bot in players
            ],
            custom_data=custom_data or {},
        )

    def get_duration_seconds(self) -> float:
        """Get game duration in seconds (20 ticks = 1 second)."""
        return self.duration_ticks / 20.0

    def get_duration_formatted(self) -> str:
        """Get game duration as a formatted string (e.g., '5:32')."""
        total_seconds = int(self.get_duration_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_player_ids(self) -> list[str]:
        """Get list of all player IDs."""
        return [p.player_id for p in self.player_results]

    def get_human_player_ids(self) -> list[str]:
        """Get list of human (non-bot) player IDs."""
        return [p.player_id for p in self.player_results if not p.is_bot]

    def has_human_players(self) -> bool:
        """Check if any human players participated."""
        return any(not p.is_bot for p in self.player_results)
