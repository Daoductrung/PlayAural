"""Tests for the shared, preference-aware menu hint API."""

from pathlib import Path

import pytest

from ..core.server import Server
from ..messages.localization import Localization
from ..users.base import MenuItem
from ..users.network_user import NetworkUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def _menu_packets(user: NetworkUser) -> list[dict]:
    return [
        packet
        for packet in user.get_queued_messages()
        if packet.get("type") == "menu"
    ]


def test_menu_item_renders_localized_and_dynamic_hints() -> None:
    dynamic = MenuItem(
        text="Play card",
        id="play_card",
        description="Deal one damage.",
    )
    localized = MenuItem(
        text="Menu Hints",
        id="menu_hints",
        description_key="general-desc-menu-hints",
    )
    parameterized = MenuItem(
        text="Rounds",
        description_key="option-desc-integer",
        description_kwargs={
            "label": "Rounds",
            "min": 1,
            "max": 10,
            "default": 3,
        },
    )

    dynamic_packet = dynamic.to_dict(locale="en", show_description=True)
    localized_packet = localized.to_dict(locale="en", show_description=True)
    parameterized_packet = parameterized.to_dict(
        locale="en",
        show_description=True,
    )

    assert dynamic_packet["text"] == "Play card: Deal one damage."
    assert dynamic_packet["label"] == "Play card"
    assert dynamic_packet["description"] == "Deal one damage."
    assert "Show available descriptions directly in menu rows" in localized_packet["text"]
    assert "whole number from 1 to 10" in parameterized_packet["text"]


def test_menu_item_rejects_two_description_sources() -> None:
    with pytest.raises(ValueError):
        MenuItem(
            text="Invalid",
            description="Already localized",
            description_key="general-desc-menu-hints",
        )


def test_network_menu_repaints_when_hint_preference_changes() -> None:
    user = NetworkUser("Tester", "en", connection=None)
    items = [
        MenuItem(
            text="Play card",
            id="play_card",
            description="Deal one damage.",
        )
    ]

    user.show_menu("turn_menu", items)
    first_packet = _menu_packets(user)[0]
    assert first_packet["items"][0]["text"] == "Play card: Deal one damage."

    user.preferences.show_menu_hints = False
    user.show_menu("turn_menu", items)
    second_packet = _menu_packets(user)[0]
    assert second_packet["items"][0]["text"] == "Play card"
    assert second_packet["items"][0]["description"] == "Deal one damage."


def test_restoring_a_rendered_menu_does_not_duplicate_its_hint() -> None:
    item = MenuItem(
        text="Play card",
        id="play_card",
        description="Deal one damage.",
    )
    stored = item.to_dict(locale="en", show_description=True)

    restored = Server._restoreable_menu_items([stored])[0]
    restored_packet = restored.to_dict(locale="en", show_description=True)

    assert restored_packet["text"] == "Play card: Deal one damage."
    assert restored_packet["text"].count("Deal one damage.") == 1
