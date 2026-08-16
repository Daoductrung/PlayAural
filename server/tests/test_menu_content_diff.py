"""Tests for NetworkUser's menu content-diff skip.

A repaint of the menu the client is currently displaying, with identical
content and no explicit focus directive, must not spend a packet: clients
diff same-id menu packets silently, so the resend is pure waste. The skip
must NOT fire when the client has since been shown a different menu or an
editbox (the repaint is then a genuine re-show), nor when the repaint
carries an explicit position/selection_id (a focus directive must reach
the client even if the items are unchanged).
"""

from ..users.base import MenuItem
from ..users.network_user import NetworkUser


def make_user() -> NetworkUser:
    return NetworkUser("Tester", "en", connection=None)


def menu_packets(user: NetworkUser) -> list[dict]:
    return [p for p in user.get_queued_messages() if p.get("type") == "menu"]


def items(*ids: str) -> list[MenuItem]:
    return [MenuItem(text=f"Label {i}", id=i) for i in ids]


def test_identical_reshow_is_skipped() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"), multiletter=False)
    assert len(menu_packets(user)) == 1

    user.show_menu("turn_menu", items("a", "b"), multiletter=False)
    assert menu_packets(user) == []


def test_changed_items_are_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"), multiletter=False)
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "c"), multiletter=False)
    assert len(menu_packets(user)) == 1


def test_changed_grid_layout_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"), grid_enabled=True, grid_width=2)
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"), grid_enabled=True, grid_width=1)
    assert len(menu_packets(user)) == 1


def test_explicit_focus_is_always_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"), selection_id="b")
    packets = menu_packets(user)
    assert len(packets) == 1
    assert packets[0]["selection_id"] == "b"

    user.show_menu("turn_menu", items("a", "b"), position=2)
    packets = menu_packets(user)
    assert len(packets) == 1
    assert packets[0]["position"] == 1  # 1-based -> 0-based


def test_reshow_after_other_menu_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.show_menu("online_users", items("x"))
    user.get_queued_messages()

    # The client now displays online_users; an identical turn_menu repaint
    # is a genuine re-show and must go out.
    user.show_menu("turn_menu", items("a", "b"))
    assert len(menu_packets(user)) == 1


def test_reshow_after_dismissed_editbox_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    user.show_editbox("rename", "New name?")
    user.remove_editbox("rename")
    user.get_queued_messages()

    # An explicitly dismissed editbox must be followed by a full menu paint,
    # even when that menu has the same content as before the input opened.
    user.show_menu("turn_menu", items("a", "b"))
    assert len(menu_packets(user)) == 1


def test_remove_editbox_notifies_remote_client() -> None:
    user = make_user()
    user.show_editbox("action_input_editbox", "Amount?")
    user.get_queued_messages()

    user.remove_editbox("action_input_editbox")

    assert user.get_queued_messages() == [
        {
            "type": "remove_editbox",
            "input_id": "action_input_editbox",
        }
    ]


def test_remove_editbox_forces_next_menu_reshow() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    # Even if server-side recovery did not observe the original request_input,
    # dismissing a possible client overlay invalidates the menu snapshot.
    user.remove_editbox("action_input_editbox")
    user.get_queued_messages()
    user.show_menu("turn_menu", items("a", "b"))

    assert len(menu_packets(user)) == 1


def test_reshow_after_clear_ui_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.clear_ui()
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"))
    assert len(menu_packets(user)) == 1


def test_reshow_after_remove_menu_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.remove_menu("turn_menu")
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"))
    assert len(menu_packets(user)) == 1


def test_positioned_show_then_plain_identical_reshow_is_skipped() -> None:
    # position is a one-shot focus directive, not content: after a positioned
    # show, a plain repaint with the same items is still a client-side no-op.
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"), position=2)
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"))
    assert menu_packets(user) == []


def test_update_menu_identical_is_skipped() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    user.update_menu("turn_menu", items("a", "b"))
    assert menu_packets(user) == []


def test_update_menu_changed_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    user.update_menu("turn_menu", items("a", "b", "c"))
    assert len(menu_packets(user)) == 1


def test_update_menu_with_focus_is_sent() -> None:
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.get_queued_messages()

    user.update_menu("turn_menu", items("a", "b"), selection_id="b")
    assert len(menu_packets(user)) == 1


def test_skip_keeps_stored_state_current() -> None:
    # A skipped repaint must still refresh the stored state, so a later
    # genuinely-changed repaint diffs against the right baseline.
    user = make_user()
    user.show_menu("turn_menu", items("a", "b"))
    user.show_menu("turn_menu", items("a", "b"))  # skipped
    user.get_queued_messages()

    user.show_menu("turn_menu", items("a", "b"))  # still identical, skipped
    assert menu_packets(user) == []
