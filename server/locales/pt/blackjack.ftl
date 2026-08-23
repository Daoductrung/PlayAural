# Blackjack

game-name-blackjack = Blackjack

blackjack-set-rules-profile = Perfil de regras: { $profile }
blackjack-select-rules-profile = Selecionar perfil de regras
blackjack-option-changed-rules-profile = Perfil de regras definido para { $profile }.
blackjack-desc-rules-profile = Aplica um pacote predefinido de regras de Blackjack: Vegas, Europeu ou Amigável.

blackjack-set-starting-chips = Fichas iniciais: { $count }
blackjack-enter-starting-chips = Insira as fichas iniciais
blackjack-option-changed-starting-chips = Fichas iniciais definidas para { $count }.
blackjack-desc-starting-chips = Com quantas fichas cada jogador começa na mesa de Blackjack (padrão 500, intervalo de 50 a 1000000).

blackjack-set-base-bet = Aposta base: { $count }
blackjack-enter-base-bet = Insira a aposta base
blackjack-option-changed-base-bet = Aposta base definida para { $count }.
blackjack-desc-base-bet = A aposta padrão oferecida entre as mãos de Blackjack (padrão 10, intervalo de 1 a 100000).
blackjack-enter-bet = Insira sua aposta em fichas
blackjack-option-changed-bet = Aposta definida para { $count } fichas.

blackjack-set-table-min-bet = Aposta mínima da mesa: { $count }
blackjack-enter-table-min-bet = Insira a aposta mínima da mesa
blackjack-option-changed-table-min-bet = Aposta mínima da mesa definida para { $count }.
blackjack-desc-table-min-bet = A menor aposta permitida no Blackjack (padrão 5, intervalo de 1 a 100000).

blackjack-set-table-max-bet = Aposta máxima da mesa: { $count }
blackjack-enter-table-max-bet = Insira a aposta máxima da mesa
blackjack-option-changed-table-max-bet = Aposta máxima da mesa definida para { $count }.
blackjack-desc-table-max-bet = A maior aposta permitida no Blackjack (padrão 100, intervalo de 1 a 100000).

blackjack-set-deck-count = Número de baralhos: { $count }
blackjack-enter-deck-count = Insira o número de baralhos
blackjack-option-changed-deck-count = Número de baralhos definido para { $count }.
blackjack-desc-deck-count = Quantos baralhos padrão de 52 cartas são embaralhados no sabot do Blackjack (padrão 4, intervalo de 1 a 8).

blackjack-set-dealer-soft-17 = Dealer pede carta em 17 macio: { $enabled }
blackjack-option-changed-dealer-soft-17 = Dealer pede carta em 17 macio definido para { $enabled }.
blackjack-desc-dealer-hits-soft-17 = Controla se o dealer deve puxar carta em 17 macio, como Ás mais 6.

blackjack-set-dealer-peek-blackjack = Dealer confere blackjack: { $enabled }
blackjack-option-changed-dealer-peek-blackjack = Conferência de blackjack pelo dealer definida para { $enabled }.
blackjack-desc-dealer-peeks-blackjack = Controla se o dealer confere Blackjack ao mostrar um Ás ou carta de valor dez.

blackjack-set-players-cards-face-up = Cartas dos jogadores viradas para cima: { $enabled }
blackjack-option-changed-players-cards-face-up = Cartas dos jogadores viradas para cima definidas para { $enabled }.
blackjack-desc-players-cards-face-up = Controla se as cartas dos jogadores são públicas para toda a mesa.

blackjack-set-allow-insurance = Oferecer seguro e dinheiro igual: { $enabled }
blackjack-option-changed-allow-insurance = Seguro e dinheiro igual definidos para { $enabled }.
blackjack-desc-allow-insurance = Controla se as opções de seguro e dinheiro igual são oferecidas quando o dealer mostra um Ás.

blackjack-set-allow-late-surrender = Permitir rendição tardia: { $enabled }
blackjack-option-changed-allow-late-surrender = Rendição tardia definida para { $enabled }.
blackjack-desc-allow-late-surrender = Controla se os jogadores podem se render antes de pedir carta; isso requer regras de conferência do dealer.

blackjack-set-blackjack-payout = Pagamento de blackjack: { $mode }
blackjack-select-blackjack-payout = Selecionar pagamento de blackjack
blackjack-option-changed-blackjack-payout = Pagamento de blackjack definido para { $mode }.
blackjack-desc-blackjack-payout = Define o pagamento para um Blackjack natural: 3 para 2, 6 para 5 ou dinheiro igual.

blackjack-set-double-down-rule = Regra de dobrar: { $mode }
blackjack-select-double-down-rule = Selecionar regra de dobrar
blackjack-option-changed-double-down-rule = Regra de dobrar definida para { $mode }.
blackjack-desc-double-down-rule = Controla quais totais iniciais podem dobrar: quaisquer duas cartas, 9-11 apenas ou 10-11 apenas.

blackjack-set-allow-double-after-split = Dobrar após divisão: { $enabled }
blackjack-option-changed-allow-double-after-split = Dobrar após divisão definido para { $enabled }.
blackjack-desc-allow-double-after-split = Controla se mãos divididas podem dobrar.

blackjack-set-split-rule = Regra de divisão: { $mode }
blackjack-select-split-rule = Selecionar regra de divisão
blackjack-option-changed-split-rule = Regra de divisão definida para { $mode }.
blackjack-desc-split-rule = Controla se uma divisão exige exatamente o mesmo valor nominal ou apenas o mesmo valor de carta.

blackjack-set-max-split-hands = Máximo de mãos divididas: { $count }
blackjack-enter-max-split-hands = Insira o máximo de mãos divididas
blackjack-option-changed-max-split-hands = Máximo de mãos divididas definido para { $count }.
blackjack-desc-max-split-hands = Número máximo de mãos que um jogador pode criar dividindo (padrão 2, intervalo de 1 a 2).

blackjack-set-split-aces-one-card = Áses divididos puxam apenas uma carta: { $enabled }
blackjack-option-changed-split-aces-one-card = Regra de uma carta para Áses divididos definida para { $enabled }.
blackjack-desc-split-aces-one-card-only = Controla se cada Ás dividido recebe exatamente uma carta e depois para.

blackjack-set-split-aces-blackjack = Áses divididos podem contar como blackjack: { $enabled }
blackjack-option-changed-split-aces-blackjack = Regra de blackjack para Áses divididos definida para { $enabled }.
blackjack-desc-split-aces-count-as-blackjack = Controla se Ás mais valor dez após dividir Áses conta como um Blackjack natural.

blackjack-set-turn-timer = Temporizador de turno: { $mode }
blackjack-select-turn-timer = Selecionar temporizador de turno
blackjack-option-changed-turn-timer = Temporizador de turno definido para { $mode }.
blackjack-desc-turn-timer = Limite de tempo opcional para cada decisão no Blackjack; escolha Ilimitado para sem temporizador.

blackjack-rules-profile-vegas = Vegas
blackjack-rules-profile-european = Europeu
blackjack-rules-profile-friendly = Amigável
blackjack-payout-3-to-2 = 3 para 2
blackjack-payout-6-to-5 = 6 para 5
blackjack-payout-1-to-1 = 1 para 1
blackjack-double-rule-any-two = Quaisquer duas cartas
blackjack-double-rule-9-to-11 = Totais de 9 a 11
blackjack-double-rule-10-to-11 = Totais de 10 a 11
blackjack-split-rule-same-value = Mesmo valor
blackjack-split-rule-same-rank = Mesmo valor nominal

blackjack-hit = Pedir carta
blackjack-stand = Parar
blackjack-double-down = Dobrar
blackjack-split = Dividir
blackjack-surrender = Rendição
blackjack-take-insurance = Fazer seguro
blackjack-decline-insurance = Recusar seguro
blackjack-even-money = Dinheiro igual
blackjack-read-hand = Ler mão
blackjack-read-dealer = Ler dealer
blackjack-read-bets = Ler apostas
blackjack-table-status = Status da mesa
blackjack-read-rules = Ler regras

blackjack-not-player-phase = Os jogadores não estão tomando ações no momento.
blackjack-not-insurance-phase = As decisões de seguro não estão ativas no momento.
blackjack-hand-complete = Sua mão está concluída.
blackjack-error-bet-too-high = A aposta base não pode ser maior que as fichas iniciais.
blackjack-error-starting-chips-below-min = As fichas iniciais não podem ser menores que a aposta mínima da mesa.
blackjack-error-table-limits-invalid = A aposta mínima da mesa não pode ser maior que a aposta máxima da mesa.
blackjack-error-bet-below-min = A aposta não pode ser menor que a aposta mínima da mesa.
blackjack-error-bet-above-max = A aposta não pode ser maior que a aposta máxima da mesa.
blackjack-error-bet-above-chips = Você não pode apostar mais fichas do que possui.
blackjack-error-late-surrender-requires-peek = A rendição tardia exige que a conferência de blackjack do dealer esteja ativada.
blackjack-cannot-split = Você não pode dividir esta mão.
blackjack-cannot-double-down = Você não pode dobrar no momento.
blackjack-cannot-surrender = Você não pode se render nesta mão.
blackjack-insurance-closed = Você não pode tomar uma decisão de seguro no momento.
blackjack-cannot-insure = Você não pode fazer seguro no momento.
blackjack-cannot-even-money = Você não pode aceitar dinheiro igual no momento.
blackjack-bet-already-locked = Sua aposta já está travada para esta mão.
blackjack-out-of-chips = Você está sem fichas.

blackjack-hand-start = Mão { $hand }. Faça suas apostas.
blackjack-you-bet = Você apostou { $amount }.
blackjack-player-bets = { $player } aposta { $amount }.
blackjack-bet-locked = Aposta travada em { $amount } fichas.
blackjack-insurance-offer = O seguro está aberto.
blackjack-insurance-prompt = Seguro disponível. Você pode fazer um seguro de { $amount } fichas ou recusar.
blackjack-insurance-prompt-player = Decisão de seguro para { $player }.
blackjack-insurance-prompt-even-money = Você pode aceitar dinheiro igual agora.
blackjack-insurance-prompt-even-money-player = { $player } pode aceitar dinheiro igual.

blackjack-dealer-shows = O dealer mostra { $card }.
blackjack-dealer-reveals = O dealer revela { $card }, totalizando { $total }.
blackjack-dealer-hits = O dealer puxa { $card }, totalizando { $total }.
blackjack-dealer-stands = O dealer para com { $total }.
blackjack-dealer-bust = O dealer estourou com { $total }.
blackjack-dealer-blackjack = O dealer tem blackjack.

blackjack-you-have = Você tem { $cards } ({ $total }).
blackjack-player-has = { $player } tem { $cards } ({ $total }).
blackjack-you-blackjack = Você tem blackjack.
blackjack-player-blackjack = { $player } tem blackjack.

blackjack-you-hit = Você puxa { $card }.
blackjack-player-hits = { $player } puxa { $card }.
blackjack-you-stand = Você para.
blackjack-player-stands = { $player } para.
blackjack-you-double-down = Você dobra em { $amount } fichas.
blackjack-player-double-downs = { $player } dobra em { $amount } fichas.
blackjack-you-split = Você divide sua mão e adiciona { $amount } fichas.
blackjack-player-splits = { $player } divide sua mão e adiciona { $amount } fichas.
blackjack-you-surrender = Você se rende e perde { $amount } fichas.
blackjack-player-surrenders = { $player } se rende e perde { $amount } fichas.
blackjack-you-take-insurance = Você faz uma aposta de seguro de { $amount } fichas.
blackjack-player-takes-insurance = { $player } faz uma aposta de seguro de { $amount } fichas.
blackjack-you-decline-insurance = Você recusa o seguro.
blackjack-player-declines-insurance = { $player } recusa o seguro.
blackjack-you-take-even-money = Você aceita dinheiro igual.
blackjack-player-takes-even-money = { $player } aceita dinheiro igual.
blackjack-you-split-aces-auto-stand = Áses divididos puxam uma carta cada e param automaticamente.
blackjack-player-splits-aces-auto-stand = { $player } divide áses e ambas as mãos param.
blackjack-you-stand-auto = Você para em 21.
blackjack-player-stands-auto = { $player } para em 21.
blackjack-you-bust = Você estourou com { $total }.
blackjack-player-bust = { $player } estourou com { $total }.
blackjack-your-total = Seu total é { $total }.
blackjack-player-total = { $player } tem { $total }.
blackjack-your-total-hand = Mão { $hand }: { $total }.
blackjack-player-total-hand = Mão { $hand } de { $player }: { $total }.

blackjack-you-win = Você ganha { $amount } fichas.
blackjack-player-wins = { $player } ganha { $amount } fichas.
blackjack-you-even-money-win = Dinheiro igual paga { $amount } fichas.
blackjack-player-even-money-win = { $player } recebe { $amount } fichas por dinheiro igual.
blackjack-you-lose = Você perde { $amount } fichas.
blackjack-player-loses = { $player } perde { $amount } fichas.
blackjack-you-push = Empate.
blackjack-player-push = { $player } empata.
blackjack-you-win-hand = Mão { $hand }: Você ganha { $amount } fichas.
blackjack-player-wins-hand = Mão { $hand } de { $player } ganha { $amount } fichas.
blackjack-you-lose-hand = Mão { $hand }: Você perde { $amount } fichas.
blackjack-player-loses-hand = Mão { $hand } de { $player } perde { $amount } fichas.
blackjack-you-push-hand = Mão { $hand }: Empate.
blackjack-player-push-hand = Mão { $hand } de { $player } empata.
blackjack-you-insurance-wins = O seguro ganha { $amount } fichas.
blackjack-player-insurance-wins = { $player } ganha { $amount } fichas com o seguro.
blackjack-you-insurance-loses = O seguro perde { $amount } fichas.
blackjack-player-insurance-loses = { $player } perde uma aposta de seguro de { $amount } fichas.
blackjack-you-broke = Você está sem fichas.
blackjack-player-broke = { $player } está sem fichas.
blackjack-you-win-game = Você vence o jogo com { $chips } fichas.
blackjack-player-wins-game = { $player } vence o jogo com { $chips } fichas.

blackjack-total-soft = { $total } macio
blackjack-total-hard = { $total }

blackjack-read-hand-response = Sua mão é { $cards } ({ $total }).
blackjack-read-hand-response-split = Mão 1: { $hand1 } ({ $total1 }). Mão 2: { $hand2 } ({ $total2 }). Mão ativa: { $active }.
blackjack-no-hand = Você não está na mão atual.
blackjack-no-dealer-cards = O dealer ainda não tem cartas.
blackjack-read-dealer-up = O dealer mostra { $card }.
blackjack-read-dealer-full = O dealer tem { $cards } ({ $total }).
blackjack-rule-yes = sim
blackjack-rule-no = não
blackjack-rules-readout = Regras: perfil { $profile }. Limites da mesa de { $min_bet } a { $max_bet }, aposta base { $base_bet }. Dealer pede em 17 macio: { $soft_17 }. Dealer confere blackjack: { $peek }. Cartas dos jogadores para cima: { $players_cards_face_up }. Seguro e dinheiro igual: { $insurance }. Rendição tardia: { $surrender }. Pagamento de blackjack: { $payout }. Regra de dobrar: { $double_rule }. Dobrar após divisão: { $das }. Regra de divisão: { $split_rule }. Máximo de mãos divididas: { $split_hands }. Regra de uma carta para áses divididos: { $split_aces_one }. Áses divididos blackjack: { $split_aces_blackjack }.

blackjack-status-line = { $player }: { $chips } fichas
blackjack-status-line-out = { $player }: sem fichas
blackjack-status-line-bet = { $player }: { $chips } fichas, aposta { $bet }
blackjack-status-line-hand = { $player }: { $chips } fichas, aposta { $bet }, total { $total }
blackjack-status-line-hands = { $player }: { $chips } fichas, aposta da mão 1 { $bet1 } total { $total1 }, aposta da mão 2 { $bet2 } total { $total2 }
blackjack-status-dealer = Dealer: { $cards } ({ $total })
blackjack-status-dealer-up = Dealer: mostrando { $card }
blackjack-no-active-players = Nenhum jogador ativo.
blackjack-waiting-for-bets = Aguardando apostas de { $players }.
blackjack-bet-previous-label = Aposta { $amount }
blackjack-end-screen-line = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
blackjack-change-bet = Alterar aposta
