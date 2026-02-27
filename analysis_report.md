# PlayAural Codebase Analysis

## 1. Directory Structure

```text
/
├── client/                 # Python Desktop Client (wxPython)
│   ├── locales/            # Client-side localization files
│   ├── sounds/             # Audio assets
│   ├── ui/                 # UI components (MainWindow, Dialogs)
│   ├── client.py           # Main client entry point
│   ├── network_manager.py  # Client networking logic
│   └── ...
├── server/                 # Game Server
│   ├── auth/               # Authentication & Session Management
│   │   └── auth.py         # AuthManager class (Argon2, Sessions)
│   ├── core/               # Core Server Logic
│   │   ├── administration.py # Admin features (Kick, Ban, Broadcast)
│   │   ├── server.py       # Main Server class (Connection glue)
│   │   └── tick.py         # TickScheduler (Game loop)
│   ├── game_utils/         # Reusable Game Logic Mixins
│   │   ├── actions.py      # Action/ActionSet definitions
│   │   ├── options.py      # Declarative Game Options
│   │   ├── bot_helper.py   # AI Logic Helper
│   │   └── ... (mixins for menus, turns, sound, etc.)
│   ├── games/              # Game Implementations
│   │   ├── base.py         # Abstract Game class
│   │   ├── registry.py     # GameRegistry
│   │   ├── pig/            # Example: Pig Game
│   │   └── ... (other games)
│   ├── messages/           # Server-side Localization
│   │   └── localization.py # Localization logic
│   ├── network/            # WebSocket Networking
│   │   ├── protocol.py     # Protocol definitions
│   │   └── websocket_server.py # Async Server Wrapper
│   ├── persistence/        # Database Access
│   │   └── database.py     # SQLite wrapper
│   ├── tables/             # Table Management
│   │   ├── manager.py      # TableManager
│   │   └── table.py        # Table class (Lobby logic)
│   ├── users/              # User Objects
│   │   ├── base.py         # Abstract User
│   │   ├── network_user.py # Connected Player
│   │   └── bot.py          # AI Player
│   ├── main.py             # Server Entry Point
│   └── cli.py              # CLI for simulation/testing
├── web_client/             # Web Client (HTML/JS)
│   ├── game.js             # Main Game Logic (Audio, WS, UI)
│   ├── index.html          # Entry page
│   └── ...
├── README.md               # Project Documentation
└── ... (Build scripts, etc.)
```

## 2. Core File Analysis

### Server Core (`server/core/`)
*   **`server.py`**: The central hub. It initializes the `WebSocketServer`, `Database`, `AuthManager`, and `TableManager`. It handles the main event loop, routing incoming packets (`authorize`, `menu`, `game_action`) to the appropriate components (User, Table, or Game).
*   **`administration.py`**: A Mixin for the `Server` class. It implements the "Administration" menu logic. Currently supports:
    *   **Account Approval:** Listing/approving/declining pending users.
    *   **Role Management:** Promoting/demoting admins.
    *   **Broadcasting:** Sending server-wide messages.
    *   **Kicking:** Removing users from the server.
    *   *Observation:* Logic is tightly coupled to the Server class via the Mixin pattern.
*   **`tick.py`**: Implements a fixed-timestep loop (default 50ms). It calls `on_tick()` on the server, which propagates to tables and games. This ensures deterministic game logic execution separate from async network I/O.

### Networking (`server/network/`)
*   **`websocket_server.py`**: Wraps the `websockets` library. It maintains a dictionary of `ClientConnection` objects. It handles the raw async send/receive and SSL termination. It monkey-patches `ServerProtocol` to handle proxy header stripping (Cloudflare/Nginx fix).

### Authentication (`server/auth/`)
*   **`auth.py`**: Manages user credentials using `Argon2` for hashing. It supports automatic migration from legacy SHA-256 hashes. It handles registration validation (unique usernames) and session token generation.

### Persistence (`server/persistence/`)
*   **`database.py`**: A wrapper around `sqlite3`. It handles all SQL queries for:
    *   Users (credentials, preferences, trust levels).
    *   Game Results (history, statistics).
    *   Saved Tables (serialized game states).
    *   Player Ratings (TrueSkill-like ELO).

### Game Architecture (`server/games/` & `server/game_utils/`)
*   **`base.py` (`Game`)**: The abstract base class for all games. It inherits from numerous Mixins in `game_utils` (e.g., `GameSoundMixin`, `TurnManagementMixin`). It defines the lifecycle (`on_start`, `on_tick`) and state serialization (`Mashumaro`).
*   **`game_utils/actions.py`**: Defines the Command pattern used for game logic. `Action` objects wrap callbacks (`handler`, `is_enabled`, `is_hidden`). `ActionSet` groups them (e.g., "turn", "lobby"). This allows declarative UI construction.
*   **`game_utils/lobby_actions_mixin.py`**: Implements standard lobby features like adding bots, starting the game, and saving the table.

## 3. Administration Feature Deep Dive

The administration system is currently implemented as a Mixin (`AdministrationMixin`) in `server/core/administration.py`.

**Current Capabilities:**
1.  **Menu Interface:** Accessible via "Administration" in the Main Menu (visible only to users with `trust_level >= 2`).
2.  **User Management:**
    *   View pending accounts.
    *   Approve/Decline pending accounts (decline = delete).
    *   Promote users to Admin.
    *   Demote Admins (restricted: cannot demote Developers `trust_level >= 3`).
    *   Kick online users.
3.  **Communication:**
    *   Broadcast message to all online users (as "System").

**Limitations & Observations:**
*   **Lack of Granularity:** Admin actions are binary (Admin vs User). There is no "Moderator" role.
*   **No Ban System:** Kicking is temporary. There is no mechanism to permanently ban a user or IP in the codebase currently.
*   **No Logs:** Admin actions play sounds and send chat notifications, but there is no persistent audit log in the database to track who did what.
*   **Rudimentary UI:** All interactions are via standard game menus. There is no dashboard or advanced search.
*   **Server-Coupling:** The logic resides directly in the Server core, making it hard to extend without modifying the main server file structure.

## 4. Web Client (`web_client/game.js`)
*   **Architecture:** Monolithic JS file handling WebSocket connection, DOM manipulation, and Audio context.
*   **Audio:** Uses `AudioContext` for mixing Music, SFX, and Ambience. Features an "Audio Wake-Lock" (playing silent buffer) to keep mobile browsers from sleeping the audio engine.
*   **Accessibility:** Heavily focused on ARIA integration. Uses `aria-live` regions for game announcements and TTS integration.
