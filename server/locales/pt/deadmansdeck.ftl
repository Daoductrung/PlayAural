game-name-deadmansdeck = O Baralho do Morto

deadmansdeck-call-liar = Acusar de mentiroso
deadmansdeck-play-selected = Jogar cartas selecionadas
deadmansdeck-clear-selection = Limpar seleção
deadmansdeck-read-hand = Ler mão
deadmansdeck-read-table = Ler mesa
deadmansdeck-read-revolvers = Ler revólveres
deadmansdeck-read-card-counts = Ler contagem de cartas

deadmansdeck-rank-ace = Ás
deadmansdeck-rank-ace-plural = Áses
deadmansdeck-rank-king = Rei
deadmansdeck-rank-king-plural = Reis
deadmansdeck-rank-queen = Dama
deadmansdeck-rank-queen-plural = Damas
deadmansdeck-rank-joker = Coringa
deadmansdeck-rank-joker-plural = Coringas
deadmansdeck-claim-text = { $count } { $rank }

deadmansdeck-card-label = { $card }
deadmansdeck-selected-card-label = Selecionada: { $card }
deadmansdeck-card-selected = { $card } selecionada.
deadmansdeck-card-unselected = { $card } deselecionada.
deadmansdeck-selection-cleared = Seleção limpa.
deadmansdeck-card-not-found = Essa carta não está mais disponível.
deadmansdeck-too-many-selected = Você pode declarar no máximo três cartas.
deadmansdeck-select-card-first = Selecione de uma a três cartas primeiro.
deadmansdeck-no-claim-to-challenge = Não há declaração para desafiar.
deadmansdeck-cannot-challenge-self = Você não pode desafiar sua própria declaração.
deadmansdeck-action-sequence-running = Aguarde a sequência atual terminar.
deadmansdeck-action-eliminated = Você foi eliminado.

deadmansdeck-prepare-revolver = Os revólveres estão sendo preparados.
deadmansdeck-round-start = Rodada { $round }. A carta da mesa é { $target }.
deadmansdeck-turn-order = Ordem de turnos nesta rodada: { $order }.
deadmansdeck-your-hand = Sua mão: { $cards }.
deadmansdeck-hand-empty = Sua mão está vazia.
deadmansdeck-no-cards = sem cartas
deadmansdeck-you-skipped-no-cards = Você não tem cartas e foi pulado.
deadmansdeck-player-skipped-no-cards = { $player } não tem cartas e foi pulado.
deadmansdeck-you-out-of-cards = Você não tem mais cartas.
deadmansdeck-player-out-of-cards = { $player } não tem mais cartas.
deadmansdeck-you-forced-challenge = Você deve desafiar porque a rodada não pode continuar.
deadmansdeck-forced-challenge = { $player } deve desafiar porque a rodada não pode continuar.
deadmansdeck-you-claim = Você declara { $claim }.
deadmansdeck-player-claims = { $player } declara { $claim }.
deadmansdeck-you-call-liar = Você acusa { $accused } de mentiroso.
deadmansdeck-player-calls-liar = { $challenger } acusa { $accused } de mentiroso.
deadmansdeck-player-calls-you-liar = { $challenger } acusa você de mentiroso.
deadmansdeck-you-forced-liar-call = Você é obrigado a acusar { $accused } de mentiroso.
deadmansdeck-forced-liar-call = { $challenger } é obrigado a acusar { $accused } de mentiroso.
deadmansdeck-forced-liar-call-you = { $challenger } é obrigado a acusar você de mentiroso.
deadmansdeck-your-revealed-cards = Suas cartas reveladas: { $cards }.
deadmansdeck-revealed-cards = { $player } revelou: { $cards }.
deadmansdeck-you-caught-bluff = Você pegou { $accused } blefando. { $accused } deve puxar o gatilho.
deadmansdeck-your-bluff-caught = { $challenger } pegou seu blefe. Você deve puxar o gatilho.
deadmansdeck-bluff-caught = { $challenger } pegou o blefe de { $accused }. { $accused } deve puxar o gatilho.
deadmansdeck-you-wrong-challenge = { $accused } estava falando a verdade. Você deve puxar o gatilho.
deadmansdeck-your-truthful-claim = Sua declaração era verdadeira. { $challenger } deve puxar o gatilho.
deadmansdeck-truthful-claim = { $accused } estava falando a verdade. { $challenger } deve puxar o gatilho.
deadmansdeck-you-face-revolver = Você encara o revólver.
deadmansdeck-roulette-start = { $player } encara o revólver.
deadmansdeck-you-roulette-survived = Câmara vazia. Você sobrevive. Seu próximo puxão tem 1 em { $remaining } de risco.
deadmansdeck-roulette-survived = Câmara vazia. { $player } sobrevive. O próximo puxão tem 1 em { $remaining } de risco.
deadmansdeck-you-eliminated-by-gun = A arma dispara. Você foi eliminado.
deadmansdeck-player-eliminated = A arma dispara. { $player } foi eliminado.
deadmansdeck-you-win-game = Você é o último jogador sobrevivente e vence o Dead Man's Deck.
deadmansdeck-player-wins = { $player } é o último jogador sobrevivente e vence o Dead Man's Deck.
deadmansdeck-no-winner = Nenhum vencedor pôde ser determinado.
deadmansdeck-you-are-eliminated = Você foi eliminado deste jogo.

deadmansdeck-table-round = Rodada { $round }. Alvo: { $target }.
deadmansdeck-table-target-pending = ainda não definido
deadmansdeck-table-current-turn = Turno atual: { $player }.
deadmansdeck-table-last-claim = Última declaração: { $player } declarou { $claim }.
deadmansdeck-table-no-claim = Não há declaração ativa.
deadmansdeck-table-alive = Ainda vivos: { $players }.
deadmansdeck-table-eliminated = Eliminados: { $players }.

deadmansdeck-card-count-line = { $player }: { $count ->
    [one] 1 carta
   *[other] { $count } cartas
} restam.
deadmansdeck-card-count-eliminated = { $player }: eliminado.

deadmansdeck-revolvers-header = Status dos revólveres
deadmansdeck-revolver-status = { $player }: { $survived } câmaras vazias usadas; próximo puxão é 1 em { $remaining }.
deadmansdeck-revolver-eliminated = { $player }: eliminado.

deadmansdeck-results-header = Resultados de Dead Man's Deck
deadmansdeck-results-winner = Vencedor: { $player }.
deadmansdeck-results-survived = sobreviveu
deadmansdeck-results-eliminated = eliminado
deadmansdeck-results-line = { $player }: { $status }, acusações certas { $correct }, blefes bem-sucedidos { $bluffs }, sobrevivências na roleta { $survivals }.
