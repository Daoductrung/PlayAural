game-name-battle = Battle

battle-set-game-mode = Game mode: { $mode }
battle-select-game-mode = Select a game mode:
battle-option-changed-game-mode = Game mode changed to { $mode }.
battle-desc-game-mode = Chooses the Battle format: fixed fighter counts, Team Battle, Chaos Free For All, Spitting Image, arena, survival, or wave modes.

battle-desc-team-mode = Chooses individual play or fixed team sizes. This is used by Team Battle and must fit the current player count.
battle-set-turn-mode = Turn mode: { $mode }
battle-select-turn-mode = Select a turn mode:
battle-option-changed-turn-mode = Turn mode changed to { $mode }.
battle-desc-turn-mode = Chooses turn order: Initiative sorts combatants by speed each round, while Round Robin follows a fixed rotation.

battle-set-balance-mode = Balance mode: { $enabled }
battle-option-changed-balance-mode = Balance mode changed to { $enabled }.
battle-desc-balance-mode = When enabled, fighters outside the balanced baseline are reset before combat to 50 health, 0 attack, 0 defense, and 100 speed.

battle-set-unlimited-selection-limit = Unlimited-mode fighter limit: { $count }
battle-enter-unlimited-selection-limit = Enter the fighter limit for unlimited modes:
battle-option-changed-unlimited-selection-limit = Unlimited-mode fighter limit changed to { $count }.
battle-desc-unlimited-selection-limit = How many fighters each player may select in unlimited-selection modes such as Chaos Free For All, Team Battle, arenas, survival, and waves (default 3, range 1-6).

battle-set-classic-enemy-preset = Classic enemy preset: { $preset }
battle-select-classic-enemy-preset = Select the classic enemy preset:
battle-option-changed-classic-enemy-preset = Classic enemy preset changed to { $preset }.
battle-desc-classic-enemy-preset = Chooses the fixed enemy preset used only by Classic Arena, Classic Survival, and Classic Waves.

battle-set-arena-difficulty = Arena difficulty: { $difficulty }
battle-select-arena-difficulty = Select arena difficulty:
battle-option-changed-arena-difficulty = Arena difficulty changed to { $difficulty }.
battle-desc-arena-difficulty = Sets how dangerous generated arena, survival, and wave opponents are, from Easy through Ultimate.

battle-set-survival-target = Survival target: { $count }
battle-enter-survival-target = Enter the survival target (0 for endless):
battle-option-changed-survival-target = Survival target changed to { $count }.
battle-desc-survival-target = How many enemies must be defeated in Survival or Waves. Set 0 for endless play with no fixed defeat target (range 0-10000).

battle-set-survival-heal-percent = Survival heal percent: { $percent }
battle-enter-survival-heal-percent = Enter the survival heal percent:
battle-option-changed-survival-heal-percent = Survival heal percent changed to { $percent }.
battle-desc-survival-heal-percent = Percentage of maximum health living allied fighters recover after each survival replacement or cleared wave (default 0%, range 0-100).

battle-mode-free-for-all = Chaos Free For All
battle-mode-one-each = 1 Each
battle-mode-two-each = 2 Each
battle-mode-three-each = 3 Each
battle-mode-team-battle = Team Battle
battle-mode-spitting-image = Spitting Image
battle-mode-classic-arena = Classic Arena
battle-mode-mixed-arena = Mixed Arena
battle-mode-classic-survival = Classic Survival
battle-mode-mixed-survival = Mixed Survival
battle-mode-classic-waves = Classic Waves
battle-mode-mixed-waves = Mixed Waves

battle-turn-mode-initiative = Initiative
battle-turn-mode-round-robin = Round Robin

battle-difficulty-easy = Easy
battle-difficulty-normal = Normal
battle-difficulty-hard = Hard
battle-difficulty-insane = Insane
battle-difficulty-professional = Professional
battle-difficulty-ultimate = Ultimate

battle-classic-preset-novice-boxer = Novice Boxer
battle-classic-preset-boxer = Boxer
battle-classic-preset-the-great-fighter = The Great Fighter
battle-classic-preset-fighter-plane = Fighter Plane
battle-classic-preset-low-rank-soldier = Low-Rank Soldier
battle-classic-preset-high-rank-soldier = High-Rank Soldier
battle-classic-preset-ghostly-fighter = Ghostly Fighter
battle-classic-preset-the-alpha-wolf = The Alpha Wolf
battle-classic-preset-the-fiery-lion = The Fiery Lion
battle-classic-preset-master-mage = Master Mage
battle-classic-preset-the-wizardly-warrior = The Wizardly Warrior
battle-classic-preset-master-of-the-storm = Master of the Storm

battle-read-status = Read battle status
battle-read-status-detailed = Detailed battle status
battle-read-roster = Read roster
battle-read-allied-fighters = View allied fighters
battle-read-enemy-fighters = View enemy fighters
battle-undo-selection = Undo last selection
battle-done-selecting = Done selecting
battle-pick-preset-label = { $preset }. Health { $health }, attack { $attack }, defense { $defense }, speed { $speed }.
battle-fighter-selected = Selected: { $fighter }
battle-fighter-unselected = Not selected: { $fighter }
battle-submit-selection = Submit selection. Selected { $count } of { $limit }.
battle-submit-selection-required = Submit selection. Selected { $count } of { $required } required.
battle-skill-description = { $scope } targeting { $target }. { $effects }
battle-skill-scope-single = Single-target
battle-skill-target-self = yourself
battle-skill-target-ally = one ally
battle-skill-target-enemy = one enemy
battle-skill-target-any-fighter = any fighter
battle-skill-target-other-fighter = another fighter
battle-skill-effect-damage = deal { $min } to { $max } damage
battle-skill-effect-healing = restore { $min } to { $max } health
battle-skill-effect-drain = deal { $min } to { $max } damage and recover { $percent } percent of the damage dealt
battle-skill-effect-raise-own-stat = raise your { $stat } by { $amount }
battle-skill-effect-lower-own-stat = lower your { $stat } by { $amount }
battle-skill-effect-raise-target-stat = raise the target's { $stat } by { $amount }
battle-skill-effect-lower-target-stat = lower the target's { $stat } by { $amount }
battle-skill-effect-unknown = no additional effect listed
battle-select-target = Select a target:
battle-target-option = { $fighter }, { $team }, { $health } health
battle-target-option-no-team = { $fighter }, { $health } health

battle-selection-start = Fighter selection has begun.
battle-selection-start-chaos = Chaos selection has begun. Every fighter you choose will enter as its own side, even if you control more than one.
battle-selected-fighter = { $player } selected { $fighter }.
battle-selected-fighters-you = You selected { $fighters }.
battle-selected-fighters-player = { $player } selected { $fighters }.
battle-selection-locked = { $player } is ready.
battle-selection-locked-you = You are ready.
battle-selection-locked-player = { $player } is ready.
battle-combat-start = The battle begins.
battle-combat-start-chaos = Chaos battle begins. Every active fighter now fights for itself.
battle-turn-start = { $fighter } takes the turn.
battle-turn-start-you = Your { $fighter } takes the turn.
battle-turn-start-player = { $fighter } takes the turn.
battle-whose-turn-selection = The game is in the fighter selection phase.
battle-whose-turn-combat = It is { $fighter}'s turn. Health { $health}. Team: { $team}.
battle-used-move = { $fighter } used { $move } on { $target }.
battle-used-move-with-teams = { $fighter } from { $fighter_team } used { $move } on { $target } from { $target_team }.
battle-used-move-you = Your { $fighter } used { $move } on { $target }.
battle-used-move-player = { $fighter } used { $move } on { $target }.
battle-used-move-with-teams-you = Your { $fighter } from { $fighter_team } used { $move } on { $target } from { $target_team }.
battle-used-move-with-teams-player = { $fighter } from { $fighter_team } used { $move } on { $target } from { $target_team }.
battle-critical-hit = Critical hit!
battle-damage = { $target } took { $amount } damage.
battle-damage-you = Your { $target } took { $amount } damage.
battle-damage-player = { $target } took { $amount } damage.
battle-healing = { $target } recovered { $amount } health.
battle-healing-you = Your { $target } recovered { $amount } health.
battle-healing-player = { $target } recovered { $amount } health.
battle-stat-change = { $target } had { $stat } changed by { $amount }.
battle-stat-change-you = Your { $target } had { $stat } changed by { $amount }.
battle-stat-change-player = { $target } had { $stat } changed by { $amount }.
battle-fighter-defeated = { $fighter } has been defeated and is out.
battle-fighter-defeated-you = Your { $fighter } has been defeated and is out.
battle-fighter-defeated-player = { $fighter } has been defeated and is out.
battle-fighter-incapacitated = { $fighter } is too dizzy to keep fighting.
battle-fighter-incapacitated-you = Your { $fighter } is too dizzy to keep fighting.
battle-fighter-incapacitated-player = { $fighter } is too dizzy to keep fighting.
battle-enemies-arrive = { $count } new enemy fighters enter the arena.
battle-no-valid-targets = No valid targets are available for that move.
battle-no-fight-same-team = Everyone is on the same team, so no fight can happen.

battle-score-summary = { $fighters } fighters remain across { $teams } teams.
battle-score-summary-endurance = { $fighters } fighters remain across { $teams } teams. Survival kills: { $kills }.
battle-survival-progress-target = Survival run. Kills: { $kills }. Target: { $target }.
battle-survival-progress-endless = Endless survival run. Kills: { $kills }.
battle-wave-progress-target = Wave run. Current wave: { $wave }. Kills: { $kills }. Target: { $target }.
battle-wave-progress-endless = Endless wave run. Current wave: { $wave }. Kills: { $kills }.

battle-status-header = Battle status
battle-status-mode-line = Mode: { $mode }. Turn mode: { $turn_mode }.
battle-status-selection-limit-line = Fighter limit per player: { $limit }.
battle-status-chaos-line = Chaos rule: every selected fighter is its own side, so your own fighters may become enemies.
battle-status-team-mode-line = Team mode: { $mode }.
battle-status-classic-enemy-line = Classic enemy preset: { $preset }.
battle-status-arena-difficulty-line = Arena difficulty: { $difficulty }.
battle-status-endurance-options-line = Endurance target: { $target }. Recovery between reinforcements: { $heal_percent } percent.
battle-status-target-endless = endless
battle-roster-header = Combat roster
battle-allied-roster-header = Allied fighters
battle-enemy-roster-header = Enemy fighters
battle-selection-phase = The game is still in the fighter selection phase.
battle-selection-status-header = Fighter selection
battle-selection-score-line = { $player }: { $picks }
battle-selection-none = No fighters selected
battle-no-moves = No moves
battle-fighter-summary-line = { $fighter }: health { $health }, attack { $attack }, defense { $defense }, speed { $speed }, side { $team }, moves { $moves }.
battle-fighter-summary-line-no-team = { $fighter }: health { $health }, attack { $attack }, defense { $defense }, speed { $speed }, moves { $moves }.
battle-fighter-name-numbered = { $name } { $number }
battle-no-fighters-in-list = No fighters are available in this list.

battle-end-header = Battle result
battle-end-winner = Winning team: { $team }
battle-end-draw = The battle ended without a winner.

battle-team-allies = Ally Team
battle-team-enemies = Enemy Team
battle-team-contestants = Contestant Side
battle-team-arena = Arena Side
battle-team-owned = { $player }'s Team

battle-stat-attack = attack
battle-stat-defense = defense
battle-stat-speed = speed

battle-error-no-registry = The bundled Battle registry could not be loaded.
battle-error-mode-min-players = This mode requires at least { $count } players.
battle-error-survival-target-mode = Survival target can only be used in Survival or Waves modes.
battle-error-survival-heal-mode = Survival heal percent can only be used in Survival or Waves modes.
battle-error-selection-limit = The unlimited-mode fighter limit must be at least 1.
battle-error-invalid-classic-preset = The selected classic enemy preset is invalid.
battle-error-team-mode-only-team-battle = Shared team modes can only be used with Team Battle mode.
battle-error-team-battle-needs-team-mode = Team Battle requires a shared team mode that fits the current player count.
battle-selection-limit-reached = You have reached the fighter limit for this mode.
battle-selection-required-count = Select the required number of fighters before submitting.
battle-roster-unavailable-selection = Fighters are not available to view until selection is complete.
battle-team-action-unavailable = Allied and enemy fighter lists are only available to participating players in team-based modes.
