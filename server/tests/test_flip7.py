"""Tests for the Flip 7 card game."""

from pathlib import Path
import json

from ..games.flip7.game import (
    ACTION_COPIES,
    CARD_DOUBLE,
    CARD_FLIP_THREE,
    CARD_MODIFIER,
    CARD_NUMBER,
    CARD_SECOND_CHANCE,
    CARD_STOP,
    CHOICE_SECOND_CHANCE,
    CHOICE_STOP,
    FLIP_SEVEN_BONUS,
    FLIP_SEVEN_TARGET,
    FLIP_THREE_COUNT,
    MAX_NUMBER,
    MODIFIER_VALUES,
    OUTCOME_BUST,
    OUTCOME_CHOICE,
    OUTCOME_FLIP7,
    OUTCOME_OK,
    OUTCOME_SAVED,
    PHASE_MATCH_END,
    PHASE_PLAYING,
    PHASE_ROUND_END,
    STATUS_BUSTED,
    STATUS_PLAYING,
    STATUS_STAYED,
    Flip7Card,
    Flip7FlipState,
    Flip7Game,
    Flip7Options,
)
from ..games.registry import GameRegistry
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]


def _card(kind, value=0, uid=0):
    return Flip7Card(kind=kind, value=value, uid=uid)


def _make_game(
    player_count=2,
    *,
    start=True,
    bot_all=False,
    target_score=200,
    mobile_user=False,
):
    game = Flip7Game(options=Flip7Options(target_score=target_score))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
        if mobile_user:
            user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
        game.flush_menus()
    return game


def advance_until(game, condition, max_ticks: int = 4000) -> bool:
    for _ in range(max_ticks):
        game.on_tick()
        game.flush_menus()
        if condition():
            return True
    return condition()


def _deal_number_cards(game, values):
    """Overwrite the deck with number cards and run the initial deal."""
    game.deck = [_card(CARD_NUMBER, value, uid=value) for value in values]
    assert advance_until(
        game,
        lambda: (
            game.deal_index >= len(game.deal_order)
            and all(len(player.numbers) == 1 for player in game.players)
            and game.pending_choice is None
        ),
    )


def _locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and "=" in line
        and not line[0].isspace()
    }


# ---------------------------------------------------------------------------
# Metadata / registration / options
# ---------------------------------------------------------------------------


def test_flip7_registration_metadata_and_leaderboards():
    assert GameRegistry.get("flip7") is Flip7Game
    game = Flip7Game()
    assert game.get_name() == "Flip 7"
    assert game.get_type() == "flip7"
    assert game.get_category() == "cards"
    assert (game.get_min_players(), game.get_max_players()) == (2, 10)
    assert game.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]


def test_flip7_options_defaults():
    assert Flip7Options().target_score == 200
    game = Flip7Game(options=Flip7Options(target_score=50))
    assert game.options.target_score == 50


def test_flip7_localization_and_documentation_are_present():
    expected = _locale_keys(ROOT / "server" / "locales" / "en" / "flip7.ftl")
    for locale in ("en", "es", "pt", "vi"):
        ftl = ROOT / "server" / "locales" / locale / "flip7.ftl"
        doc = (
            ROOT / "server" / "documentation" / "content" / locale / "games" / "flip7.md"
        )
        assert ftl.exists(), ftl
        assert doc.exists(), doc
        assert _locale_keys(ftl) == expected


# ---------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------


def test_flip7_deck_composition():
    deck = Flip7Game.build_deck()
    assert len(deck) == 94
    assert len({c.uid for c in deck}) == 94

    kinds = {kind: [c for c in deck if c.kind == kind] for kind in set(c.kind for c in deck)}
    numbers = kinds[CARD_NUMBER]
    assert len(numbers) == 1 + sum(range(1, MAX_NUMBER + 1))
    assert len(kinds[CARD_MODIFIER]) == len(MODIFIER_VALUES)
    assert len(kinds[CARD_DOUBLE]) == 1
    assert len(kinds[CARD_SECOND_CHANCE]) == ACTION_COPIES
    assert len(kinds[CARD_STOP]) == ACTION_COPIES
    assert len(kinds[CARD_FLIP_THREE]) == ACTION_COPIES

    # Each value v appears exactly v times: one zero, one ace, six sixes, etc.
    for value in range(1, MAX_NUMBER + 1):
        assert len([c for c in numbers if c.value == value]) == value
    assert [c.value for c in kinds[CARD_MODIFIER]] == list(MODIFIER_VALUES)


# ---------------------------------------------------------------------------
# Startup / play
# ---------------------------------------------------------------------------


def test_flip7_start_initializes_round_and_players():
    game = _make_game(player_count=3)
    assert game.status == "playing"
    assert game.phase == PHASE_PLAYING
    assert game.round == 1
    assert [p.total_score for p in game.players] == [0, 0, 0]
    assert [p.round_status for p in game.players] == [
        STATUS_PLAYING,
        STATUS_PLAYING,
        STATUS_PLAYING,
    ]
    assert len(game.deck) == 94
    assert game.options.target_score == 200


def test_flip7_initial_deal_gives_every_player_one_number_card():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    first, second = game.players
    # Dealer is Player1, so Player2 is dealt first and gets the top card (4).
    assert first.numbers == [3]
    assert second.numbers == [4]
    assert first.total_score == 0


def test_flip7_hit_draws_a_card_into_the_area():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    game.deck = [_card(CARD_NUMBER, 9, uid=100)]
    actor.hits_taken = 0
    game.before_menu_build(actor)
    game.execute_action(actor, "hit")
    assert actor.numbers == sorted(actor.numbers)
    assert actor.hits_taken == 1
    assert actor.round_status == STATUS_PLAYING


def test_flip7_hit_disabled_while_dealing():
    game = _make_game(player_count=2)
    for player in game.players:
        assert game._is_hit_enabled(player) == "flip7-error-wait-dealing"


def test_flip7_hit_disabled_for_waiting_player_after_deal():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    game.deck = [_card(CARD_NUMBER, 9, uid=100)]
    actor = game.current_player
    waiting = next(p for p in game.players if p is not actor)
    assert game._is_hit_enabled(actor) is None
    assert game._is_hit_enabled(waiting) == "action-not-your-turn"


def test_flip7_stay_disabled_without_cards():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    waiting = next(p for p in game.players if p is not game.current_player)
    waiting.numbers = []
    waiting.modifiers = []
    waiting.has_double = False
    waiting.round_status = STATUS_PLAYING
    game.turn_index = game.turn_player_ids.index(waiting.id)
    assert game._is_stay_enabled(waiting) == "flip7-error-no-cards-to-bank"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def test_flip7_round_points_double_before_modifiers():
    game = _make_game(player_count=2, start=False)
    player = game.players[0]
    player.numbers = [3, 5]
    player.modifiers = [2]
    assert game.round_points(player) == 10
    player.has_double = True
    assert game.round_points(player) == 18
    player.modifiers = [2, 10]
    assert game.round_points(player) == 28


def test_flip7_repeated_number_busts_without_second_chance():
    game = _make_game(player_count=2)
    player = game.players[0]
    player.numbers = [7]
    outcome = game._resolve_card(
        player, _card(CARD_NUMBER, 7, uid=1), forced=False, chooser=player
    )
    assert outcome == OUTCOME_BUST
    assert player.round_status == STATUS_BUSTED
    assert player.busts == 1
    assert player.numbers == [7]


def test_flip7_second_chance_saves_against_repeated_number():
    game = _make_game(player_count=2)
    player = game.players[0]
    player.numbers = [7]
    player.second_chance = True
    outcome = game._resolve_card(
        player, _card(CARD_NUMBER, 7, uid=1), forced=False, chooser=player
    )
    assert outcome == OUTCOME_SAVED
    assert player.second_chance is False
    assert player.round_status == STATUS_PLAYING
    assert player.numbers == [7]


def test_flip7_seven_unique_numbers_scores_bonus_and_ends_round():
    game = _make_game(player_count=2)
    player = game.players[0]
    player.numbers = [1, 2, 3, 4, 5, 6]
    outcome = game._resolve_card(
        player, _card(CARD_NUMBER, 7, uid=1), forced=False, chooser=player
    )
    assert outcome == OUTCOME_FLIP7
    assert player.numbers == [1, 2, 3, 4, 5, 6, 7]
    assert FLIP_SEVEN_TARGET == 7

    game._schedule_flip_seven_award(player)
    assert advance_until(game, lambda: game.phase != PHASE_PLAYING)
    assert player.flip_sevens == 1
    assert player.total_score == sum(range(1, 8)) + FLIP_SEVEN_BONUS
    assert player.numbers == []
    assert game.phase in (PHASE_ROUND_END, PHASE_MATCH_END)


# ---------------------------------------------------------------------------
# Targeted choices
# ---------------------------------------------------------------------------


def test_flip7_stop_card_opens_a_targeted_choice():
    game = _make_game(player_count=3)
    actor = game.players[0]
    outcome = game._resolve_card(
        actor, _card(CARD_STOP, uid=1), forced=False, chooser=actor
    )
    assert outcome == OUTCOME_CHOICE
    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_STOP
    assert len(game._choice_targets()) == 3


def test_flip7_choice_action_stops_a_chosen_player():
    game = _make_game(player_count=3)
    actor = game.players[0]
    target = game.players[1]
    game._resolve_card(actor, _card(CARD_STOP, uid=1), forced=False, chooser=actor)
    game.before_menu_build(actor)
    game.execute_action(actor, f"choose_stop_{game._slot_of(target)}")
    assert target.round_status == STATUS_STAYED
    assert game.pending_choice is None
    assert target.total_score == 0


def test_flip7_stop_alone_stops_the_last_playing_player():
    game = _make_game(player_count=2)
    actor = game.players[0]
    actor.numbers = [5]
    game.players[1].round_status = STATUS_BUSTED
    outcome = game._resolve_card(
        actor, _card(CARD_STOP, uid=1), forced=False, chooser=actor
    )
    assert outcome == OUTCOME_OK
    assert actor.round_status == STATUS_STAYED


def test_flip7_second_chance_sets_aside_when_not_held():
    game = _make_game(player_count=2)
    actor = game.players[0]
    outcome = game._resolve_card(
        actor, _card(CARD_SECOND_CHANCE, uid=1), forced=False, chooser=actor
    )
    assert outcome == OUTCOME_OK
    assert actor.second_chance is True
    assert game.pending_choice is None


def test_flip7_held_second_chance_opens_choice_to_pass_it_on():
    game = _make_game(player_count=3)
    actor = game.players[0]
    actor.second_chance = True
    outcome = game._resolve_card(
        actor, _card(CARD_SECOND_CHANCE, uid=1), forced=False, chooser=actor
    )
    assert outcome == OUTCOME_CHOICE
    assert game.pending_choice.kind == CHOICE_SECOND_CHANCE
    targets = game._choice_targets()
    assert actor not in targets
    assert len(targets) == 2


def test_flip7_given_second_chance_lands_on_a_target():
    game = _make_game(player_count=3)
    actor = game.players[0]
    target = game.players[2]
    actor.second_chance = True
    game._resolve_card(
        actor, _card(CARD_SECOND_CHANCE, uid=1), forced=False, chooser=actor
    )
    game.before_menu_build(actor)
    action_id = f"choose_second_chance_{game._slot_of(target)}"
    game.execute_action(actor, action_id)
    assert target.second_chance is True
    assert game.pending_choice is None


# ---------------------------------------------------------------------------
# Flip Three
# ---------------------------------------------------------------------------


def test_flip7_flip_three_forced_draws_apply_cards():
    game = _make_game(player_count=2)
    target = game.players[1]
    game.flip_state = Flip7FlipState(target_slot=1, chooser_slot=0, remaining=3)
    game.deck = [_card(CARD_NUMBER, v, uid=v) for v in (4, 5, 6)]
    for _ in range(FLIP_THREE_COUNT):
        game._flip_draw()
    assert target.numbers == [4, 5, 6]
    assert game.flip_state is not None
    assert game.flip_state.remaining == 0
    game._flip_finish()
    assert game.flip_state is None


def test_flip7_forced_stop_counts_and_does_not_open_choice():
    game = _make_game(player_count=3)
    target = game.players[1]
    game.flip_state = Flip7FlipState(target_slot=1, chooser_slot=0, remaining=3)
    outcome = game._resolve_card(
        target, _card(CARD_STOP, uid=1), forced=True, chooser=game.players[0]
    )
    assert outcome == OUTCOME_OK
    assert game.pending_choice is None
    assert game.flip_state.stops == 1


def test_flip7_forced_action_cards_count_toward_the_queue():
    game = _make_game(player_count=3)
    target = game.players[1]
    chooser = game.players[0]
    game.flip_state = Flip7FlipState(target_slot=1, chooser_slot=0, remaining=3)

    outcome = game._resolve_card(
        target, _card(CARD_FLIP_THREE, uid=1), forced=True, chooser=chooser
    )
    assert outcome == OUTCOME_OK
    assert game.flip_state.flips == 1

    target.second_chance = True
    outcome = game._resolve_card(
        target, _card(CARD_SECOND_CHANCE, uid=1), forced=True, chooser=chooser
    )
    assert outcome == OUTCOME_OK
    assert game.flip_state.second_chances == 1
    assert game.pending_choice is None


def test_flip7_flip_three_discover_of_seven_ends_flow_with_award():
    game = _make_game(player_count=2)
    target = game.players[1]
    target.numbers = [1, 2, 3, 4, 5, 6]
    game.deck = [_card(CARD_NUMBER, FLIP_SEVEN_TARGET, uid=7)]
    game.flip_state = Flip7FlipState(target_slot=1, chooser_slot=0, remaining=1)
    game._flip_draw()
    assert game.flip_state is None


# ---------------------------------------------------------------------------
# Round and match end
# ---------------------------------------------------------------------------


def test_flip7_end_round_scores_stayers_and_zeroes_busters():
    game = _make_game(player_count=2)
    first, second = game.players
    first.numbers = [3, 5]
    first.modifiers = [2]
    first.round_status = STATUS_STAYED
    second.numbers = [4]
    second.round_status = STATUS_BUSTED
    game.phase = PHASE_PLAYING

    game._end_round()

    assert first.total_score == 10
    assert second.total_score == 0
    assert game._team_manager.get_team(first.name).total_score == 10
    assert game.phase == PHASE_ROUND_END
    assert first.numbers == [] and first.modifiers == []
    assert second.numbers == []


def test_flip7_match_leader_is_the_unique_score_above_target():
    game = _make_game(player_count=2, start=False)
    game.game_active = True
    first, second = game.players
    first.total_score = 201
    second.total_score = 100
    assert game._match_leader() == (first, 201)

    second.total_score = 201
    assert game._match_leader() is None

    first.total_score = 100
    second.total_score = 0
    assert game._match_leader() is None


def test_flip7_match_reaches_end_phase_when_target_is_met():
    game = _make_game(player_count=2)
    first, second = game.players
    first.total_score = 198
    first.numbers = [5]
    first.round_status = STATUS_STAYED
    second.round_status = STATUS_BUSTED
    game.phase = PHASE_PLAYING

    game._end_round()

    assert game.phase == PHASE_MATCH_END
    assert game.status == "finished"
    assert first.total_score == 203


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------


def test_flip7_turn_menu_orders_areas_below_main_actions():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    user = game.get_user(actor)
    game.before_menu_build(actor)
    build = game.build_menu_items(actor, user)

    ids = [item.id for item in build.items]
    assert "hit" in ids
    assert "stay" in ids
    area_ids = [item_id for item_id in ids if item_id.startswith("flip7_area_")]
    assert len(area_ids) == 2
    assert ids.index("hit") < ids.index(area_ids[0])
    assert ids.index("stay") < ids.index(area_ids[0])
    assert all(item.read_only for item in build.items if item.id in area_ids)


def test_flip7_turn_menu_swaps_to_choice_actions():
    game = _make_game(player_count=3)
    actor = game.players[0]
    game._resolve_card(actor, _card(CARD_STOP, uid=1), forced=False, chooser=actor)
    game.before_menu_build(actor)

    ids = [resolved.action.id for resolved in game.get_all_visible_actions(actor)]
    assert "hit" not in ids
    assert "stay" not in ids
    for target in game._choice_targets():
        assert f"choose_stop_{game._slot_of(target)}" in ids


def test_flip7_information_actions_touch_visibility():
    desktop = _make_game(player_count=2)
    mobile = _make_game(player_count=2, mobile_user=True)

    for game in (desktop, mobile):
        actor = game.players[0]
        for action_id in ("check_area", "check_table", "check_deck"):
            action = game.find_action(actor, action_id)
            resolved = game.resolve_action(actor, action)
            expected = game.is_touch_player(actor)
            assert resolved.visible is expected, (action_id, expected)
            assert resolved.enabled is True


def test_flip7_read_card_actions_are_hidden_but_enabled():
    game = _make_game(player_count=2)
    actor = game.players[0]
    game.before_menu_build(actor)
    for position in range(1, 11):
        action = game.find_action(actor, f"read_card_{position}")
        assert action is not None
        resolved = game.resolve_action(actor, action)
        assert resolved.visible is False
        assert resolved.enabled is True


# ---------------------------------------------------------------------------
# Keybinds
# ---------------------------------------------------------------------------


def test_flip7_keybind_setup_states_and_actions():
    game = _make_game(player_count=2, start=False)

    def actions_for(key):
        return {
            tuple(keybind.actions) for keybind in game._keybinds[key]
        }

    assert actions_for("space") == {("hit",)}
    assert actions_for("h") == {("stay",)}
    assert actions_for("c") == {("check_area",)}
    assert actions_for("shift+c") == {("check_table",)}
    assert actions_for("d") == {("check_deck",)}
    for key in (str(n) for n in range(1, 10)):
        position = int(key)
        assert actions_for(key) == {(f"read_card_{position}",)}
    assert actions_for("0") == {("read_card_10",)}

    for key in ("space", "h", "c", "shift+c", "d", "1", "5", "9", "0"):
        assert all(k.state == KeybindState.ACTIVE for k in game._keybinds[key]), key


def test_flip7_keybind_c_speaks_the_area_even_though_hidden():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    actor.numbers = [5]
    user = game.get_user(actor)
    user.clear_messages()

    game.handle_event(actor, {"type": "keybind", "key": "c"})

    spoken = [
        message.data["text"]
        for message in user.messages
        if message.type == "speak" and message.data.get("buffer") == "game"
    ]
    assert any("Total" in text for text in spoken)


def test_flip7_keybind_reads_card_positions():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    actor.numbers = [5, 9]
    user = game.get_user(actor)
    user.clear_messages()

    game.handle_event(actor, {"type": "keybind", "key": "1"})

    spoken = [
        message.data["text"]
        for message in user.messages
        if message.type == "speak" and message.data.get("buffer") == "game"
    ]
    assert "Card 1: 5." in spoken

    user.clear_messages()
    game.handle_event(actor, {"type": "keybind", "key": "0"})
    spoken = [
        message.data["text"]
        for message in user.messages
        if message.type == "speak" and message.data.get("buffer") == "game"
    ]
    assert "You do not have card 10 yet." in spoken


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_flip7_game_state_serializes_round_trip():
    game = _make_game(player_count=2)
    first = game.players[0]
    first.numbers = [2, 7]
    first.modifiers = [4]
    first.total_score = 33
    first.round_status = STATUS_STAYED

    raw = game.to_json()
    data = json.loads(raw)
    assert data["round"] == 1

    loaded = Flip7Game.from_json(raw)
    assert loaded.options.target_score == 200
    assert loaded.players[0].numbers == [2, 7]
    assert loaded.players[0].modifiers == [4]
    assert loaded.players[0].total_score == 33
    assert loaded.players[0].round_status == STATUS_STAYED


# ---------------------------------------------------------------------------
# Bot completion
# ---------------------------------------------------------------------------


def test_flip7_bots_play_a_full_match_to_finished():
    game = _make_game(player_count=3, start=True, bot_all=True, target_score=50)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=60000)
    assert game.phase == PHASE_MATCH_END
    scores = [p.total_score for p in game.players]
    assert max(scores) >= 50