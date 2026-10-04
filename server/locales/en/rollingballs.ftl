# Rolling Balls

game-name-rollingballs = Rolling Balls

# Actions
rb-take = Take { $count } { $count ->
    [one] ball
   *[other] balls
}
rb-reshuffle-action = Reshuffle the front of the pipe ({ $remaining } uses remaining)
rb-view-pipe-action = Preview the pipe ({ $remaining } uses remaining)
rb-check-pipe-status = Check pipe status
rb-key-reshuffle-pipe = Reshuffle the front of the pipe
rb-key-view-pipe = Preview the pipe

# Taking and revealing balls
rb-you-take = You commit to taking { $count } { $count ->
    [one] ball
   *[other] balls
} from the front of the { $remaining }-ball pipe.
rb-player-takes = { $player } commits to taking { $count } { $count ->
    [one] ball
   *[other] balls
} from the front of the { $remaining }-ball pipe.
rb-you-take-brief = You take { $count } { $count ->
    [one] ball
   *[other] balls
}.
rb-player-takes-brief = { $player } takes { $count } { $count ->
    [one] ball
   *[other] balls
}.
rb-you-forced-take = Only { $count } { $count ->
    [one] ball remains
   *[other] balls remain
}, fewer than the minimum take of { $minimum }, so you must take the rest.
rb-player-forced-takes = Only { $count } { $count ->
    [one] ball remains
   *[other] balls remain
}, fewer than the minimum take of { $minimum }, so { $player } must take the rest.
rb-you-forced-take-brief = You must take the final { $count } { $count ->
    [one] ball
   *[other] balls
}.
rb-player-forced-takes-brief = { $player } must take the final { $count } { $count ->
    [one] ball
   *[other] balls
}.

rb-your-ball-plus = Your ball { $num }: { $description }. Plus { $value } { $value ->
    [one] point
   *[other] points
}.
rb-player-ball-plus = { $player }'s ball { $num }: { $description }. Plus { $value } { $value ->
    [one] point
   *[other] points
}.
rb-your-ball-minus = Your ball { $num }: { $description }. Minus { $value } { $value ->
    [one] point
   *[other] points
}.
rb-player-ball-minus = { $player }'s ball { $num }: { $description }. Minus { $value } { $value ->
    [one] point
   *[other] points
}.
rb-your-ball-zero = Your ball { $num }: { $description }. No score change.
rb-player-ball-zero = { $player }'s ball { $num }: { $description }. No score change.

rb-your-draw-summary = Your { $count }-ball draw has a net value of { $delta } points. Your score is now { $score }, with { $remaining } balls left in the pipe.
rb-player-draw-summary = { $player }'s { $count }-ball draw has a net value of { $delta } points. { $player }'s score is now { $score }, with { $remaining } balls left in the pipe.
rb-your-draw-summary-brief = Net { $delta }; your score is { $score }. { $remaining } balls remain.
rb-player-draw-summary-brief = { $player }: net { $delta }, score { $score }. { $remaining } balls remain.
rb-your-score-legacy = Your score is now { $score }, with { $remaining } balls left in the pipe.
rb-player-score-legacy = { $player }'s score is now { $score }, with { $remaining } balls left in the pipe.

# Reshuffling
rb-you-reshuffle = You reshuffle the first { $count } balls. { $penalty ->
    [0] There is no penalty
   *[other] You pay a { $penalty }-point penalty
}; your score is now { $score }, and you have { $remaining } reshuffles left.
rb-player-reshuffles = { $player } reshuffles the first { $count } balls. { $penalty ->
    [0] There is no penalty
   *[other] { $player } pays a { $penalty }-point penalty
}; { GENDER_TERM($player_gender, "possessive-determiner") } score is now { $score }, and { GENDER_TERM($player_gender, "subject-have") } { $remaining } reshuffles left.
rb-you-reshuffle-brief = You reshuffle { $count } balls; penalty { $penalty }, score { $score }, { $remaining } uses left.
rb-player-reshuffles-brief = { $player } reshuffles { $count } balls; penalty { $penalty }, score { $score }, { $remaining } uses left.

# Pipe preview and status
rb-view-pipe-header = Showing the next { $shown } of { $total } balls. You have { $remaining } new previews remaining.
rb-view-pipe-ball = { $num }: { $description }. Value: { $value } points.
rb-status-pipe = Round { $round }. { $count } balls remain in the pipe.
rb-status-take-range = Each normal turn requires between { $min } and { $max } balls.
rb-status-turn = Current turn: { $player }.
rb-status-resources = You have { $views } new pipe previews and { $reshuffles } reshuffles remaining.

# Start and round flow
rb-pipe-filled = The pipe has been filled with { $count } unique balls from: { $packs }.
rb-round-start = Round { $round } begins with { $count } balls remaining in the pipe.
rb-round-start-brief = Round { $round }; { $count } balls remain.

# End of game
rb-pipe-empty = The pipe is empty.
rb-winner = { $player } wins with { $score } points.
rb-you-win = You win with { $score } points.
rb-you-tie = You share the win with { $players }; each of you finished on { $score } points.
rb-tie = { $players } share the win with { $score } points.
rb-line-format = { $rank }. { $player }: { $points }

# Options
rb-set-min-take = Minimum balls per turn: { $count }
rb-enter-min-take = Enter the minimum balls per turn, from 1 to 5:
rb-option-changed-min-take = Minimum balls per turn set to { $count }.
rollingballs-desc-min-take = Minimum number of balls a player must take on a turn (default 1, range 1-5).
rb-set-max-take = Maximum balls per turn: { $count }
rb-enter-max-take = Enter the maximum balls per turn, from 1 to 5:
rb-option-changed-max-take = Maximum balls per turn set to { $count }.
rollingballs-desc-max-take = Maximum number of balls a player may take on a turn. The game cannot start if this is lower than the minimum (default 3, range 1-5).
rb-set-view-pipe-limit = New pipe previews per player: { $count }
rb-enter-view-pipe-limit = Enter new pipe previews per player, from 0 to 100; 0 disables previews:
rb-option-changed-view-pipe-limit = New pipe previews per player set to { $count }.
rollingballs-desc-view-pipe-limit = How many upcoming balls can be previewed from the pipe. Set 0 to disable previews (default 5, range 0-100).
rb-set-reshuffle-limit = Reshuffles per player: { $count }
rb-enter-reshuffle-limit = Enter reshuffles per player, from 0 to 100; 0 disables reshuffling:
rb-option-changed-reshuffle-limit = Reshuffles per player set to { $count }.
rollingballs-desc-reshuffle-limit = How many reshuffles are available before the pipe is exhausted (default 3, range 0-100).
rb-set-reshuffle-penalty = Reshuffle penalty: { $points } points
rb-enter-reshuffle-penalty = Enter the reshuffle penalty, from 0 to 5 points:
rb-option-changed-reshuffle-penalty = Reshuffle penalty set to { $points } points.
rollingballs-desc-reshuffle-penalty = Score penalty applied when a reshuffle is used. This option appears only when reshuffles are available (default 1, range 0-5).
rb-set-ball-packs = Ball sets ({ $count } of { $total } selected)
rb-option-changed-ball-packs = Ball set selection changed.
rollingballs-desc-ball-packs = Choose which themed ball sets are included in the pipe. At least one pack must stay selected.

# Contextual disabled reasons and setup validation
rb-draw-resolving = Wait until { $player }'s current ball draw finishes before starting another pipe action.
rb-take-not-your-turn = You cannot take { $count } balls now because it is { $player }'s turn.
rb-take-outside-range = You tried to take { $count } balls, but this game allows { $min } to { $max } per normal turn.
rb-not-enough-balls = You tried to take { $count } balls, but only { $remaining } remain in the pipe.
rb-reshuffle-not-your-turn = You cannot reshuffle now because it is { $player }'s turn.
rb-no-reshuffles-left = You have used all { $limit } of your reshuffles for this game.
rb-already-reshuffled = You already reshuffled during this turn. Take balls to finish the turn.
rb-not-enough-balls-to-reshuffle = Reshuffling needs at least { $required } balls, but only { $remaining } remain. Take balls instead.
rb-no-views-left = The pipe has changed, and you have used all { $limit } of your new previews. You may still reopen an unchanged preview before the pipe moves.
rb-error-min-take-invalid = The minimum take is { $count }; it must be from { $min } to { $max }.
rb-error-max-take-invalid = The maximum take is { $count }; it must be from { $min } to { $max }.
rb-error-take-range-conflict = The minimum take is { $min }, above the maximum of { $max }. Lower the minimum or raise the maximum before starting.
rb-error-view-limit-invalid = The preview limit is { $count }; it must be from { $min } to { $max }.
rb-error-reshuffle-limit-invalid = The reshuffle limit is { $count }; it must be from { $min } to { $max }.
rb-error-reshuffle-penalty-invalid = The reshuffle penalty is { $points }; it must be from { $min } to { $max } points.
rb-error-no-ball-packs = Select at least one ball set before starting Rolling Balls.
rb-error-invalid-ball-packs = The selection contains { $count } unavailable ball { $count ->
    [one] set
   *[other] sets
}. Remove unavailable sets before starting.

# Ball sets
rb-pack-international = Around the World
rb-pack-vietnam = Journey Through Vietnam

# Around the World: -5
rb-ball-paris-pickpocket = Passport and wallet stolen abroad
rb-ball-lost-luggage-in-london = Emergency medical visit abroad
rb-ball-tokyo-train-delay = Missed the last international connection
rb-ball-sahara-sandstorm = Severe-weather evacuation
rb-ball-passport-lost-before-flight = Passport lost before departure
# Around the World: -4
rb-ball-venice-flood = Flood closes your accommodation
rb-ball-new-york-traffic = Overnight flight cancellation
rb-ball-amazon-mosquito-swarm = Essential luggage sent to the wrong country
rb-ball-berlin-club-rejected = Hotel reservation missing at check-in
rb-ball-hotel-booking-vanished = Mountain route closed for several days
# Around the World: -3
rb-ball-spilled-coffee-in-rome = Phone cracked during a transfer
rb-ball-sydney-sunburn = Heat exhaustion cancels a day trip
rb-ball-istanbul-bazaar-scam = Prepaid tour booking falls through
rb-ball-moscow-blizzard = Snowstorm strands your train
rb-ball-dubai-heatwave = Rental vehicle breaks down
# Around the World: -2
rb-ball-mexico-city-smog = Poor air quality changes the itinerary
rb-ball-cairo-camel-spit = Motion sickness on a long journey
rb-ball-athens-ruins-trip = Sprained ankle on a walking tour
rb-ball-rio-carnival-hangover = Overslept and missed the morning tour
rb-ball-bali-belly = Upset stomach costs an afternoon
# Around the World: -1
rb-ball-swiss-alps-avalanche = Scenic trail closed for safety
rb-ball-amsterdam-bicycle-crash = Flat bicycle tire
rb-ball-bangkok-tuk-tuk-breakdown = Tuk-tuk stalls in traffic
rb-ball-iceland-volcano-ash = Weather alert delays the flight
rb-ball-cape-town-wind = Strong wind closes the viewpoint
# Around the World: 0
rb-ball-neutral-passport = A fresh passport stamp
rb-ball-airport-layover = A quiet airport layover
rb-ball-hotel-lobby = Waiting in the hotel lobby
rb-ball-tourist-map = Folding out the city map
rb-ball-souvenir-magnet = Choosing a souvenir magnet
# Around the World: +1
rb-ball-free-museum-day = Free museum admission
rb-ball-street-food-snack = Excellent street-food snack
rb-ball-post-card-home = Postcard sent home
rb-ball-friendly-local = Helpful directions from a local
rb-ball-sunny-day = Perfect weather for exploring
# Around the World: +2
rb-ball-eiffel-tower-view = Paris skyline from the Eiffel Tower
rb-ball-taj-mahal-sunrise = Sunrise at the Taj Mahal
rb-ball-great-wall-hike = Hike on the Great Wall
rb-ball-machu-picchu-climb = Morning at Machu Picchu
rb-ball-kyoto-cherry-blossoms = Cherry blossoms in Kyoto
# Around the World: +3
rb-ball-colosseum-tour = Guided visit to the Colosseum
rb-ball-pyramids-exploration = Exploring the Giza pyramid complex
rb-ball-santorini-sunset = Sunset over Santorini
rb-ball-aurora-borealis = Northern Lights overhead
rb-ball-safari-lion-sighting = Responsible safari wildlife sighting
# Around the World: +4
rb-ball-bora-bora-villa = Lagoon stay in Bora Bora
rb-ball-maldives-scuba = Reef dive in the Maldives
rb-ball-niagara-falls-boat = Boat journey at Niagara Falls
rb-ball-grand-canyon-heli = Grand Canyon flightseeing tour
rb-ball-serengeti-migration = Great Migration in the Serengeti
# Around the World: +5
rb-ball-first-class-upgrade = Surprise first-class upgrade
rb-ball-lottery-in-macau = A year-long rail pass won
rb-ball-private-jet = Once-in-a-lifetime island voyage
rb-ball-royal-palace-invite = Private after-hours museum visit
rb-ball-world-tour-ticket = Round-the-world ticket

# Journey Through Vietnam: -5
rb-ball-stolen-motorbike = Passport and wallet stolen during the journey
rb-ball-flooded-street-saigon = Flood forces an emergency relocation
rb-ball-food-poisoning-bun-mam = Medical emergency interrupts the trip
rb-ball-fake-taxi-scam = Transport breakdown causes a missed flight
rb-ball-passport-lost-at-airport = Passport lost at the airport
# Journey Through Vietnam: -4
rb-ball-typhoon-in-central-vietnam = Typhoon evacuation on the central coast
rb-ball-lost-wallet-ben-thanh = Essential luggage lost in transit
rb-ball-traffic-jam-hanoi = Overnight train cancellation
rb-ball-pickpocketed-in-bui-vien = Phone stolen in a crowded district
rb-ball-mountain-road-landslide = Mountain pass closed by a landslide
# Journey Through Vietnam: -3
rb-ball-spilled-pho = Camera damaged in sudden rain
rb-ball-overcharged-for-coffee = Hotel booking mix-up
rb-ball-sunburn-in-mui-ne = Heat exhaustion in Mui Ne
rb-ball-missed-train-to-sapa = Missed the overnight train to Lao Cai
rb-ball-loud-karaoke-next-door = Sleepless night before an early departure
# Journey Through Vietnam: -2
rb-ball-broken-flip-flop = Sandal strap snaps on a walking tour
rb-ball-sudden-downpour = Sudden tropical downpour
rb-ball-dog-chased-you = Wrong bus stop far from the hotel
rb-ball-bitten-by-mosquitoes = An evening of mosquito bites
rb-ball-out-of-gas = Motorbike runs out of fuel
# Journey Through Vietnam: -1
rb-ball-spicy-chili-bite = An unexpectedly fierce chili
rb-ball-delayed-flight = Short domestic flight delay
rb-ball-wifi-disconnected = Weak signal in the mountains
rb-ball-forgot-umbrella = Raincoat left at the hotel
rb-ball-minor-scratch = Wrong turn in the Old Quarter
# Journey Through Vietnam: 0
rb-ball-plastic-stool = A seat on a sidewalk stool
rb-ball-iced-tea-tra-da = Glass of tra da
rb-ball-waiting-for-green-light = Waiting through a long red light
rb-ball-bamboo-hat = Trying on a non la
rb-ball-motorbike-helmet = Fastening a motorbike helmet
# Journey Through Vietnam: +1
rb-ball-tasty-banh-mi = Crisp banh mi for breakfast
rb-ball-free-sugar-cane-juice = Fresh sugarcane juice
rb-ball-friendly-street-vendor = Warm welcome from a market vendor
rb-ball-cool-breeze = Cool breeze after the rain
rb-ball-found-10k-vnd = A bargain local bus ride
# Journey Through Vietnam: +2
rb-ball-delicious-pho-bowl = Fragrant bowl of pho
rb-ball-egg-coffee-in-hanoi = Egg coffee in Hanoi
rb-ball-boat-ride-in-ninh-binh = Sampan ride through the Trang An Landscape Complex
rb-ball-lantern-festival-hoian = Lantern-lit evening in Hoi An Ancient Town
rb-ball-motorbike-road-trip = Orchard boat ride in the Mekong Delta
# Journey Through Vietnam: +3
rb-ball-ha-long-bay-cruise = Cruise through Ha Long Bay - Cat Ba Archipelago
rb-ball-golden-bridge-bana-hills = Golden Bridge above Ba Na Hills
rb-ball-phu-quoc-sunset = Sunset on Phu Quoc
rb-ball-sapa-terraced-fields = Terraced fields around Sa Pa
rb-ball-phong-nha-cave-exploration = Cave journey in Phong Nha - Ke Bang
# Journey Through Vietnam: +4
rb-ball-tet-holiday-lucky-money = Tet reunion and lucky money
rb-ball-vip-ticket-to-concert = Sunrise on the Ha Giang loop
rb-ball-luxury-resort-stay = Community conservation visit in Con Dao
rb-ball-business-class-flight = Scenic berth on the Reunification Express
rb-ball-won-lottery-vietlott = Festival night among the monuments of Hue
# Journey Through Vietnam: +5
rb-ball-billionaire-inheritance = Son Doong expedition
rb-ball-found-gold-treasure = Private cultural workshop with master artisans
rb-ball-free-house-in-district-1 = Month-long rail journey across Vietnam
rb-ball-national-hero-award = Honored guest at a village festival
rb-ball-ultimate-happiness = Dream journey from Ha Giang to Ca Mau
