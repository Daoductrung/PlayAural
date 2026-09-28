game-name-lightturret = Light Turret

lightturret-intro = Light Turret begins with { $power } power capacity and { $rounds } complete rounds. Fire to gain light and twice as many coins. A turret overloads only when light exceeds power. Core upgrades cost { $cost } coins and may backfire.
lightturret-intro-brief = Light Turret: { $power } power, { $rounds } rounds, upgrades { $cost } coins.
lightturret-round-start = Round { $round } of { $total } begins with { $alive } active { $alive ->
    [one] turret
   *[other] turrets
}.
lightturret-round-start-brief = Round { $round }/{ $total }. Active: { $alive }.

lightturret-shoot = Fire turret
lightturret-shoot-safe-label = Fire turret; { $headroom } safe capacity
lightturret-shoot-risk-label = Fire turret; { $risk }% overload risk
lightturret-upgrade = Upgrade core
lightturret-upgrade-label = Upgrade core; costs { $cost } coins, you have { $coins }
lightturret-check-stats = View turret status

lightturret-you-shoot = You fire and gain { $gain } light plus { $coins } coins. Your turret is at { $light } of { $power } power, with { $headroom } safe capacity and { $total_coins } coins.
lightturret-player-shoots = { $player } fires and gains { $gain } light plus { $coins } coins. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } turret is at { $light } of { $power } power, with { $headroom } safe capacity and { $total_coins } coins.
lightturret-you-shoot-brief = You fire: +{ $gain } light, +{ $coins } coins. Light { $light }/{ $power}; coins { $total_coins }.
lightturret-player-shoots-brief = { $player } fires: +{ $gain } light, +{ $coins } coins. Light { $light }/{ $power}; coins { $total_coins }.

lightturret-you-shoot-overload = You fire and gain { $gain } light plus { $coins } coins, reaching { $light } light against { $power } power. You exceed capacity by { $overload } and are eliminated with { $total_coins } coins remaining.
lightturret-player-shoots-overload = { $player } fires and gains { $gain } light plus { $coins } coins, reaching { $light } light against { $power } power. The overload puts { GENDER_TERM($player_gender, "object") } { $overload } over capacity and eliminates { GENDER_TERM($player_gender, "object") } with { $total_coins } coins remaining.
lightturret-you-shoot-overload-brief = You overload: +{ $gain } light, { $light }/{ $power}, over by { $overload}. Eliminated.
lightturret-player-shoots-overload-brief = { $player } overloads: +{ $gain } light, { $light }/{ $power}, over by { $overload}. Eliminated.

lightturret-you-upgrade = You spend { $cost } coins and upgrade the core by { $gain } power. Your turret is now at { $light } light, { $power } power, { $headroom } safe capacity, and { $coins } coins.
lightturret-player-upgrades = { $player } spends { $cost } coins and upgrades the core by { $gain } power. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } turret is now at { $light } light, { $power } power, { $headroom } safe capacity, and { $coins } coins.
lightturret-you-upgrade-brief = You upgrade: +{ $gain } power. Light { $light }/{ $power}; coins { $coins }.
lightturret-player-upgrades-brief = { $player } upgrades: +{ $gain } power. Light { $light }/{ $power}; coins { $coins }.

lightturret-you-upgrade-accident = You spend { $cost } coins, but the core backfires and adds { $gain } light. Your turret is at { $light } of { $power } power, with { $headroom } safe capacity and { $coins } coins.
lightturret-player-upgrades-accident = { $player } spends { $cost } coins, but the core backfires and adds { $gain } light. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } turret is at { $light } of { $power } power, with { $headroom } safe capacity and { $coins } coins.
lightturret-you-upgrade-accident-brief = Your upgrade backfires: +{ $gain } light. Light { $light }/{ $power}; coins { $coins }.
lightturret-player-upgrades-accident-brief = { $player }'s upgrade backfires: +{ $gain } light. Light { $light }/{ $power}; coins { $coins }.

lightturret-you-upgrade-overload = You spend { $cost } coins, but the core backfires and adds { $gain } light. You reach { $light } light against { $power } power, exceed capacity by { $overload }, and are eliminated with { $coins } coins remaining.
lightturret-player-upgrades-overload = { $player } spends { $cost } coins, but the core backfires and adds { $gain } light. The backfire puts { GENDER_TERM($player_gender, "object") } at { $light } light against { $power } power, { $overload } over capacity, and eliminates { GENDER_TERM($player_gender, "object") } with { $coins } coins remaining.
lightturret-you-upgrade-overload-brief = Upgrade overload: +{ $gain } light, { $light }/{ $power}, over by { $overload}. Eliminated.
lightturret-player-upgrades-overload-brief = { $player } upgrade overload: +{ $gain } light, { $light }/{ $power}, over by { $overload}. Eliminated.

lightturret-action-resolving = Your turret action is already resolving. Wait for its sound and result to finish.
lightturret-not-enough-coins = You need { $need } coins to upgrade the core, but you have { $have }.
lightturret-you-are-eliminated = Your turret has overloaded and you are eliminated, so you cannot take another action.
lightturret-confirm-risky-shot = Firing now has a { $risk }% overload risk at { $light } light and { $power } power. Fire again within { $seconds } seconds to confirm.

lightturret-status-round = Round { $round } of { $total }. Active turrets: { $alive }.
lightturret-stats-alive = { $player}: { $light } light, { $power } power, { $headroom } safe capacity, { $coins } coins, next-shot overload risk { $risk }%.
lightturret-stats-eliminated = { $player}: eliminated at { $light } light against { $power } power.

lightturret-end-max-rounds = All { $total } rounds are complete. Final light totals decide the winner.
lightturret-end-max-rounds-brief = { $total } rounds complete.
lightturret-end-all-eliminated = Every turret has overloaded during round { $round }. Final light totals decide the winner.
lightturret-end-all-eliminated-brief = All turrets overloaded in round { $round }.

lightturret-you-win = You win with { $light } light and { $power } power. { $survived ->
    [true] Your turret survived.
   *[false] Your final light total leads despite the overload.
}
lightturret-player-wins = { $player } wins with { $light } light and { $power } power. { $survived ->
    [true] { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } turret survived.
   *[false] { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } final light total leads despite the overload.
}
lightturret-you-win-brief = You win: { $light } light.
lightturret-player-wins-brief = { $player } wins: { $light } light.
lightturret-you-tie = You tie for first with { $players } at { $light } light.
lightturret-players-tie = { $players } tie for first at { $light } light.
lightturret-you-tie-brief = You tie with { $players}: { $light } light.
lightturret-players-tie-brief = Tie: { $players}, { $light } light.

lightturret-set-starting-power = Starting power: { $power }
lightturret-enter-starting-power = Enter starting power:
lightturret-option-changed-power = Starting power set to { $power }.
lightturret-desc-starting-power = Each turret's initial overload capacity. Light equal to power is safe; only light above power overloads (default 10, range 5-30).
lightturret-set-max-rounds = Maximum rounds: { $rounds }
lightturret-enter-max-rounds = Enter maximum rounds:
lightturret-option-changed-rounds = Maximum rounds set to { $rounds }.
lightturret-desc-max-rounds = The number of complete rounds. Every active turret receives one turn in the final round (default 50, range 10-200).
lightturret-error-starting-power-invalid = Starting power must be between { $min } and { $max }; the current value is { $power }.
lightturret-error-max-rounds-invalid = Maximum rounds must be between { $min } and { $max }; the current value is { $rounds }.

lightturret-status-survived = Active
lightturret-status-eliminated = Eliminated
lightturret-end-winner = Winner: { $player } with { $light } light.
lightturret-end-tie = First-place tie: { $players } with { $light } light.
lightturret-line-format = { $rank }. { $player}: { $light } light, { $power } power, { $coins } coins, { $status }
