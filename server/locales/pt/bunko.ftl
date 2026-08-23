game-name-bunko = Bunko

bunko-roll = Rolar os dados
bunko-check-status = Verificar status
bunko-check-last-roll = Verificar última rolagem

bunko-game-start = Bunko começa. Jogadores: { $players }.
bunko-round-start = Rodada { $round } de { $total_rounds }. O número alvo desta rodada é { $target }.
bunko-round-start-brief = Rodada { $round }/{ $total_rounds }. Alvo { $target }.
bunko-you-win-round = Você vence a rodada { $round } com { $score } pontos contra o alvo { $target }.
bunko-player-wins-round = { $player } vence a rodada { $round } com { $score } pontos contra o alvo { $target }.
bunko-you-win-round-brief = Você vence a R{ $round }: { $score }.
bunko-player-wins-round-brief = { $player } vence a R{ $round }: { $score }.

bunko-you-roll-match = Você tira { $dice } e pontua { $points } { $points ->
    [one] ponto
   *[other] pontos
} em direção ao alvo { $target }. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-player-rolls-match = { $player } tira { $dice } e pontua { $points } { $points ->
    [one] ponto
   *[other] pontos
} em direção ao alvo { $target }. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-you-roll-match-brief = Você: { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.
bunko-player-rolls-match-brief = { $player }: { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.

bunko-you-roll-mini_bunko = Você tira { $dice }, marca um mini Bunko porque todos os dados coincidem entre si, mas não com o alvo { $target }, e ganha { $points } pontos. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-player-rolls-mini_bunko = { $player } tira { $dice }, marca um mini Bunko porque todos os dados coincidem entre si, mas não com o alvo { $target }, e ganha { $points } pontos. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-you-roll-mini_bunko-brief = Você: mini Bunko { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.
bunko-player-rolls-mini_bunko-brief = { $player }: mini Bunko { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.

bunko-you-roll-bunko = Você tira { $dice } e marca um Bunko: três alvos { $target } por { $points } pontos. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-player-rolls-bunko = { $player } tira { $dice } e marca um Bunko: três alvos { $target } por { $points } pontos. Total da rodada: { $round_total }. Pontuação geral: { $total }.
bunko-you-roll-bunko-brief = Você: Bunko { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.
bunko-player-rolls-bunko-brief = { $player }: Bunko { $dice }, +{ $points }. Rodada { $round_total }; total { $total }.

bunko-you-roll-no_score = Você tira { $dice } e não pontua nada porque nenhum dos dados coincide com o alvo { $target } e não há mini Bunko. Seu turno passa.
bunko-player-rolls-no_score = { $player } tira { $dice } e não pontua nada porque nenhum dos dados coincide com o alvo { $target } e não há mini Bunko. O turno passa.
bunko-you-roll-no_score-brief = Você: { $dice }, 0. Passa.
bunko-player-rolls-no_score-brief = { $player }: { $dice }, 0. Passa.

bunko-last-roll-none = Nenhuma rolagem foi feita ainda nesta rodada.
bunko-last-roll-match = { $player } tirou por último { $dice } e pontuou { $points } { $points ->
    [one] ponto
   *[other] pontos
} em direção ao alvo { $target }.
bunko-last-roll-match-you = Você tirou por último { $dice } e pontuou { $points } { $points ->
    [one] ponto
   *[other] pontos
} em direção ao alvo { $target }.
bunko-last-roll-mini_bunko = { $player } tirou por último { $dice } para um mini Bunko, pontuando { $points } pontos porque os dados coincidiam entre si, mas não com o alvo { $target }.
bunko-last-roll-mini_bunko-you = Você tirou por último { $dice } para um mini Bunko, pontuando { $points } pontos porque os dados coincidiam entre si, mas não com o alvo { $target }.
bunko-last-roll-bunko = { $player } tirou por último { $dice } para um Bunko: três alvos { $target }, valendo { $points } pontos.
bunko-last-roll-bunko-you = Você tirou por último { $dice } para um Bunko: três alvos { $target }, valendo { $points } pontos.
bunko-last-roll-no_score = { $player } tirou por último { $dice } e não pontuou nada contra o alvo { $target }.
bunko-last-roll-no_score-you = Você tirou por último { $dice } e não pontuou nada contra o alvo { $target }.

bunko-status-round = Rodada { $round } de { $total_rounds }. Número alvo: { $target }.
bunko-status-turn = Jogador atual: { $player }.
bunko-status-leader = Líder: { $player } com { $rounds } { $rounds ->
    [one] vitória de rodada
   *[other] vitórias de rodada
} e { $total } pontos gerais.

bunko-standings-header = Classificação. Vencedor decidido por { $mode }.
bunko-score-line = { $rank }. { $player }: { $rounds } { $rounds ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}, { $total } pontos gerais, { $current } nesta rodada, { $bunkos } { $bunkos ->
    [one] Bunko
   *[other] Bunkos
}, { $mini_bunkos } { $mini_bunkos ->
    [one] mini Bunko
   *[other] mini Bunkos
}

bunko-roll-already-resolving = Seus dados ainda estão rolando. Aguarde o resultado antes de rolar novamente.
bunko-error-round-count-invalid = O Bunko requer entre { $min } e { $max } rodadas. A configuração atual é { $count }.
bunko-error-winning-mode-invalid = O Bunko não suporta o modo de vitória "{ $mode }". Escolha vitórias de rodada ou pontuação total.

bunko-set-round-count = Rodadas: { $count }
bunko-enter-round-count = Insira o número de rodadas:
bunko-option-changed-round-count = Número de rodadas alterado para { $count }.
bunko-desc-round-count = Quantas rodadas de Bunko são jogadas antes que o vencedor seja decidido (padrão 6, intervalo de 1 a 12).

bunko-set-winning-mode = Modo de vitória: { $mode }
bunko-select-winning-mode = Selecione o modo de vitória:
bunko-option-changed-winning-mode = Modo de vitória alterado para { $mode }.
bunko-desc-winning-mode = Escolhe se os vencedores do Bunko são classificados por rodadas vencidas ou por pontuação total.
bunko-winning-mode-round-wins = vitórias de rodada
bunko-winning-mode-total-score = pontuação total
