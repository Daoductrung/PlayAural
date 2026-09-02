# Rolling Balls

game-name-rollingballs = Bolas Rolantes

# Actions
rb-take = Pegar { $count } { $count ->
    [one] bola
   *[other] bolas
}
rb-reshuffle-action = Reembaralhar o início do tubo ({ $remaining } usos restantes)
rb-view-pipe-action = Visualizar o tubo ({ $remaining } usos restantes)
rb-check-pipe-status = Verificar estado do tubo
rb-key-reshuffle-pipe = Reembaralhar o início do tubo
rb-key-view-pipe = Visualizar o tubo

# Taking and revealing balls
rb-you-take = Você se compromete a pegar { $count } { $count ->
    [one] bola
   *[other] bolas
} do início do tubo de { $remaining } bolas.
rb-player-takes = { $player } se compromete a pegar { $count } { $count ->
    [one] bola
   *[other] bolas
} do início do tubo de { $remaining } bolas.
rb-you-take-brief = Você pega { $count } { $count ->
    [one] bola
   *[other] bolas
}.
rb-player-takes-brief = { $player } pega { $count } { $count ->
    [one] bola
   *[other] bolas
}.
rb-you-forced-take = Apenas { $count } { $count ->
    [one] bola permanece
   *[other] bolas permanecem
}, menos do que a retirada mínima de { $minimum }, então você deve pegar o resto.
rb-player-forced-takes = Apenas { $count } { $count ->
    [one] bola permanece
   *[other] bolas permanecem
}, menos do que a retirada mínima de { $minimum }, então { $player } deve pegar o resto.
rb-you-forced-take-brief = Você deve pegar as { $count } { $count ->
    [one] bola finais
   *[other] bolas finais
}.
rb-player-forced-takes-brief = { $player } deve pegar as { $count } { $count ->
    [one] bola finais
   *[other] bolas finais
}.

rb-your-ball-plus = Sua bola { $num }: { $description }. Mais { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
rb-player-ball-plus = Bola { $num } de { $player }: { $description }. Mais { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
rb-your-ball-minus = Sua bola { $num }: { $description }. Menos { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
rb-player-ball-minus = Bola { $num } de { $player }: { $description }. Menos { $value } { $value ->
    [one] ponto
   *[other] pontos
}.
rb-your-ball-zero = Sua bola { $num }: { $description }. Sem alteração na pontuação.
rb-player-ball-zero = Bola { $num } de { $player }: { $description }. Sem alteração na pontuação.

rb-your-draw-summary = Sua extração de { $count } bolas tem um valor líquido de { $delta } pontos. Sua pontuação agora é { $score }, com { $remaining } bolas restantes no tubo.
rb-player-draw-summary = A extração de { $count } bolas de { $player } tem um valor líquido de { $delta } pontos. A pontuação de { $player } agora é { $score }, com { $remaining } bolas restantes no tubo.
rb-your-draw-summary-brief = Líquido { $delta }; sua pontuação é { $score }. Restam { $remaining } bolas.
rb-player-draw-summary-brief = { $player }: líquido { $delta }, pontuação { $score }. Restam { $remaining } bolas.
rb-your-score-legacy = Sua pontuação agora é { $score }, com { $remaining } bolas restantes no tubo.
rb-player-score-legacy = A pontuação de { $player } agora é { $score }, com { $remaining } bolas restantes no tubo.

# Reshuffling
rb-you-reshuffle = Você reembaralha as primeiras { $count } bolas. { $penalty ->
    [0] Não há penalidade
   *[other] Você paga uma penalidade de { $penalty } pontos
}; sua pontuação agora é { $score }, e você tem { $remaining } reembaralhamentos restantes.
rb-player-reshuffles = { $player } reembaralha as primeiras { $count } bolas. { $penalty ->
    [0] Não há penalidade
   *[other] { $player } paga uma penalidade de { $penalty } pontos
}; pontuação atual: { $score }; reembaralhamentos restantes: { $remaining }.
rb-you-reshuffle-brief = Você reembaralha { $count } bolas; penalidade { $penalty }, pontuação { $score }, restam { $remaining } usos.
rb-player-reshuffles-brief = { $player } reembaralha { $count } bolas; penalidade { $penalty }, pontuação { $score }, restam { $remaining } usos.

# Pipe preview and status
rb-view-pipe-header = Mostrando as próximas { $shown } de { $total } bolas. Você tem { $remaining } novas visualizações restantes.
rb-view-pipe-ball = { $num }: { $description }. Valor: { $value } pontos.
rb-status-pipe = Rodada { $round }. Restam { $count } bolas no tubo.
rb-status-take-range = Cada turno normal exige entre { $min } e { $max } bolas.
rb-status-turn = Turno atual: { $player }.
rb-status-resources = Você tem { $views } novas visualizações de tubo e { $reshuffles } reembaralhamentos restantes.

# Start and round flow
rb-pipe-filled = O tubo foi preenchido com { $count } bolas únicas de: { $packs }.
rb-round-start = A rodada { $round } começa com { $count } bolas restantes no tubo.
rb-round-start-brief = Rodada { $round }; restam { $count } bolas.

# End of game
rb-pipe-empty = O tubo está vazio.
rb-winner = { $player } vence com { $score } pontos.
rb-you-win = Você vence com { $score } pontos.
rb-you-tie = Você compartilha a vitória com { $players }; cada um de vocês terminou com { $score } pontos.
rb-tie = { $players } compartilham a vitória com { $score } pontos.
rb-line-format = { $rank }. { $player }: { $points }

# Options
rb-set-min-take = Mínimo de bolas por turno: { $count }
rb-enter-min-take = Insira o mínimo de bolas por turno, de 1 a 5:
rb-option-changed-min-take = Mínimo de bolas por turno definido para { $count }.
rollingballs-desc-min-take = Número mínimo de bolas que um jogador deve pegar em um turno (padrão 1, intervalo de 1 a 5).
rb-set-max-take = Máximo de bolas por turno: { $count }
rb-enter-max-take = Insira o máximo de bolas por turno, de 1 a 5:
rb-option-changed-max-take = Máximo de bolas por turno definido para { $count }.
rollingballs-desc-max-take = Número máximo de bolas que um jogador pode pegar em um turno. O jogo não pode começar se este valor for menor que o mínimo (padrão 3, intervalo de 1 a 5).
rb-set-view-pipe-limit = Novas visualizações de tubo por jogador: { $count }
rb-enter-view-pipe-limit = Insira as novas visualizações de tubo por jogador, de 0 a 100; 0 desativa as visualizações:
rb-option-changed-view-pipe-limit = Novas visualizações de tubo por jogador definidas para { $count }.
rollingballs-desc-view-pipe-limit = Quantas bolas futuras podem ser visualizadas no tubo. Defina como 0 para desativar visualizações (padrão 5, intervalo de 0 a 100).
rb-set-reshuffle-limit = Reembaralhamentos por jogador: { $count }
rb-enter-reshuffle-limit = Insira os reembaralhamentos por jogador, de 0 a 100; 0 desativa o reembaralhamento:
rb-option-changed-reshuffle-limit = Reembaralhamentos por jogador definidos para { $count }.
rollingballs-desc-reshuffle-limit = Quantos reembaralhamentos estão disponíveis antes que o tubo se esgote (padrão 3, intervalo de 0 a 100).
rb-set-reshuffle-penalty = Penalidade de reembaralhamento: { $points } pontos
rb-enter-reshuffle-penalty = Insira a penalidade de reembaralhamento, de 0 a 5 pontos:
rb-option-changed-reshuffle-penalty = Penalidade de reembaralhamento definida para { $points } pontos.
rollingballs-desc-reshuffle-penalty = Penalidade de pontuação aplicada quando um reembaralhamento é usado. Esta opção aparece apenas quando há reembaralhamentos disponíveis (padrão 1, intervalo de 0 a 5).
rb-set-ball-packs = Conjuntos de bolas ({ $count } de { $total } selecionados)
rb-option-changed-ball-packs = Seleção de conjuntos de bolas alterada.
rollingballs-desc-ball-packs = Escolha quais conjuntos temáticos de bolas estão incluídos no tubo. Pelo menos um pacote deve permanecer selecionado.

# Contextual disabled reasons and setup validation
rb-draw-resolving = Aguarde até que a extração de bolas atual de { $player } termine antes de iniciar outra ação no tubo.
rb-take-not-your-turn = Você não pode pegar { $count } bolas agora porque é o turno de { $player }.
rb-take-outside-range = Você tentou pegar { $count } bolas, mas este jogo permite de { $min } a { $max } por turno normal.
rb-not-enough-balls = Você tentou pegar { $count } bolas, mas apenas { $remaining } permanecem no tubo.
rb-reshuffle-not-your-turn = Você não pode reembaralhar agora porque é o turno de { $player }.
rb-no-reshuffles-left = Você usou todos os seus { $limit } reembaralhamentos para este jogo.
rb-already-reshuffled = Você já reembaralhou durante este turno. Pegue bolas para terminar o turno.
rb-not-enough-balls-to-reshuffle = O reembaralhamento precisa de pelo menos { $required } bolas, mas apenas { $remaining } restam. Pegue bolas em vez disso.
rb-no-views-left = O tubo mudou e você usou todas as suas { $limit } novas visualizações. Você ainda pode reabrir uma visualização inalterada antes que o tubo se mova.
rb-error-min-take-invalid = A retirada mínima é { $count }; deve ser de { $min } a { $max }.
rb-error-max-take-invalid = A retirada máxima é { $count }; deve ser de { $min } a { $max }.
rb-error-take-range-conflict = A retirada mínima é { $min }, acima do máximo de { $max }. Reduza o mínimo ou aumente o máximo antes de começar.
rb-error-view-limit-invalid = O limite de visualização é { $count }; deve ser de { $min } a { $max }.
rb-error-reshuffle-limit-invalid = O limite de reembaralhamento é { $count }; deve ser de { $min } a { $max }.
rb-error-reshuffle-penalty-invalid = A penalidade de reembaralhamento é { $points }; deve ser de { $min } a { $max } pontos.
rb-error-no-ball-packs = Selecione pelo menos um conjunto de bolas antes de iniciar o Rolling Balls.
rb-error-invalid-ball-packs = A seleção contém { $count } { $count ->
    [one] conjunto de bolas indisponível
   *[other] conjuntos de bolas indisponíveis
}. Remova conjuntos indisponíveis antes de começar.

# Ball sets
rb-pack-all = Todos os conjuntos de bolas misturados
rb-pack-international = Volta ao Mundo
rb-pack-vietnam = Jornada pelo Vietnã

# Around the World: -5
rb-ball-paris-pickpocket = Passaporte e carteira roubados no exterior
rb-ball-lost-luggage-in-london = Visita médica de emergência no exterior
rb-ball-tokyo-train-delay = Perdeu a última conexão internacional
rb-ball-sahara-sandstorm = Evacuação por clima severo
rb-ball-passport-lost-before-flight = Passaporte perdido antes da partida
# Around the World: -4
rb-ball-venice-flood = Inundação fecha sua acomodação
rb-ball-new-york-traffic = Cancelamento de voo noturno
rb-ball-amazon-mosquito-swarm = Bagagem essencial enviada para o país errado
rb-ball-berlin-club-rejected = Reserva de hotel ausente no check-in
rb-ball-hotel-booking-vanished = Rota de montanha fechada por vários dias
# Around the World: -3
rb-ball-spilled-coffee-in-rome = Telefone trincado durante uma transferência
rb-ball-sydney-sunburn = Esgotamento por calor cancela um passeio de um dia
rb-ball-istanbul-bazaar-scam = Reserva de excursão pré-paga cancelada
rb-ball-moscow-blizzard = Tempestade de neve bloqueia seu trem
rb-ball-dubai-heatwave = Veículo de aluguel quebra
# Around the World: -2
rb-ball-mexico-city-smog = Má qualidade do ar altera o itinerário
rb-ball-cairo-camel-spit = Enjoo de movimento em uma longa jornada
rb-ball-athens-ruins-trip = Torção no tornozelo em um tour a pé
rb-ball-rio-carnival-hangover = Dormiu demais e perdeu o passeio da manhã
rb-ball-bali-belly = Dor de estômago estraga uma tarde
# Around the World: -1
rb-ball-swiss-alps-avalanche = Trilha panorâmica fechada por segurança
rb-ball-amsterdam-bicycle-crash = Pneu de bicicleta furado
rb-ball-bangkok-tuk-tuk-breakdown = Tuk-tuk enguiça no trânsito
rb-ball-iceland-volcano-ash = Alerta meteorológico atrasa o voo
rb-ball-cape-town-wind = Vento forte fecha o mirante
# Around the World: 0
rb-ball-neutral-passport = Um carimbo de passaporte novo
rb-ball-airport-layover = Uma escala tranquila no aeroporto
rb-ball-hotel-lobby = Esperando no lobby do hotel
rb-ball-tourist-map = Desdobrando o mapa da cidade
rb-ball-souvenir-magnet = Escolhendo um ímã de lembrança
# Around the World: +1
rb-ball-free-museum-day = Entrada gratuita no museu
rb-ball-street-food-snack = Excelente lanche de rua
rb-ball-post-card-home = Cartão postal enviado para casa
rb-ball-friendly-local = Direções úteis de um morador local
rb-ball-sunny-day = Clima perfeito para explorar
# Around the World: +2
rb-ball-eiffel-tower-view = Horizonte de Paris a partir da Torre Eiffel
rb-ball-taj-mahal-sunrise = Nascer do sol no Taj Mahal
rb-ball-great-wall-hike = Caminhada na Grande Muralha
rb-ball-machu-picchu-climb = Manhã em Machu Picchu
rb-ball-kyoto-cherry-blossoms = Cerejeiras em flor em Quioto
# Around the World: +3
rb-ball-colosseum-tour = Visita guiada ao Coliseu
rb-ball-pyramids-exploration = Explorando o complexo das pirâmides de Gizé
rb-ball-santorini-sunset = Pôr do sol sobre Santorini
rb-ball-aurora-borealis = Aurora boreal no céu
rb-ball-safari-lion-sighting = Observação responsável de vida selvagem em safári
# Around the World: +4
rb-ball-bora-bora-villa = Estadia na lagoa em Bora Bora
rb-ball-maldives-scuba = Mergulho em recife nas Maldivas
rb-ball-niagara-falls-boat = Passeio de barco nas Cataratas do Niágara
rb-ball-grand-canyon-heli = Excursão de helicóptero pelo Grand Canyon
rb-ball-serengeti-migration = Grande Migração no Serengeti
# Around the World: +5
rb-ball-first-class-upgrade = Upgrade surpresa para a primeira classe
rb-ball-lottery-in-macau = Um passe ferroviário de um ano ganho
rb-ball-private-jet = Viagem insubstituível pelas ilhas
rb-ball-royal-palace-invite = Visita privada ao museu após o expediente
rb-ball-world-tour-ticket = Passagem de volta ao mundo

# Journey Through Vietnam: -5
rb-ball-stolen-motorbike = Passaporte e carteira roubados durante a viagem
rb-ball-flooded-street-saigon = Inundação força uma realocação de emergência
rb-ball-food-poisoning-bun-mam = Emergência médica interrompe a viagem
rb-ball-fake-taxi-scam = Falha de transporte causa perda de voo
rb-ball-passport-lost-at-airport = Passaporte perdido no aeroporto
# Journey Through Vietnam: -4
rb-ball-typhoon-in-central-vietnam = Evacuação por tufão na costa central
rb-ball-lost-wallet-ben-thanh = Bagagem essencial perdida em trânsito
rb-ball-traffic-jam-hanoi = Cancelamento de trem noturno
rb-ball-pickpocketed-in-bui-vien = Telefone roubado em um distrito lotado
rb-ball-mountain-road-landslide = Passo de montanha fechado por deslizamento de terra
# Journey Through Vietnam: -3
rb-ball-spilled-pho = Câmera danificada em chuva repentina
rb-ball-overcharged-for-coffee = Confusão na reserva de hotel
rb-ball-sunburn-in-mui-ne = Esgotamento por calor em Mui Ne
rb-ball-missed-train-to-sapa = Perdeu o trem noturno para Lao Cai
rb-ball-loud-karaoke-next-door = Noite sem dormir antes de uma partida cedo
# Journey Through Vietnam: -2
rb-ball-broken-flip-flop = Tira da sandália arrebenta em um tour a pé
rb-ball-sudden-downpour = Pancada de chuva tropical repentina
rb-ball-dog-chased-you = Ponto de ônibus errado longe do hotel
rb-ball-bitten-by-mosquitoes = Uma noite de picadas de mosquito
rb-ball-out-of-gas = Moto fica sem combustível
# Journey Through Vietnam: -1
rb-ball-spicy-chili-bite = Uma pimenta surpreendentemente forte
rb-ball-delayed-flight = Pequeno atraso em voo doméstico
rb-ball-wifi-disconnected = Sinal fraco nas montanhas
rb-ball-forgot-umbrella = Capa de chuva esquecida no hotel
rb-ball-minor-scratch = Caminho errado no Bairro Antigo
# Journey Through Vietnam: 0
rb-ball-plastic-stool = Um assento em um banquinho de calçada
rb-ball-iced-tea-tra-da = Copo de tra da
rb-ball-waiting-for-green-light = Esperando em um semáforo longo
rb-ball-bamboo-hat = Experimentando um non la
rb-ball-motorbike-helmet = Afivelando um capacete de moto
# Journey Through Vietnam: +1
rb-ball-tasty-banh-mi = Banh mi crocante no café da manhã
rb-ball-free-sugar-cane-juice = Caldo de cana fresco
rb-ball-friendly-street-vendor = Recepção calorosa de um vendedor de mercado
rb-ball-cool-breeze = Brisa fresca após a chuva
rb-ball-found-10k-vnd = Uma viagem econômica de ônibus local
# Journey Through Vietnam: +2
rb-ball-delicious-pho-bowl = Tigela perfumada de pho
rb-ball-egg-coffee-in-hanoi = Café com ovo em Hanói
rb-ball-boat-ride-in-ninh-binh = Passeio de barco pelo Complexo Paisagístico de Trang An
rb-ball-lantern-festival-hoian = Noite iluminada por lanternas na Cidade Antiga de Hoi An
rb-ball-motorbike-road-trip = Passeio de barco em pomar no Delta do Mekong
# Journey Through Vietnam: +3
rb-ball-ha-long-bay-cruise = Cruzeiro pela Baía de Ha Long - Arquipélago de Cat Ba
rb-ball-golden-bridge-bana-hills = Ponte Dourada acima de Ba Na Hills
rb-ball-phu-quoc-sunset = Pôr do sol em Phu Quoc
rb-ball-sapa-terraced-fields = Campos em terraço ao redor de Sa Pa
rb-ball-phong-nha-cave-exploration = Jornada em caverna em Phong Nha - Ke Bang
# Journey Through Vietnam: +4
rb-ball-tet-holiday-lucky-money = Reunião do Tet e dinheiro da sorte
rb-ball-vip-ticket-to-concert = Nascer do sol no circuito de Ha Giang
rb-ball-luxury-resort-stay = Visita de conservação comunitária em Con Dao
rb-ball-business-class-flight = Beliche panorâmico no Expresso da Reunificação
rb-ball-won-lottery-vietlott = Noite de festival entre os monumentos de Hue
# Journey Through Vietnam: +5
rb-ball-billionaire-inheritance = Expedição a Son Doong
rb-ball-found-gold-treasure = Oficina cultural privada com mestres artesãos
rb-ball-free-house-in-district-1 = Viagem de trem de um mês pelo Vietnã
rb-ball-national-hero-award = Convidado de honra em um festival de vila
rb-ball-ultimate-happiness = Viagem dos sonhos de Ha Giang a Ca Mau
