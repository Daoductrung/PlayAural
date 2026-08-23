game-name-pig = Pig
pig-desc-team-mode = Jogue individualmente ou em uma organização de equipes suportada. Uma equipe compartilha uma pontuação e vence imediatamente quando um membro possui pontos suficientes.

pig-roll = Rolar o dado
pig-hold = Guardar { $points } pontos
pig-check-turn-status = Verificar status do turno

pig-game-start =
    Pig começa. O primeiro { $team ->
        [yes] time
       *[no] jogador
    } a guardar { $target } pontos vence. O dado tem { $sides } lados, e rolar um 1 perde cada ponto não guardado daquele turno. { $minimum ->
        [0] Você pode guardar após qualquer rolagem pontuada.
       *[other] Você deve acumular pelo menos { $minimum } pontos de turno antes de guardar.
    }
pig-game-start-brief =
    Pig começa. Alvo: { $target }. Dado: { $sides } lados. Guarda mínima: { $minimum }.{ $team ->
        [yes] Equipes compartilham pontuações.
       *[no] Pontuações individuais.
    }
pig-round-start = A rodada { $round } começa. Cada jogador ativo fará um turno.
pig-round-start-brief = Rodada { $round }.

pig-you-roll-result = Você rolou { $roll }. O total do seu turno agora é { $total } pontos.
pig-player-roll-result = { $player } rolou { $roll }. O total do turno dele agora é { $total } pontos.
pig-you-roll-result-brief = Você: { $roll }; total do turno { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; total do turno { $total }.

pig-you-bust = Você rolou um 1 e perde todos os { $points } pontos não guardados. Seu turno termina sem pontuação.
pig-player-busts = { $player } rolou um 1 e perde todos os { $points } pontos não guardados. O turno dele termina sem pontuação.
pig-you-bust-brief = Você rolou 1 e perde { $points } pontos de turno.
pig-player-busts-brief = { $player } rolou 1 e perde { $points } pontos de turno.

pig-you-hold =
    Você guarda { $points } pontos. { $team ->
        [yes] Sua equipe agora tem { $total } pontos.
       *[no] Sua pontuação total agora é { $total } pontos.
    }
pig-player-holds =
    { $player } guarda { $points } pontos. { $team ->
        [yes] { $team_name } agora tem { $total } pontos.
       *[no] A pontuação total dele agora é { $total } pontos.
    }
pig-you-hold-brief =
    Você guarda { $points };{ $team ->
        [yes] total da equipe { $team_name } { $total }.
       *[no] seu total { $total }.
    }
pig-player-holds-brief =
    { $player } guarda { $points };{ $team ->
        [yes] total da equipe { $team_name } { $total }.
       *[no] total { $total }.
    }

pig-you-win =
    { $team ->
        [yes] Sua equipe, { $winner }, é a vencedora de Pig com { $score } pontos!
       *[no] Você é o vencedor de Pig com { $score } pontos!
    }
pig-winner =
    { $team ->
        [yes] O vencedor é { $winner }, com { $score } pontos!
       *[no] O vencedor é { $winner }, com { $score } pontos!
    }
pig-you-win-brief =
    { $team ->
        [yes] Vencedor: sua equipe, { $winner }, com { $score }.
       *[no] Vencedor: você, com { $score }.
    }
pig-winner-brief = Vencedor: { $winner }, com { $score }.

pig-confirm-risky-roll =
    Rolar novamente coloca { $points } pontos não guardados em risco, com uma chance de { $risk }% de perdê-los. { $winning ->
        [yes] Guardar agora lhe daria { $total } pontos e venceria o jogo.
       *[no] Guardar agora lhe daria { $total } dos { $target } pontos necessários para vencer.
    } Pressione Rolar novamente em até { $seconds } segundos para confirmar.

pig-action-resolving = O dado ainda está rolando. Aguarde o resultado.
pig-no-turn-points = Role o dado pelo menos uma vez antes de guardar.
pig-need-more-points = Você tem { $current } pontos de turno, mas esta mesa exige pelo menos { $required } antes de guardar.

pig-desc-target-score = O primeiro jogador ou equipe a guardar esta quantidade de pontos totais vence imediatamente (padrão 100, intervalo de 10 a 1000).
pig-set-min-bank = Guarda mínima: { $points }
pig-set-dice-sides = Lados do dado: { $sides }
pig-enter-min-bank = Digite os pontos de turno mínimos necessários para guardar:
pig-enter-dice-sides = Digite o número de lados do dado:
pig-option-changed-min-bank = Guarda mínima alterada para { $points } pontos.
pig-desc-min-bank = O número de pontos de turno necessários antes que a opção Guardar fique disponível. Defina como 0 para o Pig padrão; deve ficar abaixo da pontuação alvo (padrão 0, intervalo de 0 a 999).
pig-option-changed-dice = O dado agora tem { $sides } lados.
pig-desc-dice-sides = O número de lados no dado único. Rolar 1 sempre perde o total do turno (padrão 6, intervalo de 4 a 20).

pig-error-target-out-of-range = A pontuação alvo { $value } é inválida. Escolha um valor de { $min } a { $max }.
pig-error-min-bank-out-of-range = A guarda mínima { $value } é inválida. Escolha um valor de { $min } a { $max }.
pig-error-dice-sides-out-of-range = Um dado de { $value } lados não é suportado. Escolha de { $min } a { $max } lados.
pig-error-min-bank-too-high = A guarda mínima { $minimum } deve ser menor que a pontuação alvo de { $target }.

pig-status-target = Pontuação alvo: { $target } pontos.
pig-status-round = Rodada atual: { $round }.
pig-status-current-turn = { $player } está jogando: { $banked } guardados, { $turn } neste turno, { $potential } se guardado agora.
pig-status-standing = { $rank }. { $team }: { $score } pontos.

pig-line-format = { $rank }. { $player }: { $points }
