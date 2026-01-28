"""Mixin providing win probability prediction for games."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User

from .stats_helpers import RatingHelper
from ..messages.localization import Localization


class GamePredictionMixin:
    """Mixin providing win probability predictions based on player ratings.

    Expects on the Game class:
        - self._table: Any
        - self.players: list[Player]
        - self.get_user(player) -> User | None
        - self.get_type() -> str
        - self.status_box(player, lines)
    """

    def _action_predict_outcomes(self, player: "Player", action_id: str) -> None:
        """Show predicted outcomes based on player ratings."""
        user = self.get_user(player)
        if not user:
            return

        if not self._table or not self._table._db:
            user.speak_l("predict-unavailable")
            return

        rating_helper = RatingHelper(self._table._db, self.get_type())

        # Get human players only (exclude spectators)
        human_players = [
            p for p in self.players if not p.is_bot and not p.is_spectator
        ]

        if len(human_players) < 2:
            user.speak_l("predict-need-players")
            return

        # Get ratings for all players
        player_ratings = []
        for p in human_players:
            rating = rating_helper.get_rating(p.id)
            player_ratings.append((p, rating))

        # Sort by ordinal (conservative skill estimate) descending
        player_ratings.sort(key=lambda x: x[1].ordinal, reverse=True)

        # Format predictions
        lines = [Localization.get(user.locale, "predict-header")]

        for rank, (p, rating) in enumerate(player_ratings, 1):
            # Calculate win probability against the field
            if len(player_ratings) == 2:
                # 2 players: show head-to-head probability
                other = player_ratings[1] if rank == 1 else player_ratings[0]
                win_prob = rating_helper.predict_win_probability(p.id, other[0].id)
                lines.append(
                    Localization.get(
                        user.locale,
                        "predict-entry-2p",
                        rank=rank,
                        player=p.name,
                        rating=round(rating.ordinal),
                        probability=round(win_prob * 100),
                    )
                )
            else:
                # 3+ players: show rating only (probabilities get complex)
                lines.append(
                    Localization.get(
                        user.locale,
                        "predict-entry",
                        rank=rank,
                        player=p.name,
                        rating=round(rating.ordinal),
                    )
                )

        self.status_box(player, lines)
