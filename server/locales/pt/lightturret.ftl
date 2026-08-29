game-name-lightturret = Torreta de Luz

lightturret-intro = Light Turret começa com { $power } de capacidade de energia e { $rounds } rodadas completas. Dispare para ganhar luz e o dobro de moedas. Uma torre só sofre sobrecarga quando a luz excede a energia. Os upgrades de núcleo custam { $cost } moedas e podem falhar.
lightturret-intro-brief = Light Turret: { $power } energia, { $rounds } rodadas, upgrades { $cost } moedas.
lightturret-round-start = A rodada { $round } de { $total } começa com { $alive } { $alive ->
    [one] torre ativa
   *[other] torres ativas
}.
lightturret-round-start-brief = Rodada { $round }/{ $total }. Ativas: { $alive }.

lightturret-shoot = Disparar torre
lightturret-shoot-safe-label = Disparar torre; { $headroom } de capacidade segura
lightturret-shoot-risk-label = Disparar torre; { $risk }% de risco de sobrecarga
lightturret-upgrade = Atualizar núcleo
lightturret-upgrade-label = Atualizar núcleo; custa { $cost } moedas, você tem { $coins }
lightturret-check-stats = Ver status da torre

lightturret-you-shoot = Você dispara e ganha { $gain } de luz mais { $coins } moedas. Sua torre está em { $light } de { $power } de energia, com { $headroom } de capacidade segura e { $total_coins } moedas.
lightturret-player-shoots = { $player } dispara e ganha { $gain } de luz mais { $coins } moedas. A torre dele está em { $light } de { $power } de energia, com { $headroom } de capacidade segura e { $total_coins } moedas.
lightturret-you-shoot-brief = Você dispara: +{ $gain } luz, +{ $coins } moedas. Luz { $light }/{ $power}; moedas { $total_coins }.
lightturret-player-shoots-brief = { $player } dispara: +{ $gain } luz, +{ $coins } moedas. Luz { $light }/{ $power}; moedas { $total_coins }.

lightturret-you-shoot-overload = Você dispara e ganha { $gain } de luz mais { $coins } moedas, atingindo { $light } de luz contra { $power } de energia. Você excede a capacidade em { $overload } e é eliminado com { $total_coins } moedas restantes.
lightturret-player-shoots-overload = { $player } dispara e ganha { $gain } de luz mais { $coins } moedas, atingindo { $light } de luz contra { $power } de energia. Ele excede a capacidade em { $overload } e é eliminado com { $total_coins } moedas restantes.
lightturret-you-shoot-overload-brief = Você sofre sobrecarga: +{ $gain } luz, { $light }/{ $power}, excedido em { $overload}. Eliminado.
lightturret-player-shoots-overload-brief = { $player } sofre sobrecarga: +{ $gain } luz, { $light }/{ $power}, excedido em { $overload}. Eliminado.

lightturret-you-upgrade = Você gasta { $cost } moedas e atualiza o núcleo em { $gain } de energia. Sua torre agora está em { $light } de luz, { $power } de energia, { $headroom } de capacidade segura e { $coins } moedas.
lightturret-player-upgrades = { $player } gasta { $cost } moedas e atualiza o núcleo em { $gain } de energia. A torre dele agora está em { $light } de luz, { $power } de energia, { $headroom } de capacidade segura e { $coins } moedas.
lightturret-you-upgrade-brief = Você atualiza: +{ $gain } energia. Luz { $light }/{ $power}; moedas { $coins }.
lightturret-player-upgrades-brief = { $player } atualiza: +{ $gain } energia. Luz { $light }/{ $power}; moedas { $coins }.

lightturret-you-upgrade-accident = Você gasta { $cost } moedas, mas o núcleo falha e adiciona { $gain } de luz. Sua torre está em { $light } de { $power } de energia, com { $headroom } de capacidade segura e { $coins } moedas.
lightturret-player-upgrades-accident = { $player } gasta { $cost } moedas, mas o núcleo falha e adiciona { $gain } de luz. A torre dele está em { $light } de { $power } de energia, com { $headroom } de capacidade segura e { $coins } moedas.
lightturret-you-upgrade-accident-brief = Sua atualização falha: +{ $gain } luz. Luz { $light }/{ $power}; moedas { $coins }.
lightturret-player-upgrades-accident-brief = A atualização de { $player } falha: +{ $gain } luz. Luz { $light }/{ $power}; moedas { $coins }.

lightturret-you-upgrade-overload = Você gasta { $cost } moedas, mas o núcleo falha e adiciona { $gain } de luz. Você atinge { $light } de luz contra { $power } de energia, excede a capacidade em { $overload } e é eliminado com { $coins } moedas restantes.
lightturret-player-upgrades-overload = { $player } gasta { $cost } moedas, mas o núcleo falha e adiciona { $gain } de luz. Ele atinge { $light } de luz contra { $power } de energia, excede a capacidade em { $overload } e é eliminado com { $coins } moedas restantes.
lightturret-you-upgrade-overload-brief = Sobrecarga na atualização: +{ $gain } luz, { $light }/{ $power}, excedido em { $overload}. Eliminado.
lightturret-player-upgrades-overload-brief = Sobrecarga na atualização de { $player }: +{ $gain } luz, { $light }/{ $power}, excedido em { $overload}. Eliminado.

lightturret-action-resolving = A ação da sua torre já está sendo resolvida. Aguarde o som e o resultado terminarem.
lightturret-not-enough-coins = Você precisa de { $need } moedas para atualizar o núcleo, mas tem { $have }.
lightturret-you-are-eliminated = Sua torre sofreu sobrecarga e você foi eliminado, portanto não pode realizar outra ação.
lightturret-confirm-risky-shot = Disparar agora tem um risco de sobrecarga de { $risk }% com { $light } de luz e { $power } de energia. Dispare novamente em até { $seconds } segundos para confirmar.

lightturret-status-round = Rodada { $round } de { $total }. Torres ativas: { $alive }.
lightturret-stats-alive = { $player}: { $light } luz, { $power } energia, { $headroom } capacidade segura, { $coins } moedas, risco de sobrecarga no próximo disparo { $risk }%.
lightturret-stats-eliminated = { $player}: eliminado com { $light } de luz contra { $power } de energia.

lightturret-end-max-rounds = Todas as { $total } rodadas foram concluídas. Os totais finais de luz decidem o vencedor.
lightturret-end-max-rounds-brief = { $total } rodadas concluídas.
lightturret-end-all-eliminated = Todas as torres sofreram sobrecarga durante a rodada { $round }. Os totais finais de luz decidem o vencedor.
lightturret-end-all-eliminated-brief = Todas as torres sofreram sobrecarga na rodada { $round }.

lightturret-you-win = Você venceu com { $light } de luz e { $power } de energia. { $survived ->
    [true] Sua torre sobreviveu.
   *[false] Seu total final de luz lidera apesar da sobrecarga.
}
lightturret-player-wins = { $player } venceu com { $light } de luz e { $power } de energia. { $survived ->
    [true] A torre dele sobreviveu.
   *[false] O total final de luz dele lidera apesar da sobrecarga.
}
lightturret-you-win-brief = Você vence: { $light } de luz.
lightturret-player-wins-brief = { $player } vence: { $light } de luz.
lightturret-you-tie = Você empata em primeiro lugar com { $players } com { $light } de luz.
lightturret-players-tie = { $players } empatam em primeiro lugar com { $light } de luz.
lightturret-you-tie-brief = Você empata com { $players}: { $light } de luz.
lightturret-players-tie-brief = Empate: { $players}, { $light } de luz.

lightturret-set-starting-power = Energia inicial: { $power }
lightturret-enter-starting-power = Digite a energia inicial:
lightturret-option-changed-power = Energia inicial definida para { $power }.
lightturret-desc-starting-power = A capacidade inicial de sobrecarga de cada torre. Luz igual à energia é segura; apenas luz acima da energia causa sobrecarga (padrão 10, intervalo de 5 a 30).
lightturret-set-max-rounds = Máximo de rodadas: { $rounds }
lightturret-enter-max-rounds = Digite o máximo de rodadas:
lightturret-option-changed-rounds = Máximo de rodadas definido para { $rounds }.
lightturret-desc-max-rounds = O número de rodadas completas. Cada torre ativa recebe um turno na rodada final (padrão 50, intervalo de 10 a 200).
lightturret-error-starting-power-invalid = A energia inicial deve estar entre { $min } e { $max }; o valor atual é { $power }.
lightturret-error-max-rounds-invalid = O máximo de rodadas deve estar entre { $min } e { $max }; o valor atual é { $rounds }.

lightturret-status-survived = Ativa
lightturret-status-eliminated = Eliminada
lightturret-end-winner = Vencedor: { $player } com { $light } de luz.
lightturret-end-tie = Empate no primeiro lugar: { $players } com { $light } de luz.
lightturret-line-format = { $rank }. { $player}: { $light } luz, { $power } energia, { $coins } moedas, { $status }
