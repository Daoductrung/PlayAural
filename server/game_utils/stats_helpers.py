"""Skill-rating helpers and canonical competitive-result encoding."""

from dataclasses import dataclass
import math
from typing import Any, Iterable, TYPE_CHECKING

from openskill.models import PlackettLuce

if TYPE_CHECKING:
    from .game_result import GameResult
    from ..persistence.database import Database


RATING_COMPETITORS_KEY = "rating_competitors"
RATING_CONFIDENCE_Z = 3.0


def rating_competitors_from_scores(
    ranked_competitors: Iterable[tuple[Iterable[str], Any]],
) -> list[dict[str, Any]]:
    """Encode already-sorted competitors with dense ranks and UUID identities.

    Each competitor is either one player or a real cooperating team. Equal
    score values receive the same rank. Games remain responsible for ordering
    the values according to their own rules before calling this helper.
    """
    encoded: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    previous_score: Any = object()
    rank = -1

    for player_ids, score in ranked_competitors:
        normalized_ids = list(player_ids)
        if not normalized_ids or any(
            not isinstance(player_id, str) or not player_id
            for player_id in normalized_ids
        ):
            raise ValueError("rating competitors require non-empty player ids")
        if len(set(normalized_ids)) != len(normalized_ids):
            raise ValueError("a rating competitor contains duplicate player ids")
        duplicate_ids = seen_ids.intersection(normalized_ids)
        if duplicate_ids:
            raise ValueError("a player cannot belong to multiple rating competitors")

        if rank == -1 or score != previous_score:
            rank += 1
        encoded.append({"player_ids": normalized_ids, "rank": rank})
        seen_ids.update(normalized_ids)
        previous_score = score

    return encoded


@dataclass
class PlayerRating:
    """A player's skill rating."""

    player_id: str
    mu: float  # Mean skill estimate
    sigma: float  # Uncertainty (standard deviation)

    @property
    def skill_score(self) -> float:
        """Return the stable player-facing score derived from model state."""
        return self.mu - RATING_CONFIDENCE_Z * self.sigma


class RatingHelper:
    """
    Helper for tracking player skill ratings using OpenSkill.

    Uses the Plackett-Luce model which supports:
    - Any number of players (not just 2)
    - Teams
    - Ties (players in same rank group)

    Existing ratings are read from the database, while update calculation is
    pure so the result and all resulting ratings can be committed atomically.
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
        existing = self.get_existing_rating(player_id)
        if existing is not None:
            return existing
        return PlayerRating(
            player_id=player_id,
            mu=self.DEFAULT_MU,
            sigma=self.DEFAULT_SIGMA,
        )

    def get_existing_rating(self, player_id: str) -> PlayerRating | None:
        """Return a persisted rating, or ``None`` before the first rated match."""
        result = self.db.get_player_rating(player_id, self.game_type)
        if result is None:
            return None
        mu, sigma = result
        return PlayerRating(player_id=player_id, mu=mu, sigma=sigma)

    def get_ratings(self, player_ids: list[str]) -> dict[str, PlayerRating]:
        """Get ratings for multiple players."""
        return {pid: self.get_rating(pid) for pid in player_ids}

    def calculate_updates(
        self,
        teams: list[list[str]],
        ranks: list[int] | None = None,
    ) -> dict[str, PlayerRating]:
        """
        Calculate rating updates without writing them to persistence.

        Args:
            teams: Competitors in the match. Each inner list is either a
                   single player or a true team of cooperating players.
            ranks: Optional placement ranks aligned with ``teams``.
                   Lower values are better. Equal values indicate ties.

        Returns:
            Dictionary of updated ratings for all players.

        Example:
            # Alice won, Bob and Charlie tied for 2nd
            helper.calculate_updates(
                [["alice_id"], ["bob_id"], ["charlie_id"]],
                ranks=[0, 1, 1],
            )

            # Team game: Alice and Bob beat Charlie and Dana
            helper.calculate_updates(
                [["alice", "bob"], ["charlie", "dana"]],
                ranks=[0, 1],
            )
        """
        if ranks is not None and len(ranks) != len(teams):
            raise ValueError("rating ranks must align with competitors")
        if ranks is not None and any(
            isinstance(rank, bool) or not isinstance(rank, int) or rank < 0
            for rank in ranks
        ):
            raise ValueError("rating ranks must be non-negative integers")

        all_players = [pid for group in teams for pid in group]
        if any(not group for group in teams):
            raise ValueError("rating competitors cannot be empty")
        if any(not isinstance(pid, str) or not pid for pid in all_players):
            raise ValueError("rating player ids must be non-empty strings")
        if len(set(all_players)) != len(all_players):
            raise ValueError("a player cannot appear in multiple rating competitors")
        if len(teams) < 2:
            return {}

        current_ratings = self.get_ratings(all_players)

        model_teams = []
        for group in teams:
            team_ratings = []
            for pid in group:
                r = current_ratings[pid]
                if not math.isfinite(r.mu) or not math.isfinite(r.sigma) or r.sigma <= 0:
                    raise ValueError("stored ratings must be finite with positive sigma")
                team_ratings.append(self.model.rating(mu=r.mu, sigma=r.sigma))
            model_teams.append(team_ratings)

        new_teams = self.model.rate(model_teams, ranks=ranks)
        updated_ratings: dict[str, PlayerRating] = {}

        for group_idx, group in enumerate(teams):
            for player_idx, pid in enumerate(group):
                new_rating = new_teams[group_idx][player_idx]
                if (
                    not math.isfinite(new_rating.mu)
                    or not math.isfinite(new_rating.sigma)
                    or new_rating.sigma <= 0
                ):
                    raise ValueError("rating model produced an invalid rating")
                updated_ratings[pid] = PlayerRating(
                    player_id=pid,
                    mu=new_rating.mu,
                    sigma=new_rating.sigma,
                )

        return updated_ratings

    @staticmethod
    def extract_teams_and_ranks(
        result: "GameResult",
    ) -> tuple[list[list[str]], list[int]]:
        """Build validated OpenSkill competitors from immutable result ids."""
        human_players = [p for p in result.player_results if not p.is_bot]
        if not human_players:
            return [], []
        all_player_ids = [player.player_id for player in result.player_results]
        if any(not player_id for player_id in all_player_ids):
            raise ValueError("game results cannot contain empty player ids")
        if len(set(all_player_ids)) != len(all_player_ids):
            raise ValueError("game results cannot contain duplicate player ids")
        human_ids = {player.player_id for player in human_players}
        result_ids = set(all_player_ids)

        encoded_competitors = result.custom_data.get(RATING_COMPETITORS_KEY)
        if encoded_competitors is not None:
            if not isinstance(encoded_competitors, list) or not encoded_competitors:
                raise ValueError("rating competitors must be a non-empty list")
            teams: list[list[str]] = []
            ranks: list[int] = []
            represented_ids: set[str] = set()
            for entry in encoded_competitors:
                if not isinstance(entry, dict):
                    raise ValueError("each rating competitor must be an object")
                player_ids = entry.get("player_ids")
                rank = entry.get("rank")
                if (
                    not isinstance(player_ids, list)
                    or not player_ids
                    or any(not isinstance(pid, str) or not pid for pid in player_ids)
                ):
                    raise ValueError("rating competitors require player id lists")
                if len(set(player_ids)) != len(player_ids):
                    raise ValueError("a rating competitor contains duplicate ids")
                if represented_ids.intersection(player_ids):
                    raise ValueError("a player appears in multiple rating competitors")
                if not set(player_ids).issubset(result_ids):
                    raise ValueError("a rating competitor references an unknown player")
                if isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
                    raise ValueError("rating competitor ranks must be non-negative integers")

                represented_ids.update(player_ids)
                human_team = [pid for pid in player_ids if pid in human_ids]
                if not human_team:
                    continue
                teams.append(human_team)
                ranks.append(rank)

            if represented_ids != result_ids:
                raise ValueError("rating competitors must cover every result participant")
            return teams, ranks

        if "winner_ids" not in result.custom_data:
            raise ValueError("rated game results must declare immutable winner ids")
        winner_ids = result.custom_data["winner_ids"]
        if (
            not isinstance(winner_ids, list)
            or any(not isinstance(pid, str) or not pid for pid in winner_ids)
            or len(set(winner_ids)) != len(winner_ids)
        ):
            raise ValueError("winner ids must be a unique list of non-empty strings")
        if not set(winner_ids).issubset(result_ids):
            raise ValueError("winner ids must reference result participants")

        human_winner_ids = [pid for pid in winner_ids if pid in human_ids]
        if human_winner_ids:
            winner_set = set(human_winner_ids)
            teams = [[pid] for pid in human_winner_ids]
            ranks = [0] * len(teams)

            for player in human_players:
                if player.player_id in winner_set:
                    continue
                teams.append([player.player_id])
                ranks.append(1)

            if teams:
                return teams, ranks

        teams = [[player.player_id] for player in human_players]
        ranks = [0] * len(teams)
        return teams, ranks

    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, PlayerRating]]:
        """
        Get the rating leaderboard for this game type.

        Returns entries sorted by the conservative player-facing skill score.
        """
        rows = self.db.get_rating_leaderboard(
            self.game_type,
            limit,
            confidence_z=RATING_CONFIDENCE_Z,
        )
        return [
            (pname, PlayerRating(player_id=pid, mu=mu, sigma=sigma))
            for pid, pname, mu, sigma in rows
        ]
