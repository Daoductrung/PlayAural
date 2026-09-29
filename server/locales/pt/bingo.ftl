game-name-bingo = Bingo

bingo-pattern-line = Qualquer linha
bingo-pattern-four-corners = Quatro cantos
bingo-pattern-letter-x = Letra X
bingo-pattern-blackout = Cartela cheia

bingo-call-interval-5 = 5 segundos
bingo-call-interval-15 = 15 segundos
bingo-call-interval-30 = 30 segundos
bingo-call-interval-45 = 45 segundos
bingo-call-interval-60 = 60 segundos

bingo-set-pattern = Padrão para vencer: { $pattern }
bingo-select-pattern = Selecione o padrão para vencer:
bingo-option-changed-pattern = O padrão para vencer agora é { $pattern }.
bingo-desc-pattern = O padrão que uma cartela deve completar para vencer. Qualquer linha aceita uma linha, coluna ou diagonal completa. Quatro cantos exige as quatro casas dos cantos. Letra X exige as duas diagonais. Cartela cheia exige a cartela inteira.

bingo-set-call-interval = Sortear a cada { $seconds }
bingo-select-call-interval = Selecione o intervalo de sorteio:
bingo-option-changed-interval = Um novo número será sorteado a cada { $seconds }.
bingo-desc-call-interval = Quanto tempo o locutor espera entre cada número anunciado (padrão 15, intervalo de 5 a 60 segundos).

bingo-cell-free = Casa livre.
bingo-cell-marked = { $letter } { $number }, marcada.
bingo-cell-unmarked = { $letter } { $number }, não marcada.
bingo-cell-is-free = Esta casa já é livre.
bingo-you-already-won = Você já fez Bingo nesta rodada.

bingo-you-mark = Você marcou { $letter } { $number }.
bingo-you-unmark = Você desmarcou { $letter } { $number }.

bingo-claim-bingo = Gritar Bingo!
bingo-repeat-call = Repetir o último número
bingo-check-called = Ver números sorteados
bingo-no-calls-yet = Ainda nenhum número foi sorteado.
bingo-claim-in-progress = Outro pedido de Bingo está sendo verificado agora. Tente novamente em instantes.
bingo-claim-in-progress-you = Seu pedido já está sendo verificado.
bingo-claim-wait-for-call = Espere o número sendo sorteado ser anunciado, depois tente novamente.
bingo-claim-unchanged = Sua cartela não mudou desde que foi rejeitada. Marque outro número ou espere o próximo sorteio antes de pedir novamente.
bingo-checking-claim-you = Você grita Bingo. Verificando sua cartela...
bingo-checking-claim = { $player } grita Bingo. Verificando a cartela...
bingo-whose-turn-checking = Verificando a cartela de { $player }...
bingo-whose-turn-checking-you = Sua cartela está sendo verificada...
bingo-whose-turn-drawing = Sorteando o próximo número...
bingo-whose-turn-waiting = { $seconds ->
    [one] Próximo número em { $seconds } segundo.
   *[other] Próximo número em { $seconds } segundos.
}
bingo-claim-incorrect-you = Cartela incorreta.
bingo-claim-incorrect = A cartela de { $player } está incorreta.
bingo-claim-incomplete-you = Você ainda não tem o padrão completo.
bingo-claim-incomplete = { $player } ainda não tem o padrão completo.
bingo-marked-number-not-called = Você marcou { $letter } { $number }, mas esse número ainda não foi sorteado.

bingo-last-call = { $letter } { $number }

bingo-status-called-count = { $count } de { $total } números sorteados.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = O Bingo começa! Padrão: { $pattern }. Um novo número será sorteado a cada { $interval } segundos. Marque sua cartela e pressione B para gritar Bingo quando fizer Bingo.
bingo-game-start-touch = O Bingo começa! Padrão: { $pattern }. Um novo número será sorteado a cada { $interval } segundos. Marque sua cartela e, quando fizer Bingo, use o gesto de toque sustentado do seu cliente em qualquer lugar dela, ou escolha Gritar Bingo.
bingo-game-start-spectator = O Bingo começa! Padrão: { $pattern }. Um novo número será sorteado a cada { $interval } segundos.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = Sim! Cartela correta. Você vence com { $numbers }!
bingo-claim-correct = Sim! Cartela correta. { $player } vence com { $numbers }!
bingo-claim-correct-no-numbers-you = Sim! Cartela correta. Você vence!
bingo-claim-correct-no-numbers = Sim! Cartela correta. { $player } vence!
bingo-deck-exhausted = Todos os 75 números foram sorteados. A rodada termina aqui.

bingo-error-invalid-interval = "{ $value }" não é um intervalo de sorteio válido.
bingo-error-invalid-pattern = { $value } não é um padrão para vencer reconhecido.

bingo-end-calls = { $count ->
    [one] { $count } número foi sorteado nesta rodada.
   *[other] { $count } números foram sorteados nesta rodada.
}
bingo-end-winner-line = Vencedor: { $player }
bingo-end-no-winner = Nenhum pedido de Bingo válido foi feito nesta rodada.
