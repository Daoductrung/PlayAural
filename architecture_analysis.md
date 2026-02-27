# PlayAural Architecture and Workflow Analysis

## 1. High-Level Architecture

The PlayAural architecture follows a classic **Client-Server** model with a **Stateful Game Server**.

*   **Communication:** WebSocket (JSON payloads).
*   **State:** The server is the single source of truth. Clients are "dumb terminals" that render the current state provided by the server.
*   **Concurrency:** Async I/O (Networking) + Synchronous Logic (Game Loop).

```mermaid
graph TD
    Client[Client (Python/Web)] <-->|WebSocket| Server[WebSocket Server]
    Server --> Router[Packet Router]
    Router --> Auth[Auth Manager]
    Router --> Tables[Table Manager]
    Router --> Admin[Admin Mixin]

    Tables --> GameInst[Game Instance]
    GameInst --> Logic[Game Logic Mixins]

    Server --> DB[(SQLite Database)]
    Server --> Loop[Tick Scheduler]
    Loop -->|50ms| GameInst
```

## 2. Key Workflows

### A. Authentication & Session
1.  **Connect:** Client opens WebSocket connection.
2.  **Auth Request:** Client sends `authorize` packet with credentials.
3.  **Validation:** `AuthManager` checks DB (Argon2 hash).
4.  **Session:** On success, `NetworkUser` is created. `authorize_success` packet sent with preferences and update info.
5.  **Reconnection:** If user disconnects, `NetworkUser` remains briefly in memory to allow quick reconnects (debounce).

### B. Game Loop & State Management
1.  **Tick:** `TickScheduler` fires every 50ms.
2.  **Update:** Server calls `on_tick()` on all active tables.
3.  **Bot AI:** Games call `BotHelper.on_tick()` to process AI logic.
4.  **Events:** User inputs (Menu selection, Keybinds) are routed to `EventHandlingMixin`.
5.  **Actions:** `ActionExecutionMixin` executes the logic (e.g., `_action_roll`).
6.  **State Change:** Game state changes (imperative).
7.  **Feedback:** Game calls `rebuild_all_menus()` or `broadcast_l()` to push updates to clients.

### C. Administration Workflow
The Administration system is built directly into the `Server` class via inheritance (`AdministrationMixin`).

1.  **Access:** User selects "Administration" from Main Menu.
2.  **Permission Check:** Server checks `user.trust_level >= 2`.
3.  **Menu Generation:** `_show_admin_menu` builds a dynamic menu of available tools.
4.  **Action:**
    *   **Broadcast:** Admin enters text -> Server iterates all online users -> Sends `chat` packet.
    *   **Kick:** Admin selects user -> Server sends `force_exit` packet -> Server closes connection.
    *   **Account:** Admin approves/declines -> DB update -> Notification sent.

## 3. Architecture Strengths & Weaknesses for Admin Tasks

### Strengths
*   **Centralized Control:** Since the admin logic is in the server core, it has direct access to all `NetworkUser` objects, active tables, and the database.
*   **Real-time:** Admin actions (like kicks or broadcasts) happen instantly via the websocket connection.
*   **Unified Interface:** Admin tools use the same Menu/Input UI as the game itself, ensuring accessibility and consistency.

### Weaknesses (Critical for next task)
*   **Tight Coupling:** `AdministrationMixin` modifies `Server` state directly. Adding complex features (like banning logic or logs) risks cluttering the core server class.
*   **Ephemeral Actions:** Current admin actions (Kick) are memory-only or one-off DB updates. There is no persistent "Ban List" or "Audit Log" table in the DB schema.
*   **Limited Scope:** The current implementation mostly handles *User* administration. It lacks *Game* administration (e.g., force-closing a stuck table, pausing the server, inspecting running games without joining).

## 4. Conclusion
The system is robust for gameplay but the administration features are a basic "v0.1" implementation. The architecture allows for easy expansion (adding new DB tables for bans/logs and new menu items), but care must be taken to decouple new complex admin logic from the main `Server` class to maintain maintainability.
