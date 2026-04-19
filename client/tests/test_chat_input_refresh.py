import ast
from pathlib import Path


def _get_main_window_class() -> ast.ClassDef:
    source_path = Path(__file__).resolve().parents[1] / "ui" / "main_window.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "MainWindow":
            return node
    raise AssertionError("MainWindow class not found")


def _get_main_window_function(function_name: str) -> ast.FunctionDef:
    main_window = _get_main_window_class()
    for child in main_window.body:
        if isinstance(child, ast.FunctionDef) and child.name == function_name:
            return child
    raise AssertionError(f"MainWindow.{function_name} not found")


def _main_window_method_names() -> set[str]:
    main_window = _get_main_window_class()
    return {
        child.name
        for child in main_window.body
        if isinstance(child, ast.FunctionDef)
    }


def _has_method_call(function: ast.FunctionDef, method_name: str) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
            and node.func.attr == method_name
        ):
            return True
    return False


def _has_wx_callafter_target(function: ast.FunctionDef, method_name: str) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "wx"
            and node.func.attr == "CallAfter"
            and node.args
        ):
            target = node.args[0]
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
                and target.attr == method_name
            ):
                return True
    return False


def _has_wx_find_focus_call(function: ast.FunctionDef) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "FindFocus"
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "Window"
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "wx"
        ):
            return True
    return False


def _contains_wx_constructor_call(function: ast.FunctionDef, constructor_name: str) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "wx"
            and node.func.attr == constructor_name
        ):
            return True
    return False


def _contains_attribute_call(function: ast.FunctionDef, attribute_name: str, method_name: str) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "self"
            and node.func.value.attr == attribute_name
            and node.func.attr == method_name
        ):
            return True
    return False


def _contains_name_call(function: ast.FunctionDef, local_name: str, method_name: str) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == local_name
            and node.func.attr == method_name
        ):
            return True
    return False


def _referenced_self_attributes(function: ast.FunctionDef) -> set[str]:
    attributes: set[str] = set()
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        ):
            attributes.add(node.attr)
    return attributes


def test_global_menu_shortcuts_prepare_menu_focus_before_sending_packets():
    for function_name in (
        "on_list_online",
        "on_list_online_with_games",
        "on_open_friends_hub",
        "on_open_options",
    ):
        function = _get_main_window_function(function_name)
        assert _has_method_call(function, "_prepare_for_menu_shortcut_navigation")


def test_chat_send_refreshes_input_in_place_after_enter():
    function = _get_main_window_function("on_chat_enter")
    assert _has_wx_callafter_target(function, "_refresh_chat_input_after_send")


def test_chat_refresh_rebuilds_control_and_restores_tab_order():
    function = _get_main_window_function("_refresh_chat_input_after_send")
    assert _has_method_call(function, "_create_chat_controls")
    assert _has_method_call(function, "_apply_accessibility_labels")
    assert _has_method_call(function, "_sync_chat_area_tab_order")
    assert _has_wx_find_focus_call(function)
    assert _contains_attribute_call(function, "chat_input", "SetFocus")


def test_chat_input_control_sets_explicit_accessibility_name():
    function = _get_main_window_function("_create_chat_input_control")
    assert _contains_name_call(function, "chat_input", "SetName")


def test_chat_controls_are_created_as_a_label_and_input_pair():
    function = _get_main_window_function("_create_chat_controls")
    assert _contains_wx_constructor_call(function, "StaticText")
    assert _has_method_call(function, "_create_chat_input_control")


def test_non_menu_focus_controls_include_voice_controls():
    function = _get_main_window_function("_get_non_menu_focus_controls")
    attributes = _referenced_self_attributes(function)
    assert "chat_input" in attributes
    assert "history_text" in attributes
    assert "voice_join_button" in attributes
    assert "voice_leave_button" in attributes
    assert "voice_mic_checkbox" in attributes


def test_voice_ui_restores_the_same_voice_control_when_possible():
    function = _get_main_window_function("update_voice_ui")
    assert _has_method_call(function, "_get_voice_focus_target")
    assert _has_wx_callafter_target(function, "_restore_voice_control_focus")


def test_legacy_chat_focus_bounce_helpers_are_removed():
    method_names = _main_window_method_names()
    assert "_clear_chat_input_after_send" not in method_names
    assert "_set_chat_input_value" not in method_names
    assert "_finalize_chat_input_clear" not in method_names
    assert "_reset_chat_input_ime_context" not in method_names
    assert "_restore_chat_input_after_ime_reset" not in method_names
    assert "_looks_like_stale_chat_ime_commit" not in method_names
    assert "_cancel_pending_chat_ime_reset_focus" not in method_names


def test_legacy_voice_mic_button_name_is_removed():
    source_path = Path(__file__).resolve().parents[1] / "ui" / "main_window.py"
    source = source_path.read_text(encoding="utf-8")
    assert "voice_mic_button" not in source
