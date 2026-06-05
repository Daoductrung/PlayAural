from dataclasses import dataclass, field
from typing import Optional

from mashumaro.mixins.json import DataClassJSONMixin

from ...game_utils.cards import Card


@dataclass
class SequenceState(DataClassJSONMixin):
    """
    Represents the state of a sequence for a single suit on the table.
    """

    low_card: Optional[Card] = None
    high_card: Optional[Card] = None


@dataclass
class NineState(DataClassJSONMixin):
    """
    Game-specific state for the Nine card game.
    """

    # Dictionary mapping suit (int) to its SequenceState
    sequences: dict[int, SequenceState] = field(default_factory=dict)

    # Flag to indicate if the nine of clubs has been played to start the game
    nine_of_clubs_played: bool = False
