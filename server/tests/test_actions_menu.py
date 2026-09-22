from ..game_utils.actions import Action, ActionSet, Visibility


class DummyGame:
    def _enabled(self, player, *, action_id: str | None = None) -> str | None:
        return None

    def _hidden(self, player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE


class DummyPlayer:
    is_spectator = False


def test_actions_menu_respects_show_in_actions_menu():
    action_set = ActionSet(name="turn")
    action_set.add(
        Action(
            id="shown",
            label="Shown",
            handler="_action",
            is_enabled="_enabled",
            is_hidden="_hidden",
        )
    )
    action_set.add(
        Action(
            id="hidden",
            label="Hidden",
            handler="_action",
            is_enabled="_enabled",
            is_hidden="_hidden",
            show_in_actions_menu=False,
        )
    )
    game = DummyGame()
    player = DummyPlayer()

    enabled = action_set.get_enabled_actions(game, player)
    assert [ra.action.id for ra in enabled] == ["shown"]


def test_turn_menu_preserves_state_callback_order_and_skips_hidden_presentation():
    calls = []

    class LazyGame:
        def _hidden(self, player, *, action_id: str | None = None):
            calls.append((action_id, "visibility"))
            return Visibility.HIDDEN

        def _enabled(self, player, *, action_id: str | None = None):
            calls.append((action_id, "enabled"))
            return None

        def _label(self, player, action_id: str):
            calls.append((action_id, "label"))
            return "Hidden"

    action_set = ActionSet(name="turn")
    action_set.add(
        Action(
            id="hidden",
            label="",
            handler="_action",
            is_enabled="_enabled",
            is_hidden="_hidden",
            get_label="_label",
        )
    )

    assert action_set.get_visible_actions(LazyGame(), DummyPlayer()) == []
    assert calls == [("hidden", "enabled"), ("hidden", "visibility")]


def test_turn_menu_can_filter_hidden_actions_before_enabled_resolution():
    calls = []

    class LazyGame:
        visibility_first_action_sets = frozenset({"turn"})

        def _hidden(self, player, *, action_id: str | None = None):
            calls.append((action_id, "visibility"))
            return Visibility.HIDDEN

        def _enabled(self, player, *, action_id: str | None = None):
            calls.append((action_id, "enabled"))
            return None

        def _label(self, player, action_id: str):
            calls.append((action_id, "label"))
            return "Hidden"

    action_set = ActionSet(name="turn")
    action_set.add(
        Action(
            id="hidden",
            label="",
            handler="_action",
            is_enabled="_enabled",
            is_hidden="_hidden",
            get_label="_label",
        )
    )

    assert action_set.get_visible_actions(LazyGame(), DummyPlayer()) == []
    assert calls == [("hidden", "visibility")]


def test_turn_menu_keeps_disabled_visible_action_and_resolves_its_label():
    class DisabledGame:
        def _visible(self, player, *, action_id: str | None = None):
            return Visibility.VISIBLE

        def _disabled(self, player, *, action_id: str | None = None):
            return "specific-disabled-reason"

        def _label(self, player, action_id: str):
            return "Persistent control"

    action_set = ActionSet(name="turn")
    action_set.add(
        Action(
            id="persistent",
            label="",
            handler="_action",
            is_enabled="_disabled",
            is_hidden="_visible",
            get_label="_label",
        )
    )

    [resolved] = action_set.get_visible_actions(DisabledGame(), DummyPlayer())
    assert resolved.action.id == "persistent"
    assert resolved.enabled is False
    assert resolved.disabled_reason == "specific-disabled-reason"
    assert resolved.label == "Persistent control"


def test_actions_menu_skips_non_menu_actions_without_resolving_callbacks():
    class StrictGame:
        def _unexpected(self, player, *, action_id: str | None = None):
            raise AssertionError("non-menu action should not be resolved")

    action_set = ActionSet(name="turn")
    action_set.add(
        Action(
            id="turn_only",
            label="Turn only",
            handler="_action",
            is_enabled="_unexpected",
            is_hidden="_unexpected",
            get_label="_unexpected",
            show_in_actions_menu=False,
        )
    )

    assert action_set.get_enabled_actions(StrictGame(), DummyPlayer()) == []


def test_actions_menu_preserves_state_callbacks_but_skips_disabled_presentation():
    calls = []

    class DisabledGame:
        def _disabled(self, player, *, action_id: str | None = None):
            calls.append((action_id, "enabled"))
            return "disabled"

        def _hidden(self, player, *, action_id: str | None = None):
            calls.append((action_id, "visibility"))
            return Visibility.HIDDEN

        def _label(self, player, action_id: str):
            calls.append((action_id, "label"))
            return "Disabled"

    action_set = ActionSet(name="standard")
    action_set.add(
        Action(
            id="disabled",
            label="",
            handler="_action",
            is_enabled="_disabled",
            is_hidden="_hidden",
            get_label="_label",
        )
    )

    assert action_set.get_enabled_actions(DisabledGame(), DummyPlayer()) == []
    assert calls == [("disabled", "enabled"), ("disabled", "visibility")]


def test_shared_action_copy_isolates_collections_but_reuses_definitions():
    source = ActionSet(name="turn")
    shared_action = Action(
        id="shared",
        label="Shared",
        handler="_action",
        is_enabled="_enabled",
        is_hidden="_hidden",
    )
    source.add(shared_action)

    copied = source.copy_shared_actions()
    assert copied is not source
    assert copied._actions is not source._actions
    assert copied._order is not source._order
    assert copied.get_action("shared") is shared_action

    copied.remove("shared")
    assert source.get_action("shared") is shared_action
    assert source._order == ["shared"]

