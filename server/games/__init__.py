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
from .ageofheroes.game import AgeOfHeroesGame
from .fivecarddraw.game import FiveCardDrawGame
from .holdem.game import HoldemGame
from .crazyeights.game import CrazyEightsGame

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
    "AgeOfHeroesGame",
    "FiveCardDrawGame",
    "HoldemGame",
    "CrazyEightsGame",
]
