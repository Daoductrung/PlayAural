game-name-bunko = Bunko

bunko-roll = Lanzar los dados
bunko-check-status = Ver estado
bunko-check-last-roll = Ver última tirada

bunko-game-start = Comienza Bunko. Jugadores: { $players }.
bunko-round-start = Ronda { $round } de { $total_rounds }. El número objetivo de esta ronda es { $target }.
bunko-round-start-brief = Ronda { $round }/{ $total_rounds }. Objetivo { $target }.
bunko-you-win-round = Ganas la ronda { $round } con { $score } puntos contra el objetivo { $target }.
bunko-player-wins-round = { $player } gana la ronda { $round } con { $score } puntos contra el objetivo { $target }.
bunko-you-win-round-brief = Ganas R{ $round }: { $score }.
bunko-player-wins-round-brief = { $player } gana R{ $round }: { $score }.

bunko-you-roll-match = Sacas { $dice } y anotas { $points } { $points ->
    [one] punto
   *[other] puntos
} hacia el objetivo { $target }. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-player-rolls-match = { $player } saca { $dice } y anota { $points } { $points ->
    [one] punto
   *[other] puntos
} hacia el objetivo { $target }. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-you-roll-match-brief = Tú: { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.
bunko-player-rolls-match-brief = { $player }: { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.

bunko-you-roll-mini_bunko = Sacas { $dice }, anotas un mini Bunko porque todos los dados coinciden entre sí pero no con el objetivo { $target }, y ganas { $points } puntos. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-player-rolls-mini_bunko = { $player } saca { $dice }, anota un mini Bunko porque todos los dados coinciden entre sí pero no con el objetivo { $target }, y gana { $points } puntos. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-you-roll-mini_bunko-brief = Tú: mini Bunko { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.
bunko-player-rolls-mini_bunko-brief = { $player }: mini Bunko { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.

bunko-you-roll-bunko = Sacas { $dice } y anotas un Bunko: tres { $target } para { $points } puntos. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-player-rolls-bunko = { $player } saca { $dice } y anota un Bunko: tres { $target } para { $points } puntos. Total de la ronda: { $round_total }. Puntuación general: { $total }.
bunko-you-roll-bunko-brief = Tú: Bunko { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.
bunko-player-rolls-bunko-brief = { $player }: Bunko { $dice }, +{ $points }. Ronda { $round_total }; total { $total }.

bunko-you-roll-no_score = Sacas { $dice } y no anotas nada porque ningún dado coincide con el objetivo { $target } y no hay mini Bunko. Tu turno pasa.
bunko-player-rolls-no_score = { $player } saca { $dice } y no anota nada porque ningún dado coincide con el objetivo { $target } y no hay mini Bunko. El turno pasa.
bunko-you-roll-no_score-brief = Tú: { $dice }, 0. Pasas.
bunko-player-rolls-no_score-brief = { $player }: { $dice }, 0. Pasa.

bunko-last-roll-none = Aún no se ha hecho ninguna tirada esta ronda.
bunko-last-roll-match = { $player } sacó por última vez { $dice } y anotó { $points } { $points ->
    [one] punto
   *[other] puntos
} hacia el objetivo { $target }.
bunko-last-roll-match-you = Sacaste por última vez { $dice } y anotaste { $points } { $points ->
    [one] punto
   *[other] puntos
} hacia el objetivo { $target }.
bunko-last-roll-mini_bunko = { $player } sacó por última vez { $dice } para un mini Bunko, anotando { $points } puntos porque los dados coincidieron entre sí pero no con el objetivo { $target }.
bunko-last-roll-mini_bunko-you = Sacaste por última vez { $dice } para un mini Bunko, anotando { $points } puntos porque los dados coincidieron entre sí pero no con el objetivo { $target }.
bunko-last-roll-bunko = { $player } sacó por última vez { $dice } para un Bunko: tres { $target }, con un valor de { $points } puntos.
bunko-last-roll-bunko-you = Sacaste por última vez { $dice } para un Bunko: tres { $target }, con un valor de { $points } puntos.
bunko-last-roll-no_score = { $player } sacó por última vez { $dice } y no anotó nada contra el objetivo { $target }.
bunko-last-roll-no_score-you = Sacaste por última vez { $dice } y no anotaste nada contra el objetivo { $target }.

bunko-status-round = Ronda { $round } de { $total_rounds }. Número objetivo: { $target }.
bunko-status-turn = Jugador actual: { $player }.
bunko-status-leader = Líder: { $player } con { $rounds } { $rounds ->
    [one] ronda ganada
   *[other] rondas ganadas
} y { $total } puntos en general.

bunko-standings-header = Clasificación. Ganador decidido por { $mode }.
bunko-score-line = { $rank }. { $player }: { $rounds } { $rounds ->
    [one] ronda ganada
   *[other] rondas ganadas
}, { $total } puntos en general, { $current } esta ronda, { $bunkos } { $bunkos ->
    [one] Bunko
   *[other] Bunkos
}, { $mini_bunkos } { $mini_bunkos ->
    [one] mini Bunko
   *[other] mini Bunkos
}

bunko-roll-already-resolving = Tus dados todavía están rodando. Espera el resultado antes de volver a lanzar.
bunko-error-round-count-invalid = Bunko requiere entre { $min } y { $max } rondas. El valor actual es { $count }.
bunko-error-winning-mode-invalid = Bunko no admite el modo de victoria "{ $mode }". Elige rondas ganadas o puntuación total.

bunko-set-round-count = Rondas: { $count }
bunko-enter-round-count = Ingresa el número de rondas:
bunko-option-changed-round-count = Número de rondas cambiado a { $count }.
bunko-desc-round-count = Cuántas rondas de Bunko se juegan antes de decidir al ganador (por defecto 6, rango 1-12).

bunko-set-winning-mode = Modo de victoria: { $mode }
bunko-select-winning-mode = Selecciona el modo de victoria:
bunko-option-changed-winning-mode = Modo de victoria cambiado a { $mode }.
bunko-desc-winning-mode = Define si los ganadores de Bunko se clasifican por rondas ganadas o por puntuación total.
bunko-winning-mode-round-wins = rondas ganadas
bunko-winning-mode-total-score = puntuación total
