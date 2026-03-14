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

#### Turn Management Rules
- **`set_turn_players(players)`** resets `turn_index` to 0, making `players[0]` the current player immediately.
- **`advance_turn()`** increments the index. Never call it immediately after `set_turn_players` at the start of a round — that skips the first player.
- The canonical pattern for starting a round: `set_turn_players(alive_players)` → `_announce_turn()` (no `advance_turn` between them). See ChaosBear's `on_start` / `_next_round_step` as the reference.
- **`get_active_players()`** excludes spectators. Always use it (never iterate `self.players` directly) when building game results, calculating winners, or announcing per-player results.

#### Host Management / Transient Server-Side Menus
The server can push a transient menu (e.g. Host Management) on top of the in-game UI. To prevent `rebuild_all_menus()` from immediately overwriting it when a keybind fires:
- Add `player.id` to `game._actions_menu_open` **before** pushing the menu to the user.
- Clear it (`_actions_menu_open.discard(player.id)`) in `_return_to_game()` **before** calling `rebuild_player_menu()`.
- `rebuild_all_menus()` skips any player whose ID is in `_actions_menu_open`.

`_is_host_management_hidden` always returns `Visibility.HIDDEN` so the action never appears in the turn menu. It remains accessible via the actions/F5 menu (which checks `show_in_actions_menu`, not `visible`) and the `Ctrl+Shift+M` keybind (`KeybindState.ALWAYS`, `include_spectators=True`). Non-host spectators receive the `action-not-host` disabled reason from the keybind handler.

#### Game Event / Sound Scheduling
- Games use `self.event_queue` (list of `(tick, event_type, data)` tuples) for deferred state changes and `self.schedule_sound(path, delay_ticks)` for audio timing.
- `on_tick()` must call `super().on_tick()` and `self.process_scheduled_sounds()`.
- When writing deterministic tests for bot behaviour, use `advance_until(game, condition_fn, max_ticks=500)` rather than fixed tick counts. Combine state conditions with phase checks (e.g. `len(player.live_influences) == 1 and g.turn_phase != "losing_influence"`) to avoid stopping one tick before a post-event fires.

### Desktop Client Architecture
- **`client/ui/main_window.py`** — Core UI (2,500+ lines), handles all in-game interaction
- **`client/network_manager.py`** — WebSocket client, receives packets, dispatches to UI
- **`client/sound_manager.py`** — Audio playback
- **`client/config_manager.py`** — User preferences persistence; passwords stored in system keyring (never in JSON)
- **`client/localization.py`** — Fluent runtime localization
- **`client/ssl_utils.py`** — Centralized SSL context factory; CA-strict for production (`wss://`), relaxed for localhost

#### Desktop Client Rules
- **Credentials**: Passwords live exclusively in the OS keyring via `keyring` library. `config_manager.py` migrates any legacy plaintext passwords on first load. Never write passwords to JSON.
- **Config file**: All client configuration lives in a single `identities.json` (`%APPDATA%/ddt.one/PlayAural/`). It stores server/account data **and** client options under the top-level `"client_options"` key. There is no separate `option_profiles.json` — a one-shot migration absorbs it on first load if still present. Never split config back into two files.
- **Auto-login failure**: `on_login_failed` in `main_window.py` disables the `auto_login` flag (via `config_manager.update_account`) for permanent credential errors (`wrong_password`, `user_not_found`). Transient errors (`rate_limit`) leave the flag intact. The `client.py` main loop skips auto-login when `came_from_failure` is True, ensuring the user always sees the error dialog after a failed auto-login.
- **SSL**: Always use `make_ssl_context(server_url)` from `ssl_utils.py`. Do not construct `ssl.SSLContext` objects inline.
- **Imports**: All imports at module level. No in-function imports except inside `main()` where CWD must be set first.
- **Dialogs**: Always call `dlg.ShowModal()` and capture the result before calling `dlg.Destroy()`. Never skip `ShowModal()`.
- **PyInstaller**: `client/pyproject.toml` is the source of truth for dependencies (not `requirements.txt`). When adding a dependency that uses dynamic imports (e.g. keyring), add `collect_all('pkg')` plus explicit `hiddenimports` to `PlayAural.spec`.

### Web Client Architecture
- **`web_client/game.js`** — Single-file game logic (~2,900 lines), connects to same WebSocket server
- **`web_client/locales.js`** — i18n strings
- ARIA live regions for screen reader announcements; service worker for PWA offline support

#### Web Client Rules
- **XSS**: Never use `innerHTML` with server-controlled content. Use `element.textContent` or DOM API (`createElement` / `appendChild`) for all user/server data.
- **Credentials**: `pa_pass` lives in `sessionStorage` by default (session-only). When the user checks "Remember Me", write `pa_pass` to `localStorage` and set `localStorage.pa_remember = '1'` as the opt-in flag. Always read `pa_remember` first to determine which store to use for `pa_pass`. `pa_user` always stays in `localStorage`.
- **TTS cleanup**: On `socket.onclose`, always call `stopTTSKeepAlive()`, clear `ttsTimeout`, flush `ttsQueue = []`, reset `isTTSPlaying = false`, and call `speechSynthesis.cancel()`.
- **Reconnect state**: `reconnectAttempts` and `reconnectTimer` are initialized in the `GameClient` constructor. Exponential backoff is capped at 30 s with MAX_RETRIES = 5.

### Server Menu Auto-Refresh Pattern
The canonical pattern for any menu that displays live data:

1. **`_get_<menu>_items(user) -> list[MenuItem]`** — pure data builder, no side effects.
2. **`_show_<menu>(user)`** — calls `_get_*_items`, then `user.show_menu(...)` and sets `_user_states`. Used for **initial display only**.
3. **Auto-refresh callbacks** (`on_tables_changed`, `on_user_presence_changed`, `on_friend_requests_changed`) — call `_get_*_items` and then **`user.update_menu(...)`** to push new content without resetting the user's cursor position.

**Never call `_show_<menu>()` from a refresh callback** — that triggers `show_menu()` which snaps the user's selection to item #1.

Menus that currently auto-refresh:
| Menu | Refresh trigger |
|---|---|
| `active_tables_menu` | `on_tables_changed` |
| `tables_menu` (per-game) | `on_tables_changed` |
| `friends_list_menu` | `on_user_presence_changed`, `on_friend_requests_changed` |
| `friends_hub_menu` | `on_friend_requests_changed` |
| `friend_requests_menu` | `on_friend_requests_changed` |
| `online_users` | `on_user_presence_changed` |

### Key Tech Stack
- Python 3.11, `asyncio`, `websockets>=12.0`, `mashumaro`, `fluent-compiler`, `openskill`, `argon2-cffi`
- Desktop: `wxPython>=4.2.0`, `accessible-output2`, `sound-lib`, `keyring>=24.0`
- Package manager: `uv`
- Languages: English, Vietnamese (`vi_VN`)
