game-name-pirates = Piratas dos Mares Perdidos

# Setup and round flow
pirates-welcome = Bem-vindo a Piratas dos Mares Perdidos. Navegue pela rota de quarenta casas, recupere as joias espalhadas e supere as tripulações rivais.
pirates-welcome-brief = Bem-vindo a Piratas dos Mares Perdidos.
pirates-oceans = Sua viagem cruza { $oceans }.
pirates-gems-placed = Todas as { $total } joias foram escondidas ao longo da rota. O maior valor de carga vence após a recuperação da última joia.
pirates-gems-placed-brief = { $total } joias estão escondidas ao longo da rota.
pirates-golden-moon = A Lua Dourada se eleva na rodada { $round }. Cada recompensa de EXP nesta rodada é triplicada.
pirates-golden-moon-brief = Lua Dourada: EXP tripla na rodada { $round }.
pirates-turn-you = Seu turno na rodada { $round }. Você está na posição { $position } em { $ocean }.
pirates-turn-you-brief = Seu turno. Posição { $position }.
pirates-turn = Turno de { $player } na rodada { $round }, na posição { $position } em { $ocean }.
pirates-turn-brief = Turno de { $player }.

# Movement and map information
pirates-move-left = Navegar uma casa para a esquerda
pirates-move-right = Navegar uma casa para a direita
pirates-move-2-left = Navegar duas casas para a esquerda
pirates-move-2-right = Navegar duas casas para a direita
pirates-move-3-left = Navegar três casas para a esquerda
pirates-move-3-right = Navegar três casas para a direita
pirates-move-you = Você navega { $tiles } { $tiles ->
    [one] casa
   *[other] casas
} para a { $direction } até a posição { $position } em { $ocean }.
pirates-move-you-brief = Você navega para a posição { $position }.
pirates-move = { $player } navega { $tiles } { $tiles ->
    [one] casa
   *[other] casas
} para a { $direction } até a posição { $position } em { $ocean }.
pirates-move-brief = { $player } navega para a posição { $position }.
pirates-map-edge = Você não pode navegar mais nessa direção; a posição { $position } é o limite da rota. Escolha outra ação.
pirates-dir-left = esquerda
pirates-dir-right = direita
pirates-your-position = Você está na posição { $position }, setor { $sector }, em { $ocean }.
pirates-check-position = Verificar posição
pirates-check-moon = Verificar Lua Dourada
pirates-moon-active = A Lua Dourada está ativa na rodada { $round }. A EXP é triplicada. As tripulações recuperaram { $collected } de { $total } joias, com { $remaining } restantes.
pirates-moon-inactive = A Lua Dourada não está ativa na rodada { $round }. Ela retorna em { $rounds } { $rounds ->
    [one] rodada
   *[other] rodadas
}. As tripulações recuperaram { $collected } de { $total } joias, com { $remaining } restantes.

# Status and results
pirates-check-status = Verificar status da tripulação
pirates-check-status-detailed = Status detalhado da tripulação
pirates-status-line = { $player }: nível { $level }; { $xp } EXP total, { $progress } de { $needed } EXP para o próximo nível; { $points }; { $gem_count } { $gem_count ->
    [one] joia
   *[other] joias
}{ $detail ->
    [yes] ; posição { $position } em { $ocean }; carga: { $gems }; efeitos ativos: { $skills }
    [no] { "" }
}.
pirates-end-score-line = { $rank }. { $player }: { $points }, nível { $level }
pirates-all-gems-collected = A última joia foi recuperada. As tripulações comparam suas cargas.
pirates-all-gems-collected-brief = Última joia recuperada.
pirates-you-win = Você venceu com { $score } pontos.
pirates-you-win-brief = Você vence: { $score } pontos.
pirates-winner = { $player } vence com { $score } pontos.
pirates-winner-brief = { $player } vence: { $score } pontos.
pirates-you-tie = Você empata em primeiro lugar com { $players } com { $score } pontos.
pirates-you-tie-brief = Você empata em primeiro com { $score }.
pirates-players-tie = { $players } empatam em primeiro lugar com { $score } pontos.
pirates-players-tie-brief = { $players } empatam com { $score }.

# Gems and XP
pirates-gem-found-you = Você recupera a/o { $gem }, no valor de { $value } { $value ->
    [one] ponto
   *[other] pontos
}. Sua carga agora vale { $score } pontos; { $remaining } joias continuam no mar.
pirates-gem-found-you-brief = Você recupera a/o { $gem }. Pontuação: { $score }.
pirates-gem-found = { $player } recupera a/o { $gem }, no valor de { $value } { $value ->
    [one] ponto
   *[other] pontos
}. A carga deles agora vale { $score } pontos; { $remaining } joias continuam no mar.
pirates-gem-found-brief = { $player } recupera a/o { $gem }.
pirates-xp-gained-you = Você ganha { $xp } EXP por { $reason ->
    [gem] recuperar uma joia
    [attack] acertar um tiro de canhão
    [defense] repelir um ataque de canhão
   *[other] concluir uma ação
}. Agora você tem { $total } de EXP total.
pirates-xp-gained-you-brief = Você ganha { $xp } EXP. Total: { $total }.
pirates-xp-gained-player = { $player } ganha { $xp } EXP por { $reason ->
    [gem] recuperar uma joia
    [attack] acertar um tiro de canhão
    [defense] repelir um ataque de canhão
   *[other] concluir uma ação
}, alcançando { $total } de EXP total.
pirates-xp-gained-player-brief = { $player } ganha { $xp } EXP.
pirates-level-up-you = Você alcançou o nível { $level }.
pirates-level-up-you-brief = Você alcançou o nível { $level }.
pirates-level-up = { $player } alcançou o nível { $level }.
pirates-level-up-brief = { $player } alcançou o nível { $level }.
pirates-level-up-multiple-you = Você ganhou { $levels } níveis e alcançou o nível { $level }.
pirates-level-up-multiple-you-brief = Você alcançou o nível { $level }.
pirates-level-up-multiple = { $player } ganhou { $levels } níveis e alcançou o nível { $level }.
pirates-level-up-multiple-brief = { $player } alcançou o nível { $level }.
pirates-skills-unlocked-you = No nível { $level }, você desbloqueia { $skills }.
pirates-skills-unlocked-you-brief = Você desbloqueia { $skills }.
pirates-skills-unlocked = No nível { $level }, { $player } desbloqueia { $skills }.
pirates-skills-unlocked-brief = { $player } desbloqueia { $skills }.

# Cannon combat
pirates-cannonball = Disparar bala de canhão
pirates-select-cannon-target = Escolha um navio dentro do alcance do canhão
pirates-target-option = { $player }, a { $distance } { $distance ->
    [one] casa
   *[other] casas
} de distância, { $score } pontos, transportando { $gems } { $gems ->
    [one] joia
   *[other] joias
}
pirates-target-unavailable = Navio indisponível
pirates-no-targets = Nenhum navio rival está dentro do seu alcance atual de canhão de { $range } casas. Escolha movimento ou outra habilidade disponível.
pirates-target-out-of-range = { $target } não está mais dentro do seu alcance de canhão de { $range } casas a partir da posição { $position }. Escolha outra ação.
pirates-attack-you-fire = Você dispara uma bala de canhão contra { $target }.
pirates-attack-you-fire-brief = Você dispara contra { $target }.
pirates-attack-incoming = { $attacker } dispara uma bala de canhão contra você.
pirates-attack-incoming-brief = { $attacker } dispara contra você.
pirates-attack-fired = { $attacker } dispara uma bala de canhão contra { $defender }.
pirates-attack-fired-brief = { $attacker } dispara contra { $defender }.
pirates-combat-rolls-you = Seu dado de ataque é { $attack_die }, mais { $attack_bonus }, totalizando { $attack_total }. O dado de defesa de { $defender } é { $defense_die }, mais { $defense_bonus }, totalizando { $defense_total }.
pirates-combat-rolls-you-brief = Ataque { $attack_total }; defesa { $defense_total }.
pirates-combat-rolls-defender = { $attacker } ataca com { $attack_die }, mais { $attack_bonus }, totalizando { $attack_total }. Seu dado de defesa é { $defense_die }, mais { $defense_bonus }, totalizando { $defense_total }.
pirates-combat-rolls-defender-brief = Ataque { $attack_total }; sua defesa { $defense_total }.
pirates-combat-rolls-observer = { $attacker } ataca com { $attack_die }, mais { $attack_bonus }, totalizando { $attack_total }. { $defender } defende com { $defense_die }, mais { $defense_bonus }, totalizando { $defense_total }.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total }; { $defender } { $defense_total }.
pirates-attack-hit-you = Acerto crítico. Seu { $attack_total } supera o { $defense_total } de { $target }; escolha uma ação de abordagem disponível.
pirates-attack-hit-you-brief = Você acerta { $target }, { $attack_total } a { $defense_total }.
pirates-attack-hit-them = { $attacker } acerta você, { $attack_total } a { $defense_total }, e agora pode abordar seu navio.
pirates-attack-hit-them-brief = { $attacker } acerta você, { $attack_total } a { $defense_total }.
pirates-attack-hit = { $attacker } acerta { $defender }, { $attack_total } a { $defense_total }, e pode abordar.
pirates-attack-hit-brief = { $attacker } acerta { $defender }.
pirates-attack-hit-no-boarding-you = Acerto direto. Seu { $attack_total } supera o { $defense_total } de { $target }. Este acerto de Encouraçado concede EXP, mas nenhuma ação de abordagem.
pirates-attack-hit-no-boarding-you-brief = Você acerta { $target }, { $attack_total } a { $defense_total }; sem abordagem.
pirates-attack-hit-no-boarding-them = { $attacker } acerta você, { $attack_total } a { $defense_total }. Acertos de Encouraçado não concedem ações de abordagem.
pirates-attack-hit-no-boarding-them-brief = { $attacker } acerta você; sem abordagem.
pirates-attack-hit-no-boarding = { $attacker } acerta { $defender }, { $attack_total } a { $defense_total }. Este acerto de Encouraçado não concede ação de abordagem.
pirates-attack-hit-no-boarding-brief = { $attacker } acerta { $defender }; sem abordagem.
pirates-attack-miss-you = Seu total de ataque de { $attack_total } não supera o total de defesa de { $target } de { $defense_total }. Seu turno termina.
pirates-attack-miss-you-brief = Você erra { $target }, { $attack_total } a { $defense_total }.
pirates-attack-miss-them = Você repele { $attacker } com um total de defesa de { $defense_total } contra { $attack_total }.
pirates-attack-miss-them-brief = Você repele { $attacker }, { $defense_total } a { $attack_total }.
pirates-attack-miss = { $defender } repele { $attacker }, { $defense_total } a { $attack_total }.
pirates-attack-miss-brief = { $attacker } erra { $defender }.

# Boarding
pirates-resolve-boarding = Resolver abordagem
pirates-select-boarding-action = O canhão acertou. Escolha como resolver a ação de abordagem
pirates-boarding-steal = Tentar roubar uma joia
pirates-boarding-push-left = Empurrar o defensor para a esquerda
pirates-boarding-push-right = Empurrar o defensor para a direita
pirates-boarding-option-unknown = Ação de abordagem desconhecida
pirates-must-resolve-boarding = Resolva sua ação de abordagem pendente antes de tomar outra ação de turno.
pirates-no-pending-boarding = Não há ação de abordagem pendente para você resolver.
pirates-boarding-stale = A ação de abordagem pendente não tem mais um defensor válido, portanto foi cancelada. Escolha outra ação de turno.
pirates-boarding-option-unavailable = { $action } não está mais disponível contra { $defender }. Escolha uma das opções de abordagem atuais.
pirates-push-you = Você empurra { $target } para a { $direction } da posição { $old_pos } para { $new_pos }, movendo-o por { $distance } casas. Seu bônus de Empurrão contribuiu com { $bonus } casas extras.
pirates-push-you-brief = Você empurra { $target } para a posição { $position }.
pirates-push-them = { $attacker } empurra você para a { $direction } da posição { $old_pos } para { $new_pos }, movendo-o por { $distance } casas.
pirates-push-them-brief = { $attacker } empurra você para a posição { $position }.
pirates-push = { $attacker } empurra { $defender } para a { $direction } da posição { $old_pos } para { $new_pos }, a uma distância de { $distance } casas.
pirates-push-brief = { $attacker } empurra { $defender } para a posição { $position }.
pirates-steal-rolls-you = Seu total de roubo é { $steal }; o total de guarda de { $target } é { $defend }.
pirates-steal-rolls-you-brief = Roubo { $steal }; guarda { $defend }.
pirates-steal-rolls-defender = O total de roubo de { $attacker } é { $steal }; seu total de guarda é { $defend }.
pirates-steal-rolls-defender-brief = Roubo { $steal }; sua guarda { $defend }.
pirates-steal-rolls-observer = { $attacker } tenta roubar de { $defender }: roubo { $steal }, guarda { $defend }.
pirates-steal-rolls-observer-brief = { $attacker } rouba com { $steal } contra { $defender } com { $defend }.
pirates-steal-success-you = Você rouba a/o { $gem } de { $target }. Sua carga vale { $attacker_score } pontos; a deles vale { $defender_score }.
pirates-steal-success-you-brief = Você rouba a/o { $gem } de { $target }.
pirates-steal-success-them = { $attacker } rouba sua/seu { $gem }. A carga deles vale { $attacker_score } pontos; a sua vale { $defender_score }.
pirates-steal-success-them-brief = { $attacker } rouba sua/seu { $gem }.
pirates-steal-success = { $attacker } rouba a/o { $gem } de { $defender }. Os valores das cargas deles agora são { $attacker_score } e { $defender_score } pontos, respectivamente.
pirates-steal-success-brief = { $attacker } rouba a/o { $gem } de { $defender }.
pirates-steal-failed-you = Seu total de roubo de { $steal } não supera o total de guarda de { $target } de { $defend }. Você não rouba nada.
pirates-steal-failed-you-brief = Seu roubo falha, { $steal } a { $defend }.
pirates-steal-failed-defender = Você impede o roubo de { $attacker }, { $defend } a { $steal }, e mantém sua carga.
pirates-steal-failed-defender-brief = Você impede o roubo de { $attacker }.
pirates-steal-failed = { $defender } impede o roubo de { $attacker }, { $defend } a { $steal }.
pirates-steal-failed-brief = { $attacker } falha ao roubar de { $defender }.
pirates-steal-no-gems-you = Você não pode roubar de { $target } porque eles não carregam mais nenhuma joia. Escolha um empurrão em vez disso.
pirates-steal-no-gems-you-brief = { $target } não tem joias para roubar.
pirates-steal-no-gems-defender = { $attacker } não pode roubar de você porque sua carga não contém joias.
pirates-steal-no-gems-defender-brief = Você não tem nenhuma joia para { $attacker } roubar.
pirates-steal-no-gems = { $attacker } não pode roubar de { $defender } porque o defensor não carrega joias.
pirates-steal-no-gems-brief = { $defender } não tem joias para roubar.

# Skills and skill state
pirates-use-skill = Usar uma habilidade
pirates-select-skill = Escolher uma habilidade desbloqueada
pirates-unknown-skill = Habilidade desconhecida
pirates-skill-error = { $message }
pirates-skill-selection-stale = Essa seleção de habilidade não está mais disponível no seu nível atual ou estado de jogo. Reabra o menu de habilidades e escolha uma habilidade disponível.
pirates-req-level = { $skill } requer o nível { $required }; você está no nível { $current }.
pirates-requires-level = { $action ->
    [move_2] Navegar duas casas
    [move_3] Navegar três casas
   *[other] Essa ação
} requer o nível { $required }; você está no nível { $current }.
pirates-skill-cooldown = { $name } está se recuperando por mais { $turns } turnos seus.
pirates-skill-active = { $name } já está ativo por mais { $turns } turnos seus.
pirates-skill-already-activated-this-turn = Você já ativou um bônus de combate neste turno. Faça uma ação de movimento ou canhão em seguida.
pirates-skill-no-uses = Caçador de Joias não tem mais usos restantes nesta partida.
pirates-skill-no-gems = Caçador de Joias não pode encontrar um alvo porque não restam joias não coletadas.
pirates-skill-no-targets = Nenhum navio rival está dentro do alcance atual de { $range } casas para esta habilidade.
pirates-skill-incompatible = { $skill } não pode ser ativado enquanto { $active } estiver ativo. Aguarde o efeito atual expirar.
pirates-battleship-after-buff = Encouraçado não pode ser lançado após ativar um bônus de combate neste turno. Use o bônus com um tiro normal de canhão ou aguarde até o seu próximo turno.
pirates-menu-active = { $name } (ativo por mais { $turns } turnos)
pirates-menu-cooldown = { $name } (se recuperando por mais { $turns } turnos)
pirates-menu-activate = Ativar { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } usos restantes)
pirates-active-skill-status = { $skill }, restam { $turns } turnos
pirates-no-active-skills = nenhum
pirates-skill-activated = { $player } ativa { $skill }. { $effect }
pirates-skill-activated-brief = { $player } ativa { $skill }.
pirates-buff-expired-you = Seu efeito de { $skill } expira antes que este turno comece.
pirates-buff-expired-you-brief = Seu/Sua { $skill } expira.
pirates-buff-expired = O efeito de { $skill } de { $player } expira antes que o turno dele comece.
pirates-buff-expired-brief = O/A { $skill } de { $player } expira.

pirates-skill-instinct-name = Instinto de Marinheiro
pirates-skill-instinct-desc = Revise cada setor de cinco casas, incluindo joias não coletadas e navios rivais. Esta ação de informação não encerra o turno.
pirates-instinct-header = Carta de Instinto de Marinheiro, dividida em oito setores:
pirates-instinct-sector = Setor { $sector }, posições { $start } até { $end }: { $gems } { $gems ->
    [one] joia não coletada
   *[other] joias não coletadas
 }, { $players } { $players ->
    [one] navio rival
   *[other] navios rivais
 }.

pirates-skill-portal-name = Portal
pirates-skill-portal-desc = Escolha um oceano diferente ocupado por rivais ou escolha Aleatório para se teletransportar para qualquer casa do mapa. Tempo de recarga: 3 dos seus turnos.
pirates-resolve-portal = Escolher destino do Portal
pirates-select-portal-ocean = Escolha um oceano diferente ocupado por rivais ou escolha Aleatório para qualquer casa do mapa
pirates-portal-option = { $ocean }; navios: { $ships }; { $gems } { $gems ->
    [one] joia não coletada
   *[other] joias não coletadas
}
pirates-portal-option-random = Casa aleatória do mapa
pirates-portal-option-unavailable = Esse oceano não é um destino de Portal válido porque é o seu oceano atual ou nenhum navio rival o ocupa. Escolha outro destino.
pirates-must-resolve-portal = Como você usou o Portal, seu turno está travado nessa habilidade. Escolha um destino ou escolha Aleatório para completar o Portal e encerrar seu turno.
pirates-no-pending-portal = Não há destino de Portal pendente para você resolver.
pirates-portal-no-ships = Nenhum destino de Portal em oceano rival específico está disponível, mas Aleatório ainda pode enviá-lo para qualquer casa do mapa.
pirates-portal-fizzle-you = Seu destino de Portal não é mais válido. Escolha Aleatório para se teletransportar para qualquer lugar do mapa ou escolha outro destino válido.
pirates-portal-fizzle-you-brief = Escolha Aleatório ou outro destino de Portal válido.
pirates-portal-fizzle = O destino de Portal de { $player } não é mais válido.
pirates-portal-fizzle-brief = { $player } deve escolher outro destino de Portal.
pirates-portal-success-you = Você viaja através do Portal para { $ocean }, chegando à posição { $position }. O Portal entra em recarga por 3 dos seus turnos.
pirates-portal-success-you-brief = Você se teletransporta para a posição { $position } em { $ocean }.
pirates-portal-success = { $player } viaja através de um Portal para { $ocean }, chegando à posição { $position }.
pirates-portal-success-brief = { $player } se teletransporta para a posição { $position }.

pirates-skill-seeker-name = Caçador de Joias
pirates-skill-seeker-desc = Revele a posição exata de uma joia não coletada. Três usos por partida; usá-lo não encerra o turno.
pirates-gem-seeker-reveal = Caçador de Joias localiza a/o { $gem } na posição { $position }. Você tem { $uses } usos restantes nesta partida.

pirates-skill-sword-name = Espadachim
pirates-skill-sword-desc = Ganhe +2 de ataque por 3 dos seus turnos. Recarga: 6 turnos. Não pode se sobrepor a Capitão Experiente.
pirates-sword-fighter-activated = Você ativa Espadachim: +{ $bonus } de ataque por { $turns } dos seus turnos. Recarga: { $cooldown } turnos. Você ainda pode se mover ou disparar neste turno.
pirates-sword-fighter-activated-brief = Espadachim ativo: +{ $bonus } de ataque.

pirates-skill-push-name = Velocidade de Abarroamento
pirates-skill-push-desc = Adicione 2 casas aos empurrões de abordagem por 3 dos seus turnos. Recarga: 6 turnos.
pirates-push-activated = Você ativa Velocidade de Abarroamento: +{ $bonus } casas aos empurrões de abordagem por { $turns } dos seus turnos. Recarga: { $cooldown } turnos. Você ainda pode se mover ou disparar neste turno.
pirates-push-activated-brief = Velocidade de Abarroamento ativa: +{ $bonus } de distância de empurrão.

pirates-skill-captain-name = Capitão Experiente
pirates-skill-captain-desc = Ganhe +1 de ataque e +1 de defesa por 4 dos seus turnos. Recarga: 7 turnos. Não pode se sobrepor a Espadachim.
pirates-skilled-captain-activated = Você ativa Capitão Experiente: +{ $attack } de ataque e +{ $defense } de defesa por { $turns } dos seus turnos. Recarga: { $cooldown } turnos. Você ainda pode se mover ou disparar neste turno.
pirates-skilled-captain-activated-brief = Capitão Experiente ativo: +{ $attack } de ataque, +{ $defense } de defesa.

pirates-skill-battleship-name = Encouraçado
pirates-skill-battleship-desc = Dispare dois tiros de canhão visando a tripulação, sem recompensas de abordagem. Isso encerra o turno. Recarga: 4 turnos.
pirates-battleship-activated = Você lança o Encouraçado por { $shots } tiros de canhão. Sua tripulação seleciona o alvo mais valioso ao alcance para cada tiro; acertos não concedem abordagem. Recarga: { $cooldown } turnos.
pirates-battleship-activated-brief = Você lança o Encouraçado por { $shots } tiros.
pirates-battleship-activated-player = { $player } lança o Encouraçado por { $shots } tiros de canhão. Acertos desses tiros não concedem abordagem.
pirates-battleship-activated-player-brief = { $player } lança o Encouraçado.
pirates-battleship-shot = Sua tripulação dispara o tiro { $shot } do Encouraçado contra { $target }.
pirates-battleship-shot-brief = Tiro { $shot } contra { $target }.
pirates-battleship-shot-player = A tripulação de { $player } dispara o tiro { $shot } do Encouraçado contra { $target }.
pirates-battleship-shot-player-brief = { $player } dispara contra { $target }.
pirates-battleship-no-targets = Sua tripulação não pode disparar o tiro { $shot } porque nenhum rival permanece dentro de { $range } casas. O Encouraçado termina.
pirates-battleship-no-targets-brief = Nenhum alvo para o tiro { $shot }.
pirates-battleship-no-targets-player = { $player } não pode disparar o tiro { $shot } do Encouraçado porque nenhum rival permanece dentro de { $range } casas.
pirates-battleship-no-targets-player-brief = { $player } não tem alvo para o tiro { $shot }.

pirates-skill-devastation-name = Dupla Devastação
pirates-skill-devastation-desc = Aumente o alcance normal do canhão de 5 para 10 casas por 3 dos seus turnos. Recarga: 10 turnos. Incompatível com Encouraçado.
pirates-double-devastation-activated = Você ativa Dupla Devastação: o alcance do canhão passa a ser de { $range } casas por { $turns } dos seus turnos. Recarga: { $cooldown } turnos. Você ainda pode se mover ou disparar neste turno.
pirates-double-devastation-activated-brief = Dupla Devastação ativa: alcance { $range }.

# Options and validation
pirates-set-combat-xp-multiplier = Multiplicador de EXP de combate: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Insira um multiplicador de EXP de combate de 0,1 a 3,0
pirates-option-changed-combat-xp = Multiplicador de EXP de combate definido para { $combat_multiplier }.
pirates-desc-combat-xp-multiplier = Dimensiona a EXP de acertos de canhão e defesas bem-sucedidas. O multiplicador da Lua Dourada é aplicado separadamente (padrão 1,0, intervalo de 0,1 a 3,0).
pirates-set-find-gem-xp-multiplier = Multiplicador de EXP de recuperação de joias: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Insira um multiplicador de EXP de recuperação de joias de 0,1 a 3,0
pirates-option-changed-find-gem-xp = Multiplicador de EXP de recuperação de joias definido para { $find_gem_multiplier }.
pirates-desc-find-gem-xp-multiplier = Dimensiona a EXP concedida quando um navio recupera uma joia, inclusive após movimento forçado (padrão 1,0, intervalo de 0,1 a 3,0).
pirates-set-gem-stealing = Roubo de joias: { $mode }
pirates-select-gem-stealing = Escolha como as rolagens de roubo em abordagem usam bônus de combate
pirates-option-changed-stealing = Roubo de joias definido para { $mode }.
pirates-desc-gem-stealing = Controla se o roubo de joias está disponível após um acerto direto e se os bônus ativos de ataque e defesa modificam a rolagem de roubo.
pirates-stealing-with-bonus = Habilitado com bônus de combate
pirates-stealing-no-bonus = Habilitado sem bônus de combate
pirates-stealing-disabled = Desabilitado; a abordagem só pode empurrar
pirates-error-combat-xp-range = O multiplicador de EXP de combate é { $value }, fora do intervalo suportado de { $min } a { $max }. Defina-o dentro desse intervalo antes de começar.
pirates-error-gem-xp-range = O multiplicador de EXP de recuperação de joias é { $value }, fora do intervalo suportado de { $min } a { $max }. Defina-o dentro desse intervalo antes de começar.
pirates-error-stealing-mode = O modo de roubo de joias armazenado, { $mode }, não é suportado. Escolha um dos modos de roubo de joias listados antes de começar.

# Ocean names
pirates-ocean-rory = Oceano de Rory
pirates-ocean-dev = Abismo do Desenvolvedor
pirates-ocean-par = Mar do Paraíso do Programador
pirates-ocean-pal = Águas do Palácio
pirates-ocean-sil = Estreito de Silva
pirates-ocean-kai = Corrente de Kai
pirates-ocean-gam = Golfo do Gamer
pirates-ocean-ser = Mar da Sala de Servidores
pirates-ocean-bat = Baía da Batalha
pirates-ocean-cod = Canal de Compilação de Código
pirates-ocean-unknown = Oceano Desconhecido

# Gem names
pirates-gem-0 = opala
pirates-gem-1 = rubi
pirates-gem-2 = granada
pirates-gem-3 = diamante
pirates-gem-4 = safira
pirates-gem-5 = esmeralda
pirates-gem-6 = joia do palácio
pirates-gem-7 = joia de plástico grande
pirates-gem-8 = pedra azul maldita incrível
pirates-gem-9 = ametista
pirates-gem-10 = anel de ouro
pirates-gem-11 = pedra vermelha pulpstone incrível
pirates-gem-12 = pedra vermelha gorestone incrível
pirates-gem-13 = pedra da lua
pirates-gem-14 = lápis-lazúli
pirates-gem-15 = âmbar
pirates-gem-16 = citrino
pirates-gem-17 = pérola negra definitivamente não amaldiçoada (tm)
pirates-gem-unknown = joia desconhecida
pirates-gem-none = nenhuma joia
