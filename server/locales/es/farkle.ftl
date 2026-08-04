game-name-farkle = Farkle

farkle-roll = Lanzar { $count } { $count ->
    [one] dado
   *[other] dados
}
farkle-bank = Guardar { $points } puntos

farkle-take-single-one = Un solo 1 por { $points } puntos
farkle-take-single-five = Un solo 5 por { $points } puntos
farkle-take-three-kind = Trío de { $number } por { $points } puntos
farkle-take-four-kind = Cuatro { $number } por { $points } puntos
farkle-take-five-kind = Cinco { $number } por { $points } puntos
farkle-take-six-kind = Seis { $number } por { $points } puntos
farkle-take-small-straight = Escalera pequeña por { $points } puntos
farkle-take-large-straight = Escalera grande por { $points } puntos
farkle-take-three-pairs = Tres pares por { $points } puntos
farkle-take-double-triplets = Dos tríos por { $points } puntos
farkle-take-full-house = Póker con un par por { $points } puntos

farkle-you-roll = Lanzas { $count } { $count ->
    [one] dado
   *[other] dados
}.
farkle-player-rolls = { $player } lanza { $count } { $count ->
    [one] dado
   *[other] dados
}.
farkle-you-roll-brief = Lanzas { $count }.
farkle-player-rolls-brief = { $player } lanza { $count }.
farkle-roll-result = Los dados muestran: { $dice }.
farkle-roll-result-brief = Dados: { $dice }.

farkle-you-farkle = ¡FARKLE! Pierdes { $points } puntos del turno.
farkle-player-farkles = ¡FARKLE! { $player } pierde { $points } puntos del turno.
farkle-you-farkle-brief = Farkle: pierdes { $points }.
farkle-player-farkles-brief = Farkle: { $player } pierde { $points }.

farkle-you-take-combo = Guardas { $combo } por { $points } puntos.
farkle-player-takes-combo = { $player } guarda { $combo } por { $points } puntos.
farkle-you-take-combo-brief = Tú: { $combo }, +{ $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }, +{ $points }.

farkle-you-hot-dice = ¡Dados calientes! Puntuaste con los seis dados y puedes volver a lanzar los seis.
farkle-player-hot-dice = ¡Dados calientes! { $player } puntuó con los seis dados y puede volver a lanzar los seis.
farkle-you-hot-dice-brief = Tú: dados calientes.
farkle-player-hot-dice-brief = { $player }: dados calientes.

farkle-you-bank = Guardas { $points } puntos. Tu total ahora es { $total }.
farkle-player-banks = { $player } guarda { $points } puntos, para un total de { $total }.
farkle-you-bank-brief = Guardas { $points}; total { $total }.
farkle-player-banks-brief = { $player } guarda { $points}; total { $total }.

farkle-you-win = ¡Ganas con { $score } puntos!
farkle-winner = ¡{ $player } gana con { $score } puntos!
farkle-you-win-brief = Ganas: { $score }.
farkle-winner-brief = { $player } gana: { $score }.
farkle-winners-tie = ¡Empate en el objetivo! Jugadores en desempate: { $players }.
farkle-tiebreaker-round-start = Ronda de desempate { $round }. Aún compitiendo: { $players }.

farkle-your-turn-score = Tienes { $points } puntos en este turno.
farkle-turn-score = { $player } tiene { $points } puntos en este turno.
farkle-no-turn = Nadie está tomando un turno en este momento.

farkle-set-target-score = Puntuación objetivo: { $score }
farkle-enter-target-score = Ingresa la puntuación objetivo (500-5000):
farkle-option-changed-target = Puntuación objetivo establecida en { $score }.
farkle-desc-target-score = Puntuación necesaria para activar los turnos finales de Farkle y potencialmente ganar (por defecto 1000, rango 500-5000).

farkle-set-entrance-score = Puntuación mínima de entrada: { $score }
farkle-enter-entrance-score = Ingresa la puntuación mínima de entrada (0-5000):
farkle-option-changed-entrance = Puntuación mínima de entrada establecida en { $score }.
farkle-desc-min-entrance-score = Puntuación mínima de turno requerida para guardar los primeros puntos de un jugador. No puede ser mayor que la puntuación objetivo (por defecto 50, rango 0-5000).

farkle-set-bank-score = Puntuación mínima para guardar: { $score }
farkle-enter-bank-score = Ingresa la puntuación mínima para guardar (0-5000):
farkle-option-changed-bank = Puntuación mínima para guardar establecida en { $score }.
farkle-desc-min-bank-score = Puntuación mínima de turno requerida antes de que Guardar esté disponible una vez que el jugador ya está en el marcador. No puede ser mayor que la puntuación objetivo (por defecto 30, rango 0-5000).

farkle-error-entrance-above-target = La puntuación mínima de entrada ({ $entrance }) no puede ser mayor que la puntuación objetivo ({ $target }).
farkle-error-bank-above-target = La puntuación mínima para guardar ({ $bank }) no puede ser mayor que la puntuación objetivo ({ $target }).

farkle-must-take-combo = Debes guardar al menos un dado o combinación puntuable antes de volver a lanzar.
farkle-cannot-bank = Solo puedes guardar puntos después de haber guardado un dado o combinación puntuable en este turno.
farkle-must-reach-entrance-score = Necesitas al menos { $points } puntos de turno antes de guardar tu primera puntuación.
farkle-must-reach-bank-score = Necesitas al menos { $points } puntos de turno antes de guardar.
farkle-confirm-risky-roll = Puedes guardar { $points } puntos ahora. Volver a lanzar arriesga perderlos; repite Lanzar dentro de { $seconds } segundos para confirmar.
farkle-invalid-combo-action = Esa opción de puntuación no se reconoce. Elige una de las combinaciones que aparecen en la lista actual.
farkle-combo-no-longer-available = Esa combinación puntuable ya no está disponible. Se actualizaron las opciones de puntuación actuales.

farkle-combo-single-1 = Un solo 1
farkle-combo-single-5 = Un solo 5
farkle-combo-three-kind = Trío de { $number }
farkle-combo-four-kind = Cuatro { $number }
farkle-combo-five-kind = Cinco { $number }
farkle-combo-six-kind = Seis { $number }
farkle-combo-small-straight = Escalera pequeña
farkle-combo-large-straight = Escalera grande
farkle-combo-three-pairs = Tres pares
farkle-combo-double-triplets = Dos tríos
farkle-combo-full-house = Póker con un par

farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } por { $points } puntos

farkle-check-turn-score = Ver puntuación del turno
farkle-roll-label = Lanzar dados
farkle-bank-label = Guardar puntos
