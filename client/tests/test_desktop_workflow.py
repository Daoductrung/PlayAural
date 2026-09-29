import json
from pathlib import Path
import tomllib

from ui import main_window as main_window_module
from ui.copy_directive import (
    COPY_DIRECTIVE_VERSION,
    MAX_COPY_FEEDBACK_LENGTH,
    MAX_COPY_TEXT_LENGTH,
    copy_text_to_clipboard,
    execute_copy_directive,
    validate_copy_directive,
)
from ui.main_window import LOGOUT_RESPONSE_TIMEOUT_MS, MainWindow


CLIENT_DIR = Path(__file__).resolve().parents[1]
COPY_CONFORMANCE = json.loads(
    (CLIENT_DIR.parent / "copy_directive_conformance.json").read_text(
        encoding="utf-8"
    )
)


def test_desktop_logout_dialog_localizes_decisions_and_defaults_safe(monkeypatch):
    captured = {}

    class Dialog:
        def __init__(self, parent, message, title, style):
            captured.update(
                parent=parent,
                message=message,
                title=title,
                style=style,
            )

        @staticmethod
        def SetYesNoLabels(yes, no):
            captured["labels"] = (yes, no)

        @staticmethod
        def ShowModal():
            return main_window_module.wx.ID_NO

        @staticmethod
        def Destroy():
            captured["destroyed"] = True

    monkeypatch.setattr(main_window_module.wx, "MessageDialog", Dialog)
    window = object()

    assert MainWindow._show_logout_confirmation(window) is False
    assert captured["parent"] is window
    assert captured["labels"] == (
        main_window_module.Localization.get("logout-confirm-yes"),
        main_window_module.Localization.get("logout-confirm-no"),
    )
    assert captured["style"] & main_window_module.wx.NO_DEFAULT
    assert captured["destroyed"] is True


def test_desktop_close_cancel_preserves_session_and_restores_focus(monkeypatch):
    sent_packets = []
    focus_restores = []
    vetoes = []

    focused = type(
        "FocusedControl",
        (),
        {
            "IsEnabled": staticmethod(lambda: True),
            "IsShown": staticmethod(lambda: True),
            "SetFocus": staticmethod(lambda: focus_restores.append(True)),
        },
    )()
    monkeypatch.setattr(
        main_window_module.wx,
        "Window",
        type("Window", (), {"FindFocus": staticmethod(lambda: focused)}),
    )
    monkeypatch.setattr(
        main_window_module.wx,
        "CallAfter",
        lambda callback: callback(),
    )

    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "quitting": False,
            "_logout_request_pending": False,
            "_show_logout_confirmation": staticmethod(lambda: False),
            "network": type(
                "Network",
                (),
                {"send_packet": staticmethod(lambda packet: sent_packets.append(packet))},
            )(),
            "_restore_focus_after_close_cancel": staticmethod(
                MainWindow._restore_focus_after_close_cancel
            ),
        },
    )()
    event = type(
        "CloseEvent",
        (),
        {
            "CanVeto": staticmethod(lambda: True),
            "Veto": staticmethod(lambda: vetoes.append(True)),
        },
    )()

    MainWindow.on_close(window, event)

    assert vetoes == [True]
    assert sent_packets == []
    assert focus_restores == [True]


def test_desktop_confirmed_close_sends_one_generic_logout_request(monkeypatch):
    sent_packets = []
    scheduled = []
    vetoes = []
    spoken = []

    monkeypatch.setattr(
        main_window_module.wx,
        "Window",
        type("Window", (), {"FindFocus": staticmethod(lambda: None)}),
    )
    timer = type("Timer", (), {"Stop": staticmethod(lambda: None)})()

    def call_later(delay, callback):
        scheduled.append((delay, callback))
        return timer

    monkeypatch.setattr(main_window_module.wx, "CallLater", call_later)

    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "quitting": False,
            "is_reconnecting": True,
            "expecting_reconnect": True,
            "_logout_request_pending": False,
            "_logout_response_timer": None,
            "_show_logout_confirmation": staticmethod(lambda: True),
            "network": type(
                "Network",
                (),
                {
                    "send_packet": staticmethod(
                        lambda packet: sent_packets.append(packet) or True
                    )
                },
            )(),
            "speaker": type(
                "Speaker",
                (),
                {
                    "speak": staticmethod(
                        lambda text, interrupt: spoken.append((text, interrupt))
                    )
                },
            )(),
            "_finish_local_exit": staticmethod(lambda: None),
            "_restore_focus_after_close_cancel": staticmethod(
                MainWindow._restore_focus_after_close_cancel
            ),
        },
    )()
    event = type(
        "CloseEvent",
        (),
        {
            "CanVeto": staticmethod(lambda: True),
            "Veto": staticmethod(lambda: vetoes.append(True)),
        },
    )()

    MainWindow.on_close(window, event)
    MainWindow.on_close(window, event)

    assert vetoes == [True, True]
    assert sent_packets == [{"type": "logout"}]
    assert window._logout_request_pending is True
    assert window.is_reconnecting is False
    assert window.expecting_reconnect is False
    assert spoken and spoken[0][1] is True
    assert scheduled == [(LOGOUT_RESPONSE_TIMEOUT_MS, window._finish_local_exit)]


def test_read_only_menu_rows_never_send_desktop_selections():
    sent_packets = []
    activation_sounds = []

    class MenuList:
        @staticmethod
        def GetSelection():
            return 0

    class Network:
        @staticmethod
        def send_packet(packet):
            sent_packets.append(packet)

    class SoundManager:
        @staticmethod
        def play_menuenter():
            activation_sounds.append("menuenter")

    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "current_menu_id": "confirmation",
            "current_menu_item_ids": ["summary"],
            "current_menu_item_read_only": [True],
            "menu_list": MenuList(),
            "network": Network(),
            "sound_manager": SoundManager(),
            "_activate_menu_copy_at": MainWindow._activate_menu_copy_at,
        },
    )()
    event = type("EventHarness", (), {"Skip": staticmethod(lambda: None)})()

    MainWindow.on_menu_activate(window, event)
    assert sent_packets == []
    assert activation_sounds == []

    window.current_menu_item_ids = ["confirm"]
    window.current_menu_item_read_only = [False]
    MainWindow.on_menu_activate(window, event)
    assert sent_packets == [
        {
            "menu_id": "confirmation",
            "selection": 1,
            "selection_id": "confirm",
            "type": "menu",
        }
    ]
    assert activation_sounds == ["menuenter"]


def test_desktop_copy_directives_copy_exact_text_without_server_selection(monkeypatch):
    copied = []
    sent_packets = []
    feedback = []

    class Clipboard:
        def Open(self):
            return True

        def SetData(self, data):
            copied.append(data.GetText())
            return True

        def Flush(self):
            return True

        def Close(self):
            pass

    assert copy_text_to_clipboard("first\nsecond", Clipboard()) is True
    assert copied == ["first\nsecond"]

    directive = {
        "version": 1,
        "text": "first\nsecond",
        "success_text": "Copied two messages.",
        "failure_text": "Copy failed.",
    }
    monkeypatch.setattr(
        "ui.main_window.execute_copy_directive",
        lambda value: execute_copy_directive(
            value,
            lambda text: copied.append(text) or True,
        ),
    )
    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "current_menu_id": "audit",
            "current_menu_item_ids": ["copy_page"],
            "current_menu_item_read_only": [False],
            "current_menu_item_copy_directives": [directive],
            "menu_list": type("MenuList", (), {"GetSelection": staticmethod(lambda: 0)})(),
            "network": type("Network", (), {"send_packet": staticmethod(sent_packets.append)})(),
            "sound_manager": type("Sound", (), {"play_menuenter": staticmethod(lambda: None)})(),
            "add_history": staticmethod(
                lambda text, buffer, speak_aloud: feedback.append(
                    (text, buffer, speak_aloud)
                )
            ),
            "_activate_menu_copy_at": MainWindow._activate_menu_copy_at,
            "perform_copy_directive": MainWindow.perform_copy_directive,
        },
    )()
    event = type("EventHarness", (), {"Skip": staticmethod(lambda: None)})()

    MainWindow.on_menu_activate(window, event)

    assert copied[-1] == "first\nsecond"
    assert sent_packets == []
    assert feedback == [("Copied two messages.", "system", True)]


def test_desktop_copy_directives_cover_modified_enter_and_escape(monkeypatch):
    copied = []
    sent_packets = []
    directive = {
        "version": 1,
        "text": "current page",
        "success_text": "Copied.",
        "failure_text": "Failed.",
    }
    monkeypatch.setattr(
        "ui.main_window.execute_copy_directive",
        lambda value: execute_copy_directive(
            value,
            lambda text: copied.append(text) or True,
        ),
    )

    menu_list = type(
        "MenuList",
        (),
        {
            "GetCount": staticmethod(lambda: 1),
            "GetSelection": staticmethod(lambda: 0),
        },
    )()
    monkeypatch.setattr(
        main_window_module.wx,
        "Window",
        type("Window", (), {"FindFocus": staticmethod(lambda: menu_list)}),
    )
    feedback = []
    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "current_menu_id": "audit",
            "current_menu_item_ids": ["copy_page"],
            "current_menu_item_read_only": [False],
            "current_menu_item_copy_directives": [directive],
            "current_mode": "list",
            "escape_behavior": "select_last_option",
            "menu_list": menu_list,
            "multiletter_enabled": True,
            "network": type(
                "Network",
                (),
                {"send_packet": staticmethod(sent_packets.append)},
            )(),
            "sound_manager": type(
                "Sound",
                (),
                {"play_menuenter": staticmethod(lambda: None)},
            )(),
            "add_history": staticmethod(
                lambda text, buffer, speak_aloud: feedback.append(text)
            ),
            "_activate_menu_copy_at": MainWindow._activate_menu_copy_at,
            "perform_copy_directive": MainWindow.perform_copy_directive,
        },
    )()

    def event(key_code, *, shift=False):
        return type(
            "EventHarness",
            (),
            {
                "AltDown": staticmethod(lambda: False),
                "ControlDown": staticmethod(lambda: False),
                "GetKeyCode": staticmethod(lambda: key_code),
                "GetModifiers": staticmethod(
                    lambda: main_window_module.wx.MOD_SHIFT if shift else 0
                ),
                "ShiftDown": staticmethod(lambda: shift),
                "Skip": staticmethod(lambda: None),
            },
        )()

    MainWindow.on_char_hook(
        window,
        event(main_window_module.wx.WXK_RETURN, shift=True),
    )
    MainWindow.on_char_hook(window, event(main_window_module.wx.WXK_ESCAPE))

    assert copied == ["current page", "current page"]
    assert feedback == ["Copied.", "Copied."]
    assert sent_packets == []


def test_desktop_copy_directives_fail_closed_for_malformed_or_failed_payloads():
    invalid = execute_copy_directive(
        {
            "version": 1,
            "text": "unsafe\x00text",
            "success_text": "Copied.",
            "failure_text": "Failed.",
        },
        lambda _text: True,
    )
    assert invalid.accepted is False
    assert invalid.feedback == ""

    failed = execute_copy_directive(
        {
            "version": 1,
            "text": "safe text",
            "success_text": "Copied.",
            "failure_text": "Failed.",
        },
        lambda _text: (_ for _ in ()).throw(RuntimeError("clipboard unavailable")),
    )
    assert failed.accepted is True
    assert failed.copied is False
    assert failed.feedback == "Failed."


def test_desktop_copy_directive_shared_conformance_and_boundaries():
    assert COPY_CONFORMANCE["protocol_version"] == COPY_DIRECTIVE_VERSION
    assert COPY_CONFORMANCE["limits"] == {
        "text_code_points": MAX_COPY_TEXT_LENGTH,
        "feedback_code_points": MAX_COPY_FEEDBACK_LENGTH,
    }
    for case in COPY_CONFORMANCE["valid"]:
        assert validate_copy_directive(case["directive"]) is not None, case["name"]
    for case in COPY_CONFORMANCE["invalid"]:
        assert validate_copy_directive(case["directive"]) is None, case["name"]

    common = {
        "version": COPY_DIRECTIVE_VERSION,
        "success_text": "Copied.",
        "failure_text": "Failed.",
    }
    assert validate_copy_directive(
        {**common, "text": "😀" * MAX_COPY_TEXT_LENGTH}
    ) is not None
    assert validate_copy_directive(
        {**common, "text": "x" * (MAX_COPY_TEXT_LENGTH + 1)}
    ) is None
    assert validate_copy_directive({**common, "text": "bad\ud800value"}) is None

    class HostileMapping(dict):
        def get(self, *_args, **_kwargs):
            raise RuntimeError("unexpected mapping behavior")

    assert validate_copy_directive(
        HostileMapping({**common, "text": "payload"})
    ) is None


def test_desktop_malformed_copy_directive_stays_local_and_silent():
    sent_packets = []
    feedback = []
    window = type(
        "WindowHarness",
        (),
        {
            "connected": True,
            "current_menu_id": "audit",
            "current_menu_item_ids": ["copy_page"],
            "current_menu_item_read_only": [False],
            "current_menu_item_copy_directives": [None],
            "menu_list": type(
                "MenuList",
                (),
                {"GetSelection": staticmethod(lambda: 0)},
            )(),
            "network": type(
                "Network",
                (),
                {"send_packet": staticmethod(sent_packets.append)},
            )(),
            "sound_manager": None,
            "add_history": staticmethod(
                lambda text, buffer, speak_aloud: feedback.append(text)
            ),
            "_activate_menu_copy_at": MainWindow._activate_menu_copy_at,
            "perform_copy_directive": MainWindow.perform_copy_directive,
        },
    )()
    event = type("EventHarness", (), {"Skip": staticmethod(lambda: None)})()

    MainWindow.on_menu_activate(window, event)

    assert sent_packets == []
    assert feedback == []


def test_client_dev_extra_installs_test_tools():
    pyproject = tomllib.loads((CLIENT_DIR / "pyproject.toml").read_text())

    dev_deps = pyproject["project"]["optional-dependencies"]["dev"]

    assert any(dep.startswith("pytest") for dep in dev_deps)
    assert any(dep.startswith("pytest-asyncio") for dep in dev_deps)
    assert any(dep.startswith("pytest-xdist") for dep in dev_deps)


def test_desktop_numpy_constraint_preserves_legacy_x86_compatibility():
    repo_root = CLIENT_DIR.parent
    pyproject = tomllib.loads((CLIENT_DIR / "pyproject.toml").read_text())
    runtime_deps = pyproject["project"]["dependencies"]
    requirements = {
        line.strip()
        for line in (repo_root / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    lock = tomllib.loads((CLIENT_DIR / "uv.lock").read_text())
    locked_numpy = [
        package for package in lock["package"] if package["name"] == "numpy"
    ]
    build_script = (repo_root / "build_prod.bat").read_text(encoding="utf-8")

    expected = "numpy>=1.26,<2.4"
    assert expected in runtime_deps
    assert expected in requirements
    assert len(locked_numpy) == 1
    locked_version = tuple(map(int, locked_numpy[0]["version"].split(".")[:2]))
    assert (1, 26) <= locked_version < (2, 4)
    assert "SpecifierSet('>=1.26,<2.4')" in build_script
    assert "or sys.exit('Production builds require NumPy >=1.26,<2.4')" in build_script


def test_run_client_syncs_development_dependencies():
    script = (CLIENT_DIR / "run_client.bat").read_text(encoding="utf-8").lower()

    assert "uv sync --extra dev" in script
    assert "uv pip install" not in script


def test_main_window_applies_server_locale_without_restart_prompt():
    source = (CLIENT_DIR / "ui" / "main_window.py").read_text(encoding="utf-8")

    assert 'self._apply_locale_change(packet.get("locale", "en"))' in source
    assert "Localization.set_locale(locale)" in source
    assert "options-restart-required-message" not in source


def test_welcome_sound_has_one_server_ordering_authority():
    repo_root = CLIENT_DIR.parent
    client_handlers = [
        CLIENT_DIR / "ui" / "main_window.py",
        repo_root / "web_client" / "app.js",
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx",
    ]

    for handler in client_handlers:
        source = handler.read_text(encoding="utf-8")
        assert "playSound(\"welcome.ogg\"" not in source
        assert 'playSound({ name: "welcome.ogg"' not in source
        assert 'sound_manager.play("welcome.ogg"' not in source

    for pack in ("client", "web_client", "mobile_client"):
        assert (repo_root / pack / "sounds" / "welcome.ogg").is_file()


def test_all_clients_adopt_server_canonical_username_after_authorization():
    repo_root = CLIENT_DIR.parent
    network_source = (CLIENT_DIR / "network_manager.py").read_text(encoding="utf-8")
    window_source = (CLIENT_DIR / "ui" / "main_window.py").read_text(
        encoding="utf-8"
    )
    web_source = (repo_root / "web_client" / "app.js").read_text(encoding="utf-8")
    mobile_source = (
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx"
    ).read_text(encoding="utf-8")

    assert 'canonical_username = packet.get("username")' in network_source
    assert 'self.credentials["username"] = canonical_username' in window_source
    assert "username: packet.username || this.lastUser" in web_source
    assert "this.elements.username.value = packet.username" in web_source
    assert "credentialsRef.current.username = authPacket.username" in mobile_source
    assert "setUsername(authPacket.username);" in mobile_source


def test_all_clients_dismiss_server_superseded_editboxes():
    repo_root = CLIENT_DIR.parent
    network_source = (CLIENT_DIR / "network_manager.py").read_text(
        encoding="utf-8"
    )
    window_source = (CLIENT_DIR / "ui" / "main_window.py").read_text(
        encoding="utf-8"
    )
    web_source = (repo_root / "web_client" / "app.js").read_text(encoding="utf-8")
    mobile_source = (
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx"
    ).read_text(encoding="utf-8")

    assert 'packet_type == "remove_editbox"' in network_source
    assert "on_server_remove_editbox" in window_source
    assert 'case "remove_editbox":' in web_source
    assert 'packet.type === "remove_editbox"' in mobile_source

    web_handler = web_source.split('case "remove_editbox":', 1)[1].split(
        'case "update_locale":', 1
    )[0]
    mobile_handler = mobile_source.split(
        "const handleRemoveEditboxPacket", 1
    )[1].split("const applyMenuPacket", 1)[0]
    assert "this.focusMenuOnNextPacket = true" in web_handler
    assert "requestNativeMenuFocusOnNextPacket();" in mobile_handler


def test_all_clients_retire_runtime_ui_and_voice_on_session_displacement():
    repo_root = CLIENT_DIR.parent
    desktop_source = (CLIENT_DIR / "ui" / "main_window.py").read_text(
        encoding="utf-8"
    )
    web_source = (repo_root / "web_client" / "app.js").read_text(
        encoding="utf-8"
    )
    mobile_source = (
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx"
    ).read_text(encoding="utf-8")

    desktop_handler = desktop_source.split(
        "    def on_server_disconnect(self, packet):", 1
    )[1].split("    def on_force_exit", 1)[0]
    assert (
        "self.cleanup_voice_chat(send_leave=False, announce=False)"
        in desktop_handler
    )
    assert "self.is_reconnecting = False" in desktop_handler
    assert "self.quitting = True" in desktop_handler

    web_retirement = web_source.split("  retireLocalSession(reason", 1)[1].split(
        "  handleServerDisconnect(packet) {", 1
    )[0]
    web_disconnect_handler = web_source.split(
        "  handleServerDisconnect(packet) {", 1
    )[1].split(
        "  handleForceExit(packet) {", 1
    )[0]
    web_force_exit_handler = web_source.split(
        "  handleForceExit(packet) {", 1
    )[1].split("  handleVoiceJoinError(packet) {", 1)[0]
    assert "this.shouldReconnect = false;" in web_retirement
    assert "this.cleanupRuntime(true);" in web_retirement
    assert "this.clearSessionHistory();" in web_retirement
    assert web_retirement.index("this.clearSessionHistory();") < (
        web_retirement.index("this.speak(reason")
    )
    assert "this.retireLocalSession(reason);" in web_disconnect_handler
    assert "this.retireLocalSession(reason);" in web_force_exit_handler
    web_reconnect_failure = web_source.split("  failReconnect() {", 1)[1].split(
        "  disconnectManually() {", 1
    )[0]
    web_manual_disconnect = web_source.split(
        "  disconnectManually() {", 1
    )[1].split("  cleanupRuntime(full = false) {", 1)[0]
    assert "this.retireLocalSession(" in web_reconnect_failure
    assert "this.retireLocalSession(" in web_manual_disconnect

    web_voice_cleanup = web_source.split(
        "  async cleanup(sendLeave = true, announce = true, cancelJoin = true) {",
        1,
    )[1].split("  leave() {", 1)[0]
    assert web_voice_cleanup.index("this.presenceRegistered = false;") < (
        web_voice_cleanup.index("await this.retireRoom(room);")
    )
    web_voice_connect = web_source.split(
        "  async connect(packet, joinGeneration) {", 1
    )[1].split("  attachExistingTracks(room) {", 1)[0]
    assert web_voice_connect.count(
        "this.ownsRoomAttempt(room, joinGeneration)"
    ) == 4
    web_voice_owner = web_source.split(
        "  ownsRoomAttempt(room, joinGeneration) {", 1
    )[1].split("  async retireRoom(room) {", 1)[0]
    assert "this.room === room" in web_voice_owner
    assert "this.joinGeneration === joinGeneration" in web_voice_owner

    mobile_handler = mobile_source.split(
        '        if (packet.type === "disconnect") {', 1
    )[1].split('        if (packet.type === "force_exit") {', 1)[0]
    assert "leaveVoiceChat({" in mobile_handler
    assert "disableAutoReconnect();" in mobile_handler
    assert "resetToLoginScreen(reason);" in mobile_handler


def test_all_clients_clear_old_runtime_ui_before_restored_session_packets():
    repo_root = CLIENT_DIR.parent
    desktop_source = (CLIENT_DIR / "ui" / "main_window.py").read_text(
        encoding="utf-8"
    )
    web_source = (repo_root / "web_client" / "app.js").read_text(
        encoding="utf-8"
    )
    mobile_source = (
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx"
    ).read_text(encoding="utf-8")

    desktop_handler = desktop_source.split(
        "    def on_authorize_success(self, packet):", 1
    )[1].split("    def on_server_speak", 1)[0]
    assert 'if packet.get("reset_ui", False):' in desktop_handler
    assert "self.on_server_clear_ui({})" in desktop_handler

    web_handler = web_source.split("  handleAuthorizeSuccess(packet) {", 1)[1].split(
        "  retireLocalSession(reason", 1
    )[0]
    assert "if (packet.reset_ui === true)" in web_handler
    assert "this.cleanupRuntime(true);" in web_handler

    mobile_handler = mobile_source.split(
        '        if (packet.type === "authorize_success") {', 1
    )[1].split('        if (packet.type === "chat") {', 1)[0]
    assert "if (authPacket.reset_ui === true)" in mobile_handler
    assert "resetRuntimeUiForSession(false);" in mobile_handler
