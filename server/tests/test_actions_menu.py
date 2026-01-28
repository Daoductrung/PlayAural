from server.game_utils.actions import Action, ActionSet, Visibility


class DummyGame:
    def _enabled(self, player, *, action_id: str | None = None) -> str | None:
        return None

    def _hidden(self, player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE


class DummyPlayer:
    pass


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
