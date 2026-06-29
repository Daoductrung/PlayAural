"""Reusable helpers for server-owned paginated menus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Sequence, TypeVar

from .messages.localization import Localization
from .users.base import MenuItem

DEFAULT_MENU_PAGE_SIZE = 100
MAX_MENU_PAGE_SIZE = 100
MENU_PAGE_FIRST = "page_first"
MENU_PAGE_PREVIOUS = "page_previous"
MENU_PAGE_NEXT = "page_next"
MENU_PAGE_LAST = "page_last"
MENU_PAGE_REFRESH = "refresh"
MENU_PAGE_IDS = frozenset(
    {
        MENU_PAGE_FIRST,
        MENU_PAGE_PREVIOUS,
        MENU_PAGE_NEXT,
        MENU_PAGE_LAST,
        MENU_PAGE_REFRESH,
    }
)

T = TypeVar("T")


def normalize_page_size(page_size: int) -> int:
    """Clamp menu page sizes so accidental huge renders cannot reach clients."""
    return max(1, min(int(page_size), MAX_MENU_PAGE_SIZE))


def total_pages_for(total: int, page_size: int) -> int:
    """Return at least one page so empty lists still have stable page state."""
    page_size = normalize_page_size(page_size)
    return max(1, (max(0, int(total)) + page_size - 1) // page_size)


def clamp_page(page: int, total: int, page_size: int) -> int:
    """Clamp a requested page into the range available for a total count."""
    try:
        requested = int(page)
    except (TypeError, ValueError):
        requested = 1
    return min(max(1, requested), total_pages_for(total, page_size))


def page_for_selection(
    selection_id: str,
    current_page: int,
    page_count: int,
) -> int | None:
    """Resolve a pagination control id into the page it should display."""
    if selection_id not in MENU_PAGE_IDS:
        return None
    try:
        safe_current = int(current_page)
    except (TypeError, ValueError):
        safe_current = 1
    try:
        safe_count = max(1, int(page_count))
    except (TypeError, ValueError):
        safe_count = 1

    safe_current = min(max(1, safe_current), safe_count)
    if selection_id == MENU_PAGE_FIRST:
        return 1
    if selection_id == MENU_PAGE_PREVIOUS:
        return max(1, safe_current - 1)
    if selection_id == MENU_PAGE_NEXT:
        return min(safe_count, safe_current + 1)
    if selection_id == MENU_PAGE_LAST:
        return safe_count
    if selection_id == MENU_PAGE_REFRESH:
        return safe_current
    return None


def is_page_refresh(selection_id: str) -> bool:
    """Return True when the pagination action is a manual refresh request."""
    return selection_id == MENU_PAGE_REFRESH


def is_page_navigation(selection_id: str) -> bool:
    """Return True when the pagination action moves to a different page area."""
    return selection_id in {
        MENU_PAGE_FIRST,
        MENU_PAGE_PREVIOUS,
        MENU_PAGE_NEXT,
        MENU_PAGE_LAST,
    }


@dataclass(frozen=True)
class PaginatedMenuPage(Generic[T]):
    """A page of menu rows plus display metadata for accessible summaries."""

    items: list[T]
    total: int
    page: int
    page_size: int = DEFAULT_MENU_PAGE_SIZE

    @property
    def total_pages(self) -> int:
        return total_pages_for(self.total, self.page_size)

    @property
    def start_index(self) -> int:
        if self.total <= 0:
            return 0
        return (self.page - 1) * self.page_size + 1

    @property
    def end_index(self) -> int:
        if self.total <= 0:
            return 0
        return min(self.total, self.page * self.page_size)

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


def paginate_sequence(
    items: Sequence[T],
    page: int,
    *,
    page_size: int = DEFAULT_MENU_PAGE_SIZE,
) -> PaginatedMenuPage[T]:
    """Return a bounded page from an in-memory sequence."""
    page_size = normalize_page_size(page_size)
    total = len(items)
    safe_page = clamp_page(page, total, page_size)
    offset = (safe_page - 1) * page_size
    return PaginatedMenuPage(
        items=list(items[offset : offset + page_size]),
        total=total,
        page=safe_page,
        page_size=page_size,
    )


def pagination_menu_items(
    locale: str,
    page_data: PaginatedMenuPage[Any],
    *,
    include_refresh: bool = False,
) -> list[MenuItem]:
    """Build standard accessible pagination controls for a server menu."""
    controls: list[MenuItem] = []
    if include_refresh and page_data.total > 0:
        controls.append(
            MenuItem(
                text=Localization.get(locale, "menu-page-refresh"),
                id=MENU_PAGE_REFRESH,
            )
        )
    if page_data.total_pages <= 1:
        return controls

    for enabled, key, item_id in (
        (page_data.has_previous, "menu-page-first", MENU_PAGE_FIRST),
        (page_data.has_previous, "menu-page-previous", MENU_PAGE_PREVIOUS),
        (page_data.has_next, "menu-page-next", MENU_PAGE_NEXT),
        (page_data.has_next, "menu-page-last", MENU_PAGE_LAST),
    ):
        if not enabled:
            continue
        controls.append(
            MenuItem(
                text=Localization.get(locale, key),
                id=item_id,
            )
        )
    return controls
