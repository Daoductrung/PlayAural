game-name-colorgame = Juego de Colores

colorgame-set-starting-bankroll = Fichas iniciales: { $amount }
colorgame-enter-starting-bankroll = Ingresa las fichas iniciales:
colorgame-option-changed-starting-bankroll = Fichas iniciales establecidas en { $amount }.
colorgame-desc-starting-bankroll = Con cuántas fichas empieza cada jugador en el Juego de Colores (por defecto 100, rango 10-1000).

colorgame-set-minimum-bet = Apuesta mínima: { $amount }
colorgame-enter-minimum-bet = Ingresa la apuesta mínima:
colorgame-option-changed-minimum-bet = Apuesta mínima establecida en { $amount }.
colorgame-desc-minimum-bet = La apuesta más pequeña permitida en un color por ronda (por defecto 1, rango 1-100).

colorgame-set-maximum-total-bet = Apuesta total máxima por ronda: { $amount }
colorgame-enter-maximum-total-bet = Ingresa la apuesta total máxima por ronda:
colorgame-option-changed-maximum-total-bet = Apuesta total máxima por ronda establecida en { $amount }.
colorgame-desc-maximum-total-bet = Máximo total de fichas que un jugador puede arriesgar en una ronda del Juego de Colores. Debe ser al menos la apuesta mínima y no mayor que las fichas iniciales; el límite real de cada jugador también está limitado por sus fichas actuales (por defecto 20, rango 1-1000).

colorgame-set-betting-timer = Temporizador de apuestas: { $seconds } segundos
colorgame-enter-betting-timer = Ingresa el temporizador de apuestas en segundos:
colorgame-option-changed-betting-timer = Temporizador de apuestas establecido en { $seconds } segundos.
colorgame-desc-betting-timer-seconds = Cuánto dura la fase de apuestas en cada ronda (por defecto 15 segundos, rango 5-60).

colorgame-set-round-limit = Límite de rondas: { $count }
colorgame-enter-round-limit = Ingresa el límite de rondas:
colorgame-option-changed-round-limit = Límite de rondas establecido en { $count }.
colorgame-desc-round-limit = Número máximo de rondas del Juego de Colores antes de decidir al ganador (por defecto 20, rango 1-100).

colorgame-set-win-condition = Condición de victoria: { $mode }
colorgame-select-win-condition = Selecciona la condición de victoria:
colorgame-option-changed-win-condition = Condición de victoria establecida en { $mode }.
colorgame-desc-win-condition = Elige si el Juego de Colores termina con el último jugador en pie o con las fichas más altas al llegar al límite de rondas.
colorgame-win-condition-last-player = Último jugador en pie
colorgame-win-condition-highest-bankroll = Fichas más altas al límite de rondas

colorgame-color-red = rojo
colorgame-color-blue = azul
colorgame-color-yellow = amarillo
colorgame-color-green = verde
colorgame-color-white = blanco
colorgame-color-orange = naranja

colorgame-game-start = Comienza el Juego de Colores. Jugadores: { $players }.
colorgame-round-start = Ronda { $round } de { $limit }. Las apuestas están abiertas por { $seconds } segundos.
colorgame-round-start-brief = Ronda { $round }. Apuesta ahora: { $seconds } segundos.
colorgame-roll-result = Los dados muestran { $colors }.
colorgame-roll-result-brief = Tirada: { $colors }.
colorgame-you-locked-bets = Bloqueas { $total } fichas.
colorgame-player-locked-bets = { $player } bloquea { $total } fichas.
colorgame-you-locked-bets-brief = Bloqueas { $total }.
colorgame-player-locked-bets-brief = { $player } bloquea { $total }.
colorgame-you-sit-out = Te quedas fuera de esta ronda.
colorgame-player-sits-out = { $player } se queda fuera de esta ronda.
colorgame-you-sit-out-brief = Te quedas fuera.
colorgame-player-sits-out-brief = { $player } se queda fuera.
colorgame-you-sat-out = Te quedaste fuera y sigues con { $bankroll } fichas.
colorgame-player-sat-out = { $player } se quedó fuera y sigue con { $bankroll } fichas.
colorgame-you-sat-out-brief = Tú: sin apuesta, { $bankroll }.
colorgame-player-sat-out-brief = { $player }: sin apuesta, { $bankroll }.
colorgame-you-won = Ganas { $amount } fichas y subes a { $bankroll }.
colorgame-player-won = { $player } gana { $amount } fichas y sube a { $bankroll }.
colorgame-you-won-brief = Tú: +{ $amount }, { $bankroll }.
colorgame-player-won-brief = { $player }: +{ $amount }, { $bankroll }.
colorgame-you-even = No ganas ni pierdes y sigues con { $bankroll } fichas.
colorgame-player-even = { $player } no gana ni pierde y sigue con { $bankroll } fichas.
colorgame-you-even-brief = Tú: sin cambios, { $bankroll }.
colorgame-player-even-brief = { $player }: sin cambios, { $bankroll }.
colorgame-you-lost = Pierdes { $amount } fichas y bajas a { $bankroll }.
colorgame-player-lost = { $player } pierde { $amount } fichas y baja a { $bankroll }.
colorgame-you-lost-brief = Tú: -{ $amount }, { $bankroll }.
colorgame-player-lost-brief = { $player }: -{ $amount }, { $bankroll }.

colorgame-set-bet-color = Apostar en { $color }: { $amount }
colorgame-clear-bets = Borrar apuestas
colorgame-confirm-bets = Bloquear apuestas ({ $total })
colorgame-confirm-sit-out = Bloquear sin apostar
colorgame-check-status = Ver estado
colorgame-check-bets = Ver apuestas
colorgame-check-last-roll = Ver última tirada

colorgame-select-quick-bet = Selecciona un monto de apuesta:
colorgame-quick-bet-minimum = Mínimo: { $amount }
colorgame-quick-bet-preset = Apostar { $amount }
colorgame-quick-bet-quarter = 25 por ciento disponible: { $amount }
colorgame-quick-bet-half = 50 por ciento disponible: { $amount }
colorgame-quick-bet-all-in = All-in, hasta el límite de la ronda: { $amount }
colorgame-quick-bet-clear = Borrar este color
colorgame-quick-bet-custom = Ingresar monto personalizado
colorgame-enter-custom-bet-amount = Ingresa la apuesta exacta para este color. Ingresa 0 para borrarla.
colorgame-invalid-bet-amount = Ingresa un número entero válido para la apuesta.
colorgame-bet-below-minimum = Cada apuesta por color debe ser de al menos { $amount }.
colorgame-bet-exceeds-bankroll = El total de tus apuestas no puede superar tus { $amount } fichas disponibles.
colorgame-bet-exceeds-round-limit = El total de tus apuestas no puede superar el límite de ronda de { $amount } fichas.
colorgame-no-room-for-color-bet = Solo te quedan { $available } fichas de capacidad de apuesta, por debajo del mínimo de { $minimum } para otro color. Reduce o borra otra apuesta primero.
colorgame-betting-closed = Las apuestas están cerradas mientras los dados están rodando o se está resolviendo el resultado.
colorgame-bet-updated = { $color } ahora está en { $amount }. Total comprometido esta ronda: { $total }.
colorgame-color-bet-cleared = Tu apuesta en { $color } se borró. Total comprometido esta ronda: { $total }.
colorgame-bets-cleared = Todas tus apuestas fueron borradas.
colorgame-below-minimum-bankroll = Tienes { $bankroll } fichas, por debajo de la apuesta mínima de { $minimum }, así que no puedes volver a apostar en esta partida.
colorgame-bets-already-locked = Tus apuestas ya están bloqueadas para esta ronda.
colorgame-no-bets-placed = No has hecho ninguna apuesta.
colorgame-confirm-all-in = Esto establecerá { $color } en { $amount }, usando toda la capacidad de apuesta disponible esta ronda. Repite la misma elección de All-in dentro de { $seconds } segundos para confirmar.
colorgame-confirm-sit-out-risk = No tienes apuestas. Presiona Bloquear sin apostar de nuevo dentro de { $seconds } segundos para quedarte fuera de esta ronda.

colorgame-no-bets = sin apuesta
colorgame-bet-entry = { $color } { $amount }
colorgame-bets-header = Apuestas actuales:
colorgame-bets-line = { $player }: { $bets }. Total { $total }. { $locked }.
colorgame-bets-open-status = Las apuestas siguen abiertas
colorgame-bets-locked-status = Las apuestas están bloqueadas

colorgame-last-roll-none = Aún no se ha registrado ninguna tirada.
colorgame-last-roll-header = Última tirada: { $colors }.
colorgame-last-roll-line = { $player }: { $bets }. Neto { $net }. Fichas { $bankroll }.

colorgame-status-betting = Fase de apuestas. Ronda { $round } de { $limit }. Quedan { $seconds } segundos. Condición de victoria: { $win_mode }.
colorgame-status-rolling = Los dados están rodando para la ronda { $round } de { $limit }. Condición de victoria: { $win_mode }.
colorgame-status-resolving = Se está resolviendo la ronda { $round } de { $limit }. Condición de victoria: { $win_mode }.
colorgame-status-bankroll = Tus fichas son { $bankroll }. Comprometiste { $total } esta ronda. Tu límite esta ronda es { $cap }.
colorgame-status-bet-lock = Estado de tu apuesta: { $state }.
colorgame-status-leader = El líder actual es { $player } con { $bankroll } fichas.

colorgame-whose-turn-betting = Fase de apuestas. Todos los jugadores activos pueden actuar. Quedan { $seconds } segundos.
colorgame-whose-turn-rolling = Los dados están rodando ahora.
colorgame-whose-turn-resolving = La ronda se está resolviendo ahora.

colorgame-standings-header = Clasificación:
colorgame-standing-live = sigue en juego
colorgame-standing-bust = fuera, por debajo de la apuesta mínima
colorgame-score-line = { $rank }. { $player }: { $bankroll } fichas, { $profitable_rounds } rondas ganadoras, mayor victoria { $biggest_win }, { $status }.
colorgame-game-winner = Ganador: { $player }.
colorgame-game-tie = Ganadores empatados: { $players }.

colorgame-error-minimum-exceeds-bankroll = La apuesta mínima de { $minimum } no puede superar las fichas iniciales de { $bankroll }.
colorgame-error-max-bet-too-small = La apuesta total máxima de { $maximum } debe ser al menos la apuesta mínima de { $minimum }.
colorgame-error-max-bet-too-large = La apuesta total máxima de { $maximum } no puede superar las fichas iniciales de { $bankroll }.
