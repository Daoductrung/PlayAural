"""Tests for Age of Heroes action visibility."""

from pathlib import Path

from ..game_utils.actions import Visibility
from ..games.ageofheroes.cards import Card, CardType, EventType, ResourceType
from ..games.ageofheroes.bot import bot_execute_discard_excess
from ..games.ageofheroes.combat import (
    execute_war_battle,
    finish_war_battle,
    resolve_battle_round,
    return_surviving_forces,
    use_fortune_reroll,
)
from ..games.ageofheroes.construction import can_build, spend_resources
from ..games.ageofheroes import game as ageofheroes_game_module
from ..games.ageofheroes.game import (
    AgeOfHeroesGame,
    ActionType,
    BuildingType,
    GamePhase,
    MAX_HAND_SIZE,
    PlaySubPhase,
    WarGoal,
)
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_started_game(player_count: int = 3) -> AgeOfHeroesGame:
    game = AgeOfHeroesGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    game.on_start()
    return game


def test_main_action_hidden_when_disabled() -> None:
    """A main action that is disabled for the player drops out of the menu.

    Construction with no affordable buildings used to linger as a disabled
    button; it should now be hidden, while a generally-available action such
    as tax collection stays visible.
    """
    game = make_started_game()
    player = game.get_active_players()[0]
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.SELECT_ACTION
    game.set_turn_players([player])

    # A fresh player has no resources, so construction is unavailable.
    construction_id = f"action_{ActionType.CONSTRUCTION.value}"
    assert game._is_main_action_enabled(player, construction_id) == "ageofheroes-no-resources"
    assert game._is_main_action_hidden(player, construction_id) == Visibility.HIDDEN

    tax_id = f"action_{ActionType.TAX_COLLECTION.value}"
    assert game._is_main_action_enabled(player, tax_id) is None
    assert game._is_main_action_hidden(player, tax_id) == Visibility.VISIBLE


def test_ageofheroes_uses_coup_background_music() -> None:
    game = make_started_game()

    assert any(
        state.kind == "music" and state.asset == "game_coup/music.ogg"
        for state in game.active_audio.values()
    )


def test_build_action_hidden_when_unaffordable() -> None:
    """Unaffordable buildings are hidden from the construction menu."""
    game = make_started_game()
    player = game.get_active_players()[0]
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.CONSTRUCTION
    game.set_turn_players([player])

    # Exactly the cost of an army (iron + grain + grain) and nothing else.
    player.hand = [
        Card(id=1, card_type=CardType.RESOURCE, subtype=ResourceType.IRON),
        Card(id=2, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
        Card(id=3, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
    ]

    assert game._is_build_enabled(player, "build_army") is None
    assert game._is_build_hidden(player, "build_army") == Visibility.VISIBLE

    # A fortress needs iron + wood + stone, which the player cannot cover.
    assert game._is_build_enabled(player, "build_fortress") == "ageofheroes-no-resources"
    assert game._is_build_hidden(player, "build_fortress") == Visibility.HIDDEN


def test_construction_menu_focuses_first_building_when_opened() -> None:
    """Opening the construction prompt should start at the first visible building."""
    game = make_started_game()
    player = game.get_active_players()[0]
    user = game.get_user(player)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.SELECT_ACTION
    game.set_turn_players([player])
    player.hand = [
        Card(id=21, card_type=CardType.RESOURCE, subtype=ResourceType.IRON),
        Card(id=22, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
        Card(id=23, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
    ]

    game._action_select_main_action(player, f"action_{ActionType.CONSTRUCTION.value}")
    game.flush_menus()

    assert user.menus["turn_menu"]["selection_id"] == "build_army"


def test_road_target_menu_focuses_first_target_when_opened() -> None:
    """The road target prompt should not inherit focus from the build menu."""
    game = make_started_game()
    player = game.get_active_players()[0]
    user = game.get_user(player)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.CONSTRUCTION
    game.set_turn_players(game.get_active_players())
    player.hand = [
        Card(id=31, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
        Card(id=32, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
    ]

    game._action_build_building(player, "build_road")
    game.flush_menus()

    assert user.menus["turn_menu"]["selection_id"] == "road_target_0"


def test_road_permission_prompt_focuses_first_response() -> None:
    """A new road approval prompt should focus Approve for the responder."""
    game = make_started_game()
    builder, responder, _ = game.get_active_players()
    responder_user = game.get_user(responder)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.ROAD_TARGET
    game.set_turn_players(game.get_active_players())
    builder.pending_road_targets = [(1, "right")]

    game._action_select_road_target(builder, "road_target_0")
    game.flush_menus()

    assert game.sub_phase == PlaySubPhase.ROAD_PERMISSION
    assert responder_user.menus["turn_menu"]["selection_id"] == "approve_road"


def test_war_goal_menu_focuses_first_goal_after_target_selection() -> None:
    """War goal focus should use real action ids even when goals are enum values."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    user = game.get_user(attacker)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.WAR_DECLARE
    game.current_day = 3
    game.set_turn_players([attacker, defender])
    attacker.pending_war_targets = [(1, defender)]
    attacker.tribe_state.armies = 2
    defender.tribe_state.cities = 1
    defender.hand = [Card(id=41, card_type=CardType.RESOURCE, subtype=ResourceType.WOOD)]

    game._action_select_war_target(attacker, "war_target_0")
    game.flush_menus()

    assert attacker.pending_war_goals == [WarGoal.CONQUEST, WarGoal.PLUNDER]
    assert user.menus["turn_menu"]["selection_id"] == "war_goal_conquest"


def test_war_battle_prompt_focuses_roll_for_combatants() -> None:
    """Entering battle mode should land both human combatants on Roll dice."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)
    game.phase = GamePhase.PLAY
    game.set_turn_players([attacker, defender])
    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.goal = WarGoal.PLUNDER
    game.war_state.attacker_armies = 1
    game.war_state.defender_armies = 1

    execute_war_battle(game)
    game.flush_menus()

    assert game.sub_phase == PlaySubPhase.WAR_BATTLE
    assert attacker_user.menus["turn_menu"]["selection_id"] == "war_roll_dice"
    assert defender_user.menus["turn_menu"]["selection_id"] == "war_roll_dice"


def test_gold_wildcard_does_not_double_pay_explicit_gold() -> None:
    """A single Gold cannot pay both an explicit Gold cost and a wildcard shortfall."""
    game = make_started_game()
    player = game.get_active_players()[0]

    player.hand = [Card(id=10, card_type=CardType.RESOURCE, subtype=ResourceType.GOLD)]
    assert not can_build(game, player, BuildingType.GENERAL)

    player.hand = [
        Card(id=11, card_type=CardType.RESOURCE, subtype=ResourceType.GOLD),
        Card(id=12, card_type=CardType.RESOURCE, subtype=ResourceType.GOLD),
    ]
    assert can_build(game, player, BuildingType.GENERAL)

    discard_pile: list[Card] = []
    spent = spend_resources(player, [ResourceType.IRON, ResourceType.GOLD], discard_pile)

    assert len(spent) == 2
    assert player.hand == []
    assert discard_pile == spent


def test_war_survivors_do_not_duplicate_when_returning_later() -> None:
    """Committed units stay in totals; delayed return only marks them unavailable."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    attacker.tribe_state.armies = 3
    attacker.tribe_state.generals = 1
    defender.tribe_state.armies = 2
    defender.tribe_state.generals = 1
    game.set_turn_players([attacker, defender])

    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.attacker_armies = 2
    game.war_state.attacker_generals = 1
    game.war_state.defender_armies = 2
    game.war_state.defender_generals = 1

    return_surviving_forces(game)

    assert attacker.tribe_state.armies == 3
    assert attacker.tribe_state.generals == 1
    assert attacker.tribe_state.returning_armies == 2
    assert attacker.tribe_state.returning_generals == 1
    assert defender.tribe_state.armies == 2
    assert defender.tribe_state.generals == 1


def test_war_survivors_do_not_duplicate_when_returning_by_road() -> None:
    """Road-connected survivors are immediately available without increasing totals."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    attacker.tribe_state.armies = 3
    attacker.tribe_state.generals = 1
    attacker.tribe_state.road_right = True
    defender.tribe_state.road_left = True
    defender.tribe_state.armies = 2
    game.set_turn_players([attacker, defender])

    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.attacker_armies = 2
    game.war_state.attacker_generals = 1
    game.war_state.defender_armies = 1

    return_surviving_forces(game)

    assert attacker.tribe_state.armies == 3
    assert attacker.tribe_state.generals == 1
    assert attacker.tribe_state.returning_armies == 0
    assert attacker.tribe_state.returning_generals == 0
    assert defender.tribe_state.armies == 2


def test_immediate_attacker_victory_uses_each_battle_perspective(monkeypatch) -> None:
    game = make_started_game(player_count=3)
    attacker, defender, observer = game.get_active_players()
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)
    observer_user = game.get_user(observer)
    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.attacker_armies = 1
    game.war_state.defender_armies = 0
    game.war_state.battle_in_progress = False
    checked_players = []
    ended_players = []
    monkeypatch.setattr(game, "_check_elimination", lambda player: checked_players.append(player.id))
    monkeypatch.setattr(game, "_end_action", lambda player: ended_players.append(player.id))
    attacker_user.clear_messages()
    defender_user.clear_messages()
    observer_user.clear_messages()

    finish_war_battle(game)

    assert attacker_user.get_last_spoken() == "You defeat Player2."
    assert defender_user.get_last_spoken() == "Player1 defeats you."
    assert observer_user.get_last_spoken() == "Player1 defeats Player2."
    assert checked_players == [attacker.id, defender.id]
    assert ended_players == [attacker.id]
    assert game.war_state.attacker_index == -1
    assert game.war_state.defender_index == -1


def test_immediate_defender_victory_uses_each_battle_perspective(monkeypatch) -> None:
    game = make_started_game(player_count=3)
    attacker, defender, observer = game.get_active_players()
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)
    observer_user = game.get_user(observer)
    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.attacker_armies = 0
    game.war_state.defender_armies = 1
    game.war_state.battle_in_progress = False
    monkeypatch.setattr(game, "_check_elimination", lambda _player: None)
    monkeypatch.setattr(game, "_end_action", lambda _player: None)
    attacker_user.clear_messages()
    defender_user.clear_messages()
    observer_user.clear_messages()

    finish_war_battle(game)

    assert attacker_user.get_last_spoken() == "Player2 defends successfully against you."
    assert defender_user.get_last_spoken() == "You defend successfully against Player1."
    assert observer_user.get_last_spoken() == (
        "Player2 defends successfully against Player1."
    )


def test_bot_discard_excess_preserves_discard_pile(monkeypatch) -> None:
    game = make_started_game()
    player = game.get_active_players()[0]
    player.is_bot = True
    player.hand = [
        Card(id=i, card_type=CardType.RESOURCE, subtype=ResourceType.WOOD)
        for i in range(MAX_HAND_SIZE + 2)
    ]

    ended: list[bool] = []
    monkeypatch.setattr(game, "_end_turn", lambda: ended.append(True))

    bot_execute_discard_excess(game, player)

    assert len(player.hand) == MAX_HAND_SIZE
    assert len(game.discard_pile) == 2
    assert player.pending_discard == 0
    assert ended == [True]


def test_do_nothing_respects_confirm_risky_actions_preference() -> None:
    game = make_started_game()
    player = game.get_active_players()[0]
    user = game.get_user(player)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.SELECT_ACTION
    game.set_turn_players([player])

    action_id = f"action_{ActionType.DO_NOTHING.value}"
    game._action_select_main_action(player, action_id)

    assert player.current_action is None
    assert player.do_nothing_confirm_ticks > 0
    assert any(
        "Press Do Nothing again to confirm" in message.data.get("text", "")
        for message in user.messages
    )

    game._action_select_main_action(player, action_id)

    assert player.do_nothing_confirm_ticks == 0


def test_brief_draw_messages_are_per_listener() -> None:
    game = make_started_game(player_count=2)
    actor, observer = game.get_active_players()
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    actor_user.preferences.brief_announcements = True
    observer_user.preferences.brief_announcements = True

    game._broadcast_draw(
        actor,
        Card(id=99, card_type=CardType.RESOURCE, subtype=ResourceType.IRON),
    )

    assert actor_user.messages[-1].data["text"] == "Draw: Iron."
    assert observer_user.messages[-1].data["text"] == f"{actor.name} draws."


def test_brief_battle_round_uses_concise_combat_log() -> None:
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)
    attacker_user.preferences.brief_announcements = True
    defender_user.preferences.brief_announcements = True
    game.set_turn_players([attacker, defender])

    game.war_state.attacker_index = 0
    game.war_state.defender_index = 1
    game.war_state.attacker_armies = 1
    game.war_state.defender_armies = 1
    game.war_state.attacker_roll = 6
    game.war_state.defender_roll = 3

    resolve_battle_round(game)

    expected = f"{attacker.name} 6 beats {defender.name} 3. {defender.name} -1 army."
    assert any(message.data.get("text") == expected for message in attacker_user.messages)
    assert any(message.data.get("text") == expected for message in defender_user.messages)


def test_deny_road_request_returns_human_builder_to_construction() -> None:
    """Denying a road request must not crash the construction flow."""
    game = make_started_game()
    active_players = game.get_active_players()
    builder = active_players[0]
    target = active_players[1]
    assert not builder.is_bot

    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.ROAD_PERMISSION
    game.set_turn_players(active_players)
    builder.hand = [
        Card(id=101, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
        Card(id=102, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
    ]
    builder.pending_road_targets = [(1, "right")]
    game.road_request_from = 0
    game.road_request_to = 1

    game._action_deny_road(target, "deny_road")

    assert game.road_request_from == -1
    assert game.road_request_to == -1
    assert builder.pending_road_targets == []
    assert builder.declined_road_targets == [1]
    assert game.sub_phase == PlaySubPhase.CONSTRUCTION


def test_deny_road_request_resumes_bot_builder_construction(monkeypatch) -> None:
    """Bot road denials should route through the same safe handler path."""
    game = make_started_game()
    active_players = game.get_active_players()
    builder = active_players[0]
    target = active_players[1]
    builder.is_bot = True

    resumed: list[object] = []

    def fake_bot_perform_construction(game_arg, player_arg) -> None:
        resumed.append((game_arg, player_arg))

    monkeypatch.setattr(
        ageofheroes_game_module.bot_ai,
        "bot_perform_construction",
        fake_bot_perform_construction,
    )

    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.ROAD_PERMISSION
    game.set_turn_players(active_players)
    builder.hand = [
        Card(id=201, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
        Card(id=202, card_type=CardType.RESOURCE, subtype=ResourceType.STONE),
    ]
    builder.pending_road_targets = [(1, "right")]
    game.road_request_from = 0
    game.road_request_to = 1

    game._action_deny_road(target, "deny_road")

    assert game.road_request_from == -1
    assert game.road_request_to == -1
    assert builder.pending_road_targets == []
    assert builder.declined_road_targets == [1]
    assert resumed == [(game, builder)]


def test_offer_request_cancel_returns_focus_to_offer_list() -> None:
    """Closing the request submenu should route focus back to an offerable card."""
    game = make_started_game()
    player = game.get_active_players()[0]
    user = game.get_user(player)
    game.phase = GamePhase.FAIR
    game.set_turn_players([player])
    player.hand = [
        Card(id=601, card_type=CardType.RESOURCE, subtype=ResourceType.WOOD),
        Card(id=602, card_type=CardType.RESOURCE, subtype=ResourceType.IRON),
    ]

    game._action_select_offer_card(player, "offer_card_0")
    game.flush_menus()

    assert user.menus["turn_menu"]["selection_id"] == "request_any"

    game._action_cancel_offer_selection(player, "cancel_offer_selection")
    game.flush_menus()

    assert user.menus["turn_menu"]["selection_id"] == "offer_card_0"


def _make_lobby_game(player_count: int = 3) -> AgeOfHeroesGame:
    """Build a game with players seated but still in the lobby (not started)."""
    game = AgeOfHeroesGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    return game


def test_roll_dice_hidden_before_game_starts() -> None:
    """Roll Dice must not surface in the lobby.

    ``phase`` defaults to ``GamePhase.SETUP`` while the table is still waiting,
    so without a status guard the Roll Dice button leaked into the lobby for
    touch clients before the game had started.
    """
    game = _make_lobby_game()
    player = game.players[0]

    # Sanity: the conditions that used to make this VISIBLE all hold.
    assert game.status != "playing"
    assert game.phase == GamePhase.SETUP
    assert player.id not in game.setup_rolls

    assert game._is_roll_dice_hidden(player) == Visibility.HIDDEN


def test_roll_dice_visible_in_setup_for_unrolled_player() -> None:
    """Once the game starts, a seated player who hasn't rolled sees Roll Dice."""
    game = make_started_game()
    player = game.get_active_players()[0]

    assert game.status == "playing"
    assert game.phase == GamePhase.SETUP
    assert player.id not in game.setup_rolls

    assert game._is_roll_dice_hidden(player) == Visibility.VISIBLE


def test_roll_dice_hidden_after_player_rolled() -> None:
    """Roll Dice disappears for a player who has already rolled in setup."""
    game = make_started_game()
    player = game.get_active_players()[0]
    game.setup_rolls[player.id] = 9

    assert game._is_roll_dice_hidden(player) == Visibility.HIDDEN


def test_roll_dice_hidden_for_spectator() -> None:
    """Spectators never see the gameplay-mutating Roll Dice button."""
    game = make_started_game()
    player = game.get_active_players()[0]
    player.is_spectator = True

    assert game._is_roll_dice_hidden(player) == Visibility.HIDDEN


def test_whose_turn_reports_setup_roll_context() -> None:
    """The setup dice phase should not announce that no one has the turn."""
    game = make_started_game()
    viewer = game.get_active_players()[0]
    user = game.get_user(viewer)

    game.setup_rolls[viewer.id] = 8
    game._action_whose_turn(viewer, "whose_turn")

    assert user.messages[-1].data["text"] == (
        "Setup phase. Waiting for Player2 and Player3 to roll for turn order."
    )


def test_human_defender_can_answer_bot_war() -> None:
    """A bot attacker must not auto-pick a human defender's committed forces."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    attacker.is_bot = True
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.SELECT_ACTION
    game.current_day = 3
    game.set_turn_players([attacker, defender])
    attacker.tribe_state.armies = 3
    defender.tribe_state.armies = 2
    defender.hand = [Card(id=301, card_type=CardType.RESOURCE, subtype=ResourceType.WOOD)]

    game.war_state.attacker_index = 0
    ageofheroes_game_module.bot_ai.bot_perform_war(game, attacker)

    assert game.sub_phase == PlaySubPhase.WAR_PREPARE_DEFENDER
    assert game.war_state.attacker_prepared is True
    assert game.war_state.defender_prepared is False
    assert defender.pending_war_armies == 2


def test_war_force_controls_use_explicit_add_remove_labels() -> None:
    """Force controls should describe the current committed count, not a cycle target."""
    game = make_started_game(player_count=2)
    player = game.get_active_players()[0]
    user = game.get_user(player)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.WAR_PREPARE_ATTACKER
    game.set_turn_players([player])
    player.tribe_state.armies = 3
    player.tribe_state.generals = 1
    player.pending_war_armies = 1
    player.pending_war_generals = 0
    player.hand = [Card(id=501, card_type=CardType.EVENT, subtype=EventType.HERO)]

    add_action = game.find_action(player, "war_armies_add")
    remove_action = game.find_action(player, "war_armies_remove")
    assert add_action is not None
    assert remove_action is not None

    assert game.resolve_action(player, add_action).label == (
        "Add one army. Armies committed: 1 of 3."
    )
    assert game.resolve_action(player, remove_action).label == (
        "Remove one army. Armies committed: 1 of 3."
    )

    game._action_adjust_war_force(player, "war_armies_add")

    assert player.pending_war_armies == 2
    assert user.messages[-1].data["text"] == (
        "Forces committed: 2 armies, 0 generals, 0 Hero armies, 0 Hero generals."
    )


def test_war_force_menu_focuses_top_control_when_opened() -> None:
    """Entering war force selection should reset the cursor to the top control."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    user = game.get_user(attacker)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.WAR_DECLARE
    game.current_day = 3
    game.set_turn_players([attacker, defender])
    attacker.tribe_state.armies = 3
    defender.tribe_state.armies = 2
    attacker.pending_war_target_index = 1
    attacker.pending_war_goals = [WarGoal.PLUNDER.value]

    game._action_select_war_goal(attacker, f"war_goal_{WarGoal.PLUNDER.value}")
    game.flush_menus()

    assert game.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER
    assert user.menus["turn_menu"]["selection_id"] == "war_armies_remove"


def test_cancel_war_target_returns_focus_to_main_actions() -> None:
    """Canceling a contextual prompt should not leave focus on a removed button."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    user = game.get_user(attacker)
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.WAR_DECLARE
    game.current_day = 3
    game.set_turn_players([attacker, defender])
    attacker.pending_war_targets = [(1, defender)]
    attacker.tribe_state.armies = 2

    game._action_cancel_war_target(attacker, "cancel_war_target")
    game.flush_menus()

    assert game.sub_phase == PlaySubPhase.SELECT_ACTION
    assert user.menus["turn_menu"]["selection_id"] == f"action_{ActionType.TAX_COLLECTION.value}"


def test_olympics_prompts_human_defender_before_war_forces(monkeypatch) -> None:
    """A human defender with Olympic Games gets a real cancel decision window."""
    game = make_started_game(player_count=2)
    attacker, defender = game.get_active_players()
    game.phase = GamePhase.PLAY
    game.sub_phase = PlaySubPhase.WAR_DECLARE
    game.current_day = 3
    game.set_turn_players([attacker, defender])
    attacker.tribe_state.armies = 2
    defender.hand = [
        Card(id=401, card_type=CardType.EVENT, subtype=EventType.OLYMPICS),
        Card(id=402, card_type=CardType.RESOURCE, subtype=ResourceType.WOOD),
    ]
    attacker.pending_war_target_index = 1
    attacker.pending_war_goals = [WarGoal.PLUNDER.value]
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)
    ended_players = []
    monkeypatch.setattr(game, "_end_action", lambda player: ended_players.append(player.id))

    game._action_select_war_goal(attacker, f"war_goal_{WarGoal.PLUNDER.value}")

    assert game.sub_phase == PlaySubPhase.WAR_OLYMPICS
    assert game.war_state.defender_index == 1
    attacker_user.clear_messages()
    defender_user.clear_messages()

    game._action_use_olympics(defender, "use_olympics")

    assert game.war_state.defender_index == -1
    assert all(card.subtype != EventType.OLYMPICS for card in defender.hand)
    assert any(card.subtype == EventType.OLYMPICS for card in game.discard_pile)
    assert ended_players == [attacker.id]
    assert defender_user.get_last_spoken() == (
        "You play Olympic Games, cancelling the declared war."
    )
    assert attacker_user.get_last_spoken() == (
        "Player2 plays Olympic Games, cancelling the declared war."
    )


def test_fortune_reroll_uses_actor_and_observer_perspectives() -> None:
    game = make_started_game(player_count=2)
    actor, observer = game.get_active_players()
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    actor.hand = [Card(id=450, card_type=CardType.EVENT, subtype=EventType.FORTUNE)]
    actor_user.clear_messages()
    observer_user.clear_messages()

    assert use_fortune_reroll(game, actor) is True

    assert actor_user.get_last_spoken() == "You use Fortune to reroll the battle die."
    assert observer_user.get_last_spoken() == (
        "Player1 uses Fortune to reroll the battle die."
    )
