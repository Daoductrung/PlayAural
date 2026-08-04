game-name-tossup = Dados al Vuelo

tossup-roll-first =
    Lanzar { $count } { $count ->
        [one] dado
       *[other] dados
    }
tossup-roll-remaining =
    Lanzar { $count } { $count ->
        [one] dado restante
       *[other] dados restantes
    }
tossup-bank =
    Guardar { $points } { $points ->
        [one] punto
       *[other] puntos
    }
tossup-check-turn-status = Ver estado del turno

tossup-game-start = Comienza Dados al Vuelo con reglas { $rules }, { $dice } dados por conjunto, y un umbral objetivo de { $target }. Supera el umbral y termina los turnos restantes para ganar.
tossup-game-start-brief = Comienza Dados al Vuelo. Supera { $target }.
tossup-round-start = Comienza la ronda { $round }.
tossup-round-start-brief = Ronda { $round }.

tossup-your-turn =
    Tu turno. Tu puntuación guardada es { $score }; lanza { $dice } { $dice ->
        [one] dado
       *[other] dados
    } para empezar.
tossup-player-turn =
    Turno de { $player } con { $score } puntos guardados y { $dice } { $dice ->
        [one] dado
       *[other] dados
    }.
tossup-your-turn-brief = Tu turno: { $score } puntos.
tossup-player-turn-brief = Turno de { $player }: { $score } puntos.

tossup-you-roll = Sacaste { $results }.
tossup-player-rolls = { $player } sacó { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] Tú: { $results }; total del turno { $turn_points }; conjunto nuevo de { $dice_count }.
       *[no] Tú: { $results }; total del turno { $turn_points }; quedan { $dice_count }.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; total del turno { $turn_points }; conjunto nuevo de { $dice_count }.
       *[no] { $player }: { $results }; total del turno { $turn_points }; quedan { $dice_count }.
    }

tossup-result-green = { $count } verdes
tossup-result-yellow = { $count } amarillos
tossup-result-red = { $count } rojos

tossup-you-have-points =
    Apartas { $gained } { $gained ->
        [one] dado verde
       *[other] dados verdes
    }. El total de tu turno es { $turn_points }, con { $dice_count } { $dice_count ->
        [one] dado restante
       *[other] dados restantes
    }.
tossup-player-has-points =
    { $player } aparta { $gained } { $gained ->
        [one] dado verde
       *[other] dados verdes
    } y tiene { $turn_points } puntos de turno, con { $dice_count } { $dice_count ->
        [one] dado restante
       *[other] dados restantes
    }.

tossup-you-get-fresh = Todos los dados son verdes. Recibes un conjunto nuevo de { $count } dados y puedes volver a lanzar o guardar.
tossup-player-gets-fresh = Todos los dados son verdes. { $player } recibe un conjunto nuevo de { $count } dados.

tossup-you-bust =
    { $variant ->
        [Standard] Luz roja: no sacaste ningún verde y al menos un rojo. Tu turno termina y pierdes { $points } puntos sin guardar.
       *[PlayAural] Todos los dados que lanzaste son rojos. Tu turno termina y pierdes { $points } puntos sin guardar.
    }
tossup-player-busts =
    { $variant ->
        [Standard] Luz roja: { $player } no sacó ningún verde y al menos un rojo, terminando el turno y perdiendo { $points } puntos sin guardar.
       *[PlayAural] Todos los dados que lanzó { $player } son rojos, terminando el turno y perdiendo { $points } puntos sin guardar.
    }
tossup-you-bust-brief = Tú: { $results }; te pasas; pierdes { $points }.
tossup-player-busts-brief = { $player }: { $results }; se pasa; pierde { $points }.

tossup-you-bank = Guardas { $points } puntos, llevando tu puntuación total a { $total }.
tossup-player-banks = { $player } guarda { $points } puntos, llevando su puntuación total a { $total }.
tossup-you-bank-brief = Guardas { $points }; total { $total }.
tossup-player-banks-brief = { $player } guarda { $points }; total { $total }.

tossup-you-trigger-final-turns =
    Superas el umbral de { $target } puntos con { $score }.
    { $count ->
        [one] El jugador restante recibe un turno final.
       *[other] Los { $count } jugadores restantes reciben cada uno un turno final.
    }
tossup-player-triggers-final-turns =
    { $player } supera el umbral de { $target } puntos con { $score }.
    { $count ->
        [one] El jugador restante recibe un turno final.
       *[other] Los { $count } jugadores restantes reciben cada uno un turno final.
    }
tossup-you-trigger-final-turns-brief =
    Estableces la puntuación a superar en { $score }; { $count } { $count ->
        [one] turno restante.
       *[other] turnos restantes.
    }
tossup-player-triggers-final-turns-brief =
    { $player } establece la puntuación a superar en { $score }; { $count } { $count ->
        [one] turno restante.
       *[other] turnos restantes.
    }

tossup-you-win = Ganas Dados al Vuelo con { $score } puntos.
tossup-winner = { $player } gana Dados al Vuelo con { $score } puntos.
tossup-you-win-brief = Ganas: { $score }.
tossup-winner-brief = { $player } gana: { $score }.
tossup-tie-tiebreaker = { $players } están empatados con la puntuación más alta por encima del objetivo. Solo esos jugadores continúan a una ronda de desempate.
tossup-tie-tiebreaker-brief = Desempate: { $players }.
tossup-tiebreaker-round-start = Comienza la ronda de desempate { $round } para { $players }.
tossup-tiebreaker-round-start-brief = Ronda de desempate { $round }: { $players }.

tossup-your-turn-awaiting-roll =
    Tu turno todavía no ha empezado a lanzar. Tienes { $score } puntos guardados y { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } listos.
tossup-player-turn-awaiting-roll =
    { $player } todavía no ha lanzado. Tiene { $score } puntos guardados y { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } listos.
tossup-your-turn-status =
    Tu última tirada fue { $results }. Tienes { $turn_points } puntos de turno sin guardar, { $score } puntos guardados, y { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } listos para lanzar.
tossup-player-turn-status =
    La última tirada de { $player } fue { $results }. Tiene { $turn_points } puntos de turno sin guardar, { $score } puntos guardados, y { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } listos para lanzar.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] Guardar ahora te pondría a la cabeza con { $total } puntos, por encima del umbral de { $target } puntos.
       *[no] Actualmente tienes { $points } puntos de turno sin guardar.
    }
    Lanzar { $dice } { $dice ->
        [one] dado
       *[other] dados
    } tiene alrededor de un { $risk } por ciento de probabilidad de pasarte. Presiona Lanzar de nuevo dentro de { $seconds } segundos para confirmar, o guarda para proteger los puntos.

tossup-set-rules-variant = Reglas: { $variant }
tossup-select-rules-variant = Selecciona las reglas de dados y de pasarse:
tossup-option-changed-rules = Reglas cambiadas a { $variant }.
tossup-desc-rules-variant = Clásico usa tres caras verdes, dos amarillas y una roja por dado; una tirada sin verdes y con al menos un rojo hace que te pases. Indulgente da a los tres colores las mismas probabilidades y solo te pasas si todos salen rojos.

tossup-desc-target-score = La partida entra en sus turnos finales de respuesta después de que un jugador guarde más de esta puntuación (por defecto 100, rango 20-500).
tossup-set-starting-dice = Dados por conjunto: { $count }
tossup-enter-starting-dice = Ingresa el número de dados en cada conjunto nuevo:
tossup-option-changed-dice = Dados por conjunto cambiados a { $count }.
tossup-desc-starting-dice = Elige cuántos dados empiezan cada turno y regresan después de que cada dado se vuelve verde (por defecto 10, rango 5-20).


tossup-rules-standard = Clásico
tossup-rules-PlayAural = Indulgente
tossup-rules-standard-desc = Tres caras verdes, dos amarillas y una roja. Te pasas si no sale ningún verde y hay al menos un rojo.
tossup-rules-PlayAural-desc = Las mismas probabilidades para los tres colores. Solo te pasas si todos los dados lanzados salen rojos.

tossup-error-roll-not-playing = No puedes lanzar porque Dados al Vuelo no está en curso actualmente.
tossup-error-roll-no-turn = No puedes lanzar porque Dados al Vuelo no tiene ningún turno activo en este momento.
tossup-error-roll-not-your-turn = No puedes lanzar durante el turno de { $player }. Espera a que te llegue el turno.
tossup-error-bank-not-playing = No puedes guardar porque Dados al Vuelo no está en curso actualmente.
tossup-error-bank-no-turn = No puedes guardar porque Dados al Vuelo no tiene ningún turno activo en este momento.
tossup-error-bank-not-your-turn = No puedes guardar durante el turno de { $player }. Espera a que te llegue el turno.
tossup-error-bank-roll-first = Lanza al menos una vez antes de guardar. Una tirada de solo amarillos puede guardarse por cero puntos para terminar tu turno.
tossup-error-spectator-action = Los espectadores pueden ver el estado público de Dados al Vuelo, pero no pueden lanzar ni guardar puntos.
tossup-error-status-not-playing = El estado del turno no está disponible porque Dados al Vuelo no está en curso actualmente.
tossup-error-status-no-turn = El estado del turno no está disponible porque Dados al Vuelo no tiene ningún jugador activo en este momento.
tossup-error-target-out-of-range = El umbral objetivo es { $value }; debe estar entre { $min } y { $max } puntos.
tossup-error-dice-out-of-range = El tamaño del conjunto nuevo es { $value }; debe estar entre { $min } y { $max } dados.
tossup-error-rules-variant = El valor de reglas "{ $variant }" no es compatible. Elige Clásico o Indulgente.

tossup-line-format = { $rank }. { $player }: { $points }
