client = None  # The wx.Window instance the client receives
allow_server_commands = True


def convert_to_bool(
    state: str, initial_value: bool = None, *, allow_no_value: bool = False, no_value_error: str= "The state parameter is required."
) -> bool | str:
    """Convert a string input parameter into a boolean state.
    Supports flipping the existing state, or allowing for returning None type if the existing state is only accessible on the server."""
    if state == "":  # Field is empty, user didn't do this parameter
        if initial_value is None:
            if not allow_no_value:
                client.speaker.speak(no_value_error)
                return ""
            return None
        return not state

    positive = {"y", "yes", "t", "true", "on", "enable", "enabled", "1"}
    negative = {"n", "no", "f", "false", "off", "disable", "disabled", "0"}
    state = state.lower()
    if state in positive:
        return True
    elif state in negative:
        return False
    client.speaker.speak(
        "Invalid state value.\nPositive values: "
        + ", ".join(positive)
        + ".\nNegative values: "
        + ", ".join(negative)
        + "."
    )
    return ""


def get_command_func(command: str) -> callable:
    for alias in aliases:
        if command in alias[1]:
            return alias[0]
    return None


def process_command(command: str, args: str):
    func = get_command_func(command)
    if not func:
        if allow_server_commands:
            client.network.send_packet(
                {"type": "slash_command", "command": command, "args": args}
            )
        else:
            client.speaker.speak(f"Slash command {command} not found.")
        return
    try:
        func(args)
    except Exception as e:
        print(f"Error executing slash command {command}: {e}")
        # Notify user of error
        client.speaker.speak(Localization.get("slash-command-error", command=command))
        client.speaker.speak(str(e))


def arg_parser(min_args: int = 0, max_args: int = 0):
    if max_args < min_args:
        max_args = min_args

    def decorator(func):
        def wrapper(arg_string):
            parts = arg_string.split(" ", max_args - 1) if arg_string else []
            if len(parts) < min_args:
                client.speaker.speak(
                    f"{func.__name__} requires at least {min_args} arguments."
                )
                return
            if len(parts) > max_args:
                client.speaker.speak(
                    f"{func.__name__} takes at most {max_args} arguments."
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
)
