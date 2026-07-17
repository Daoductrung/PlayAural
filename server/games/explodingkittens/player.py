"""Player state for Exploding Kittens."""

from dataclasses import dataclass, field

from ...game_utils.player import Player
from .cards import ExplodingKittensCard


@dataclass
class ExplodingKittensPlayer(Player):
    """Persistent hand, elimination, knowledge, and bot planning state."""

    hand: list[ExplodingKittensCard] = field(default_factory=list)
    selected_card_ids: list[int] = field(default_factory=list)
    known_future_card_ids: list[int] = field(default_factory=list)
    eliminated: bool = False
    elimination_order: int = 0
    bot_combo_kind: str = ""
    bot_combo_card_ids: list[int] = field(default_factory=list)
    bot_planned_target_id: str = ""
    bot_requested_kind: str = ""
