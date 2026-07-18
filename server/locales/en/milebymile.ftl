game-name-milebymile = Mile by Mile

milebymile-set-distance = Race distance: { $miles } miles
milebymile-enter-distance = Enter race distance (300-3000)
milebymile-set-winning-score = Winning score: { $score } points
milebymile-enter-winning-score = Enter winning score (1000-10000)
milebymile-desc-team-mode = Play individually or in a team arrangement supported by the current player count.
milebymile-toggle-perfect-crossing = Require exact finish: { $enabled }
milebymile-toggle-stacking = Allow stacking attacks: { $enabled }
milebymile-toggle-reshuffle = Reshuffle discard pile: { $enabled }
milebymile-toggle-karma = Karma rule: { $enabled }
milebymile-set-rig = Deck rigging: { $rig }
milebymile-select-rig = Select deck rigging option
milebymile-rig-none = None
milebymile-rig-no-duplicates = No Duplicates
milebymile-rig-2x-attacks = 2x Attacks
milebymile-rig-2x-defenses = 2x Defenses

milebymile-option-changed-distance = Race distance set to { $miles } miles.
milebymile-desc-round-distance = Target distance for each race. If exact finish is enabled, this distance must be divisible by 25 (default 1,000 miles, range 300-3,000).
milebymile-option-changed-winning = Winning score set to { $score } points.
milebymile-desc-winning-score = Total score needed to win the Mile by Mile match (default 5,000, range 1,000-10,000).
milebymile-option-changed-crossing = Require exact finish { $enabled }.
milebymile-desc-only-allow-perfect-crossing = When enabled, a player must reach the race target exactly; distance cards that would pass the finish cannot be played.
milebymile-option-changed-stacking = Allow stacking attacks { $enabled }.
milebymile-desc-allow-stacking-attacks = When enabled, multiple hazards can affect the same car instead of being blocked by an existing hazard.
milebymile-option-changed-reshuffle = Reshuffle discard pile { $enabled }.
milebymile-desc-reshuffle-discard-pile = When enabled, the discard pile is shuffled back into the draw deck when the deck runs out.
milebymile-option-changed-karma = Karma rule { $enabled }.
milebymile-desc-karma-rule = Controls whether karma cards and shunning are used. Attacking while both sides have karma neutralizes the attack; a shunned attacker can only target another shunned side. Requires at least 3 cars or teams.
milebymile-option-changed-rig = Deck rigging set to { $rig }.
milebymile-desc-rig-game = Optional deck composition variant: normal, no duplicate cards, double attacks, or double defenses.

milebymile-status = { $score_info }, { $miles } miles, Problems: { $problems }, Safeties: { $safeties }

milebymile-no-matching-safety = You don't have the matching safety card!
milebymile-dirty-trick-wait = Wait for the Dirty Trick response.
milebymile-cant-play = You can't play { $card } because { $reason }.
milebymile-unplayable-card-menu-title = Card cannot be played
milebymile-unplayable-discard-question = You cannot play { $card } because { $reason }. Do you want to discard it?
milebymile-no-card-selected = No card selected to discard.
milebymile-no-valid-targets = No valid targets for this hazard!
milebymile-you-drew = You drew: { $card }
milebymile-you-discard = You discard { $card }.
milebymile-discards = { $player } discards { $card }.
milebymile-select-target = Select a target

milebymile-you-play-distance-individual = You play { $distance } miles, and are now at { $total } miles.
milebymile-plays-distance-individual = { $player } plays { $distance } miles, and is now at { $total } miles.
milebymile-you-play-distance-team = You play { $distance } miles; your team is now at { $total } miles.
milebymile-plays-distance-team = { $player } plays { $distance } miles; their team is now at { $total } miles.

milebymile-you-complete-perfect-individual = You complete the journey with a perfect crossing!
milebymile-journey-complete-perfect-individual = { $player } has completed the journey with a perfect crossing!
milebymile-your-team-completes-perfect = Your team completes the journey with a perfect crossing!
milebymile-journey-complete-perfect-team = Team { $team } has completed the journey with a perfect crossing!
milebymile-you-complete-individual = You complete the journey!
milebymile-journey-complete-individual = { $player } has completed the journey!
milebymile-your-team-completes = Your team completes the journey!
milebymile-journey-complete-team = Team { $team } has completed the journey!

milebymile-you-play-hazard-individual = You play { $card } on { $target }.
milebymile-hazard-played-on-you = { $player } plays { $card } on you.
milebymile-plays-hazard-individual = { $player } plays { $card } on { $target }.
milebymile-you-play-hazard-team = You play { $card } on Team { $team }.
milebymile-hazard-played-on-your-team = { $player } plays { $card } on your team.
milebymile-plays-hazard-team = { $player } plays { $card } on Team { $team }.

milebymile-you-play-card = You play { $card }.
milebymile-plays-card = { $player } plays { $card }.
milebymile-you-play-dirty-trick = You play { $card } as a Dirty Trick!
milebymile-plays-dirty-trick = { $player } plays { $card } as a Dirty Trick!

milebymile-deck-reshuffled = Discard pile shuffled back into deck.

milebymile-new-race = New race begins!
milebymile-race-complete = Race complete! Calculating scores...
milebymile-earned-points = { $name } earned { $score } points this race: { $breakdown }.
milebymile-total-scores = Total scores:
milebymile-team-score = { $name }: { $score } points

milebymile-from-distance = { $miles } from distance travelled
milebymile-from-trip = { $points } from completing the trip
milebymile-from-delayed = { $points } from delayed action
milebymile-from-perfect = { $points } from a perfect crossing
milebymile-from-safe = { $points } from a safe trip
milebymile-from-shutout = { $points } from a shut out
milebymile-from-safeties = { $points } from { $count } { $count ->
    [one] safety
    *[other] safeties
}
milebymile-from-all-safeties = { $points } from all 4 safeties
milebymile-from-dirty-tricks = { $points } from { $count } { $count ->
    [one] dirty trick
    *[other] dirty tricks
}

milebymile-you-win-individual = You win the game!
milebymile-wins-individual = { $player } wins the game!
milebymile-your-team-wins = Your team wins the game!
milebymile-wins-team = Team { $team } wins the game! ({ $members })
milebymile-final-score = Final score: { $score } points

milebymile-karma-clash-you-target = You and your target are both shunned! The attack is neutralized.
milebymile-karma-clash-you-attacker = You and { $attacker } are both shunned! The attack is neutralized.
milebymile-karma-clash-others = { $attacker } and { $target } are both shunned! The attack is neutralized.
milebymile-karma-clash-your-team = Your team and your target are both shunned! The attack is neutralized.
milebymile-karma-clash-target-team = You and Team { $team } are both shunned! The attack is neutralized.
milebymile-karma-clash-other-teams = Team { $attacker } and Team { $target } are both shunned! The attack is neutralized.

milebymile-karma-shunned-you = You have been shunned for your aggression! Your karma is lost.
milebymile-karma-shunned-other = { $player } has been shunned for their aggression!
milebymile-karma-shunned-your-team = Your team has been shunned for its aggression! Your team's karma is lost.
milebymile-karma-shunned-other-team = Team { $team } has been shunned for its aggression!

milebymile-false-virtue-you = You play False Virtue and regain your karma!
milebymile-false-virtue-other = { $player } plays False Virtue and regains their karma!
milebymile-false-virtue-your-team = Your team plays False Virtue and regains its karma!
milebymile-false-virtue-other-team = Team { $team } plays False Virtue and regains its karma!

milebymile-none = none

milebymile-reason-not-on-team = you're not on a team
milebymile-reason-stopped = you need a Green Light before you can drive
milebymile-reason-has-problem = a road problem is stopping your car
milebymile-reason-out-of-gas = you cannot move because you are out of gas; play Gasoline or Extra Tank first
milebymile-reason-flat-tire = you cannot move because you have a flat tire; play Spare Tire or Puncture Proof first
milebymile-reason-accident = you cannot move because you had an accident; play Repairs or Driving Ace first
milebymile-reason-speed-limit = you are under a Speed Limit, so only 25 or 50 mile cards are allowed
milebymile-reason-exceeds-distance = you are at { $current } miles, and a { $distance }-mile card would put you at { $total } miles, past the { $target }-mile finish; exact finish is on, so you need exactly { $miles } more miles
milebymile-reason-too-many-200s = you have already played two 200-mile cards this race
milebymile-reason-no-targets = no opponent can legally receive this hazard right now
milebymile-reason-no-opponents = there are no opposing teams to target
milebymile-reason-hazard-protected = every possible target is protected from { $card } by { $safety }
milebymile-reason-hazard-karma = you have lost karma and can only attack a target that has also lost karma
milebymile-reason-hazard-duplicate-speed-limit = every possible target is already under a Speed Limit
milebymile-reason-hazard-duplicate = every possible target already has { $card }
milebymile-reason-hazard-blocked = every possible target is already stopped by another hazard
milebymile-reason-no-speed-limit = you're not under a speed limit
milebymile-reason-has-right-of-way = Right of Way lets you go without green lights
milebymile-reason-already-moving = you're already moving
milebymile-reason-must-fix-first = you must fix the { $problem } first with { $remedy }
milebymile-reason-has-gas = your car has gas
milebymile-reason-tires-fine = your tires are fine
milebymile-reason-no-accident = your car hasn't been in an accident
milebymile-reason-has-safety = you already have that safety
milebymile-reason-has-karma = you still have your karma
milebymile-reason-generic = it can't be played right now

milebymile-card-out-of-gas = Out of Gas
milebymile-card-flat-tire = Flat Tire
milebymile-card-accident = Accident
milebymile-card-speed-limit = Speed Limit
milebymile-card-stop = Stop
milebymile-card-gasoline = Gasoline
milebymile-card-spare-tire = Spare Tire
milebymile-card-repairs = Repairs
milebymile-card-end-of-limit = End of Limit
milebymile-card-green-light = Green Light
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Puncture Proof
milebymile-card-driving-ace = Driving Ace
milebymile-card-right-of-way = Right of Way
milebymile-card-false-virtue = False Virtue
milebymile-card-miles = { $miles } miles

milebymile-no-dirty-trick-window = No dirty trick window is active.
milebymile-not-your-dirty-trick = It's not your team's dirty trick window.
milebymile-between-races = Wait for the next race to start.

milebymile-error-karma-needs-three-teams = Karma rule requires at least 3 distinct cars/teams.
milebymile-error-perfect-distance-step = Exact finish requires a race distance divisible by 25, because all distance cards are multiples of 25.

milebymile-line-format = { $rank }. { $name }: { $points }

milebymile-target-individual = { $name } ({ $miles } miles)
milebymile-target-team = Team { $team }: { $members } ({ $miles } miles)

milebymile-discard-card = Discard card
milebymile-detailed-status = Detailed status
milebymile-check-status = Check status
milebymile-dirty-trick = Play dirty trick
milebymile-info-button = Info
milebymile-info-msg-individual = { $player }: Hazards: { $hazards }. Safeties: { $safeties }. Distance: { $miles } miles.
milebymile-info-msg-team = { $team } ({ $members }): Hazards: { $hazards }. Safeties: { $safeties }. Distance: { $miles } miles.
