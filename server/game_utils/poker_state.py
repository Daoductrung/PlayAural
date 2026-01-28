"""Shared helpers for poker seat ordering."""

from __future__ import annotations


def order_after_button(active_ids: list[str], button_id: str | None) -> list[str]:
    """Return seat order starting left of the button."""
    if not active_ids:
        return []
    if button_id and button_id in active_ids:
        start_index = (active_ids.index(button_id) + 1) % len(active_ids)
        return active_ids[start_index:] + active_ids[:start_index]
    return active_ids
