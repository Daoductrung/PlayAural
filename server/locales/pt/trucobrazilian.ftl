# Opções
trucobrazilian-desc-team-mode = Individual é uma partida um contra um para 2 jogadores. 2v2 usa 4 jogadores e 3v3 usa 6 jogadores; os parceiros dividem a pontuação e podem cantar por toda a equipe.

# Baralho francês
trucobrazilian-rank-ace = Ás
trucobrazilian-rank-jack = Valete
trucobrazilian-rank-queen = Dama
trucobrazilian-rank-king = Rei
trucobrazilian-suit-diamonds = ouros
trucobrazilian-suit-spades = espadas
trucobrazilian-suit-hearts = copas
trucobrazilian-suit-clubs = paus
trucobrazilian-card-name = { $rank } de { $suit }

# Cantos
trucobrazilian-call-truco = Truco
trucobrazilian-call-seis = Seis
trucobrazilian-call-nove = Nove
trucobrazilian-call-doze = Doze
trucobrazilian-call-onze = Mão de onze

# Ações e informações
trucobrazilian-action-onze-play = Jogar (jogar a mão)
trucobrazilian-action-onze-run = Correr (fugir e desistir da mão)
trucobrazilian-read-vira = Ler a vira e a manilha
trucobrazilian-no-vira = Ainda não foi virada a vira.
trucobrazilian-vira = A vira é { $card }. A manilha é { $manilha }.
trucobrazilian-vira-is = A vira é { $card }. A manilha é { $manilha }.

# Andamento da partida
trucobrazilian-game-start = O truco brasileiro começa. Vence quem chegar primeiro a { $points } pontos. A cada mão, uma carta virada chamada vira define as manilhas.
trucobrazilian-onze-your-team = Sua equipe tem 11 pontos: mão de onze. Escolha Jogar para jogar a mão por 3 pontos sem cantos, ou Correr para dar 1 ponto à outra equipe.
trucobrazilian-onze-team = { $team } tem 11 pontos e está decidindo se joga a mão de onze.
trucobrazilian-onze-play-you = Você joga a mão de onze. A mão vale 3 pontos e não são permitidos cantos.
trucobrazilian-onze-play-player = { $player } joga a mão de onze. A mão vale 3 pontos e não são permitidos cantos.
trucobrazilian-onze-run-you = Você corre. A outra equipe marca 1 ponto.
trucobrazilian-onze-run-player = { $player } corre. A outra equipe marca 1 ponto.
trucobrazilian-ferro = As duas equipes têm 11 pontos: mão de ferro. Não são permitidos cantos e quem ganhar a mão vence a partida.
trucobrazilian-reason-onze-run = a corrida na mão de onze
trucobrazilian-hand-annulled = As três vazas empataram. A mão é anulada e ninguém marca pontos.

# Erros e descrições
trucobrazilian-error-onze-pending = { $team } precisa decidir primeiro se joga a mão de onze.
trucobrazilian-error-no-calls = Nesta mão não é permitido cantar, pois é uma mão de onze ou uma mão de ferro.
trucobrazilian-desc-onze-play = Jogar a mão. Vale { $points } { $points ->
    [one] ponto
   *[other] pontos
} e não são permitidos cantos.
trucobrazilian-desc-onze-run = Correr e desistir da mão. A outra equipe marca 1 ponto.

trucobrazilian-action-accept = Aceito (aceitar)
trucobrazilian-action-decline = Correr (recusar e fugir)
trucobrazilian-accept-you = Você diz Aceito a { $call }.
trucobrazilian-accept-player = { $player } diz Aceito a { $call }.
trucobrazilian-decline-you = Você corre de { $call }.
trucobrazilian-decline-player = { $player } corre de { $call }.
trucobrazilian-pending-answer = { $player } cantou { $call }. Responda com Aceito ou Correr, ou aumente a aposta.
trucobrazilian-error-answer-first = Você precisa responder a { $call } antes de fazer outra coisa. Escolha Aceito ou Correr, ou aumente a aposta.
trucobrazilian-error-raise-max = O Doze já é o canto mais alto e não pode ser aumentado.
trucobrazilian-status-onze-pending = { $team } precisa decidir se joga a mão de onze.
trucobrazilian-status-no-calls = Nesta mão não são permitidos cantos. A mão vale { $points } { $points ->
    [one] ponto
   *[other] pontos
}.

# Mão de ferro (os dois lados com 11) é jogada com as cartas viradas; na mão de onze os parceiros veem as cartas um do outro
trucobrazilian-blind-cards = Mão de ferro: suas { $count } cartas estão viradas para baixo e você não pode vê-las. Escolha-as pela posição; cada uma é revelada quando é jogada.
trucobrazilian-blind-hand = Mão de ferro: você tem { $count } { $count ->
    [one] carta virada para baixo e não pode vê-la
   *[other] cartas viradas para baixo e não pode vê-las
}.
trucobrazilian-action-play-blind = Jogar a carta coberta { $number }
trucobrazilian-desc-blind-card = Uma carta virada para baixo. Você só a verá quando ela for jogada.
trucobrazilian-onze-partner-cards = Seu parceiro { $partner } mostra suas cartas: { $cards }.
