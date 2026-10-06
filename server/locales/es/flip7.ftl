game-name-flip7 = Flip 7

# Opciones
flip7-set-target-score = Puntuación objetivo: { $score }
flip7-enter-target-score = Ingresa la puntuación objetivo
flip7-option-changed-target = Puntuación objetivo establecida en { $score }.
flip7-desc-target-score = La puntuación que activa la comprobación del ganador al final de una ronda. Gana el total más alto; un empate en el liderato prolonga la partida. Predeterminado: 200, rango 50-1000.

# Cartas
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Doble
flip7-card-second-chance = Segunda oportunidad
flip7-card-freeze = Congelar
flip7-card-flip-three = Voltea 3

# Acciones del turno
flip7-hit = Voltea una carta
flip7-stay = Detente y guarda { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }
flip7-stay-base = Detente y guarda
flip7-stay-banked = Detente y guarda (puntos ya guardados)
flip7-you-stay = Te detienes y guardas { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stays = { $player } se detiene y guarda { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.

# Ronda
flip7-round-start = Ronda { $round }. { $dealer } reparte.
flip7-round-start-you = Ronda { $round }. Tú repartes.
flip7-round-end = La ronda { $round } terminó.
flip7-round-score = { $player } guarda { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }, total { $total } punto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-score-you = Guardas { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }, total { $total } punto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-bust = { $player } se pasó y no anota nada.
flip7-round-bust-you = Te pasaste y no anotas nada esta ronda.
flip7-match-win = ¡{ $player } gana la partida!
flip7-match-win-you = ¡Ganaste la partida!
flip7-deck-reshuffled = El descarte se barajó de nuevo para formar la baraja.
flip7-you-pending-bust-discarded = Te pasaste, así que tus cartas de acción pendientes se descartan.
flip7-player-pending-bust-discarded = { $player } se pasó, así que las cartas de acción pendientes se descartan.

# Voltear cartas
flip7-you-turn-card = Volteas una carta.
flip7-player-turns-card = { $player } voltea una carta.
flip7-your-card-is = Carta: { $card }.
flip7-player-card-is = Carta de { $player }: { $card }.
flip7-you-stop-alone = Como solo quedabas tú jugando, te detuviste y guardaste { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-alone = Como solo { $player } quedaba jugando, se detuvo y guardó { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-set-second-chance = Guardas una Segunda oportunidad.
flip7-player-sets-second-chance = { $player } guarda una Segunda oportunidad.
flip7-second-chance-saves = Segunda oportunidad salva a { $player } del { $value } repetido.
flip7-second-chance-saves-you = Segunda oportunidad te salva del { $value } repetido.
flip7-you-bust = Volteas { $value } otra vez y te pasas. Pierdes esta ronda.
flip7-player-busts = { $player } voltea { $value } otra vez, se pasa y no anota nada esta ronda.
flip7-flip-seven = ¡{ $player } consigue Flip 7 y gana el bono de { $bonus } puntos!
flip7-flip-seven-you = ¡Consigues Flip 7 y ganas el bono de { $bonus } puntos!

# Elecciones con objetivo
flip7-target-freeze = Congela a { $target } ({ $points } punto{ $points ->
        [one] { "" }
       *[other] s
    })
flip7-target-flip-three = Haz que { $target } voltee 3 cartas
flip7-target-second-chance-self = Guardar Segunda oportunidad
flip7-target-second-chance = Dale una Segunda oportunidad a { $target }
flip7-you-stop-player = Haces que { $target } se detenga con { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-player = { $player } hace que { $target } se detenga con { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-stop-yourself = Te detienes y guardas { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-themself = { $player } se detiene y guarda { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-flip-three = Haces que { $target } voltee 3 cartas.
flip7-player-flip-three = { $player } hace que { $target } voltee 3 cartas.
flip7-you-flip-three-self = Volteas 3 cartas.
flip7-player-flips-three-self = { $player } voltea 3 cartas.
flip7-you-give-second-chance = Le das una Segunda oportunidad a { $target }.
flip7-player-gives-second-chance = { $player } le da una Segunda oportunidad a { $target }.
flip7-you-discard-second-chance = Nadie puede recibirla, así que la Segunda oportunidad se descarta.
flip7-player-discards-second-chance = { $player } no puede entregar la Segunda oportunidad, así que se descarta.
flip7-you-discard-action = No hay nadie a quien elegir, así que { $action } se descarta.
flip7-player-discards-action = { $player } no tiene a nadie a quien elegir, así que { $action } se descarta.

# Acciones de información
flip7-check-area = Revisar mi área
flip7-check-area-description = Escucha tus cartas boca arriba, estado, bonos y total actual de la ronda.
flip7-check-table = Revisar la mesa
flip7-check-table-description = Abre una vista en vivo de la ronda, la fase actual y el área pública y la puntuación de cada jugador.
flip7-check-deck = Revisar la baraja
flip7-check-deck-description = Escucha cuántas cartas quedan en la baraja y en el descarte.
flip7-check-scores = Revisar puntuaciones
flip7-review-scores = Puntuaciones detalladas
flip7-you-label = Tú
flip7-area-status-playing = sigue jugando
flip7-area-status-scored = puntuó
flip7-area-status-stayed = se detuvo
flip7-area-status-busted = se pasó
flip7-area-numbers-none = ninguna
flip7-area-inline = { $who}, { $status }. Cartas de número: { $numbers }. Puntuación de la ronda: { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-inline-with-specials = { $who}, { $status }. Cartas de número: { $numbers }. Otras cartas: { $specials }. Puntuación de la ronda: { $points } punto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-resolving-card = { $area } Carta en resolución: { $card }.
flip7-check-round = Ronda { $round }. Puntuación objetivo { $target }.
flip7-table-line = { $area } Total de la partida: { $total } punto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-deck-line = Baraja: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }
flip7-discard-line = Descarte: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }

# Estado del turno y de las secuencias
flip7-whose-turn-choice-you = Estás eligiendo un objetivo para { $action }.
flip7-whose-turn-choice-player = { $player } está eligiendo un objetivo para { $action }.
flip7-whose-turn-dealing-you = Ronda { $round }: tú repartes.
flip7-whose-turn-dealing-player = Ronda { $round }: { $player } reparte.
flip7-whose-turn-deal-card-you = Ronda { $round }: tu carta inicial se está resolviendo.
flip7-whose-turn-deal-card-player = Ronda { $round }: la carta inicial de { $player } se está resolviendo.
flip7-whose-turn-card-you = Tu carta se está resolviendo.
flip7-whose-turn-card-player = La carta de { $player } se está resolviendo.
flip7-whose-turn-flip-three-you = Estás volteando 3 cartas.
flip7-whose-turn-flip-three-player = { $player } está volteando 3 cartas.
flip7-whose-turn-banking-you = Te estás deteniendo y guardando puntos.
flip7-whose-turn-banking-player = { $player } se está deteniendo y guardando puntos.
flip7-whose-turn-round-end = La ronda { $round } está cerrando su puntuación.
flip7-whose-turn-match-end = Se está anunciando al ganador.
flip7-whose-turn-resolving = Se está resolviendo una secuencia de cartas.

# Motivos de bloqueo
flip7-error-wait-card = Espera a que se resuelva la carta revelada.
flip7-error-wait-choice = Espera a que se resuelva la elección de carta actual.
flip7-error-wait-flip-three = Espera a que termine Voltea 3.
flip7-error-wait-dealing = Espera a que se repartan las cartas.
flip7-error-not-playing-round = Ya no estás jugando esta ronda.
flip7-error-no-cards-to-bank = Todavía no tienes cartas para guardar puntos.
flip7-error-no-choice = No hay ninguna elección de carta que responder.
flip7-error-wait-banking = Espera a que se guarden los puntos actuales.
flip7-error-choice-not-ready = Espera a que la elección de objetivo esté lista.

# Pantalla final
flip7-line-format = { $rank }. { $player }: { $points }
