import pytest
from ..games.pusoydos.game import PusoyDosGame, PusoyDosPlayer, PusoyDosOptions
from ..users.test_user import MockUser
from ..game_utils.cards import Card
from ..games.pusoydos.evaluator import get_rank_value, get_suit_value, evaluate_combo, Combo

def test_evaluator():
    # Test card evaluation mappings
    assert get_rank_value(3) == 3
    assert get_rank_value(2) == 15
    assert get_rank_value(1) == 14 # Ace

    # Test Combos
    single = evaluate_combo([Card(0, 3, 2)]) # 3 of Clubs
    assert single.type_name == "single"
    assert single.rank_value == 3
    assert single.suit_value == 1 # Clubs = 1

    single2 = evaluate_combo([Card(1, 3, 4)]) # 3 of Spades
    assert single2.type_name == "single"
    assert single2.rank_value == 3
    assert single2.suit_value == 2 # Spades = 2

    assert single2.beats(single) # 3 of Spades beats 3 of Clubs

def test_game_initialization():
    game = PusoyDosGame()

    u1 = MockUser("p1")
    u2 = MockUser("p2")

    p1 = game.add_player("p1", u1)
    p2 = game.add_player("p2", u2)

    game.on_start()

    assert game.status == "playing"
    assert p1.score == 1000
    assert p2.score == 1000
    assert game.intro_wait_ticks == 140

def test_first_turn_requires_3_of_clubs():
    game = PusoyDosGame()
    u1 = MockUser("p1")
    u2 = MockUser("p2")
    p1 = game.add_player("p1", u1)
    p2 = game.add_player("p2", u2)
    game.on_start()

    # Fast forward intro
    game.intro_wait_ticks = 1
    game.on_tick() # generates deck and starts

    current = game.current_player

    # Fake a 3 of clubs play for testing
    current.hand = [Card(1, 3, 2), Card(2, 4, 1), Card(3, 5, 1)] # 3c, 4d, 5d

    current.selected_cards = {2}
    game.execute_action(current, "play_selected")

    # Should be an error
    user = game.get_user(current)
    assert user.get_last_spoken() == "You must include the 3 of Clubs in the first play."

    current.selected_cards = {1}
    game.execute_action(current, "play_selected")

    # Now it works
    assert game.trick_winner_id == current.id
    assert game.current_combo.type_name == "single"
