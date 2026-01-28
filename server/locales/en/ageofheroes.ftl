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

# War goals
ageofheroes-war-conquest = Conquest
ageofheroes-war-plunder = Plunder
ageofheroes-war-destruction = Destruction

# Game options
ageofheroes-set-victory-cities = Victory cities: { $cities }
ageofheroes-enter-victory-cities = Enter number of cities to win (3-7)
ageofheroes-set-victory-monument = Monument completion: { $progress }%
ageofheroes-toggle-neighbor-roads = Roads only to neighbors: { $enabled }
ageofheroes-set-max-hand = Maximum hand size: { $cards } cards

# Option change announcements
ageofheroes-option-changed-victory-cities = Victory requires { $cities } cities.
ageofheroes-option-changed-victory-monument = Monument completion threshold set to { $progress }%.
ageofheroes-option-changed-neighbor-roads = Roads only to neighbors { $enabled }.
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
ageofheroes-earthquake = An earthquake strikes { $player }'s tribe; their armies go into recovery.
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
ageofheroes-trade-cancelled = { $player } withdraws their offer for { $card }.
ageofheroes-trade-cancelled-you = You withdraw your offer for { $card }.
ageofheroes-stop-trading = Stop Trading
ageofheroes-select-request = You are offering { $card }. What do you want in return?
ageofheroes-cancel = Cancel
ageofheroes-left-auction = { $player } departs.
ageofheroes-left-auction-you = You depart from the marketplace.
ageofheroes-any-card = Any card
ageofheroes-cannot-trade-own-special = You cannot trade your own special monument resource.
ageofheroes-resource-not-in-game = This special resource is not being used in this game.

# Main play phase
ageofheroes-play-start = Play phase.
ageofheroes-day = Day { $day }
ageofheroes-draw-card = { $player } draws a card from the deck.
ageofheroes-draw-card-you = You draw { $card } from the deck.
ageofheroes-your-action = What do you want to do?

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
ageofheroes-tax-no-city = Tax Collection: You have no surviving cities. Discard a card to draw a new one.
ageofheroes-tax-no-city-done = { $player } chooses Tax Collection but has no cities, so they exchange a card.
ageofheroes-tax-no-city-done-you = Tax Collection: You exchanged { $card } for a new card.

# Construction
ageofheroes-construction-menu = What do you want to build?
ageofheroes-construction-done = { $player } built { $article } { $building }.
ageofheroes-construction-done-you = You built { $article } { $building }.
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

# War
ageofheroes-war-declare = { $attacker } declares war on { $defender }. Goal: { $goal }.
ageofheroes-war-prepare = Select your armies for { $action }.
ageofheroes-war-no-army = You have no armies or hero cards available.
ageofheroes-war-no-targets = No valid targets for war.
ageofheroes-war-no-valid-goal = No valid war goals against this target.
ageofheroes-war-select-target = Select which player to attack.
ageofheroes-war-select-goal = Select your war goal.
ageofheroes-war-prepare-attack = Select your attacking forces.
ageofheroes-war-prepare-defense = { $attacker } is attacking you; Select your defending forces.
ageofheroes-war-select-armies = Select armies: { $count }
ageofheroes-war-select-generals = Select generals: { $count }
ageofheroes-war-select-heroes = Select heroes: { $count }
ageofheroes-war-attack = Attack...
ageofheroes-war-defend = Defend...
ageofheroes-war-prepared = Your forces: { $armies } { $armies ->
    [one] army
    *[other] armies
}{ $generals ->
    [0] {""}
    [one] {" and 1 general"}
    *[other] {" and { $generals } generals"}
}{ $heroes ->
    [0] {""}
    [one] {" and 1 hero"}
    *[other] {" and { $heroes } heroes"}
}.
ageofheroes-war-roll-you = You roll { $roll }.
ageofheroes-war-roll-other = { $player } rolls { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] {
        { $fortress ->
            [0] {""}
            [1] {"+1 from fortress = { $total } total"}
            *[other] {"+{ $fortress } from fortresses = { $total } total"}
        }
    }
    *[other] {
        { $fortress ->
            [0] {"+{ $general } from general = { $total } total"}
            [1] {"+{ $general } from general, +1 from fortress = { $total } total"}
            *[other] {"+{ $general } from general, +{ $fortress } from fortresses = { $total } total"}
        }
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] {
        { $fortress ->
            [0] {""}
            [1] {"{ $player }: +1 from fortress = { $total } total"}
            *[other] {"{ $player }: +{ $fortress } from fortresses = { $total } total"}
        }
    }
    *[other] {
        { $fortress ->
            [0] {"{ $player }: +{ $general } from general = { $total } total"}
            [1] {"{ $player }: +{ $general } from general, +1 from fortress = { $total } total"}
            *[other] {"{ $player }: +{ $general } from general, +{ $fortress } from fortresses = { $total } total"}
        }
    }
}

# Battle
ageofheroes-battle-start = Battle begins. { $attacker }'s { $att_armies } { $att_armies ->
    [one] army
    *[other] armies
} versus { $defender }'s { $def_armies } { $def_armies ->
    [one] army
    *[other] armies
}.
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
ageofheroes-battle-victory-attacker = { $attacker } defeats { $defender }.
ageofheroes-battle-victory-defender = { $defender } defends successfully against { $attacker }.
ageofheroes-battle-mutual-defeat = Both { $attacker } and { $defender } lose all armies.
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
ageofheroes-olympics-cancel = { $player } plays Olympic Games. War cancelled.
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
ageofheroes-victory-cities = { $player } has built 5 cities! Empire of Five Cities.
ageofheroes-victory-cities-you = You have built 5 cities! Empire of Five Cities.
ageofheroes-victory-monument = { $player } has completed their monument! Carriers of Great Culture.
ageofheroes-victory-monument-you = You have completed your monument! Carriers of Great Culture.
ageofheroes-victory-last-standing = { $player } is the last tribe standing! The Most Persistent.
ageofheroes-victory-last-standing-you = You are the last tribe standing! The Most Persistent.
ageofheroes-game-over = Game Over.

# Elimination
ageofheroes-eliminated = { $player } has been eliminated.
ageofheroes-eliminated-you = You have been eliminated.

# Hand
ageofheroes-hand-empty = You have no cards.
ageofheroes-hand-contents = Your hand ({ $count } { $count ->
    [one] card
    *[other] cards
}): { $cards }

# Status
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
ageofheroes-fortune-reroll = { $player } uses Fortune to reroll.
ageofheroes-fortune-prompt = You lost the roll. Use Fortune to reroll?

# Disabled action reasons
ageofheroes-not-your-turn = It's not your turn.
ageofheroes-game-not-started = The game hasn't started yet.
ageofheroes-wrong-phase = This action is not available in the current phase.
ageofheroes-no-resources = You don't have the required resources.

# Building costs (for display)
ageofheroes-cost-army = 2 Grain, Iron
ageofheroes-cost-fortress = Iron, Wood, Stone
ageofheroes-cost-general = Iron, Gold
ageofheroes-cost-road = 2 Stone
ageofheroes-cost-city = 2 Wood, Stone

# Formats
ageofheroes-winner-line = Winner: {  }
ageofheroes-days-line = Days: {  }
