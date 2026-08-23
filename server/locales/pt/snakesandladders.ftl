game-name-snakesandladders = Cobras e Escadas
game-snakesandladders-desc = Dispute uma corrida da área inicial até a casa 100. Suba escadas, deslize pelas cobras e seja o primeiro a chegar ao fim.

snakes-roll = Rolar dado
snakes-check-positions = Ver posições

snakes-turn-start-you = Seu turno. Sua peça está na área inicial, antes da casa 1.
snakes-turn-start-other = Turno de { $player }. A peça está na área inicial, antes da casa 1.
snakes-turn-you = Seu turno. Você está na casa { $position }.
snakes-turn-other = Turno de { $player }. Está na casa { $position }.

snakes-roll-you = Você tira { $roll }.
snakes-roll-other = { $player } tira { $roll }.
snakes-enter-you = Você sai da área inicial e vai para a casa { $position }.
snakes-enter-other = { $player } sai da área inicial e vai para a casa { $position }.
snakes-enter-you-brief = Você: casa { $position }.
snakes-enter-other-brief = { $player }: casa { $position }.
snakes-move-you = Você avança { $roll } casas, da casa { $start } para a casa { $position }.
snakes-move-other = { $player } avança { $roll } casas, da casa { $start } para a casa { $position }.
snakes-move-you-brief = Você: casa { $position }.
snakes-move-other-brief = { $player }: casa { $position }.
snakes-bounce-you = Da casa { $start }, sua tirada de { $roll } passa da casa { $target }, então você volta da chegada para a casa { $position }.
snakes-bounce-other = Da casa { $start }, { $player } tira { $roll }, passa da casa { $target } e volta da chegada para a casa { $position }.
snakes-bounce-you-brief = Você volta para a casa { $position }.
snakes-bounce-other-brief = { $player } volta para a casa { $position }.
snakes-restored-bounce-you = Sua tirada salva termina e sua peça volta para a casa { $position }.
snakes-restored-bounce-other = A tirada salva de { $player } termina e a peça volta para a casa { $position }.
snakes-exact-miss-you = Você precisa de { $needed } para chegar à casa { $target }, mas tirou { $roll } e permanece na casa { $position }.
snakes-exact-miss-other = { $player } precisa de { $needed } para chegar à casa { $target }, mas tira { $roll } e permanece na casa { $position }.
snakes-exact-miss-you-brief = Você precisa de { $needed }, tirou { $roll } e fica na casa { $position }.
snakes-exact-miss-other-brief = { $player } precisa de { $needed }, tira { $roll } e fica na casa { $position }.
snakes-ladder-you = Você cai no pé de uma escada na casa { $start } e sobe para a casa { $end }, ganhando { $distance } casas.
snakes-ladder-other = { $player } cai no pé de uma escada na casa { $start } e sobe para a casa { $end }, ganhando { $distance } casas.
snakes-ladder-you-brief = Você sobe da casa { $start } para a { $end }.
snakes-ladder-other-brief = { $player } sobe da casa { $start } para a { $end }.
snakes-snake-you = Você cai na cabeça de uma cobra na casa { $start } e desliza até a cauda na casa { $end }, perdendo { $distance } casas.
snakes-snake-other = { $player } cai na cabeça de uma cobra na casa { $start } e desliza até a cauda na casa { $end }, perdendo { $distance } casas.
snakes-snake-you-brief = Você desliza da casa { $start } para a { $end }.
snakes-snake-other-brief = { $player } desliza da casa { $start } para a { $end }.
snakes-extra-turn-you = Você tirou 6 e joga novamente a partir da casa { $position }.
snakes-extra-turn-other = { $player } tirou 6 e joga novamente a partir da casa { $position }.
snakes-win-you = Você chega à casa { $position } e vence o jogo!
snakes-win-other = { $player } chega à casa { $position } e vence o jogo!

snakes-status-goal = Meta: casa { $target }. Regra de chegada: { $rule }.
snakes-status-current-start = { $player }: área inicial antes da casa 1. Turno atual.
snakes-status-player-start = { $player }: área inicial antes da casa 1.
snakes-status-current-position = { $player }: casa { $position }, faltam { $remaining }. Turno atual.
snakes-status-player-position = { $player }: casa { $position }, faltam { $remaining }.
snakes-status-player-finished = { $player }: casa { $position }, finalizado.

snakes-finish-bounce-back = Retorno
snakes-finish-exact-stay = Tirada exata; permanece ao passar da meta
snakes-set-finish-rule = Regra de chegada: { $rule }
snakes-select-finish-rule = Selecionar regra de chegada
snakes-option-changed-finish-rule = Regra de chegada alterada para { $rule }.
snakesandladders-desc-finish-rule = Define se ultrapassar a casa 100 faz o jogador retornar ou aguardar uma tirada exata.
snakes-set-extra-turn-six = Turno extra no 6: { $enabled }
snakes-option-changed-extra-turn-six = Turno extra no 6 alterado para { $enabled }.
snakesandladders-desc-extra-turn-on-six = Controla se tirar 6 concede outro turno.

snakes-error-roll-not-playing = Você só pode rolar o dado depois que um jogo de Cobras e Escadas começar.
snakes-error-roll-not-your-turn = Você ainda não pode rolar porque outro jogador está jogando seu turno. Aguarde a vez chegar a você.
snakes-error-roll-resolving = Sua tirada anterior ainda está sendo resolvida. Aguarde a sequência de movimento, cobra ou escada terminar antes de rolar novamente.
snakes-error-positions-not-playing = As posições estão disponíveis apenas durante um jogo de Cobras e Escadas.
snakes-error-invalid-finish-rule = A regra de chegada selecionada, { $rule }, não é suportada. Escolha Retorno ou Tirada exata; permanece ao passar da meta.

snakes-end-score = { $rank }. { $player }: casa { $position }
snakes-end-score-start = { $rank }. { $player }: área inicial antes da casa 1
