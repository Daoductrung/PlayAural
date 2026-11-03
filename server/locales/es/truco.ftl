game-name-truco = Truco

# Opciones
truco-set-variant = Variante: { $mode }
truco-select-variant = Selecciona la variante del truco:
truco-option-changed-variant = La variante ahora es { $mode }.
truco-desc-variant = El truco argentino usa la baraja española de 40 cartas, con envido y flor opcional. El truco brasileño (paulista) usa una baraja francesa con una carta volteada, la vira, que decide las cartas más fuertes, y subidas que valen 3, 6, 9 y 12 puntos. El truco español (truc valenciano) usa una baraja de 22 cartas con envit y el Joc fora, que vale toda la partida.
truco-variant-argentine = Truco argentino
truco-variant-brazilian = Truco brasileño
truco-variant-spanish = Truco español
truco-length-15 = 15 puntos
truco-length-30 = 30 puntos
truco-set-length = Duración de la partida: { $mode }
truco-select-length = Selecciona la duración de la partida:
truco-option-changed-length = La duración de la partida ahora es { $mode }.
truco-desc-length = En una partida a 15 puntos gana quien llegue primero a 15 puntos. En una partida a 30 puntos, los puntos del 1 al 15 son las malas (primera mitad) y los del 16 al 30 son las buenas (segunda mitad); gana quien llegue primero a 30.
truco-set-flor = Flor: { $enabled }
truco-option-changed-flor = La flor ahora está { $enabled }.
truco-desc-flor = Si está activada, quien recibe tres cartas del mismo palo tiene flor. Se anuncia automáticamente y cancela el envido. La Flor vale 3 puntos, la Contraflor 6 y la Contraflor al resto vale lo que le falta al equipo que va adelante para ganar. Solo quien tiene flor puede responder o subir. La flor vale 20 más el valor de las tres cartas (las figuras valen cero), así que 7, 6 y 5 de un palo suman 38; gana la flor más alta. Si está desactivada, tres cartas de un mismo palo no tienen ningún valor especial.
truco-desc-team-mode = Individual es una partida uno contra uno para 2 jugadores. 2v2 usa 4 jugadores y 3v3 usa 6 jugadores; los compañeros comparten el puntaje y pueden cantar por todo el equipo.

# Baraja española
truco-suit-oros = oros
truco-suit-copas = copas
truco-suit-espadas = espadas
truco-suit-bastos = bastos
truco-card-name = { $rank } de { $suit }

# Cantos
truco-call-truco = Truco
truco-call-retruco = Retruco
truco-call-valecuatro = Vale cuatro
truco-call-envido = Envido
truco-call-real-envido = Real envido
truco-call-falta-envido = Falta envido
truco-call-flor = Flor
truco-call-contraflor = Contraflor
truco-call-contraflor-al-resto = Contraflor al resto

# Acciones
truco-action-play-card = { $card }
truco-action-accept = Quiero (aceptar)
truco-action-decline = No quiero (rechazar)
truco-action-mazo = Me voy al mazo (abandonar tus cartas)
truco-read-hand = Leer tus cartas
truco-read-table = Leer las cartas de la mesa
truco-read-calls = Leer los cantos actuales

# Desarrollo de la partida y de la mano
truco-game-start-flor = Comienza el truco con flor. Gana quien llegue primero a { $points } puntos.
truco-game-start-no-flor = Comienza el truco sin flor. Gana quien llegue primero a { $points } puntos.
truco-hand-start = Comienza la mano { $hand }. Se reparten las cartas.
truco-dealer-you = Tú repartes.
truco-dealer-player = { $player } reparte.
truco-mano-you = Eres mano y juegas primero.
truco-mano-player = { $player } es mano y juega primero.
truco-your-cards = Tus cartas: { $cards }.
truco-no-cards = Ya no te quedan cartas.
truco-your-turn = Es tu turno de jugar una carta.

# Cartas jugadas y bazas
truco-play-you = Juegas { $card }.
truco-play-player = { $player } juega { $card }.
truco-trick-win-you = Baza { $trick }: ganas tú con { $card }.
truco-trick-win-teammate = Baza { $trick }: gana tu compañero { $player } con { $card }.
truco-trick-win-opponent = Baza { $trick }: gana { $player } con { $card } para { $team }.
truco-trick-tie = La baza { $trick } queda empatada: es parda.

# Cantar y responder
truco-call-you = Cantas { $call }.
truco-call-player = { $player } canta { $call }.
truco-call-goes-first-you = Cantas { $call }. El envido va primero, antes de responder al truco.
truco-call-goes-first-player = { $player } canta { $call }. El envido va primero, antes de responder al truco.
truco-pending-answer = { $player } cantó { $call }. Responde con Quiero o No quiero, o sube la apuesta.
truco-pending-wait = Esperando que { $team } responda a { $call }.
truco-accept-you = Dices Quiero a { $call }.
truco-accept-player = { $player } dice Quiero a { $call }.
truco-decline-you = Dices No quiero a { $call }.
truco-decline-player = { $player } dice No quiero a { $call }.
truco-mazo-you = Dices Me voy al mazo y abandonas tus cartas.
truco-mazo-player = { $player } dice Me voy al mazo y abandona sus cartas.
truco-team-folded-your-team = Todos los integrantes de tu equipo se fueron al mazo.
truco-team-folded-team = Todos los integrantes de { $team } se fueron al mazo.
truco-flor-announce-you = Tienes flor.
truco-flor-announce-player = { $player } tiene flor.
truco-flor-cancels-envido = El envido se cancela por la flor.
truco-reveal-envido-you = El envido se ganó con tus cartas: { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.
truco-reveal-envido-player = El envido lo ganó { $player } con { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.
truco-reveal-flor-you = La flor se ganó con tus cartas: { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.
truco-reveal-flor-player = La flor la ganó { $player } con { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.

# Envido y flor
truco-falta-envido-value = La falta envido vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.
truco-falta-envido-game = Falta envido: ambos equipos están en las malas, así que quien la gane gana la partida completa.

# Puntos y puntaje
truco-reason-truco = el Truco
truco-reason-envido = el Envido
truco-reason-flor = la Flor
truco-reason-hand = la mano
truco-points-your-team = Tu equipo suma { $points } { $points ->
    [one] punto
   *[other] puntos
} por { $reason }.
truco-points-team = { $team } suma { $points } { $points ->
    [one] punto
   *[other] puntos
} por { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] punto
   *[other] puntos
}.
truco-half-buenas-your-team = Tu equipo entra en las buenas, la segunda mitad.
truco-half-buenas-team = { $team } entra en las buenas, la segunda mitad.

# Información
truco-status-no-truco = No se ha cantado Truco. La mano vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.
truco-status-truco = La mano está en { $call } y vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.
truco-status-truco-pending = { $call } espera la respuesta de { $team }.
truco-status-envido-open = Todavía se puede cantar el envido en esta mano.
truco-status-envido-closed = El envido está cerrado en esta mano.
truco-table-empty = Todavía no se jugó ninguna carta.
truco-table-trick = Baza { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Errores y motivos de acciones deshabilitadas
truco-error-bad-count = El truco necesita 2, 4 o 6 jugadores, pero hay { $count }.
truco-error-team-mode-count = No se puede usar el modo de equipos { $mode } con { $count } jugadores. Usa Individual con 2 jugadores, 2v2 con 4 o 3v3 con 6.
truco-error-not-your-turn = Es el turno de { $player } para jugar una carta.
truco-error-answer-first = Debes responder a { $call } antes de hacer otra cosa. Elige Quiero o No quiero, o sube la apuesta.
truco-error-nothing-to-answer = No hay ningún canto esperando tu respuesta.
truco-error-own-team-call = Tu equipo hizo ese canto. Espera a que { $team } responda a { $call }.
truco-error-envido-late = El envido solo se puede cantar antes de jugar tu primera carta.
truco-error-envido-closed = El envido está cerrado porque el truco ya fue aceptado.
truco-error-envido-done = El envido ya se jugó en esta mano.
truco-error-raise-max = El truco ya está en Vale cuatro y no se puede subir más.
truco-error-raise-holder = Tu equipo hizo el último canto del truco. Solo { $team } puede subirlo ahora.
truco-error-flor-none = Te fuiste al mazo en esta mano, así que no puedes cantar ni responder.
truco-error-flor-holders-only = Solo quien tiene flor puede responder o subir una flor.
truco-error-card-not-held = No tienes esa carta.
truco-error-hand-over = La mano ya terminó.

# Fin de la partida
truco-game-win-you = ¡Ganas la partida con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
truco-game-win-player = ¡{ $player } gana la partida con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
truco-game-win-your-team = ¡Tu equipo gana la partida con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
truco-game-win-team = ¡{ $team } gana la partida con { $score } { $score ->
    [one] punto
   *[other] puntos
}!
truco-end-title = Resultados del truco
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] punto
   *[other] puntos
}.

# Errores adicionales y mensajes del modo individual
truco-error-flor-off = La flor está desactivada en esta partida, así que no hay nada que cantar ni responder.
truco-error-flor-window = Primero hay que resolver la flor. No se puede cantar truco hasta que se juegue la primera carta.
truco-error-flor-window-closed = La contraflor solo se puede cantar mientras ambos equipos tienen flor y antes de jugar la primera carta.
truco-error-envido-flor = El envido se canceló en esta mano porque alguien tiene flor.
truco-error-envido-cannot-raise = No se puede agregar { $call } al envido que se está jugando.
truco-points-you = Sumas { $points } { $points ->
    [one] punto
   *[other] puntos
} por { $reason }.
truco-points-player = { $player } suma { $points } { $points ->
    [one] punto
   *[other] puntos
} por { $reason }.
truco-half-buenas-you = Entras en las buenas, la segunda mitad.
truco-half-buenas-player = { $player } entra en las buenas, la segunda mitad.

# Información de cartas, descripciones y gestos táctiles
truco-card-info-label = Información del elemento
truco-card-info = { $card }: gana a { $beats } de las otras { $total } cartas de esta baraja.
truco-card-info-envido = { $card }: gana a { $beats } de las otras { $total } cartas de esta baraja. Valor para el envido: { $value }.
truco-desc-call-ladder = { $call }: sube la mano a { $points } { $points ->
    [one] punto
   *[other] puntos
}. Si lo rechazan, quien cantó gana { $refused } { $refused ->
    [one] punto
   *[other] puntos
}.
truco-desc-call-envido = { $call }: ambos lados comparan su envido. Si lo aceptan, quien gane suma { $points } { $points ->
    [one] punto
   *[other] puntos
}. Si lo rechazan, quien cantó suma { $refused } { $refused ->
    [one] punto
   *[other] puntos
}.
truco-desc-call-flor = { $call }: quienes tienen flor comparan sus flores. Si lo aceptan, quien gane suma { $points } { $points ->
    [one] punto
   *[other] puntos
}. Si lo rechazan, quien cantó suma { $refused } { $refused ->
    [one] punto
   *[other] puntos
}.
truco-desc-accept = Aceptar { $call } y seguir jugando.
truco-desc-decline = Rechazar { $call }. El otro lado suma { $points } { $points ->
    [one] punto
   *[other] puntos
} y la mano termina.
truco-desc-mazo = Abandonar tus cartas. Si todo tu equipo se va al mazo, el otro lado gana la mano.
truco-trick-tie-neutral = La baza { $trick } queda empatada.
