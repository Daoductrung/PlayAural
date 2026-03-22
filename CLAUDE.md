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

**`silent` flag on `chat` packets**: Adding `"silent": True` to a `chat` packet suppresses both the notification sound (`notify.ogg` / `chat.ogg`) and the TTS readout in both the desktop and web clients. The message is still written to the chat log. Use this when the server is also sending an explicit `speak` packet and a `play_sound` packet to take full control over audio output — e.g. the server alert broadcast countdown. Never set `silent` on regular user-visible chat messages.

### Server Architecture
- **`server/core/server.py`** — Main orchestrator
- **`server/network/websocket_server.py`** — Async WebSocket connection management
- **`server/games/`** — 25 game implementations; each extends an abstract `Game` base class via 14 mixins
- **`server/game_utils/`** — ~40 shared utility modules (cards, dice, poker logic, turn management, scoring)
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

#### Spectator Action Visibility (`include_spectators`)

Every `Action` has an `include_spectators: bool = False` field that controls whether spectators can see and execute the action. The default is `False` — spectators are blocked from all actions unless explicitly opted in.

Enforcement happens at three layers:
1. **`ActionSet.get_visible_actions`** — turn menu; filters per-action using `include_spectators`. Spectators see only actions where `include_spectators=True` AND `is_hidden` returns `VISIBLE`.
2. **`ActionSet.get_enabled_actions`** — actions menu (Escape); spectators see only actions with `include_spectators=True`.
3. **`ActionExecutionMixin.execute_action`** — defense-in-depth; blocks execution of non-`include_spectators` actions regardless of how the request arrived.

**When adding a new game action**, decide at definition time:
- `include_spectators=True` — public information readable by any observer (e.g. table state, scores, turn timer, start game for host). The corresponding `define_keybind` call should also have `include_spectators=True`.
- `include_spectators=False` (default) — player-private actions (e.g. play a card, read your hand, fold, raise, view your captured cards, your seat position). The keybind should also omit `include_spectators` (defaults to `False`).

The `include_spectators` flag on `Action` and `Keybind` must always agree. Inconsistency (action accessible in actions menu but keybind blocked, or vice versa) creates confusing UX.

**Host spectator edge case**: `start_game`, `add_bot`, `remove_bot` are marked `include_spectators=True` so a player who toggles to spectator in the lobby retains host management. Non-host spectators cannot trigger these because the `is_enabled` callbacks gate by host identity (`player.name != self.host`).

Standard/lobby actions already marked `include_spectators=True` in the base class: `show_actions`, `toggle_spectator`, `host_management`, `leave_game`, `start_game`, `add_bot`, `remove_bot`, `whose_turn`, `whos_at_table`, `check_scores`, `check_scores_detailed`, `predict_outcomes`, `game_info`, `game_rules`.

#### Action Set Ordering & Menu Deduplication

`get_all_enabled_actions()` combines action sets in this order: **turn → lobby → options → standard**. The Escape/actions menu displays them in this combined order. Two rules prevent UX issues:

**1. Info/status actions belong in `create_standard_action_set`, not `create_turn_action_set`.**
Game-specific read-only actions (check hand, view dice, check status, view table, etc.) must be defined in `create_standard_action_set`. Placing them in the turn set causes them to appear *above* the platform's default global actions (leave game, scores, game info) in the Escape menu, breaking consistent ordering across games. They are still accessible via their keybinds regardless of which set they belong to.

**2. Turn actions that should not appear in the Escape menu need `show_in_actions_menu=False`.**
Core gameplay actions (hit, stand, roll, play card, shoot, etc.) already appear as tappable buttons in the turn menu. Without `show_in_actions_menu=False`, they also appear at the *top* of the Escape/actions menu, pushing global actions down. Set `show_in_actions_menu=False` on any turn action that is already visible in the turn menu and has no reason to appear in the global actions list.

**Summary:**
- **Turn action set**: Only actions that need to appear as turn menu buttons (play, roll, pass, etc.) with `show_in_actions_menu=False`.
- **Standard action set**: Info/status actions (check hand, view scores, view table, etc.) — always below default global actions in the Escape menu.
- **Keybinds**: Work independently of which action set an action belongs to.

#### Turn Management Rules
- **`set_turn_players(players)`** resets `turn_index` to 0, making `players[0]` the current player immediately.
- **`advance_turn()`** increments the index. Never call it immediately after `set_turn_players` at the start of a round — that skips the first player.
- The canonical pattern for starting a round: `set_turn_players(alive_players)` → `announce_turn()` (no `advance_turn` between them). See ChaosBear's `on_start` / `_next_round_step` as the reference.
- **`get_active_players()`** excludes spectators. Always use it (never iterate `self.players` directly) when building game results, calculating winners, or announcing per-player results.

#### Server-Side Menu Navigation Stack

All server-side menu navigation uses a breadcrumb stack stored in `_user_states[username]["_stack"]`. Four primitives manage it:

- **`_nav_push(user, show_fn, *args)`** — Captures the current state frame, pushes it onto `_stack`, calls `show_fn`, then re-injects the stack. Use for **forward navigation** (opening a sub-menu). Contains the modal-focus guard (see below) — automatically a no-op when any editbox is active.
- **`_nav_back(user)`** — Pops the top frame and calls `_restore_frame`. If the stack is empty, falls back to the game table or main menu. Use for all **Back** button handlers.
- **`_nav_refresh(user, show_fn, *args)`** — Saves `_stack`, calls `show_fn`, then re-injects the stack unchanged. Use when an **action completes** and the user stays on the same menu level (e.g. accept friend request → refresh friend requests menu). Never use a bare `_show_*()` call in an action handler — it drops the stack.
- **`_restore_frame(user, frame, stack)`** — Re-enters the correct show function for a popped frame, then re-injects the remaining stack. Routes `in_game`/`post_game`/etc. to `_return_to_game`; routes all overlay menus (including admin menus) to their show functions. Falls back to game/main-menu for any unrecognised ID.

**Rules:**
- `_nav_push` = navigate forward (add a frame to history)
- `_nav_refresh` = stay in place after an action (preserve history)
- `_nav_back` = go back (pop a frame from history)
- Never call `_show_*()` directly in an action handler — always use `_nav_refresh` so the stack survives. This applies to **all** action handlers: confirmations, toggle flips, error paths, editbox returns, and fallback/offline paths alike.

#### Editbox Input States (`_enter_input_state`)

Any time the server transitions a user into an editbox, call `_enter_input_state(user, input_id, **extra)` instead of mutating `_user_states` directly. It:
1. Snapshots the current (stable, non-editbox) state as `_parent_frame`
2. Sets `_transient = True` in the state

This prevents two classes of bugs:

**Stack corruption**: `_nav_push` checks `_transient` and, when True, pushes `_parent_frame` instead of the unrestorable editbox ID. Editbox states therefore never end up on the nav stack, so `_restore_frame` never needs to handle them.

**Modal-focus desync**: `_nav_push` calls `_user_is_in_input_state(username)` at the top and returns immediately if it returns True. This covers both:
- Server-side editboxes (`_transient = True`, set by `_enter_input_state`)
- Game-side editboxes (`_pending_actions[player.id]` set by `_request_action_input`)

Because the guard lives inside `_nav_push` itself — not in individual hotkey handlers — every code path (Alt+F friends hub, Alt+O options, Shift+F2 online users, game keybind actions, future additions) is automatically protected. No per-handler decoration needed or possible to forget.

Use `self.server.enter_input_state(user, input_id, **extra)` from `administration/manager.py` (public alias). Never assign `_user_states[username]["menu"] = "..._input"` directly.

#### Host Management / Transient Server-Side Menus
The server can push a transient menu (e.g. Host Management) on top of the in-game UI. To prevent `rebuild_all_menus()` from immediately overwriting it when a keybind fires:
- Add `player.id` to `game._actions_menu_open` **before** pushing the menu to the user.
- Clear it (`_actions_menu_open.discard(player.id)`) in `_return_to_game()` **before** calling `rebuild_player_menu()`.
- `rebuild_all_menus()` skips any player whose ID is in `_actions_menu_open`.

`_is_host_management_hidden` always returns `Visibility.HIDDEN` so the action never appears in the turn menu. It remains accessible via the actions menu/Escape (which checks `show_in_actions_menu`, not `visible`) and the `Ctrl+M` keybind (`KeybindState.ALWAYS`, `include_spectators=True`). Non-host spectators receive the `action-not-host` disabled reason from the keybind handler.

#### Universal Redraw Guard (GLOBAL_SYSTEM_MENUS)
`server.GLOBAL_SYSTEM_MENUS` is a class-level set of menu IDs that represent server-side overlays (friends hub, options, online users, public profile, etc.). Two invariants are enforced:

1. **`rebuild_player_menu` / `update_player_menu`** in `menu_management_mixin.py` return early if `_user_states[username]["menu"]` is in `GLOBAL_SYSTEM_MENUS` **or** `_user_states[username]["_transient"]` is True. This prevents game tick redraws from overwriting an overlay or an active editbox the user is currently viewing.
2. **`_show_end_screen_to_player`** in `game_result_mixin.py` checks if the player's current state is in `GLOBAL_SYSTEM_MENUS` and, if so, resets it to `{"menu": "in_game", "table_id": ...}` and clears `_actions_menu_open`. This prevents the post-game screen from being unresponsive when the game ends while an overlay is open.

When the `_user_states` assignment must happen **before** `rebuild_all_menus()` or `initialize_lobby()` fires (table creation/join), set state first or the guard will block the initial turn-menu push.

#### Reconnect / Ghost Player Cleanup (`_restore_user_state`)
When a player reconnects, `_restore_user_state` checks `_tables.find_user_table(username)` and applies the following cleanup rules before restoring game state:

- **Lobby (no active game)**: `table.game is None` → call `table.remove_member(username)` immediately. The player lands on the main menu. Without this, they become a ghost member that the lobby-kick timer later fires on.
- **Spectator**: remove from `table.members` and call `table.game.remove_spectator(user.uuid)`. Spectators are never auto-restored.
- **Active player, UUID found**: reattach via `table.attach_user` + `table.game.attach_user`; mark `restored_game = True`. Immediately call `table.game.rebuild_player_menu(player)` after setting `_user_states` — do not rely on the next game tick.
- **Active player, UUID not found** (inconsistent saved state): call `table.remove_member(username)`. Player lands on the main menu cleanly with no ghost membership.

`table.remove_member` always cleans up `_username_to_table` — no stale mapping remains.

**Non-game state restoration**: when `restored_game = False`, call `self._restore_menu_from_state(user, state)`. This delegates to `_restore_frame`, which is the single canonical router covering every menu ID (including GLOBAL_SYSTEM_MENUS, admin menus, and `main_menu`) and re-injects the saved `_stack`. Never use a hardcoded `elif` chain here — it will always be incomplete and will silently fail for any menu ID not listed.

#### Server Alert Broadcast (`/reboot` and `/stop`)
The shutdown sequence is a 32-second structured countdown managed by `self._shutdown_task: asyncio.Task | None`.

- **Double-invocation guard**: if `_shutdown_task` is already running (not `None` and not `.done()`), the second command is silently ignored.
- **Countdown schedule**: broadcast at 30 s and 20 s (full localized sentence + `server_alert_warning.ogg`), then every second from 10 s down to 1 s (raw number only + `server_alert_tick.ogg`).
- **TTS control**: all countdown chat packets carry `"silent": True` (suppresses both notification sound and TTS in both clients). A separate `{"type": "speak", "text": "..."}` packet drives TTS with the exact desired text — bare number for countdown ticks, full sentence for warnings.
- **Final phase**: shutdown sound (`server_alert_shutdown.ogg`) + silent chat + explicit `speak` + `disconnect` packet (`"reconnect": true/false`) sent to all approved users, then 2 s sleep, then `stop()` → `os._exit(1)`.
- **`stop()` order**: tick scheduler → WS server (disconnect handlers fire here) → cancel `_pending_disconnects` tasks → cancel `_shutdown_task` → `_save_tables()` → close DB.
- **Locale keys**: `server-restarting` (with `$seconds`), `server-restarting-now`, `server-shutting-down` (with `$seconds`), `server-shutting-down-now` — all in both `en` and `vi` FTL files.
- **Sound files**: `client/sounds/server_alert_warning.ogg`, `server_alert_tick.ogg`, `server_alert_shutdown.ogg`.

#### Game Event / Sound Scheduling
- Games use `self.event_queue` (list of `(tick, event_type, data)` tuples) for deferred state changes and `self.schedule_sound(path, delay_ticks)` for audio timing.
- `on_tick()` must call `super().on_tick()` and `self.process_scheduled_sounds()`.
- When writing deterministic tests for bot behaviour, use `advance_until(game, condition_fn, max_ticks=500)` rather than fixed tick counts. Combine state conditions with phase checks (e.g. `len(player.live_influences) == 1 and g.turn_phase != "losing_influence"`) to avoid stopping one tick before a post-event fires.

#### Web/Mobile UI Consideration (Mandatory)
When implementing a new game, always consider the web/mobile client experience alongside the desktop client. Desktop users have keyboard shortcuts for every action, but web/mobile users rely on tappable buttons in the Turn Menu. Key rules:
- **Time-critical reaction actions** (e.g. buzzer, jump-in, challenge, accept) must be visible as tappable buttons in the Turn Menu during their active windows for web clients. Use `getattr(user, "client_type", "") == "web"` in `is_hidden` callbacks to show them only for web users (desktop users use keybinds).
- **Utility actions** that desktop users access via keybinds (e.g. sort hand) should also appear in the Turn Menu for web clients.
- **Turn Menu ordering** matters for screen readers: place reaction buttons first (top), then card/play actions in the middle, then utility buttons (draw, pass, sort) last. Use the `_sync_turn_actions` reordering pattern from LastCard/CrazyEights as the reference.
- **Standard action ordering for web** must be consistent across all games: game-specific info actions first, then `check_scores` (if applicable), then `whose_turn`, then `whos_at_table`. Add web reordering in `create_standard_action_set` and `_is_check_scores_hidden` visibility override for games that track scores.
- See `server/games/lastcard/game.py` (`_is_buzzer_hidden`, `_is_jump_in_hidden`, `_is_sort_turn_hidden`, and the web reordering block in `_sync_turn_actions`) for the canonical implementation.

#### TTS Buffer Categorization
Every `user.speak_l()` and `broadcast_l()` call must carry an explicit `buffer=` parameter. Defaults are wrong in almost every case:
- `user.speak_l()` defaults to `"misc"` — almost never correct in `server.py`
- `broadcast_l()` defaults to `"game"` — correct for in-game events only

Rules:
- **`buffer="chat"`**: Player-to-player text only (global chat, room chat, private messages).
- **`buffer="game"`**: All gameplay events — turn announcements, dice rolls, card plays, scores, game state changes. Use for all `broadcast_l` calls inside game files.
- **`buffer="system"`**: Server-wide announcements, player connections/disconnections, room joins/leaves, host management (kicks, bans, invitations, host-pass), settings confirmations, profile changes, friend events, and all error/validation messages in `server.py`. Most `user.speak_l` calls in `server/core/server.py` belong here.
- **`buffer="misc"`**: Only for genuinely minor informational messages that fit none of the above.

Connectivity/membership `broadcast_l` calls in `base.py`, `table.py`, and `lobby_actions_mixin.py` (player-rejoined, table-joined, now-spectating, player-replaced-by-bot, game-resumed, etc.) also use `buffer="system"`.

#### Administration Privilege Tiers

The server has three privilege levels stored as `user.trust_level` (integer):

| Level | Role | Capabilities |
|---|---|---|
| 1 | **User** | Default; no admin access |
| 2 | **Admin** | Account approval, promote/demote admins, ban/unban, mute/unmute, kick, broadcast, MOTD |
| 3 | **Dev** | All admin capabilities plus SMTP configuration; immune from demotion/banning |

The first user to register is automatically promoted to Dev (`trust_level = 3`).

**Dev-only features**: SMTP configuration (`smtp_settings` menu and all sub-menus) is restricted to `trust_level >= 3`. Enforcement is three-layer:
1. **UI**: `_show_admin_menu` only appends the SMTP menu item when `user.trust_level >= 3`.
2. **Routing**: the `smtp_settings` selection handler re-checks `trust_level >= 3` and speaks `dev-only-action` + refreshes the admin menu for Admins.
3. **Defense-in-depth**: `_show_smtp_settings_menu`, `_handle_smtp_settings_selection`, `_handle_smtp_encryption_selection`, and the editbox input handler each guard `trust_level < 3` at the top before touching any data.

When adding a new Dev-only admin action, apply the same three layers; do not rely on menu visibility alone.

#### Server Import Rules
All imports at module level. No in-function imports anywhere in the server codebase — this rule mirrors the Desktop Client rule and applies equally to `server/core/server.py`, all mixins, and all utility modules.

### Desktop Client Architecture
- **`client/ui/main_window.py`** — Core UI (2,500+ lines), handles all in-game interaction
- **`client/network_manager.py`** — WebSocket client, receives packets, dispatches to UI
- **`client/sound_manager.py`** — Audio playback
- **`client/config_manager.py`** — User preferences persistence; passwords stored in system keyring (never in JSON)
- **`client/localization.py`** — Fluent runtime localization
- **`client/ssl_utils.py`** — Centralized SSL context factory; CA-strict for production (`wss://`), relaxed for localhost

#### Desktop Client Rules
- **Credentials**: Passwords live exclusively in the OS keyring via `keyring` library. Never write passwords to JSON.
- **Config file**: All client configuration lives in a single `identities.json` (`%APPDATA%/ddt.one/PlayAural/`). It stores server/account data **and** client options under the top-level `"client_options"` key. Never split config into multiple files.
- **Auto-login failure**: `on_login_failed` in `main_window.py` disables the `auto_login` flag (via `config_manager.update_account`) for permanent credential errors (`wrong_password`, `user_not_found`). Transient errors (`rate_limit`) leave the flag intact. The `client.py` main loop skips auto-login when `came_from_failure` is True, ensuring the user always sees the error dialog after a failed auto-login.
- **SSL**: Always use `make_ssl_context(server_url)` from `ssl_utils.py`. Do not construct `ssl.SSLContext` objects inline.
- **Imports**: All imports at module level. No in-function imports except inside `main()` where CWD must be set first.
- **Dialogs**: Always call `dlg.ShowModal()` and capture the result before calling `dlg.Destroy()`. Never skip `ShowModal()`.
- **PyInstaller**: `client/pyproject.toml` is the source of truth for dependencies (not `requirements.txt`). When adding a dependency that uses dynamic imports (e.g. keyring), add `collect_all('pkg')` plus explicit `hiddenimports` to `PlayAural.spec`.
- **`network.connect()` version parameter**: Always pass `client_version=VERSION` to every `network.connect()` call, including all reconnect paths (`_attempt_silent_reconnect`, `_do_reconnect`). Omitting it defaults to `"0.0.0"`, causing the server to skip `_restore_user_state` and silently drop all menu selections after reconnect (chat still works, making the bug hard to diagnose).

### Web Client Architecture
- **`web_client/game.js`** — Single-file game logic (~3,000 lines), connects to same WebSocket server
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
