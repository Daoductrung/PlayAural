"""Rules, accessibility, persistence, and localization tests for Pirates."""

from pathlib import Path
import random
import re
from unittest.mock import patch

from ..games.pirates import bot as bot_ai
from ..games.pirates import combat, skills
from ..games.pirates.combat import CombatResult
from ..games.pirates.game import PiratesGame, PiratesOptions
from ..games.pirates.leveling import get_xp_for_level
from ..games.pirates.player import PiratesPlayer
from ..messages.localization import Localization
from ..users.base import MenuItem
from ..users.test_user import MockUser


LOCALES_DIR = Path(__file__).parent.parent / "locales"
DOCS_DIR = Path(__file__).parent.parent / "documentation" / "content"
Localization.init(LOCALES_DIR)


def make_game(
    player_count: int = 2,
    *,
    start: bool = True,
    bots: bool = False,
    touch_first: bool = False,
    locales: tuple[str, ...] = (),
) -> tuple[PiratesGame, list[PiratesPlayer], list[MockUser]]:
    game = PiratesGame()
    players = []
    users = []
    for index in range(player_count):
        name = chr(ord("A") + index) + "lice" if index == 0 else f"Player{index + 1}"
        locale = locales[index] if index < len(locales) else "en"
        user = MockUser(name, locale=locale, uuid=f"pirates-player-{index + 1}")
        if touch_first and index == 0:
            user.client_type = "mobile"
        player = game.add_player(name, user)
        player.is_bot = bots
        players.append(player)
        users.append(user)
    if start:
        game.on_start()
    return game, players, users


def menu_items(user: MockUser) -> list[MenuItem]:
    return [
        item
        for item in user.get_current_menu_items("action_input_menu") or []
        if isinstance(item, MenuItem)
    ]


def advance_until(game: PiratesGame, predicate, max_ticks: int = 40000) -> bool:
    for _ in range(max_ticks):
        if predicate():
            return True
        game.on_tick()
    return predicate()


def ftl_messages(text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    current = ""
    for line in text.splitlines():
        match = re.match(r"^([a-z0-9-]+)\s*=", line)
        if match:
            current = match.group(1)
            result[current] = set()
        if current:
            result[current].update(
                re.findall(r"\{\s*\$([a-zA-Z_][\w-]*)", line)
            )
    return result


def test_metadata_defaults_and_relevant_preferences() -> None:
    options = PiratesOptions()

    assert PiratesGame.get_min_players() == 2
    assert PiratesGame.get_max_players() == 5
    assert PiratesGame.get_category() == "arcade"
    assert PiratesGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]
    assert options.combat_xp_multiplier == 1.0
    assert options.find_gem_xp_multiplier == 1.0
    assert options.gem_stealing == "with_roll_bonus"
    assert PiratesGame.relevant_preferences == ["brief_announcements"]


def test_prestart_validation_rejects_corrupt_loaded_options() -> None:
    game, _, _ = make_game(start=False)
    game.options.combat_xp_multiplier = 3.1
    game.options.find_gem_xp_multiplier = 0.0
    game.options.gem_stealing = "board_everything"

    keys = {
        error[0] if isinstance(error, tuple) else error
        for error in game.prestart_validate()
    }

    assert "pirates-error-combat-xp-range" in keys
    assert "pirates-error-gem-xp-range" in keys
    assert "pirates-error-stealing-mode" in keys


def test_start_places_gems_and_crews_on_distinct_empty_spaces() -> None:
    game, players, _ = make_game(player_count=5)

    gem_spaces = {
        position for position, gem_type in game.gem_positions.items() if gem_type != -1
    }
    player_spaces = {player.position for player in players}
    assert game.status == "playing"
    assert game.round == 1
    assert len(game.selected_oceans) == 4
    assert len(gem_spaces) == 18
    assert len(player_spaces) == 5
    assert player_spaces.isdisjoint(gem_spaces)
    assert all(game.charted_tiles[position] for position in player_spaces)


def test_pirates_ambience_stem_has_complete_teardown_metadata() -> None:
    game, _, users = make_game()
    ambience = next(
        state
        for state in game.active_audio.values()
        if state.kind == "ambience"
    )

    assert ambience.asset == "game_pirates/amloop.ogg"
    assert ambience.intro == "game_pirates/am_intro.ogg"
    assert ambience.outro == "game_pirates/am_outro.ogg"
    assert ambience.seamless is True

    for user in users:
        user.clear_messages()
    game.stop_all_ambience()

    for user in users:
        packet = user.messages[-1].data
        assert packet["command"] == "stop"
        assert packet["kind"] == "ambience"
        assert packet["all_layers"] is True
        assert packet.get("play_outro", True) is True
        assert packet.get("outro_mode", "immediate") == "immediate"


def test_leveling_threshold_and_golden_moon_multiplier() -> None:
    game, (player, _), _ = make_game()

    assert get_xp_for_level(1) == 20
    assert get_xp_for_level(10) == 200
    player.leveling.give_xp(game, player.name, 25)
    assert (player.level, player.xp) == (1, 25)
    player.leveling.give_xp(game, player.name, 10, golden_moon_multiplier=3.0)
    assert (player.level, player.xp) == (2, 55)


def test_movement_unlocks_return_contextual_disabled_reasons() -> None:
    game, (player, _), _ = make_game()
    player.leveling.level = 0

    assert game._is_move_enabled(player) is None
    assert game._is_move_2_enabled(player) == (
        "pirates-requires-level",
        {"action": "move_2", "current": 0, "required": 15},
    )
    assert game._is_move_3_enabled(player) == (
        "pirates-requires-level",
        {"action": "move_3", "current": 0, "required": 150},
    )
    player.leveling.level = 150
    assert game._is_move_2_enabled(player) is None
    assert game._is_move_3_enabled(player) is None


def test_edge_movement_announces_actual_distance() -> None:
    game, (alice, _), (alice_user, observer_user) = make_game()
    alice.position = 39
    alice.leveling.level = 150
    alice_user.clear_messages()
    observer_user.clear_messages()

    assert game._move_player(alice, 3)

    assert alice.position == 40
    assert "1 space right" in alice_user.get_last_spoken()
    assert "1 space right" in observer_user.get_last_spoken()


def test_sailors_instinct_has_no_blank_items_and_correct_sector_counts() -> None:
    game, (alice, rival), _ = make_game()
    alice.leveling.level = 10
    alice.position = 1
    rival.position = 3
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[2] = 0
    game.gem_positions[4] = 1
    captured: list[str] = []

    with patch.object(game, "status_box", side_effect=lambda _player, lines: captured.extend(lines)):
        assert skills.SAILORS_INSTINCT.do_action(game, alice) == "continue"

    assert len(captured) == 10
    assert all(line.strip() for line in captured)
    assert "positions 1 through 5" in captured[2]
    assert "2 uncollected gems" in captured[2]
    assert "1 rival ship" in captured[2]


def test_skill_menu_uses_stable_nonblank_ids_and_labels() -> None:
    game, (alice, _), _ = make_game()
    alice.leveling.level = 200

    options = game._get_skill_options(alice)
    labels = [game._get_skill_option_label(alice, option) for option in options]

    assert options == [skill.skill_id for skill in skills.ALL_SKILLS]
    assert "cannonball" not in options
    assert len(options) == len(set(options))
    assert all(label.strip() for label in labels)


def test_touch_actions_hidden_while_waiting_and_ordered_during_play() -> None:
    game, (alice, _), _ = make_game(start=False, touch_first=True)
    waiting_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(alice)
    }
    assert "move_left" not in waiting_ids
    assert "cannonball" not in waiting_ids
    assert "use_skill" not in waiting_ids

    game.on_start()
    playing_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(alice)
    }
    assert "check_position" in playing_ids

    standard = game.create_standard_action_set(alice)
    relevant = [
        action_id
        for action_id in standard._order
        if action_id
        in {"check_position", "check_moon", "check_status", "whose_turn", "whos_at_table"}
    ]
    assert relevant == [
        "check_position",
        "check_moon",
        "check_status",
        "whose_turn",
        "whos_at_table",
    ]


def test_cannon_target_menu_uses_player_ids_and_contextual_labels() -> None:
    game, (alice, rival), (alice_user, _) = make_game()
    alice.position = 10
    rival.position = 13
    rival.add_gem(0, 1)
    alice_user.clear_messages()

    game.execute_action(alice, "cannonball")

    items = menu_items(alice_user)
    assert [item.id for item in items] == [rival.id, "_cancel"]
    assert rival.name in items[0].text
    assert "3 spaces away" in items[0].text
    assert "carrying 1 gem" in items[0].text


def test_combat_broadcasts_exactly_one_message_per_listener_role() -> None:
    game, (alice, defender, observer), users = make_game(player_count=3)
    alice.position = 10
    defender.position = 12
    observer.position = 30
    for user in users:
        user.clear_messages()

    with patch.object(combat.random, "randint", side_effect=[1, 6, 1, 1, 100]):
        result = combat.do_attack(game, alice, defender)

    alice_text = "\n".join(users[0].get_spoken_messages())
    defender_text = "\n".join(users[1].get_spoken_messages())
    observer_text = "\n".join(users[2].get_spoken_messages())
    assert result.hit and result.boarding_pending
    assert alice_text.count("You fire a cannonball") == 1
    assert "Direct hit" in alice_text
    assert defender_text.count(f"{alice.name} fires a cannonball at you") == 1
    assert "hits you" in defender_text
    assert observer_text.count(
        f"{alice.name} fires a cannonball at {defender.name}"
    ) == 1
    assert f"hits {defender.name}" in observer_text


def test_boarding_choice_survives_save_and_resolves_turn() -> None:
    game, (alice, defender), _ = make_game()
    alice.position = 10
    defender.position = 12
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.begin_boarding(alice, defender, attack_bonus=2, defense_bonus=1)

    restored = PiratesGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored_alice = restored.get_player_by_id(alice.id)
    restored_defender = restored.get_player_by_id(defender.id)
    restored_alice.reconnect_grace_ticks = 0

    assert restored.pending_boarding_attacker_id == alice.id
    assert restored._get_boarding_options(restored_alice) == [
        "push_left",
        "push_right",
    ]

    def fixed_push(low: int, high: int) -> int:
        return 3 if (low, high) == (3, 8) else low

    with patch.object(combat.random, "randint", side_effect=fixed_push):
        restored.execute_action(restored_alice, "resolve_boarding", "push_right")

    assert restored.pending_boarding_attacker_id == ""
    assert restored_defender.position == 15
    assert restored.current_player.id == defender.id


def test_portal_destination_is_human_selected_and_survives_save() -> None:
    game, (alice, rival), (alice_user, _) = make_game()
    alice.leveling.level = 25
    alice.position = 2
    rival.position = 24
    alice_user.clear_messages()

    assert skills.PORTAL.do_action(game, alice) == "continue"
    assert game.pending_portal_player_id == alice.id
    assert [item.id for item in menu_items(alice_user)] == ["2", "random", "_cancel"]
    assert alice_user.menus["action_input_menu"]["selection_id"] == "2"
    alice_user.clear_messages()
    game.execute_action(alice, "move_right")
    assert game.pending_portal_player_id == alice.id
    assert "locked into that skill" in "\n".join(alice_user.get_spoken_messages())

    restored = PiratesGame.from_json(game.to_json())
    for player in restored.players:
        restored.attach_user(player.id, MockUser(player.name, uuid=player.id))
    restored_alice = restored.get_player_by_id(alice.id)
    restored_alice.reconnect_grace_ticks = 0

    def fixed_portal(low: int, high: int) -> int:
        return 21 if (low, high) == (21, 30) else low

    with patch.object(random, "randint", side_effect=fixed_portal):
        restored.execute_action(restored_alice, "resolve_portal", "2")

    assert restored.pending_portal_player_id == ""
    assert restored_alice.position == 21
    assert restored_alice.skill_cooldowns[skills.PORTAL.skill_id] == 3
    assert restored.current_player.id == rival.id


def test_portal_random_destination_chooses_any_map_position() -> None:
    game, (alice, rival), _ = make_game()
    alice.leveling.level = 25
    alice.position = 2
    rival.position = 34
    game.pending_portal_player_id = alice.id

    def fixed_portal_random(low: int, high: int) -> int:
        return 17 if (low, high) == (1, 40) else low

    with patch.object(random, "randint", side_effect=fixed_portal_random):
        game.execute_action(alice, "resolve_portal", "random")

    assert game.pending_portal_player_id == ""
    assert alice.position == 17
    assert alice.skill_cooldowns[skills.PORTAL.skill_id] == 3
    assert game.current_player.id == rival.id


def test_portal_random_escape_available_without_rival_in_different_ocean() -> None:
    game, (alice, rival), (alice_user, _) = make_game()
    alice.leveling.level = 25
    alice.position = 2
    rival.position = 8

    can_use, reason = skills.PORTAL.can_perform(game, alice)

    assert can_use
    assert reason is None
    assert game._occupied_portal_oceans(alice) == []

    alice_user.clear_messages()
    assert skills.PORTAL.do_action(game, alice) == "continue"
    assert game.pending_portal_player_id == alice.id
    assert [item.id for item in menu_items(alice_user)] == ["random", "_cancel"]
    assert alice_user.menus["action_input_menu"]["selection_id"] == "random"

    def fixed_escape_random(low: int, high: int) -> int:
        return 27 if (low, high) == (1, 40) else low

    with patch.object(random, "randint", side_effect=fixed_escape_random):
        game.execute_action(alice, "resolve_portal", "random")

    assert game.pending_portal_player_id == ""
    assert alice.position == 27
    assert alice.skill_cooldowns[skills.PORTAL.skill_id] == 3


def test_pending_choice_guards_ignore_wrong_player_and_clear_stale_state() -> None:
    game, (alice, rival), (alice_user, rival_user) = make_game()

    game.pending_boarding_attacker_id = alice.id
    game.pending_boarding_defender_id = rival.id
    game._action_resolve_boarding(rival, "push_left", "resolve_boarding")

    assert game.pending_boarding_attacker_id == alice.id
    assert "no pending boarding" in "\n".join(rival_user.get_spoken_messages()).lower()

    game.pending_boarding_defender_id = "missing-defender"
    alice_user.clear_messages()
    game.execute_action(alice, "resolve_boarding")

    assert game.pending_boarding_attacker_id == ""
    assert "no longer has a valid defender" in "\n".join(
        alice_user.get_spoken_messages()
    )

    alice.leveling.level = 25
    alice.position = 2
    rival.position = 24
    game.pending_portal_player_id = alice.id
    game._action_resolve_portal(rival, "2", "resolve_portal")

    assert game.pending_portal_player_id == alice.id

    rival.position = 8
    alice_user.clear_messages()
    game.execute_action(alice, "resolve_portal")

    assert game.pending_portal_player_id == alice.id
    assert [item.id for item in menu_items(alice_user)] == ["random", "_cancel"]


def test_skill_balance_and_incompatibility_rules() -> None:
    game, (alice, _), _ = make_game()
    alice.leveling.level = 200

    assert skills.SWORD_FIGHTER.attack_bonus == 2
    assert skills.SWORD_FIGHTER.duration == 3
    assert skills.PUSH.push_bonus == 2
    assert skills.PUSH.duration == 3
    assert skills.SKILLED_CAPTAIN.attack_bonus == 1
    assert skills.SKILLED_CAPTAIN.defense_bonus == 1
    assert skills.BATTLESHIP.max_cooldown == 4

    assert skills.SWORD_FIGHTER.do_action(game, alice) == "continue"
    assert game.current_player is alice
    assert skills.get_attack_bonus(alice) == 2
    assert skills.get_defense_bonus(alice) == 0
    alice.skill_activated_this_turn = False
    allowed, reason = skills.SKILLED_CAPTAIN.can_perform(game, alice)
    assert not allowed
    assert "Sword Fighter" in reason


def test_battleship_shots_never_open_boarding() -> None:
    game, (alice, rival), _ = make_game()
    alice.leveling.level = 125
    alice.position = 10
    rival.position = 12
    result = CombatResult(False, 1, 6, 0, 0, 50)

    with (
        patch.object(bot_ai, "bot_select_target", return_value=rival),
        patch.object(combat, "do_attack", return_value=result) as do_attack,
    ):
        assert skills.BATTLESHIP.do_action(game, alice) == "end_turn"

    assert do_attack.call_count == 2
    assert all(call.kwargs["allow_boarding"] is False for call in do_attack.call_args_list)
    assert all(call.kwargs["announce_fire"] is False for call in do_attack.call_args_list)
    assert game.pending_boarding_attacker_id == ""
    assert alice.skill_cooldowns[skills.BATTLESHIP.skill_id] == 4


def test_nonboarding_hit_has_contextual_outcome_without_fire_duplication() -> None:
    game, (alice, defender), (alice_user, defender_user) = make_game()
    alice.position = 10
    defender.position = 12
    alice_user.clear_messages()
    defender_user.clear_messages()

    with patch.object(combat.random, "randint", side_effect=[1, 6, 1, 1, 100]):
        result = combat.do_attack(
            game,
            alice,
            defender,
            allow_boarding=False,
            announce_fire=False,
        )

    assert result.hit and not result.boarding_pending
    assert game.pending_boarding_attacker_id == ""
    assert not any("fire a cannonball" in text for text in alice_user.get_spoken_messages())
    assert "grants XP but no boarding action" in "\n".join(
        alice_user.get_spoken_messages()
    )
    assert "do not grant boarding actions" in "\n".join(
        defender_user.get_spoken_messages()
    )


def test_rammed_ship_collects_gem_on_forced_landing() -> None:
    game, (alice, defender), _ = make_game()
    alice.position = 2
    defender.position = 5
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[8] = 0
    game.total_gems = 1

    with patch.object(combat.random, "randint", return_value=3):
        combat.push_defender(game, alice, defender, "right")

    assert defender.position == 8
    assert defender.gems == [0]
    assert defender.score == 1
    assert game.total_gems == 0


def test_tied_high_scores_share_victory_and_result_ids() -> None:
    game, (alice, rival), _ = make_game()
    alice.score = 4
    rival.score = 4
    game.total_gems = 0

    game._end_game()
    result = game.build_game_result()

    assert game.status == "finished"
    assert game.winner_ids == [alice.id, rival.id]
    assert result.custom_data["winner_name"] is None
    assert result.custom_data["winner_ids"] == [alice.id, rival.id]
    score_lines = game.format_end_screen(result, "en")
    assert score_lines[1].startswith("1.")
    assert score_lines[2].startswith("1.")


def test_brief_announcements_are_per_listener_and_keep_perspective() -> None:
    game, (alice, _), (alice_user, observer_user) = make_game()
    alice.position = 10
    observer_user.preferences.set_game_override(
        "brief_announcements", "pirates", True
    )
    alice_user.clear_messages()
    observer_user.clear_messages()

    game._move_player(alice, 1)

    assert alice_user.get_last_spoken().startswith("You sail 1 space")
    assert observer_user.get_last_spoken() == f"{alice.name} sails to position 11."


def test_locale_key_and_variable_parity_and_required_rendering() -> None:
    en_text = (LOCALES_DIR / "en" / "pirates.ftl").read_text(encoding="utf-8")
    vi_text = (LOCALES_DIR / "vi" / "pirates.ftl").read_text(encoding="utf-8")

    assert ftl_messages(en_text) == ftl_messages(vi_text)
    required_keys = {
        "pirates-turn-you",
        "pirates-turn",
        "pirates-attack-hit-you",
        "pirates-attack-hit-them",
        "pirates-attack-hit",
        "pirates-portal-success-you",
        "pirates-portal-success",
        "pirates-option-changed-combat-xp",
        "pirates-option-changed-find-gem-xp",
    }
    assert required_keys <= ftl_messages(en_text).keys()
    assert Localization.get(
        "vi",
        "pirates-requires-level",
        action="move_2",
        current=4,
        required=15,
    ) != "pirates-requires-level"


def test_vietnamese_documentation_matches_localized_nautical_terms() -> None:
    doc = (DOCS_DIR / "vi" / "games" / "pirates.md").read_text(encoding="utf-8")

    for term in (
        "Hải Tặc: Những Vùng Biển Thất Lạc",
        "ô biển",
        "áp mạn",
        "Trực Giác Thủy Thủ",
        "Tốc Độ Húc Mạn",
        "Thuyền Trưởng Lão Luyện",
        "Hỏa Lực Tầm Xa",
    ):
        assert term in doc
    assert "+2 tấn công" in doc
    assert "Hồi phục: 4 lượt" in doc


def test_bot_collects_nearby_gem_instead_of_low_value_attack() -> None:
    game, (alice, rival), _ = make_game()
    alice.is_bot = True
    alice.position = 10
    rival.position = 12
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[11] = 17
    game.total_gems = 1

    assert bot_ai.bot_think(game, alice) == "move_right"
    assert game._bot_decision.direction == "right"
    assert game._bot_decision.target is None


def test_bot_activates_sword_before_high_value_boarding_attack() -> None:
    game, (alice, rival), _ = make_game()
    alice.is_bot = True
    alice.leveling.level = 60
    alice.position = 10
    rival.position = 12
    rival.gems = [17]
    rival.score = 3
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[30] = 0
    game.total_gems = 1

    assert bot_ai.bot_think(game, alice) == "use_skill"
    assert game._bot_decision.skill_name == skills.SWORD_FIGHTER.skill_id
    assert game._bot_decision.target is rival


def test_bot_uses_double_devastation_for_out_of_range_gem_leader() -> None:
    game, (alice, rival), _ = make_game()
    alice.is_bot = True
    alice.leveling.level = 200
    alice.position = 10
    rival.position = 18
    rival.gems = [17, 6]
    rival.score = 5
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[1] = 0
    game.total_gems = 1

    assert bot_ai.bot_think(game, alice) == "use_skill"
    assert game._bot_decision.skill_name == skills.DOUBLE_DEVASTATION.skill_id
    assert game._bot_decision.target is rival


def test_bot_uses_random_portal_escape_when_carrying_gems_under_threat() -> None:
    game, (alice, threat, distant), _ = make_game(player_count=3)
    alice.is_bot = True
    alice.leveling.level = 25
    alice.position = 10
    alice.add_gem(17, 3)
    alice.add_gem(6, 2)
    threat.position = 12
    distant.position = 25
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[35] = 0
    game.total_gems = 1

    assert bot_ai.bot_think(game, alice) == "use_skill"
    assert game._bot_decision.skill_name == skills.PORTAL.skill_id
    assert game._bot_decision.portal_random

    game.pending_portal_player_id = alice.id
    assert game._bot_select_portal_ocean(alice, ["2", "random"]) == "random"


def test_bot_boarding_steals_high_value_gems_and_pushes_away_from_treasure() -> None:
    game, (alice, rival), _ = make_game()
    alice.is_bot = True
    rival.gems = [17, 6]
    rival.score = 5

    assert bot_ai.bot_select_boarding_action(game, alice, rival, True) == "steal"

    rival.gems = []
    rival.score = 0
    rival.position = 10
    game.gem_positions = {position: -1 for position in range(1, 41)}
    game.gem_positions[18] = 17
    game.total_gems = 1

    assert bot_ai.bot_select_boarding_action(game, alice, rival, False) == "left"


def test_two_bot_game_completes() -> None:
    random.seed(20260620)
    game, _, _ = make_game(bots=True)

    assert advance_until(game, lambda: game.status == "finished")
    assert game.winner_ids
    assert game.total_gems == 0
