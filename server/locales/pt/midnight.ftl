game-name-midnight = 1-4-24

midnight-roll = Rolar os dados
midnight-keep-die = Manter { $value }
midnight-bank = Guardar pontos
midnight-check-dice = Ler dados atuais
midnight-check-round-status = Ver status da rodada

midnight-round-start = Rodada { $round } de { $total }.
midnight-round-start-brief = Rodada { $round }/{ $total }.

midnight-you-rolled = Você rolou: { $dice }.
midnight-player-rolled = { $player } rolou: { $dice }.
midnight-you-rolled-brief = Você rola { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = Você mantém o dado { $index }, mostrando { $die }.
midnight-player-keeps = { $player } mantém o dado { $index }, mostrando { $die }.
midnight-you-keep-brief = Você mantém { $die }.
midnight-player-keeps-brief = { $player } mantém { $die }.
midnight-you-unkeep = Você devolve o dado { $index }, mostrando { $die }, para a reserva de rolagem.
midnight-player-unkeeps = { $player } devolve o dado { $index }, mostrando { $die }, para a reserva de rolagem.
midnight-you-unkeep-brief = Você rola novamente { $die }.
midnight-player-unkeeps-brief = { $player } rola novamente { $die }.

midnight-you-scored = Você se qualifica com 1 e 4, pontuando { $score } a partir de { $scoring_dice }.
midnight-scored = { $player } se qualifica com 1 e 4, pontuando { $score } a partir de { $scoring_dice }.
midnight-you-scored-brief = Você pontua { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = Você não se qualifica porque falta { $missing }.
midnight-player-disqualified = { $player } não se qualifica porque falta { $missing }.
midnight-you-disqualified-brief = Você perde { $missing }.
midnight-player-disqualified-brief = { $player } perde { $missing }.

midnight-you-win-round = Você vence a rodada { $round } com { $score }.
midnight-round-winner = { $player } vence a rodada { $round } com { $score }.
midnight-you-win-round-brief = Você vence a R{ $round }: { $score }.
midnight-round-winner-brief = { $player } vence a R{ $round }: { $score }.
midnight-round-tie = Rodada empatada em { $score } entre { $players }. Nenhuma vitória de rodada é concedida.
midnight-all-disqualified = Todos os jogadores perderam o 1 e o 4 necessários. Nenhuma vitória de rodada é concedida.
midnight-all-disqualified-brief = Ninguém se qualifica.

midnight-you-win-game = Você vence o jogo com { $wins } { $wins ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}!
midnight-game-winner = { $player } vence o jogo com { $wins } { $wins ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}!
midnight-you-win-game-brief = Você vence: { $wins }.
midnight-game-winner-brief = { $player } vence: { $wins }.
midnight-game-tie = É um empate no jogo. { $players } terminaram cada um com { $wins } { $wins ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}.

midnight-set-rounds = Rodadas para jogar: { $rounds }
midnight-enter-rounds = Digite o número de rodadas para jogar:
midnight-option-changed-rounds = Rodadas para jogar alteradas para { $rounds }
midnight-desc-rounds = Número de rodadas de Midnight a jogar antes da pontuação final (padrão 5, intervalo de 1 a 20).
midnight-error-rounds-out-of-range = Midnight suporta de { $min } a { $max } rodadas. Configuração atual: { $rounds }.

midnight-need-to-roll = Role os dados antes de escolher quais manter.
midnight-no-dice-to-keep = Não há mais dados para rolar ou manter.
midnight-must-keep-one = Mantenha pelo menos um dado recém-rolado antes de rolar novamente.
midnight-must-roll-first = Role os dados antes de guardar seus pontos.
midnight-keep-all-first = Decida sobre cada dado antes de guardar. Mantenha ou devolva todos os dados destravados primeiro.
midnight-invalid-die-index = Esse dado não está disponível nesta rolagem.

midnight-die-locked = { $value } (travado)
midnight-die-kept = { $value } (mantido)
midnight-die-value = { $value }
midnight-die-index = Dado { $index }

midnight-your-dice-not-rolled = Você ainda não rolou neste turno.
midnight-player-dice-not-rolled = { $player } ainda não rolou neste turno.
midnight-your-dice-status =
    { $qualified ->
        [yes] Seus dados: { $dice }. Travados: { $locked }; mantidos para a próxima rolagem: { $kept }; dados ainda ativos: { $remaining }. A pontuação de qualificação atual seria { $score } a partir de { $scoring_dice }.
       *[no] Seus dados: { $dice }. Travados: { $locked }; mantidos para a próxima rolagem: { $kept }; dados ainda ativos: { $remaining }. Você ainda precisa de { $missing } para se qualificar.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] Dados de { $player }: { $dice }. Travados: { $locked }; mantidos para a próxima rolagem: { $kept }; dados ainda ativos: { $remaining }. A pontuação de qualificação atual seria { $score } a partir de { $scoring_dice }.
       *[no] Dados de { $player }: { $dice }. Travados: { $locked }; mantidos para a próxima rolagem: { $kept }; dados ainda ativos: { $remaining }. Ele ainda precisa de { $missing } para se qualificar.
    }

midnight-status-round = Rodada { $round } de { $total }
midnight-status-current-player = Turno atual: { $player }
midnight-status-current-not-rolled = { $player } ainda não rolou.
midnight-status-current-dice =
    { $qualified ->
        [yes] Dados atuais de { $player }: { $dice }. Pontuação potencial: { $score } a partir de { $scoring_dice }. Travados { $locked }, mantidos { $kept}, ativos { $remaining}.
       *[no] Dados atuais de { $player }: { $dice }. Falta { $missing}. Travados { $locked }, mantidos { $kept}, ativos { $remaining}.
    }
midnight-status-dice-not-rolled = não rolado
midnight-status-last-qualified = Último turno: { $player } rolou { $dice } e pontuou { $score }.
midnight-status-last-disqualified = Último turno: { $player } rolou { $dice } e não se qualificado.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } vitórias de rodada; rodada atual { $current}, qualificado.
       *[no] { $rank }. { $player }: { $wins } vitórias de rodada; rodada atual { $current}, não qualificado.
    }

midnight-score-unit-round-wins = { $count ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] vitória de rodada
   *[other] vitórias de rodada
}
