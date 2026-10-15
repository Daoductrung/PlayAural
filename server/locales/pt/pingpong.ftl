game-name-pingpong = Ping Pong

pingpong-intro = O Ping Pong começou. Vence o game quem chegar primeiro a 11 pontos, com dois pontos de vantagem. A partida é melhor de { $best_of }. A cada bola, use a seta correspondente ao som e aperte X; logo depois, use uma seta para escolher o destino. No saque, escolha a direção e aperte C.
pingpong-aim-left = Direção esquerda
pingpong-aim-right = Direção direita
pingpong-aim-center = Direção do meio
pingpong-serve-announcement = Saque de { $player }.
pingpong-serve-ball = Sacar a bola
pingpong-hit-ball = Rebater a bola
pingpong-read-position = Ler sua posição e a bola
pingpong-read-match = Ler o estado da partida

pingpong-your-serve = Seu saque. Pressione C.
pingpong-player-serves = { $player } saca.
pingpong-press-c-to-serve = É hora de sacar. Pressione C, não X.
pingpong-serve-between-points = Você só pode sacar quando o próximo ponto começar.
pingpong-waiting-for-serve = Aguardando { $player } sacar.
pingpong-waiting-for-return = Aguardando { $player } rebater a bola.
pingpong-point-resetting = O próximo ponto está sendo preparado.
pingpong-error-not-player = Somente um jogador ativo pode rebater a bola.
pingpong-edge-of-court = Você chegou ao limite da sua área de jogo.

pingpong-position-left = à esquerda
pingpong-position-center = no centro
pingpong-position-right = à direita
pingpong-position-close = perto da mesa
pingpong-position-middle = a meia distância
pingpong-position-far = longe da mesa
pingpong-position-summary = Você está { $horizontal }.
pingpong-ball-status = A bola vai para { $side }, { $depth }. { $bounced ->
    [true] Ela já quicou.
   *[false] Ela ainda não quicou.
}

pingpong-point-won = Você ganhou o ponto contra { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-player-wins-point = { $player } ganhou o ponto. Placar: { $points } a { $opponent_points }.
pingpong-score-announcement = Placar: { $first }, { $first_points }; { $second }, { $second_points }.
pingpong-point-lost-early = Você rebateu antes de a bola quicar. Ponto para { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-point-lost-out-of-reach = A bola estava fora do alcance da sua raquete. Ponto para { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-point-lost-net = Sua rebatida atingiu a rede. Ponto para { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-point-lost-late = Você rebateu tarde demais. Ponto para { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-point-lost-passed = A bola passou por você. Ponto para { $opponent }. Placar: { $your_points } a { $opponent_points }.
pingpong-game-won = { $player } venceu o game por { $winner_points } a { $loser_points } e agora tem { $games } games vencidos.
pingpong-you-win-match = Você venceu a partida com { $games } games. Maior troca de bola: { $longest } rebatidas.
pingpong-player-wins-match = { $player } venceu a partida com { $games } games. Maior troca de bola: { $longest } rebatidas.

pingpong-match-summary = Game { $game } de uma partida melhor de { $best_of }. Troca atual: { $rally } rebatidas.
pingpong-player-score = { $player }: { $games } games, { $points } pontos.
pingpong-end-player-line = { $player }: { $games } games vencidos.
pingpong-end-longest-rally = Maior troca de bola: { $count } rebatidas.

pingpong-best-of-one = Um game
pingpong-best-of-three = Melhor de três
pingpong-best-of-five = Melhor de cinco
pingpong-best-of-seven = Melhor de sete
pingpong-set-best-of = Duração da partida: { $format }
pingpong-select-best-of = Escolha a duração da partida.
pingpong-option-changed-best-of = Duração da partida definida como { $format }.
pingpong-desc-best-of = Escolha um game ou uma partida melhor de três, cinco ou sete.

pingpong-pace-relaxed = Tranquilo
pingpong-pace-standard = Padrão
pingpong-pace-fast = Rápido
pingpong-set-pace = Velocidade da bola: { $pace }
pingpong-select-pace = Escolha a velocidade da bola.
pingpong-option-changed-pace = Velocidade da bola definida como { $pace }.
pingpong-desc-pace = Controla o tempo disponível para localizar e rebater a bola.

pingpong-bot-easy = Fácil
pingpong-bot-normal = Normal
pingpong-bot-hard = Difícil
pingpong-set-bot-difficulty = Dificuldade do bot: { $difficulty }
pingpong-select-bot-difficulty = Escolha a dificuldade do bot.
pingpong-option-changed-bot-difficulty = Dificuldade do bot definida como { $difficulty }.
pingpong-desc-bot-difficulty = Controla o movimento, o tempo e a precisão das rebatidas do bot.

pingpong-language-en = Inglês
pingpong-language-es = Espanhol
pingpong-language-pt = Português
pingpong-language-vi = Vietnamita
pingpong-language-fa = Persa
pingpong-set-language = Idioma da mesa: { $language }
pingpong-select-language = Escolha o idioma da mesa.
pingpong-option-changed-language = Idioma da mesa definido como { $language }.
pingpong-desc-language = Define todas as falas e todos os controles desta mesa em português, inglês, espanhol, vietnamita ou persa.

pingpong-desc-team-mode = Escolha o modo individual oficial para dois jogadores ou o modo de duplas oficial para duas equipes de dois.
pingpong-error-singles-players = O modo individual exige exatamente dois jogadores ativos; atualmente há { $count }.
pingpong-error-doubles-players = O modo de duplas exige exatamente quatro jogadores ativos; atualmente há { $count }.
pingpong-error-best-of = A duração escolhida para a partida é inválida.
pingpong-error-pace = A velocidade escolhida para a bola é inválida.
pingpong-error-bot-difficulty = A dificuldade escolhida para o bot é inválida.
pingpong-error-language = O idioma escolhido para a mesa é inválido.
