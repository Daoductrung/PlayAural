from server.games.backgammon.game import BackgammonGame, TURN_PHASE_MOVING
from server.games.farkle.game import FarkleGame
from server.games.pig.game import PigGame
from server.games.tradeoff.game import TradeoffGame
from server.users.test_user import MockUser


def _spoken_since(user: MockUser, before: int) -> list[dict]:
    return [message.data for message in user.messages[before:] if message.type == "speak"]


def test_whos_at_table_uses_game_buffer() -> None:
    game = FarkleGame()
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    host_player = game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)
    game.host = "Host"

    before = len(host_user.messages)
    game._action_whos_at_table(host_player, "whos_at_table")

    spoken = _spoken_since(host_user, before)
    assert spoken
    assert all(message["buffer"] == "game" for message in spoken)


def test_predict_outcomes_unavailable_uses_game_buffer() -> None:
    game = PigGame()
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    host_player = game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)

    before = len(host_user.messages)
    game._action_predict_outcomes(host_player, "predict_outcomes")

    spoken = _spoken_since(host_user, before)
    assert spoken[-1]["buffer"] == "game"


def test_farkle_check_turn_score_uses_game_buffer() -> None:
    game = FarkleGame()
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    host_player = game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)
    game.on_start()

    current = game.current_player
    assert current is host_player
    current.turn_score = 250

    before = len(host_user.messages)
    game._action_check_turn_score(host_player, "check_turn_score")

    spoken = _spoken_since(host_user, before)
    assert spoken[-1]["buffer"] == "game"


def test_backgammon_illegal_move_uses_game_buffer() -> None:
    game = BackgammonGame()
    red_user = MockUser("Red", uuid="red")
    white_user = MockUser("White", uuid="white")
    game.add_player("Red", red_user)
    game.add_player("White", white_user)
    game.host = "Red"
    game.on_start()

    game.turn_phase = TURN_PHASE_MOVING
    current = game.current_player
    assert current is not None
    current_user = game.get_user(current)
    assert current_user is not None

    before = len(current_user.messages)
    game._action_move_option(current, "move_p0_p0_6")

    spoken = _spoken_since(current_user, before)
    assert spoken[-1]["buffer"] == "game"


def test_tradeoff_view_hand_uses_game_buffer() -> None:
    game = TradeoffGame()
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    host_player = game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)
    host_player.hand = [1, 3, 5]

    before = len(host_user.messages)
    game._action_view_hand(host_player, "view_hand")

    spoken = _spoken_since(host_user, before)
    assert spoken[-1]["buffer"] == "game"
