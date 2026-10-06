game-name-skipbo = Skip-Bo

skipbo-stock-mode-standard = Estándar (30 o 20 cartas)
skipbo-stock-mode-short = Rápido de 10 cartas
skipbo-stock-mode-short-15 = Rápido de 15 cartas
skipbo-scoring-single = Partida única
skipbo-scoring-match = Serie puntuada

skipbo-set-stock-mode = Pilas de reserva: { $mode }
skipbo-select-stock-mode = Selecciona la cantidad de cartas de las pilas de reserva:
skipbo-option-changed-stock-mode = Las pilas de reserva ahora usan { $mode }.
skipbo-desc-stock-mode = Estándar usa 30 cartas de reserva con 2 a 4 jugadores y 20 con 5 o 6 jugadores. Las partidas rápidas usan 10 o 15 cartas de reserva para cada jugador.

skipbo-set-scoring-mode = Formato de la serie: { $mode }
skipbo-select-scoring-mode = Selecciona el formato de la serie:
skipbo-option-changed-scoring-mode = El formato de la serie ahora es { $mode }.
skipbo-desc-scoring-mode = Partida única termina cuando un jugador o un equipo vacía sus pilas de reserva. Serie puntuada continúa a lo largo de varias partidas hasta que alguien alcanza la puntuación objetivo.

skipbo-set-winning-score = Objetivo de la serie: { $score } puntos
skipbo-enter-winning-score = Ingresa el objetivo de la serie, de 25 a 5000 puntos:
skipbo-option-changed-winning-score = El objetivo de la serie ahora es de { $score } puntos.
skipbo-desc-winning-score = Puntos necesarios para ganar una serie puntuada. El objetivo oficial es de 500 puntos.
skipbo-desc-team-mode = Individual le da a cada jugador una pila de reserva y una puntuación separadas. Los equipos oficiales son de dos; los compañeros pueden jugar desde las pilas de reserva y de descarte de cualquiera de los dos, pero nunca desde la mano del otro.

skipbo-card-number = { $value }
skipbo-card-wild = Comodín Skip-Bo
skipbo-card-wild-as = Skip-Bo como { $value }

skipbo-source-your-hand = tu mano
skipbo-source-player-hand = la mano de { $owner }
skipbo-source-your-stock = tu pila de reserva
skipbo-source-player-stock = la pila de reserva de { $owner }
skipbo-source-your-discard = tu pila de descarte { $pile }
skipbo-source-player-discard = la pila de descarte { $pile } de { $owner }

skipbo-action-source-hand = mano
skipbo-action-source-stock = reserva
skipbo-action-source-player-stock = reserva de { $owner }
skipbo-action-source-discard = pila de descarte { $pile }
skipbo-action-source-player-discard = pila de descarte { $pile } de { $owner }

skipbo-play-action = { $card } — { $source } a la pila { $pile }
skipbo-card-action = { $card } — { $source }
skipbo-card-desc-play-or-discard = Pilas de construcción disponibles: { $piles }. Elige la carta para jugarla o descartarla y terminar tu turno.
skipbo-card-desc-discard-only = Elige la carta para descartarla y terminar tu turno.
skipbo-card-desc-choose-building = Pilas de construcción disponibles: { $piles }. Elige la carta para seleccionar una.
skipbo-end-turn-empty = Terminar turno sin descartar
skipbo-end-turn-empty-desc = Tu mano está vacía y no se pueden robar cartas, así que no es posible descartar.
skipbo-select-card-move = Elige a dónde mover esta carta:
skipbo-move-building-empty = Pila de construcción { $pile}: vacía; jugar { $card }
skipbo-move-building-top = Pila de construcción { $pile}: { $current } encima; jugar { $card }
skipbo-move-discard-empty = Pila de descarte { $pile}: vacía; descartar aquí y terminar turno
skipbo-move-discard-top = Pila de descarte { $pile}: { $top } encima; descartar aquí y terminar turno

skipbo-read-building-piles = Ver pilas de construcción
skipbo-read-stock-piles = Ver pilas de reserva
skipbo-read-own-discard-piles = Ver tus pilas de descarte
skipbo-read-discard-piles = Ver las pilas de descarte de otro jugador
skipbo-select-discard-owner = Elige de quién ver las pilas de descarte:

skipbo-game-start = Comienza la partida. Cada pila de reserva tiene { $stock_count } cartas.
skipbo-game-start-quick = Comienza la partida rápida. Cada pila de reserva tiene { $stock_count } cartas.
skipbo-match-game-start = Comienza la partida puntuada { $game }. Cada pila de reserva tiene { $stock_count } cartas.
skipbo-match-game-start-quick = Comienza la partida puntuada rápida { $game }. Cada pila de reserva tiene { $stock_count } cartas.
skipbo-initial-stock-you = Tu carta visible de la pila de reserva es { $card }.
skipbo-initial-stock-player = La carta visible de la pila de reserva de { $player } es { $card }.
skipbo-draw-turn-you = Robas { $count } { $count ->
    [one] carta
   *[other] cartas
} para comenzar tu turno. Tu mano es { $hand }.
skipbo-draw-turn-player = { $player } roba { $count } { $count ->
    [one] carta
   *[other] cartas
} para comenzar { GENDER_TERM($player_gender, "possessive-determiner") } turno.
skipbo-refill-you = Usaste todas las cartas de tu mano, así que robas { $count } { $count ->
    [one] carta
   *[other] cartas
} de inmediato. Tu mano es { $hand }.
skipbo-refill-player = { $player } usó todas las cartas de { GENDER_TERM($player_gender, "possessive-determiner") } mano y roba { $count } { $count ->
    [one] carta
   *[other] cartas
} de inmediato.
skipbo-no-refill-you = Tu mano está vacía y no hay cartas disponibles para robar.
skipbo-no-refill-player = { $player } tiene la mano vacía, pero no hay cartas disponibles para robar.
skipbo-recycle-completed = La pila de robo está vacía. Las pilas de construcción completadas se barajan para formar una nueva pila de robo con { $count } cartas.

skipbo-play-you = Juegas { $card } desde { $source } a la pila de construcción { $pile }.
skipbo-play-player = { $player } juega { $card } desde { $source } a la pila de construcción { $pile }.
skipbo-complete-building-you = Completas la pila de construcción { $pile } en 12. Sus cartas se apartan para barajarlas de nuevo y el espacio de construcción vuelve a quedar vacío.
skipbo-complete-building-player = { $player } completa la pila de construcción { $pile } en 12. Sus cartas se apartan para barajarlas de nuevo y el espacio de construcción vuelve a quedar vacío.
skipbo-next-stock-you = Tu siguiente carta visible de la pila de reserva es { $card }; en tu pila de reserva { $count ->
    [one] queda { $count } carta
   *[other] quedan { $count } cartas
}.
skipbo-next-stock-player = La siguiente carta visible de la pila de reserva de { $player } es { $card }; en esa pila de reserva { $count ->
    [one] queda { $count } carta
   *[other] quedan { $count } cartas
}.
skipbo-stock-cleared-you = Tu pila de reserva ahora está vacía. Tu equipo aún debe vaciar la otra pila de reserva.
skipbo-stock-cleared-player = La pila de reserva de { $player } ahora está vacía. El equipo aún debe vaciar su otra pila de reserva.
skipbo-discard-you = Descartas { $card } en la pila de descarte { $pile } y terminas tu turno.
skipbo-discard-player = { $player } descarta { $card } en la pila de descarte { $pile } y termina { GENDER_TERM($player_gender, "possessive-determiner") } turno.
skipbo-empty-end-you = No tienes ninguna carta disponible para descartar, así que terminas tu turno sin hacerlo.
skipbo-empty-end-player = { $player } no tiene ninguna carta disponible para descartar y termina { GENDER_TERM($player_gender, "possessive-determiner") } turno sin hacerlo.

skipbo-single-win-you = Vacías tu pila de reserva y ganas la partida.
skipbo-single-win-player = { $player } vacía { GENDER_TERM($player_gender, "possessive-determiner") } pila de reserva y gana la partida.
skipbo-single-win-team-you = Tu equipo vacía las dos pilas de reserva y gana la partida.
skipbo-single-win-team = El equipo { $team } vacía las dos pilas de reserva y gana la partida.
skipbo-scored-game-win-you = Vacías tu pila de reserva y ganas la partida puntuada { $game }: obtienes { $points } puntos, con { $remaining } restantes entre las pilas de reserva rivales. Tu total en la serie es { $total }.
skipbo-scored-game-win-player = { $player } vacía { GENDER_TERM($player_gender, "possessive-determiner") } pila de reserva y gana la partida puntuada { $game }: obtiene { $points } puntos, con { $remaining } restantes entre las pilas de reserva rivales. El total en la serie es { $total }.
skipbo-scored-game-win-team-you = Tu equipo vacía las dos pilas de reserva y gana la partida puntuada { $game }: obtiene { $points } puntos, con { $remaining } restantes entre las pilas de reserva rivales. Tu total en la serie es { $total }.
skipbo-scored-game-win-team = El equipo { $team } vacía las dos pilas de reserva y gana la partida puntuada { $game }: obtiene { $points } puntos, con { $remaining } restantes entre las pilas de reserva rivales. El total del equipo en la serie es { $total }.
skipbo-next-round = La próxima partida puntuada comenzará en breve. La posición inicial avanza un asiento.
skipbo-match-win-you = Ganas la serie de Skip-Bo con { $score } puntos.
skipbo-match-win-player = { $player } gana la serie de Skip-Bo con { $score } puntos.
skipbo-match-win-team-you = Tu equipo gana la serie de Skip-Bo con { $score } puntos.
skipbo-match-win-team = El equipo { $team } gana la serie de Skip-Bo con { $score } puntos.

skipbo-building-empty = Pila de construcción { $pile }: vacía; necesita 1.
skipbo-building-top = Pila de construcción { $pile }: { $value } encima; necesita { $needed }.
skipbo-draw-count = Pila de robo: { $draw_count } cartas. Cartas de construcción completadas en espera de barajarse: { $recycle_count }.
skipbo-stock-empty = Pila de reserva de { $player }: vacía.
skipbo-stock-status = Pila de reserva de { $player }: { $card } boca arriba, { $count } { $count ->
    [one] carta en total
   *[other] cartas en total
}.
skipbo-discard-your-header = Tus pilas de descarte:
skipbo-discard-player-header = Pilas de descarte de { $player }:
skipbo-discard-empty = Pila de descarte { $pile }: vacía.
skipbo-discard-top = Pila de descarte { $pile }: { $card } encima, { $count } { $count ->
    [one] carta en total
   *[other] cartas en total
}.
skipbo-hand-empty = Todavía no tienes cartas en la mano.
skipbo-hand-menu-card = Mano: { $card }

skipbo-error-invalid-stock-mode = La cantidad de cartas de las pilas de reserva seleccionada no es compatible. Elige Estándar, Rápido de 10 o Rápido de 15.
skipbo-error-invalid-scoring-mode = El formato de la serie seleccionado no es compatible. Elige Partida única o Serie puntuada.
skipbo-error-winning-score-range = El objetivo de la serie debe estar entre { $min } y { $max } puntos; actualmente es { $value }.
skipbo-error-partnership-player-count = Los equipos requieren exactamente 4 jugadores para dos equipos o 6 jugadores para tres equipos.
skipbo-error-game-not-active = Esta partida de Skip-Bo no está activa en este momento.
skipbo-error-round-transition = La partida actual terminó. Espera a que comience la siguiente.
skipbo-error-card-move-selection-you = Primero elige a dónde mover la carta seleccionada.
skipbo-error-play-changed = Esa jugada ya no está disponible porque la carta o la pila de construcción cambió. Elige una acción actual del menú de turno.
skipbo-error-card-changed = Esa carta ya no está disponible. Elige una acción actual del menú de turno.
skipbo-error-cards-available = Todavía tienes una carta disponible para descartar. Termina tu turno eligiendo esa carta y una de tus cuatro pilas de descarte.
skipbo-error-no-discard-targets = No hay pilas de descarte de otros jugadores disponibles.
skipbo-error-discard-target-changed = Las pilas de descarte de ese jugador ya no están disponibles. Elige un jugador actual.
skipbo-discard-owner-unavailable = Jugador ya no disponible

skipbo-result-line = { $rank }. { $player }: { $points }
