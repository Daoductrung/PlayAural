game-name-farkle = Farkle

farkle-roll = Rolar { $count } { $count ->
    [one] dado
   *[other] dados
}
farkle-bank = Guardar { $points } pontos

farkle-take-single-one = Um 1 isolado por { $points } pontos
farkle-take-single-five = Um 5 isolado por { $points } pontos
farkle-take-three-kind = Três { $number }s por { $points } pontos
farkle-take-four-kind = Quatro { $number }s por { $points } pontos
farkle-take-five-kind = Cinco { $number }s por { $points } pontos
farkle-take-six-kind = Seis { $number }s por { $points } pontos
farkle-take-small-straight = Sequência menor por { $points } pontos
farkle-take-large-straight = Sequência maior por { $points } pontos
farkle-take-three-pairs = Três pares por { $points } pontos
farkle-take-double-triplets = Tripletos duplos por { $points } pontos
farkle-take-full-house = Quadra com um par por { $points } pontos

farkle-you-roll = Você rola { $count } { $count ->
    [one] dado
   *[other] dados
}.
farkle-player-rolls = { $player } rola { $count } { $count ->
    [one] dado
   *[other] dados
}.
farkle-you-roll-brief = Você rola { $count }.
farkle-player-rolls-brief = { $player } rola { $count }.
farkle-roll-result = Os dados mostram: { $dice }.
farkle-roll-result-brief = Dados: { $dice }.

farkle-you-farkle = FARKLE! Você perde { $points } pontos do turno.
farkle-player-farkles = FARKLE! { $player } perde { $points } pontos do turno.
farkle-you-farkle-brief = Farkle: você perde { $points }.
farkle-player-farkles-brief = Farkle: { $player } perde { $points }.

farkle-you-take-combo = Você guarda { $combo } por { $points } pontos.
farkle-player-takes-combo = { $player } guarda { $combo } por { $points } pontos.
farkle-you-take-combo-brief = Você: { $combo }, +{ $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }, +{ $points }.

farkle-you-hot-dice = Dados quentes! Você pontuou com todos os seis dados e pode rolar todos os seis novamente.
farkle-player-hot-dice = Dados quentes! { $player } pontuou com todos os seis dados e pode rolar todos os seis novamente.
farkle-you-hot-dice-brief = Você: dados quentes.
farkle-player-hot-dice-brief = { $player }: dados quentes.

farkle-you-bank = Você guarda { $points } pontos. Seu total agora é { $total }.
farkle-player-banks = { $player } guarda { $points } pontos e chega a um total de { $total }.
farkle-you-bank-brief = Você guarda { $points}; total { $total }.
farkle-player-banks-brief = { $player } guarda { $points}; total { $total }.

farkle-you-win = Você vence com { $score } pontos!
farkle-winner = { $player } vence com { $score } pontos!
farkle-you-win-brief = Você vence: { $score }.
farkle-winner-brief = { $player } vence: { $score }.
farkle-winners-tie = Empate no alvo! Jogadores no desempate: { $players }.
farkle-tiebreaker-round-start = Rodada de desempate { $round }. Ainda competindo: { $players }.

farkle-your-turn-score = Você tem { $points } pontos neste turno.
farkle-turn-score = { $player } tem { $points } pontos neste turno.
farkle-no-turn = Ninguém está jogando no momento.

farkle-set-target-score = Pontuação alvo: { $score }
farkle-enter-target-score = Digite a pontuação alvo (500-5000):
farkle-option-changed-target = Pontuação alvo definida para { $score }.
farkle-desc-target-score = Pontuação necessária para acionar os turnos finais de Farkle e potencialmente vencer (padrão 1000, intervalo 500-5000).

farkle-set-entrance-score = Pontuação mínima de entrada: { $score }
farkle-enter-entrance-score = Digite a pontuação mínima de entrada (0-5000):
farkle-option-changed-entrance = Pontuação mínima de entrada definida para { $score }.
farkle-desc-min-entrance-score = Pontuação de turno mínima necessária para guardar os primeiros pontos de um jogador. Não pode ser maior que a pontuação alvo (padrão 50, intervalo 0-5000).

farkle-set-bank-score = Pontuação mínima para guardar: { $score }
farkle-enter-bank-score = Digite a pontuação mínima para guardar (0-5000):
farkle-option-changed-bank = Pontuação mínima para guardar definida para { $score }.
farkle-desc-min-bank-score = Pontuação de turno mínima necessária antes que a ação de guardar esteja disponível após o jogador já estar no tabuleiro. Não pode ser maior que a pontuação alvo (padrão 30, intervalo 0-5000).

farkle-error-entrance-above-target = A pontuação mínima de entrada ({ $entrance }) não pode ser maior que a pontuação alvo ({ $target }).
farkle-error-bank-above-target = A pontuação mínima para guardar ({ $bank }) não pode ser maior que a pontuação alvo ({ $target }).

farkle-must-take-combo = Você deve guardar pelo menos um dado ou combinação pontuável antes de rolar novamente.
farkle-cannot-bank = Você só pode guardar pontos depois de guardar um dado ou combinação pontuável neste turno.
farkle-must-reach-entrance-score = Você precisa de pelo menos { $points } pontos no turno antes de guardar sua primeira pontuação.
farkle-must-reach-bank-score = Você precisa de pelo menos { $points } pontos no turno antes de guardar.
farkle-confirm-risky-roll = Você pode guardar { $points } pontos agora. Rolar novamente arrisca perdê-los; repita a rolagem dentro de { $seconds } segundos para confirmar.
farkle-invalid-combo-action = Essa escolha de pontuação não foi reconhecida. Escolha uma das combinações listadas atualmente.
farkle-combo-no-longer-available = Essa combinação de pontuação não está mais disponível. As opções de pontuação atuais foram atualizadas.

farkle-combo-single-1 = 1 isolado
farkle-combo-single-5 = 5 isolado
farkle-combo-three-kind = Três { $number }s
farkle-combo-four-kind = Quatro { $number }s
farkle-combo-five-kind = Cinco { $number }s
farkle-combo-six-kind = Seis { $number }s
farkle-combo-small-straight = Sequência menor
farkle-combo-large-straight = Sequência maior
farkle-combo-three-pairs = Três pares
farkle-combo-double-triplets = Tripletos duplos
farkle-combo-full-house = Quadra com um par

farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } por { $points } pontos

farkle-check-turn-score = Verificar pontuação do turno
farkle-roll-label = Rolar dados
farkle-bank-label = Guardar pontos
