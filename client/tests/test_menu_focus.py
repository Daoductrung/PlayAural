from ui.menu_focus import resolve_menu_focus_index


def test_explicit_menu_focus_wins_and_clamps() -> None:
    assert resolve_menu_focus_index(
        ["old"],
        ["first", "second"],
        0,
        same_menu=True,
        explicit_index=8,
    ) == 1


def test_same_menu_focus_follows_surviving_item_identity() -> None:
    assert resolve_menu_focus_index(
        ["a", "focused", "c"],
        ["c", "a", "focused"],
        1,
        same_menu=True,
    ) == 2


def test_removed_focus_lands_on_next_surviving_logical_neighbor() -> None:
    assert resolve_menu_focus_index(
        [
            "toggle_select_queen_hearts",
            "play_selected",
            "pass",
            "check_trick",
            "read_hand",
        ],
        ["check_trick", "read_hand"],
        0,
        same_menu=True,
    ) == 0


def test_removed_focus_lands_on_previous_neighbor_when_no_next_survives() -> None:
    assert resolve_menu_focus_index(
        ["read_hand", "check_trick", "removed"],
        ["read_hand", "check_trick"],
        2,
        same_menu=True,
    ) == 1


def test_numeric_fallback_only_when_no_stable_relationship_survives() -> None:
    assert resolve_menu_focus_index(
        [None, "", "removed"],
        ["new_a", "new_b"],
        2,
        same_menu=True,
    ) == 1


def test_empty_new_menu_returns_zero() -> None:
    assert resolve_menu_focus_index(
        ["a"],
        [],
        0,
        same_menu=True,
    ) == 0


def test_duplicate_ids_are_not_used_as_stable_anchors() -> None:
    assert resolve_menu_focus_index(
        ["dup", "dup", "next"],
        ["dup", "next"],
        0,
        same_menu=True,
    ) == 1
