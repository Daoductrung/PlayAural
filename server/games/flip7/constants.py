"""Shared constants for Flip 7.

Live in their own module so ``game.py`` and ``bot.py`` can both import them
at module scope without a circular import.
"""

FLIP_SEVEN_TARGET = 7
FLIP_SEVEN_BONUS = 15
FLIP_THREE_COUNT = 3
MAX_NUMBER = 12
MODIFIER_VALUES = (2, 4, 6, 8, 10)
ACTION_COPIES = 3

CARD_NUMBER = "number"
CARD_MODIFIER = "modifier"
CARD_DOUBLE = "double"
CARD_SECOND_CHANCE = "second_chance"
CARD_FREEZE = "freeze"
CARD_FLIP_THREE = "flip_three"

STATUS_PLAYING = "playing"
STATUS_STAYED = "stayed"
STATUS_BUSTED = "busted"

PHASE_PLAYING = "playing"
PHASE_ROUND_END = "round_end"
PHASE_MATCH_END = "match_end"

CHOICE_FREEZE = "freeze"
CHOICE_FLIP_THREE = "flip_three"
CHOICE_SECOND_CHANCE = "second_chance"

# Choice kinds use ids internally but hyphenated suffixes in locale keys.
CHOICE_KEY_SUFFIX = {
    CHOICE_FREEZE: "freeze",
    CHOICE_FLIP_THREE: "flip-three",
    CHOICE_SECOND_CHANCE: "second-chance",
}

OUTCOME_OK = "ok"
OUTCOME_SAVED = "saved"
OUTCOME_BUST = "bust"
OUTCOME_FLIP7 = "flip7"
OUTCOME_CHOICE = "choice"
OUTCOME_STOP_ALONE = "stop_alone"
# Forced action cards drawn inside a Flip Three become queued pending actions.
OUTCOME_PENDING = "pending"
# A targeted choice resolved by handing control to a freshly started flow.
OUTCOME_FLOW = "flow"

TICKS_PER_SECOND = 20

# Fixed speech pacing before a reveal. This covers a short localized line
# ("Player1 turns over a card."), not an audio asset, so it stays fixed.
TURN_CARD_TICKS = TICKS_PER_SECOND

# Floor after a reveal sound so the localized card label has room to speak.
# Number/modifier reveal cues are shorter than a spoken sentence.
MIN_REVEAL_SPEECH_TICKS = 24

BOT_MIN_THINK_TICKS = TICKS_PER_SECOND
BOT_MAX_THINK_TICKS = TICKS_PER_SECOND + TICKS_PER_SECOND // 2

SEQUENCE_CARD_FLOW_PREFIX = "flip7_card_flow"
SEQUENCE_ROUND_START_PREFIX = "flip7_round_start"
SEQUENCE_MATCH_END_PREFIX = "flip7_match_end"
TAG_FLOW = "flip7_card_flow"

# Continuation callback ids understood by on_sequence_callback.
CONTINUE_FLOW = "continue_flow"
NEXT_FLIP_DRAW = "next_flip_draw"