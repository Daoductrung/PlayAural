"""
Command-line interface for AI agents to simulate and watch games.

All operations are parameter-based with no interactive input required.

Usage examples:
    # Simulate a Light Turret game with 2 bots
    python -m server.cli simulate lightturret --bots 2

    # Simulate with specific bot names
    python -m server.cli simulate lightturret --bots Alice,Bob,Charlie

    # Set game options
    python -m server.cli simulate lightturret --bots 3 -o starting_power=15 -o max_rounds=30

    # Output as JSON for machine parsing
    python -m server.cli simulate lightturret --bots 2 --json

    # Test serialization (save/restore after each tick)
    python -m server.cli simulate threes --bots 2 --test-serialization

    # List available games
    python -m server.cli list-games

    # Show game options
    python -m server.cli show-options lightturret
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Allow running as standalone script (uv run cli.py)
_MODULE_DIR = Path(__file__).parent
if __name__ == "__main__":
    # Add parent dir to path to find 'server' package if it exists
    sys.path.insert(0, str(_MODULE_DIR.parent))
    # Add current dir to path to find submodules directly if 'server' package doesn't exist
    sys.path.insert(0, str(_MODULE_DIR))

# Handle 'server' package aliasing for root deployment
# This allows 'from server.games import ...' to work even if we are in the root
# and 'server' is not a real package directory.
import types
if "server" not in sys.modules:
    # Create a dummy 'server' package that points to the current directory
    server_pkg = types.ModuleType("server")
    server_pkg.__path__ = [str(_MODULE_DIR)]
    sys.modules["server"] = server_pkg

# Initialize localization before importing games
HAS_SERVER_PACKAGE = False
try:
    # Try direct imports first (script execution)
    from messages.localization import Localization  # noqa: E402
    from games.registry import GameRegistry, get_game_class  # noqa: E402
    from games.base import Game, BOT_NAMES  # noqa: E402
    from users.base import User, generate_uuid  # noqa: E402
    from users.bot import Bot  # noqa: E402
except ImportError:
    # Fallback to package imports (module execution)
    HAS_SERVER_PACKAGE = True
    from server.messages.localization import Localization  # noqa: E402
    from server.games.registry import GameRegistry, get_game_class  # noqa: E402
    from server.games.base import Game, BOT_NAMES  # noqa: E402
    from server.users.base import User, generate_uuid  # noqa: E402
    from server.users.bot import Bot  # noqa: E402


@dataclass
class SpectatorUser(User):
    """
    A spectator user that captures all game output.
    Used for CLI simulation to watch games play out.
    """

    _username: str = ""
    _locale: str = "en"
    _uuid: str = field(default_factory=generate_uuid)
    _messages: list = field(default_factory=list)
    _menus: dict = field(default_factory=dict)  # menu_id -> items
    _json_mode: bool = False
    _quiet: bool = False

    @property
    def username(self) -> str:
        return self._username

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def uuid(self) -> str:
        return self._uuid

    def _log(self, text: str) -> None:
        """Log a message."""
        # Skip messages about the spectator
        if "__spectator__" in text:
            return
        self._messages.append(text)
        if not self._quiet and not self._json_mode:
            print(f"  {text}")

    def speak(self, text: str, buffer: str = "misc") -> None:
        self._log(text)

    def play_sound(
        self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100
    ) -> None:
        pass  # Ignore sounds

    def play_music(self, name: str, looping: bool = True) -> None:
        pass  # Ignore music

    def stop_music(self) -> None:
        pass

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        pass  # Ignore ambience

    def stop_ambience(self) -> None:
        pass

    def show_menu(self, menu_id: str, items: list, **kwargs) -> None:
        # Extract text from MenuItem objects
        item_texts = []
        for item in items:
            if hasattr(item, "text"):
                item_texts.append(item.text)
            elif isinstance(item, dict):
                item_texts.append(item.get("text", str(item)))
            else:
                item_texts.append(str(item))
        self._menus[menu_id] = item_texts

    def update_menu(
        self,
        menu_id: str,
        items: list,
        position: int | None = None,
        selection_id: str | None = None,
    ) -> None:
        self.show_menu(menu_id, items)

    def remove_menu(self, menu_id: str) -> None:
        self._menus.pop(menu_id, None)

    def show_editbox(
        self, input_id: str, prompt: str, default_value: str = "", **kwargs
    ) -> None:
        pass

    def remove_editbox(self, input_id: str) -> None:
        pass

    def clear_ui(self) -> None:
        self._menus.clear()


class GameSimulator:
    """Runs a game simulation with bots and a spectator."""

    def __init__(
        self,
        game_type: str,
        bot_names: list[str],
        options: dict[str, Any],
        json_mode: bool = False,
        quiet: bool = False,
        max_ticks: int = 10000000,
        test_serialization: bool = False,
    ):
        self.game_type = game_type
        self.bot_names = bot_names
        self.options = options
        self.json_mode = json_mode
        self.quiet = quiet
        self.max_ticks = max_ticks
        self.test_serialization = test_serialization

        self.game: Game | None = None
        self.spectator: SpectatorUser | None = None
        self.game_class: type | None = None

    def setup(self) -> bool:
        """Set up the game. Returns True on success."""
        # Get game class
        self.game_class = get_game_class(self.game_type)
        if not self.game_class:
            if not self.json_mode:
                print(f"Error: Unknown game type '{self.game_type}'")
                print("Use 'list-games' to see available games.")
            return False

        # Check player count
        min_players = self.game_class.get_min_players()
        max_players = self.game_class.get_max_players()

        if len(self.bot_names) < min_players:
            if not self.json_mode:
                print(
                    f"Error: {self.game_type} requires at least {min_players} players"
                )
            return False

        if len(self.bot_names) > max_players:
            if not self.json_mode:
                print(f"Error: {self.game_type} allows at most {max_players} players")
            return False

        # Create game instance
        self.game = self.game_class()

        # Apply options
        if hasattr(self.game, "options"):
            for key, value in self.options.items():
                if hasattr(self.game.options, key):
                    # Convert value to appropriate type
                    # Note: Check bool before int because bool is a subclass of int
                    current = getattr(self.game.options, key)
                    if isinstance(current, bool):
                        value = value.lower() in ("true", "1", "yes")
                    elif isinstance(current, int):
                        value = int(value)
                    elif isinstance(current, float):
                        value = float(value)
                    setattr(self.game.options, key, value)
                elif not self.json_mode:
                    print(f"Warning: Unknown option '{key}' for {self.game_type}")

        # Create spectator to watch the game
        self.spectator = SpectatorUser(
            _username="__spectator__", _json_mode=self.json_mode, _quiet=self.quiet
        )

        # Set up host
        self.game.host = self.bot_names[0]

        # Add bot players
        for name in self.bot_names:
            bot_user = Bot(name)
            player = self.game.create_player(bot_user.uuid, name, is_bot=True)
            self.game.players.append(player)
            self.game.attach_user(player.id, bot_user)
            self.game.setup_player_actions(player)

        # Add spectator as a player to receive broadcasts
        spectator_player = self.game.create_player(self.spectator.uuid, "__spectator__", is_bot=False)
        spectator_player.is_spectator = True
        self.game.players.append(spectator_player)
        self.game.attach_user(spectator_player.id, self.spectator)
        self.game.setup_player_actions(spectator_player)

        return True

    def _save_and_restore(self, tick: int) -> None:
        """Save game to JSON and restore it, testing serialization."""
        if not self.game or not self.game_class:
            return

        # Save non-serialized runtime state
        saved_users = dict(self.game._users)
        saved_table = self.game._table
        saved_keybinds = dict(self.game._keybinds)
        saved_pending_actions = dict(self.game._pending_actions)
        saved_status_box_open = set(self.game._status_box_open)
        saved_actions_menu_open = set(self.game._actions_menu_open)
        saved_turn_index = self.game.turn_index

        # Serialize to JSON
        try:
            game_json = self.game.to_json()
        except Exception as e:
            raise RuntimeError(f"Serialization failed at tick {tick}: {e}")

        # Deserialize back
        try:
            self.game = self.game_class.from_json(game_json)
        except Exception as e:
            raise RuntimeError(f"Deserialization failed at tick {tick}: {e}")

        # Restore non-serialized runtime state
        self.game._users = saved_users
        self.game._table = saved_table
        self.game._keybinds = saved_keybinds
        self.game._pending_actions = saved_pending_actions
        self.game._status_box_open = saved_status_box_open
        self.game._actions_menu_open = saved_actions_menu_open

        # Restore turn_index before rebuild
        self.game.turn_index = saved_turn_index
        self.game.rebuild_runtime_state()

    def run(self) -> dict[str, Any]:
        """Run the simulation to completion. Returns results dict."""
        if not self.game or not self.spectator:
            return {"error": "Game not set up"}

        if not self.json_mode and not self.quiet:
            mode_str = " [testing serialization]" if self.test_serialization else ""
            print(
                f"\n=== {self.game.get_name()} ({len(self.bot_names)} bots){mode_str} ===\n"
            )

        # Start the game
        self.game.setup_keybinds()
        self.game.on_start()

        # Run game loop
        tick = 0
        serialization_error = None
        while self.game.game_active and tick < self.max_ticks:
            self.game.on_tick()
            tick += 1

            # Test serialization after each tick if enabled
            if self.test_serialization:
                try:
                    self._save_and_restore(tick)
                except RuntimeError as e:
                    serialization_error = str(e)
                    if not self.json_mode:
                        print(f"\nError: {serialization_error}")
                    break

        # Check for timeout
        timed_out = tick >= self.max_ticks
        if timed_out and not self.json_mode:
            print(f"\nWarning: Game timed out after {self.max_ticks} ticks")

        # Build results - filter out spectator references
        filtered_messages = [
            m for m in self.spectator._messages if "__spectator__" not in m
        ]
        filtered_menu = [
            item
            for item in self.spectator._menus.get("game_over", [])
            if "__spectator__" not in item
        ]

        results = {
            "game_type": self.game_type,
            "game_name": self.game.get_name(),
            "ticks": tick,
            "rounds": self.game.round,
            "timed_out": timed_out,
            "messages": filtered_messages,
            "final_menu": filtered_menu,
        }

        # Add serialization test results
        if self.test_serialization:
            results["serialization_tested"] = True
            if serialization_error:
                results["serialization_error"] = serialization_error
            else:
                results["serialization_passed"] = True

        return results


def cmd_list_games(args):
    """List all available games."""
    games = GameRegistry.get_all()

    if args.json:
        output = []
        for game_class in games:
            output.append(
                {
                    "type": game_class.get_type(),
                    "name": game_class.get_name(),
                    "category": game_class.get_category(),
                    "min_players": game_class.get_min_players(),
                    "max_players": game_class.get_max_players(),
                }
            )
        print(json.dumps(output, indent=2))
    else:
        print("Available games:\n")
        for game_class in games:
            print(f"  {game_class.get_type()}")
            print(f"    Name: {game_class.get_name()}")
            print(f"    Category: {game_class.get_category()}")
            print(
                f"    Players: {game_class.get_min_players()}-{game_class.get_max_players()}"
            )
            print()


def cmd_show_options(args):
    """Show options for a specific game."""
    game_class = get_game_class(args.game_type)
    if not game_class:
        print(f"Error: Unknown game type '{args.game_type}'")
        sys.exit(1)

    # Create instance to inspect options
    game = game_class()

    if not hasattr(game, "options"):
        if args.json:
            print(json.dumps({"options": []}))
        else:
            print(f"{args.game_type} has no configurable options.")
        return

    options_obj = game.options
    options_list = []

    # Inspect the options dataclass
    if HAS_SERVER_PACKAGE:
        from server.game_utils.options import get_option_meta
    else:
        from game_utils.options import get_option_meta

    for field_name in options_obj.__dataclass_fields__:
        current_value = getattr(options_obj, field_name)

        option_data = {
            "name": field_name,
            "type": type(current_value).__name__,
            "default": current_value,
        }

        # Try to get metadata from option_field
        meta = get_option_meta(options_obj, field_name)
        if meta:
            if hasattr(meta, "min_val"):
                option_data["min"] = meta.min_val
            if hasattr(meta, "max_val"):
                option_data["max"] = meta.max_val
            if hasattr(meta, "label"):
                option_data["label"] = meta.label

        options_list.append(option_data)

    if args.json:
        print(
            json.dumps({"game_type": args.game_type, "options": options_list}, indent=2)
        )
    else:
        print(f"Options for {args.game_type}:\n")
        for opt in options_list:
            print(f"  {opt['name']} ({opt['type']})")
            print(f"    Default: {opt['default']}")
            if "min" in opt:
                print(f"    Range: {opt['min']} - {opt['max']}")
            print()


def cmd_simulate(args):
    """Simulate a game with bots."""
    # Parse bot names
    if args.bots.isdigit():
        num_bots = int(args.bots)
        bot_names = BOT_NAMES[:num_bots]
    else:
        bot_names = [name.strip() for name in args.bots.split(",")]

    # Parse options
    options = {}
    if args.option:
        for opt in args.option:
            if "=" in opt:
                key, value = opt.split("=", 1)
                options[key.strip()] = value.strip()

    # Create and run simulator
    simulator = GameSimulator(
        game_type=args.game_type,
        bot_names=bot_names,
        options=options,
        json_mode=args.json,
        quiet=args.quiet,
        max_ticks=args.max_ticks,
        test_serialization=args.test_serialization,
    )

    if not simulator.setup():
        sys.exit(1)

    results = simulator.run()

    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        print(
            f"\n=== Finished: {results['ticks']} ticks, {results['rounds']} rounds ==="
        )
        if results.get("final_menu"):
            print("\nFinal standings:")
            for line in results["final_menu"]:
                if line and not line.lower().startswith("leave"):
                    print(f"  {line}")



def cmd_create_user(args):
    """Create a new user."""
    if HAS_SERVER_PACKAGE:
        from server.persistence.database import Database
        from server.auth.auth import AuthManager
    else:
        from persistence.database import Database
        from auth.auth import AuthManager

    db = Database()
    db.connect()
    auth = AuthManager(db)

    print(f"Creating user '{args.username}'...")
    if auth.register(args.username, args.password, args.locale):
        print(f"Success: User '{args.username}' created.")
        user = db.get_user(args.username)
        if user and user.trust_level >= 2:
             print("Note: User granted ADMIN privileges (First user).")
    else:
        print(f"Error: User '{args.username}' already exists.")
    
    db.close()

def cmd_reset_password(args):
    """Reset a user's password."""
    if HAS_SERVER_PACKAGE:
        from server.persistence.database import Database
        from server.auth.auth import AuthManager
    else:
        from persistence.database import Database
        from auth.auth import AuthManager
    
    db = Database()
    db.connect()
    auth = AuthManager(db)
    
    print(f"Resetting password for '{args.username}'...")
    if auth.reset_password(args.username, args.password):
        print(f"Success: Password updated for '{args.username}'.")
    else:
        print(f"Error: User '{args.username}' not found.")
        
    db.close()

def main():
    parser = argparse.ArgumentParser(
        description="PlayAural CLI for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-games command
    list_parser = subparsers.add_parser("list-games", help="List available games")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # show-options command
    options_parser = subparsers.add_parser(
        "show-options", help="Show options for a game"
    )
    options_parser.add_argument("game_type", help="Game type (e.g., lightturret, pig)")
    options_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # simulate command
    sim_parser = subparsers.add_parser("simulate", help="Simulate a game with bots")
    sim_parser.add_argument("game_type", help="Game type (e.g., lightturret, pig)")
    sim_parser.add_argument(
        "--bots",
        "-b",
        required=True,
        help="Number of bots (e.g., 3) or comma-separated names (e.g., Alice,Bob)",
    )
    sim_parser.add_argument(
        "--option",
        "-o",
        action="append",
        help="Set game option (e.g., -o starting_power=15)",
    )
    sim_parser.add_argument("--json", action="store_true", help="Output as JSON")
    sim_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress game output"
    )
    sim_parser.add_argument(
        "--max-ticks",
        type=int,
        default=10000000,
        help="Maximum ticks before timeout (default: 10000000)",
    )
    sim_parser.add_argument(
        "--test-serialization",
        "-s",
        action="store_true",
        help="Save and restore game state after each tick to test serialization",
    )
    
    # create-user command
    create_user_parser = subparsers.add_parser("create-user", help="Create a new user")
    create_user_parser.add_argument("username", help="Username")
    create_user_parser.add_argument("password", help="Password")
    create_user_parser.add_argument("--locale", default="en", help="Locale (default: en)")

    # reset-password command
    reset_pw_parser = subparsers.add_parser("reset-password", help="Reset a user's password")
    reset_pw_parser.add_argument("username", help="Username")
    reset_pw_parser.add_argument("password", help="New Password")

    args = parser.parse_args()

    if args.command == "list-games":
        cmd_list_games(args)
    elif args.command == "show-options":
        cmd_show_options(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    elif args.command == "create-user":
        cmd_create_user(args)
    elif args.command == "reset-password":
        cmd_reset_password(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
