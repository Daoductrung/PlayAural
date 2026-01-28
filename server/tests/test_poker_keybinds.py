from server.games.fivecarddraw.game import FiveCardDrawGame
from server.games.holdem.game import HoldemGame


def test_poker_keybind_dealer_label():
    draw = FiveCardDrawGame()
    draw.setup_keybinds()
    assert any(k.name == "Dealer" for k in draw._keybinds.get("x", []))

    holdem = HoldemGame()
    holdem.setup_keybinds()
    assert any(k.name == "Button" for k in holdem._keybinds.get("x", []))
