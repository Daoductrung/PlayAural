"""
Scoring logic for Scopa game.

Handles round scoring, winner detection, and game end.
"""

from typing import TYPE_CHECKING

from ...game_utils.cards import Card
from ...game_utils.teams import Team

if TYPE_CHECKING:
    from .game import ScopaGame, ScopaPlayer


def get_team_captured_cards(players: list["ScopaPlayer"], team: Team) -> list[Card]:
    """Get all cards captured by team members."""
    cards = []
    for player in players:
        if player.name in team.members:
            cards.extend(player.captured)
    return cards


def score_round(game: "ScopaGame") -> None:
    """
    Calculate and award round scores.

    Awards points for:
    - Most cards (1 point)
    - Most diamonds (1 point)
    - 7 of diamonds (1 point)
    - Most sevens (1 point)
    """
    game.broadcast_l("scopa-scoring-round", buffer="game")

    teams = game.team_manager.get_alive_teams()
    if not teams:
        teams = game.team_manager.teams

    # Build team card data
    team_data: list[tuple[Team, list[Card]]] = []
    for team in teams:
        if game.options.team_card_scoring:
            cards = get_team_captured_cards(game.players, team)
        else:
            # Individual scoring - just use first member's cards
            cards = get_team_captured_cards(game.players, team)
        team_data.append((team, cards))

    # Most cards
    card_counts = [(team, len(cards)) for team, cards in team_data]
    max_cards = max(count for _, count in card_counts)
    winners = [team for team, count in card_counts if count == max_cards]
    if len(winners) == 1:
        game.team_manager.add_to_team_round_score(winners[0].members[0], 1)
        game.broadcast_team_l("scopa-most-cards", team=winners[0], count=max_cards)
    else:
        game.broadcast_l("scopa-most-cards-tie", buffer="game")

    # Most diamonds (suit 1)
    diamond_counts = [
        (team, sum(1 for c in cards if c.suit == 1)) for team, cards in team_data
    ]
    max_diamonds = max(count for _, count in diamond_counts)
    if max_diamonds > 0:
        winners = [team for team, count in diamond_counts if count == max_diamonds]
        if len(winners) == 1:
            game.team_manager.add_to_team_round_score(winners[0].members[0], 1)
            game.broadcast_team_l("scopa-most-diamonds", team=winners[0], count=max_diamonds)
        else:
            game.broadcast_l("scopa-most-diamonds-tie", buffer="game")

    # 7 of diamonds
    seven_diamond_counts = [
        (team, sum(1 for c in cards if c.rank == 7 and c.suit == 1))
        for team, cards in team_data
    ]
    max_seven_diamonds = max(count for _, count in seven_diamond_counts)
    if max_seven_diamonds > 0:
        winners = [
            team for team, count in seven_diamond_counts if count == max_seven_diamonds
        ]
        if len(winners) == 1:
            game.team_manager.add_to_team_round_score(winners[0].members[0], 1)
            if max_seven_diamonds == 1:
                game.broadcast_team_l("scopa-seven-diamonds", team=winners[0])
            else:
                game.broadcast_team_l(
                    "scopa-seven-diamonds-multi", team=winners[0], count=max_seven_diamonds
                )
        else:
            game.broadcast_l("scopa-seven-diamonds-tie", buffer="game")

    if game.options.primiera_scoring:
        # Primiera scoring
        # Primiera values: 7=21, 6=18, 1=16, 5=15, 4=14, 3=13, 2=12, face cards (8,9,10)=10
        def get_primiera_value(card: Card) -> int:
            if card.rank == 7: return 21
            if card.rank == 6: return 18
            if card.rank == 1: return 16
            if card.rank == 5: return 15
            if card.rank == 4: return 14
            if card.rank == 3: return 13
            if card.rank == 2: return 12
            return 10

        primiera_scores = []
        for team, cards in team_data:
            team_total = 0
            # Calculate best card for each of the 4 suits (0 to 3)
            for suit in range(4):
                suit_cards = [c for c in cards if c.suit == suit]
                if suit_cards:
                    team_total += max(get_primiera_value(c) for c in suit_cards)
            primiera_scores.append((team, team_total))

        if primiera_scores:
            max_primiera = max(score for _, score in primiera_scores)
            if max_primiera > 0:
                winners = [team for team, score in primiera_scores if score == max_primiera]
                if len(winners) == 1:
                    game.team_manager.add_to_team_round_score(winners[0].members[0], 1)
                    game.broadcast_team_l("scopa-primiera", team=winners[0], score=max_primiera)
                else:
                    game.broadcast_l("scopa-primiera-tie", buffer="game")
    else:
        # Most sevens
        seven_counts = [
            (team, sum(1 for c in cards if c.rank == 7)) for team, cards in team_data
        ]
        max_sevens = max(count for _, count in seven_counts)
        if max_sevens > 0:
            winners = [team for team, count in seven_counts if count == max_sevens]
            if len(winners) == 1:
                game.team_manager.add_to_team_round_score(winners[0].members[0], 1)
                game.broadcast_team_l("scopa-most-sevens", team=winners[0], count=max_sevens)
            else:
                game.broadcast_l("scopa-most-sevens-tie", buffer="game")

    if game.options.napola:
        # Napola: continuous sequence of diamonds starting from Ace
        for team, cards in team_data:
            diamond_ranks = {c.rank for c in cards if c.suit == 1}
            # Must have Ace (1), 2, 3
            if {1, 2, 3}.issubset(diamond_ranks):
                napola_points = 3
                for r in range(4, 11):
                    if r in diamond_ranks:
                        napola_points += 1
                    else:
                        break
                game.team_manager.add_to_team_round_score(team.members[0], napola_points)
                game.broadcast_team_l("scopa-napola", team=team, points=napola_points)

    # Announce round scores
    game.broadcast_l("scopa-round-scores", buffer="game")
    for team in teams:
        game.broadcast_team_l(
            "scopa-round-score-line",
            team=team,
            round_score=team.round_score,
            total_score=team.total_score,
        )

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
    game.broadcast_team_l("game-winner-score", team=team, score=team.total_score)

    game.play_sound("game_pig/win.ogg")

    # Mark game as finished (auto-destroys if no humans)
    # finish_game() now handles both persisting the result and showing the end screen
    game.finish_game()
