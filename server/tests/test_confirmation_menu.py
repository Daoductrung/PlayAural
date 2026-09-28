from __future__ import annotations

import pytest

from ..ui.confirmation import (
    CONFIRMATION_PROMPT_ITEM_ID,
    ConfirmationChoice,
    show_confirmation_menu,
)
from ..users.base import EscapeBehavior, MenuItem
from ..users.test_user import MockUser


def _item_ids(user: MockUser, menu_id: str) -> list[str | None]:
    return [item.id for item in user.menus[menu_id]["items"]]


def test_confirmation_menu_announces_and_exposes_the_same_prompt() -> None:
    user = MockUser("Alice", locale="en")

    show_confirmation_menu(
        user,
        "remove_friend_confirmation",
        prompt_key="friend-remove-confirm",
        prompt_kwargs={"username": "Bob"},
        buffer="system",
    )

    menu = user.menus["remove_friend_confirmation"]
    prompt = menu["items"][0]
    assert prompt.id == CONFIRMATION_PROMPT_ITEM_ID
    assert prompt.read_only is True
    assert prompt.text == "Remove Bob from your friends list?"
    assert _item_ids(user, "remove_friend_confirmation") == [
        CONFIRMATION_PROMPT_ITEM_ID,
        "yes",
        "no",
    ]
    assert menu["selection_id"] == CONFIRMATION_PROMPT_ITEM_ID
    assert menu["escape_behavior"] is EscapeBehavior.SELECT_LAST
    assert menu["multiletter"] is False
    assert user.get_last_spoken() == prompt.text
    assert user.messages[-2].data["buffer"] == "system"


def test_confirmation_menu_orders_context_alternatives_and_cancel_safely() -> None:
    user = MockUser("Alice", locale="en")
    detail = MenuItem(text="Review detail", id="detail", read_only=True)

    show_confirmation_menu(
        user,
        "report_confirmation",
        prompt_key="report-confirm-summary",
        prompt_kwargs={
            "username": "Bob",
            "reason": "Spam",
            "channel": "English",
        },
        confirm_choice=ConfirmationChoice("submit", "report-submit"),
        alternative_choices=(
            ConfirmationChoice("change_reason", "report-change-reason"),
        ),
        cancel_choice=ConfirmationChoice("back", "back"),
        context_items=(detail,),
        buffer="system",
    )

    assert _item_ids(user, "report_confirmation") == [
        CONFIRMATION_PROMPT_ITEM_ID,
        "detail",
        "submit",
        "change_reason",
        "back",
    ]
    assert user.menus["report_confirmation"]["items"][-1].text == "Back"


def test_confirmation_menu_rejects_actionable_context_and_duplicate_ids() -> None:
    user = MockUser("Alice", locale="en")

    with pytest.raises(ValueError, match="server-inert"):
        show_confirmation_menu(
            user,
            "unsafe_confirmation",
            prompt_key="logout-confirm-title",
            context_items=(MenuItem(text="Unexpected action", id="action"),),
            buffer="system",
        )

    with pytest.raises(ValueError, match="unique"):
        show_confirmation_menu(
            user,
            "duplicate_confirmation",
            prompt_key="logout-confirm-title",
            confirm_choice=ConfirmationChoice("same", "confirm-yes"),
            cancel_choice=ConfirmationChoice("same", "confirm-no"),
            buffer="system",
        )
