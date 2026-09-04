# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PlayAural is an audio-first multiplayer online gaming platform with four first-party components:
- **`server/`** — Python async WebSocket server with game logic, auth, tables, persistence, localization, and ratings
- **`client/`** — Python wxPython desktop client with screen reader-oriented keyboard UX
- **`web_client/`** — Modular vanilla JS PWA with ARIA live output, desktop-style keyboard navigation, touch menus, browser audio/Web Speech, capped history buffers, and table voice chat
- **`mobile_client/`** — Expo / React Native / TypeScript mobile client with self-voicing gesture navigation

PlayAural also supports table-scoped real-time voice chat. The game server authorizes access and tracks voice membership, while a separate LiveKit-based media service carries the actual audio stream.

The project is open source under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE).

## Commands

### Server
```bash
# Run server (default port 8000)
cd server && python -m server
python -m server --host 0.0.0.0 --port 9000 --ssl-cert cert.pem --ssl-key key.pem

# Run tests. pytest and the asyncio/xdist plugins live in the server project's
# `dev` extra, so go through uv with `--extra dev` — bare `python` is the global
# interpreter and has none of the project deps. `--project server` selects the
# server venv; the command runs in the current directory, so invoke it from the
# repo root.
uv run --project server --extra dev python -m pytest server/tests -q
# Single test / file
uv run --project server --extra dev python -m pytest server/tests/test_file.py::test_function
```

During iteration, run only the tests covering the files you touched and their
dependents. The suite is ~1650 tests and takes about 25 seconds serially (add
`-n auto` for the `pytest-xdist` parallel path) on a modern machine; running it
whole as an inner-loop step is still a waste. Run the full suite before
committing anything that crosses subsystems, and before landing a feature — not
after every edit.

The suite no longer depends on the working directory — every test now pins the
Fluent locales dir `__file__`-relative — but run from the repo root anyway so
the `uv run --project server` command resolves naturally.

The suite is parallel-safe under `pytest-xdist` (in the `dev` extra; `-n auto`
or `-n 6`). An autouse `_isolate_localization` fixture in
`server/tests/conftest.py` snapshots and restores the class-level `Localization`
state around every test, so a test that repoints or wipes the global Fluent
bundle cache (e.g. the MOTD fixture) can no longer leak to siblings on the same
worker. Keep new tests RNG-deterministic — disable random-outcome options
(e.g. pusoydos `instant_wins=False`) when asserting on exact game state, since
parallel runs surface latent RNG flakiness fast.

### Desktop Client
```bash
python client/client.py
```

### Web Client
Serve `web_client/` from any HTTP server. For local development:
```bash
python -m http.server 8080 --directory web_client
node web_client/scripts/generate-sound-manifest.mjs
```

### Mobile Client
```bash
cd mobile_client
cmd /c npm install
cmd /c npm run generate:sounds
cmd /c npm run generate:locales
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
- `remove_editbox`
- `speak`
- `audio`
- `chat`
- `disconnect`
- `table_context`
- `voice_join_info`
- `voice_join_error`
- `voice_leave_ack`
- `voice_context_closed`

**`silent` flag on `chat` packets**: Adding `"silent": True` suppresses both chat notification sounds and TTS in the first-party clients. Use it only when the server is also sending explicit `speak` and/or `audio` packets to control the output precisely.

### Social Blocking Boundary

User blocks are directional persistent records retained until explicit
unblocking or either account is deleted. A block in either direction creates a
mutual direct-contact boundary: neither account may send the other friend
requests, private messages, or table invites; ordinary local/global text chat
and presence notifications are filtered in both directions. Applying a block
atomically removes any accepted friendship, pending requests in either
direction, and queued relationship notifications between the pair. Unblocking
does not recreate any of that deleted state. A blocked pair cannot newly enter
tables hosted by one another or be brought together by manually restoring a
saved table. Shared membership, reserved-seat recovery, planned-reboot
restoration, later host transfer, and table voice chat remain unchanged; the
confirmation UI must explain this distinction. Suppress optional global
notifications attributable to blocked accounts, such as table creation.
Enforce the boundary in database and shared server handlers; hidden buttons
alone are never a security or privacy control. Manual saved-table restoration
is an owner-scoped, all-or-nothing new admission: validate the complete
serialized game and member roster before exposing a table, retain the save on
every failure, treat bot-held human seats as their original human accounts,
and identify only the restorer's own blocks when giving unblock instructions.

### Audio Control Protocol

Server-controlled SFX, music, and ambience use the single versioned `audio`
packet. Do not add per-feature packet types or client-specific audio branches.
The server validates relative asset paths, ids, numeric ranges, commands,
kinds, and scopes through `server/audio.py`; clients validate again before
loading an asset.

- Commands are `play`, `stop`, `pause`, `resume`, `set_bus`, and `stop_all`.
- Kinds are `sfx`, `music`, and `ambience`. A named bus may be added without
  changing the protocol and inherits its kind's user-volume preference.
- Randomized numbered one-shot SFX use the validated `family` field. Desktop
  discovers family members from the installed pack, while Web and Mobile use
  generated sound manifests. A family named `notify` resolves dynamically to
  positive-integer assets such as `notify1.ogg`; never hardcode the count, and
  never use a family for loops, music, or ambience.
- Stable handles own lifecycle. Looping SFX must keep the returned/provided
  handle and stop it explicitly. Stop/pause/resume are idempotent.
- Music and ambience replacement use simultaneous fade-out/fade-in. Pausing
  music preserves position. Abrupt music stops are reserved for strict
  lifecycle boundaries where audio must not survive into the next context.
- Ambience is keyed by `scope + context + layer`: `global`, `player`, or
  `context` scopes may coexist, and changing one layer must not stop another.
- Ambience assets may be a simple loop or a segmented stem with optional intro
  and outro. When `seamless` is enabled, intro-to-loop and loop-to-outro are
  contiguous same-stem boundaries: never fade or crossfade those transitions.
  External fades still apply to starting, replacing, pausing, or force-stopping
  independent sources. Normal stop uses an immediate no-fade splice from the
  active loop into its outro, matching legacy teardown behavior and preventing
  a long loop from surviving into another UI context. `outro_mode="boundary"`
  is an explicit opt-in for content whose caller can wait until the current
  loop iteration reaches its authored seam. Waiting lobbies never own
  background music, whether initially created or entered after completion or a
  manual reset. Game completion and reset use `stop_replayable_audio` to retire
  music, ambience, and persistent looping SFX without interrupting untracked
  one-shot result cues; ambience may finish through its authored outro.
  Table-to-main-menu teardown uses `stop_all` with `play_outros=True`, while
  hard resets/transfers may suppress outros to avoid overlap with the next table
  context. Reconnect replay starts at the loop and does not replay an intro that
  the table already heard.
- `priority` and `max_instances` bound SFX pressure. `ducking` temporarily
  lowers named buses for the life of its source and restores them on every
  completion/stop/error path. User volume remains the master gain.
- Ducking is implemented but dormant and strictly opt-in. First-party gameplay
  must not send non-empty `ducking` maps until a future feature explicitly
  adopts and tunes it. Empty/default ducking must have no audible side effects.
- Android playback must preserve the system-selected wired, Bluetooth, or
  speaker route; game-audio setup must never force speakerphone routing. ExpoAV
  is the single audio-focus coordinator. The modern `expo-audio` playlist path
  mixes without requesting a competing focus lease, and its guarded native
  routing patch is applied by the mobile `postinstall` script. Keep the patch
  and its fail-closed regression test until upstream provides the same behavior.
  Android autolinking must build `expo-audio` from that guarded local source;
  the default precompiled artifact does not contain the fix.
- Mobile LiveKit voice is media audio, not a phone-call audio session. Android
  must pin `MODE_NORMAL`, `STREAM_MUSIC`, and `USAGE_MEDIA`, leave device
  selection to the system, disable forced AudioSwitch routing, and avoid a
  second LiveKit focus lease even while the microphone is published. iOS must
  disable LiveKit's automatic getUserMedia category override: listen-only uses
  `playback` with `default` mode, and explicit microphone publishing uses the
  required `playAndRecord` category with `default` mode—never `voiceChat` or
  `videoChat`. Preserve stereo Bluetooth A2DP output and exclude the HFP
  hands-free route, which takes priority and collapses output to mono. Keep the
  guarded LiveKit native iOS patch, postinstall hook, and fail-closed dependency
  regression tests.
- Async clients must generation-guard asset loads and fades so a late load or
  retiring source cannot resurrect, silence, or replace a newer command.
- Replayable music, ambience, and explicitly persistent SFX loops live in the
  game's Mashumaro-safe `active_audio` state, including recipient ids and
  paused state. One-shots and client mixer state are runtime-only. Old
  `current_music`/`current_ambience` fields are read-migration bridges for
  pre-protocol saves and must not become a second playback authority.
- `active_audio` has the same lifespan and retention as its containing
  table/game save. Explicit stop, phase reset, table transfer, and game
  replacement remove stale entries; deleting the containing save/table or
  account-owned data deletes it as part of that existing lifecycle. Schema
  migration reads the legacy current-track fields only when unified state is
  absent.
- Gameplay WebSockets carry control JSON only. Voice media remains on LiveKit.

### Server Architecture
- **`server/core/server.py`** — Main orchestrator, auth routing, menus, reconnect, moderation, MOTD, presence
- **`server/network/websocket_server.py`** — Async WebSocket transport
- **`server/games/`** — 45 registered game implementations
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
- Server-owned automation reuses `voice_join_info` with
  `server_requested=true`. First-party clients may connect automatically but
  always enter listen-only; microphone publishing remains a separate explicit
  user action. `voice_context_closed` cancels both pending and active joins.
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

The canonical shared player and action-context types live in `server/game_utils/player.py` and `server/game_utils/action_context.py`. Game modules can use the re-exports from `server/games/base.py`, but they must not create duplicate base `Player` or ad-hoc action context classes.

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
- `SequenceBeat.after_audio(duration_ticks, wait_ratio=..., ops=[...])` for
  dynamic delays before the following beat that remain correct when an asset
  is replaced; add a following beat when the sequence must remain active

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

#### Keybind State Scoping
`setup_keybinds()` must call `super().setup_keybinds()` first. Gameplay
keybinds use `KeybindState.ACTIVE`, lobby-only actions use `IDLE`, and truly
global actions use `ALWAYS`.

Keybind dispatch is state-scoped: `IDLE` bindings are available only while
`game.status != "playing"`, `ACTIVE` bindings are available only while
`game.status == "playing"`, and `ALWAYS` bindings are available in both states.
Because state is part of the binding scope, the same physical key may be reused
across non-overlapping states. For example, the base `b` Add bot binding is
`IDLE`, so a game may safely bind `b` to an `ACTIVE` gameplay action without
conflicting, as UNO does. Likewise, `enter` can start the game while idle and
select a grid cell while active.

Base/client bindings to respect include `enter`, `escape`, `b`, `shift+b`,
`f3`, `t`, `s`, `shift+s`, `ctrl+m`, `ctrl+q`, `ctrl+u`, `ctrl+s`, `ctrl+r`,
`ctrl+i`, and `ctrl+f1`. Do not reuse `ALWAYS` bindings or same-state
base/client bindings for unrelated game-specific actions unless the behavior is
deliberately shared or overridden. When reusing a key across states, keep the
scope explicit, keep matching `Action`/`Keybind` spectator visibility aligned,
and add tests or clear coverage for the intended state separation.

#### Turn Management Rules
- `set_turn_players(players)` resets `turn_index` to `0`
- `advance_turn()` immediately after `set_turn_players(...)` skips the first player and is almost always wrong
- use `get_active_players()` for gameplay logic, results, and winner calculations

#### Menu Refresh and Focus (Mandatory)
Game code never paints turn menus directly. It records turn-menu intent through
exactly two calls on `MenuManagementMixin`:

- `refresh_menus(player=None)` — mark one player (or everyone) as needing a
  repaint. Recording only; nothing is built or sent here. Over-marking costs
  one set-insert and no packet, so the safe habit — refresh after any state
  change — is also the cheap habit.
- `request_menu_focus(player, action_id)` — queue a one-shot focus jump for
  a player (and mark them for repaint). One slot per player, last writer
  wins, consumed by the next flush that paints that player — so a delayed
  sequence-runner repaint can never double-jump the cursor, and other
  players' repaints never carry the actor's focus.

These per-player entry points are the supported mechanism for strictly
isolated, per-client menu replacement. Use them, or the framework-owned
per-player action-input/status overlays, when an action should change only the
actor's UI: for example, replacing Player A's card list with a "choose suit"
menu while Player B's menu receives no packet at all. This isolation is a
powerful accessibility tool for touch and screen-reader users because it avoids
unrelated focus churn on other clients.

It is not an absolute, always-on rule. Before modifying an existing game or
creating a new one, first understand the full gameplay flow and audience for
the state change. Deliberately classify each menu update:
- private/individual transition: repaint or focus only the affected player;
- public table-state change: refresh every affected player, and use a
  table-wide `refresh_menus()` only when other players' visible choices,
  information, or turn affordances genuinely changed.

Do not blindly convert table-wide refreshes to player-only refreshes, and do
not blindly mark everyone dirty for actor-only choice menus. The correct scope
is part of the game rule/UX design.

One sealed flush point builds and sends: `flush_menus()`, called by the
framework only — at the end of every `Game.handle_event()` and once per
server tick (after game ticks, before the packet flush). Games never call
it; tests call it explicitly at the same boundaries the framework provides
in production (after a direct `execute_action`/`_action_*` call or an
`on_start`/`on_tick` loop, before asserting on menus).

The flush orchestrators — `refresh_menus`, `flush_menus`,
`_paint_player_menu`, `_is_menu_refresh_blocked` — are **sealed**: a game
class that overrides one fails at import time with a `TypeError` (so the
server will not start and pytest will not collect). The flush owns the
focus-steal guards (status boxes, global system menus, pending inputs),
in-place actions-menu refresh, bot skipping, finished-state end screens, and
focus delivery; per-game copies of that logic were the root cause of a long
line of focus-stealing bugs.

Games customize what gets painted through the hooks:
- `before_menu_build(player)` — sync dynamic action sets (per-card play
  actions, standard-action ordering) before any menu paint. Called for bots
  too, so action sets stay valid for bot decisions. Must be idempotent.
  Note that mid-event the action sets are stale (the flush hasn't run yet);
  game code that reads its own action sets right after mutating state should
  call its own `before_menu_build(player)` first (see citadels'
  `_refresh_menus_for_focus`).
- `build_menu_items(player, user) -> MenuBuild` — supply a custom item list
  and grid layout (`MenuBuild(items=..., grid_kwargs=...)`); this is how the
  backgammon and senet boards arrange their grids.

Status overlays are the sanctioned exception: use `status_box(...)` or
`live_status_box(...)` as described below. Games still must not call
`user.show_menu()` / `user.update_menu()` directly.

#### How Clients Treat Menu Packets (Why Plain Refreshes Are Safe)
All three first-party clients treat a menu packet for the menu they are
already displaying as an in-place diff: the cursor follows the focused item
by *identity*, with no announcement and no reset. Focus resets come from
menu-identity changes (turn_menu -> status_box -> turn_menu), from an explicit
`selection_id`, or from a same-menu update where no stable old item survives -
never from a repaint itself. (The old `rebuild_*`-resets /
`update_*`-preserves doctrine was stale; the verb never mattered on any client,
which is why the names are gone.)

Consequences that still matter when designing a menu:
- When the focused item's id leaves the menu, clients fall forward to the next
  surviving item from the old logical order, then backward to the previous
  surviving item, and only then to a clamped numeric fallback. A persistent
  control must stay *present* across refreshes to keep its exact anchor.
- This bit the backgammon board hard. The 24 grid points are a persistent
  grid, but `get_visible_actions` once dropped *disabled* actions — and a
  point disables on the opponent's turn. The off-turn player's board
  collapsed to zero items mid-opponent-turn, destroying the focus anchor
  ("focus teleports to square 13"). The fix was keeping
  disabled-but-visible actions in `get_visible_actions`.
- Where the action list legitimately changes shape and a fixed landing spot
  is preferable, jump focus deliberately with `request_menu_focus` at the
  start of the user's turn — choose one, don't leave focus to chance.
- `NetworkUser` content-diffs repaints: an identical same-menu repaint with
  no focus directive sends no packet at all, and the per-flush coalescer
  collapses same-tick duplicates. Bandwidth is not a reason to avoid
  `refresh_menus()`.
- Open `MenuInput` selectors repaint in place from their current options,
  labels, and descriptions when their player is marked dirty; keep option ids
  semantic and stable so this live update preserves focus. Pending
  `EditboxInput` prompts never repaint passively because that would destroy
  typed text. When choosing from a selector must freeze public mutation, set
  `MenuInput(locks_gameplay=True)` and consult `_gameplay_input_lock_owner()`
  from the game's actor/permission checks; do not couple the lock to an action
  id. Information actions may remain available when the game permits them.
- A specialized `MenuInput` surface overrides the idempotent
  `_build_action_menu_input_items(action, player, user, options)` hook instead
  of painting a menu directly. Put announcements and opening sounds in
  `_on_action_menu_input_opened(action, player)`; the builder may run on every
  dirty flush or stale-packet recovery and must be silent. Treat
  `_on_action_input_cancelled(player, action_id)` as cleanup-only: it also runs
  when authoritative state invalidates the input and when a human seat is
  removed or replaced, preventing game-owned draft state from leaking past the
  UI lifecycle.
- The Escape/actions menu is refreshed in place by the sealed flush while it
  is open. Do not block state changes just because a player is reading that
  menu, and do not manually rebuild it from a game.
- Framework-owned exits restore focus to the opener when possible:
  actions-menu Back, actions selected from the actions menu, action-input
  Cancel/submit, leave-confirmation No, status-box close, and server menus
  that close after a selection all use the recorded action context. Games
  should pass stable action ids and avoid ad-hoc focus jumps for these
  standard exits.

#### Static vs. Live Status Boxes
Use the right status-box helper for the job:

- `status_box(player, lines)` is for static snapshots: rules/help text,
  one-shot action results, limited-use private reveals, and information that
  should not change while the player is reading it.
- `live_status_box(player, box_id, builder, focus_id=None)` is for dynamic
  state views that should stay current while open: boards, scoreboards,
  standings, city/hand summaries, battle rosters, clocks, and similar
  gameplay status panels.

Live status boxes are still game overlays using the `status_box` menu id, so
all clients apply the normal same-menu content diff. They repaint only through
the sealed flush path when `refresh_menus()` records a dirty player/all-player
update; identical content is skipped by `NetworkUser`, and passive refreshes
must not pass `selection_id` or `position`. Use `focus_id` only for the initial
direct user action that opens the box.

Global or in-game overlay navigation requested while a status box is open is
deferred by the server and replayed after the status box closes. Active inputs
(`_transient` server editboxes and game `_pending_actions`) still block forward
navigation without queuing it, because completing or cancelling an input can
change the user's intent. In-game overlays such as Host Management must enter
through `_nav_push` or another modal-aware server helper, never by calling a
show function directly from a game action.

Builder rules:
- A live builder receives `(player, user)` and returns `list[str | MenuItem]`
  or `StatusBoxBuild`.
- Prefer `MenuItem` rows with stable semantic ids (`player:<id>`,
  `token:<id>`, `square:<n>`, `score:<team>`) whenever rows can reorder,
  appear, or disappear. String rows get stable fallback ids by line index,
  which is only appropriate for fixed-layout panels.
- Never directly call `user.show_menu()` from games to refresh a status box.
  Update game state, call `refresh_menus()`, and let the framework repaint any
  open live boxes without clobbering turn menus or touch-client focus.

#### Score Management and Units
Shared score display is handled by `GameScoresMixin` and `TeamManager`.

Rules:
- games that use default score actions must keep `TeamManager` synchronized with their authoritative score state
- games with non-point score units must set `score_unit_key` to a localized `game-score-unit-*` key
- score unit keys live in both `server/locales/en/games.ftl` and `server/locales/vi/games.ftl`, unless an existing shared unit key already matches the game
- score unit strings should use Fluent plural/select rules and receive the formatter's `count` value
- games whose target score is not stored as `options.target_score` or `options.winning_score` should override `get_score_target()`
- games with custom non-`TeamManager` scoring should override `supports_score_actions()`, `_action_check_scores`, and `_action_check_scores_detailed` as one coherent set
- scoreless games should not claim score support; their score buttons stay hidden and `s` / `shift+s` are silently ignored
- brief score checks speak one TTS message per player/team in the `game` buffer instead of one combined sentence
- detailed score checks use a live status box with one line per player/team unless the game has a stronger custom detail view
- score units are display text only; leaderboards, ratings, personal statistics, and `GameResult.custom_data` continue to store numeric values in their established schema

#### Team Management and Arrangement
Team-based games use `TeamManager` and the shared lobby team arrangement flow.

Rules:
- games with `TeamModeOption` validate `self.options.team_mode` in `prestart_validate()` with `_validate_team_mode(...)`
- team setup should call `_setup_team_manager_for_start(self.options.team_mode, active_players)` so confirmed host arrangements are preserved and direct `on_start()` calls still auto-assign teams
- team games whose turn sequence depends on team seating should pass `_get_team_turn_players(active_players)` to `set_turn_players(...)` so manual swaps keep the same round-robin balance as automatic assignment
- non-`individual` team modes enter host-controlled team arrangement by default before `on_start()`; override `allows_team_arrangement()` only for games whose rules require fixed or automatic teams
- individual games should not implement their own team-selection menus; shared lobby actions handle reading teams, selecting a member, swapping across teams, cancelling, and confirming
- team arrangement remains a lobby-only state; do not set `status = "playing"` until the host confirms teams and the game actually starts
- roster and option changes during arrangement must be blocked, cancelled, or deliberately refreshed through the shared helpers rather than silently changing teams

#### Persistent Start Action
The `start_game` action remains visible for every user throughout the normal
`waiting` lobby, including while team arrangement is active. Only the host can
execute it. During team arrangement the same stable action id is relabeled as
the localized team-confirmation action; the legacy `confirm_team_arrangement`
action remains executable for compatibility but is not shown as a duplicate.

Readiness must never be implemented by hiding Start. The framework-owned
`validate_start()` enforces minimum, maximum, or exact active-player counts and
then combines those errors with the game's `prestart_validate()` hook. Start
attempts announce all localized validation errors. They do not request focus:
the stable `start_game` item remains present and normal same-menu focus
preservation keeps the cursor in place. Games use `prestart_validate()` only
for their specific deal, ruleset, option-conflict, and team-mode checks.

Every start also requires at least one active human-controlled player. Bots may
satisfy a game's numeric player count, but spectators never satisfy the human
requirement. Keep this rule in shared `validate_start()` so every game reports
the same localized blocker before mutation. If start preparation converts any
disconnected lobby seats to replacement bots, validate the resulting roster
again before team arrangement or `on_start()`. A bot-only roster must remain in
the waiting lobby; do not enter gameplay and depend on abandoned-table cleanup
to destroy it afterward.

#### Server-Side Navigation Stack
Server menus use the breadcrumb stack in `_user_states[username]["_stack"]`.

Core primitives:
- `_nav_push(user, show_fn, *args)` — forward navigation
- `_nav_back(user)` — go back
- `_nav_refresh(user, show_fn, *args)` — redraw same level without losing history
- `_restore_frame(user, frame, stack)` — centralized state restore

The stack records the item that opened a child menu and restores focus to that
semantic item id when the child exits with Back or an equivalent cancel flow.
Use the navigation helpers rather than direct `_show_*()` calls so focus
memory works consistently across main menus, options, documentation,
leaderboards, statistics, and in-game overlays.
Server-owned menu selections are validated against the currently displayed
menu before dispatch, so stale client packets and forged item ids are ignored
rather than routed into the wrong handler.

Do not call `_show_*()` directly from action handlers. Use `_nav_refresh(...)` so stack history survives.

#### Editbox Input States
Use `_enter_input_state(user, input_id, **extra)` / `server.enter_input_state(...)` instead of mutating `_user_states` directly. This protects the nav stack and modal focus rules.

#### Reconnect and Ghost Cleanup
`_restore_user_state` handles reconnect and cleans up stale lobby membership, spectators, and inconsistent table mappings. Reconnect restoration should always route through the centralized restore flow, not custom menu-specific chains.

Session ownership is the exact `ClientConnection` held by the current
`NetworkUser`, not merely a matching username or authenticated flag. Serialize
authorization, authenticated packet dispatch, disconnect cleanup, and external
security eviction per canonical username. A retired socket's late packet,
queued send, transport-finally callback, or voice event must be harmless to its
successor. Credential verification and account/password deletion or eviction
must share the same account lock so a checked credential cannot become stale
before session activation.

First-party releases update the server and all clients in lockstep. Installing
an authenticated session requires an exact client/server version match.
Outdated native clients may receive the credential-verified
`authorize_success` update bootstrap required by the deployed mandatory
updater, but that transport must never own a `NetworkUser`, replace a live
session, emit presence, or dispatch gameplay. Reject outdated Web clients
before authentication. Do not retain obsolete packet-field aliases between
first-party builds. This rule does not remove database, account preference,
local config, table, checkpoint, or saved-game migrations: persisted data
survives a release and must still load safely.

Never copy rendered menus or editboxes across sessions. Rebuild UI from
authoritative server/game intent against the replacement client's capabilities,
normalizing device-only navigation frames to a valid shared parent. A live
device handover keeps authoritative timers and sequences running, replays active
audio layers, preserves reconstructable gameplay overlays, does not substitute
bots or add reconnect grace, and does not reset chat/voice rate limits. Retired
`NetworkUser` output queues are inert, and retained reconnect UI state has a
bounded runtime cleanup lifecycle.

#### Server Alert Broadcast
Scheduled server power alerts use:
- deduplicated task guard
- tiered warning/tick/shutdown sounds
- silent chat packets plus explicit `speak` packets
- reconnect-aware disconnect packets for planned reboots

#### Server Power Management
Server reboot and shutdown flows are framework-owned. Use the centralized
server power manager and developer-only Administration menu; do not add
chat-command reboot/shutdown paths or per-game shutdown hooks.

- Planned reboot preserves active tables through transient checkpoints, freezes
  framework-owned mutation during finalization, skips normal disconnect bot
  substitution, and tells clients to auto-reconnect.
- Planned shutdown clears active table checkpoints and must warn players to
  save games they want to keep before the server goes offline.
- Table checkpoints are transient data with explicit kind, creation time,
  expiration, pruning, account-deletion cleanup, and a one-day TTL unless a
  future migration deliberately changes that lifecycle.
- Post-reboot no-show handling belongs in shared table/game framework logic:
  restored tables get a grace window, then missing active players are replaced
  with bots only when at least one human has returned; tables with no returning
  humans eventually close through abandoned-table cleanup.

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

`Game.on_discard()` is the idempotent lifecycle hook for match-scoped caches,
bot observations, and similar memory that must not outlive its game instance.
The framework calls it on both table destruction and game restart; it does not
replace the retention and cleanup rules required for genuinely persistent data.

### Localization
- Use "user" / "người dùng" for account-level entities (presence, profiles,
  friends, blocks, and moderation). Reserve "player" / "người chơi" for
  game-table participants; account lookups must not reuse game-player errors.
- All player-facing strings go through Fluent (`speak_l`, `broadcast_l`,
  `broadcast_personal_l`, and the localized option/pref/sequence helpers). No
  hardcoded English may reach players.
- Pass raw data as kwargs and let Fluent render; do not pre-format strings.
  Use select/plural expressions when output varies by game state.
- PlayAural ships English and Vietnamese, and — unlike upstream PlayPalace,
  where translators own everything but `en` — here the agent authors **both**.
  A new or changed `en` key must land with its `vi` counterpart, kept in
  structural parity: same keys, same `$variables`, matching plural/select arms.
- Agent-authored Vietnamese is provisional: write it and keep parity, but flag
  it for native review rather than treating it as final.
- Prefer writing the `en` strings before the game/feature code — it forces the
  flow to be planned and every announcement to be enumerated up front.
- Locale discovery, language selection, and fallback must remain dynamic. Do
  not hardcode feature branches for specific language codes; add new languages
  through locale files and the appropriate metadata/registry layer. Missing
  translated strings and missing translated documentation must fall back to
  English, never to raw keys or empty manuals.
- Validate server Fluent changes with `server/tools/compare_locales.py`. The
  tool reports missing and obsolete files/keys, plus variable, select/plural
  arm, and attribute mismatches. Obsolete target keys are cleanup work, not
  harmless leftovers.

#### String Localization & Contextual Broadcasting Standard (Mandatory)

Whenever a new game is added or an existing game is modified with
player-facing string changes, the implementation must include a deliberate
audit of every affected string, announcement path, listener perspective, and
reachable state. This is part of the feature work, not optional cleanup.

**Perspective split**
- Every actor-attributable gameplay broadcast must have distinct personal
  first-person and public third-person forms. The actor hears a direct
  "You ..." message; every other listener hears "<PlayerName> ...".
- Use `broadcast_personal_l(...)` when one personal/public pair is sufficient.
  Use an equivalent per-listener localized helper when brief announcements,
  team names, hidden information, locale-dependent values, or other listener
  context requires individual rendering.
- Do not broadcast one third-person message to everyone and make the actor hear
  their own name. Genuinely global events with no actor, such as a round start
  or neutral environmental change, may use one shared form.

**Complete contextual awareness**
- Evaluate affected strings against the full applicable state and audience
  matrix: actor versus observer, individual versus team, success versus
  failure, active versus waiting/resolving state, option and ruleset variants,
  spectators, bots, reconnect/save restoration, and full versus brief
  announcements.
- Include the concrete values that make the event understandable, such as the
  action or object involved, amount gained or lost, resulting total, target,
  remaining requirement, current phase, risk, consequence, or next available
  step. Localize listener-dependent values separately for each recipient.
- Do not reuse a broad string when different branches have materially
  different causes, consequences, private information, or recovery steps.

**Errors, warnings, and action feedback**
- Every disabled-action reason, validation error, warning, confirmation, and
  gameplay notification must identify the attempted action and the specific
  condition that blocked or resulted from it.
- Tell the player what state caused the outcome and, whenever useful, what must
  change or what action is available next. Avoid generic feedback such as
  "Invalid action", "Not allowed", or "You cannot do that" when a precise
  situational explanation can be provided.
- Maintain EN/VI key, variable, plural, and select-arm parity. Add regression
  coverage for actor and observer forms, listener-specific rendering, and the
  important success, failure, edge, and validation branches introduced or
  changed by the work.

### Documentation

When writing or updating documentation, agents must first reference existing
polished project manuals for similar games and match their structure,
formatting, and player-facing style. Documentation is part of the accessible
game experience, not a developer changelog.

- Write for beginners. Use plain, concrete vocabulary, introduce game terms
  before relying on them, and explain what the player does, hears, chooses, and
  wins.
- Cover the practical player manual shape: overview, goal, turn flow, special
  mechanics, scoring or win condition, customizable options with defaults and
  ranges, useful information actions, and game-specific shortcuts where
  relevant.
- Never write manuals like changelogs, patch notes, design notes, or
  implementation summaries. Do not include unnecessary technical development
  details, justifications, or rationale that do not help someone play.
- Keep EN and VI documentation synchronized in structure, meaning, terminology,
  and attribution. Vietnamese manuals should be natural, friendly, and aligned
  with the matching `.ftl` terminology.
- Community translation work must follow `TRANSLATING.md`: preserve variables,
  maintain first-person/third-person key parity, keep documentation
  player-facing, and update language contributor metadata.

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
- **`web_client/game.js`** — version marker and bootstrap entry that imports the modular runtime
- **`web_client/app.js`** — main runtime, auth flow, packet dispatch, menu/input orchestration, speech preferences, and voice-chat coordination
- **`web_client/store.js`** — UI state store for connection state, current menu, capped history buffers, pending input state, and server option data
- **`web_client/network.js`** — WebSocket connection, packet validation, reconnect-safe send handling, and protocol dispatch boundaries
- **`web_client/audio.js`** — browser audio engine for effects, music, ambience, volume/mute state, sound-pack versioning, effect preloading, and stale-effect protection
- **`web_client/generated/soundManifest.js`** — generated asset registry used
  for data-driven numbered sound families
- **`web_client/a11y.js`** — ARIA live announcer with polite/assertive regions and duplicate-announcement guards
- **`web_client/keybinds.js`** — desktop-style keyboard shortcuts, menu navigation, grid movement, buffer controls, and global command routing
- **`web_client/ui/menus.js`** — menu rendering, stable item identity, keyboard/touch selection, grid layout, type navigation, context actions, and iOS-friendly pointer activation
- **`web_client/ui/history.js`** — capped/coalesced history rendering, buffer switching, screen-reader announcements, and mobile history presentation
- **`web_client/locales/manifest.js`**, **`web_client/locales/index.js`**, and locale catalog files — client-side locale metadata, dynamic loading, and UI strings
- **`web_client/sw.js`** — PWA service worker and static shell cache

Web rules:
- never use `innerHTML` with server-controlled content
- remember-me password storage is opt-in and controlled by `pa_remember`
- TTS, Web Speech queues, audio handles, voice chat, pending inputs, and reconnect
  state must be cleaned up on disconnect
- current client version is tracked in `web_client/game.js`
- server `request_input` packets determine single-line versus multiline web
  controls through `multiline`; single-line input submits with Enter, multiline
  follows the desktop Enter behavior and still auto-selects default text
- ARIA live regions belong at the bottom of the reading order, while game focus
  remains bounded to menu/history/chat targets during play
- history buffers are capped and render work is coalesced; do not reintroduce
  unbounded per-message DOM rebuilds
- Web Speech voice selection exposes a Default Voice option and stores browser
  voice values through stable client-generated menu ids
- menu selection sounds, typing sounds, and action sounds should preload when
  possible and must not delay touch menu activation
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
- mobile locale catalogs are loaded through `mobile_client/src/i18n/localeCatalogs.ts`; update `mobile_client/locales/metadata.json` and run `cmd /c npm run generate:locales` when adding a mobile language
- server locale directories must include `metadata.json` for translator credit
  and official/community status. Keep `languages.ftl` for viewer-localized
  language names; metadata complements it and does not replace it.

### Game Counts and Catalog
The server currently registers **45 games**:
- category ids are `cards`, `dice`, `board`, `poker`, `arcade`, and `misc`
- the Play menu exposes a persisted category filter with dynamic per-category game counts
- games usually expose one category through `get_category()`, while `get_categories()` supports future multi-category games
- recent additions include `Metal Pipe`, `Nine`, `Senet`, `Cards Against Humanity`, `21`, `Age of Heroes`, `UNO`, `Exploding Kittens`, `BANG! The Bullet`, and `Monopoly`

### Key Tech Stack
- Python 3.11, `asyncio`, `websockets>=12.0`, `mashumaro`, `fluent-runtime`, `openskill`, `argon2-cffi`
- Desktop: `wxPython`, `accessible-output2`, `sound-lib`, `keyring`, `livekit`, `sounddevice`
- Mobile: `expo`, `react-native`, `expo-audio`, `expo-speech`, `@react-native-async-storage/async-storage`, `expo-secure-store`
- Package manager: `uv` for Python components, `npm` for the mobile client
- Languages: English and Vietnamese are official defaults; partial community translations fall back to English
