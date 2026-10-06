game-name-skipbo = Skip-Bo

skipbo-stock-mode-standard = Padrão (30 ou 20 cartas)
skipbo-stock-mode-short = Rápido com 10 cartas
skipbo-stock-mode-short-15 = Rápido com 15 cartas
skipbo-scoring-single = Partida única
skipbo-scoring-match = Série pontuada

skipbo-set-stock-mode = Pilhas de reserva: { $mode }
skipbo-select-stock-mode = Escolha o tamanho das pilhas de reserva:
skipbo-option-changed-stock-mode = As pilhas de reserva agora usam { $mode }.
skipbo-desc-stock-mode = O modo Padrão usa 30 cartas de reserva com 2 a 4 jogadores e 20 com 5 ou 6. Partidas rápidas usam 10 ou 15 cartas de reserva para cada jogador.

skipbo-set-scoring-mode = Formato da série: { $mode }
skipbo-select-scoring-mode = Escolha o formato da série:
skipbo-option-changed-scoring-mode = O formato da série agora é { $mode }.
skipbo-desc-scoring-mode = Partida única termina quando um jogador ou uma equipe esvazia suas pilhas de reserva. Série pontuada continua por várias partidas até alguém alcançar a pontuação-alvo.

skipbo-set-winning-score = Objetivo da série: { $score } pontos
skipbo-enter-winning-score = Digite o objetivo da série, de 25 a 5000 pontos:
skipbo-option-changed-winning-score = O objetivo da série agora é de { $score } pontos.
skipbo-desc-winning-score = Pontos necessários para vencer uma série pontuada. O objetivo oficial é de 500 pontos.
skipbo-desc-team-mode = Individual dá a cada jogador uma pilha de reserva e uma pontuação separadas. As equipes oficiais têm dois integrantes; cada parceiro pode jogar das pilhas de reserva e de descarte de ambos, mas nunca da mão do outro.

skipbo-card-number = { $value }
skipbo-card-wild = Curinga Skip-Bo
skipbo-card-wild-as = Skip-Bo como { $value }

skipbo-source-your-hand = sua mão
skipbo-source-player-hand = mão de { $owner }
skipbo-source-your-stock = sua pilha de reserva
skipbo-source-player-stock = pilha de reserva de { $owner }
skipbo-source-your-discard = sua pilha de descarte { $pile }
skipbo-source-player-discard = pilha de descarte { $pile } de { $owner }

skipbo-action-source-hand = mão
skipbo-action-source-stock = reserva
skipbo-action-source-player-stock = reserva de { $owner }
skipbo-action-source-discard = pilha de descarte { $pile }
skipbo-action-source-player-discard = pilha de descarte { $pile } de { $owner }

skipbo-play-action = { $card } — { $source } para a pilha { $pile }
skipbo-card-action = { $card } — { $source }
skipbo-card-desc-play-or-discard = Pilhas de construção disponíveis: { $piles }. Escolha a carta para jogá-la ou descartá-la e encerrar sua vez.
skipbo-card-desc-discard-only = Escolha a carta para descartá-la e encerrar sua vez.
skipbo-card-desc-choose-building = Pilhas de construção disponíveis: { $piles }. Escolha a carta para selecionar uma delas.
skipbo-end-turn-empty = Encerrar vez sem descartar
skipbo-end-turn-empty-desc = Sua mão está vazia e não há cartas para comprar, então não é possível descartar.
skipbo-select-card-move = Escolha para onde mover esta carta:
skipbo-move-building-empty = Pilha de construção { $pile}: vazia; jogar { $card }
skipbo-move-building-top = Pilha de construção { $pile}: { $current } no topo; jogar { $card }
skipbo-move-discard-empty = Pilha de descarte { $pile}: vazia; descartar aqui e encerrar a vez
skipbo-move-discard-top = Pilha de descarte { $pile}: { $top } no topo; descartar aqui e encerrar a vez

skipbo-read-building-piles = Ver pilhas de construção
skipbo-read-stock-piles = Ver pilhas de reserva
skipbo-read-own-discard-piles = Ver suas pilhas de descarte
skipbo-read-discard-piles = Ver pilhas de descarte de outro jogador
skipbo-select-discard-owner = Escolha de quem deseja ver as pilhas de descarte:

skipbo-game-start = A partida começa. Cada pilha de reserva tem { $stock_count } cartas.
skipbo-game-start-quick = A partida rápida começa. Cada pilha de reserva tem { $stock_count } cartas.
skipbo-match-game-start = Começa a partida pontuada { $game }. Cada pilha de reserva tem { $stock_count } cartas.
skipbo-match-game-start-quick = Começa a partida rápida pontuada { $game }. Cada pilha de reserva tem { $stock_count } cartas.
skipbo-initial-stock-you = Sua carta de reserva virada para cima é { $card }.
skipbo-initial-stock-player = A carta de reserva virada para cima de { $player } é { $card }.
skipbo-draw-turn-you = Você compra { $count } { $count ->
    [one] carta
   *[other] cartas
} para começar sua vez. Sua mão é { $hand }.
skipbo-draw-turn-player = { $player } compra { $count } { $count ->
    [one] carta
   *[other] cartas
} para começar sua vez.
skipbo-refill-you = Você usou todas as cartas da sua mão, então compra imediatamente { $count } { $count ->
    [one] carta
   *[other] cartas
}. Sua mão é { $hand }.
skipbo-refill-player = { $player } usou todas as cartas da própria mão e compra imediatamente { $count } { $count ->
    [one] carta
   *[other] cartas
}.
skipbo-no-refill-you = Sua mão está vazia e não há cartas disponíveis para comprar.
skipbo-no-refill-player = { $player } está com a mão vazia, mas não há cartas disponíveis para comprar.
skipbo-recycle-completed = A pilha de compra está vazia. As pilhas de construção concluídas são embaralhadas para formar uma nova pilha de compra com { $count } cartas.

skipbo-play-you = Você joga { $card } de { $source } na pilha de construção { $pile }.
skipbo-play-player = { $player } joga { $card } de { $source } na pilha de construção { $pile }.
skipbo-complete-building-you = Você completa a pilha de construção { $pile } com o 12. As cartas são separadas para serem reembaralhadas, e o espaço de construção volta a ficar vazio.
skipbo-complete-building-player = { $player } completa a pilha de construção { $pile } com o 12. As cartas são separadas para serem reembaralhadas, e o espaço de construção volta a ficar vazio.
skipbo-next-stock-you = Sua próxima carta de reserva virada para cima é { $card }; { $count ->
    [one] resta { $count } carta
   *[other] restam { $count } cartas
} na sua pilha de reserva.
skipbo-next-stock-player = A próxima carta de reserva virada para cima de { $player } é { $card }; { $count ->
    [one] resta { $count } carta
   *[other] restam { $count } cartas
} nessa pilha de reserva.
skipbo-stock-cleared-you = Sua pilha de reserva agora está vazia. Sua equipe ainda precisa esvaziar a outra pilha de reserva.
skipbo-stock-cleared-player = A pilha de reserva de { $player } agora está vazia. A equipe ainda precisa esvaziar sua outra pilha de reserva.
skipbo-discard-you = Você descarta { $card } na pilha de descarte { $pile } e encerra sua vez.
skipbo-discard-player = { $player } descarta { $card } na pilha de descarte { $pile } e encerra sua vez.
skipbo-empty-end-you = Você não tem nenhuma carta disponível para descartar, então encerra sua vez sem fazer um descarte.
skipbo-empty-end-player = { $player } não tem nenhuma carta disponível para descartar e encerra sua vez sem fazer um descarte.

skipbo-single-win-you = Você esvazia sua pilha de reserva e vence a partida.
skipbo-single-win-player = { $player } esvazia a própria pilha de reserva e vence a partida.
skipbo-single-win-team-you = Sua equipe esvazia as duas pilhas de reserva e vence a partida.
skipbo-single-win-team = A equipe { $team } esvazia as duas pilhas de reserva e vence a partida.
skipbo-scored-game-win-you = Você esvazia sua pilha de reserva e vence a partida pontuada { $game }, ganhando { $points } pontos com { $remaining } cartas restantes nas pilhas de reserva adversárias. Seu total na série é { $total }.
skipbo-scored-game-win-player = { $player } esvazia a própria pilha de reserva e vence a partida pontuada { $game }, ganhando { $points } pontos com { $remaining } cartas restantes nas pilhas de reserva adversárias. O total na série é { $total }.
skipbo-scored-game-win-team-you = Sua equipe esvazia as duas pilhas de reserva e vence a partida pontuada { $game }, ganhando { $points } pontos com { $remaining } cartas restantes nas pilhas de reserva adversárias. Seu total na série é { $total }.
skipbo-scored-game-win-team = A equipe { $team } esvazia as duas pilhas de reserva e vence a partida pontuada { $game }, ganhando { $points } pontos com { $remaining } cartas restantes nas pilhas de reserva adversárias. O total da equipe na série é { $total }.
skipbo-next-round = A próxima partida pontuada começará em breve. A posição inicial avança um assento.
skipbo-match-win-you = Você vence a série de Skip-Bo com { $score } pontos.
skipbo-match-win-player = { $player } vence a série de Skip-Bo com { $score } pontos.
skipbo-match-win-team-you = Sua equipe vence a série de Skip-Bo com { $score } pontos.
skipbo-match-win-team = A equipe { $team } vence a série de Skip-Bo com { $score } pontos.

skipbo-building-empty = Pilha de construção { $pile }: vazia; precisa de 1.
skipbo-building-top = Pilha de construção { $pile }: { $value } no topo; precisa de { $needed }.
skipbo-draw-count = Pilha de compra: { $draw_count } cartas. Cartas de construção concluídas aguardando para serem reembaralhadas: { $recycle_count }.
skipbo-stock-empty = Pilha de reserva de { $player }: vazia.
skipbo-stock-status = Pilha de reserva de { $player }: { $card } virada para cima, { $count } { $count ->
    [one] carta no total
   *[other] cartas no total
}.
skipbo-discard-your-header = Suas pilhas de descarte:
skipbo-discard-player-header = Pilhas de descarte de { $player }:
skipbo-discard-empty = Pilha de descarte { $pile }: vazia.
skipbo-discard-top = Pilha de descarte { $pile }: { $card } no topo, { $count } { $count ->
    [one] carta no total
   *[other] cartas no total
}.
skipbo-hand-empty = Você ainda não tem cartas na mão.
skipbo-hand-menu-card = Mão: { $card }

skipbo-error-invalid-stock-mode = O tamanho selecionado para as pilhas de reserva não é compatível. Escolha Padrão, Rápido com 10 ou Rápido com 15.
skipbo-error-invalid-scoring-mode = O formato de série selecionado não é compatível. Escolha Partida única ou Série pontuada.
skipbo-error-winning-score-range = O objetivo da série deve estar entre { $min } e { $max } pontos; o valor atual é { $value }.
skipbo-error-partnership-player-count = O modo de equipes exige exatamente 4 jogadores para duas equipes ou 6 jogadores para três equipes.
skipbo-error-game-not-active = Esta partida de Skip-Bo não está ativa no momento.
skipbo-error-round-transition = A partida atual terminou. Aguarde o início da próxima.
skipbo-error-card-move-selection-you = Primeiro escolha para onde mover a carta selecionada.
skipbo-error-play-changed = Essa jogada não está mais disponível porque a carta ou a pilha de construção mudou. Escolha uma ação atual do menu da vez.
skipbo-error-card-changed = Essa carta não está mais disponível. Escolha uma ação atual do menu da vez.
skipbo-error-cards-available = Você ainda tem uma carta disponível para descartar. Encerre sua vez escolhendo essa carta e uma das suas quatro pilhas de descarte.
skipbo-error-no-discard-targets = Não há pilhas de descarte de outros jogadores disponíveis.
skipbo-error-discard-target-changed = As pilhas de descarte desse jogador não estão mais disponíveis. Escolha um jogador atual.
skipbo-discard-owner-unavailable = Jogador não está mais disponível

skipbo-result-line = { $rank }. { $player }: { $points }
