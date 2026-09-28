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
from ui.main_window import MainWindow


CLIENT_DIR = Path(__file__).resolve().parents[1]
COPY_CONFORMANCE = json.loads(
    (CLIENT_DIR.parent / "copy_directive_conformance.json").read_text(
        encoding="utf-8"
    )
)


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
