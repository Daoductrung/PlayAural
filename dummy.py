import sys
sys.path.append('server')
from server.games.scopa.game import ScopaGame
from server.users.test_user import MockUser
from server.game_utils.cards import Card
from server.games.scopa.capture import find_captures
table_cards = [
    Card(id=1, rank=5, suit=1),
    Card(id=2, rank=2, suit=2),
    Card(id=3, rank=3, suit=3)
]
captures = find_captures(table_cards, 5)
print(captures)
