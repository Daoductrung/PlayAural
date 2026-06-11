"""Tests for the sealed menu orchestrators and focus-intent APIs.

The menu orchestrators in MenuManagementMixin are sealed: a game subclass
that overrides one must fail loudly at class-creation (i.e. import) time
with a message that names the offender and points at the sanctioned hooks.
These tests pin that contract, plus the semantics of the focus-intent APIs
that replaced the per-game plumbing (sorry's pending-focus dict and
deadmanspoker's deferred-refresh flag).
"""

from pathlib import Path

import pytest

from ..game_utils.menu_management_mixin import SEALED_MENU_ORCHESTRATORS
from ..games.pig.game import PigGame
from ..messages.localization import Localization
from ..users.test_user import MockUser

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(player_count: int = 2) -> PigGame:
    game = PigGame()
    game.setup_keybinds()
    for index in range(player_count):
        user = MockUser(f"Player{index + 1}", uuid=f"p{index + 1}")
        game.add_player(f"Player{index + 1}", user)
    game.host = "Player1"
    return game


def turn_menu_messages(user: MockUser) -> list:
    return [
        m
        for m in user.messages
        if m.type in ("show_menu", "update_menu")
        and m.data.get("menu_id") == "turn_menu"
    ]


class TestSealedOrchestrators:
    @pytest.mark.parametrize("name", SEALED_MENU_ORCHESTRATORS)
    def test_override_raises_at_class_creation(self, name: str) -> None:
        with pytest.raises(TypeError) as excinfo:
            type("BadGame", (PigGame,), {name: lambda self, *a, **k: None})
        message = str(excinfo.value)
        assert "BadGame" in message
        assert name in message
        assert "sealed menu orchestrator" in message
        # The error must guide toward the fix, not just forbid.
        assert "before_menu_build" in message
        assert "build_menu_items" in message

    def test_hook_overrides_are_allowed(self) -> None:
        cls = type(
            "GoodGame",
            (PigGame,),
            {
                "before_menu_build": lambda self, player: None,
                "build_menu_items": lambda self, player, user: None,
            },
        )
        assert issubclass(cls, PigGame)


class TestFocusIntent:
    def test_request_menu_focus_lands_once_and_only_for_target(self) -> None:
        game = make_game()
        p1, p2 = game.players
        user1 = game.get_user(p1)
        user2 = game.get_user(p2)

        game.request_menu_focus(p1, "some_item")
        game.rebuild_all_menus()
        assert turn_menu_messages(user1)[-1].data["selection_id"] == "some_item"
        assert turn_menu_messages(user2)[-1].data["selection_id"] is None

        # Consumed: the next rebuild must not jump the cursor again.
        game.rebuild_all_menus()
        assert turn_menu_messages(user1)[-1].data["selection_id"] is None

    def test_explicit_focus_supersedes_pending_intent(self) -> None:
        game = make_game()
        p1 = game.players[0]
        user1 = game.get_user(p1)

        game.request_menu_focus(p1, "stale_item")
        game.rebuild_all_menus(focus="fresh_item", focus_player=p1)
        assert turn_menu_messages(user1)[-1].data["selection_id"] == "fresh_item"

        # The superseded intent is discarded, not deferred to fire stale.
        game.rebuild_all_menus()
        assert turn_menu_messages(user1)[-1].data["selection_id"] is None

    def test_focus_player_scopes_explicit_focus(self) -> None:
        game = make_game()
        p1, p2 = game.players
        user1 = game.get_user(p1)
        user2 = game.get_user(p2)

        game.rebuild_all_menus(focus="target_item", focus_player=p1)
        assert turn_menu_messages(user1)[-1].data["selection_id"] == "target_item"
        assert turn_menu_messages(user2)[-1].data["selection_id"] is None


class TestDeferredRebuild:
    def test_next_plain_rebuild_becomes_update(self) -> None:
        game = make_game()
        user1 = game.get_user(game.players[0])
        # Establish a painted menu so updates are meaningful.
        game.rebuild_all_menus()

        game.defer_next_rebuild_to_update()
        game.rebuild_all_menus()
        assert turn_menu_messages(user1)[-1].type == "update_menu"

        # Consumed: the rebuild after that is a real rebuild again.
        game.rebuild_all_menus()
        assert turn_menu_messages(user1)[-1].type == "show_menu"

    def test_focused_rebuild_is_not_deferred(self) -> None:
        game = make_game()
        p1 = game.players[0]
        user1 = game.get_user(p1)
        game.rebuild_all_menus()

        game.defer_next_rebuild_to_update()
        game.rebuild_all_menus(focus="some_item", focus_player=p1)
        last = turn_menu_messages(user1)[-1]
        assert last.type == "show_menu"
        assert last.data["selection_id"] == "some_item"
