"""Rules profiles for Sorry."""

from dataclasses import dataclass
from typing import Protocol


class SorryRulesProfile(Protocol):
    profile_id: str
    display_name: str
    pawns_per_player: int

    def card_faces(self) -> tuple[str, ...]:
        ...

    def can_leave_start_with_card(self, card_face: str) -> bool:
        ...

    def forward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        ...

    def backward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        ...

    def allows_split_seven(self, card_face: str) -> bool:
        ...

    def allows_swap(self, card_face: str) -> bool:
        ...

    def allows_sorry(self, card_face: str) -> bool:
        ...

    def sorry_fallback_forward_steps(self, card_face: str) -> tuple[int, ...]:
        ...

    def card_two_grants_extra_turn(self) -> bool:
        ...

    def slide_policy_id(self) -> str:
        ...


@dataclass(frozen=True)
class Classic00390Rules:
    profile_id: str = "classic_00390"
    display_name: str = "Classic 00390"
    pawns_per_player: int = 4
    _faces: tuple[str, ...] = (
        "1",
        "2",
        "3",
        "4",
        "5",
        "7",
        "8",
        "10",
        "11",
        "12",
        "sorry",
    )

    def card_faces(self) -> tuple[str, ...]:
        return self._faces

    def can_leave_start_with_card(self, card_face: str) -> bool:
        return card_face in {"1", "2"}

    def forward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        if card_face in {"1", "2", "3", "5", "7", "8", "10", "11", "12"}:
            return (int(card_face),)
        return ()

    def backward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        if card_face == "4":
            return (4,)
        if card_face == "10":
            return (1,)
        return ()

    def allows_split_seven(self, card_face: str) -> bool:
        return card_face == "7"

    def allows_swap(self, card_face: str) -> bool:
        return card_face == "11"

    def allows_sorry(self, card_face: str) -> bool:
        return card_face == "sorry"

    def sorry_fallback_forward_steps(self, card_face: str) -> tuple[int, ...]:
        _ = card_face
        return ()

    def card_two_grants_extra_turn(self) -> bool:
        return True

    def slide_policy_id(self) -> str:
        return "classic_00390"


_CLASSIC_00390_RULES = Classic00390Rules()


@dataclass(frozen=True)
class A5065CoreRules:
    profile_id: str = "a5065_core"
    display_name: str = "A5065 Core"
    pawns_per_player: int = 3

    def card_faces(self) -> tuple[str, ...]:
        return _CLASSIC_00390_RULES.card_faces()

    def can_leave_start_with_card(self, card_face: str) -> bool:
        return bool(self.forward_steps_for_card(card_face))

    def forward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        return _CLASSIC_00390_RULES.forward_steps_for_card(card_face)

    def backward_steps_for_card(self, card_face: str) -> tuple[int, ...]:
        return _CLASSIC_00390_RULES.backward_steps_for_card(card_face)

    def allows_split_seven(self, card_face: str) -> bool:
        return _CLASSIC_00390_RULES.allows_split_seven(card_face)

    def allows_swap(self, card_face: str) -> bool:
        return _CLASSIC_00390_RULES.allows_swap(card_face)

    def allows_sorry(self, card_face: str) -> bool:
        return _CLASSIC_00390_RULES.allows_sorry(card_face)

    def sorry_fallback_forward_steps(self, card_face: str) -> tuple[int, ...]:
        if card_face == "sorry":
            return (4,)
        return ()

    def card_two_grants_extra_turn(self) -> bool:
        return False

    def slide_policy_id(self) -> str:
        return "a5065_core"


RULES_PROFILES: dict[str, SorryRulesProfile] = {
    "classic_00390": _CLASSIC_00390_RULES,
    "a5065_core": A5065CoreRules(),
}


def get_rules_profile_by_id(profile_id: str | None) -> SorryRulesProfile | None:
    if profile_id is None:
        return None
    return RULES_PROFILES.get(profile_id)


def get_supported_profile_ids() -> tuple[str, ...]:
    return tuple(RULES_PROFILES.keys())
