game-name-snakesandladders = Serpientes y Escaleras
game-snakesandladders-desc = Corre desde el área de salida hasta la casilla 100. Sube por las escaleras, resbala por las serpientes y sé el primero en llegar a la meta.

snakes-roll = Lanzar dado
snakes-check-positions = Ver posiciones

snakes-turn-start-you = Tu turno. Tu ficha está en el área de salida, antes de la casilla 1.
snakes-turn-start-other = Turno de { $player }. Su ficha está en el área de salida, antes de la casilla 1.
snakes-turn-you = Tu turno. Estás en la casilla { $position }.
snakes-turn-other = Turno de { $player }. Está en la casilla { $position }.

snakes-roll-you = Sacas { $roll }.
snakes-roll-other = { $player } saca { $roll }.
snakes-enter-you = Te mueves del área de salida a la casilla { $position }.
snakes-enter-other = { $player } se mueve del área de salida a la casilla { $position }.
snakes-enter-you-brief = Tú: casilla { $position }.
snakes-enter-other-brief = { $player }: casilla { $position }.
snakes-move-you = Avanzas { $roll } casillas, de la casilla { $start } a la casilla { $position }.
snakes-move-other = { $player } avanza { $roll } casillas, de la casilla { $start } a la casilla { $position }.
snakes-move-you-brief = Tú: casilla { $position }.
snakes-move-other-brief = { $player }: casilla { $position }.
snakes-bounce-you = Desde la casilla { $start }, tu tirada de { $roll } pasa la casilla { $target }, así que rebotas desde la meta hasta la casilla { $position }.
snakes-bounce-other = Desde la casilla { $start }, { $player } saca { $roll }, pasa la casilla { $target } y rebota desde la meta hasta la casilla { $position }.
snakes-bounce-you-brief = Rebotas hasta la casilla { $position }.
snakes-bounce-other-brief = { $player } rebota hasta la casilla { $position }.
snakes-restored-bounce-you = Tu tirada guardada termina haciéndote rebotar hasta la casilla { $position }.
snakes-restored-bounce-other = La tirada guardada de { $player } termina haciéndolo rebotar hasta la casilla { $position }.
snakes-exact-miss-you = Necesitas { $needed } para llegar a la casilla { $target }, pero sacaste { $roll }, así que te quedas en la casilla { $position }.
snakes-exact-miss-other = { $player } necesita { $needed } para llegar a la casilla { $target }, pero saca { $roll }, así que se queda en la casilla { $position }.
snakes-exact-miss-you-brief = Necesitas { $needed }, sacaste { $roll } y te quedas en la casilla { $position }.
snakes-exact-miss-other-brief = { $player } necesita { $needed }, saca { $roll } y se queda en la casilla { $position }.
snakes-ladder-you = Caes al pie de una escalera en la casilla { $start } y subes hasta la casilla { $end }, avanzando { $distance } casillas.
snakes-ladder-other = { $player } cae al pie de una escalera en la casilla { $start } y sube hasta la casilla { $end }, avanzando { $distance } casillas.
snakes-ladder-you-brief = Subes de la casilla { $start } a la { $end }.
snakes-ladder-other-brief = { $player } sube de la casilla { $start } a la { $end }.
snakes-snake-you = Caes en la cabeza de una serpiente en la casilla { $start } y resbalas hasta su cola en la casilla { $end }, retrocediendo { $distance } casillas.
snakes-snake-other = { $player } cae en la cabeza de una serpiente en la casilla { $start } y resbala hasta su cola en la casilla { $end }, retrocediendo { $distance } casillas.
snakes-snake-you-brief = Resbalas de la casilla { $start } a la { $end }.
snakes-snake-other-brief = { $player } resbala de la casilla { $start } a la { $end }.
snakes-extra-turn-you = Sacaste 6, así que tomas otro turno desde la casilla { $position }.
snakes-extra-turn-other = { $player } sacó 6, así que toma otro turno desde la casilla { $position }.
snakes-win-you = ¡Llegas a la casilla { $position } y ganas la partida!
snakes-win-other = ¡{ $player } llega a la casilla { $position } y gana la partida!

snakes-status-goal = Meta: casilla { $target }. Regla de llegada: { $rule }.
snakes-status-current-start = { $player }: área de salida, antes de la casilla 1. Turno actual.
snakes-status-player-start = { $player }: área de salida, antes de la casilla 1.
snakes-status-current-position = { $player }: casilla { $position }, faltan { $remaining }. Turno actual.
snakes-status-player-position = { $player }: casilla { $position }, faltan { $remaining }.
snakes-status-player-finished = { $player }: casilla { $position }, terminó.

snakes-finish-bounce-back = Rebotar
snakes-finish-exact-stay = Tirada exacta; quedarse quieto si se pasa
snakes-set-finish-rule = Regla de llegada: { $rule }
snakes-select-finish-rule = Selecciona la regla de llegada
snakes-option-changed-finish-rule = Regla de llegada cambiada a { $rule }.
snakesandladders-desc-finish-rule = Define si pasarse de la casilla 100 hace rebotar hacia atrás o deja al jugador esperando una tirada exacta.
snakes-set-extra-turn-six = Turno extra al sacar 6: { $enabled }
snakes-option-changed-extra-turn-six = Turno extra al sacar 6 cambiado a { $enabled }.
snakesandladders-desc-extra-turn-on-six = Controla si sacar un seis otorga otro turno.

snakes-error-roll-not-playing = Solo puedes lanzar el dado después de que haya comenzado una partida de Serpientes y Escaleras.
snakes-error-roll-not-your-turn = Aún no puedes lanzar porque otro jugador está tomando su turno. Espera a que te toque.
snakes-error-roll-resolving = Tu tirada anterior todavía se está resolviendo. Espera a que termine la secuencia de movimiento, serpiente o escalera antes de volver a lanzar.
snakes-error-positions-not-playing = Las posiciones solo están disponibles mientras hay una partida de Serpientes y Escaleras en curso.
snakes-error-invalid-finish-rule = La regla de llegada seleccionada, { $rule }, no es compatible. Elige Rebotar o Tirada exacta; quedarse quieto si se pasa.

snakes-end-score = { $rank }. { $player }: casilla { $position }
snakes-end-score-start = { $rank }. { $player }: área de salida, antes de la casilla 1
