"""Truco Paulista and Valencian Truc: rules, flows, spectators, gestures, locales."""

import random
import re
from pathlib import Path

import pytest

from ..games.registry import GameRegistry
from ..games.truco import decks, rules
from ..games.truco.cards import (
    SUIT_BASTOS,
    SUIT_COPAS,
    SUIT_ESPADAS,
    SUIT_OROS,
    TrucoCard,
)
from ..games.truco.game import TrucoGame, TrucoOptions
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
Localization.init(ROOT / "server" / "locales")
LOCALES = ("en", "es", "pt", "vi")


def PC(rank, suit) -> TrucoCard:
    return TrucoCard(
        id=decks.FRENCH_SUITS.index(suit) * 10 + decks.FRENCH_RANKS.index(rank),
        rank=rank,
        suit=suit,
    )


def VC(rank, suit) -> TrucoCard:
    return next(
        c for c in decks.build_spanish_deck() if c.rank == rank and c.suit == suit
    )


def make(
    kind, count=2, *, start=True, client_type="python", seed=3, bots=False, **opts
):
    mode = opts.pop("mode", None) or {2: "individual", 4: "2v2", 6: "3v3"}[count]
    if kind == "brazilian":
        game = TrucoGame(options=TrucoOptions(variant="brazilian", team_mode=mode))
    else:
        length = opts.pop("target_length", "18")
        game = TrucoGame(
            options=TrucoOptions(
                variant="spanish", team_mode=mode, spanish_length=length
            )
        )
    game.setup_keybinds()
    for i in range(count):
        name = f"Player{i + 1}"
        user = Bot(name, uuid=f"p{i + 1}") if bots else MockUser(name, uuid=f"p{i + 1}")
        if not bots:
            user.client_type = client_type
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        random.seed(seed)
        game.on_start()
        game.flush_menus()
    return game


def set_hands(game, hands, vira=None):
    for player, hand in zip(game.players, hands):
        player.hand = list(hand)
        player.dealt = list(hand)
        player.has_flor = False
    if vira is not None:
        game.vira = vira
    game.refresh_menus()
    game.flush_menus()


def act(game, player, action_id):
    game.execute_action(player, action_id)
    game.flush_menus()


def texts(game, player) -> str:
    return " | ".join(game.get_user(player).get_spoken_messages())


def clear(game):
    for player in (
        game.players + game.spectators if hasattr(game, "spectators") else game.players
    ):
        user = game.get_user(player)
        if user is not None:
            user.messages.clear() if hasattr(user, "messages") else None


def mano(game):
    return game.get_player_by_id(game.turn_player_ids[game.mano_index])


def other(game, player):
    return next(p for p in game.players if p is not player)


def play_first(game):
    player = game.current_player
    act(game, player, f"play_{player.hand[0].id}")
    return player


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_one_game_with_three_variants():
    assert GameRegistry.get("truco") is TrucoGame
    assert GameRegistry.get("trucobrazilian") is None
    assert GameRegistry.get("trucospanish") is None
    assert [c for c in TrucoOptions().variant and ["argentine", "brazilian", "spanish"]]
    assert TrucoOptions().variant == "argentine"
    assert (TrucoGame.get_min_players(), TrucoGame.get_max_players()) == (2, 6)


def test_variant_option_selects_rules_and_hides_irrelevant_options():
    argentine = TrucoGame(options=TrucoOptions())
    brazilian = TrucoGame(options=TrucoOptions(variant="brazilian"))
    spanish = TrucoGame(options=TrucoOptions(variant="spanish"))
    assert argentine.LADDER[0] == "truco" and len(argentine.LADDER) == 3
    assert (
        brazilian.LADDER == ("truco", "seis", "nove", "doze") and brazilian.target == 12
    )
    assert spanish.LADDER[-1] == "jocfora" and spanish.target == 24
    assert argentine.options.is_option_visible("flor")
    assert not brazilian.options.is_option_visible("flor")
    assert not spanish.options.is_option_visible("flor")
    assert argentine.options.is_option_visible("target_length")
    assert not spanish.options.is_option_visible("target_length")
    assert spanish.options.is_option_visible("spanish_length")
    assert not brazilian.options.is_option_visible("spanish_length")


def test_variant_survives_save_and_restore():
    game = make("brazilian", 2)
    data = game.to_json()
    restored = TrucoGame.from_json(data)
    assert restored.options.variant == "brazilian"
    assert restored.vira == game.vira and restored.LADDER == game.LADDER


def test_spanish_variant_rejects_six_players_and_odd_counts():
    game = make("spanish", 4, start=False, mode="2v2")
    assert not game.prestart_validate()
    six = make("spanish", 4, start=False, mode="2v2")
    six.options.team_mode = "3v3"
    assert six.prestart_validate()
    game = make("spanish", 3, start=False, mode="individual")
    assert game.prestart_validate()


# ---------------------------------------------------------------------------
# Paulista cards and rules
# ---------------------------------------------------------------------------


def test_brazilian_deck_has_forty_french_cards():
    deck = decks.build_french_deck()
    assert len(deck) == 40 and len({c.id for c in deck}) == 40
    assert {c.rank for c in deck} == set(decks.FRENCH_RANKS)


@pytest.mark.parametrize(
    ("vira", "manilha"),
    [(4, 5), (7, 12), (12, 11), (13, 1), (1, 2), (2, 3), (3, 4)],
)
def test_manilha_follows_the_vira(vira, manilha):
    assert decks.manilha_rank(PC(vira, decks.SUIT_HEARTS)) == manilha


def test_brazilian_strength_order_and_manilha_suits():
    vira = PC(2, decks.SUIT_DIAMONDS)  # manilha is 3
    order = [3, 2, 1, 13, 11, 12, 7, 6, 5, 4]
    natural = [decks.brazilian_power(PC(r, decks.SUIT_HEARTS), vira) for r in order[1:]]
    assert natural == sorted(natural, reverse=True)
    manilhas = [decks.brazilian_power(PC(3, s), vira) for s in decks.FRENCH_SUITS]
    assert manilhas == sorted(manilhas)
    assert decks.brazilian_power(PC(3, decks.SUIT_CLUBS), vira) == max(manilhas)
    assert min(manilhas) > decks.brazilian_power(PC(2, decks.SUIT_CLUBS), vira)


def test_brazilian_hand_decision_annuls_three_ties():
    assert rules.decide_hand_annulling([None, None, None]) == rules.ANNULLED
    assert rules.decide_hand_annulling([None, 1]) == 1
    assert rules.decide_hand_annulling([0, None]) == 0
    assert rules.decide_hand_annulling([None, None, 1]) == 1
    assert rules.decide_hand_annulling([0, 1, None]) == 0


def test_brazilian_ladder_values():
    game = make("brazilian", 2)
    assert [game._level_points(level) for level in game.LADDER] == [3, 6, 9, 12]
    assert [game._level_points(level, accepted=False) for level in game.LADDER] == [
        1,
        3,
        6,
        9,
    ]
    assert game._level_points(None) == 1


def test_brazilian_start_turns_up_vira_and_has_no_envido_or_mazo():
    game = make("brazilian", 2)
    assert game.vira is not None
    assert len(game.deck) == 40 - 6 - 1
    mine = mano(game)
    ids = [r.action.id for r in game.get_all_visible_actions(mine)]
    assert "call_truco" in ids
    assert not {"call_envido", "mazo", "call_contraflor"} & set(ids)
    assert "Mão de onze" not in texts(game, mine)
    assert "vira" in texts(game, mine).lower()


def test_brazilian_three_ties_annul_the_hand_and_redeal():
    game = make("brazilian", 2)
    a = mano(game)
    set_hands(
        game,
        [
            [
                PC(7, decks.SUIT_HEARTS),
                PC(6, decks.SUIT_HEARTS),
                PC(5, decks.SUIT_HEARTS),
            ],
            [PC(7, decks.SUIT_CLUBS), PC(6, decks.SUIT_CLUBS), PC(5, decks.SUIT_CLUBS)],
        ]
        if a is game.players[0]
        else [
            [PC(7, decks.SUIT_CLUBS), PC(6, decks.SUIT_CLUBS), PC(5, decks.SUIT_CLUBS)],
            [
                PC(7, decks.SUIT_HEARTS),
                PC(6, decks.SUIT_HEARTS),
                PC(5, decks.SUIT_HEARTS),
            ],
        ],
        vira=PC(2, decks.SUIT_DIAMONDS),
    )
    first_round = game.round
    for _ in range(6):
        play_first(game)
    assert not game.hand_active
    assert game._scores() == [0, 0]
    assert "annulled" in texts(game, a)
    for _ in range(200):
        game.on_tick()
        game.flush_menus()
        if game.hand_active:
            break
    assert game.hand_active and game.round == first_round + 1


def test_brazilian_truco_raise_and_refusal_values():
    game = make("brazilian", 2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "call_truco")  # seis
    assert game.truco_pending == "seis"
    act(game, a, "call_truco")  # nove
    act(game, b, "decline")
    assert game._scores()[game._team_index(a)] == 6
    assert game._scores()[game._team_index(b)] == 0


# ---------------------------------------------------------------------------
# Mão de onze and mão de ferro
# ---------------------------------------------------------------------------


def set_scores(game, first, second):
    game._team_manager.teams[0].total_score = first
    game._team_manager.teams[1].total_score = second
    game._sync_scores()


def test_mao_de_onze_is_offered_to_the_team_with_eleven():
    game = make("brazilian", 2)
    set_scores(game, 11, 4)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    assert game.onze_pending and game.onze_team == 0
    holder, rival = game.players[0], game.players[1]
    holder_ids = [r.action.id for r in game.get_all_visible_actions(holder)]
    rival_ids = [r.action.id for r in game.get_all_visible_actions(rival)]
    assert "accept" in holder_ids and "decline" in holder_ids
    assert "accept" not in rival_ids
    assert not any(i.startswith("play_") for i in holder_ids)
    assert "decide" in texts(game, rival) or "11" in texts(game, rival)


def test_mao_de_onze_play_makes_the_hand_worth_three_without_calls():
    game = make("brazilian", 2)
    set_scores(game, 11, 4)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    holder = game.players[0]
    act(game, holder, "accept")
    assert not game.onze_pending and game.no_calls and game.hand_base == 3
    player = game.current_player
    assert game._call_error(player, "call_truco")
    ids = [r.action.id for r in game.get_all_visible_actions(player)]
    assert "call_truco" not in ids


def test_mao_de_onze_run_gives_one_point_to_the_other_side():
    game = make("brazilian", 2)
    set_scores(game, 11, 4)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    act(game, game.players[0], "decline")
    assert game._scores() == [11, 5]
    assert not game.hand_active


def test_mao_de_onze_won_hand_ends_the_game():
    game = make("brazilian", 2)
    set_scores(game, 11, 4)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    holder, _rival = game.players
    act(game, holder, "accept")
    set_hands(
        game,
        [
            [
                PC(3, decks.SUIT_HEARTS),
                PC(2, decks.SUIT_HEARTS),
                PC(1, decks.SUIT_HEARTS),
            ],
            [PC(4, decks.SUIT_CLUBS), PC(5, decks.SUIT_CLUBS), PC(6, decks.SUIT_CLUBS)],
        ],
        vira=PC(7, decks.SUIT_DIAMONDS),
    )
    for _ in range(4):
        if game.status != "playing":
            break
        play_first(game)
    assert game.status != "playing"
    assert game._scores()[0] == 12


def test_mao_de_ferro_blocks_calls_and_decides_the_game():
    game = make("brazilian", 2)
    set_scores(game, 11, 11)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    assert game.no_calls and not game.onze_pending
    assert "ferro" in texts(game, game.players[0])
    player = game.current_player
    assert game._call_error(player, "call_truco")
    set_hands(
        game,
        [
            [
                PC(3, decks.SUIT_HEARTS),
                PC(2, decks.SUIT_HEARTS),
                PC(1, decks.SUIT_HEARTS),
            ],
            [PC(4, decks.SUIT_CLUBS), PC(5, decks.SUIT_CLUBS), PC(6, decks.SUIT_CLUBS)],
        ],
        vira=PC(7, decks.SUIT_DIAMONDS),
    )
    for _ in range(4):
        if game.status != "playing":
            break
        play_first(game)
    assert game.status != "playing"
    assert max(game._scores()) == 12


def test_mao_de_onze_in_teams_lets_any_live_member_answer():
    game = make("brazilian", 4)
    set_scores(game, 11, 2)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    team_members = [p for p in game.players if game._team_index(p) == 0]
    assert {p.id for p in game._responders()} == {p.id for p in team_members}
    act(game, team_members[1], "decline")
    assert game._scores() == [11, 3]


def test_brazilian_read_vira_is_public_and_works_for_spectators():
    game = make("brazilian", 2)
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher_user.client_type = "mobile"
    watcher = game.add_spectator("Watcher", watcher_user)
    game.refresh_menus(watcher)
    game.flush_menus()
    ids = [r.action.id for r in game.get_all_visible_actions(watcher)]
    assert "read_vira" in ids and "read_hand" not in ids
    watcher_user.messages.clear()
    game.handle_event(watcher, {"type": "keybind", "key": "v"})
    assert "vira" in texts_user(watcher_user).lower()


def texts_user(user) -> str:
    return " | ".join(user.get_spoken_messages())


# ---------------------------------------------------------------------------
# Valencian cards and rules
# ---------------------------------------------------------------------------


def test_spanish_deck_and_strength_order():
    deck = decks.build_spanish_deck()
    assert len(deck) == 22 and len({c.id for c in deck}) == 22
    order = [
        VC(1, SUIT_ESPADAS),
        VC(1, SUIT_BASTOS),
        VC(7, SUIT_ESPADAS),
        VC(7, SUIT_OROS),
        VC(3, SUIT_COPAS),
        VC(6, SUIT_OROS),
        VC(5, SUIT_OROS),
        VC(4, SUIT_OROS),
    ]
    powers = [decks.spanish_power(c) for c in order]
    assert powers == sorted(powers, reverse=True) and len(set(powers)) == len(powers)
    assert decks.spanish_power(VC(7, SUIT_COPAS)) == decks.spanish_power(
        VC(7, SUIT_BASTOS)
    )
    assert decks.spanish_power(VC(7, SUIT_COPAS)) < decks.spanish_power(
        VC(3, SUIT_COPAS)
    )


def test_envit_chain_rules_and_values():
    assert rules.can_add_envit_call([], rules.ENVIDO)
    assert not rules.can_add_envit_call([], rules.REAL_ENVIDO)
    assert rules.can_add_envit_call([rules.ENVIDO], rules.REAL_ENVIDO)
    assert rules.can_add_envit_call([rules.ENVIDO], rules.FALTA_ENVIDO)
    assert not rules.can_add_envit_call([rules.ENVIDO, rules.REAL_ENVIDO], rules.ENVIDO)
    assert not rules.can_add_envit_call([rules.FALTA_ENVIDO], rules.FALTA_ENVIDO)
    assert rules.envit_accepted_points([rules.ENVIDO], 0) == 2
    assert rules.envit_accepted_points([rules.ENVIDO, rules.REAL_ENVIDO], 0) == 4
    assert rules.envit_accepted_points([rules.ENVIDO, rules.FALTA_ENVIDO], 7) == 7
    assert rules.envit_declined_points([rules.ENVIDO]) == 1
    assert rules.envit_declined_points([rules.ENVIDO, rules.REAL_ENVIDO]) == 2
    # A refused raise pays what the step below it already made: 1 / 2 / 4.
    assert rules.envit_declined_points([rules.FALTA_ENVIDO]) == 1
    assert rules.envit_declined_points([rules.ENVIDO, rules.FALTA_ENVIDO]) == 2
    assert (
        rules.envit_declined_points(
            [rules.ENVIDO, rules.REAL_ENVIDO, rules.FALTA_ENVIDO]
        )
        == 4
    )
    assert rules.envit_falta_points([5, 9], 24) == 15


def test_spanish_default_length_and_ladder():
    assert TrucoOptions(variant="spanish").spanish_length == "24"
    game = make("spanish", 2, target_length="24")
    # Two cames of 24 points (Campionat Faller, UPV); joc fora is both cames.
    assert game.target == 24 and game.CAMES_TO_WIN == 2
    assert [game._level_points(level) for level in game.LADDER] == [2, 3, 4, 48]
    assert game._level_points("jocfora", accepted=False) == 4
    assert len(game.deck) == 22 - 6


def test_spanish_envit_declined_and_torna():
    game = make("spanish", 2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_envido")
    act(game, b, "decline")
    assert game._scores()[game._team_index(a)] == 1

    game = make("spanish", 2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_envido")
    act(game, b, "call_real_envido")  # torna
    act(game, a, "decline")
    assert game._scores()[game._team_index(b)] == 2


def test_spanish_torna_accepted_pays_four_to_the_better_envit():
    game = make("spanish", 2)
    a = mano(game)
    b = other(game, a)
    strong = [VC(7, SUIT_OROS), VC(6, SUIT_OROS), VC(3, SUIT_COPAS)]
    weak = [VC(4, SUIT_ESPADAS), VC(5, SUIT_BASTOS), VC(3, SUIT_OROS)]
    set_hands(game, [strong, weak] if a is game.players[0] else [weak, strong])
    act(game, a, "call_envido")
    act(game, b, "call_real_envido")
    act(game, a, "accept")
    assert game._scores()[game._team_index(a)] == 4


def test_spanish_joc_fora_wins_the_game():
    game = make("spanish", 2)
    a = mano(game)
    b = other(game, a)
    strong = [VC(1, SUIT_ESPADAS), VC(1, SUIT_BASTOS), VC(7, SUIT_ESPADAS)]
    weak = [VC(4, SUIT_OROS), VC(4, SUIT_COPAS), VC(5, SUIT_OROS)]
    set_hands(game, [strong, weak] if a is game.players[0] else [weak, strong])
    act(game, a, "call_truco")
    act(game, b, "call_truco")
    act(game, a, "call_truco")
    act(game, b, "call_truco")
    assert game.truco_pending == "jocfora"
    assert game._call_error(a, "call_truco")
    act(game, a, "accept")
    for _ in range(6):
        if game.status != "playing":
            break
        play_first(game)
    assert game.status != "playing"
    assert game.winner_team_index == game._team_index(a)


def test_spanish_fold_gives_up_for_the_whole_team():
    game = make("spanish", 4)
    a = mano(game)
    mates = [p for p in game.players if game._team_index(p) == game._team_index(a)]
    rivals = [p for p in game.players if game._team_index(p) != game._team_index(a)]
    clear_all(game)
    act(game, a, "mazo")
    assert all(p.folded for p in mates)
    assert not game.hand_active
    assert game._scores()[game._team_index(rivals[0])] >= 1
    assert game._scores()[game._team_index(a)] == 0


def clear_all(game):
    for player in game.players:
        user = game.get_user(player)
        if user is not None:
            user.messages.clear()


def test_spanish_winning_a_came_resets_the_score_and_two_cames_win():
    game = make("spanish", 2)
    set_scores(game, 17, 9)
    clear_all(game)
    assert game._award(0, 2, "truco-reason-hand") is False
    assert game.status == "playing"
    assert game._scores() == [0, 0] and game.came_wins == [1, 0]
    spoken = " ".join(texts(game, p) for p in game.players).lower()
    assert "came" in spoken
    # Points beyond the came are not carried over; the second came is won the same way.
    set_scores(game, 17, 3)
    assert game._award(0, 1, "truco-reason-hand") is True
    assert game.came_wins == [2, 0] and game.winner_team_index == 0
    assert game.status != "playing"


def test_spanish_cames_can_be_split_between_the_sides():
    game = make("spanish", 2)
    set_scores(game, 18 - 1, 5)
    game._award(0, 1, "truco-reason-hand")
    set_scores(game, 4, 17)
    assert game._award(1, 1, "truco-reason-hand") is False
    assert game.came_wins == [1, 1] and game.status == "playing"
    set_scores(game, 2, 17)
    assert game._award(1, 3, "truco-reason-hand") is True
    assert game.winner_team_index == 1


def test_spanish_la_falta_is_measured_inside_the_current_came():
    game = make("spanish", 2)
    set_scores(game, 11, 4)
    assert game._falta_points() == 7
    game.came_wins = [1, 0]
    set_scores(game, 3, 6)
    assert game._falta_points() == 12


def test_spanish_scores_report_cames_and_results_rank_by_cames():
    game = make("spanish", 2)
    set_scores(game, 17, 12)
    game._award(0, 2, "truco-reason-hand")
    clear_all(game)
    game._action_check_scores(game.players[0], "check_scores")
    assert "1" in texts(game, game.players[0])
    set_scores(game, 5, 17)
    game._award(1, 1, "truco-reason-hand")
    assert game.came_wins == [1, 1]
    set_scores(game, 17, 16)
    game._award(0, 2, "truco-reason-hand")
    result = game.build_game_result()
    rankings = result.custom_data["team_rankings"]
    assert (
        rankings[0]["members"] == [game.players[0].name] and rankings[0]["score"] == 2
    )
    assert result.custom_data["winner_ids"] == [game.players[0].id]


def test_spanish_joc_fora_wins_both_cames_at_once():
    game = make("spanish", 2)
    set_scores(game, 3, 3)
    assert game._award(1, game._level_points("jocfora"), "truco-reason-truc") is True
    assert game.winner_team_index == 1 and game.came_wins[1] == 2


# ---------------------------------------------------------------------------
# Bots: complete games
# ---------------------------------------------------------------------------


def run_bots(game, limit=80000):
    for _ in range(limit):
        game.on_tick()
        game.flush_menus()
        if game.status != "playing":
            return
    raise AssertionError("game did not finish")


@pytest.mark.parametrize("count", [2, 4, 6])
def test_brazilian_bot_only_games_finish(count):
    for seed in range(3):
        random.seed(seed)
        game = make("brazilian", count, bots=True, start=False)
        game.on_start()
        game.flush_menus()
        run_bots(game)
        assert max(game._scores()) == 12


@pytest.mark.parametrize(
    ("count", "length"), [(2, "18"), (2, "24"), (4, "18"), (4, "24")]
)
def test_spanish_bot_only_games_finish(count, length):
    for seed in range(3):
        random.seed(seed)
        game = make("spanish", count, bots=True, start=False, target_length=length)
        game.on_start()
        game.flush_menus()
        run_bots(game)
        assert max(game.came_wins) == 2
        assert game.winner_team_index in (0, 1)


# ---------------------------------------------------------------------------
# Spectators
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
def test_spectator_joining_mid_hand_sees_only_public_actions(kind):
    game = make(kind, 2)
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher_user.client_type = "mobile"
    watcher = game.add_spectator("Watcher", watcher_user)
    game.refresh_menus(watcher)
    game.flush_menus()
    ids = [r.action.id for r in game.get_all_visible_actions(watcher)]
    assert "read_table" in ids and "read_calls" in ids
    private = {
        "read_hand",
        "mazo",
        "accept",
        "decline",
        "call_truco",
        "call_envido",
        CARD_GESTURE,
    }
    assert not private & set(ids)
    assert not any(i.startswith("play_") for i in ids)
    # Spectators cannot act even by forging the action.
    before = (game.truco_level, game.truco_pending, list(game.trick_results))
    game.execute_action(watcher, "call_truco")
    game.handle_event(watcher, {"type": "keybind", "key": "shift+enter"})
    assert before == (game.truco_level, game.truco_pending, list(game.trick_results))
    # They hear public calls but never a player's cards.
    a = mano(game)
    act(game, a, "call_truco")
    heard = texts_user(watcher_user)
    assert "Truc" in heard
    assert "Your cards" not in heard


CARD_GESTURE = "card_info_gesture"


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
def test_spectator_never_hears_private_cards_during_a_bot_game(kind):
    random.seed(5)
    game = make(kind, 2, bots=True, start=False)
    watcher_user = MockUser("Watcher", uuid="watcher")
    game.add_spectator("Watcher", watcher_user)
    game.on_start()
    game.flush_menus()
    run_bots(game)
    heard = texts_user(watcher_user)
    assert "Your cards" not in heard
    assert heard


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
@pytest.mark.parametrize("locale", LOCALES)
def test_every_announcement_renders_in_every_locale(kind, locale):
    random.seed(11)
    game = make(kind, 2, bots=True, start=False)
    watcher_user = MockUser("Watcher", uuid="watcher", locale=locale)
    game.add_spectator("Watcher", watcher_user)
    game.on_start()
    game.flush_menus()
    run_bots(game)
    heard = texts_user(watcher_user)
    assert heard
    assert not re.search(r"\b(truco|trucobrazilian|trucospanish)-[a-z]", heard)
    assert "{" not in heard and "$" not in heard


# ---------------------------------------------------------------------------
# Touch gestures and descriptions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
def test_shift_enter_on_a_card_reads_its_strength_on_touch(kind):
    game = make(kind, 2, client_type="web")
    player = game.current_player
    card = player.hand[0]
    user = game.get_user(player)
    user.messages.clear()
    game.handle_event(
        player,
        {
            "type": "keybind",
            "key": "enter",
            "shift": True,
            "menu_item_id": f"play_{card.id}",
        },
    )
    heard = texts_user(user)
    assert "beats" in heard
    assert game._format_card(card, "en") in heard
    assert len(player.hand) == 3  # reading never plays the card
    assert game.current_player is player


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
def test_shift_enter_is_a_silent_no_op_on_desktop_and_non_actions(kind):
    game = make(kind, 2, client_type="python")
    player = game.current_player
    user = game.get_user(player)
    user.messages.clear()
    game.handle_event(
        player,
        {
            "type": "keybind",
            "key": "enter",
            "shift": True,
            "menu_item_id": f"play_{player.hand[0].id}",
        },
    )
    assert not user.get_spoken_messages()
    touch = make(kind, 2, client_type="web")
    toucher = touch.current_player
    tuser = touch.get_user(toucher)
    tuser.messages.clear()
    touch.handle_event(
        toucher,
        {
            "type": "keybind",
            "key": "enter",
            "shift": True,
            "menu_item_id": "whose_turn",
        },
    )
    assert not tuser.get_spoken_messages()


def test_descriptions_explain_cards_calls_and_answers():
    game = make("brazilian", 2)
    a = mano(game)
    b = other(game, a)
    card_id = f"play_{a.hand[0].id}"
    assert "beats" in game._get_action_description(a, card_id)
    desc = game._get_action_description(a, "call_truco")
    assert "3" in desc and "1" in desc
    act(game, a, "call_truco")
    assert "Truco" in game._get_action_description(b, "accept")
    assert "1" in game._get_action_description(b, "decline")
    assert "6" in game._get_action_description(b, "call_truco")


def test_onze_answer_descriptions():
    game = make("brazilian", 2)
    set_scores(game, 11, 0)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    holder = game.players[0]
    assert "3" in game._get_action_description(holder, "accept")
    assert "1 point" in game._get_action_description(holder, "decline")


def test_spanish_descriptions_use_spanish_values():
    game = make("spanish", 2)
    a = mano(game)
    desc = game._get_action_description(a, "call_envido")
    assert "Envit" in desc and "2" in desc
    assert "Retruc" in game._get_action_description(
        a, "call_truco"
    ) or "Truc" in game._get_action_description(a, "call_truco")
    assert "whole team" in game._get_action_description(a, "mazo")


# ---------------------------------------------------------------------------
# Localization files
# ---------------------------------------------------------------------------


def locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and "=" in line
        and not line[0].isspace()
    }


@pytest.mark.parametrize("name", ["truco", "trucobrazilian", "trucospanish"])
def test_locale_parity(name):
    base = locale_keys(ROOT / "server" / "locales" / "en" / f"{name}.ftl")
    for lang in ("es", "pt", "vi"):
        assert locale_keys(ROOT / "server" / "locales" / lang / f"{name}.ftl") == base


def test_variant_keys_used_in_code_exist():
    available: set[str] = set()
    for name in ("truco", "trucobrazilian", "trucospanish"):
        available |= locale_keys(ROOT / "server" / "locales" / "en" / f"{name}.ftl")
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "server" / "games" / "truco" / "engine.py",
            ROOT / "server" / "games" / "truco" / "decks.py",
            ROOT / "server" / "games" / "truco" / "variants.py",
            ROOT / "server" / "games" / "truco" / "game.py",
        ]
    )
    used = set(
        re.findall(r'"((?:truco|trucobrazilian|trucospanish)-[a-z0-9-]+)"', source)
    )
    dynamic = {
        "truco-reveal-",
        "trucobrazilian-onze-",
        "trucobrazilian-suit-",
        "trucospanish-came",
        "truco-half-buenas",
    }
    missing = {
        key
        for key in used
        if key not in available
        and not any(key.startswith(prefix) for prefix in dynamic)
    }
    assert not missing, missing
    for who in ("you", "player"):
        for word in ("play", "run"):
            assert f"trucobrazilian-onze-{word}-{who}" in available
        assert f"trucospanish-came-{who}" in available
    assert (
        "trucospanish-came-your-team" in available
        and "trucospanish-came-team" in available
    )


# ---------------------------------------------------------------------------
# Gestures on every important action, variant wording, status reads
# ---------------------------------------------------------------------------


def gesture(game, player, item_id):
    user = game.get_user(player)
    user.messages.clear()
    game.handle_event(
        player,
        {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": item_id},
    )
    return texts_user(user)


@pytest.mark.parametrize("kind", ["brazilian", "spanish"])
def test_gesture_describes_calls_answers_and_fold_on_touch(kind):
    game = make(kind, 2, client_type="web")
    a = mano(game)
    b = other(game, a)
    heard = gesture(game, a, "call_truco")
    assert "points" in heard
    if kind == "spanish":
        assert "Envit" in gesture(game, a, "call_envido")
        assert "whole team" in gesture(game, a, "mazo")
    act(game, a, "call_truco")
    assert "refuse" in gesture(game, b, "decline").lower() or "Refuse" in gesture(
        game, b, "decline"
    )
    assert "Accept" in gesture(game, b, "accept")
    assert gesture(game, b, "call_truco")  # raise value
    assert gesture(game, b, "not_an_action") == ""


def test_gesture_works_in_the_mao_de_onze_answers():
    game = make("brazilian", 2, client_type="web")
    set_scores(game, 11, 0)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    holder = game.players[0]
    assert "3 points" in gesture(game, holder, "accept")
    assert "1 point" in gesture(game, holder, "decline")


def test_brazilian_wording_has_no_argentine_terms():
    game = make("brazilian", 2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    heard = texts(game, a) + texts(game, b)
    assert "Quiero" not in heard
    act(game, b, "accept")
    assert "Aceito" in texts(game, a)
    game.refresh_menus()
    game.flush_menus()
    for player in (a, b):
        spoken = texts(game, player)
        assert "Quiero" not in spoken and "mazo" not in spoken.lower()
    assert game._call_error(b, "call_envido")


def test_spanish_wording_uses_spanish_terms():
    game = make("spanish", 2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_envido")
    heard = texts(game, b)
    assert "Vull" in heard and "Quiero" not in heard and "Envido" not in heard
    act(game, b, "decline")
    assert "No vull" in texts(game, a)
    game2 = make("spanish", 2)
    a2 = mano(game2)
    game2.truco_level = "truco"
    game2.truco_raiser_team = game2._team_index(a2)
    reason = game2._call_error(a2, "call_envido")
    assert reason == "trucospanish-error-envit-closed"


def test_spanish_validation_errors_use_spanish_variant_text():
    game = make("spanish", 3, start=False, mode="individual")
    errors = game.prestart_validate()
    assert any(
        e[0] == "trucospanish-error-bad-count" for e in errors if isinstance(e, tuple)
    )


def test_read_calls_reports_mao_de_onze_and_no_call_hands():
    game = make("brazilian", 2)
    set_scores(game, 11, 0)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    rival = game.players[1]
    clear_all(game)
    act(game, rival, "read_calls")
    assert "decide" in texts(game, rival)
    act(game, game.players[0], "accept")
    clear_all(game)
    act(game, rival, "read_calls")
    assert "3 points" in texts(game, rival)


def test_every_variant_message_override_exists_in_all_locales():
    from ..games.truco.variants import RULE_SETS

    keys = {}
    for lang in LOCALES:
        collected: set[str] = set()
        for name in ("truco", "trucobrazilian", "trucospanish"):
            collected |= locale_keys(ROOT / "server" / "locales" / lang / f"{name}.ftl")
        keys[lang] = collected
    for rule_set in RULE_SETS.values():
        for original, replacement in getattr(rule_set, "MSG", {}).items():
            for lang in LOCALES:
                assert original in keys[lang] and replacement in keys[lang], (
                    lang,
                    replacement,
                )


# ---------------------------------------------------------------------------
# Mão de ferro is played face down; mão de onze partners see each other's cards
# ---------------------------------------------------------------------------


def card_names(game, locale="en"):
    deck = decks.build_french_deck() if hasattr(decks, "build_french_deck") else []
    names = set()
    for card in deck:
        names.add(game._format_card(card, locale))
    return names


def all_text(game, player) -> str:
    return texts(game, player)


def test_mao_de_ferro_hides_every_private_card_channel():
    game = make("brazilian", 2, client_type="mobile")
    set_scores(game, 11, 11)
    for user in (game.get_user(p) for p in game.players):
        user.messages.clear()
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    assert game.blind_hand and game.no_calls
    for player in game.players:
        shown = [c for c in player.dealt]
        spoken = texts(game, player)
        labels = " | ".join(
            game._get_card_label(player, f"play_{c.id}") for c in player.hand
        )
        descriptions = " | ".join(
            game._get_action_description(player, f"play_{c.id}") or ""
            for c in player.hand
        )
        game.get_user(player).messages.clear()
        game._action_read_hand(player, "read_hand")
        read = texts(game, player)
        probes = []
        for card in shown:
            probes.append(game._format_card(card, "en"))
        for text in (spoken, labels, descriptions, read):
            for probe in probes:
                assert probe not in text, (probe, text)
        assert "face-down" in labels or "face down" in (spoken + read)
        assert len(game._ordered_hand(player)) == 3


def test_mao_de_ferro_cards_are_revealed_only_when_played_and_keep_deal_order():
    game = make("brazilian", 2)
    set_scores(game, 11, 11)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    player = game.current_player
    order = [c.id for c in player.dealt]
    assert [c.id for c in game._ordered_hand(player)] == order
    first = player.hand[1]
    for other_player in game.players:
        game.get_user(other_player).messages.clear()
    act(game, player, f"play_{first.id}")
    announced = texts(game, other(game, player))
    assert game._format_card(first, "en") in announced
    assert [c.id for c in game._ordered_hand(player)] == [
        i for i in order if i != first.id
    ]


def test_mao_de_ferro_bots_play_without_looking():
    game = make("brazilian", 2, bots=True, start=False)
    game.on_start()
    set_scores(game, 11, 11)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    assert game.blind_hand
    seen = set()
    for seed in range(40):
        random.seed(seed)
        from ..games.truco.bot import choose_action

        seen.add(choose_action(game, game.current_player))
    assert len(seen) > 1


def test_mao_de_ferro_gestures_do_not_reveal_the_card():
    game = make("brazilian", 2, client_type="mobile")
    set_scores(game, 11, 11)
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    player = game.current_player
    card = player.hand[0]
    spoken = gesture(game, player, f"play_{card.id}")
    assert spoken and game._format_card(card, "en") not in spoken


def test_a_normal_hand_is_not_blind():
    game = make("brazilian", 2)
    set_scores(game, 11, 4)
    game._start_hand(rotate_dealer=True)
    assert not game.blind_hand
    set_scores(game, 5, 5)
    game._start_hand(rotate_dealer=True)
    assert not game.blind_hand


def test_mao_de_onze_partners_see_each_others_cards_but_rivals_do_not():
    game = make("brazilian", 4)
    set_scores(game, 11, 2)
    for p in game.players:
        game.get_user(p).messages.clear()
    game._start_hand(rotate_dealer=True)
    game.flush_menus()
    holders = [p for p in game.players if game._team_index(p) == 0]
    rivals = [p for p in game.players if game._team_index(p) == 1]
    for holder in holders:
        mate = next(p for p in holders if p is not holder)
        spoken = texts(game, holder)
        assert mate.name in spoken
        for card in mate.dealt:
            assert game._format_card(card, "en") in spoken
    for rival in rivals:
        spoken = texts(game, rival)
        for holder in holders:
            for card in holder.dealt:
                assert game._format_card(card, "en") not in spoken
    # Reading the hand during the decision repeats the partner's cards, for the holders only.
    game.get_user(holders[0]).messages.clear()
    game._action_read_hand(holders[0], "read_hand")
    assert holders[1].name in texts(game, holders[0])
    game.get_user(rivals[0]).messages.clear()
    game._action_read_hand(rivals[0], "read_hand")
    assert holders[0].name not in texts(game, rivals[0])


def test_flor_in_a_game_compares_all_three_cards():
    from ..games.truco.game import TrucoGame as Game
    from ..games.truco.game import TrucoOptions as Opts

    game = Game(options=Opts(variant="argentine", team_mode="individual", flor=True))
    game.setup_keybinds()
    for i in range(2):
        game.add_player(f"Player{i + 1}", MockUser(f"Player{i + 1}", uuid=f"p{i + 1}"))
    game.host = "Player1"
    game.on_start()
    game.flush_menus()
    low = [
        TrucoCard(id=1, rank=7, suit=SUIT_OROS),
        TrucoCard(id=2, rank=6, suit=SUIT_OROS),
        TrucoCard(id=3, rank=5, suit=SUIT_OROS),
    ]
    high = [
        TrucoCard(id=4, rank=7, suit=SUIT_COPAS),
        TrucoCard(id=5, rank=6, suit=SUIT_COPAS),
        TrucoCard(id=6, rank=4, suit=SUIT_COPAS),
    ]
    assert rules.flor_score(low) == 38
    assert rules.flor_score(high) == 37
    game.players[0].dealt = list(low)
    game.players[1].dealt = list(high)
    winner = game._best_by_score(
        list(game.players), lambda p: rules.flor_score(p.dealt)
    )
    assert winner is game.players[0]


# ---------------------------------------------------------------------------
# Physical-card conservation
# ---------------------------------------------------------------------------


def _assert_cards_conserved(game):
    """While a hand is live, every card of the deck exists exactly once."""

    if not game.hand_active:
        return
    in_play = [card.id for card in game.deck]
    for player in game.players:
        in_play.extend(card.id for card in player.dealt)
        held = {card.id for card in player.hand}
        assert held <= {card.id for card in player.dealt}
    if game.vira is not None:
        in_play.append(game.vira.id)
    assert len(in_play) == len(set(in_play)), "a card exists twice"
    assert sorted(in_play) == sorted(card.id for card in game._build_deck()), (
        "a card was lost or invented"
    )
    dealt_ids = {card.id for player in game.players for card in player.dealt}
    for trick in game.plays:
        for play in trick:
            assert play.card.id in dealt_ids


def _conservation_game(kind, count):
    if kind == "argentine":
        mode = {2: "individual", 4: "2v2", 6: "3v3"}[count]
        game = TrucoGame(options=TrucoOptions(team_mode=mode, flor=True))
        game.setup_keybinds()
        for i in range(count):
            game.add_player(f"Robot{i + 1}", Bot(f"Robot{i + 1}", uuid=f"b{i + 1}"))
        game.host = "Robot1"
        return game
    return make(kind, count, bots=True, start=False)


@pytest.mark.parametrize(
    ("kind", "count"),
    [
        ("argentine", 2),
        ("argentine", 4),
        ("argentine", 6),
        ("brazilian", 2),
        ("brazilian", 4),
        ("spanish", 2),
        ("spanish", 4),
    ],
)
def test_bot_matches_never_duplicate_or_lose_cards(kind, count):
    for seed in range(2):
        random.seed(seed)
        game = _conservation_game(kind, count)
        game.on_start()
        game.flush_menus()
        for _ in range(80000):
            game.on_tick()
            game.flush_menus()
            _assert_cards_conserved(game)
            if game.status != "playing":
                break
        assert game.status != "playing"


def test_cards_are_conserved_after_save_and_restore_mid_hand():
    random.seed(7)
    game = _conservation_game("brazilian", 4)
    game.on_start()
    game.flush_menus()
    for _ in range(300):
        game.on_tick()
        game.flush_menus()
    restored = TrucoGame.from_json(game.to_json())
    _assert_cards_conserved(restored)
    assert [sorted(c.id for c in p.hand) for p in restored.players] == [
        sorted(c.id for c in p.hand) for p in game.players
    ]


# ---------------------------------------------------------------------------
# Spanish truc: three tied tricks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("tied_last", "winner_seat"), [("ab", 1), ("bc", 2)])
def test_spanish_three_tied_tricks_go_to_the_tied_player_nearest_the_mano(
    tied_last, winner_seat
):
    game = make("spanish", 4)
    seats = game._order_from(game.mano_index)  # mano, then clockwise
    suit_o, suit_c = decks.SUIT_OROS, decks.SUIT_COPAS
    suit_e, suit_b = decks.SUIT_ESPADAS, decks.SUIT_BASTOS
    first, second, third = {}, {}, {}
    # Trick 1: the 3s of seats 1 and 2 tie on top. Trick 2: the 6s tie on top.
    first.update(
        {1: VC(3, suit_o), 2: VC(3, suit_c), 0: VC(4, suit_o), 3: VC(4, suit_c)}
    )
    second.update(
        {1: VC(6, suit_o), 2: VC(6, suit_c), 0: VC(5, suit_o), 3: VC(5, suit_c)}
    )
    low = [VC(4, suit_e), VC(4, suit_b)]
    top = [VC(7, suit_c), VC(7, suit_b)]  # the two false sevens tie
    pair = (1, 2) if tied_last == "ab" else (2, 3)
    rest = [seat for seat in range(4) if seat not in pair]
    third[pair[0]], third[pair[1]] = top
    third[rest[0]], third[rest[1]] = low
    hands = {
        seats[seat].id: [first[seat], second[seat], third[seat]] for seat in range(4)
    }
    set_hands(game, [hands[player.id] for player in game.players])
    for number in range(3):
        for seat in range(4):
            player = seats[seat]
            assert game.current_player is player
            act(game, player, f"play_{hands[player.id][number].id}")
    winner_team = game._team_index(seats[winner_seat])
    assert game._scores()[winner_team] == 1
    assert game._scores()[1 - winner_team] == 0
