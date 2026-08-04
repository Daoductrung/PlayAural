# Humanity Cards - localización en español

game-name-humanitycards = Cartas contra la Humanidad

# Opciones
hc-set-winning-score = Puntuación para ganar: { $score }
hc-enter-winning-score = Ingresa la puntuación para ganar:
hc-option-changed-winning-score = Puntuación para ganar establecida en { $score }.
hc-desc-winning-score = Cantidad de cartas ganadoras que un jugador necesita reunir para ganar la partida (por defecto 7, rango 3-20).

hc-set-hand-size = Tamaño de mano: { $count }
hc-enter-hand-size = Ingresa el tamaño de mano:
hc-option-changed-hand-size = Tamaño de mano establecido en { $count }.
hc-desc-hand-size = Cuántas cartas de respuesta tiene cada jugador después de cada recarga. Manos más grandes dan más opciones pero alargan las rondas (por defecto 10, rango 5-15).

hc-set-card-packs = Paquetes de cartas ({ $count } de { $total } seleccionados)
hc-option-changed-card-packs = Se cambió la selección de paquetes de cartas.
hc-desc-card-packs = Elige qué paquetes de respuestas y preguntas se mezclan en la partida. Debe quedar seleccionado al menos un paquete.

hc-set-czar-selection = Selección del Zar de la Carta: { $mode }
hc-select-czar-selection = Selecciona el modo de selección del Zar de la Carta
hc-option-changed-czar-selection = Selección del Zar de la Carta establecida en { $mode }.
hc-desc-czar-selection = Controla quién juzga cada ronda: rotando por orden de asiento, elegido al azar, o el ganador más reciente de la ronda.

hc-set-num-judges = Número de jueces: { $count }
hc-enter-num-judges = Ingresa el número de jueces:
hc-option-changed-num-judges = Número de jueces establecido en { $count }.
hc-desc-num-judges = Cuántos Zares de la Carta juzgan cada ronda. La cantidad debe ser menor que la de jugadores para que al menos uno pueda enviar una respuesta; con varios jueces, cualquiera puede elegir al ganador (por defecto 1, rango 1-3).

hc-czar-rotating = Rotativo
hc-czar-random = Aleatorio
hc-czar-winner = Ganador más reciente

# Flujo de la partida
hc-game-starting = Barajando los mazos...
hc-dealing-cards = Repartiendo { $count } cartas a cada jugador.
hc-round-start = Ronda { $round }.

# Anuncio del juez
hc-judge-is = { $judges } { $count ->
    [1] es el Zar de la Carta
   *[other] son los Zares de la Carta
}.
hc-you-are-judge = Eres el Zar de la Carta esta ronda.
hc-you-and-others-are-judges = Tú y { $judges } son los Zares de la Carta esta ronda.
hc-you-are-not-judge = No eres el Zar de la Carta esta ronda.

# Carta negra
hc-black-card = La pregunta es: { $text }
hc-black-card-pick = Elige { $count }.
hc-view-black-card = Ver la carta de pregunta

# Fase de envío
hc-select-cards = Selecciona { $count } { $count ->
    [one] carta
   *[other] cartas
} de tu mano.
hc-card-selected = { $text }, seleccionada
hc-card-not-selected = { $text }
hc-submit-cards = Enviar ({ $selected } de { $required } seleccionadas)
hc-submission-progress = { $submitted } de { $total } jugadores enviaron su respuesta.
hc-waiting-for-submissions = Esperando envíos...
hc-already-submitted = Ya enviaste tus cartas.
hc-you-submitted = Enviaste tus cartas.
hc-player-submitted = { $player } envió sus cartas.
hc-judge-cannot-submit = Eres el Zar de la Carta esta ronda, así que no puedes enviar una respuesta.
hc-not-submission-phase = Solo puedes seleccionar y enviar cartas blancas durante la fase de envío.
hc-card-not-in-hand = Esa carta ya no está en tu mano.
hc-judge-has-no-submission = El Zar de la Carta no tiene una respuesta para previsualizar esta ronda.
hc-no-submission-active = No hay ninguna respuesta activa para previsualizar en este momento.
hc-wrong-card-count = Necesitas seleccionar exactamente { $count } { $count ->
    [one] carta
   *[other] cartas
}.

# Fase de juicio
hc-judging-start = ¡Todas las cartas están listas! Hora de juzgar.
hc-choose-best-card = Elige la mejor carta
hc-choose-best-card-for = Elige la mejor carta para: { $prompt }
hc-select-winner-prompt = Selecciona la respuesta ganadora
hc-card-number = Carta { $number }
hc-submission-number = Respuesta { $number }
hc-submission-option = { $text }
hc-only-judges-pick = Solo el Zar de la Carta puede elegir la respuesta ganadora.
hc-not-judging-phase = Solo puedes elegir una respuesta ganadora durante la fase de juicio.
hc-submission-not-available = Esa respuesta ya no está disponible.

# Resultados
hc-you-win-round = ¡Ganas la ronda! Tu puntuación ahora es { $score }.
hc-player-wins-round = ¡{ $player } gana la ronda! Puntuación: { $score }.
hc-round-scores = Puntuaciones después de la ronda { $round }:
hc-score-line = { $player }: { $score } { $score ->
    [one] punto
   *[other] puntos
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] punto
   *[other] puntos
}
hc-all-submissions = Otras respuestas:
hc-your-winning-answer = Tu respuesta ganadora: { $text }
hc-winning-answer-player = Respuesta ganadora de { $player }: { $text }
hc-your-other-submission = Tu otra respuesta: { $text }
hc-other-submission-player = { $player }: { $text }

# Vista
hc-preview-submission = Previsualizar tu respuesta
hc-view-submission = Ver tu respuesta
hc-preview-submission-text = Vista previa: { $text }
hc-your-submission = Tu respuesta: { $text }
hc-select-cards-first = Primero selecciona al menos 1 carta.

# Victoria
hc-game-winner = ¡{ $player } gana con { $score } puntos!
hc-you-win = ¡Ganas con { $score } puntos!
hc-english-content-note = Nota: por ahora, el texto de las cartas de pregunta y respuesta solo está disponible en inglés.

# Gestión del mazo
hc-deck-reshuffled = El descarte de cartas blancas se volvió a barajar en el mazo.
hc-black-deck-reshuffled = El descarte de cartas negras se volvió a barajar en el mazo.
hc-not-enough-cards = No hay suficientes cartas. Intenta activar más paquetes.
hc-error-too-many-judges = { $judges } jueces requieren al menos { $required } jugadores, pero esta mesa tiene { $players }. Reduce el número de jueces o agrega más jugadores.
hc-error-no-valid-packs = No hay ningún paquete de cartas válido seleccionado. Selecciona al menos un paquete antes de empezar.
hc-error-no-black-cards = Los paquetes de cartas seleccionados no contienen ninguna carta negra de pregunta. Selecciona otro paquete antes de empezar.
hc-error-not-enough-white-cards = { $players } jugadores con un tamaño de mano de { $hand_size } necesitan al menos { $needed } cartas blancas, pero los paquetes seleccionados solo proveen { $available }. Activa más paquetes o reduce el tamaño de mano.
hc-error-pick-exceeds-hand-size = Los paquetes seleccionados incluyen una pregunta que requiere { $pick } respuestas, pero el tamaño de mano es solo { $hand_size }. Aumenta el tamaño de mano o elige otros paquetes.

# Gestión de la mano
hc-view-hand = Ver mano
hc-toggle-card-keybind = Alternar carta { $number }
hc-submit-cards-keybind = Enviar cartas

# Puntuaciones
hc-view-scores = Ver puntuaciones
hc-no-scores = Aún no hay puntuaciones.

# De quién es el turno / quién juzga
hc-whose-judge = Quién está juzgando
hc-waiting-for = Esperando a que { $names } envíen su respuesta.
hc-all-submitted-waiting-judge = Todos los jugadores enviaron su respuesta. Esperando a que { $judge } juzgue.
