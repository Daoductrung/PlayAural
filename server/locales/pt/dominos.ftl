game-name-dominos = Dominó
dominos-desc-team-mode = Jogue individualmente ou use qualquer arranjo de equipes pares válido suportado pela contagem atual de jogadores.

# Options
dominos-set-target-score = Pontuação alvo: { $score }
dominos-enter-target-score = Digite a pontuação alvo
dominos-option-changed-target-score = Pontuação alvo definida para { $score }.
dominos-desc-target-score = Alvo de pontuação necessário para vencer o Dominó (padrão 100, intervalo 20-500).

dominos-set-draw-mode = Modo: { $mode }
dominos-select-draw-mode = Selecionar modo
dominos-option-changed-draw-mode = Modo definido para { $mode }.
dominos-desc-draw-mode = Escolhe o modo Compra, onde os jogadores compram do monte, ou o modo Bloqueio, onde jogadores bloqueados passam.

dominos-set-domino-set = Conjunto de dominós: { $domino_set }
dominos-select-domino-set = Selecionar conjunto de dominós
dominos-option-changed-domino-set = Conjunto de dominós alterado para { $domino_set }.
dominos-desc-domino-set = Tamanho do conjunto de dominós. Duplo-6 suporta até 5 jogadores, Duplo-9 suporta até 7 jogadores e Duplo-12 suporta até 12 jogadores (padrão Duplo-6).

dominos-set-spinner = Carretel: { $enabled }
dominos-option-changed-spinner = Carretel definido para { $enabled }.
dominos-desc-spinner-enabled = Controla se um duplo inicial cria um carretel de quatro vias (padrão ligado).

dominos-set-opening-rule = Regra de abertura: { $opening_rule }
dominos-select-opening-rule = Selecionar regra de abertura
dominos-option-changed-opening-rule = Regra de abertura definida para { $opening_rule }.
dominos-desc-opening-rule = Escolhe como a primeira peça de cada rodada de Dominó é selecionada.

# Option choice labels
dominos-mode-draw = Compra
dominos-mode-block = Bloqueio

dominos-set-double6 = Duplo-6
dominos-set-double9 = Duplo-9
dominos-set-double12 = Duplo-12

dominos-opening-highest-double = Maior duplo
dominos-opening-highest-tile = Maior peça
dominos-opening-set-max-double = Maior duplo do conjunto
dominos-opening-random-player = Jogador aleatório
dominos-opening-round-winner = Vencedor da rodada anterior

# Actions
dominos-draw = Comprar
dominos-knock = Bater
dominos-view-chain = Ver corrente
dominos-read-ends = Ler pontas
dominos-read-hand = Ler mão
dominos-read-counts = Ler contagens
dominos-play-tile = { $tile }
dominos-open-with-tile = Abrir com { $tile }
dominos-play-tile-at = Jogar { $tile } na { $side }
dominos-play-tile-multi = Jogar { $tile } nas { $sides }
dominos-select-side = Selecione um lado

# Board sides
dominos-side-left = esquerda
dominos-side-right = direita
dominos-side-up = cima
dominos-side-down = baixo

# Validation and disabled reasons
dominos-draw-only-mode = A compra só está disponível no modo Compra.
dominos-must-play = Você já tem uma peça jogável.
dominos-boneyard-empty = O monte está vazio.
dominos-must-draw = Você deve comprar antes de bater.
dominos-illegal-side = Esse lado não é válido para a peça selecionada.
dominos-no-play-for-tile = { $tile } não pode ser jogada agora.
dominos-choose-side-keybind = Escolha um lado com a tecla de direção. Lados válidos: { $sides }.
dominos-opening-must-play = A rodada ainda não foi aberta. Você deve escolher uma peça para iniciar a corrente.
dominos-error-set-too-small = { $players } jogadores não podem receber peças suficientes de um conjunto Duplo-{ $selected_pip }. Escolha pelo menos Duplo-{ $required_pip } para este tamanho de mesa.

# Gameplay
dominos-you-open-round = Você lidera esta rodada. Escolha qualquer peça da sua mão para abrir a corrente.
dominos-player-opens-round = { $player } lidera esta rodada e está escolhendo a peça de abertura.
dominos-you-opened = Você abriu a rodada com { $tile }.
dominos-player-opened = { $player } abriu a rodada com { $tile }.
dominos-you-opened-spinner = Você abriu a rodada com { $tile }, criando um carretel de quatro vias.
dominos-player-opened-spinner = { $player } abriu a rodada com { $tile }, criando um carretel de quatro vias.
dominos-you-drew-single = Você comprou { $tile } do monte.
dominos-you-drew-many = Você comprou { $count } peças do monte.
dominos-player-drew-single = { $player } comprou 1 peça do monte.
dominos-player-drew-many = { $player } comprou { $count } peças do monte.
dominos-you-played = Você jogou { $tile } no ramo da { $side }.
dominos-you-played-drawn = Você comprou e jogou { $tile } no ramo da { $side }.
dominos-player-played = { $player } jogou { $tile } no ramo da { $side }.
dominos-you-knock = Você bateu porque não tem nenhuma peça válida para jogar.
dominos-player-knocks = { $player } bateu.
dominos-you-won-round = Você esvaziou sua mão e marcou { $points } pontos com as peças dos oponentes.
dominos-player-won-round = { $player } esvaziou a mão e marcou { $points } pontos com as peças dos oponentes.
dominos-round-blocked-tie = A rodada está bloqueada. O menor total de pontos é { $pips }, mas houve empate. Nenhum ponto é marcado.
dominos-round-blocked-winner = A rodada está bloqueada. { $team } tem o menor total de pontos com { $pips } e marca { $points } pontos.
dominos-match-tied-continue = Várias equipes alcançaram { $score } pontos. O jogo continua até o empate ser desfeito.
dominos-match-winner = { $team } vence o jogo com { $score } pontos.

# Status boxes
dominos-chain-header = Corrente
dominos-chain-empty = A corrente está vazia.
dominos-chain-center = Centro: { $tile }
dominos-branch-empty = sem peças
dominos-chain-branch = { $side }: { $tiles }. Ponta aberta { $open_end }.
dominos-boneyard-count = Monte: { $count } peças restantes.
dominos-end-info = { $side } { $value }

dominos-hand-header = Sua mão
dominos-hand-line = { $tile } vale { $points } pontos.
dominos-hand-line-playable = { $tile } vale { $points } pontos. Jogável na { $sides }.
dominos-hand-line-opening-playable = { $tile } vale { $points } pontos. Você pode usá-la para abrir esta rodada.
dominos-hand-total = Total de pontos na mão: { $pips }.
dominos-player-count = { $player } tem { $count } peças
dominos-no-other-players = Sem outros jogadores.

# End screen
dominos-line-format = { $rank }. { $player }: { $points }
