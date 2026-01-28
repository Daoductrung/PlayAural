from __future__ import annotations

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class PokerTableState(DataClassJSONMixin):
    """Tracks dealer/button and blind positions."""
    button_index: int = 0
    button_player_id: str | None = None

    def advance_button(self, active_ids: list[str]) -> None:
        if not active_ids:
            self.button_index = 0
            self.button_player_id = None
            return
        # Remap button to current active list before advancing
        if self.button_player_id and self.button_player_id in active_ids:
            self.button_index = active_ids.index(self.button_player_id)
        else:
            self.button_index = 0
        self.button_index = (self.button_index + 1) % len(active_ids)
        self.button_player_id = active_ids[self.button_index]

    def get_button_id(self, active_ids: list[str]) -> str | None:
        if not active_ids:
            return None
        if self.button_player_id and self.button_player_id in active_ids:
            return self.button_player_id
        return active_ids[self.button_index % len(active_ids)]

    def get_blind_indices(self, active_ids: list[str]) -> tuple[int, int]:
        if not active_ids:
            return (0, 0)
        if len(active_ids) == 2:
            sb = self.button_index % 2
            bb = (sb + 1) % 2
            return (sb, bb)
        sb = (self.button_index + 1) % len(active_ids)
        bb = (sb + 1) % len(active_ids)
        return (sb, bb)
