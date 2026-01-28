"""Trading/Auction system for Age of Heroes."""

from __future__ import annotations
from typing import TYPE_CHECKING

from .cards import Card, CardType, ResourceType, SpecialResourceType, EventType, get_card_name
from .state import TradeOffer, TRIBE_SPECIAL_RESOURCE
from ...messages.localization import Localization

if TYPE_CHECKING:
    from .game import AgeOfHeroesGame, AgeOfHeroesPlayer


def can_offer_card(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, card_index: int
) -> str | None:
    """Check if a card can be offered for trade. Returns error message or None."""
    if card_index < 0 or card_index >= len(player.hand):
        return "Invalid card index"

    card = player.hand[card_index]

    # Cannot trade your own special monument resource
    if player.tribe_state and card.card_type == CardType.SPECIAL:
        own_special = TRIBE_SPECIAL_RESOURCE.get(player.tribe_state.tribe)
        if card.subtype == own_special:
            return "ageofheroes-cannot-trade-own-special"

    # Cannot trade special resources not in the game
    if card.card_type == CardType.SPECIAL:
        if not is_special_resource_in_game(game, card.subtype):
            return "ageofheroes-resource-not-in-game"

    return None


def is_special_resource_in_game(game: AgeOfHeroesGame, special_type: str) -> bool:
    """Check if a special resource type is being used by any player."""
    for player in game.get_active_players():
        if hasattr(player, "tribe_state") and player.tribe_state:
            player_special = TRIBE_SPECIAL_RESOURCE.get(player.tribe_state.tribe)
            if player_special == special_type:
                return True
    return False


def create_offer(
    game: AgeOfHeroesGame,
    player: AgeOfHeroesPlayer,
    card_index: int,
    wanted_type: str | None = None,
    wanted_subtype: str | None = None,
) -> TradeOffer | None:
    """Create a new trade offer."""
    error = can_offer_card(game, player, card_index)
    if error:
        return None

    active_players = game.get_active_players()
    player_index = active_players.index(player)

    # Check if player already has an offer for this card
    for offer in game.trade_offers:
        if offer.player_index == player_index and offer.card_index == card_index:
            # Update existing offer
            offer.wanted_type = wanted_type
            offer.wanted_subtype = wanted_subtype
            return offer

    # Create new offer
    offer = TradeOffer(
        player_index=player_index,
        card_index=card_index,
        wanted_type=wanted_type,
        wanted_subtype=wanted_subtype,
    )
    game.trade_offers.append(offer)
    return offer


def cancel_offer(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, card_index: int
) -> bool:
    """Cancel a trade offer."""
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    for i, offer in enumerate(game.trade_offers):
        if offer.player_index == player_index and offer.card_index == card_index:
            game.trade_offers.pop(i)
            return True
    return False


def get_matching_offers(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, card: Card
) -> list[TradeOffer]:
    """Get offers that match a card the player has."""
    matches = []
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    for offer in game.trade_offers:
        # Can't trade with yourself
        if offer.player_index == player_index:
            continue

        # Check if offer wants this type of card
        if offer.wanted_type is not None and offer.wanted_type != card.card_type:
            continue
        if offer.wanted_subtype is not None and offer.wanted_subtype != card.subtype:
            continue

        matches.append(offer)

    return matches


def can_accept_offer(
    game: AgeOfHeroesGame,
    acceptor: AgeOfHeroesPlayer,
    offer: TradeOffer,
    acceptor_card_index: int,
) -> str | None:
    """Check if a player can accept an offer. Returns error message or None."""
    if acceptor_card_index < 0 or acceptor_card_index >= len(acceptor.hand):
        return "Invalid card index"

    active_players = game.get_active_players()

    # Can't accept your own offer
    acceptor_index = active_players.index(acceptor)
    if offer.player_index == acceptor_index:
        return "Cannot accept your own offer"

    # Check if the offered card is still available
    offerer = active_players[offer.player_index]
    if not hasattr(offerer, "hand"):
        return "Offerer has no hand"
    if offer.card_index >= len(offerer.hand):
        return "Offered card no longer available"

    # Check if acceptor's card matches what's wanted
    acceptor_card = acceptor.hand[acceptor_card_index]

    if offer.wanted_type is not None and acceptor_card.card_type != offer.wanted_type:
        return "Card type doesn't match"
    if (
        offer.wanted_subtype is not None
        and acceptor_card.subtype != offer.wanted_subtype
    ):
        return "Card subtype doesn't match"

    # Check special resource restrictions
    error = can_offer_card(game, acceptor, acceptor_card_index)
    if error:
        return error

    return None


def execute_trade(
    game: AgeOfHeroesGame,
    offer: TradeOffer,
    acceptor: AgeOfHeroesPlayer,
    acceptor_card_index: int,
) -> bool:
    """Execute a trade between two players."""
    active_players = game.get_active_players()

    if offer.player_index >= len(active_players):
        return False

    offerer = active_players[offer.player_index]
    if not hasattr(offerer, "hand") or not hasattr(acceptor, "hand"):
        return False

    if offer.card_index >= len(offerer.hand):
        return False
    if acceptor_card_index >= len(acceptor.hand):
        return False

    # Swap cards
    offerer_card = offerer.hand.pop(offer.card_index)
    acceptor_card = acceptor.hand.pop(acceptor_card_index)

    offerer.hand.append(acceptor_card)
    acceptor.hand.append(offerer_card)

    # Remove the offer
    if offer in game.trade_offers:
        game.trade_offers.remove(offer)

    # Update any other offers that had invalid indices
    cleanup_offers(game)

    # Play trade sound
    game.play_sound("game_ageofheroes/trade.ogg")

    return True


def cleanup_offers(game: AgeOfHeroesGame) -> None:
    """Remove invalid offers (e.g., card indices out of range)."""
    active_players = game.get_active_players()
    valid_offers = []

    for offer in game.trade_offers:
        if offer.player_index >= len(active_players):
            continue

        player = active_players[offer.player_index]
        if not hasattr(player, "hand"):
            continue

        if offer.card_index >= len(player.hand):
            continue

        valid_offers.append(offer)

    game.trade_offers = valid_offers


def stop_trading(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Mark a player as having stopped trading."""
    player.has_stopped_trading = True

    # Cancel all their offers
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    game.trade_offers = [
        offer for offer in game.trade_offers if offer.player_index != player_index
    ]


def is_trading_complete(game: AgeOfHeroesGame) -> bool:
    """Check if all players have stopped trading."""
    for player in game.get_active_players():
        if hasattr(player, "has_stopped_trading") and not player.has_stopped_trading:
            return False
    return True


def get_player_offers(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> list[TradeOffer]:
    """Get all offers made by a specific player."""
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    return [offer for offer in game.trade_offers if offer.player_index == player_index]


def format_offer(
    game: AgeOfHeroesGame, offer: TradeOffer, locale: str
) -> str:
    """Format a trade offer for display."""
    active_players = game.get_active_players()

    if offer.player_index >= len(active_players):
        return ""

    offerer = active_players[offer.player_index]
    if not hasattr(offerer, "hand"):
        return ""

    if offer.card_index >= len(offerer.hand):
        return ""

    offered_card = offerer.hand[offer.card_index]
    offered_name = get_card_name(offered_card, locale)

    # Format wanted
    if offer.wanted_type is None and offer.wanted_subtype is None:
        wanted_name = Localization.get(locale, "ageofheroes-any-card")
    elif offer.wanted_subtype is not None:
        # Create a dummy card for name lookup
        wanted_card = Card(id=-1, card_type=offer.wanted_type or "", subtype=offer.wanted_subtype)
        wanted_name = get_card_name(wanted_card, locale)
    else:
        wanted_name = offer.wanted_type or ""

    return f"{offerer.name}: {offered_name} -> {wanted_name}"


def announce_offer(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, offered_card: Card, wanted_subtype: str | None
) -> None:
    """Announce a trade offer."""
    for p in game.players:
        user = game.get_user(p)
        if user:
            offered_name = get_card_name(offered_card, user.locale)

            # Get wanted name based on type
            if wanted_subtype is None:
                wanted_name = Localization.get(user.locale, "ageofheroes-any-card")
            elif wanted_subtype in [r for r in ResourceType]:
                wanted_card = Card(id=-1, card_type=CardType.RESOURCE, subtype=wanted_subtype)
                wanted_name = get_card_name(wanted_card, user.locale)
            elif wanted_subtype in [s for s in SpecialResourceType]:
                wanted_card = Card(id=-1, card_type=CardType.SPECIAL, subtype=wanted_subtype)
                wanted_name = get_card_name(wanted_card, user.locale)
            elif wanted_subtype in [e for e in EventType]:
                wanted_card = Card(id=-1, card_type=CardType.EVENT, subtype=wanted_subtype)
                wanted_name = get_card_name(wanted_card, user.locale)
            else:
                wanted_name = wanted_subtype

            if p == player:
                user.speak_l(
                    "ageofheroes-offer-made-you",
                    card=offered_name,
                    wanted=wanted_name,
                )
            else:
                user.speak_l(
                    "ageofheroes-offer-made",
                    player=player.name,
                    card=offered_name,
                    wanted=wanted_name,
                )


def check_and_execute_trades(game: AgeOfHeroesGame) -> bool:
    """Check for matching offers and execute trades. Returns True if any trade made."""
    trades_made = False
    active_players = game.get_active_players()

    # Check all pairs of offers for matches
    i = 0
    while i < len(game.trade_offers):
        offer1 = game.trade_offers[i]
        if offer1.player_index >= len(active_players):
            i += 1
            continue

        player1 = active_players[offer1.player_index]
        if not hasattr(player1, "hand"):
            i += 1
            continue

        if offer1.card_index >= len(player1.hand):
            i += 1
            continue

        card1 = player1.hand[offer1.card_index]

        j = i + 1
        while j < len(game.trade_offers):
            offer2 = game.trade_offers[j]
            if offer2.player_index >= len(active_players):
                j += 1
                continue
            if offer2.player_index == offer1.player_index:
                j += 1
                continue

            player2 = active_players[offer2.player_index]
            if not hasattr(player2, "hand"):
                j += 1
                continue

            if offer2.card_index >= len(player2.hand):
                j += 1
                continue

            card2 = player2.hand[offer2.card_index]

            # Check if offers match
            # offer1 wants what player2 offers, and offer2 wants what player1 offers
            match1 = (
                (offer1.wanted_type is None or offer1.wanted_type == card2.card_type)
                and (offer1.wanted_subtype is None or offer1.wanted_subtype == card2.subtype)
            )
            match2 = (
                (offer2.wanted_type is None or offer2.wanted_type == card1.card_type)
                and (offer2.wanted_subtype is None or offer2.wanted_subtype == card1.subtype)
            )

            if match1 and match2:
                # Check special resource restrictions
                # Special resources can only go to the tribe that needs them
                valid = True
                if card1.card_type == CardType.SPECIAL:
                    needed_by = None
                    for tribe, special in TRIBE_SPECIAL_RESOURCE.items():
                        if special == card1.subtype:
                            needed_by = tribe
                            break
                    if needed_by and hasattr(player2, "tribe_state") and player2.tribe_state:
                        if player2.tribe_state.tribe != needed_by:
                            valid = False

                if card2.card_type == CardType.SPECIAL:
                    needed_by = None
                    for tribe, special in TRIBE_SPECIAL_RESOURCE.items():
                        if special == card2.subtype:
                            needed_by = tribe
                            break
                    if needed_by and hasattr(player1, "tribe_state") and player1.tribe_state:
                        if player1.tribe_state.tribe != needed_by:
                            valid = False

                if valid:
                    # Execute the trade
                    execute_matched_trade(game, player1, offer1, player2, offer2)
                    trades_made = True
                    # Restart search since indices changed
                    i = 0
                    break

            j += 1
        else:
            i += 1
            continue
        break  # Restart outer loop after trade

    return trades_made


def execute_matched_trade(
    game: AgeOfHeroesGame,
    player1: AgeOfHeroesPlayer,
    offer1: TradeOffer,
    player2: AgeOfHeroesPlayer,
    offer2: TradeOffer,
) -> None:
    """Execute a matched trade between two players."""
    card1 = player1.hand[offer1.card_index]
    card2 = player2.hand[offer2.card_index]

    # Swap cards
    player1.hand[offer1.card_index] = card2
    player2.hand[offer2.card_index] = card1

    # Remove offers
    if offer1 in game.trade_offers:
        game.trade_offers.remove(offer1)
    if offer2 in game.trade_offers:
        game.trade_offers.remove(offer2)

    # Announce trade
    game.play_sound("game_ageofheroes/trade.ogg")

    for p in game.players:
        user = game.get_user(p)
        if user:
            card1_name = get_card_name(card1, user.locale)
            card2_name = get_card_name(card2, user.locale)

            if p == player1:
                user.speak_l(
                    "ageofheroes-trade-accepted-you",
                    other=player2.name,
                    receive=card2_name,
                )
            elif p == player2:
                user.speak_l(
                    "ageofheroes-trade-accepted-you",
                    other=player1.name,
                    receive=card1_name,
                )
            else:
                user.speak_l(
                    "ageofheroes-trade-accepted",
                    player=player1.name,
                    other=player2.name,
                    give=card1_name,
                    receive=card2_name,
                )
