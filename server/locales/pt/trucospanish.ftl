# Opções
trucospanish-length-18 = 18 pontos por came
trucospanish-length-24 = 24 pontos por came
trucospanish-set-length = Duração da came: { $mode }
trucospanish-select-length = Selecione a duração da came:
trucospanish-option-changed-length = A duração da came agora é { $mode }.
trucospanish-desc-length = A partida é vencida ao ganhar duas cames. Cada came é jogada até o número de pontos escolhido: 24 como no campeonato fallero de València e no torneio da Universitat Politècnica de València, ou 18 como no torneio de Torrent e na descrição do Museu d'Història de València. Quando uma equipe o alcança, ela vence a came e os dois placares voltam a zero. A falta vale o que falta a quem está na frente para terminar a came, e o Joc fora vence a partida inteira.
trucospanish-desc-team-mode = Individual é uma partida um contra um para 2 jogadores. 2v2 usa 4 jogadores; os parceiros dividem a pontuação e podem cantar por toda a equipe.

# Cantos
trucospanish-call-truc = Truc
trucospanish-call-retruc = Retruc
trucospanish-call-quatre-val = Quatre val
trucospanish-call-joc-fora = Joc fora
trucospanish-call-envit = Envit
trucospanish-call-torna = Torna
trucospanish-call-la-falta = La falta

# Ações e mensagens
trucospanish-action-accept = Vull (aceitar)
trucospanish-action-decline = No vull (recusar)
trucospanish-action-mazo = Me'n vaig (desistir da mão)
trucospanish-accept-you = Você diz Vull a { $call }.
trucospanish-accept-player = { $player } diz Vull a { $call }.
trucospanish-decline-you = Você diz No vull a { $call }.
trucospanish-decline-player = { $player } diz No vull a { $call }.
trucospanish-mazo-you = Você diz Me'n vaig e desiste da mão por toda a sua equipe.
trucospanish-mazo-player = { $player } diz Me'n vaig e desiste da mão por toda a equipe.
trucospanish-reason-truc = o Truc
trucospanish-reason-envit = o Envit
trucospanish-game-start = O truco espanhol começa. Vence a partida quem ganhar duas cames de { $points } pontos.
trucospanish-desc-mazo = Desistir da mão por toda a sua equipe. A outra equipe marca o valor atual da mão.
trucospanish-came-you = Você ganha uma came! Você tem { $cames } { $cames ->
    [one] came
   *[other] cames
}. O placar volta a zero.
trucospanish-came-player = { $player } ganha uma came e tem { $cames } { $cames ->
    [one] came
   *[other] cames
}. O placar volta a zero.
trucospanish-came-your-team = Sua equipe ganha uma came! Vocês têm { $cames } { $cames ->
    [one] came
   *[other] cames
}. O placar volta a zero.
trucospanish-came-team = { $team } ganha uma came e tem { $cames } { $cames ->
    [one] came
   *[other] cames
}. O placar volta a zero.

trucospanish-pending-answer = { $player } cantou { $call }. Responda com Vull ou No vull, ou aumente a aposta.
trucospanish-error-answer-first = Você precisa responder a { $call } antes de fazer outra coisa. Escolha Vull ou No vull, ou aumente a aposta.
trucospanish-error-raise-max = O Joc fora já é o canto mais alto e não pode ser aumentado.
trucospanish-error-bad-count = O truco espanhol precisa de 2 ou 4 jogadores, mas há { $count }.
trucospanish-error-team-mode-count = O modo de equipes { $mode } não pode ser usado com { $count } jogadores. Use Individual para 2 jogadores ou 2v2 para 4 jogadores.
trucospanish-status-envit-open = Ainda é possível cantar envit nesta mão.
trucospanish-status-envit-closed = O envit está fechado nesta mão.
trucospanish-status-no-truc = Nenhum Truc foi cantado. A mão vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.
trucospanish-falta-value = La falta vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.
trucospanish-reveal-envit-you = O envit foi ganho com as suas cartas: { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
trucospanish-reveal-envit-player = { $player } ganhou o envit com { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
trucospanish-error-envit-late = O envit só pode ser cantado antes de você jogar a sua primeira carta.
trucospanish-error-envit-closed = O envit está fechado porque o Truc já foi aceito.
trucospanish-error-envit-done = O envit já foi jogado nesta mão.
trucospanish-error-envit-cannot-raise = { $call } não pode ser adicionado ao envit que está sendo jogado.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] ponto
   *[other] pontos
} nesta came, { $cames } { $cames ->
    [one] came ganha
   *[other] cames ganhas
}
trucospanish-game-win-you = Você vence a partida com { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-player = { $player } vence a partida com { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-game-win-your-team = Sua equipe vence a partida com { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-team = { $team } vence a partida com { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] came
   *[other] cames
}
trucospanish-cames-line = { $team }: { $cames } { $cames ->
    [one] came ganha
   *[other] cames ganhas
}
