game-round-start = Ronda { $round }.
game-round-end = Ronda { $round } completada.
game-turn-start = Es el turno de { $player }.
game-turn-start-you = Es tu turno.
game-turn-start-player = Es el turno de { $player }.
game-no-turn = No es el turno de nadie por ahora.

game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score }/{ $target } { $unit }
game-score-unit-points = { $count ->
    [one] punto
   *[other] puntos
}
game-score-unit-chips = { $count ->
    [one] ficha
   *[other] fichas
}
game-score-unit-coins = { $count ->
    [one] moneda
   *[other] monedas
}
game-score-unit-health = de vida
game-score-unit-ninetynine-tokens = { $count ->
    [one] token
   *[other] tokens
}
game-score-unit-tokens-home = { $count ->
    [one] token en casa
   *[other] tokens en casa
}
game-score-unit-pawns-home = { $count ->
    [one] ficha en casa
   *[other] fichas en casa
}
game-score-unit-hand-wins = { $count ->
    [one] mano ganada
   *[other] manos ganadas
}
game-score-unit-light = de luz
game-final-scores-header = Puntuaciones finales:

game-winner = ¡{ $player } gana!
game-winner-you = ¡Ganaste!
game-winner-score = ¡{ $player } gana con { $score } puntos!
game-tiebreaker = ¡Es un empate! ¡Ronda de desempate!
game-tiebreaker-players = ¡Hay un empate entre { $players }! ¡Ronda de desempate!
game-eliminated = { $player } fue eliminado con { $score } puntos.

game-set-target-score = Puntuación objetivo: { $score }
game-enter-target-score = Ingresa la puntuación objetivo:
game-option-changed-target = Puntuación objetivo establecida en { $score }.

game-set-team-mode = Modo de equipos: { $mode }
game-select-team-mode = Selecciona el modo de equipos
game-option-changed-team = Modo de equipos establecido en { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } equipos de { $team_size }
game-team-name = Equipo { $index }
team-arrangement-started = Se inició la organización de equipos. Revisa los equipos, intercambia miembros si hace falta y confirma para empezar.
team-arrangement-confirm = Confirmar equipos y empezar
team-arrangement-read = Leer equipos
team-arrangement-select-member-action = Seleccionar miembro del equipo
team-arrangement-select-member = Selecciona un miembro del equipo
team-arrangement-select-swap-target = Selecciona un jugador con quien intercambiar
team-arrangement-swap-member = Elegir con quién intercambiar
team-arrangement-swap-member-selected = Intercambiar { $player } con...
team-arrangement-cancel = Cancelar organización de equipos
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = Orden de turnos: { $players }
team-arrangement-member-option = { $player }, { $team }, { $selected }
team-arrangement-selected = seleccionado
team-arrangement-not-selected = no seleccionado
team-arrangement-member-selected = { $player } de { $team } seleccionado. Elige un jugador de otro equipo para intercambiar.
team-arrangement-swapped = { $first } y { $second } intercambiaron de equipo.
team-arrangement-cancelled = Se canceló la organización de equipos.
team-arrangement-cancelled-roster = Se canceló la organización de equipos porque cambió la lista de jugadores.
team-arrangement-refreshed = La lista de jugadores cambió. Se actualizó la organización de equipos.
team-arrangement-in-progress = Termina o cancela la organización de equipos primero.
team-arrangement-not-active = La organización de equipos no está activa.
team-arrangement-select-first = Selecciona primero un miembro del equipo.
team-arrangement-player-missing = Ese jugador ya no está disponible para la organización de equipos.
team-arrangement-same-team = Elige a alguien de un equipo diferente.
team-arrangement-swap-failed = No se pudo intercambiar a esos miembros del equipo.

status-box-closed = Información de estado cerrada.

game-leave = Salir de la partida

round-timer-paused = { $player } pausó la partida (presiona p para iniciar la siguiente ronda).
round-timer-resumed = Se reanudó el temporizador de ronda.
round-timer-countdown = Siguiente ronda en { $seconds }...

dice-keeping = Guardando { $value }.
dice-rerolling = Volviendo a lanzar { $value }.
dice-locked = Ese dado está bloqueado y no se puede cambiar.
dice-status-label-locked = { $value } (bloqueado)
dice-status-label-kept = { $value } (guardado)

game-deal-counter = Reparto { $current }/{ $total }.
game-you-deal = Repartes las cartas.
game-player-deals = { $player } reparte las cartas.

card-name = { $rank } de { $suit }
no-cards = Sin cartas

suit-diamonds = diamantes
suit-clubs = tréboles
suit-hearts = corazones
suit-spades = picas

rank-ace = as
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = jota
rank-queen = reina
rank-king = rey

rank-ace-plural = ases
rank-two-plural = doses
rank-three-plural = treses
rank-four-plural = cuatros
rank-five-plural = cincos
rank-six-plural = seises
rank-seven-plural = sietes
rank-eight-plural = ochos
rank-nine-plural = nueves
rank-ten-plural = dieces
rank-jack-plural = jotas
rank-queen-plural = reinas
rank-king-plural = reyes


poker-high-card-with = Carta alta: { $high }, con { $rest }
poker-high-card = Carta alta: { $high }
poker-pair-with = Par de { $pair }, con { $rest }
poker-pair = Par de { $pair }
poker-two-pair-with = Doble par, { $high } y { $low }, con { $kicker }
poker-two-pair = Doble par, { $high } y { $low }
poker-trips-with = Trío de { $trips }, con { $rest }
poker-trips = Trío de { $trips }
poker-straight-high = Escalera con carta alta { $high }
poker-flush-high-with = Color con carta alta { $high }, con { $rest }
poker-full-house = Full, { $trips } sobre { $pair }
poker-quads-with = Póker de { $quads }, con { $kicker }
poker-quads = Póker de { $quads }
poker-royal-flush = Escalera real
poker-straight-flush-high = Escalera de color con carta alta { $high }
poker-unknown-hand = Mano desconocida

game-error-invalid-team-mode = El modo de equipos seleccionado no es válido para el número actual de jugadores.

documentation-menu = Documentación
introduction = Introducción
community-rules = Normas de la comunidad
global-keys = Controles globales
game-rules = Reglas del juego
changelog = Registro de cambios
donation = Donación
contact = Contacto
document-not-found = Documento no encontrado.
help = Ayuda

# Game Info (Ctrl+I)
game-info = Información del juego
game-info-header = Información de la partida actual
game-info-name = Juego: {$game}
game-info-players = Jugadores: {$count}
game-info-host = Anfitrión: {$host}
game-info-status = Estado: {$status}
game-info-status-waiting = Esperando en el vestíbulo
game-info-status-playing = En curso
game-info-options-header = Configuración:
game-info-no-options = Este juego no tiene opciones de configuración personalizadas.

# How to Play (Ctrl+F1)
how-to-play = Cómo jugar
game-rules-not-available = Las reglas de {$game} aún no están disponibles.
