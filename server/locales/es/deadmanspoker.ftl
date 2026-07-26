game-name-deadmanspoker = El Póker del Muerto

deadmanspoker-call = Igualar
deadmanspoker-match-all-in = Igualar el all-in
deadmanspoker-fold = Retirarse
deadmanspoker-coward-fold = Retiro del Cobarde
deadmanspoker-switch-card = Cambiar carta
deadmanspoker-all-in = All-in
deadmanspoker-read-hand = Leer mano
deadmanspoker-read-community-cards = Leer cartas comunitarias
deadmanspoker-read-hand-value = Leer fuerza de la mano
deadmanspoker-read-table = Leer mesa
deadmanspoker-read-revolvers = Leer revólveres

deadmanspoker-action-sequence-running = Espera a que termine la secuencia actual.
deadmanspoker-action-eliminated = Has sido eliminado.
deadmanspoker-action-folded = Estás fuera de esta mano.
deadmanspoker-not-decision-phase = No puedes hacer eso durante esta fase.
deadmanspoker-max-bullets = Ya tienes comprometido el máximo de balas.
deadmanspoker-no-opponents = No queda ningún oponente en esta mano.
deadmanspoker-already-matched-all-in = Ya igualaste el all-in.
deadmanspoker-coward-used = Ya usaste el Retiro del Cobarde en esta partida.
deadmanspoker-coward-first-decision-only = El Retiro del Cobarde solo está disponible en tu primera decisión de una mano.
deadmanspoker-all-in-too-early = El all-in solo está disponible desde la ronda de apuestas 2, después de que se revelen las primeras tres cartas comunitarias.
deadmanspoker-switch-not-now = No puedes cambiar una carta en este momento.
deadmanspoker-switch-used = Ya cambiaste una carta en esta mano.
deadmanspoker-switch-too-late = Ya es muy tarde para cambiar una carta.
deadmanspoker-switch-no-cards = No tienes ninguna carta privada para cambiar.
deadmanspoker-switch-no-deck = El mazo no tiene suficientes cartas de reemplazo.
deadmanspoker-switch-choice-missing = Esa carta de reemplazo ya no está disponible.

deadmanspoker-match-start = Comienza El Póker del Muerto. Cada bala en la mesa es una apuesta con tu vida detrás.
deadmanspoker-hand-start = Mano { $hand }. Cada jugador activo compromete la primera bala.
deadmanspoker-hand-start-all-alive = Mano { $hand }. Todos comprometen la primera bala.
deadmanspoker-hand-start-survivors = Mano { $hand }. Cada superviviente compromete la primera bala.
deadmanspoker-community-arrives = Llegan cinco cartas comunitarias boca abajo.
deadmanspoker-your-hand = Tus cartas privadas: { $cards }.
deadmanspoker-hand-empty = Tu mano está vacía.
deadmanspoker-round-stage = Ronda de apuestas { $round_stage }.
deadmanspoker-community-revealed = Cartas comunitarias reveladas: { $cards }. Mesa: { $table }.
deadmanspoker-you-call = Igualas y colocas { $added ->
    [one] 1 bala
   *[other] { $added } balas
} en la mesa. Total comprometido: { $total }.
deadmanspoker-player-calls = { $player } iguala y coloca { $added ->
    [one] 1 bala
   *[other] { $added } balas
} en la mesa. Total comprometido: { $total }.
deadmanspoker-you-match-all-in = Igualas el all-in con { $added ->
    [one] 1 bala
   *[other] { $added } balas
}. Total comprometido: { $total }.
deadmanspoker-player-matches-all-in = { $player } iguala el all-in con { $added ->
    [one] 1 bala
   *[other] { $added } balas
}. Total comprometido: { $total }.
deadmanspoker-you-all-in = Vas all-in y colocas { $added ->
    [one] 1 bala
   *[other] { $added } balas
} en la mesa. Total comprometido: { $total }.
deadmanspoker-player-all-in = { $player } va all-in y coloca { $added ->
    [one] 1 bala
   *[other] { $added } balas
} en la mesa. Total comprometido: { $total }.
deadmanspoker-you-fold = Te retiras y debes enfrentar el revólver con { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-player-folds = { $player } se retira y debe enfrentar el revólver con { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-you-coward-fold = Usas el Retiro del Cobarde y enfrentas el revólver con 1 bala.
deadmanspoker-player-coward-folds = { $player } usa el Retiro del Cobarde y enfrenta el revólver con 1 bala.
deadmanspoker-switch-select-card = Elige la carta privada para cambiar.
deadmanspoker-switch-card-option = Cambiar { $card }
deadmanspoker-switch-candidates = Opciones de reemplazo: { $cards }.
deadmanspoker-choose-switch-placeholder = Reemplazo { $index }
deadmanspoker-choose-switch-card = Elegir { $card }
deadmanspoker-you-switch = Cambias una carta privada y descartas { $card }.
deadmanspoker-player-switches = { $player } cambia una carta privada y descarta { $card }.
deadmanspoker-your-private-reveal = Revelas { $cards }. Mejor mano: { $hand }.
deadmanspoker-private-reveal = { $player } revela { $cards }. Mejor mano: { $hand }.
deadmanspoker-showdown-you-win = Ganas la revelación de cartas con { $hand }.
deadmanspoker-showdown-winner = { $player } gana la revelación de cartas con { $hand }.
deadmanspoker-showdown-you-draw = Empatas la revelación de cartas con { $players } usando { $hand }. Los jugadores empatados no ganan esta mano.
deadmanspoker-showdown-draw = Empate en la revelación de cartas: { $players } empatan con { $hand }. Los jugadores empatados no ganan esta mano.
deadmanspoker-showdown-tie-no-penalty = La revelación de cartas es un empate total. Nadie gana ni enfrenta el revólver en esta mano.
deadmanspoker-you-win-hand = Ganas la mano sin oposición.
deadmanspoker-hand-winner = { $player } gana la mano sin oposición.
deadmanspoker-hand-no-winner = Nadie gana esta mano.

deadmanspoker-roulette-start = Comienza la ruleta para { $players }.
deadmanspoker-you-load-bullets = Cargas { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-load-bullets = { $player } carga { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-you-roulette-survived = Cámara vacía. Sobrevives tras arriesgar { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-roulette-survived = Cámara vacía. { $player } sobrevive tras arriesgar { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-you-eliminated = El arma dispara. Quedas eliminado tras arriesgar { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-player-eliminated = El arma dispara. { $player } queda eliminado tras arriesgar { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
}.
deadmanspoker-you-win-game = Eres el último superviviente y ganas El Póker del Muerto.
deadmanspoker-player-wins = { $player } es el último superviviente y gana El Póker del Muerto.
deadmanspoker-no-winner = No se pudo determinar un ganador.
deadmanspoker-you-are-eliminated = Has sido eliminado de esta partida.

deadmanspoker-table-hand = Mano { $hand }, ronda de apuestas { $round_stage }.
deadmanspoker-table-community = Comunitarias: { $cards }. Ocultas: { $hidden }.
deadmanspoker-community-status = Cartas comunitarias: { $cards }. Ocultas: { $hidden }.
deadmanspoker-table-turn = Turno actual: { $player }.
deadmanspoker-table-no-turn = Ningún jugador tiene el turno actualmente.
deadmanspoker-table-player = { $player }: { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
} comprometidas, { $status }.
deadmanspoker-community-none = ninguna revelada
deadmanspoker-hidden-community = { $count ->
    [one] 1 carta oculta
   *[other] { $count } cartas ocultas
}
deadmanspoker-status-active = activo
deadmanspoker-status-folded = retirado
deadmanspoker-status-eliminated = eliminado
deadmanspoker-status-waiting = esperando

deadmanspoker-revolvers-header = Riesgo del revólver
deadmanspoker-revolver-status = { $player }: { $bullets ->
    [one] 1 bala
   *[other] { $bullets } balas
} comprometidas; { $risk }.
deadmanspoker-revolver-eliminated = { $player }: eliminado.
deadmanspoker-risk-none = sin riesgo de ruleta actualmente
deadmanspoker-risk-normal = probabilidad de muerte { $bullets } de 8
deadmanspoker-risk-eight = 95 por ciento de probabilidad de muerte, 5 por ciento de supervivencia por Gracia Divina

deadmanspoker-results-header = Resultados de El Póker del Muerto
deadmanspoker-results-winner = Ganador: { $player }.
deadmanspoker-results-survived = sobrevivió
deadmanspoker-results-eliminated = eliminado
deadmanspoker-results-line = { $player }: { $status }, manos ganadas { $hands }, all-ins iniciados { $allins }, supervivencias a la ruleta { $survivals }, balas arriesgadas { $bullets }.
