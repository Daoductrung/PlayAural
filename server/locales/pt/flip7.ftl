game-name-flip7 = Flip 7

# Opções
flip7-set-target-score = Pontuação-alvo: { $score }
flip7-enter-target-score = Digite a pontuação-alvo
flip7-option-changed-target = Pontuação-alvo definida como { $score }.
flip7-desc-target-score = A pontuação que inicia a verificação do vencedor ao fim de uma rodada. O maior total vence; um empate na liderança prolonga a partida. Padrão: 200, intervalo 50-1000.

# Cartas
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Dobro
flip7-card-second-chance = Segunda Chance
flip7-card-freeze = Congelar
flip7-card-flip-three = Vira 3

# Ações da vez
flip7-hit = Vire uma carta
flip7-stay = Pare e garanta { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }
flip7-stay-base = Pare e garanta
flip7-stay-banked = Pare e garanta (pontos já garantidos)
flip7-you-stay = Você para e garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stays = { $player } para e garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.

# Rodada
flip7-round-start = Rodada { $round }. { $dealer } distribui.
flip7-round-start-you = Rodada { $round }. Você distribui.
flip7-round-end = A rodada { $round } terminou.
flip7-round-score = { $player } garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }, total de { $total } ponto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-score-you = Você garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }, total de { $total } ponto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-bust = { $player } estourou e não pontua nada.
flip7-round-bust-you = Você estourou e não pontua nada nesta rodada.
flip7-match-win = { $player } venceu a partida!
flip7-match-win-you = Você venceu a partida!
flip7-deck-reshuffled = O descarte foi re-embaralhado para formar o baralho.
flip7-you-pending-bust-discarded = Você estourou, então suas cartas de ação guardadas são descartadas.
flip7-player-pending-bust-discarded = { $player } estourou, então as cartas de ação guardadas são descartadas.

# Vindo cartas
flip7-you-turn-card = Você vira uma carta.
flip7-player-turns-card = { $player } vira uma carta.
flip7-your-card-is = Carta: { $card }.
flip7-player-card-is = Carta de { $player }: { $card }.
flip7-you-stop-alone = Como só você continuava jogando, parou e garantiu { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-alone = Como só { $player } continuava jogando, parou e garantiu { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-set-second-chance = Você guarda uma Segunda Chance.
flip7-player-sets-second-chance = { $player } guarda uma Segunda Chance.
flip7-second-chance-saves = A Segunda Chance salva { $player } do { $value } repetido.
flip7-second-chance-saves-you = A Segunda Chance salva você do { $value } repetido.
flip7-you-bust = Você virou { $value } de novo e estourou. A rodada é perdida para você.
flip7-player-busts = { $player } virou { $value } de novo, estourou e não pontua nesta rodada.
flip7-flip-seven = { $player } fez o Flip 7 e ganha o bônus de { $bonus } pontos!
flip7-flip-seven-you = Você fez o Flip 7 e ganha o bônus de { $bonus } pontos!

# Escolhas com alvo
flip7-choice-required = Escolha um alvo para { $action }.
flip7-target-freeze = Faça { $target } congelar ({ $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    })
flip7-target-flip-three = Faça { $target } virar 3 cartas
flip7-target-second-chance-self = Guardar Segunda Chance
flip7-target-second-chance = Dê uma Segunda Chance para { $target }
flip7-you-stop-player = Você faz { $target } congelar com { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-player = { $player } faz { $target } congelar com { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-stop-yourself = Você para e garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-themself = { $player } para e garante { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
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
flip7-check-area-description = Ouça suas cartas viradas, estado, bônus e total atual da rodada.
flip7-check-table = Verificar a mesa
flip7-check-table-description = Abra uma visão ao vivo da rodada, da fase atual e da área pública e pontuação de cada jogador.
flip7-check-deck = Verificar o baralho
flip7-check-deck-description = Ouça quantas cartas restam no baralho e no descarte.
flip7-check-scores = Verificar pontuações
flip7-review-scores = Pontuações detalhadas
flip7-you-label = Você
flip7-area-status-playing = ainda está jogando
flip7-area-status-scored = pontuou
flip7-area-status-stayed = parou
flip7-area-status-busted = estourou
flip7-area-numbers-none = nenhuma
flip7-area-inline = { $who}, { $status }. Cartas de número: { $numbers }. Pontuação da rodada: { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-inline-with-specials = { $who}, { $status }. Cartas de número: { $numbers }. Outras cartas: { $specials }. Pontuação da rodada: { $points } ponto{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-resolving-card = { $area } Carta em resolução: { $card }.
flip7-check-round = Rodada { $round }. Pontuação-alvo { $target }.
flip7-table-line = { $area } Total da partida: { $total } ponto{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-deck-line = Baralho: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }
flip7-discard-line = Descarte: { $count ->
        [one] { $count } carta
       *[other] { $count } cartas
    }

# Estado da vez e das sequências
flip7-whose-turn-choice-you = Você está escolhendo um alvo para { $action }.
flip7-whose-turn-choice-player = { $player } está escolhendo um alvo para { $action }.
flip7-whose-turn-dealing-you = Rodada { $round }: você está distribuindo.
flip7-whose-turn-dealing-player = Rodada { $round }: { $player } está distribuindo.
flip7-whose-turn-deal-card-you = Rodada { $round }: sua carta inicial está sendo resolvida.
flip7-whose-turn-deal-card-player = Rodada { $round }: a carta inicial de { $player } está sendo resolvida.
flip7-whose-turn-card-you = Sua carta está sendo resolvida.
flip7-whose-turn-card-player = A carta de { $player } está sendo resolvida.
flip7-whose-turn-flip-three-you = Você está virando 3 cartas.
flip7-whose-turn-flip-three-player = { $player } está virando 3 cartas.
flip7-whose-turn-banking-you = Você está parando e garantindo pontos.
flip7-whose-turn-banking-player = { $player } está parando e garantindo pontos.
flip7-whose-turn-round-end = A rodada { $round } está fechando a pontuação.
flip7-whose-turn-match-end = O vencedor está sendo anunciado.
flip7-whose-turn-resolving = Uma sequência de cartas está sendo resolvida.

# Motivos de bloqueio
flip7-error-wait-card = Espere a carta revelada ser resolvida.
flip7-error-make-choice = Escolha um alvo antes de virar outra carta ou parar.
flip7-error-wait-choice = Espere a escolha de carta atual ser resolvida.
flip7-error-wait-flip-three = Espere o Vira 3 terminar.
flip7-error-wait-dealing = Espere a distribuição das cartas terminar.
flip7-error-not-playing-round = Você não está mais jogando nesta rodada.
flip7-error-no-cards-to-bank = Você ainda não tem cartas para garantir.
flip7-error-no-choice = Não há escolha de carta para responder.
flip7-error-wait-banking = Espere os pontos atuais serem garantidos.
flip7-error-choice-not-ready = Espere a escolha de alvo ficar pronta.

# Tela final
flip7-line-format = { $rank }. { $player }: { $points }
