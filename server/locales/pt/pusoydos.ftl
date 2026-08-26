game-name-pusoydos = Pusoy Dos

# =============================================================================
# =============================================================================


# =============================================================================
# Option labels and prompts
# =============================================================================

pusoydos-set-game-mode = Modo de Jogo: { $choice }
pusoydos-select-game-mode = Selecione o modo de jogo:
pusoydos-option-changed-game-mode = Modo de jogo definido para { $choice }.
pusoydos-desc-game-mode = Eliminação: vença rodadas para sair, o último jogador é o perdedor. Derrotas: os últimos colocados acumulam faltas, o primeiro a atingir o limite perde. Pontos: o vencedor da rodada coleta pontos de penalidade dos perdedores, o primeiro a atingir o alvo vence. Eliminação por Pontos: os perdedores coletam seus próprios pontos de penalidade, atingiu o limite está fora, o último sobrevivente vence.

pusoydos-mode-elimination = Eliminação
pusoydos-mode-losses = Derrotas
pusoydos-mode-points = Pontos
pusoydos-mode-points-elimination = Eliminação por Pontos

pusoydos-set-rounds-to-win = Rodadas para Vencer: { $count }
pusoydos-enter-rounds-to-win = Insira as rodadas necessárias para ser eliminado (mín: 1, máx: 10):
pusoydos-option-changed-rounds-to-win = Rodadas para vencer definidas para { $count }.
pusoydos-desc-rounds-to-win = Apenas no modo Eliminação: quantas rodadas um jogador deve vencer antes de deixar o jogo como vencedor (padrão 2, intervalo de 1 a 10).

pusoydos-set-losses-to-lose = Derrotas para Perder: { $count }
pusoydos-enter-losses-to-lose = Insira as derrotas necessárias para perder (mín: 1, máx: 10):
pusoydos-option-changed-losses-to-lose = Derrotas para perder definidas para { $count }.
pusoydos-desc-losses-to-lose = Apenas no modo Derrotas: quantas vezes um jogador pode ficar em último lugar antes de perder o jogo (padrão 3, intervalo de 1 a 10).

pusoydos-set-target-score = Pontuação Alvo: { $score }
pusoydos-enter-target-score = Insira a pontuação alvo (mín: 10, máx: 10000):
pusoydos-option-changed-target-score = Pontuação alvo definida para { $score }.
pusoydos-desc-target-score = Apenas nos modos de Pontos: limite de pontuação para vencer no modo Pontos, ou eliminação no modo Eliminação por Pontos (padrão 100, intervalo de 10 a 10000).

pusoydos-set-turn-timer = Temporizador de Turno: { $choice }
pusoydos-select-turn-timer = Selecione a duração do temporizador de turno:
pusoydos-option-changed-turn-timer = Temporizador de turno definido para { $choice }.
pusoydos-desc-turn-timer = Limite de tempo por turno: Ilimitado, 10, 15, 20, 30, 45, 60 ou 90 segundos (padrão Ilimitado).

pusoydos-timer-10 = 10 Segundos
pusoydos-timer-15 = 15 Segundos
pusoydos-timer-20 = 20 Segundos
pusoydos-timer-30 = 30 Segundos
pusoydos-timer-45 = 45 Segundos
pusoydos-timer-60 = 60 Segundos
pusoydos-timer-90 = 90 Segundos
pusoydos-timer-unlimited = Ilimitado

pusoydos-set-allow-2-in-straights = Permitir 2 em Sequências: { $enabled }
pusoydos-option-changed-allow-2-in-straights = Permitir 2 em sequências definido para { $enabled }.
pusoydos-desc-allow-2-in-straights = Se o 2 pode ser usado em sequências (ex: A-2-3-4-5).

pusoydos-set-instant-wins = Vitórias Instantâneas: { $enabled }
pusoydos-option-changed-instant-wins = Vitórias instantâneas definidas para { $enabled }.
pusoydos-desc-instant-wins = Se mãos distribuídas especiais (Dragão, Quatro 2s, Seis Pares) vencem a rodada instantaneamente. Isso não pode ser combinado com troca de cartas.

pusoydos-set-card-passing = Troca de Cartas: { $choice }
pusoydos-select-card-passing = Selecione o modo de troca de cartas:
pusoydos-option-changed-card-passing = Troca de cartas definida para { $choice }.
pusoydos-desc-card-passing = Troca de cartas entre vencedores e perdedores após a distribuição: Desativado, Simples ou Completo. A troca completa exige exatamente 2 ou 4 jogadores, e a troca não pode ser combinada com vitórias instantâneas.

pusoydos-passing-off = Desativado
pusoydos-passing-simple = Simples (1º e último trocam 1 carta)
pusoydos-passing-full = Completo (1º/último trocam 2, 2º/3º trocam 1)

pusoydos-set-penalty-tier = Nível de Penalidade: { $choice }
pusoydos-select-penalty-tier = Selecione o nível de penalidade:
pusoydos-option-changed-penalty-tier = Nível de penalidade definido para { $choice }.
pusoydos-desc-penalty-tier = Apenas nos modos de Pontos: quão agressivamente as cartas restantes são penalizadas no final de uma rodada.

pusoydos-penalty-standard = Padrão (10+ cartas: x2, 13 cartas: x3)
pusoydos-penalty-aggressive = Agressivo (8-9: x2, 10-12: x3, 13: x4)
pusoydos-penalty-flat = Fixo (1 ponto por carta, sem multiplicador)

pusoydos-set-penalty-per-two = Penalidade por 2 na Mão: { $enabled }
pusoydos-option-changed-penalty-per-two = Penalidade por 2 na mão definida para { $enabled }.
pusoydos-desc-penalty-per-two = Apenas nos modos de Pontos: cada 2 deixado em uma mão perdedora dobra a penalidade dessa mão.

# =============================================================================
# Game flow announcements
# =============================================================================


pusoydos-new-hand = Rodada { $round }.
pusoydos-dealt = Distribuídas { $count } cartas: { $cards }.

pusoydos-you-first-player = Você tem o 3 de Paus e começa.
pusoydos-first-player = { $player } tem o 3 de Paus e começa.
pusoydos-you-first-player-lowest = Você tem a menor carta e começa.
pusoydos-first-player-lowest = { $player } tem a menor carta e começa.

# Elimination mode
pusoydos-you-eliminated = Você venceu { $count } rodadas e está fora! Bem jogado.
pusoydos-player-eliminated = { $player } venceu { $count } rodadas e está fora! Bem jogado.
pusoydos-you-last-player = Você é o último jogador restante. Fim de jogo!
pusoydos-last-player = { $player } é o último jogador restante. Fim de jogo!
pusoydos-players-remaining = Resta { $count } { $count ->
    [one] jogador
   *[other] jogadores
}.

# Losses mode
pusoydos-you-round-loser = Você termina em último e leva uma derrota! ({ $count } { $count ->
    [one] derrota
   *[other] derrotas
} no total.)
pusoydos-round-loser = { $player } termina em último e leva uma derrota! ({ $count } { $count ->
    [one] derrota
   *[other] derrotas
} no total.)
pusoydos-you-losses-game-over = Você atinge { $count } derrotas e perde o jogo!
pusoydos-losses-game-over = { $player } atinge { $count } derrotas e perde o jogo!

# Points mode
pusoydos-penalty-entry = { $points } { $points ->
    [one] ponto
   *[other] pontos
} de { $player }
pusoydos-you-penalty-summary = Você vence a rodada: { $breakdown }. ({ $gained } nesta rodada, { $total } no total.)
pusoydos-penalty-summary = { $player } vence a rodada: { $breakdown }. ({ $gained } nesta rodada, { $total } no total.)
pusoydos-you-win-round = Você vence a rodada!
pusoydos-round-winner = { $player } vence a rodada!
pusoydos-you-go-out = Você bateu!
pusoydos-player-goes-out = { $player } bateu!
pusoydos-you-points-winner = Você atinge { $score } pontos e vence o jogo!
pusoydos-points-winner = { $player } atinge { $score } pontos e vence o jogo!

# Points elimination mode
pusoydos-you-points-elim-penalty = Você recebe { $points } pontos. ({ $total } no total.)
pusoydos-points-elim-penalty = { $player } recebe { $points } pontos. ({ $total } no total.)
pusoydos-you-points-elim-eliminated = Você atinge { $score } pontos e é eliminado!
pusoydos-points-elim-eliminated = { $player } atinge { $score } pontos e é eliminado!
pusoydos-you-points-elim-winner = Você é o último jogador sobrevivente. Você vence!
pusoydos-points-elim-winner = { $player } é o último jogador sobrevivente. { $player } vence!

# Instant wins
pusoydos-you-instant-win-dragon = Você tem um Dragão (sequência de 13 cartas)! Vitória instantânea!
pusoydos-instant-win-dragon = { $player } tem um Dragão (sequência de 13 cartas)! Vitória instantânea!
pusoydos-you-instant-win-four-twos = Você tem todos os quatro 2s! Vitória instantânea!
pusoydos-instant-win-four-twos = { $player } tem todos os quatro 2s! Vitória instantânea!
pusoydos-you-instant-win-six-pairs = Você tem seis pares! Vitória instantânea!
pusoydos-instant-win-six-pairs = { $player } tem seis pares! Vitória instantânea!
pusoydos-checking-instant-wins = Verificando mãos de vitória instantânea...
pusoydos-no-instant-wins = Sem vitórias instantâneas nesta rodada.

# Card passing
pusoydos-passing-phase = Fase de troca de cartas.
pusoydos-loser-gives = { $loser } dá { $count ->
    [one] sua carta mais alta
   *[other] suas { $count } cartas mais altas
} para { $winner }.
pusoydos-winner-gives-back = { $winner } devolve { $count ->
    [one] uma carta
   *[other] { $count } cartas
} para { $loser }.
pusoydos-select-cards-to-give = Selecione { $count ->
    [one] 1 carta
   *[other] { $count } cartas
} para devolver para { $recipient }:
pusoydos-cards-exchanged = Cartas trocadas.
pusoydos-passed-cards = Você deu { $cards } para { $recipient }.
pusoydos-received-cards = Você recebeu { $cards } de { $sender }.

# =============================================================================
# Card interaction and actions
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (selecionada)

pusoydos-play-none = Selecione cartas para jogar.
pusoydos-play-invalid = Combinação inválida.
pusoydos-play-combo = Jogar { $combo }

pusoydos-pass = Passar
pusoydos-check-trick = Verificar jogada
pusoydos-read-hand = Ler mão
pusoydos-check-turn-timer = Verificar temporizador de turno
pusoydos-read-card-counts = Contagem de cartas
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] carta
   *[other] cartas
}
pusoydos-card-counts-empty = Nenhum jogador ativo tem cartas para contar.
pusoydos-timer-disabled = O temporizador de turno está desativado.
pusoydos-timer-remaining = Restam { $seconds } segundos.

# Keybind labels
pusoydos-key-play = Jogar cartas selecionadas
pusoydos-key-pass = Passar
pusoydos-key-trick = Verificar jogada atual
pusoydos-key-hand = Ler sua mão
pusoydos-key-counts = Contagem de cartas
pusoydos-key-timer = Temporizador de turno

# =============================================================================
# Errors
# =============================================================================

pusoydos-error-full-passing-players = A troca completa de cartas exige exatamente 2 ou 4 jogadores.
pusoydos-error-instant-wins-card-passing = Vitórias instantâneas e troca de cartas entram em conflito. Desative uma delas antes de iniciar o jogo.
pusoydos-error-no-cards = Você não selecionou nenhuma carta.
pusoydos-error-invalid-combo = As cartas selecionadas não formam uma combinação válida.
pusoydos-error-first-turn-3c = Você deve incluir o 3 de Paus na primeira jogada.
pusoydos-error-wrong-length = Você deve jogar exatamente { $count } { $count ->
    [one] carta
   *[other] cartas
} para superar a jogada atual.
pusoydos-error-lower-combo = Sua combinação é menor do que a jogada atual.
pusoydos-error-must-play = Você não pode passar ao iniciar uma nova jogada.
pusoydos-error-select-cards-to-give = Selecione exatamente { $count } { $count ->
    [one] carta
   *[other] cartas
} para devolver para { $recipient }.
pusoydos-error-select-required-give-cards = Selecione o número necessário de cartas antes de confirmar a troca.
pusoydos-error-eliminated = Você já está fora deste jogo.
pusoydos-confirm-pass = Use a ação de passar novamente para confirmar.

# =============================================================================
# Broadcasts
# =============================================================================

pusoydos-you-play-single = Você joga { $card }.
pusoydos-player-plays-single = { $player } joga { $card }.
pusoydos-you-play-combo = Você joga um { $combo } de { $cards }.
pusoydos-player-plays-combo = { $player } joga um { $combo } de { $cards }.
pusoydos-you-pass = Você passa.
pusoydos-player-passes = { $player } passa.
pusoydos-you-win-trick = Você vence a rodada de cartas.
pusoydos-trick-won = { $player } vence a rodada de cartas.

pusoydos-trick-empty = A mesa está vazia.
pusoydos-trick-status = { $player } jogou um { $combo } de { $cards }.
pusoydos-your-hand = Sua mão: { $cards }.

pusoydos-score-no-scores = Sem pontuações ainda.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] vitória
   *[other] vitórias
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] derrota
   *[other] derrotas
}
pusoydos-score-points = { $player }: { $score } pontos

pusoydos-you-one-card = Você tem uma carta restante!
pusoydos-one-card = { $player } tem uma carta restante!

# =============================================================================
# Combo names
# =============================================================================

pusoydos-combo-single = Carta Individual
pusoydos-combo-pair = Par
pusoydos-combo-three_of_a_kind = Trinca
pusoydos-combo-straight = Sequência
pusoydos-combo-flush = Flush
pusoydos-combo-full_house = Full House
pusoydos-combo-four_of_a_kind = Quadra
pusoydos-combo-straight_flush = Straight Flush

# Instant win hand names
pusoydos-combo-dragon = Dragão
pusoydos-combo-four_twos = Quatro 2s
pusoydos-combo-six_pairs = Seis Pares

# =============================================================================
# End screen
# =============================================================================

pusoydos-game-over = O jogo terminou! { $player } perdeu!
pusoydos-game-over-points = O jogo terminou! { $player } vence com { $score } pontos!
pusoydos-game-over-losses = O jogo terminou! { $player } perde com { $count } derrotas!
pusoydos-line-format = { $rank }. { $player }: { $score } pontos
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] vitória
   *[other] vitórias
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] derrota
   *[other] derrotas
}
