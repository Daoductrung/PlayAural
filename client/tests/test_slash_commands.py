from pathlib import Path
from types import SimpleNamespace
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from localization import Localization
from ui import slash_commands


class _Speaker:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def speak(self, message: str) -> None:
        self.messages.append(message)


def _install_client(monkeypatch) -> _Speaker:
    speaker = _Speaker()
    client = SimpleNamespace(
        speaker=speaker,
        network=SimpleNamespace(send_packet=lambda packet: None),
    )
    monkeypatch.setattr(slash_commands, "client", client)
    Localization.init(locales_dir=CLIENT_DIR / "locales", locale="en")
    return speaker


def test_invalid_boolean_state_uses_deterministic_localized_feedback(monkeypatch):
    speaker = _install_client(monkeypatch)

    assert slash_commands.convert_to_bool("unexpected") == ""

    assert speaker.messages == [
        "Invalid state value. Values that enable it: "
        "y, yes, t, true, on, enable, enabled, 1. Values that disable it: "
        "n, no, f, false, off, disable, disabled, 0."
    ]


def test_empty_boolean_state_toggles_the_initial_value(monkeypatch):
    _install_client(monkeypatch)

    assert slash_commands.convert_to_bool("", True) is False
    assert slash_commands.convert_to_bool("   ", True) is False
    assert slash_commands.convert_to_bool("", False) is True
    assert slash_commands.convert_to_bool("  YES  ") is True


def test_unknown_local_command_is_localized(monkeypatch):
    speaker = _install_client(monkeypatch)
    monkeypatch.setattr(slash_commands, "allow_server_commands", False)

    slash_commands.process_command("missing", "")

    assert speaker.messages == ["Slash command missing was not found."]


def test_unknown_local_command_uses_vietnamese_catalog(monkeypatch):
    speaker = _install_client(monkeypatch)
    Localization.set_locale("vi")
    monkeypatch.setattr(slash_commands, "allow_server_commands", False)

    slash_commands.process_command("khongco", "")

    assert speaker.messages == [
        "Không tìm thấy lệnh gạch chéo khongco."
    ]


def test_command_failure_does_not_disclose_internal_exception(monkeypatch):
    speaker = _install_client(monkeypatch)

    def fail(_args: str) -> None:
        raise RuntimeError("sensitive implementation detail")

    monkeypatch.setattr(slash_commands, "get_command_func", lambda command: fail)

    slash_commands.process_command("broken", "")

    assert speaker.messages == ["Error processing slash command broken."]


def test_argument_errors_are_localized(monkeypatch):
    speaker = _install_client(monkeypatch)

    @slash_commands.arg_parser(1, 1)
    def required_command(_value: str) -> None:
        raise AssertionError("the command must not run")

    @slash_commands.arg_parser(0, 0)
    def no_argument_command() -> None:
        raise AssertionError("the command must not run")

    required_command("")
    no_argument_command("unexpected")

    assert speaker.messages == [
        "required_command requires at least one argument.",
        "no_argument_command accepts at most 0 arguments.",
    ]
