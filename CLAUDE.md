# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PlayAural is an audio-first multiplayer online gaming platform with three components:
- **`server/`** — Python async WebSocket server with game logic and SQLite persistence
- **`client/`** — Python wxPython desktop client (accessibility-focused, screen reader support)
- **`web_client/`** — Vanilla JS PWA web client with ARIA accessibility

## Commands

### Server
```bash
# Run server (default port 8000)
cd server && python -m server
python -m server --host 0.0.0.0 --port 9000 --ssl-cert cert.pem --ssl-key key.pem

# Run tests
cd server && pytest
# Single test
cd server && pytest tests/test_file.py::test_function
```

### Desktop Client
```bash
python client/client.py
```

### Production Build (Windows)
```bat
build_prod.bat
```
This runs PyInstaller twice: once for `updater.spec` (updater.exe), then for `PlayAural.spec` (full client bundle with sounds and locales).

### Web Client
Serve `web_client/` from any HTTP server — it's a static PWA.

## Architecture

### Network Protocol
All communication is WebSocket JSON packets:
```python
Packet(type: str, data: dict)  # PacketType enum defines all message types
```
Key packet types: `AUTHORIZE`, `MENU`, `KEYBIND`, `CHAT`, `SPEAK`, `PLAY_SOUND`, `GAME_ACTION`, etc.

### Server Architecture
- **`server/core/server.py`** — Main orchestrator
- **`server/network/websocket_server.py`** — Async WebSocket connection management
- **`server/games/`** — 21 game implementations; each extends an abstract `Game` base class via 14 mixins
- **`server/game_utils/`** — 40+ shared utility modules (cards, dice, poker logic, turn management, scoring)
- **`server/auth/`** — Argon2 password hashing, rate limiting
- **`server/persistence/database.py`** — SQLite (`PlayAural.db`), user accounts, game history, OpenSkill ratings
- **`server/tables/`** — Table creation, joining, host/guest management, state persistence
- **`server/administration/`** — Admin and moderation tools
- **`server/messages/`** — Fluent-based localization

### Game Implementation Pattern
Games use a mixin-based architecture. Each game class inherits from `Game` plus 14 mixins:
`GameSoundMixin`, `GameCommunicationMixin`, `GameResultMixin`, `GameScoresMixin`,
`GamePredictionMixin`, `TurnManagementMixin`, `MenuManagementMixin`, `ActionVisibilityMixin`,
`LobbyActionsMixin`, `EventHandlingMixin`, `ActionSetCreationMixin`, `ActionExecutionMixin`,
`OptionsHandlerMixin`, `ActionSetSystemMixin`

Games are dataclasses serialized via Mashumaro for state persistence.

### Desktop Client Architecture
- **`client/ui/main_window.py`** — Core UI (2,500+ lines), handles all in-game interaction
- **`client/network_manager.py`** — WebSocket client, receives packets, dispatches to UI
- **`client/sound_manager.py`** — Audio playback
- **`client/config_manager.py`** — User preferences persistence
- **`client/localization.py`** — Fluent runtime localization

### Web Client Architecture
- **`web_client/game.js`** — Single-file game logic (~2,900 lines), connects to same WebSocket server
- **`web_client/locales.js`** — i18n strings
- ARIA live regions for screen reader announcements; service worker for PWA offline support

### Key Tech Stack
- Python 3.11, `asyncio`, `websockets>=12.0`, `mashumaro`, `fluent-compiler`, `openskill`, `argon2-cffi`
- Desktop: `wxPython>=4.2.0`, `accessible-output2`, `sound-lib`
- Package manager: `uv`
- Languages: English, Vietnamese (`vi_VN`)
