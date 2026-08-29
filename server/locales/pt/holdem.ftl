game-name-holdem = Poker Texas Hold'em

holdem-set-starting-chips = Fichas iniciais: { $count }
holdem-enter-starting-chips = Digite as fichas iniciais
holdem-option-changed-starting-chips = Fichas iniciais definidas para { $count }.
holdem-desc-starting-chips = Pilha inicial de cada jogador no Texas Hold'em, de 100 a 1.000.000 fichas. Padrão: 20.000.

holdem-set-big-blind = Blind grande: { $count }
holdem-enter-big-blind = Digite o big blind
holdem-option-changed-big-blind = Big blind definido para { $count }.
holdem-desc-big-blind = Valor base do big blind. Deve ser menor que a pilha inicial (padrão 200, intervalo 1-1.000.000 de fichas).

holdem-set-ante = Ante: { $count }
holdem-enter-ante = Digite o ante
holdem-option-changed-ante = Ante definido para { $count }.
holdem-desc-ante = Contribuição obrigatória opcional que cada jogador ativo coloca quando os antes estão ativos, de 0 a 1.000.000 de fichas. Padrão: 0.

holdem-set-ante-start = Ante começa no nível: { $count }
holdem-enter-ante-start = Digite o nível de blinds para ativar o ante
holdem-option-changed-ante-start = Nível de início do ante definido para { $count }.
holdem-desc-ante-start-level = Nível de blind em que os antes começam. Um ante positivo fica ativo desde a primeira mão quando este valor é 0 (padrão 0, intervalo 0-20).

holdem-set-turn-timer = Temporizador de turno: { $mode }
holdem-select-turn-timer = Selecionar temporizador de turno
holdem-option-changed-turn-timer = Temporizador de turno definido para { $mode }.
holdem-desc-turn-timer = Limite de tempo opcional para cada decisão no Hold'em: 5, 10, 15, 20, 30, 45, 60 ou 90 segundos, ou Ilimitado. Padrão: Ilimitado.

holdem-set-blind-timer = Temporizador de blind: { $mode }
holdem-select-blind-timer = Selecionar temporizador de blind
holdem-option-changed-blind-timer = Temporizador de blind definido para { $mode }.
holdem-desc-blind-timer = Minutos entre os aumentos de blind: 5, 10, 15, 20 ou 30. Padrão: 20 minutos.

holdem-set-raise-mode = Modo de aumento: { $mode }
holdem-select-raise-mode = Selecionar modo de aumento
holdem-option-changed-raise-mode = Modo de aumento definido para { $mode }.
holdem-desc-raise-mode = Estilo de limite de aumento: Sem limite, Limite do pote ou Limite do pote duplo. Padrão: Sem limite.

holdem-set-max-raises = Máximo de aumentos por rodada de apostas: { $count }
holdem-enter-max-raises = Digite o máximo de aumentos por rodada de apostas (0 para ilimitado)
holdem-option-changed-max-raises = Máximo de aumentos por rodada de apostas definido para { $count }.
holdem-desc-max-raises = Máximo de aumentos permitidos em uma rodada de apostas, de 0 a 10. Defina 0 para sem limite de aumentos. Padrão: 0.

holdem-error-big-blind-too-high = O big blind ({ $blind } fichas) deve ser menor que a pilha inicial ({ $chips } fichas).
holdem-error-ante-too-high = O ante ({ $ante } fichas) deve ser menor que a pilha inicial ({ $chips } fichas).
holdem-error-forced-bets-too-high = Com os antes ativos a partir do nível 0, o ante mais o big blind ({ $ante } + { $blind } fichas) devem ser menores que a pilha inicial ({ $chips } fichas).

holdem-antes-posted = Os antes foram apostados. O pote agora contém { $amount } fichas.
holdem-you-post-small-blind = Você aposta o small blind ({ $sb } fichas). { $bb_player } aposta o big blind ({ $bb } fichas).
holdem-you-post-big-blind = { $sb_player } aposta o small blind ({ $sb } fichas). Você aposta o big blind ({ $bb } fichas).
holdem-players-post-blinds = { $sb_player } aposta o small blind ({ $sb } fichas). { $bb_player } aposta o big blind ({ $bb } fichas).

holdem-raise-invalid = Digite um número inteiro maior que 0 para o valor do aumento.
holdem-raise-cap-reached = O limite de { $count } aumentos já foi atingido nesta rodada de apostas. Você pode pagar ou correr.
holdem-raise-over-stack = Você tentou aumentar em { $requested } fichas, mas tem apenas { $chips } fichas restantes. Digite um aumento menor ou escolha All-in.
holdem-raise-too-small = Você tentou aumentar em { $requested } fichas. O aumento mínimo é { $minimum } fichas.
holdem-raise-over-limit = Você tentou aumentar em { $requested } fichas. Sob { $mode ->
    [pot_limit] o limite do pote
    [double_pot] o limite do pote duplo
   *[other] o modo de aumento selecionado
}, o maior aumento disponível após pagar é { $maximum } fichas.
holdem-all-in-over-limit = Você não pode ir all-in com suas { $stack } fichas restantes porque { $mode ->
    [pot_limit] o limite do pote
    [double_pot] o limite do pote duplo
   *[other] o modo de aumento selecionado
} atualmente permite um aumento de no máximo { $maximum } fichas após pagar. Use Aumentar para digitar um valor permitido.
holdem-all-in-raise-cap-reached = Você não pode ir all-in como um aumento total porque o limite de { $count } aumentos já foi atingido. Você pode pagar ou correr.
holdem-all-in-unavailable-raise-cap = O all-in está indisponível porque seria um aumento total após o limite de aumentos ser atingido. Você pode pagar ou correr.
holdem-all-in-unavailable-limit = O all-in está indisponível porque sua pilha excede o limite de apostas atual. Use Aumentar para digitar um valor permitido.
holdem-raise-unavailable-cap = O aumento está indisponível porque esta rodada de apostas atingiu seu limite de aumentos.
holdem-raise-unavailable-limit = Um aumento total está indisponível com sua pilha e o limite de apostas atual. Você pode pagar, correr ou usar All-in quando for legal.

holdem-current-bet = A aposta atual na mesa é { $amount } fichas.
holdem-raise-range = O aumento mínimo é { $minimum } fichas. Você pode aumentar em até { $maximum } fichas após pagar.
holdem-no-full-raise-available = Você precisa de { $to_call } fichas para pagar e tem { $chips } fichas restantes, portanto não pode fazer um aumento total. Você pode pagar all-in ou correr.
holdem-button-unavailable = Ainda não há uma posição de botão para a mão atual.
holdem-position-unavailable = Você não está ativo na mão atual, portanto não tem uma posição de aposta.
holdem-reveal-no-live-hand = Você pode revelar as cartas particulares apenas quando chegar ao showdown com uma mão ativa.
holdem-private-hand-unavailable = Você está sem fichas e não tem mais uma mão ativa para ler.

holdem-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
