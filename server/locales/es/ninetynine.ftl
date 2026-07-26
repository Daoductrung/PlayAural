game-name-ninetynine = Noventa y Nueve
ninetynine-description = Un juego de cartas donde los jugadores intentan evitar que el total acumulado supere 99. ¡Gana el último jugador en pie!

ninetynine-round = Ronda { $round }.

ninetynine-player-turn = Turno de { $player }.

ninetynine-you-play = Juegas { $card }. El total ahora es { $count }.
ninetynine-player-plays = { $player } juega { $card }. El total ahora es { $count }.

ninetynine-direction-reverses = ¡El sentido del juego se invierte!

ninetynine-you-skipped = Se salta tu turno.
ninetynine-player-skipped = Se salta el turno de { $player }.

n99-card-plus-10 = +10
n99-card-minus-10 = -10
n99-card-pass = Pasar
n99-card-reverse = Invertir
n99-card-skip = Saltar
n99-card-ninety-nine = Noventa y Nueve

ninetynine-you-lose-tokens = Pierdes { $amount } { $amount ->
    [one] token
    *[other] tokens
}.
ninetynine-player-loses-tokens = { $player } pierde { $amount } { $amount ->
    [one] token
    *[other] tokens
}.

ninetynine-you-eliminated = ¡Has sido eliminado!
ninetynine-player-eliminated = ¡{ $player } ha sido eliminado!

ninetynine-you-win = ¡Ganas la partida!
ninetynine-player-wins = ¡{ $player } gana la partida!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] token
   *[other] tokens
}

ninetynine-you-deal = Repartes las cartas.
ninetynine-player-deals = { $player } reparte las cartas.

ninetynine-you-draw = Robas { $card }.
ninetynine-player-draws = { $player } roba una carta.

ninetynine-you-no-valid-cards = ¡No tienes ninguna carta que no supere 99!
ninetynine-player-no-valid-cards = ¡{ $player } no tiene ninguna carta que no supere 99!
ninetynine-no-valid-cards = ¡{ $player } no tiene ninguna carta que no supere 99!

ninetynine-current-count = El total es { $count }.
ninetynine-next-round-wait = La siguiente ronda comenzará en { $seconds } segundos.

ninetynine-ace-choice = ¿Jugar el As como +1 o +11?
ninetynine-ace-add-eleven = Sumar 11
ninetynine-ace-add-one = Sumar 1

ninetynine-ten-choice = ¿Jugar el 10 como +10 o -10?
ninetynine-ten-add = Sumar 10
ninetynine-ten-subtract = Restar 10
ninetynine-select-card-choice = Elige cómo jugar esta carta.
ninetynine-choice-1 = Opción 1
ninetynine-choice-2 = Opción 2

ninetynine-draw-card = Robar carta
ninetynine-draw-prompt = Roba una carta.
ninetynine-no-card-to-draw = No hay ninguna carta disponible para robar. Continúa con tu mano actual.

ninetynine-set-tokens = Tokens iniciales: { $tokens }
ninetynine-enter-tokens = Ingresa el número de tokens iniciales:
ninetynine-option-changed-tokens = Tokens iniciales establecidos en { $tokens }.
ninetynine-desc-starting-tokens = Con cuántos tokens de supervivencia empieza cada jugador de Noventa y Nueve. Un jugador queda eliminado al perder todos sus tokens (por defecto 9, rango 1-50).
ninetynine-set-rules = Variante de reglas: { $rules }
ninetynine-select-rules = Selecciona la variante de reglas
ninetynine-option-changed-rules = Variante de reglas establecida en { $rules }.
ninetynine-desc-rules-variant = Elige entre la baraja estándar de 52 cartas de Noventa y Nueve o la baraja especial con cartas de acción.
ninetynine-set-hand-size = Tamaño de mano: { $size }
ninetynine-enter-hand-size = Ingresa el tamaño de mano:
ninetynine-option-changed-hand-size = Tamaño de mano establecido en { $size }.
ninetynine-desc-hand-size = Cuántas cartas se reparten a cada jugador al inicio de cada ronda de Noventa y Nueve (por defecto 3, rango 1-13).
ninetynine-set-autodraw = Robo automático: { $enabled }
ninetynine-option-changed-autodraw = Robo automático establecido en { $enabled }.
ninetynine-desc-autodraw = Cuando está activado, los jugadores roban automáticamente una carta de reemplazo después de jugar. Cuando está desactivado, los jugadores deben robar manualmente.

ninetynine-rules-standard = Reglas estándar.
ninetynine-rules-action-cards = Reglas con cartas de acción.

ninetynine-rules-variant-standard = Estándar
ninetynine-rules-variant-action-cards = Cartas de Acción

ninetynine-choose-first = Primero debes hacer una elección.
ninetynine-round-transition-waiting = Esperando a que comience la siguiente ronda.
ninetynine-pause-timer = Pausar temporizador
ninetynine-timer-not-active = El temporizador de la ronda no está activo.
ninetynine-error-too-many-cards = Se necesitan demasiadas cartas: { $players } jugadores × { $hand_size } cartas supera la baraja de { $deck_size } cartas.
ninetynine-check-count = Ver total
