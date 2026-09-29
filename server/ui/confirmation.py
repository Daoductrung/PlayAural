"""Shared, accessible confirmation-menu presentation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from ..audio import AUDIO_OUTPUT_BUFFERS
from ..messages.localization import Localization
from ..users.base import EscapeBehavior, MenuItem, User

CONFIRMATION_PROMPT_ITEM_ID = "confirmation_prompt"


@dataclass(frozen=True, slots=True)
class ConfirmationChoice:
    """One localized action in a confirmation menu."""

    id: str
    label_key: str
    label_kwargs: Mapping[str, Any] = field(default_factory=dict, hash=False)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id or self.id.strip() != self.id:
            raise ValueError("Confirmation choice ids must be non-empty stable tokens")
        if (
            not isinstance(self.label_key, str)
            or not self.label_key
            or self.label_key.strip() != self.label_key
        ):
            raise ValueError("Confirmation choice label keys must be non-empty")
        if not isinstance(self.label_kwargs, Mapping):
            raise TypeError("Confirmation choice label kwargs must be a mapping")
        object.__setattr__(
            self,
            "label_kwargs",
            MappingProxyType(dict(self.label_kwargs)),
        )

    def to_menu_item(self, locale: str) -> MenuItem:
        """Build the localized actionable menu row."""
        return MenuItem(
            text=Localization.get(locale, self.label_key, **self.label_kwargs),
            id=self.id,
        )


YES_CONFIRMATION_CHOICE = ConfirmationChoice("yes", "confirm-yes")
NO_CONFIRMATION_CHOICE = ConfirmationChoice("no", "confirm-no")


def show_confirmation_menu(
    user: User,
    menu_id: str,
    *,
    prompt_key: str,
    buffer: str,
    prompt_kwargs: Mapping[str, Any] | None = None,
    confirm_choice: ConfirmationChoice = YES_CONFIRMATION_CHOICE,
    cancel_choice: ConfirmationChoice = NO_CONFIRMATION_CHOICE,
    alternative_choices: Sequence[ConfirmationChoice] = (),
    context_items: Sequence[MenuItem] = (),
    capture_focus_context_id: str | None = None,
) -> None:
    """Announce and display one consistently ordered confirmation menu.

    The prompt is the initial focus target and remains available for review.
    Context rows must be server-inert. The cancel choice is always last so the
    shared Escape behavior cannot accidentally select a destructive action.
    """
    if not isinstance(menu_id, str) or not menu_id or menu_id.strip() != menu_id:
        raise ValueError("Confirmation menu ids must be non-empty stable tokens")
    if (
        not isinstance(prompt_key, str)
        or not prompt_key
        or prompt_key.strip() != prompt_key
    ):
        raise ValueError("Confirmation prompt keys must be non-empty")
    if buffer not in AUDIO_OUTPUT_BUFFERS:
        raise ValueError("Confirmation announcements require a canonical buffer")
    if prompt_kwargs is not None and not isinstance(prompt_kwargs, Mapping):
        raise TypeError("Confirmation prompt kwargs must be a mapping")

    choices = [confirm_choice, *alternative_choices, cancel_choice]
    if not all(isinstance(choice, ConfirmationChoice) for choice in choices):
        raise TypeError("Confirmation choices must be ConfirmationChoice instances")
    choice_ids = [choice.id for choice in choices]
    if len(set(choice_ids)) != len(choice_ids):
        raise ValueError("Confirmation choice ids must be unique")
    if CONFIRMATION_PROMPT_ITEM_ID in choice_ids:
        raise ValueError("Confirmation choices cannot use the prompt item id")

    normalized_context = list(context_items)
    for item in normalized_context:
        if not isinstance(item, MenuItem):
            raise TypeError("Confirmation context rows must be MenuItem instances")
        if not item.read_only and item.copy_directive is None:
            raise ValueError("Confirmation context rows must be server-inert")
    context_ids = [item.id for item in normalized_context if item.id]
    all_ids = [CONFIRMATION_PROMPT_ITEM_ID, *context_ids, *choice_ids]
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("Confirmation menu item ids must be unique")

    localized_kwargs = dict(prompt_kwargs or {})
    prompt_text = Localization.get(user.locale, prompt_key, **localized_kwargs)
    items = [
        MenuItem(
            text=prompt_text,
            id=CONFIRMATION_PROMPT_ITEM_ID,
            read_only=True,
        ),
        *normalized_context,
        *(choice.to_menu_item(user.locale) for choice in choices),
    ]

    user.speak_l(prompt_key, buffer=buffer, **localized_kwargs)
    user.show_menu(
        menu_id,
        items,
        multiletter=False,
        escape_behavior=EscapeBehavior.SELECT_LAST,
        selection_id=CONFIRMATION_PROMPT_ITEM_ID,
        capture_focus_context_id=capture_focus_context_id,
    )


__all__ = [
    "CONFIRMATION_PROMPT_ITEM_ID",
    "NO_CONFIRMATION_CHOICE",
    "YES_CONFIRMATION_CHOICE",
    "ConfirmationChoice",
    "show_confirmation_menu",
]
