# Age of Heroes game messages
# A civilization-building card game for 2-6 players

# Game name
game-name-ageofheroes = Era dos Heróis

# Tribes
ageofheroes-tribe-egyptians = Egípcios
ageofheroes-tribe-romans = Romanos
ageofheroes-tribe-greeks = Gregos
ageofheroes-tribe-babylonians = Babilônios
ageofheroes-tribe-celts = Celtas
ageofheroes-tribe-chinese = Chineses

# Special Resources (for monuments)
ageofheroes-special-limestone = Calcário
ageofheroes-special-concrete = Concreto
ageofheroes-special-marble = Mármore
ageofheroes-special-bricks = Tijolos
ageofheroes-special-sandstone = Arenito
ageofheroes-special-granite = Granito

# Standard Resources
ageofheroes-resource-iron = Ferro
ageofheroes-resource-wood = Madeira
ageofheroes-resource-grain = Grão
ageofheroes-resource-stone = Pedra
ageofheroes-resource-gold = Ouro

# Events
ageofheroes-event-population-growth = Crescimento Populacional
ageofheroes-event-earthquake = Terremoto
ageofheroes-event-eruption = Erupção
ageofheroes-event-hunger = Fome
ageofheroes-event-barbarians = Bárbaros
ageofheroes-event-olympics = Jogos Olímpicos
ageofheroes-event-hero = Herói
ageofheroes-event-fortune = Sorte

# Buildings
ageofheroes-building-army = Exército
ageofheroes-building-fortress = Fortaleza
ageofheroes-building-general = General
ageofheroes-building-road = Estrada
ageofheroes-building-city = Cidade

# Actions
ageofheroes-action-tax-collection = Coleta de Impostos
ageofheroes-action-construction = Construção
ageofheroes-action-war = Guerra
ageofheroes-action-do-nothing = Não Fazer Nada
ageofheroes-play = Jogar
ageofheroes-play-card-label = Jogar { $card }
ageofheroes-card-count = { $count } { $card }
ageofheroes-player-tribe = { $player } ({ $tribe })
ageofheroes-player-tribe-direction = { $player } ({ $tribe }) - { $direction }

# War goals
ageofheroes-war-conquest = Conquista
ageofheroes-war-plunder = Saque
ageofheroes-war-destruction = Destruição

# Game options
ageofheroes-set-victory-cities = Cidades de vitória: { $cities }
ageofheroes-enter-victory-cities = Digite o número de cidades para vencer (3-7)
ageofheroes-set-victory-monument = Conclusão do monumento: { $progress }%
ageofheroes-set-max-hand = Tamanho máximo da mão: { $cards } cartas

# Option change announcements
ageofheroes-option-changed-victory-cities = A vitória requer { $cities } cidades.
ageofheroes-desc-victory-cities = Quantas cidades um lado precisa controlar para vencer Age of Heroes (padrão 5, intervalo de 3 a 7).
ageofheroes-option-changed-victory-monument = Limite de conclusão do monumento definido para { $progress }%.
ageofheroes-option-changed-max-hand = Tamanho máximo da mão definido para { $cards } cartas.

# Setup phase
ageofheroes-setup-start = Você é o líder da tribo { $tribe }. Seu recurso especial de monumento é { $special }. Role os dados para determinar a ordem dos turnos.
ageofheroes-setup-viewer = Os jogadores estão rolando os dados para determinar a ordem dos turnos.
ageofheroes-roll-dice = Rolar os dados
ageofheroes-war-roll-dice = Rolar os dados
ageofheroes-dice-result = Você tirou { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = { $player } tirou { $total }.
ageofheroes-dice-tie = Vários jogadores empataram com { $total }. Rolando novamente...
ageofheroes-first-player = { $player } tirou o valor mais alto com { $total } e começa.
ageofheroes-first-player-you = Com { $total } pontos, você começa.
ageofheroes-whose-turn-setup = Fase de configuração. Aguardando { $players } rolar para definir a ordem.
ageofheroes-whose-turn-setup-resolving = Fase de configuração. Todos os dados lançados; definindo a ordem dos turnos.
ageofheroes-whose-turn-prepare = Fase de preparação. Eventos e desastres sendo resolvidos.
ageofheroes-whose-turn-fair = Fase de mercado. { $players } ainda podem negociar.
ageofheroes-whose-turn-fair-resolving = Fase de mercado. Negociações sendo resolvidas.
ageofheroes-whose-turn-road = Fase de permissão de estrada. { $responder } deve responder à solicitação de estrada de { $requester }.
ageofheroes-whose-turn-olympics = Guerra declarada. { $defender } deve decidir se usará os Jogos Olímpicos contra { $attacker }.
ageofheroes-whose-turn-war-attack = Preparação para guerra. { $attacker } está escolhendo as forças contra { $defender }.
ageofheroes-whose-turn-war-defense = Preparação para guerra. { $defender } está escolhendo as forças de defesa contra { $attacker }.
ageofheroes-whose-turn-war-roll = Fase de batalha. Aguardando { $players } rolar.
ageofheroes-whose-turn-game-over = O jogo acabou.

# Preparation phase
ageofheroes-prepare-start = Os jogadores devem jogar cartas de evento e descartar desastres.
ageofheroes-prepare-your-turn = Você tem { $count } { $count ->
    [one] carta
    *[other] cartas
} para jogar ou descartar.
ageofheroes-prepare-done = Fase de preparação concluída.

# Events played/discarded
ageofheroes-population-growth = { $player } joga Crescimento Populacional e constrói uma nova cidade.
ageofheroes-population-growth-you = Você joga Crescimento Populacional e constrói uma nova cidade.
ageofheroes-discard-card = { $player } descarta { $card }.
ageofheroes-discard-card-you = Você descarta { $card }.
ageofheroes-earthquake = Um terremoto atinge a tribo de { $player }; os exércitos entram em recuperação.
ageofheroes-earthquake-you = Um terremoto atinge sua tribo; seus exércitos entram em recuperação.
ageofheroes-eruption = Uma erupção destrói uma das cidades de { $player }.
ageofheroes-eruption-you = Uma erupção destrói uma de suas cidades.

# Disaster effects
ageofheroes-hunger-strikes = A fome ataca.
ageofheroes-lose-card-hunger = Você perde { $card }.
ageofheroes-barbarians-pillage = Os bárbaros atacam os recursos de { $player }.
ageofheroes-barbarians-attack = Os bárbaros atacam os recursos de { $player }.
ageofheroes-barbarians-attack-you = Os bárbaros atacam seus recursos.
ageofheroes-lose-card-barbarians = Você perde { $card }.
ageofheroes-block-with-card = { $player } bloqueia o desastre usando { $card }.
ageofheroes-block-with-card-you = Você bloqueia o desastre usando { $card }.

# Targeted disaster cards (Earthquake/Eruption)
ageofheroes-select-disaster-target = Selecione um alvo para { $card }.
ageofheroes-no-targets = Nenhum alvo válido disponível.
ageofheroes-earthquake-strikes-you = { $attacker } joga Terremoto contra você. Seus exércitos estão desativados.
ageofheroes-earthquake-strikes = { $attacker } joga Terremoto contra { $player }.
ageofheroes-armies-disabled = { $count } { $count ->
    [one] exército está desativado
    *[other] exércitos estão desativados
} por um turno.
ageofheroes-eruption-strikes-you = { $attacker } joga Erupção contra você. Uma de suas cidades foi destruída.
ageofheroes-eruption-strikes = { $attacker } joga Erupção contra { $player }.
ageofheroes-city-destroyed = Uma cidade foi destruída pela erupção.

# Fair phase
ageofheroes-fair-start = O dia amanhece no mercado.
ageofheroes-fair-draw-base = Você compra { $count } { $count ->
    [one] carta
    *[other] cartas
}.
ageofheroes-fair-draw-roads = Você compra { $count } { $count ->
    [one] carta adicional
    *[other] cartas adicionais
} graças à sua rede de estradas.
ageofheroes-fair-draw-other = { $player } compra { $count } { $count ->
    [one] carta
    *[other] cartas
}.

# Trading/Auction
ageofheroes-auction-start = O leilão começa.
ageofheroes-offer-trade = Oferecer troca
ageofheroes-offer-made = { $player } oferece { $card } por { $wanted }.
ageofheroes-offer-made-you = Você oferece { $card } por { $wanted }.
ageofheroes-trade-accepted = { $player } aceita a oferta de { $other } e troca { $give } por { $receive }.
ageofheroes-trade-accepted-you = Você aceita a oferta de { $other } e recebe { $receive }.
ageofheroes-trade-cancelled = { $player } retira sua oferta por { $card }.
ageofheroes-trade-cancelled-you = Você retira sua oferta por { $card }.
ageofheroes-stop-trading = Parar de Negociar
ageofheroes-select-request = Você está oferecendo { $card }. O que quer em troca?
ageofheroes-cancel = Cancelar
ageofheroes-left-auction = { $player } partiu.
ageofheroes-left-auction-you = Você saiu do mercado.
ageofheroes-already-left-auction = Você já saiu do mercado.
ageofheroes-any-card = Qualquer carta
ageofheroes-cannot-trade-own-special = Você não pode negociar seu próprio recurso especial de monumento.
ageofheroes-resource-not-in-game = Este recurso especial não está sendo usado nesta partida.

# Main play phase
ageofheroes-play-start = Fase de ação.
ageofheroes-day = Dia { $day }
ageofheroes-draw-card = { $player } compra uma carta do baralho.
ageofheroes-draw-card-you = Você compra { $card } do baralho.
ageofheroes-draw-card-brief = { $player } comprou.
ageofheroes-draw-card-you-brief = Compra: { $card }.
ageofheroes-your-action = O que você deseja fazer?
ageofheroes-your-action-brief = Ação?

# Tax Collection
ageofheroes-tax-collection = { $player } escolhe Coleta de Impostos: { $cities } { $cities ->
    [one] cidade coleta
    *[other] cidades coletam
} { $cards } { $cards ->
    [one] carta
    *[other] cartas
}.
ageofheroes-tax-collection-you = Você escolhe Coleta de Impostos: { $cities } { $cities ->
    [one] cidade coleta
    *[other] cidades coletam
} { $cards } { $cards ->
    [one] carta
    *[other] cartas
}.
ageofheroes-tax-collection-brief = { $player } imposto: { $cards } de { $cities }.
ageofheroes-tax-collection-you-brief = Imposto: { $cards } de { $cities }.
ageofheroes-tax-no-city = Coleta de Impostos: Você não tem cidades sobreviventes. Descarte uma carta para comprar uma nova.
ageofheroes-tax-no-city-done = { $player } escolhe Coleta de Impostos mas não tem cidades, então troca uma carta.
ageofheroes-tax-no-city-done-you = Coleta de Impostos: Você trocou { $card } por uma nova carta.

# Construction
ageofheroes-construction-menu = O que você deseja construir?
ageofheroes-construction-done = { $player } construiu { $building }.
ageofheroes-construction-done-you = Você construiu { $building }.
ageofheroes-build-cost-resource = { $count ->
    [one] { $resource }
    *[other] { $count }x { $resource }
}
ageofheroes-build-menu-label = { $building } ({ $cost })
ageofheroes-construction-stop = Parar de construir
ageofheroes-construction-stopped = Você decidiu parar de construir.
ageofheroes-road-select-neighbor = Selecione o vizinho para construir uma estrada.
ageofheroes-direction-left = À sua esquerda
ageofheroes-direction-right = À sua direita
ageofheroes-road-request-sent = Solicitação de estrada enviada. Aguardando a aprovação do vizinho.
ageofheroes-road-request-received = { $requester } pede permissão para construir uma estrada até sua tribo.
ageofheroes-road-request-denied-you = Você recusou a solicitação de estrada.
ageofheroes-road-request-denied = { $denier } recusou sua solicitação de estrada.
ageofheroes-road-built = { $tribe1 } e { $tribe2 } agora estão conectadas por estrada.
ageofheroes-road-no-target = Nenhuma tribo vizinha disponível para construção de estrada.
ageofheroes-approve = Aprovar
ageofheroes-deny = Recusar
ageofheroes-supply-exhausted = Não há mais { $building } disponíveis para construir.

# Do Nothing
ageofheroes-do-nothing = { $player } passa a vez.
ageofheroes-do-nothing-you = Você passa a vez...
ageofheroes-do-nothing-brief = { $player } passa.
ageofheroes-do-nothing-you-brief = Passar.
ageofheroes-confirm-do-nothing = Passar pula sua ação neste turno. Pressione Não Fazer Nada novamente para confirmar.

# War
ageofheroes-war-declare = { $attacker } declara guerra contra { $defender }. Objetivo: { $goal }.
ageofheroes-war-prepare = Selecione seus exércitos para { $action }.
ageofheroes-war-no-army = Você não tem exércitos ou cartas de herói disponíveis.
ageofheroes-war-no-tribe = Você não tem uma tribo nesta batalha.
ageofheroes-war-no-targets = Nenhum alvo válido para guerra.
ageofheroes-war-no-valid-goal = Nenhum objetivo de guerra válido contra este alvo.
ageofheroes-war-invalid-forces = Essas forças não são mais válidas. Revise seus exércitos, gerais e cartas de Herói disponíveis.
ageofheroes-war-select-target = Selecione qual jogador atacar.
ageofheroes-war-select-goal = Selecione seu objetivo de guerra.
ageofheroes-war-prepare-attack = Selecione suas forças de ataque.
ageofheroes-war-prepare-defense = { $attacker } está atacando você; Selecione suas forças de defesa.
ageofheroes-war-force-add-armies = Adicionar um exército. Exércitos comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-armies = Remover um exército. Exércitos comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-generals = Adicionar um general. Gerais comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-generals = Remover um general. Gerais comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-hero-armies = Adicionar um Herói como exército. Exércitos de heróis comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-hero-armies = Remover um exército de herói. Exércitos de heróis comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-hero-generals = Adicionar um Herói como general. Gerais de heróis comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-hero-generals = Remover um general de herói. Gerais de heróis comprometidos: { $current } de { $max }.
ageofheroes-war-force-unit-armies = exércitos
ageofheroes-war-force-unit-generals = gerais
ageofheroes-war-force-unit-hero-armies = exércitos de herói
ageofheroes-war-force-unit-hero-generals = gerais de herói
ageofheroes-war-force-max = Já está no máximo: { $unit } ({ $max }).
ageofheroes-war-force-min = Nenhum comprometido: { $unit }.
ageofheroes-war-force-updated = Forças comprometidas: { $armies } exércitos, { $generals } gerais, { $hero_armies } exércitos de herói, { $hero_generals } gerais de herói.
ageofheroes-war-attack = Atacar...
ageofheroes-war-defend = Defender...
ageofheroes-war-clear-forces = Limpar forças
ageofheroes-war-prepared = Suas forças: { $armies } { $armies ->
    [one] exército
    *[other] exércitos
}{ $generals ->
    [0] {""}
    [one] {" e 1 general"}
    *[other] { " e " }{ $generals } gerais
}{ $heroes ->
    [0] {""}
    [one] {" e 1 herói"}
    *[other] { " e " }{ $heroes } heróis
}.
ageofheroes-war-roll-you = Você tira { $roll }.
ageofheroes-war-roll-other = { $player } tira { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] +1 da fortaleza = { $total } total
        *[other] +{ $fortress } das fortalezas = { $total } total
    }
    *[other] { $fortress ->
        [0] +{ $general } do general = { $total } total
        [1] +{ $general } do general, +1 da fortaleza = { $total } total
        *[other] +{ $general } do general, +{ $fortress } das fortalezas = { $total } total
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] { $player }: +1 da fortaleza = { $total } total
        *[other] { $player }: +{ $fortress } das fortalezas = { $total } total
    }
    *[other] { $fortress ->
        [0] { $player }: +{ $general } do general = { $total } total
        [1] { $player }: +{ $general } do general, +1 da fortaleza = { $total } total
        *[other] { $player }: +{ $general } do general, +{ $fortress } das fortalezas = { $total } total
    }
}
ageofheroes-war-bonuses-you-brief = Bônus +{ $bonus } = { $total }.
ageofheroes-war-bonuses-other-brief = Bônus de { $player } +{ $bonus } = { $total }.

# Battle
ageofheroes-battle-start = A batalha começa. { $att_armies } { $att_armies ->
    [one] exército
    *[other] exércitos
} de { $attacker } contra { $def_armies } { $def_armies ->
    [one] exército
    *[other] exércitos
} de { $defender }.
ageofheroes-battle-start-brief = Batalha: { $attacker } { $att_armies } vs { $defender } { $def_armies }.
ageofheroes-dice-roll-detailed = { $name } tira { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } do general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 da fortaleza" }
    *[other] { " + { $fortress } das fortalezas" }
} = { $total }.
ageofheroes-dice-roll-detailed-you = Você tira { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } do general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 da fortaleza" }
    *[other] { " + { $fortress } das fortalezas" }
} = { $total }.
ageofheroes-round-attacker-wins = { $attacker } vence a rodada ({ $att_total } vs { $def_total }). { $defender } perde um exército.
ageofheroes-round-defender-wins = { $defender } defende com sucesso ({ $def_total } vs { $att_total }). { $attacker } perde um exército.
ageofheroes-round-draw = Empate em { $total }. Nenhum exército perdido.
ageofheroes-round-attacker-wins-brief = { $attacker } { $att_total } vence { $defender } { $def_total }. { $defender } -1 exército.
ageofheroes-round-defender-wins-brief = { $defender } { $def_total } vence { $attacker } { $att_total }. { $attacker } -1 exército.
ageofheroes-round-draw-brief = Empate { $total }. Sem perdas.
ageofheroes-you-win-battle-as-attacker = Você derrota { $defender }.
ageofheroes-you-lose-battle-as-defender = { $attacker } derrota você.
ageofheroes-battle-victory-attacker = { $attacker } derrota { $defender }.
ageofheroes-you-lose-battle-as-attacker = { $defender } se defende com sucesso contra você.
ageofheroes-you-win-battle-as-defender = Você se defende com sucesso contra { $attacker }.
ageofheroes-battle-victory-defender = { $defender } se defende com sucesso contra { $attacker }.
ageofheroes-you-draw-battle = Você e { $opponent } perdem todas as forças comprometidas na batalha.
ageofheroes-battle-mutual-defeat = Tanto { $attacker } quanto { $defender } perdem todas as forças comprometidas na batalha.
ageofheroes-general-bonus = +{ $count } { $count ->
    [one] do general
    *[other] dos generais
}
ageofheroes-fortress-bonus = +{ $count } da defesa da fortaleza
ageofheroes-battle-winner = { $winner } vence a batalha.
ageofheroes-battle-draw = A batalha termina em empate...
ageofheroes-battle-continue = Continuar a batalha.
ageofheroes-battle-end = A batalha acabou.

# War outcomes
ageofheroes-conquest-success = { $attacker } conquista { $count } { $count ->
    [one] cidade
    *[other] cidades
} de { $defender }.
ageofheroes-plunder-success = { $attacker } saqueia { $count } { $count ->
    [one] carta
    *[other] cartas
} de { $defender }.
ageofheroes-destruction-success = { $attacker } destrói { $count } { $count ->
    [one] recurso de monumento
    *[other] recursos de monumento
} de { $defender }.
ageofheroes-conquest-success-brief = { $attacker } leva { $count } { $count ->
    [one] cidade
    *[other] cidades
} de { $defender }.
ageofheroes-plunder-success-brief = { $attacker } leva { $count } { $count ->
    [one] carta
    *[other] cartas
} de { $defender }.
ageofheroes-destruction-success-brief = { $attacker } destrói { $count } { $count ->
    [one] recurso
    *[other] recursos
} de monumento de { $defender }.
ageofheroes-army-losses = { $player } perde { $count } { $count ->
    [one] exército
    *[other] exércitos
}.
ageofheroes-army-losses-you = Você perde { $count } { $count ->
    [one] exército
    *[other] exércitos
}.

# Army return
ageofheroes-army-return-road = Suas tropas retornam imediatamente via estrada.
ageofheroes-army-return-delayed = { $count } { $count ->
    [one] unidade retorna
    *[other] unidades retornam
} no final do seu próximo turno.
ageofheroes-army-returned = As tropas de { $player } retornaram da guerra.
ageofheroes-army-returned-you = Suas tropas retornaram da guerra.
ageofheroes-army-recover = Os exércitos de { $player } se recuperam do terremoto.
ageofheroes-army-recover-you = Seus exércitos se recuperam do terremoto.

# Olympics
ageofheroes-you-cancel-war-with-olympics = Você joga Jogos Olímpicos, cancelando a guerra declarada.
ageofheroes-player-cancels-war-with-olympics = { $player } joga Jogos Olímpicos, cancelando a guerra declarada.
ageofheroes-olympics-prompt = { $attacker } declarou guerra. Você tem Jogos Olímpicos - deseja usá-lo para cancelar?
ageofheroes-yes = Sim
ageofheroes-no = Não

# Monument progress
ageofheroes-monument-progress = O monumento de { $player } está { $count }/5 concluído.
ageofheroes-monument-progress-you = Seu monumento está { $count }/5 concluído.

# Hand management
ageofheroes-discard-excess = Você tem mais de { $max } cartas. Descarte { $count } { $count ->
    [one] carta
    *[other] cartas
}.
ageofheroes-discard-excess-other = { $player } deve descartar o excesso de cartas.
ageofheroes-discard-more = Descarte mais { $count } { $count ->
    [one] carta
    *[other] cartas
}.

# Victory
ageofheroes-victory-cities = { $player } construiu { $cities } cidades! Império das Cidades.
ageofheroes-victory-cities-you = Você construiu { $cities } cidades! Império das Cidades.
ageofheroes-victory-monument = { $player } concluiu seu monumento! Portadores da Grande Cultura.
ageofheroes-victory-monument-you = Você concluiu seu monumento! Portadores da Grande Cultura.
ageofheroes-victory-last-standing = { $player } é a última tribo sobrevivente! Os Mais Persistentes.
ageofheroes-victory-last-standing-you = Você é a última tribo sobrevivente! Os Mais Persistentes.
ageofheroes-game-over = Fim de Jogo.
ageofheroes-final-winner = Vencedor: { $player }
ageofheroes-final-days = Dias jogados: { $days }

# Elimination
ageofheroes-eliminated = { $player } foi eliminado.
ageofheroes-eliminated-you = Você foi eliminado.

# Hand
ageofheroes-check-hand = Verificar mão
ageofheroes-hand-empty = Você não tem cartas.
ageofheroes-initial-hand = Sua mão inicial ({ $count } { $count ->
    [one] carta
    *[other] cartas
}): { $cards }
ageofheroes-hand-contents = Sua mão ({ $count } { $count ->
    [one] carta
    *[other] cartas
}): { $cards }

# Status
ageofheroes-check-status = Verificar status
ageofheroes-check-status-detailed = Status detalhado
ageofheroes-status = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] cidade
    *[other] cidades
}, { $armies } { $armies ->
    [one] exército
    *[other] exércitos
}, { $monument }/5 monumento
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-cities = Cidades: { $count }
ageofheroes-status-armies = Exércitos: { $count }
ageofheroes-status-generals = Gerais: { $count }
ageofheroes-status-fortresses = Fortalezas: { $count }
ageofheroes-status-monument = Monumento: { $count }/5
ageofheroes-status-roads = Estradas: { $left }{ $right }
ageofheroes-status-road-left = esquerda
ageofheroes-status-road-right = direita
ageofheroes-status-none = nenhum
ageofheroes-status-earthquake-armies = Exércitos recuperando: { $count }
ageofheroes-status-returning-armies = Exércitos retornando: { $count }
ageofheroes-status-returning-generals = Gerais retornando: { $count }
ageofheroes-status-detailed-line = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] cidade
    *[other] cidades
}, { $armies } { $armies ->
    [one] exército
    *[other] exércitos
}, { $generals } { $generals ->
    [one] general
    *[other] gerais
}, { $fortresses } { $fortresses ->
    [one] fortaleza
    *[other] fortalezas
}, monumento { $monument }/5, estradas: { $roads }{ $details }
ageofheroes-status-detail-recovering-armies = { $count } { $count ->
    [one] exército se recuperando
    *[other] exércitos se recuperando
}
ageofheroes-status-detail-returning-armies = { $count } { $count ->
    [one] exército retornando
    *[other] exércitos retornando
}
ageofheroes-status-detail-returning-generals = { $count } { $count ->
    [one] general retornando
    *[other] gerais retornando
}

# Deck info
ageofheroes-deck-empty = Não há mais cartas de { $card } no baralho.
ageofheroes-deck-count = Cartas restantes: { $count }
ageofheroes-deck-reshuffled = A pilha de descarte foi reembaralhada no baralho.

# Give up
ageofheroes-give-up-confirm = Tem certeza de que deseja desistir?
ageofheroes-gave-up = { $player } desistiu!
ageofheroes-gave-up-you = Você desistiu!

# Hero card
ageofheroes-hero-use = Usar como exército ou general?
ageofheroes-hero-army = Exército
ageofheroes-hero-general = General

# Fortune card
ageofheroes-you-use-fortune = Você usa Sorte para rolar novamente o dado de batalha.
ageofheroes-player-uses-fortune = { $player } usa Sorte para rolar novamente o dado de batalha.
ageofheroes-fortune-prompt = Você perdeu a rolagem. Deseja usar Sorte para rolar novamente?

# Disabled action reasons
ageofheroes-not-your-turn = Não é o seu turno.
ageofheroes-game-not-started = O jogo ainda não começou.
ageofheroes-wrong-phase = Esta ação não está disponível na fase atual.
ageofheroes-invalid-player = Esta ação não está disponível para você.
ageofheroes-not-in-game = Você não está nesta partida.
ageofheroes-not-in-war = Você não está envolvido nesta guerra.
ageofheroes-already-rolled = Você já rolou os dados.
ageofheroes-invalid-card-index = Essa carta não está mais disponível.
ageofheroes-no-card-selected = Selecione uma carta primeiro.
ageofheroes-no-cards-to-discard = Você não tem cartas para descartar.
ageofheroes-disaster-too-early = Cartas de desastre só podem ser jogadas a partir do dia 2.
ageofheroes-no-resources = Você não tem os recursos necessários.
ageofheroes-cannot-accept-own-offer = Você não pode aceitar sua própria oferta de troca.
ageofheroes-offerer-unavailable = Essa oferta de troca não está mais disponível.
ageofheroes-offered-card-unavailable = A carta oferecida não está mais disponível.
ageofheroes-trade-card-type-mismatch = A carta selecionada não corresponde ao tipo de carta solicitado.
ageofheroes-trade-card-subtype-mismatch = A carta selecionada não corresponde à carta solicitada.
ageofheroes-trade-offer-label = { $player }: { $offered } por { $wanted }

# Building costs (for display)
ageofheroes-cost-army = 2 Grãos, Ferro
ageofheroes-cost-fortress = Ferro, Madeira, Pedra
ageofheroes-cost-general = Ferro, Ouro
ageofheroes-cost-road = 2 Pedras
ageofheroes-cost-city = 2 Madeiras, Pedra
