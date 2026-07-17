"""Game implementations."""

from .base import Game
from .registry import GameRegistry, register_game, get_game_class

# Import all games to trigger registration
from .pig.game import PigGame
from .scopa.game import ScopaGame
from .lightturret.game import LightTurretGame
from .threes.game import ThreesGame
from .milebymile.game import MileByMileGame
from .chaosbear.game import ChaosBearGame
from .farkle.game import FarkleGame
from .yahtzee.game import YahtzeeGame
from .ninetynine.game import NinetyNineGame
from .tradeoff.game import TradeoffGame
from .pirates.game import PiratesGame
from .leftrightcenter.game import LeftRightCenterGame
from .tossup.game import TossUpGame
from .midnight.game import MidnightGame
from .fivecarddraw.game import FiveCardDrawGame
from .holdem.game import HoldemGame
from .crazyeights.game import CrazyEightsGame
from .snakesandladders.game import SnakesAndLaddersGame
from .coup.game import CoupGame
from .pusoydos.game import PusoyDosGame
from .rollingballs.game import RollingBallsGame
from .blackjack.game import BlackjackGame
from .dominos.game import DominosGame
from .battleship.game import BattleshipGame
from .ludo.game import LudoGame
from .backgammon.game import BackgammonGame
from .chess.game import ChessGame
from .sorry.game import SorryGame
from .bunko.game import BunkoGame
from .tienlen.game import TienLenGame
from .colorgame.game import ColorGameGame
from .battle.game import BattleGame
from .citadels.game import CitadelsGame
from .deadmansdeck.game import DeadMansDeckGame
from .deadmanspoker.game import DeadMansPokerGame
from .metalpipe.game import MetalPipeGame
from .nine.game import NineGame
from .senet.game import SenetGame
from .humanitycards.game import HumanityCardsGame
from .twentyone.game import TwentyOneGame
from .ageofheroes.game import AgeOfHeroesGame
from .uno.game import UnoGame
from .explodingkittens.game import ExplodingKittensGame

__all__ = [
    "Game",
    "GameRegistry",
    "register_game",
    "get_game_class",
    "PigGame",
    "ScopaGame",
    "LightTurretGame",
    "ThreesGame",
    "MileByMileGame",
    "ChaosBearGame",
    "FarkleGame",
    "YahtzeeGame",
    "NinetyNineGame",
    "TradeoffGame",
    "PiratesGame",
    "LeftRightCenterGame",
    "TossUpGame",
    "MidnightGame",
    "FiveCardDrawGame",
    "HoldemGame",
    "CrazyEightsGame",
    "SnakesAndLaddersGame",
    "CoupGame",
    "PusoyDosGame",
    "RollingBallsGame",
    "BlackjackGame",
    "DominosGame",
    "BattleshipGame",
    "LudoGame",
    "BackgammonGame",
    "ChessGame",
    "SorryGame",
    "BunkoGame",
    "TienLenGame",
    "ColorGameGame",
    "BattleGame",
    "CitadelsGame",
    "DeadMansDeckGame",
    "DeadMansPokerGame",
    "MetalPipeGame",
    "NineGame",
    "SenetGame",
    "HumanityCardsGame",
    "TwentyOneGame",
    "AgeOfHeroesGame",
    "UnoGame",
    "ExplodingKittensGame",
]
