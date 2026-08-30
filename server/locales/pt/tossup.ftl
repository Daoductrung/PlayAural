game-name-tossup = Dados ao Voo

tossup-roll-first =
    Rolar { $count } { $count ->
        [one] dado
       *[other] dados
    }
tossup-roll-remaining =
    Rolar os { $count } { $count ->
        [one] dado
       *[other] dados
    } restantes
tossup-bank =
    Guardar { $points } { $points ->
        [one] ponto
       *[other] pontos
    }
tossup-check-turn-status = Verificar status do turno

tossup-game-start = O Toss Up começa com as regras { $rules }, { $dice } dados por conjunto e um limite-alvo de { $target }. Supere o limite e complete os turnos restantes para vencer.
tossup-game-start-brief = O Toss Up começa. Supere { $target }.
tossup-round-start = Começa a rodada { $round }.
tossup-round-start-brief = Rodada { $round }.

tossup-your-turn =
    Seu turno. Seus pontos guardados são { $score }; role { $dice } { $dice ->
        [one] dado
       *[other] dados
    } para começar.
tossup-player-turn =
    Turno de { $player } com { $score } pontos guardados e { $dice } { $dice ->
        [one] dado
       *[other] dados
    }.
tossup-your-turn-brief = Seu turno: { $score } pontos.
tossup-player-turn-brief = Turno de { $player }: { $score } pontos.

tossup-you-roll = Você tirou { $results }.
tossup-player-rolls = { $player } tirou { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] Você: { $results }; total do turno { $turn_points }; novo conjunto de { $dice_count }.
       *[no] Você: { $results }; total do turno { $turn_points }; restam { $dice_count }.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; total do turno { $turn_points }; novo conjunto de { $dice_count }.
       *[no] { $player }: { $results }; total do turno { $turn_points }; restam { $dice_count }.
    }

tossup-result-green = { $count } verdes
tossup-result-yellow = { $count } amarelos
tossup-result-red = { $count } vermelhos

tossup-you-have-points =
    Você reservou { $gained } { $gained ->
        [one] dado verde
       *[other] dados verdes
    }. Seu total no turno é { $turn_points }, com { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } restantes.
tossup-player-has-points =
    { $player } reserva { $gained } { $gained ->
        [one] dado verde
       *[other] dados verdes
    } e tem { $turn_points } pontos no turno, com { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } restantes.

tossup-you-get-fresh = Todos os dados são verdes. Você recebe um novo conjunto de { $count } dados e pode rolar novamente ou guardar.
tossup-player-gets-fresh = Todos os dados são verdes. { $player } recebe um novo conjunto de { $count } dados.

tossup-you-bust =
    { $variant ->
        [Standard] Luz vermelha: você não tirou nenhum verde e tirou pelo menos um vermelho. Seu turno termina e você perde { $points } pontos não guardados.
       *[PlayAural] Todos os dados rolados são vermelhos. Seu turno termina e você perde { $points } pontos não guardados.
    }
tossup-player-busts =
    { $variant ->
        [Standard] Luz vermelha: { $player } não tirou nenhum verde e tirou pelo menos um vermelho, encerrando o turno e perdendo { $points } pontos não guardados.
       *[PlayAural] Todos os dados rolados de { $player } são vermelhos, encerrando o turno e perdendo { $points } pontos não guardados.
    }
tossup-you-bust-brief = Você: { $results }; estourou; perde { $points }.
tossup-player-busts-brief = { $player }: { $results }; estourou; perde { $points }.

tossup-you-bank = Você guarda { $points } pontos, chegando a um total de { $total }.
tossup-player-banks = { $player } guarda { $points } pontos, chegando a um total de { $total }.
tossup-you-bank-brief = Você guarda { $points }; total { $total }.
tossup-player-banks-brief = { $player } guarda { $points }; total { $total }.

tossup-you-trigger-final-turns =
    Você supera o limite de { $target } pontos com { $score }.
    { $count ->
        [one] O jogador restante recebe um turno final.
       *[other] Os { $count } jogadores restantes recebem cada um um turno final.
    }
tossup-player-triggers-final-turns =
    { $player } supera o limite de { $target } pontos com { $score }.
    { $count ->
        [one] O jogador restante recebe um turno final.
       *[other] Os { $count } jogadores restantes recebem cada um um turno final.
    }
tossup-you-trigger-final-turns-brief =
    Você define a pontuação a bater em { $score }; { $count } { $count ->
        [one] turno resta.
       *[other] turnos restam.
    }
tossup-player-triggers-final-turns-brief =
    { $player } define a pontuação a bater em { $score }; { $count } { $count ->
        [one] turno resta.
       *[other] turnos restam.
    }

tossup-you-win = Você vence o Toss Up com { $score } pontos.
tossup-winner = { $player } vence o Toss Up com { $score } pontos.
tossup-you-win-brief = Você vence: { $score }.
tossup-winner-brief = { $player } vence: { $score }.
tossup-tie-tiebreaker = { $players } empatam na maior pontuação acima do alvo. Apenas esses jogadores seguem para a rodada de desempate.
tossup-tie-tiebreaker-brief = Desempate: { $players }.
tossup-tiebreaker-round-start = Começa a rodada de desempate { $round } para { $players }.
tossup-tiebreaker-round-start-brief = Rodada de desempate { $round }: { $players }.

tossup-your-turn-awaiting-roll =
    Seu turno ainda não começou a rolar. Você tem { $score } pontos guardados e { $dice_count } { $dice_count ->
        [one] dado pronto
       *[other] dados prontos
    }.
tossup-player-turn-awaiting-roll =
    { $player } ainda não rolou. Tem { $score } pontos guardados e { $dice_count } { $dice_count ->
        [one] dado pronto
       *[other] dados prontos
    }.
tossup-your-turn-status =
    Sua última tirada foi { $results }. Você tem { $turn_points } pontos de turno não guardados, { $score } pontos guardados e { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } prontos para rolar.
tossup-player-turn-status =
    Última tirada de { $player }: { $results }. Tem { $turn_points } pontos de turno não guardados, { $score } pontos guardados e { $dice_count } { $dice_count ->
        [one] dado
       *[other] dados
    } prontos para rolar.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] Guardar agora colocaria você na frente, com { $total } pontos acima do limite de { $target } pontos.
       *[no] Você tem atualmente { $points } pontos de turno não guardados.
    }
    Rolar { $dice } { $dice ->
        [one] dado
       *[other] dados
    } tem cerca de { $risk } por cento de chance de estouro. Pressione Rolar novamente dentro de { $seconds } segundos para confirmar, ou guarde para proteger os pontos.

tossup-set-rules-variant = Regras: { $variant }
tossup-select-rules-variant = Selecionar as regras de dados e estouro:
tossup-option-changed-rules = Regras alteradas para { $variant }.
tossup-desc-rules-variant = O clássico usa três faces verdes, duas amarelas e uma vermelha por dado; uma tirada sem verde e com pelo menos um vermelho é estouro. O tolerante dá chances iguais às três cores e só estoura quando todos são vermelhos.

tossup-desc-target-score = O jogo entra nos turnos finais de resposta depois que um jogador guarda mais do que esta pontuação (padrão 100, intervalo de 20 a 500).
tossup-set-starting-dice = Dados por conjunto: { $count }
tossup-enter-starting-dice = Digite o número de dados de cada novo conjunto:
tossup-option-changed-dice = Dados por conjunto alterados para { $count }.
tossup-desc-starting-dice = Escolhe quantos dados começam cada turno e retornam depois que todos ficarem verdes (padrão 10, intervalo de 5 a 20).


tossup-rules-standard = Clássico
tossup-rules-PlayAural = Tolerante
tossup-rules-standard-desc = Três faces verdes, duas amarelas e uma vermelha. Estouro sem nenhum verde e com pelo menos um vermelho.
tossup-rules-PlayAural-desc = Chances iguais para as três cores. Só estoura quando todos os dados rolados forem vermelhos.

tossup-error-roll-not-playing = Você não pode rolar porque o Toss Up não está em andamento.
tossup-error-roll-no-turn = Você não pode rolar porque o Toss Up não tem um turno ativo agora.
tossup-error-roll-not-your-turn = Você não pode rolar durante o turno de { $player }. Aguarde a vez chegar a você.
tossup-error-bank-not-playing = Você não pode guardar porque o Toss Up não está em andamento.
tossup-error-bank-no-turn = Você não pode guardar porque o Toss Up não tem um turno ativo agora.
tossup-error-bank-not-your-turn = Você não pode guardar durante o turno de { $player }. Aguarde a vez chegar a você.
tossup-error-bank-roll-first = Role pelo menos uma vez antes de guardar. Uma tirada toda amarela pode ser guardada com zero pontos para encerrar seu turno.
tossup-error-spectator-action = Espectadores podem verificar o status público do Toss Up, mas não podem rolar nem guardar pontos.
tossup-error-status-not-playing = O status do turno está indisponível porque o Toss Up não está em andamento.
tossup-error-status-no-turn = O status do turno está indisponível porque o Toss Up não tem um jogador ativo agora.
tossup-error-target-out-of-range = O limite-alvo é { $value }; deve ser de { $min } a { $max } pontos.
tossup-error-dice-out-of-range = O tamanho do novo conjunto é { $value }; deve ser de { $min } a { $max } dados.
tossup-error-rules-variant = O valor de regras “{ $variant }” não é suportado. Escolha Clássico ou Tolerante.

tossup-line-format = { $rank }. { $player }: { $points }
