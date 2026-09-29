from collections.abc import Callable
import logging
from typing import Any

from localization import Localization


LOGGER = logging.getLogger("playaural.slash_commands")

client = None  # The wx.Window instance the client receives
allow_server_commands = True

POSITIVE_STATE_VALUES = (
    "y",
    "yes",
    "t",
    "true",
    "on",
    "enable",
    "enabled",
    "1",
)
NEGATIVE_STATE_VALUES = (
    "n",
    "no",
    "f",
    "false",
    "off",
    "disable",
    "disabled",
    "0",
)
_POSITIVE_STATE_VALUE_SET = frozenset(POSITIVE_STATE_VALUES)
_NEGATIVE_STATE_VALUE_SET = frozenset(NEGATIVE_STATE_VALUES)


def convert_to_bool(
    state: str,
    initial_value: bool | None = None,
    *,
    allow_no_value: bool = False,
    no_value_error: str | None = None,
) -> bool | None | str:
    """Convert a string parameter into a boolean or a permitted missing value.

    When an initial value is available, an omitted state toggles it. Otherwise,
    callers may either allow a missing value or request localized feedback.
    """
    state = state.strip().lower()
    if state == "":
        if initial_value is None:
            if not allow_no_value:
                client.speaker.speak(
                    no_value_error
                    or Localization.get("slash-command-state-required")
                )
                return ""
            return None
        return not initial_value

    if state in _POSITIVE_STATE_VALUE_SET:
        return True
    if state in _NEGATIVE_STATE_VALUE_SET:
        return False
    client.speaker.speak(
        Localization.get(
            "slash-command-invalid-state",
            positive=", ".join(POSITIVE_STATE_VALUES),
            negative=", ".join(NEGATIVE_STATE_VALUES),
        )
    )
    return ""


def get_command_func(command: str) -> Callable[[str], Any] | None:
    for alias in aliases:
        if command in alias[1]:
            return alias[0]
    return None


def process_command(command: str, args: str) -> None:
    func = get_command_func(command)
    if not func:
        if allow_server_commands:
            client.network.send_packet(
                {"type": "slash_command", "command": command, "args": args}
            )
        else:
            client.speaker.speak(
                Localization.get("slash-command-not-found", command=command)
            )
        return
    try:
        func(args)
    except Exception:
        LOGGER.exception("Error executing slash command %s", command)
        client.speaker.speak(Localization.get("slash-command-error", command=command))


def arg_parser(min_args: int = 0, max_args: int = 0):
    if max_args < min_args:
        max_args = min_args

    def decorator(func):
        def wrapper(arg_string):
            parts = arg_string.split(" ", max_args - 1) if arg_string else []
            if len(parts) < min_args:
                client.speaker.speak(
                    Localization.get(
                        "slash-command-min-arguments",
                        command=func.__name__,
                        count=min_args,
                    )
                )
                return
            if len(parts) > max_args:
                client.speaker.speak(
                    Localization.get(
                        "slash-command-max-arguments",
                        command=func.__name__,
                        count=max_args,
                    )
                )
                return
            return func(*parts)

        return wrapper

    return decorator


@arg_parser(0)
def admins():
    client.network.send_packet({"type": "admins_cmd"})


@arg_parser(1)
def broadcast(message: str):
    client.network.send_packet({"type": "broadcast_cmd", "message": message})


@arg_parser(1, 1)
def global_chat(message: str):
    """Send a message to global chat."""
    client.network.send_packet(
        {"type": "chat", "convo": "global", "message": message}
    )

@arg_parser(0, 1)
def set_table_visibility(state: str = ""):
    state = convert_to_bool(state, allow_no_value=True)
    if state == "":
        return
    client.network.send_packet({"type": "set_table_visibility_cmd", "state": state})


@arg_parser(0)
def check_table_visibility():
    client.network.send_packet({"type": "check_table_visibility_cmd"})


@arg_parser(1)
def set_table_pw(password: str):
    client.network.send_packet(
        {
            "type": "set_table_pw_cmd",
            "password": password,
        }
    )


@arg_parser(0)
def remove_table_pw():
    client.network.send_packet({"type": "remove_table_pw_cmd"})


@arg_parser(0)
def check_table_pw():
    client.network.send_packet({"type": "check_table_pw_cmd"})


@arg_parser(0)
def reboot():
    """Reboot the server (Admin only)."""
    # Send as chat message so server _handle_chat intercepts it
    client.network.send_packet(
        {"type": "chat", "convo": "global", "message": "/reboot"}
    )


@arg_parser(0)
def stop():
    """Stop the server (Admin only)."""
    # Send as chat message so server _handle_chat intercepts it
    client.network.send_packet(
        {"type": "chat", "convo": "global", "message": "/stop"}
    )


@arg_parser(1)
def kick(args: str):
    """Kick a user (Admin only)."""
    client.network.send_packet(
        {"type": "chat", "convo": "global", "message": f"/kick {args}"}
    )


aliases = (
    (
        admins,
        {
            "adm",
            "adms",
            "admlist",
            "admslist",
            "admin",
            "admins",
            "adminlist",
            "adminslist",
            "dev",
            "devs",
            "devlist",
            "devslist",
        },
    ),
    (broadcast, {"broadcast", "bcast", "announcement", "announce", "alert", "notify"}),
    (global_chat, {"global", "g", "shout", "s"}),
    (set_table_visibility, {"setvisible", "setvis"}),
    (check_table_visibility, {"checkvisible", "checkvis"}),
    (set_table_pw, {"setpw"}),
    (remove_table_pw, {"removepw"}),
    (check_table_pw, {"checkpw"}),
    (reboot, {"reboot", "restart"}),
    (stop, {"stop", "shutdown", "exit"}),
    (kick, {"kick"}),
)
