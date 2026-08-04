game-name-sorry = ¡Sorry!

sorry-set-rules-profile = Perfil de reglas: { $profile }
sorry-select-rules-profile = Elige un perfil de reglas
sorry-option-changed-rules-profile = Perfil de reglas establecido en { $profile }.
sorry-desc-rules-profile = Elige el perfil de reglas de Sorry, incluyendo el mazo clásico 00390 o las reglas base más nuevas estilo A5065.
sorry-rules-profile-classic-00390 = Clásico 00390
sorry-rules-profile-a5065-core = Base A5065

sorry-toggle-auto-apply-single-move = Aplicar movimiento único automáticamente: { $enabled }
sorry-option-changed-auto-apply-single-move = Aplicar movimiento único automáticamente establecido en { $enabled }.
sorry-desc-auto-apply-single-move = Cuando está activado, una carta con una sola jugada legal se aplica automáticamente.
sorry-toggle-faster-setup-one-pawn-out = Preparación más rápida (un peón afuera): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = Preparación más rápida establecida en { $enabled }.
sorry-desc-faster-setup-one-pawn-out = Empieza a cada jugador con un peón ya fuera para reducir la espera inicial.
sorry-error-unsupported-rules-profile = El perfil de reglas de Sorry seleccionado "{ $profile }" no es compatible. Elige Clásico 00390 o Base A5065 antes de empezar.

sorry-draw-card = Robar carta
sorry-check-board = Leer tablero
sorry-check-pawns = Ver tus peones
sorry-check-card = Ver carta actual
sorry-check-status = Ver estado

sorry-move-slot = Opción de movimiento { $slot }
sorry-move-slot-fallback = Elegir movimiento
sorry-move-start = Sacar el peón { $pawn } desde { $position } fuera de la salida
sorry-move-forward = Mover el peón { $pawn } desde { $position } { $steps } casillas adelante
sorry-move-backward = Mover el peón { $pawn } desde { $position } { $steps } casillas atrás
sorry-move-swap = Intercambiar el peón { $pawn } en { $position } con el peón { $target_pawn } de { $target_player } en { $target_position }
sorry-move-sorry = Usar ¡Sorry! con el peón { $pawn } en { $position } contra el peón { $target_pawn } de { $target_player } en { $target_position }
sorry-move-split7-pick = Repartir el 7 entre el peón { $pawn_a } en { $position_a } y el peón { $pawn_b } en { $position_b }
sorry-move-split7-option = El peón { $pawn_a } en { $position_a } avanza { $steps_a }, el peón { $pawn_b } en { $position_b } avanza { $steps_b }

sorry-card-none = sin carta activa
sorry-card-sorry = ¡Sorry!
sorry-choose-move = Elige un movimiento.
sorry-choose-split = Elige cómo repartir el 7.
sorry-error-draw-pending-move = Ya robaste una carta. Elige uno de los movimientos disponibles para esa carta antes de volver a robar.

sorry-game-started = Comienza Sorry. Jugadores: { $players }.
sorry-draw-announcement = { $player } roba { $card }.
sorry-you-draw-announcement = Robas { $card }.
sorry-no-legal-moves = { $player } no tiene ningún movimiento legal para { $card }.
sorry-you-no-legal-moves = No tienes ningún movimiento legal para { $card }.
sorry-deck-exhausted = El mazo de Sorry está vacío, así que la partida termina aquí.
sorry-you-extra-turn = Robaste un 2 y tomas otro turno.
sorry-player-extra-turn = { $player } robó un 2 y toma otro turno.

sorry-play-start =
    { $brief ->
        [yes] { $player }: peón { $pawn } sale a { $destination }.
       *[no] { $player } saca el peón { $pawn } a { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] Tú: peón { $pawn } sale a { $destination }.
       *[no] Sacas el peón { $pawn } a { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: peón { $pawn } +{ $steps } a { $destination }.
       *[no] { $player } mueve el peón { $pawn } { $steps } casillas adelante, a { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] Tú: peón { $pawn } +{ $steps } a { $destination }.
       *[no] Mueves el peón { $pawn } { $steps } casillas adelante, a { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: peón { $pawn } -{ $steps } a { $destination }.
       *[no] { $player } mueve el peón { $pawn } { $steps } casillas atrás, a { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] Tú: peón { $pawn } -{ $steps } a { $destination }.
       *[no] Mueves el peón { $pawn } { $steps } casillas atrás, a { $destination }.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: peón { $pawn } intercambia con el peón { $target_pawn } de { $target_player }; { $destination }.
       *[no] { $player } intercambia el peón { $pawn } con el peón { $target_pawn } de { $target_player } y termina en { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] Tú: peón { $pawn } intercambia con el peón { $target_pawn } de { $target_player }; { $destination }.
       *[no] Intercambias el peón { $pawn } con el peón { $target_pawn } de { $target_player } y terminas en { $destination }.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: ¡Sorry! peón { $pawn } a { $destination }; el peón { $target_pawn } de { $target_player } vuelve a la salida.
       *[no] { $player } juega ¡Sorry!, reemplazando al peón { $target_pawn } de { $target_player }, y termina en { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] Tú: ¡Sorry! peón { $pawn } a { $destination }; el peón { $target_pawn } de { $target_player } vuelve a la salida.
       *[no] Juegas ¡Sorry!, reemplazas al peón { $target_pawn } de { $target_player }, y terminas en { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: peón { $pawn_a } +{ $steps_a } a { $destination_a }; peón { $pawn_b } +{ $steps_b } a { $destination_b }.
       *[no] { $player } reparte el 7: el peón { $pawn_a } avanza { $steps_a } casillas hasta { $destination_a }, y el peón { $pawn_b } avanza { $steps_b } casillas hasta { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] Tú: peón { $pawn_a } +{ $steps_a } a { $destination_a }; peón { $pawn_b } +{ $steps_b } a { $destination_b }.
       *[no] Repartes el 7: el peón { $pawn_a } avanza { $steps_a } casillas hasta { $destination_a }, y el peón { $pawn_b } avanza { $steps_b } casillas hasta { $destination_b }.
    }

sorry-pawn-home = { $player } lleva el peón { $pawn } a la meta.
sorry-you-pawn-home = Tu peón { $pawn } llega a la meta.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: tu peón { $pawn } vuelve a la salida.
       *[no] Tu peón { $pawn } fue devuelto a la salida por { $by_player }.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] Tú: el peón { $pawn } de { $target_player } vuelve a la salida.
       *[no] Devuelves a la salida al peón { $pawn } de { $target_player }.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: el peón { $pawn } de { $target_player } vuelve a la salida.
       *[no] { $player } devuelve a la salida al peón { $pawn } de { $target_player }.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] Tú: tu propio peón { $pawn } vuelve a la salida.
       *[no] Devuelves a la salida tu propio peón { $pawn }.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: su propio peón { $pawn } vuelve a la salida.
       *[no] { $player } devuelve a la salida su propio peón { $pawn }.
    }

sorry-current-card = Carta actual: { $card }.
sorry-view-your-pawn = Tu peón { $pawn }: { $zone }.
sorry-board-your-color = Tu color: { $color }.
sorry-board-summary-heading = Resumen rápido:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = peón { $pawn } en { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = Casillas del recorrido:
sorry-board-private-areas-heading = Áreas privadas:
sorry-board-square-line = Casilla { $square }: { $status }
sorry-board-square-empty = vacía
sorry-board-square-slide = resbaladero { $color }
sorry-board-square-token = peón { $pawn } de { $player }
sorry-board-start-line = Área de salida { $color } de { $player }: { $pawns }
sorry-board-safety-line = Espacio seguro { $color } { $space } de { $player }: { $pawns }
sorry-board-home-line = Meta { $color } de { $player }: { $pawns }
sorry-board-area-empty = vacía
sorry-board-area-pawn = peón { $pawn }
sorry-color-red = rojo
sorry-color-blue = azul
sorry-color-yellow = amarillo
sorry-color-green = verde
sorry-location-start = salida
sorry-location-track = casilla { $position }
sorry-location-home-path = espacio seguro { $steps }
sorry-location-home = meta
sorry-zone-start = en la salida
sorry-zone-track = en la casilla { $position } del recorrido
sorry-zone-home-path = en el paso { $steps } de la zona segura
sorry-zone-home = en la meta

sorry-status-turn-number = Turno { $count }
sorry-status-phase = Fase: { $phase }
sorry-status-current-card = Carta: { $card }
sorry-status-current-player = Jugador actual: { $player }
sorry-phase-draw = robar
sorry-phase-choose-move = elegir movimiento
sorry-phase-choose-split = repartir el siete
sorry-phase-resolving = resolviendo movimiento

sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 peón en meta
   *[other] { $count } peones en meta
}
