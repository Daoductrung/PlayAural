game-name-citadels = Citadels

citadels-character-1 = Assassin
citadels-character-2 = Thief
citadels-character-3 = Magician
citadels-character-4 = King
citadels-character-5 = Bishop
citadels-character-6 = Merchant
citadels-character-7 = Architect
citadels-character-8 = Warlord
citadels-character-9 = Queen

citadels-district-type-noble = Noble
citadels-district-type-religious = Religious
citadels-district-type-trade = Trade
citadels-district-type-military = Military
citadels-district-type-unique = Unique

citadels-district-temple = Temple
citadels-district-church = Church
citadels-district-monastery = Monastery
citadels-district-cathedral = Cathedral
citadels-district-manor = Manor
citadels-district-castle = Castle
citadels-district-palace = Palace
citadels-district-tavern = Tavern
citadels-district-market = Market
citadels-district-trading_post = Trading Post
citadels-district-docks = Docks
citadels-district-harbor = Harbor
citadels-district-town_hall = Town Hall
citadels-district-watchtower = Watchtower
citadels-district-prison = Prison
citadels-district-barracks = Barracks
citadels-district-fortress = Fortress
citadels-district-dragon_gate = Dragon Gate
citadels-district-factory = Factory
citadels-district-haunted_quarter = Haunted Quarter
citadels-district-imperial_treasury = Imperial Treasury
citadels-district-keep = Keep
citadels-district-laboratory = Laboratory
citadels-district-library = Library
citadels-district-map_room = Map Room
citadels-district-quarry = Quarry
citadels-district-school_of_magic = School of Magic
citadels-district-smithy = Smithy
citadels-district-statue = Statue
citadels-district-thieves_den = Thieves' Den
citadels-district-wishing_well = Wishing Well

citadels-game-start = Citadels has begun.
citadels-selection-start-you = Round { $round }. You choose a character first.
citadels-selection-start = Round { $round }. { $player } chooses a character first.
citadels-selection-prompt = Choose a character now.
citadels-you-chose-character = You chose a character.
citadels-character-chosen = { $player } has chosen a character.
citadels-select-character-line = { $brief ->
    [yes] { $character }
   *[no] Rank { $rank }: { $character }
}
citadels-turn-phase-start = Character calling begins.
citadels-no-characters = There is no { $characters }.
citadels-list-pair = { $first } or { $last }
citadels-list-series = { $head }, or { $last }
citadels-you-character-revealed = { $brief ->
    [yes] You reveal the { $character }.
   *[no] You reveal rank { $rank }, { $character }.
}
citadels-character-revealed = { $brief ->
    [yes] { $player } reveals the { $character }.
   *[no] { $player } reveals rank { $rank }, { $character }.
}
citadels-you-took-crown = You take the crown and will choose first next round.
citadels-crown-taken = { $player } takes the crown.
citadels-you-king-heir = You reveal the King at end of round and take the crown.
citadels-king-heir = { $player } reveals the King at end of round and takes the crown.
citadels-you-assassin-targeted = { $brief ->
    [yes] You name the { $character } for assassination.
   *[no] You name rank { $rank }, { $character }, for assassination.
}
citadels-assassin-targeted = { $brief ->
    [yes] { $player }, the Assassin, names the { $character }.
   *[no] { $player }, the Assassin, names rank { $rank }, { $character }.
}
citadels-character-killed-skip = { $brief ->
    [yes] The { $character } was assassinated and loses its turn.
   *[no] Rank { $rank }, { $character }, was assassinated and loses its turn.
}
citadels-you-character-killed-skip = { $brief ->
    [yes] You were assassinated as the { $character } and lose this turn.
   *[no] You were assassinated as rank { $rank }, { $character }, and lose this turn.
}
citadels-you-thief-targeted = { $brief ->
    [yes] You will rob the { $character } when that character is revealed.
   *[no] You will rob rank { $rank }, { $character }, when that character is revealed.
}
citadels-thief-targeted = { $brief ->
    [yes] { $player }, the Thief, marks the { $character } for robbery.
   *[no] { $player }, the Thief, marks rank { $rank }, { $character }, for robbery.
}
citadels-you-thief-found-nothing = Your robbery finds no gold to steal.
citadels-thief-found-nothing = { $player }, the Thief, finds no gold to steal.
citadels-you-thief-stole-gold = You steal { $amount } gold as the Thief.
citadels-thief-stole-gold = { $player }, the Thief, steals { $amount } gold.
citadels-you-took-gold = You take { $amount } gold.
citadels-player-took-gold = { $player } takes { $amount } gold.
citadels-you-drew-options = You draw district cards and must keep one.
citadels-player-drew-options = { $player } draws district cards and must keep one.
citadels-player-kept-card = { $player } keeps one district card.
citadels-you-kept-card = You keep { $district }.
citadels-you-income-collected = You collect { $amount } gold from the { $character }.
citadels-income-collected = { $player } collects { $amount } gold from the { $character }.
citadels-you-architect-bonus = You draw { $count } bonus cards as the Architect.
citadels-architect-bonus = { $player } draws { $count } bonus cards.
citadels-you-magician-swapped = You swap hands with { $target }.
citadels-magician-swapped = { $player } swaps hands with { $target }.
citadels-you-magician-redrew = You redraw { $count } cards.
citadels-magician-redrew = { $player } redraws { $count } cards.
citadels-you-laboratory-used = You use the Laboratory and gain { $amount } gold.
citadels-laboratory-used = { $player } uses the Laboratory and gains { $amount } gold.
citadels-you-smithy-used = You use the Smithy and draw { $count } cards.
citadels-smithy-used = { $player } uses the Smithy and draws { $count } cards.
citadels-you-library-draw = You use the Library and keep all { $count } drawn cards.
citadels-library-draw = { $player } uses the Library and keeps all { $count } drawn cards.
citadels-you-built-district = You build { $district } and pay { $gold } gold.
citadels-district-built = { $player } builds { $district } and pays { $gold } gold.
citadels-thieves-den-payment = You discard { $cards } to help pay for Thieves' Den.
citadels-you-city-completed = You complete your city with { $count } districts.
citadels-city-completed = { $player } completes a city with { $count } districts.
citadels-you-queen-bonus = You gain { $amount } bonus gold from the Queen.
citadels-queen-bonus = { $player } gains { $amount } bonus gold from the Queen.
citadels-you-warlord-destroyed = You destroy { $target }'s { $district }.
citadels-warlord-destroyed = { $player } destroys { $target }'s { $district }.

citadels-take-gold = Take 2 gold
citadels-draw-cards = Draw district cards
citadels-collect-income = Collect character income
citadels-magician-swap = Swap hands
citadels-magician-redraw = Redraw cards
citadels-use-laboratory = Use Laboratory
citadels-use-smithy = Use Smithy
citadels-warlord-destroy = Destroy a district
citadels-confirm-redraw = Confirm redraw
citadels-build-thieves-den = Build Thieves' Den
citadels-end-turn = End turn
citadels-read-status = Read status summary
citadels-read-status-detailed = Read detailed status
citadels-read-character = Read character
citadels-read-hand = Read hand
citadels-read-cities = Read cities
citadels-read-discards = Read discards

citadels-assassinate-target-line = { $brief ->
    [yes] Assassinate the { $character }
   *[no] Assassinate rank { $rank }: { $character }
}
citadels-thief-target-line = { $brief ->
    [yes] Rob the { $character }
   *[no] Rob rank { $rank }: { $character }
}
citadels-magician-swap-line = Swap with { $player } ({ $cards } cards)
citadels-warlord-target-line = Destroy { $player }'s { $district } for { $cost } gold
citadels-build-card-line = Build { $district } ({ $cost } gold)
citadels-build-card-disabled-line = Cannot build { $district } ({ $cost } gold): { $reason }
citadels-district-line = { $district }, cost { $cost }, { $type }. { $description }
citadels-district-menu-line = { $district }, cost { $cost }, { $type }
citadels-toggle-selected = Selected: { $district }, cost { $cost }
citadels-toggle-not-selected = Not selected: { $district }, cost { $cost }

citadels-build-error = You cannot build { $district }: { $reason }
citadels-build-error-card-missing = That district card is no longer in your hand.
citadels-build-reason-need-resource = You must take gold or draw district cards before building.
citadels-build-reason-limit = You have already built the { $limit } { $limit ->
    [one] district
   *[other] districts
} allowed this turn.
citadels-build-reason-duplicate = Your city already contains { $district }, and you do not have Quarry to allow duplicate districts.
citadels-build-reason-gold = You need { $needed } more gold.
citadels-build-reason-thieves-den-payment = Even after discarding every other card in your hand, you still need { $needed } more gold worth of payment.

citadels-district-effect-none = No special ability.
citadels-district-effect-dragon_gate = End of game: gain 2 extra points.
citadels-district-effect-factory = Your other unique districts cost 1 less to build.
citadels-district-effect-haunted_quarter = End of game: this may count as noble, religious, trade, military, or unique for the five-color bonus.
citadels-district-effect-imperial_treasury = End of game: gain 1 point for each gold you still have.
citadels-district-effect-keep = The Warlord cannot destroy this district.
citadels-district-effect-laboratory = Once per turn, discard a card from your hand to gain 2 gold.
citadels-district-effect-library = When you draw district cards, keep both drawn cards.
citadels-district-effect-map_room = End of game: gain 1 point for each card in your hand.
citadels-district-effect-quarry = You may build duplicate districts in your city.
citadels-district-effect-school_of_magic = During King, Bishop, Merchant, or Warlord income, this counts as a district type of your choice.
citadels-district-effect-smithy = Once per turn after taking resources, pay 2 gold to draw 3 cards.
citadels-district-effect-statue = End of game: gain 5 points if you hold the crown.
citadels-district-effect-thieves_den = When building this district, you may discard cards from your hand to pay 1 gold per discarded card.
citadels-district-effect-wishing_well = End of game: gain 1 point for each unique district in your city, including this one.

citadels-hand-header = Your hand has { $count } cards.
citadels-hand-empty = Your hand is empty.
citadels-cities-header = Cities at the table
citadels-city-empty = no districts
citadels-city-line = { $player }: { $count } districts, { $gold } gold, { $score } points. { $districts }
citadels-character-none = You do not currently hold a character. You have { $gold } gold.
citadels-character-line = { $brief ->
    [yes] { $character }. You have { $gold } gold.
   *[no] Rank { $rank }: { $character }. You have { $gold } gold.
}
citadels-discards-none = none
citadels-faceup-discards-line = Faceup discarded characters: { $characters }

citadels-status-header = Citadels status
citadels-status-crown = Crown holder: { $player }
citadels-status-selection = Character selection. { $player } is choosing.
citadels-status-rank-resolution = { $brief ->
    [yes] Calling the { $character }.
   *[no] Calling rank { $rank }: { $character }.
}
citadels-status-turn = { $brief ->
    [yes] { $player } is taking a turn as the { $character }.
   *[no] { $player } is taking a turn as rank { $rank }, { $character }.
}
citadels-status-turn-progress = Built { $builds } of { $limit } allowed districts this turn.
citadels-status-killed = { $brief ->
    [yes] Assassinated: { $character }.
   *[no] Assassinated rank: { $rank }, { $character }.
}
citadels-status-killed-none = No character has been assassinated this round.
citadels-status-robbed = { $brief ->
    [yes] Robbed: { $character }.
   *[no] Robbed rank: { $rank }, { $character }.
}
citadels-status-robbed-none = No character has been marked for robbery this round.
citadels-status-first-completed = First completed city: { $player }

citadels-standings-header = Current standings
citadels-standing-line = Rank { $rank }: { $player }, { $score } points, { $gold } gold, { $districts } districts, { $cards } cards in hand.
citadels-end-line = Rank { $rank }: { $player }, { $score } points, { $gold } gold, { $districts } districts.
