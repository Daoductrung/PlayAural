"""Shared menu focus restoration helpers for the desktop client."""

from collections.abc import Sequence


def _stable_item_id(item_id: object) -> str | None:
    if isinstance(item_id, str) and item_id:
        return item_id
    return None


def _unique_index_by_id(item_ids: Sequence[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    indices: dict[str, int] = {}
    for index, candidate in enumerate(item_ids):
        item_id = _stable_item_id(candidate)
        if item_id is None:
            continue
        counts[item_id] = counts.get(item_id, 0) + 1
        indices[item_id] = index
    return {item_id: indices[item_id] for item_id, count in counts.items() if count == 1}


def _clamp_index(index: int, length: int) -> int:
    if length <= 0:
        return 0
    return max(0, min(length - 1, index))


def resolve_menu_focus_index(
    old_item_ids: Sequence[object],
    new_item_ids: Sequence[object],
    old_index: int,
    *,
    same_menu: bool,
    explicit_index: int | None = None,
) -> int:
    """Choose the least-surprising focus index after a menu repaint.

    Explicit server focus wins. Same-menu refreshes then preserve the focused
    stable id when possible. If that row disappeared, focus lands on the first
    subsequent stable row from the old logical order that still exists, or the
    nearest previous stable row. Numeric fallback is only used when no stable
    relationship survives.
    """

    if not new_item_ids:
        return 0

    if isinstance(explicit_index, int):
        return _clamp_index(explicit_index, len(new_item_ids))

    if not same_menu:
        return 0

    if not old_item_ids:
        return 0

    bounded_old_index = _clamp_index(old_index, len(old_item_ids))
    old_unique_indices = _unique_index_by_id(old_item_ids)
    new_unique_indices = _unique_index_by_id(new_item_ids)

    old_focused_id = _stable_item_id(old_item_ids[bounded_old_index])
    if old_focused_id in old_unique_indices and old_focused_id in new_unique_indices:
        return new_unique_indices[old_focused_id]

    for index in range(bounded_old_index + 1, len(old_item_ids)):
        candidate_id = _stable_item_id(old_item_ids[index])
        if candidate_id in old_unique_indices and candidate_id in new_unique_indices:
            return new_unique_indices[candidate_id]

    for index in range(bounded_old_index - 1, -1, -1):
        candidate_id = _stable_item_id(old_item_ids[index])
        if candidate_id in old_unique_indices and candidate_id in new_unique_indices:
            return new_unique_indices[candidate_id]

    return _clamp_index(old_index, len(new_item_ids))
