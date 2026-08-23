game-name-sorry = Sorry!

sorry-set-rules-profile = Perfil de regras: { $profile }
sorry-select-rules-profile = Escolha um perfil de regras
sorry-option-changed-rules-profile = Perfil de regras definido para { $profile }.
sorry-desc-rules-profile = Escolhe o perfil de regras do Sorry, incluindo o baralho clássico 00390 ou as regras básicas mais recentes no estilo A5065.
sorry-rules-profile-classic-00390 = Clássico 00390
sorry-rules-profile-a5065-core = Básico A5065

sorry-toggle-auto-apply-single-move = Aplicar automaticamente lance único: { $enabled }
sorry-option-changed-auto-apply-single-move = Aplicar automaticamente lance único definido para { $enabled }.
sorry-desc-auto-apply-single-move = Quando ativado, uma carta com apenas um lance possível é aplicada automaticamente.
sorry-toggle-faster-setup-one-pawn-out = Preparação mais rápida (um peão fora): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = Preparação mais rápida definida para { $enabled }.
sorry-desc-faster-setup-one-pawn-out = Começa cada jogador com um peão já fora para reduzir a espera no começo.
sorry-error-unsupported-rules-profile = O perfil de regras do Sorry selecionado, "{ $profile }", não é suportado. Escolha Clássico 00390 ou Básico A5065 antes de começar.

sorry-draw-card = Comprar carta
sorry-check-board = Ler tabuleiro
sorry-check-pawns = Ver seus peões
sorry-check-card = Ver carta atual
sorry-check-status = Ver status

sorry-move-slot = Opção de lance { $slot }
sorry-move-slot-fallback = Escolher lance
sorry-move-start = Mover peão { $pawn } de { $position } para fora do início
sorry-move-forward = Mover peão { $pawn } de { $position }, avançando { $steps }
sorry-move-backward = Mover peão { $pawn } de { $position }, recuando { $steps }
sorry-move-swap = Trocar o peão { $pawn } em { $position } com o peão { $target_pawn } de { $target_player } em { $target_position }
sorry-move-sorry = Usar o Sorry! com o peão { $pawn } em { $position } contra o peão { $target_pawn } de { $target_player } em { $target_position }
sorry-move-split7-pick = Dividir o 7 entre o peão { $pawn_a } em { $position_a } e o peão { $pawn_b } em { $position_b }
sorry-move-split7-option = Peão { $pawn_a } em { $position_a } anda { $steps_a }; peão { $pawn_b } em { $position_b } anda { $steps_b }

sorry-card-none = nenhuma carta ativa
sorry-card-sorry = Sorry!
sorry-choose-move = Escolha um lance.
sorry-choose-split = Escolha como dividir o 7.
sorry-error-draw-pending-move = Você já comprou uma carta. Escolha um dos lances disponíveis para ela antes de comprar novamente.

sorry-game-started = O Sorry começa. Jogadores: { $players }.
sorry-draw-announcement = { $player } compra { $card }.
sorry-you-draw-announcement = Você compra { $card }.
sorry-no-legal-moves = { $player } não tem lance possível para { $card }.
sorry-you-no-legal-moves = Você não tem lance possível para { $card }.
sorry-deck-exhausted = O baralho do Sorry acabou, então o jogo termina aqui.
sorry-you-extra-turn = Você comprou um 2 e joga outra vez.
sorry-player-extra-turn = { $player } comprou um 2 e joga outra vez.

sorry-play-start =
    { $brief ->
        [yes] { $player }: peão { $pawn } do início para { $destination }.
       *[no] { $player } coloca o peão { $pawn } fora do início, em { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] Você: peão { $pawn } do início para { $destination }.
       *[no] Você coloca o peão { $pawn } fora do início, em { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: peão { $pawn } +{ $steps } para { $destination }.
       *[no] { $player } move o peão { $pawn } { $steps } casas para frente, até { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] Você: peão { $pawn } +{ $steps } para { $destination }.
       *[no] Você move o peão { $pawn } { $steps } casas para frente, até { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: peão { $pawn } -{ $steps } para { $destination }.
       *[no] { $player } move o peão { $pawn } { $steps } casas para trás, até { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] Você: peão { $pawn } -{ $steps } para { $destination }.
       *[no] Você move o peão { $pawn } { $steps } casas para trás, até { $destination }.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: peão { $pawn } troca com o peão { $target_pawn } de { $target_player }; { $destination }.
       *[no] { $player } troca o peão { $pawn } com o peão { $target_pawn } de { $target_player } e termina em { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] Você: peão { $pawn } troca com o peão { $target_pawn } de { $target_player }; { $destination }.
       *[no] Você troca o peão { $pawn } com o peão { $target_pawn } de { $target_player } e termina em { $destination }.
    }

sorry-play-sorry =
    { $brief ->
        [yes] { $player }: Sorry! peão { $pawn } para { $destination }; peão { $target_pawn } de { $target_player } para o início.
       *[no] { $player } usa o Sorry!, substitui o peão { $target_pawn } de { $target_player } e termina em { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] Você: Sorry! peão { $pawn } para { $destination }; peão { $target_pawn } de { $target_player } para o início.
       *[no] Você usa o Sorry!, substitui o peão { $target_pawn } de { $target_player } e termina em { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: peão { $pawn_a } +{ $steps_a } para { $destination_a }; peão { $pawn_b } +{ $steps_b } para { $destination_b }.
       *[no] { $player } divide o 7: peão { $pawn_a } anda { $steps_a } casas até { $destination_a }, e peão { $pawn_b } anda { $steps_b } casas até { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] Você: peão { $pawn_a } +{ $steps_a } para { $destination_a }; peão { $pawn_b } +{ $steps_b } para { $destination_b }.
       *[no] Você divide o 7: peão { $pawn_a } anda { $steps_a } casas até { $destination_a }, e peão { $pawn_b } anda { $steps_b } casas até { $destination_b }.
    }

sorry-pawn-home = { $player } leva o peão { $pawn } ao destino.
sorry-you-pawn-home = Seu peão { $pawn } chega ao destino.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: seu peão { $pawn } para o início.
       *[no] Seu peão { $pawn } foi enviado de volta ao início por { $by_player }.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] Você: peão { $pawn } de { $target_player } para o início.
       *[no] Você envia o peão { $pawn } de { $target_player } de volta ao início.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: peão { $pawn } de { $target_player } para o início.
       *[no] { $player } envia o peão { $pawn } de { $target_player } de volta ao início.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] Você: próprio peão { $pawn } para o início.
       *[no] Você envia seu próprio peão { $pawn } de volta ao início.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: próprio peão { $pawn } para o início.
       *[no] { $player } envia o próprio peão { $pawn } de volta ao início.
    }

sorry-current-card = Carta atual: { $card }.
sorry-view-your-pawn = Seu peão { $pawn }: { $zone }.
sorry-board-your-color = Sua cor: { $color }.
sorry-board-summary-heading = Resumo rápido:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = peão { $pawn } em { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = Casas da trilha:
sorry-board-private-areas-heading = Áreas privativas:
sorry-board-square-line = Casa { $square }: { $status }
sorry-board-square-empty = vazia
sorry-board-square-slide = escorregador { $color }
sorry-board-square-token = peão { $pawn } de { $player }
sorry-board-start-line = área de início { $color } de { $player }: { $pawns }
sorry-board-safety-line = espaço seguro { $space } { $color } de { $player }: { $pawns }
sorry-board-home-line = destino { $color } de { $player }: { $pawns }
sorry-board-area-empty = vazio
sorry-board-area-pawn = peão { $pawn }
sorry-color-red = vermelho
sorry-color-blue = azul
sorry-color-yellow = amarelo
sorry-color-green = verde
sorry-location-start = início
sorry-location-track = casa { $position }
sorry-location-home-path = espaço seguro { $steps }
sorry-location-home = destino
sorry-zone-start = no início
sorry-zone-track = na casa { $position } da trilha
sorry-zone-home-path = no passo { $steps } da zona segura
sorry-zone-home = no destino

sorry-status-turn-number = Turno { $count }
sorry-status-phase = Fase: { $phase }
sorry-status-current-card = Carta: { $card }
sorry-status-current-player = Jogador atual: { $player }
sorry-phase-draw = compra
sorry-phase-choose-move = escolha de lance
sorry-phase-choose-split = divisão do 7
sorry-phase-resolving = resolvendo o lance

sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 peão no destino
   *[other] { $count } peões no destino
}
