# PlayAural v0.1

PlayAural is an accessible online gaming platform. This repository contains both the server (v0.1, modern) and client (ported from v10).

## Contact

If you have questions, want realtime information, or plan to develop for the project, you can join the [PlayAural discord server](https://discord.gg/PBPZegdsTN) here.

This is the primary place for discussion about the project.

## Quick Start

You need Python 3.11 or later. We use [uv](https://docs.astral.sh/uv/) for dependency management on the server and client.

### Running the Server

```bash
cd server
uv sync
uv run python main.py
```

To run a local server with the default configuration, you can launch the "run_server.bat" file as a shortcut.

The server starts on port 8000 by default. Use `--help` to see all options:

```bash
uv run python main.py --help
```

Common options:
- `--port PORT` - Port number (default: 8000)
- `--host HOST` - Host address (default: 0.0.0.0)
- `--ssl-cert PATH` - SSL certificate for WSS (secure WebSocket)
- `--ssl-key PATH` - SSL private key for WSS

### Running with SSL/WSS (Secure WebSocket)

To run the server with SSL encryption (required for production deployments):

**Using Let's Encrypt certificates:**
```bash
uv run python main.py --port 8000 \
  --ssl-cert /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
  --ssl-key /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

**Using self-signed certificates (for testing):**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"

# Run server with self-signed certificate
uv run python main.py --port 8443 --ssl-cert cert.pem --ssl-key key.pem
```

When SSL is enabled, the server will report `wss://` instead of `ws://` in its startup message. Clients connecting to a WSS server must use the `wss://` protocol in their connection URL.

### Running the Client

```bash
cd client
uv sync
uv run python client.py
```

You can launch the "run_client.bat" file as a shortcut.

The client requires wxPython and a few other dependencies from v10.

The client supports both `ws://` and `wss://` connections. When connecting to a server with SSL enabled, enter the server address with the `wss://` prefix (e.g., `wss://example.com`). The client will handle SSL certificate validation automatically.
Use the **Server Manager** button on the login screen to add/edit servers (name, host, port, notes) and manage saved accounts for each server. You can add `localhost` for local testing.

## Project Structure

The server and client are separate codebases with different philosophies.

### Server

The server is a complete rewrite for v0.1. It uses modern Python practices: dataclasses for all state, Mashumaro for serialization, websockets for networking, and Mozilla Fluent for localization.

We hold the view that game simulations should be entirely state-based. If a game can't be saved and loaded without custom save/load code, something has gone wrong. This is why everything is a dataclass, and why games never touch the network directly.

Key directories:
- `server/core/` - Server infrastructure, websocket handling, tick scheduler
- `server/games/` - Game implementations (Pig, Scopa, Threes, Light Turret, etc.)
- `server/game_utils/` - Shared utilities for games (cards, dice, teams, turn order)
- `server/auth/` - Authentication and session management
- `server/persistence/` - SQLite database for users and tables
- `server/messages/` - Localization system
- `server/plans/` - Design documents explaining architectural decisions

### Client

The client is ported from v10. It works, but it carries some technical debt from the older codebase. You may encounter rough edges.

The client is built with wxPython and designed for accessibility. It communicates with the server over websockets using JSON packets.

## Running Tests

The server has comprehensive tests. We run them frequently during development.

```bash
cd server
uv run pytest
```

For verbose output:

```bash
uv run pytest -v
```

The test suite includes unit tests, integration tests, and "play tests" that run complete games with bots. Play tests save and reload game state periodically to verify persistence works correctly.

See also: CLI tool.

## Available Games

Note: many games are still works in progress.

- **Pig** - A push-your-luck dice game
- **Threes** - Another push-your-luck game, with a little more complexity
- **Scopa** - A complex game about collecting cards
- **Light Turret** - A dice game from the RB Play Center
- **Chaos Bear** - Another RB Play Center game about getting away from a bear
- **Mile by Mile** - A racing card game
- **Farkle** - A dice game somewhat reminiscent of Yahtzee
- **Yahtzee** - Classic dice game with 13 scoring categories
- **Ninety Nine** - Card game about keeping the running total under 99
- **Pirates of the Lost Seas** - RPG adventure with sailing, combat, and leveling
- **Tradeoff** - Dice trading game with set-based scoring
- **Toss Up** - Push-your-luck dice game with green/yellow/red dice
- **1-4-24** - Dice game where you keep 1 and 4, score the rest
- **Left Right Center** - Dice-and-chip elimination game
- **Age of Heroes** - Civilization-building card game (cities, monument, or last standing)

## CLI Tool

The server also includes a CLI for simulating games without running the full server. This is useful for testing and for AI agents. It does not supercede play tests, but works alongside them, and allows you to very quickly test specific scenarios.

```bash
cd server

# List available games
uv run python -m server.cli list-games

# Simulate a game with bots
uv run python -m server.cli simulate pig --bots 2

# Simulate with specific bot names
uv run python -m server.cli simulate lightturret --bots Alice,Bob,Charlie

# Output as JSON
uv run python -m server.cli simulate pig --bots 3 --json

# Test serialization (save/restore each tick)
uv run python -m server.cli simulate threes --bots 2 --test-serialization
```

## Architecture Notes

A few things worth understanding about how the server works:

**Tick-based simulation.** The server runs a tick every 50 milliseconds. Games don't use coroutines or async/await internally. All game logic is synchronous and state-based. This makes testing straightforward and persistence trivial.

**User abstraction.** Games never send network packets directly. They receive objects implementing the `User` interface and call methods like `speak()` and `show_menu()`. The actual user might be a real network client, a test mock, or a bot. Games don't need to know or care.

**Actions, not events.** There's a layer between "event received from network" and "action executed in game". Bots call actions directly on tick. Human players trigger actions through network events. The game logic is the same either way.

**Imperative state changes.** We recommend changing game state imperatively, not declaratively. Actions should directly end turns and send messages, not return results describing what should happen.

For more details, see the design documents in `server/plans/`.

## Known Issues

The client is a port from v10 and may have compatibility issues with some v0.1 features. If something doesn't work as expected, the server is likely fine and the client needs adjustment.

## Development

The server uses uv for dependency management. To add a dependency:

```bash
cd server
uv add <package>
```

For development dependencies:

```bash
uv add --dev <package>
```

When writing new games, look at existing implementations in `server/games/` for patterns. Pig is a good simple example. Scopa demonstrates card games with team support.
