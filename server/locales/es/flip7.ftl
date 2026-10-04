game-name-flip7 = Flip 7

# Opciones
flip7-set-target-score = Puntuación objetivo: { $score }
flip7-enter-target-score = Ingresa la puntuación objetivo
flip7-option-changed-target = Puntuación objetivo establecida en { $score }.
flip7-desc-target-score = Cuántos puntos se necesitan para ganar la partida. Predeterminado: 200, rango 50-1000.

# Cartas
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Doble
flip7-card-second-chance = Segunda oportunidad
flip7-card-freeze = Congelar
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
flip7-match-win-you = ¡Ganaste la partida!
flip7-deck-reshuffled = El descarte se barajó de nuevo para formar la baraja.
flip7-you-pending-discarded = Ya no estás jugando esta ronda, así que tus cartas de acción pendientes se descartan.
flip7-player-pending-discarded = { $player } ya no juega esta ronda, así que las cartas de acción pendientes se descartan.
flip7-you-pending-bust-discarded = Te pasaste, así que tus cartas de acción pendientes se descartan.
flip7-player-pending-bust-discarded = { $player } se pasó, así que las cartas de acción pendientes se descartan.

# Voltear cartas
flip7-you-turn-card = Volteas una carta.
flip7-player-turns-card = { $player } voltea una carta.
flip7-your-card-is = Carta: { $card }.
flip7-player-card-is = Carta de { $player }: { $card }.
flip7-you-stop-alone = Como solo quedabas tú jugando, te detuviste y guardaste { $points } puntos.
flip7-player-stops-alone = Como solo { $player } quedaba jugando, se detuvo y guardó { $points } puntos.
flip7-you-set-second-chance = Guardas una Segunda oportunidad.
flip7-player-sets-second-chance = { $player } guarda una Segunda oportunidad.
flip7-second-chance-saves = Segunda oportunidad salva a { $player } del { $value } repetido.
flip7-second-chance-saves-you = Segunda oportunidad te salva del { $value } repetido.
flip7-you-bust = Volteas { $value } otra vez y te pasas. Pierdes esta ronda.
flip7-player-busts = { $player } voltea { $value } otra vez y se pasa.
flip7-flip-seven = ¡{ $player } consigue Flip 7 y gana el bono de 15 puntos!
flip7-flip-seven-you = ¡Consigues Flip 7 y ganas el bono de 15 puntos!

# Elecciones con objetivo
flip7-target-freeze = Congela a { $target } ({ $points } puntos)
flip7-target-flip-three = Haz que { $target } voltee 3 cartas
flip7-target-second-chance = Dale una Segunda oportunidad a { $target }
flip7-you-stop-player = Haces que { $target } se detenga con { $points } puntos.
flip7-player-stops-player = { $player } hace que { $target } se detenga con { $points } puntos.
flip7-you-stop-yourself = Te detienes y guardas { $points } puntos.
flip7-player-stops-themself = { $player } se detiene y guarda { $points } puntos.
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
flip7-check-table = Revisar la mesa
flip7-check-deck = Revisar la baraja
flip7-you-label = Tú
flip7-area-status-stayed = , se detuvo esta ronda
flip7-area-status-busted = , se pasó esta ronda
flip7-area-numbers-none = Ninguna carta de número todavía
flip7-area-inline = { $who }{ $status }: { $numbers }. Total { $points } puntos.
flip7-area-inline-with-bonuses = { $who }{ $status }: { $numbers }. Total { $points } puntos. Bonos: { $bonuses }.
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
flip7-error-wait-card = Espera a que se resuelva la carta revelada.
flip7-error-wait-choice = Espera a que se resuelva la elección de carta actual.
flip7-error-wait-flip-three = Espera a que termine Voltea 3.
flip7-error-wait-dealing = Espera a que se repartan las cartas.
flip7-error-not-playing-round = Ya no estás jugando esta ronda.
flip7-error-no-cards-left = No quedan cartas para voltear.
flip7-error-no-cards-to-bank = Todavía no tienes cartas para guardar puntos.
flip7-error-no-choice = No hay ninguna elección de carta que responder.

# Pantalla final
flip7-line-format = { $rank }. { $player }: { $points }
