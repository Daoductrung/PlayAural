game-name-tradeoff = Intercâmbio

tradeoff-round-start = Rodada { $round }.
tradeoff-iteration = Mão { $iteration } de 3.

tradeoff-you-rolled = Você tirou: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = trocando
tradeoff-trade-status-keeping = mantendo
tradeoff-confirm-trades = Confirmar trocas ({ $count } dados)
tradeoff-keeping = Mantendo { $value }.
tradeoff-trading = Trocando { $value }.
tradeoff-you-traded = Você trocou { $count } dados para o pote: { $dice }.
tradeoff-player-traded = { $player } trocou { $count } dados para o pote: { $dice }.
tradeoff-you-traded-brief = Você trocou { $count } dados.
tradeoff-player-traded-brief = { $player } trocou { $count } dados.
tradeoff-you-traded-none = Você manteve os cinco dados desta mão, então não vai pegar do pote desta vez.
tradeoff-player-traded-none = { $player } manteve os cinco dados desta mão.

tradeoff-your-turn-take = Sua vez de pegar um dado do pote.
tradeoff-take-die = Pegar um { $value } ({ $remaining } restantes)
tradeoff-you-take = Você pega um { $value }.
tradeoff-player-takes = { $player } pega um { $value }.

tradeoff-you-scored = Você marcou { $points } pontos com { $sets }.
tradeoff-player-scored = { $player } marcou { $points } pontos com { $sets }.
tradeoff-you-scored-brief = Você marcou { $points } pontos nesta rodada.
tradeoff-player-scored-brief = { $player } marcou { $points } pontos nesta rodada.
tradeoff-you-no-sets = Você marcou 0 pontos porque seus 15 dados não formaram nenhuma combinação pontuável.
tradeoff-no-sets = { $player } marcou 0 pontos porque os 15 dados dele não formaram nenhuma combinação pontuável.

tradeoff-set-triple = trinca de { $value }
tradeoff-set-group = grupo de { $value }
tradeoff-set-mini-straight = mini sequência { $low }-{ $high }
tradeoff-set-double-triple = trinca dupla ({ $v1 } e { $v2 })
tradeoff-set-straight = sequência { $low }-{ $high }
tradeoff-set-double-group = grupo duplo ({ $v1 } e { $v2 })
tradeoff-set-all-groups = todos os grupos
tradeoff-set-all-triplets = todas as trincas

tradeoff-round-scores = Pontuação da rodada { $round }:
tradeoff-round-scores-brief = Pontuação:
tradeoff-score-line = { $player }: +{ $round_points } (total: { $total })
tradeoff-score-line-brief = { $player}: +{ $round_points }, total { $total }.
tradeoff-leader = { $player } lidera com { $score }.
tradeoff-leader-brief = Líder: { $player }, { $score }.

tradeoff-you-win = Você vence com { $score } pontos!
tradeoff-winner = { $player } vence com { $score } pontos!
tradeoff-you-tie-win = Você empata na primeira posição com { $players }, com { $score } pontos!
tradeoff-winners-tie = Empate! { $players } empataram com { $score } pontos!

tradeoff-view-hand = Ver sua mão
tradeoff-view-pool = Ver o pote
tradeoff-view-players = Ver jogadores
tradeoff-hand-state-empty = nenhum dado mantido ainda
tradeoff-hand-empty = Sua mão está vazia. Se você acabou de rolar, use as escolhas de dados para decidir o que manter antes de confirmar as trocas.
tradeoff-hand-display = Sua mão mantida nesta rodada ({ $count } dados): { $dice }.
tradeoff-hand-display-with-roll = Sua mão mantida nesta rodada ({ $count } dados): { $dice }. Tirada atual: { $roll }. { $trade_count } dados ainda marcados para troca.
tradeoff-roll-die-status = posição { $position}: { $value }, { $status }
tradeoff-die-count = { $value}: { $count }
tradeoff-pool-display = Pote ({ $count } dados): { $dice }.
tradeoff-pool-empty = O pote está vazio.
tradeoff-player-info = { $player}: mão mantida: { $hand }. Última troca: { $traded }.
tradeoff-player-info-no-trade = { $player}: mão mantida: { $hand }. Não trocou nada da última vez.

tradeoff-not-trading-phase = Você só pode mudar ou confirmar escolhas de troca enquanto seus dados recém-rolados aguardam na fase de troca.
tradeoff-not-taking-phase = Você só pode pegar dados depois que todos os jogadores confirmarem as trocas e o pote compartilhado for aberto.
tradeoff-already-confirmed = Você já confirmou esta seleção de troca. Espere os outros jogadores; se você trocou dados, vai pegar do pote quando chegar sua vez.
tradeoff-no-die = Não há dado disponível para essa ação de troca.
tradeoff-no-die-position = A posição { $position } não está disponível na sua tirada atual.
tradeoff-no-rolled-dice = Você não tem dados rolados aguardando escolhas de troca no momento.
tradeoff-no-more-takes = Você já devolveu a mesma quantidade de dados que trocou nesta mão.
tradeoff-not-in-pool = Não há { $value } no pote compartilhado agora. Escolha um dos valores visíveis no pote.
tradeoff-not-your-take-turn = É a vez de { $player } de pegar do pote. Espere seu nome ser anunciado antes de escolher um dado.
tradeoff-no-trading-die-value = Você não tem um { $value } marcado para troca no momento.
tradeoff-no-kept-die-value = Você não tem um { $value } mantido para marcar para troca.
tradeoff-value-trade-style-required = Os controles Shift+número só são usados com o estilo de manutenção por valores dos dados. Use as teclas numéricas simples por posição ou mude seu estilo pessoal de manutenção dos dados.
tradeoff-use-plain-number-to-take = Use a tecla numérica simples, sem Shift, para pegar um dado do pote.
tradeoff-no-dice-key-phase = As teclas numéricas só são usadas ao escolher trocas ou pegar dados do pote.

tradeoff-set-target = Pontuação alvo: { $score }
tradeoff-enter-target = Digite a pontuação alvo:
tradeoff-option-changed-target = Pontuação alvo definida para { $score }.
tradeoff-desc-target-score = A pontuação total que um jogador deve alcançar ou ultrapassar após uma rodada de pontuação para vencer (padrão 60, intervalo de 30 a 500).
tradeoff-error-target-out-of-range = A pontuação alvo { $score } está fora do intervalo permitido de { $min } a { $max }.
