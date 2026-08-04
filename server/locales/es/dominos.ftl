game-name-dominos = Dominó
dominos-desc-team-mode = Juega individualmente, o usa cualquier organización de equipos pares válida según la cantidad actual de jugadores.

# Options
dominos-set-target-score = Puntuación objetivo: { $score }
dominos-enter-target-score = Ingresa la puntuación objetivo
dominos-option-changed-target-score = Puntuación objetivo establecida en { $score }.
dominos-desc-target-score = Puntuación objetivo necesaria para ganar en Dominó (por defecto 100, rango 20-500).

dominos-set-draw-mode = Modo: { $mode }
dominos-select-draw-mode = Selecciona el modo
dominos-option-changed-draw-mode = Modo establecido en { $mode }.
dominos-desc-draw-mode = Elige el modo Robo, donde los jugadores roban del pozo, o el modo Bloqueo, donde los jugadores bloqueados pasan.

dominos-set-domino-set = Juego de fichas: { $domino_set }
dominos-select-domino-set = Selecciona el juego de fichas
dominos-option-changed-domino-set = Juego de fichas cambiado a { $domino_set }.
dominos-desc-domino-set = Tamaño del juego de fichas. Doble-6 admite hasta 5 jugadores, Doble-9 admite hasta 7 jugadores, y Doble-12 admite hasta 12 jugadores (por defecto Doble-6).

dominos-set-spinner = Doble giratorio: { $enabled }
dominos-option-changed-spinner = Doble giratorio establecido en { $enabled }.
dominos-desc-spinner-enabled = Controla si el doble de apertura crea un cruce en cuatro direcciones (por defecto activado).

dominos-set-opening-rule = Regla de apertura: { $opening_rule }
dominos-select-opening-rule = Selecciona la regla de apertura
dominos-option-changed-opening-rule = Regla de apertura establecida en { $opening_rule }.
dominos-desc-opening-rule = Elige cómo se selecciona la primera ficha de cada ronda de Dominó.

# Option choice labels
dominos-mode-draw = Robo
dominos-mode-block = Bloqueo

dominos-set-double6 = Doble-6
dominos-set-double9 = Doble-9
dominos-set-double12 = Doble-12

dominos-opening-highest-double = Doble más alto
dominos-opening-highest-tile = Ficha más alta
dominos-opening-set-max-double = Doble máximo del juego
dominos-opening-random-player = Jugador aleatorio
dominos-opening-round-winner = Ganador de la ronda anterior

# Actions
dominos-draw = Robar
dominos-knock = Pasar
dominos-view-chain = Ver cadena
dominos-read-ends = Leer extremos
dominos-read-hand = Leer mano
dominos-read-counts = Leer cantidades
dominos-play-tile = { $tile }
dominos-open-with-tile = Abrir con { $tile }
dominos-play-tile-at = Jugar { $tile } en { $side }
dominos-play-tile-multi = Jugar { $tile } en { $sides }
dominos-select-side = Selecciona un lado

# Board sides
dominos-side-left = izquierda
dominos-side-right = derecha
dominos-side-up = arriba
dominos-side-down = abajo

# Validation and disabled reasons
dominos-draw-only-mode = Robar solo está disponible en modo Robo.
dominos-must-play = Ya tienes una ficha jugable.
dominos-boneyard-empty = El pozo está vacío.
dominos-must-draw = Debes robar antes de pasar.
dominos-illegal-side = Ese lado no es válido para la ficha seleccionada.
dominos-no-play-for-tile = { $tile } no se puede jugar en este momento.
dominos-choose-side-keybind = Elige un lado con la tecla de dirección. Lados válidos: { $sides }.
dominos-opening-must-play = La ronda aún no se ha abierto. Debes elegir una ficha para iniciar la cadena.
dominos-error-set-too-small = No se le pueden repartir suficientes fichas a { $players } jugadores con un juego Doble-{ $selected_pip }. Elige al menos Doble-{ $required_pip } para este tamaño de mesa.

# Gameplay
dominos-you-open-round = Tú abres esta ronda. Elige cualquier ficha de tu mano para iniciar la cadena.
dominos-player-opens-round = { $player } abre esta ronda y está eligiendo la ficha de apertura.
dominos-you-opened = Abriste la ronda con { $tile }.
dominos-player-opened = { $player } abrió la ronda con { $tile }.
dominos-you-opened-spinner = Abriste la ronda con { $tile }, creando un cruce en cuatro direcciones.
dominos-player-opened-spinner = { $player } abrió la ronda con { $tile }, creando un cruce en cuatro direcciones.
dominos-you-drew-single = Robaste { $tile } del pozo.
dominos-you-drew-many = Robaste { $count } fichas del pozo.
dominos-player-drew-single = { $player } robó 1 ficha del pozo.
dominos-player-drew-many = { $player } robó { $count } fichas del pozo.
dominos-you-played = Jugaste { $tile } en la rama { $side }.
dominos-you-played-drawn = Robaste y jugaste { $tile } en la rama { $side }.
dominos-player-played = { $player } jugó { $tile } en la rama { $side }.
dominos-you-knock = Pasas porque no tienes ninguna ficha legal para jugar.
dominos-player-knocks = { $player } pasa.
dominos-you-won-round = Vaciaste tu mano y anotaste { $points } puntos de las fichas de los oponentes.
dominos-player-won-round = { $player } vació su mano y anotó { $points } puntos de las fichas de los oponentes.
dominos-round-blocked-tie = La ronda está bloqueada. El total de puntos más bajo es { $pips }, pero hay empate. No se anotan puntos.
dominos-round-blocked-winner = La ronda está bloqueada. { $team } tiene el total de puntos más bajo con { $pips } y anota { $points } puntos.
dominos-match-tied-continue = Varios equipos llegaron a { $score } puntos. La partida continúa hasta romper el empate.
dominos-match-winner = { $team } gana la partida con { $score } puntos.

# Status boxes
dominos-chain-header = Cadena
dominos-chain-empty = La cadena está vacía.
dominos-chain-center = Centro: { $tile }
dominos-branch-empty = sin fichas
dominos-chain-branch = { $side }: { $tiles }. Extremo abierto { $open_end }.
dominos-boneyard-count = Pozo: quedan { $count } fichas.
dominos-end-info = { $side } { $value }

dominos-hand-header = Tu mano
dominos-hand-line = { $tile }, vale { $points } puntos.
dominos-hand-line-playable = { $tile }, vale { $points } puntos. Jugable en { $sides }.
dominos-hand-line-opening-playable = { $tile }, vale { $points } puntos. Puedes usarla para abrir esta ronda.
dominos-hand-total = Total de puntos en mano: { $pips }.
dominos-player-count = { $player } tiene { $count } fichas
dominos-no-other-players = No hay otros jugadores.

# End screen
dominos-line-format = { $rank }. { $player }: { $points }
