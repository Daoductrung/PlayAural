game-name-pusoydos = Pusoy Dos

# =============================================================================
# =============================================================================


# =============================================================================
# Etiquetas y mensajes de opciones
# =============================================================================

pusoydos-set-game-mode = Modo de juego: { $choice }
pusoydos-select-game-mode = Selecciona el modo de juego:
pusoydos-option-changed-game-mode = Modo de juego establecido en { $choice }.
pusoydos-desc-game-mode = Eliminación: gana rondas para salir; el último jugador es el perdedor. Derrotas: quienes terminan últimos acumulan strikes; el primero en llegar al límite pierde. Puntos: el ganador de la ronda recolecta puntos de penalización de los perdedores; el primero en llegar al objetivo gana. Eliminación por puntos: los perdedores acumulan sus propios puntos de penalización; al llegar al límite quedas fuera, y gana el último en pie.

pusoydos-mode-elimination = Eliminación
pusoydos-mode-losses = Derrotas
pusoydos-mode-points = Puntos
pusoydos-mode-points-elimination = Eliminación por puntos

pusoydos-set-rounds-to-win = Rondas para ganar: { $count }
pusoydos-enter-rounds-to-win = Ingresa las rondas necesarias para ser eliminado (mín: 1, máx: 10):
pusoydos-option-changed-rounds-to-win = Rondas para ganar establecidas en { $count }.
pusoydos-desc-rounds-to-win = Solo en modo Eliminación: cuántas rondas debe ganar un jugador antes de salir de la partida como ganador (por defecto 2, rango 1-10).

pusoydos-set-losses-to-lose = Derrotas para perder: { $count }
pusoydos-enter-losses-to-lose = Ingresa las derrotas necesarias para perder (mín: 1, máx: 10):
pusoydos-option-changed-losses-to-lose = Derrotas para perder establecidas en { $count }.
pusoydos-desc-losses-to-lose = Solo en modo Derrotas: cuántas veces puede un jugador terminar último antes de perder la partida (por defecto 3, rango 1-10).

pusoydos-set-target-score = Puntuación objetivo: { $score }
pusoydos-enter-target-score = Ingresa la puntuación objetivo (mín: 10, máx: 10000):
pusoydos-option-changed-target-score = Puntuación objetivo establecida en { $score }.
pusoydos-desc-target-score = Solo en modos de Puntos: umbral de puntuación para ganar en modo Puntos, o para eliminación en modo Eliminación por puntos (por defecto 100, rango 10-10000).

pusoydos-set-turn-timer = Temporizador de turno: { $choice }
pusoydos-select-turn-timer = Selecciona la duración del temporizador de turno:
pusoydos-option-changed-turn-timer = Temporizador de turno establecido en { $choice }.
pusoydos-desc-turn-timer = Límite de tiempo por turno: Ilimitado, 10, 15, 20, 30, 45, 60 o 90 segundos (por defecto Ilimitado).

pusoydos-timer-10 = 10 segundos
pusoydos-timer-15 = 15 segundos
pusoydos-timer-20 = 20 segundos
pusoydos-timer-30 = 30 segundos
pusoydos-timer-45 = 45 segundos
pusoydos-timer-60 = 60 segundos
pusoydos-timer-90 = 90 segundos
pusoydos-timer-unlimited = Ilimitado

pusoydos-set-allow-2-in-straights = Permitir el 2 en escaleras: { $enabled }
pusoydos-option-changed-allow-2-in-straights = Permitir el 2 en escaleras establecido en { $enabled }.
pusoydos-desc-allow-2-in-straights = Si el 2 se puede usar en escaleras (por ejemplo, A-2-3-4-5).

pusoydos-set-instant-wins = Victorias instantáneas: { $enabled }
pusoydos-option-changed-instant-wins = Victorias instantáneas establecidas en { $enabled }.
pusoydos-desc-instant-wins = Si las manos especiales repartidas (Dragón, Cuatro Doses, Seis Parejas) ganan la ronda de inmediato. No se puede combinar con el paso de cartas.

pusoydos-set-card-passing = Paso de cartas: { $choice }
pusoydos-select-card-passing = Selecciona el modo de paso de cartas:
pusoydos-option-changed-card-passing = Paso de cartas establecido en { $choice }.
pusoydos-desc-card-passing = Intercambio de cartas entre ganadores y perdedores después de repartir: Desactivado, Simple o Completo. El paso Completo requiere exactamente 2 o 4 jugadores, y no se puede combinar con las victorias instantáneas.

pusoydos-passing-off = Desactivado
pusoydos-passing-simple = Simple (1º y último intercambian 1 carta)
pusoydos-passing-full = Completo (1º/último intercambian 2, 2º/3º intercambian 1)

pusoydos-set-penalty-tier = Nivel de penalización: { $choice }
pusoydos-select-penalty-tier = Selecciona el nivel de penalización:
pusoydos-option-changed-penalty-tier = Nivel de penalización establecido en { $choice }.
pusoydos-desc-penalty-tier = Solo en modos de Puntos: qué tan agresivamente se penalizan las cartas restantes al final de una ronda.

pusoydos-penalty-standard = Estándar (10 o más cartas: x2, 13 cartas: x3)
pusoydos-penalty-aggressive = Agresivo (8-9: x2, 10-12: x3, 13: x4)
pusoydos-penalty-flat = Plano (1 punto por carta, sin multiplicador)

pusoydos-set-penalty-per-two = Penalización por cada 2 en mano: { $enabled }
pusoydos-option-changed-penalty-per-two = Penalización por cada 2 en mano establecida en { $enabled }.
pusoydos-desc-penalty-per-two = Solo en modos de Puntos: cada 2 que quede en una mano perdedora duplica la penalización de esa mano.

# =============================================================================
# Anuncios del flujo de juego
# =============================================================================


pusoydos-new-hand = Ronda { $round }.
pusoydos-dealt = Se repartieron { $count } cartas: { $cards }.

pusoydos-you-first-player = Tienes el 3 de tréboles y vas primero.
pusoydos-first-player = { $player } tiene el 3 de tréboles y va primero.
pusoydos-you-first-player-lowest = Tienes la carta más baja y vas primero.
pusoydos-first-player-lowest = { $player } tiene la carta más baja y va primero.

# Modo eliminación
pusoydos-you-eliminated = ¡Ganaste { $count } rondas y quedas fuera! Bien jugado.
pusoydos-player-eliminated = ¡{ $player } ganó { $count } rondas y queda fuera! Bien jugado.
pusoydos-you-last-player = Eres el último jugador en pie. ¡Fin de la partida!
pusoydos-last-player = { $player } es el último jugador en pie. ¡Fin de la partida!
pusoydos-players-remaining = Quedan { $count } { $count ->
    [one] jugador
   *[other] jugadores
}.

# Modo derrotas
pusoydos-you-round-loser = ¡Terminas último y sumas una derrota! ({ $count } { $count ->
    [one] derrota
   *[other] derrotas
} en total.)
pusoydos-round-loser = ¡{ $player } termina último y suma una derrota! ({ $count } { $count ->
    [one] derrota
   *[other] derrotas
} en total.)
pusoydos-you-losses-game-over = ¡Llegas a { $count } derrotas y pierdes la partida!
pusoydos-losses-game-over = ¡{ $player } llega a { $count } derrotas y pierde la partida!

# Modo puntos
pusoydos-penalty-entry = { $points } { $points ->
    [one] punto
   *[other] puntos
} de { $player }
pusoydos-you-penalty-summary = Ganas la ronda: { $breakdown }. ({ $gained } esta ronda, { $total } en total.)
pusoydos-penalty-summary = { $player } gana la ronda: { $breakdown }. ({ $gained } esta ronda, { $total } en total.)
pusoydos-you-win-round = ¡Ganas la ronda!
pusoydos-round-winner = ¡{ $player } gana la ronda!
pusoydos-you-go-out = ¡Sales de la ronda!
pusoydos-player-goes-out = ¡{ $player } sale de la ronda!
pusoydos-you-points-winner = ¡Llegas a { $score } puntos y ganas la partida!
pusoydos-points-winner = ¡{ $player } llega a { $score } puntos y gana la partida!

# Modo eliminación por puntos
pusoydos-you-points-elim-penalty = Recibes { $points } puntos. ({ $total } en total.)
pusoydos-points-elim-penalty = { $player } recibe { $points } puntos. ({ $total } en total.)
pusoydos-you-points-elim-eliminated = ¡Llegas a { $score } puntos y eres eliminado!
pusoydos-points-elim-eliminated = ¡{ $player } llega a { $score } puntos y es eliminado!
pusoydos-you-points-elim-winner = Eres el último jugador en pie. ¡Ganas!
pusoydos-points-elim-winner = { $player } es el último jugador en pie. ¡{ $player } gana!

# Victorias instantáneas
pusoydos-you-instant-win-dragon = ¡Tienes un Dragón (escalera de 13 cartas)! ¡Victoria instantánea!
pusoydos-instant-win-dragon = ¡{ $player } tiene un Dragón (escalera de 13 cartas)! ¡Victoria instantánea!
pusoydos-you-instant-win-four-twos = ¡Tienes los cuatro doses! ¡Victoria instantánea!
pusoydos-instant-win-four-twos = ¡{ $player } tiene los cuatro doses! ¡Victoria instantánea!
pusoydos-you-instant-win-six-pairs = ¡Tienes seis parejas! ¡Victoria instantánea!
pusoydos-instant-win-six-pairs = ¡{ $player } tiene seis parejas! ¡Victoria instantánea!
pusoydos-checking-instant-wins = Buscando manos de victoria instantánea...
pusoydos-no-instant-wins = No hay victorias instantáneas esta ronda.

# Paso de cartas
pusoydos-passing-phase = Fase de paso de cartas.
pusoydos-loser-gives = { $loser } le da { $count ->
    [one] su carta más alta
   *[other] sus { $count } cartas más altas
} a { $winner }.
pusoydos-winner-gives-back = { $winner } le devuelve { $count ->
    [one] una carta
   *[other] { $count } cartas
} a { $loser }.
pusoydos-select-cards-to-give = Selecciona { $count ->
    [one] 1 carta
   *[other] { $count } cartas
} para devolverle a { $recipient }:
pusoydos-cards-exchanged = Cartas intercambiadas.
pusoydos-passed-cards = Le diste { $cards } a { $recipient }.
pusoydos-received-cards = Recibiste { $cards } de { $sender }.

# =============================================================================
# Interacción con cartas y acciones
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (seleccionada)

pusoydos-play-none = Selecciona cartas para jugar.
pusoydos-play-invalid = Combinación no válida.
pusoydos-play-combo = Jugar { $combo }

pusoydos-pass = Pasar
pusoydos-check-trick = Ver baza
pusoydos-read-hand = Leer mano
pusoydos-check-turn-timer = Ver temporizador de turno
pusoydos-read-card-counts = Cantidad de cartas
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] carta
   *[other] cartas
}
pusoydos-card-counts-empty = Ningún jugador activo tiene cartas para contar.
pusoydos-timer-disabled = El temporizador de turno está desactivado.
pusoydos-timer-remaining = Quedan { $seconds } segundos.

# Etiquetas de teclas rápidas
pusoydos-key-play = Jugar cartas seleccionadas
pusoydos-key-pass = Pasar
pusoydos-key-trick = Ver la baza actual
pusoydos-key-hand = Leer tu mano
pusoydos-key-counts = Cantidad de cartas
pusoydos-key-timer = Temporizador de turno

# =============================================================================
# Errores
# =============================================================================

pusoydos-error-full-passing-players = El paso de cartas completo requiere exactamente 2 o 4 jugadores.
pusoydos-error-instant-wins-card-passing = Las victorias instantáneas y el paso de cartas están en conflicto. Desactiva una de las dos opciones antes de empezar la partida.
pusoydos-error-no-cards = No has seleccionado ninguna carta.
pusoydos-error-invalid-combo = Las cartas seleccionadas no forman una combinación válida.
pusoydos-error-first-turn-3c = Debes incluir el 3 de tréboles en la primera jugada.
pusoydos-error-wrong-length = Debes jugar exactamente { $count } { $count ->
    [one] carta
   *[other] cartas
} para superar la baza actual.
pusoydos-error-lower-combo = Tu combinación es más baja que la de la baza actual.
pusoydos-error-must-play = No puedes pasar al iniciar una nueva baza.
pusoydos-error-select-cards-to-give = Selecciona exactamente { $count } { $count ->
    [one] carta
   *[other] cartas
} para devolverle a { $recipient }.
pusoydos-error-select-required-give-cards = Selecciona la cantidad requerida de cartas antes de confirmar el intercambio.
pusoydos-error-eliminated = Ya estás fuera de esta partida.
pusoydos-confirm-pass = Usa la acción de pasar de nuevo para confirmar.

# =============================================================================
# Anuncios
# =============================================================================

pusoydos-you-play-single = Juegas { $card }.
pusoydos-player-plays-single = { $player } juega { $card }.
pusoydos-you-play-combo = Juegas un { $combo } de { $cards }.
pusoydos-player-plays-combo = { $player } juega un { $combo } de { $cards }.
pusoydos-you-pass = Pasas.
pusoydos-player-passes = { $player } pasa.
pusoydos-you-win-trick = Ganas la baza.
pusoydos-trick-won = { $player } gana la baza.

pusoydos-trick-empty = La baza está vacía.
pusoydos-trick-status = { $player } jugó un { $combo } de { $cards }.
pusoydos-your-hand = Tu mano: { $cards }.

pusoydos-score-no-scores = Aún no hay puntuaciones.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] victoria
   *[other] victorias
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] derrota
   *[other] derrotas
}
pusoydos-score-points = { $player }: { $score } puntos

pusoydos-you-one-card = ¡Te queda una sola carta!
pusoydos-one-card = ¡A { $player } le queda una sola carta!

# =============================================================================
# Nombres de combinaciones
# =============================================================================

pusoydos-combo-single = Solitaria
pusoydos-combo-pair = Pareja
pusoydos-combo-three_of_a_kind = Trío
pusoydos-combo-straight = Escalera
pusoydos-combo-flush = Color
pusoydos-combo-full_house = Full
pusoydos-combo-four_of_a_kind = Póker
pusoydos-combo-straight_flush = Escalera de Color

# Nombres de manos de victoria instantánea
pusoydos-combo-dragon = Dragón
pusoydos-combo-four_twos = Cuatro Doses
pusoydos-combo-six_pairs = Seis Parejas

# =============================================================================
# Pantalla final
# =============================================================================

pusoydos-game-over = ¡La partida terminó! ¡{ $player } perdió!
pusoydos-game-over-points = ¡La partida terminó! ¡{ $player } gana con { $score } puntos!
pusoydos-game-over-losses = ¡La partida terminó! ¡{ $player } pierde con { $count } derrotas!
pusoydos-line-format = { $rank }. { $player }: { $score } puntos
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] victoria
   *[other] victorias
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] derrota
   *[other] derrotas
}
