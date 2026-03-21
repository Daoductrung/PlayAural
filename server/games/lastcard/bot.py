"""Strategic bot AI for LastCard."""

from __future__ import annotations

from typing import TYPE_CHECKING
import random

from ...game_utils.cards import Card

if TYPE_CHECKING:
    from .game import LastCardGame, LastCardPlayer

# Rank constants (duplicated to avoid circular import)
RANK_SKIP = 10
RANK_REVERSE = 11
RANK_DRAW_TWO = 12
RANK_WILD = 13
RANK_WILD_DRAW_FOUR = 14

COLOR_RED = 1
COLOR_BLUE = 2
COLOR_GREEN = 3
COLOR_YELLOW = 4
COLOR_WILD = 0


def _card_priority(game: "LastCardGame", card: Card, hand_size: int) -> float:
    """Score a card for priority (higher = play first).

    Strategy:
    - Play action cards early to disrupt opponents
    - Save wilds for when you need them
    - When hand is small, play high-value cards to reduce penalty risk
    - Prefer cards that match the most cards in hand (color synergy)
    """
    score = 0.0

    # Base score by type
    if card.rank == RANK_DRAW_TWO:
        score = 8.0  # Strong disruption
    elif card.rank == RANK_SKIP:
        score = 7.0
    elif card.rank == RANK_REVERSE:
        score = 6.0
    elif card.rank == RANK_WILD_DRAW_FOUR:
        score = 3.0 if hand_size > 3 else 9.0  # Save when hand is big, play when small
    elif card.rank == RANK_WILD:
        score = 2.0 if hand_size > 3 else 8.0  # Save when hand is big
    else:
        # Number cards: prefer higher values (reduce points in hand)
        score = 4.0 + card.rank * 0.1

    # When down to 2-3 cards, prefer high-value cards to shed points
    if hand_size <= 3:
        if card.rank in (RANK_WILD, RANK_WILD_DRAW_FOUR):
            score += 5.0  # Use wilds to go out
        elif card.rank >= RANK_SKIP:
            score += 3.0

    return score


def choose_best_color(game: "LastCardGame", player: "LastCardPlayer") -> int:
    """Choose the best color based on cards in hand."""
    color_counts = {COLOR_RED: 0, COLOR_BLUE: 0, COLOR_GREEN: 0, COLOR_YELLOW: 0}
    color_values = {COLOR_RED: 0, COLOR_BLUE: 0, COLOR_GREEN: 0, COLOR_YELLOW: 0}

    for card in player.hand:
        if card.suit in color_counts:
            color_counts[card.suit] += 1
            # Weight action cards higher
            if card.rank >= RANK_SKIP:
                color_values[card.suit] += 3
            else:
                color_values[card.suit] += 1

    # Prefer the color with most cards, break ties by value
    best = max(color_counts.keys(),
               key=lambda c: (color_counts[c], color_values[c], random.random()))
    return best


def choose_playable_card(game: "LastCardGame", player: "LastCardPlayer") -> Card | None:
    """Choose the best card to play from the player's hand."""
    playable = [card for card in player.hand if game._is_card_playable(card, player)]
    if not playable:
        return None

    hand_size = len(player.hand)
    scored = []
    for card in playable:
        priority = _card_priority(game, card, hand_size)
        # Add small random tiebreaker
        scored.append((priority + random.random() * 0.5, card))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1]


def _should_challenge_wd4(game: "LastCardGame", player: "LastCardPlayer") -> bool:
    """Decide whether to challenge a Wild Draw Four.

    Strategy:
    - If player has few cards, more likely to challenge (less to lose)
    - Consider if the WD4 player likely had matching colors
    - More aggressive when behind in score
    """
    hand_size = len(player.hand)

    # Base challenge probability
    if hand_size <= 2:
        prob = 0.6  # Small hand = less risk
    elif hand_size <= 5:
        prob = 0.35
    else:
        prob = 0.15  # Big hand = risky to challenge

    # If WD4 player has few cards, they're more likely to have played legally
    wd4_player = game.get_player_by_id(game.interrupt_wd4_player_id)
    if wd4_player and hasattr(wd4_player, "hand"):
        if len(wd4_player.hand) <= 2:
            prob -= 0.1  # Less likely they had other options

    return random.random() < prob


def _should_jump_in(game: "LastCardGame", player: "LastCardPlayer") -> bool:
    """Decide whether to jump in with a matching card."""
    top = game.top_card
    if not top:
        return False

    matching = [c for c in player.hand if c.rank == top.rank and c.suit == top.suit]
    if not matching:
        return False

    hand_size = len(player.hand)

    # Always jump in if down to 2-3 cards
    if hand_size <= 3:
        return True

    # More likely to jump in with action cards (skip opponent's turn)
    card = matching[0]
    if card.rank >= RANK_SKIP:
        return random.random() < 0.8

    # Otherwise moderate probability
    return random.random() < 0.5


def _should_catch_last_card(game: "LastCardGame", player: "LastCardPlayer") -> bool:
    """Decide whether to press the buzzer to catch someone."""
    # Bots have a high chance of catching
    return random.random() < 0.7


def bot_think(game: "LastCardGame", player: "LastCardPlayer") -> str | None:
    """Main bot decision function for turn-based actions."""

    # Awaiting color choice after wild
    if game.awaiting_color_choice and game.current_player == player:
        color = choose_best_color(game, player)
        color_map = {COLOR_RED: "color_red", COLOR_BLUE: "color_blue",
                     COLOR_GREEN: "color_green", COLOR_YELLOW: "color_yellow"}
        return color_map.get(color, "color_red")

    # Awaiting swap target (Seven rule)
    if game.awaiting_swap_target and game.swap_player_id == player.id:
        active = [p for p in game.turn_players if not p.is_spectator and p.id != player.id]
        if active:
            # Target player with most cards (benefit from swap)
            best_idx = 0
            best_count = 0
            for i, p in enumerate(active):
                if hasattr(p, "hand") and len(p.hand) > best_count:
                    best_count = len(p.hand)
                    best_idx = i
            return f"swap_target_{best_idx}"
        return None

    # Normal turn: try to play a card
    if game.current_player == player:
        # Multi-play mode: select all same-rank cards, then confirm
        if game.options.allow_multiple_play:
            return _bot_think_multi(game, player)

        # Pre-buzz if about to play down to 1 card
        if (len(player.hand) == 2 and game.options.last_card_callout
                and game.options.buzzer_enabled and not player.called_last_card):
            player.called_last_card = True
            # Don't return buzzer action — just set flag and play card
            # (Bots can multi-act in the same think call)

        card = choose_playable_card(game, player)
        if card is not None:
            return f"play_card_{card.id}"

        if game.turn_has_drawn:
            return "pass"

        if game._can_draw(player):
            return "draw"

        return "pass"

    return None


def _bot_think_multi(game: "LastCardGame", player: "LastCardPlayer") -> str | None:
    """Bot logic for multi-play mode using toggle+confirm pattern."""
    # If cards are already selected, confirm the play
    if player.selected_cards:
        return "play_selected"

    # Find the best card to play
    card = choose_playable_card(game, player)
    if card is None:
        if game.turn_has_drawn:
            return "pass"
        if game._can_draw(player):
            return "draw"
        return "pass"

    # Pre-buzz if about to play down to last card
    remaining_after = len(player.hand)  # will subtract selected count later

    # Find all same-rank cards in hand (wilds excluded from multi-play)
    if card.rank not in (RANK_WILD, RANK_WILD_DRAW_FOUR):
        same_rank = [c for c in player.hand if c.rank == card.rank]
    else:
        same_rank = [card]

    remaining_after = len(player.hand) - len(same_rank)

    # Pre-buzz if playing down to 1 card
    if (remaining_after == 1 and game.options.last_card_callout
            and game.options.buzzer_enabled and not player.called_last_card):
        player.called_last_card = True

    # Select all same-rank cards at once, then the next bot_think tick will confirm
    for c in same_rank:
        player.selected_cards.add(c.id)
    return "play_selected"


def bot_react(game: "LastCardGame", player: "LastCardPlayer") -> str | None:
    """Bot reactions during interrupt windows (buzzer, challenge, jump-in)."""

    if game.interrupt_phase == "last_card_callout":
        target = game.get_player_by_id(game.interrupt_target_id)
        if target and hasattr(target, "hand"):
            if player.id == target.id:
                # I'm the one with 1 card — buzz!
                if not player.called_last_card:
                    return "buzzer"
            else:
                # Try to catch them
                if not target.called_last_card and _should_catch_last_card(game, player):
                    return "buzzer"

    elif game.interrupt_phase == "challenge_wd4":
        next_p = game._next_player()
        if next_p and next_p.id == player.id:
            if _should_challenge_wd4(game, player):
                return "challenge_wd4"
            else:
                return "accept_draw"

    elif game.interrupt_phase == "jump_in_window":
        if game.current_player != player and _should_jump_in(game, player):
            return "jump_in"

    return None
