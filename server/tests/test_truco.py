"""Game-flow, persistence, menu, and bot coverage for Argentine Truco."""

import random
from pathlib import Path

import pytest

from ..games.registry import GameRegistry
from ..games.truco import cards, rules
from ..games.truco.cards import TrucoCard
from ..games.truco.engine import CARD_ACTION_PREFIX
from ..games.truco.game import TrucoGame, TrucoOptions, TrucoPlayer
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
Localization.init(ROOT / "server" / "locales")


def C(rank: int, suit: str) -> TrucoCard:
    index = cards.SUITS.index(suit) * len(cards.RANKS) + cards.RANKS.index(rank)
    return TrucoCard(id=index, rank=rank, suit=suit)


def make_game(
    count=2, *, mode=None, bots=False, start=True, client_type="python", seed=3, **opts
):
    mode = mode or {2: "individual", 4: "2v2", 6: "3v3"}[count]
    game = TrucoGame(options=TrucoOptions(team_mode=mode, **opts))
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


def set_hands(game, hands):
    for player, hand in zip(game.players, hands):
        player.hand = list(hand)
        player.dealt = list(hand)
        player.has_flor = False
    game.refresh_menus()
    game.flush_menus()


def mano(game) -> TrucoPlayer:
    return game.get_player_by_id(game.turn_player_ids[game.mano_index])


def other(game, player):
    return next(p for p in game.players if p is not player)


def act(game, player, action_id):
    game.execute_action(player, action_id)
    game.flush_menus()


def play(game, player, card):
    act(game, player, f"play_{card.id}")


def spoken(player) -> list[str]:
    return player_user(player).get_spoken_messages()


def player_user(player):
    return player._user if hasattr(player, "_user") else None


def texts(game, player) -> str:
    return " | ".join(game.get_user(player).get_spoken_messages())


def clear(game):
    for player in game.players:
        user = game.get_user(player)
        if hasattr(user, "clear_messages"):
            user.clear_messages()
        else:
            user.messages.clear()


def team_score(game, player) -> int:
    return game._team_manager.get_team(player.name).total_score


# ---------------------------------------------------------------------------
# Registry and validation
# ---------------------------------------------------------------------------


def test_registered_with_player_limits():
    cls = GameRegistry.get("truco")
    assert cls is TrucoGame
    assert (cls.get_min_players(), cls.get_max_players()) == (2, 6)
    assert cls.get_category() == "cards"


@pytest.mark.parametrize(
    ("count", "mode", "ok"),
    [
        (2, "individual", True),
        (4, "2v2", True),
        (6, "3v3", True),
        (4, "individual", False),
        (6, "2v2", False),
        (3, "individual", False),
        (5, "individual", False),
    ],
)
def test_prestart_validation(count, mode, ok):
    game = make_game(count, mode=mode, start=False)
    errors = game.prestart_validate()
    assert (not errors) is ok


def test_deal_and_mano():
    game = make_game(4)
    assert all(len(p.hand) == 3 and p.dealt == p.hand for p in game.players)
    ids = {c.id for p in game.players for c in p.hand}
    assert len(ids) == 12 and len(game.deck) == 28
    assert game.current_player is mano(game)
    assert game.hand_active and game.round == 1
    teams = [
        game._team_index(p)
        for p in (game.get_player_by_id(i) for i in game.turn_player_ids)
    ]
    assert teams in ([0, 1, 0, 1], [1, 0, 1, 0])


# ---------------------------------------------------------------------------
# Tricks
# ---------------------------------------------------------------------------


def test_two_tricks_win_the_hand():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    set_hands(
        game,
        [
            [C(1, "espadas"), C(4, "copas"), C(5, "copas")]
            if p is a
            else [C(4, "oros"), C(5, "oros"), C(6, "oros")]
            for p in game.players
        ],
    )
    play(game, a, C(1, "espadas"))
    play(game, b, C(4, "oros"))
    assert game.trick_results == [game._team_index(a)]
    assert game.current_player is a
    play(game, a, C(4, "copas"))
    play(game, b, C(5, "oros"))
    # a lost trick 2? 4 copas (1) < 5 oros? both power: 4 -> 1, 5 -> 2: b wins.
    assert game.trick_results == [game._team_index(a), game._team_index(b)]
    assert game.current_player is b
    play(game, b, C(6, "oros"))
    play(game, a, C(5, "copas"))
    # b's 6 (3) beats a's 5 (2): b takes tricks 2 and 3 and the hand
    assert team_score(game, b) == 1 and team_score(game, a) == 0
    assert not game.hand_active


def test_parda_first_trick_next_decides():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    set_hands(
        game,
        [
            [C(3, "oros"), C(4, "copas"), C(5, "copas")]
            if p is a
            else [C(3, "copas"), C(5, "oros"), C(6, "oros")]
            for p in game.players
        ],
    )
    play(game, a, C(3, "oros"))
    play(game, b, C(3, "copas"))
    assert game.trick_results == [None]
    assert game.current_player is a
    play(game, a, C(5, "copas"))
    play(game, b, C(6, "oros"))
    assert team_score(game, b) == 1


def test_all_tricks_tie_mano_team_wins():
    assert rules.decide_hand([None, None, None], 1) == 1


def test_teammate_tie_is_not_parda():
    game = make_game(4)
    first = mano(game)
    start = game.turn_player_ids.index(first.id)
    seq = [
        game.get_player_by_id(game.turn_player_ids[(start + i) % 4]) for i in range(4)
    ]
    hands = {
        seq[0].id: [C(3, "oros"), C(4, "copas"), C(5, "copas")],
        seq[1].id: [C(4, "oros"), C(5, "oros"), C(6, "oros")],
        seq[2].id: [C(3, "copas"), C(6, "copas"), C(10, "copas")],
        seq[3].id: [C(5, "bastos"), C(6, "bastos"), C(4, "bastos")],
    }
    for p in game.players:
        p.hand = list(hands[p.id])
        p.dealt = list(hands[p.id])
    game.refresh_menus()
    game.flush_menus()
    play(game, seq[0], C(3, "oros"))
    play(game, seq[1], C(4, "oros"))
    play(game, seq[2], C(3, "copas"))
    play(game, seq[3], C(5, "bastos"))
    assert game.trick_results == [game._team_index(seq[0])]


def test_off_turn_and_wrong_card_rejected():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    before = list(b.hand)
    play(game, b, b.hand[0])
    assert b.hand == before and not any(game.plays)


# ---------------------------------------------------------------------------
# Truco
# ---------------------------------------------------------------------------


def test_truco_accept_then_hand_pays_two():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    set_hands(
        game,
        [
            [C(1, "espadas"), C(1, "bastos"), C(3, "oros")]
            if p is a
            else [C(4, "oros"), C(5, "oros"), C(6, "oros")]
            for p in game.players
        ],
    )
    act(game, a, "call_truco")
    assert game.truco_pending == "truco"
    play(game, a, C(1, "espadas"))  # blocked while waiting
    assert not game.plays[0]
    act(game, b, "accept")
    assert game.truco_level == "truco" and game.truco_raiser_team == game._team_index(b)
    play(game, a, C(1, "espadas"))
    play(game, b, C(4, "oros"))
    play(game, a, C(1, "bastos"))
    play(game, b, C(5, "oros"))
    assert team_score(game, a) == 2


def test_truco_decline_pays_one_and_raise_chain():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "decline")
    assert team_score(game, a) == 1 and not game.hand_active

    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "call_truco")  # raise to retruco while answering
    assert (
        game.truco_pending == "retruco"
        and game.truco_pending_team == game._team_index(b)
    )
    act(game, a, "decline")  # refusing retruco concedes the truco value
    assert team_score(game, b) == 2


def test_only_accepter_may_raise():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "accept")
    act(game, a, "call_truco")
    assert game.truco_pending == ""
    act(game, b, "call_truco")
    assert game.truco_pending == "retruco"
    act(game, a, "accept")
    act(game, b, "call_truco")
    assert game.truco_pending == ""  # a, the accepter, holds the raise now
    act(game, a, "call_truco")
    assert game.truco_pending == "valecuatro"
    act(game, b, "decline")
    assert team_score(game, a) == 3


def test_any_teammate_can_call_and_answer():
    game = make_game(4)
    a = mano(game)
    mate = next(
        p
        for p in game.players
        if p is not a and game._team_index(p) == game._team_index(a)
    )
    _foe1, foe2 = [
        p for p in game.players if game._team_index(p) != game._team_index(a)
    ]
    act(game, mate, "call_truco")  # off turn, teammate of the mano
    assert game.truco_pending_team == game._team_index(a)
    act(game, mate, "accept")  # caller's own team cannot answer
    assert game.truco_pending == "truco"
    act(game, foe2, "accept")
    assert game.truco_level == "truco"


def test_truco_blocked_by_envido_chain_and_answer_first():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_envido")
    act(game, b, "call_truco")
    assert game.truco_pending == ""
    play(game, a, a.hand[0])
    assert not game.plays[0]


# ---------------------------------------------------------------------------
# Envido
# ---------------------------------------------------------------------------


def envido_game():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    set_hands(
        game,
        [
            [C(7, "espadas"), C(6, "espadas"), C(1, "oros")]
            if p is a
            else [C(7, "oros"), C(5, "copas"), C(4, "bastos")]
            for p in game.players
        ],
    )
    return game, a, b


def test_envido_accepted_winner_scores_and_reveals_at_hand_end():
    game, a, b = envido_game()
    act(game, a, "call_envido")
    act(game, b, "accept")
    assert team_score(game, a) == 2 and team_score(game, b) == 0
    assert game.reveals and game.reveals[0].value == 33
    clear(game)
    act(game, b, "mazo")
    out = texts(game, b)
    assert "33" in out
    assert not game.reveals


def test_envido_declined_and_raised():
    game, a, b = envido_game()
    act(game, a, "call_envido")
    act(game, b, "decline")
    assert team_score(game, a) == 1 and game.envido_done
    act(game, b, "call_envido")
    assert not game.envido_pending

    game, a, b = envido_game()
    act(game, a, "call_envido")
    act(game, b, "call_real_envido")
    act(game, a, "decline")  # pays what was accepted: envido = 2
    assert team_score(game, b) == 2


def test_envido_closed_after_own_card_and_after_truco_accept():
    game, a, b = envido_game()
    play(game, a, C(1, "oros"))
    act(game, a, "call_envido")
    assert not game.envido_pending
    act(game, b, "call_envido")  # b has not played yet
    assert game.envido_pending
    game, a, b = envido_game()
    act(game, a, "call_truco")
    act(game, b, "accept")
    act(game, a, "call_envido")
    assert not game.envido_pending


def test_envido_goes_first_before_truco_answer():
    game, a, b = envido_game()
    act(game, a, "call_truco")
    act(game, b, "call_envido")
    assert game.envido_pending and game.truco_pending == "truco"
    act(game, a, "accept")  # answers the envido
    assert game.envido_done and game.truco_pending == "truco"
    assert team_score(game, a) == 2
    act(game, b, "accept")
    assert game.truco_level == "truco"


def test_falta_envido_malas_decides_game_in_30():
    game, a, b = envido_game()
    game.options.target_length = "30"
    act(game, a, "call_falta_envido")
    act(game, b, "accept")
    assert not game.hand_active or game.status != "playing"
    assert game.winner_team_index == game._team_index(a)
    assert game.status == "finished" or not game.game_active


def test_falta_envido_buenas_pays_leader_gap():
    game, a, b = envido_game()
    game.options.target_length = "30"
    game._team(game._team_index(b)).total_score = 20
    act(game, a, "call_falta_envido")
    act(game, b, "accept")
    assert team_score(game, a) == 10
    assert game.status == "playing"


def test_envido_tie_goes_to_mano():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    set_hands(
        game,
        [
            [C(7, "espadas"), C(6, "espadas"), C(1, "oros")]
            if p is a
            else [C(7, "oros"), C(6, "oros"), C(4, "bastos")]
            for p in game.players
        ],
    )
    act(game, b, "call_envido")
    act(game, a, "accept")
    assert team_score(game, a) == 2


# ---------------------------------------------------------------------------
# Mazo
# ---------------------------------------------------------------------------


def test_mazo_single_player_team_gives_opponent_envido_and_hand():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "mazo")
    assert team_score(game, b) == 2  # 1 envido + 1 hand
    assert not game.hand_active


def test_mazo_after_truco_accepted_pays_truco_value_without_envido():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "accept")
    act(game, a, "mazo")
    assert team_score(game, b) == 2


def test_mazo_teammate_continues_and_is_skipped():
    game = make_game(4)
    a = mano(game)
    mate = next(
        p
        for p in game.players
        if p is not a and game._team_index(p) == game._team_index(a)
    )
    act(game, mate, "mazo")
    assert mate.folded and game.hand_active
    play(game, a, a.hand[0])
    nxt = game.current_player
    assert nxt is not mate and not nxt.folded


def test_mazo_blocked_while_call_pending():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    act(game, b, "mazo")
    assert not b.folded


def test_whole_team_mazo_2v2():
    game = make_game(4)
    a = mano(game)
    mates = [p for p in game.players if game._team_index(p) == game._team_index(a)]
    foe = next(p for p in game.players if game._team_index(p) != game._team_index(a))
    for p in mates:
        act(game, p, "mazo")
    assert team_score(game, foe) == 2
    assert not game.hand_active


# ---------------------------------------------------------------------------
# Flor
# ---------------------------------------------------------------------------


def flor_game(flor_hands):
    game = make_game(2, flor=True, start=False)
    random.seed(1)
    game.on_start()
    game.flush_menus()
    return game


def deal_flor(game, hands):
    set_hands(game, hands)
    for p, hand in zip(game.players, hands):
        p.has_flor = rules.has_flor(hand)
    game.envido_flor = any(p.has_flor for p in game.players)
    game.envido_done = game.envido_done or game.envido_flor
    game.refresh_menus()
    game.flush_menus()


def test_flor_off_by_default_and_no_cancel():
    game = make_game(2)
    assert game.options.flor is False
    assert not any(p.has_flor for p in game.players) and not game.envido_flor


def test_single_flor_scores_three_and_cancels_envido():
    wins = 0
    for seed in range(400):
        game = make_game(2, flor=True, seed=seed)
        holders = [p for p in game.players if p.has_flor]
        if len(holders) == 1:
            assert team_score(game, holders[0]) == 3
            assert game.envido_flor and game.envido_done
            a = mano(game)
            act(game, a, "call_envido")
            assert not game.envido_pending
            wins += 1
            break
    assert wins == 1


def test_contraflor_accept_decline():
    game = make_game(2, flor=True)
    a = mano(game)
    b = other(game, a)
    game.flor_window = True
    a.has_flor = b.has_flor = True
    a.hand = a.dealt = [C(7, "oros"), C(6, "oros"), C(5, "oros")]
    b.hand = b.dealt = [C(7, "copas"), C(4, "copas"), C(3, "copas")]
    game.envido_flor = game.envido_done = True
    game.refresh_menus()
    game.flush_menus()
    act(game, a, "call_truco")  # blocked until the flor is settled
    assert game.truco_pending == ""
    act(game, b, "call_contraflor")
    assert game.flor_pending == rules.CONTRAFLOR
    act(game, a, "accept")
    assert team_score(game, a) == 6 and not game.flor_window

    game = make_game(2, flor=True)
    a = mano(game)
    b = other(game, a)
    game.flor_window = True
    a.has_flor = b.has_flor = True
    a.hand = a.dealt = [C(7, "oros"), C(6, "oros"), C(5, "oros")]
    b.hand = b.dealt = [C(7, "copas"), C(4, "copas"), C(3, "copas")]
    game.refresh_menus()
    game.flush_menus()
    act(game, b, "call_contraflor")
    act(game, a, "decline")
    assert team_score(game, b) == 4


def test_uncontested_flores_when_first_card_played():
    game = make_game(2, flor=True)
    a = mano(game)
    b = other(game, a)
    game.flor_window = True
    a.has_flor = b.has_flor = True
    a.hand = a.dealt = [C(7, "oros"), C(6, "oros"), C(5, "oros")]
    b.hand = b.dealt = [C(7, "copas"), C(4, "copas"), C(3, "copas")]
    game.refresh_menus()
    game.flush_menus()
    play(game, a, C(7, "oros"))
    assert team_score(game, a) == 3 and team_score(game, b) == 3


# ---------------------------------------------------------------------------
# Game end
# ---------------------------------------------------------------------------


def test_game_ends_and_clamps_at_target():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    game._team(game._team_index(a)).total_score = 14
    act(game, a, "call_truco")
    act(game, b, "accept")
    act(game, a, "call_truco") if False else None
    set_hands(
        game,
        [
            [C(1, "espadas"), C(1, "bastos"), C(3, "oros")]
            if p is a
            else [C(4, "oros"), C(5, "oros"), C(6, "oros")]
            for p in game.players
        ],
    )
    play(game, a, C(1, "espadas"))
    play(game, b, C(4, "oros"))
    play(game, a, C(1, "bastos"))
    play(game, b, C(5, "oros"))
    assert team_score(game, a) == 15
    assert game.winner_team_index == game._team_index(a)
    result = game.build_game_result()
    assert result.custom_data["winner_ids"] == [a.id]
    lines = game.format_end_screen(result, "en")
    assert lines[0] == Localization.get("en", "truco-end-title")


def test_next_hand_rotates_dealer_after_sequence():
    game = make_game(2)
    first_dealer = game.dealer_index
    a = mano(game)
    act(game, a, "mazo")
    for _ in range(100):
        game.on_tick()
        game.flush_menus()
    assert game.round == 2
    assert game.dealer_index != first_dealer
    assert all(len(p.hand) == 3 for p in game.players)


# ---------------------------------------------------------------------------
# Persistence and menus
# ---------------------------------------------------------------------------


def test_save_and_restore_midhand():
    game = make_game(4, flor=True)
    a = mano(game)
    play(game, a, a.hand[0]) if not game.flor_window and game.hand_active else None
    loaded = TrucoGame.from_json(game.to_json())
    assert loaded.round == game.round
    assert [p.hand for p in loaded.players] == [p.hand for p in game.players]
    assert loaded.plays == game.plays
    assert loaded.truco_level == game.truco_level


def test_menu_answer_actions_first_for_responders():
    game = make_game(2, client_type="web")
    a = mano(game)
    b = other(game, a)
    act(game, a, "call_truco")
    visible = [r.action.id for r in game.get_all_visible_actions(b)]
    turn_ids = [
        i
        for i in visible
        if i in ("accept", "decline") or i.startswith(("call_", "play_")) or i == "mazo"
    ]
    assert turn_ids[:2] == ["accept", "decline"]
    assert not any(i.startswith("play_") for i in turn_ids)
    own = [r.action.id for r in game.get_all_visible_actions(a)]
    assert "accept" not in own


def test_menu_cards_first_on_own_turn():
    game = make_game(2)
    a = mano(game)
    ids = [r.action.id for r in game.get_all_visible_actions(a)]
    play_ids = [i for i in ids if i.startswith("play_")]
    assert len(play_ids) == 3
    assert ids.index(play_ids[0]) < ids.index("call_truco")
    assert "call_envido" in ids and "mazo" in ids
    assert "call_contraflor" not in ids


def test_spectator_sees_public_info_only_and_hears_calls():
    game = make_game(2)
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher_user.client_type = "mobile"
    watcher = game.add_spectator("Watcher", watcher_user)
    game.refresh_menus(watcher)
    game.flush_menus()
    ids = [r.action.id for r in game.get_all_visible_actions(watcher)]
    assert "read_table" in ids and "read_calls" in ids
    assert "read_hand" not in ids and "mazo" not in ids and "call_truco" not in ids
    assert not any(i.startswith("play_") for i in ids)
    a = mano(game)
    act(game, a, "call_truco")
    assert "Truco" in texts(game, watcher)
    act(game, watcher, "accept")
    assert game.truco_pending == "truco"


def test_info_actions_speak():
    game = make_game(2)
    a = mano(game)
    clear(game)
    act(game, a, "read_hand")
    act(game, a, "read_table")
    act(game, a, "read_calls")
    out = texts(game, a)
    assert out


# ---------------------------------------------------------------------------
# Bots
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("count", "flor", "target"),
    [(2, False, "15"), (2, True, "30"), (4, True, "30"), (6, False, "15")],
)
def test_bot_only_games_finish(count, flor, target):
    for seed in range(2):
        random.seed(seed)
        mode = {2: "individual", 4: "2v2", 6: "3v3"}[count]
        game = TrucoGame(
            options=TrucoOptions(team_mode=mode, flor=flor, target_length=target)
        )
        game.setup_keybinds()
        for i in range(count):
            game.add_player(f"Robot{i + 1}", Bot(f"Robot{i + 1}", uuid=f"b{i + 1}"))
        game.host = "Robot1"
        game.on_start()
        game.flush_menus()
        for _ in range(60000):
            game.on_tick()
            game.flush_menus()
            if game.status != "playing":
                break
        assert game.status != "playing"
        assert max(team.total_score for team in game._team_manager.teams) == int(target)


def test_human_teammate_answers_before_bot():
    game = make_game(4)
    a = mano(game)
    bot_player = next(
        p for p in game.players if game._team_index(p) != game._team_index(a)
    )
    bot_player.is_bot = True
    act(game, a, "call_truco")
    assert (
        game._bot_actor() is None
        or not game._bot_actor().is_bot
        or all(p.is_bot for p in game._responders())
    )


# ---------------------------------------------------------------------------
# Localization
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


def test_locale_parity_and_used_keys_exist():
    base = locale_keys(ROOT / "server" / "locales" / "en" / "truco.ftl")
    for lang in ("es", "pt", "vi"):
        assert locale_keys(ROOT / "server" / "locales" / lang / "truco.ftl") == base
    import re

    source = "\n".join(
        (ROOT / "server" / "games" / "truco" / name).read_text(encoding="utf-8")
        for name in ("game.py", "engine.py", "bot.py")
    )
    used = set(re.findall(r'"(truco-[a-z0-9-]+)"', source))
    used |= {
        f"truco-reveal-{kind}-{who}"
        for kind in ("envido", "flor")
        for who in ("you", "player")
    }
    missing = {
        key
        for key in used
        if key not in base
        and not key.startswith("truco-reveal-")
        and key != "truco-half-buenas"
    }
    assert not missing, missing


# ---------------------------------------------------------------------------
# Touch gestures, descriptions, and spectators
# ---------------------------------------------------------------------------


def test_shift_enter_on_a_card_reads_its_strength_and_envido_on_touch():
    game = make_game(2, client_type="web")
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
    heard = " | ".join(user.get_spoken_messages())
    assert "beats" in heard and "Envido value" in heard
    assert len(player.hand) == 3 and game.current_player is player


def test_shift_enter_is_silent_on_desktop():
    game = make_game(2, client_type="python")
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


def test_descriptions_explain_calls_answers_and_fold():
    game = make_game(2)
    a = mano(game)
    b = other(game, a)
    assert "2 points" in game._get_action_description(a, "call_truco")
    assert "Envido" in game._get_action_description(a, "call_envido")
    assert "Fold" in game._get_action_description(a, "mazo")
    act(game, a, "call_truco")
    assert "Truco" in game._get_action_description(b, "accept")
    assert "1 point" in game._get_action_description(b, "decline")
    assert "3 points" in game._get_action_description(b, "call_truco")


def test_spectator_cannot_use_the_card_gesture_or_act():
    game = make_game(2)
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher_user.client_type = "mobile"
    watcher = game.add_spectator("Watcher", watcher_user)
    game.refresh_menus(watcher)
    game.flush_menus()
    ids = [r.action.id for r in game.get_all_visible_actions(watcher)]
    assert "card_info_gesture" not in ids
    watcher_user.messages.clear()
    game.handle_event(
        watcher,
        {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": "play_1"},
    )
    assert not watcher_user.get_spoken_messages()


def test_spectator_present_through_a_whole_bot_game():
    random.seed(4)
    game = TrucoGame(options=TrucoOptions(team_mode="individual", flor=True))
    game.setup_keybinds()
    for i in range(2):
        game.add_player(f"Robot{i + 1}", Bot(f"Robot{i + 1}", uuid=f"b{i + 1}"))
    watcher_user = MockUser("Watcher", uuid="watcher")
    game.add_spectator("Watcher", watcher_user)
    game.host = "Robot1"
    game.on_start()
    game.flush_menus()
    for _ in range(60000):
        game.on_tick()
        game.flush_menus()
        if game.status != "playing":
            break
    assert game.status != "playing"
    heard = " | ".join(watcher_user.get_spoken_messages())
    assert "Your cards" not in heard and heard


def test_gesture_describes_calls_answers_and_fold_on_touch():
    game = make_game(2, client_type="web")
    a = mano(game)
    b = other(game, a)

    def gesture(player, item_id):
        user = game.get_user(player)
        user.messages.clear()
        game.handle_event(
            player,
            {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": item_id},
        )
        return " | ".join(user.get_spoken_messages())

    assert "2 points" in gesture(a, "call_truco")
    assert "Envido" in gesture(a, "call_envido")
    assert "Falta envido" in gesture(a, "call_falta_envido")
    assert "Fold" in gesture(a, "mazo")
    act(game, a, "call_truco")
    assert "Accept" in gesture(b, "accept")
    assert "1 point" in gesture(b, "decline")
    assert "3 points" in gesture(b, "call_truco")
    assert gesture(b, "whose_turn") == ""


def _escape_ids(game, player):
    game.before_menu_build(player)
    return [
        item.id
        for item in game._build_actions_menu_items(player, game.get_user(player))
    ]


def test_escape_menu_lists_only_the_fixed_actions():
    game = make_game(2, client_type="python")
    a = mano(game)
    b = other(game, a)
    transient = {"call_truco", "call_envido", "call_real_envido", "mazo"}
    transient |= {"call_falta_envido", "accept", "decline", "card_info_gesture"}
    for player in (a, b):
        ids = _escape_ids(game, player)
        assert not transient & set(ids)
        assert not any(i.startswith(CARD_ACTION_PREFIX) for i in ids)
        assert "read_hand" in ids and "check_scores" in ids
    act(game, a, "call_truco")
    assert not transient & set(_escape_ids(game, b))


def test_mobile_long_press_packet_is_shift_enter_with_item_id():
    game = make_game(2, client_type="mobile")
    a = mano(game)
    user = game.get_user(a)
    user.messages.clear()
    before = (len(a.hand), game.current_player)
    game.handle_event(
        a,
        {
            "type": "keybind",
            "key": "shift+enter",
            "shift": True,
            "menu_item_id": "call_truco",
        },
    )
    assert "2 points" in " | ".join(user.get_spoken_messages())
    assert before == (len(a.hand), game.current_player)
