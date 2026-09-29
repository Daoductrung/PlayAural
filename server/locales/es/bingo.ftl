game-name-bingo = Bingo

bingo-pattern-line = Cualquier línea
bingo-pattern-four-corners = Cuatro esquinas
bingo-pattern-letter-x = Letra X
bingo-pattern-blackout = Cartón lleno

bingo-call-interval-5 = 5 segundos
bingo-call-interval-15 = 15 segundos
bingo-call-interval-30 = 30 segundos
bingo-call-interval-45 = 45 segundos
bingo-call-interval-60 = 60 segundos

bingo-set-pattern = Patrón para ganar: { $pattern }
bingo-select-pattern = Selecciona el patrón para ganar:
bingo-option-changed-pattern = El patrón para ganar ahora es { $pattern }.
bingo-desc-pattern = El patrón que un cartón debe completar para ganar. Cualquier línea acepta una fila, columna o diagonal completa. Cuatro esquinas requiere las cuatro casillas de las esquinas. Letra X requiere ambas diagonales. Cartón lleno requiere todo el cartón.

bingo-set-call-interval = Cantar cada { $seconds }
bingo-select-call-interval = Selecciona el intervalo de canto:
bingo-option-changed-interval = Ahora se cantará un número cada { $seconds }.
bingo-desc-call-interval = Cuánto espera quien canta entre cada número anunciado (por defecto 15, rango de 5 a 60 segundos).

bingo-cell-free = Casilla libre.
bingo-cell-marked = { $letter } { $number }, marcada.
bingo-cell-unmarked = { $letter } { $number }, sin marcar.
bingo-cell-is-free = Esta casilla ya está libre.
bingo-you-already-won = Ya tienes Bingo en esta ronda.

bingo-you-mark = Marcaste { $letter } { $number }.
bingo-you-unmark = Desmarcaste { $letter } { $number }.

bingo-claim-bingo = ¡Cantar Bingo!
bingo-repeat-call = Repetir el último número
bingo-check-called = Ver números cantados
bingo-no-calls-yet = Todavía no se ha cantado ningún número.
bingo-claim-in-progress = Se está verificando otro reclamo en este momento. Intenta de nuevo en un momento.
bingo-claim-in-progress-you = Tu reclamo ya se está verificando.
bingo-claim-wait-for-call = Espera a que se anuncie el número que se está cantando, luego intenta de nuevo.
bingo-claim-unchanged = Tu cartón no ha cambiado desde que fue rechazado. Marca otro número o espera al siguiente canto antes de volver a reclamar.
bingo-checking-claim-you = Cantas Bingo. Verificando tu cartón...
bingo-checking-claim = { $player } canta Bingo. Verificando el cartón...
bingo-whose-turn-checking = Verificando el cartón de { $player }...
bingo-whose-turn-checking-you = Se está verificando tu cartón...
bingo-whose-turn-checking-card = Se está verificando un cartón de Bingo...
bingo-whose-turn-drawing = Sacando el siguiente número...
bingo-whose-turn-waiting = { $seconds ->
    [one] Próximo número en { $seconds } segundo.
   *[other] Próximo número en { $seconds } segundos.
}
bingo-claim-incorrect-you = Cartón incorrecto.
bingo-claim-incorrect = El cartón de { $player } es incorrecto.
bingo-claim-incomplete-you = Todavía no tienes el patrón completo.
bingo-claim-incomplete = { $player } todavía no tiene el patrón completo.
bingo-marked-number-not-called = Marcaste { $letter } { $number }, pero todavía no se ha cantado.

bingo-last-call = { $letter } { $number }

bingo-status-called-count = { $count } de { $total } números cantados.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = ¡Comienza el Bingo! Patrón: { $pattern }. Se cantará un número nuevo cada { $interval } segundos. Marca tu cartón y presiona B para cantar Bingo cuando lo tengas.
bingo-game-start-touch = ¡Comienza el Bingo! Patrón: { $pattern }. Se cantará un número nuevo cada { $interval } segundos. Marca tu cartón y, cuando lo tengas, usa el gesto de mantener pulsado de tu cliente en cualquier parte del cartón, o elige Cantar Bingo.
bingo-game-start-spectator = ¡Comienza el Bingo! Patrón: { $pattern }. Se cantará un número nuevo cada { $interval } segundos.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = ¡Sí! Cartón correcto. Ganas con { $numbers }!
bingo-claim-correct = ¡Sí! Cartón correcto. { $player } gana con { $numbers }!
bingo-claim-correct-no-numbers-you = ¡Sí! Cartón correcto. ¡Ganas!
bingo-claim-correct-no-numbers = ¡Sí! Cartón correcto. { $player } gana!
bingo-deck-exhausted = Se cantaron los 75 números. La ronda termina aquí.

bingo-error-invalid-interval = "{ $value }" no es un intervalo de canto válido.
bingo-error-invalid-pattern = { $value } no es un patrón para ganar reconocido.

bingo-end-calls = { $count ->
    [one] Se cantó { $count } número en esta ronda.
   *[other] Se cantaron { $count } números en esta ronda.
}
bingo-end-winner-line = Ganador: { $player }
bingo-end-no-winner = No se realizó ningún reclamo de Bingo válido esta ronda.
