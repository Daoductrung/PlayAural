# Humanity Cards - Portuguese localization

game-name-humanitycards = Cartas contra a Humanidade

# Options
hc-set-winning-score = Pontuação para vencer: { $score }
hc-enter-winning-score = Digite a pontuação para vencer:
hc-option-changed-winning-score = Pontuação para vencer definida para { $score }.
hc-desc-winning-score = O número de cartas vencedoras que um jogador precisa coletar para vencer a partida (padrão 7, intervalo de 3 a 20).

hc-set-hand-size = Tamanho da mão: { $count }
hc-enter-hand-size = Digite o tamanho da mão:
hc-option-changed-hand-size = Tamanho da mão definido para { $count }.
hc-desc-hand-size = Quantas cartas de resposta cada jogador segura após cada reposição. Mãos maiores oferecem mais escolhas, mas tornam as rodadas mais longas (padrão 10, intervalo de 5 a 15).

hc-set-card-language = Idioma das cartas: { $language }
hc-select-card-language = Selecione o idioma das cartas
hc-option-changed-card-language = Idioma das cartas definido como { $language }.
hc-desc-card-language = Define o idioma de todas as cartas de pergunta e resposta da partida, independentemente do idioma da interface de cada jogador (padrão inglês; opções: inglês, espanhol e português do Brasil).
hc-card-language-pt-br = Português do Brasil
hc-card-blank = espaço em branco
hc-card-same-again = a mesma carta novamente

hc-set-card-packs = Pacotes de cartas ({ $count } de { $total } selecionados)
hc-option-changed-card-packs = Seleção de pacotes de cartas alterada.
hc-desc-card-packs = Escolha quais pacotes de respostas e perguntas em inglês serão embaralhados no jogo. Cartas idênticas de pacotes sobrepostos são incluídas apenas uma vez. Pelo menos um pacote deve permanecer selecionado.
hc-pack-group-current = Baralho principal atual dos EUA
hc-pack-group-main-decks = Edições do baralho principal
hc-pack-group-official-add-ons = Expansões e pacotes oficiais
hc-pack-group-family = Edição para a família
hc-pack-group-community = Pacotes da comunidade
hc-pack-group-all = Todos os pacotes

hc-set-czar-selection = Seleção do Czar das Cartas: { $mode }
hc-select-czar-selection = Selecionar modo de escolha do Czar das Cartas
hc-option-changed-czar-selection = Seleção do Czar das Cartas definida para { $mode }.
hc-desc-czar-selection = Controla quem julga cada rodada: em rotação na ordem dos assentos, escolhido aleatoriamente ou o vencedor da rodada mais recente.

hc-set-num-judges = Número de juízes: { $count }
hc-enter-num-judges = Digite o número de juízes:
hc-option-changed-num-judges = Número de juízes definido para { $count }.
hc-desc-num-judges = Quantos Czars das Cartas julgam cada rodada. A contagem deve ser menor que o número de jogadores para que pelo menos um não-juiz possa enviar; com vários juízes, qualquer um pode escolher o vencedor (padrão 1, intervalo de 1 a 3).

hc-czar-rotating = Rotativo
hc-czar-random = Aleatório
hc-czar-winner = Vencedor mais recente

# Game flow
hc-game-starting = Embaralhando os baralhos...
hc-dealing-cards = Distribuindo { $count } cartas para cada jogador.
hc-round-start = Rodada { $round }.

# Judge announcement
hc-judge-is = { $judges } { $count ->
    [1] é o Czar das Cartas
   *[other] são os Czars das Cartas
}.
hc-you-are-judge = Você é o Czar das Cartas nesta rodada.
hc-you-and-others-are-judges = Você e { $judges } são os Czars das Cartas nesta rodada.

# Black card
hc-black-card = A pergunta é: { $text }
hc-black-card-draw = Primeiro, compre { $count } { $count ->
    [one] carta extra
   *[other] cartas extras
}.
hc-black-card-pick = Escolha { $count }.
hc-view-black-card = Ver a carta de pergunta
hc-no-question-card = Não há uma carta de pergunta ativa no momento.

# Submission phase
hc-select-cards = Selecione { $count } { $count ->
    [one] carta
   *[other] cartas
} da sua mão.
hc-card-selected = { $text }, selecionada
hc-card-selected-position = { $text }, selecionada como resposta { $position }
hc-card-not-selected = { $text }
hc-submit-cards = Enviar ({ $selected } de { $required } selecionadas)
hc-submission-progress = { $submitted } de { $total } jogadores enviaram.
hc-already-submitted = Você já enviou suas cartas.
hc-you-submitted = Você enviou suas cartas.
hc-player-submitted = { $player } enviou as cartas { GENDER_TERM($player_gender, "possessive-determiner") }.
hc-judge-cannot-submit = Você é o Czar das Cartas nesta rodada, então não pode enviar uma resposta.
hc-not-submission-phase = Você só pode selecionar e enviar cartas brancas durante a fase de envio.
hc-card-not-in-hand = Esse espaço de carta não está na sua mão.
hc-judge-has-no-submission = O Czar das Cartas não tem um envio para visualizar nesta rodada.
hc-no-submission-active = Não há nenhum envio ativo para visualizar no momento.
hc-wrong-card-count = Você precisa selecionar exatamente { $count } { $count ->
    [one] carta
   *[other] cartas
}.
hc-selection-full = Você já selecionou { $count } { $count ->
    [one] carta
   *[other] cartas
}. Desmarque uma antes de escolher outra.

# Judging phase
hc-judging-start = Todas as cartas estão prontas! Hora de julgar.
hc-choose-best-card = Escolha a melhor carta
hc-choose-best-card-for = Escolha a melhor carta que combine com: { $prompt }
hc-card-number = Carta { $number }
hc-submission-number = Envio { $number }
hc-only-judges-pick = Apenas o Czar das Cartas pode escolher o envio vencedor.
hc-not-judging-phase = Você só pode escolher um envio vencedor durante a fase de julgamento.
hc-submission-not-available = Esse envio não está mais disponível.

# Results
hc-you-win-round = Você venceu a rodada! Sua pontuação agora é { $score }.
hc-player-wins-round = { $player } venceu a rodada! Pontuação: { $score }.
hc-score-line = { $player }: { $score } { $score ->
    [one] ponto
   *[other] pontos
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] ponto
   *[other] pontos
}
hc-all-submissions = Outros envios:
hc-your-winning-answer = Sua resposta vencedora: { $text }
hc-winning-answer-player = Resposta vencedora de { $player }: { $text }
hc-your-other-submission = Seu outro envio: { $text }
hc-other-submission-player = { $player }: { $text }

# View
hc-preview-submission = Visualizar seu envio
hc-view-submission = Ver seu envio
hc-preview-submission-text = Pré-visualização: { $text }
hc-your-submission = Seu envio: { $text }
hc-select-cards-first = Selecione pelo menos 1 carta primeiro.
hc-review-hand = Revisar sua mão
hc-hand-empty = Sua mão está vazia.
hc-hand-card = { $number }. { $text }
hc-hand-card-selected = { $number }. { $text }, selecionada como resposta { $position }
hc-review-answers = Revisar as respostas
hc-answer-line = Resposta { $number }: { $text }
hc-no-answers-to-review = Não há respostas para revisar agora.

# Win
hc-game-winner = { $player } venceu com { $score } pontos!
hc-you-win = Você venceu com { $score } pontos!

# Deck management
hc-deck-reshuffled = Pilha de descarte de cartas brancas embaralhada de volta no baralho.
hc-black-deck-reshuffled = Pilha de descarte de cartas pretas embaralhada de volta no baralho.
hc-not-enough-cards = Cartas insuficientes. Tente ativar mais pacotes.
hc-error-too-many-judges = { $judges } juízes exigem pelo menos { $required } jogadores, mas esta mesa tem { $players }. Reduza o número de juízes ou adicione mais jogadores.
hc-error-no-valid-packs = Nenhum pacote de cartas válido está selecionado. Selecione pelo menos um pacote antes de começar.
hc-error-no-black-cards = Os pacotes de cartas selecionados não contêm cartas de perguntas pretas. Selecione outro pacote antes de começar.
hc-error-not-enough-white-cards = { $players } jogadores com um tamanho de mão de { $hand_size } precisam de pelo menos { $needed } cartas brancas, mas os pacotes selecionados fornecem apenas { $available }. Ative mais pacotes ou diminua o tamanho da mão.
hc-error-pick-exceeds-hand-size = Os pacotes selecionados incluem uma pergunta que exige { $pick } respostas, mas o tamanho da mão é de apenas { $hand_size }. Aumente o tamanho da mão ou escolha pacotes diferentes.

# Hand management
hc-toggle-card-keybind = Alternar carta { $number }
hc-submit-cards-keybind = Enviar cartas

# Whose turn / whose judge
hc-whose-judge = Quem está julgando
hc-waiting-for = Aguardando { $names } enviarem.
hc-all-submitted-waiting-judge = Todos os jogadores enviaram. Aguardando { $judge } julgar.
