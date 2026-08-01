import asyncio
from unittest.mock import MagicMock

import pytest

from server.core import server as server_module
from server.core.server import Server
from server.persistence.database import Database
from server.users.network_user import NetworkUser
from server.users.preferences import UserPreferences


class _Client:
    def __init__(self, address: str):
        self.address = address
        self.ip_address = "127.0.0.1"
        self.username = None
        self.authenticated = False
        self.retired = False
        self.session_ready = False
        self.sent_messages = []

    async def send(self, message):
        self.sent_messages.append(message)


class _WebSocketRegistry:
    def __init__(self):
        self._clients_by_address = {}
        self._clients_by_username = {}

    def bind(self, client):
        self._clients_by_address[client.address] = client

    def get_client_by_username(self, username):
        return self._clients_by_username.get(username)

    def register_client_username(self, address, username):
        self._clients_by_username[username] = self._clients_by_address[address]

    def unregister_client_username(self, username, client):
        if self._clients_by_username.get(username) is client:
            self._clients_by_username.pop(username, None)


@pytest.fixture
def presence_server(tmp_path):
    db_path = tmp_path / "presence.db"
    db = Database(str(db_path))
    db.connect()
    server = Server(db_path=str(db_path))
    server._db = db
    yield server
    for task in server._pending_disconnects.values():
        task.cancel()
    for task in server._pending_session_state_cleanups.values():
        task.cancel()
    db.close()


def _create_account(
    server: Server,
    username: str,
    *,
    trust_level: int = 1,
):
    record = server._db.create_user(
        username,
        "hash",
        trust_level=trust_level,
        approved=True,
    )
    assert record is not None
    return record


def _add_recipient(
    server: Server,
    record,
    *,
    notify_users: bool,
    notify_friends: bool,
    approved: bool = True,
) -> NetworkUser:
    user = NetworkUser(
        record.username,
        record.locale,
        MagicMock(),
        uuid=record.uuid,
        preferences=UserPreferences(
            notify_user_presence=notify_users,
            notify_friend_presence=notify_friends,
        ),
        approved=approved,
    )
    user.speak_l = MagicMock()
    user.play_sound = MagicMock()
    server._users[user.username] = user
    return user


def _make_friends(server: Server, first, second) -> None:
    assert server._db.send_friend_request(first.uuid, second.uuid) == "sent"
    assert server._db.accept_friend_request(first.uuid, second.uuid)


@pytest.mark.parametrize(
    ("is_online", "trust_level", "expected_message", "expected_sound"),
    [
        (True, 2, "friend-online", "onlineadmin.ogg"),
        (False, 2, "friend-offline", "offlineadmin.ogg"),
        (True, 3, "friend-online", "onlinedev.ogg"),
        (False, 3, "friend-offline", "offlinedev.ogg"),
    ],
)
def test_privileged_friend_presence_uses_role_sound(
    presence_server,
    is_online,
    trust_level,
    expected_message,
    expected_sound,
):
    target = _create_account(
        presence_server,
        "PrivilegedFriend",
        trust_level=trust_level,
    )
    recipient_record = _create_account(presence_server, "Recipient")
    _make_friends(presence_server, target, recipient_record)
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=False,
        notify_friends=True,
    )

    assert presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=trust_level,
        is_online=is_online,
    )

    recipient.speak_l.assert_called_once_with(
        expected_message,
        buffer="system",
        player=target.username,
    )
    recipient.play_sound.assert_called_once_with(expected_sound)


@pytest.mark.parametrize("trust_level", [2, 3])
def test_privileged_presence_respects_each_recipient_preference(
    presence_server,
    trust_level,
):
    target = _create_account(
        presence_server,
        "PrivilegedUser",
        trust_level=trust_level,
    )
    muted_record = _create_account(presence_server, "Muted")
    enabled_record = _create_account(presence_server, "Enabled")
    muted = _add_recipient(
        presence_server,
        muted_record,
        notify_users=False,
        notify_friends=False,
    )
    enabled = _add_recipient(
        presence_server,
        enabled_record,
        notify_users=True,
        notify_friends=False,
    )

    presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=trust_level,
        is_online=True,
    )

    muted.speak_l.assert_not_called()
    muted.play_sound.assert_not_called()
    enabled.speak_l.assert_called_once_with(
        "user-online",
        buffer="system",
        player=target.username,
    )
    expected_sound = "onlinedev.ogg" if trust_level >= 3 else "onlineadmin.ogg"
    enabled.play_sound.assert_called_once_with(expected_sound)


def test_disabled_friend_notifications_fall_back_to_general_preference(
    presence_server,
):
    target = _create_account(
        presence_server,
        "AdminFriend",
        trust_level=2,
    )
    recipient_record = _create_account(presence_server, "Recipient")
    _make_friends(presence_server, target, recipient_record)
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=True,
        notify_friends=False,
    )

    presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=target.trust_level,
        is_online=True,
    )

    recipient.speak_l.assert_called_once_with(
        "user-online",
        buffer="system",
        player=target.username,
    )
    recipient.play_sound.assert_called_once_with("onlineadmin.ogg")


def test_friend_presence_respects_both_disabled_preferences(presence_server):
    target = _create_account(
        presence_server,
        "AdminFriend",
        trust_level=2,
    )
    recipient_record = _create_account(presence_server, "Recipient")
    _make_friends(presence_server, target, recipient_record)
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=False,
        notify_friends=False,
    )

    presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=target.trust_level,
        is_online=True,
    )

    recipient.speak_l.assert_not_called()
    recipient.play_sound.assert_not_called()


def test_normal_friend_presence_keeps_friend_sound(presence_server):
    target = _create_account(presence_server, "Friend")
    recipient_record = _create_account(presence_server, "Recipient")
    _make_friends(presence_server, target, recipient_record)
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=False,
        notify_friends=True,
    )

    presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=target.trust_level,
        is_online=False,
    )

    recipient.speak_l.assert_called_once_with(
        "friend-offline",
        buffer="system",
        player=target.username,
    )
    recipient.play_sound.assert_called_once_with("offlinefriend.ogg")


def test_duplicate_presence_events_are_debounced_but_transitions_are_not(
    presence_server,
):
    target = _create_account(presence_server, "Target")
    recipient_record = _create_account(presence_server, "Recipient")
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=True,
        notify_friends=False,
    )

    results = [
        presence_server._broadcast_presence(
            target.username,
            target.uuid,
            trust_level=target.trust_level,
            is_online=is_online,
        )
        for is_online in (True, True, False, False)
    ]

    assert results == [True, False, True, False]
    assert [call.args[0] for call in recipient.speak_l.call_args_list] == [
        "user-online",
        "user-offline",
    ]
    assert [call.args[0] for call in recipient.play_sound.call_args_list] == [
        "online.ogg",
        "offline.ogg",
    ]


def test_duplicate_attempts_extend_quiet_window(presence_server, monkeypatch):
    target = _create_account(presence_server, "Target")
    now = [100.0]
    monkeypatch.setattr(server_module.time, "monotonic", lambda: now[0])

    assert presence_server._claim_presence_event(target.uuid, True)
    now[0] += 4.0
    assert not presence_server._claim_presence_event(target.uuid, True)
    now[0] += 4.0
    assert not presence_server._claim_presence_event(target.uuid, True)
    now[0] += 6.0
    assert presence_server._claim_presence_event(target.uuid, True)


def test_presence_debounce_state_is_bounded(presence_server, monkeypatch):
    monkeypatch.setattr(server_module, "MAX_RECENT_PRESENCE_EVENTS", 2)

    for account_id in ("account-1", "account-2", "account-3"):
        assert presence_server._claim_presence_event(account_id, True)

    assert list(presence_server._recent_presence_events) == [
        "account-2",
        "account-3",
    ]


def test_unapproved_recipients_never_receive_presence(presence_server):
    target = _create_account(presence_server, "Target")
    recipient_record = _create_account(presence_server, "Recipient")
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=True,
        notify_friends=True,
        approved=False,
    )

    presence_server._broadcast_presence(
        target.username,
        target.uuid,
        trust_level=target.trust_level,
        is_online=True,
    )

    recipient.speak_l.assert_not_called()
    recipient.play_sound.assert_not_called()


@pytest.mark.asyncio
async def test_admin_authorization_emits_one_event_and_handover_emits_none(
    presence_server,
):
    admin = _create_account(
        presence_server,
        "Admin",
        trust_level=2,
    )
    recipient_record = _create_account(presence_server, "Recipient")
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=True,
        notify_friends=False,
    )
    registry = _WebSocketRegistry()
    presence_server._ws_server = registry

    first_client = _Client("127.0.0.1:10001")
    registry.bind(first_client)
    await presence_server._activate_authenticated_session(
        first_client,
        canonical_username=admin.username,
        client_type="python",
        client_platform="Windows",
        user_record=admin,
    )

    recipient.speak_l.assert_called_once_with(
        "user-online",
        buffer="system",
        player=admin.username,
    )
    recipient.play_sound.assert_called_once_with("onlineadmin.ogg")

    recipient.speak_l.reset_mock()
    recipient.play_sound.reset_mock()
    second_client = _Client("127.0.0.1:10002")
    registry.bind(second_client)
    old_client, _ = await presence_server._activate_authenticated_session(
        second_client,
        canonical_username=admin.username,
        client_type="mobile",
        client_platform="Android",
        user_record=admin,
    )

    assert old_client is first_client
    recipient.speak_l.assert_not_called()
    recipient.play_sound.assert_not_called()


@pytest.mark.asyncio
async def test_quick_reconnect_suppresses_offline_online_flap(presence_server):
    target = _create_account(presence_server, "Target")
    recipient_record = _create_account(presence_server, "Recipient")
    recipient = _add_recipient(
        presence_server,
        recipient_record,
        notify_users=True,
        notify_friends=False,
    )
    registry = _WebSocketRegistry()
    presence_server._ws_server = registry

    first_client = _Client("127.0.0.1:10001")
    registry.bind(first_client)
    await presence_server._activate_authenticated_session(
        first_client,
        canonical_username=target.username,
        client_type="python",
        client_platform="Windows",
        user_record=target,
    )
    recipient.speak_l.reset_mock()
    recipient.play_sound.reset_mock()

    await presence_server._on_client_disconnect(first_client)
    assert target.username in presence_server._pending_disconnects

    second_client = _Client("127.0.0.1:10002")
    registry.bind(second_client)
    await presence_server._activate_authenticated_session(
        second_client,
        canonical_username=target.username,
        client_type="web",
        client_platform="Browser",
        user_record=target,
    )
    await asyncio.sleep(0)

    assert target.username not in presence_server._pending_disconnects
    recipient.speak_l.assert_not_called()
    recipient.play_sound.assert_not_called()
