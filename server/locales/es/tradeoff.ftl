game-name-tradeoff = Intercambio

tradeoff-round-start = Ronda { $round }.
tradeoff-iteration = Mano { $iteration } de 3.

tradeoff-you-rolled = Sacaste: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = para intercambiar
tradeoff-trade-status-keeping = guardado
tradeoff-confirm-trades = Confirmar intercambios ({ $count } dados)
tradeoff-keeping = Guardando { $value }.
tradeoff-trading = Intercambiando { $value }.
tradeoff-you-traded = Intercambiaste { $count } dados al montón: { $dice }.
tradeoff-player-traded = { $player } intercambió { $count } dados al montón: { $dice }.
tradeoff-you-traded-brief = Intercambiaste { $count } dados.
tradeoff-player-traded-brief = { $player } intercambió { $count } dados.
tradeoff-you-traded-none = Guardaste los cinco dados de esta mano, así que esta vez no tomarás del montón.
tradeoff-player-traded-none = { $player } guardó los cinco dados de esta mano.

tradeoff-your-turn-take = Tu turno para tomar un dado del montón.
tradeoff-take-die = Tomar un { $value } (quedan { $remaining })
tradeoff-you-take = Tomas un { $value }.
tradeoff-player-takes = { $player } toma un { $value }.

tradeoff-you-scored = Anotaste { $points } puntos con { $sets }.
tradeoff-player-scored = { $player } anotó { $points } puntos con { $sets }.
tradeoff-you-scored-brief = Anotaste { $points } puntos esta ronda.
tradeoff-player-scored-brief = { $player } anotó { $points } puntos esta ronda.
tradeoff-you-no-sets = Anotaste 0 puntos porque tus 15 dados no formaron ninguna combinación puntuable.
tradeoff-no-sets = { $player } anotó 0 puntos porque sus 15 dados no formaron ninguna combinación puntuable.

tradeoff-set-triple = trío de { $value }
tradeoff-set-group = grupo de { $value }
tradeoff-set-mini-straight = mini escalera { $low }-{ $high }
tradeoff-set-double-triple = doble trío ({ $v1 } y { $v2 })
tradeoff-set-straight = escalera { $low }-{ $high }
tradeoff-set-double-group = doble grupo ({ $v1 } y { $v2 })
tradeoff-set-all-groups = todos grupos
tradeoff-set-all-triplets = todos tríos

tradeoff-round-scores = Puntuaciones de la ronda { $round }:
tradeoff-round-scores-brief = Puntuaciones:
tradeoff-score-line = { $player }: +{ $round_points } (total: { $total })
tradeoff-score-line-brief = { $player}: +{ $round_points }, total { $total }.
tradeoff-leader = { $player } va a la cabeza con { $score }.
tradeoff-leader-brief = Líder: { $player }, { $score }.

tradeoff-you-win = ¡Ganas con { $score } puntos!
tradeoff-winner = ¡{ $player } gana con { $score } puntos!
tradeoff-you-tie-win = ¡Empatas la victoria con { $players } con { $score } puntos!
tradeoff-winners-tie = ¡Es un empate! ¡{ $players } empataron con { $score } puntos!

tradeoff-view-hand = Ver tu mano
tradeoff-view-pool = Ver el montón
tradeoff-view-players = Ver jugadores
tradeoff-hand-state-empty = aún sin dados guardados
tradeoff-hand-empty = Tu mano guardada está vacía. Si acabas de lanzar, usa las opciones de dados para decidir qué guardar antes de confirmar los intercambios.
tradeoff-hand-display = Tu mano guardada esta ronda ({ $count } dados): { $dice }.
tradeoff-hand-display-with-roll = Tu mano guardada esta ronda ({ $count } dados): { $dice }. Tirada actual: { $roll }. { $trade_count } dados todavía están marcados para intercambiar.
tradeoff-roll-die-status = posición { $position}: { $value }, { $status }
tradeoff-die-count = { $value}: { $count }
tradeoff-pool-display = Montón ({ $count } dados): { $dice }.
tradeoff-pool-empty = El montón está vacío.
tradeoff-player-info = { $player}: mano guardada: { $hand }. Último intercambio: { $traded }.
tradeoff-player-info-no-trade = { $player}: mano guardada: { $hand }. No intercambió nada la última vez.

tradeoff-not-trading-phase = Solo puedes cambiar o confirmar las opciones de intercambio mientras tus dados recién lanzados esperan en la fase de intercambio.
tradeoff-not-taking-phase = Solo puedes tomar dados después de que todos los jugadores hayan confirmado sus intercambios y el montón compartido esté abierto.
tradeoff-already-confirmed = Ya confirmaste esta selección de intercambio. Espera a los demás jugadores; si intercambiaste dados, tomarás del montón cuando llegue tu turno.
tradeoff-no-die = No hay ningún dado disponible para esa acción de intercambio.
tradeoff-no-die-position = La posición { $position } no está disponible en tu tirada actual.
tradeoff-no-rolled-dice = Actualmente no tienes dados lanzados esperando opciones de intercambio.
tradeoff-no-more-takes = Ya tomaste de vuelta la misma cantidad de dados que intercambiaste en esta mano.
tradeoff-not-in-pool = En este momento no hay un { $value } en el montón compartido. Elige uno de los valores visibles del montón.
tradeoff-not-your-take-turn = Es el turno de { $player } para tomar del montón. Espera a que anuncien tu nombre antes de elegir un dado.
tradeoff-no-trading-die-value = No tienes un { $value } marcado actualmente para intercambiar.
tradeoff-no-kept-die-value = No tienes un { $value } guardado para marcar como intercambio.
tradeoff-value-trade-style-required = Los controles de intercambio con Mayús+número solo se usan con el estilo Valores de los dados. Usa las teclas numéricas simples por posición, o cambia tu estilo personal para guardar dados.
tradeoff-use-plain-number-to-take = Usa la tecla numérica simple, no Mayús+número, para tomar un dado del montón.
tradeoff-no-dice-key-phase = Las teclas numéricas solo se usan al elegir intercambios o al tomar dados del montón.

tradeoff-set-target = Puntuación objetivo: { $score }
tradeoff-enter-target = Ingresa la puntuación objetivo:
tradeoff-option-changed-target = Puntuación objetivo establecida en { $score }.
tradeoff-desc-target-score = La puntuación total que un jugador debe alcanzar o superar después de una ronda con puntos para ganar (por defecto 60, rango 30-500).
tradeoff-error-target-out-of-range = La puntuación objetivo { $score } está fuera del rango permitido de { $min } a { $max }.
