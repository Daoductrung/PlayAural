game-name-lastoutpost = Last Outpost
lo-root-vitals = HP { $hp }/{ $maximum }; AP { $ap }; { $item }.
lo-root-spectator = Spectating Last Outpost.
lo-menu-attack = Attack
lo-menu-move = Move
lo-menu-equipment = Weapons and reload
lo-menu-support = Aid and cargo
lo-menu-interact = Objectives and surroundings
lo-menu-supplies = Supplies and upgrades
lo-menu-back = Back to main menu
lo-menu-available = { $menu }; Available
lo-menu-equipment-state = { lo-menu-equipment }: { $weapon }; loaded { $loaded }, reserve { $reserve }.
lo-shop-balance = Credits: { $credits }.
lo-shop-done = Close shop
lo-help-shop-done = Close the shop without ending your turn. E or X also closes it.
lo-key-finish-or-end = Ready, close shop or end turn
lo-menu-close-information = Close the information panel first.
lo-help-menu-attack = Choose a gun, knife or grenade target.
lo-help-menu-move = Open routes, movement costs and destination occupants.
lo-help-menu-equipment = Reload or switch weapons. Switching costs no AP.
lo-help-menu-support = { $party_size ->
    [1] Heal yourself or drop cargo.
   *[other] Heal, revive or transfer cargo.
    }
lo-help-menu-interact = Restore power and radio, open gates or repair barricades.
lo-help-menu-supplies = Buy supplies and upgrades. Purchases keep the shop open. X goes back.
lo-help-menu-back = Return to your category button on the main menu.
lo-empty-attack = No targets available.
lo-empty-move = No open routes.
lo-empty-equipment = No weapon actions available.
lo-empty-preparation = Unavailable during preparation.
lo-empty-support = No aid or cargo actions available.
lo-empty-interact = No interactions available.
lo-empty-supplies = No supplies available here.
lo-move-location = { $zone }. { $description }
lo-destination = { $party_size ->
    [1] { $zone }; { $ap } AP. Enemies: { $inside } inside, { $outside } outside. { $barricade }
   *[other] { $zone }; { $ap } AP. Zombies: { $inside } inside, { $outside } outside. Squad: { $survivors }. { $barricade }
    }
lo-destination-survivor = { $name } ({ $condition })
lo-destination-barricade = Enemy entrance; barricade strength { $strength }.
lo-enemies = Enemy inspector
lo-help-enemies = Targets within reach come first, then more distant enemies and reinforcements. You still need your turn, AP and ammunition to attack.
lo-enemies-context = Targets from { $zone }.
lo-enemies-spectator-context = Overview from { $zone }.
lo-enemies-empty = No enemies on the map.
lo-enemy-detail = { $pack }. Health per enemy: { $health }. { $distance } { $access }
lo-enemy-distance = Route distance: { $count ->
    [one] { $count } connection.
   *[other] { $count } connections.
    }
lo-enemy-unreachable = No open route.
lo-enemy-barricade = Behind a barricade of strength { $strength }; attacks are blocked.
lo-enemy-reach = Within reach: { $actions }.
lo-enemy-reposition = Out of reach with current equipment.
lo-enemy-observe = Spectator view.
lo-health = Check health
lo-help-health = Current HP and rescue status.
lo-health-report = HP { $hp }/{ $maximum }. { $condition }.
lo-health-upright = Standing
lo-health-downed = { $party_size ->
    [1] Down
   *[other] Down; rescue within { $phases } horde phases
    }
lo-health-awaiting-recovery = Awaiting wave recovery
lo-slot-primary = Equip primary weapon
lo-slot-sidearm = Equip pistol
lo-error-slot-empty = No primary weapon equipped.
lo-error-preparation = Combat actions are unavailable during preparation.
lo-option-voices = Character dialogue: { $enabled }
lo-change-voices = Character dialogue set to { $enabled }.
lo-desc-voices = English character dialogue, including strong language. Tactical reports use your selected language.
lo-you = You
lo-team = { $party_size ->
    [1] Survivor
   *[other] Team
    }
lo-none = None
lo-yes = Yes
lo-no = No
lo-inside = inside
lo-outside = outside the barricade
lo-message = { $text }
lo-term-none = { lo-none }
lo-term-courtyard = Courtyard
lo-term-gatehouse = Gatehouse
lo-term-workshop = Workshop
lo-term-infirmary = Infirmary
lo-term-loading = Loading Bay
lo-term-generator = Generator Room
lo-term-pump = Pump Hall
lo-term-roof = Radio Roof
lo-term-walker = { $count ->
    [one] Walker
   *[other] Walkers
    }
lo-term-hound = { $count ->
    [one] Hound
   *[other] Hounds
    }
lo-term-brute = { $count ->
    [one] Brute
   *[other] Brutes
    }
lo-term-pistol = M1911 pistol
lo-term-rifle = AK rifle
lo-term-shotgun = Shotgun
lo-term-marksman = Marksman rifle
lo-term-knife = Knife
lo-term-medkit = Medical kit
lo-term-grenade = Grenade
lo-term-endurance = Endurance
lo-term-medic = Field Medic
lo-term-quickhands = Quick Hands
lo-term-combat = Survivor phase
lo-term-resolving = Action resolving
lo-term-reloading = Reloading
lo-term-prep = Preparation
lo-term-finished = Finished
lo-term-dempsey = Dempsey
lo-term-nikolai = Nikolai
lo-term-takeo = Takeo
lo-term-richtofen = Richtofen
lo-term-victory = { $party_size ->
    [1] Survived
   *[other] Squad survived
    }
lo-term-objectives = Radio or power unfinished
lo-term-overwhelmed = { $party_size ->
    [1] Overwhelmed
   *[other] The team was overwhelmed
    }
lo-term-overrun = Wave time limit reached
lo-turn-resolving = { lo-error-resolving }
lo-turn-prep = { $survivor_count ->
    [1] Preparation. Ready starts the next wave.
   *[other] Preparation. The next wave starts when everyone is ready.
    }
lo-map = Map and enemy packs
lo-forecast = Next horde forecast
lo-inventory = Equipment and supplies
lo-help-map = Routes, barricades, enemy packs and arrival schedule. Audio faces north.
lo-help-forecast = Next horde phase if nobody acts further.
lo-help-inventory = Your credits, weapons and supplies, plus parts for repairs and objectives.
lo-header = Wave { $wave }; cycle { $cycle }/{ $limit }. { $phase }. { $zone }. HP { $hp }; AP { $ap }; credits { $credits }; parts { $parts }.
lo-spectator-header = Spectating. Wave { $wave }; cycle { $cycle }. { $phase }; parts { $parts }.
lo-objectives = Objectives
lo-survivor = { $name } ({ $character }): { $zone }; health { $hp }/{ $maximum }; AP { $ap }. { $condition }; ready { $ready }; braced { $guard }.
lo-zone = { $zone }: { $description } Open routes: { $links }. Enemies: { $enemies }. { $barrier } Melee contact slots: { $frontage }.
lo-pack = { $count } { $kind }, { $zone }, { $side }; combined health { $hp }
lo-incoming = { $zone }: { $count } reinforcements after horde phase { $cycle }; first action in phase { $first }.
lo-forecast-caveat = Assumes no further actions. Brutes use two contact slots; other enemies use one. Crowded enemies still contest objectives. Reading costs no time.
lo-weapon-status = { $name }, { $weapon }: loaded { $ammo }, reserve { $reserve }; damage { $damage } per target, up to { $targets } targets; range { $minimum } to { $maximum }; equipped { $equipped }.
lo-kit-status = { $name }: credits { $credits }; medical kits { $medkits }, grenades { $grenades }; perks { $perks }.
lo-action-label = { $action }: { $detail } ({ $ap } AP)
lo-action-label-simple = { $action } ({ $ap } AP)
lo-reload-detail = { $weapon }; loaded { $loaded }/{ $capacity }, reserve { $reserve }
lo-attack-detail = { $weapon }, loaded { $ammo }; { $target }
lo-price = { $item }, { $cost } credits
lo-ammo-price = { $item }, { $amount } reserve rounds for { $cost } credits
lo-parts-price = { $item }, { $cost } parts
lo-work-price = { $item }, { $done } of { $total } work, { $cost } parts due
lo-verb-fire = Fire
lo-verb-knife = Knife
lo-verb-reload = Reload
lo-verb-grenade = Throw grenade
lo-verb-heal = Use medical kit
lo-verb-revive = Revive
lo-verb-open = Open gate
lo-verb-repair = Repair barricade
lo-verb-work = Repair equipment
lo-verb-ammo = Buy ammunition
lo-verb-buy = Buy equipment
lo-verb-perk = Buy perk
lo-verb-upgrade = Upgrade primary
lo-verb-equip = Equip
lo-verb-ready = Ready for next wave
lo-verb-end = End turn
lo-help-fire = Hits the most wounded enemy in the pack first. Shotguns hit up to two. Barricades protect outside enemies until destroyed.
lo-help-knife = 1 damage; 1 AP; same zone. No ammunition.
lo-help-move = 1 AP per connection; 2 when leaving enemies. Cargo adds 1 AP.
lo-help-reload = 1 AP; transfers reserve ammo when finished. Walking remains available. Quick Hands waives the first reload's AP cost each wave.
lo-help-grenade = { $party_size ->
    [1] 3 damage to up to four enemies; 1 AP. Your zone or a visible adjacent zone. Only hits enemies inside the perimeter.
   *[other] 3 damage to up to four enemies; 1 AP. Your zone or a visible adjacent zone. Only hits enemies inside the perimeter; no friendly fire.
    }
lo-help-heal = 1 kit and 1 AP; restores up to 3 HP to a standing survivor in your zone.
lo-help-revive = Revive with 2 HP; 2 AP, or 1 with Field Medic. Same zone. No extra turn.
lo-help-revive-preview = { lo-help-revive } Without further actions, { $target } would have { $health } HP after the next horde phase.
lo-gate-link = { $origin } to { $destination }
lo-gate-service = Service gate
lo-gate-shortcut = Infirmary shortcut
lo-gate-roof = Radio access gate
lo-gate-crossing = Freight crossing
lo-gate-bulkhead = Flood bulkhead
lo-gate-status = { $gate }: open { $opened }; { $cost } parts; needs power { $power }. Routes: { $routes }. Contact slots after opening: { $frontages }.
lo-help-open-routes = { $cost } parts; 1 AP; your zone must be clear. Opens { $routes } permanently for both sides. Needs power: { $power }. Contact slots afterward: { $frontages }.
lo-frontage-site = { $zone }, { $count } contact slots
lo-gate-opened-routes = New routes for both sides: { $routes }.
lo-defense-until-clear = Keep defending { $zone } until the wave ends; enemies can still damage the relay.
lo-help-repair = 1 part and 1 AP; restores 2 barricade strength, up to 4. Once per cycle; clear zone.
lo-help-work = 1 AP per work unit. First unit pays the listed parts cost. Clear zone required; radio needs power.
lo-help-ammo = Reserve capacity: three magazines. During combat, buy at a clear ammo station. During preparation, buy anywhere.
lo-help-buy = Preparation only. Primary weapons replace your current primary. First purchase includes ammo; rebuying retains old ammo. No refund.
lo-help-perk = Needs power; two perks maximum. Endurance: +2 HP. Field Medic: revive for 1 AP. Quick Hands: first reload each wave costs no AP.
lo-help-upgrade = Needs power; 500 credits per weapon type. Damage: AK 4, shotgun 6, marksman 9.
lo-help-equip = Switch weapons; no AP cost.
lo-help-ready = { $survivor_count ->
    [1] Start the next wave.
   *[other] Toggle readiness. All ready starts the next wave. Cancel readiness to buy again.
    }
lo-help-end = { $party_size ->
    [1] Discard remaining AP. Enemies act next.
   *[other] Discard remaining AP. Enemies act after the squad finishes.
    }
lo-error-unavailable = Unavailable in this phase.
lo-error-stale = That choice is no longer available.
lo-error-turn = { action-not-your-turn }
lo-error-down = You are down.
lo-error-ready = Cancel readiness before buying.
lo-error-ap = Not enough AP.
lo-error-range = Target outside firing range or line of sight.
lo-error-ammo = Not enough loaded ammunition.
lo-error-grenade = No grenades.
lo-error-medkit = No medical kits.
lo-error-engaged = Clear the enemies from this zone first.
lo-error-complete = This objective is already complete.
lo-error-power = Restore power first.
lo-error-parts = Not enough parts.
lo-error-credits = Not enough credits.
lo-error-equipped = This weapon is already equipped.
lo-error-resolving = The current action is resolving.
lo-event-wave = Wave { $amount }; { $count } enemies. { $deployment }.
lo-deployment-now = { $count } outside now
lo-deployment-later = { $count } arrive after horde phase { $cycle }
lo-event-final_warning = Final wave. { $amount } infrastructure work remaining; { $count } parts due. Finish infrastructure and mission before the wave ends.
lo-event-clear = { $party_size ->
    [1] Wave { $amount } cleared. +{ $count } credits; +3 parts. Heal { $healing } HP, or recover with { $recovery } HP if down. Up to { $ammo } pistol reserve rounds. Preparation.
   *[other] Wave { $amount } cleared. Each survivor gains { $count } credits and up to { $ammo } pistol reserve rounds. Standing survivors heal { $healing } HP; downed survivors return with { $recovery } HP. Team: +3 parts. Preparation.
    }
lo-event-fire = { $actor } fired { $item } at { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife = { $actor } struck with a knife at { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade = { $actor } detonated a grenade at { $zone }. { $hits }. { lo-combat-kills }
lo-event-move = { $actor } moved from { $origin } to { $zone }.
lo-event-reload = { $actor } loaded { $amount } rounds into { $item }.
lo-reload-start = { $actor } is reloading.
lo-reload-start-personal = Reloading.
lo-error-reloading = { lo-reload-start-personal }
lo-event-heal = { $actor } treated { $target }; health now { $amount }.
lo-event-revive = { $actor } revived { $target } with { $amount } HP.
lo-event-open = { $actor } opened { $item }; { $amount } parts remaining. { $routes }
lo-event-repair = { $actor } repaired the barricade at { $zone } to { $amount } strength.
lo-event-work = { $count ->
    [1] { $actor } restored { $item } at { $zone }.
   *[0] { $actor } worked on { $item } at { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo = { $actor } bought { $amount } rounds for { $item }, paid { $count } credits.
lo-event-buy = { $actor } bought { $item }; { $amount } credits left.
lo-event-perk = { $actor } acquired { $item }.
lo-event-upgrade = { $actor } upgraded { $item }.
lo-event-equip = { $actor } equipped { $item }.
lo-event-ready = { $actor } is { $amount ->
    [1] ready for the next wave.
   *[0] not ready.
    }
lo-event-end = { $actor } ended their turn.
lo-event-barrier = { $zone }: { $count } barricade strikes by { $item }; strength now { $amount }.
lo-event-enter = { $count } { $item } entered { $zone }.
lo-event-approach = { $count } { $item } moved from { $origin } to { $zone }.
lo-event-hurt = { $target }: { $count } attacks by { $item }, { $amount } total damage at { $zone }.
lo-event-down = { $target } is down at { $zone }. Revive within the next two horde phases.
lo-event-incapacitated = { $target } is incapacitated until the next wave.
lo-event-recovery = { $target }: last emergency recovery. HP { $amount }; next turn { $count } AP. Cargo stays where they fell.
lo-event-arrivals = { $count } reinforcements outside. They act next horde phase.
lo-event-finish = { $item }. Waves cleared: { $amount } of { $waves }.
lo-result-cycles = Horde phases: { $count }.
lo-error-magazine-full = The equipped magazine is already full.
lo-error-reserve-empty = No reserve ammunition.
lo-error-barrier-full = This barricade is at full strength.
lo-error-already-repaired = This barricade was already repaired this cycle.
lo-error-weapon-owned = You already carry this primary weapon.
lo-error-kit-capacity = Medical kit capacity reached.
lo-error-grenade-capacity = Grenade capacity reached.
lo-error-ammo-capacity = Reserve ammunition capacity reached.
lo-error-perk-owned = You already have this perk.
lo-error-perk-capacity = Perk limit reached.
lo-error-no-primary = Buy a primary weapon first.
lo-error-upgraded = This weapon is already upgraded.
lo-event-heal-self = { $actor } used a medical kit; health now { $amount }.
lo-event-heal-self-personal = You treated yourself; health now { $amount }.
lo-event-heal-target = { $actor } treated you; health now { $amount }.
lo-event-revive-target = { $actor } revived you with { $amount } HP. You act next cycle.
lo-event-hurt-personal = You took { $count } attacks from { $item }, { $amount } total damage at { $zone }.
lo-event-down-personal = You are down at { $zone }. Your team has the next two horde phases to revive you.
lo-event-down-solo-recovery = { $target } fell at { $zone }. Emergency recovery: { $recovery_seconds } seconds after this horde phase.
lo-event-down-solo-recovery-personal = You fell at { $zone }. Emergency recovery: { $recovery_seconds } seconds after this horde phase.
lo-event-down-solo-final = { $target } fell at { $zone }. No survivors or recoveries remain.
lo-event-down-solo-final-personal = You fell at { $zone }. No survivors or recoveries remain.
lo-event-incapacitated-personal = You are out until the next wave.
lo-event-recovery-personal = You used your last emergency recovery. HP { $amount }; next turn { $count } AP. Cargo stays where you fell.
lo-event-fire-personal = You fired { $item } at { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife-personal = You struck with a knife at { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade-personal = You threw a grenade at { $zone }. { $hits }. { lo-combat-kills }
lo-event-move-personal = You moved from { $origin } to { $zone }.
lo-event-reload-personal = You loaded { $amount } rounds into { $item }.
lo-event-heal-personal = You treated { $target }; health now { $amount }.
lo-event-revive-personal = You revived { $target } with { $amount } HP.
lo-event-open-personal = You opened { $item }; { $amount } parts remaining. { $routes }
lo-event-repair-personal = You repaired { $zone } barricade to { $amount } strength.
lo-event-work-personal = { $count ->
    [1] You restored { $item } at { $zone }.
   *[0] You worked on { $item } at { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo-personal = You bought { $amount } rounds for { $item }, paid { $count } credits.
lo-event-buy-personal = You bought { $item }; credits remaining { $amount }.
lo-event-perk-personal = You acquired { $item }.
lo-event-upgrade-personal = You upgraded { $item }.
lo-event-equip-personal = You equipped { $item }.
lo-event-ready-personal = You are { $amount ->
    [1] ready for the next wave.
   *[0] not ready.
    }
lo-event-end-personal = You ended your turn.
lo-term-horde = enemies
lo-help-move-destination = { $description } { lo-help-move }
lo-zone-description-courtyard = Cracked concrete surrounds an empty flagpole beneath the open sky. The Workshop stands to the west, the Infirmary to the east; south, the Gatehouse faces the dark beyond the perimeter.
lo-zone-description-gatehouse = South of the Courtyard, the gatehouse roof has fallen away, leaving splintered floorboards exposed to the night. The guard's empty chair faces the outer entrance, where the perimeter fence meets the road.
lo-zone-description-workshop = Oil stains spread beneath abandoned workbenches, and rust streaks the sheet-metal walls. The ammunition locker stands against the back wall; a service gate leads toward the generator.
lo-zone-description-infirmary = Narrow cots line a timber room east of the Courtyard. Dusty bandages hang from a tipped trolley, and pale light catches the window glass. A side passage leads toward the Pump Hall.
lo-zone-description-loading = Rusted steel decking runs past stacks of empty pallets under the open sky. The Workshop lies south; to the east, a passage leads into the damp of the Pump Hall.
lo-zone-description-generator = A squat generator fills a concrete chamber beyond the Workshop's service gate. Thick cables cross the metal floor toward a scarred switchboard. This is where the outpost's power must be restored.
lo-zone-description-pump = Shallow water covers the floor beneath thick pipes and corroded valves. A tide mark stains the concrete walls. The Infirmary passage meets the route from the Loading Bay here.
lo-zone-description-roof = An antenna leans above a bare concrete roof, its guy wires stretched against the sky. The radio sits in a battered weatherproof cabinet. Powered access gates guard the approaches from below.
lo-option-map = Map: { $value }
lo-prompt-map = Choose a map
lo-change-map = Map set to { $value }.
lo-desc-map = Abandoned Outpost: a battered garrison around an open courtyard. Switchyard: deserted rails beneath a narrow overpass. Floodworks: flooded machinery halls split by heavy gates.
lo-option-mode = Mode: { $value }
lo-prompt-mode = Choose a mode
lo-change-mode = Mode set to { $value }.
lo-desc-mode = Operations: missions and infrastructure. Siege: defend relay integrity. Salvage: recover cargo. Classic Extraction: eight waves, power, radio and a final supply run.
lo-extraction-route = Wave { $wave }: move supplies from { $pickup } to { $destination } within { $deadline } horde phases. Clear pickup and delivery zones. Cargo: +1 AP per move, pistol only.
lo-option-difficulty = Difficulty: { $value }
lo-prompt-difficulty = Choose difficulty
lo-change-difficulty = Difficulty set to { $value }.
lo-desc-difficulty = Recruit: more recovery and supplies. Standard: stronger hordes and changing conditions. Veteran: maximum pressure, scarce income, no free wave healing or sidearm ammo.
lo-error-scenario = Unsupported map, mode or difficulty. Check lobby options.
lo-event-start = { $map }. { $mode }, { $difficulty }. { $waves } waves. Starting at { $spawn }.
lo-scenario-status = { $map }; { $mode }; { $difficulty }. { $condition }.
lo-mission-status-retrieve = Recover cargo at { $cargo }; carrier { $carrier }; deliver to { $destination }. { $remaining } horde phases left.
lo-mission-status-relay = Relay terminals: { $zone } and { $destination }. { $remaining } horde phases left.
lo-mission-status-hold = Defend { $zone }: { $progress } of { $total } holding phases. { $remaining } horde phases left.
lo-mission-help-retrieve = 1 AP to pick up, deliver, hand off or drop. Clear zone required except when dropping. Cargo: +1 AP per move, pistol only. Going down drops the cargo; its deadline keeps running.
lo-mission-help-relay = { $survivor_count ->
    [1] 1 AP per terminal in a clear zone. Activate both sites; activations persist across cycles. Both sites must be clear after the horde.
   *[other] 1 AP per terminal in a clear zone. Two survivors activate separate sites in the same cycle, then stay standing there through the horde. Both sites must finish clear.
    }
lo-mission-help-hold = Keep a survivor standing at the site, with no enemies inside, at the end of two horde phases. An empty or contested site loses one progress. In Siege, protect the relay until the wave ends; missing the deadline costs integrity.
lo-terminal-status = { $zone }: activated by { $actor }.
lo-verb-mission = Mission interaction
lo-verb-handoff = Hand over cargo
lo-verb-drop = Put down cargo
lo-verb-guard = Brace
lo-help-mission = 1 AP; perform the marked task in a clear zone.
lo-help-handoff = 1 AP; transfer cargo to a standing teammate in the same clear zone.
lo-help-drop = 1 AP; drop cargo here. Restores normal movement and primary fire.
lo-help-guard = 1 AP; intercept the next local attack and reduce its damage by one. Expires next cycle; does not stack or draw distant enemies.
lo-error-guarded = You are already braced.
lo-error-carrying = Cargo blocks primary fire. Use your pistol or put the cargo down.
lo-error-terminal = This terminal is already active.
lo-error-relay-partner = A different survivor must activate the other terminal.
lo-task-activate = Activate this relay terminal; partner site: { $zone }
lo-task-pickup = Collect cargo for { $zone }
lo-task-deliver = Deliver cargo at { $zone }
lo-event-mission_complete = { $party_size ->
    [1] { $item } complete: { $sites }. +{ $count } credits; +1 part. { $defense }
   *[other] { $item } complete: { $sites }. Each survivor +{ $count } credits; team +1 part. { $defense }
    }
lo-event-mission_failed = { $item } failed. Failed missions: { $amount }.
lo-event-mission_clock = { $item }: { $amount } horde phases remain.
lo-event-mission_pressure = Mission noise drew { $count } walkers outside { $zone }. Active next horde phase.
lo-event-hold_progress = Defense at { $zone }: { $amount } of { $count } phases secured.
lo-event-core_damage = Relay at { $zone } loses { $amount } integrity; { $count } remains.
lo-event-relay_reset = Relays: { $item }.
lo-event-cargo_lost = Cargo dropped at { $zone }.
lo-event-condition = { $item }. First reinforcements after horde phase { $amount }.
lo-term-outpost = Abandoned Outpost
lo-term-switchyard = Switchyard
lo-term-floodworks = Floodworks
lo-term-operations = Operations
lo-term-siege = Siege
lo-term-salvage = Salvage
lo-term-classic = Classic Extraction
lo-term-recruit = Recruit
lo-term-standard = Standard
lo-term-veteran = Veteran
lo-term-retrieve = Cargo recovery
lo-term-relay = Coordinated relay
lo-term-hold = Sector defense
lo-term-mission_quota = Mission requirement failed
lo-term-core_lost = Relay destroyed
lo-term-latched = activated terminals remain ready
lo-term-reset = activate both terminals again in the same cycle
lo-term-condition-normal = Clear conditions
lo-term-condition-rush = Early reinforcements
lo-term-condition-fog = Fog: firearms limited to one connection
lo-term-condition-battering = Battering horde: one extra barricade damage
lo-term-condition-shortage = Supply shortage: reserve magazines cost 90 credits
lo-term-depot = Passenger Depot
lo-term-west_tracks = West Tracks
lo-term-east_tracks = East Tracks
lo-term-signal_box = Signal Box
lo-term-freight = Freight Yard
lo-term-maintenance = Maintenance Shed
lo-term-switchgear = Switchgear Room
lo-term-overpass = Overpass
lo-term-tower = Radio Tower
lo-term-tunnel = Rail Tunnel
lo-term-quay = Landing Quay
lo-term-foyer = Intake Foyer
lo-term-canal = Drainage Canal
lo-term-filter = Filter Beds
lo-term-control = Control Room
lo-term-laboratory = Laboratory
lo-term-archive = Supply Archive
lo-term-turbine = Turbine Hall
lo-term-skybridge = Radio Skybridge
lo-term-clinic = Clinic
lo-event-guard = { $actor } braced: next incoming strike deals one less damage.
lo-event-guard-personal = You braced: next incoming strike deals one less damage.
lo-event-cargo_pickup = { $actor } collects the cargo at { $zone } for { $origin }.
lo-event-cargo_pickup-personal = You collect the cargo at { $zone } for { $origin }.
lo-event-cargo_deliver = { $actor } delivers the cargo at { $zone }.
lo-event-cargo_deliver-personal = You deliver the cargo at { $zone }.
lo-event-cargo_drop = { $actor } puts down the cargo at { $zone }.
lo-event-cargo_drop-personal = You put down the cargo at { $zone }.
lo-event-cargo_handoff = { $actor } hands the cargo to { $target } at { $zone }.
lo-event-cargo_handoff-personal = You hand the cargo to { $target } at { $zone }.
lo-event-relay_armed = { $actor } activates the terminal at { $zone }; { $amount } terminals armed.
lo-event-relay_armed-personal = You activate the terminal at { $zone }; { $amount } terminals armed.
lo-event-cargo_handoff-target = { $actor } hands you the cargo at { $zone }.
lo-zone-description-depot = Rows of empty benches face a departure board frozen on cancelled trains. Dust dulls the concrete floor. Doors at either end of the hall lead out to the western and eastern tracks.
lo-zone-description-west_tracks = A steel walkway follows rusted rails beneath dead signal lamps. Fence posts mark the edge of the yard; beyond the depot, the Signal Box rises on the northern side.
lo-zone-description-east_tracks = Empty wagons stand beside a strip of buckled steel decking. Rails stretch away into darkness beyond the perimeter; the Freight Yard opens to the north.
lo-zone-description-signal_box = Lever handles crowd a wooden cabin above a faded track diagram. Windows overlook the western rails. Passages lead toward the Maintenance Shed and the steps to the Overpass.
lo-zone-description-freight = Freight containers loom over a yard of dented steel plates. Loose chains hang from a loading frame. The crossing gate guards the approach to the Overpass; another route enters the Rail Tunnel.
lo-zone-description-maintenance = Dismantled wheels and greasy tools line a corrugated-metal shed. An ammunition locker stands on the stained concrete floor, beside the service gate to the Switchgear Room.
lo-zone-description-switchgear = Rows of heavy switches fill a concrete room beyond the service gate. Thick cables disappear beneath metal floor plates, and warning labels peel from the cabinets. Restore the yard's power here.
lo-zone-description-overpass = Open steel grating spans the rail lines, with only a narrow handrail against the drop. The Signal Box and Freight Yard lie below; the Radio Tower rises ahead to the north.
lo-zone-description-tower = A radio desk and a worn wooden chair fill the cabin above the tracks. Windows look over the yard on every side. Power is needed to open the access gates below.
lo-zone-description-tunnel = Rails vanish into a concrete tunnel streaked with soot and seepage. The Freight Yard lies behind you; a side passage climbs toward the Radio Tower's access gate.
lo-zone-description-quay = Warped landing boards jut over black water, their mooring ropes trailing loose. The southern perimeter ends here. Ahead, the plant's concrete entrance opens into the Intake Foyer.
lo-zone-description-foyer = Water stains climb the concrete walls beneath a faded evacuation plan. This cramped entrance splits toward the Drainage Canal on the west and the Supply Archive on the east.
lo-zone-description-canal = Shallow water runs between high concrete banks, carrying scraps of weed in from beyond the perimeter. The channel bends north toward the Filter Beds; the foyer lies to the east.
lo-zone-description-filter = Floodwater laps around rows of clogged filter beds beneath rusted metal walls. The service gate leads toward the turbines; a heavy bulkhead separates this hall from the Control Room.
lo-zone-description-control = A long bank of gauges and cracked screens overlooks a metal floor. The Laboratory opens to the east, the filter bulkhead to the west; the northern approach leads up to the Radio Skybridge.
lo-zone-description-laboratory = Clouded sample jars crowd the benches, and broken glass glints on the concrete. Doors connect the Supply Archive, Control Room and Clinic; every route cuts through the abandoned workroom.
lo-zone-description-archive = Water-swollen ledgers sag on wooden shelves beside sealed supply cases. The ammunition locker occupies the driest corner. The foyer is to the west, the Laboratory to the north.
lo-zone-description-turbine = Great turbine housings fill a cavernous metal hall beyond the service gate. Maintenance plates form the floor between them. The power controls stand below the route up to the Radio Skybridge.
lo-zone-description-skybridge = A narrow steel bridge hangs above the plant's northern halls, exposed to the wind. A radio cabinet stands beneath an antenna; the approaches converge here from Control, the Clinic and the turbines.
lo-zone-description-clinic = Faded privacy curtains divide a concrete room lined with examination beds. Damp has crept beneath the medicine cabinets. The Laboratory lies south; another approach climbs to the Radio Skybridge.
lo-event-mission_start-retrieve = Cargo: { $zone } to { $origin }. Deadline: { $amount } horde phases.
lo-event-mission_start-relay = Relays: { $zone } and { $origin }. Deadline: { $amount } horde phases.
lo-event-mission_start-hold = Hold { $zone }. Deadline: { $amount } horde phases.
lo-error-visibility = Fog blocks shots beyond one connection.
lo-help-weapon = Damage { $damage }; upgraded { $upgraded }; targets { $targets }; range { $minimum }–{ $maximum }; magazine { $magazine }; { $rounds } rounds per shot; { $price } credits. Replaces primary; no refund.
lo-error-barricade = The barricade blocks this attack.
lo-combat-hit = { $enemy }: { $damage } damage
lo-combat-outside = { $zone }, { lo-outside }
lo-objective-generator = Power
lo-objective-radio = Radio
lo-combat-kills = { $count ->
    [0] { "" }
    [one] 1 kill.
   *[other] { $count } kills.
    }
lo-shop-ready = Done shopping and Ready
lo-help-shop-ready = E closes the shop and marks you ready. X goes back without readying.
lo-already-ready = { $party_size ->
    [1] Ready.
   *[other] You are ready. Waiting for the squad.
    }
lo-help-teammates = { $party_size ->
    [1] Your position, health and character.
   *[other] Squad positions, health, rescue deadlines and characters.
    }
lo-help-objectives = Win requirements, infrastructure progress and the active mission.
lo-teammates = { $party_size ->
    [1] Character
   *[other] Teammates
    }
lo-required = Required
lo-optional = Optional
lo-complete = Complete
lo-incomplete = Incomplete
lo-objective-waves = Required: clear all waves. { $completed }/{ $total } cleared.
lo-objective-missions = Required: complete { $total } missions. { $completed } completed; { $failed } failed.
lo-objective-bonus-missions = Missions: { $completed } completed; { $failed } failed.
lo-objective-integrity = Required: keep the relay intact. Integrity { $current }/{ $total }.
lo-objective-project = { $project }, { $zone }: { $requirement }. { $state }; work { $progress }/{ $total }. Remaining: { $remaining } work, { $cost } parts, plus any unopened access gates.
lo-mission-idle = No active mission.
lo-verb-unready = Cancel readiness

lo-health-recovering = Down; emergency recovery { $recovery_seconds } seconds after the horde
lo-inventory-parts = { $party_size ->
    [1] Parts: { $parts }.
   *[other] Shared parts: { $parts }.
    }
lo-board-lineup = { $count ->
    [1] One survivor
   *[other] Survivors { $count }: humans { $humans }, bots { $bots }
    }
lo-board-original = No bot takeovers
lo-board-takeover = With bot takeovers
leaderboard-lo-clear-entry = { $rank }. { $player }: { $value } horde phases.
lo-personal-record = { $name }: { $value } horde phases.
lo-record-unranked = Unranked: the starting roster changed.
