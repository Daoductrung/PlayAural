game-name-fivecarddraw = Pôquer de Cinco Cartas

draw-set-starting-chips = Fichas iniciais: { $count }
draw-enter-starting-chips = Digite as fichas iniciais
draw-option-changed-starting-chips = Fichas iniciais definidas para { $count }.
fivecarddraw-desc-starting-chips = Pilha inicial de cada jogador no Five Card Draw, de 100 a 1.000.000 fichas. Padrão: 20.000.

draw-set-ante = Ante: { $count }
draw-enter-ante = Digite o valor do ante
draw-option-changed-ante = Ante definido para { $count }.
fivecarddraw-desc-ante = Contribuição obrigatória que cada jogador ativo coloca antes de cada mão. Deve ser menor que a pilha inicial (padrão 100, intervalo 0-1.000.000 de fichas).

draw-set-turn-timer = Temporizador de turno: { $mode }
draw-select-turn-timer = Selecionar temporizador de turno
draw-option-changed-turn-timer = Temporizador de turno definido para { $mode }.
fivecarddraw-desc-turn-timer = Limite de tempo opcional para cada decisão de aposta ou troca: 5, 10, 15, 20, 30, 45, 60 ou 90 segundos, ou Ilimitado. Padrão: Ilimitado.

draw-set-raise-mode = Modo de aumento: { $mode }
draw-select-raise-mode = Selecionar modo de aumento
draw-option-changed-raise-mode = Modo de aumento definido para { $mode }.
fivecarddraw-desc-raise-mode = Estilo de limite de aumento: Sem limite, Limite do pote ou Limite do pote duplo. Os modos baseados no pote exigem um ante maior que 0 para que a primeira rodada de apostas possa abrir normalmente (padrão Sem limite).

draw-set-max-raises = Máximo de aumentos por rodada de apostas: { $count }
draw-enter-max-raises = Digite o máximo de aumentos por rodada de apostas (0 para ilimitado)
draw-option-changed-max-raises = Máximo de aumentos por rodada de apostas definido para { $count }.
fivecarddraw-desc-max-raises = Máximo de aumentos permitidos em uma rodada de apostas, de 0 a 10. Defina 0 para sem limite de aumentos. Padrão: 0.

draw-set-draw-limit = Regra de troca: { $mode }
draw-select-draw-limit = Selecionar regra de troca
draw-option-changed-draw-limit = Regra de troca definida para { $mode }.
fivecarddraw-desc-draw-limit = Regra de troca: troque até 3 cartas, ou permita 4 cartas apenas ao manter um Ás. Padrão: até 3 cartas.
draw-limit-three-cards = Até 3 cartas (padrão)
draw-limit-four-with-ace = Até 4 cartas ao manter um ás

draw-error-ante-too-high = O ante ({ $ante } fichas) deve ser menor que a pilha inicial ({ $chips } fichas) para que os jogadores ainda possam tomar decisões de aposta após a distribuição.
draw-error-capped-mode-needs-ante = { $mode ->
    [pot_limit] Limite do pote
    [double_pot] Limite do pote duplo
   *[other] Este modo de aumento limitado
} exige um ante maior que 0 para que o primeiro jogador tenha um valor baseado no pote disponível para apostar.

draw-antes-posted = Os antes foram apostados. O pote agora contém { $amount } fichas.
draw-betting-round-1 = Primeira rodada de apostas.
draw-betting-round-2 = Segunda rodada de apostas.
draw-begin-draw = Fase de troca. Começando pelo primeiro jogador ativo à esquerda do dealer, escolha as cartas para trocar ou mantenha a mão.
draw-not-draw-phase = A troca de cartas está disponível apenas após a primeira rodada de apostas. Continue com a ação de apostas atual.
draw-not-betting = As apostas estão indisponíveis durante a fase de troca. Selecione quaisquer cartas para trocar e, em seguida, escolha Trocar cartas.
draw-fold-not-available = Correr está indisponível durante a fase de troca. Selecione quaisquer cartas para trocar e, em seguida, escolha Trocar cartas.

draw-toggle-discard = Selecionar carta { $index } para trocar
draw-card-keep = { $card }
draw-card-discard = { $card }, selecionada para troca
draw-draw-cards = Trocar cartas
draw-draw-cards-count = { $count ->
    [0] Manter todas
    [one] Trocar 1 carta
   *[other] Trocar { $count } cartas
}
draw-dealt-cards = Suas cinco cartas são { $cards }.
draw-you-drew-cards = Suas { $count } { $count ->
    [one] carta de substituição é
   *[other] cartas de substituição são
} { $cards }.
draw-you-draw = Você troca { $count } { $count ->
    [one] carta
   *[other] cartas
}.
draw-player-draws = { $player } troca { $count } { $count ->
    [one] carta
   *[other] cartas
}.
draw-you-stand-pat = Você mantém todas as cinco cartas.
draw-player-stands-pat = { $player } mantém todas as cinco cartas.
draw-you-discard-limit = Você não pode trocar mais do que { $count } cartas sob a regra de troca selecionada.
draw-four-requires-kept-ace = Trocar 4 cartas exige que você mantenha pelo menos um ás. Desmarque um ás ou troque no máximo 3 cartas.

draw-raise-invalid = Digite um número inteiro maior que 0 para o valor do aumento.
draw-raise-cap-reached = O limite de { $count } aumentos já foi atingido nesta rodada de apostas. Você pode pagar ou correr.
draw-raise-over-stack = Você tentou aumentar em { $requested } fichas, mas tem apenas { $chips } fichas restantes. Digite um aumento menor ou escolha All-in.
draw-raise-too-small = Você tentou aumentar em { $requested } fichas. O aumento mínimo é { $minimum } fichas.
draw-raise-over-limit = Você tentou aumentar em { $requested } fichas. Sob { $mode ->
    [pot_limit] o limite do pote
    [double_pot] o limite do pote duplo
   *[other] o modo de aumento selecionado
}, o maior aumento disponível após pagar é { $maximum } fichas.
draw-all-in-over-limit = Você não pode ir all-in com suas { $stack } fichas restantes porque { $mode ->
    [pot_limit] o limite do pote
    [double_pot] o limite do pote duplo
   *[other] o modo de aumento selecionado
} atualmente permite um aumento de no máximo { $maximum } fichas após pagar. Use Aumentar para digitar um valor permitido.
draw-all-in-raise-cap-reached = Você não pode ir all-in como um aumento total porque o limite de { $count } aumentos já foi atingido. Você pode pagar ou correr.
draw-all-in-unavailable-raise-cap = O all-in está indisponível porque seria um aumento total após o limite de aumentos ser atingido. Você pode pagar ou correr.
draw-all-in-unavailable-limit = O all-in está indisponível porque sua pilha excede o limite de apostas atual. Use Aumentar para digitar um valor permitido.
draw-raise-unavailable-cap = O aumento está indisponível porque esta rodada de apostas atingiu seu limite de aumentos.
draw-raise-unavailable-limit = Um aumento total está indisponível com sua pilha e o limite de apostas atual. Você pode pagar, correr ou usar All-in quando for legal.

draw-current-bet = A aposta atual na mesa é { $amount } fichas.
draw-raise-range = O aumento mínimo é { $minimum } fichas. Você pode aumentar em até { $maximum } fichas após pagar.
draw-no-full-raise-available = Você precisa de { $to_call } fichas para pagar e tem { $chips } fichas restantes, portanto não pode fazer um aumento total. Você pode pagar all-in ou correr.
draw-dealer-unavailable = Ainda não há uma posição de dealer para a mão atual.
draw-position-unavailable = Você não está ativo na mão atual, portanto não tem uma posição de aposta.

draw-card-key = Chave da carta { $index }

draw-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
