game-name-deadmansdeck = La Baraja del Muerto

deadmansdeck-call-liar = Acusar de mentiroso
deadmansdeck-play-selected = Jugar cartas seleccionadas
deadmansdeck-clear-selection = Borrar selección
deadmansdeck-read-hand = Leer mano
deadmansdeck-read-table = Leer mesa
deadmansdeck-read-revolvers = Leer revólveres
deadmansdeck-read-card-counts = Leer cantidad de cartas

deadmansdeck-rank-ace = As
deadmansdeck-rank-ace-plural = Ases
deadmansdeck-rank-king = Rey
deadmansdeck-rank-king-plural = Reyes
deadmansdeck-rank-queen = Reina
deadmansdeck-rank-queen-plural = Reinas
deadmansdeck-rank-joker = Comodín
deadmansdeck-rank-joker-plural = Comodines
deadmansdeck-claim-text = { $count } { $rank }

deadmansdeck-card-label = { $card }
deadmansdeck-selected-card-label = Seleccionada: { $card }
deadmansdeck-card-selected = Seleccionaste { $card }.
deadmansdeck-card-unselected = Deseleccionaste { $card }.
deadmansdeck-selection-cleared = Selección borrada.
deadmansdeck-card-not-found = Esa carta ya no está disponible.
deadmansdeck-too-many-selected = Puedes reclamar como máximo tres cartas.
deadmansdeck-select-card-first = Primero selecciona de una a tres cartas.
deadmansdeck-no-claim-to-challenge = No hay ninguna declaración para cuestionar.
deadmansdeck-cannot-challenge-self = No puedes cuestionar tu propia declaración.
deadmansdeck-action-sequence-running = Espera a que termine la secuencia actual.
deadmansdeck-action-eliminated = Has sido eliminado.

deadmansdeck-prepare-revolver = Se están preparando los revólveres.
deadmansdeck-round-start = Ronda { $round }. La carta de mesa es { $target }.
deadmansdeck-turn-order = Orden de turnos esta ronda: { $order }.
deadmansdeck-your-hand = Tu mano: { $cards }.
deadmansdeck-hand-empty = Tu mano está vacía.
deadmansdeck-no-cards = sin cartas
deadmansdeck-you-skipped-no-cards = No tienes cartas y se te salta el turno.
deadmansdeck-player-skipped-no-cards = { $player } no tiene cartas y se le salta el turno.
deadmansdeck-you-out-of-cards = Te quedaste sin cartas.
deadmansdeck-player-out-of-cards = { $player } se quedó sin cartas.
deadmansdeck-you-forced-challenge = Debes cuestionar porque la ronda no puede continuar.
deadmansdeck-forced-challenge = { $player } debe cuestionar porque la ronda no puede continuar.
deadmansdeck-you-claim = Declaras { $claim }.
deadmansdeck-player-claims = { $player } declara { $claim }.
deadmansdeck-you-call-liar = Acusas a { $accused } de mentiroso.
deadmansdeck-player-calls-liar = { $challenger } acusa a { $accused } de mentiroso.
deadmansdeck-player-calls-you-liar = { $challenger } te acusa de mentiroso.
deadmansdeck-you-forced-liar-call = Te ves obligado a acusar a { $accused } de mentiroso.
deadmansdeck-forced-liar-call = { $challenger } se ve obligado a acusar a { $accused } de mentiroso.
deadmansdeck-forced-liar-call-you = { $challenger } se ve obligado a acusarte de mentiroso.
deadmansdeck-your-revealed-cards = Tus cartas reveladas: { $cards }.
deadmansdeck-revealed-cards = { $player } reveló: { $cards }.
deadmansdeck-you-caught-bluff = Descubriste que { $accused } mentía. { $accused } debe jalar el gatillo.
deadmansdeck-your-bluff-caught = { $challenger } descubrió tu farol. Debes jalar el gatillo.
deadmansdeck-bluff-caught = { $challenger } descubrió que { $accused } mentía. { $accused } debe jalar el gatillo.
deadmansdeck-you-wrong-challenge = { $accused } decía la verdad. Debes jalar el gatillo.
deadmansdeck-your-truthful-claim = Tu declaración era verdadera. { $challenger } debe jalar el gatillo.
deadmansdeck-truthful-claim = { $accused } decía la verdad. { $challenger } debe jalar el gatillo.
deadmansdeck-you-face-revolver = Te enfrentas al revólver.
deadmansdeck-roulette-start = { $player } se enfrenta al revólver.
deadmansdeck-you-roulette-survived = Cámara vacía. Sobrevives. Tu próximo disparo tiene un riesgo de 1 entre { $remaining }.
deadmansdeck-roulette-survived = Cámara vacía. { $player } sobrevive. Su próximo disparo tiene un riesgo de 1 entre { $remaining }.
deadmansdeck-you-eliminated-by-gun = El arma dispara. Has sido eliminado.
deadmansdeck-player-eliminated = El arma dispara. { $player } ha sido eliminado.
deadmansdeck-you-win-game = Eres el último jugador en pie y ganas La Baraja del Muerto.
deadmansdeck-player-wins = { $player } es el último jugador en pie y gana La Baraja del Muerto.
deadmansdeck-no-winner = No se pudo determinar un ganador.
deadmansdeck-you-are-eliminated = Has sido eliminado de esta partida.

deadmansdeck-table-round = Ronda { $round }. Objetivo: { $target }.
deadmansdeck-table-target-pending = aún sin definir
deadmansdeck-table-current-turn = Turno actual: { $player }.
deadmansdeck-table-last-claim = Última declaración: { $player } declaró { $claim }.
deadmansdeck-table-no-claim = No hay ninguna declaración activa.
deadmansdeck-table-alive = Aún con vida: { $players }.
deadmansdeck-table-eliminated = Eliminados: { $players }.

deadmansdeck-card-count-line = { $player }: quedan { $count ->
    [one] 1 carta
   *[other] { $count } cartas
}.
deadmansdeck-card-count-eliminated = { $player }: eliminado.

deadmansdeck-revolvers-header = Estado de los revólveres
deadmansdeck-revolver-status = { $player }: { $survived } cámaras vacías usadas; el próximo disparo es 1 entre { $remaining }.
deadmansdeck-revolver-eliminated = { $player }: eliminado.

deadmansdeck-results-header = Resultados de La Baraja del Muerto
deadmansdeck-results-winner = Ganador: { $player }.
deadmansdeck-results-survived = sobrevivió
deadmansdeck-results-eliminated = eliminado
deadmansdeck-results-line = { $player }: { $status }, aciertos { $correct }, faroles exitosos { $bluffs }, veces que sobrevivió a la ruleta { $survivals }.
