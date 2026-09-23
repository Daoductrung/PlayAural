game-name-breachpoint = Breach Point

# Options
breachpoint-set-match-format = Match format: { $format }
breachpoint-select-match-format = Select the Counter-Strike match format
breachpoint-option-changed-match-format = Match format set to { $format }.
breachpoint-desc-match-format = Sets the maximum regulation rounds per half and the score needed to win: 8 for MR7, 13 for MR12, or 16 for MR15.
breachpoint-match-format-mr7 = MR7, first to 8 rounds
breachpoint-match-format-mr12 = MR12, first to 13 rounds
breachpoint-match-format-mr15 = MR15, first to 16 rounds
breachpoint-set-overtime-mode = Tied match resolution: { $mode }
breachpoint-select-overtime-mode = Select how a regulation tie is resolved
breachpoint-option-changed-overtime-mode = Tied match resolution set to { $mode }.
breachpoint-desc-overtime-mode = Chooses whether a tied regulation match ends in a draw or continues through repeatable MR3 overtime periods.
breachpoint-overtime-draw = End in a draw
breachpoint-overtime-mr3 = Repeat MR3 overtime until one squad wins

# Setup validation
breachpoint-error-even-teams = Breach Point requires two equal teams. There are currently { $players } active players; use 4, 6, 8, or 10.
breachpoint-error-match-format = Match format { $format } is unavailable. Select MR7, MR12, or MR15.
breachpoint-error-overtime-mode = Overtime mode { $mode } is unavailable. Select a registered tie resolution.
breachpoint-error-map-unavailable = Tactical map { $map } is unavailable. Select a registered map before starting.

# Teams and map
breachpoint-team-terrorists = T
breachpoint-team-counter-terrorists = CT
breachpoint-map-dust = Dust
breachpoint-node-t-spawn = T Spawn
breachpoint-node-outside-long = Outside Long
breachpoint-node-long-doors = Long Doors
breachpoint-node-pit = Pit
breachpoint-node-a-long = A Long
breachpoint-node-a-ramp = A Ramp
breachpoint-node-a-site = Bombsite A
breachpoint-node-mid = Mid
breachpoint-node-catwalk = Catwalk
breachpoint-node-a-short = A Short
breachpoint-node-mid-doors = Mid Doors
breachpoint-node-ct-mid = CT Mid
breachpoint-node-ct-spawn = CT Spawn
breachpoint-node-outside-tunnels = Outside Tunnels
breachpoint-node-upper-tunnels = Upper Tunnels
breachpoint-node-lower-tunnels = Lower Tunnels
breachpoint-node-b-tunnels = B Tunnels
breachpoint-node-b-doors = B Doors
breachpoint-node-b-site = Bombsite B
breachpoint-node-unknown = Unknown area

# Dust spatial descriptions and terrain
breachpoint-area-t-spawn-description = Three routes leave this sunken courtyard: Long, Mid, and the tunnel approach.
breachpoint-area-outside-long-description = An open yard funnels into Long Doors, where the route narrows sharply.
breachpoint-area-long-doors-description = Heavy double doors split the cramped stone gateway from the exposed street beyond.
breachpoint-area-pit-description = This low pocket at the end of Long offers cover and a clean view toward A.
breachpoint-area-a-long-description = A broad street runs uphill toward A Ramp, with little shelter between firing positions.
breachpoint-area-a-ramp-description = The street rises here and opens onto A, making this the final commitment from Long.
breachpoint-area-a-site-description = The raised site is open around its bomb crates, with approaches from Long, Short, and CT Spawn.
breachpoint-area-mid-description = Dust opens up here: Catwalk climbs toward A, Mid Doors lead toward CT, and Lower Tunnels branch toward B.
breachpoint-area-catwalk-description = This raised ledge leaves Mid and bends toward the tighter Short A approach.
breachpoint-area-a-short-description = A narrow high route overlooks A and the CT rotation below.
breachpoint-area-mid-doors-description = The double doors frame Dust's longest central duel between Mid and CT territory.
breachpoint-area-ct-mid-description = This junction joins Mid Doors, B Doors, and the CT rotation route.
breachpoint-area-ct-spawn-description = CT Spawn is the main rotation hub, with quick routes toward A, B, and Mid.
breachpoint-area-outside-tunnels-description = A sheltered yard gives T a last place to gather before entering the tunnels.
breachpoint-area-upper-tunnels-description = The broad upper chamber forks toward B or drops through Lower Tunnels into Mid.
breachpoint-area-lower-tunnels-description = This tight underground branch links the tunnel system to Mid.
breachpoint-area-b-tunnels-description = The tunnel narrows into a dangerous exit directly onto B.
breachpoint-area-b-doors-description = These doors connect B to CT Mid and the defender rotation.
breachpoint-area-b-site-description = The enclosed site wraps around a raised platform and stacked crates, with entrances from Tunnels and B Doors.
breachpoint-terrain-supply-crates = stacked supply crates
breachpoint-terrain-double-doors = heavy double doors
breachpoint-terrain-stone-pit-wall = the low Pit wall
breachpoint-terrain-disabled-car = a disabled car
breachpoint-terrain-ramp-boxes = ramp boxes
breachpoint-terrain-bomb-crates = bomb crates
breachpoint-terrain-goose-wall = the Goose wall
breachpoint-terrain-xbox = the central Xbox crate
breachpoint-terrain-catwalk-wall = the low Catwalk wall
breachpoint-terrain-short-boxes = Short boxes
breachpoint-terrain-ct-boxes = CT cover boxes
breachpoint-terrain-tunnel-pillars = thick tunnel pillars
breachpoint-terrain-tunnel-corner = the blind tunnel corner
breachpoint-terrain-tunnel-crates = tunnel crates
breachpoint-terrain-b-platform = the raised B platform

# Turn actions
breachpoint-weapon-none = no weapon
breachpoint-weapon-glock = Glock
breachpoint-weapon-usp-s = USP-S
breachpoint-weapon-desert-eagle = Desert Eagle
breachpoint-weapon-mac10 = MAC-10
breachpoint-weapon-mp9 = MP9
breachpoint-weapon-nova = Nova
breachpoint-weapon-galil-ar = Galil AR
breachpoint-weapon-famas = FAMAS
breachpoint-weapon-ssg08 = SSG 08
breachpoint-weapon-ak47 = AK-47
breachpoint-weapon-m4 = M4
breachpoint-weapon-awp = AWP
breachpoint-armor-kevlar = Kevlar
breachpoint-equipment-none = no equipment
breachpoint-equipment-defuse-kit = Defuse Kit
breachpoint-utility-none = no utility
breachpoint-utility-smoke = Smoke Grenade
breachpoint-utility-flashbang = Flashbang
breachpoint-utility-he-grenade = HE Grenade
breachpoint-utility-molotov = Molotov
breachpoint-utility-incendiary-grenade = Incendiary Grenade
breachpoint-utility-count = { $utility } x{ $count }
breachpoint-ammo-none = no ammunition
breachpoint-ammo-unit-magazine =
    { $count ->
        [one] magazine
       *[other] magazines
    }
breachpoint-ammo-unit-shell =
    { $count ->
        [one] shell
       *[other] shells
    }
breachpoint-ammo-status = { $loaded } of { $capacity } loaded; { $reserve } reserve { $unit }
breachpoint-action-buy-weapon = Buy { $weapon } for ${ $cost }; balance ${ $cash }
breachpoint-action-buy-utility = Buy { $utility } for ${ $cost }; carrying { $count } of { $maximum }; balance ${ $cash }
breachpoint-action-buy-armor = Buy { $armor } for ${ $cost }; balance ${ $cash }
breachpoint-action-buy-equipment = Buy { $equipment } for ${ $cost }; balance ${ $cash }
breachpoint-action-donate-weapon = Buy { $weapon } for { $player }: ${ $cost }; balance ${ $cash }
breachpoint-action-accept-donation = Accept { $weapon } from { $player }
breachpoint-action-decline-donation = Decline { $weapon } from { $player }
breachpoint-action-refund-item = Refund { $item }, you have { $count }; recover ${ $amount }; balance ${ $cash }
breachpoint-action-finish-buy = Finish buying; save ${ $cash }
breachpoint-buy-summary = Loadout summary: ${ $cash }; equipped { $equipped }; primary { $primary }; armor { $armor }; { $utility } grenades
breachpoint-buy-check-teammates = Check teammate money and equipment
breachpoint-buy-ground-weapons = Ground weapons
breachpoint-buy-refunds = Refund purchases
breachpoint-buy-for-teammate = Buy for a teammate
breachpoint-buy-category-equipment = Equipment
breachpoint-buy-category-pistols = Pistols
breachpoint-buy-category-mid-tier = Mid-Tier
breachpoint-buy-category-rifles = Rifles
breachpoint-buy-category-grenades = Grenades
breachpoint-buy-category-unknown = Unavailable category
breachpoint-buy-shortcut-label = { $number }. { $item }
breachpoint-buy-donation-target = Buy for { $player }
breachpoint-buy-no-refunds = No refundable purchases
breachpoint-error-no-ground-weapons = There are no weapons on the ground here.
breachpoint-buy-donation-waiting = Waiting for { $player } to accept or decline { $weapon }
breachpoint-buy-back = Back to the previous buy menu
breachpoint-action-equip-weapon = Equip { $weapon }
breachpoint-action-reload = Reload { $weapon }, { $ammunition } ({ $cost } AP)
breachpoint-action-reload-keybind = Reload equipped weapon
breachpoint-action-pick-up-weapon = Pick up { $weapon }, { $ammunition } ({ $cost } AP)
breachpoint-action-exchange-weapon = Exchange { $replaced } for { $weapon }, { $ammunition } ({ $cost } AP)
breachpoint-action-buy-pick-up-weapon = Pick up { $weapon }, { $ammunition }; free during your buy
breachpoint-action-buy-exchange-weapon = Exchange { $replaced } for { $weapon }, { $ammunition }; free during your buy
breachpoint-action-hold-angle = Hold a { $weapon } angle toward { $location } ({ $cost } AP; ends activation)
breachpoint-action-throw-utility = Throw { $utility } at { $location } ({ $cost } AP; { $count } carried)
breachpoint-action-move = Move to { $location } ({ $cost } AP)
breachpoint-action-disengage = Disengage to { $location } ({ $cost } AP; ends activation)
breachpoint-action-move-fire = Move into fire at { $location } ({ $cost } AP; take fire damage)
breachpoint-action-disengage-fire = Disengage into fire at { $location } ({ $cost } AP; take fire damage; ends activation)
breachpoint-action-shoot = Shoot { $player } with { $weapon } at { $location }, { $health } health, { $armor } armor, { $guard } evasion, { $ammunition }, { $strength } ({ $cost } AP)
breachpoint-action-shoot-unavailable = Shoot unavailable target
breachpoint-shot-strength-full = full strength
breachpoint-shot-strength-followup = recoil-limited to { $percent } percent damage
breachpoint-action-plant = Begin planting the bomb ({ $cost } AP)
breachpoint-action-defuse = Defuse the bomb ({ $cost } AP)
breachpoint-action-pickup = Pick up the bomb ({ $cost } AP)
breachpoint-action-end-turn = End activation; prepare { $guard } evasion
breachpoint-action-skip-round-recovery = Skip weapon recovery and end the round
breachpoint-action-reaction-shoot = Fire the held { $weapon } at { $player } in { $location } ({ $percent } percent damage)
breachpoint-action-reaction-pass = Hold fire and keep the angle
breachpoint-keybind-finish-or-end = Finish buying or end activation
breachpoint-keybind-buy-shortcut = Buy menu shortcut { $number }
breachpoint-keybind-menu-back = Return to the previous game menu

# Combat menu
breachpoint-combat-summary = HP { $health }; equipped { $weapon }; in sight: { $sight }
breachpoint-combat-summary-enemy = { $player } at { $location }, enemy
breachpoint-combat-summary-teammate = { $player } at { $location }, teammate
breachpoint-combat-summary-no-contacts = no contacts
breachpoint-combat-menu-move = Move
breachpoint-combat-menu-attack = Attack ({ $count } visible)
breachpoint-combat-menu-utility = Use utility ({ $count } carried)
breachpoint-combat-menu-angle = Hold angle
breachpoint-combat-menu-objective = Objective
breachpoint-combat-menu-weapons = Weapons and reload
breachpoint-combat-menu-loot = Ground weapons ({ $count } here)
breachpoint-combat-menu-utility-choice = { $utility } ({ $count } carried)
breachpoint-combat-menu-back = Back to combat actions
breachpoint-combat-menu-unavailable = Combat action unavailable
breachpoint-combat-menu-empty-move = There are no connected areas to move to.
breachpoint-combat-menu-empty-attack = You cannot currently see a living enemy.
breachpoint-combat-menu-empty-utility = You are not carrying any utility.
breachpoint-combat-menu-empty-targets = This utility has no legal target area from here.
breachpoint-combat-menu-empty-angle = Your equipped weapon cannot hold an angle from here.
breachpoint-combat-menu-empty-objective = Your side has no objective action.
breachpoint-combat-menu-empty-weapons = You have no weapon action available.
breachpoint-combat-menu-empty-loot = There are no eligible weapons on the ground here.
breachpoint-current-location = [current location]
breachpoint-visible-contact-enemy = { $player }, enemy
breachpoint-visible-contact-teammate = { $player }, teammate
breachpoint-visible-contacts = visible here: { $contacts }
breachpoint-action-spatial-details = { $action } — { $details }

# Information actions
breachpoint-action-read-vitals = Read health and armor
breachpoint-action-read-position = Read your loadout and tactical status
breachpoint-action-read-map = Read tactical map
breachpoint-action-read-teammates = Read teammate status
breachpoint-action-read-enemies = Read known enemy status
breachpoint-action-read-bomb = Read bomb status

# Action errors
breachpoint-error-spectator-action = Spectators cannot perform tactical actions. Use the map, team, bomb, and score actions to follow the match.
breachpoint-error-eliminated-action = You have been eliminated for this combat round. You will return when the next combat round begins.
breachpoint-error-reaction-unavailable = There is no held-angle reaction to resolve.
breachpoint-error-reaction-player = Wait for { $player } to resolve the held-angle reaction.
breachpoint-error-reaction-action-only = Resolve the held-angle shot or hold fire before taking normal actions.
breachpoint-error-wait-reaction-response = Wait for { $player } to resolve the reaction before continuing your activation.
breachpoint-error-reaction-expired = The watched entry is no longer a valid shot. Hold fire to resume play.
breachpoint-error-buy-phase-active = The buy phase is still active. Finish your loadout before performing combat actions.
breachpoint-error-buy-phase-ended = Buying is closed for this combat round.
breachpoint-error-wait-movement-you = You are moving to { $location }. Wait until you arrive.
breachpoint-error-wait-movement-player = { $player } is moving to { $location }. Wait until they arrive.
breachpoint-error-wait-movement-hidden = { $player } is moving. Wait until they arrive.
breachpoint-error-wait-utility-you = Your { $utility } is still in flight. Wait for it to land.
breachpoint-error-wait-utility-player = { $player }'s { $utility } is still in flight. Wait for it to land.
breachpoint-error-wait-weapon-you = You are firing { $weapon }. Wait for the final shot.
breachpoint-error-wait-weapon-player = { $player } is firing { $weapon }. Wait for the final shot.
breachpoint-error-wait-next-round = The next combat round begins in { $seconds } { $seconds ->
    [one] second
   *[other] seconds
}. The battlefield is being reset.
breachpoint-error-wait-buy-countdown = Combat begins in { $seconds } { $seconds ->
    [one] second
   *[other] seconds
}. Wait for the buy countdown to finish.
breachpoint-error-wait-match-result = Match results appear in { $seconds } { $seconds ->
    [one] second
   *[other] seconds
}. The final round result is still playing.
breachpoint-error-wait-bomb-detonation = The bomb's final arming sequence ends in { $seconds } { $seconds ->
    [one] second
   *[other] seconds
}. It is too late to defuse.
breachpoint-error-wait-event = A tactical event is still resolving. Wait for it to finish before acting.
breachpoint-error-round-recovery-unavailable = There is no post-round weapon recovery to resolve.
breachpoint-error-round-recovery-player = Wait for { $player } to recover a weapon or skip.
breachpoint-error-round-recovery-only = The final enemy is down. Pick up one offered weapon here or skip to end the round.
breachpoint-error-not-your-buy-turn = Wait for { $player } to finish buying.
breachpoint-error-weapon-unavailable = That weapon is not available for your current side and loadout.
breachpoint-error-donation-unavailable = That teammate weapon offer is no longer available. Return to the current buy choices.
breachpoint-error-donation-response-only = Respond to the weapon offer before taking another buy action.
breachpoint-error-donation-response-player = Wait for { $player } to accept or decline the weapon offer.
breachpoint-error-buy-category-unavailable = That buy category is not available from the current menu. Return to the previous buy menu and choose again.
breachpoint-error-no-refundable-purchases = You have no refundable purchases from this buy turn.
breachpoint-error-no-eligible-donation-teammates = No active teammate can receive a weapon offer right now.
breachpoint-error-armor-owned = You already have full Kevlar protection.
breachpoint-error-equipment-unavailable = That equipment is not available for your current side.
breachpoint-error-equipment-full = You are already carrying the maximum of { $maximum } for that equipment.
breachpoint-error-not-enough-cash = This purchase costs ${ $cost }, but you have ${ $cash }. Finish buying to save your cash.
breachpoint-error-no-primary = You do not have a primary weapon to equip.
breachpoint-error-weapon-equipped = That weapon is already equipped.
breachpoint-error-dropped-weapon-unavailable = That dropped weapon is no longer available in your area. Choose another action.
breachpoint-error-weapon-empty = Your { $weapon } is empty. Reload it or equip another weapon before firing or holding an angle.
breachpoint-error-no-ammunition = Your { $weapon } is empty and has no reserve ammunition. Equip another weapon before firing or holding an angle.
breachpoint-error-magazine-full = Your { $weapon } is already fully loaded.
breachpoint-error-no-reserve-ammo = Your { $weapon } has no reserve ammunition. Equip another weapon or conserve the rounds still loaded.
breachpoint-error-utility-unavailable = That utility item is not available for your current side.
breachpoint-error-utility-full = You are already carrying the maximum of { $maximum } for that utility item.
breachpoint-error-utility-total-full = You are carrying the maximum of { $maximum } utility items. Use an item before buying another.
breachpoint-error-utility-empty = You are not carrying that utility item. Buy one during a later buy phase.
breachpoint-error-utility-range = That area is beyond the utility's { $range }-area throw range. Choose your current area or a connected area.
breachpoint-error-smoke-active = Smoke already covers that area. Wait for it to clear or choose another area.
breachpoint-error-fire-active = Fire already covers that area. Wait for it to burn out, extinguish it with smoke, or choose another area.
breachpoint-error-hold-unavailable = Your equipped weapon cannot prepare a held angle.
breachpoint-error-illegal-angle = Your equipped weapon cannot hold that firing lane from your current area.
breachpoint-error-angle-held = You are already holding that angle. End your activation to keep it prepared.
breachpoint-error-hold-after-firing = You already fired during this activation. Holding an angle requires a movement-or-setup activation with no shots fired.
breachpoint-error-aim-required = Your { $weapon } is not prepared for { $player }'s area. Hold that angle during an earlier activation.
breachpoint-error-target-already-fired = Your { $weapon } has already fired at { $player } this activation. Choose another visible target or end your activation.
breachpoint-error-not-your-turn = It is not your activation. Wait for { $player } to finish.
breachpoint-error-not-enough-ap = This action needs { $needed } action points, but you have { $remaining } remaining. Choose a cheaper action or end your activation.
breachpoint-error-illegal-move = That area is not connected to your current position. Choose one of the movement actions currently shown.
breachpoint-error-enemy-blocks-move = { $player } is holding { $location }. You cannot move into an area occupied by a living enemy; shoot from your current line of sight or choose another route.
breachpoint-error-concealed-blocks-move = Movement is blocked, but smoke prevents you from identifying who is there. Choose another route or wait until you have a clear view.
breachpoint-error-target-unavailable = That target is no longer available. Review your visible contacts and choose a living enemy.
breachpoint-error-friendly-fire = Friendly fire is disabled. Choose a player on the opposing team.
breachpoint-error-target-eliminated = { $player } has already been eliminated from this combat round. Choose a living enemy.
breachpoint-error-no-line-of-sight = You do not have line of sight to { $player } from your current area. Move to a connected firing angle first.
breachpoint-error-target-out-of-range = { $player } is beyond the { $range }-area range of your { $weapon }. Move closer or equip another weapon.
breachpoint-error-already-fired = Your equipped weapon has no shots remaining this activation. Switch weapons, move, handle the objective, or end your activation.
breachpoint-error-terrorists-only = Only T can perform that bomb action.
breachpoint-error-counter-terrorists-only = Only CT can defuse the bomb.
breachpoint-error-not-carrying-bomb = You are not carrying the bomb. Find the carrier or recover the dropped bomb.
breachpoint-error-not-at-bomb-site = You can plant only at Bombsite A or Bombsite B. Move to a bombsite with at least 1 action point remaining.
breachpoint-error-bomb-not-planted = The bomb has not been planted, so it cannot be defused.
breachpoint-error-not-at-planted-bomb = You must be in the area containing the planted bomb before starting a defuse.
breachpoint-error-defuse-in-progress = A CT player is already defusing. Protect the defuser until T's response ends.
breachpoint-error-bomb-not-dropped = The bomb is not currently on the ground.
breachpoint-error-not-at-dropped-bomb = Move into the area containing the dropped bomb before trying to pick it up.

# Match and round flow
breachpoint-match-start-player = Breach Point begins on { $map } in { $format }. You start as { $team } at { $location }. Each combat round allows { $tactical_rounds } pre-plant tactical rounds.
breachpoint-match-start-spectator = Breach Point begins on { $map } in { $format }. Each combat round allows { $tactical_rounds } pre-plant tactical rounds. Enemy positions are concealed from spectators.
breachpoint-combat-round-start = Combat round { $round }. { $team_one } { $team_one_score }, { $team_two } { $team_two_score }.
breachpoint-bomb-assigned-you = You carry the bomb this combat round.
breachpoint-bomb-assigned-teammate = { $player } carries the bomb this combat round.
breachpoint-buy-phase-start = Buy phase for combat round { $round }.
breachpoint-buy-countdown-start = All ready. Combat begins.
breachpoint-buy-turn = Your buy turn. You have ${ $cash }.
breachpoint-buy-detail-cash = Money: ${ $cash }
breachpoint-buy-detail-primary = Primary: { $weapon }. { $ammunition }
breachpoint-buy-detail-sidearm = Sidearm: { $weapon }. { $ammunition }
breachpoint-buy-detail-equipped = Equipped: { $weapon }
breachpoint-buy-detail-armor = Armor: { $armor } of { $maximum }
breachpoint-buy-detail-equipment = Equipment: { $equipment }
breachpoint-buy-detail-utility = Grenades: { $utility }
breachpoint-buy-teammate-line = { $player }: ${ $cash }; primary { $primary }; sidearm { $sidearm }; armor { $armor }; equipment { $equipment }; grenades { $utility }
breachpoint-buy-no-teammates = You have no teammates in this match.
breachpoint-buy-weapon-complete = Bought and equipped { $weapon }. ${ $cash } remains.
breachpoint-buy-utility-complete = Bought { $utility }. Carrying { $count } of { $maximum }; ${ $cash } remains.
breachpoint-buy-armor-complete = Bought { $armor_name }. Armor: { $armor }; ${ $cash } remains.
breachpoint-buy-equipment-complete = Bought { $equipment }. ${ $cash } remains.
breachpoint-donation-offered-buyer = You bought { $weapon } for { $player }. Waiting for their answer; ${ $cash } remains.
breachpoint-donation-offered-recipient = { $player } bought { $weapon } for you. Accept it or decline it so buying can continue.
breachpoint-donation-accepted-recipient = You accept { $weapon } from { $player } and equip it.
breachpoint-donation-accepted-buyer = { $player } accepts the { $weapon } you bought.
breachpoint-donation-declined-recipient = You decline { $weapon } from { $player }. It drops at the buyer's position.
breachpoint-donation-declined-buyer = { $player } declines { $weapon }. It drops at your position; you may refund it or leave it there.
breachpoint-refund-complete = Refunded { $item } for ${ $amount }. Your balance is ${ $cash }.
breachpoint-buy-finished-you = Loadout ready. You save ${ $cash }.
breachpoint-buy-finished-player = { $player } is ready.
breachpoint-round-recovery-you = Your side has secured the round. You may recover one of { $count } final-elimination { $count ->
    [one] weapon
   *[other] weapons
} here, or skip.
breachpoint-round-recovery-player = { $player } may recover one of { $count } final-elimination { $count ->
    [one] weapon
   *[other] weapons
} before the round ends.
breachpoint-round-recovery-skipped-you = You skip weapon recovery. The round ends.
breachpoint-round-recovery-skipped-player = { $player } skips weapon recovery. The round ends.
breachpoint-weapon-equipped = Equipped { $weapon }.
breachpoint-weapon-dropped-you = You drop { $weapon } at { $location }.
breachpoint-weapon-dropped-player = { $player } drops { $weapon } at { $location }.
breachpoint-error-refund-unavailable = { $item } cannot be refunded because it was not bought during this buy turn or is no longer available.
breachpoint-weapon-picked-up-you = You pick up { $weapon }. { $ammunition }. { $ap } AP remains.
breachpoint-buy-weapon-picked-up-you = You pick up { $weapon } during your buy. { $ammunition }.
breachpoint-weapon-picked-up-player = { $player } picks up { $weapon } at { $location }.
breachpoint-weapon-exchanged-you = You exchange { $replaced } for { $weapon }. { $ammunition }. { $ap } AP remains.
breachpoint-buy-weapon-exchanged-you = During your buy, you exchange { $replaced } for { $weapon }. { $ammunition }.
breachpoint-weapon-exchanged-player = { $player } exchanges { $replaced } for { $weapon } at { $location }.
breachpoint-reload-magazine-you = You reload { $weapon }, discarding { $discarded } loaded rounds. { $ammunition }.
breachpoint-reload-empty-magazine-you = You insert a fresh magazine into the empty { $weapon }. { $ammunition }.
breachpoint-reload-shells-you = You load { $loaded } shells into { $weapon }. { $ammunition }.
breachpoint-reload-player = { $player } reloads { $weapon }.
breachpoint-hold-angle-you = You hold a { $weapon } angle toward { $location }. Your activation ends.
breachpoint-hold-angle-player = { $player } holds a { $weapon } angle toward { $location }.
breachpoint-round-income = Round income: ${ $amount }. Balance: ${ $cash }.
breachpoint-kill-reward = Elimination reward: ${ $amount }. Balance: ${ $cash }.
breachpoint-phase-preplant = Tactical round { $round } of { $limit }
breachpoint-phase-postplant-armed = Bomb planted; { $total } full tactical rounds remain
breachpoint-phase-postplant = Bomb planted { $round } of { $total }
breachpoint-tactical-round-start = { $phase }.
breachpoint-turn-you = Your turn. You have { $ap } AP.
breachpoint-turn-player = { $player }'s turn.
breachpoint-whose-turn-donation-you = Buying is waiting for you to accept or decline a teammate's weapon offer.
breachpoint-whose-turn-donation-player = Buying is waiting for { $player } to answer a weapon offer.
breachpoint-whose-turn-reaction-you = The game is waiting for your response.
breachpoint-whose-turn-reaction-player = The game is waiting for { $player }'s response.
breachpoint-whose-turn-recovery-you = The round is waiting for you to recover a dropped weapon or skip.
breachpoint-whose-turn-recovery-player = The round is waiting for { $player } to recover a dropped weapon or skip.
breachpoint-response-plant = plant response
breachpoint-response-defuse = defuse response
breachpoint-response-turn-you = Your { $response }. You have { $ap } AP.
breachpoint-response-turn-player = { $player } begins a { $response }.
breachpoint-watched-entry-you = Your held angle catches { $enemy } entering { $location }. Fire now or hold fire.
breachpoint-watched-entry-target = { $player } has you in a held angle at { $location }.
breachpoint-reaction-pass-you = You hold fire and keep the angle.
breachpoint-reaction-pass-target = { $player } holds fire.
breachpoint-watched-entry-resume = Your movement resumes with { $ap } AP.
breachpoint-sides-swapped = Sides swap. { $terrorists } are now T; { $counter_terrorists } are now CT.
breachpoint-halftime = Halftime is complete. The second regulation half begins.
breachpoint-overtime-starts = Regulation is tied. MR3 overtime period { $period } begins.
breachpoint-overtime-restarts = Overtime remains tied. MR3 overtime period { $period } begins.
breachpoint-combat-round-won-you = Your squad wins round { $round } as { $side }: { $reason }. { $score }
breachpoint-combat-round-won-other = { $squad } win round { $round } as { $side }: { $reason }. { $score }

# Movement and combat visibility
breachpoint-move-you = You move to { $destination }. { $ap } AP left.
breachpoint-move-player = { $player } moves to { $destination }. { $ap } AP left.
breachpoint-enemy-spotted = Contact: { $player } at { $location }.
breachpoint-enemy-moves-visible = { $player } moves to { $location }.
breachpoint-enemy-moves-hidden = { $player } moved.
breachpoint-enemy-lost = Contact lost: { $player }.
breachpoint-shot-result-evaded = no damage; every shot was evaded
breachpoint-shot-result-damage = { $health_damage } damage; shots landed: { $hits }
breachpoint-shot-result-damage-armor = { $health_damage } damage; shots landed: { $hits }; armor absorbed { $armor_absorbed }
breachpoint-shot-result-damage-evasion = { $health_damage } damage; shots landed: { $hits }; shots evaded: { $rounds_evaded }
breachpoint-shot-result-damage-armor-evasion = { $health_damage } damage; shots landed: { $hits }; armor absorbed { $armor_absorbed }; shots evaded: { $rounds_evaded }
breachpoint-shot-you = You fire at { $target } with { $weapon } at { $location }: { $result }.
breachpoint-shot-target = { $shooter } fires at you with { $weapon } at { $location }: { $result }.
breachpoint-shot-observer = { $shooter } fires at { $target } with { $weapon } at { $location }: { $result }.
breachpoint-shot-spectator = { $shooter } fires at { $target } with { $weapon }: { $result }.
breachpoint-elimination-you = You eliminate { $target } with { $weapon } at { $location }.
breachpoint-elimination-target = { $shooter } eliminates you with { $weapon } at { $location }.
breachpoint-elimination-observer = { $shooter } eliminates { $target } with { $weapon } at { $location }.
breachpoint-elimination-self-you = You eliminate yourself with { $weapon } at { $location }.
breachpoint-elimination-self-observer = { $shooter } eliminates themself with { $weapon } at { $location }.
breachpoint-end-turn-you = You end your activation with { $guard } evasion prepared against the next attack.
breachpoint-end-turn-player = { $player } ends their activation with { $guard } evasion prepared.
breachpoint-end-turn-no-evasion-you = You end your activation.
breachpoint-end-turn-no-evasion-player = { $player } ends their activation.

# Utility
breachpoint-utility-throw-you = You throw { $utility } at { $location }.
breachpoint-utility-throw-ally = { $player } throws { $utility } at { $location }.
breachpoint-utility-throw-enemy = Enemy utility: { $player } throws { $utility } at { $location }.
breachpoint-utility-throw-enemy-concealed = Enemy { $utility } at { $location }.
breachpoint-smoke-clears = Smoke clears at { $location }.
breachpoint-fire-burns-out = Fire burns out at { $location }.
breachpoint-fire-extinguished = Smoke extinguishes the fire at { $location }.
breachpoint-fire-suppressed = Smoke prevents the fire from igniting at { $location }.
breachpoint-flashed = You are flashed. Your next activation loses { $penalty } AP, and any prepared angle is broken.
breachpoint-flash-penalty-ap = Flash blindness costs { $penalty } AP. You begin with { $ap } AP.
breachpoint-utility-result-damage = { $health_damage } damage
breachpoint-utility-result-damage-armor = { $health_damage } damage; armor absorbed { $armor_absorbed }
breachpoint-utility-result-damage-evasion = { $health_damage } damage; evasion stopped { $evasion_mitigation }
breachpoint-utility-result-damage-armor-evasion = { $health_damage } damage; armor absorbed { $armor_absorbed }; evasion stopped { $evasion_mitigation }
breachpoint-utility-damage-you = Your { $utility } hits { $target } at { $location }: { $result }.
breachpoint-utility-damage-target = { $utility } hits you at { $location }: { $result }.
breachpoint-utility-damage-observer = { $utility } hits { $target } at { $location }: { $result }.

# Bomb flow
breachpoint-plant-start-you = Planting at { $location }. Your activation ends; CT has one response. Any hit interrupts.
breachpoint-plant-start-ally = { $player } is planting at { $location }. CT has one response.
breachpoint-plant-start-enemy = { $player } is planting at { $location }. Hit the planter during this response to interrupt.
breachpoint-plant-start-concealed = Plant attempt detected. CT has one response.
breachpoint-plant-completes-you = You planted at { $location }. Fuse: { $rounds } full tactical rounds. Plant reward: ${ $reward }; balance ${ $cash }.
breachpoint-plant-completes-player = { $player } planted at { $location }. Fuse: { $rounds } full tactical rounds.
breachpoint-plant-interrupted-you = You hit { $planter } and interrupt the plant.
breachpoint-plant-interrupted-target = { $player } hits you and interrupts your plant. You keep the bomb.
breachpoint-plant-interrupted-player = { $player } hits { $planter } and interrupts the plant.
breachpoint-defuse-start-you = You begin defusing at { $location } for { $cost } AP. Your activation ends; T has one response. Taking damage interrupts the defuse.
breachpoint-defuse-start-player = { $player } begins defusing at { $location }. T has one response.
breachpoint-defuse-complete-you = You defuse the bomb at { $location }. Defuse reward: ${ $reward }; balance ${ $cash }.
breachpoint-defuse-complete-player = { $player } defuses the bomb at { $location }.
breachpoint-defuse-interrupted-you = You damage { $defuser } and interrupt the defuse.
breachpoint-defuse-interrupted-target = { $player } damages you and interrupts your defuse.
breachpoint-defuse-interrupted-player = { $player } damages { $defuser } and interrupts the defuse.
breachpoint-pickup-you = You recover the dropped bomb. { $ap } action points remain.
breachpoint-pickup-player = { $player } recovers the dropped bomb. { $ap } action points remain.
breachpoint-pickup-enemy = { $player } recovers the dropped bomb at { $location }.
breachpoint-bomb-dropped = The bomb is dropped at { $location }.
breachpoint-bomb-countdown = Bomb fuse: { $rounds } full tactical rounds.
breachpoint-bomb-detonation-locked = The bomb has entered its final arming sequence. It is too late to defuse.
breachpoint-bomb-detonates = The bomb detonates at { $location }.

# Status and score
breachpoint-vitals-status = Health: { $health } of { $max_health }. Armor: { $armor }.
breachpoint-position-status = You are { $team } at { $location }. Primary: { $primary }. Sidearm: { $sidearm }. Equipped: { $equipped }. Ammunition: { $ammunition }. Ground weapons: { $ground }. Equipment: { $equipment }. Utility: { $utility }. Area effects: { $effects }. Cash: ${ $cash }. Action points: { $ap }. Evasion: { $guard }. Prepared angle: { $angle }.
breachpoint-angle-none = none
breachpoint-angle-held = toward { $location }
breachpoint-map-header = { $map }, combat round { $round }, { $phase }. Only your squad and enemies currently in team line of sight are shown.
breachpoint-map-bomb-site = bombsite
breachpoint-map-normal-area = normal area
breachpoint-map-empty = no visible occupants
breachpoint-ground-weapons-none = none
breachpoint-ground-weapons-unconfirmed = unconfirmed
breachpoint-ground-weapon-entry = { $weapon }, { $ammunition }
breachpoint-effect-smoke = smoke
breachpoint-effect-fire = fire
breachpoint-map-effects-active = active effects: { $effects }
breachpoint-map-effects-clear = clear of smoke and fire
breachpoint-map-effects-unconfirmed = no confirmed smoke or fire
breachpoint-map-spatial-context = You are at { $location }. { $description } Nearby terrain: { $terrain }. Clear firing lanes: { $sightlines }.
breachpoint-map-sightline-entry = { $location }, range { $range }
breachpoint-map-node-line = { $location }, { $site }, { $effect }. Visible occupants: { $occupants }. Ground weapons: { $ground }. Connected areas: { $exits }. Firing lanes: { $sightlines }.
breachpoint-map-occupant = { $player }, { $team }, { $health } health, { $state }
breachpoint-player-active = active
breachpoint-player-eliminated = eliminated this combat round
breachpoint-teammate-header = Teammates, currently { $team }: { $alive } of { $total } active
breachpoint-teammate-line = { $player }: { $location }, { $health } health, { $armor } armor, holding { $weapon }, ${ $cash }, { $state }
breachpoint-teammate-none = You have no teammates in this match.
breachpoint-enemy-header = Known enemies: { $known } of { $total }
breachpoint-enemy-line = { $player }: { $location }, { $health } health, { $armor } armor, { $state }
breachpoint-enemy-line-eliminated = { $player }: last seen at { $location }, eliminated this combat round
breachpoint-enemy-none = No enemy position is currently known.
breachpoint-bomb-status-carried = { $player } carries the bomb at { $location }.
breachpoint-bomb-status-planting = { $player } is planting the bomb at { $location }.
breachpoint-bomb-status-dropped = The bomb is dropped at { $location }.
breachpoint-bomb-status-planted = The bomb is planted at { $location } with { $rounds } complete tactical rounds remaining.
breachpoint-bomb-status-detonating = The bomb is in its final arming sequence at { $location }. It is too late to defuse.
breachpoint-bomb-status-defusing = { $player } is defusing at { $location }; T has one response. The fuse has { $rounds } complete tactical rounds remaining.
breachpoint-bomb-status-concealed = The bomb has not been planted. Its carrier or location is concealed from your side.
breachpoint-bomb-status-spectator-concealed = The bomb has not been planted. Spectators cannot see who has it or where it is.
breachpoint-bomb-status-unavailable = Bomb status is unavailable.
breachpoint-score-brief = Round { $round }, { $squad }: { $score } round wins, currently { $side }.
breachpoint-score-header = Match score after or during combat round { $round }, format { $format }.
breachpoint-score-line = { $squad }: { $score } round wins, currently { $side }
breachpoint-score-regulation = Regulation round { $round }; halftime follows round { $half }; first to { $target } wins.
breachpoint-score-overtime = MR3 overtime period { $period }, round { $round } of { $half } per half.
breachpoint-score-summary = { $team_one } { $team_one_score }, { $team_two } { $team_two_score }.

# Victory and end screen
breachpoint-win-reason-elimination = the opposing side was eliminated
breachpoint-win-reason-defused = the bomb was defused
breachpoint-win-reason-detonated = the bomb detonated
breachpoint-win-reason-time = the pre-plant tactical clock expired
breachpoint-win-reason-regulation = they reached the regulation winning score
breachpoint-win-reason-overtime = they won an MR3 overtime period
breachpoint-win-reason-draw = regulation ended level and overtime was disabled
breachpoint-victory-you = Your squad, { $team }, wins the match because { $reason }. Final score: { $score }
breachpoint-victory-other = { $team } win the match because { $reason }. Final score: { $score }
breachpoint-match-draw = The match ends in a draw because { $reason }. Final score: { $score }
breachpoint-end-header = Breach Point match complete
breachpoint-end-winner = Winners: { $team }
breachpoint-end-draw = Result: draw
breachpoint-end-reason = Match result: { $reason }
breachpoint-end-score = Final score: { $team_one } { $team_one_score }, { $team_two } { $team_two_score }
breachpoint-end-rounds = Combat rounds played: { $rounds }
