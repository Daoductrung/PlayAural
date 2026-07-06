"""Bot AI for Five Field Kono (stub — real implementation in a later task)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import FiveFieldKonoGame, FiveFieldKonoPlayer


def bot_think(game: "FiveFieldKonoGame", player: "FiveFieldKonoPlayer") -> str | None:
    return None
