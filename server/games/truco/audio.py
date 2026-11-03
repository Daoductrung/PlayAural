"""Sound assets shared by every Truco variant.

The effects reuse existing PlayAural sounds; the three music tracks are in
``game_truco/`` (see ``AUDIO_PROVENANCE.md``).
"""

from __future__ import annotations

SHUFFLE_FAMILY = "game_cards/shuffle"
DEAL_FAMILY = "game_cards/draw"
PLAY_FAMILY = "game_cards/play"
DEAL_STAGGER_TICKS = 3

TRUCO_CALL = "game_coup/challenge.ogg"
ENVIDO_CALL = "game_coup/claim_captain.ogg"
FLOR_CALL = "game_coup/foreign_aid.ogg"
ACCEPT = "game_blackjack/doubledown.ogg"
DECLINE = "game_deadmanspoker/fold.ogg"
FOLD = "game_deadmanspoker/fold.ogg"
POINTS = "mention.ogg"
REVEAL_CARDS = "game_deadmanspoker/reveal_private_cards.ogg"
VIRA_REVEAL = "game_deadmanspoker/reveal_card.ogg"
FLOR_ANNOUNCE = "game_uno/playable.ogg"
MAO_DE_ONZE = "game_uno/buzzerpress.ogg"
HAND_ANNULLED = "game_cards/small_shuffle.ogg"
HAND_WIN = "game_uno/winround.ogg"
HAND_LOSE = "game_uno/loseround.ogg"
CAME_WIN = "game_3cardpoker/winbet.ogg"
GAME_WIN = "game_pig/win.ogg"

MUSIC_ARGENTINE = "game_truco/music_argentine.ogg"
MUSIC_BRAZILIAN = "game_truco/music_brazilian.ogg"
MUSIC_SPANISH = "game_truco/music_spanish.ogg"
