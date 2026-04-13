"""Tests for Battle."""

from pathlib import Path
import random

from ..games.battle.game import (
    BattleGame,
    BattleOptions,
    DIFFICULTY_PROFESSIONAL,
    MODE_CLASSIC_ARENA,
    MODE_FREE_FOR_ALL,
    MODE_CLASSIC_SURVIVAL,
    MODE_CLASSIC_WAVES,
    MODE_ONE_EACH,
    MODE_TWO_EACH,
    PHASE_COMBAT,
    PHASE_SELECTION,
    TURN_MODE_ROUND_ROBIN,
)
from ..games.battle.content import get_move_map, load_battle_registry
from ..game_utils.stats_extractor import StatsExtractor
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 2,
    start: bool = False,
    bot_all: bool = False,
    web_first: bool = False,
    **option_overrides,
) -> BattleGame:
    game = BattleGame(options=BattleOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if web_first and index == 0:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def advance_until(game: BattleGame, condition, max_ticks: int = 400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def select_and_submit(game: BattleGame, player, *preset_ids: str) -> None:
    for preset_id in preset_ids:
        game.execute_action(player, f"battle_toggle_preset_{preset_id}")
    game.execute_action(player, "battle_submit_selection")


def test_game_registered_and_defaults() -> None:
    assert GameRegistry.get("battle") is BattleGame
    game = BattleGame()
    assert game.get_name() == "Battle"
    assert game.get_type() == "battle"
    assert game.get_min_players() == 1
    assert game.get_max_players() == 6
    assert game.get_supported_leaderboards() == ["games_played"]
    leaderboard_ids = [entry["id"] for entry in game.get_leaderboard_types()]
    assert leaderboard_ids == ["most_enemies_defeated", "deepest_wave_reached"]
    assert game.options.game_mode == MODE_ONE_EACH
    assert game.options.unlimited_selection_limit == 3


def test_prestart_validation_checks_mode_and_survival_conflicts() -> None:
    game = make_game(player_count=1, game_mode=MODE_TWO_EACH)
    errors = game.prestart_validate()
    assert any(error == "battle-error-mode-min-players" or (isinstance(error, tuple) and error[0] == "battle-error-mode-min-players") for error in errors)

    game = make_game(player_count=2, game_mode=MODE_ONE_EACH, survival_target=5)
    assert "battle-error-survival-target-mode" in game.prestart_validate()


def test_on_start_enters_selection_phase() -> None:
    game = make_game(start=True)
    assert game.status == "playing"
    assert game.phase == PHASE_SELECTION
    assert game.current_music == "battle/fightmus.ogg"
    assert game.current_ambience == "battle/crowds/ambience_reserves_selections.ogg"


def test_pregame_options_take_effect_in_combat() -> None:
    balanced_game = make_game(start=True, balance_mode=True)
    balanced_game.players[0].selected_preset_ids = ["boxer"]
    balanced_game.players[1].selected_preset_ids = ["novice_boxer"]
    balanced_game.players[0].selection_locked = True
    balanced_game.players[1].selection_locked = True
    assert advance_until(balanced_game, lambda: balanced_game.phase == PHASE_COMBAT and balanced_game.current_fighter is not None, max_ticks=200)
    assert balanced_game.fighters[0].attack == 0
    assert balanced_game.fighters[0].defense == 0
    assert balanced_game.fighters[0].health == 50
    assert balanced_game.fighters[0].speed == 100

    arena_game = make_game(
        player_count=1,
        start=True,
        game_mode=MODE_CLASSIC_ARENA,
        classic_enemy_preset="fighter_plane",
        arena_difficulty=DIFFICULTY_PROFESSIONAL,
    )
    select_and_submit(arena_game, arena_game.players[0], "novice_boxer")
    assert advance_until(arena_game, lambda: arena_game.phase == PHASE_COMBAT and arena_game.current_fighter is not None, max_ticks=200)
    enemy = next(fighter for fighter in arena_game.fighters if fighter.is_arena_enemy)
    assert enemy.base_name.en == "Fighter Plane"
    assert enemy.health == 130
    assert enemy.attack == 4
    assert enemy.defense == 3
    assert enemy.speed == 130

    round_robin_game = make_game(start=True, turn_mode=TURN_MODE_ROUND_ROBIN)
    select_and_submit(round_robin_game, round_robin_game.players[0], "novice_boxer")
    select_and_submit(round_robin_game, round_robin_game.players[1], "boxer")
    assert advance_until(round_robin_game, lambda: round_robin_game.phase == PHASE_COMBAT and round_robin_game.current_fighter is not None, max_ticks=200)
    assert round_robin_game.current_fighter == round_robin_game.fighters[0]

    heal_game = make_game(start=True, game_mode=MODE_CLASSIC_SURVIVAL, survival_heal_percent=25)
    heal_game.players[0].selected_preset_ids = ["novice_boxer"]
    heal_game.players[1].selected_preset_ids = ["boxer"]
    heal_game.players[0].selection_locked = True
    heal_game.players[1].selection_locked = True
    assert advance_until(heal_game, lambda: heal_game.phase == PHASE_COMBAT and len(heal_game.fighters) >= 4, max_ticks=200)
    ally = next(fighter for fighter in heal_game.fighters if not fighter.is_arena_enemy)
    ally.health = max(1, ally.health - 20)
    heal_game._heal_players_between_waves()
    assert ally.health == ally.max_health - 8

    target_game = make_game(start=True, game_mode=MODE_CLASSIC_SURVIVAL, survival_target=1)
    target_game.players[0].selected_preset_ids = ["novice_boxer"]
    target_game.players[1].selected_preset_ids = ["boxer"]
    target_game.players[0].selection_locked = True
    target_game.players[1].selection_locked = True
    assert advance_until(target_game, lambda: target_game.phase == PHASE_COMBAT and target_game.current_fighter is not None, max_ticks=200)
    target_game.survival_kills = 1
    assert target_game._check_for_winner() is True
    assert target_game.winning_team_id == "ally"


def test_unlimited_selection_limit_is_enforced() -> None:
    game = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL, unlimited_selection_limit=2)
    player = game.players[0]

    game.execute_action(player, "battle_toggle_preset_novice_boxer")
    game.execute_action(player, "battle_toggle_preset_boxer")
    game.execute_action(player, "battle_toggle_preset_master_mage")

    assert player.selected_preset_ids == ["novice_boxer", "boxer"]


def test_selection_uses_checklist_with_submit_at_bottom() -> None:
    game = make_game(start=True)
    player = game.players[0]

    turn_set = game.get_action_set(player, "turn")
    assert turn_set is not None
    visible = turn_set.get_visible_actions(game, player)
    action_ids = [entry.action.id for entry in visible]
    assert action_ids[0].startswith("battle_toggle_preset_")
    assert action_ids[-1] == "battle_submit_selection"
    assert visible[0].label.startswith("Not selected:")

    game.execute_action(player, "battle_toggle_preset_novice_boxer")

    visible = turn_set.get_visible_actions(game, player)
    selected_label = next(entry.label for entry in visible if entry.action.id == "battle_toggle_preset_novice_boxer")
    assert selected_label.startswith("Selected:")
    assert visible[-1].action.id == "battle_submit_selection"


def test_selection_advances_into_combat() -> None:
    game = make_game(start=True)
    p1, p2 = game.players

    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")

    assert p1.selection_locked is True
    assert p2.selection_locked is True
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)
    assert game.phase == PHASE_COMBAT
    assert game.current_fighter is not None
    assert len(game.fighters) == 2


def test_selection_announces_fighter_and_uses_appear_sound() -> None:
    random.seed(10)
    game = make_game(start=True)
    p1 = game.players[0]

    select_and_submit(game, p1, "novice_boxer")

    spoken = game.get_user(p1).get_spoken_messages()
    sounds = game.get_user(p1).get_sounds_played()
    assert any("Player1 selected Novice Boxer." == message for message in spoken)
    assert any(sound.startswith("battle/appear") for sound in sounds)


def test_bot_selection_announces_choices_to_room() -> None:
    random.seed(2)
    game = make_game(start=False)
    bot_player = game.players[1]
    bot_player.is_bot = True
    game.attach_user(bot_player.id, Bot(bot_player.name, uuid=bot_player.id))

    game.on_start()

    human_user = game.get_user(game.players[0])
    spoken = human_user.get_spoken_messages()
    assert any("Player2 selected" in message for message in spoken)
    assert any("Player2 is ready." == message for message in spoken)


def test_single_team_selection_finishes_without_hanging() -> None:
    game = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL)
    p1 = game.players[0]

    select_and_submit(game, p1, "novice_boxer")

    assert advance_until(game, lambda: game.status == "finished", max_ticks=200)
    assert any("no fight can happen" in message for message in game.get_user(p1).get_spoken_messages())


def test_vampiric_bite_uses_true_drain() -> None:
    game = make_game(start=True)
    p1, p2 = game.players
    p1.selected_preset_ids = ["the_alpha_wolf"]
    p2.selected_preset_ids = ["novice_boxer"]
    p1.selection_locked = True
    p2.selection_locked = True
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    attacker = game.fighters[0]
    defender = game.fighters[1]
    battle_move = get_move_map()["vampiric_bite"]

    attacker.health = max(1, attacker.health - 10)
    before = attacker.health
    game._apply_block(attacker, defender, battle_move.blocks[0])
    assert attacker.health >= before
    assert defender.health < defender.max_health


def test_survival_mode_spawns_enemies() -> None:
    game = make_game(start=True, game_mode=MODE_CLASSIC_SURVIVAL)
    p1, p2 = game.players
    p1.selected_preset_ids = ["novice_boxer"]
    p2.selected_preset_ids = ["boxer"]
    p1.selection_locked = True
    p2.selection_locked = True
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and len(game.fighters) >= 4, max_ticks=200)
    assert any(fighter.is_arena_enemy for fighter in game.fighters)


def test_target_selection_uses_action_input_menu() -> None:
    game = make_game(start=True, game_mode=MODE_TWO_EACH, turn_mode=TURN_MODE_ROUND_ROBIN)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer", "boxer")
    select_and_submit(game, p2, "master_mage", "the_alpha_wolf")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    fighter = game.current_fighter
    assert fighter is not None
    move_id = next(move_id for move_id in fighter.move_ids if len(game._valid_targets(fighter, get_move_map()[move_id])) > 1)
    game.execute_action(p1, f"battle_move_{move_id}")

    menu = game.get_user(p1).menus["action_input_menu"]
    items = menu["items"]
    assert items[0].id != "_cancel"
    assert "health" in items[0].text
    assert game._pending_actions[p1.id] == f"battle_move_{move_id}"


def test_touch_info_actions_visible() -> None:
    waiting_game = make_game(web_first=True)
    waiting_actions = {entry.action.id for entry in waiting_game.get_all_visible_actions(waiting_game.players[0])}
    assert "whos_at_table" in waiting_actions

    active_game = make_game(web_first=True, start=True)
    active_game.players[0].selected_preset_ids = ["novice_boxer"]
    active_game.players[1].selected_preset_ids = ["boxer"]
    active_game.players[0].selection_locked = True
    active_game.players[1].selection_locked = True
    assert advance_until(active_game, lambda: active_game.phase == PHASE_COMBAT and active_game.current_fighter is not None, max_ticks=200)
    active_actions = {entry.action.id for entry in active_game.get_all_visible_actions(active_game.players[0])}
    assert "battle_read_status" in active_actions
    assert "battle_read_status_detailed" in active_actions
    assert "check_scores" not in active_actions


def test_team_roster_actions_are_contextual_and_not_for_spectators() -> None:
    team_game = make_game(player_count=3, web_first=True)
    spectator = team_game.players[2]
    spectator.is_spectator = True
    team_game.on_start()
    p1, p2 = team_game.players[:2]
    select_and_submit(team_game, p1, "novice_boxer")
    select_and_submit(team_game, p2, "boxer")
    assert advance_until(team_game, lambda: team_game.phase == PHASE_COMBAT and team_game.current_fighter is not None, max_ticks=200)

    p1_actions = {entry.action.id for entry in team_game.get_all_visible_actions(p1)}
    spectator_actions = {entry.action.id for entry in team_game.get_all_visible_actions(spectator)}
    assert "battle_read_allied_fighters" in p1_actions
    assert "battle_read_enemy_fighters" in p1_actions
    assert "battle_read_allied_fighters" not in spectator_actions
    assert "battle_read_enemy_fighters" not in spectator_actions

    team_game.execute_action(p1, "battle_read_allied_fighters")
    allied_texts = [item.text for item in team_game.get_user(p1).menus["status_box"]["items"]]
    assert any("Novice Boxer" in text for text in allied_texts)
    assert not any(text.startswith("Boxer:") for text in allied_texts)

    team_game.execute_action(p1, "battle_read_enemy_fighters")
    enemy_texts = [item.text for item in team_game.get_user(p1).menus["status_box"]["items"]]
    assert any(text.startswith("Boxer:") for text in enemy_texts)
    assert not any("Novice Boxer" in text for text in enemy_texts)

    free_for_all = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL, unlimited_selection_limit=2, web_first=True)
    select_and_submit(free_for_all, free_for_all.players[0], "novice_boxer", "boxer")
    assert advance_until(free_for_all, lambda: free_for_all.phase == PHASE_COMBAT, max_ticks=200)
    ffa_actions = {entry.action.id for entry in free_for_all.get_all_visible_actions(free_for_all.players[0])}
    assert "battle_read_allied_fighters" not in ffa_actions
    assert "battle_read_enemy_fighters" not in ffa_actions


def test_team_roster_actions_only_show_active_fighters() -> None:
    game = make_game(player_count=2, start=True, game_mode=MODE_TWO_EACH, turn_mode=TURN_MODE_ROUND_ROBIN)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer", "boxer")
    select_and_submit(game, p2, "master_mage", "the_alpha_wolf")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and len(game.fighters) == 4, max_ticks=200)

    allied_fighters = [fighter for fighter in game.fighters if fighter.owner_player_id == p1.id]
    enemy_fighters = [fighter for fighter in game.fighters if fighter.owner_player_id == p2.id]
    defeated_ally = allied_fighters[0]
    living_ally = allied_fighters[1]
    defeated_enemy = enemy_fighters[0]
    living_enemy = enemy_fighters[1]

    defeated_ally.health = 0
    defeated_ally.eliminated = True
    defeated_enemy.health = 0
    defeated_enemy.eliminated = True

    game.execute_action(p1, "battle_read_allied_fighters")
    allied_texts = [item.text for item in game.get_user(p1).menus["status_box"]["items"]]
    assert any(game._fighter_name(living_ally, "en") in text for text in allied_texts)
    assert not any(game._fighter_name(defeated_ally, "en") in text for text in allied_texts)

    game.execute_action(p1, "battle_read_enemy_fighters")
    enemy_texts = [item.text for item in game.get_user(p1).menus["status_box"]["items"]]
    assert any(game._fighter_name(living_enemy, "en") in text for text in enemy_texts)
    assert not any(game._fighter_name(defeated_enemy, "en") in text for text in enemy_texts)


def test_roster_view_is_blocked_during_selection() -> None:
    game = make_game(start=True)
    player = game.players[0]

    game.execute_action(player, "battle_read_roster")

    assert game.get_user(player).get_last_spoken() == "Fighters are not available to view until selection is complete."


def test_whose_turn_is_contextual_for_selection_and_combat() -> None:
    game = make_game(start=True, turn_mode=TURN_MODE_ROUND_ROBIN)
    p1, p2 = game.players

    game.execute_action(p1, "whose_turn")
    assert game.get_user(p1).get_last_spoken() == "The game is in the fighter selection phase."

    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)
    game.get_user(p1).clear_messages()

    game.execute_action(p1, "whose_turn")

    spoken = game.get_user(p1).get_last_spoken()
    assert spoken is not None
    assert "It is Novice Boxer" in spoken
    assert "Health 50" in spoken
    assert "Team: Player1's Team" in spoken


def test_spectator_status_and_move_announcements_use_neutral_team_names() -> None:
    game = make_game(player_count=2, game_mode=MODE_CLASSIC_ARENA)
    spectator = game.players[1]
    spectator.is_spectator = True
    game.on_start()
    player = game.players[0]
    select_and_submit(game, player, "novice_boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and any(fighter.is_arena_enemy for fighter in game.fighters), max_ticks=200)

    game.execute_action(spectator, "battle_read_status_detailed")
    spectator_texts = [item.text for item in game.get_user(spectator).menus["status_box"]["items"]]
    assert any("Contestant Side" in text for text in spectator_texts)
    assert any("Arena Side" in text for text in spectator_texts)
    assert not any("Ally Team" in text or "Enemy Team" in text for text in spectator_texts)

    attacker = next(fighter for fighter in game.fighters if not fighter.is_arena_enemy)
    target = next(fighter for fighter in game.fighters if fighter.is_arena_enemy)
    move = get_move_map()[attacker.move_ids[0]]
    game.get_user(player).clear_messages()
    game.get_user(spectator).clear_messages()

    game._announce_move(attacker, target, move)

    player_message = game.get_user(player).get_last_spoken()
    spectator_message = game.get_user(spectator).get_last_spoken()
    assert player_message is not None and "Ally Team" in player_message and "Enemy Team" in player_message
    assert spectator_message is not None and "Contestant Side" in spectator_message and "Arena Side" in spectator_message

    game.winning_team_id = "ally"
    end_screen = game.format_end_screen(game.build_game_result(), "en")
    assert "Winning team: Contestant Side" in end_screen


def test_free_for_all_winner_uses_fighter_name_not_raw_team_id() -> None:
    game = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL, unlimited_selection_limit=2)
    player = game.players[0]
    select_and_submit(game, player, "novice_boxer", "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and len(game.fighters) == 2, max_ticks=200)

    game.winning_team_id = game.fighters[0].team_id
    end_screen = game.format_end_screen(game.build_game_result(), "en")

    assert "Winning team: Novice Boxer's Team" in end_screen
    assert player.id not in end_screen[1]
    assert "novice_boxer:1" not in end_screen[1]


def test_battle_results_do_not_update_win_loss_stats() -> None:
    game = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL, unlimited_selection_limit=2)
    player = game.players[0]
    select_and_submit(game, player, "novice_boxer", "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and len(game.fighters) == 2, max_ticks=200)

    game.winning_team_id = game.fighters[0].team_id
    result = game.build_game_result()
    stats = StatsExtractor.extract_incremental_stats(result)

    assert "skip_win_loss" not in result.custom_data
    assert stats[player.id] == {"games_played": 1.0}


def test_non_survival_results_do_not_store_endurance_fields() -> None:
    game = make_game(player_count=1, start=True, game_mode=MODE_FREE_FOR_ALL, unlimited_selection_limit=2)
    player = game.players[0]
    select_and_submit(game, player, "novice_boxer", "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and len(game.fighters) == 2, max_ticks=200)

    result = game.build_game_result()

    assert "survival_kills" not in result.custom_data
    assert "survival_wave" not in result.custom_data
    assert "player_stats" not in result.custom_data


def test_survival_progress_announces_endless_runs_clearly() -> None:
    game = make_game(player_count=2, start=True, game_mode=MODE_CLASSIC_SURVIVAL)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    game.survival_kills = 3
    game.survival_wave = 2

    status_lines = game._battle_status_lines("en", detailed=False, viewer=p1)
    assert "Endless survival run. Kills: 3." in status_lines
    assert not any("Target: 0" in line or "Wave:" in line for line in status_lines)

    result = game.build_game_result()
    assert result.custom_data["survival_kills"] == 3
    assert result.custom_data["survival_wave"] == 2
    assert "player_stats" in result.custom_data

    end_screen = game.format_end_screen(result, "en")
    assert "Endless survival run. Kills: 3." in end_screen


def test_survival_progress_announces_finite_targets_clearly() -> None:
    game = make_game(player_count=2, start=True, game_mode=MODE_CLASSIC_SURVIVAL, survival_target=5)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    game.survival_kills = 3
    game.survival_wave = 2

    status_lines = game._battle_status_lines("en", detailed=False, viewer=p1)
    assert "Survival run. Kills: 3. Target: 5." in status_lines
    assert not any("Wave:" in line for line in status_lines)


def test_wave_progress_announces_wave_and_target_clearly() -> None:
    game = make_game(player_count=2, start=True, game_mode=MODE_CLASSIC_WAVES, survival_target=5)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    game.survival_kills = 3
    game.survival_wave = 2

    status_lines = game._battle_status_lines("en", detailed=False, viewer=p1)
    assert "Wave run. Current wave: 2. Kills: 3. Target: 5." in status_lines

    result = game.build_game_result()
    assert result.custom_data["survival_kills"] == 3
    assert result.custom_data["survival_wave"] == 2
    assert result.custom_data["player_stats"][p1.id]["deepest_wave"] == 2


def test_battle_custom_leaderboards_extract_endurance_stats() -> None:
    survival_game = make_game(player_count=2, start=True, game_mode=MODE_CLASSIC_SURVIVAL)
    p1, p2 = survival_game.players
    select_and_submit(survival_game, p1, "novice_boxer")
    select_and_submit(survival_game, p2, "boxer")
    assert advance_until(survival_game, lambda: survival_game.phase == PHASE_COMBAT and survival_game.current_fighter is not None, max_ticks=200)
    survival_game.survival_kills = 7

    survival_stats = StatsExtractor.extract_incremental_stats(survival_game.build_game_result())
    assert survival_stats[p1.id]["games_played"] == 1.0
    assert survival_stats[p1.id]["custom_most_enemies_defeated_high"] == 7.0
    assert "custom_deepest_wave_reached_high" not in survival_stats[p1.id]

    wave_game = make_game(player_count=2, start=True, game_mode=MODE_CLASSIC_WAVES)
    p1, p2 = wave_game.players
    select_and_submit(wave_game, p1, "novice_boxer")
    select_and_submit(wave_game, p2, "boxer")
    assert advance_until(wave_game, lambda: wave_game.phase == PHASE_COMBAT and wave_game.current_fighter is not None, max_ticks=200)
    wave_game.survival_kills = 9
    wave_game.survival_wave = 4

    wave_stats = StatsExtractor.extract_incremental_stats(wave_game.build_game_result())
    assert wave_stats[p1.id]["custom_most_enemies_defeated_high"] == 9.0
    assert wave_stats[p1.id]["custom_deepest_wave_reached_high"] == 4.0


def test_turn_sound_respects_user_preference() -> None:
    game = make_game(start=True, turn_mode=TURN_MODE_ROUND_ROBIN)
    p1, p2 = game.players
    select_and_submit(game, p1, "novice_boxer")
    select_and_submit(game, p2, "boxer")
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)
    fighter = game.fighters[0]
    user = game.get_user(p1)

    user.clear_messages()
    user.preferences.play_turn_sound = True
    game._announce_current_turn(fighter)
    assert "turn.ogg" in user.get_sounds_played()

    user.clear_messages()
    user.preferences.play_turn_sound = False
    game._announce_current_turn(fighter)
    assert "turn.ogg" not in user.get_sounds_played()


def test_status_keybinds_match_mile_by_mile_pattern() -> None:
    game = make_game()
    assert [keybind.actions for keybind in game._keybinds["s"]] == [["battle_read_status"]]
    assert [keybind.actions for keybind in game._keybinds["shift+s"]] == [["battle_read_status_detailed"]]
    assert "r" not in game._keybinds or game._keybinds["r"] == []
    assert [keybind.actions for keybind in game._keybinds["a"]] == [["battle_read_allied_fighters"]]
    assert [keybind.actions for keybind in game._keybinds["e"]] == [["battle_read_enemy_fighters"]]
    assert game._keybinds["a"][0].include_spectators is False
    assert game._keybinds["e"][0].include_spectators is False


def test_detailed_status_opens_status_box_list() -> None:
    game = make_game(start=True)
    p1, p2 = game.players
    p1.selected_preset_ids = ["novice_boxer"]
    p2.selected_preset_ids = ["boxer"]
    p1.selection_locked = True
    p2.selection_locked = True
    assert advance_until(game, lambda: game.phase == PHASE_COMBAT and game.current_fighter is not None, max_ticks=200)

    game.execute_action(p1, "battle_read_status_detailed")

    status_menu = game.get_user(p1).menus["status_box"]
    texts = [item.text for item in status_menu["items"]]
    assert texts[0] == "Battle status"
    assert "Combat roster" in texts
    assert any("Novice Boxer" in text for text in texts)


def test_registry_content_is_fully_localized() -> None:
    corruption_markers = ("?", "Ã", "Ä", "Æ", "º", "»", "�")
    registry = load_battle_registry()
    assigned_move_ids = set()
    for move in registry.moves:
        assert move.name.en
        assert move.name.vi
        assert move.name.vi != move.name.en
        assert not any(marker in move.name.vi for marker in corruption_markers)
    for preset in registry.presets:
        assert preset.name.en
        assert preset.name.vi
        assert preset.name.vi != preset.name.en
        assert not any(marker in preset.name.vi for marker in corruption_markers)
        assigned_move_ids.update(preset.move_ids)
        key = f"battle-classic-preset-{preset.id.replace('_', '-')}"
        assert Localization.get("vi", key) != Localization.get("en", key)
    assert Localization.get("vi", "game-name-battle") == "Đấu Trường Chiến Kỹ"
    assert {move.id for move in registry.moves} <= assigned_move_ids


def test_bot_game_completes_or_progresses() -> None:
    random.seed(12345)
    game = make_game(player_count=2, start=True, bot_all=True, game_mode=MODE_CLASSIC_SURVIVAL, survival_target=3)
    assert advance_until(game, lambda: game.status == "finished" or game.phase == PHASE_COMBAT, max_ticks=6000)
