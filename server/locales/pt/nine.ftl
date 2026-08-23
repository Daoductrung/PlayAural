# Nine game messages

# Game name and description
game-name-nine = Nove
nine-description = Um jogo de cartas russo popular no qual os jogadores constroem sequências de naipes.

# Player count validation
nine-error-invalid-player-count = Nove usa um baralho de 36 cartas e acomoda exatamente 3, 4 ou 6 jogadores.
nine-error-starting-nine-missing = O nove de ouros não foi encontrado em nenhuma mão. O jogo não pode continuar.

# Dealing messages
nine-player-nine-deal = Distribuindo { $cards } cartas para cada jogador.

# Game start
nine-you-start-player-announcement = Você tem o nove de ouros e começa o jogo.
nine-player-start-player-announcement = { $player } tem o nove de ouros e começa o jogo.
nine-you-start-player-announcement-brief = Você começa com o nove de ouros.
nine-player-start-player-announcement-brief = { $player } começa com o nove de ouros.

# Turn actions
nine-you-plays-starting-nine = Você joga { $card } para abrir a mesa.
nine-player-plays-starting-nine = { $player } joga { $card } para abrir a mesa.
nine-you-plays-starting-nine-brief = Você joga { $card }.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = Você joga { $card } para iniciar a sequência de { $suit }.
nine-player-plays-nine-suit = { $player } joga { $card } para iniciar a sequência de { $suit }.
nine-you-plays-nine-suit-brief = Você inicia { $suit } com { $card }.
nine-player-plays-nine-suit-brief = { $player } inicia { $suit } com { $card }.

nine-you-extend-sequence = Você estende a sequência de { $suit } com { $card }.
nine-player-extend-sequence = { $player } estende a sequência de { $suit } com { $card }.
nine-you-extend-sequence-brief = Você joga { $card } em { $suit }.
nine-player-extend-sequence-brief = { $player }: { $card } em { $suit }.

nine-you-skips-turn = Você não tem nenhuma carta legal para jogar, então seu turno é pulado.
nine-player-skips-turn = { $player } não tem nenhuma carta legal para jogar e pula o turno.
nine-you-skips-turn-brief = Você pula; nenhuma carta legal.
nine-player-skips-turn-brief = { $player } pula; nenhuma carta legal.

# Reasons for not being able to play a card
nine-reason-not-your-turn = Não é o seu turno.
nine-reason-card-slot-gone = Essa carta não está mais na sua mão. Seu menu de mão foi atualizado.
nine-reason-must-play-starting-nine = A primeira jogada deve ser { $starting_card }. { $card } não pode ser jogada até que a mesa seja aberta.
nine-reason-nine-already-started = { $card } não pode ser jogada porque a sequência de { $suit } já está aberta.
nine-reason-cannot-extend = { $card } não pode estender a sequência de { $suit }. Jogue a próxima carta inferior ou superior em uma das pontas dessa sequência.
nine-reason-unopened-suit = { $card } não pode ser jogada porque a sequência de { $suit } ainda não foi aberta. Inicie esse naipe com o 9 dele primeiro.
nine-reason-must-skip = Você não tem nenhuma carta legal para jogar; seu turno será pulado automaticamente.
nine-reason-generic = Essa carta não pode ser jogada agora.

# Winning
nine-you-wins-game = Você não tem cartas restantes e vence o jogo!
nine-player-wins-game = { $player } não tem cartas restantes e vence o jogo!
nine-you-wins-game-brief = Você venceu!
nine-player-wins-game-brief = { $player } venceu!
nine-player-game-ended = O jogo de Nove terminou.
nine-you-game-ended = O jogo de Nove terminou.

nine-you-win = Você venceu!
nine-you-lose = Você perdeu!
nine-final-score = Cartas restantes: { $score }

# Status
nine-status = { $name }: { $cards_left } cartas restantes.
nine-status-sequence = Sequência de { $suit }: { $sequence }.
nine-status-no-sequence = Nenhuma sequência de { $suit } iniciada ainda.
nine-sequence-range = { $low } até { $high }
nine-none = nenhum
nine-action-check-sequences = Verificar Sequências
nine-action-check-hand-counts = Verificar Contagem de Mãos
nine-status-player-hand-count = { $player }: { $count } cartas
