import ast
from pathlib import Path

from client.buffer_system import BufferSystem


def _get_main_window_function(function_name: str) -> ast.FunctionDef:
    source_path = Path(__file__).resolve().parents[1] / "ui" / "main_window.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "MainWindow":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == function_name:
                    return child
    raise AssertionError(f"MainWindow.{function_name} not found")


def _is_self_speaker_speak_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "speak"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "speaker"
        and isinstance(func.value.value, ast.Name)
        and func.value.value.id == "self"
    )


def test_buffer_system_normalizes_legacy_chat_aliases():
    buffer_system = BufferSystem()
    buffer_system.create_buffer("all")
    buffer_system.create_buffer("chat")
    buffer_system.add_item("chats", "Hello")
    buffer_system.toggle_mute("chats")

    assert "chats" not in buffer_system.buffers
    assert [item["text"] for item in buffer_system.buffers["chat"]] == ["Hello"]
    assert [item["text"] for item in buffer_system.buffers["all"]] == ["Hello"]
    assert buffer_system.get_muted_buffers() == {"chat"}
    assert buffer_system.is_muted("chat")
    assert buffer_system.is_muted("chats")


def test_effective_mute_inherits_all_buffer():
    buffer_system = BufferSystem()
    buffer_system.toggle_mute("all")

    assert buffer_system.is_effectively_muted("game")
    assert buffer_system.is_effectively_muted("chat")


def test_should_show_message_honors_all_and_aliases():
    buffer_system = BufferSystem()

    assert buffer_system.should_show_message("all", "game")
    assert buffer_system.should_show_message("chats", "chat")
    assert not buffer_system.should_show_message("system", "chat")


def test_chat_packets_do_not_speak_directly_outside_add_history():
    function = _get_main_window_function("on_receive_chat")
    direct_speaker_calls = [
        node for node in ast.walk(function) if _is_self_speaker_speak_call(node)
    ]
    add_history_calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_history"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
    ]

    assert not direct_speaker_calls
    assert add_history_calls
