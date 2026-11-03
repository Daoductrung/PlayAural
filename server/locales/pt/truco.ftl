game-name-truco = Truco

# Opções
truco-set-variant = Variante: { $mode }
truco-select-variant = Selecione a variante do truco:
truco-option-changed-variant = A variante agora é { $mode }.
truco-desc-variant = O truco argentino usa o baralho espanhol de 40 cartas, com envido e flor opcional. O truco brasileiro (paulista) usa um baralho francês com uma carta virada, a vira, que decide as cartas mais fortes, e aumentos que valem 3, 6, 9 e 12 pontos. O truco espanhol (truc valenciano) usa um baralho de 22 cartas com envit e o Joc fora, que vale a partida inteira.
truco-variant-argentine = Truco argentino
truco-variant-brazilian = Truco brasileiro
truco-variant-spanish = Truco espanhol
truco-length-15 = 15 pontos
truco-length-30 = 30 pontos
truco-set-length = Duração da partida: { $mode }
truco-select-length = Selecione a duração da partida:
truco-option-changed-length = A duração da partida agora é { $mode }.
truco-desc-length = Em uma partida de 15 pontos, vence quem chegar primeiro a 15 pontos. Em uma partida de 30 pontos, os pontos de 1 a 15 são as malas (primeira metade) e os de 16 a 30 são as buenas (segunda metade); vence quem chegar primeiro a 30.
truco-set-flor = Flor: { $enabled }
truco-option-changed-flor = A flor agora está { $enabled }.
truco-desc-flor = Quando ativada, quem receber três cartas do mesmo naipe tem flor. Ela é anunciada automaticamente e cancela o envido. A Flor vale 3 pontos, a Contraflor 6 e a Contraflor al resto vale o que falta à equipe que está na frente para vencer. Só quem tem flor pode responder ou aumentar. A flor vale 20 mais o valor das três cartas (as figuras valem zero), então 7, 6 e 5 de um naipe somam 38; vence a flor mais alta. Quando desativada, três cartas do mesmo naipe não têm valor especial.
truco-desc-team-mode = Individual é uma partida um contra um para 2 jogadores. 2v2 usa 4 jogadores e 3v3 usa 6 jogadores; os parceiros dividem a pontuação e podem cantar por toda a equipe.

# Baralho espanhol
truco-suit-oros = ouros
truco-suit-copas = copas
truco-suit-espadas = espadas
truco-suit-bastos = paus
truco-card-name = { $rank } de { $suit }

# Cantos
truco-call-truco = Truco
truco-call-retruco = Retruco
truco-call-valecuatro = Vale cuatro
truco-call-envido = Envido
truco-call-real-envido = Real envido
truco-call-falta-envido = Falta envido
truco-call-flor = Flor
truco-call-contraflor = Contraflor
truco-call-contraflor-al-resto = Contraflor al resto

# Ações
truco-action-play-card = { $card }
truco-action-accept = Quiero (aceitar)
truco-action-decline = No quiero (recusar)
truco-action-mazo = Me voy al mazo (desistir das suas cartas)
truco-read-hand = Ler suas cartas
truco-read-table = Ler as cartas da mesa
truco-read-calls = Ler os cantos atuais

# Andamento da partida e da mão
truco-game-start-flor = O truco começa com flor. Vence quem chegar primeiro a { $points } pontos.
truco-game-start-no-flor = O truco começa sem flor. Vence quem chegar primeiro a { $points } pontos.
truco-hand-start = A mão { $hand } começa. As cartas são distribuídas.
truco-dealer-you = Você distribui as cartas.
truco-dealer-player = { $player } distribui as cartas.
truco-mano-you = Você é mano e joga primeiro.
truco-mano-player = { $player } é mano e joga primeiro.
truco-your-cards = Suas cartas: { $cards }.
truco-no-cards = Você não tem mais cartas.
truco-your-turn = É a sua vez de jogar uma carta.

# Cartas jogadas e vazas
truco-play-you = Você joga { $card }.
truco-play-player = { $player } joga { $card }.
truco-trick-win-you = Vaza { $trick }: você vence com { $card }.
truco-trick-win-teammate = Vaza { $trick }: seu parceiro { $player } vence com { $card }.
truco-trick-win-opponent = Vaza { $trick }: { $player } vence com { $card } para { $team }.
truco-trick-tie = A vaza { $trick } empata: é parda.

# Cantar e responder
truco-call-you = Você canta { $call }.
truco-call-player = { $player } canta { $call }.
truco-call-goes-first-you = Você canta { $call }. O envido vai primeiro, antes de responder ao truco.
truco-call-goes-first-player = { $player } canta { $call }. O envido vai primeiro, antes de responder ao truco.
truco-pending-answer = { $player } cantou { $call }. Responda com Quiero ou No quiero, ou aumente a aposta.
truco-pending-wait = Aguardando { $team } responder a { $call }.
truco-accept-you = Você diz Quiero a { $call }.
truco-accept-player = { $player } diz Quiero a { $call }.
truco-decline-you = Você diz No quiero a { $call }.
truco-decline-player = { $player } diz No quiero a { $call }.
truco-mazo-you = Você diz Me voy al mazo e desiste das suas cartas.
truco-mazo-player = { $player } diz Me voy al mazo e desiste das próprias cartas.
truco-team-folded-your-team = Todos os integrantes da sua equipe desistiram da mão.
truco-team-folded-team = Todos os integrantes de { $team } desistiram da mão.
truco-flor-announce-you = Você tem flor.
truco-flor-announce-player = { $player } tem flor.
truco-flor-cancels-envido = O envido é cancelado por causa da flor.
truco-reveal-envido-you = O envido foi vencido com as suas cartas: { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
truco-reveal-envido-player = O envido foi vencido por { $player } com { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
truco-reveal-flor-you = A flor foi vencida com as suas cartas: { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
truco-reveal-flor-player = A flor foi vencida por { $player } com { $cards }, que valem { $value } { $value ->
    [one] ponto
   *[other] pontos
}.

# Envido e flor
truco-falta-envido-value = A falta envido vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.
truco-falta-envido-game = Falta envido: as duas equipes estão nas malas, então quem ganhar vence a partida inteira.

# Pontos e placar
truco-reason-truco = o Truco
truco-reason-envido = o Envido
truco-reason-flor = a Flor
truco-reason-hand = a mão
truco-points-your-team = Sua equipe marca { $points } { $points ->
    [one] ponto
   *[other] pontos
} por { $reason }.
truco-points-team = { $team } marca { $points } { $points ->
    [one] ponto
   *[other] pontos
} por { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] ponto
   *[other] pontos
}.
truco-half-buenas-your-team = Sua equipe entra nas buenas, a segunda metade.
truco-half-buenas-team = { $team } entra nas buenas, a segunda metade.

# Informações
truco-status-no-truco = Nenhum Truco foi cantado. A mão vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.
truco-status-truco = A mão está em { $call } e vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.
truco-status-truco-pending = { $call } aguarda a resposta de { $team }.
truco-status-envido-open = Ainda é possível cantar o envido nesta mão.
truco-status-envido-closed = O envido está fechado nesta mão.
truco-table-empty = Nenhuma carta foi jogada ainda.
truco-table-trick = Vaza { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Erros e motivos de ações desativadas
truco-error-bad-count = O truco precisa de 2, 4 ou 6 jogadores, mas há { $count }.
truco-error-team-mode-count = O modo de equipes { $mode } não pode ser usado com { $count } jogadores. Use Individual com 2 jogadores, 2v2 com 4 ou 3v3 com 6.
truco-error-not-your-turn = É a vez de { $player } jogar uma carta.
truco-error-answer-first = Você precisa responder a { $call } antes de fazer outra coisa. Escolha Quiero ou No quiero, ou aumente a aposta.
truco-error-nothing-to-answer = Nenhum canto está aguardando a sua resposta.
truco-error-own-team-call = Sua equipe fez esse canto. Aguarde { $team } responder a { $call }.
truco-error-envido-late = O envido só pode ser cantado antes de você jogar a sua primeira carta.
truco-error-envido-closed = O envido está fechado porque o truco já foi aceito.
truco-error-envido-done = O envido já foi jogado nesta mão.
truco-error-raise-max = O truco já está em Vale cuatro e não pode ser aumentado.
truco-error-raise-holder = Sua equipe fez o último canto do truco. Agora só { $team } pode aumentá-lo.
truco-error-flor-none = Você desistiu da mão, então não pode cantar nem responder.
truco-error-flor-holders-only = Só quem tem flor pode responder ou aumentar uma flor.
truco-error-card-not-held = Você não tem essa carta.
truco-error-hand-over = A mão já terminou.

# Fim da partida
truco-game-win-you = Você vence a partida com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
truco-game-win-player = { $player } vence a partida com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
truco-game-win-your-team = Sua equipe vence a partida com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
truco-game-win-team = { $team } vence a partida com { $score } { $score ->
    [one] ponto
   *[other] pontos
}!
truco-end-title = Resultados do truco
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] ponto
   *[other] pontos
}.

# Erros adicionais e mensagens do modo individual
truco-error-flor-off = A flor está desativada nesta partida, então não há nada para cantar nem responder.
truco-error-flor-window = A flor precisa ser resolvida primeiro. Não é possível cantar truco até que a primeira carta seja jogada.
truco-error-flor-window-closed = A contraflor só pode ser cantada enquanto as duas equipes têm flor e antes de jogar a primeira carta.
truco-error-envido-flor = O envido está cancelado nesta mão porque alguém tem flor.
truco-error-envido-cannot-raise = Não é possível acrescentar { $call } ao envido que está sendo jogado.
truco-points-you = Você marca { $points } { $points ->
    [one] ponto
   *[other] pontos
} por { $reason }.
truco-points-player = { $player } marca { $points } { $points ->
    [one] ponto
   *[other] pontos
} por { $reason }.
truco-half-buenas-you = Você entra nas buenas, a segunda metade.
truco-half-buenas-player = { $player } entra nas buenas, a segunda metade.

# Informações de cartas, descrições e gestos de toque
truco-card-info-label = Informações do item
truco-card-info = { $card }: vence { $beats } das outras { $total } cartas deste baralho.
truco-card-info-envido = { $card }: vence { $beats } das outras { $total } cartas deste baralho. Valor para o envido: { $value }.
truco-desc-call-ladder = { $call }: aumenta a mão para { $points } { $points ->
    [one] ponto
   *[other] pontos
}. Se for recusado, quem cantou ganha { $refused } { $refused ->
    [one] ponto
   *[other] pontos
}.
truco-desc-call-envido = { $call }: as duas equipes comparam o envido. Se for aceito, quem vencer marca { $points } { $points ->
    [one] ponto
   *[other] pontos
}. Se for recusado, quem cantou marca { $refused } { $refused ->
    [one] ponto
   *[other] pontos
}.
truco-desc-call-flor = { $call }: quem tem flor compara as flores. Se for aceito, quem vencer marca { $points } { $points ->
    [one] ponto
   *[other] pontos
}. Se for recusado, quem cantou marca { $refused } { $refused ->
    [one] ponto
   *[other] pontos
}.
truco-desc-accept = Aceitar { $call } e continuar jogando.
truco-desc-decline = Recusar { $call }. A outra equipe marca { $points } { $points ->
    [one] ponto
   *[other] pontos
} e a mão termina.
truco-desc-mazo = Desistir das suas cartas. Se toda a sua equipe desistir, a outra equipe ganha a mão.
truco-trick-tie-neutral = A vaza { $trick } empatou.
