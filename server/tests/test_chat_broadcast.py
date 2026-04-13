import pytest

from ..auth.chat_rate_limit import ChatRateLimiter
from ..core.server import Server
from ..tables.manager import TableManager
from ..users.test_user import MockUser


class DummyClient:
    def __init__(self, username: str):
        self.username = username


class RecordingConnection:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, packet: dict) -> None:
        self.sent.append(packet)


class MutatingConnection(RecordingConnection):
    def __init__(self, server: Server, username_to_remove: str):
        super().__init__()
        self.server = server
        self.username_to_remove = username_to_remove

    async def send(self, packet: dict) -> None:
        await super().send(packet)
        self.server._users.pop(self.username_to_remove, None)


class DummyDatabase:
    def get_active_mute(self, username: str):
        return None


def _make_server() -> Server:
    server = Server.__new__(Server)
    server._db = DummyDatabase()
    server._chat_rate_limiter = ChatRateLimiter()
    server._tables = TableManager()
    server._user_states = {}
    server._users = {}
    return server


def _make_user(username: str, connection: RecordingConnection) -> MockUser:
    user = MockUser(username)
    user.connection = connection
    return user


@pytest.mark.asyncio
@pytest.mark.parametrize("convo", ["global", "local"])
async def test_chat_broadcast_snapshots_users_when_connection_changes_during_send(convo: str) -> None:
    server = _make_server()
    alice_connection = MutatingConnection(server, "Bob")
    bob_connection = RecordingConnection()
    cara_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    cara = _make_user("Cara", cara_connection)
    server._users = {
        "Alice": alice,
        "Bob": bob,
        "Cara": cara,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": convo,
            "message": "hello",
            "type": "chat",
        },
    )

    assert "Bob" not in server._users
    assert alice_connection.sent[0]["message"] == "hello"
    assert cara_connection.sent[0]["message"] == "hello"
    assert bob_connection.sent == []
