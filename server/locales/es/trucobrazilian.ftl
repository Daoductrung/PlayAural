# Opciones
trucobrazilian-desc-team-mode = Individual es una partida uno contra uno para 2 jugadores. 2v2 usa 4 jugadores y 3v3 usa 6 jugadores; los compañeros comparten el puntaje y pueden cantar por todo el equipo.

# Baraja francesa
trucobrazilian-rank-ace = As
trucobrazilian-rank-jack = Jota
trucobrazilian-rank-queen = Reina
trucobrazilian-rank-king = Rey
trucobrazilian-suit-diamonds = diamantes
trucobrazilian-suit-spades = picas
trucobrazilian-suit-hearts = corazones
trucobrazilian-suit-clubs = tréboles
trucobrazilian-card-name = { $rank } de { $suit }

# Cantos
trucobrazilian-call-truco = Truco
trucobrazilian-call-seis = Seis
trucobrazilian-call-nove = Nove
trucobrazilian-call-doze = Doze
trucobrazilian-call-onze = Mão de onze

# Acciones e información
trucobrazilian-action-onze-play = Jogar (jugar la mano)
trucobrazilian-action-onze-run = Correr (huir y abandonar la mano)
trucobrazilian-read-vira = Leer la vira y la manilha
trucobrazilian-no-vira = Todavía no se ha volteado la vira.
trucobrazilian-vira = La vira es { $card }. La manilha es { $manilha }.
trucobrazilian-vira-is = La vira es { $card }. La manilha es { $manilha }.

# Desarrollo de la partida
trucobrazilian-game-start = Comienza el truco brasileño. Gana quien llegue primero a { $points } puntos. En cada mano, una carta volteada llamada vira decide cuáles son las manilhas.
trucobrazilian-onze-your-team = Tu equipo tiene 11 puntos: mão de onze. Elige Jogar para jugar la mano por 3 puntos sin cantos, o Correr para darle 1 punto al otro lado.
trucobrazilian-onze-team = { $team } tiene 11 puntos y está decidiendo si juega la mão de onze.
trucobrazilian-onze-play-you = Juegas la mão de onze. La mano vale 3 puntos y no se permiten cantos.
trucobrazilian-onze-play-player = { $player } juega la mão de onze. La mano vale 3 puntos y no se permiten cantos.
trucobrazilian-onze-run-you = Corres. El otro lado suma 1 punto.
trucobrazilian-onze-run-player = { $player } corre. El otro lado suma 1 punto.
trucobrazilian-ferro = Ambos lados tienen 11 puntos: mão de ferro. No se permiten cantos y quien gane la mano gana la partida.
trucobrazilian-reason-onze-run = la huida en la mão de onze
trucobrazilian-hand-annulled = Las tres bazas quedaron empatadas. La mano se anula y nadie suma puntos.

# Errores y descripciones
trucobrazilian-error-onze-pending = { $team } debe decidir primero si juega la mão de onze.
trucobrazilian-error-no-calls = En esta mano no se permite cantar porque es una mão de onze o una mão de ferro.
trucobrazilian-desc-onze-play = Jugar la mano. Vale { $points } { $points ->
    [one] punto
   *[other] puntos
} y no se permiten cantos.
trucobrazilian-desc-onze-run = Huir y abandonar la mano. El otro lado suma 1 punto.

trucobrazilian-action-accept = Aceito (aceptar)
trucobrazilian-action-decline = Correr (rechazar y huir)
trucobrazilian-accept-you = Dices Aceito a { $call }.
trucobrazilian-accept-player = { $player } dice Aceito a { $call }.
trucobrazilian-decline-you = Corres ante { $call }.
trucobrazilian-decline-player = { $player } corre ante { $call }.
trucobrazilian-pending-answer = { $player } cantó { $call }. Responde con Aceito o Correr, o sube la apuesta.
trucobrazilian-error-answer-first = Debes responder a { $call } antes de hacer otra cosa. Elige Aceito o Correr, o sube la apuesta.
trucobrazilian-error-raise-max = El Doze ya es el canto más alto y no se puede subir.
trucobrazilian-status-onze-pending = { $team } debe decidir si juega la mão de onze.
trucobrazilian-status-no-calls = En esta mano no se permiten cantos. La mano vale { $points } { $points ->
    [one] punto
   *[other] puntos
}.

# Mão de ferro (ambos lados con 11) se juega con las cartas tapadas; en la mão de onze los compañeros se ven las cartas
trucobrazilian-blind-cards = Mão de ferro: tus { $count } cartas están boca abajo y no puedes verlas. Elígelas por su posición; cada una se revela al jugarla.
trucobrazilian-blind-hand = Mão de ferro: tienes { $count } { $count ->
    [one] carta boca abajo y no puedes verla
   *[other] cartas boca abajo y no puedes verlas
}.
trucobrazilian-action-play-blind = Jugar la carta tapada { $number }
trucobrazilian-desc-blind-card = Una carta boca abajo. No la verás hasta que se juegue.
trucobrazilian-onze-partner-cards = Tu compañero { $partner } te muestra sus cartas: { $cards }.
