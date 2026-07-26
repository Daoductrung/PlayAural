game-name-scopa = Scopa

scopa-initial-table = Cartas de la mesa: { $cards }
scopa-no-initial-table = No hay cartas en la mesa al empezar.
scopa-you-collect = Recoges { $cards } con { $card }
scopa-player-collects = { $player } recoge { $cards } con { $card }
scopa-you-capture = Capturas { $cards } con { $card }.
scopa-player-captures = { $player } captura { $cards } con { $card }.
scopa-you-capture-scopa = ¡Capturas { $cards } con { $card } y anotas una escoba!
scopa-player-captures-scopa = ¡{ $player } captura { $cards } con { $card } y anota una escoba!
scopa-you-capture-clear = Capturas { $cards } con { $card }, dejando la mesa vacía.
scopa-player-captures-clear = { $player } captura { $cards } con { $card }, dejando la mesa vacía.
scopa-you-put-down = Colocas { $card }.
scopa-player-puts-down = { $player } coloca { $card }.
scopa-scopa-suffix =  - ¡ESCOBA!
scopa-clear-table-suffix = , dejando la mesa vacía.
scopa-remaining-cards = { $player } se lleva las cartas restantes de la mesa.
scopa-you-get-remaining-cards = Te llevas las cartas restantes de la mesa: { $cards }.
scopa-player-gets-remaining-cards = { $player } se lleva las cartas restantes de la mesa: { $cards }.
scopa-you-instant-win = ¡Ganas de inmediato con una escoba!
scopa-your-team-instant-win = ¡Tu equipo gana de inmediato con una escoba!
scopa-instant-win = ¡{ $player } gana de inmediato con una escoba!
scopa-scoring-round = Calculando puntuación de la ronda...
scopa-you-most-cards = Anotas 1 punto por tener más cartas ({ $count } cartas).
scopa-your-team-most-cards = Tu equipo anota 1 punto por tener más cartas ({ $count } cartas).
scopa-most-cards = { $player } anota 1 punto por tener más cartas ({ $count } cartas).
scopa-most-cards-tie = Hay empate en cantidad de cartas: no se otorga punto.
scopa-you-most-diamonds = Anotas 1 punto por tener más diamantes ({ $count } diamantes).
scopa-your-team-most-diamonds = Tu equipo anota 1 punto por tener más diamantes ({ $count } diamantes).
scopa-most-diamonds = { $player } anota 1 punto por tener más diamantes ({ $count } diamantes).
scopa-most-diamonds-tie = Hay empate en cantidad de diamantes: no se otorga punto.
scopa-you-seven-diamonds = Anotas 1 punto por el 7 de diamantes.
scopa-your-team-seven-diamonds = Tu equipo anota 1 punto por el 7 de diamantes.
scopa-seven-diamonds = { $player } anota 1 punto por el 7 de diamantes.
scopa-you-seven-diamonds-multi = Anotas 1 punto por tener más 7 de diamantes ({ $count } x 7 de diamantes).
scopa-your-team-seven-diamonds-multi = Tu equipo anota 1 punto por tener más 7 de diamantes ({ $count } x 7 de diamantes).
scopa-seven-diamonds-multi = { $player } anota 1 punto por tener más 7 de diamantes ({ $count } × 7 de diamantes).
scopa-seven-diamonds-tie = Hay empate en el 7 de diamantes: no se otorga punto.
scopa-you-most-sevens = Anotas 1 punto por tener más sietes ({ $count } sietes).
scopa-your-team-most-sevens = Tu equipo anota 1 punto por tener más sietes ({ $count } sietes).
scopa-most-sevens = { $player } anota 1 punto por tener más sietes ({ $count } sietes).
scopa-most-sevens-tie = Hay empate en cantidad de sietes: no se otorga punto.
scopa-you-primiera = Anotas 1 punto por primiera ({ $score } puntos).
scopa-your-team-primiera = Tu equipo anota 1 punto por primiera ({ $score } puntos).
scopa-primiera = { $player } anota 1 punto por primiera ({ $score } puntos).
scopa-primiera-tie = Hay empate en primiera: no se otorga punto.
scopa-primiera-none = Nadie capturó cartas de los cuatro palos, así que no se otorga el punto de primiera.
scopa-you-napola = Anotas { $points } puntos por napola.
scopa-your-team-napola = Tu equipo anota { $points } puntos por napola.
scopa-napola = { $player } anota { $points } puntos por napola.

scopa-manual-select-prompt = Debes elegir qué cartas capturar.

scopa-capture-option = Capturar { $cards }

scopa-error-conflict-escoba-asso = Escoba y Asso Piglia Tutto no se pueden activar al mismo tiempo.
scopa-error-conflict-instant-inverse = La victoria instantánea por escoba no se puede activar junto con el modo inverso.
scopa-error-conflict-instant-no-scopas = La victoria instantánea por escoba no se puede activar cuando las escobas no puntúan.

scopa-score-line-target-pending = { $player }: { $score }/{ $target } { $unit } (+{ $round_score } { $pending_unit } de escoba pendientes esta ronda)
scopa-score-line-pending = { $player }: { $score } { $unit } (+{ $round_score } { $pending_unit } de escoba pendientes esta ronda)
scopa-target-tie-continue = Varios lados están empatados en { $score } { $score ->
    [one] punto
   *[other] puntos
}, así que Scopa continúa más allá del objetivo de { $target } { $target ->
    [one] punto
   *[other] puntos
} hasta que se rompa el empate.
scopa-round-scores = Puntuaciones de la ronda:
scopa-round-score-line = { $player }: +{ $round_score } (total: { $total_score })
scopa-table-empty = No hay cartas en la mesa.
scopa-no-such-card = No hay ninguna carta en esa posición.
scopa-captured-count = Has capturado { $count } cartas

scopa-view-table = Ver mesa
scopa-view-captured = Ver capturadas
scopa-view-table-card = Ver carta de mesa { $index }
scopa-pause-timer = Pausar temporizador

scopa-hint-match =  -> { $card }
scopa-hint-multi =  -> { $count } cartas

scopa-enter-target-score = Ingresa la puntuación objetivo (1-121)
scopa-desc-target-score = Puntuación necesaria para ganar en Scopa (por defecto 11, rango 1-121).
scopa-set-cards-per-deal = Cartas por reparto: { $cards }
scopa-enter-cards-per-deal = Ingresa las cartas por reparto (1-10)
scopa-set-decks = Número de barajas: { $decks }
scopa-enter-decks = Ingresa el número de barajas (1-6)
scopa-toggle-escoba = Escoba (suma 15): { $enabled }
scopa-toggle-hints = Mostrar pistas de captura: { $enabled }
scopa-set-mechanic = Mecánica de escoba: { $mechanic }
scopa-select-mechanic = Selecciona la mecánica de escoba
scopa-toggle-instant-win = Victoria instantánea por escoba: { $enabled }
scopa-desc-team-mode = Elige juego individual o equipos de tamaño fijo para Scopa.
scopa-toggle-team-scoring = Combinar cartas del equipo para puntuar: { $enabled }
scopa-toggle-inverse = Modo inverso (llegar al objetivo = eliminación): { $enabled }
scopa-toggle-manual = Selección manual de captura: { $enabled }
scopa-toggle-asso = Asso piglia tutto (el As se lo lleva todo): { $enabled }
scopa-toggle-primiera = Puntuación tradicional de primiera: { $enabled }
scopa-toggle-napola = Napola (secuencia de diamantes): { $enabled }

scopa-option-changed-cards = Cartas por reparto establecidas en { $cards }.
scopa-desc-cards-per-deal = Cuántas cartas recibe cada jugador en cada reparto de Scopa (por defecto 3, rango 1-10).
scopa-option-changed-decks = Número de barajas establecido en { $decks }.
scopa-desc-number-of-decks = Cuántas barajas de 40 cartas de Scopa se mezclan juntas (por defecto 1, rango 1-6).
scopa-option-changed-escoba = Escoba { $enabled }.
scopa-desc-escoba = Cambia las capturas a las reglas de Escoba, donde la carta jugada y las cartas capturadas de la mesa deben sumar 15.
scopa-option-changed-hints = Pistas de captura { $enabled }.
scopa-desc-show-capture-hints = Muestra qué cartas de la mesa puede capturar cada carta de la mano.
scopa-option-changed-mechanic = Mecánica de escoba establecida en { $mechanic }.
scopa-desc-scopa-mechanic = Elige puntuación normal por barrida, sin puntos de escoba, o puntuación solo por escobas.
scopa-option-changed-instant = Victoria instantánea por escoba { $enabled }.
scopa-desc-instant-win-scopas = Cuando está activado, una escoba válida gana la partida de inmediato. No se puede combinar con Sin Escobas ni Escoba Inversa.
scopa-option-changed-team-scoring = Puntuación de cartas por equipo { $enabled }.
scopa-desc-team-card-scoring = Controla si los compañeros de equipo combinan sus cartas capturadas para la puntuación de fin de ronda. Si está desactivado en una partida por equipos, las capturas de cada jugador se evalúan por separado y los puntos ganados se suman al equipo de ese jugador.
scopa-option-changed-inverse = Modo inverso { $enabled }.
scopa-desc-inverse-scopa = Invierte el objetivo, de modo que llegar a la puntuación objetivo elimina a un jugador o equipo.
scopa-option-changed-manual = Selección manual de captura { $enabled }.
scopa-desc-manual-selection = Permite a los jugadores elegir manualmente una combinación de captura cuando existe más de una captura legal.
scopa-option-changed-asso = Asso piglia tutto { $enabled }.
scopa-desc-asso-piglia-tutto = Activa "el As se lo lleva todo": un As barre la mesa y anota una escoba, salvo que ya haya otro As presente. No se puede combinar con Escoba.
scopa-option-changed-primiera = Puntuación tradicional de primiera { $enabled }.
scopa-desc-primiera-scoring = Activa la puntuación tradicional de primiera; cuando está desactivada, la partida usa la variante más simple de Más Sietes.
scopa-option-changed-napola = Napola { $enabled }.
scopa-desc-napola = Otorga puntos extra por capturar una secuencia continua de diamantes empezando por el As.

scopa-mechanic-normal = Normal
scopa-mechanic-no_scopas = Sin Escobas
scopa-mechanic-only_scopas = Solo Escobas

scopa-timer-not-active = El temporizador de la ronda no está activo.

scopa-error-not-enough-cards = No hay suficientes cartas en { $decks } { $decks ->
    [one] baraja
    *[other] barajas
} para { $players } { $players ->
    [one] jugador
    *[other] jugadores
} con { $cards_per_deal } cartas cada uno. (Se necesitan { $cards_per_deal } × { $players } = { $cards_needed } cartas, pero solo hay { $total_cards }.)

scopa-line-format = { $rank }. { $player }: { $points }
