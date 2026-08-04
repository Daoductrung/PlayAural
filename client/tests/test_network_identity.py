"""Desktop identity synchronization tests."""

from pathlib import Path
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from network_manager import NetworkManager
from ui.login_dialog import _find_saved_account_id


class _Window:
    def __init__(self):
        self.authorize_packet = None

    def IsShown(self):
        return True

    def on_authorize_success(self, packet):
        self.authorize_packet = packet


def test_authorize_success_replaces_typed_username_with_registered_casing():
    window = _Window()
    network = NetworkManager(window)
    network.username = "nguyễn văn an"
    packet = {
        "type": "authorize_success",
        "username": "Nguyễn Văn An",
    }

    network._handle_packet(packet)

    assert network.username == "Nguyễn Văn An"
    assert window.authorize_packet is packet


def test_saved_account_matching_does_not_merge_legacy_fold_collision():
    accounts = {
        "first": {"username": "Straße"},
        "typed": {"username": "trung"},
        "canonical": {"username": "Nguyễn Văn An"},
    }

    assert _find_saved_account_id(accounts, "trung", "Trung") == "typed"
    assert (
        _find_saved_account_id(accounts, "nguyễn văn an", "Nguyễn Văn An")
        == "canonical"
    )
    assert _find_saved_account_id(accounts, "STRASSE", "STRASSE") is None


def test_saved_account_matching_never_overwrites_unrelated_selected_account():
    accounts = {
        "selected": {"username": "Alice"},
        "matching": {"username": "trung"},
    }

    assert (
        _find_saved_account_id(
            accounts,
            "trung",
            "Trung",
            preferred_account_id="selected",
        )
        == "matching"
    )
    assert (
        _find_saved_account_id(
            accounts,
            "bob",
            "Bob",
            preferred_account_id="selected",
        )
        is None
    )
    assert (
        _find_saved_account_id(
            accounts,
            "Alice",
            "Alice",
            preferred_account_id="selected",
        )
        == "selected"
    )
