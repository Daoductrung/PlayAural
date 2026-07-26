game-name-pig = Cerdito
pig-desc-team-mode = Juega individualmente o en una organización de equipos compatible. Un equipo comparte una sola puntuación y gana de inmediato cuando un miembro tiene suficientes puntos.

pig-roll = Lanzar el dado
pig-hold = Plantarte con { $points } puntos
pig-check-turn-status = Ver estado del turno

pig-game-start =
    Comienza Cerdito. { $team ->
        [yes] El primer equipo
       *[no] El primer jugador
    } en plantarse con { $target } puntos gana. El dado tiene { $sides } caras, y sacar un 1 hace perder todos los puntos sin guardar de ese turno. { $minimum ->
        [0] Puedes plantarte después de cualquier tirada que sume puntos.
       *[other] Debes acumular al menos { $minimum } puntos de turno antes de plantarte.
    }
pig-game-start-brief =
    Comienza Cerdito. Objetivo: { $target }. Dado: { $sides } caras. Mínimo para plantarse: { $minimum }.{ $team ->
        [yes] Los equipos comparten puntuación.
       *[no] Puntuaciones individuales.
    }
pig-round-start = Comienza la ronda { $round }. Cada jugador activo tomará un turno.
pig-round-start-brief = Ronda { $round }.

pig-you-roll-result = Sacaste { $roll }. Tu total del turno ahora es { $total } puntos.
pig-player-roll-result = { $player } sacó { $roll }. Su total del turno ahora es { $total } puntos.
pig-you-roll-result-brief = Tú: { $roll }; total del turno { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; total del turno { $total }.

pig-you-bust = Sacaste un 1 y pierdes todos los { $points } puntos sin guardar. Tu turno termina sin puntuación.
pig-player-busts = { $player } sacó un 1 y pierde todos los { $points } puntos sin guardar. Su turno termina sin puntuación.
pig-you-bust-brief = Sacaste 1 y pierdes { $points } puntos del turno.
pig-player-busts-brief = { $player } sacó 1 y pierde { $points } puntos del turno.

pig-you-hold =
    Te plantas con { $points } puntos. { $team ->
        [yes] Tu equipo ahora tiene { $total } puntos.
       *[no] Tu puntuación total ahora es de { $total } puntos.
    }
pig-player-holds =
    { $player } se planta con { $points } puntos. { $team ->
        [yes] { $team_name } ahora tiene { $total } puntos.
       *[no] Su puntuación total ahora es de { $total } puntos.
    }
pig-you-hold-brief =
    Te plantas con { $points };{ $team ->
        [yes] { $team_name } total { $total }.
       *[no] tu total { $total }.
    }
pig-player-holds-brief =
    { $player } se planta con { $points };{ $team ->
        [yes] { $team_name } total { $total }.
       *[no] total { $total }.
    }

pig-you-win =
    { $team ->
        [yes] ¡Tu equipo, { $winner }, es el ganador de Cerdito con { $score } puntos!
       *[no] ¡Eres el ganador de Cerdito con { $score } puntos!
    }
pig-winner =
    { $team ->
        [yes] ¡El ganador es { $winner }, con { $score } puntos!
       *[no] ¡El ganador es { $winner }, con { $score } puntos!
    }
pig-you-win-brief =
    { $team ->
        [yes] Ganador: tu equipo, { $winner }, con { $score }.
       *[no] Ganador: tú, con { $score }.
    }
pig-winner-brief = Ganador: { $winner }, con { $score }.

pig-confirm-risky-roll =
    Volver a lanzar arriesga { $points } puntos sin guardar, con un { $risk } por ciento de probabilidad de perderlos. { $winning ->
        [yes] Plantarte ahora te daría { $total } puntos y ganarías la partida.
       *[no] Plantarte ahora te daría { $total } de los { $target } puntos necesarios para ganar.
    } Presiona Lanzar de nuevo dentro de { $seconds } segundos para confirmar.

pig-action-resolving = El dado todavía está rodando. Espera el resultado.
pig-no-turn-points = Lanza el dado al menos una vez antes de plantarte.
pig-need-more-points = Tienes { $current } puntos de turno, pero esta mesa requiere al menos { $required } antes de plantarte.

pig-desc-target-score = El primer jugador o equipo en acumular esta cantidad total de puntos gana de inmediato (por defecto 100, rango 10-1000).
pig-set-min-bank = Mínimo para plantarse: { $points }
pig-set-dice-sides = Caras del dado: { $sides }
pig-enter-min-bank = Ingresa el mínimo de puntos de turno requeridos para plantarte:
pig-enter-dice-sides = Ingresa el número de caras del dado:
pig-option-changed-min-bank = Mínimo para plantarse cambiado a { $points } puntos.
pig-desc-min-bank = La cantidad de puntos de turno necesarios antes de que Plantarse esté disponible. Ponlo en 0 para el Cerdito estándar; debe ser menor que la puntuación objetivo (por defecto 0, rango 0-999).
pig-option-changed-dice = El dado ahora tiene { $sides } caras.
pig-desc-dice-sides = El número de caras del dado único. Sacar un 1 siempre hace perder el total del turno (por defecto 6, rango 4-20).

pig-error-target-out-of-range = La puntuación objetivo { $value } no es válida. Elige un valor de { $min } a { $max }.
pig-error-min-bank-out-of-range = El mínimo para plantarse { $value } no es válido. Elige un valor de { $min } a { $max }.
pig-error-dice-sides-out-of-range = Un dado de { $value } caras no es compatible. Elige entre { $min } y { $max } caras.
pig-error-min-bank-too-high = El mínimo para plantarse { $minimum } debe ser menor que la puntuación objetivo de { $target }.

pig-status-target = Puntuación objetivo: { $target } puntos.
pig-status-round = Ronda actual: { $round }.
pig-status-current-turn = { $player } está jugando: { $banked } guardados, { $turn } en este turno, { $potential } si se planta ahora.
pig-status-standing = { $rank }. { $team }: { $score } puntos.

pig-line-format = { $rank }. { $player }: { $points }
