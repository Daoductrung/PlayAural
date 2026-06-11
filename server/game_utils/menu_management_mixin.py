"""Mixin providing menu management functionality for games.

The menu orchestrators (``rebuild_player_menu``, ``update_player_menu``,
``rebuild_all_menus``, ``update_all_menus``) are **sealed**: games must not
override them. They own the focus-steal guards (status boxes, actions menus,
global system menus, pending inputs), bot/finished/destroyed handling, and
focus scoping. Per-game overrides of these methods repeatedly reintroduced
focus-stealing and menu-clobbering bugs (see CLAUDE.md, "Menu Focus on
Refresh and Turn Transitions").

Games customize menu behavior through these hooks instead:

- ``before_menu_build(player)`` — sync dynamic action sets (e.g. per-card
  play actions) before any menu paint. Runs for bots too, so action sets
  stay valid for bot decision logic.
- ``build_menu_items(player, user)`` — supply custom ``MenuItem`` lists and
  grid layout kwargs (e.g. the backgammon/senet board grids).
- ``request_menu_focus(player, action_id)`` — land the cursor on a specific
  item at the next full-table rebuild.
- ``defer_next_rebuild_to_update()`` — make the next no-focus full rebuild
  focus-preserving (for delayed sequence-runner repaints).
"""

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
    "rebuild_player_menu",
    "update_player_menu",
    "rebuild_all_menus",
    "update_all_menus",
    "_is_menu_refresh_blocked",
)


@dataclass
class MenuBuild:
    """Result of the ``build_menu_items`` hook.

    ``items`` is the full turn-menu item list in display order. ``grid_kwargs``
    holds the grid layout kwargs forwarded to ``show_menu``/``update_menu``
    (``grid_enabled``, ``grid_width``, ``grid_height``), or ``{}`` for a flat
    list menu.
    """

    items: list[MenuItem]
    grid_kwargs: dict = field(default_factory=dict)


class MenuManagementMixin:
    """Mixin providing menu rebuilding and status box functionality.

    Expects on the Game class:
        - self._destroyed: bool
        - self.status: str
        - self.players: list[Player]
        - self._status_box_open: set[str]
        - self._actions_menu_open: set[str]
        - self._pending_actions: dict[str, str]
        - self._pending_menu_focus: dict[str, str]
        - self._next_full_rebuild_is_update: bool
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
                    "The orchestrators own the focus-steal guards (status "
                    "boxes, actions menus, global system menus, pending "
                    "inputs), bot/finished/destroyed handling, and focus "
                    "scoping. Per-game overrides of them repeatedly "
                    "reintroduced focus-stealing and menu-clobbering bugs "
                    "(see CLAUDE.md, 'Menu Focus on Refresh and Turn "
                    "Transitions').\n"
                    "Customize through a sanctioned hook instead:\n"
                    "  - before_menu_build(player): sync dynamic action sets "
                    "before any menu paint\n"
                    "  - build_menu_items(player, user): supply custom "
                    "MenuItem lists / grid layouts\n"
                    "  - request_menu_focus(player, action_id): land focus "
                    "on an item at the next full rebuild\n"
                    "  - defer_next_rebuild_to_update(): keep a delayed full "
                    "repaint focus-preserving\n"
                    "See server/game_utils/menu_management_mixin.py for the "
                    "hook contracts."
                )

    # ------------------------------------------------------------------
    # Hooks (override these in games; never the orchestrators below)
    # ------------------------------------------------------------------

    def before_menu_build(self, player: "Player") -> None:
        """Hook: sync dynamic action sets before any menu paint.

        Called at the very top of every per-player menu refresh, before the
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
    # Focus intent API
    # ------------------------------------------------------------------

    def request_menu_focus(self, player: "Player", action_id: str) -> None:
        """Land the cursor on ``action_id`` at the next full-table rebuild.

        The intent is per-player and used-or-discarded at the next
        ``rebuild_all_menus()`` (including one triggered later by the
        sequence runner): it is consumed at most once, so a delayed repaint
        cannot produce a second screen-reader jump, and an explicit ``focus``
        argument passed to ``rebuild_all_menus`` supersedes it entirely.
        """
        self._pending_menu_focus[player.id] = action_id

    def defer_next_rebuild_to_update(self) -> None:
        """Make the next no-focus ``rebuild_all_menus()`` focus-preserving.

        Use when a delayed flow (e.g. a sequence-runner unlock) will trigger a
        full-table rebuild that should not reset anyone's cursor because the
        interesting focus change already happened. Consumed exactly once, and
        only by a ``rebuild_all_menus()`` call with no focus arguments.
        """
        self._next_full_rebuild_is_update = True

    # ------------------------------------------------------------------
    # Sealed orchestrators — do not override in games
    # ------------------------------------------------------------------

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

    def rebuild_player_menu(self, player: "Player", focus: str | None = None) -> None:
        """Rebuild the turn menu for a player (sealed orchestrator).

        Pass ``focus`` (an item id) to land the cursor on a specific item — e.g.
        a freshly drawn card. With ``focus`` omitted, clients preserve the
        player's current focus by item identity across the refresh.
        """
        self.before_menu_build(player)

        if self._destroyed:
            return  # Don't rebuild menus after game is destroyed

        if player.is_bot:
            # Bots discard all UI (show_menu is a no-op), so skip building the
            # menu entirely. Otherwise every rebuild resolves the full action set
            # and renders each label through Fluent for a player that never sees
            # it — a large per-tick cost in bot-heavy games and on the live server.
            return

        if self.status == "finished":
            # BUGFIX: If game is finished, we should restore the end screen
            # instead of doing nothing (which leaves user with no menu)

            # Robustness: If _last_game_result is missing (e.g. after server restart),
            # try to rebuild it from current state.
            if self._last_game_result is None and hasattr(self, "build_game_result"):
                self._last_game_result = self.build_game_result()

            if self._last_game_result and hasattr(self, "_show_end_screen_to_player"):
                self._show_end_screen_to_player(player, self._last_game_result)
            return

        user = self.get_user(player)
        if not user:
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

    def rebuild_all_menus(
        self,
        focus: str | None = None,
        *,
        focus_player: "Player | None" = None,
    ) -> None:
        """Rebuild menus for all players (sealed orchestrator).

        ``focus`` (an item id) applies to every player that has such an item;
        pass ``focus_player`` to scope it to one player so the others keep
        their current focus anchor. Players without an explicit focus consume
        any pending ``request_menu_focus`` intent.
        """
        if self._destroyed:
            return  # Don't rebuild menus after game is destroyed

        if (
            focus is None
            and focus_player is None
            and self._next_full_rebuild_is_update
        ):
            self._next_full_rebuild_is_update = False
            self.update_all_menus()
            return

        for player in self.players:
            # A pending focus intent is used-or-discarded at every full
            # rebuild: an explicit focus supersedes it, and it never survives
            # to a later rebuild where it could cause a stale cursor jump.
            pending_focus = self._pending_menu_focus.pop(player.id, None)
            player_focus = (
                focus
                if focus is not None
                and (focus_player is None or player == focus_player)
                else None
            )
            if player_focus is None:
                player_focus = pending_focus
            self.rebuild_player_menu(player, focus=player_focus)

    def update_player_menu(
        self, player: "Player", selection_id: str | None = None
    ) -> None:
        """Update the turn menu for a player, preserving focus (sealed)."""
        self.before_menu_build(player)

        if self._destroyed:
            return
        if player.is_bot:
            return  # Bots discard all UI; skip menu resolution + label render.
        if self.status == "finished":
            return
        user = self.get_user(player)
        if not user:
            return

        if self._is_menu_refresh_blocked(player, user):
            return

        build = self.build_menu_items(player, user)
        user.update_menu(
            "turn_menu",
            build.items,
            selection_id=selection_id,
            **build.grid_kwargs,
        )

    def update_all_menus(self) -> None:
        """Update menus for all players, preserving focus (sealed)."""
        if self._destroyed:
            return
        for player in self.players:
            self.update_player_menu(player)

    # ------------------------------------------------------------------
    # Status boxes
    # ------------------------------------------------------------------

    def status_box(self, player: "Player", lines: list[str]) -> None:
        """Show a status box (menu with text items) to a player.

        Press Enter on any item to close. No header or close button needed
        since screen readers speak list items and Enter always closes.
        """
        user = self.get_user(player)
        if user:
            items = [MenuItem(text=line, id="status_line") for line in lines]
            user.show_menu(
                "status_box",
                items,
                multiletter=False,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
            self._status_box_open.add(player.id)
