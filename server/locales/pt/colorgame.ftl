game-name-colorgame = Jogo das Cores

colorgame-set-starting-bankroll = Banca inicial: { $amount }
colorgame-enter-starting-bankroll = Insira a banca inicial:
colorgame-option-changed-starting-bankroll = Banca inicial definida para { $amount }.
colorgame-desc-starting-bankroll = Com quantas fichas cada jogador começa o Jogo das Cores (padrão 100, intervalo de 10 a 1000).

colorgame-set-minimum-bet = Aposta mínima: { $amount }
colorgame-enter-minimum-bet = Insira a aposta mínima:
colorgame-option-changed-minimum-bet = Aposta mínima definida para { $amount }.
colorgame-desc-minimum-bet = A menor aposta permitida em uma cor a cada rodada (padrão 1, intervalo de 1 a 100).

colorgame-set-maximum-total-bet = Aposta total máxima por rodada: { $amount }
colorgame-enter-maximum-total-bet = Insira a aposta total máxima por rodada:
colorgame-option-changed-maximum-total-bet = Aposta total máxima por rodada definida para { $amount }.
colorgame-desc-maximum-total-bet = O total máximo de fichas que um jogador pode arriscar em uma rodada do Jogo das Cores. Deve ser pelo menos a aposta mínima e não maior que a banca inicial; o limite real de um jogador também é limitado por sua banca atual (padrão 20, intervalo de 1 a 1000).

colorgame-set-betting-timer = Temporizador de apostas: { $seconds } segundos
colorgame-enter-betting-timer = Insira o temporizador de apostas em segundos:
colorgame-option-changed-betting-timer = Temporizador de apostas definido para { $seconds } segundos.
colorgame-desc-betting-timer-seconds = Quanto tempo dura a fase de apostas a cada rodada (padrão 15 segundos, intervalo de 5 a 60).

colorgame-set-round-limit = Limite de rodadas: { $count }
colorgame-enter-round-limit = Insira o limite de rodadas:
colorgame-option-changed-round-limit = Limite de rodadas definido para { $count }.
colorgame-desc-round-limit = Número máximo de rodadas do Jogo das Cores antes que o vencedor seja decidido (padrão 20, intervalo de 1 a 100).

colorgame-set-win-condition = Condição de vitória: { $mode }
colorgame-select-win-condition = Selecione a condição de vitória:
colorgame-option-changed-win-condition = Condição de vitória definida para { $mode }.
colorgame-desc-win-condition = Escolhe se o Jogo das Cores termina com o último jogador restante ou com a maior banca após o limite de rodadas.
colorgame-win-condition-last-player = Último jogador restante
colorgame-win-condition-highest-bankroll = Maior banca no limite de rodadas

colorgame-color-red = vermelho
colorgame-color-blue = azul
colorgame-color-yellow = amarelo
colorgame-color-green = verde
colorgame-color-white = branco
colorgame-color-orange = laranja

colorgame-game-start = O Jogo das Cores começa. Jogadores: { $players }.
colorgame-round-start = Rodada { $round } de { $limit }. As apostas estão abertas por { $seconds } segundos.
colorgame-round-start-brief = Rodada { $round }. Aposte já: { $seconds } segundos.
colorgame-roll-result = Os dados mostram { $colors }.
colorgame-roll-result-brief = Rolagem: { $colors }.
colorgame-you-locked-bets = Você confirmou { $total } fichas.
colorgame-player-locked-bets = { $player } confirmou { $total } fichas.
colorgame-you-locked-bets-brief = Você confirmou { $total }.
colorgame-player-locked-bets-brief = { $player } confirmou { $total }.
colorgame-you-sit-out = Você fica de fora desta rodada.
colorgame-player-sits-out = { $player } fica de fora desta rodada.
colorgame-you-sit-out-brief = Você fica de fora.
colorgame-player-sits-out-brief = { $player } fica de fora.
colorgame-you-sat-out = Você ficou de fora e continua com { $bankroll } fichas.
colorgame-player-sat-out = { $player } ficou de fora e continua com { $bankroll } fichas.
colorgame-you-sat-out-brief = Você: sem aposta, { $bankroll }.
colorgame-player-sat-out-brief = { $player }: sem aposta, { $bankroll }.
colorgame-you-won = Você ganhou { $amount } fichas e subiu para { $bankroll }.
colorgame-player-won = { $player } ganhou { $amount } fichas e subiu para { $bankroll }.
colorgame-you-won-brief = Você: +{ $amount }, { $bankroll }.
colorgame-player-won-brief = { $player }: +{ $amount }, { $bankroll }.
colorgame-you-even = Você empatou e continua com { $bankroll } fichas.
colorgame-player-even = { $player } empatou e continua com { $bankroll } fichas.
colorgame-you-even-brief = Você: empate, { $bankroll }.
colorgame-player-even-brief = { $player }: empate, { $bankroll }.
colorgame-you-lost = Você perdeu { $amount } fichas e caiu para { $bankroll }.
colorgame-player-lost = { $player } perdeu { $amount } fichas e caiu para { $bankroll }.
colorgame-you-lost-brief = Você: -{ $amount }, { $bankroll }.
colorgame-player-lost-brief = { $player }: -{ $amount }, { $bankroll }.

colorgame-set-bet-color = Definir aposta em { $color }: { $amount }
colorgame-clear-bets = Limpar apostas
colorgame-confirm-bets = Confirmar apostas ({ $total })
colorgame-confirm-sit-out = Confirmar sem aposta
colorgame-check-status = Verificar status
colorgame-check-bets = Verificar apostas
colorgame-check-last-roll = Verificar última rolagem

colorgame-select-quick-bet = Selecione um valor de aposta:
colorgame-quick-bet-minimum = Mínimo: { $amount }
colorgame-quick-bet-preset = Apostar { $amount }
colorgame-quick-bet-quarter = 25 por cento disponível: { $amount }
colorgame-quick-bet-half = 50 por cento disponível: { $amount }
colorgame-quick-bet-all-in = Tudo, até o limite da rodada: { $amount }
colorgame-quick-bet-clear = Limpar esta cor
colorgame-quick-bet-custom = Entrada personalizada
colorgame-enter-custom-bet-amount = Insira a aposta exata para esta cor. Insira 0 para limpá-la.
colorgame-invalid-bet-amount = Insira um valor de aposta inteiro válido.
colorgame-bet-below-minimum = Cada aposta de cor deve ser de pelo menos { $amount }.
colorgame-bet-exceeds-bankroll = Suas apostas totais não podem exceder suas { $amount } fichas disponíveis.
colorgame-bet-exceeds-round-limit = Suas apostas totais não podem exceder o limite da rodada de { $amount } fichas.
colorgame-no-room-for-color-bet = Você tem apenas { $available } fichas de capacidade de aposta restante, abaixo do mínimo de { $minimum } para outra cor. Reduza ou limpe outra aposta primeiro.
colorgame-betting-closed = As apostas estão fechadas enquanto os dados estão rolando ou o resultado está sendo resolvido.
colorgame-bet-updated = { $color } agora está definido para { $amount }. Total comprometido nesta rodada: { $total }.
colorgame-color-bet-cleared = Sua aposta em { $color } foi limpa. Total comprometido nesta rodada: { $total }.
colorgame-bets-cleared = Todas as suas apostas foram limpas.
colorgame-below-minimum-bankroll = Você tem { $bankroll } fichas, abaixo da aposta mínima de { $minimum }, então você não pode apostar novamente nesta partida.
colorgame-bets-already-locked = Suas apostas já estão confirmadas para esta rodada.
colorgame-no-bets-placed = Você não fez nenhuma aposta.
colorgame-confirm-all-in = Isso definirá { $color } para { $amount }, usando toda a capacidade de aposta disponível nesta rodada. Repita a mesma escolha de Tudo em até { $seconds } segundos para confirmar.
colorgame-confirm-sit-out-risk = Você não tem apostas. Pressione Confirmar sem aposta novamente em até { $seconds } segundos para ficar de fora desta rodada.

colorgame-no-bets = sem aposta
colorgame-bet-entry = { $color } { $amount }
colorgame-bets-header = Apostas atuais:
colorgame-bets-line = { $player }: { $bets }. Total { $total }. { $locked }.
colorgame-bets-open-status = As apostas ainda estão abertas
colorgame-bets-locked-status = As apostas estão confirmadas

colorgame-last-roll-none = Nenhuma rolagem foi registrada ainda.
colorgame-last-roll-header = Última rolagem: { $colors }.
colorgame-last-roll-line = { $player }: { $bets }. Líquido { $net }. Banca { $bankroll }.

colorgame-status-betting = Fase de apostas. Rodada { $round } de { $limit }. { $seconds } segundos restantes. Condição de vitória: { $win_mode }.
colorgame-status-rolling = Os dados estão rolando para a rodada { $round } de { $limit }. Condição de vitória: { $win_mode }.
colorgame-status-resolving = A rodada { $round } de { $limit } está se resolvendo. Condição de vitória: { $win_mode }.
colorgame-status-bankroll = Sua banca é { $bankroll }. Você comprometeu { $total } nesta rodada. Seu limite nesta rodada é { $cap }.
colorgame-status-bet-lock = O estado da sua aposta: { $state }.
colorgame-status-leader = O líder atual é { $player } com { $bankroll } fichas.

colorgame-whose-turn-betting = Fase de apostas. Todos os jogadores ativos podem agir. Restam { $seconds } segundos.
colorgame-whose-turn-rolling = Os dados estão rolando agora.
colorgame-whose-turn-resolving = A rodada está se resolvendo agora.

colorgame-standings-header = Classificação:
colorgame-standing-live = ainda no jogo
colorgame-standing-bust = eliminado, abaixo da aposta mínima
colorgame-score-line = { $rank }. { $player }: { $bankroll } fichas, { $profitable_rounds } rodadas lucrativas, maior vitória { $biggest_win }, { $status }.
colorgame-game-winner = Vencedor: { $player }.
colorgame-game-tie = Vencedores empatados: { $players }.

colorgame-error-minimum-exceeds-bankroll = A aposta mínima de { $minimum } não pode exceder a banca inicial de { $bankroll }.
colorgame-error-max-bet-too-small = A aposta total máxima de { $maximum } deve ser pelo menos a aposta mínima de { $minimum }.
colorgame-error-max-bet-too-large = A aposta total máxima de { $maximum } não pode exceder a banca inicial de { $bankroll }.
