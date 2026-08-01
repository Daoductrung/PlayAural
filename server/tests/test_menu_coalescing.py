"""Menu-send coalescing in NetworkUser.get_queued_messages.

A single user action commonly triggers more than one menu repaint on the same
tick — an action handler rebuilds the menu and the event framework rebuilds it
again. Those redundant repaints used to reach the client as separate packets,
causing double screen-reader announcements and double focus churn (e.g.
Citadels). The flush now collapses same-menu_id `menu` packets to the last one.
"""

from server.users.network_user import NetworkUser
from server.users.base import MenuItem


def _items(*ids):
    return [MenuItem(text=i, id=i) for i in ids]


def _user():
    return NetworkUser("alice", "en", connection=object())


def test_duplicate_menu_sends_collapse_to_last():
    user = _user()
    user.show_menu("turn_menu", _items("a", "b"))
    user.update_menu("turn_menu", _items("a", "b", "c"))  # redundant second repaint

    menus = [m for m in user.get_queued_messages() if m["type"] == "menu"]
    assert len(menus) == 1
    assert [i["id"] for i in menus[0]["items"]] == ["a", "b", "c"]  # last state wins


def test_non_menu_packets_preserved_in_order():
    user = _user()
    user.speak("one")
    user.show_menu("turn_menu", _items("a"))
    user.play_sound("ding.ogg")
    user.update_menu("turn_menu", _items("a", "b"))
    user.speak("two")

    msgs = user.get_queued_messages()
    # The earlier turn_menu repaint is dropped; speaks and the sound keep order.
    assert [m["type"] for m in msgs] == ["speak", "audio", "menu", "speak"]
    assert msgs[1]["command"] == "play"
    assert msgs[1]["kind"] == "sfx"
    assert msgs[0]["text"] == "one"
    assert msgs[-1]["text"] == "two"


def test_distinct_menu_ids_both_survive():
    user = _user()
    user.show_menu("turn_menu", _items("a"))
    user.show_menu("status_box", _items("x"))

    menus = [m for m in user.get_queued_messages() if m["type"] == "menu"]
    assert {m["menu_id"] for m in menus} == {"turn_menu", "status_box"}


def test_quiet_remove_forgets_overlay_without_blank_menu_packet():
    user = _user()
    user.show_menu("status_box", _items("summary"))
    user.get_queued_messages()

    user.remove_menu("status_box", send_packet=False)
    user.show_menu("turn_menu", _items("roll"))

    menus = [m for m in user.get_queued_messages() if m["type"] == "menu"]
    assert [m["menu_id"] for m in menus] == ["turn_menu"]
    assert [item["id"] for item in menus[0]["items"]] == ["roll"]


def test_focus_intent_survives_a_later_blanket_rebuild():
    # The real 99 land-on-drawn-card ordering: the handler targets the drawn
    # card's slot, then the event framework fires a post-action rebuild with no
    # focus on the same tick. The targeted focus must survive the later repaint.
    user = _user()
    user.update_menu(
        "turn_menu", _items("card_slot_1", "card_slot_2"), selection_id="card_slot_2"
    )
    user.show_menu("turn_menu", _items("card_slot_1", "card_slot_2"))  # blanket rebuild

    menus = [m for m in user.get_queued_messages() if m["type"] == "menu"]
    assert len(menus) == 1
    assert menus[0]["selection_id"] == "card_slot_2"


def test_latest_explicit_focus_wins():
    user = _user()
    user.update_menu("turn_menu", _items("a", "b", "c"), selection_id="a")
    user.update_menu("turn_menu", _items("a", "b", "c"), selection_id="c")

    menus = [m for m in user.get_queued_messages() if m["type"] == "menu"]
    assert len(menus) == 1
    assert menus[0]["selection_id"] == "c"
