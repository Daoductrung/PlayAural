"""Player and Options definitions for Coup."""

from dataclasses import dataclass, field
from ...games.base import Player, GameOptions
from ...game_utils.options import IntOption, BoolOption, option_field
from .cards import Card


@dataclass
class CoupPlayer(Player):
    """Player state for Coup."""

    coins: int = 0
    influences: list[Card] = field(default_factory=list)
    is_dead: bool = False

    @property
    def live_influences(self) -> list[Card]:
        """Get the player's alive (face-down) influences."""
        return [card for card in self.influences if not card.is_revealed]

    @property
    def dead_influences(self) -> list[Card]:
        """Get the player's dead (face-up) influences."""
        return [card for card in self.influences if card.is_revealed]

    def has_influence(self, character: str) -> bool:
        """Check if the player has a specific alive character influence."""
        return any(card.character == character for card in self.live_influences)

    def reveal_influence(self, index: int) -> None:
        """Reveal a specific influence (it dies)."""
        live = self.live_influences
        if 0 <= index < len(live):
            # Find the actual card in the main influences list to modify its state
            target_card = live[index]
            for card in self.influences:
                if card is target_card:
                    card.is_revealed = True
                    break

        if not self.live_influences:
            self.is_dead = True


@dataclass
class CoupOptions(GameOptions):
    """Options for Coup."""

    timer_duration_seconds: int = option_field(
        IntOption(
            default=7,
            min_val=3,
            max_val=15,
            value_key="seconds",
            label="game-set-timer-duration",
            prompt="game-enter-timer-duration",
            change_msg="game-option-changed-timer",
        )
    )
    # The minimum required to Coup is 7. You *must* Coup at 10+.
    mandatory_coup_threshold: int = option_field(
        IntOption(
            default=10,
            min_val=10,
            max_val=20,
            value_key="coins",
            label="coup-set-mandatory-coup",
            prompt="coup-enter-mandatory-coup",
            change_msg="coup-option-changed-mandatory-coup",
        )
    )
