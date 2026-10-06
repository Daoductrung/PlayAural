game-name-zombiedice = Zombie Dice

zombiedice-set-target-score = Cerebros necesarios para ganar: { $score }
zombiedice-enter-target-score = Ingresa un objetivo de victoria de 5 a 50 cerebros:
zombiedice-option-changed-target-score = El objetivo de victoria ahora es de { $score } cerebros.
zombiedice-desc-target-score = Alcanzar esta puntuación inicia la ronda final para los jugadores que aún no hayan jugado. El objetivo oficial es de 13 cerebros; un objetivo menor o mayor acorta o alarga la partida.

zombiedice-roll-first = Lanzar 3 dados
zombiedice-roll-first-description = Saca tres dados ocultos del cubilete y lánzalos.
zombiedice-roll-again = Volver a lanzar — { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
} en juego
zombiedice-roll-again-description = Vuelve a lanzar { $footprints } { $footprints ->
    [one] dado con huella
   *[other] dados con huellas
} y saca { $draw } { $draw ->
    [one] dado nuevo
   *[other] dados nuevos
} hasta tener tres. Un tercer disparo elimina los { $brains } { $brains ->
    [one] cerebro sin guardar
   *[other] cerebros sin guardar
}.
zombiedice-bank = Parar y puntuar { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}
zombiedice-bank-keybind = Parar y puntuar
zombiedice-bank-description = Termina tu turno y guarda { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}.
zombiedice-check-turn-totals = Ver totales del turno
zombiedice-check-turn-totals-description = Escucha los cerebros, disparos y huellas actuales.
zombiedice-review-turn = Revisar turno actual
zombiedice-review-turn-description = Revisa todos los dados públicos, la cantidad de dados en el cubilete, la última tirada y los cerebros sin guardar.
zombiedice-review-table = Revisar mesa
zombiedice-review-table-description = Revisa el objetivo, la fase de la partida, el orden de turnos, el turno actual y las puntuaciones.

zombiedice-game-start = Comienza Zombie Dice. Objetivo: { $target } cerebros. { $first } juega primero. Orden: { $order }.
zombiedice-your-turn = Tu turno. Guardados: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}. Lanza tres dados.
zombiedice-player-turn = Turno de { $player }. Guardados: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.
zombiedice-you-refill-cup = Quedan pocos dados en el cubilete: devuelves { $count } { $count ->
    [one] dado con cerebro
   *[other] dados con cerebros
}. { $brains ->
    [one] Tu cuenta de este turno se mantiene en { $brains } cerebro.
   *[other] Tu cuenta de este turno se mantiene en { $brains } cerebros.
}
zombiedice-player-refills-cup = Quedan pocos dados en el cubilete: { $player } devuelve { $count } { $count ->
    [one] dado con cerebro
   *[other] dados con cerebros
}. { $brains ->
    [one] La cuenta de este turno de { $player } se mantiene en { $brains } cerebro.
   *[other] La cuenta de este turno de { $player } se mantiene en { $brains } cerebros.
}
zombiedice-you-roll = Lanzas: { $results }.
zombiedice-player-rolls = { $player } lanza: { $results }.
zombiedice-you-bust = Lanzas: { $results }. { $shotguns } disparos: te acribillan. Pierdes { $brains } { $brains ->
    [one] cerebro sin guardar
   *[other] cerebros sin guardar
}.
zombiedice-player-busts = { $player } lanza: { $results }. { $shotguns } disparos: queda acribillado. { $player } pierde { $brains } { $brains ->
    [one] cerebro sin guardar
   *[other] cerebros sin guardar
}.
zombiedice-you-bank = Guardas { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}. Total: { $total }.
zombiedice-player-banks = { $player } guarda { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}. Total: { $total }.
zombiedice-you-trigger-final-round = Alcanzas { $score } cerebros. { $remaining ->
    [one] Queda 1 jugador
   *[other] Quedan { $remaining } jugadores
} en la ronda final.
zombiedice-player-triggers-final-round = { $player } alcanza { $score } cerebros. { $remaining ->
    [one] Queda 1 jugador
   *[other] Quedan { $remaining } jugadores
} en la ronda final.
zombiedice-tiebreak-start = Desempate { $round }: { $players }, empatados con { $score } cerebros. Un turno para cada uno.
zombiedice-you-win = Ganas Zombie Dice con { $score } cerebros.
zombiedice-player-wins = { $player } gana Zombie Dice con { $score } cerebros.

zombiedice-error-roll-before-stopping = Lanza una vez antes de parar. Después de cualquier tirada segura, puedes parar con 0 cerebros.
zombiedice-error-roll-resolving = Los dados todavía están rodando.
zombiedice-error-target-score-range = El objetivo de victoria debe estar entre { $min } y { $max } cerebros; el valor actual es { $value }.

zombiedice-color-green = verde
zombiedice-color-yellow = amarillo
zombiedice-color-red = rojo
zombiedice-face-brain = cerebro
zombiedice-face-footprint = huella
zombiedice-face-shotgun = disparo
zombiedice-roll-result = { $color }, { $face }
zombiedice-pool-color = { $count } { $count ->
    [one] dado { $color }
   *[other] dados { $color }
}
zombiedice-no-dice = ninguno

zombiedice-status-no-turn = No hay ningún turno activo de Zombie Dice.
zombiedice-your-turn-totals = Tú: { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}, { $shotguns } { $shotguns ->
    [one] disparo
   *[other] disparos
} y { $footprints } { $footprints ->
    [one] huella
   *[other] huellas
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}, { $shotguns } { $shotguns ->
    [one] disparo
   *[other] disparos
} y { $footprints } { $footprints ->
    [one] huella
   *[other] huellas
}.
zombiedice-status-turn-you = Tu turno — guardados: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.
zombiedice-status-turn-player = Turno de { $player } — guardados: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.
zombiedice-status-turn-totals = Este turno: { $brains } { $brains ->
    [one] cerebro
   *[other] cerebros
}, { $shotguns } { $shotguns ->
    [one] disparo
   *[other] disparos
} y { $footprints } { $footprints ->
    [one] huella
   *[other] huellas
}.
zombiedice-status-cup = Cubilete: { $count } { $count ->
    [one] dado
   *[other] dados
}.
zombiedice-status-footprints = Huellas que se volverán a lanzar: { $dice }.
zombiedice-status-brain-dice = Dados con cerebros apartados: { $dice }.
zombiedice-status-shotgun-dice = Dados con disparos apartados: { $dice }.
zombiedice-status-last-roll = Última tirada: { $results }.
zombiedice-status-awaiting-roll = Todavía no hay ninguna tirada en este turno.
zombiedice-status-table-header = Zombie Dice — ronda { $round }; objetivo: { $target } cerebros.
zombiedice-status-table-header-tiebreak = Zombie Dice — objetivo: { $target } cerebros.
zombiedice-status-main-round = Fase: partida principal.
zombiedice-status-final-round = Ronda final — { $player } alcanzó el objetivo.
zombiedice-status-tiebreak = Desempate { $round }: { $players }.
zombiedice-status-current-you = Tu turno.
zombiedice-status-current-player = Turno de { $player }.
zombiedice-status-turn-order = Orden de turnos: { $players }.
zombiedice-status-score-you = Tú: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.

zombiedice-score-unit-brains = { $count ->
    [one] cerebro
   *[other] cerebros
}
zombiedice-results-header = Resultados de Zombie Dice
zombiedice-results-winner = Ganador: { $player } con { $score } cerebros.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] cerebro
   *[other] cerebros
}.
