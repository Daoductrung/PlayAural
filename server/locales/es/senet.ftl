# Senet localization

game-name-senet = Senet

# Game start
senet-game-started = { $p1 } es el jugador 1, { $p2 } es el jugador 2. Empieza { $first }.

# Throwing sticks
senet-throw-you = Lanzas { $result }.{ $bonus ->
    [yes] {" "}¡Turno extra!
   *[no] {""}
}
senet-throw-other = { $player } lanza { $result }.{ $bonus ->
    [yes] {" "}¡Turno extra!
   *[no] {""}
}

# Movement
senet-move-you = Te mueves de la casilla { $from } a la casilla { $to }.
senet-move-other = { $player } se mueve de la casilla { $from } a la casilla { $to }.
senet-swap-you = Intercambias con { $opponent } en la casilla { $to }. { $opponent } regresa a la casilla { $from }.
senet-swap-other = { $player } intercambia con { $opponent } en la casilla { $to }. { $opponent } regresa a la casilla { $from }.
senet-bearoff-you = Retiras una ficha desde la casilla { $from }. Quedan { $remaining }.
senet-bearoff-other = { $player } retira una ficha desde la casilla { $from }. Quedan { $remaining }.
senet-water-you = ¡Caíste en la Casa del Agua! La ficha fue enviada a la casilla { $dest }.
senet-water-other = ¡{ $player } cayó en la Casa del Agua! La ficha fue enviada a la casilla { $dest }.
senet-happiness-you = Llegaste a la Casa de la Felicidad.
senet-happiness-other = { $player } llegó a la Casa de la Felicidad.
senet-horus-auto-you = Tu ficha sale de la Casa de Horus porque tu primera fila está despejada. Quedan { $remaining }.
senet-horus-auto-other = La ficha de { $player } sale de la Casa de Horus porque su primera fila está despejada. Quedan { $remaining }.

# No moves
senet-no-moves-you = No tienes movimientos legales.
senet-no-moves-other = { $player } no tiene movimientos legales.

# Square labels
senet-sq-empty = { $sq }
senet-sq-own = { $sq }, tuya
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }, tuya
senet-sq-opponent-special = { $sq }, { $name }, { $owner }

# Special square names
senet-house-rebirth = Renacimiento
senet-house-happiness = Felicidad
senet-house-water = Agua
senet-house-three-truths = Tres Verdades
senet-house-re-atum = Re-Atum
senet-house-horus = Horus

# Status
senet-status = { $p1 }: { $off1 } fuera. { $p2 }: { $off2 } fuera.{ $phase ->
    [throwing] {" "}Esperando a lanzar.
   *[moving] {" "}Tirada: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = Aún no hay tirada.

# Win
senet-wins-you = ¡Ganaste! Todas tus fichas cruzaron la casa final.
senet-wins-other = ¡{ $player } gana! Todas sus fichas cruzaron la casa final.

# Action labels
senet-check-status = Estado
senet-check-sticks = Palillos
senet-next-piece = Siguiente ficha
senet-previous-piece = Ficha anterior
senet-score-line = { $player }: { $off } fuera.

# Errors
senet-not-your-piece = No es tu ficha.
senet-no-piece-there = No hay ninguna ficha ahí.
senet-no-moves-from-here = No hay movimientos legales desde esta casilla.
senet-need-throw-first = Necesitas lanzar los palillos antes de elegir una ficha para mover.
senet-no-movable-pieces = Ninguna de tus fichas puede moverse con la tirada actual.
senet-error-exactly-two-players = Senet requiere exactamente 2 jugadores activos. Jugadores activos actuales: { $count }.

# Options
senet-option-bot-difficulty = Dificultad del bot: { $bot_difficulty }
senet-option-select-bot-difficulty = Selecciona la dificultad del bot
senet-option-changed-bot-difficulty = Dificultad del bot establecida en { $bot_difficulty }.
senet-desc-bot-difficulty = Define cómo se mueven los bots de Senet: Aleatorio juega de forma más libre, mientras que Simple favorece movimientos tácticos más seguros.
senet-difficulty-random = Aleatorio
senet-difficulty-simple = Simple
