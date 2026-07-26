game-name-yahtzee = Yahtzee

yahtzee-roll = Volver a lanzar (quedan { $count })
yahtzee-roll-all = Lanzar dados

yahtzee-score-ones = Unos por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-twos = Doses por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-threes = Treses por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-fours = Cuatros por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-fives = Cincos por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-sixes = Seises por { $points } { $points ->
    [one] punto
   *[other] puntos
}

yahtzee-score-three-kind = Trío por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-four-kind = Póker por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-full-house = Full por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-small-straight = Escalera Pequeña por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-large-straight = Escalera Grande por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-yahtzee = Yahtzee por { $points } { $points ->
    [one] punto
   *[other] puntos
}
yahtzee-score-chance = Oportunidad por { $points } { $points ->
    [one] punto
   *[other] puntos
}

yahtzee-you-rolled = Sacaste: { $dice }. { $remaining ->
    [0] Elige una categoría de puntuación.
   *[other] Quedan { $remaining } { $remaining ->
        [one] lanzamiento
       *[other] lanzamientos
    }.
}
yahtzee-player-rolled = { $player } sacó: { $dice }. { $remaining ->
    [0] Debe elegir una categoría de puntuación.
   *[other] Quedan { $remaining } { $remaining ->
        [one] lanzamiento
       *[other] lanzamientos
    }.
}
yahtzee-you-rolled-brief = Sacaste: { $dice }.
yahtzee-player-rolled-brief = { $player } sacó: { $dice }.

yahtzee-you-scored = Anotaste { $points } { $points ->
    [one] punto
   *[other] puntos
} en { $category }.
yahtzee-player-scored = { $player } anotó { $points } { $points ->
    [one] punto
   *[other] puntos
} en { $category }.
yahtzee-you-scored-brief = { $points } en { $category }.
yahtzee-player-scored-brief = { $player }: { $points } en { $category }.

yahtzee-you-bonus = ¡Bonificación de Yahtzee! +100 puntos
yahtzee-player-bonus = ¡{ $player } obtuvo una bonificación de Yahtzee! +100 puntos
yahtzee-you-bonus-brief = Bonificación de Yahtzee, +100.
yahtzee-player-bonus-brief = { $player }: bonificación de Yahtzee, +100.

yahtzee-you-upper-bonus = ¡Bonificación de la sección superior! +35 puntos ({ $total } en la sección superior)
yahtzee-player-upper-bonus = ¡{ $player } obtuvo la bonificación de la sección superior! +35 puntos ({ $total } en la sección superior)
yahtzee-you-upper-bonus-brief = Bonificación superior, +35.
yahtzee-player-upper-bonus-brief = { $player }: bonificación superior, +35.
yahtzee-you-upper-bonus-missed = No lograste la bonificación de la sección superior. Anotaste { $total }; necesitabas { $needed } más.
yahtzee-player-upper-bonus-missed = { $player } no logró la bonificación de la sección superior con { $total } en la sección superior, le faltaron { $needed }.
yahtzee-you-upper-bonus-missed-brief = Bonificación superior fallida; faltaron { $needed }.
yahtzee-player-upper-bonus-missed-brief = { $player }: bonificación superior fallida, faltaron { $needed }.

yahtzee-check-scoresheet = Ver planilla
yahtzee-check-all-scorecards = Ver planilla de todos los jugadores
yahtzee-select-scorecard-player = Elige la planilla de un jugador.
yahtzee-scorecard-no-players = Aún no hay jugadores activos con planilla en esta partida.
yahtzee-scorecard-player-unavailable = Ese jugador ya no está disponible para ver. Abre la lista de planillas de nuevo y elige un jugador activo.
yahtzee-view-dice = Ver mano
yahtzee-your-dice = Tus dados: { $dice }.
yahtzee-your-dice-kept = Tus dados: { $dice }. Guardando: { $kept }.
yahtzee-current-dice = Dados de { $player }: { $dice }.
yahtzee-current-dice-kept = Dados de { $player }: { $dice }. Guardando: { $kept }.
yahtzee-not-rolled = El jugador actual todavía no ha lanzado.

yahtzee-scoresheet-header = Planilla de { $player }
yahtzee-scoresheet-upper = Sección superior:
yahtzee-scoresheet-lower = Sección inferior:
yahtzee-scoresheet-upper-total-bonus = Total superior: { $total } (bonificación: +35)
yahtzee-scoresheet-upper-total-needed = Total superior: { $total } (faltan { $needed } para la bonificación)
yahtzee-scoresheet-yahtzee-bonus = Bonificaciones de Yahtzee: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = Puntuación total: { $total }

yahtzee-category-ones = Unos
yahtzee-category-twos = Doses
yahtzee-category-threes = Treses
yahtzee-category-fours = Cuatros
yahtzee-category-fives = Cincos
yahtzee-category-sixes = Seises
yahtzee-category-three-kind = Trío
yahtzee-category-four-kind = Póker
yahtzee-category-full-house = Full
yahtzee-category-small-straight = Escalera Pequeña
yahtzee-category-large-straight = Escalera Grande
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Oportunidad

yahtzee-you-win = ¡Ganas con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
yahtzee-player-wins = ¡{ $player } gana con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
yahtzee-winners-tie = ¡Es un empate! ¡{ $players } anotaron { $score } puntos!

yahtzee-set-rounds = Número de partidas: { $rounds }
yahtzee-enter-rounds = Ingresa el número de partidas (1-10):
yahtzee-option-changed-rounds = Número de partidas establecido en { $rounds }.
yahtzee-desc-num-games = Cuántas planillas completas de Yahtzee se juegan antes de comparar los totales finales (por defecto 1, rango 1-10).

yahtzee-no-rolls-left = No te quedan lanzamientos; elige una categoría de puntuación abierta para terminar tu turno.
yahtzee-roll-first = Lanza los dados antes de elegir una categoría de puntuación.
yahtzee-category-filled = Esa categoría ya tiene una puntuación. Elige una categoría que siga abierta en tu planilla.
yahtzee-joker-upper-required = Regla del comodín: como este Yahtzee muestra { $face }, debes anotar primero la casilla de la sección superior para { $face } antes que cualquier otra categoría.
yahtzee-joker-lower-required = Regla del comodín: la casilla de la sección superior para { $face } ya está ocupada, así que debes elegir una categoría abierta de la sección inferior antes de usar otra casilla de la sección superior.
