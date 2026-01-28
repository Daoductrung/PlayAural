"""Player definition for Mile by Mile."""

from dataclasses import dataclass, field

from ..base import Player
from .cards import Card


@dataclass
class MileByMilePlayer(Player):
    """Player state for Mile by Mile."""

    hand: list[Card] = field(default_factory=list)
    team_index: int = 0
