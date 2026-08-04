# Nine game messages

# Game name and description
game-name-nine = Nueve
nine-description = Un popular juego de cartas ruso en el que los jugadores construyen secuencias por palo.

# Player count validation
nine-error-invalid-player-count = Nueve usa una baraja de 36 cartas y admite exactamente 3, 4 o 6 jugadores.
nine-error-starting-nine-missing = No se encontró el nueve de diamantes en ninguna mano. La partida no puede continuar.

# Dealing messages
nine-player-nine-deal = Repartiendo { $cards } cartas a cada jugador.

# Game start
nine-you-start-player-announcement = Tienes el nueve de diamantes y empiezas la partida.
nine-player-start-player-announcement = { $player } tiene el nueve de diamantes y empieza la partida.
nine-you-start-player-announcement-brief = Empiezas con el nueve de diamantes.
nine-player-start-player-announcement-brief = { $player } empieza con el nueve de diamantes.

# Turn actions
nine-you-plays-starting-nine = Juegas el { $card } para abrir la mesa.
nine-player-plays-starting-nine = { $player } juega el { $card } para abrir la mesa.
nine-you-plays-starting-nine-brief = Juegas { $card }.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = Juegas el { $card } para iniciar la secuencia de { $suit }.
nine-player-plays-nine-suit = { $player } juega el { $card } para iniciar la secuencia de { $suit }.
nine-you-plays-nine-suit-brief = Inicias { $suit } con { $card }.
nine-player-plays-nine-suit-brief = { $player } inicia { $suit } con { $card }.

nine-you-extend-sequence = Extiendes la secuencia de { $suit } con el { $card }.
nine-player-extend-sequence = { $player } extiende la secuencia de { $suit } con el { $card }.
nine-you-extend-sequence-brief = Juegas { $card } en { $suit }.
nine-player-extend-sequence-brief = { $player }: { $card } en { $suit }.

nine-you-skips-turn = No tienes ninguna carta legal para jugar, así que se salta tu turno.
nine-player-skips-turn = { $player } no tiene ninguna carta legal para jugar y se salta su turno.
nine-you-skips-turn-brief = Te saltas; sin carta legal.
nine-player-skips-turn-brief = { $player } se salta; sin carta legal.

# Reasons for not being able to play a card
nine-reason-not-your-turn = No es tu turno.
nine-reason-card-slot-gone = Esa carta ya no está en tu mano. Se actualizó el menú de tu mano.
nine-reason-must-play-starting-nine = La primera jugada debe ser el { $starting_card }. { $card } no se puede jugar hasta que se abra la mesa.
nine-reason-nine-already-started = { $card } no se puede jugar porque la secuencia de { $suit } ya está abierta.
nine-reason-cannot-extend = { $card } no puede extender la secuencia de { $suit }. Juega la siguiente carta menor o mayor en uno de los extremos de esa secuencia.
nine-reason-unopened-suit = { $card } no se puede jugar porque la secuencia de { $suit } aún no se ha abierto. Primero inicia ese palo con su 9.
nine-reason-must-skip = No tienes ninguna carta legal para jugar; tu turno se saltará automáticamente.
nine-reason-generic = Esa carta no se puede jugar en este momento.

# Winning
nine-you-wins-game = ¡Te quedaste sin cartas y ganas la partida!
nine-player-wins-game = ¡{ $player } se quedó sin cartas y gana la partida!
nine-you-wins-game-brief = ¡Ganaste!
nine-player-wins-game-brief = ¡{ $player } gana!
nine-player-game-ended = La partida de Nueve ha terminado.
nine-you-game-ended = La partida de Nueve ha terminado.

nine-you-win = ¡Ganaste!
nine-you-lose = ¡Perdiste!
nine-final-score = Cartas restantes: { $score }

# Status
nine-status = { $name }: { $cards_left } cartas restantes.
nine-status-sequence = Secuencia de { $suit }: { $sequence }.
nine-status-no-sequence = Aún no se ha iniciado la secuencia de { $suit }.
nine-sequence-range = { $low } a { $high }
nine-none = ninguna
nine-action-check-sequences = Ver secuencias
nine-action-check-hand-counts = Ver cantidad de cartas por jugador
nine-status-player-hand-count = { $player }: { $count } cartas
