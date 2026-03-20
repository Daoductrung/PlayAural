from ...game_utils.bot_helper import BotHelper
import random

def bot_think(game, player) -> str | None:
    """Bot AI decision making."""
    perceived_pipe = game._get_bot_perceived_pipe(player)

    # Check if we should reshuffle
    if (
        not player.has_reshuffled
        and player.reshuffle_uses < game.options.reshuffle_limit
        and len(game.pipe) >= 6
    ):
        # Count negative balls in the first 3 positions
        negative_count = sum(
            1 for i in range(min(3, len(game.pipe))) if perceived_pipe[i]["value"] <= -2
        )
        if negative_count >= 2:
            return "reshuffle"

    # Get available take actions
    take_actions = []
    turn_set = game.get_action_set(player, "turn")
    if turn_set:
        for action_id in turn_set._order:
            if action_id.startswith("take_") and game._is_take_enabled(player, action_id) is None:
                take_actions.append(int(action_id.removeprefix("take_")))

    if not take_actions:
        return None

    best_take = take_actions[0]
    best_value = -999
    for test_take in take_actions:
        cumulative = sum(
            perceived_pipe[i]["value"] for i in range(test_take)
        )
        if cumulative > best_value or (
            cumulative == best_value and random.randint(0, 1) == 0  # nosec B311
        ):
            best_value = cumulative
            best_take = test_take

    return f"take_{best_take}"
