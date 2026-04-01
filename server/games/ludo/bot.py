"""Bot AI for Ludo."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import LudoGame, LudoPlayer

_TRACK_LENGTH = 52
_HOME_COLUMN_LENGTH = 6


def bot_think(game: "LudoGame", player: "LudoPlayer") -> str | None:
    """Return the bot's next action."""
    if player != game.current_player:
        return None
    if player.move_options:
        best_index = _best_move_index(game, player)
        if best_index is not None:
            return f"move_token_{best_index + 1}"
    return "roll_dice"


def _best_move_index(game: "LudoGame", player: "LudoPlayer") -> int | None:
    """Pick the best move index for a bot.

    Priority:
    1. Finish a token (home_column that can reach end)
    2. Capture an opponent
    3. Advance in home column (closer to finish)
    4. Move to a safe square
    5. Advance on track (prefer tokens further along)
    6. Enter from yard
    """
    if not player.move_options:
        return None

    best_index = None
    best_score = -1
    for idx in player.move_options:
        token = player.tokens[idx]
        score = 0

        if token.state == "home_column":
            new_pos = token.position + game.last_roll
            if new_pos >= _HOME_COLUMN_LENGTH:
                score = 2000  # finishing a token is top priority
            else:
                score = 1000 + new_pos
        elif token.state == "track":
            home_entry = game._get_home_entry_position(player)
            new_pos = token.position + game.last_roll
            # Check if this move enters home column or finishes
            if token.position <= home_entry and new_pos > home_entry:
                overshoot = new_pos - home_entry
                if overshoot >= _HOME_COLUMN_LENGTH:
                    score = 2000  # finish
                else:
                    score = 1500 + overshoot  # entering home column
            else:
                landing = ((new_pos - 1) % _TRACK_LENGTH) + 1
                # Check for capture opportunity
                captured_tokens = game._get_tokens_at_position(landing, player)
                if captured_tokens and not game._is_safe_square(landing, player):
                    score = 1800 + len(captured_tokens) * 100  # bigger stacks are better captures
                elif game._is_safe_square(landing, player):
                    score = 700 + token.position  # safe square is good
                else:
                    score = 500 + token.position  # further along = better
        elif token.state == "yard":
            # Entering from yard — check if we'd capture on start square
            start = game._get_start_position(player)
            captured_tokens = game._get_tokens_at_position(start, player)
            if captured_tokens and not game._is_safe_square(start, player):
                score = 1800 + len(captured_tokens) * 100  # capture on entry
            else:
                score = 300

        if score > best_score:
            best_score = score
            best_index = idx

    return best_index
