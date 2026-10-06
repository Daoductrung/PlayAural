game-name-zombiedice = Zombie Dice

zombiedice-set-target-score = Cérebros necessários para vencer: { $score }
zombiedice-enter-target-score = Digite um objetivo de vitória de 5 a 50 cérebros:
zombiedice-option-changed-target-score = O objetivo de vitória agora é de { $score } cérebros.
zombiedice-desc-target-score = Alcançar esta pontuação inicia a rodada final para quem ainda não jogou. O objetivo oficial é de 13 cérebros; objetivos menores ou maiores deixam a partida mais curta ou mais longa.

zombiedice-roll-first = Rolar 3 dados
zombiedice-roll-first-description = Tire três dados escondidos do tubo e role-os.
zombiedice-roll-again = Rolar novamente — { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
} em jogo
zombiedice-roll-again-description = Role novamente { $footprints } { $footprints ->
    [one] dado com pegada
   *[other] dados com pegadas
} e tire { $draw } { $draw ->
    [one] dado novo
   *[other] dados novos
} até completar três. Uma terceira espingarda elimina os { $brains } { $brains ->
    [one] cérebro não garantido
   *[other] cérebros não garantidos
}.
zombiedice-bank = Parar e marcar { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}
zombiedice-bank-keybind = Parar e marcar pontos
zombiedice-bank-description = Encerre sua vez e garanta { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}.
zombiedice-check-turn-totals = Ver totais da vez
zombiedice-check-turn-totals-description = Ouça os cérebros, as espingardas e as pegadas atuais.
zombiedice-review-turn = Rever vez atual
zombiedice-review-turn-description = Reveja todos os dados públicos, a quantidade no tubo, a última rolagem e os cérebros não garantidos.
zombiedice-review-table = Rever mesa
zombiedice-review-table-description = Reveja o objetivo, a fase da partida, a ordem das jogadas, a vez atual e as pontuações.

zombiedice-game-start = Começa o Zombie Dice. Objetivo: { $target } cérebros. { $first } joga primeiro. Ordem: { $order }.
zombiedice-your-turn = Sua vez. Garantidos: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}. Role três dados.
zombiedice-player-turn = Vez de { $player }. Garantidos: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.
zombiedice-you-refill-cup = Restam poucos dados no tubo: você devolve { $count } { $count ->
    [one] dado com cérebro
   *[other] dados com cérebros
}. { $brains ->
    [one] Sua contagem nesta vez continua em { $brains } cérebro.
   *[other] Sua contagem nesta vez continua em { $brains } cérebros.
}
zombiedice-player-refills-cup = Restam poucos dados no tubo: { $player } devolve { $count } { $count ->
    [one] dado com cérebro
   *[other] dados com cérebros
}. { $brains ->
    [one] A contagem de { $player } nesta vez continua em { $brains } cérebro.
   *[other] A contagem de { $player } nesta vez continua em { $brains } cérebros.
}
zombiedice-you-roll = Você rola: { $results }.
zombiedice-player-rolls = { $player } rola: { $results }.
zombiedice-you-bust = Você rola: { $results }. { $shotguns } espingardas — você foi alvejado. Você perde { $brains } { $brains ->
    [one] cérebro não garantido
   *[other] cérebros não garantidos
}.
zombiedice-player-busts = { $player } rola: { $results }. { $shotguns } espingardas — { $player } foi alvejado. { $player } perde { $brains } { $brains ->
    [one] cérebro não garantido
   *[other] cérebros não garantidos
}.
zombiedice-you-bank = Você garante { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}. Total: { $total }.
zombiedice-player-banks = { $player } garante { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}. Total: { $total }.
zombiedice-you-trigger-final-round = Você alcança { $score } cérebros. { $remaining ->
    [one] Resta 1 jogador
   *[other] Restam { $remaining } jogadores
} na rodada final.
zombiedice-player-triggers-final-round = { $player } alcança { $score } cérebros. { $remaining ->
    [one] Resta 1 jogador
   *[other] Restam { $remaining } jogadores
} na rodada final.
zombiedice-tiebreak-start = Desempate { $round }: { $players }, empatados com { $score } cérebros. Uma vez para cada um.
zombiedice-you-win = Você vence Zombie Dice com { $score } cérebros.
zombiedice-player-wins = { $player } vence Zombie Dice com { $score } cérebros.

zombiedice-error-roll-before-stopping = Role uma vez antes de parar. Depois de qualquer rolagem segura, é permitido parar com 0 cérebros.
zombiedice-error-roll-resolving = Os dados ainda estão rolando.
zombiedice-error-target-score-range = O objetivo de vitória deve estar entre { $min } e { $max } cérebros; o valor atual é { $value }.

zombiedice-color-green = verde
zombiedice-color-yellow = amarelo
zombiedice-color-red = vermelho
zombiedice-face-brain = cérebro
zombiedice-face-footprint = pegada
zombiedice-face-shotgun = espingarda
zombiedice-roll-result = { $color }, { $face }
zombiedice-pool-color = { $count } { $count ->
    [one] dado { $color }
   *[other] dados { $color }
}
zombiedice-no-dice = nenhum

zombiedice-status-no-turn = Nenhuma vez de Zombie Dice está ativa.
zombiedice-your-turn-totals = Você: { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}, { $shotguns } { $shotguns ->
    [one] espingarda
   *[other] espingardas
} e { $footprints } { $footprints ->
    [one] pegada
   *[other] pegadas
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}, { $shotguns } { $shotguns ->
    [one] espingarda
   *[other] espingardas
} e { $footprints } { $footprints ->
    [one] pegada
   *[other] pegadas
}.
zombiedice-status-turn-you = Sua vez — garantidos: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.
zombiedice-status-turn-player = Vez de { $player } — garantidos: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.
zombiedice-status-turn-totals = Nesta vez: { $brains } { $brains ->
    [one] cérebro
   *[other] cérebros
}, { $shotguns } { $shotguns ->
    [one] espingarda
   *[other] espingardas
} e { $footprints } { $footprints ->
    [one] pegada
   *[other] pegadas
}.
zombiedice-status-cup = Tubo: { $count } { $count ->
    [one] dado
   *[other] dados
}.
zombiedice-status-footprints = Pegadas para rolar novamente: { $dice }.
zombiedice-status-brain-dice = Dados com cérebros separados: { $dice }.
zombiedice-status-shotgun-dice = Dados com espingardas separados: { $dice }.
zombiedice-status-last-roll = Última rolagem: { $results }.
zombiedice-status-awaiting-roll = Ainda não houve nenhuma rolagem nesta vez.
zombiedice-status-table-header = Zombie Dice — rodada { $round }; objetivo: { $target } cérebros.
zombiedice-status-table-header-tiebreak = Zombie Dice — objetivo: { $target } cérebros.
zombiedice-status-main-round = Fase: partida principal.
zombiedice-status-final-round = Rodada final — { $player } alcançou o objetivo.
zombiedice-status-tiebreak = Desempate { $round }: { $players }.
zombiedice-status-current-you = Sua vez.
zombiedice-status-current-player = Vez de { $player }.
zombiedice-status-turn-order = Ordem das jogadas: { $players }.
zombiedice-status-score-you = Você: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.

zombiedice-score-unit-brains = { $count ->
    [one] cérebro
   *[other] cérebros
}
zombiedice-results-header = Resultados de Zombie Dice
zombiedice-results-winner = Vencedor: { $player } com { $score } cérebros.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] cérebro
   *[other] cérebros
}.
