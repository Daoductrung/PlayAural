game-name-midnight = 1-4-24

midnight-roll = Lanzar los dados
midnight-keep-die = Guardar { $value }
midnight-bank = Guardar puntuación
midnight-check-dice = Leer dados actuales
midnight-check-round-status = Ver estado de la ronda

midnight-round-start = Ronda { $round } de { $total }.
midnight-round-start-brief = Ronda { $round }/{ $total }.

midnight-you-rolled = Sacaste: { $dice }.
midnight-player-rolled = { $player } sacó: { $dice }.
midnight-you-rolled-brief = Sacas { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = Guardas el dado { $index }, que muestra { $die }.
midnight-player-keeps = { $player } guarda el dado { $index }, que muestra { $die }.
midnight-you-keep-brief = Guardas { $die }.
midnight-player-keeps-brief = { $player } guarda { $die }.
midnight-you-unkeep = Devuelves el dado { $index }, que muestra { $die }, al grupo para volver a lanzar.
midnight-player-unkeeps = { $player } devuelve el dado { $index }, que muestra { $die }, al grupo para volver a lanzar.
midnight-you-unkeep-brief = Vuelves a lanzar { $die }.
midnight-player-unkeeps-brief = { $player } vuelve a lanzar { $die }.

midnight-you-scored = Calificas con 1 y 4, anotando { $score } con { $scoring_dice }.
midnight-scored = { $player } califica con 1 y 4, anotando { $score } con { $scoring_dice }.
midnight-you-scored-brief = Anotas { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = No calificas porque te falta { $missing }.
midnight-player-disqualified = { $player } no califica porque le falta { $missing }.
midnight-you-disqualified-brief = Te falta { $missing }.
midnight-player-disqualified-brief = A { $player } le falta { $missing }.

midnight-you-win-round = Ganas la ronda { $round } con { $score }.
midnight-round-winner = { $player } gana la ronda { $round } con { $score }.
midnight-you-win-round-brief = Ganas R{ $round }: { $score }.
midnight-round-winner-brief = { $player } gana R{ $round }: { $score }.
midnight-round-tie = Ronda empatada en { $score } entre { $players }. No se otorga victoria de ronda.
midnight-all-disqualified = Ningún jugador consiguió el 1 y el 4 requeridos. No se otorga victoria de ronda.
midnight-all-disqualified-brief = Nadie califica.

midnight-you-win-game = ¡Ganas la partida con { $wins } { $wins ->
    [one] ronda ganada
   *[other] rondas ganadas
}!
midnight-game-winner = ¡{ $player } gana la partida con { $wins } { $wins ->
    [one] ronda ganada
   *[other] rondas ganadas
}!
midnight-you-win-game-brief = Ganas: { $wins }.
midnight-game-winner-brief = { $player } gana: { $wins }.
midnight-game-tie = Es un empate en la partida. { $players } terminaron con { $wins } { $wins ->
    [one] ronda ganada
   *[other] rondas ganadas
} cada uno.

midnight-set-rounds = Rondas a jugar: { $rounds }
midnight-enter-rounds = Ingresa el número de rondas a jugar:
midnight-option-changed-rounds = Rondas a jugar cambiadas a { $rounds }
midnight-desc-rounds = Cantidad de rondas de 1-4-24 a jugar antes de la puntuación final (por defecto 5, rango 1-20).
midnight-error-rounds-out-of-range = 1-4-24 admite de { $min } a { $max } rondas. Configuración actual: { $rounds }.

midnight-need-to-roll = Lanza los dados antes de elegir cuáles guardar.
midnight-no-dice-to-keep = No quedan dados para lanzar o guardar.
midnight-must-keep-one = Guarda al menos un dado recién lanzado antes de volver a lanzar.
midnight-must-roll-first = Lanza los dados antes de guardar tu puntuación de turno.
midnight-keep-all-first = Decide cada dado antes de guardar. Primero guarda o devuelve todos los dados sin bloquear.
midnight-invalid-die-index = Ese dado no está disponible en esta tirada.

midnight-die-locked = { $value } (bloqueado)
midnight-die-kept = { $value } (guardado)
midnight-die-value = { $value }
midnight-die-index = Dado { $index }

midnight-your-dice-not-rolled = Aún no has lanzado en este turno.
midnight-player-dice-not-rolled = { $player } aún no ha lanzado en este turno.
midnight-your-dice-status =
    { $qualified ->
        [yes] Tus dados: { $dice }. Bloqueados: { $locked }; guardados para la siguiente tirada: { $kept }; dados aún en juego: { $remaining }. La puntuación calificada actual sería { $score } con { $scoring_dice }.
       *[no] Tus dados: { $dice }. Bloqueados: { $locked }; guardados para la siguiente tirada: { $kept }; dados aún en juego: { $remaining }. Todavía necesitas { $missing } para calificar.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] Dados de { $player }: { $dice }. Bloqueados: { $locked }; guardados para la siguiente tirada: { $kept }; dados aún en juego: { $remaining }. La puntuación calificada actual sería { $score } con { $scoring_dice }.
       *[no] Dados de { $player }: { $dice }. Bloqueados: { $locked }; guardados para la siguiente tirada: { $kept }; dados aún en juego: { $remaining }. Todavía necesita { $missing } para calificar.
    }

midnight-status-round = Ronda { $round } de { $total }
midnight-status-current-player = Turno actual: { $player }
midnight-status-current-not-rolled = { $player } aún no ha lanzado.
midnight-status-current-dice =
    { $qualified ->
        [yes] Dados actuales de { $player }: { $dice }. Puntuación potencial: { $score } con { $scoring_dice }. Bloqueados { $locked }, guardados { $kept}, en juego { $remaining}.
       *[no] Dados actuales de { $player }: { $dice }. Falta { $missing}. Bloqueados { $locked }, guardados { $kept}, en juego { $remaining}.
    }
midnight-status-dice-not-rolled = sin lanzar
midnight-status-last-qualified = Último turno: { $player } sacó { $dice } y anotó { $score }.
midnight-status-last-disqualified = Último turno: { $player } sacó { $dice } y no calificó.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } rondas ganadas; ronda actual { $current}, calificado.
       *[no] { $rank }. { $player }: { $wins } rondas ganadas; ronda actual { $current}, no calificado.
    }

midnight-score-unit-round-wins = { $count ->
    [one] ronda ganada
   *[other] rondas ganadas
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] ronda ganada
   *[other] rondas ganadas
}
