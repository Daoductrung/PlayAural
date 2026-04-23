# CLAUDE.md

This file provides guidance to Claude Code and other AI assistants working in this repository.

## Project Overview

PlayAural is an audio-first multiplayer online gaming platform with four first-party components:
- **`server/`** — Python async WebSocket server with game logic, auth, tables, persistence, localization, and ratings
- **`client/`** — Python wxPython desktop client with screen reader-oriented keyboard UX
- **`web_client/`** — Vanilla JS PWA web client with ARIA support and browser-based audio/TTS
- **`mobile_client/`** — Expo / React Native / TypeScript mobile client with self-voicing gesture navigation

PlayAural also supports table-scoped real-time voice chat. The game server authorizes access and tracks voice membership, while a separate LiveKit-based media service carries the actual audio stream.

The project is open source under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE).

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

### Web Client
Serve `web_client/` from any HTTP server. For local development:
```bash
python -m http.server 8080 --directory web_client
```

### Mobile Client
```bash
cd mobile_client
cmd /c npm install
cmd /c npm run generate:sounds
cmd /c npm run typecheck
npx expo start
```

### Production Build (Windows Desktop Client)
```bat
build_prod.bat
```

## Architecture

### Network Protocol
All communication is WebSocket JSON packets:
```python
Packet(type: str, data: dict)  # PacketType enum defines the protocol
```

Important server-driven packets include:
- `authorize_success`
- `login_failed`
- `menu`
- `update_menu`
- `request_input`
- `speak`
- `play_sound`
- `play_music`
- `play_ambience`
- `stop_music`
- `stop_ambience`
- `chat`
- `disconnect`
- `table_context`
- `voice_join_info`
- `voice_join_error`
- `voice_leave_ack`
- `voice_context_closed`

**`silent` flag on `chat` packets**: Adding `"silent": True` suppresses both chat notification sounds and TTS in the first-party clients. Use it only when the server is also sending explicit `speak` and/or `play_sound` packets to control the audio output precisely.

### Server Architecture
- **`server/core/server.py`** — Main orchestrator, auth routing, menus, reconnect, moderation, MOTD, presence
- **`server/network/websocket_server.py`** — Async WebSocket transport
- **`server/games/`** — 34 registered game implementations
- **`server/game_utils/`** — shared game mixins and helpers
- **`server/tables/`** — table lifecycle, save/restore, membership
- **`server/auth/`** — authentication, CAPTCHA checks, password reset, rate limiting
- **`server/persistence/database.py`** — SQLite storage for users, leaderboards, ratings, friends, MOTD, and related state
- **`server/messages/`** — runtime localization engine
- **`server/locales/`** — Fluent locale files
- **`server/voice/`** — voice authorization, token generation, and provider integration

### Voice Chat Architecture
- Voice chat is scoped to a server-defined context, currently game tables.
- The PlayAural game server remains the authority for whether a user may join a voice context.
- The media path is separate from gameplay networking. Gameplay continues over the normal WebSocket connection; live audio flows through the dedicated LiveKit service.
- The server issues short-lived join packets, binds voice access to the caller's current table context, and closes that voice context when table membership ends.
- Voice presence is runtime-only state. It is tied to the active table lifecycle and must not create long-lived database rows unless a future feature defines retention and cleanup rules explicitly.

### Game Implementation Pattern
Games use a mixin-based architecture. Each game class inherits from `Game`, which brings the standard shared mixins plus `SequenceRunnerMixin`.

Key built-in mixins include:
- `GameSoundMixin`
- `GameCommunicationMixin`
- `GameResultMixin`
- `GameScoresMixin`
- `GamePredictionMixin`
- `TurnManagementMixin`
- `MenuManagementMixin`
- `ActionVisibilityMixin`
- `LobbyActionsMixin`
- `EventHandlingMixin`
- `ActionSetCreationMixin`
- `ActionExecutionMixin`
- `OptionsHandlerMixin`
- `ActionSetSystemMixin`

Games are dataclasses serialized via Mashumaro for save/restore. All important game state must live in dataclass fields.

#### SequenceRunnerMixin for Cinematic Gameplay Flows
`Game` includes `SequenceRunnerMixin`. It is the standard way to build delayed, multi-step gameplay/audio flows that must survive save/load and avoid deadlocks.

Use it for:
- movement animations across ticks
- delayed reveals, captures, eliminations, and roulette-style sequences
- cinematic audio flows
- any legacy `event_queue`-style sequence that is really a timed beat/callback flow

Core primitives:
- `SequenceOperation.sound_op(path, ...)`
- `SequenceOperation.localized_sound_op({"en": "...", "vi": "..."}, ...)`
- `SequenceOperation.callback_op("callback_id", payload={...})`
- `SequenceBeat(ops=[...], delay_after_ticks=N)`
- `SequenceBeat.pause(N)`

Standard rule:
- use `SEQUENCE_LOCK_GAMEPLAY` by default
- keep info/status actions available unless a full lock is truly necessary
- call `self.process_sequences()` in `on_tick()`
- if bots should wait, pass `pause_bots=True` and gate bot ticking with `if not self.is_sequence_bot_paused(): ...`

#### Grid Mixins and Cursor Serialization
For any game using `GridGameMixin`, serialized grid fields must use Mashumaro-safe canonical types:
- `grid_cursors: dict[str, GridCursor]`
- `grid_row_labels: list[str]`
- `grid_col_labels: list[str]`

Do not replace mixin-owned serialized types with loose tuples or ad-hoc dicts.

#### Touch Client Capability Checks
Use:
- `server/game_utils/client_types.py`
- `is_touch_client(user)`
- `is_touch_client_type(client_type)`
- `uses_self_voicing_settings(user)`

Game logic uses shared touch-client helpers instead of raw `client_type` string checks. Touch-aware action visibility covers:
- `web`
- `mobile`

The menu infrastructure keeps static web-only controls such as the web actions overlay behind explicit web-only guards. Mobile clients do not receive those controls automatically.

#### Web / Mobile UI Consideration (Mandatory)
When implementing a new game, always consider touch clients alongside desktop users.

Rules:
- Time-critical reaction actions must be visible as turn-menu buttons for touch clients during their active windows.
- Utility actions that desktop users access by keybind should also be exposed in the turn menu for touch clients where appropriate.
- Turn menu ordering matters for screen readers and self-voicing clients:
  1. reaction buttons
  2. primary play actions
  3. multi-select confirmation actions
  4. utilities such as draw, pass, sort
- Standard action ordering for touch clients should remain consistent:
  1. game-specific info actions
  2. `check_scores`
  3. `whose_turn`
  4. `whos_at_table`

Use `self._order_touch_standard_actions(action_set, target_order)` for touch standard-action ordering in `create_standard_action_set` and any dynamic `_sync_standard_actions` path. The target list contains the game-specific info actions followed by `check_scores`, `whose_turn`, and `whos_at_table`; the helper preserves other actions above that group and appends only actions that exist. Do not duplicate manual `new_order` or `final_order` loops for this standard-action pattern, and keep desktop ordering separate from touch-only ordering.

#### Spectator Action Visibility (`include_spectators`)
Every `Action` has `include_spectators: bool = False` by default.

Rules:
- `include_spectators=True` only for public information or lobby controls that spectators are meant to use
- `include_spectators=False` for player-private or gameplay-mutating actions
- the `Action` and its matching `Keybind` must agree on spectator visibility

#### Action Set Ordering and Menu Deduplication
`get_all_enabled_actions()` combines action sets in this order:
**turn → lobby → options → standard**

Rules:
- Info/status actions belong in `create_standard_action_set`, not `create_turn_action_set`
- Turn-menu actions that should not appear in the Escape/actions list must use `show_in_actions_menu=False`

#### Turn Management Rules
- `set_turn_players(players)` resets `turn_index` to `0`
- `advance_turn()` immediately after `set_turn_players(...)` skips the first player and is almost always wrong
- use `get_active_players()` for gameplay logic, results, and winner calculations

#### Server-Side Navigation Stack
Server menus use the breadcrumb stack in `_user_states[username]["_stack"]`.

Core primitives:
- `_nav_push(user, show_fn, *args)` — forward navigation
- `_nav_back(user)` — go back
- `_nav_refresh(user, show_fn, *args)` — redraw same level without losing history
- `_restore_frame(user, frame, stack)` — centralized state restore

Do not call `_show_*()` directly from action handlers. Use `_nav_refresh(...)` so stack history survives.

#### Editbox Input States
Use `_enter_input_state(user, input_id, **extra)` / `server.enter_input_state(...)` instead of mutating `_user_states` directly. This protects the nav stack and modal focus rules.

#### Reconnect and Ghost Cleanup
`_restore_user_state` handles reconnect and cleans up stale lobby membership, spectators, and inconsistent table mappings. Reconnect restoration should always route through the centralized restore flow, not custom menu-specific chains.

#### Server Alert Broadcast
The `/reboot` and `/stop` shutdown countdown is a structured 32-second sequence with:
- deduplicated task guard
- warning/tick/shutdown sounds
- silent chat packets plus explicit `speak` packets
- reconnect-aware disconnect packets

#### TTS Buffer Categorization
Every `user.speak_l()` and `broadcast_l()` call must include an explicit `buffer=`:
- `game` — gameplay events
- `system` — settings, connection, moderation, errors, room/system events
- `chat` — chat only
- `misc` — minor non-chat, non-game informational output

#### Administration Privilege Tiers
`user.trust_level` tiers:
- `1` — user
- `2` — admin
- `3` — dev

Dev-only SMTP configuration is enforced at the menu, routing, and handler levels.

#### Persistence and Data Lifecycle
Any new persistent feature must define:
- what is stored
- how long it lives
- how stale data is cleaned up
- what happens on account deletion
- tests for cleanup behavior

### Desktop Client Architecture
- **`client/ui/main_window.py`** — primary desktop UI and gameplay interaction
- **`client/network_manager.py`** — WebSocket client and packet dispatch
- **`client/sound_manager.py`** — sound, music, ambience playback
- **`client/voice_manager.py`** — LiveKit voice lifecycle, microphone publishing, and disconnect cleanup
- **`client/config_manager.py`** — identities, client options, keyring-backed credentials
- **`client/localization.py`** — Fluent runtime localization
- **`client/ssl_utils.py`** — SSL context factory

Desktop rules:
- passwords live only in OS keyring
- client config lives in `identities.json`
- auto-login disables itself on permanent credential failures
- always pass `client_version=VERSION` on every `network.connect()` path
- the desktop voice client runs on its own asyncio loop and must await disconnect/cleanup paths fully
- the saved audio input device is desktop-only state; if a saved microphone is missing on the current machine, the client must fall back to the system default input device

### Web Client Architecture
- **`web_client/game.js`** — main web client runtime
- **`web_client/locales.js`** — client-side i18n strings
- PWA/service-worker support

Web rules:
- never use `innerHTML` with server-controlled content
- remember-me password storage is opt-in and controlled by `pa_remember`
- TTS and reconnect cleanup must be complete on disconnect
- current client version is tracked in `web_client/game.js`
- table voice chat lives in the Chat area and must keep browser permission handling, ARIA announcements, and voice cleanup in sync with table lifecycle packets

### Mobile Client Architecture
- **`mobile_client/src/app/PlayAuralApp.tsx`** — main app shell, auth flow, overlays, focus state
- **`mobile_client/src/network/PlayAuralConnection.ts`** — WebSocket connection and packet handling
- **`mobile_client/src/audio/MobileAudioManager.ts`** — sound, music, ambience, fade, and crossfade handling
- **`mobile_client/src/tts/TtsManager.ts`** — self-voicing speech manager
- **`mobile_client/src/state/BufferStore.ts`** — message buffers/history
- **`mobile_client/src/gestures/useSelfVoicingGestures.ts`** — gesture recognizer for self-voicing mode
- **`mobile_client/locales/en/client.json`** / **`mobile_client/locales/vi/client.json`** — mobile UI strings
- **`mobile_client/sounds/`** — bundled sound pack copied directly from the desktop layout

Mobile rules:
- the client connects as `client: "mobile"`
- it is treated as a touch client, not as `web`
- it is currently CAPTCHA-exempt like the desktop client
- local config/preferences are persisted with AsyncStorage
- credentials are stored in SecureStore
- saved credentials support auto-login with graceful fallback to manual login
- version and sound-pack mismatches trigger a mandatory APK update prompt
- the production default server URL is `wss://playaural.ddt.one:443`
- mobile speech preferences use `mobile_tts_engine`, `mobile_tts_voice`, and `mobile_tts_rate`
- web speech preferences use `speech_mode`, `speech_voice`, and `speech_rate`
- browser web-runtime tests expose browser/Web Speech voices, while Android builds expose device TTS voices through Expo Speech
- unavailable synced mobile voices or engines must fall back to the system default without throwing

### Game Counts and Catalog
The server currently registers **34 games**:
- card games, dice games, board/adventure games, and social games
- recent additions include `Bunko`, `Tien Len`, `Color Game`, and `Citadels`

### Key Tech Stack
- Python 3.11, `asyncio`, `websockets>=12.0`, `mashumaro`, `fluent-compiler`, `openskill`, `argon2-cffi`
- Desktop: `wxPython`, `accessible-output2`, `sound-lib`, `keyring`, `livekit`, `sounddevice`
- Mobile: `expo`, `react-native`, `expo-audio`, `expo-speech`, `@react-native-async-storage/async-storage`, `expo-secure-store`
- Package manager: `uv` for Python components, `npm` for the mobile client
- Languages: English and Vietnamese
