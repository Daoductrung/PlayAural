"""Mixin providing menu management functionality for games.

Game code never paints turn menus directly. It RECORDS turn-menu intent through
two calls:

- ``refresh_menus(player=None)`` — mark one player (or everyone) as needing
  a repaint.
- ``request_menu_focus(player, action_id)`` — queue a one-shot focus jump
  for a player (and mark them for repaint).

One sealed flush point — ``flush_menus()``, called by the framework at the
end of every ``handle_event()`` and once per server tick — builds and sends
the menus for dirty players. A plain refresh therefore can never move a
cursor, double-paint, or clobber an overlay: the flush owns the focus-steal
guards (status boxes, actions menus, global system menus, pending inputs),
bot skipping, finished-state end screens, and focus delivery. Per-game
copies of that logic were the root cause of a long line of focus-stealing
bugs, so the orchestrators are **sealed**: a game class that overrides one
fails at import time.

Status overlays are the sanctioned exception: ``status_box(...)`` shows static
snapshots, while ``live_status_box(...)`` opens dynamic state panels that
refresh through the same sealed flush path.

Games customize what gets painted through these hooks:

- ``before_menu_build(player)`` — sync dynamic action sets (e.g. per-card
  play actions) before any menu paint. Runs for bots too, so action sets
  stay valid for bot decision logic. Must be idempotent.
- ``build_menu_items(player, user)`` — supply custom ``MenuItem`` lists and
  grid layout kwargs (e.g. the backgammon/senet board grids).

Clients preserve the user's cursor by item identity across a same-menu
repaint, so a flush without a queued focus intent is always
focus-preserving; focus only moves when an intent says so, and each intent
fires at most once.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from ..users.base import User

from ..users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization
from .client_types import is_touch_client


#: Menu orchestrator methods that games must not override. Enforced at class
#: creation time by ``MenuManagementMixin.__init_subclass__``.
SEALED_MENU_ORCHESTRATORS = (
    "refresh_menus",
    "flush_menus",
    "_paint_player_menu",
    "_is_menu_refresh_blocked",
)


@dataclass
class MenuBuild:
    """Result of the ``build_menu_items`` hook.

    ``items`` is the full turn-menu item list in display order. ``grid_kwargs``
    holds the grid layout kwargs forwarded to ``show_menu``
    (``grid_enabled``, ``grid_width``, ``grid_height``), or ``{}`` for a flat
    list menu.
    """

    items: list[MenuItem]
    grid_kwargs: dict = field(default_factory=dict)


@dataclass
class StatusBoxBuild:
    """Result of a static or live status-box builder.

    ``items`` may contain strings or ``MenuItem`` instances. Strings and items
    without ids are assigned stable fallback ids from the status-box id prefix.
    Builders for live boxes should prefer semantic item ids whenever rows can
    reorder, appear, or disappear.
    """

    items: Sequence[str | MenuItem]
    grid_kwargs: dict = field(default_factory=dict)


StatusBoxBuilder = Callable[["Player", "User"], StatusBoxBuild | Sequence[str | MenuItem]]


@dataclass
class LiveStatusBoxState:
    """Runtime-only state for a player's open live status box."""

    box_id: str
    builder: StatusBoxBuilder


class MenuManagementMixin:
    """Mixin providing menu refresh recording, flushing, and status boxes.

    Expects on the Game class:
        - self._destroyed: bool
        - self.status: str
        - self.players: list[Player]
        - self._status_box_open: set[str]
        - self._actions_menu_open: set[str]
        - self._pending_actions: dict[str, str]
        - self._pending_menu_focus: dict[str, str]
        - self._menu_dirty: set[str]
        - self._menu_dirty_all: bool
        - self._live_status_boxes: dict[str, LiveStatusBoxState]
        - self.get_user(player) -> User | None
        - self.get_all_visible_actions(player) -> list[ResolvedAction]
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        for name in SEALED_MENU_ORCHESTRATORS:
            if name in cls.__dict__:
                raise TypeError(
                    f"{cls.__module__}.{cls.__qualname__} overrides {name}(), "
                    "which is a sealed menu orchestrator.\n"
                    "The flush owns the focus-steal guards (status boxes, "
                    "actions menus, global system menus, pending inputs), "
                    "bot/finished/destroyed handling, and focus delivery. "
                    "Per-game overrides of that logic repeatedly reintroduced "
                    "focus-stealing and menu-clobbering bugs (see CLAUDE.md, "
                    "'Menu Refresh and Focus').\n"
                    "Customize through a sanctioned hook instead:\n"
                    "  - before_menu_build(player): sync dynamic action sets "
                    "before any menu paint\n"
                    "  - build_menu_items(player, user): supply custom "
                    "MenuItem lists / grid layouts\n"
                    "  - request_menu_focus(player, action_id): queue a "
                    "one-shot focus jump for the next flush\n"
                    "See server/game_utils/menu_management_mixin.py for the "
                    "hook contracts."
                )

    # ------------------------------------------------------------------
    # Hooks (override these in games; never the orchestrators below)
    # ------------------------------------------------------------------

    def before_menu_build(self, player: "Player") -> None:
        """Hook: sync dynamic action sets before any menu paint.

        Called at the top of every per-player menu paint, before the
        destroyed/bot/finished early-outs — so action sets are also refreshed
        for bots (whose menus are never rendered but whose action sets drive
        bot decisions). Must be idempotent. Default is a no-op.
        """

    def build_menu_items(self, player: "Player", user: "User") -> MenuBuild:
        """Hook: build the turn-menu items and grid layout for ``player``.

        The default builds one item per visible action, appends the static
        touch-client table controls, and pulls grid kwargs from
        ``_build_grid_menu_kwargs()`` when the game uses ``GridGameMixin``.
        Board games with bespoke grids (backgammon, senet) override this to
        arrange items and grid dimensions themselves.
        """
        items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            items.append(MenuItem(text=resolved.label, id=resolved.action.id))

        # Touch clients get static table controls in the turn menu.
        if is_touch_client(user):
            items.append(MenuItem(
                text=Localization.get(user.locale, "actions-menu"),
                id="web_actions_menu"
            ))
            items.append(MenuItem(
                text=Localization.get(user.locale, "game-leave"),
                id="web_leave_table"
            ))

        grid_kwargs = {}
        if hasattr(self, "_build_grid_menu_kwargs"):
            grid_kwargs = self._build_grid_menu_kwargs()
        return MenuBuild(items=items, grid_kwargs=grid_kwargs)

    # ------------------------------------------------------------------
    # Recording API (what game code calls)
    # ------------------------------------------------------------------

    def refresh_menus(self, player: "Player | None" = None) -> None:
        """Mark ``player`` (or every player) as needing a menu repaint.

        Recording only — nothing is built or sent here. The framework flushes
        at the end of the current ``handle_event()`` and once per server
        tick, so over-marking costs one set insert, never a packet or a
        Fluent render. A repaint without a queued focus intent preserves
        every player's cursor (clients follow item identity), so the safe
        habit — refresh after any state change — is also the cheap habit.
        """
        if player is None:
            self._menu_dirty_all = True
        else:
            self._menu_dirty.add(player.id)

    def request_menu_focus(self, player: "Player", action_id: str) -> None:
        """Queue a one-shot focus jump to ``action_id`` for ``player``.

        The intent is a single per-player slot (the last writer wins) and is
        consumed by the next flush that paints this player, so a delayed
        repaint can never produce a second screen-reader jump. Requesting
        focus marks the player for repaint; no separate ``refresh_menus``
        call is needed unless other players' menus changed too.
        """
        self._pending_menu_focus[player.id] = action_id
        self._menu_dirty.add(player.id)

    # ------------------------------------------------------------------
    # Sealed orchestrators — do not override in games
    # ------------------------------------------------------------------

    def flush_menus(self) -> None:
        """Build and send menus for players marked dirty (sealed).

        Called by the framework only: at the end of every
        ``Game.handle_event()`` and once per server tick (after game ticks,
        before the per-user packet flush). Game code records intent with
        ``refresh_menus()`` / ``request_menu_focus()`` and never flushes.
        """
        if self._destroyed:
            self._menu_dirty.clear()
            self._menu_dirty_all = False
            return

        if self._menu_dirty_all:
            targets = list(self.players)
        elif self._menu_dirty:
            targets = [p for p in self.players if p.id in self._menu_dirty]
        else:
            return
        self._menu_dirty.clear()
        self._menu_dirty_all = False

        for player in targets:
            # The focus intent is used-or-discarded at this flush: it never
            # survives to a later flush where it could fire stale.
            focus = self._pending_menu_focus.pop(player.id, None)
            self._paint_player_menu(player, focus)

    def _is_menu_refresh_blocked(self, player: "Player", user: "User") -> bool:
        """True when painting a turn menu would clobber an open overlay.

        FOCUS-STEAL PREVENTION — three guards, in order:

        1. Action Menu or Status Box (from LobbyActionsMixin and
           MenuManagementMixin).
        2. Server-level system overlay (online_users, friends_hub, options,
           etc.). If _user_states says the user is viewing ANY global system
           menu, never overwrite it with a game turn_menu. Also guard
           transient editbox states (_transient=True) for any game-specific
           editbox not registered in GLOBAL_SYSTEM_MENUS.
        3. Pending action input (action_input_menu, action_input_editbox,
           leave_game_confirm): any pending action implies an open input UI.
        """
        if player.id in self._actions_menu_open or player.id in self._status_box_open:
            return True

        server = getattr(getattr(self, "_table", None), "_server", None)
        if server is not None:
            state = server._user_states.get(user.username, {})
            if state.get("menu") in server.GLOBAL_SYSTEM_MENUS or state.get("_transient"):
                return True

        return bool(self._pending_actions.get(player.id))

    def _paint_player_menu(self, player: "Player", focus: str | None) -> None:
        """Build and send one player's turn menu (sealed; flush-internal).

        Always sends the full show form; clients treat a same-id menu packet
        as an in-place diff that preserves focus by item identity, so this
        never resets a cursor. ``focus`` (an item id) is the player's
        consumed focus intent, delivered as an explicit selection.
        """
        self.before_menu_build(player)

        if self._destroyed:
            return

        if player.is_bot:
            # Bots discard all UI (show_menu is a no-op), so skip building the
            # menu entirely. Otherwise every flush resolves the full action set
            # and renders each label through Fluent for a player that never sees
            # it — a large per-tick cost in bot-heavy games and on the live server.
            return

        if self.status == "finished":
            # A dirty flush on a finished game restores the end screen instead
            # of doing nothing (which would leave the user with no menu).

            # Robustness: If _last_game_result is missing (e.g. after server
            # restart), try to rebuild it from current state.
            if self._last_game_result is None and hasattr(self, "build_game_result"):
                self._last_game_result = self.build_game_result()

            if self._last_game_result and hasattr(self, "_show_end_screen_to_player"):
                self._show_end_screen_to_player(player, self._last_game_result)
            return

        user = self.get_user(player)
        if not user:
            return

        if player.id in self._status_box_open and player.id in self._live_status_boxes:
            self._paint_live_status_box(player, focus_id=None)
            return

        if self._is_menu_refresh_blocked(player, user):
            return

        build = self.build_menu_items(player, user)
        user.show_menu(
            "turn_menu",
            build.items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            selection_id=focus,
            **build.grid_kwargs,
        )

    # ------------------------------------------------------------------
    # Status boxes
    # ------------------------------------------------------------------

    def _normalize_status_box_content(
        self,
        content: StatusBoxBuild | Sequence[str | MenuItem],
        *,
        fallback_id_prefix: str,
    ) -> tuple[list[MenuItem], dict]:
        """Normalize status-box content into uniquely identified menu items."""
        if isinstance(content, StatusBoxBuild):
            raw_items = content.items
            grid_kwargs = dict(content.grid_kwargs)
        else:
            raw_items = content
            grid_kwargs = {}

        items: list[MenuItem] = []
        seen_ids: dict[str, int] = {}
        for index, raw_item in enumerate(raw_items):
            if isinstance(raw_item, MenuItem):
                item = MenuItem(
                    text=raw_item.text,
                    id=raw_item.id or f"{fallback_id_prefix}:line:{index}",
                    sound=raw_item.sound,
                )
            else:
                item = MenuItem(
                    text=str(raw_item),
                    id=f"{fallback_id_prefix}:line:{index}",
                )

            if item.id is not None:
                seen_count = seen_ids.get(item.id, 0)
                seen_ids[item.id] = seen_count + 1
                if seen_count:
                    item.id = f"{item.id}:duplicate:{seen_count}"
            items.append(item)

        return items, grid_kwargs

    def status_box(self, player: "Player", lines: list[str]) -> None:
        """Show a status box (menu with text items) to a player.

        Press Enter on any item to close. No header or close button needed
        since screen readers speak list items and Enter always closes.
        """
        user = self.get_user(player)
        if user:
            self._actions_menu_open.discard(player.id)
            self._live_status_boxes.pop(player.id, None)
            items, grid_kwargs = self._normalize_status_box_content(
                lines,
                fallback_id_prefix="status_box",
            )
            user.show_menu(
                "status_box",
                items,
                multiletter=False,
                escape_behavior=EscapeBehavior.SELECT_LAST,
                **grid_kwargs,
            )
            self._status_box_open.add(player.id)

    def live_status_box(
        self,
        player: "Player",
        box_id: str,
        builder: StatusBoxBuilder,
        *,
        focus_id: str | None = None,
    ) -> None:
        """Open a live status box that refreshes through the sealed menu flush.

        Live boxes are opt-in overlays for dynamic state views such as boards,
        standings, and round status. They use the same ``status_box`` menu id
        so all clients apply the normal same-menu content diff. Passive
        refreshes never send a focus directive; ``focus_id`` is only for the
        initial, action-driven opening.
        """
        user = self.get_user(player)
        if not user:
            return

        self._actions_menu_open.discard(player.id)
        self._live_status_boxes[player.id] = LiveStatusBoxState(
            box_id=box_id,
            builder=builder,
        )
        self._status_box_open.add(player.id)
        self._paint_live_status_box(player, focus_id=focus_id)

    def _paint_live_status_box(
        self,
        player: "Player",
        *,
        focus_id: str | None,
    ) -> None:
        """Repaint one open live status box without changing focus by default."""
        state = self._live_status_boxes.get(player.id)
        user = self.get_user(player)
        if not state or not user:
            return

        content = state.builder(player, user)
        items, grid_kwargs = self._normalize_status_box_content(
            content,
            fallback_id_prefix=f"live_status:{state.box_id}",
        )
        user.show_menu(
            "status_box",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            selection_id=focus_id,
            **grid_kwargs,
        )
