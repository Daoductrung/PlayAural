from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class PokerPot(DataClassJSONMixin):
    amount: int
    eligible_player_ids: set[str] = field(default_factory=set)


@dataclass
class PokerPotManager(DataClassJSONMixin):
    """Track contributions and compute main/side pots."""

    contributions: dict[str, int] = field(default_factory=dict)
    folded: set[str] = field(default_factory=set)

    def reset(self) -> None:
        self.contributions.clear()
        self.folded.clear()

    def add_contribution(self, player_id: str, amount: int) -> None:
        if amount <= 0:
            return
        self.contributions[player_id] = self.contributions.get(player_id, 0) + amount

    def mark_folded(self, player_id: str) -> None:
        self.folded.add(player_id)

    def total_pot(self) -> int:
        return sum(self.contributions.values())

    def get_pots(self) -> list[PokerPot]:
        """Compute main/side pots from contributions."""
        amounts = [amt for amt in self.contributions.values() if amt > 0]
        if not amounts:
            return []

        levels = sorted(set(amounts))
        pots: list[PokerPot] = []
        prev = 0
        for level in levels:
            contributors = [pid for pid, amt in self.contributions.items() if amt >= level]
            pot_amount = (level - prev) * len(contributors)
            if pot_amount <= 0:
                prev = level
                continue
            eligible = {pid for pid in contributors if pid not in self.folded}
            pots.append(PokerPot(amount=pot_amount, eligible_player_ids=eligible))
            prev = level
        return pots
