from typing import Any
from .game_result import GameResult

class StatsExtractor:
    """Utility class to extract stats from GameResult for updating player_game_stats."""

    @staticmethod
    def extract_incremental_stats(result: GameResult) -> dict[str, dict[str, float]]:
        """
        Extracts incremental statistics updates for all human players in a game result.
        Returns dict: player_id -> {stat_key: value_to_add_or_max}
        """
        updates: dict[str, dict[str, float]] = {}

        # Built-in stats extraction
        winner_name = result.custom_data.get("winner_name")
        winner_ids = result.custom_data.get("winner_ids", [])
        final_scores = result.custom_data.get("final_scores", {})
        final_light = result.custom_data.get("final_light", {})

        from ..games.registry import get_game_class
        game_class = get_game_class(result.game_type)
        if not game_class:
            return updates

        for p in result.player_results:
            if p.is_bot:
                continue

            player_id = p.player_id
            player_name = p.player_name
            updates[player_id] = {}

            # games_played
            updates[player_id]["games_played"] = 1.0

            # wins/losses
            is_winner = False
            if winner_ids:
                if player_id in winner_ids:
                    is_winner = True
            elif winner_name == player_name:
                is_winner = True

            if is_winner:
                updates[player_id]["wins"] = 1.0
            else:
                updates[player_id]["losses"] = 1.0

            # scores
            score = final_scores.get(player_name, 0)
            if not score:
                score = final_light.get(player_name, 0)

            if score:
                updates[player_id]["total_score"] = float(score)
                # Using special suffix '_high' to tell caller to MAX instead of SUM
                updates[player_id]["high_score_high"] = float(score)

            # Custom stats
            for config in game_class.get_leaderboard_types():
                lb_id = config["id"]
                path = config.get("path")
                numerator_path = config.get("numerator")
                denominator_path = config.get("denominator")
                aggregate = config.get("aggregate", "sum")

                # Check path extraction
                if path:
                    resolved_path = path.replace("{player_name}", player_name).replace("{player_id}", player_id)
                    val = StatsExtractor._extract_path_value(result.custom_data, resolved_path)
                    if val is not None:
                        if aggregate == "max":
                            updates[player_id][f"custom_{lb_id}_high"] = float(val)
                        else:
                            updates[player_id][f"custom_{lb_id}"] = float(val)

                # Check numerator/denominator extraction (e.g. for ratios like win percentage in Coup)
                elif numerator_path and denominator_path:
                    num_path = numerator_path.replace("{player_name}", player_name).replace("{player_id}", player_id)
                    denom_path = denominator_path.replace("{player_name}", player_name).replace("{player_id}", player_id)

                    num_val = StatsExtractor._extract_path_value(result.custom_data, num_path)
                    denom_val = StatsExtractor._extract_path_value(result.custom_data, denom_path)

                    if num_val is not None and denom_val is not None:
                        updates[player_id][f"custom_{lb_id}_numerator"] = float(num_val)
                        updates[player_id][f"custom_{lb_id}_denominator"] = float(denom_val)

        return updates

    @staticmethod
    def _extract_path_value(data: dict, path: str) -> float | None:
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        if isinstance(current, (int, float)):
            return float(current)
        return None
