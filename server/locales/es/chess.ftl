game-name-chess = Ajedrez

chess-set-time-control = Control de tiempo: { $control }
chess-select-time-control = Elige un control de tiempo
chess-option-changed-time-control = Control de tiempo establecido en { $control }.
chess-desc-time-control = Elige el reloj de ajedrez, desde partidas sin tiempo hasta controles bala, blitz, rápidas o clásicas.
chess-time-untimed = Sin tiempo
chess-time-bullet-1-0 = Bala 1+0
chess-time-bullet-2-1 = Bala 2+1
chess-time-blitz-3-0 = Blitz 3+0
chess-time-blitz-3-2 = Blitz 3+2
chess-time-blitz-5-0 = Blitz 5+0
chess-time-rapid-10-0 = Rápidas 10+0
chess-time-rapid-10-5 = Rápidas 10+5
chess-time-classical-30-0 = Clásicas 30+0

chess-set-draw-handling = Manejo de tablas: { $mode }
chess-select-draw-handling = Elige el manejo de tablas
chess-option-changed-draw-handling = Manejo de tablas establecido en { $mode }.
chess-desc-draw-handling = Elige si las reglas automáticas de tablas terminan la partida de inmediato o requieren que un jugador las reclame.
chess-draw-handling-automatic = Automático
chess-draw-handling-claim-required = Requiere reclamo

chess-toggle-draw-offers = Permitir ofrecer tablas: { $enabled }
chess-option-changed-draw-offers = Permitir ofrecer tablas establecido en { $enabled }.
chess-desc-allow-draw-offers = Controla si los jugadores pueden ofrecer y responder a tablas de mutuo acuerdo.
chess-toggle-undo-requests = Permitir solicitudes de deshacer: { $enabled }
chess-option-changed-undo-requests = Permitir solicitudes de deshacer establecido en { $enabled }.
chess-desc-allow-undo-requests = Controla si los jugadores pueden solicitar deshacer una jugada, que el oponente puede aceptar o rechazar.
chess-error-invalid-time-control = El control de tiempo seleccionado "{ $control }" no es compatible con Ajedrez.
chess-error-invalid-draw-handling = El modo de manejo de tablas seleccionado "{ $mode }" no es compatible con Ajedrez.

chess-read-board = Leer tablero
chess-check-status = Ver estado
chess-flip-board = Voltear tablero
chess-check-clock = Ver reloj
chess-claim-draw = Reclamar tablas
chess-offer-draw = Ofrecer tablas
chess-accept-draw = Aceptar tablas
chess-decline-draw = Rechazar tablas
chess-request-undo = Solicitar deshacer
chess-accept-undo = Aceptar deshacer
chess-decline-undo = Rechazar deshacer
chess-type-move = Escribir jugada
chess-enter-move = Escribe tu jugada, como e2e4, Cf3, O-O, o e8=D

chess-promote-queen = Coronar a dama
chess-promote-rook = Coronar a torre
chess-promote-bishop = Coronar a alfil
chess-promote-knight = Coronar a caballo

chess-color-white = blancas
chess-color-black = negras

chess-piece-pawn = peón
chess-piece-knight = caballo
chess-piece-bishop = alfil
chess-piece-rook = torre
chess-piece-queen = dama
chess-piece-king = rey
chess-piece-with-color = { $piece } { $color }

chess-square-empty-label = { $square }, vacía
chess-square-piece-label = { $square }, { $piece }
chess-square-selected-label = seleccionada, { $label }
chess-square-move-target = { $square }, jugada legal
chess-square-capture-target = { $square }, capturar { $piece }
chess-square-empty = { $square } está vacía.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = Primero selecciona una de tus propias piezas.
chess-piece-no-legal-moves = Esa pieza no tiene jugadas legales.
chess-piece-selected = { $piece } seleccionado en { $square }. { $count } jugadas legales disponibles.
chess-selection-cleared = Selección borrada.
chess-illegal-move = Jugada ilegal.
chess-invalid-castle = El enroque no es legal ahí.
chess-promotion-pending = Primero elige una pieza para la coronación.
chess-choose-promotion = Elige una pieza para coronar.
chess-typed-move-empty = Escribe una jugada antes de enviarla.
chess-typed-move-parse-error = No pude entender "{ $move }" como una jugada de ajedrez. Prueba con notación de coordenadas como e2e4, notación algebraica como Cf3, enroque como O-O, o coronación como e8=D.
chess-typed-move-ambiguous = "{ $move }" coincide con más de una jugada legal. Agrega la columna, la fila o la casilla de origen completa, como Cbd2 o Tae1.
chess-typed-move-illegal = "{ $move }" no es legal en la posición actual.
chess-typed-move-bad-promotion = "{ $move }" incluye una pieza de coronación, pero la coronación solo funciona cuando uno de tus peones llega a la última fila. Usa dama, torre, alfil o caballo.

chess-game-started = Comienza el Ajedrez. { $white } juega con blancas. { $black } juega con negras.
chess-you-win-checkmate = Jaque mate. Ganas.
chess-player-wins-checkmate = Jaque mate. { $player } gana.
chess-draw = Tablas.
chess-draw-stalemate = Tablas por ahogado.
chess-draw-fifty-move = Tablas por la regla de las cincuenta jugadas.
chess-draw-seventy-five-move = Tablas por la regla obligatoria de las setenta y cinco jugadas.
chess-draw-threefold = Tablas por triple repetición.
chess-draw-fivefold = Tablas por repetición quíntuple obligatoria.
chess-draw-insufficient-material = Tablas por material insuficiente.
chess-draw-agreement = Tablas de mutuo acuerdo.
chess-draw-timeout-insufficient = Tablas. El oponente se quedó sin tiempo, pero no había suficiente material para dar mate.
chess-you-are-in-check = Tu rey está en jaque.
chess-player-is-in-check = El rey de { $player } está en jaque.
chess-you-lose-on-time = Se te acaba el tiempo. { $winner } gana por tiempo.
chess-player-loses-on-time = { $player } se queda sin tiempo. { $winner } gana por tiempo.

chess-you-en-passant = Mueves tu { $piece } de { $from_square } a { $to_square } y capturas al paso.
chess-player-en-passant = { $player } mueve su { $piece } de { $from_square } a { $to_square } y captura al paso.
chess-you-en-passant-brief = { $from_square } x { $to_square } a.p.
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } a.p.
chess-you-capture = Mueves tu { $piece } de { $from_square } a { $to_square }, capturando { $captured_piece }.
chess-player-captures = { $player } mueve su { $piece } de { $from_square } a { $to_square }, capturando { $captured_piece }.
chess-you-capture-brief = { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = Enrocas corto.
chess-player-castles-kingside = { $player } enroca corto.
chess-you-castle-kingside-brief = O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = Enrocas largo.
chess-player-castles-queenside = { $player } enroca largo.
chess-you-castle-queenside-brief = O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = Mueves tu { $piece } de { $from_square } a { $to_square }.
chess-player-moves = { $player } mueve su { $piece } de { $from_square } a { $to_square }.
chess-you-move-brief = { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = Coronas en { $square }.
chess-player-promotes = { $player } corona en { $square }.
chess-you-promote-to = Coronas el peón en { $square } a { $piece }.
chess-player-promotes-to = { $player } corona el peón en { $square } a { $piece }.
chess-you-promote-to-brief = Coronas { $square } a { $piece }.
chess-player-promotes-to-brief = { $player } corona { $square } a { $piece }.
chess-you-offer-draw = Ofreces tablas.
chess-player-offers-draw = { $player } ofrece tablas.
chess-you-accept-draw = Aceptas las tablas.
chess-player-accepts-draw = { $player } acepta las tablas.
chess-you-decline-draw = Rechazas las tablas.
chess-player-declines-draw = { $player } rechaza las tablas.
chess-you-request-undo = Solicitas deshacer.
chess-player-requests-undo = { $player } solicita deshacer.
chess-you-accept-undo = Aceptas la solicitud de deshacer.
chess-player-accepts-undo = { $player } acepta la solicitud de deshacer.
chess-you-decline-undo = Rechazas la solicitud de deshacer.
chess-player-declines-undo = { $player } rechaza la solicitud de deshacer.
chess-draw-offer-too-early = Las ofertas de tablas solo están disponibles después de que ambos jugadores hayan hecho al menos una jugada.
chess-claim-available-fifty-move = Ahora se puede reclamar tablas por las cincuenta jugadas.
chess-claim-available-threefold = Ahora se puede reclamar tablas por triple repetición.
chess-you-claim-draw-fifty-move = Reclamas tablas por la regla de las cincuenta jugadas.
chess-draw-claimed-fifty-move = { $player } reclama tablas por la regla de las cincuenta jugadas.
chess-you-claim-draw-threefold = Reclamas tablas por triple repetición.
chess-draw-claimed-threefold = { $player } reclama tablas por triple repetición.

chess-status-white = Blancas: { $player }
chess-status-black = Negras: { $player }
chess-status-turn = Turno: { $color } ({ $player })
chess-status-move-count = Jugadas completas realizadas: { $count }. Medias jugadas realizadas: { $plies }.
chess-status-promotion-pending = Hay una elección de coronación pendiente.
chess-status-check = El bando en turno está en jaque.
chess-status-time-control = Control de tiempo: { $control }
chess-status-draw-offer = Hay una oferta de tablas pendiente de { $player }.
chess-status-undo-request = Hay una solicitud de deshacer pendiente de { $player }.
chess-clock-line = Reloj de { $color }: { $time }
chess-clock-untimed = ilimitado
chess-clock-announcement = Blancas { $white }. Negras { $black }.
chess-clock-announcement-untimed = Esta partida es sin tiempo.

chess-board-flipped = Tablero volteado hacia el lado de las { $color }.
chess-empty = vacía
chess-board-rank-line = Fila { $rank }: { $pieces }

chess-end-winner = { $player } gana con { $color }.
chess-end-move-count = Jugadas completas realizadas: { $count }. Medias jugadas realizadas: { $plies }.
