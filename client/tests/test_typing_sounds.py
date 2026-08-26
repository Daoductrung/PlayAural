from __future__ import annotations

import ast
from pathlib import Path
import sys

import pytest

CLIENT_ROOT = Path(__file__).resolve().parents[1]
if str(CLIENT_ROOT) not in sys.path:
    sys.path.insert(0, str(CLIENT_ROOT))

from typing_sounds import (  # noqa: E402
    DIGIT_SOUND_ASSETS,
    GENERIC_TYPING_CUE,
    TYPING_DELETE_ASSET,
    TYPING_RETURN_ASSET,
    resolve_typing_sound_cue,
)
from windows_typing import (  # noqa: E402
    WindowsTextInputObserver,
    recover_windows_virtual_key,
    resolve_windows_typing_sound_cue,
)


@pytest.mark.parametrize("digit", range(10))
def test_digits_use_semantic_assets(digit: int) -> None:
    cue = resolve_typing_sound_cue(str(digit))

    assert cue is not None
    assert cue.asset == DIGIT_SOUND_ASSETS[digit]
    assert not cue.family


@pytest.mark.parametrize("key", ["Backspace", "Delete"])
def test_delete_keys_share_the_delete_asset_even_with_modifiers(key: str) -> None:
    cue = resolve_typing_sound_cue(key, modified=True)

    assert cue is not None
    assert cue.asset == TYPING_DELETE_ASSET


@pytest.mark.parametrize("key", ["Enter", "NumpadEnter"])
def test_return_keys_share_the_return_asset_even_with_modifiers(key: str) -> None:
    cue = resolve_typing_sound_cue(key, modified=True)

    assert cue is not None
    assert cue.asset == TYPING_RETURN_ASSET


@pytest.mark.parametrize("key", ["a", "â", " ", ";", "字"])
def test_printable_text_uses_the_dynamic_typing_family(key: str) -> None:
    assert resolve_typing_sound_cue(key) == GENERIC_TYPING_CUE


def test_shortcuts_and_held_keys_are_silent_without_throttling_real_presses() -> None:
    assert resolve_typing_sound_cue("a", modified=True) is None
    assert resolve_typing_sound_cue("a", auto_repeat=True) is None
    assert resolve_typing_sound_cue("a") == GENERIC_TYPING_CUE
    assert resolve_typing_sound_cue("a") == GENERIC_TYPING_CUE


def test_non_text_navigation_keys_are_silent() -> None:
    for key in ("", "ArrowLeft", "Escape", "F1", "Process", "Unidentified"):
        assert resolve_typing_sound_cue(key) is None


@pytest.mark.skipif(sys.platform != "win32", reason="Windows scan-code API")
def test_windows_ime_scan_code_recovers_replaced_letter_key() -> None:
    letter_a_scan_code = 0x1E
    raw_flags = letter_a_scan_code << 16

    assert recover_windows_virtual_key(raw_flags) == ord("A")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows key-message API")
def test_windows_native_telex_messages_resolve_every_physical_press() -> None:
    letter_a_scan_code = 0x1E
    process_key = 0xE5
    raw_flags = letter_a_scan_code << 16

    first_press = resolve_windows_typing_sound_cue(process_key, raw_flags)
    second_press = resolve_windows_typing_sound_cue(process_key, raw_flags)
    held_press = resolve_windows_typing_sound_cue(
        process_key,
        raw_flags | (1 << 30),
    )

    assert first_press == GENERIC_TYPING_CUE
    assert second_press == GENERIC_TYPING_CUE
    assert held_press is None


@pytest.mark.skipif(sys.platform != "win32", reason="Windows window subclass API")
def test_windows_text_observer_sees_native_and_ime_key_messages_once() -> None:
    import ctypes
    import wx

    app = wx.GetApp() or wx.App(False)
    frame = wx.Frame(None)
    text_control = wx.TextCtrl(frame)
    cues = []
    observer = WindowsTextInputObserver(text_control.GetHandle(), cues.append)
    send_message = ctypes.windll.user32.SendMessageW
    key_flags = 1 | (0x1E << 16)

    try:
        assert observer.installed
        send_message(text_control.GetHandle(), 0x0100, ord("A"), key_flags)
        assert cues == [GENERIC_TYPING_CUE]

        cues.clear()
        ime_key_flags = 1 | (0x30 << 16)
        send_message(text_control.GetHandle(), 0x0290, ord("B"), ime_key_flags)
        assert cues == [GENERIC_TYPING_CUE]

        cues.clear()
        send_message(
            text_control.GetHandle(),
            0x0100,
            ord("A"),
            key_flags | (1 << 30),
        )
        assert cues == []

        observer.close()
        send_message(text_control.GetHandle(), 0x0100, ord("A"), key_flags)
        assert cues == []
    finally:
        observer.close()
        frame.Destroy()
        app.ProcessPendingEvents()


def test_main_window_routes_text_controls_through_the_shared_typing_pipeline() -> None:
    source_path = Path(__file__).resolve().parents[1] / "ui" / "main_window.py"
    source = source_path.read_text(encoding="utf-8")
    module = ast.parse(source)
    main_window = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "MainWindow"
    )
    methods = {
        node.name: node
        for node in main_window.body
        if isinstance(node, ast.FunctionDef)
    }

    hook_calls = {
        node.func.attr
        for node in ast.walk(methods["on_char_hook"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    event_playback_calls = {
        node.func.attr
        for node in ast.walk(methods["_play_typing_sound_for_event"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    cue_playback_calls = {
        node.func.attr
        for node in ast.walk(methods["_play_typing_cue"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "_play_typing_sound_for_event" in hook_calls
    assert "_play_typing_cue" in event_playback_calls
    assert "IsEditable" in cue_playback_calls
    assert "play_family" in cue_playback_calls
    assert "play" in cue_playback_calls
    assert "WindowsTextInputObserver" in source
    assert "_native_typing_control_handles" in source
    assert "import random" not in source
    assert "randint(1, 4)" not in source


def test_web_chat_uses_the_shared_typing_pipeline_offline() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    app_source = (repository_root / "web_client" / "app.js").read_text(
        encoding="utf-8"
    )
    service_worker = (repository_root / "web_client" / "sw.js").read_text(
        encoding="utf-8"
    )

    assert 'this.elements.chatInput?.addEventListener("keydown"' in app_source
    assert (
        "this.playTypingSoundForEvent(event, this.elements.chatInput)"
        in app_source
    )
    assert '"./typing_sounds.js"' in service_worker
