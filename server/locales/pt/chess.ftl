game-name-chess = Xadrez

chess-set-time-control = Controle de tempo: { $control }
chess-select-time-control = Escolher um controle de tempo
chess-option-changed-time-control = Controle de tempo definido para { $control }.
chess-desc-time-control = Escolhe o relógio de xadrez, desde partidas sem relógio até bullet, blitz, rapid ou classical.
chess-time-untimed = Sem relógio
chess-time-bullet-1-0 = Bullet 1+0
chess-time-bullet-2-1 = Bullet 2+1
chess-time-blitz-3-0 = Blitz 3+0
chess-time-blitz-3-2 = Blitz 3+2
chess-time-blitz-5-0 = Blitz 5+0
chess-time-rapid-10-0 = Rapid 10+0
chess-time-rapid-10-5 = Rapid 10+5
chess-time-classical-30-0 = Classical 30+0

chess-set-draw-handling = Tratamento de empate: { $mode }
chess-select-draw-handling = Escolher tratamento de empate
chess-option-changed-draw-handling = Tratamento de empate definido para { $mode }.
chess-desc-draw-handling = Escolhe se as regras automáticas de empate terminam o jogo imediatamente ou exigem que um jogador reivindique o empate.
chess-draw-handling-automatic = Automático
chess-draw-handling-claim-required = Reivindicação obrigatória

chess-toggle-draw-offers = Permitir ofertas de empate: { $enabled }
chess-option-changed-draw-offers = Permitir ofertas de empate definido para { $enabled }.
chess-desc-allow-draw-offers = Controla se os jogadores podem oferecer e responder a empates em comum acordo.
chess-toggle-undo-requests = Permitir pedidos de desfazer: { $enabled }
chess-option-changed-undo-requests = Permitir pedidos de desfazer definido para { $enabled }.
chess-desc-allow-undo-requests = Controla se os jogadores podem solicitar reversões de lances que o oponente pode aceitar ou recusar.
chess-error-invalid-time-control = O controle de tempo selecionado "{ $control }" não é suportado no Xadrez.
chess-error-invalid-draw-handling = O modo de tratamento de empate selecionado "{ $mode }" não é suportado no Xadrez.

chess-read-board = Ler tabuleiro
chess-check-status = Verificar status
chess-flip-board = Virar tabuleiro
chess-check-clock = Verificar relógio
chess-claim-draw = Reivindicar empate
chess-offer-draw = Oferecer empate
chess-accept-draw = Aceitar empate
chess-decline-draw = Recusar empate
chess-request-undo = Solicitar desfazer
chess-accept-undo = Aceitar desfazer
chess-decline-undo = Recusar desfazer
chess-type-move = Digitar lance
chess-enter-move = Digite seu lance, como e2e4, Nf3, O-O ou e8=Q

chess-promote-queen = Promover a dama
chess-promote-rook = Promover a torre
chess-promote-bishop = Promover o bispo
chess-promote-knight = Promover o cavalo

chess-color-white = branco
chess-color-black = preto

chess-piece-pawn = peão
chess-piece-knight = cavalo
chess-piece-bishop = bispo
chess-piece-rook = torre
chess-piece-queen = dama
chess-piece-king = rei
chess-piece-with-color = { $color } { $piece }

chess-square-empty-label = { $square }, vazio
chess-square-piece-label = { $square }, { $piece }
chess-square-selected-label = selecionado, { $label }
chess-square-move-target = { $square }, lance válido
chess-square-capture-target = { $square }, capturar { $piece }
chess-square-empty = { $square } está vazio.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = Selecione uma de suas próprias peças primeiro.
chess-piece-no-legal-moves = Essa peça não possui lances legais.
chess-piece-selected = { $piece } selecionado em { $square }. { $count } lances legais disponíveis.
chess-selection-cleared = Seleção limpa.
chess-illegal-move = Lance ilegal.
chess-invalid-castle = O roque não é legal nessa posição.
chess-promotion-pending = Escolha uma peça para promoção primeiro.
chess-choose-promotion = Escolha uma peça de promoção.
chess-typed-move-empty = Digite um lance antes de enviar.
chess-typed-move-parse-error = Não foi possível entender "{ $move }" como um lance de xadrez. Tente notação de coordenadas como e2e4, notação algébrica como Nf3, roque como O-O ou promoção como e8=Q.
chess-typed-move-ambiguous = "{ $move }" corresponde a mais de um lance legal. Adicione a coluna de origem, fileira ou a casa de origem completa, como Nbd2 ou Rae1.
chess-typed-move-illegal = "{ $move }" não é legal na posição atual.
chess-typed-move-bad-promotion = "{ $move }" inclui uma peça de promoção, mas a promoção só funciona quando um dos seus peões chega à última fileira. Use dama, torre, bispo ou cavalo.

chess-game-started = O xadrez começa. { $white } joga de brancas. { $black } joga de pretas.
chess-you-win-checkmate = Xeque-mate. Você venceu.
chess-player-wins-checkmate = Xeque-mate. { $player } vence.
chess-draw = Empate.
chess-draw-stalemate = Empate por afogamento.
chess-draw-fifty-move = Empate pela regra dos cinquenta lances.
chess-draw-seventy-five-move = Empate pela regra obrigatória dos setenta e cinco lances.
chess-draw-threefold = Empate por tripla repetição.
chess-draw-fivefold = Empate por repetição quíntupla obrigatória.
chess-draw-insufficient-material = Empate por material insuficiente.
chess-draw-agreement = Empate por acordo.
chess-draw-timeout-insufficient = Empate. O oponente estourou o tempo, mas não havia material suficiente para dar xeque-mate.
chess-you-are-in-check = Seu rei está em xeque.
chess-player-is-in-check = O rei de { $player } está em xeque.
chess-you-lose-on-time = Seu tempo acabou. { $winner } vence por tempo.
chess-player-loses-on-time = O tempo de { $player } acabou. { $winner } vence por tempo.

chess-you-en-passant = Você move seu { $piece } de { $from_square } para { $to_square } e captura en passant.
chess-player-en-passant = { $player } move seu { $piece } de { $from_square } para { $to_square } e captura en passant.
chess-you-en-passant-brief = Você { $from_square } x { $to_square } e.p.
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } e.p.
chess-you-capture = Você move seu { $piece } de { $from_square } para { $to_square }, capturando o { $captured_piece }.
chess-player-captures = { $player } move seu { $piece } de { $from_square } para { $to_square }, capturando o { $captured_piece }.
chess-you-capture-brief = Você { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = Você faz o roque pelo lado do rei.
chess-player-castles-kingside = { $player } faz o roque pelo lado do rei.
chess-you-castle-kingside-brief = Você O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = Você faz o roque pelo lado da dama.
chess-player-castles-queenside = { $player } faz o roque pelo lado da dama.
chess-you-castle-queenside-brief = Você O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = Você move seu { $piece } de { $from_square } para { $to_square }.
chess-player-moves = { $player } move seu { $piece } de { $from_square } para { $to_square }.
chess-you-move-brief = Você { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = Você promove em { $square }.
chess-player-promotes = { $player } promove em { $square }.
chess-you-promote-to = Você promove o peão em { $square } a { $piece }.
chess-player-promotes-to = { $player } promove o peão em { $square } a { $piece }.
chess-you-promote-to-brief = Você promove { $square } para { $piece }.
chess-player-promotes-to-brief = { $player } promove { $square } para { $piece }.
chess-you-offer-draw = Você oferece um empate.
chess-player-offers-draw = { $player } oferece um empate.
chess-you-accept-draw = Você aceita o empate.
chess-player-accepts-draw = { $player } aceita o empate.
chess-you-decline-draw = Você recusa o empate.
chess-player-declines-draw = { $player } recusa o empate.
chess-you-request-undo = Você solicita desfazer.
chess-player-requests-undo = { $player } solicita desfazer.
chess-you-accept-undo = Você aceita o pedido de desfazer.
chess-player-accepts-undo = { $player } aceita o pedido de desfazer.
chess-you-decline-undo = Você recusa o pedido de desfazer.
chess-player-declines-undo = { $player } recusa o pedido de desfazer.
chess-draw-offer-too-early = Ofertas de empate só estão disponíveis após ambos os jogadores terem feito pelo menos um lance.
chess-claim-available-fifty-move = O empate por cinquenta lances pode ser reivindicado agora.
chess-claim-available-threefold = O empate por tripla repetição pode ser reivindicado agora.
chess-you-claim-draw-fifty-move = Você reivindica um empate pela regra dos cinquenta lances.
chess-draw-claimed-fifty-move = { $player } reivindica um empate pela regra dos cinquenta lances.
chess-you-claim-draw-threefold = Você reivindica um empate por tripla repetição.
chess-draw-claimed-threefold = { $player } reivindica um empate por tripla repetição.

chess-status-white = Brancas: { $player }
chess-status-black = Pretas: { $player }
chess-status-turn = Turno: { $color } ({ $player })
chess-status-move-count = Lances completos jogados: { $count }. Meios-lances jogados: { $plies }.
chess-status-promotion-pending = Há uma escolha de promoção pendente.
chess-status-check = O lado da vez está em xeque.
chess-status-time-control = Controle de tempo: { $control }
chess-status-draw-offer = Oferta de empate aguardando de { $player }.
chess-status-undo-request = Pedido de desfazer aguardando de { $player }.
chess-clock-line = Relógio das { $color }: { $time }
chess-clock-untimed = ilimitado
chess-clock-announcement = Brancas: { $white }. Pretas: { $black }.
chess-clock-announcement-untimed = Esta partida não tem tempo limite.

chess-board-flipped = Tabuleiro virado para o lado { $color }.
chess-empty = vazio
chess-board-rank-line = Fileira { $rank }: { $pieces }

chess-end-winner = { $player } vence como { $color }.
chess-end-move-count = Lances completos jogados: { $count }. Meios-lances jogados: { $plies }.
