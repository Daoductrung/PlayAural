game-name-yahtzee = Yahtzee

yahtzee-roll = Rolar de novo ({ $count } restantes)
yahtzee-roll-all = Rolar dados

yahtzee-score-ones = 1s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-twos = 2s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-threes = 3s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-fours = 4s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-fives = 5s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-sixes = 6s para { $points } { $points ->
    [one] ponto
   *[other] pontos
}

yahtzee-score-three-kind = Trinca para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-four-kind = Quadra para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-full-house = Full House para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-small-straight = Sequência menor para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-large-straight = Sequência maior para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-yahtzee = Yahtzee para { $points } { $points ->
    [one] ponto
   *[other] pontos
}
yahtzee-score-chance = Chance para { $points } { $points ->
    [one] ponto
   *[other] pontos
}

yahtzee-you-rolled = Você tirou: { $dice }. { $remaining ->
    [0] Escolha uma categoria de pontuação.
   *[other] Restam { $remaining } { $remaining ->
        [one] rolagem
       *[other] rolagens
    }.
}
yahtzee-player-rolled = { $player } tirou: { $dice }. { $remaining ->
    [0] É preciso escolher uma categoria de pontuação.
   *[other] Restam { $remaining } { $remaining ->
        [one] rolagem
       *[other] rolagens
    }.
}
yahtzee-you-rolled-brief = Você tirou: { $dice }.
yahtzee-player-rolled-brief = { $player } tirou: { $dice }.

yahtzee-you-scored = Você marcou { $points } { $points ->
    [one] ponto
   *[other] pontos
} em { $category }.
yahtzee-player-scored = { $player } marcou { $points } { $points ->
    [one] ponto
   *[other] pontos
} em { $category }.
yahtzee-you-scored-brief = { $points } em { $category }.
yahtzee-player-scored-brief = { $player }: { $points } em { $category }.

yahtzee-you-bonus = Bônus de Yahtzee! +100 pontos
yahtzee-player-bonus = { $player } ganhou um bônus de Yahtzee! +100 pontos
yahtzee-you-bonus-brief = Bônus de Yahtzee, +100.
yahtzee-player-bonus-brief = { $player }: bônus de Yahtzee, +100.

yahtzee-you-upper-bonus = Bônus da seção superior! +35 pontos ({ $total } na seção superior)
yahtzee-player-upper-bonus = { $player } conquistou o bônus da seção superior! +35 pontos ({ $total } na seção superior)
yahtzee-you-upper-bonus-brief = Bônus superior, +35.
yahtzee-player-upper-bonus-brief = { $player }: bônus superior, +35.
yahtzee-you-upper-bonus-missed = Bônus da seção superior perdido. Você fez { $total }; faltaram { $needed }.
yahtzee-player-upper-bonus-missed = { $player } perdeu o bônus da seção superior com { $total }, faltando { $needed }.
yahtzee-you-upper-bonus-missed-brief = Bônus superior perdido; faltaram { $needed }.
yahtzee-player-upper-bonus-missed-brief = { $player }: bônus superior perdido, faltaram { $needed }.

yahtzee-check-scoresheet = Verificar cartela
yahtzee-check-all-scorecards = Verificar a cartela de todos os jogadores
yahtzee-select-scorecard-player = Escolha a cartela de um jogador.
yahtzee-scorecard-no-players = Nenhum jogador ativo tem cartela neste jogo ainda.
yahtzee-scorecard-player-unavailable = Esse jogador não está mais disponível para consulta. Abra a lista de cartelas novamente e escolha um jogador ativo.
yahtzee-view-dice = Verificar dados
yahtzee-your-dice = Seus dados: { $dice }.
yahtzee-your-dice-kept = Seus dados: { $dice }. Mantendo: { $kept }.
yahtzee-current-dice = Dados de { $player }: { $dice }.
yahtzee-current-dice-kept = Dados de { $player }: { $dice }. Mantendo: { $kept }.
yahtzee-not-rolled = O jogador atual ainda não rolou.

yahtzee-scoresheet-header = Cartela de { $player }
yahtzee-scoresheet-upper = Seção superior:
yahtzee-scoresheet-lower = Seção inferior:
yahtzee-scoresheet-upper-total-bonus = Total da parte superior: { $total } (bônus: +35)
yahtzee-scoresheet-upper-total-needed = Total da parte superior: { $total } (faltam { $needed } para o bônus)
yahtzee-scoresheet-yahtzee-bonus = Bônus de Yahtzee: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = Pontuação total: { $total }

yahtzee-category-ones = 1s
yahtzee-category-twos = 2s
yahtzee-category-threes = 3s
yahtzee-category-fours = 4s
yahtzee-category-fives = 5s
yahtzee-category-sixes = 6s
yahtzee-category-three-kind = Trinca
yahtzee-category-four-kind = Quadra
yahtzee-category-full-house = Full House
yahtzee-category-small-straight = Sequência menor
yahtzee-category-large-straight = Sequência maior
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Chance

yahtzee-you-win = Você vence com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
yahtzee-player-wins = { $player } vence com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
yahtzee-winners-tie = Empate! { $players } marcaram { $score } pontos!

yahtzee-set-rounds = Número de partidas: { $rounds }
yahtzee-enter-rounds = Digite o número de partidas (1-10):
yahtzee-option-changed-rounds = Número de partidas definido para { $rounds }.
yahtzee-desc-num-games = Quantas cartelas completas de Yahtzee são jogadas antes da comparação dos totais finais (padrão 1, intervalo de 1 a 10).

yahtzee-no-rolls-left = Você não tem mais rolagens; escolha uma categoria aberta para encerrar seu turno.
yahtzee-roll-first = Role os dados antes de escolher uma categoria de pontuação.
yahtzee-category-filled = Essa categoria já tem pontuação. Escolha uma categoria ainda aberta na sua cartela.
yahtzee-joker-upper-required = Regra do curinga: como este Yahtzee mostra { $face }, você deve pontuar a casa da seção superior para { $face } antes de qualquer outra categoria.
yahtzee-joker-lower-required = Regra do curinga: a casa da seção superior para { $face } já está preenchida, então você deve escolher uma categoria aberta da seção inferior antes de usar outra casa da seção superior.
