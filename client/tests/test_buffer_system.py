import ast
from pathlib import Path
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from buffer_system import BufferSystem


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


def test_global_mute_blocks_individual_toggles_and_preserves_direct_mutes():
    buffer_system = BufferSystem()
    buffer_system.create_default_buffers()
    assert buffer_system.toggle_mute("chat")
    assert buffer_system.toggle_mute("all")

    assert not buffer_system.toggle_mute("chat")
    assert buffer_system.is_muted("chat")
    assert all(
        buffer_system.is_effectively_muted(name)
        for name in buffer_system.BUFFER_NAMES
    )

    assert buffer_system.toggle_mute("all")
    assert not buffer_system.is_effectively_muted("game")
    assert buffer_system.is_effectively_muted("chat")


def test_muted_sources_retain_backlogs_without_leaking_into_all():
    buffer_system = BufferSystem()
    buffer_system.create_default_buffers()
    buffer_system.toggle_mute("chat")
    buffer_system.add_item("chat", "hidden chat")

    assert [item["text"] for item in buffer_system.buffers["chat"]] == [
        "hidden chat"
    ]
    assert buffer_system.buffers["all"] == []


def test_global_mute_keeps_combined_history_accumulating():
    buffer_system = BufferSystem()
    buffer_system.create_default_buffers()
    buffer_system.toggle_mute("all")
    buffer_system.add_item("game", "turn result")

    assert [item["text"] for item in buffer_system.buffers["game"]] == [
        "turn result"
    ]
    assert [item["text"] for item in buffer_system.buffers["all"]] == [
        "turn result"
    ]


def test_muted_buffer_preferences_are_canonical_and_ordered():
    buffer_system = BufferSystem()
    buffer_system.create_default_buffers()

    assert buffer_system.set_muted_buffers(
        ["system", "chats", "bogus", {"name": "game"}, "all", "chat"]
    )
    assert buffer_system.get_muted_buffers() == {"all", "chat", "system"}
    assert buffer_system.get_muted_buffers_in_order() == ["all", "chat", "system"]
    assert not buffer_system.set_muted_buffers(["all", "chat", "system"])
    assert buffer_system.set_muted_buffers(None)
    assert buffer_system.get_muted_buffers_in_order() == []


def test_buffer_history_is_bounded_per_source_and_combined_view():
    buffer_system = BufferSystem(max_items_per_buffer=2)
    buffer_system.create_default_buffers()
    for text in ("one", "two", "three"):
        buffer_system.add_item("game", text)

    assert [item["text"] for item in buffer_system.buffers["game"]] == [
        "two",
        "three",
    ]
    assert [item["text"] for item in buffer_system.buffers["all"]] == [
        "two",
        "three",
    ]


def test_buffer_capacity_must_be_a_positive_integer():
    for invalid in (0, -1, True, 1.5):
        try:
            BufferSystem(max_items_per_buffer=invalid)
        except ValueError:
            continue
        raise AssertionError(f"Expected invalid capacity to fail: {invalid!r}")


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


def test_chat_alerts_are_gated_by_effective_chat_buffer_mute():
    function = _get_main_window_function("on_receive_chat")
    should_alert_assignments = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "should_alert"
            for target in node.targets
        )
    ]
    assert len(should_alert_assignments) == 1
    effective_mute_calls = [
        node
        for node in ast.walk(should_alert_assignments[0].value)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "is_effectively_muted"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "chat"
    ]
    assert effective_mute_calls


def test_desktop_buffer_announcements_use_effective_mute_state():
    function = _get_main_window_function("_announce_buffer_info")
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "is_effectively_muted"
        for node in ast.walk(function)
    )


def test_desktop_history_updates_keep_the_latest_line_visible():
    add_history = _get_main_window_function("add_history")
    refresh_history = _get_main_window_function(
        "_refresh_history_text_from_current_buffer"
    )
    scroll_history = _get_main_window_function("_scroll_history_to_latest")

    for function in (add_history, refresh_history):
        assert any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_scroll_history_to_latest"
            for node in ast.walk(function)
        )
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "_refresh_history_text_from_current_buffer"
        and any(
            keyword.arg == "caret_distance_from_end" for keyword in node.keywords
        )
        for node in ast.walk(add_history)
    )
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "ShowPosition"
        and node.args
        and isinstance(node.args[0], ast.Call)
        and isinstance(node.args[0].func, ast.Attribute)
        and node.args[0].func.attr == "GetLastPosition"
        for node in ast.walk(scroll_history)
    )
