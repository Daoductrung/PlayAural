game-name-leftrightcenter = Esquerda Centro Direita

lrc-roll = Rolar { $count } { $count ->
    [one] dado
   *[other] dados
}
lrc-roll-label = Rolar dados

lrc-face-left = Esquerda
lrc-face-center = Centro
lrc-face-right = Direita
lrc-face-dot = Ponto

lrc-you-roll = Você rola { $results }.
lrc-player-rolls = { $player } rola { $results }.
lrc-you-roll-brief = Você: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = Você passa { $count } { $count ->
    [one] ficha
   *[other] fichas
} à esquerda para { $target }. Você tem { $remaining } restantes; { $target } agora tem { $target_total }.
lrc-player-passes-left = { $player } passa { $count } { $count ->
    [one] ficha
   *[other] fichas
} à esquerda para { $target }. { $player } tem { $remaining } restantes; { $target } agora tem { $target_total }.
lrc-you-pass-left-brief = Você, à esquerda para { $target }: { $count }. Restantes: { $remaining }.
lrc-player-passes-left-brief = { $player }, à esquerda para { $target }: { $count }. Restantes: { $remaining }.

lrc-you-pass-right = Você passa { $count } { $count ->
    [one] ficha
   *[other] fichas
} à direita para { $target }. Você tem { $remaining } restantes; { $target } agora tem { $target_total }.
lrc-player-passes-right = { $player } passa { $count } { $count ->
    [one] ficha
   *[other] fichas
} à direita para { $target }. { $player } tem { $remaining } restantes; { $target } agora tem { $target_total }.
lrc-you-pass-right-brief = Você, à direita para { $target }: { $count }. Restantes: { $remaining }.
lrc-player-passes-right-brief = { $player }, à direita para { $target }: { $count }. Restantes: { $remaining }.

lrc-you-pass-center = Você coloca { $count } { $count ->
    [one] ficha
   *[other] fichas
} no centro. Você tem { $remaining } restantes; o centro agora possui { $center }.
lrc-player-passes-center = { $player } coloca { $count } { $count ->
    [one] ficha
   *[other] fichas
} no centro. { $player } tem { $remaining } restantes; o centro agora possui { $center }.
lrc-you-pass-center-brief = Você, centro: { $count }. Restantes: { $remaining }. Total do centro: { $center }.
lrc-player-passes-center-brief = { $player }, centro: { $count }. Restantes: { $remaining }. Total do centro: { $center }.

lrc-you-keep-all = Todos os seus dados são pontos, então você mantém todas as { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-player-keeps-all = Todos os dados de { $player } são pontos, então eles mantêm todas as { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-you-keep-all-brief = Você: sem transferências; { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-player-keeps-all-brief = { $player }: sem transferências; { $count } { $count ->
    [one] ficha
   *[other] fichas
}.

lrc-you-skip-no-chips = Você não tem fichas, então seu turno é pulado. Você continua no jogo e pode receber fichas de qualquer vizinho.
lrc-player-skips-no-chips = { $player } não tem fichas, então o turno dele é pulado. Ele continua no jogo e pode receber fichas de qualquer vizinho.
lrc-you-skip-no-chips-brief = Você: sem fichas; turno pulado.
lrc-player-skips-no-chips-brief = { $player }: sem fichas; turno pulado.

lrc-you-win = Você é o último jogador com fichas e vence com { $count } restantes. Você reivindica as { $center } { $center ->
    [one] ficha
   *[other] fichas
} no centro.
lrc-player-wins = { $player } é o último jogador com fichas e vence com { $count } restantes. Ele reivindica as { $center } { $center ->
    [one] ficha
   *[other] fichas
} no centro.
lrc-you-win-brief = Você vence. Suas fichas: { $count }. Centro: { $center }.
lrc-player-wins-brief = { $player } vence. Fichas: { $count }. Centro: { $center }.

lrc-roll-already-resolving = Sua rolagem já está sendo resolvida. Aguarde o término das transferências de fichas.
lrc-no-chips-to-roll = Você não tem fichas para rolar. Seu turno será pulado automaticamente.

lrc-center-pot = Pote central: { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-check-center = Verificar pote central
lrc-check-last-roll = Verificar última rolagem
lrc-last-roll-none = Nenhum dado foi rolado ainda.
lrc-last-roll-you = Sua última rolagem foi { $results }.
lrc-last-roll-player = { $player } rolou por último { $results }.

lrc-set-starting-chips = Fichas iniciais: { $count }
lrc-enter-starting-chips = Digite as fichas iniciais:
lrc-option-changed-starting-chips = Fichas iniciais definidas para { $count }.
leftrightcenter-desc-starting-chips = Com quantas fichas cada jogador de Left Right Center começa (padrão 3, intervalo de 1 a 10).
lrc-error-starting-chips-invalid = As fichas iniciais devem estar entre { $min } e { $max }; o valor atual é { $count }.

lrc-line-format = { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
