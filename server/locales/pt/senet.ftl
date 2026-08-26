# Senet localization

game-name-senet = Senet

# Game start
senet-game-started = { $p1 } é o jogador 1, { $p2 } é o jogador 2. { $first } começa.

# Throwing sticks
senet-throw-you = Você tira { $result }.{ $bonus ->
    [yes] {" "}Jogada bônus!
   *[no] {""}
}
senet-throw-other = { $player } tira { $result }.{ $bonus ->
    [yes] {" "}Jogada bônus!
   *[no] {""}
}

# Movement
senet-move-you = Você move da casa { $from } para a casa { $to }.
senet-move-other = { $player } move da casa { $from } para a casa { $to }.
senet-swap-you = Você troca de lugar com { $opponent } na casa { $to }. { $opponent } volta para a casa { $from }.
senet-swap-other = { $player } troca de lugar com { $opponent } na casa { $to }. { $opponent } volta para a casa { $from }.
senet-bearoff-you = Você retira sua peça da casa { $from }. Restam { $remaining }.
senet-bearoff-other = { $player } retira a peça da casa { $from }. Restam { $remaining }.
senet-water-you = Você caiu na Casa da Água! Peça enviada para a casa { $dest }.
senet-water-other = { $player } caiu na Casa da Água! Peça enviada para a casa { $dest }.
senet-happiness-you = Você chegou à Casa da Felicidade.
senet-happiness-other = { $player } chegou à Casa da Felicidade.
senet-horus-auto-you = Sua peça sai da Casa de Hórus porque sua primeira fileira está livre. Restam { $remaining }.
senet-horus-auto-other = A peça de { $player } sai da Casa de Hórus porque a primeira fileira dela está livre. Restam { $remaining }.

# No moves
senet-no-moves-you = Você não tem movimentos possíveis.
senet-no-moves-other = { $player } não tem movimentos possíveis.

# Square labels
senet-sq-empty = { $sq }
senet-sq-own = { $sq }, sua
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }, sua
senet-sq-opponent-special = { $sq }, { $name }, { $owner }

# Special square names
senet-house-rebirth = Renascimento
senet-house-happiness = Felicidade
senet-house-water = Água
senet-house-three-truths = Três Verdades
senet-house-re-atum = Ré-Atum
senet-house-horus = Hórus

# Status
senet-status = { $p1 }: { $off1 } fora. { $p2 }: { $off2 } fora.{ $phase ->
    [throwing] {" "}Aguardando o lançamento.
   *[moving] {" "}Tirada: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = Nenhum lançamento ainda.

# Win
senet-wins-you = Você venceu! Todas as suas peças atravessaram a última casa.
senet-wins-other = { $player } venceu! Todas as peças desse jogador atravessaram a última casa.

# Action labels
senet-check-status = Status
senet-check-sticks = Gravetos
senet-next-piece = Próxima peça
senet-previous-piece = Peça anterior
senet-score-line = { $player }: { $off } fora.

# Errors
senet-not-your-piece = Essa peça não é sua.
senet-no-piece-there = Não há peça nesse lugar.
senet-no-moves-from-here = Nenhum movimento possível a partir desta casa.
senet-need-throw-first = Você precisa lançar os gravetos antes de escolher uma peça para mover.
senet-no-movable-pieces = Nenhuma das suas peças pode mover com esta tirada.
senet-error-exactly-two-players = O Senet exige exatamente 2 jogadores ativos. Jogadores ativos atualmente: { $count }.

# Options
senet-option-bot-difficulty = Dificuldade do bot: { $bot_difficulty }
senet-option-select-bot-difficulty = Selecionar dificuldade do bot
senet-option-changed-bot-difficulty = Dificuldade do bot definida para { $bot_difficulty }.
senet-desc-bot-difficulty = Define como os bots de Senet jogam: Aleatório joga de forma solta, enquanto Simples prefere jogadas táticas mais seguras.
senet-difficulty-random = Aleatório
senet-difficulty-simple = Simples
