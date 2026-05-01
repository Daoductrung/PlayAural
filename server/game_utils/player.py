"""Base player state shared by all games."""

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class Player(DataClassJSONMixin):
    """
    A player in a game.

    This is serialized with game state. Runtime user objects are reattached
    after loading and are never stored on the player.
    """

    id: str
    name: str
    is_bot: bool = False
    replaced_human: bool = False
    replaced_human_name: str = ""
    replacement_bot_name: str = ""
    is_spectator: bool = False
    bot_think_ticks: int = 0
    bot_pending_action: str | None = None
    bot_target: int | None = None
    reconnect_grace_ticks: int = 0
