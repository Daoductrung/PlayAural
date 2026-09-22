"""Serialized ground-item and buy-transaction state for Breach Point."""

from dataclasses import dataclass


@dataclass
class DroppedWeapon:
    """One recoverable firearm at an authoritative spatial position."""

    drop_id: int
    weapon_id: str
    node_id: str
    grid_x: int
    grid_y: int
    magazine_ammo: int
    reserve_units: int


@dataclass
class BuyTransaction:
    """One reversible purchase made during the current player's buy turn."""

    player_id: str
    item_kind: str
    item_id: str
    cost: int
    previous_amount: int = 0
    dropped_weapon_id: int = 0


@dataclass
class PendingWeaponDonation:
    """One paid teammate weapon awaiting an accept-or-drop response."""

    buyer_id: str
    recipient_id: str
    weapon_id: str
    cost: int
