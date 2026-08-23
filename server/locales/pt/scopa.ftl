game-name-scopa = Scopa

scopa-initial-table = Cartas na mesa: { $cards }
scopa-no-initial-table = Nenhuma carta na mesa para começar.
scopa-you-collect = Você recolhe { $cards } com { $card }
scopa-player-collects = { $player } recolhe { $cards } com { $card }
scopa-you-capture = Você captura { $cards } com { $card }.
scopa-player-captures = { $player } captura { $cards } com { $card }.
scopa-you-capture-scopa = Você captura { $cards } com { $card } e faz uma scopa!
scopa-player-captures-scopa = { $player } captura { $cards } com { $card } e faz uma scopa!
scopa-you-capture-clear = Você captura { $cards } com { $card }, limpando a mesa.
scopa-player-captures-clear = { $player } captura { $cards } com { $card }, limpando a mesa.
scopa-you-put-down = Você coloca { $card }.
scopa-player-puts-down = { $player } coloca { $card }.
scopa-scopa-suffix =  - SCOPA!
scopa-clear-table-suffix = , limpando a mesa.
scopa-remaining-cards = { $player } leva as cartas restantes da mesa.
scopa-you-get-remaining-cards = Você leva as cartas restantes da mesa: { $cards }.
scopa-player-gets-remaining-cards = { $player } leva as cartas restantes da mesa: { $cards }.
scopa-you-instant-win = Você vence imediatamente com uma scopa!
scopa-your-team-instant-win = Sua equipe vence imediatamente com uma scopa!
scopa-instant-win = { $player } vence imediatamente com uma scopa!
scopa-scoring-round = Rodada de pontuação...
scopa-you-most-cards = Você marca 1 ponto pela maioria das cartas ({ $count } cartas).
scopa-your-team-most-cards = Sua equipe marca 1 ponto pela maioria das cartas ({ $count } cartas).
scopa-most-cards = { $player } marca 1 ponto pela maioria das cartas ({ $count } cartas).
scopa-most-cards-tie = Empate na maioria das cartas - nenhum ponto atribuído.
scopa-you-most-diamonds = Você marca 1 ponto pela maioria dos ouros ({ $count } ouros).
scopa-your-team-most-diamonds = Sua equipe marca 1 ponto pela maioria dos ouros ({ $count } ouros).
scopa-most-diamonds = { $player } marca 1 ponto pela maioria dos ouros ({ $count } ouros).
scopa-most-diamonds-tie = Empate na maioria dos ouros - nenhum ponto atribuído.
scopa-you-seven-diamonds = Você marca 1 ponto pelo 7 de ouros.
scopa-your-team-seven-diamonds = Sua equipe marca 1 ponto pelo 7 de ouros.
scopa-seven-diamonds = { $player } marca 1 ponto pelo 7 de ouros.
scopa-you-seven-diamonds-multi = Você marca 1 ponto pela maioria dos 7 de ouros ({ $count } x 7 de ouros).
scopa-your-team-seven-diamonds-multi = Sua equipe marca 1 ponto pela maioria dos 7 de ouros ({ $count } x 7 de ouros).
scopa-seven-diamonds-multi = { $player } marca 1 ponto pela maioria dos 7 de ouros ({ $count } × 7 de ouros).
scopa-seven-diamonds-tie = Empate nos 7 de ouros - nenhum ponto atribuído.
scopa-you-most-sevens = Você marca 1 ponto pela maioria dos setes ({ $count } setes).
scopa-your-team-most-sevens = Sua equipe marca 1 ponto pela maioria dos setes ({ $count } setes).
scopa-most-sevens = { $player } marca 1 ponto pela maioria dos setes ({ $count } setes).
scopa-most-sevens-tie = Empate na maioria dos setes - nenhum ponto atribuído.
scopa-you-primiera = Você marca 1 ponto pela primiera ({ $score } pontos).
scopa-your-team-primiera = Sua equipe marca 1 ponto pela primiera ({ $score } pontos).
scopa-primiera = { $player } marca 1 ponto pela primiera ({ $score } pontos).
scopa-primiera-tie = Empate na primiera - nenhum ponto atribuído.
scopa-primiera-none = Ninguém capturou cartas dos quatro naipes, então nenhum ponto de primiera é atribuído.
scopa-you-napola = Você marca { $points } pontos pela napola.
scopa-your-team-napola = Sua equipe marca { $points } pontos pela napola.
scopa-napola = { $player } marca { $points } pontos pela napola.

scopa-manual-select-prompt = Você deve escolher quais cartas capturar.

scopa-capture-option = Capturar { $cards }

scopa-error-conflict-escoba-asso = Escoba e Asso Piglia Tutto não podem ser ativados ao mesmo tempo.
scopa-error-conflict-instant-inverse = Vitória instantânea por scopa não pode ser ativada junto com o modo inverso.
scopa-error-conflict-instant-no-scopas = Vitória instantânea por scopa não pode ser ativada quando scopas não pontuam.

scopa-score-line-target-pending = { $player }: { $score }/{ $target } { $unit } (+{ $round_score } { $pending_unit } de Scopa pendentes nesta rodada)
scopa-score-line-pending = { $player }: { $score } { $unit } (+{ $round_score } { $pending_unit } de Scopa pendentes nesta rodada)
scopa-target-tie-continue = Vários lados empataram em { $score } { $score ->
    [one] ponto
   *[other] pontos
}, então a Scopa continua além do alvo de { $target } { $target ->
    [one] ponto
   *[other] pontos
} até que o empate seja quebrado.
scopa-round-scores = Pontuação da rodada:
scopa-round-score-line = { $player }: +{ $round_score } (total: { $total_score })
scopa-table-empty = Não há cartas na mesa.
scopa-no-such-card = Nenhuma carta nessa posição.
scopa-captured-count = Você capturou { $count } cartas

scopa-view-table = Ver mesa
scopa-view-captured = Ver capturadas
scopa-view-table-card = Ver carta da mesa { $index }
scopa-pause-timer = Pausar temporizador

scopa-hint-match =  -> { $card }
scopa-hint-multi =  -> { $count } cartas

scopa-enter-target-score = Digite a pontuação alvo (1-121)
scopa-desc-target-score = Pontuação necessária para vencer a Scopa (padrão 11, intervalo de 1 a 121).
scopa-set-cards-per-deal = Cartas por distribuição: { $cards }
scopa-enter-cards-per-deal = Digite as cartas por distribuição (1-10)
scopa-set-decks = Número de baralhos: { $decks }
scopa-enter-decks = Digite o número de baralhos (1-6)
scopa-toggle-escoba = Escoba (somar 15): { $enabled }
scopa-toggle-hints = Mostrar dicas de captura: { $enabled }
scopa-set-mechanic = Mecânica da Scopa: { $mechanic }
scopa-select-mechanic = Selecionar mecânica da scopa
scopa-toggle-instant-win = Vitória instantânea por scopa: { $enabled }
scopa-desc-team-mode = Escolhe jogo individual ou equipes de tamanho fixo para a Scopa.
scopa-toggle-team-scoring = Juntar cartas da equipe na pontuação: { $enabled }
scopa-toggle-inverse = Modo inverso (atingir o alvo = eliminação): { $enabled }
scopa-toggle-manual = Seleção manual de captura: { $enabled }
scopa-toggle-asso = Asso piglia tutto (ás leva tudo): { $enabled }
scopa-toggle-primiera = Pontuação tradicional da Primiera: { $enabled }
scopa-toggle-napola = Napola (sequência de ouros): { $enabled }

scopa-option-changed-cards = Cartas por distribuição definidas para { $cards }.
scopa-desc-cards-per-deal = Quantas cartas cada jogador recebe por distribuição na Scopa (padrão 3, intervalo de 1 a 10).
scopa-option-changed-decks = Número de baralhos definido para { $decks }.
scopa-desc-number-of-decks = Quantos baralhos de 40 cartas da Scopa são embaralhados juntos (padrão 1, intervalo de 1 a 6).
scopa-option-changed-escoba = Escoba { $enabled }.
scopa-desc-escoba = Muda as capturas para as regras de Escoba, em que a carta jogada e as cartas capturadas da mesa devem somar 15.
scopa-option-changed-hints = Dicas de captura { $enabled }.
scopa-desc-show-capture-hints = Mostra quais cartas da mesa cada carta da mão pode capturar.
scopa-option-changed-mechanic = Mecânica da Scopa definida para { $mechanic }.
scopa-desc-scopa-mechanic = Escolhe pontuação normal de varredura, sem pontos de Scopa, ou pontuação apenas por Scopas.
scopa-option-changed-instant = Vitória instantânea por scopa { $enabled }.
scopa-desc-instant-win-scopas = Quando ativada, uma Scopa válida vence o jogo imediatamente. Não pode ser combinada com Sem Scopas nem com a Scopa Inversa.
scopa-option-changed-team-scoring = Pontuação de cartas da equipe { $enabled }.
scopa-desc-team-card-scoring = Controla se os companheiros de equipe juntam as cartas capturadas para a pontuação do fim da rodada. Se desativado em um jogo de equipes, as capturas de cada jogador são avaliadas separadamente e os pontos obtidos são somados à equipe desse jogador.
scopa-option-changed-inverse = Modo inverso { $enabled }.
scopa-desc-inverse-scopa = Inverte o objetivo: atingir a pontuação alvo elimina um jogador ou equipe.
scopa-option-changed-manual = Seleção manual de captura { $enabled }.
scopa-desc-manual-selection = Permite escolher manualmente uma combinação de captura quando existe mais de uma captura válida.
scopa-option-changed-asso = Asso piglia tutto { $enabled }.
scopa-desc-asso-piglia-tutto = Ativa o ás leva tudo: um ás varre a mesa e faz scopa, a menos que outro ás já esteja na mesa. Não pode ser combinado com Escoba.
scopa-option-changed-primiera = Pontuação tradicional da Primiera { $enabled }.
scopa-desc-primiera-scoring = Ativa a pontuação tradicional da Primiera; quando desativada, o jogo usa a variante mais simples da maioria dos setes.
scopa-option-changed-napola = Napola { $enabled }.
scopa-desc-napola = Concede pontos bônus por capturar uma sequência contínua de ouros começando pelo ás.

scopa-mechanic-normal = Normal
scopa-mechanic-no_scopas = Sem Scopas
scopa-mechanic-only_scopas = Só Scopas

scopa-timer-not-active = O temporizador da rodada não está ativo.

scopa-error-not-enough-cards = Cartas insuficientes em { $decks } { $decks ->
    [one] baralho
    *[other] baralhos
} para { $players } { $players ->
    [one] jogador
    *[other] jogadores
} com { $cards_per_deal } cartas cada. (São necessárias { $cards_per_deal } × { $players } = { $cards_needed } cartas, mas há apenas { $total_cards }.)

scopa-line-format = { $rank }. { $player }: { $points }
