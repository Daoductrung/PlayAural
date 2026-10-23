game-name-lastoutpost = Último Posto Avançado
lo-root-vitals = Saúde { $hp }/{ $maximum }; PA { $ap }; { $item }.
lo-root-spectator = Assistindo ao Último Posto Avançado.
lo-menu-attack = Ataque
lo-menu-move = Mover
lo-menu-equipment = Armas e recarga
lo-menu-support = Ajuda e carga
lo-menu-interact = Objetivos e arredores
lo-menu-supplies = Suprimentos e melhorias
lo-menu-back = Voltar ao menu principal
lo-menu-available = { $menu }; Disponível
lo-menu-equipment-state = { lo-menu-equipment }: { $weapon }; no carregador { $loaded }, reserva { $reserve }.
lo-shop-balance = Créditos: { $credits }.
lo-shop-done = Fechar loja
lo-help-shop-done = Fecha a loja sem encerrar seu turno. E ou X também fecham.
lo-key-finish-or-end = Pronto, fechar loja ou encerrar turno
lo-menu-close-information = Feche o painel de informações primeiro.
lo-help-menu-attack = Escolha um alvo para arma de fogo, faca ou granada.
lo-help-menu-move = Abre rotas abertas, custos de movimento e ocupantes do destino.
lo-help-menu-equipment = Recarregue ou troque de arma. Trocar não custa PA.
lo-help-menu-support = { $party_size ->
    [1] Cure-se ou solte a carga.
   *[other] Cure, reanime ou transfira a carga.
    }
lo-help-menu-interact = Restaure a energia e o rádio, abra portões ou repare barricadas.
lo-help-menu-supplies = Compre suprimentos e melhorias. As compras mantêm a loja aberta. X volta.
lo-help-menu-back = Volte ao botão da sua categoria no menu principal.
lo-empty-attack = Nenhum alvo disponível.
lo-empty-move = Nenhuma rota aberta.
lo-empty-equipment = Nenhuma ação de arma disponível.
lo-empty-preparation = Indisponível durante a preparação.
lo-empty-support = Nenhuma ação de ajuda ou carga disponível.
lo-empty-interact = Nenhuma interação disponível.
lo-empty-supplies = Nenhum suprimento disponível aqui.
lo-move-location = { $zone }. { $description }
lo-destination = { $party_size ->
    [1] { $zone }; { $ap } PA. Inimigos: { $inside } dentro, { $outside } fora. { $barricade }
   *[other] { $zone }; { $ap } PA. Zumbis: { $inside } dentro, { $outside } fora. Esquadrão: { $survivors }. { $barricade }
    }
lo-destination-survivor = { $name } ({ $condition })
lo-destination-barricade = Entrada inimiga; resistência da barricada { $strength }.
lo-enemies = Inspetor de inimigos
lo-help-enemies = Alvos ao alcance vêm primeiro, depois inimigos mais distantes e reforços. Você ainda precisa do seu turno, de PA e de munição para atacar.
lo-enemies-context = Alvos de { $zone }.
lo-enemies-spectator-context = Visão geral de { $zone }.
lo-enemies-empty = Nenhum inimigo no mapa.
lo-enemy-detail = { $pack }. Saúde por inimigo: { $health }. { $distance } { $access }
lo-enemy-distance = Distância pela rota: { $count ->
    [one] { $count } conexão.
   *[other] { $count } conexões.
    }
lo-enemy-unreachable = Nenhuma rota aberta.
lo-enemy-barricade = Atrás de uma barricada de resistência { $strength }; os ataques são bloqueados.
lo-enemy-reach = Ao alcance: { $actions }.
lo-enemy-reposition = Fora de alcance com o equipamento atual.
lo-enemy-observe = Visão de espectador.
lo-health = Verificar saúde
lo-help-health = Saúde atual e estado de resgate.
lo-health-report = Saúde { $hp }/{ $maximum }. { $condition }.
lo-health-upright = Em pé
lo-health-downed = { $party_size ->
    [1] Caído
   *[other] Caído; resgate em até { $phases } fases da horda
    }
lo-health-awaiting-recovery = Aguardando recuperação da onda
lo-slot-primary = Equipar arma principal
lo-slot-sidearm = Equipar pistola
lo-error-slot-empty = Nenhuma arma principal equipada.
lo-error-preparation = As ações de combate ficam indisponíveis durante a preparação.
lo-option-voices = Diálogos dos personagens: { $enabled }
lo-change-voices = Diálogos dos personagens definidos como { $enabled }.
lo-desc-voices = Diálogos dos personagens em inglês, incluindo linguagem forte. Os relatórios táticos usam o idioma selecionado.
lo-you = Você
lo-team = { $party_size ->
    [1] Sobrevivente
   *[other] Equipe
    }
lo-none = Nenhum
lo-yes = Sim
lo-no = Não
lo-inside = dentro
lo-outside = fora da barricada
lo-message = { $text }
lo-term-none = { lo-none }
lo-term-courtyard = Pátio
lo-term-gatehouse = Guarita
lo-term-workshop = Oficina
lo-term-infirmary = Enfermaria
lo-term-loading = Doca de carga
lo-term-generator = Sala do gerador
lo-term-pump = Salão das bombas
lo-term-roof = Telhado do rádio
lo-term-walker = { $count ->
    [one] Caminhante
   *[other] Caminhantes
    }
lo-term-hound = { $count ->
    [one] Cão
   *[other] Cães
    }
lo-term-brute = { $count ->
    [one] Bruto
   *[other] Brutos
    }
lo-term-pistol = Pistola M1911
lo-term-rifle = Fuzil AK
lo-term-shotgun = Escopeta
lo-term-marksman = Fuzil de precisão
lo-term-knife = Faca
lo-term-medkit = Kit médico
lo-term-grenade = Granada
lo-term-endurance = Vigor
lo-term-medic = Médico de Campo
lo-term-quickhands = Mãos Rápidas
lo-term-combat = Fase dos sobreviventes
lo-term-resolving = Ação em andamento
lo-term-reloading = Recarregando
lo-term-prep = Preparação
lo-term-finished = Concluído
lo-term-dempsey = Dempsey
lo-term-nikolai = Nikolai
lo-term-takeo = Takeo
lo-term-richtofen = Richtofen
lo-term-victory = { $party_size ->
    [1] Sobreviveu
   *[other] O esquadrão sobreviveu
    }
lo-term-objectives = Rádio ou energia inacabados
lo-term-overwhelmed = { $party_size ->
    [1] Dominado
   *[other] A equipe foi dominada
    }
lo-term-overrun = Limite de tempo da onda atingido
lo-turn-resolving = { lo-error-resolving }
lo-turn-prep = { $survivor_count ->
    [1] Preparação. Pronto inicia a próxima onda.
   *[other] Preparação. A próxima onda começa quando todos estiverem prontos.
    }
lo-map = Mapa e grupos de inimigos
lo-forecast = Previsão da próxima horda
lo-inventory = Equipamento e suprimentos
lo-help-map = Rotas, barricadas, grupos de inimigos e agenda de chegadas. O áudio aponta para o norte.
lo-help-forecast = Próxima fase da horda se ninguém agir mais.
lo-help-inventory = Seus créditos, armas e suprimentos, além das peças para reparos e objetivos.
lo-header = Onda { $wave }; ciclo { $cycle }/{ $limit }. { $phase }. { $zone }. Saúde { $hp }; PA { $ap }; créditos { $credits }; peças { $parts }.
lo-spectator-header = Assistindo. Onda { $wave }; ciclo { $cycle }. { $phase }; peças { $parts }.
lo-objectives = Objetivos
lo-survivor = { $name } ({ $character }): { $zone }; saúde { $hp }/{ $maximum }; PA { $ap }. { $condition }; pronto { $ready }; protegido { $guard }.
lo-zone = { $zone }: { $description } Rotas abertas: { $links }. Inimigos: { $enemies }. { $barrier } Espaços de contato corpo a corpo: { $frontage }.
lo-pack = { $count } { $kind }, { $zone }, { $side }; saúde combinada { $hp }
lo-incoming = { $zone }: { $count } reforços após a fase da horda { $cycle }; primeira ação na fase { $first }.
lo-forecast-caveat = Pressupõe que não haja mais ações. Brutos ocupam dois espaços de contato; os outros inimigos, um. Inimigos amontoados ainda disputam objetivos. Ler não consome tempo.
lo-weapon-status = { $name }, { $weapon }: no carregador { $ammo }, reserva { $reserve }; dano { $damage } por alvo, até { $targets } alvos; alcance de { $minimum } a { $maximum }; equipada: { $equipped }.
lo-kit-status = { $name }: créditos { $credits }; kits médicos { $medkits }, granadas { $grenades }; vantagens { $perks }.
lo-action-label = { $action }: { $detail } ({ $ap } PA)
lo-action-label-simple = { $action } ({ $ap } PA)
lo-reload-detail = { $weapon }; carregador { $loaded }/{ $capacity }, reserva { $reserve }
lo-attack-detail = { $weapon }, no carregador { $ammo }; { $target }
lo-price = { $item }, { $cost } créditos
lo-ammo-price = { $item }, { $amount } balas de reserva por { $cost } créditos
lo-parts-price = { $item }, { $cost } peças
lo-work-price = { $item }, { $done } de { $total } de trabalho, { $cost } peças a pagar
lo-verb-fire = Disparar
lo-verb-knife = Atacar com faca
lo-verb-reload = Recarregar
lo-verb-grenade = Lançar granada
lo-verb-heal = Usar kit médico
lo-verb-revive = Reanimar
lo-verb-open = Abrir portão
lo-verb-repair = Reparar barricada
lo-verb-work = Reparar equipamento
lo-verb-ammo = Comprar munição
lo-verb-buy = Comprar equipamento
lo-verb-perk = Comprar vantagem
lo-verb-upgrade = Melhorar arma principal
lo-verb-equip = Equipar
lo-verb-ready = Pronto para a próxima onda
lo-verb-end = Encerrar turno
lo-help-fire = Atinge primeiro o inimigo mais ferido do grupo. Escopetas atingem até dois. Barricadas protegem inimigos do lado de fora até serem destruídas.
lo-help-knife = 1 de dano; 1 PA; mesma zona. Sem munição.
lo-help-move = 1 PA por conexão; 2 ao sair de uma zona com inimigos. Carregar carga adiciona 1 PA.
lo-help-reload = 1 PA; ao terminar, transfere a munição de reserva. Você pode continuar andando. Mãos Rápidas dispensa o custo de PA da primeira recarga de cada onda.
lo-help-grenade = { $party_size ->
    [1] 3 de dano a até quatro inimigos; 1 PA. Sua zona ou uma zona adjacente visível. Só atinge inimigos dentro do perímetro.
   *[other] 3 de dano a até quatro inimigos; 1 PA. Sua zona ou uma zona adjacente visível. Só atinge inimigos dentro do perímetro; sem fogo amigo.
    }
lo-help-heal = 1 kit e 1 PA; restaura até 3 de saúde a um sobrevivente em pé na sua zona.
lo-help-revive = Reanima com 2 de saúde; 2 PA, ou 1 com Médico de Campo. Mesma zona. Sem turno extra.
lo-help-revive-preview = { lo-help-revive } Sem outras ações, { $target } teria { $health } de saúde após a próxima fase da horda.
lo-gate-link = { $origin } para { $destination }
lo-gate-service = Portão de serviço
lo-gate-shortcut = Atalho da enfermaria
lo-gate-roof = Portão de acesso ao rádio
lo-gate-crossing = Travessia de cargas
lo-gate-bulkhead = Comporta estanque
lo-gate-status = { $gate }: aberto { $opened }; { $cost } peças; requer energia { $power }. Rotas: { $routes }. Espaços de contato após abrir: { $frontages }.
lo-help-open-routes = { $cost } peças; 1 PA; sua zona deve estar livre. Abre { $routes } permanentemente para os dois lados. Requer energia: { $power }. Espaços de contato depois: { $frontages }.
lo-frontage-site = { $zone }, { $count } espaços de contato
lo-gate-opened-routes = Novas rotas para os dois lados: { $routes }.
lo-defense-until-clear = Continue defendendo { $zone } até a onda terminar; os inimigos ainda podem danificar o retransmissor.
lo-help-repair = 1 peça e 1 PA; restaura 2 de resistência da barricada, até 4. Uma vez por ciclo; zona livre.
lo-help-work = 1 PA por unidade de trabalho. A primeira unidade paga o custo de peças indicado. Requer zona livre; o rádio precisa de energia.
lo-help-ammo = Capacidade de reserva: três carregadores. Em combate, compre em uma estação de munição com a zona livre. Na preparação, compre em qualquer lugar.
lo-help-buy = Apenas na preparação. Armas principais substituem a atual. A primeira compra inclui munição; comprar de novo mantém a munição antiga. Sem reembolso.
lo-help-perk = Requer energia; no máximo duas vantagens. Vigor: +2 de saúde. Médico de Campo: reanima por 1 PA. Mãos Rápidas: a primeira recarga de cada onda não custa PA.
lo-help-upgrade = Requer energia; 500 créditos por tipo de arma. Dano: AK 4, escopeta 6, fuzil de precisão 9.
lo-help-equip = Troca de arma; sem custo de PA.
lo-help-ready = { $survivor_count ->
    [1] Inicia a próxima onda.
   *[other] Alterna sua prontidão. Quando todos estiverem prontos, a próxima onda começa. Cancele a prontidão para comprar de novo.
    }
lo-help-end = { $party_size ->
    [1] Descarta o PA restante. Os inimigos agem em seguida.
   *[other] Descarta o PA restante. Os inimigos agem quando o esquadrão terminar.
    }
lo-error-unavailable = Indisponível nesta fase.
lo-error-stale = Essa escolha não está mais disponível.
lo-error-turn = { action-not-your-turn }
lo-error-down = Você está caído.
lo-error-ready = Cancele a prontidão antes de comprar.
lo-error-ap = PA insuficiente.
lo-error-range = Alvo fora do alcance de tiro ou da linha de visão.
lo-error-ammo = Munição carregada insuficiente.
lo-error-grenade = Sem granadas.
lo-error-medkit = Sem kits médicos.
lo-error-engaged = Limpe primeiro os inimigos desta zona.
lo-error-complete = Este objetivo já está concluído.
lo-error-power = Restaure a energia primeiro.
lo-error-parts = Peças insuficientes.
lo-error-credits = Créditos insuficientes.
lo-error-equipped = Esta arma já está equipada.
lo-error-resolving = A ação atual está em andamento.
lo-event-wave = Onda { $amount }; { $count } inimigos. { $deployment }.
lo-deployment-now = { $count } fora agora
lo-deployment-later = { $count } chegam após a fase da horda { $cycle }
lo-event-final_warning = Onda final. { $amount } de trabalho de infraestrutura restante; { $count } peças a pagar. Termine a infraestrutura e a missão antes que a onda acabe.
lo-event-clear = { $party_size ->
    [1] Onda { $amount } concluída. +{ $count } créditos; +3 peças. Recupere { $healing } de saúde, ou volte com { $recovery } de saúde se estiver caído. Até { $ammo } balas de reserva da pistola. Preparação.
   *[other] Onda { $amount } concluída. Cada sobrevivente ganha { $count } créditos e até { $ammo } balas de reserva da pistola. Sobreviventes em pé recuperam { $healing } de saúde; sobreviventes caídos voltam com { $recovery } de saúde. Equipe: +3 peças. Preparação.
    }
lo-event-fire = { $actor } disparou { $item } em { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife = { $actor } atacou com faca em { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade = { $actor } detonou uma granada em { $zone }. { $hits }. { lo-combat-kills }
lo-event-move = { $actor } se moveu de { $origin } para { $zone }.
lo-event-reload = { $actor } carregou { $amount } balas em { $item }.
lo-reload-start = { $actor } está recarregando.
lo-reload-start-personal = Recarregando.
lo-error-reloading = { lo-reload-start-personal }
lo-event-heal = { $actor } tratou { $target }; saúde atual { $amount }.
lo-event-revive = { $actor } reanimou { $target } com { $amount } de saúde.
lo-event-open = { $actor } abriu { $item }; { $amount } peças restantes. { $routes }
lo-event-repair = { $actor } reparou a barricada em { $zone } até { $amount } de resistência.
lo-event-work = { $count ->
    [1] { $actor } restaurou { $item } em { $zone }.
   *[0] { $actor } trabalhou em { $item } em { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo = { $actor } comprou { $amount } balas para { $item }, pagou { $count } créditos.
lo-event-buy = { $actor } comprou { $item }; restam { $amount } créditos.
lo-event-perk = { $actor } adquiriu { $item }.
lo-event-upgrade = { $actor } melhorou { $item }.
lo-event-equip = { $actor } equipou { $item }.
lo-event-ready = { $actor } está { $amount ->
    [1] pronto para a próxima onda.
   *[0] não está pronto.
    }
lo-event-end = { $actor } encerrou o turno.
lo-event-barrier = { $zone }: { $count } golpes na barricada de { $item }; resistência atual { $amount }.
lo-event-enter = { $count } { $item } entraram em { $zone }.
lo-event-approach = { $count } { $item } se moveram de { $origin } para { $zone }.
lo-event-hurt = { $target }: { $count } ataques de { $item }, { $amount } de dano total em { $zone }.
lo-event-down = { $target } está caído em { $zone }. Reanime dentro das próximas duas fases da horda.
lo-event-incapacitated = { $target } está incapacitado até a próxima onda.
lo-event-recovery = { $target }: última recuperação de emergência. Saúde { $amount }; próximo turno { $count } PA. A carga fica onde caiu.
lo-event-arrivals = { $count } reforços do lado de fora. Eles agem na próxima fase da horda.
lo-event-finish = { $item }. Ondas concluídas: { $amount } de { $waves }.
lo-result-cycles = Fases da horda: { $count }.
lo-error-magazine-full = O carregador equipado já está cheio.
lo-error-reserve-empty = Sem munição de reserva.
lo-error-barrier-full = Esta barricada está com resistência máxima.
lo-error-already-repaired = Esta barricada já foi reparada neste ciclo.
lo-error-weapon-owned = Você já carrega esta arma principal.
lo-error-kit-capacity = Capacidade de kits médicos atingida.
lo-error-grenade-capacity = Capacidade de granadas atingida.
lo-error-ammo-capacity = Capacidade de munição de reserva atingida.
lo-error-perk-owned = Você já tem esta vantagem.
lo-error-perk-capacity = Limite de vantagens atingido.
lo-error-no-primary = Compre uma arma principal primeiro.
lo-error-upgraded = Esta arma já foi melhorada.
lo-event-heal-self = { $actor } usou um kit médico; saúde atual { $amount }.
lo-event-heal-self-personal = Você se tratou; saúde atual { $amount }.
lo-event-heal-target = { $actor } tratou você; saúde atual { $amount }.
lo-event-revive-target = { $actor } reanimou você com { $amount } de saúde. Você age no próximo ciclo.
lo-event-hurt-personal = Você recebeu { $count } ataques de { $item }, { $amount } de dano total em { $zone }.
lo-event-down-personal = Você está caído em { $zone }. Sua equipe tem as próximas duas fases da horda para reanimar você.
lo-event-down-solo-recovery = { $target } caiu em { $zone }. Recuperação de emergência: { $recovery_seconds } segundos após esta fase da horda.
lo-event-down-solo-recovery-personal = Você caiu em { $zone }. Recuperação de emergência: { $recovery_seconds } segundos após esta fase da horda.
lo-event-down-solo-final = { $target } caiu em { $zone }. Não restam sobreviventes nem recuperações.
lo-event-down-solo-final-personal = Você caiu em { $zone }. Não restam sobreviventes nem recuperações.
lo-event-incapacitated-personal = Você está fora até a próxima onda.
lo-event-recovery-personal = Você usou sua última recuperação de emergência. Saúde { $amount }; próximo turno { $count } PA. A carga fica onde você caiu.
lo-event-fire-personal = Você disparou { $item } em { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife-personal = Você atacou com faca em { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade-personal = Você lançou uma granada em { $zone }. { $hits }. { lo-combat-kills }
lo-event-move-personal = Você se moveu de { $origin } para { $zone }.
lo-event-reload-personal = Você carregou { $amount } balas em { $item }.
lo-event-heal-personal = Você tratou { $target }; saúde atual { $amount }.
lo-event-revive-personal = Você reanimou { $target } com { $amount } de saúde.
lo-event-open-personal = Você abriu { $item }; { $amount } peças restantes. { $routes }
lo-event-repair-personal = Você reparou a barricada de { $zone } até { $amount } de resistência.
lo-event-work-personal = { $count ->
    [1] Você restaurou { $item } em { $zone }.
   *[0] Você trabalhou em { $item } em { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo-personal = Você comprou { $amount } balas para { $item }, pagou { $count } créditos.
lo-event-buy-personal = Você comprou { $item }; restam { $amount } créditos.
lo-event-perk-personal = Você adquiriu { $item }.
lo-event-upgrade-personal = Você melhorou { $item }.
lo-event-equip-personal = Você equipou { $item }.
lo-event-ready-personal = Você está { $amount ->
    [1] pronto para a próxima onda.
   *[0] não está pronto.
    }
lo-event-end-personal = Você encerrou seu turno.
lo-term-horde = inimigos
lo-help-move-destination = { $description } { lo-help-move }
lo-zone-description-courtyard = Concreto rachado cerca um mastro de bandeira vazio sob o céu aberto. A Oficina fica a oeste e a Enfermaria a leste; ao sul, a Guarita encara a escuridão além do perímetro.
lo-zone-description-gatehouse = Ao sul do Pátio, o telhado da guarita desabou, deixando as tábuas do piso lascadas expostas à noite. A cadeira vazia do guarda encara a entrada externa, onde a cerca do perímetro encontra a estrada.
lo-zone-description-workshop = Manchas de óleo se espalham sob bancadas abandonadas, e ferrugem risca as paredes de chapa metálica. O armário de munição fica contra a parede dos fundos; um portão de serviço leva em direção ao gerador.
lo-zone-description-infirmary = Macas estreitas alinham uma sala de madeira a leste do Pátio. Ataduras empoeiradas pendem de um carrinho tombado, e uma luz pálida bate no vidro da janela. Uma passagem lateral leva ao Salão das Bombas.
lo-zone-description-loading = Piso de aço enferrujado passa por pilhas de paletes vazios sob o céu aberto. A Oficina fica ao sul; a leste, uma passagem entra na umidade do Salão das Bombas.
lo-zone-description-generator = Um gerador atarracado ocupa uma câmara de concreto além do portão de serviço da Oficina. Cabos grossos cruzam o piso metálico até um quadro de distribuição marcado. É aqui que a energia do posto avançado deve ser restaurada.
lo-zone-description-pump = Água rasa cobre o piso sob canos grossos e válvulas corroídas. Uma marca de maré mancha as paredes de concreto. A passagem da Enfermaria encontra aqui a rota da Doca de Carga.
lo-zone-description-roof = Uma antena se inclina sobre um telhado de concreto nu, com seus cabos de sustentação esticados contra o céu. O rádio fica em um armário à prova d'água amassado. Portões de acesso energizados protegem as aproximações vindas de baixo.
lo-option-map = Mapa: { $value }
lo-prompt-map = Escolha um mapa
lo-change-map = Mapa definido como { $value }.
lo-desc-map = Posto Avançado Abandonado: uma guarnição castigada em torno de um pátio aberto. Pátio Ferroviário: trilhos desertos sob um viaduto estreito. Usina Inundada: salões de máquinas alagados divididos por portões pesados.
lo-option-mode = Modo: { $value }
lo-prompt-mode = Escolha um modo
lo-change-mode = Modo definido como { $value }.
lo-desc-mode = Operações: missões e infraestrutura. Cerco: defenda a integridade do retransmissor. Salvamento: recupere carga. Extração Clássica: oito ondas, energia, rádio e uma corrida final por suprimentos.
lo-extraction-route = Onda { $wave }: leve suprimentos de { $pickup } até { $destination } dentro de { $deadline } fases da horda. Limpe as zonas de coleta e entrega. Carga: +1 PA por movimento, apenas pistola.
lo-option-difficulty = Dificuldade: { $value }
lo-prompt-difficulty = Escolha a dificuldade
lo-change-difficulty = Dificuldade definida como { $value }.
lo-desc-difficulty = Recruta: mais recuperação e suprimentos. Padrão: hordas mais fortes e condições variáveis. Veterano: pressão máxima, renda escassa, sem cura gratuita entre ondas nem munição gratuita para a pistola.
lo-error-scenario = Conjunto de mapa, modo ou dificuldade não compatível. Verifique as opções do saguão.
lo-event-start = { $map }. { $mode }, { $difficulty }. { $waves } ondas. Início em { $spawn }.
lo-scenario-status = { $map }; { $mode }; { $difficulty }. { $condition }.
lo-mission-status-retrieve = Recupere a carga em { $cargo }; portador { $carrier }; entregue em { $destination }. { $remaining } fases da horda restantes.
lo-mission-status-relay = Terminais do retransmissor: { $zone } e { $destination }. { $remaining } fases da horda restantes.
lo-mission-status-hold = Defenda { $zone }: { $progress } de { $total } fases de defesa. { $remaining } fases da horda restantes.
lo-mission-help-retrieve = 1 PA para pegar, entregar, passar ou soltar a carga. Zona livre necessária, exceto ao soltar. Carga: +1 PA por movimento, apenas pistola. Cair derruba a carga; o prazo continua correndo.
lo-mission-help-relay = { $survivor_count ->
    [1] 1 PA por terminal em uma zona livre. Ative os dois locais; as ativações persistem entre ciclos. Os dois locais devem ficar livres após a horda.
   *[other] 1 PA por terminal em uma zona livre. Dois sobreviventes ativam locais separados no mesmo ciclo e depois permanecem em pé ali durante a horda. Os dois locais devem terminar livres.
    }
lo-mission-help-hold = Mantenha um sobrevivente em pé no local, sem inimigos dentro, ao final de duas fases da horda. Um local vazio ou disputado perde um progresso. No Cerco, proteja o retransmissor até a onda terminar; perder o prazo custa integridade.
lo-terminal-status = { $zone }: ativado por { $actor }.
lo-verb-mission = Interação de missão
lo-verb-handoff = Passar a carga
lo-verb-drop = Largar a carga
lo-verb-guard = Proteger-se
lo-help-mission = 1 PA; executa a tarefa marcada em uma zona livre.
lo-help-handoff = 1 PA; transfere a carga para um companheiro em pé na mesma zona livre.
lo-help-drop = 1 PA; solta a carga aqui. Restaura o movimento normal e o disparo da arma principal.
lo-help-guard = 1 PA; intercepta o próximo ataque local e reduz o dano em um. Expira no próximo ciclo; não acumula nem atrai inimigos distantes.
lo-error-guarded = Você já está protegido.
lo-error-carrying = A carga impede o disparo da arma principal. Use a pistola ou largue a carga.
lo-error-terminal = Este terminal já está ativo.
lo-error-relay-partner = Um sobrevivente diferente precisa ativar o outro terminal.
lo-task-activate = Ative este terminal de retransmissão; local parceiro: { $zone }
lo-task-pickup = Colete a carga para { $zone }
lo-task-deliver = Entregue a carga em { $zone }
lo-event-mission_complete = { $party_size ->
    [1] { $item } concluída: { $sites }. +{ $count } créditos; +1 peça. { $defense }
   *[other] { $item } concluída: { $sites }. Cada sobrevivente +{ $count } créditos; equipe +1 peça. { $defense }
    }
lo-event-mission_failed = { $item } falhou. Missões falhas: { $amount }.
lo-event-mission_clock = { $item }: { $amount } fases da horda restantes.
lo-event-mission_pressure = O ruído da missão atraiu { $count } caminhantes para fora de { $zone }. Ativos na próxima fase da horda.
lo-event-hold_progress = Defesa em { $zone }: { $amount } de { $count } fases garantidas.
lo-event-core_damage = O retransmissor em { $zone } perde { $amount } de integridade; restam { $count }.
lo-event-relay_reset = Retransmissores: { $item }.
lo-event-cargo_lost = Carga solta em { $zone }.
lo-event-condition = { $item }. Primeiros reforços após a fase da horda { $amount }.
lo-term-outpost = Posto Avançado Abandonado
lo-term-switchyard = Pátio Ferroviário
lo-term-floodworks = Usina Inundada
lo-term-operations = Operações
lo-term-siege = Cerco
lo-term-salvage = Salvamento
lo-term-classic = Extração Clássica
lo-term-recruit = Recruta
lo-term-standard = Padrão
lo-term-veteran = Veterano
lo-term-retrieve = Recuperação de carga
lo-term-relay = Retransmissão coordenada
lo-term-hold = Defesa do setor
lo-term-mission_quota = Requisito de missões não cumprido
lo-term-core_lost = Retransmissor destruído
lo-term-latched = os terminais ativados continuam prontos
lo-term-reset = ative os dois terminais novamente no mesmo ciclo
lo-term-condition-normal = Condições normais
lo-term-condition-rush = Reforços antecipados
lo-term-condition-fog = Neblina: armas de fogo limitadas a uma conexão
lo-term-condition-battering = Horda arrombadora: um dano extra à barricada
lo-term-condition-shortage = Escassez de suprimentos: carregadores de reserva custam 90 créditos
lo-term-depot = Terminal de Passageiros
lo-term-west_tracks = Trilhos Oeste
lo-term-east_tracks = Trilhos Leste
lo-term-signal_box = Cabine de Sinalização
lo-term-freight = Pátio de Cargas
lo-term-maintenance = Galpão de Manutenção
lo-term-switchgear = Sala dos Interruptores
lo-term-overpass = Viaduto
lo-term-tower = Torre de Rádio
lo-term-tunnel = Túnel Ferroviário
lo-term-quay = Cais de Desembarque
lo-term-foyer = Vestíbulo de Captação
lo-term-canal = Canal de Drenagem
lo-term-filter = Leitos de Filtragem
lo-term-control = Sala de Controle
lo-term-laboratory = Laboratório
lo-term-archive = Arquivo de Suprimentos
lo-term-turbine = Salão das Turbinas
lo-term-skybridge = Passarela de Rádio
lo-term-clinic = Clínica
lo-event-guard = { $actor } se protegeu: o próximo golpe recebido causa um dano a menos.
lo-event-guard-personal = Você se protegeu: o próximo golpe recebido causa um dano a menos.
lo-event-cargo_pickup = { $actor } coleta a carga em { $zone } para { $origin }.
lo-event-cargo_pickup-personal = Você coleta a carga em { $zone } para { $origin }.
lo-event-cargo_deliver = { $actor } entrega a carga em { $zone }.
lo-event-cargo_deliver-personal = Você entrega a carga em { $zone }.
lo-event-cargo_drop = { $actor } larga a carga em { $zone }.
lo-event-cargo_drop-personal = Você larga a carga em { $zone }.
lo-event-cargo_handoff = { $actor } passa a carga para { $target } em { $zone }.
lo-event-cargo_handoff-personal = Você passa a carga para { $target } em { $zone }.
lo-event-relay_armed = { $actor } ativa o terminal em { $zone }; { $amount } terminais armados.
lo-event-relay_armed-personal = Você ativa o terminal em { $zone }; { $amount } terminais armados.
lo-event-cargo_handoff-target = { $actor } passa a carga para você em { $zone }.
lo-zone-description-depot = Fileiras de bancos vazios encaram um painel de partidas congelado em trens cancelados. A poeira embota o piso de concreto. Portas nas duas extremidades do salão dão para os trilhos oeste e leste.
lo-zone-description-west_tracks = Uma passarela de aço acompanha trilhos enferrujados sob lâmpadas de sinal apagadas. Postes de cerca marcam a borda do pátio; além do terminal, a Cabine de Sinalização se ergue no lado norte.
lo-zone-description-east_tracks = Vagões vazios ficam ao lado de uma faixa de piso de aço empenado. Os trilhos se estendem para a escuridão além do perímetro; o Pátio de Cargas se abre ao norte.
lo-zone-description-signal_box = Alavancas se amontoam em uma cabine de madeira sobre um diagrama de trilhos desbotado. As janelas dão para os trilhos oeste. Passagens levam ao Galpão de Manutenção e às escadas para o Viaduto.
lo-zone-description-freight = Contêineres de carga dominam um pátio de chapas de aço amassadas. Correntes soltas pendem de uma estrutura de carregamento. O portão de travessia protege a aproximação ao Viaduto; outra rota entra no Túnel Ferroviário.
lo-zone-description-maintenance = Rodas desmontadas e ferramentas engorduradas alinham um galpão de metal ondulado. Um armário de munição fica no piso de concreto manchado, ao lado do portão de serviço para a Sala dos Interruptores.
lo-zone-description-switchgear = Fileiras de interruptores pesados preenchem uma sala de concreto além do portão de serviço. Cabos grossos desaparecem sob placas metálicas do piso, e etiquetas de advertência se descolam dos armários. Restaure a energia do pátio aqui.
lo-zone-description-overpass = Grade de aço aberta atravessa os trilhos, com apenas um corrimão estreito contra a queda. A Cabine de Sinalização e o Pátio de Cargas ficam abaixo; a Torre de Rádio se ergue à frente, ao norte.
lo-zone-description-tower = Uma mesa de rádio e uma cadeira de madeira gasta ocupam a cabine acima dos trilhos. As janelas dão para o pátio em todos os lados. É preciso energia para abrir os portões de acesso abaixo.
lo-zone-description-tunnel = Os trilhos desaparecem em um túnel de concreto manchado de fuligem e infiltração. O Pátio de Cargas fica atrás de você; uma passagem lateral sobe em direção ao portão de acesso da Torre de Rádio.
lo-zone-description-quay = Tábuas de desembarque empenadas se projetam sobre a água negra, com as cordas de amarração soltas. O perímetro sul termina aqui. À frente, a entrada de concreto da usina se abre para o Vestíbulo de Captação.
lo-zone-description-foyer = Manchas de água sobem pelas paredes de concreto sob um plano de evacuação desbotado. Esta entrada apertada se divide para o Canal de Drenagem, a oeste, e o Arquivo de Suprimentos, a leste.
lo-zone-description-canal = Água rasa corre entre margens altas de concreto, trazendo restos de vegetação de além do perímetro. O canal curva ao norte em direção aos Leitos de Filtragem; o vestíbulo fica a leste.
lo-zone-description-filter = A água da enchente lambe fileiras de leitos de filtragem entupidos sob paredes de metal enferrujado. O portão de serviço leva em direção às turbinas; uma comporta pesada separa este salão da Sala de Controle.
lo-zone-description-control = Uma longa fileira de medidores e telas rachadas domina um piso metálico. O Laboratório se abre a leste, a comporta dos filtros a oeste; a aproximação norte sobe para a Passarela de Rádio.
lo-zone-description-laboratory = Potes de amostras turvos lotam as bancadas, e vidro quebrado brilha no concreto. Portas conectam o Arquivo de Suprimentos, a Sala de Controle e a Clínica; todas as rotas atravessam a sala de trabalho abandonada.
lo-zone-description-archive = Livros-caixa inchados de água murcham em prateleiras de madeira ao lado de caixas de suprimentos lacradas. O armário de munição ocupa o canto mais seco. O vestíbulo fica a oeste, o Laboratório ao norte.
lo-zone-description-turbine = Grandes carcaças de turbinas preenchem um salão metálico cavernoso além do portão de serviço. Placas de manutenção formam o piso entre elas. Os controles de energia ficam sob a rota que sobe para a Passarela de Rádio.
lo-zone-description-skybridge = Uma estreita ponte de aço pende sobre os salões norte da usina, exposta ao vento. Um armário de rádio fica sob uma antena; as aproximações convergem aqui vindas do Controle, da Clínica e das turbinas.
lo-zone-description-clinic = Cortinas de privacidade desbotadas dividem uma sala de concreto forrada de macas de exame. A umidade se infiltrou sob os armários de remédios. O Laboratório fica ao sul; outra aproximação sobe para a Passarela de Rádio.
lo-event-mission_start-retrieve = Carga: { $zone } para { $origin }. Prazo: { $amount } fases da horda.
lo-event-mission_start-relay = Retransmissores: { $zone } e { $origin }. Prazo: { $amount } fases da horda.
lo-event-mission_start-hold = Defenda { $zone }. Prazo: { $amount } fases da horda.
lo-error-visibility = A neblina bloqueia disparos além de uma conexão.
lo-help-weapon = Dano { $damage }; melhorada { $upgraded }; alvos { $targets }; alcance { $minimum }–{ $maximum }; carregador { $magazine }; { $rounds } balas por disparo; { $price } créditos. Substitui a arma principal; sem reembolso.
lo-error-barricade = A barricada bloqueia este ataque.
lo-combat-hit = { $enemy }: { $damage } de dano
lo-combat-outside = { $zone }, { lo-outside }
lo-objective-generator = Energia
lo-objective-radio = Rádio
lo-combat-kills = { $count ->
    [0] { "" }
    [one] 1 abate.
   *[other] { $count } abates.
    }
lo-shop-ready = Terminar as compras e ficar Pronto
lo-help-shop-ready = E fecha a loja e marca você como pronto. X volta sem marcar.
lo-already-ready = { $party_size ->
    [1] Pronto.
   *[other] Você está pronto. Aguardando o esquadrão.
    }
lo-help-teammates = { $party_size ->
    [1] Sua posição, saúde e personagem.
   *[other] Posições, saúde, prazos de resgate e personagens do esquadrão.
    }
lo-help-objectives = Requisitos de vitória, progresso da infraestrutura e missão ativa.
lo-teammates = { $party_size ->
    [1] Personagem
   *[other] Companheiros
    }
lo-required = Obrigatório
lo-optional = Opcional
lo-complete = Concluído
lo-incomplete = Incompleto
lo-objective-waves = Obrigatório: conclua todas as ondas. { $completed }/{ $total } concluídas.
lo-objective-missions = Obrigatório: conclua { $total } missões. { $completed } concluídas; { $failed } falhas.
lo-objective-bonus-missions = Missões: { $completed } concluídas; { $failed } falhas.
lo-objective-integrity = Obrigatório: mantenha o retransmissor intacto. Integridade { $current }/{ $total }.
lo-objective-project = { $project }, { $zone }: { $requirement }. { $state }; trabalho { $progress }/{ $total }. Restante: { $remaining } de trabalho, { $cost } peças, além de quaisquer portões de acesso não abertos.
lo-mission-idle = Nenhuma missão ativa.
lo-verb-unready = Cancelar prontidão

lo-health-recovering = Caído; recuperação de emergência { $recovery_seconds } segundos após a horda
lo-inventory-parts = { $party_size ->
    [1] Peças: { $parts }.
   *[other] Peças compartilhadas: { $parts }.
    }
lo-board-lineup = { $count ->
    [1] Um sobrevivente
   *[other] Sobreviventes { $count }: humanos { $humans }, bots { $bots }
    }
lo-board-original = Sem tomada de controle por bots
lo-board-takeover = Com tomada de controle por bots
leaderboard-lo-clear-entry = { $rank }. { $player }: { $value } fases da horda.
lo-personal-record = { $name }: { $value } fases da horda.
lo-record-unranked = Sem classificação: a escalação inicial mudou.
