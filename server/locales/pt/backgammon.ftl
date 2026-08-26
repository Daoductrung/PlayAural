# Backgammon localization

game-name-backgammon = Gamão

# Colors
backgammon-color-red = vermelho
backgammon-color-white = branco

# Game start
backgammon-game-started = { $red } joga com Vermelho, { $white } joga com Branco.
backgammon-opening-roll = Rolagem inicial: { $red } tirou { $red_die }, { $white } tirou { $white_die }.
backgammon-opening-tie = Ambos tiraram { $die }, rolando novamente.
backgammon-opening-winner-you = Você começa com { $die1 } e { $die2 }.
backgammon-opening-winner-player = { $player } começa com { $die1 } e { $die2 }.

# Dice
backgammon-roll-you = Você tirou { $die1 } e { $die2 }.
backgammon-roll-player = { $player } tirou { $die1 } e { $die2 }.

# No moves
backgammon-no-moves-you = Você não tem jogadas válidas, então seu turno termina.
backgammon-no-moves-player = { $player } não tem jogadas válidas, então o turno dele termina.

# Brief move commentary
backgammon-brief-move-normal = { $is_self ->
    [yes] Você: { $src } para { $dest }.
    *[no] { $player }: { $src } para { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] Você: { $src } para { $dest }, capturou { $opponent }.
    [spectator] { $player }: { $src } para { $dest }, capturou { $opponent }.
    *[no] { $player }: { $src } para { $dest }, capturou você.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] Você: barra para { $dest }.
    *[no] { $player }: barra para { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] Você: barra para { $dest }, capturou { $opponent }.
    [spectator] { $player }: barra para { $dest }, capturou { $opponent }.
    *[no] { $player }: barra para { $dest }, capturou você.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] Você: retirou { $src }.
    *[no] { $player }: retirou { $src }.
}

# Verbose move commentary
backgammon-verbose-move-normal = { $is_self ->
    [yes] Você move uma dama da ponta { $src } para a ponta { $dest }.
    *[no] { $player } move uma dama da ponta { $src } para a ponta { $dest }.
} { $src_count ->
    [0] A ponta { $src } agora está vazia, há { $dest_count } na ponta { $dest }.
    *[other] Há { $src_count } agora na ponta { $src }, e { $dest_count } na ponta { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] Você move uma dama da ponta { $src } para capturar a dama de { $opponent } na ponta { $dest }.
    [spectator] { $player } move uma dama da ponta { $src } para capturar a dama de { $opponent } na ponta { $dest }.
    *[no] { $player } move uma dama da ponta { $src } para capturar a sua dama na ponta { $dest }.
} { $src_count ->
    [0] A ponta { $src } agora está vazia.
    *[other] Restam { $src_count } na ponta { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] Você entra da barra para a ponta { $dest }.
    *[no] { $player } entra da barra para a ponta { $dest }.
} { $dest_count } agora na ponta { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] Você entra da barra para capturar a dama de { $opponent } na ponta { $dest }.
    [spectator] { $player } entra da barra para capturar a dama de { $opponent } na ponta { $dest }.
    *[no] { $player } entra da barra para capturar a sua dama na ponta { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] Você retira uma dama da ponta { $src }.
    *[no] { $player } retira uma dama da ponta { $src }.
} { $src_count ->
    [0] A ponta { $src } agora está vazia.
    *[other] Restam { $src_count } na ponta { $src }.
}

# Doubling
backgammon-doubles-you = Você oferece dobrar o cubo para { $value }.
backgammon-doubles-player = { $player } oferece dobrar o cubo para { $value }.
backgammon-accepts-you = Você aceita o dobro e assume a posse do cubo.
backgammon-accepts-player = { $player } aceita o dobro e assume a posse do cubo.
backgammon-drops-you = Você rejeita o dobro e concede o valor atual do cubo.
backgammon-drops-player = { $player } rejeita o dobro e concede o valor atual do cubo.
backgammon-accept = Aceitar
backgammon-drop = Rejeitar

# Point labels
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } selecionada
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } selecionada

# Action labels
backgammon-label-double = Dobrar
backgammon-label-undo = Desfazer
backgammon-label-deselect = Desselecionar
backgammon-label-next-destination = Próximo destino
backgammon-label-previous-destination = Destino anterior

# Selection feedback
backgammon-no-checkers-there = Não há damas lá.
backgammon-not-your-checkers = Essas damas não são suas.
backgammon-no-moves-from-here = Nenhuma jogada válida a partir daqui.
backgammon-must-enter-from-bar = Deve entrar da barra primeiro.
backgammon-illegal-move = Jogada ilegal.
backgammon-no-dice-remaining = Você não tem dados restantes para usar neste turno.
backgammon-no-checkers-on-bar = Você não tem damas na barra para entrar.
backgammon-invalid-destination = Esse destino não é uma ponta de gamão válida.
backgammon-source-empty = A ponta { $point } não tem damas para mover.
backgammon-source-opponent = A ponta { $point } contém as damas do seu oponente.
backgammon-destination-blocked = A ponta { $point } está bloqueada por { $count } damas oponentes.
backgammon-bar-entry-blocked = Você não pode entrar na ponta { $point }; ela está bloqueada por { $count } damas oponentes.
backgammon-no-die-for-bar-entry = Nenhum dos seus dados restantes ({ $dice }) entra na ponta { $point }.
backgammon-no-die-for-destination = Nenhum dos seus dados restantes ({ $dice }) move da ponta { $src } para a ponta { $dest }.
backgammon-must-use-forced-die = Você deve usar { $dice } agora porque o gamão exige ambos os dados quando possível, ou o maior dado quando apenas um pode ser jogado.
backgammon-bearoff-blocked = Você não pode retirar damas da ponta { $point } com um { $die }, porque há damas na sua ponta { $blocking_point }.
backgammon-bearoff-no-die = Você não pode retirar damas da ponta { $point } com seus dados restantes ({ $die }).
backgammon-nothing-to-undo = Nada para desfazer.
backgammon-undone = Jogada desfeita.
backgammon-cannot-double = Você não pode dobrar agora.
backgammon-cannot-undo = Nada para desfazer.
backgammon-not-doubling-phase = Nenhum dobro para responder.
backgammon-need-roll-first = Você precisa rolar os dados antes de mover uma dama.

# Info keybinds
backgammon-check-status = Status
backgammon-check-cube = Cubo
backgammon-check-pip = Contagem de pips
backgammon-check-score = Placar
backgammon-check-score-detailed = Placar detalhado
backgammon-check-dice = Dados
backgammon-dice = { $dice }
backgammon-dice-none = Sem dados.
backgammon-cube-status = Cubo em { $value }. { $owner ->
    [center] Centralizado, qualquer jogador pode dobrar.
    *[other] Pertence a { $owner }.
} { $can_double ->
    [yes] O dobro está disponível agora.
    [crawford] Esta é uma partida Crawford, dobrar não é permitido.
    *[no] O dobro não está disponível agora.
}
backgammon-cube-no-match = Sem cubo de dobro em partidas únicas.
backgammon-pip-count = Contagem de pips vermelha: { $red_pip }. Contagem de pips branca: { $white_pip }.
backgammon-match-score-line = { $player }: { $score } de { $match_length }.
backgammon-match-score-cube-line = Cubo: { $cube }.

# Scoring
backgammon-wins-game-you = Você ganha { $points } ponto{ $points ->
    [one] {""}
    *[other] s
}.
backgammon-wins-game-player = { $player } ganha { $points } ponto{ $points ->
    [one] {""}
    *[other] s
}.
backgammon-new-game = Iniciando partida { $number }.
backgammon-match-winner-you = Você venceu a disputa!
backgammon-match-winner-player = { $player } venceu a disputa!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. Disputa até { $match_length }.
backgammon-crawford = Partida Crawford: sem dobro nesta partida.

# Difficulty levels
backgammon-difficulty-random = Aleatório
backgammon-difficulty-simple = Simples

# Options
backgammon-option-match-length = Comprimento da disputa: { $match_length }
backgammon-option-select-match-length = Definir comprimento da disputa (1-25)
backgammon-option-changed-match-length = Comprimento da disputa definido para { $match_length }.
backgammon-desc-match-length = Pontos necessários para vencer a disputa de Gamão. O valor 1 é uma partida única sem cubo de dobro (padrão 1, intervalo de 1 a 25).
backgammon-option-bot-difficulty = Dificuldade do bot: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Selecionar dificuldade do bot
backgammon-option-changed-bot-difficulty = Dificuldade do bot definida para { $bot_difficulty }.
backgammon-desc-bot-difficulty = Escolhe como os bots fazem jogadas: Aleatório faz jogadas válidas livremente, enquanto Simples prefere jogadas táticas mais fortes.
