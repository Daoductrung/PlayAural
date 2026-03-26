"""
Stats helper utilities for leaderboards and player ratings.

Provides:
- LeaderboardHelper: Build leaderboards from game results
- RatingHelper: Track player skill ratings using OpenSkill (Plackett-Luce model)
"""

from dataclasses import dataclass
from typing import Any, Callable, TYPE_CHECKING

from openskill.models import PlackettLuce

if TYPE_CHECKING:
    from .game_result import GameResult
    from ..persistence.database import Database


@dataclass
class LeaderboardEntry:
    """An entry in a leaderboard."""

    player_id: str
    player_name: str
    value: int | float
    rank: int


class LeaderboardHelper:
    """
    Helper for building leaderboards from game results.

    Supports various aggregation modes (sum, max, avg, count) and
    custom score extraction functions.
    """

    @staticmethod
    def build_from_results(
        results: list["GameResult"],
        score_extractor: Callable[["GameResult", str], int | float | None],
        aggregate: str = "sum",
    ) -> list[LeaderboardEntry]:
        """
        Build a leaderboard from game results.

        Args:
            results: List of game results to aggregate
            score_extractor: Function that extracts a score for a player from a result.
                             Takes (result, player_id) and returns score or None.
            aggregate: Aggregation mode - "sum", "max", "avg", or "count"

        Returns:
            Sorted list of LeaderboardEntry (highest first)

        Example:
            # Total points scored across all Pig games
            leaderboard = LeaderboardHelper.build_from_results(
                results,
                score_extractor=lambda r, pid: r.custom_data.get("final_scores", {}).get(pid),
                aggregate="sum"
            )
        """
        # Collect scores per player
        player_scores: dict[str, list[int | float]] = {}
        player_names: dict[str, str] = {}

        for result in results:
            for player in result.player_results:
                if player.is_bot:
                    continue  # Skip bots in leaderboards

                score = score_extractor(result, player.player_id)
                if score is not None:
                    if player.player_id not in player_scores:
                        player_scores[player.player_id] = []
                        player_names[player.player_id] = player.player_name
                    player_scores[player.player_id].append(score)

        # Aggregate scores
        aggregated: dict[str, int | float] = {}
        for player_id, scores in player_scores.items():
            if aggregate == "sum":
                aggregated[player_id] = sum(scores)
            elif aggregate == "max":
                aggregated[player_id] = max(scores)
            elif aggregate == "avg":
                aggregated[player_id] = sum(scores) / len(scores) if scores else 0
            elif aggregate == "count":
                aggregated[player_id] = len(scores)
            else:
                raise ValueError(f"Unknown aggregate mode: {aggregate}")

        # Sort and build entries
        sorted_players = sorted(
            aggregated.items(), key=lambda x: x[1], reverse=True
        )

        entries = []
        for rank, (player_id, value) in enumerate(sorted_players, 1):
            entries.append(
                LeaderboardEntry(
                    player_id=player_id,
                    player_name=player_names[player_id],
                    value=value,
                    rank=rank,
                )
            )

        return entries

    @staticmethod
    def build_wins_leaderboard(
        results: list["GameResult"],
        winner_extractor: Callable[["GameResult"], str | None] = None,
    ) -> list[LeaderboardEntry]:
        """
        Build a leaderboard based on win count.

        Args:
            results: List of game results
            winner_extractor: Function to extract winner player_id from result.
                              Defaults to checking custom_data["winner_name"].

        Returns:
            Sorted list of LeaderboardEntry by wins (highest first)
        """
        if winner_extractor is None:
            # Default: look up winner by name in player_results
            def winner_extractor(r: "GameResult") -> str | None:
                winner_name = r.custom_data.get("winner_name")
                if winner_name:
                    for p in r.player_results:
                        if p.player_name == winner_name:
                            return p.player_id
                return None

        def score_extractor(result: "GameResult", player_id: str) -> int | None:
            winner_id = winner_extractor(result)
            if winner_id == player_id:
                return 1
            return 0

        return LeaderboardHelper.build_from_results(
            results, score_extractor, aggregate="sum"
        )


@dataclass
class PlayerRating:
    """A player's skill rating."""

    player_id: str
    mu: float  # Mean skill estimate
    sigma: float  # Uncertainty (standard deviation)

    @property
    def ordinal(self) -> float:
        """Conservative skill estimate (mu - 3*sigma)."""
        return self.mu - 3 * self.sigma

    def __str__(self) -> str:
        return f"{self.mu:.1f} ± {self.sigma:.1f}"


class RatingHelper:
    """
    Helper for tracking player skill ratings using OpenSkill.

    Uses the Plackett-Luce model which supports:
    - Any number of players (not just 2)
    - Teams
    - Ties (players in same rank group)

    Ratings are stored in the database and updated after each game.
    """

    # Default rating values (same as OpenSkill defaults)
    DEFAULT_MU = 25.0
    DEFAULT_SIGMA = 25.0 / 3  # ~8.333

    def __init__(self, db: "Database", game_type: str):
        """
        Create a rating helper for a specific game type.

        Args:
            db: Database connection for persistence
            game_type: The game type these ratings are for
        """
        self.db = db
        self.game_type = game_type
        self.model = PlackettLuce()

    def get_rating(self, player_id: str) -> PlayerRating:
        """
        Get a player's current rating.

        Returns default rating if player has no rating history.
        """
        result = self.db.get_player_rating(player_id, self.game_type)
        if result:
            mu, sigma = result
            return PlayerRating(player_id=player_id, mu=mu, sigma=sigma)
        return PlayerRating(
            player_id=player_id,
            mu=self.DEFAULT_MU,
            sigma=self.DEFAULT_SIGMA,
        )

    def get_ratings(self, player_ids: list[str]) -> dict[str, PlayerRating]:
        """Get ratings for multiple players."""
        return {pid: self.get_rating(pid) for pid in player_ids}

    def update_ratings(
        self,
        teams: list[list[str]],
        ranks: list[int] | None = None,
    ) -> dict[str, PlayerRating]:
        """
        Update ratings based on game outcome.

        Args:
            teams: Competitors in the match. Each inner list is either a
                   single player or a true team of cooperating players.
            ranks: Optional placement ranks aligned with ``teams``.
                   Lower values are better. Equal values indicate ties.

        Returns:
            Dictionary of updated ratings for all players.

        Example:
            # Alice won, Bob and Charlie tied for 2nd
            helper.update_ratings(
                [["alice_id"], ["bob_id"], ["charlie_id"]],
                ranks=[0, 1, 1],
            )

            # Team game: Alice and Bob beat Charlie and Dana
            helper.update_ratings([["alice", "bob"], ["charlie", "dana"]], ranks=[0, 1])
        """
        # Flatten to get all player IDs
        all_players = [pid for group in teams for pid in group]

        # Get current ratings
        current_ratings = self.get_ratings(all_players)

        # Convert to OpenSkill format
        model_teams = []
        for group in teams:
            team_ratings = []
            for pid in group:
                r = current_ratings[pid]
                team_ratings.append(self.model.rating(mu=r.mu, sigma=r.sigma))
            model_teams.append(team_ratings)

        # Calculate new ratings
        new_teams = self.model.rate(model_teams, ranks=ranks)

        # Update database and build result
        updated_ratings: dict[str, PlayerRating] = {}

        for group_idx, group in enumerate(teams):
            for player_idx, pid in enumerate(group):
                new_rating = new_teams[group_idx][player_idx]
                self.db.set_player_rating(
                    pid, self.game_type, new_rating.mu, new_rating.sigma
                )
                updated_ratings[pid] = PlayerRating(
                    player_id=pid,
                    mu=new_rating.mu,
                    sigma=new_rating.sigma,
                )

        return updated_ratings

    def update_from_result(
        self,
        result: "GameResult",
        ranking_extractor: Callable[["GameResult"], list[list[str]]] | None = None,
    ) -> dict[str, PlayerRating]:
        """
        Update ratings from a GameResult.

        Args:
            result: The game result
            ranking_extractor: Optional function that returns actual competitors
                               in finishing order. Each inner list must be a
                               real team, not a tie bucket.

        Returns:
            Dictionary of updated ratings.
        """
        if ranking_extractor is None:
            teams, ranks = self.extract_teams_and_ranks(result)
        else:
            teams = ranking_extractor(result)
            if not teams:
                return {}
            ranks = list(range(len(teams)))

        if not teams:
            return {}

        return self.update_ratings(teams, ranks=ranks)

    @staticmethod
    def extract_teams_and_ranks(
        result: "GameResult",
    ) -> tuple[list[list[str]], list[int]]:
        """Build true OpenSkill competitors and placement ranks from a game result."""
        human_players = [p for p in result.player_results if not p.is_bot]
        if not human_players:
            return [], []

        name_to_id = {p.player_name: p.player_id for p in human_players}
        team_rankings = result.custom_data.get("team_rankings")
        if isinstance(team_rankings, list) and team_rankings:
            teams: list[list[str]] = []
            ranks: list[int] = []
            last_score = object()
            current_rank = -1

            for entry in team_rankings:
                if not isinstance(entry, dict):
                    continue
                members = entry.get("members", [])
                if not isinstance(members, list):
                    continue
                team_ids = [name_to_id[name] for name in members if name in name_to_id]
                if not team_ids:
                    continue

                score = entry.get("score")
                if current_rank == -1:
                    current_rank = 0
                elif score != last_score:
                    current_rank += 1

                teams.append(team_ids)
                ranks.append(current_rank)
                last_score = score

            if teams:
                return teams, ranks

        winner_ids = result.custom_data.get("winner_ids") or []
        if not winner_ids:
            winner_name = result.custom_data.get("winner_name")
            if winner_name:
                winner_ids = [
                    p.player_id for p in human_players if p.player_name == winner_name
                ]

        if winner_ids:
            winner_set = set(winner_ids)
            human_ids = {p.player_id for p in human_players}
            teams = [[pid] for pid in winner_ids if pid in human_ids]
            ranks = [0] * len(teams)

            for player in human_players:
                if player.player_id in winner_set:
                    continue
                teams.append([player.player_id])
                ranks.append(1)

            if teams:
                return teams, ranks

        teams = [[p.player_id] for p in human_players]
        ranks = [0] * len(teams)
        return teams, ranks

    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, PlayerRating]]:
        """
        Get the rating leaderboard for this game type.

        Returns a list of (player_name, PlayerRating) tuples sorted by ordinal.
        """
        rows = self.db.get_rating_leaderboard(self.game_type, limit)
        return [
            (pname, PlayerRating(player_id=pid, mu=mu, sigma=sigma))
            for pid, pname, mu, sigma in rows
        ]

    def predict_win_probability(
        self, player1_id: str, player2_id: str
    ) -> float:
        """
        Predict the probability that player1 beats player2.

        Returns a value between 0 and 1.
        """
        r1 = self.get_rating(player1_id)
        r2 = self.get_rating(player2_id)

        rating1 = self.model.rating(mu=r1.mu, sigma=r1.sigma)
        rating2 = self.model.rating(mu=r2.mu, sigma=r2.sigma)

        # Use OpenSkill's predict_win
        return self.model.predict_win([[rating1], [rating2]])[0]
