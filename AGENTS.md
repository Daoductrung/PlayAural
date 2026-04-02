# Agents.md — AI Development Guide for PlayAural

This document is the authoritative reference for any AI assistant (Claude, Codex, or other) contributing to the PlayAural codebase. Follow every rule exactly. When in doubt, read the existing code — especially `lastcard/game.py` and `dominos/game.py` as canonical examples.

## 1. Project Overview

PlayAural is an **audio-first multiplayer online gaming platform** with full screen reader support. It has three components:

| Component | Stack | Purpose |
|-----------|-------|---------|
| `server/` | Python 3.11, asyncio, WebSocket | Game logic, auth, persistence |
| `client/` | Python, wxPython | Desktop client (screen reader accessible) |
| `web_client/` | Vanilla JS PWA | Browser client (ARIA, service worker) |

All communication is WebSocket JSON packets: `Packet(type: str, data: dict)`.

---

## 2. Core Architecture

### 2.1 Game Class Hierarchy

Every game is a Python `@dataclass` decorated with `@register_game`, inheriting from `Game` plus 14 mixins:

```
Game (ABC, DataClassJSONMixin)
├── GameSoundMixin          — play_sound, play_music, schedule_sound
├── GameCommunicationMixin  — broadcast_l, speak to players
├── GameResultMixin         — finish_game, end screen
├── GameScoresMixin         — score display
├── GamePredictionMixin     — outcome predictions
├── TurnManagementMixin     — set_turn_players, advance_turn
├── MenuManagementMixin     — rebuild_player_menu, update_player_menu
├── ActionVisibilityMixin   — action visibility resolution
├── LobbyActionsMixin       — lobby phase, bots, prestart_validate
├── EventHandlingMixin      — on_tick, event_queue
├── ActionSetCreationMixin  — keybinds, turn/standard action sets
├── ActionExecutionMixin    — execute_action, find_action
├── OptionsHandlerMixin     — declarative option handling + broadcast
└── ActionSetSystemMixin    — action set resolution
```

Game state is serialized via Mashumaro for persistence. **All game state must live in dataclass fields** — runtime-only state goes in `__post_init__`.

### 2.1b Optional Mixins

Beyond the 14 base mixins, games can inherit from additional utility mixins:

| Mixin | Module | Purpose |
|-------|--------|---------|
| `GridGameMixin` | `game_utils.grid_mixin` | 2D grid navigation, per-player cursors, arrow-key movement, cell actions with `grid_enabled`/`grid_width` protocol flags for web grid rendering. Override `get_cell_label`, `on_grid_select`, `is_grid_cell_enabled`, `is_grid_cell_hidden`. Call `_init_grid()` in `on_start()`, `setup_grid_keybinds()` in `setup_keybinds()`, and `build_grid_actions(player)` + `build_grid_nav_actions()` in `create_turn_action_set()`. Grid games must declare `grid_cursors: dict[str, GridCursor]` exactly — not tuples, lists, or untyped dicts — so Mashumaro can serialize saved table state safely. |
| `TurnTimerMixin` | `game_utils.turn_timer_mixin` | Turn countdown timer using `PokerTurnTimer`. Call `start_turn_timer()`, `stop_turn_timer()`, `on_tick_turn_timer()` in `on_tick()`. |

MRO placement: `class MyGame(Game, TurnTimerMixin)` or `class MyGame(GridGameMixin, TurnTimerMixin, Game)`. `GridGameMixin` must come before `Game`; `TurnTimerMixin` can go either side.

**Grid serialization rule:** If a game uses `GridGameMixin`, every serialized grid field must use Mashumaro-safe types. In particular:
- `grid_cursors` must be annotated as `dict[str, GridCursor]`
- `grid_row_labels` must be `list[str]`
- `grid_col_labels` must be `list[str]`
- Do not store raw `(row, col)` tuples, ad-hoc dicts, or other cursor shapes in serialized game state

Reason: Mashumaro serializers are generated from type annotations, not just runtime values. A mismatched annotation like `dict[str, tuple[int, int]]` can crash table save/restore even if the runtime objects happen to be `GridCursor` instances.

### 2.2 File Structure for a New Game

```
server/games/<game_name>/
├── __init__.py       # from .game import <GameName>Game
├── game.py           # Core game logic
└── bot.py            # Bot AI (optional — can stay in game.py for simple bots)
```

Additionally required:
- `server/locales/en/<game_name>.ftl` — English strings
- `server/locales/vi/<game_name>.ftl` — Vietnamese strings
- `server/documentation/content/en/games/<game_name>.md` — English docs
- `server/documentation/content/vi/games/<game_name>.md` — Vietnamese docs
- `server/tests/test_<game_name>.py` — pytest test suite

Registration:
- Add `from .<game_name>.game import <GameName>Game` to `server/games/__init__.py`
- Add `"<GameName>Game"` to the `__all__` list in the same file

### 2.3 Required Class Methods

Every game must implement these `@classmethod` methods:

| Method | Returns | Example |
|--------|---------|---------|
| `get_name()` | `str` — English display name | `"Dominos"` |
| `get_type()` | `str` — type identifier (lowercase) | `"dominos"` |
| `get_category()` | `str` — category localization key | `"category-board-games"` |
| `get_min_players()` | `int` | `2` |
| `get_max_players()` | `int` | `4` |
| `get_supported_leaderboards()` | `list[str]` | `["wins", "rating", "games_played"]` |

Available categories: `category-card-games`, `category-dice-games`, `category-board-games`, `category-poker`, `category-rb-play-center`, `category-uncategorized`.

### 2.4 Required Instance Methods

| Method | Purpose |
|--------|---------|
| `create_player(id, name, is_bot)` | Return your custom `Player` subclass |
| `on_start()` | Initialize round, deal, set turn order |
| `on_tick()` | Called every 50ms — handle bot AI, timers, events |
| `create_turn_action_set(player)` | Build the turn menu action set |
| `create_standard_action_set(player)` | Build the actions/Escape menu |
| `setup_keybinds()` | Register keyboard shortcuts |
| `bot_think(player)` | Return an action ID for bot AI |
| `build_game_result()` | Build `GameResult` for leaderboards |
| `format_end_screen(result, locale)` | Format end-of-game display |

### 2.5 Player Subclass

Always create a game-specific `Player` subclass as a `@dataclass`:

```python
@dataclass
class MyGamePlayer(Player):
    hand: list[MyCard] = field(default_factory=list)
    score: int = 0
```

Data model classes (cards, tiles, tokens) must also be `@dataclass` with `DataClassJSONMixin` for serialization.

---

## 3. Action System

### 3.1 Action Anatomy

```python
Action(
    id="draw",                          # Unique string ID
    label="Draw a card",                # Static label (or empty if using get_label)
    handler="_action_draw",             # Method name: (self, player, action_id)
    is_enabled="_is_draw_enabled",      # -> str | None (None = enabled, str = disabled reason key)
    is_hidden="_is_draw_hidden",        # -> Visibility.VISIBLE | Visibility.HIDDEN
    get_label="_get_draw_label",        # Optional dynamic label: (self, player, action_id) -> str
    input_request=None,                 # Optional MenuInput or EditboxInput
    show_in_actions_menu=True,          # False = hidden from Escape/Actions menu
    include_spectators=False,           # True = spectators can see/execute
)
```

### 3.2 Action Sets

Games have two action sets per player:
- **Turn set** (`"turn"`) — The primary gameplay menu. Dynamic per-tick.
- **Standard set** (`"standard"`) — The Escape/Actions menu. Static utility actions.

`get_all_enabled_actions()` combines action sets in this order: **turn → lobby → options → standard**. The Escape/actions menu displays them in this combined order. Two rules prevent UX issues:

**Rule 1: Info/status actions belong in `create_standard_action_set`, not `create_turn_action_set`.**
Game-specific read-only actions (check hand, view dice, check status, view table, etc.) must be defined in `create_standard_action_set`. Placing them in the turn set causes them to appear *above* the platform's default global actions (leave game, scores, game info) in the Escape menu, breaking consistent ordering across games. They are still accessible via their keybinds regardless of which set they belong to.

**Rule 2: Turn actions need `show_in_actions_menu=False`.**
Core gameplay actions (hit, stand, roll, play card, shoot, etc.) already appear as tappable buttons in the turn menu. Without `show_in_actions_menu=False`, they also appear at the *top* of the Escape/actions menu, pushing global actions down. Set `show_in_actions_menu=False` on every turn action that is already visible in the turn menu.

**Summary:**
- **Turn action set**: Only actions that need to appear as turn menu buttons (play, roll, pass, etc.) — always with `show_in_actions_menu=False`.
- **Standard action set**: Info/status actions (check hand, view scores, view table, etc.) — always below default global actions in the Escape menu.
- **Keybinds**: Work independently of which action set an action belongs to.

### 3.3 Spectator Visibility (`include_spectators`)

- **Default `False`** — player-private actions (play card, read hand, fold)
- **Set `True`** — public information (scores, turn status, table info, game rules)
- The `include_spectators` flag on `Action` and its corresponding `Keybind` **must always agree**

Standard/lobby actions already `include_spectators=True` in base class: `show_actions`, `toggle_spectator`, `host_management`, `leave_game`, `start_game`, `add_bot`, `remove_bot`, `whose_turn`, `whos_at_table`, `check_scores`, `check_scores_detailed`, `predict_outcomes`, `game_info`, `game_rules`.

### 3.4 Dynamic Turn Menu (`_sync_turn_actions`)

For games with dynamic hand/tile content, implement `_sync_turn_actions(player)` to rebuild tile/card actions each tick:

1. Remove old dynamic actions: `turn_set.remove_by_prefix("play_tile_")`
2. Re-add based on current hand
3. Set `turn_set._order` to control display order
4. Call from `rebuild_player_menu`, `update_player_menu`, and `rebuild_all_menus`

---

## 4. Keybind System

### 4.1 Defining Keybinds

```python
def setup_keybinds(self) -> None:
    super().setup_keybinds()  # MUST call super — registers all base keybinds
    self.define_keybind("space", "Draw", ["draw"], state=KeybindState.ACTIVE)
    self.define_keybind("v", "View chain", ["view_chain"],
                        state=KeybindState.ACTIVE, include_spectators=True)
```

### 4.2 KeybindState Values

| State | When active |
|-------|-------------|
| `NEVER` | Disabled |
| `IDLE` | Lobby/waiting only |
| `ACTIVE` | During gameplay only |
| `ALWAYS` | Always available |

### 4.3 Reserved Keys — DO NOT USE

These keys are bound by the base class or client. **Never assign them in a game:**

| Key | Base Function |
|-----|---------------|
| `enter` | Start game (lobby) |
| `escape` | Actions menu |
| `b` | Add bot (lobby) |
| `shift+b` | Remove bot (lobby) |
| `f3` | Toggle spectator (lobby) |
| `t` | Whose turn |
| `s` | Check scores |
| `shift+s` | Detailed scores |
| `ctrl+m` | Host management |
| `ctrl+q` | Leave table |
| `ctrl+u` | Who's at table |
| `ctrl+s` | Save table |
| `ctrl+r` | Predict outcomes |
| `ctrl+i` | Game info |
| `ctrl+f1` | How to play |

### 4.4 Keybind Audit Rule

Before finalizing keybinds, verify:
- No collision with reserved keys above
- `include_spectators` on keybind matches the corresponding `Action`
- Every gameplay keybind uses `state=KeybindState.ACTIVE`

---

## 5. GameOptions (Declarative Options System)

### 5.1 Defining Options

```python
@dataclass
class MyGameOptions(GameOptions):
    target_score: int = option_field(
        IntOption(default=100, min_val=10, max_val=500,
                  value_key="score",
                  label="mygame-set-target-score",
                  prompt="mygame-enter-target-score",
                  change_msg="mygame-option-changed-target-score"))
    mode: str = option_field(
        MenuOption(default="normal", choices=["normal", "hard"],
                   label="mygame-set-mode", prompt="mygame-select-mode",
                   change_msg="mygame-option-changed-mode",
                   choice_labels={"normal": "mygame-mode-normal", "hard": "mygame-mode-hard"}))
    hints: bool = option_field(
        BoolOption(default=True, label="mygame-set-hints",
                   change_msg="mygame-option-changed-hints"))
```

Option types: `IntOption`, `FloatOption`, `MenuOption`, `BoolOption`, `TeamModeOption`.

### 5.2 Rules

- **Every option MUST have working game logic.** No dead options. Grep `self.options.<name>` to verify it's used.
- **Every option MUST have a `change_msg` key** defined in both EN and VI `.ftl` files. The system broadcasts changes automatically.
- **`MenuOption` must have `choice_labels`** mapping internal values to localization keys so users see localized text, not raw strings.
- **`TeamModeOption`** uses `TeamManager.get_all_team_modes(min, max)` for dynamic choices.

### 5.3 Pre-start Validation

Override `prestart_validate()` to catch invalid option combinations before the game starts:

```python
def prestart_validate(self) -> list[str | tuple[str, dict]]:
    errors = super().prestart_validate()
    # Validate team mode
    team_error = self._validate_team_mode(self.options.team_mode)
    if team_error:
        errors.append(team_error)
    # Validate deck/hand constraints
    if self.options.hand_size * len(self.get_active_players()) + 1 > 108:
        errors.append(("mygame-error-too-many-cards",
                       {"players": len(self.get_active_players()), "hand_size": self.options.hand_size}))
    return errors
```

---

## 6. Audio-First Design & Screen Reader Accessibility

### 6.1 Core Principle

PlayAural is designed for visually impaired users. **Every game state change must be communicated through audio** — either TTS announcements or sound effects. The UI is navigated entirely by keyboard (desktop) or sequential button taps (web).

### 6.2 TTS Buffer Rules

Every `speak_l()` and `broadcast_l()` call **must** include an explicit `buffer=` parameter:

| Buffer | Use For |
|--------|---------|
| `"game"` | All gameplay events — turns, plays, scores, state changes |
| `"system"` | Connections, host management, settings, errors |
| `"chat"` | Player-to-player messages only |
| `"misc"` | Minor informational messages that fit none of the above |

### 6.3 Sound Design

- Use `self.play_sound(path)` for global events all players hear
- Use `user.play_sound(path)` for player-specific feedback
- Use `self.play_music(path)` for background music
- Use `self.schedule_sound(path, delay_ticks)` for timed audio
- `on_tick()` must call `super().on_tick()` and `self.process_scheduled_sounds()`

### 6.4 Information Actions

Provide keybind-accessible information actions so players can query game state at any time:
- Read hand / Read tiles (player-private, `include_spectators=False`)
- View board / Read chain (public, `include_spectators=True`)
- Read opponent counts (public, `include_spectators=True`)
- Check scores (inherited from base class)

---

## 7. Web/Mobile UI Rules (Mandatory)

Desktop users have keyboard shortcuts. Web/mobile users rely on **tappable buttons in the Turn Menu**. Every game must account for both.

### 7.1 Web Client Detection

```python
user = self.get_user(player)
if user and getattr(user, "client_type", "") == "web":
    return Visibility.VISIBLE
```

### 7.2 Time-Critical Reaction Actions

Actions that require fast response (buzzer, challenge, jump-in, accept) **must** be visible as tappable buttons in the Turn Menu during their active windows for web clients. Use `is_hidden` callbacks to conditionally show them:

```python
def _is_buzzer_hidden(self, player: Player) -> Visibility:
    # Desktop users use keybinds — hide from turn menu
    if self.status != "playing" or player.is_spectator:
        return Visibility.HIDDEN
    user = self.get_user(player)
    if user and getattr(user, "client_type", "") == "web":
        if self._is_reaction_window_active():
            return Visibility.VISIBLE
    return Visibility.HIDDEN
```

### 7.3 Utility Actions for Web

Actions that desktop users access via keybinds (sort hand, read hand, view board, read counts) should appear in the Turn Menu for web clients. Override their `is_hidden` to return `VISIBLE` when `client_type == "web"`.

### 7.4 Turn Menu Ordering

Order matters for screen readers — users navigate sequentially top-to-bottom:

1. **Reaction buttons** (buzzer, challenge, accept) — top
2. **Card/tile play actions** — middle
3. **Confirm selection** (if multi-select) — after cards
4. **Utility buttons** (draw, pass, knock, sort) — bottom

Implement ordering in `_sync_turn_actions` by manipulating `turn_set._order`:

```python
user = self.get_user(player)
if user and getattr(user, "client_type", "") == "web":
    top = ["buzzer", "challenge"]
    bottom = ["draw", "knock", "sort"]
    card_ids = [aid for aid in turn_set._order if aid.startswith("play_")]
    pinned = set(top) | set(bottom) | set(card_ids)
    middle = [aid for aid in turn_set._order if aid not in pinned]
    turn_set._order = (
        [aid for aid in top if aid in turn_set._order]
        + middle + card_ids
        + [aid for aid in bottom if aid in turn_set._order]
    )
```

### 7.5 Standard Action Ordering for Web

Within the standard action set, web clients must maintain a **consistent ordering** of the platform's base info actions across all games:

1. **Game-specific info actions** (check status, view table, read hand, etc.) — top
2. **`check_scores`** (if the game tracks scores) — after game-specific
3. **`whose_turn`** — after check_scores
4. **`whos_at_table`** — last

Implement this via web reordering in `create_standard_action_set`:

```python
if user and getattr(user, "client_type", "") == "web":
    target_order = ["game_specific_action", "check_scores", "whose_turn", "whos_at_table"]
    new_order = [aid for aid in action_set._order if aid not in target_order]
    for aid in target_order:
        if action_set.get_action(aid):
            new_order.append(aid)
    action_set._order = new_order
```

For games that track scores, also add a `_is_check_scores_hidden` visibility override (visible for web when playing). See `pig/game.py` or `farkle/game.py` as references.

---

## 8. Turn Management

### 8.1 Critical Rules

- **`set_turn_players(players)`** resets `turn_index` to 0. `players[0]` becomes current immediately.
- **`advance_turn()`** increments the index. **Never** call immediately after `set_turn_players` — it skips the first player.
- **Canonical round start pattern:**
  ```python
  self.set_turn_players(active_players)
  self.announce_turn()  # NO advance_turn() between these
  ```
- **`get_active_players()`** excludes spectators. Always use it for game logic — never iterate `self.players` directly.

### 8.2 Bot Turn Management

```python
def _queue_bot_turn(self) -> None:
    current = self.current_player
    if current and current.is_bot:
        BotHelper.jolt_bot(current, ticks=random.randint(12, 24))

def on_tick(self) -> None:
    super().on_tick()
    self.process_scheduled_sounds()
    if self.status == "playing" and self.current_player and self.current_player.is_bot:
        BotHelper.on_tick(self)

def bot_think(self, player: Player) -> str | None:
    # Return an action ID string, or None to skip
    ...
```

- `BotHelper.jolt_bot` sets `bot_think_ticks` for a delay before the bot acts
- `BotHelper.on_tick` decrements ticks and calls `bot_think` → `execute_action`
- In tests, use `advance_until(game, condition_fn, max_ticks=500)` instead of fixed tick counts

---

## 9. Localization

### 9.1 Locale File Structure

Every game needs two `.ftl` files:
- `server/locales/en/<game_type>.ftl`
- `server/locales/vi/<game_type>.ftl`

### 9.2 Required Key Patterns

```ftl
# Game name (required — used by server menu system)
game-name-<type> = <English Name>

# Option labels (one per option — use $<value_key> as the variable name)
<type>-set-<option> = <Label>: { $<value_key> }
<type>-enter-<option> = <Prompt>               # IntOption/FloatOption only
<type>-select-<option> = <Prompt>              # MenuOption only
<type>-option-changed-<option> = <Changed message with $<value_key>>.

# Option choice labels (MenuOption)
<type>-mode-<choice> = <Localized choice name>

# Action labels
<type>-<action> = <Label>

# Disabled reasons
<type>-<reason> = <Explanation>.

# Gameplay messages
<type>-<event> = <Message with $player, $tile, etc.>
```

### 9.3 Rules

- Every key in the EN file must have a corresponding key in the VI file
- Use Fluent plurals for countable nouns: `{ $count -> [one] tile *[other] tiles }`
- Use `Localization.get(locale, key, **kwargs)` for formatting
- Use `Localization.format_list_and(locale, items)` for joining lists with localized "and"

---

## 10. Documentation

### 10.1 File Locations

- `server/documentation/content/en/games/<game_type>.md`
- `server/documentation/content/vi/games/<game_type>.md`

### 10.2 Required Sections

1. **Game title** — bold, first line
2. **Overview** — 1-2 sentence summary
3. **Gameplay** — How a round works
4. **Special mechanics** — Opening rules, drawing, blocking, etc.
5. **Scoring** — How points are calculated
6. **Customizable Options** — Every option with default and range
7. **Keyboard Shortcuts** — Every game-specific keybind

### 10.3 Formatting Convention

Documentation uses escaped markdown: `\*\*Bold\*\*`, `\* Bullet item`. This is the established pattern — follow it exactly.

---

## 11. Testing

### 11.1 File Location

`server/tests/test_<game_type>.py`

### 11.2 Standard Test Helpers

```python
def make_game(player_count=2, start=False, **option_overrides) -> MyGame:
    game = MyGame(options=MyGameOptions(**option_overrides))
    game.setup_keybinds()
    for i in range(player_count):
        name = f"Player{i + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{i + 1}"))
    game.host = "Player1"
    if start:
        game.on_start()
    return game

def advance_until(game, condition, max_ticks=400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()
```

### 11.3 Required Test Coverage

- Game registration and default options
- Pre-start validation (valid and invalid cases)
- Core gameplay mechanics (play, draw, pass/knock)
- Scoring (round win, blocked round, team mode)
- Bot AI completes a game without infinite loops
- Web client turn menu visibility and ordering
- Keybind registration (no reserved key collisions)
- Sound and TTS broadcast to all players
- Round transitions and match completion

### 11.4 Bot Test Rule

Always test that a bot game completes: use `advance_until` with a high `max_ticks` and assert the game finishes. Bot infinite loops are a critical regression.

---

## 12. Code Style Rules

### 12.1 Imports

- **All imports at module level.** No in-function imports anywhere in the server codebase.
- Only exception: `main()` in `client/client.py` where CWD must be set first.

### 12.2 Naming

- Game class: `<Name>Game` (e.g., `DominosGame`)
- Player class: `<Name>Player` (e.g., `DominosPlayer`)
- Options class: `<Name>Options` (e.g., `DominosOptions`)
- Game type string: lowercase, no separators (e.g., `"dominos"`, `"lastcard"`)
- Action IDs: `snake_case` (e.g., `"play_tile"`, `"draw"`, `"read_hand"`)
- Handler methods: `_action_<id>` (e.g., `_action_draw`)
- Visibility methods: `_is_<id>_hidden` (e.g., `_is_draw_hidden`)
- Enabled methods: `_is_<id>_enabled` (e.g., `_is_draw_enabled`)

### 12.3 General

- Keep game logic in `game.py` per game (bot AI can live in a separate `bot.py`)
- Use `get_active_players()` — never iterate `self.players` for gameplay logic
- Always call `super().on_tick()` and `self.process_scheduled_sounds()` in `on_tick`
- Always call `super().setup_keybinds()` in `setup_keybinds`
- Always call `super().create_standard_action_set(player)` when overriding
- Never use `innerHTML` with server data in the web client — use `textContent`

### 12.4 Persistence & Data Lifecycle

Any new database-backed feature must define its data lifecycle up front. Do not add persistent storage without also deciding how that data ages, expires, or gets removed.

Required review for every new persistent table, column, or record type:
- **Stored data**: Document exactly what is stored and why it must persist.
- **Lifespan**: Decide whether the data is permanent, bounded, or time-limited.
- **Cleanup mechanism**: If the data can become stale, define how it is cleaned up. This can be immediate deletion on use, periodic pruning at startup, scheduled cleanup, bounded retention, or explicit admin/user deletion.
- **Account deletion behavior**: Decide whether the data should be deleted, anonymized, or preserved when an account is removed. Never leave orphaned rows behind.
- **Testing**: Add tests that prove the cleanup path works, especially for expiry, stale-row pruning, and account deletion behavior.

Examples of features that require this review include chat logs, notifications, invitations, friend requests, password reset tokens, moderation records, saved states, temporary UI records, and any future time-bound or accumulative data.

Rule: if a feature can create rows that are no longer useful after some time or after a user is deleted, the implementation is incomplete until its cleanup policy and tests are in place.

---

## 13. New Game Checklist

Use this checklist when implementing a new game. Every item is mandatory.

### Architecture
- [ ] Game class is a `@dataclass` decorated with `@register_game`
- [ ] Game inherits from `Game` (which brings all 14 mixins), plus optional mixins like `GridGameMixin`, `TurnTimerMixin` as needed
- [ ] Custom `Player` subclass with `DataClassJSONMixin`-compatible fields
- [ ] Custom data model classes (cards/tiles/tokens) are `@dataclass` with `DataClassJSONMixin`
- [ ] `GameOptions` subclass uses declarative `option_field()` for every setting
- [ ] Game registered in `server/games/__init__.py` (import + `__all__`)

### Game Logic
- [ ] `on_start` sets `status = "playing"`, calls `_sync_table_status()`, initializes round
- [ ] `on_tick` calls `super().on_tick()` and `self.process_scheduled_sounds()`
- [ ] `bot_think` returns a valid action ID for every possible game state
- [ ] Bot game tested to completion — no infinite loops
- [ ] `build_game_result` uses `get_active_players()` for player list
- [ ] `prestart_validate` checks team mode and any option conflicts

### Actions & Keybinds
- [ ] `setup_keybinds` calls `super().setup_keybinds()` first
- [ ] No keybind collisions with reserved keys (see Section 4.3)
- [ ] `include_spectators` agrees between `Action` and `Keybind`
- [ ] Dynamic actions use `_sync_turn_actions` pattern
- [ ] Player-private actions: `include_spectators=False`
- [ ] Public info actions: `include_spectators=True`
- [ ] Turn actions have `show_in_actions_menu=False` (see Section 3.2)
- [ ] Info/status actions defined in `create_standard_action_set`, not turn set (see Section 3.2)

### Options
- [ ] Every option has working game logic (no dead options)
- [ ] Every option has `change_msg` defined in both EN and VI `.ftl` files
- [ ] `MenuOption` has `choice_labels` mapping values to locale keys
- [ ] `prestart_validate` catches invalid combinations

### Web/Mobile UI
- [ ] Reaction actions visible in Turn Menu for web clients during active windows
- [ ] Utility actions (read hand, sort, etc.) visible in Turn Menu for web clients
- [ ] Turn Menu ordered: reactions → cards/tiles → utilities
- [ ] Standard actions reordered for web: game-specific → `check_scores` → `whose_turn` → `whos_at_table` (see Section 7.5)
- [ ] `whose_turn`, `whos_at_table` visible for web clients; `check_scores` visible if game tracks scores

### Audio & Accessibility
- [ ] Every game state change announced via TTS (`broadcast_l` / `speak_l`)
- [ ] Correct `buffer=` on every TTS call (see Section 6.2)
- [ ] Sound effects for key events (play, draw, win, blocked, etc.)
- [ ] Information actions queryable by keybind (read hand, read board, etc.)

### Localization
- [ ] `game-name-<type>` key in both EN and VI `.ftl` files
- [ ] All option keys, action labels, gameplay messages in both locales
- [ ] All keys in EN file have corresponding keys in VI file
- [ ] Option `choice_labels` keys defined in both locales

### Documentation
- [ ] EN and VI documentation files in `server/documentation/content/`
- [ ] Covers: overview, gameplay, scoring, all options with defaults, all keybinds
- [ ] Uses `\*\*bold\*\*` escaped markdown format

### Testing
- [ ] Test file at `server/tests/test_<game_type>.py`
- [ ] Registration and default options test
- [ ] Pre-start validation tests
- [ ] Core gameplay tests (play, draw/knock, scoring)
- [ ] Bot completion test
- [ ] Web client visibility tests
- [ ] Keybind collision test
- [ ] All tests pass: `cd server && pytest tests/test_<game_type>.py`

### Project Files
- [ ] Game count updated in `CLAUDE.md`
- [ ] Game added to `README.md` Game Catalog (correct category)
