"""Centralized sound routing and measured timing for Monopoly."""

from __future__ import annotations

from functools import cache
from pathlib import Path, PurePosixPath

from ...game_utils.audio_duration import measure_audio_duration_ticks
from ...game_utils.dice import DICE_THROW_SOUNDS

TICKS_PER_SECOND = 20

# Human-facing pacing. Sequence delays are serialized, so these transitions
# remain deterministic through save/restore even though cue selection is random.
BOT_ACTION_DELAY_MIN_TICKS = TICKS_PER_SECOND // 2
BOT_ACTION_DELAY_MAX_TICKS = TICKS_PER_SECOND * 2
ROLL_TO_LANDING_PAUSE_TICKS = TICKS_PER_SECOND // 2
LANDING_TO_EVENT_PAUSE_TICKS = TICKS_PER_SECOND // 2
OPENING_ROLL_GAP_TICKS = TICKS_PER_SECOND // 2

SOUND_BOARD_SETUP = "game_monopoly/board_setup.ogg"
SOUND_DECK_SHUFFLE = "game_monopoly/deck_shuffle.ogg"
SOUND_OPENING_ROLLS = DICE_THROW_SOUNDS
SOUND_DICE_ROLLS = tuple(f"game_monopoly/dice_roll{index}.ogg" for index in range(1, 3))
SOUND_ROLL_DOUBLES = "game_monopoly/roll_doubles.ogg"
SOUND_SENT_TO_JAIL = "game_monopoly/sent_to_jail.ogg"
SOUND_LEAVE_JAIL = "game_monopoly/leave_jail.ogg"
SOUND_TOKEN_LANDED = "game_monopoly/token_landed.ogg"
SOUND_CASH_RECEIVED = tuple(
    f"game_monopoly/cash_received{index}.ogg" for index in range(1, 3)
)
SOUND_SNAKE_EYES_BONUS = "game_monopoly/snake_eyes_bonus.ogg"
SOUND_TAX_OR_FINE_PAID = "game_monopoly/tax_or_fine_paid.ogg"
SOUND_LARGE_CASH_PAYOUT = "game_monopoly/large_cash_payout.ogg"
SOUND_PROPERTY_PURCHASED = "game_monopoly/property_purchased.ogg"
SOUND_COLOR_GROUP_COMPLETED = "game_monopoly/color_group_completed.ogg"
SOUND_RENT_PAID = "game_monopoly/rent_paid.ogg"
SOUND_DEVELOPMENT_BUILT = "game_monopoly/development_built.ogg"
SOUND_DEVELOPMENT_SOLD = "game_monopoly/development_sold.ogg"
SOUND_PROPERTY_MORTGAGED = "game_monopoly/property_mortgaged.ogg"
SOUND_PROPERTY_UNMORTGAGED = "game_monopoly/property_unmortgaged.ogg"
SOUND_CARD_DRAWS = tuple(f"game_citadels/deal{index}.ogg" for index in range(1, 3))
SOUND_REPAIR_FEE = "game_monopoly/repair_fee.ogg"
SOUND_AUCTION_STARTED = "game_monopoly/auction_started.ogg"
SOUND_AUCTION_BID = "game_monopoly/auction_bid.ogg"
SOUND_AUCTION_SOLD = "game_monopoly/auction_sold.ogg"
SOUND_TRADE_ACCEPTED = "game_monopoly/trade_accepted.ogg"
SOUND_TRADE_PROPOSED = "game_monopoly/trade_proposed.ogg"
SOUND_DEBT_WARNING = "game_monopoly/debt_warning.ogg"
SOUND_BANKRUPTCY_DECLARED = "game_monopoly/bankruptcy_declared.ogg"
SOUND_GAME_WON = "game_monopoly/game_won.ogg"
SOUND_MUSIC_LOOP = "game_monopoly/music_loop.ogg"
SOUND_TURN = "turn.ogg"

# Ceiling-rounded from the shipped OGG granules. These values are fallbacks;
# development runs remeasure the first available first-party sound pack so an
# asset replacement automatically keeps sequence timing accurate.
AUDIO_DURATIONS_TICKS = {
    SOUND_BOARD_SETUP: 58,
    SOUND_DECK_SHUFFLE: 13,
    SOUND_OPENING_ROLLS[0]: 13,
    SOUND_OPENING_ROLLS[1]: 9,
    SOUND_OPENING_ROLLS[2]: 12,
    SOUND_DICE_ROLLS[0]: 17,
    SOUND_DICE_ROLLS[1]: 21,
    SOUND_ROLL_DOUBLES: 43,
    SOUND_SENT_TO_JAIL: 59,
    SOUND_LEAVE_JAIL: 68,
    SOUND_TOKEN_LANDED: 8,
    SOUND_CASH_RECEIVED[0]: 10,
    SOUND_CASH_RECEIVED[1]: 7,
    SOUND_SNAKE_EYES_BONUS: 45,
    SOUND_TAX_OR_FINE_PAID: 22,
    SOUND_LARGE_CASH_PAYOUT: 61,
    SOUND_PROPERTY_PURCHASED: 42,
    SOUND_COLOR_GROUP_COMPLETED: 89,
    SOUND_RENT_PAID: 26,
    SOUND_DEVELOPMENT_BUILT: 36,
    SOUND_DEVELOPMENT_SOLD: 26,
    SOUND_PROPERTY_MORTGAGED: 26,
    SOUND_PROPERTY_UNMORTGAGED: 26,
    SOUND_CARD_DRAWS[0]: 18,
    SOUND_CARD_DRAWS[1]: 19,
    SOUND_REPAIR_FEE: 19,
    SOUND_AUCTION_STARTED: 6,
    SOUND_AUCTION_BID: 22,
    SOUND_AUCTION_SOLD: 61,
    SOUND_TRADE_ACCEPTED: 14,
    SOUND_TRADE_PROPOSED: 14,
    SOUND_DEBT_WARNING: 82,
    SOUND_BANKRUPTCY_DECLARED: 20,
    SOUND_GAME_WON: 135,
    SOUND_MUSIC_LOOP: 473,
}

MONOPOLY_ASSET_PATHS = tuple(
    path for path in AUDIO_DURATIONS_TICKS if path.startswith("game_monopoly/")
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


@cache
def sound_ticks(sound: str) -> int:
    """Return this server run's asset duration, with metadata as fallback."""

    relative_path = PurePosixPath(sound)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=TICKS_PER_SECOND,
        )
        if measured is not None:
            return measured
    return AUDIO_DURATIONS_TICKS.get(sound, 0)
