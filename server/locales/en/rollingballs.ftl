# Rolling Balls game messages
# Note: Common messages like round-start, turn-start are in games.ftl

# Game info
game-name-rollingballs = Rolling Balls

# Turn actions
rb-take = Take { $count } { $count ->
    [one] ball
   *[other] balls
}
rb-reshuffle-action = Reshuffle pipe ({ $remaining } uses remaining)
rb-view-pipe-action = View pipe ({ $remaining } uses remaining)

# Take ball events
rb-you-take = You take { $count } { $count ->
    [one] ball
   *[other] balls
}!
rb-player-takes = { $player } takes { $count } { $count ->
    [one] ball
   *[other] balls
}!
rb-ball-plus = Ball { $num }: { $description }! Plus { $value } points!
rb-ball-minus = Ball { $num }: { $description }! Minus { $value } points!
rb-ball-zero = Ball { $num }: { $description }! No change!
rb-new-score = { $player }'s score: { $score } points.

# Reshuffle events
rb-you-reshuffle = You reshuffle the pipe!
rb-player-reshuffles = { $player } reshuffles the pipe!
rb-reshuffled = The pipe has been reshuffled!
rb-reshuffle-penalty = { $player } loses { $points } { $points ->
    [one] point
   *[other] points
} for reshuffling.

# View pipe
rb-view-pipe-header = There are { $count } balls:
rb-view-pipe-ball = { $num }: { $description }. Value: { $value } points.

# Game start
rb-pipe-filled = The pipe has been filled with { $count } balls!
rb-balls-remaining = { $count } balls remain in the pipe.

# Game end
rb-pipe-empty = The pipe is empty!
rb-score-line = { $player }: { $score } points.
rb-winner = The winner is { $player } with { $score } points!
rb-you-win = You win with { $score } points!
rb-tie = It's a tie between { $players } with { $score } points!
rb-line-format = { $rank }. { $player }: { $points }

# Options
rb-set-min-take = Minimum balls required to take each turn: { $count }
rb-enter-min-take = Enter the minimum number of balls to take (1-5):
rb-option-changed-min-take = Minimum balls to take set to { $count }.

rb-set-max-take = Maximum balls allowed to take each turn: { $count }
rb-enter-max-take = Enter the maximum number of balls to take (1-5):
rb-option-changed-max-take = Maximum balls to take set to { $count }.

rb-set-view-pipe-limit = View pipe limit: { $count }
rb-enter-view-pipe-limit = Enter view pipe limit (0 to disable, max 100):
rb-option-changed-view-pipe-limit = View pipe limit set to { $count }.

rb-set-reshuffle-limit = Reshuffle limit: { $count }
rb-enter-reshuffle-limit = Enter reshuffle limit (0 to disable, max 100):
rb-option-changed-reshuffle-limit = Reshuffle limit set to { $count }.

rb-set-reshuffle-penalty = Reshuffle penalty: { $points }
rb-enter-reshuffle-penalty = Enter reshuffle penalty (0-5):
rb-option-changed-reshuffle-penalty = Reshuffle penalty set to { $points }.

rb-set-ball-pack = Ball pack: { $pack }
rb-select-ball-pack = Select the ball pack to use:
rb-option-changed-ball-pack = Ball pack set to { $pack }.

# Disabled reasons
rb-not-enough-balls = Not enough balls in the pipe.
rb-no-reshuffles-left = No reshuffles remaining.
rb-already-reshuffled = You already reshuffled this turn.
rb-no-views-left = No pipe views remaining.

# Ball pack items
rb-pack-all = All Packs Mixed
rb-pack-international = International Travel
rb-ball-paris-pickpocket = Paris Pickpocket
rb-ball-lost-luggage-in-london = Lost Luggage in London
rb-ball-tokyo-train-delay = Tokyo Train Delay
rb-ball-sahara-sandstorm = Sahara Sandstorm
rb-ball-venice-flood = Venice Flood
rb-ball-new-york-traffic = New York Traffic
rb-ball-amazon-mosquito-swarm = Amazon Mosquito Swarm
rb-ball-berlin-club-rejected = Rejected at Berlin Club
rb-ball-spilled-coffee-in-rome = Spilled Coffee in Rome
rb-ball-sydney-sunburn = Sydney Sunburn
rb-ball-istanbul-bazaar-scam = Istanbul Bazaar Scam
rb-ball-moscow-blizzard = Moscow Blizzard
rb-ball-dubai-heatwave = Dubai Heatwave
rb-ball-mexico-city-smog = Mexico City Smog
rb-ball-cairo-camel-spit = Cairo Camel Spit
rb-ball-athens-ruins-trip = Tripped in Athens Ruins
rb-ball-rio-carnival-hangover = Rio Carnival Hangover
rb-ball-bali-belly = Bali Belly
rb-ball-swiss-alps-avalanche = Swiss Alps Avalanche
rb-ball-amsterdam-bicycle-crash = Amsterdam Bicycle Crash
rb-ball-bangkok-tuk-tuk-breakdown = Bangkok Tuk-Tuk Breakdown
rb-ball-iceland-volcano-ash = Iceland Volcano Ash
rb-ball-cape-town-wind = Cape Town Wind
rb-ball-neutral-passport = Neutral Passport
rb-ball-airport-layover = Airport Layover
rb-ball-hotel-lobby = Hotel Lobby Wait
rb-ball-tourist-map = Tourist Map
rb-ball-souvenir-magnet = Souvenir Magnet
rb-ball-free-museum-day = Free Museum Day
rb-ball-street-food-snack = Street Food Snack
rb-ball-post-card-home = Postcard Home
rb-ball-friendly-local = Friendly Local
rb-ball-sunny-day = Sunny Day
rb-ball-eiffel-tower-view = Eiffel Tower View
rb-ball-taj-mahal-sunrise = Taj Mahal Sunrise
rb-ball-great-wall-hike = Great Wall Hike
rb-ball-machu-picchu-climb = Machu Picchu Climb
rb-ball-kyoto-cherry-blossoms = Kyoto Cherry Blossoms
rb-ball-colosseum-tour = Colosseum Tour
rb-ball-pyramids-exploration = Pyramids Exploration
rb-ball-santorini-sunset = Santorini Sunset
rb-ball-aurora-borealis = Aurora Borealis
rb-ball-safari-lion-sighting = Safari Lion Sighting
rb-ball-bora-bora-villa = Bora Bora Villa
rb-ball-maldives-scuba = Maldives Scuba Diving
rb-ball-niagara-falls-boat = Niagara Falls Boat Ride
rb-ball-grand-canyon-heli = Grand Canyon Helicopter
rb-ball-serengeti-migration = Serengeti Migration
rb-ball-first-class-upgrade = First Class Upgrade
rb-ball-lottery-in-macau = Lottery Win in Macau
rb-ball-private-jet = Private Jet Charter
rb-ball-royal-palace-invite = Royal Palace Invite
rb-ball-world-tour-ticket = World Tour Ticket

rb-pack-vietnam = Vietnam Adventure
rb-ball-stolen-motorbike = Stolen Motorbike
rb-ball-flooded-street-saigon = Flooded Street in Saigon
rb-ball-food-poisoning-bun-mam = Food Poisoning from Bun Mam
rb-ball-fake-taxi-scam = Fake Taxi Scam
rb-ball-typhoon-in-central-vietnam = Typhoon in Central Vietnam
rb-ball-lost-wallet-ben-thanh = Lost Wallet at Ben Thanh Market
rb-ball-traffic-jam-hanoi = Traffic Jam in Hanoi
rb-ball-pickpocketed-in-bui-vien = Pickpocketed in Bui Vien
rb-ball-spilled-pho = Spilled Pho
rb-ball-overcharged-for-coffee = Overcharged for Coffee
rb-ball-sunburn-in-mui-ne = Sunburn in Mui Ne
rb-ball-missed-train-to-sapa = Missed Train to Sapa
rb-ball-loud-karaoke-next-door = Loud Karaoke Next Door
rb-ball-broken-flip-flop = Broken Flip-Flop
rb-ball-sudden-downpour = Sudden Downpour
rb-ball-dog-chased-you = Chased by a Dog
rb-ball-bitten-by-mosquitoes = Bitten by Mosquitoes
rb-ball-out-of-gas = Out of Gas
rb-ball-spicy-chili-bite = Spicy Chili Bite
rb-ball-delayed-flight = Delayed Flight
rb-ball-wifi-disconnected = Wi-Fi Disconnected
rb-ball-forgot-umbrella = Forgot Umbrella
rb-ball-minor-scratch = Minor Scratch
rb-ball-plastic-stool = Plastic Stool
rb-ball-iced-tea-tra-da = Iced Tea (Tra Da)
rb-ball-waiting-for-green-light = Waiting for Green Light
rb-ball-bamboo-hat = Non La (Bamboo Hat)
rb-ball-motorbike-helmet = Motorbike Helmet
rb-ball-tasty-banh-mi = Tasty Banh Mi
rb-ball-free-sugar-cane-juice = Free Sugar Cane Juice
rb-ball-friendly-street-vendor = Friendly Street Vendor
rb-ball-cool-breeze = Cool Breeze
rb-ball-found-10k-vnd = Found 10k VND
rb-ball-delicious-pho-bowl = Delicious Pho Bowl
rb-ball-egg-coffee-in-hanoi = Egg Coffee in Hanoi
rb-ball-boat-ride-in-ninh-binh = Boat Ride in Ninh Binh
rb-ball-lantern-festival-hoian = Lantern Festival in Hoi An
rb-ball-motorbike-road-trip = Motorbike Road Trip
rb-ball-ha-long-bay-cruise = Ha Long Bay Cruise
rb-ball-golden-bridge-bana-hills = Golden Bridge in Ba Na Hills
rb-ball-phu-quoc-sunset = Phu Quoc Sunset
rb-ball-sapa-terraced-fields = Sapa Terraced Fields
rb-ball-phong-nha-cave-exploration = Phong Nha Cave Exploration
rb-ball-tet-holiday-lucky-money = Tet Holiday Lucky Money
rb-ball-vip-ticket-to-concert = VIP Ticket to Concert
rb-ball-luxury-resort-stay = Luxury Resort Stay
rb-ball-business-class-flight = Business Class Flight
rb-ball-won-lottery-vietlott = Won Lottery (Vietlott)
rb-ball-billionaire-inheritance = Billionaire Inheritance
rb-ball-found-gold-treasure = Found Gold Treasure
rb-ball-free-house-in-district-1 = Free House in District 1
rb-ball-national-hero-award = National Hero Award
rb-ball-ultimate-happiness = Ultimate Happiness
