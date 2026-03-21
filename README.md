# PlayAural

An audio-first multiplayer online gaming platform with a strong focus on accessibility, screen reader support, and multi-language play.

Built upon the open-source foundation of **PlayPalace**. Developed and maintained by **Trung (ddt.one)**.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running in Development](#running-in-development)
- [Configuration](#configuration)
- [Production Build](#production-build)
- [Running Tests](#running-tests)
- [Game Catalog](#game-catalog)
- [Network Protocol](#network-protocol)
- [Localization](#localization)
- [Game Implementation Pattern](#game-implementation-pattern)

---

## Architecture Overview

PlayAural has three independent components that communicate over WebSocket:

| Component | Language / Stack | Description |
|-----------|-----------------|-------------|
| `server/` | Python 3.11, asyncio | Async WebSocket server — game logic, auth, persistence |
| `client/` | Python, wxPython | Desktop client — accessibility-focused, screen reader support |
| `web_client/` | Vanilla JS PWA | Browser client — ARIA live regions, service worker, offline support |

All client↔server communication uses JSON-encoded `Packet(type, data)` messages defined by the `PacketType` enum.

---

## Project Structure

```
PlayAural/
├── server/
│   ├── core/               # Main server orchestrator
│   ├── network/            # Async WebSocket connection management
│   ├── games/              # all game implementations (one directory each)
│   ├── game_utils/         # 40+ shared mixins & utilities (cards, dice, scoring…)
│   ├── tables/             # Table creation, joining, host/guest management
│   ├── auth/               # Argon2 password hashing, rate limiting
│   ├── persistence/        # SQLite database (PlayAural.db), OpenSkill ratings
│   ├── administration/     # Admin & moderation tools
│   ├── messages/           # Fluent localization files (EN, VI)
│   ├── tests/              # pytest test suite
│   └── pyproject.toml
├── client/
│   ├── ui/                 # wxPython UI
│   ├── network_manager.py  # WebSocket client, packet dispatch
│   ├── sound_manager.py    # Audio playback
│   ├── config_manager.py   # User preferences
│   ├── localization.py     # Fluent runtime localization
│   └── pyproject.toml
├── web_client/
│   ├── game.js             # Single-file game logic
│   ├── locales.js          # i18n strings
│   └── service_worker.js   # PWA offline support
├── sounds/                 # Shared audio assets
├── requirements.txt        # Unified pip requirements (all components + dev)
├── build_prod.bat          # Windows production build (PyInstaller)
└── CLAUDE.md               # AI assistant guidance
```

---

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) — fast Python package manager
  - Alternatively, use `pip` with `requirements.txt`
- **wxPython** — required for the desktop client; not needed for server-only setups
- **A WebSocket-capable browser** — for the web client

---

## Installation & Setup

### Server

```bash
cd server
uv sync                      # installs dependencies from pyproject.toml
```

Or with pip:

```bash
pip install websockets>=12.0 mashumaro>=3.11 fluent-compiler>=1.0 \
            babel>=2.14 openskill>=6.1.3 argon2-cffi>=23.1
```

### Desktop Client

```bash
cd client
uv sync
uv pip install fluent.runtime   # must be installed separately
```

Or with pip:

```bash
pip install wxPython>=4.2.0 accessible-output2>=0.16 websockets>=12.0 \
            sound-lib>=0.2.2 fluent-runtime>=0.4.0 requests psutil
```

### All-in-one (pip, all components + dev tools)

```bash
pip install -r requirements.txt
```

---

## Running in Development

### Server

```bash
# Default: localhost:8000
cd server && python -m server

# Custom host/port, with TLS
python -m server --host 0.0.0.0 --port 9000 --ssl-cert cert.pem --ssl-key key.pem
```

On Windows: `server\run_server.bat`

### Desktop Client

```bash
python client/client.py
```

On Windows: `client\run_client.bat`

### Web Client

The web client is a static PWA — serve `web_client/` from any HTTP server:

```bash
python -m http.server 8080 --directory web_client
```

On Windows: `run_web_local.bat`

Then open `http://localhost:8080`. The server URL is configured inside `web_client/game.js`.

---

## Configuration

### Server

Key settings are in `server/config.py` (or passed as CLI arguments):

- `--host` / `--port` — bind address (default `localhost:8000`)
- `--ssl-cert` / `--ssl-key` — optional TLS certificate paths
- The SQLite database (`PlayAural.db`) is created automatically on first run

### Desktop Client

User preferences are persisted by `client/config_manager.py`. The server URL and other options are configurable from the client's Settings menu.

---

## Production Build

Windows only — requires [PyInstaller](https://pyinstaller.org/):

```bat
build_prod.bat
```

This runs PyInstaller twice:
1. `updater.spec` → `updater.exe` (auto-updater stub)
2. `PlayAural.spec` → full client bundle (sounds, locales, dependencies bundled)

Output appears in `dist/`.

---

## Running Tests

Tests live in `server/tests/` and use `pytest` with `pytest-asyncio`:

```bash
cd server
pytest                                         # run all tests
pytest tests/test_file.py::test_function       # single test
pytest -v                                      # verbose output
```

---

## Game Catalog

24 games across four categories:

### Card Games

| Game | Description |
|------|-------------|
| Texas Hold'em | Classic community-card poker |
| Five Card Draw | Traditional draw poker |
| Blackjack | Classic casino card game against the dealer |
| Pusoy Dos | Filipino shedding card game |
| Crazy Eights | Classic shedding card game |
| Last Card | Uno-style shedding game with stacking, jump-ins, and 20+ customizable house rules |
| Scopa | Traditional Italian card-capture game |
| Ninety Nine | Keep the running count under 99 |
| Mile by Mile | Strategic racing card game |

### Dice Games

| Game | Description |
|------|-------------|
| Farkle | Push-your-luck dice scoring |
| Toss Up | Push-your-luck with color-coded dice faces |
| Threes | Low-score dice game — threes are worth zero |
| Yahtzee | Classic combination dice game |
| Left Right Center | Fast-paced social dice game |
| Midnight | Build the best hand before midnight |
| Pig | Simple push-your-luck dice race |
| Rolling Balls | Draw balls from a pipe for points |

### Adventure & Board

| Game | Description |
|------|-------------|
| Pirates of the Lost Seas | Competitive RPG — sail, battle, collect gems |
| Snakes and Ladders | Classic board game |
| Light Turret | Resource management — power and light |
| Chaos Bear | Push-your-luck chase game |
| Dominos | Classic tile-matching game with Draw/Block modes, spinner support, and team play |

### Social / Party

| Game | Description |
|------|-------------|
| Coup | Hidden-role social deduction |
| Trade-off | Competitive dice-trading game |

---

## Network Protocol

All messages are JSON-encoded packets:

```python
Packet(type: str, data: dict)
```

Key packet types (defined in `PacketType` enum):

| Packet | Direction | Purpose |
|--------|-----------|---------|
| `AUTHORIZE` | C→S | Login / register |
| `MENU` | S→C | Send menu structure to client |
| `KEYBIND` | S→C | Register keyboard shortcut |
| `CHAT` | Both | Chat messages |
| `SPEAK` | S→C | Screen reader announcement |
| `PLAY_SOUND` | S→C | Trigger audio playback |
| `GAME_ACTION` | C→S | Player performs a game action |

---

## Localization

The server uses [Fluent](https://projectfluent.org/) for all player-facing strings. Locale files live in `server/messages/`:

- `en/` — English (default)
- `vi/` — Vietnamese (`vi_VN`)

The desktop client uses `fluent-runtime` via `client/localization.py`. The web client uses `web_client/locales.js`.

To add a language: create a matching locale directory under `server/messages/` and add corresponding entries to `web_client/locales.js`.

---

## Game Implementation Pattern

Each game is a Python dataclass in `server/games/<name>/game.py` that inherits from the abstract `Game` base class plus 14 shared mixins:

```
GameSoundMixin, GameCommunicationMixin, GameResultMixin, GameScoresMixin,
GamePredictionMixin, TurnManagementMixin, MenuManagementMixin, ActionVisibilityMixin,
LobbyActionsMixin, EventHandlingMixin, ActionSetCreationMixin, ActionExecutionMixin,
OptionsHandlerMixin, ActionSetSystemMixin
```

Game state is serialized to/from JSON via Mashumaro (`DataClassJSONMixin`) for persistence across server restarts.
