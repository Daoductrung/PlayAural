"""
Scoring logic for Scopa game.

Handles round scoring, winner detection, and game end.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...game_utils.cards import Card
from ...game_utils.teams import Team

if TYPE_CHECKING:
    from .game import ScopaGame, ScopaPlayer


@dataclass(frozen=True)
class ScoringUnit:
    """A team or player pile evaluated for one Scopa scoring category."""

    owner_name: str
    team: Team
    cards: list[Card]
    members: list[str]
    is_team: bool = False


def get_team_captured_cards(players: list["ScopaPlayer"], team: Team) -> list[Card]:
    """Get all cards captured by team members."""
    cards = []
    for player in players:
        if player.name in team.members:
            cards.extend(player.captured)
    return cards


def build_scoring_units(game: "ScopaGame") -> list[ScoringUnit]:
    """Build card piles according to the team card scoring option."""
    teams = game.team_manager.get_alive_teams() or game.team_manager.teams
    active_players = [
        player
        for player in game.get_active_players()
        if not player.is_spectator
    ]

    if game.options.team_card_scoring:
        units: list[ScoringUnit] = []
        for team in teams:
            units.append(
                ScoringUnit(
                    owner_name=game.team_manager.get_team_name(team),
                    team=team,
                    cards=get_team_captured_cards(game.players, team),
                    members=list(team.members),
                    is_team=len(team.members) > 1,
                )
            )
        return units

    units = []
    alive_teams = set(id(team) for team in teams)
    for player in active_players:
        team = game.team_manager.get_team(player.name)
        if not team or id(team) not in alive_teams:
            continue
        units.append(
            ScoringUnit(
                owner_name=player.name,
                team=team,
                cards=list(player.captured),
                members=[player.name],
                is_team=False,
            )
        )
    return units


def _unit_display_name(game: "ScopaGame", unit: ScoringUnit, locale: str) -> str:
    if unit.is_team:
        return game.team_manager.get_team_name(unit.team, locale)
    return unit.owner_name


def _award_unit_point(game: "ScopaGame", unit: ScoringUnit, points: int = 1) -> None:
    if unit.team.members:
        game.team_manager.add_to_team_round_score(unit.team.members[0], points)


def broadcast_scoring_unit_l(
    game: "ScopaGame",
    unit: ScoringUnit,
    personal_message_id: str,
    team_message_id: str,
    others_message_id: str,
    **kwargs,
) -> None:
    """Announce a scoring result in first person to the scoring side."""
    for player in game.players:
        user = game.get_user(player)
        if not user:
            continue

        if player.name in unit.members:
            message_id = team_message_id if unit.is_team else personal_message_id
            user.speak_l(message_id, buffer="game", **kwargs)
        else:
            user.speak_l(
                others_message_id,
                buffer="game",
                player=_unit_display_name(game, unit, user.locale),
                **kwargs,
            )


def announce_round_scores(game: "ScopaGame") -> None:
    """Announce per-round and total scores before round scores are committed."""
    game.broadcast_l("scopa-round-scores", buffer="game")
    teams = game.team_manager.get_alive_teams() or game.team_manager.teams
    for team in teams:
        game.broadcast_team_l(
            "scopa-round-score-line",
            team=team,
            round_score=team.round_score,
            total_score=team.total_score + team.round_score,
        )


def score_round(game: "ScopaGame") -> None:
    """
    Calculate and award round scores.

    Awards points for:
    - Most cards (1 point)
    - Most diamonds (1 point)
    - 7 of diamonds (1 point)
    - Primiera by default, or Most sevens when that variant is selected (1 point)
    - Optional Napola bonus
    """
    game.broadcast_l("scopa-scoring-round", buffer="game")

    units = build_scoring_units(game)
    if not units:
        announce_round_scores(game)
        return

    # Most cards
    card_counts = [(unit, len(unit.cards)) for unit in units]
    max_cards = max(count for _, count in card_counts)
    winners = [unit for unit, count in card_counts if count == max_cards]
    if len(winners) == 1:
        _award_unit_point(game, winners[0])
        broadcast_scoring_unit_l(
            game,
            winners[0],
            "scopa-you-most-cards",
            "scopa-your-team-most-cards",
            "scopa-most-cards",
            count=max_cards,
        )
    else:
        game.broadcast_l("scopa-most-cards-tie", buffer="game")

    # Most diamonds (suit 1)
    diamond_counts = [
        (unit, sum(1 for c in unit.cards if c.suit == 1)) for unit in units
    ]
    max_diamonds = max(count for _, count in diamond_counts)
    if max_diamonds > 0:
        winners = [unit for unit, count in diamond_counts if count == max_diamonds]
        if len(winners) == 1:
            _award_unit_point(game, winners[0])
            broadcast_scoring_unit_l(
                game,
                winners[0],
                "scopa-you-most-diamonds",
                "scopa-your-team-most-diamonds",
                "scopa-most-diamonds",
                count=max_diamonds,
            )
        else:
            game.broadcast_l("scopa-most-diamonds-tie", buffer="game")

    # 7 of diamonds
    seven_diamond_counts = [
        (unit, sum(1 for c in unit.cards if c.rank == 7 and c.suit == 1))
        for unit in units
    ]
    max_seven_diamonds = max(count for _, count in seven_diamond_counts)
    if max_seven_diamonds > 0:
        winners = [
            unit for unit, count in seven_diamond_counts if count == max_seven_diamonds
        ]
        if len(winners) == 1:
            _award_unit_point(game, winners[0])
            if max_seven_diamonds == 1:
                broadcast_scoring_unit_l(
                    game,
                    winners[0],
                    "scopa-you-seven-diamonds",
                    "scopa-your-team-seven-diamonds",
                    "scopa-seven-diamonds",
                )
            else:
                broadcast_scoring_unit_l(
                    game,
                    winners[0],
                    "scopa-you-seven-diamonds-multi",
                    "scopa-your-team-seven-diamonds-multi",
                    "scopa-seven-diamonds-multi",
                    count=max_seven_diamonds,
                )
        else:
            game.broadcast_l("scopa-seven-diamonds-tie", buffer="game")

    if game.options.primiera_scoring:
        # Primiera scoring
        # Primiera values: 7=21, 6=18, 1=16, 5=15, 4=14,
        # 3=13, 2=12, face cards (8, 9, 10)=10.
        def get_primiera_value(card: Card) -> int:
            if card.rank == 7:
                return 21
            if card.rank == 6:
                return 18
            if card.rank == 1:
                return 16
            if card.rank == 5:
                return 15
            if card.rank == 4:
                return 14
            if card.rank == 3:
                return 13
            if card.rank == 2:
                return 12
            return 10

        primiera_scores = []
        for unit in units:
            team_total = 0
            has_all_suits = True
            # Calculate the best card in each suit.
            for suit in range(1, 5):
                suit_cards = [c for c in unit.cards if c.suit == suit]
                if suit_cards:
                    team_total += max(get_primiera_value(c) for c in suit_cards)
                else:
                    has_all_suits = False
                    break
            if has_all_suits:
                primiera_scores.append((unit, team_total))

        if primiera_scores:
            max_primiera = max(score for _, score in primiera_scores)
            if max_primiera > 0:
                winners = [unit for unit, score in primiera_scores if score == max_primiera]
                if len(winners) == 1:
                    _award_unit_point(game, winners[0])
                    broadcast_scoring_unit_l(
                        game,
                        winners[0],
                        "scopa-you-primiera",
                        "scopa-your-team-primiera",
                        "scopa-primiera",
                        score=max_primiera,
                    )
                else:
                    game.broadcast_l("scopa-primiera-tie", buffer="game")
        else:
            game.broadcast_l("scopa-primiera-none", buffer="game")
    else:
        # Most sevens
        seven_counts = [
            (unit, sum(1 for c in unit.cards if c.rank == 7)) for unit in units
        ]
        max_sevens = max(count for _, count in seven_counts)
        if max_sevens > 0:
            winners = [unit for unit, count in seven_counts if count == max_sevens]
            if len(winners) == 1:
                _award_unit_point(game, winners[0])
                broadcast_scoring_unit_l(
                    game,
                    winners[0],
                    "scopa-you-most-sevens",
                    "scopa-your-team-most-sevens",
                    "scopa-most-sevens",
                    count=max_sevens,
                )
            else:
                game.broadcast_l("scopa-most-sevens-tie", buffer="game")

    if game.options.napola:
        # Napola: continuous sequence of diamonds starting from Ace
        for unit in units:
            diamond_ranks = {c.rank for c in unit.cards if c.suit == 1}
            # Must have Ace (1), 2, 3
            if {1, 2, 3}.issubset(diamond_ranks):
                napola_points = 3
                for r in range(4, 11):
                    if r in diamond_ranks:
                        napola_points += 1
                    else:
                        break
                _award_unit_point(game, unit, napola_points)
                broadcast_scoring_unit_l(
                    game,
                    unit,
                    "scopa-you-napola",
                    "scopa-your-team-napola",
                    "scopa-napola",
                    points=napola_points,
                )

    announce_round_scores(game)

    # Play round end sound
    game.play_sound("game_pig/win.ogg")


def check_winner(game: "ScopaGame") -> Team | None:
    """
    Check for a winner.

    Args:
        game: The Scopa game instance.

    Returns:
        Winning team or None if no winner yet.
    """
    target = game.options.target_score

    if game.options.inverse_scopa:
        # Inverse: eliminate teams that reach target
        alive_teams = game.team_manager.get_alive_teams()
        for team in alive_teams:
            if team.total_score >= target:
                game.team_manager.eliminate_team(team)
                game.broadcast_team_l("game-eliminated", team=team, score=team.total_score)

        # Check for last standing
        remaining = game.team_manager.get_alive_teams()
        if len(remaining) == 1:
            return remaining[0]
        elif len(remaining) == 0:
            # All eliminated - lowest score wins
            teams = game.team_manager.teams
            return min(teams, key=lambda t: t.total_score)
    else:
        # Normal: first to target wins
        teams_at_target = game.team_manager.get_teams_at_or_above_score(target)
        if teams_at_target:
            # Highest score wins
            return max(teams_at_target, key=lambda t: t.total_score)

    return None


def declare_winner(game: "ScopaGame", team: Team) -> None:
    """Declare a winner and end the game."""
    game.winner_team_index = team.index
    game.broadcast_team_l("game-winner-score", team=team, score=team.total_score)

    game.play_sound("game_pig/win.ogg")

    # Mark game as finished (auto-destroys if no humans)
    # finish_game() now handles both persisting the result and showing the end screen
    game.finish_game()
