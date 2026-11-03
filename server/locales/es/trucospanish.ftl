# Opciones
trucospanish-length-18 = 18 puntos por came
trucospanish-length-24 = 24 puntos por came
trucospanish-set-length = Duración de la came: { $mode }
trucospanish-select-length = Selecciona la duración de la came:
trucospanish-option-changed-length = La duración de la came ahora es { $mode }.
trucospanish-desc-length = La partida se gana al ganar dos cames. Cada came se juega hasta el número de puntos elegido: 24 como en el campeonato fallero de València y en el torneo de la Universitat Politècnica de València, o 18 como en el torneo de Torrent y en la descripción del Museu d'Història de València. Cuando un lado lo alcanza, gana la came y los dos marcadores vuelven a cero. La falta vale lo que le falta al que va adelante para terminar la came, y el Joc fora gana la partida entera.
trucospanish-desc-team-mode = Individual es una partida uno contra uno para 2 jugadores. 2v2 usa 4 jugadores; los compañeros comparten el puntaje y pueden cantar por todo el equipo.

# Cantos
trucospanish-call-truc = Truc
trucospanish-call-retruc = Retruc
trucospanish-call-quatre-val = Quatre val
trucospanish-call-joc-fora = Joc fora
trucospanish-call-envit = Envit
trucospanish-call-torna = Torna
trucospanish-call-la-falta = La falta

# Acciones y mensajes
trucospanish-action-accept = Vull (aceptar)
trucospanish-action-decline = No vull (rechazar)
trucospanish-action-mazo = Me'n vaig (abandonar la mano)
trucospanish-accept-you = Dices Vull a { $call }.
trucospanish-accept-player = { $player } dice Vull a { $call }.
trucospanish-decline-you = Dices No vull a { $call }.
trucospanish-decline-player = { $player } dice No vull a { $call }.
trucospanish-mazo-you = Dices Me'n vaig y abandonas la mano por todo tu equipo.
trucospanish-mazo-player = { $player } dice Me'n vaig y abandona la mano por todo el equipo.
trucospanish-reason-truc = el Truc
trucospanish-reason-envit = el Envit
trucospanish-game-start = Comienza el truco español. Gana la partida quien gane dos cames de { $points } puntos.
trucospanish-desc-mazo = Abandonar la mano por todo tu equipo. El otro lado suma el valor actual de la mano.
trucospanish-came-you = ¡Ganas una came! Llevas { $cames } { $cames ->
    [one] came
   *[other] cames
}. El marcador vuelve a cero.
trucospanish-came-player = { $player } gana una came y lleva { $cames } { $cames ->
    [one] came
   *[other] cames
}. El marcador vuelve a cero.
trucospanish-came-your-team = ¡Tu equipo gana una came! Lleváis { $cames } { $cames ->
    [one] came
   *[other] cames
}. El marcador vuelve a cero.
trucospanish-came-team = { $team } gana una came y lleva { $cames } { $cames ->
    [one] came
   *[other] cames
}. El marcador vuelve a cero.

trucospanish-pending-answer = { $player } cantó { $call }. Responde con Vull o No vull, o sube la apuesta.
trucospanish-error-answer-first = Debes responder a { $call } antes de hacer otra cosa. Elige Vull o No vull, o sube la apuesta.
trucospanish-error-raise-max = El Joc fora ya es el canto más alto y no se puede subir.
trucospanish-error-bad-count = El truco español necesita 2 o 4 jugadores, pero hay { $count }.
trucospanish-error-team-mode-count = El modo de equipos { $mode } no se puede usar con { $count } jugadores. Usa Individual para 2 jugadores o 2v2 para 4 jugadores.
trucospanish-status-envit-open = Aún se puede cantar envit en esta mano.
trucospanish-status-envit-closed = El envit está cerrado en esta mano.
trucospanish-status-no-truc = No se ha cantado Truc. La mano vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.
trucospanish-falta-value = La falta vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.
trucospanish-reveal-envit-you = El envit se ganó con tus cartas: { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.
trucospanish-reveal-envit-player = { $player } ganó el envit con { $cards }, que valen { $value } { $value ->
    [one] punto
   *[other] puntos
}.
trucospanish-error-envit-late = El envit solo se puede cantar antes de jugar tu primera carta.
trucospanish-error-envit-closed = El envit está cerrado porque ya se aceptó el Truc.
trucospanish-error-envit-done = El envit ya se jugó en esta mano.
trucospanish-error-envit-cannot-raise = { $call } no se puede añadir al envit que se está jugando.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] punto
   *[other] puntos
} en esta came, { $cames } { $cames ->
    [one] came ganada
   *[other] cames ganadas
}
trucospanish-game-win-you = ¡Ganas la partida con { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-player = { $player } gana la partida con { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-game-win-your-team = ¡Tu equipo gana la partida con { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-team = { $team } gana la partida con { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] came
   *[other] cames
}
trucospanish-cames-line = { $team }: { $cames } { $cames ->
    [one] came ganada
   *[other] cames ganadas
}
