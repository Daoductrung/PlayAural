"""Tests for the MultiSelectOption declarative option engine and its handlers.

Covers the path-aware renderer (top level / group level / toggle level), the
navigation handlers (open, group-open, toggle, select-all, deselect-all, back
with min/max validation), and an end-to-end drive through Cards Against
Humanity's card_packs option using the real action-execution path.
"""

from dataclasses import dataclass
from pathlib import Path

from ..game_utils.options import (
    GameOptions,
    IntOption,
    MultiSelectOption,
    get_option_meta,
    multi_select_field,
    option_field,
)
from ..games.humanitycards.game import HumanityCardsGame, get_pack_groups
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


# ---------------------------------------------------------------------------
# A tiny game-like harness for engine-level (renderer) tests.
# ---------------------------------------------------------------------------


@dataclass
class _DemoOptions(GameOptions):
    packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=["standard"],
            choices=["standard", "premium", "classic"],
            label="opt-packs",
            change_msg="opt-packs-change",
            min_selected=1,
            show_bulk_actions=True,
        )
    )
    other_option: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=10,
            label="opt-other",
            prompt="opt-other-prompt",
            change_msg="opt-other-change",
        )
    )


@dataclass
class _GroupedOptions(GameOptions):
    packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=["a"],
            choices=["a", "b", "c", "d"],
            label="opt-packs",
            change_msg="opt-packs-change",
            min_selected=1,
            show_bulk_actions=True,
            groups={"First": ["a", "b"], "Second": ["c", "d"]},
        )
    )


class _DemoGame:
    """Minimal stand-in exposing only what the renderer touches."""

    def __init__(self, options):
        self.options = options
        self._user = MockUser("Alice")
        player = type("P", (), {"id": "p1", "name": "Alice"})()
        self.players = [player]
        self.player = player
        self._options_path: dict[str, list[str]] = {}

    def get_user(self, player):
        return self._user


def _build(options):
    game = _DemoGame(options)
    return game, game.player


# ---------------------------------------------------------------------------
# Field defaults
# ---------------------------------------------------------------------------


def test_multi_select_default_value():
    assert _DemoOptions().packs == ["standard"]


def test_multi_select_default_is_independent_copy():
    o1, o2 = _DemoOptions(), _DemoOptions()
    o1.packs.append("premium")
    assert o2.packs == ["standard"]


def test_multi_select_option_meta_accessible():
    meta = get_option_meta(_DemoOptions, "packs")
    assert isinstance(meta, MultiSelectOption)
    assert meta.min_selected == 1
    assert meta.get_choices() == ["standard", "premium", "classic"]


# ---------------------------------------------------------------------------
# Renderer: top level
# ---------------------------------------------------------------------------


def test_top_level_shows_parent_action():
    options = _DemoOptions()
    game, player = _build(options)
    action_set = options.create_options_action_set(game, player)
    assert action_set.get_action("multiselect_packs") is not None
    # Other options render normally alongside.
    assert action_set.get_action("set_other_option") is not None
    # No toggles or back at top level.
    assert action_set.get_action("mstoggle_packs_standard") is None
    assert action_set.get_action("options_back") is None


# ---------------------------------------------------------------------------
# Renderer: ungrouped toggle level
# ---------------------------------------------------------------------------


def test_navigate_in_shows_toggles_and_bulk_and_back():
    options = _DemoOptions()
    game, player = _build(options)
    game._options_path[player.id] = ["packs"]
    action_set = options.create_options_action_set(game, player)

    assert action_set.get_action("mstoggle_packs_standard") is not None
    assert action_set.get_action("mstoggle_packs_premium") is not None
    assert action_set.get_action("mstoggle_packs_classic") is not None
    assert action_set.get_action("mselectall_packs") is not None
    assert action_set.get_action("mdeselectall_packs") is not None
    assert action_set.get_action("options_back") is not None
    # Parent action and unrelated options are suppressed inside the sub-menu.
    assert action_set.get_action("multiselect_packs") is None
    assert action_set.get_action("set_other_option") is None


def test_toggle_labels_reflect_selection():
    options = _DemoOptions()
    options.packs = ["standard", "premium"]
    game, player = _build(options)
    game._options_path[player.id] = ["packs"]
    action_set = options.create_options_action_set(game, player)

    on = Localization.get("en", "option-on")
    off = Localization.get("en", "option-off")
    assert action_set.get_action("mstoggle_packs_standard").label.endswith(on)
    assert action_set.get_action("mstoggle_packs_premium").label.endswith(on)
    assert action_set.get_action("mstoggle_packs_classic").label.endswith(off)


# ---------------------------------------------------------------------------
# Renderer: grouped
# ---------------------------------------------------------------------------


def test_grouped_top_level_shows_group_openers():
    options = _GroupedOptions()
    game, player = _build(options)
    game._options_path[player.id] = ["packs"]
    action_set = options.create_options_action_set(game, player)

    assert action_set.get_action("msgroup_packs_First") is not None
    assert action_set.get_action("msgroup_packs_Second") is not None
    # Individual toggles are not shown at the group-selection level.
    assert action_set.get_action("mstoggle_packs_a") is None
    assert action_set.get_action("options_back") is not None


def test_grouped_inside_group_shows_only_that_group_toggles():
    options = _GroupedOptions()
    game, player = _build(options)
    game._options_path[player.id] = ["packs", "group:First"]
    action_set = options.create_options_action_set(game, player)

    assert action_set.get_action("mstoggle_packs_a") is not None
    assert action_set.get_action("mstoggle_packs_b") is not None
    assert action_set.get_action("mstoggle_packs_c") is None
    assert action_set.get_action("mstoggle_packs_d") is None
    assert action_set.get_action("options_back") is not None


# ---------------------------------------------------------------------------
# Functional end-to-end through Cards Against Humanity.
# ---------------------------------------------------------------------------


def _make_cah(locale: str = "en"):
    game = HumanityCardsGame()
    host = MockUser("Host")
    host._locale = locale
    player = game.add_player("Host", host)
    game.host = "Host"          # option actions are host-only
    game.status = "waiting"
    game.setup_player_actions(player)
    return game, host, player


def test_cah_default_packs_are_base_set():
    game, _, _ = _make_cah()
    base_set = get_pack_groups()["Base Set"]
    assert game.options.card_packs == base_set
    assert game._get_active_packs() == base_set


def test_cah_open_toggle_and_active_packs_update():
    game, _, player = _make_cah()

    # Open the multi-select sub-menu.
    game.execute_action(player, "multiselect_card_packs")
    assert game._options_path[player.id] == ["card_packs"]

    # Open a group, then toggle a pack inside it on.
    game.execute_action(player, "msgroup_card_packs_Holiday Packs")
    assert game._options_path[player.id][-1] == "group:Holiday Packs"

    holiday = get_pack_groups()["Holiday Packs"]
    target = holiday[0]
    assert target not in game.options.card_packs
    game.execute_action(player, f"mstoggle_card_packs_{target}")
    assert target in game.options.card_packs
    assert target in game._get_active_packs()

    # Toggle it back off.
    game.execute_action(player, f"mstoggle_card_packs_{target}")
    assert target not in game.options.card_packs


def test_cah_select_all_then_deselect_all_scoped_to_group():
    game, _, player = _make_cah()
    game.execute_action(player, "multiselect_card_packs")
    game.execute_action(player, "msgroup_card_packs_Holiday Packs")

    holiday = set(get_pack_groups()["Holiday Packs"])
    game.execute_action(player, "mselectall_card_packs")
    assert holiday.issubset(set(game.options.card_packs))

    game.execute_action(player, "mdeselectall_card_packs")
    assert holiday.isdisjoint(set(game.options.card_packs))


def test_cah_back_refused_when_below_min_selected():
    game, _, player = _make_cah()
    game.execute_action(player, "multiselect_card_packs")  # path: [card_packs]

    # Clear every selection by deselecting all inside the "All Packs" group
    # (which contains every pack), then return to the group-selection level.
    game.execute_action(player, "msgroup_card_packs_All Packs")
    game.execute_action(player, "mdeselectall_card_packs")
    assert game.options.card_packs == []
    game.execute_action(player, "options_back")  # pop the group → [card_packs]
    assert game._options_path[player.id] == ["card_packs"]

    # Back from the option level must be refused (min_selected=1); path stays.
    game.execute_action(player, "options_back")
    assert game._options_path[player.id] == ["card_packs"]

    # Re-select one pack inside a group; now back succeeds and pops to top level.
    base = get_pack_groups()["Base Set"][0]
    game.execute_action(player, "msgroup_card_packs_Base Set")
    game.execute_action(player, f"mstoggle_card_packs_{base}")
    game.execute_action(player, "options_back")  # pop group → [card_packs]
    game.execute_action(player, "options_back")  # pop option → []
    assert game._options_path[player.id] == []
