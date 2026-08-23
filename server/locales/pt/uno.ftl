game-name-uno = UNO

# Colors
uno-color-red = Vermelho
uno-color-yellow = Amarelo
uno-color-green = Verde
uno-color-blue = Azul
uno-color-wild = Coringa

# Card names
uno-card-number = { $color } { $value }
uno-card-skip = Bloqueio { $color }
uno-card-reverse = Inversão { $color }
uno-card-draw-two = Comprar Duas { $color }
uno-card-wild = Coringa
uno-card-wild-four = Coringa Comprar Quatro

# Options
uno-set-winning-score = Limite de pontuação: { $score }
uno-enter-winning-score = Insira o limite de pontuação
uno-option-changed-winning-score = Limite de pontuação definido para { $score }.
uno-desc-winning-score = Limite de pontuação usado pelo modo de pontuação do UNO selecionado (padrão 300, intervalo de 10 a 2000).

uno-set-scoring-mode = Pontuação: { $mode }
uno-select-scoring-mode = Selecione o modo de pontuação
uno-option-changed-scoring-mode = Pontuação definida para { $mode }.
uno-desc-scoring-mode = Escolhe se o primeiro jogador a atingir o limite vence, ou se os jogadores no limite são eliminados.
uno-scoring-first = Primeiro a atingir o limite vence
uno-scoring-elimination = Eliminação

uno-set-skip-after-draw = Penalidades de compra pulam o turno: { $enabled }
uno-option-changed-skip-after-draw = Penalidades de compra pulam o turno { $enabled }.
uno-desc-skip-after-draw = Controla se as penalidades de Comprar Duas e Coringa Comprar Quatro também pulam o turno do alvo.

uno-set-responses = Empilhamento de respostas: { $enabled }
uno-option-changed-responses = Empilhamento de respostas { $enabled }.
uno-desc-responses = Permite que os jogadores empilhem cartas de compra em resposta a penalidades de Comprar Duas ou Coringa Comprar Quatro.

uno-set-advanced-responses = Respostas avançadas: { $enabled }
uno-option-changed-advanced-responses = Respostas avançadas { $enabled }.
uno-desc-advanced-responses = Permite respostas defensivas extras a pilhas de compra, como combinar cartas de Bloqueio, Inversão ou Coringa. Requer empilhamento de respostas.

uno-set-wait-for-draw-responses = Aguardar respostas de compra: { $enabled }
uno-option-changed-wait-for-draw-responses = Aguardar respostas de compra { $enabled }.
uno-desc-wait-for-draw-responses = Se a última carta cria uma pilha de compra, aguarda o próximo jogador responder ou comprar antes de pontuar a rodada. Requer empilhamento de respostas.

uno-set-bluff = Desafios de Coringa Comprar Quatro: { $enabled }
uno-option-changed-bluff = Desafios de Coringa Comprar Quatro { $enabled }.
uno-desc-bluff = Ativa as regras de desafio de Coringa Comprar Quatro para jogadas ilegais.

uno-set-straights = Sequências: { $enabled }
uno-option-changed-straights = Sequências { $enabled }.
uno-desc-straights = Permite que um jogador continue fora de turno com o número seguinte ou anterior da mesma cor após uma carta numérica.

uno-set-interceptions = Interceptações: { $enabled }
uno-option-changed-interceptions = Interceptações { $enabled }.
uno-desc-interceptions = Permite que os jogadores entrem fora de turno com uma carta de correspondência exata. Tentativas inválidas adicionam 3 pontos de penalidade.

uno-set-super-interceptions = Super interceptações: { $enabled }
uno-option-changed-super-interceptions = Super interceptações { $enabled }.
uno-desc-super-interceptions = Expande as interceptações para corresponder ao número ou símbolo de ação mesmo quando a cor difere. Requer interceptações.

uno-set-zero-seven = Regra zero / sete: { $enabled }
uno-option-changed-zero-seven = Regra zero / sete { $enabled }.
uno-desc-zero-seven-rule = Ativa a regra da casa onde o 0 rotaciona as mãos de todos e o 7 permite ao jogador trocar de mão ou recusar.

uno-set-free-draws = Compras gratuitas por turno: { $count }
uno-enter-free-draws = Insira as compras gratuitas por turno
uno-option-changed-free-draws = Compras gratuitas por turno definidas para { $count }.
uno-desc-free-draws = Quantas vezes um jogador humano pode comprar apesar de possuir uma carta jogável (padrão 0, intervalo de 0 a 999).

# Option validation
uno-error-advanced-responses-require-responses = Respostas avançadas exigem que o empilhamento de respostas esteja ativado.
uno-error-wait-responses-require-responses = Aguardar respostas de compra exige que o empilhamento de respostas esteja ativado.
uno-error-super-interceptions-require-interceptions = Super interceptações exigem que as interceptações estejam ativadas.

# Actions
uno-draw = Comprar
uno-say-uno = UNO
uno-read-top = Ler carta do topo
uno-read-color = Ler cor atual
uno-read-counts = Ler contagem de cartas
uno-read-hand = Ler valor da sua mão
uno-sort-color = Ordenar por cor
uno-sort-number = Ordenar por número

# Gameplay announcements
uno-new-hand = Rodada { $round }.
uno-start-card = { $player } revela { $card }.
uno-you-start-card = Você revela { $card }.
uno-current-color = Cor atual: { $color }.
uno-dealt-cards = Todos recebem { $cards } cartas.
uno-choose-opening-color-you = Escolha a cor inicial.
uno-choose-opening-color-player = { $player } deve escolher a cor inicial.
uno-direction-reversed = A direção foi invertida.
uno-player-plays = { $player } joga { $card }.
uno-you-play = Você joga { $card }.
uno-player-chooses-color = { $player } escolhe { $color }.
uno-you-choose-color = Você escolhe { $color }.
uno-player-draws-one = { $player } compra uma carta.
uno-player-draws-many = { $player } compra { $count } cartas.
uno-you-draw-one = Você compra uma carta.
uno-you-draw-many = Você compra { $count } cartas.
uno-cant-play = { $player } não pode jogar.
uno-you-cant-play = Você não pode jogar.
uno-you-skipped = Você foi pulado.
uno-says-uno = { $player } diz UNO!
uno-you-say-uno = Você diz UNO!
uno-callout = { $caller } chama a atenção de { $player } por não dizer UNO! { $player } compra { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-you-callout = Você chama a atenção de { $player } por não dizer UNO! { $player } compra { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-callout-you = { $caller } chama a sua atenção por não dizer UNO! Você compra { $count } { $count ->
    [one] carta
   *[other] cartas
}.
uno-error-already-said-uno = Você já disse UNO.
uno-error-no-uno-call = Nenhuma chamada de UNO está disponível no momento.
uno-cannot-play-that = Você não pode jogar { $card }. { $reason }
uno-reshuffle = Reembaralhando a pilha de descarte.
uno-hand-blocked = Ninguém pode jogar. A rodada termina.
uno-error-choose-color-first = Escolha uma cor para sua carta Coringa antes de jogar outra carta.
uno-error-wait-color-choice = Aguarde o jogador da carta Coringa escolher uma cor antes de jogar.
uno-error-wild-transition = Aguarde a cor escolhida entrar em vigor antes de jogar outra carta.
uno-error-choose-swap-first = Escolha um alvo de troca de mão ou recuse antes de realizar outra ação.
uno-error-wait-swap-choice = Aguarde a escolha de troca de mão do sete terminar antes de jogar.
uno-error-wait-next-hand = Aguarde a próxima rodada começar antes de jogar uma carta.
uno-error-wait-intro = Aguarde a configuração da rodada terminar antes de jogar uma carta.
uno-reason-draw-stack-response = Há uma pilha de compra de { $count } { $count ->
    [one] carta
   *[other] cartas
} contra você; jogue uma carta de resposta válida ou compre a penalidade.
uno-reason-draw-stack-no-response = Há uma penalidade de compra de { $count } { $count ->
    [one] carta
   *[other] cartas
} contra você, e o empilhamento de respostas está desativado; compre a penalidade.
uno-reason-match-required = A carta do topo é { $top } e a cor ativa é { $color }; combine a cor, combine o número ou símbolo de ação, ou jogue uma carta Coringa.
uno-reason-card-not-available = Essa carta não está disponível no estado atual.

# Bluff challenge
uno-bluff-challenge = Desafiar Coringa Comprar Quatro
uno-bluff-caught = { $player } jogou um Coringa Comprar Quatro ilegal e compra { $count } cartas!
uno-you-bluff-caught = Você jogou um Coringa Comprar Quatro ilegal e compra { $count } cartas!
uno-bluff-wrong = { $player } desafiou o Coringa Comprar Quatro incorretamente e compra { $count } cartas!
uno-you-bluff-wrong = Você desafiou o Coringa Comprar Quatro incorretamente e compra { $count } cartas!

# Zero / seven rule
uno-rotate-hands = Todos passam suas mãos!
uno-swap-hands = { $player } troca de mão com { $target }!
uno-you-swap = Você troca de mão com { $target }!
uno-swap-with-you = { $player } troca de mão com você!
uno-swap-with = Trocar de mão com { $player }
uno-choose-swap = Escolha um jogador para trocar de mão, ou recuse.
uno-swap-none = Não trocar
uno-you-swap-none = Você mantém sua mão.
uno-swap-none-other = { $player } mantém sua mão.

# Interceptions / straights
uno-player-intercepts = { $player } intercepta com { $card }!
uno-you-intercept = Você intercepta com { $card }!
uno-bad-intercept = Interceptação inválida. { $points } pontos de penalidade.
uno-not-your-turn = Não é o seu turno.

# Info
uno-no-top = Ainda não há carta no topo.
uno-top-card = { $card }.
uno-color-is = { $color }.
uno-count-you = Você { $count }
uno-count-player = { $player } { $count }
uno-deck-count = baralho { $count }
uno-sorting-color = Ordenando por cor.
uno-sorting-number = Ordenando por número.

# Round / game end
uno-round-winner = { $player } vence a rodada!
uno-you-win-round = Você vence a rodada!
uno-round-points-from = { $points } de { $player }
uno-round-points-from-you = { $points } de você
uno-round-points-from-with-interception = { $points } de { $player } ({ $hand_points } da mão + { $penalty } de penalidade por interceptação)
uno-round-points-from-you-with-interception = { $points } de você ({ $hand_points } da mão + { $penalty } de penalidade por interceptação)
uno-round-details-none = Nenhum ponto foi tirado dos oponentes.
uno-round-summary = { $details }. { $player } ganha { $total }.
uno-round-summary-you = { $details }. Você ganha { $total }.
uno-you-add-penalty-points = Você adiciona { $points } pontos de penalidade ao seu total para esta rodada.
uno-player-adds-penalty-points = { $player } adiciona { $points } pontos de penalidade ao total deles para esta rodada.
uno-you-add-penalty-points-with-interception = Você adiciona { $points } pontos de penalidade ao seu total para esta rodada ({ $hand_points } da sua mão mais { $penalty } de penalidade por interceptação).
uno-player-adds-penalty-points-with-interception = { $player } adiciona { $points } pontos de penalidade ao total deles para esta rodada ({ $hand_points } da mão deles mais { $penalty } de penalidade por interceptação).
uno-you-are-eliminated = Você atingiu o limite de eliminação de { $limit } pontos e está fora do jogo.
uno-player-is-eliminated = { $player } atingiu o limite de eliminação de { $limit } pontos e está fora do jogo.
uno-you-win-game =
    { $mode ->
        [elimination] Você é o último jogador restante e vence com { $score } pontos de penalidade.
       *[first_to_limit] Você vence o jogo com { $score } pontos!
    }
uno-player-wins-game =
    { $mode ->
        [elimination] { $player } é o último jogador restante e vence com { $score } pontos de penalidade.
       *[first_to_limit] { $player } vence o jogo com { $score } pontos!
    }
uno-game-tie = Todos foram eliminados. O jogo terminou empatado!
uno-line-format = { $rank }. { $player }: { $score }
uno-score-line-first = { $player }: { $score }/{ $target } pontos.
uno-score-line-elimination = { $player }: { $score }/{ $target } pontos de penalidade.

# Hand value (d key)
uno-read-hand-value = { $count ->
    [one] { $count } carta
   *[other] { $count } cartas
  } no valor de { $points ->
    [one] { $points } ponto
   *[other] { $points } pontos
  }.
