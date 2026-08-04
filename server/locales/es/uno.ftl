game-name-uno = UNO

# Colores
uno-color-red = Rojo
uno-color-yellow = Amarillo
uno-color-green = Verde
uno-color-blue = Azul
uno-color-wild = Comodín

# Nombres de cartas
uno-card-number = { $color } { $value }
uno-card-skip = { $color } Salta Turno
uno-card-reverse = { $color } Sentido Contrario
uno-card-draw-two = { $color } Roba Dos
uno-card-wild = Comodín
uno-card-wild-four = Comodín Roba Cuatro

# Opciones
uno-set-winning-score = Límite de puntuación: { $score }
uno-enter-winning-score = Ingresa el límite de puntuación
uno-option-changed-winning-score = Límite de puntuación establecido en { $score }.
uno-desc-winning-score = Límite de puntuación usado por el modo de puntuación de UNO seleccionado (por defecto 300, rango 10-2000).

uno-set-scoring-mode = Puntuación: { $mode }
uno-select-scoring-mode = Selecciona el modo de puntuación
uno-option-changed-scoring-mode = Puntuación establecida en { $mode }.
uno-desc-scoring-mode = Elige si gana el primer jugador en llegar al límite, o si los jugadores que llegan al límite quedan eliminados.
uno-scoring-first = Gana el primero en llegar al límite
uno-scoring-elimination = Eliminación

uno-set-skip-after-draw = Las penalizaciones de robo saltan el turno: { $enabled }
uno-option-changed-skip-after-draw = Las penalizaciones de robo saltan el turno { $enabled }.
uno-desc-skip-after-draw = Controla si las penalizaciones de Roba Dos y Comodín Roba Cuatro también saltan el turno del objetivo.

uno-set-responses = Respuestas acumulables: { $enabled }
uno-option-changed-responses = Respuestas acumulables { $enabled }.
uno-desc-responses = Permite a los jugadores acumular cartas de robo en respuesta a las penalizaciones de Roba Dos o Comodín Roba Cuatro.

uno-set-advanced-responses = Respuestas avanzadas: { $enabled }
uno-option-changed-advanced-responses = Respuestas avanzadas { $enabled }.
uno-desc-advanced-responses = Permite respuestas defensivas adicionales a las pilas de robo, como igualar con cartas de Salta Turno, Sentido Contrario o Comodín. Requiere Respuestas acumulables.

uno-set-wait-for-draw-responses = Esperar respuestas de robo: { $enabled }
uno-option-changed-wait-for-draw-responses = Esperar respuestas de robo { $enabled }.
uno-desc-wait-for-draw-responses = Si la última carta crea una pila de robo, espera a que el siguiente jugador responda o robe antes de puntuar la ronda. Requiere Respuestas acumulables.

uno-set-bluff = Desafíos al Comodín Roba Cuatro: { $enabled }
uno-option-changed-bluff = Desafíos al Comodín Roba Cuatro { $enabled }.
uno-desc-bluff = Activa las reglas de desafío al Comodín Roba Cuatro para jugadas ilegales.

uno-set-straights = Secuencias: { $enabled }
uno-option-changed-straights = Secuencias { $enabled }.
uno-desc-straights = Permite que un jugador continúe fuera de turno con el número siguiente o anterior del mismo color después de una carta numérica.

uno-set-interceptions = Intercepciones: { $enabled }
uno-option-changed-interceptions = Intercepciones { $enabled }.
uno-desc-interceptions = Permite a los jugadores intervenir fuera de turno con una carta exactamente igual. Los intentos inválidos suman 3 puntos de penalización.

uno-set-super-interceptions = Súper intercepciones: { $enabled }
uno-option-changed-super-interceptions = Súper intercepciones { $enabled }.
uno-desc-super-interceptions = Amplía las intercepciones para igualar por número o símbolo de acción aunque el color sea distinto. Requiere Intercepciones.

uno-set-zero-seven = Regla del cero / siete: { $enabled }
uno-option-changed-zero-seven = Regla del cero / siete { $enabled }.
uno-desc-zero-seven-rule = Activa la regla casera donde el 0 rota las manos de todos y el 7 permite al jugador intercambiar su mano o declinar.

uno-set-free-draws = Robos gratuitos por turno: { $count }
uno-enter-free-draws = Ingresa los robos gratuitos por turno
uno-option-changed-free-draws = Robos gratuitos por turno establecidos en { $count }.
uno-desc-free-draws = Cuántas veces puede robar un jugador humano a pesar de tener una carta jugable (por defecto 0, rango 0-999).

# Validación de opciones
uno-error-advanced-responses-require-responses = Las respuestas avanzadas requieren que las Respuestas acumulables estén activadas.
uno-error-wait-responses-require-responses = Esperar respuestas de robo requiere que las Respuestas acumulables estén activadas.
uno-error-super-interceptions-require-interceptions = Las súper intercepciones requieren que las Intercepciones estén activadas.

# Acciones
uno-draw = Robar
uno-say-uno = ¡UNO!
uno-read-top = Leer carta superior
uno-read-color = Leer color actual
uno-read-counts = Leer cantidad de cartas
uno-read-hand = Leer valor de tu mano
uno-sort-color = Ordenar por color
uno-sort-number = Ordenar por número

# Anuncios de juego
uno-new-hand = Ronda { $round }.
uno-start-card = { $player } voltea { $card }.
uno-you-start-card = Volteas { $card }.
uno-current-color = Color actual: { $color }.
uno-choose-opening-color-you = Elige el color de apertura.
uno-choose-opening-color-player = { $player } debe elegir el color de apertura.
uno-dealt-cards = A todos se les reparten { $cards } cartas.
uno-direction-reversed = El sentido del juego se invierte.
uno-player-plays = { $player } juega { $card }.
uno-you-play = Juegas { $card }.
uno-player-chooses-color = { $player } elige { $color }.
uno-you-choose-color = Eliges { $color }.
uno-player-draws-one = { $player } roba una carta.
uno-player-draws-many = { $player } roba { $count } cartas.
uno-you-draw-one = Robas una carta.
uno-you-draw-many = Robas { $count } cartas.
uno-cant-play = { $player } no puede jugar.
uno-you-cant-play = No puedes jugar.
uno-you-skipped = Se te salta el turno.
uno-says-uno = ¡{ $player } dice UNO!
uno-you-say-uno = ¡Dices UNO!
uno-callout = ¡{ $caller } acusa a { $player } de no decir UNO! { $player } roba { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-you-callout = ¡Acusas a { $player } de no decir UNO! { $player } roba { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-callout-you = ¡{ $caller } te acusa de no decir UNO! Robas { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-error-already-said-uno = Ya dijiste UNO.
uno-error-no-uno-call = No hay ninguna llamada de UNO disponible en este momento.
uno-cannot-play-that = No puedes jugar { $card }. { $reason }
uno-reshuffle = Volviendo a barajar el descarte.
uno-hand-blocked = Nadie puede jugar. La ronda termina.
uno-error-choose-color-first = Elige un color para tu carta Comodín antes de jugar otra carta.
uno-error-wait-color-choice = Espera a que el jugador de la carta Comodín elija un color antes de jugar.
uno-error-wild-transition = Espera a que el color elegido surta efecto antes de jugar otra carta.
uno-error-choose-swap-first = Elige un objetivo para intercambiar mano o declina antes de realizar otra acción.
uno-error-wait-swap-choice = Espera a que termine la elección de intercambio de mano del siete antes de jugar.
uno-error-wait-next-hand = Espera a que empiece la siguiente ronda antes de jugar una carta.
uno-error-wait-intro = Espera a que termine la preparación de la ronda antes de jugar una carta.
uno-reason-draw-stack-response = Hay una pila de robo de { $count } { $count ->
    [one] carta
   *[other] cartas
} en tu contra; juega una carta de respuesta válida o roba la penalización.
uno-reason-draw-stack-no-response = Hay una penalización de robo de { $count } { $count ->
    [one] carta
   *[other] cartas
} en tu contra, y las respuestas acumulables están desactivadas; roba la penalización.
uno-reason-match-required = La carta superior es { $top }, y el color activo es { $color }; iguala el color, iguala el número o símbolo de acción, o juega un Comodín.
uno-reason-card-not-available = Esa carta no está disponible en el estado actual.

# Desafío de farol
uno-bluff-challenge = Desafiar Comodín Roba Cuatro
uno-bluff-caught = ¡{ $player } jugó un Comodín Roba Cuatro ilegal y roba { $count } cartas!
uno-you-bluff-caught = ¡Jugaste un Comodín Roba Cuatro ilegal y robas { $count } cartas!
uno-bluff-wrong = ¡{ $player } desafió el Comodín Roba Cuatro incorrectamente y roba { $count } cartas!
uno-you-bluff-wrong = ¡Desafiaste el Comodín Roba Cuatro incorrectamente y robas { $count } cartas!

# Regla del cero / siete
uno-rotate-hands = ¡Todos pasan su mano!
uno-swap-hands = ¡{ $player } intercambia su mano con { $target }!
uno-you-swap = ¡Intercambias tu mano con { $target }!
uno-swap-with-you = ¡{ $player } intercambia su mano contigo!
uno-swap-with = Intercambiar mano con { $player }
uno-choose-swap = Elige un jugador para intercambiar manos, o declina.
uno-swap-none = No intercambiar
uno-you-swap-none = Conservas tu mano.
uno-swap-none-other = { $player } conserva su mano.

# Intercepciones / secuencias
uno-player-intercepts = ¡{ $player } intercepta con { $card }!
uno-you-intercept = ¡Interceptas con { $card }!
uno-bad-intercept = Esa no fue una intercepción válida. { $points } puntos de penalización.
uno-not-your-turn = No es tu turno.

# Información
uno-no-top = Todavía no hay carta superior.
uno-top-card = { $card }.
uno-color-is = { $color }.
uno-count-you = Tú { $count }
uno-count-player = { $player } { $count }
uno-deck-count = mazo { $count }
uno-sorting-color = Ordenando por color.
uno-sorting-number = Ordenando por número.

# Fin de ronda / partida
uno-round-winner = ¡{ $player } gana la ronda!
uno-you-win-round = ¡Ganas la ronda!
uno-round-points-from = { $points } de { $player }
uno-round-points-from-you = { $points } de ti
uno-round-points-from-with-interception = { $points } de { $player } ({ $hand_points } de mano + { $penalty } de penalización por intercepción)
uno-round-points-from-you-with-interception = { $points } de ti ({ $hand_points } de mano + { $penalty } de penalización por intercepción)
uno-round-details-none = No se tomaron puntos de los oponentes.
uno-round-summary = { $details }. { $player } gana { $total }.
uno-round-summary-you = { $details }. Ganas { $total }.
uno-you-add-penalty-points = Sumas { $points } puntos de penalización a tu total de esta ronda.
uno-player-adds-penalty-points = { $player } suma { $points } puntos de penalización a su total de esta ronda.
uno-you-add-penalty-points-with-interception = Sumas { $points } puntos de penalización a tu total de esta ronda ({ $hand_points } de tu mano más { $penalty } de penalización por intercepción).
uno-player-adds-penalty-points-with-interception = { $player } suma { $points } puntos de penalización a su total de esta ronda ({ $hand_points } de su mano más { $penalty } de penalización por intercepción).
uno-you-are-eliminated = Llegaste al límite de eliminación de { $limit } puntos y quedas fuera de la partida.
uno-player-is-eliminated = { $player } llegó al límite de eliminación de { $limit } puntos y queda fuera de la partida.
uno-you-win-game =
    { $mode ->
        [elimination] Eres el último jugador en pie y ganas con { $score } puntos de penalización.
       *[first_to_limit] ¡Ganas la partida con { $score } puntos!
    }
uno-player-wins-game =
    { $mode ->
        [elimination] { $player } es el último jugador en pie y gana con { $score } puntos de penalización.
       *[first_to_limit] ¡{ $player } gana la partida con { $score } puntos!
    }
uno-game-tie = Todos quedaron eliminados. ¡La partida termina en empate!
uno-score-line-first = { $player }: { $score }/{ $target } puntos.
uno-score-line-elimination = { $player }: { $score }/{ $target } puntos de penalización.
uno-line-format = { $rank }. { $player }: { $score }

# Valor de la mano (tecla d)
uno-read-hand-value = { $count ->
    [one] { $count } carta
   *[other] { $count } cartas
 } por un valor de { $points ->
    [one] { $points } punto
   *[other] { $points } puntos
 }.
