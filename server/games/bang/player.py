"""Persistent player state for BANG!."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...game_utils.player import Player
from .cards import BangCard, BangInPlayCard


@dataclass
class BangPlayer(Player):
    role: str = ""
    role_revealed: bool = False
    character: str = ""
    alternate_character: str = ""
    copied_character: str = ""
    hand: list[BangCard] = field(default_factory=list)
    in_play: list[BangInPlayCard] = field(default_factory=list)
    life: int = 0
    max_life: int = 0
    eliminated: bool = False
    ghost_active: bool = False
    elimination_order: int = 0
    bangs_played: int = 0
    doc_holyday_used: int = 0
    jose_delgado_uses: int = 0
    uncle_will_used: int = 0
    law_card_id: int = 0
    handcuffs_suit: str = ""
    molly_deferred_draws: int = 0
    vendetta_extra_turn: bool = False
    bot_role_suspicion: dict[str, int] = field(default_factory=dict)
