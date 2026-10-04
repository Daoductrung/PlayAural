import math

from .game_result import GameResult
from ..games import registry as game_registry


class StatsExtractor:
    """Utility class to extract stats from GameResult for updating player_game_stats."""

    @staticmethod
    def supported_persisted_stat_keys(game_class: type) -> set[str]:
        """Return the complete derived-stat schema owned by one game class."""
        supported_leaderboards = set(game_class.get_supported_leaderboards())
        keys: set[str] = set()
        if "games_played" in supported_leaderboards:
            keys.add("games_played")
        if "wins" in supported_leaderboards:
            keys.update(("wins", "losses"))
        if "total_score" in supported_leaderboards:
            keys.add("total_score")
        if "high_score" in supported_leaderboards:
            keys.add("high_score")

        for config in game_class.get_leaderboard_types():
            leaderboard_id = config["id"]
            aggregate = config.get("aggregate", "sum")
            if config.get("path"):
                if aggregate == "avg":
                    keys.update(
                        (
                            f"custom_{leaderboard_id}_sum",
                            f"custom_{leaderboard_id}_count",
                        )
                    )
                elif aggregate == "max":
                    keys.add(f"custom_{leaderboard_id}_high")
                else:
                    keys.add(f"custom_{leaderboard_id}")
            elif config.get("numerator") and config.get("denominator"):
                keys.update(
                    (
                        f"custom_{leaderboard_id}_numerator",
                        f"custom_{leaderboard_id}_denominator",
                    )
                )
        return keys

    @staticmethod
    def extract_incremental_stats(result: GameResult) -> dict[str, dict[str, float]]:
        """
        Extracts incremental statistics updates for all human players in a game result.
        Returns dict: player_id -> {stat_key: value_to_add_or_max}
        """
        updates: dict[str, dict[str, float]] = {}
        if result.custom_data.get("competitive") is False:
            return updates

        game_class = game_registry.get_game_class(result.game_type)
        if not game_class:
            return updates

        supported_leaderboards = set(game_class.get_supported_leaderboards())
        supports_games_played = "games_played" in supported_leaderboards
        supports_wins = "wins" in supported_leaderboards
        supports_total_score = "total_score" in supported_leaderboards
        supports_high_score = "high_score" in supported_leaderboards

        result_ids = [player.player_id for player in result.player_results]
        if any(
            not isinstance(player_id, str) or not player_id
            for player_id in result_ids
        ):
            raise ValueError("game results require non-empty player ids")
        if len(set(result_ids)) != len(result_ids):
            raise ValueError("game results cannot contain duplicate player ids")

        winner_ids: set[str] = set()
        if supports_wins:
            if "winner_ids" not in result.custom_data:
                raise ValueError("win statistics require immutable winner ids")
            raw_winner_ids = result.custom_data["winner_ids"]
            if (
                not isinstance(raw_winner_ids, list)
                or any(
                    not isinstance(player_id, str) or not player_id
                    for player_id in raw_winner_ids
                )
                or len(set(raw_winner_ids)) != len(raw_winner_ids)
            ):
                raise ValueError(
                    "winner ids must be a unique list of non-empty strings"
                )
            winner_ids = set(raw_winner_ids)
            if not winner_ids.issubset(result_ids):
                raise ValueError("winner ids must reference result participants")

        has_decisive_outcome = bool(winner_ids)
        final_scores = result.custom_data.get("final_scores", {})
        final_light = result.custom_data.get("final_light", {})

        for p in result.player_results:
            if p.is_bot:
                continue

            player_id = p.player_id
            player_name = p.player_name
            player_updates: dict[str, float] = {}

            # games_played
            if supports_games_played:
                player_updates["games_played"] = 1.0

            # wins/losses
            if supports_wins:
                if player_id in winner_ids:
                    player_updates["wins"] = 1.0
                elif has_decisive_outcome:
                    player_updates["losses"] = 1.0

            # scores
            score = final_scores.get(player_name)
            if score is None:
                score = final_light.get(player_name)

            if StatsExtractor._is_finite_number(score):
                if supports_total_score:
                    player_updates["total_score"] = float(score)
                if supports_high_score:
                    # Using special suffix '_high' to tell caller to MAX instead of SUM
                    player_updates["high_score_high"] = float(score)

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
                            player_updates[f"custom_{lb_id}_high"] = float(val)
                        elif aggregate == "avg":
                            player_updates[f"custom_{lb_id}_sum"] = float(val)
                            player_updates[f"custom_{lb_id}_count"] = 1.0
                        else:
                            player_updates[f"custom_{lb_id}"] = float(val)

                # Check numerator/denominator extraction (e.g. for ratios like win percentage in Coup)
                elif numerator_path and denominator_path:
                    num_path = numerator_path.replace("{player_name}", player_name).replace("{player_id}", player_id)
                    denom_path = denominator_path.replace("{player_name}", player_name).replace("{player_id}", player_id)

                    num_val = StatsExtractor._extract_path_value(result.custom_data, num_path)
                    denom_val = StatsExtractor._extract_path_value(result.custom_data, denom_path)

                    if num_val is not None and denom_val is not None:
                        player_updates[f"custom_{lb_id}_numerator"] = float(num_val)
                        player_updates[f"custom_{lb_id}_denominator"] = float(denom_val)

            if player_updates:
                updates[player_id] = player_updates

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
        if StatsExtractor._is_finite_number(current):
            return float(current)
        return None

    @staticmethod
    def _is_finite_number(value: object) -> bool:
        """Return whether a stat value is numeric, finite, and not boolean."""
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(value)
        )
