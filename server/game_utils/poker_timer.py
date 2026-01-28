from __future__ import annotations

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class PokerTurnTimer(DataClassJSONMixin):
    """Simple per-turn countdown timer (ticks at 20/s)."""
    ticks_remaining: int = 0

    def start(self, seconds: int) -> None:
        self.ticks_remaining = max(0, seconds) * 20

    def clear(self) -> None:
        self.ticks_remaining = 0

    def tick(self) -> bool:
        if self.ticks_remaining <= 0:
            return False
        self.ticks_remaining -= 1
        return self.ticks_remaining == 0

    def seconds_remaining(self) -> int:
        if self.ticks_remaining <= 0:
            return 0
        return (self.ticks_remaining + 19) // 20
