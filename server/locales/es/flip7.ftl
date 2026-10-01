game-name-flip7 = Flip 7

# Opciones
flip7-set-target-score = Puntuación objetivo: { $score }
flip7-enter-target-score = Ingresa la puntuación objetivo
flip7-option-changed-target = Puntuación objetivo establecida en { $score }.
flip7-desc-target-score = El primer jugador que conserve esta cantidad de puntos totales después de una ronda completa gana la partida (por defecto 200, rango 50-1000).

# Cartas
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Doble
flip7-card-second-chance = Segunda oportunidad
flip7-card-stop = Stop
flip7-card-flip-three = Voltea 3

# Acciones del turno
flip7-hit = Voltea una carta
flip7-stay = Detente y guarda { $points } puntos
flip7-you-stay = Te detienes y guardas { $points } puntos.
flip7-player-stays = { $player } se detiene y guarda { $points } puntos.

# Ronda
flip7-round-start = Ronda { $round }. { $dealer } reparte.
flip7-round-end = La ronda { $round } terminó.
flip7-round-end-deck = Se acabó la baraja. La ronda terminó.
flip7-round-score = { $player } guarda { $points } puntos, total { $total }.
flip7-round-score-you = Guardas { $points } puntos, total { $total }.
flip7-round-bust = { $player } se pasó y no anota nada.
flip7-round-bust-you = Te pasaste y no anotas nada esta ronda.
flip7-match-win = ¡{ $player } gana la partida!
flip7-deck-reshuffled = El descarte se barajó de nuevo para formar la baraja.
flip7-pending-actions-discarded = { $player } se pasó, así que las cartas de acción pendientes se descartan.

# Voltear cartas
flip7-you-turn-card = Volteas una carta.
flip7-player-turns-card = { $player } voltea una carta.
flip7-your-card-is = Carta: { $card }.
flip7-player-card-is = Carta de { $player }: { $card }.
flip7-you-turn-stop = Volteaste Stop y debes elegir quién se detiene.
flip7-player-turns-stop = { $player } volteó Stop y debe elegir quién se detiene.
flip7-you-stop-alone = Como eras el único que seguía jugando, te detuviste solo y guardaste { $points } puntos.
flip7-player-stops-alone = { $player } era el único que seguía jugando, así que se detuvo y guardó { $points } puntos.
flip7-you-set-second-chance = Guardas una Segunda oportunidad.
flip7-player-sets-second-chance = { $player } guarda una Segunda oportunidad.
flip7-second-chance-held = { $player } tiene una Segunda oportunidad para entregarla más tarde.
flip7-second-chance-saves = Segunda oportunidad salva a { $player } del { $value } repetido.
flip7-second-chance-saves-you = Segunda oportunidad te salva del { $value } repetido.
flip7-you-bust = Volteas { $value } otra vez y te pasas. Pierdes esta ronda.
flip7-player-busts = { $player } voltea { $value } otra vez y se pasa.
flip7-flip-seven = ¡{ $player } consigue Flip 7 y gana el bono de 15 puntos!

# Elecciones con objetivo
flip7-target-stop = Haz que { $target } se detenga ({ $points } puntos)
flip7-target-flip-three = Haz que { $target } voltee 3 cartas
flip7-target-second-chance = Dale una Segunda oportunidad a { $target }
flip7-you-stop-player = Haces que { $target } se detenga con { $points } puntos.
flip7-player-stops-player = { $player } hace que { $target } se detenga con { $points } puntos.
flip7-you-flip-three = Haces que { $target } voltee 3 cartas.
flip7-player-flip-three = { $player } hace que { $target } voltee 3 cartas.
flip7-you-give-second-chance = Le das una Segunda oportunidad a { $target }.
flip7-player-gives-second-chance = { $player } le da una Segunda oportunidad a { $target }.
flip7-you-discard-second-chance = Nadie puede recibirla, así que la Segunda oportunidad se descarta.
flip7-player-discards-second-chance = { $player } no puede entregar la Segunda oportunidad, así que se descarta.
flip7-you-discard-action = No hay nadie a quien elegir, así que { $action } se descarta.
flip7-player-discards-action = { $player } no tiene a nadie a quien elegir, así que { $action } se descarta.

# Acciones de información
flip7-check-area = Revisar mi área
flip7-check-table = Revisar la mesa
flip7-check-deck = Revisar la baraja
flip7-read-card = Leer carta { $pos }
flip7-card-position = Carta { $pos }: { $value }.
flip7-no-card-position = Todavía no tienes la carta { $pos }.
flip7-you-label = Tú
flip7-area-status-stayed = , se detuvo esta ronda
flip7-area-status-busted = , se pasó esta ronda
flip7-area-numbers-none = Ninguna carta de número todavía
flip7-area-inline = { $who }{ $status }: { $numbers }. Total { $points } puntos.{ $bonus }
flip7-area-bonus-suffix = Bonos: { $bonuses }.
flip7-check-round = Ronda { $round }. Puntuación objetivo { $target }.
flip7-status-playing = sigue jugando
flip7-status-stayed = se detuvo
flip7-status-busted = se pasó
flip7-table-line = { $player }: { $status }, { $points } esta ronda, { $total } total
flip7-deck-line = Baraja: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }
flip7-discard-line = Descarte: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }

# Motivos de bloqueo
flip7-error-wait-choice = Espera a que se resuelva la elección de carta actual.
flip7-error-wait-flip-three = Espera a que termine Voltea 3.
flip7-error-wait-dealing = Espera a que se repartan las cartas.
flip7-error-not-playing-round = Ya no estás jugando esta ronda.
flip7-error-no-cards-left = No quedan cartas para voltear.
flip7-error-no-cards-to-bank = Todavía no tienes cartas para guardar puntos.
flip7-error-no-choice = No hay ninguna elección de carta que responder.

# Pantalla final
flip7-line-format = { $rank }. { $player }: { $points }
