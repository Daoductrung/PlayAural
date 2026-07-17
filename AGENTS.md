# AGENTS.md - PlayAural AI Development Guide

Concise mandatory rules for AI agents working on PlayAural. `CLAUDE.md` is the
detailed source of truth; keep this file synchronized with it. If the two ever
conflict, follow `CLAUDE.md` and update `AGENTS.md`.

## Project

PlayAural is an audio-first multiplayer gaming platform for screen reader users.
It is GPL-licensed and has four first-party components:

- `server/`: Python 3.11 asyncio WebSocket server, games, auth, tables,
  persistence, localization, ratings, voice authorization.
- `client/`: Python wxPython desktop client with keyboard/screen-reader UX.
- `web_client/`: modular vanilla JS PWA with ARIA live output, keyboard and
  touch menu navigation, capped history buffers, browser audio/Web Speech, and
  table voice chat.
- `mobile_client/`: Expo/React Native/TypeScript Android-first touch and
  self-voicing client.

All gameplay communication is WebSocket JSON packets. Table voice chat is
server-authorized but media flows through the separate LiveKit service. Never
merge voice media into gameplay WebSocket traffic. Voice membership is
runtime-only table state unless a future feature explicitly defines retention,
cleanup, and account-deletion behavior.

## Commands

Run server tests from the repo root through uv:

```bash
uv run --project server --extra dev python -m pytest server/tests -q
uv run --project server --extra dev python -m pytest server/tests/test_file.py::test_name
```

Run focused tests while iterating. Run the full suite before landing
cross-subsystem changes or features. Tests are parallel-safe with `-n auto`;
keep new tests deterministic and avoid RNG-dependent exact assertions.

Other common commands:

```bash
cd server && python -m server
python client/client.py
python -m http.server 8080 --directory web_client
cd mobile_client && cmd /c npm install && cmd /c npm run generate:sounds && cmd /c npm run generate:locales
cd mobile_client && cmd /c npm run typecheck && npx expo start
```

## Core Architecture

- `server/games/` currently registers 43 games. Categories are `cards`, `dice`,
  `board`, `poker`, `arcade`, and `misc`; user-facing category labels must be
  localized. The Play menu uses dynamic counts, not hardcoded category counts.
- Games are `@dataclass` classes registered with `@register_game`, inherit from
  `Game`, and may add utility mixins such as `GridGameMixin` or
  `TurnTimerMixin`.
- Persistent game state must be dataclass fields serialized safely by
  Mashumaro. Runtime-only state belongs in `__post_init__`.
- Use the canonical `Player` and `ActionContext` types from
  `server/game_utils/` or the `server/games/base.py` re-exports. Do not create
  duplicate base player/context classes.
- Every game implements metadata methods including `get_name`, `get_type`,
  `get_category`, player bounds, and `get_supported_leaderboards`.
- Use `get_active_players()` for gameplay, results, and winner logic. Do not
  iterate `self.players` for active-player decisions unless spectators/bots are
  deliberately included.
- `set_turn_players(players)` resets `turn_index` to 0. Do not call
  `advance_turn()` immediately afterward.
- `on_tick()` must call `super().on_tick()`, process scheduled sounds, process
  sequences, and gate bot logic when sequences pause bots.

## Timed Flows

Use `SequenceRunnerMixin` for delayed gameplay/audio flows that must survive
save/load: movement animations, reveals, captures, roulette, cutscenes, and any
legacy event-queue style flow.

Rules:

- Build explicit `SequenceBeat` lists with `sound_op`, `localized_sound_op`,
  and `callback_op`.
- State changes happen in callbacks, not because a sound played.
- Payloads must be Mashumaro-safe primitives, lists, dicts, or safe dataclasses.
- Prefer `SEQUENCE_LOCK_GAMEPLAY`; keep info/status actions available.
- Use `pause_bots=True` when bots must wait.
- Cancel stale tagged sequences when resetting a phase or round.

## Grid Games

For `GridGameMixin`, serialized fields must use exact safe types:

- `grid_cursors: dict[str, GridCursor]`
- `grid_row_labels: list[str]`
- `grid_col_labels: list[str]`

Do not store raw tuples or ad-hoc cursor dicts in serialized grid state.

## Actions, Menus, and Focus

Action sets resolve in this order: `turn -> lobby -> options -> standard`.

- Turn-menu gameplay actions use `show_in_actions_menu=False`.
- Game-specific info/status actions belong in `create_standard_action_set`, not
  the turn set.
- `Action.include_spectators` and matching keybind `include_spectators` must
  agree.
- Public information may use `include_spectators=True`; private or mutating
  gameplay actions normally must not.

Game code does not paint turn menus directly. It records turn-menu intent with:

- `refresh_menus(player=None)`: mark one player or everyone dirty.
- `request_menu_focus(player, action_id)`: one-shot focus jump for one player.

Per-client isolated rendering is supported and important for individualized
flows: use `refresh_menus(player)`, `request_menu_focus(player, action_id)`, or
framework-owned per-player input/status overlays when only that player should
see a menu replacement. This is a deliberate tool, not an always-on rule.
Before modifying or creating a game, understand the gameplay flow and decide
whether a change is private to the actor or reflects public table state. Use
strict per-player isolation for private/action-specific transitions such as
choosing a suit after a card play; use table-wide refreshes when other players'
visible choices or public information genuinely changed.

Status overlays are the sanctioned exception: use `status_box(...)` for static
snapshots and `live_status_box(...)` for dynamic state panels. Games still must
not call `user.show_menu()` / `user.update_menu()` directly.
Server navigation requested while a status box is open is deferred and replayed
after the box closes; active editbox/action-input states block navigation
without queuing it. In-game overlays such as Host Management must enter through
modal-aware server navigation, not direct show calls from game actions.

`flush_menus()` is sealed and framework-owned. Games must not override or call
menu flush internals except tests calling `flush_menus()` at production
boundaries after direct `execute_action`, `_action_*`, `on_start`, or `on_tick`.
Do not resurrect old `rebuild_*` / `update_*` patterns.

Customize painting through:

- `before_menu_build(player)`: idempotently sync dynamic action sets and order.
- `build_menu_items(player, user) -> MenuBuild`: custom item/grid layout.

Client focus doctrine:

- Same-menu repaint preserves focus by item id; if the focused item leaves the
  menu, clients fall forward to the next surviving item from the old logical
  order, then backward to the previous surviving item, and only then to a
  clamped numeric fallback. `NetworkUser` skips identical same-menu repaints
  with no focus directive.
- Anchors reset only when the menu identity changes, no stable old item
  survives, or `selection_id` explicitly jumps focus.
- Keep disabled-but-visible persistent controls when they anchor touch or screen
  reader focus. Use `request_menu_focus` only for deliberate action-driven jumps.
- The Escape/actions menu auto-refreshes in place through sealed
  `flush_menus()`. Games must not repaint or block it manually.
- Framework-owned exits restore focus to the opener when possible: actions-menu
  Back, actions selected from the actions menu, action-input Cancel/submit,
  leave-confirmation No, status-box close, and server menus that close after a
  selection. Use stable action ids so this works.
- Use `status_box(player, lines)` for static snapshots/help/limited reveals.
  Use `live_status_box(player, box_id, builder, focus_id=None)` for dynamic
  state panels such as boards, standings, clocks, rosters, and detailed scores.
  Live builders return strings or `MenuItem`s, refresh only through the sealed
  flush after `refresh_menus()`, and must use stable semantic item ids whenever
  rows can reorder, appear, or disappear.

## Touch Clients

Use `server/game_utils/client_types.py` helpers (`is_touch_client`,
`is_touch_client_type`, `uses_self_voicing_settings`) instead of raw
`client_type` checks. Touch clients include web and mobile; mobile is not web.

Rules:

- Time-critical reaction actions must be visible in the turn menu during active
  windows for touch clients.
- Utility actions normally reached by desktop keybinds should be touch-visible
  when useful.
- Turn order for touch menus: reactions, primary card/tile/play actions,
  multi-select confirmation, utilities.
- Touch standard-action order: game-specific info, `check_scores` if supported,
  `whose_turn`, `whos_at_table`.
- Use `_order_touch_standard_actions(action_set, target_order)`; do not copy
  manual ordering loops. Keep desktop ordering separate.

## Keybinds

`setup_keybinds()` must call `super().setup_keybinds()` first. Gameplay
keybinds use `KeybindState.ACTIVE`; lobby-only actions use `IDLE`; truly global
actions use `ALWAYS`.

Keybinds are scoped by state. The same physical key may be reused across
non-overlapping states when the actions cannot both be active. For example, the
base `b` Add bot binding is `IDLE`, so a game may safely bind `b` to an
`ACTIVE` gameplay action, as UNO does. Likewise, `enter` can start a lobby game
while idle and select a grid cell while active.

Base/client bindings to respect: `enter`, `escape`, `b`, `shift+b`, `f3`, `t`,
`s`, `shift+s`, `ctrl+m`, `ctrl+q`, `ctrl+u`, `ctrl+s`, `ctrl+r`, `ctrl+i`,
`ctrl+f1`. Do not reuse `ALWAYS` bindings or same-state base/client bindings
for unrelated game-specific actions unless deliberately matching the standard
behavior. When reusing a key across states, keep the scope explicit and add
coverage for the intended separation.

## Options

Use declarative `GameOptions` with `option_field()`.

- Every option must have working logic; no dead options.
- Every option needs a localized `change_msg` in EN and VI.
- `MenuOption` needs `choice_labels` for every raw value.
- `TeamModeOption` uses shared team-mode helpers.
- The framework keeps `start_game` visible throughout the waiting lobby.
  `validate_start()` owns player-count checks and combines them with the game's
  `prestart_validate()` errors; never hide Start merely because setup is
  invalid.
- `prestart_validate()` must block impossible deals, unsupported option
  combinations, and team-mode conflicts with clear localized errors.

## Audio and Accessibility

Audio-first is mandatory. Every important state change needs TTS and/or sound.

- Every `speak_l()` and `broadcast_l()` call must pass explicit `buffer=`.
- Buffers: `game` for gameplay, `system` for settings/connection/moderation,
  `chat` for chat only, `misc` for minor non-game informational output.
- Use `play_sound`, `user.play_sound`, `play_music`, ambience helpers, scheduled
  sounds, or sequences as appropriate.
- Provide information actions for state queries such as hand, board/table,
  counts, status, scores, and whose turn.

## Localization

All player-facing strings go through Fluent. No hardcoded English may reach
players.

- Use `speak_l`, `broadcast_l`, `broadcast_personal_l`, localized option/pref
  helpers, and localized sequence helpers.
- Pass raw data as kwargs and let Fluent format lists, plurals, and selects.
- Maintain EN/VI parity: same keys, variables, and plural/select arms.
- Agents author both EN and VI strings in this repo, but Vietnamese is
  provisional and should be flagged for native review when quality matters.
- Prefer writing locale keys before feature code so every announcement path is
  planned.
- Locale discovery and fallback must stay dynamic. Do not hardcode language
  branches in feature code; new languages should be added through locale files
  and metadata/registry layers. Missing translated strings or documentation
  must fall back to English rather than exposing raw keys to players.
- Validate server Fluent changes with `server/tools/compare_locales.py`; it
  reports missing keys, obsolete keys, variables, select/plural arms, and
  attributes. Do not leave obsolete target keys behind after refactors.

### String Localization & Contextual Broadcasting Standard

Whenever a new game is added or an existing game is modified with player-facing
string changes, perform a complete string and broadcast-context audit.

- Every actor-attributable gameplay broadcast must have distinct personal
  first-person and public third-person forms: the actor hears "You ...", while
  other listeners hear "<PlayerName> ...". Use `broadcast_personal_l(...)` or
  an equivalent per-listener localized helper. Do not send the actor the same
  third-person message as everyone else. Genuinely global events with no actor
  may use one shared form.
- Evaluate every message against the complete state and audience matrix,
  including actor versus observer, player versus team, success versus failure,
  active versus waiting/resolving state, option variants, spectators, bots,
  reconnect/save restoration, and relevant brief-announcement variants.
- Errors, warnings, disabled-action reasons, confirmations, and gameplay
  notifications must identify the attempted action, the specific blocking or
  resulting condition, and the state values needed to understand what happened
  and what the player can do next. Avoid generic messages such as "You cannot
  do that" when a contextual explanation is available.
- Keep EN/VI keys and variables structurally synchronized, localize
  listener-dependent values per recipient, and add tests for both actor and
  observer wording plus important contextual and error branches.

## Documentation

When writing or updating documentation, first read existing polished project
manuals for similar games and follow their standard structure, formatting, and
player-facing tone.

- Manuals must be beginner-friendly, accessible, and focused on how to play:
  overview, goal, turn flow, special mechanics, scoring, options, information
  actions, and shortcuts where relevant.
- Do not write manuals like changelogs, patch notes, design notes, or developer
  justifications. Leave out unnecessary implementation details and rationale
  that do not help a player understand the game.
- Keep vocabulary plain and concrete. Explain game terms before relying on
  them, especially for custom games or mechanics that may be unfamiliar.
- Keep EN/VI documentation synchronized in structure, meaning, terminology, and
  attribution. Vietnamese docs should be natural and friendly, with terminology
  aligned to the matching `.ftl` strings.
- Community translation work must follow `TRANSLATING.md`, including variable
  preservation, perspective-key parity, documentation fallback, and contributor
  credit metadata.

## Scores, Leaderboards, and Teams

- Only games with real leaderboard support should expose
  `get_supported_leaderboards()` entries.
- Scoreless games should not claim score support; score buttons are hidden and
  `s` / `shift+s` are ignored silently.
- Games using default score actions must keep `TeamManager` synchronized.
- Non-point units need a localized `score_unit_key` in shared `games.ftl` or the
  game locale when unique. Units are display only; stored stats remain numeric.
- Brief score checks speak one line per player/team in the `game` buffer.
- Detailed score checks normally use `live_status_box(...)` with one line per
  player/team.
- Team games use shared team arrangement. Call
  `_setup_team_manager_for_start(...)`; use `_get_team_turn_players(...)` when
  seating affects turn order. Do not build per-game team selection UI.

## Persistence and Data Lifecycle

Any persistent feature must define and test:

- what is stored and why
- lifespan/retention
- cleanup/pruning of stale data
- account-deletion behavior
- migration/backward compatibility when schemas or supported games change

Do not add database rows, tables, saved runtime state, notifications, chat logs,
tokens, invites, moderation records, or similar data without this lifecycle.

## Server Power Management

Server reboot and shutdown flows must go through the centralized server power
manager and admin UI. Do not add chat-command reboot/shutdown paths or
per-game shutdown hooks.

- Planned reboot preserves active tables through transient table checkpoints,
  freezes framework-owned mutation during finalization, skips normal bot
  substitution on disconnect, and lets clients auto-reconnect.
- Planned shutdown clears active table checkpoints and must warn players to
  save anything they want to keep before the server goes offline.
- Transient checkpoints need kind, creation time, expiration, pruning, and
  account-deletion cleanup. Keep the one-day checkpoint TTL unless a future
  migration explicitly changes the lifecycle.
- Post-reboot no-show handling belongs in shared table/game framework logic:
  restored tables receive a grace window, then missing active players are
  replaced with bots only when at least one human has returned; tables with no
  humans eventually close through abandoned-table cleanup.

## Server, Web, Desktop, and Mobile Rules

- Server navigation uses `_nav_push`, `_nav_back`, `_nav_refresh`, and
  `_restore_frame`; action handlers should not call `_show_*()` directly.
  The stack remembers the opener item and restores focus on Back/cancel and
  action completion.
  Server-owned menu selections are validated against the active menu before
  dispatch; stale client packets and forged item ids are ignored.
- Use `_enter_input_state(...)` / `server.enter_input_state(...)` for editbox
  input state instead of mutating `_user_states`.
- Reconnect restoration and ghost cleanup must route through centralized restore
  code.
- Web client must never use `innerHTML` with server-controlled content.
- Web client code is modular: `game.js` is only the version/bootstrap entry;
  runtime logic belongs in `app.js`, `store.js`, `network.js`, `audio.js`,
  `a11y.js`, `keybinds.js`, `ui/`, and `locales/`.
- Web menus must preserve desktop-style keyboard behavior, touch activation,
  focus anchoring, bottom-ordered ARIA live regions, and capped/coalesced
  history rendering. Server editbox packets choose single-line versus
  multiline inputs through the `multiline` flag.
- Web speech prefs are `speech_mode`, `speech_voice`, `speech_rate`.
- Mobile speech prefs are `mobile_tts_engine`, `mobile_tts_voice`,
  `mobile_tts_rate`; unavailable synced voices/engines must fall back safely.
- Web locale catalogs are loaded through `web_client/locales/manifest.js` and
  `index.js`; mobile locale catalogs are loaded through the generated
  `mobile_client/src/i18n/localeCatalogs.ts` registry. Keep registry metadata
  synchronized when adding languages.
- Server locale directories must include `metadata.json` for translator credit
  and official/community status. Keep `languages.ftl` for localized language
  names; do not replace viewer-localized names with metadata-only labels.
- Mobile connects as `client: "mobile"`, is treated as touch, uses SecureStore
  for credentials, AsyncStorage for local prefs, and must enforce mandatory APK
  updates on version/sound-pack mismatch.
- Desktop passwords live only in OS keyring. Saved microphone devices must fall
  back to system default if unavailable.

## New Game Requirements

Files normally required:

- `server/games/<type>/__init__.py`
- `server/games/<type>/game.py`
- optional `server/games/<type>/bot.py`
- `server/locales/en/<type>.ftl`
- `server/locales/vi/<type>.ftl`
- `server/documentation/content/en/games/<type>.md`
- `server/documentation/content/vi/games/<type>.md`
- `server/tests/test_<type>.py`

Also register the game in `server/games/__init__.py`.

Documentation must follow the Documentation rules above and established game
docs: escaped markdown bold, overview, gameplay, special mechanics, scoring,
customizable options with defaults/ranges, and game-specific keyboard shortcuts.

Tests should cover registration/default options, pre-start validation, core
mechanics, scoring/scoreless behavior, bot completion, touch visibility/order,
keybind collisions, sound/TTS paths, transitions, and game completion.

## Code Style

- Module-level imports only, except `main()` in `client/client.py` where CWD
  setup must happen first.
- Prefer existing helpers and local patterns over new abstractions.
- Keep edits scoped; do not refactor unrelated code.
- Game classes: `<Name>Game`; player classes: `<Name>Player`; options:
  `<Name>Options`; type ids lowercase without separators; action ids
  `snake_case`.
- Handler names: `_action_<id>`; visibility: `_is_<id>_hidden`; enabled:
  `_is_<id>_enabled`.
- Use structured parsers/APIs where available; avoid ad-hoc string parsing.
- Update `CLAUDE.md` and `README.md` when catalog counts or user-facing catalog
  data changes.
