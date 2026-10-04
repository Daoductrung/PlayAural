game-name-flip7 = Flip 7

# Opções
flip7-set-target-score = Pontuação-alvo: { $score }
flip7-enter-target-score = Digite a pontuação-alvo
flip7-option-changed-target = Pontuação-alvo definida como { $score }.
flip7-desc-target-score = Quantos pontos são necessários para vencer a partida. Padrão: 200, intervalo 50-1000.

# Cartas
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Dobro
flip7-card-second-chance = Segunda Chance
flip7-card-freeze = Congelar
flip7-card-flip-three = Vira 3

# Ações da vez
flip7-hit = Vire uma carta
flip7-stay = Pare e garanta { $points } pontos
flip7-stay-base = Pare e garanta
flip7-stay-banked = Pare e garanta (pontos já garantidos)
flip7-you-stay = Você para e garante { $points } pontos.
flip7-player-stays = { $player } para e garante { $points } pontos.

# Rodada
flip7-round-start = Rodada { $round }. { $dealer } distribui.
flip7-round-end = A rodada { $round } terminou.
flip7-round-end-deck = O baralho acabou. A rodada terminou.
flip7-round-score = { $player } garante { $points } pontos, total de { $total }.
flip7-round-score-you = Você garante { $points } pontos, total de { $total }.
flip7-round-bust = { $player } estourou e não pontua nada.
flip7-round-bust-you = Você estourou e não pontua nada nesta rodada.
flip7-match-win = { $player } venceu a partida!
flip7-match-win-you = Você venceu a partida!
flip7-deck-reshuffled = O descarte foi re-embaralhado para formar o baralho.
flip7-you-pending-discarded = Você não está mais jogando nesta rodada, então suas cartas de ação guardadas são descartadas.
flip7-player-pending-discarded = { $player } não está mais jogando nesta rodada, então as cartas de ação guardadas são descartadas.
flip7-you-pending-bust-discarded = Você estourou, então suas cartas de ação guardadas são descartadas.
flip7-player-pending-bust-discarded = { $player } estourou, então as cartas de ação guardadas são descartadas.

# Vindo cartas
flip7-you-turn-card = Você vira uma carta.
flip7-player-turns-card = { $player } vira uma carta.
flip7-your-card-is = Carta: { $card }.
flip7-player-card-is = Carta de { $player }: { $card }.
flip7-you-stop-alone = Como só você continuava jogando, parou e garantiu { $points } pontos.
flip7-player-stops-alone = Como só { $player } continuava jogando, parou e garantiu { $points } pontos.
flip7-you-set-second-chance = Você guarda uma Segunda Chance.
flip7-player-sets-second-chance = { $player } guarda uma Segunda Chance.
flip7-second-chance-saves = A Segunda Chance salva { $player } do { $value } repetido.
flip7-second-chance-saves-you = A Segunda Chance salva você do { $value } repetido.
flip7-you-bust = Você virou { $value } de novo e estourou. A rodada é perdida para você.
flip7-player-busts = { $player } virou { $value } de novo e estourou.
flip7-flip-seven = { $player } fez o Flip 7 e ganha o bônus de 15 pontos!
flip7-flip-seven-you = Você fez o Flip 7 e ganha o bônus de 15 pontos!

# Escolhas com alvo
flip7-target-freeze = Faça { $target } congelar ({ $points } pontos)
flip7-target-flip-three = Faça { $target } virar 3 cartas
flip7-target-second-chance = Dê uma Segunda Chance para { $target }
flip7-you-stop-player = Você faz { $target } congelar com { $points } pontos.
flip7-player-stops-player = { $player } faz { $target } congelar com { $points } pontos.
flip7-you-stop-yourself = Você para e garante { $points } pontos.
flip7-player-stops-themself = { $player } para e garante { $points } pontos.
flip7-you-flip-three = Você faz { $target } virar 3 cartas.
flip7-player-flip-three = { $player } faz { $target } virar 3 cartas.
flip7-you-flip-three-self = Você vira 3 cartas.
flip7-player-flips-three-self = { $player } vira 3 cartas.
flip7-you-give-second-chance = Você dá uma Segunda Chance para { $target }.
flip7-player-gives-second-chance = { $player } dá uma Segunda Chance para { $target }.
flip7-you-discard-second-chance = Ninguém pode receber, então a Segunda Chance é descartada.
flip7-player-discards-second-chance = { $player } não pode entregar a Segunda Chance, então ela é descartada.
flip7-you-discard-action = Não há ninguém para atingir, então { $action } é descartada.
flip7-player-discards-action = { $player } não tem ninguém para atingir, então { $action } é descartada.

# Ações de informação
flip7-check-area = Verificar minha área
flip7-check-table = Verificar a mesa
flip7-check-deck = Verificar o baralho
flip7-you-label = Você
flip7-area-status-stayed = , parou nesta rodada
flip7-area-status-busted = , estourou nesta rodada
flip7-area-numbers-none = Nenhuma carta de número ainda
flip7-area-inline = { $who }{ $status }: { $numbers }. Total { $points } pontos.
flip7-area-inline-with-bonuses = { $who }{ $status }: { $numbers }. Total { $points } pontos. Bônus: { $bonuses }.
flip7-check-round = Rodada { $round }. Pontuação-alvo { $target }.
flip7-status-playing = ainda jogando
flip7-status-stayed = parou
flip7-status-busted = estourou
flip7-table-line = { $player }: { $status }, { $points } nesta rodada, { $total } no total
flip7-deck-line = Baralho: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }
flip7-discard-line = Descarte: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }

# Motivos de bloqueio
flip7-error-wait-card = Espere a carta revelada ser resolvida.
flip7-error-wait-choice = Espere a escolha de carta atual ser resolvida.
flip7-error-wait-flip-three = Espere o Vira 3 terminar.
flip7-error-wait-dealing = Espere a distribuição das cartas terminar.
flip7-error-not-playing-round = Você não está mais jogando nesta rodada.
flip7-error-no-cards-left = Não há mais cartas para virar.
flip7-error-no-cards-to-bank = Você ainda não tem cartas para garantir.
flip7-error-no-choice = Não há escolha de carta para responder.

# Tela final
flip7-line-format = { $rank }. { $player }: { $points }
