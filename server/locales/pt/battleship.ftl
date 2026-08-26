game-name-battleship = Batalha Naval

# Options
battleship-set-grid-size = Zona de combate: { $size }
battleship-select-grid-size = Selecione o tamanho da zona de combate
battleship-option-changed-grid-size = Zona de combate definida para { $size }.
battleship-desc-grid-size = Escolhe o tamanho da grade oceânica para Batalha Naval; grades maiores criam buscas mais longas.

battleship-set-placement-mode = Implantação: { $mode }
battleship-select-placement-mode = Selecione o modo de implantação
battleship-option-changed-placement-mode = Modo de implantação definido para { $mode }.
battleship-desc-placement-mode = Escolhe se os navios são posicionados automática ou manualmente antes do início da batalha.

battleship-set-replay-on-hit = Salva extra ao acertas: { $enabled }
battleship-option-changed-replay-on-hit = Salva extra ao acertar definida para { $enabled }.
battleship-desc-replay-on-hit = Quando ativado, um jogador que pontua um acerto efetua imediatamente outro disparo.

battleship-set-turn-timer = Temporizador de turno: { $seconds }
battleship-select-turn-timer = Selecione o temporizador de turno
battleship-option-changed-turn-timer = Temporizador de turno definido para { $seconds }.
battleship-desc-turn-timer = Limite de tempo opcional para cada turno de Batalha Naval; se o tempo esgotar, o jogo dispara em uma coordenada aleatória. Escolha Ilimitado para nenhum temporizador.

# Option choice labels
battleship-grid-6x6 = 6 por 6
battleship-grid-8x8 = 8 por 8
battleship-grid-10x10 = 10 por 10
battleship-grid-12x12 = 12 por 12

battleship-placement-auto = Automática
battleship-placement-manual = Manual

battleship-timer-off = Desligado
battleship-timer-30 = 30 segundos
battleship-timer-45 = 45 segundos
battleship-timer-60 = 60 segundos

# Setup validation
battleship-error-invalid-grid-size = O tamanho da zona de combate { $size } não é suportado.
battleship-error-grid-too-small = A zona de combate de { $size } por { $size } é muito pequena para a frota completa. Use pelo menos { $minimum } por { $minimum }.
battleship-error-invalid-placement-mode = O modo de implantação { $mode } não é suportado.
battleship-error-invalid-turn-timer = O temporizador de turno { $seconds } não é suportado.

# Ship names
battleship-ship-carrier = Porta-aviões
battleship-ship-battleship = Couraçado
battleship-ship-destroyer = Destruidor
battleship-ship-submarine = Submarino
battleship-ship-patrol = Lancha Patrulha
battleship-ship-unknown = Embarcação

# Orientations
battleship-horizontal = Horizontal
battleship-vertical = Vertical

# Actions
battleship-orient-horizontal = Implantar na Horizontal
battleship-orient-vertical = Implantar na Vertical
battleship-orient-horizontal-at = Implantar { $ship } horizontalmente em { $coord }
battleship-orient-vertical-at = Implantar { $ship } verticalmente em { $coord }
battleship-select-orientation = Selecione a orientação de implantação
battleship-toggle-view = Alternar Grade
battleship-read-fleet = Status da Frota
battleship-read-enemy-fleet = Informações da Frota Inimiga

# Deployment phase
battleship-deploy-start = Fase de implantação. Posicione seu { $ship }, com { $size } setores de comprimento. Selecione uma coordenada e escolha a orientação.
battleship-choose-orientation = Implantando { $ship } em { $coord }, { $size } setores. Selecione a orientação.
battleship-ship-placed = { $ship } implantado em { $coord }, orientação { $orientation }.
battleship-cannot-place = Não é possível implantar { $ship } em { $coord } { $orientation }. A embarcação não cabe ou se sobrepõe a outro navio.
battleship-place-next-ship = Próxima embarcação: { $ship }, { $size } setores.
battleship-deploy-done = Frota implantada. Aguardando o inimigo.
battleship-deploy-complete = Implantação concluída.
battleship-select-cell-first = Selecione primeiro uma coordenada na grade.
battleship-deploy-in-progress = Implantação ainda em andamento.
battleship-deploy-status-header = Fase de posicionamento de navios.
battleship-deploy-status-ready-self = Você está pronto.
battleship-deploy-status-ready-other = { $player } está pronto.
battleship-deploy-status-not-ready-self = Você ainda não está pronto.
battleship-deploy-status-not-ready-other = { $player } ainda não está pronto.

# Battle phase
battleship-battle-start = Todos os navios em posição. Comecem a disparar!

# Hit — first-person (shooter), second-person (target), third-person (spectator)
battleship-hit-self = Você dispara em { $coord }. Acerto em cheio!
battleship-hit-target = { $player } dispara no seu { $coord }. Acerto em cheio!
battleship-hit-spectator = { $player } dispara em { $coord } de { $target }. Acerto em cheio!

# Miss — first/second/third
battleship-miss-self = Você dispara em { $coord }. Água.
battleship-miss-target = { $player } dispara no seu { $coord }. Água.
battleship-miss-spectator = { $player } dispara em { $coord } de { $target }. Água.

# Sunk — first/second/third
battleship-sunk-self = Você afundou o { $ship } inimigo!
battleship-sunk-target = { $player } afundou o seu { $ship }!
battleship-sunk-spectator = { $player } afundou o { $ship } de { $target }!

# Victory — first/second/third
battleship-victory-self = Você venceu! Todas as embarcações inimigas foram afundadas.
battleship-victory-target = { $player } venceu! Todas as suas embarcações foram afundadas.
battleship-victory-spectator = { $player } venceu! Todas as embarcações de { $target } foram afundadas.

battleship-shot-in-flight = Um projétil ainda está em voo. Aguarde o resultado antes de disparar novamente.
battleship-not-your-turn = Não é o seu turno de disparar. Aguarde { $player } escolher uma coordenada.
battleship-wait-for-turn = Aguarde a próxima ordem de disparo antes de escolher uma coordenada.
battleship-already-shot = Você já disparou em { $coord }. Escolha uma coordenada não mapeada.
battleship-switch-to-shots = Você está visualizando suas próprias águas, portanto o disparo está bloqueado. Pressione V para alternar para a grade de alvos.
battleship-timeout-fire = Tempo esgotado! Disparando automaticamente em { $coord }.

# View toggle
battleship-view-own = Visualizando suas águas.
battleship-view-shots = Visualizando grade de alvos.

# Cell labels
battleship-cell-empty = { $coord }, mar aberto.
battleship-cell-ship-placed = { $coord }, { $ship }.
battleship-cell-unknown = { $coord }, não mapeado.
battleship-cell-hit = { $coord }, atingido.
battleship-cell-sunk = { $coord }, { $ship }, afundado.
battleship-cell-miss = { $coord }, água.
battleship-cell-own-ship = { $coord }, seu { $ship }.
battleship-cell-own-hit = { $coord }, seu { $ship }, atingido.
battleship-cell-own-sunk = { $coord }, seu { $ship }, afundado.
battleship-cell-own-miss = { $coord }, tiro inimigo na água.

# Fleet status
battleship-fleet-header = Sua Frota
battleship-status-intact = Pronto para o combate
battleship-status-damaged = Danificado ({ $hits } de { $size } atingidos)
battleship-status-sunk = Afundado

battleship-enemy-fleet-header = Frota Inimiga
battleship-enemy-fleet-summary = { $sunk } de { $total } embarcações inimigas afundadas.
battleship-enemy-ship-sunk = { $ship } (tamanho { $size }): Afundado

# End screen
battleship-winner-line = { $player } venceu!
battleship-stats-line = { $player }: { $shots } disparos efetuados, { $hits } acertos, precisão de { $accuracy }%
