"""Tests for shared menu rows, hints, and client-local directives."""

import json
from pathlib import Path

import pytest

from ..core.server import Server
from ..cli import CapturingBot, SpectatorUser
from ..copy_protocol import (
    COPY_DIRECTIVE_VERSION,
    MAX_COPY_FEEDBACK_LENGTH,
    MAX_COPY_TEXT_LENGTH,
    CopyDirective,
    parse_copy_directive,
)
from ..messages.localization import Localization
from ..users.base import MenuItem, menu_selection_targets_server_inert
from ..users.network_user import NetworkUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)
_copy_conformance = json.loads(
    (Path(__file__).parents[2] / "copy_directive_conformance.json").read_text(
        encoding="utf-8"
    )
)


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


def test_missing_localized_hint_is_not_exposed_as_a_raw_key() -> None:
    item = MenuItem(
        text="Safe label",
        id="safe",
        description_key="missing-menu-hint-key",
    )

    packet = item.to_dict(locale="en", show_description=True)

    assert packet == {"text": "Safe label", "id": "safe"}


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


def test_read_only_menu_item_survives_network_render_and_restoration() -> None:
    item = MenuItem(
        text="Confirmation details",
        id="confirmation_summary",
        read_only=True,
    )

    stored = item.to_dict(locale="en", show_description=False)
    restored = Server._restoreable_menu_items([stored])[0]

    assert stored["read_only"] is True
    assert isinstance(restored, MenuItem)
    assert restored.read_only is True


def test_menu_item_without_action_id_uses_explicit_read_only_semantics() -> None:
    item = MenuItem(text="Informational text", id="")

    assert item.read_only is True
    assert item.to_dict() == {
        "text": "Informational text",
        "id": "",
        "read_only": True,
    }


def test_copy_directive_is_validated_serialized_and_restored() -> None:
    directive = CopyDirective(
        text="first\nsecond",
        success_text="Copied two entries.",
        failure_text="Copy failed.",
    )
    item = MenuItem(
        text="Copy page",
        id="copy_page",
        copy_directive=directive,
    )

    stored = item.to_dict()
    restored = Server._restoreable_menu_items([stored])[0]

    assert stored["copy_directive"] == {
        "version": 1,
        "text": "first\nsecond",
        "success_text": "Copied two entries.",
        "failure_text": "Copy failed.",
    }
    assert isinstance(restored, MenuItem)
    assert restored.copy_directive == directive

    with pytest.raises(ValueError):
        MenuItem(text="No id", copy_directive=directive)
    with pytest.raises(ValueError):
        MenuItem(
            text="Information",
            id="info",
            read_only=True,
            copy_directive=directive,
        )
    with pytest.raises(TypeError):
        MenuItem(text="Wrong type", id="copy", copy_directive={})
    with pytest.raises(ValueError):
        MenuItem(text="Wrong id type", id=1, copy_directive=directive)


def test_copy_directive_shared_conformance_corpus() -> None:
    assert _copy_conformance["protocol_version"] == COPY_DIRECTIVE_VERSION
    assert _copy_conformance["limits"] == {
        "text_code_points": MAX_COPY_TEXT_LENGTH,
        "feedback_code_points": MAX_COPY_FEEDBACK_LENGTH,
    }
    for case in _copy_conformance["valid"]:
        assert parse_copy_directive(case["directive"]) is not None, case["name"]
    for case in _copy_conformance["invalid"]:
        assert parse_copy_directive(case["directive"]) is None, case["name"]


def test_copy_directive_boundaries_and_surrogates() -> None:
    common = {
        "version": COPY_DIRECTIVE_VERSION,
        "success_text": "Copied.",
        "failure_text": "Failed.",
    }
    assert parse_copy_directive(
        {**common, "text": "😀" * MAX_COPY_TEXT_LENGTH}
    ) is not None
    assert parse_copy_directive(
        {**common, "text": "x" * (MAX_COPY_TEXT_LENGTH + 1)}
    ) is None
    assert parse_copy_directive(
        {
            **common,
            "text": "payload",
            "success_text": "x" * MAX_COPY_FEEDBACK_LENGTH,
        }
    ) is not None
    assert parse_copy_directive(
        {
            **common,
            "text": "payload",
            "success_text": "x" * (MAX_COPY_FEEDBACK_LENGTH + 1),
        }
    ) is None
    assert parse_copy_directive({**common, "text": "bad\ud800value"}) is None

    class HostileMapping(dict):
        def get(self, *_args, **_kwargs):
            raise RuntimeError("unexpected mapping behavior")

    assert parse_copy_directive(
        HostileMapping({**common, "text": "payload"})
    ) is None


def test_malformed_restored_copy_directive_becomes_informational() -> None:
    restored = Server._restoreable_menu_items(
        [
            {
                "id": "copy_page",
                "text": "Copy page",
                "copy_directive": {
                    "version": 1,
                    "text": "unsafe\u202epayload",
                    "success_text": "Copied.",
                    "failure_text": "Failed.",
                },
            }
        ]
    )[0]

    assert isinstance(restored, MenuItem)
    assert restored.read_only is True
    assert restored.copy_directive is None


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        {},
        {
            "version": True,
            "text": "payload",
            "success_text": "Copied.",
            "failure_text": "Failed.",
        },
        {
            "version": 2,
            "text": "payload",
            "success_text": "Copied.",
            "failure_text": "Failed.",
        },
        {
            "version": 1,
            "text": "payload\x00",
            "success_text": "Copied.",
            "failure_text": "Failed.",
        },
        {
            "version": 1,
            "text": "payload",
            "success_text": "Copied.\u202e",
            "failure_text": "Failed.",
        },
        {
            "version": 1,
            "text": "payload",
            "success_text": "Copied.",
            "failure_text": "Failed.",
            "unexpected": "field",
        },
    ],
)
def test_malformed_copy_directives_fail_closed(value: object) -> None:
    assert parse_copy_directive(value) is None


def test_shared_server_inert_guard_supports_stable_ids_and_legacy_indexes() -> None:
    directive = CopyDirective(
        text="payload",
        success_text="Copied.",
        failure_text="Failed.",
    )
    items = [
        MenuItem(text="Information", id="summary", read_only=True),
        MenuItem(text="Copy", id="copy", copy_directive=directive),
        MenuItem(text="Continue", id="continue"),
    ]

    assert menu_selection_targets_server_inert(items, selection_id="summary")
    assert menu_selection_targets_server_inert(items, selection=1)
    assert menu_selection_targets_server_inert(items, selection_id="copy")
    assert menu_selection_targets_server_inert(items, selection=2)
    assert not menu_selection_targets_server_inert(items, selection_id="continue")
    assert not menu_selection_targets_server_inert(items, selection=3)
    assert menu_selection_targets_server_inert(
        [{"id": "malformed", "copy_directive": None}],
        selection_id="malformed",
    )


def test_restoring_a_mock_style_menu_item_does_not_duplicate_its_hint() -> None:
    rendered = MenuItem(
        text="Play card",
        id="play_card",
        description="Deal one damage.",
    ).rendered("en", show_description=True)

    restored = Server._restoreable_menu_items([rendered])[0]
    rerendered = restored.rendered("en", show_description=True)

    assert rerendered.text == "Play card: Deal one damage."
    assert rerendered.text.count("Deal one damage.") == 1


@pytest.mark.parametrize("user", [SpectatorUser(), CapturingBot("Bot")])
def test_cli_capture_uses_the_shared_menu_hint_renderer(user) -> None:
    item = MenuItem(
        text="Play card",
        id="play_card",
        description="Deal one damage.",
    )

    user.show_menu("turn_menu", [item])

    if isinstance(user, SpectatorUser):
        captured = user._menus["turn_menu"]
    else:
        captured = user.captured_menus[-1]["items"]
    assert captured == ["Play card: Deal one damage."]
