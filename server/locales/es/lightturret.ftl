game-name-lightturret = Torreta de Luz

lightturret-intro = Torreta de Luz empieza con { $power } de capacidad de energía y { $rounds } rondas completas. Dispara para ganar luz y el doble de monedas. Una torreta se sobrecarga solo cuando la luz supera la energía. Mejorar el núcleo cuesta { $cost } monedas y puede salir mal.
lightturret-intro-brief = Torreta de Luz: { $power } de energía, { $rounds } rondas, mejoras { $cost } monedas.
lightturret-round-start = La ronda { $round } de { $total } comienza con { $alive } { $alive ->
    [one] torreta activa
   *[other] torretas activas
}.
lightturret-round-start-brief = Ronda { $round }/{ $total }. Activas: { $alive }.

lightturret-shoot = Disparar torreta
lightturret-shoot-safe-label = Disparar torreta; { $headroom } de capacidad segura
lightturret-shoot-risk-label = Disparar torreta; { $risk }% de riesgo de sobrecarga
lightturret-upgrade = Mejorar núcleo
lightturret-upgrade-label = Mejorar núcleo; cuesta { $cost } monedas, tienes { $coins }
lightturret-check-stats = Ver estado de la torreta

lightturret-you-shoot = Disparas y ganas { $gain } de luz más { $coins } monedas. Tu torreta está en { $light } de { $power } de energía, con { $headroom } de capacidad segura y { $total_coins } monedas.
lightturret-player-shoots = { $player } dispara y gana { $gain } de luz más { $coins } monedas. Su torreta está en { $light } de { $power } de energía, con { $headroom } de capacidad segura y { $total_coins } monedas.
lightturret-you-shoot-brief = Disparas: +{ $gain } luz, +{ $coins } monedas. Luz { $light }/{ $power}; monedas { $total_coins }.
lightturret-player-shoots-brief = { $player } dispara: +{ $gain } luz, +{ $coins } monedas. Luz { $light }/{ $power}; monedas { $total_coins }.

lightturret-you-shoot-overload = Disparas y ganas { $gain } de luz más { $coins } monedas, llegando a { $light } de luz contra { $power } de energía. Superas la capacidad por { $overload } y quedas eliminado con { $total_coins } monedas restantes.
lightturret-player-shoots-overload = { $player } dispara y gana { $gain } de luz más { $coins } monedas, llegando a { $light } de luz contra { $power } de energía. Supera la capacidad por { $overload } y queda eliminado con { $total_coins } monedas restantes.
lightturret-you-shoot-overload-brief = Te sobrecargas: +{ $gain } luz, { $light }/{ $power}, excedido por { $overload}. Eliminado.
lightturret-player-shoots-overload-brief = { $player } se sobrecarga: +{ $gain } luz, { $light }/{ $power}, excedido por { $overload}. Eliminado.

lightturret-you-upgrade = Gastas { $cost } monedas y mejoras el núcleo en { $gain } de energía. Tu torreta ahora tiene { $light } de luz, { $power } de energía, { $headroom } de capacidad segura y { $coins } monedas.
lightturret-player-upgrades = { $player } gasta { $cost } monedas y mejora el núcleo en { $gain } de energía. Su torreta ahora tiene { $light } de luz, { $power } de energía, { $headroom } de capacidad segura y { $coins } monedas.
lightturret-you-upgrade-brief = Mejoras: +{ $gain } energía. Luz { $light }/{ $power}; monedas { $coins }.
lightturret-player-upgrades-brief = { $player } mejora: +{ $gain } energía. Luz { $light }/{ $power}; monedas { $coins }.

lightturret-you-upgrade-accident = Gastas { $cost } monedas, pero el núcleo falla y añade { $gain } de luz. Tu torreta está en { $light } de { $power } de energía, con { $headroom } de capacidad segura y { $coins } monedas.
lightturret-player-upgrades-accident = { $player } gasta { $cost } monedas, pero el núcleo falla y añade { $gain } de luz. Su torreta está en { $light } de { $power } de energía, con { $headroom } de capacidad segura y { $coins } monedas.
lightturret-you-upgrade-accident-brief = Tu mejora falla: +{ $gain } luz. Luz { $light }/{ $power}; monedas { $coins }.
lightturret-player-upgrades-accident-brief = La mejora de { $player } falla: +{ $gain } luz. Luz { $light }/{ $power}; monedas { $coins }.

lightturret-you-upgrade-overload = Gastas { $cost } monedas, pero el núcleo falla y añade { $gain } de luz. Llegas a { $light } de luz contra { $power } de energía, superas la capacidad por { $overload } y quedas eliminado con { $coins } monedas restantes.
lightturret-player-upgrades-overload = { $player } gasta { $cost } monedas, pero el núcleo falla y añade { $gain } de luz. Llega a { $light } de luz contra { $power } de energía, supera la capacidad por { $overload } y queda eliminado con { $coins } monedas restantes.
lightturret-you-upgrade-overload-brief = Sobrecarga por mejora: +{ $gain } luz, { $light }/{ $power}, excedido por { $overload}. Eliminado.
lightturret-player-upgrades-overload-brief = { $player } sobrecarga por mejora: +{ $gain } luz, { $light }/{ $power}, excedido por { $overload}. Eliminado.

lightturret-action-resolving = La acción de tu torreta ya se está resolviendo. Espera a que termine su sonido y resultado.
lightturret-not-enough-coins = Necesitas { $need } monedas para mejorar el núcleo, pero tienes { $have }.
lightturret-you-are-eliminated = Tu torreta se sobrecargó y quedaste eliminado, así que no puedes realizar otra acción.
lightturret-confirm-risky-shot = Disparar ahora tiene un { $risk }% de riesgo de sobrecarga con { $light } de luz y { $power } de energía. Dispara de nuevo dentro de { $seconds } segundos para confirmar.

lightturret-status-round = Ronda { $round } de { $total }. Torretas activas: { $alive }.
lightturret-stats-alive = { $player}: { $light } de luz, { $power } de energía, { $headroom } de capacidad segura, { $coins } monedas, riesgo de sobrecarga del próximo disparo { $risk }%.
lightturret-stats-eliminated = { $player}: eliminado con { $light } de luz contra { $power } de energía.

lightturret-end-max-rounds = Se completaron las { $total } rondas. Los totales finales de luz deciden al ganador.
lightturret-end-max-rounds-brief = { $total } rondas completadas.
lightturret-end-all-eliminated = Todas las torretas se sobrecargaron durante la ronda { $round }. Los totales finales de luz deciden al ganador.
lightturret-end-all-eliminated-brief = Todas las torretas se sobrecargaron en la ronda { $round }.

lightturret-you-win = Ganas con { $light } de luz y { $power } de energía. { $survived ->
    [true] Tu torreta sobrevivió.
   *[false] Tu total final de luz lidera a pesar de la sobrecarga.
}
lightturret-player-wins = { $player } gana con { $light } de luz y { $power } de energía. { $survived ->
    [true] Su torreta sobrevivió.
   *[false] Su total final de luz lidera a pesar de la sobrecarga.
}
lightturret-you-win-brief = Ganas: { $light } de luz.
lightturret-player-wins-brief = { $player } gana: { $light } de luz.
lightturret-you-tie = Empatas el primer lugar con { $players } con { $light } de luz.
lightturret-players-tie = { $players } empatan el primer lugar con { $light } de luz.
lightturret-you-tie-brief = Empatas con { $players}: { $light } de luz.
lightturret-players-tie-brief = Empate: { $players}, { $light } de luz.

lightturret-set-starting-power = Energía inicial: { $power }
lightturret-enter-starting-power = Ingresa la energía inicial:
lightturret-option-changed-power = Energía inicial establecida en { $power }.
lightturret-desc-starting-power = Capacidad de sobrecarga inicial de cada torreta. La luz igual a la energía es segura; solo la luz por encima de la energía provoca sobrecarga (por defecto 10, rango 5-30).
lightturret-set-max-rounds = Máximo de rondas: { $rounds }
lightturret-enter-max-rounds = Ingresa el máximo de rondas:
lightturret-option-changed-rounds = Máximo de rondas establecido en { $rounds }.
lightturret-desc-max-rounds = La cantidad de rondas completas. Cada torreta activa recibe un turno en la ronda final (por defecto 50, rango 10-200).
lightturret-error-starting-power-invalid = La energía inicial debe estar entre { $min } y { $max }; el valor actual es { $power }.
lightturret-error-max-rounds-invalid = El máximo de rondas debe estar entre { $min } y { $max }; el valor actual es { $rounds }.

lightturret-status-survived = Activa
lightturret-status-eliminated = Eliminada
lightturret-end-winner = Ganador: { $player } con { $light } de luz.
lightturret-end-tie = Empate en primer lugar: { $players } con { $light } de luz.
lightturret-line-format = { $rank }. { $player}: { $light } de luz, { $power } de energía, { $coins } monedas, { $status }
