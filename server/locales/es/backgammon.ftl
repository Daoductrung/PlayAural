# Localización de Backgammon

game-name-backgammon = Backgammon

# Colores
backgammon-color-red = rojo
backgammon-color-white = blanco

# Inicio de la partida
backgammon-game-started = { $red } juega con rojo, { $white } juega con blanco.
backgammon-opening-roll = Tirada inicial: { $red } saca { $red_die }, { $white } saca { $white_die }.
backgammon-opening-tie = Ambos sacaron { $die }, se vuelve a lanzar.
backgammon-opening-winner-you = Empiezas tú con { $die1 } y { $die2 }.
backgammon-opening-winner-player = { $player } empieza con { $die1 } y { $die2 }.

# Dados
backgammon-roll-you = Sacas { $die1 } y { $die2 }.
backgammon-roll-player = { $player } saca { $die1 } y { $die2 }.

# Sin movimientos
backgammon-no-moves-you = No tienes movimientos legales, así que tu turno termina.
backgammon-no-moves-player = { $player } no tiene movimientos legales, así que su turno termina.

# Comentario breve de movimiento
backgammon-brief-move-normal = { $is_self ->
    [yes] Tú: { $src } a { $dest }.
    *[no] { $player }: { $src } a { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] Tú: { $src } a { $dest }, capturas a { $opponent }.
    [spectator] { $player }: { $src } a { $dest }, captura a { $opponent }.
    *[no] { $player }: { $src } a { $dest }, te captura.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] Tú: barra a { $dest }.
    *[no] { $player }: barra a { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] Tú: barra a { $dest }, capturas a { $opponent }.
    [spectator] { $player }: barra a { $dest }, captura a { $opponent }.
    *[no] { $player }: barra a { $dest }, te captura.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] Tú: sacas de { $src }.
    *[no] { $player }: saca de { $src }.
}

# Comentario detallado de movimiento
backgammon-verbose-move-normal = { $is_self ->
    [yes] Mueves una ficha del punto { $src } al punto { $dest }.
    *[no] { $player } mueve una ficha del punto { $src } al punto { $dest }.
} { $src_count ->
    [0] El punto { $src } ahora está vacío, { $dest_count } en el punto { $dest }.
    *[other] { $src_count } ahora en el punto { $src }, { $dest_count } en el punto { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] Mueves una ficha del punto { $src } y capturas la ficha de { $opponent } en el punto { $dest }.
    [spectator] { $player } mueve una ficha del punto { $src } y captura la ficha de { $opponent } en el punto { $dest }.
    *[no] { $player } mueve una ficha del punto { $src } y captura tu ficha en el punto { $dest }.
} { $src_count ->
    [0] El punto { $src } ahora está vacío.
    *[other] Quedan { $src_count } en el punto { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] Entras desde la barra al punto { $dest }.
    *[no] { $player } entra desde la barra al punto { $dest }.
} Ahora hay { $dest_count } en el punto { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] Entras desde la barra y capturas la ficha de { $opponent } en el punto { $dest }.
    [spectator] { $player } entra desde la barra y captura la ficha de { $opponent } en el punto { $dest }.
    *[no] { $player } entra desde la barra y captura tu ficha en el punto { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] Sacas una ficha del punto { $src }.
    *[no] { $player } saca una ficha del punto { $src }.
} { $src_count ->
    [0] El punto { $src } ahora está vacío.
    *[other] Quedan { $src_count } en el punto { $src }.
}

# Doblaje
backgammon-doubles-you = Ofreces doblar el cubo a { $value }.
backgammon-doubles-player = { $player } ofrece doblar el cubo a { $value }.
backgammon-accepts-you = Aceptas el doblaje y tomas posesión del cubo.
backgammon-accepts-player = { $player } acepta el doblaje y toma posesión del cubo.
backgammon-drops-you = Rechazas el doblaje y concedes el valor actual del cubo.
backgammon-drops-player = { $player } rechaza el doblaje y concede el valor actual del cubo.
backgammon-accept = Aceptar
backgammon-drop = Rechazar

# Etiquetas de punto
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } seleccionado
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } seleccionado

# Etiquetas de acción
backgammon-label-double = Doblar
backgammon-label-undo = Deshacer
backgammon-label-deselect = Deseleccionar
backgammon-label-next-destination = Siguiente destino
backgammon-label-previous-destination = Destino anterior

# Retroalimentación de selección
backgammon-no-checkers-there = No hay fichas ahí.
backgammon-not-your-checkers = Esas no son tus fichas.
backgammon-no-moves-from-here = No hay movimientos legales desde aquí.
backgammon-must-enter-from-bar = Primero debes entrar desde la barra.
backgammon-illegal-move = Movimiento ilegal.
backgammon-no-dice-remaining = No te quedan dados para usar este turno.
backgammon-no-checkers-on-bar = No tienes fichas en la barra para entrar.
backgammon-invalid-destination = Ese destino no es un punto jugable de backgammon.
backgammon-source-empty = El punto { $point } no tiene ninguna ficha para mover.
backgammon-source-opponent = El punto { $point } contiene fichas de tu oponente.
backgammon-destination-blocked = El punto { $point } está bloqueado por { $count } fichas del oponente.
backgammon-bar-entry-blocked = No puedes entrar en el punto { $point }; está bloqueado por { $count } fichas del oponente.
backgammon-no-die-for-bar-entry = Ninguno de tus dados restantes ({ $dice }) te permite entrar en el punto { $point }.
backgammon-no-die-for-destination = Ninguno de tus dados restantes ({ $dice }) mueve del punto { $src } al punto { $dest }.
backgammon-must-use-forced-die = Debes usar { $dice } ahora porque el backgammon requiere usar ambos dados cuando sea posible, o el dado más alto cuando solo se pueda jugar uno.
backgammon-bearoff-not-home = Todavía no puedes sacar fichas porque no todas están en tu cuadrante final.
backgammon-bearoff-blocked = No puedes sacar del punto { $point } con un { $die }, porque hay fichas en tu punto { $blocking_point }.
backgammon-bearoff-no-die = No puedes sacar del punto { $point } con los dados que te quedan ({ $die }).
backgammon-nothing-to-undo = No hay nada que deshacer.
backgammon-undone = Movimiento deshecho.
backgammon-cannot-double = No puedes doblar en este momento.
backgammon-cannot-undo = No hay nada que deshacer.
backgammon-not-doubling-phase = No hay ningún doblaje que responder.
backgammon-need-roll-first = Debes lanzar los dados antes de mover una ficha.
backgammon-confirm-drop-double = Rechazar concede esta partida al valor actual del cubo. Presiona Rechazar de nuevo dentro de 10 segundos para confirmar.

# Atajos de información
backgammon-check-status = Estado
backgammon-check-cube = Cubo
backgammon-check-pip = Cuenta de pips
backgammon-check-score = Puntuación
backgammon-check-score-detailed = Puntuación detallada
backgammon-check-dice = Dados
backgammon-status = Barra roja: { $bar_red }. Barra blanca: { $bar_white }. Rojo fuera: { $off_red }. Blanco fuera: { $off_white }.
backgammon-dice = { $dice }
backgammon-dice-none = Sin dados.
backgammon-cube-status = Cubo en { $value }. { $owner ->
    [center] Centrado, cualquier jugador puede doblar.
    *[other] Propiedad de { $owner }.
} { $can_double ->
    [yes] El doblaje está disponible ahora.
    [crawford] Esta es una partida Crawford, no se permite doblar.
    *[no] El doblaje no está disponible en este momento.
}
backgammon-cube-no-match = No hay cubo de doblaje en partidas individuales.
backgammon-pip-count = Pips del rojo: { $red_pip }. Pips del blanco: { $white_pip }.
backgammon-match-score-line = { $player }: { $score } de { $match_length }.
backgammon-match-score-cube-line = Cubo: { $cube }.

# Puntuación
backgammon-wins-game-you = Ganas { $points } { $points ->
    [one] punto
   *[other] puntos
}.
backgammon-wins-game-player = { $player } gana { $points } { $points ->
    [one] punto
   *[other] puntos
}.
backgammon-new-game = Comenzando la partida { $number }.
backgammon-match-winner-you = ¡Ganas el enfrentamiento!
backgammon-match-winner-player = ¡{ $player } gana el enfrentamiento!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. Enfrentamiento a { $match_length }.
backgammon-crawford = Partida Crawford: no se permite doblar en esta partida.

# Niveles de dificultad
backgammon-difficulty-random = Aleatorio
backgammon-difficulty-simple = Simple

# Opciones
backgammon-option-match-length = Duración del enfrentamiento: { $match_length }
backgammon-option-select-match-length = Establecer duración del enfrentamiento (1-25)
backgammon-option-changed-match-length = Duración del enfrentamiento establecida en { $match_length }.
backgammon-desc-match-length = Puntos necesarios para ganar el enfrentamiento de Backgammon. Un valor de 1 es una sola partida sin cubo de doblaje (por defecto 1, rango 1-25).
backgammon-option-bot-difficulty = Dificultad del bot: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Selecciona la dificultad del bot
backgammon-option-changed-bot-difficulty = Dificultad del bot establecida en { $bot_difficulty }.
backgammon-desc-bot-difficulty = Elige cómo mueven los bots: Aleatorio juega movimientos legales de forma más libre, mientras que Simple prefiere movimientos tácticos más fuertes.
