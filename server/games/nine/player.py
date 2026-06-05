from dataclasses import dataclass, field

from ...game_utils.cards import Card
from ..base import Player


@dataclass
class NinePlayer(Player):
    """
    Player-specific state for the Nine card game.
    """

    hand: list[Card] = field(default_factory=list)
