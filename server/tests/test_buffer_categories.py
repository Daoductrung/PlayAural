import ast
from pathlib import Path

from server.users.network_user import NetworkUser


def test_all_server_speech_calls_supply_buffer_category() -> None:
    root = Path(__file__).resolve().parents[1]
    missing: list[str] = []

    for path in root.rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            if node.func.attr not in {"speak", "speak_l", "broadcast_l"}:
                continue
            has_buffer_keyword = any(
                keyword.arg == "buffer" for keyword in node.keywords if keyword.arg
            )
            has_buffer_positional = len(node.args) >= 2
            if not has_buffer_keyword and not has_buffer_positional:
                missing.append(f"{path.relative_to(root).as_posix()}:{node.lineno}")

    assert not missing, "Missing buffer category on server speech calls:\n" + "\n".join(missing)


def test_network_user_speak_serializes_misc_buffer_explicitly() -> None:
    user = NetworkUser("alice", "en", connection=object())
    user.speak("hello")

    packet = user.get_queued_messages()[-1]
    assert packet["buffer"] == "misc"


def test_network_user_speak_l_serializes_misc_buffer_explicitly() -> None:
    user = NetworkUser("alice", "en", connection=object())
    user.speak_l("document-not-found")

    packet = user.get_queued_messages()[-1]
    assert packet["buffer"] == "misc"
