"""Shared betting helpers for poker games."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PotLimitCaps:
    """Pot-limit caps for a bet."""

    total_cap: int


def compute_pot_limit_caps(
    pot_total: int,
    to_call: int,
    raise_mode: str,
) -> Optional[PotLimitCaps]:
    """Return total bet caps for pot-limit/double-pot modes."""
    if raise_mode == "no_limit":
        return None
    total_cap = pot_total + to_call * 2
    if raise_mode == "double_pot":
        total_cap = pot_total * 2 + to_call * 2
    return PotLimitCaps(total_cap=total_cap)


def clamp_total_to_cap(total: int, caps: Optional[PotLimitCaps]) -> int:
    if not caps:
        return total
    return min(total, caps.total_cap)
