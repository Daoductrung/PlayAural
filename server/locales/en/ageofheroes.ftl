# Age of Heroes game messages
# A civilization-building card game for 2-6 players

# Game name
game-name-ageofheroes = Age of Heroes

# Tribes
ageofheroes-tribe-egyptians = Egyptians
ageofheroes-tribe-romans = Romans
ageofheroes-tribe-greeks = Greeks
ageofheroes-tribe-babylonians = Babylonians
ageofheroes-tribe-celts = Celts
ageofheroes-tribe-chinese = Chinese

# Special Resources (for monuments)
ageofheroes-special-limestone = Limestone
ageofheroes-special-concrete = Concrete
ageofheroes-special-marble = Marble
ageofheroes-special-bricks = Bricks
ageofheroes-special-sandstone = Sandstone
ageofheroes-special-granite = Granite

# Standard Resources
ageofheroes-resource-iron = Iron
ageofheroes-resource-wood = Wood
ageofheroes-resource-grain = Grain
ageofheroes-resource-stone = Stone
ageofheroes-resource-gold = Gold

# Events
ageofheroes-event-population-growth = Population Growth
ageofheroes-event-earthquake = Earthquake
ageofheroes-event-eruption = Eruption
ageofheroes-event-hunger = Hunger
ageofheroes-event-barbarians = Barbarians
ageofheroes-event-olympics = Olympic Games
ageofheroes-event-hero = Hero
ageofheroes-event-fortune = Fortune

# Buildings
ageofheroes-building-army = Army
ageofheroes-building-fortress = Fortress
ageofheroes-building-general = General
ageofheroes-building-road = Road
ageofheroes-building-city = City

# Actions
ageofheroes-action-tax-collection = Tax Collection
ageofheroes-action-construction = Construction
ageofheroes-action-war = War
ageofheroes-action-do-nothing = Do Nothing
ageofheroes-play = Play
ageofheroes-play-card-label = Play { $card }
ageofheroes-card-count = { $count } { $card }
ageofheroes-player-tribe = { $player } ({ $tribe })
ageofheroes-player-tribe-direction = { $player } ({ $tribe }) - { $direction }

# War goals
ageofheroes-war-conquest = Conquest
ageofheroes-war-plunder = Plunder
ageofheroes-war-destruction = Destruction

# Game options
ageofheroes-set-victory-cities = Victory cities: { $cities }
ageofheroes-enter-victory-cities = Enter number of cities to win (3-7)
ageofheroes-set-victory-monument = Monument completion: { $progress }%
ageofheroes-set-max-hand = Maximum hand size: { $cards } cards

# Option change announcements
ageofheroes-option-changed-victory-cities = Victory requires { $cities } cities.
ageofheroes-desc-victory-cities = How many cities a side must control to win Age of Heroes (default 5, range 3-7).
ageofheroes-option-changed-victory-monument = Monument completion threshold set to { $progress }%.
ageofheroes-option-changed-max-hand = Maximum hand size set to { $cards } cards.

# Setup phase
ageofheroes-setup-start = You are the leader of the { $tribe } tribe. Your special monument resource is { $special }. Roll the dice to determine turn order.
ageofheroes-setup-viewer = Players are rolling dice to determine turn order.
ageofheroes-roll-dice = Roll the dice
ageofheroes-war-roll-dice = Roll the dice
ageofheroes-dice-result = You rolled { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = { $player } rolled { $total }.
ageofheroes-dice-tie = Multiple players tied with { $total }. Rolling again...
ageofheroes-first-player = { $player } rolled highest with { $total } and goes first.
ageofheroes-first-player-you = With { $total } points, you go first.
ageofheroes-whose-turn-setup = Setup phase. Waiting for { $players } to roll for turn order.
ageofheroes-whose-turn-setup-resolving = Setup phase. All dice are in; turn order is resolving.
ageofheroes-whose-turn-prepare = Preparation phase. Events and disasters are resolving.
ageofheroes-whose-turn-fair = Marketplace phase. { $players } may still trade.
ageofheroes-whose-turn-fair-resolving = Marketplace phase. Trades are resolving.
ageofheroes-whose-turn-road = Road permission phase. { $responder } must answer { $requester }'s road request.
ageofheroes-whose-turn-olympics = War declared. { $defender } must decide whether to use Olympic Games against { $attacker }.
ageofheroes-whose-turn-war-attack = War preparation. { $attacker } is choosing forces against { $defender }.
ageofheroes-whose-turn-war-defense = War preparation. { $defender } is choosing defending forces against { $attacker }.
ageofheroes-whose-turn-war-roll = Battle phase. Waiting for { $players } to roll.
ageofheroes-whose-turn-game-over = The game is over.

# Preparation phase
ageofheroes-prepare-start = Players must play event cards and discard disasters.
ageofheroes-prepare-your-turn = You have { $count } { $count ->
    [one] card
    *[other] cards
} to play or discard.
ageofheroes-prepare-done = Preparation phase complete.

# Events played/discarded
ageofheroes-population-growth = { $player } plays Population Growth and builds a new city.
ageofheroes-population-growth-you = You play Population Growth and build a new city.
ageofheroes-discard-card = { $player } discards { $card }.
ageofheroes-discard-card-you = You discard { $card }.
ageofheroes-earthquake = An earthquake strikes { $player }'s tribe; { GENDER_TERM($player_gender, "possessive-determiner") } armies go into recovery.
ageofheroes-earthquake-you = An earthquake strikes your tribe; your armies go into recovery.
ageofheroes-eruption = An eruption destroys one of { $player }'s cities.
ageofheroes-eruption-you = An eruption destroys one of your cities.

# Disaster effects
ageofheroes-hunger-strikes = Hunger strikes.
ageofheroes-lose-card-hunger = You lose { $card }.
ageofheroes-barbarians-pillage = Barbarians attack { $player }'s resources.
ageofheroes-barbarians-attack = Barbarians attack { $player }'s resources.
ageofheroes-barbarians-attack-you = Barbarians attack your resources.
ageofheroes-lose-card-barbarians = You lose { $card }.
ageofheroes-block-with-card = { $player } blocks the disaster using { $card }.
ageofheroes-block-with-card-you = You block the disaster using { $card }.

# Targeted disaster cards (Earthquake/Eruption)
ageofheroes-select-disaster-target = Select a target for { $card }.
ageofheroes-no-targets = No valid targets available.
ageofheroes-earthquake-strikes-you = { $attacker } plays Earthquake against you. Your armies are disabled.
ageofheroes-earthquake-strikes = { $attacker } plays Earthquake against { $player }.
ageofheroes-armies-disabled = { $count } { $count ->
    [one] army is
    *[other] armies are
} disabled for one turn.
ageofheroes-eruption-strikes-you = { $attacker } plays Eruption against you. One of your cities is destroyed.
ageofheroes-eruption-strikes = { $attacker } plays Eruption against { $player }.
ageofheroes-city-destroyed = A city is destroyed by the eruption.

# Fair phase
ageofheroes-fair-start = The day dawns at the marketplace.
ageofheroes-fair-draw-base = You draw { $count } { $count ->
    [one] card
    *[other] cards
}.
ageofheroes-fair-draw-roads = You draw { $count } additional { $count ->
    [one] card
    *[other] cards
} thanks to your road network.
ageofheroes-fair-draw-other = { $player } draws { $count } { $count ->
    [one] card
    *[other] cards
}.

# Trading/Auction
ageofheroes-auction-start = Auction begins.
ageofheroes-offer-trade = Offer to trade
ageofheroes-offer-made = { $player } offers { $card } for { $wanted }.
ageofheroes-offer-made-you = You offer { $card } for { $wanted }.
ageofheroes-trade-accepted = { $player } accepts { $other }'s offer and trades { $give } for { $receive }.
ageofheroes-trade-accepted-you = You accept { $other }'s offer and receive { $receive }.
ageofheroes-trade-cancelled = { $player } withdraws { GENDER_TERM($player_gender, "possessive-determiner") } offer for { $card }.
ageofheroes-trade-cancelled-you = You withdraw your offer for { $card }.
ageofheroes-stop-trading = Stop Trading
ageofheroes-select-request = You are offering { $card }. What do you want in return?
ageofheroes-cancel = Cancel
ageofheroes-left-auction = { $player } departs.
ageofheroes-left-auction-you = You depart from the marketplace.
ageofheroes-already-left-auction = You have already left the marketplace.
ageofheroes-any-card = Any card
ageofheroes-cannot-trade-own-special = You cannot trade your own special monument resource.
ageofheroes-resource-not-in-game = This special resource is not being used in this game.

# Main play phase
ageofheroes-play-start = Play phase.
ageofheroes-day = Day { $day }
ageofheroes-draw-card = { $player } draws a card from the deck.
ageofheroes-draw-card-you = You draw { $card } from the deck.
ageofheroes-draw-card-brief = { $player } draws.
ageofheroes-draw-card-you-brief = Draw: { $card }.
ageofheroes-your-action = What do you want to do?
ageofheroes-your-action-brief = Action?

# Tax Collection
ageofheroes-tax-collection = { $player } chooses Tax Collection: { $cities } { $cities ->
    [one] city
    *[other] cities
} collects { $cards } { $cards ->
    [one] card
    *[other] cards
}.
ageofheroes-tax-collection-you = You choose Tax Collection: { $cities } { $cities ->
    [one] city
    *[other] cities
} collects { $cards } { $cards ->
    [one] card
    *[other] cards
}.
ageofheroes-tax-collection-brief = { $player } tax: { $cards } from { $cities }.
ageofheroes-tax-collection-you-brief = Tax: { $cards } from { $cities }.
ageofheroes-tax-no-city = Tax Collection: You have no surviving cities. Discard a card to draw a new one.
ageofheroes-tax-no-city-done = { $player } chooses Tax Collection but has no cities, prompting { GENDER_TERM($player_gender, "object") } to exchange a card.
ageofheroes-tax-no-city-done-you = Tax Collection: You exchanged { $card } for a new card.

# Construction
ageofheroes-construction-menu = What do you want to build?
ageofheroes-construction-done = { $player } built { $building }.
ageofheroes-construction-done-you = You built { $building }.
ageofheroes-build-cost-resource = { $count ->
    [one] { $resource }
    *[other] { $count }x { $resource }
}
ageofheroes-build-menu-label = { $building } ({ $cost })
ageofheroes-construction-stop = Stop building
ageofheroes-construction-stopped = You decided to stop building.
ageofheroes-road-select-neighbor = Select which neighbor to build a road to.
ageofheroes-direction-left = To your left
ageofheroes-direction-right = To your right
ageofheroes-road-request-sent = Road request sent. Waiting for neighbor's approval.
ageofheroes-road-request-received = { $requester } requests permission to build a road to your tribe.
ageofheroes-road-request-denied-you = You declined the road request.
ageofheroes-road-request-denied = { $denier } declined your road request.
ageofheroes-road-built = { $tribe1 } and { $tribe2 } are now connected by road.
ageofheroes-road-no-target = No neighboring tribes available for road construction.
ageofheroes-approve = Approve
ageofheroes-deny = Deny
ageofheroes-supply-exhausted = No more { $building } available to build.

# Do Nothing
ageofheroes-do-nothing = { $player } passes.
ageofheroes-do-nothing-you = You pass...
ageofheroes-do-nothing-brief = { $player } passes.
ageofheroes-do-nothing-you-brief = Pass.
ageofheroes-confirm-do-nothing = Passing skips your action for this turn. Press Do Nothing again to confirm.

# War
ageofheroes-war-declare = { $attacker } declares war on { $defender }. Goal: { $goal }.
ageofheroes-war-prepare = Select your armies for { $action }.
ageofheroes-war-no-army = You have no armies or hero cards available.
ageofheroes-war-no-tribe = You do not have a tribe in this battle.
ageofheroes-war-no-targets = No valid targets for war.
ageofheroes-war-no-valid-goal = No valid war goals against this target.
ageofheroes-war-invalid-forces = Those forces are no longer valid. Review your available armies, generals, and Hero cards.
ageofheroes-war-select-target = Select which player to attack.
ageofheroes-war-select-goal = Select your war goal.
ageofheroes-war-prepare-attack = Select your attacking forces.
ageofheroes-war-prepare-defense = { $attacker } is attacking you; Select your defending forces.
ageofheroes-war-force-add-armies = Add one army. Armies committed: { $current } of { $max }.
ageofheroes-war-force-remove-armies = Remove one army. Armies committed: { $current } of { $max }.
ageofheroes-war-force-add-generals = Add one general. Generals committed: { $current } of { $max }.
ageofheroes-war-force-remove-generals = Remove one general. Generals committed: { $current } of { $max }.
ageofheroes-war-force-add-hero-armies = Add one Hero as an army. Hero armies committed: { $current } of { $max }.
ageofheroes-war-force-remove-hero-armies = Remove one Hero army. Hero armies committed: { $current } of { $max }.
ageofheroes-war-force-add-hero-generals = Add one Hero as a general. Hero generals committed: { $current } of { $max }.
ageofheroes-war-force-remove-hero-generals = Remove one Hero general. Hero generals committed: { $current } of { $max }.
ageofheroes-war-force-unit-armies = armies
ageofheroes-war-force-unit-generals = generals
ageofheroes-war-force-unit-hero-armies = Hero armies
ageofheroes-war-force-unit-hero-generals = Hero generals
ageofheroes-war-force-max = Already at the maximum: { $unit } ({ $max }).
ageofheroes-war-force-min = None committed: { $unit }.
ageofheroes-war-force-updated = Forces committed: { $armies } armies, { $generals } generals, { $hero_armies } Hero armies, { $hero_generals } Hero generals.
ageofheroes-war-attack = Attack...
ageofheroes-war-defend = Defend...
ageofheroes-war-clear-forces = Clear forces
ageofheroes-war-prepared = Your forces: { $armies } { $armies ->
    [one] army
    *[other] armies
}{ $generals ->
    [0] {""}
    [one] {" and 1 general"}
    *[other] { " and " }{ $generals } generals
}{ $heroes ->
    [0] {""}
    [one] {" and 1 hero"}
    *[other] { " and " }{ $heroes } heroes
}.
ageofheroes-war-roll-you = You roll { $roll }.
ageofheroes-war-roll-other = { $player } rolls { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] +1 from fortress = { $total } total
        *[other] +{ $fortress } from fortresses = { $total } total
    }
    *[other] { $fortress ->
        [0] +{ $general } from general = { $total } total
        [1] +{ $general } from general, +1 from fortress = { $total } total
        *[other] +{ $general } from general, +{ $fortress } from fortresses = { $total } total
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] { $player }: +1 from fortress = { $total } total
        *[other] { $player }: +{ $fortress } from fortresses = { $total } total
    }
    *[other] { $fortress ->
        [0] { $player }: +{ $general } from general = { $total } total
        [1] { $player }: +{ $general } from general, +1 from fortress = { $total } total
        *[other] { $player }: +{ $general } from general, +{ $fortress } from fortresses = { $total } total
    }
}
ageofheroes-war-bonuses-you-brief = Bonus +{ $bonus } = { $total }.
ageofheroes-war-bonuses-other-brief = { $player } bonus +{ $bonus } = { $total }.

# Battle
ageofheroes-battle-start = Battle begins. { $attacker }'s { $att_armies } { $att_armies ->
    [one] army
    *[other] armies
} versus { $defender }'s { $def_armies } { $def_armies ->
    [one] army
    *[other] armies
}.
ageofheroes-battle-start-brief = Battle: { $attacker } { $att_armies } vs { $defender } { $def_armies }.
ageofheroes-dice-roll-detailed = { $name } rolls { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } from general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 from fortress" }
    *[other] { " + { $fortress } from fortresses" }
} = { $total }.
ageofheroes-dice-roll-detailed-you = You roll { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } from general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 from fortress" }
    *[other] { " + { $fortress } from fortresses" }
} = { $total }.
ageofheroes-round-attacker-wins = { $attacker } wins the round ({ $att_total } vs { $def_total }). { $defender } loses an army.
ageofheroes-round-defender-wins = { $defender } defends successfully ({ $def_total } vs { $att_total }). { $attacker } loses an army.
ageofheroes-round-draw = Both sides tie at { $total }. No armies lost.
ageofheroes-round-attacker-wins-brief = { $attacker } { $att_total } beats { $defender } { $def_total }. { $defender } -1 army.
ageofheroes-round-defender-wins-brief = { $defender } { $def_total } beats { $attacker } { $att_total }. { $attacker } -1 army.
ageofheroes-round-draw-brief = Tie { $total }. No loss.
ageofheroes-you-win-battle-as-attacker = You defeat { $defender }.
ageofheroes-you-lose-battle-as-defender = { $attacker } defeats you.
ageofheroes-battle-victory-attacker = { $attacker } defeats { $defender }.
ageofheroes-you-lose-battle-as-attacker = { $defender } defends successfully against you.
ageofheroes-you-win-battle-as-defender = You defend successfully against { $attacker }.
ageofheroes-battle-victory-defender = { $defender } defends successfully against { $attacker }.
ageofheroes-you-draw-battle = You and { $opponent } both lose all forces committed to the battle.
ageofheroes-battle-mutual-defeat = Both { $attacker } and { $defender } lose all forces committed to the battle.
ageofheroes-general-bonus = +{ $count } from { $count ->
    [one] general
    *[other] generals
}
ageofheroes-fortress-bonus = +{ $count } from fortress defense
ageofheroes-battle-winner = { $winner } wins the battle.
ageofheroes-battle-draw = The battle ends in a draw...
ageofheroes-battle-continue = Continue the battle.
ageofheroes-battle-end = The battle is over.

# War outcomes
ageofheroes-conquest-success = { $attacker } conquers { $count } { $count ->
    [one] city
    *[other] cities
} from { $defender }.
ageofheroes-plunder-success = { $attacker } plunders { $count } { $count ->
    [one] card
    *[other] cards
} from { $defender }.
ageofheroes-destruction-success = { $attacker } destroys { $count } of { $defender }'s monument { $count ->
    [one] resource
    *[other] resources
}.
ageofheroes-conquest-success-brief = { $attacker } takes { $count } { $count ->
    [one] city
    *[other] cities
} from { $defender }.
ageofheroes-plunder-success-brief = { $attacker } takes { $count } { $count ->
    [one] card
    *[other] cards
} from { $defender }.
ageofheroes-destruction-success-brief = { $attacker } destroys { $count } monument { $count ->
    [one] resource
    *[other] resources
} from { $defender }.
ageofheroes-army-losses = { $player } loses { $count } { $count ->
    [one] army
    *[other] armies
}.
ageofheroes-army-losses-you = You lose { $count } { $count ->
    [one] army
    *[other] armies
}.

# Army return
ageofheroes-army-return-road = Your troops return immediately via road.
ageofheroes-army-return-delayed = { $count } { $count ->
    [one] unit returns
    *[other] units return
} at the end of your next turn.
ageofheroes-army-returned = { $player }'s troops have returned from war.
ageofheroes-army-returned-you = Your troops have returned from war.
ageofheroes-army-recover = { $player }'s armies recover from the earthquake.
ageofheroes-army-recover-you = Your armies recover from the earthquake.

# Olympics
ageofheroes-you-cancel-war-with-olympics = You play Olympic Games, cancelling the declared war.
ageofheroes-player-cancels-war-with-olympics = { $player } plays Olympic Games, cancelling the declared war.
ageofheroes-olympics-prompt = { $attacker } has declared war. You have Olympic Games - use it to cancel?
ageofheroes-yes = Yes
ageofheroes-no = No

# Monument progress
ageofheroes-monument-progress = { $player }'s monument is { $count }/5 complete.
ageofheroes-monument-progress-you = Your monument is { $count }/5 complete.

# Hand management
ageofheroes-discard-excess = You have more than { $max } cards. Discard { $count } { $count ->
    [one] card
    *[other] cards
}.
ageofheroes-discard-excess-other = { $player } must discard excess cards.
ageofheroes-discard-more = Discard { $count } more { $count ->
    [one] card
    *[other] cards
}.

# Victory
ageofheroes-victory-cities = { $player } has built { $cities } cities! Empire of Cities.
ageofheroes-victory-cities-you = You have built { $cities } cities! Empire of Cities.
ageofheroes-victory-monument = { $player } has completed { GENDER_TERM($player_gender, "possessive-determiner") } monument! Carriers of Great Culture.
ageofheroes-victory-monument-you = You have completed your monument! Carriers of Great Culture.
ageofheroes-victory-last-standing = { $player } is the last tribe standing! The Most Persistent.
ageofheroes-victory-last-standing-you = You are the last tribe standing! The Most Persistent.
ageofheroes-game-over = Game Over.
ageofheroes-final-winner = Winner: { $player }
ageofheroes-final-days = Days played: { $days }

# Elimination
ageofheroes-eliminated = { $player } has been eliminated.
ageofheroes-eliminated-you = You have been eliminated.

# Hand
ageofheroes-check-hand = Check hand
ageofheroes-hand-empty = You have no cards.
ageofheroes-initial-hand = Your starting hand ({ $count } { $count ->
    [one] card
    *[other] cards
}): { $cards }
ageofheroes-hand-contents = Your hand ({ $count } { $count ->
    [one] card
    *[other] cards
}): { $cards }

# Status
ageofheroes-check-status = Check status
ageofheroes-check-status-detailed = Detailed status
ageofheroes-status = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] city
    *[other] cities
}, { $armies } { $armies ->
    [one] army
    *[other] armies
}, { $monument }/5 monument
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-cities = Cities: { $count }
ageofheroes-status-armies = Armies: { $count }
ageofheroes-status-generals = Generals: { $count }
ageofheroes-status-fortresses = Fortresses: { $count }
ageofheroes-status-monument = Monument: { $count }/5
ageofheroes-status-roads = Roads: { $left }{ $right }
ageofheroes-status-road-left = left
ageofheroes-status-road-right = right
ageofheroes-status-none = none
ageofheroes-status-earthquake-armies = Recovering armies: { $count }
ageofheroes-status-returning-armies = Returning armies: { $count }
ageofheroes-status-returning-generals = Returning generals: { $count }
ageofheroes-status-detailed-line = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] city
    *[other] cities
}, { $armies } { $armies ->
    [one] army
    *[other] armies
}, { $generals } { $generals ->
    [one] general
    *[other] generals
}, { $fortresses } { $fortresses ->
    [one] fortress
    *[other] fortresses
}, monument { $monument }/5, roads: { $roads }{ $details }
ageofheroes-status-detail-recovering-armies = { $count } recovering { $count ->
    [one] army
    *[other] armies
}
ageofheroes-status-detail-returning-armies = { $count } returning { $count ->
    [one] army
    *[other] armies
}
ageofheroes-status-detail-returning-generals = { $count } returning { $count ->
    [one] general
    *[other] generals
}

# Deck info
ageofheroes-deck-empty = No more { $card } cards in the deck.
ageofheroes-deck-count = Cards remaining: { $count }
ageofheroes-deck-reshuffled = The discard pile has been reshuffled into the deck.

# Give up
ageofheroes-give-up-confirm = Are you sure you want to give up?
ageofheroes-gave-up = { $player } gave up!
ageofheroes-gave-up-you = You gave up!

# Hero card
ageofheroes-hero-use = Use as army or general?
ageofheroes-hero-army = Army
ageofheroes-hero-general = General

# Fortune card
ageofheroes-you-use-fortune = You use Fortune to reroll the battle die.
ageofheroes-player-uses-fortune = { $player } uses Fortune to reroll the battle die.
ageofheroes-fortune-prompt = You lost the roll. Use Fortune to reroll?

# Disabled action reasons
ageofheroes-not-your-turn = It's not your turn.
ageofheroes-game-not-started = The game hasn't started yet.
ageofheroes-wrong-phase = This action is not available in the current phase.
ageofheroes-invalid-player = This action is not available to you.
ageofheroes-not-in-game = You are not in this game.
ageofheroes-not-in-war = You are not involved in this war.
ageofheroes-already-rolled = You have already rolled.
ageofheroes-invalid-card-index = That card is no longer available.
ageofheroes-no-card-selected = Select a card first.
ageofheroes-no-cards-to-discard = You have no cards to discard.
ageofheroes-disaster-too-early = Disaster cards can only be played from day 2 onward.
ageofheroes-no-resources = You don't have the required resources.
ageofheroes-cannot-accept-own-offer = You cannot accept your own trade offer.
ageofheroes-offerer-unavailable = That trade offer is no longer available.
ageofheroes-offered-card-unavailable = The offered card is no longer available.
ageofheroes-trade-card-type-mismatch = Your selected card does not match the requested card type.
ageofheroes-trade-card-subtype-mismatch = Your selected card does not match the requested card.
ageofheroes-trade-offer-label = { $player }: { $offered } for { $wanted }

# Building costs (for display)
ageofheroes-cost-army = 2 Grain, Iron
ageofheroes-cost-fortress = Iron, Wood, Stone
ageofheroes-cost-general = Iron, Gold
ageofheroes-cost-road = 2 Stone
ageofheroes-cost-city = 2 Wood, Stone
