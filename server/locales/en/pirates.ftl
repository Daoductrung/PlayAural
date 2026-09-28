game-name-pirates = Pirates of the Lost Seas

# Setup and round flow
pirates-welcome = Welcome to Pirates of the Lost Seas. Sail the forty-space route, recover the scattered gems, and outmaneuver rival crews.
pirates-welcome-brief = Welcome to Pirates of the Lost Seas.
pirates-oceans = Your voyage crosses { $oceans }.
pirates-gems-placed = All { $total } gems have been hidden along the route. The highest cargo value wins after the final gem is recovered.
pirates-gems-placed-brief = { $total } gems are hidden along the route.
pirates-golden-moon = The Golden Moon rises in round { $round }. Every XP award this round is tripled.
pirates-golden-moon-brief = Golden Moon: triple XP in round { $round }.
pirates-turn-you = Your turn in round { $round }. You are at position { $position } in { $ocean }.
pirates-turn-you-brief = Your turn. Position { $position }.
pirates-turn = { $player }'s turn in round { $round }, at position { $position } in { $ocean }.
pirates-turn-brief = { $player }'s turn.

# Movement and map information
pirates-move-left = Sail one space left
pirates-move-right = Sail one space right
pirates-move-2-left = Sail two spaces left
pirates-move-2-right = Sail two spaces right
pirates-move-3-left = Sail three spaces left
pirates-move-3-right = Sail three spaces right
pirates-move-you = You sail { $tiles } { $tiles ->
    [one] space
   *[other] spaces
} { $direction } to position { $position } in { $ocean }.
pirates-move-you-brief = You sail to position { $position }.
pirates-move = { $player } sails { $tiles } { $tiles ->
    [one] space
   *[other] spaces
} { $direction } to position { $position } in { $ocean }.
pirates-move-brief = { $player } sails to position { $position }.
pirates-map-edge = You cannot sail farther in that direction; position { $position } is the edge of the route. Choose another action.
pirates-dir-left = left
pirates-dir-right = right
pirates-your-position = You are at position { $position }, sector { $sector }, in { $ocean }.
pirates-check-position = Check position
pirates-check-moon = Check Golden Moon
pirates-moon-active = The Golden Moon is active in round { $round }. XP is tripled. Crews have recovered { $collected } of { $total } gems, with { $remaining } remaining.
pirates-moon-inactive = The Golden Moon is not active in round { $round }. It returns in { $rounds } { $rounds ->
    [one] round
   *[other] rounds
}. Crews have recovered { $collected } of { $total } gems, with { $remaining } remaining.

# Status and results
pirates-check-status = Check crew status
pirates-check-status-detailed = Detailed crew status
pirates-status-line = { $player }: level { $level}; { $xp } total XP, { $progress } of { $needed } XP toward the next level; { $points }; { $gem_count } { $gem_count ->
    [one] gem
   *[other] gems
}{ $detail ->
    [yes] ; position { $position } in { $ocean }; cargo: { $gems }; active effects: { $skills }
   *[no] { "" }
}.
pirates-end-score-line = { $rank }. { $player}: { $points }, level { $level }
pirates-all-gems-collected = The final gem has been recovered. The crews compare their cargo.
pirates-all-gems-collected-brief = Final gem recovered.
pirates-you-win = You win with { $score } points.
pirates-you-win-brief = You win: { $score } points.
pirates-winner = { $player } wins with { $score } points.
pirates-winner-brief = { $player } wins: { $score } points.
pirates-you-tie = You tie for first with { $players } at { $score } points.
pirates-you-tie-brief = You tie for first at { $score }.
pirates-players-tie = { $players } tie for first with { $score } points.
pirates-players-tie-brief = { $players } tie at { $score }.

# Gems and XP
pirates-gem-found-you = You recover the { $gem }, worth { $value } { $value ->
    [one] point
   *[other] points
}. Your cargo is now worth { $score } points; { $remaining } gems remain at sea.
pirates-gem-found-you-brief = You recover the { $gem }. Score: { $score }.
pirates-gem-found = { $player } recovers the { $gem }, worth { $value } { $value ->
    [one] point
   *[other] points
}. Their cargo is now worth { $score } points; { $remaining } gems remain at sea.
pirates-gem-found-brief = { $player } recovers the { $gem }.
pirates-xp-gained-you = You gain { $xp } XP for { $reason ->
    [gem] recovering a gem
    [attack] landing a cannon hit
    [defense] repelling a cannon attack
   *[other] completing an action
}. You now have { $total } total XP.
pirates-xp-gained-you-brief = You gain { $xp } XP. Total: { $total }.
pirates-xp-gained-player = { $player } gains { $xp } XP for { $reason ->
    [gem] recovering a gem
    [attack] landing a cannon hit
    [defense] repelling a cannon attack
   *[other] completing an action
}, reaching { $total } total XP.
pirates-xp-gained-player-brief = { $player } gains { $xp } XP.
pirates-level-up-you = You reach level { $level }.
pirates-level-up-you-brief = You reach level { $level }.
pirates-level-up = { $player } reaches level { $level }.
pirates-level-up-brief = { $player } reaches level { $level }.
pirates-level-up-multiple-you = You gain { $levels } levels and reach level { $level }.
pirates-level-up-multiple-you-brief = You reach level { $level }.
pirates-level-up-multiple = { $player } gains { $levels } levels and reaches level { $level }.
pirates-level-up-multiple-brief = { $player } reaches level { $level }.
pirates-skills-unlocked-you = At level { $level }, you unlock { $skills }.
pirates-skills-unlocked-you-brief = You unlock { $skills }.
pirates-skills-unlocked = At level { $level }, { $player } unlocks { $skills }.
pirates-skills-unlocked-brief = { $player } unlocks { $skills }.

# Cannon combat
pirates-cannonball = Fire cannonball
pirates-select-cannon-target = Choose a ship within cannon range
pirates-target-option = { $player }, { $distance } { $distance ->
    [one] space
   *[other] spaces
} away, { $score } points, carrying { $gems } { $gems ->
    [one] gem
   *[other] gems
}
pirates-target-unavailable = Unavailable ship
pirates-no-targets = No rival ship is within your current cannon range of { $range } spaces. Choose movement or another available skill.
pirates-target-out-of-range = { $target } is no longer within your { $range }-space cannon range from position { $position }. Choose another action.
pirates-attack-you-fire = You fire a cannonball at { $target }.
pirates-attack-you-fire-brief = You fire at { $target }.
pirates-attack-incoming = { $attacker } fires a cannonball at you.
pirates-attack-incoming-brief = { $attacker } fires at you.
pirates-attack-fired = { $attacker } fires a cannonball at { $defender }.
pirates-attack-fired-brief = { $attacker } fires at { $defender }.
pirates-combat-rolls-you = Your attack die is { $attack_die}, plus { $attack_bonus}, for { $attack_total}. { $defender }'s defense die is { $defense_die}, plus { $defense_bonus}, for { $defense_total}.
pirates-combat-rolls-you-brief = Attack { $attack_total}; defense { $defense_total}.
pirates-combat-rolls-defender = { $attacker } attacks with { $attack_die}, plus { $attack_bonus}, for { $attack_total}. Your defense die is { $defense_die}, plus { $defense_bonus}, for { $defense_total}.
pirates-combat-rolls-defender-brief = Attack { $attack_total}; your defense { $defense_total}.
pirates-combat-rolls-observer = { $attacker } attacks with { $attack_die}, plus { $attack_bonus}, for { $attack_total}. { $defender } defends with { $defense_die}, plus { $defense_bonus}, for { $defense_total}.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total}; { $defender } { $defense_total}.
pirates-attack-hit-you = Direct hit. Your { $attack_total } beats { $target }'s { $defense_total}; choose an available boarding action.
pirates-attack-hit-you-brief = You hit { $target }, { $attack_total } to { $defense_total}.
pirates-attack-hit-them = { $attacker } hits you, { $attack_total } to { $defense_total}, and may now board your ship.
pirates-attack-hit-them-brief = { $attacker } hits you, { $attack_total } to { $defense_total}.
pirates-attack-hit = { $attacker } hits { $defender }, { $attack_total } to { $defense_total}, and may board.
pirates-attack-hit-brief = { $attacker } hits { $defender }.
pirates-attack-hit-no-boarding-you = Direct hit. Your { $attack_total } beats { $target }'s { $defense_total}. This Battleship hit grants XP but no boarding action.
pirates-attack-hit-no-boarding-you-brief = You hit { $target }, { $attack_total } to { $defense_total}; no boarding.
pirates-attack-hit-no-boarding-them = { $attacker } hits you, { $attack_total } to { $defense_total}. Battleship hits do not grant boarding actions.
pirates-attack-hit-no-boarding-them-brief = { $attacker } hits you; no boarding.
pirates-attack-hit-no-boarding = { $attacker } hits { $defender }, { $attack_total } to { $defense_total}. This Battleship hit grants no boarding action.
pirates-attack-hit-no-boarding-brief = { $attacker } hits { $defender}; no boarding.
pirates-attack-miss-you = Your attack total of { $attack_total } does not beat { $target }'s defense total of { $defense_total}. Your turn ends.
pirates-attack-miss-you-brief = You miss { $target }, { $attack_total } to { $defense_total}.
pirates-attack-miss-them = You repel { $attacker } with a defense total of { $defense_total } against { $attack_total}.
pirates-attack-miss-them-brief = You repel { $attacker }, { $defense_total } to { $attack_total}.
pirates-attack-miss = { $defender } repels { $attacker }, { $defense_total } to { $attack_total}.
pirates-attack-miss-brief = { $attacker } misses { $defender }.

# Boarding
pirates-resolve-boarding = Resolve boarding
pirates-select-boarding-action = The cannon hit. Choose how to resolve the boarding action
pirates-boarding-steal = Attempt to steal a gem
pirates-boarding-push-left = Ram the defender left
pirates-boarding-push-right = Ram the defender right
pirates-boarding-option-unknown = Unknown boarding action
pirates-must-resolve-boarding = Resolve your pending boarding action before taking another turn action.
pirates-no-pending-boarding = There is no pending boarding action for you to resolve.
pirates-boarding-stale = The pending boarding action no longer has a valid defender, so it has been cancelled. Choose another turn action.
pirates-boarding-option-unavailable = { $action } is no longer available against { $defender }. Choose one of the current boarding options.
pirates-push-you = You ram { $target } { $direction } from position { $old_pos } to { $new_pos }, moving { GENDER_TERM($target_gender, "object") } { $distance } spaces. Your Push bonus contributed { $bonus } extra spaces.
pirates-push-you-brief = You ram { $target } to position { $position }.
pirates-push-them = { $attacker } rams you { $direction } from position { $old_pos } to { $new_pos }, moving you { $distance } spaces.
pirates-push-them-brief = { $attacker } rams you to position { $position }.
pirates-push = { $attacker } rams { $defender } { $direction } from position { $old_pos } to { $new_pos }, a distance of { $distance } spaces.
pirates-push-brief = { $attacker } rams { $defender } to position { $position }.
pirates-steal-rolls-you = Your theft total is { $steal}; { $target }'s guard total is { $defend}.
pirates-steal-rolls-you-brief = Theft { $steal}; guard { $defend}.
pirates-steal-rolls-defender = { $attacker }'s theft total is { $steal}; your guard total is { $defend}.
pirates-steal-rolls-defender-brief = Theft { $steal}; your guard { $defend}.
pirates-steal-rolls-observer = { $attacker } attempts to steal from { $defender}: theft { $steal}, guard { $defend}.
pirates-steal-rolls-observer-brief = { $attacker } steals at { $steal } against { $defender } at { $defend}.
pirates-steal-success-you = You steal the { $gem } from { $target }. Your cargo is worth { $attacker_score } points; { GENDER_TERM($target_gender, "possessive-pronoun") } is worth { $defender_score}.
pirates-steal-success-you-brief = You steal the { $gem } from { $target }.
pirates-steal-success-them = { $attacker } steals your { $gem }. { GENDER_TERM($attacker_gender, "possessive-determiner-capitalized") } cargo is worth { $attacker_score } points; yours is worth { $defender_score}.
pirates-steal-success-them-brief = { $attacker } steals your { $gem }.
pirates-steal-success = { $attacker } steals the { $gem } from { $defender }. Their cargo values are now { $attacker_score } and { $defender_score } points respectively.
pirates-steal-success-brief = { $attacker } steals the { $gem } from { $defender }.
pirates-steal-failed-you = Your theft total of { $steal } does not beat { $target }'s guard total of { $defend}. You steal nothing.
pirates-steal-failed-you-brief = Your theft fails, { $steal } to { $defend}.
pirates-steal-failed-defender = You stop { $attacker }'s theft, { $defend } to { $steal}, and keep your cargo.
pirates-steal-failed-defender-brief = You stop { $attacker }'s theft.
pirates-steal-failed = { $defender } stops { $attacker }'s theft, { $defend } to { $steal}.
pirates-steal-failed-brief = { $attacker } fails to steal from { $defender }.
pirates-steal-no-gems-you = You cannot steal from { $target } because { GENDER_TERM($target_gender, "possessive-determiner") } ship carries no gems. Choose a push instead.
pirates-steal-no-gems-you-brief = { $target } has no gem to steal.
pirates-steal-no-gems-defender = { $attacker } cannot steal from you because your cargo contains no gems.
pirates-steal-no-gems-defender-brief = You have no gem for { $attacker } to steal.
pirates-steal-no-gems = { $attacker } cannot steal from { $defender } because the defender carries no gems.
pirates-steal-no-gems-brief = { $defender } has no gem to steal.

# Skills and skill state
pirates-use-skill = Use a skill
pirates-select-skill = Choose an unlocked skill
pirates-unknown-skill = Unknown skill
pirates-skill-error = { $message }
pirates-skill-selection-stale = That skill selection is no longer available at your current level or game state. Reopen the skill menu and choose an available skill.
pirates-req-level = { $skill } requires level { $required}; you are level { $current}.
pirates-requires-level = { $action ->
    [move_2] Sailing two spaces
    [move_3] Sailing three spaces
   *[other] That action
} requires level { $required}; you are level { $current}.
pirates-skill-cooldown = { $name } is recovering for { $turns } more of your turns.
pirates-skill-active = { $name } is already active for { $turns } more of your turns.
pirates-skill-already-activated-this-turn = You already activated a combat buff this turn. Take a movement or cannon action next.
pirates-skill-no-uses = Gem Seeker has no uses remaining this game.
pirates-skill-no-gems = Gem Seeker cannot find a target because no uncollected gems remain.
pirates-skill-no-targets = No rival ship is within the current { $range }-space range for this skill.
pirates-skill-incompatible = { $skill } cannot be activated while { $active } is active. Wait for the current effect to expire.
pirates-battleship-after-buff = Battleship cannot be launched after activating a combat buff this turn. Use the buff with a normal cannon shot, or wait until your next turn.
pirates-menu-active = { $name } (active for { $turns } more turns)
pirates-menu-cooldown = { $name } (recovering for { $turns } more turns)
pirates-menu-activate = Activate { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } uses remaining)
pirates-active-skill-status = { $skill }, { $turns } turns remaining
pirates-no-active-skills = none
pirates-skill-activated = { $player } activates { $skill}. { $effect }
pirates-skill-activated-brief = { $player } activates { $skill}.
pirates-buff-expired-you = Your { $skill } effect expires before this turn begins.
pirates-buff-expired-you-brief = Your { $skill } expires.
pirates-buff-expired = { $player }'s { $skill } effect expires before { GENDER_TERM($player_gender, "possessive-determiner") } turn begins.
pirates-buff-expired-brief = { $player }'s { $skill } expires.

pirates-skill-instinct-name = Sailor's Instinct
pirates-skill-instinct-desc = Review every five-space sector, including uncollected gems and rival ships. This information action does not end the turn.
pirates-instinct-header = Sailor's Instinct chart, divided into eight sectors:
pirates-instinct-sector = Sector { $sector}, positions { $start } through { $end}: { $gems } { $gems ->
    [one] uncollected gem
   *[other] uncollected gems
}, { $players } rival { $players ->
    [one] ship
   *[other] ships
}.

pirates-skill-portal-name = Portal
pirates-skill-portal-desc = Choose a different rival-occupied ocean, or choose Random to teleport to any space on the map. Cooldown: 3 of your turns.
pirates-resolve-portal = Choose Portal destination
pirates-select-portal-ocean = Choose a different rival-occupied ocean, or choose Random for any map space
pirates-portal-option = { $ocean }; ships: { $ships}; { $gems } uncollected { $gems ->
    [one] gem
   *[other] gems
}
pirates-portal-option-random = Random map space
pirates-portal-option-unavailable = That ocean is not a valid Portal destination because it is your current ocean or no rival ship occupies it. Choose another destination.
pirates-must-resolve-portal = Because you used Portal, your turn is locked into that skill. Choose a destination, or choose Random, to complete the Portal and end your turn.
pirates-no-pending-portal = There is no pending Portal destination for you to resolve.
pirates-portal-no-ships = No specific rival-ocean Portal destination is available, but Random can still send you to any map space.
pirates-portal-fizzle-you = Your Portal destination is no longer valid. Choose Random to teleport anywhere on the map, or choose another valid destination.
pirates-portal-fizzle-you-brief = Choose Random or another valid Portal destination.
pirates-portal-fizzle = { $player }'s Portal destination is no longer valid.
pirates-portal-fizzle-brief = { $player } must choose another Portal destination.
pirates-portal-success-you = You travel through the Portal to { $ocean}, arriving at position { $position}. Portal enters cooldown for 3 of your turns.
pirates-portal-success-you-brief = You portal to position { $position } in { $ocean}.
pirates-portal-success = { $player } travels through a Portal to { $ocean}, arriving at position { $position}.
pirates-portal-success-brief = { $player } portals to position { $position}.

pirates-skill-seeker-name = Gem Seeker
pirates-skill-seeker-desc = Reveal the exact position of one uncollected gem. Three uses per game; using it does not end the turn.
pirates-gem-seeker-reveal = Gem Seeker locates the { $gem } at position { $position}. You have { $uses } uses remaining this game.

pirates-skill-sword-name = Sword Fighter
pirates-skill-sword-desc = Gain +2 attack for 3 of your turns. Cooldown: 6 turns. Cannot overlap Skilled Captain.
pirates-sword-fighter-activated = You activate Sword Fighter: +{ $bonus } attack for { $turns } of your turns. Cooldown: { $cooldown } turns. You may still move or fire this turn.
pirates-sword-fighter-activated-brief = Sword Fighter active: +{ $bonus } attack.

pirates-skill-push-name = Ramming Speed
pirates-skill-push-desc = Add 2 spaces to boarding pushes for 3 of your turns. Cooldown: 6 turns.
pirates-push-activated = You activate Ramming Speed: +{ $bonus } spaces to boarding pushes for { $turns } of your turns. Cooldown: { $cooldown } turns. You may still move or fire this turn.
pirates-push-activated-brief = Ramming Speed active: +{ $bonus } push distance.

pirates-skill-captain-name = Skilled Captain
pirates-skill-captain-desc = Gain +1 attack and +1 defense for 4 of your turns. Cooldown: 7 turns. Cannot overlap Sword Fighter.
pirates-skilled-captain-activated = You activate Skilled Captain: +{ $attack } attack and +{ $defense } defense for { $turns } of your turns. Cooldown: { $cooldown } turns. You may still move or fire this turn.
pirates-skilled-captain-activated-brief = Skilled Captain active: +{ $attack } attack, +{ $defense } defense.

pirates-skill-battleship-name = Battleship
pirates-skill-battleship-desc = Fire two crew-targeted cannon shots, without boarding rewards. This ends the turn. Cooldown: 4 turns.
pirates-battleship-activated = You launch Battleship for { $shots } cannon shots. Your crew selects the most valuable target in range for each shot; hits do not grant boarding. Cooldown: { $cooldown } turns.
pirates-battleship-activated-brief = You launch Battleship for { $shots } shots.
pirates-battleship-activated-player = { $player } launches Battleship for { $shots } cannon shots. Hits from these shots do not grant boarding.
pirates-battleship-activated-player-brief = { $player } launches Battleship.
pirates-battleship-shot = Your crew fires Battleship shot { $shot } at { $target}.
pirates-battleship-shot-brief = Shot { $shot } at { $target}.
pirates-battleship-shot-player = { $player }'s crew fires Battleship shot { $shot } at { $target}.
pirates-battleship-shot-player-brief = { $player } fires at { $target}.
pirates-battleship-no-targets = Your crew cannot fire shot { $shot } because no rival remains within { $range } spaces. Battleship ends.
pirates-battleship-no-targets-brief = No target for shot { $shot}.
pirates-battleship-no-targets-player = { $player } cannot fire Battleship shot { $shot } because no rival remains within { $range } spaces.
pirates-battleship-no-targets-player-brief = { $player } has no target for shot { $shot}.

pirates-skill-devastation-name = Double Devastation
pirates-skill-devastation-desc = Increase normal cannon range from 5 to 10 spaces for 3 of your turns. Cooldown: 10 turns. Incompatible with Battleship.
pirates-double-devastation-activated = You activate Double Devastation: cannon range becomes { $range } spaces for { $turns } of your turns. Cooldown: { $cooldown } turns. You may still move or fire this turn.
pirates-double-devastation-activated-brief = Double Devastation active: range { $range}.

# Options and validation
pirates-set-combat-xp-multiplier = Combat XP multiplier: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Enter a combat XP multiplier from 0.1 to 3.0
pirates-option-changed-combat-xp = Combat XP multiplier set to { $combat_multiplier}.
pirates-desc-combat-xp-multiplier = Scales XP from cannon hits and successful defenses. The Golden Moon multiplier is applied separately (default 1.0, range 0.1-3.0).
pirates-set-find-gem-xp-multiplier = Gem recovery XP multiplier: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Enter a gem recovery XP multiplier from 0.1 to 3.0
pirates-option-changed-find-gem-xp = Gem recovery XP multiplier set to { $find_gem_multiplier}.
pirates-desc-find-gem-xp-multiplier = Scales XP awarded when a ship recovers a gem, including after forced movement (default 1.0, range 0.1-3.0).
pirates-set-gem-stealing = Gem stealing: { $mode }
pirates-select-gem-stealing = Choose how boarding theft rolls use combat bonuses
pirates-option-changed-stealing = Gem stealing set to { $mode}.
pirates-desc-gem-stealing = Controls whether gem theft is available after a direct hit and whether active attack and defense bonuses modify the theft roll.
pirates-stealing-with-bonus = Enabled with combat bonuses
pirates-stealing-no-bonus = Enabled without combat bonuses
pirates-stealing-disabled = Disabled; boarding can only push
pirates-error-combat-xp-range = The combat XP multiplier is { $value}, outside the supported range of { $min } to { $max}. Set it within that range before starting.
pirates-error-gem-xp-range = The gem recovery XP multiplier is { $value}, outside the supported range of { $min } to { $max}. Set it within that range before starting.
pirates-error-stealing-mode = The stored gem stealing mode, { $mode}, is unsupported. Choose one of the listed gem stealing modes before starting.

# Ocean names
pirates-ocean-rory = Rory's Ocean
pirates-ocean-dev = Developer's Deep
pirates-ocean-par = Programmer's Paradise Sea
pirates-ocean-pal = Palace Waters
pirates-ocean-sil = Silva's Strait
pirates-ocean-kai = Kai's Current
pirates-ocean-gam = Gamer's Gulf
pirates-ocean-ser = Server Room Sea
pirates-ocean-bat = Battle Bay
pirates-ocean-cod = Code Compilation Channel
pirates-ocean-unknown = Unknown Ocean

# Gem names
pirates-gem-0 = opal
pirates-gem-1 = ruby
pirates-gem-2 = garnet
pirates-gem-3 = diamond
pirates-gem-4 = sapphire
pirates-gem-5 = emerald
pirates-gem-6 = gem of the palace
pirates-gem-7 = large plastic gem
pirates-gem-8 = awesome blue bastardstone
pirates-gem-9 = amethyst
pirates-gem-10 = golden ring
pirates-gem-11 = awesome red ppulpstone
pirates-gem-12 = awesome red gorestone
pirates-gem-13 = moonstone
pirates-gem-14 = lapis lazuli
pirates-gem-15 = amber
pirates-gem-16 = citrine
pirates-gem-17 = definitely not cursed black pearl (tm)
pirates-gem-unknown = unknown gem
pirates-gem-none = no gems
