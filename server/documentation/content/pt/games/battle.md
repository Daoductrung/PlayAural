**Batalha**

Batalha é um jogo de combate baseado em turnos onde você constrói um pequeno plantel de lutadores predefinidos e tenta durar mais que o outro lado. Algumas habilidades causam dano direto, algumas restauram a saúde e algumas alteram estatísticas de combate importantes, como ataque, defesa e velocidade.

# **Jogabilidade**

* Cada partida começa com uma **fase de seleção de lutadores**.
* Você escolhe a partir de um conjunto compartilhado de predefinições de lutadores embutidas.
* Assim que a seleção termina, a batalha começa e os lutadores começam a se revezar.
* No turno de um lutador, você escolhe **uma habilidade** e então escolhe **um alvo** para essa habilidade.
* Algumas habilidades têm como alvo um inimigo, algumas têm como alvo um aliado e algumas afetam apenas o usuário.
* Um lutador é removido da batalha se sua **saúde chegar a 0** ou se sua **velocidade cair abaixo de 30**.
* Na maioria dos modos, a batalha termina quando apenas um lado ainda tem lutadores ativos.

# **Mecânicas Especiais**

* **Seleção de lutadores:** a tela de seleção funciona como uma lista de verificação. Escolha uma predefinição para marcá-la, escolha-a novamente para desmarcá-la, depois use **Enviar seleção** ou **Concluir seleção** para fixar seu plantel final.
* **Modos de contagem fixa:** em modos como **1 Cada**, **2 Cada** e **3 Cada**, cada jogador deve escolher exatamente essa quantidade de lutadores.
* **Modos ilimitados:** em modos como **Cada um por Si Caótico**, **Arena**, **Sobrevivência** e **Ondas**, o host define o número máximo de lutadores que cada jogador pode trazer.
* **Batalha em Equipe:** quando o host escolhe um modo de equipe compartilhado, como **2 equipes de 2** ou **2 equipes de 3**, a tela de organização de equipe padrão é aberta antes da seleção de lutadores para que o host possa confirmar ou trocar os membros da equipe.
* **Ordem de turno:** se a mesa usar **Iniciativa**, o próximo lutador é escolhido por meio de uma rolagem de iniciativa ponderada pela velocidade. Se a mesa usar **Revezamento**, os lutadores se revezam em uma ordem repetida.
* **Estatísticas importam:** o ataque torna as habilidades ofensivas mais fortes, a defesa amacia o dano recebido e a velocidade ajuda a determinar o fluxo do turno e também pode decidir se um lutador permanece ativo.
* **Combate de alvo único:** cada habilidade no conjunto de regras atual afeta um alvo de cada vez. Não há habilidades de área de efeito.
* **Descrições de habilidades:** com **Dicas de Menu** ativadas, cada linha de habilidade inclui seu tipo de alvo e efeitos. Desative as Dicas de Menu em **Pessoal e Opções > Opções gerais > Acessibilidade** se preferir que as linhas de habilidades contenham apenas nomes.
* **Grupos de inimigos Clássicos vs Mistos:** em vários modos solo ou de resistência, **Clássico** significa que os lutadores inimigos vêm todos de uma predefinição escolhida, enquanto **Misto** significa que os inimigos são sorteados aleatoriamente de todo o plantel empacotado.

# **Modos**

* **Cada um por Si Caótico:** cada lutador se torna seu próprio lado. Se você selecionou mais de um lutador, pode acabar controlando lutadores que estão tentando derrotar uns aos outros.
* **1 Cada / 2 Cada / 3 Cada:** cada jogador traz 1, 2 ou 3 lutadores. Todos os lutadores escolhidos pelo mesmo jogador pertencem ao mesmo lado.
* **Batalha em Equipe:** os jogadores são atribuídos a equipes compartilhadas antes da partida. Cada jogador então escolhe até o limite de lutadores configurado, e todos os lutadores da mesma equipe organizada lutam juntos.
* **Cópia Fiel:** os jogadores primeiro escolhem o plantel aliado, depois o jogo cria clones inimigos correspondentes a partir dessas mesmas predefinições.
* **Arena Clássica:** o lado aliado luta contra inimigos construídos a partir de uma predefinição específica escolhida pelo host.
* **Arena Mista:** o lado aliado luta contra inimigos sorteados aleatoriamente de todo o plantel de predefinições.
* **Sobrevivência Clássica:** você luta contra um fluxo constante de inimigos de uma predefinição escolhida. Cada vez que você derrota um inimigo, o jogo traz outro imediatamente.
* **Sobrevivência Mista:** a mesma estrutura de sobrevivência, mas cada inimigo de substituição é escolhido aleatoriamente do plantel empacotado.
* **Ondas Clássicas:** você luta contra grupos de inimigos uma onda de cada vez usando uma predefinição escolhida. Uma nova onda começa apenas após o grupo inimigo atual ser totalmente derrotado.
* **Ondas Mistas:** a mesma estrutura de ondas, mas cada novo inimigo é escolhido aleatoriamente do plantel empacotado.
* Em **Ondas**, o tamanho da próxima onda é baseado em quantos lutadores aliados ainda estão vivos quando essa onda começa.
* Em **Sobrevivência** e **Ondas**, um **Alvo de Sobrevivência** igual a `0` significa que a corrida não tem limite de mortes e continua até que o lado aliado seja derrotado.

# **Pontuação**

* Nos modos de batalha normais, o vencedor é o último lado com lutadores ativos.
* Em **Sobrevivência** e **Ondas**, o lado aliado também pode vencer imediatamente alcançando o **Alvo de Sobrevivência** configurado.
* Se todos os lutadores aliados forem derrotados em **Sobrevivência** ou **Ondas**, a corrida termina em derrota.
* Batalha registra **Partidas Jogadas** para cada partida concluída.
* Sobrevivência e Ondas também alimentam recordes de resistência:
* **Mais Inimigos Derrotados:** sua melhor contagem de mortes em uma corrida de resistência.
* **Onda Mais Profunda Alcançada:** seu melhor número de ondas em uma corrida de Ondas.

# **Opções Personalizáveis**

* **Modo de Jogo:** Escolha a variante geral de Batalha (padrão: `1 Cada`, opções: `Cada um por Si Caótico`, `1 Cada`, `2 Cada`, `3 Cada`, `Batalha em Equipe`, `Cópia Fiel`, `Arena Clássica`, `Arena Mista`, `Sobrevivência Clássica`, `Sobrevivência Mista`, `Ondas Clássicas`, `Ondas Mistas`).
* **Modo de Equipe:** Usado apenas por `Batalha em Equipe`; iniciar `Batalha em Equipe` exige um modo de equipe não individual que se ajuste ao número atual de jogadores (padrão: `Individual`, as opções dependem da contagem de jogadores e incluem `2 equipes de 2`, `3 equipes de 2` e `2 equipes de 3` onde válido).
* **Modo de Turno:** Escolha se a ordem dos turnos segue a iniciativa ou a ordem da mesa (padrão: `Iniciativa`, opções: `Iniciativa`, `Revezamento`).
* **Modo de Equilíbrio:** Quando ativado, qualquer predefinição cuja linha de estatísticas esteja fora da linha de base equilibrada é reiniciada para `50 de saúde`, `0 de ataque`, `0 de defesa` e `100 de velocidade` (padrão: `Desligado`, opções: `Ligado` ou `Desligado`).
* **Limite de Lutadores em Modo Ilimitado:** Usado por `Cada um por Si Caótico`, `Batalha em Equipe`, `Cópia Fiel`, `Arena Clássica`, `Arena Mista`, `Sobrevivência Clássica`, `Sobrevivência Mista`, `Ondas Clássicas` e `Ondas Mistas` (padrão: `3`, intervalo: `1` a `6`).
* **Predefinição Inimiga Clássica:** Usado apenas por `Arena Clássica`, `Sobrevivência Clássica` e `Ondas Clássicas` (padrão: `Boxeador Iniciante`, opções: `Boxeador Iniciante`, `Boxeador`, `O Grande Lutador`, `Avião de Caça`, `Soldado de Baixa Patente`, `Soldado de Alta Patente`, `Lutador Fantasmagórico`, `O Lobo Alfa`, `O Leão Ardente`, `Mago Mestre`, `O Guerreiro Mágico`, `Mestre da Tempestade`).
* **Dificuldade da Arena:** Usado apenas quando o jogo gera inimigos de arena, sobrevivência ou onda (padrão: `Normal`, opções: `Fácil`, `Normal`, `Difícil`, `Insano`, `Profissional`, `Extrema`).
* **Alvo de Sobrevivência:** Usado apenas por `Sobrevivência Clássica`, `Sobrevivência Mista`, `Ondas Clássicas` e `Ondas Mistas`; um valor de `0` significa infinito (padrão: `0`, intervalo: `0` a `10000`).
* **Porcentagem de Cura de Sobrevivência:** Após cada surgimento de substituição em Sobrevivência, ou após cada onda limpa em Ondas, os lutadores aliados vivos recuperam esta porcentagem de sua saúde máxima. Usado apenas por `Sobrevivência Clássica`, `Sobrevivência Mista`, `Ondas Clássicas` e `Ondas Mistas` (padrão: `0`, intervalo: `0` a `100`).

# **Predefinições de Personagens**

* **Boxeador Iniciante:** Saúde 52, ataque 1, defesa 0, velocidade 100. Carga: Jab leve, Jab esquerdo, Jab direito, Cruzado esquerdo, Cruzado direito, Contragolpe, Gancho ascendente, Chute rápido, Rasteira, Cotovelada, Joelhada.
* **Boxeador:** Saúde 50, ataque 1, defesa 0, velocidade 100. Carga: Jab leve, Jab direito, Jab esquerdo, Soco no nariz, Soco no queixo, Soco giratório, Soco tonto, Soco estomacal, Golpe de nocaute, Soco surpresa, Soco combo, Barragem de socos, Soco espiritual, Soco de pedra, Chute combo, Chute giratório, Chute voador, Chutes frenéticos, Rajada de golpes, Pancada corporal, Arremesso, Soco contínuo, Briga.
* **O Grande Lutador:** Saúde 60, ataque 2, defesa 1, velocidade 100. Carga: Espada de aço, Espada de chama, Espada de gelo, Espada eletrificada, Espada amaldiçoada, Espada animada, Corte rápido, Corte giratório, Chicote com ponta de aço, Martelo de guerra vulcânico, Martelo de guerra antigo, Martelo de guerra de aço, Machado de guerra feérico, Arremesso de machado, Adaga sangrenta, Faca de fogo, Adaga congelada, Faca de gelo, Adaga das sombras, Kunai, Cutelo de carne, Cassetete.
* **Avião de Caça:** Saúde 72, ataque 2, defesa 1, velocidade 95. Carga: Canhão de aeronave, Canhão de plasma, Metralhadora de aeronave, Arma laser, Laser ocular, Metralhadora, Espingarda, Rifle de precisão, Granada de mão, Taser pesado, Choque elétrico, Explosão elétrica, Granada disruptora, Bomba dissolvente, Bomba de veneno.
* **Soldado de Baixa Patente:** Saúde 50, ataque 1, defesa 1, velocidade 100. Carga: Cruzado direito, Metralhadora, Espingarda, Rasteira, Rolamento de combate, Cassetete, Cutelo de carne, Kunai, Conter, Investida, Fugir, Tirar sangue, Contragolpe, Cotovelada, Joelhada, Mergulho suicida.
* **Soldado de Alta Patente:** Saúde 64, ataque 1, defesa 1, velocidade 100. Carga: Rifle de precisão, Metralhadora, Arma laser, Granada de mão, Canhão de plasma, Rolamento de combate, Armadura de batalha, Forja de batalha, Frenesi, Acelerar, Velocidade, Preso em combate, Sacrifício por poder, Sacrifício por guarda, Sacrifício por velocidade, Negociação mágica, Intimidar.
* **Lutador Fantasmagórico:** Saúde 50, ataque 2, defesa 0, velocidade 105. Carga: Espada de chama, Martelo de guerra antigo, Chicote com ponta de aço, Grito fantasmagórico, Alteração espectral, Rugido, Riso assustador, Comer cérebro, Explodir das sombras, Vórtice dos falecidos, Drenar, Mini drenar, Drenar guarda, Drenar poder, Drenar velocidade, Super drenar, Mordida vampírica, Enfraquecer, Intimidar, Escudo mágico.
* **O Lobo Alfa:** Saúde 55, ataque 3, defesa 0, velocidade 100. Carga: Uivo, Círculo, Mordida, Mordida feroz, Imobilizar, Mandíbula estalando, Garra, Arranhão, Garra de leão, Despedaçar, Tacle de rúgbi, Agarrão, Chave de cabeça, Chave de braço, Chave de perna, Conduzir ao chão, Rugido, Conter.
* **O Leão Ardente:** Saúde 60, ataque 2, defesa 0, velocidade 100. Carga: Bola de fogo, Flecha de chama, Esfera flamejante, Brasa, Mordida feroz, Rugido, Garra, Pó ardente, Voleio de bolas de fogo, Faca de fogo, Machado de guerra feérico, Espada de chama, Chuva de faíscas.
* **Mago Mestre:** Saúde 46, ataque 4, defesa 0, velocidade 105. Carga: Bola de fogo, Bola de gelo, Esfera flamejante, Raio, Flecha de chama, Flecha de raio, Criosfera, Esfera elétrica, Arco longo élfico, Cubo de gelo, Chuva de gelo, Avalanche, Esfera mágica, Força mágica, Escudo mágico, Curar, Cura maior, Esfera divina, Explosão sísmica.
* **O Guerreiro Mágico:** Saúde 58, ataque 2, defesa 2, velocidade 100. Carga: Espada de aço, Martelo de guerra antigo, Raio, Flecha de chama, Pancada corporal, Rugido, Machado de guerra feérico, Espada eletrificada, Espada amaldiçoada, Espada animada, Lâmina mágica de proteção, Força mágica, Armadura de batalha, Relâmpago, Corte rápido.
* **Mestre da Tempestade:** Saúde 50, ataque 4, defesa 0, velocidade 100. Carga: Nuvem de tempestade, Relâmpago, Onda de trovão, Esfera elétrica, Choque elétrico, Flecha de raio, Chuva de faíscas, Raio, Explosão elétrica, Explosão sísmica, Avalanche, Bola de gelo, Criosfera, Taser pesado.

# **Diretório de Habilidades**

* Cada habilidade abaixo usa o nome embutido exato do registro empacotado.
* **Canhão de aeronave:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do alvo em 3. Atribuído a: Avião de Caça.
* **Metralhadora de aeronave:** Tem como alvo um lutador inimigo. Efeitos: causa 2-8 de dano; aumenta a velocidade do usuário em 5; aumenta a velocidade do alvo em 5. Atribuído a: Avião de Caça.
* **Martelo de guerra antigo:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; aumenta o ataque do usuário em 4; reduz a velocidade do usuário em 4. Atribuído a: Lutador Fantasmagórico, O Grande Lutador, O Guerreiro Mágico.
* **Espada animada:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; aumenta o ataque do usuário em 3. Atribuído a: O Grande Lutador, O Guerreiro Mágico.
* **Chave de braço:** Tem como alvo um lutador inimigo. Efeitos: causa 4-9 de dano; reduz a defesa do alvo em 2. Atribuído a: O Lobo Alfa.
* **Avalanche:** Tem como alvo um lutador inimigo. Efeitos: causa 12-20 de dano; reduz o ataque do usuário em 4; reduz a velocidade do alvo em 10. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Arremesso de machado:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano; reduz o ataque do usuário em 2; reduz a velocidade do alvo em 10. Atribuído a: O Grande Lutador.
* **Contragolpe:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 10. Atribuído a: Soldado de Baixa Patente, Boxeador Iniciante.
* **Armadura de batalha:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: aumenta a defesa do alvo em 3; reduz a velocidade do alvo em 2. Atribuído a: Soldado de Alta Patente, O Guerreiro Mágico.
* **Forja de batalha:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: aumenta o ataque do alvo em 2; aumenta a defesa do alvo em 1. Atribuído a: Soldado de Alta Patente.
* **Frenesi:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3. Atribuído a: Soldado de Alta Patente.
* **Mordida:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano. Atribuído a: O Lobo Alfa.
* **Adaga sangrenta:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz o ataque do alvo em 1. Atribuído a: O Grande Lutador.
* **Pancada corporal:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do alvo em 3. Atribuído a: Boxeador, O Guerreiro Mágico.
* **Comer cérebro:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 2; reduz a velocidade do alvo em 15. Atribuído a: Lutador Fantasmagórico.
* **Briga:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2; aumenta a defesa do usuário em 2; aumenta a velocidade do usuário em 10; aumenta o ataque do alvo em 2; aumenta a defesa do alvo em 2; aumenta a velocidade do alvo em 10. Atribuído a: Boxeador.
* **Pó ardente:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 12. Atribuído a: O Leão Ardente.
* **Círculo:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; aumenta o ataque do alvo em 3. Atribuído a: O Lobo Alfa.
* **Garra:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a defesa do alvo em 1. Atribuído a: O Lobo Alfa, O Leão Ardente.
* **Rolamento de combate:** Tem como alvo um lutador inimigo. Efeitos: causa 1-5 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 4; aumenta a velocidade do usuário em 12. Atribuído a: Soldado de Alta Patente, Soldado de Baixa Patente.
* **Chute combo:** Tem como alvo um lutador inimigo. Efeitos: causa 10-16 de dano; reduz o ataque do usuário em 2; reduz a velocidade do usuário em 2. Atribuído a: Boxeador.
* **Soco combo:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 1. Atribuído a: Boxeador.
* **Criosfera:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 25. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Espada amaldiçoada:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 5. Atribuído a: O Grande Lutador, O Guerreiro Mágico.
* **Granada disruptora:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; reduz o ataque do alvo em 3; reduz a defesa do alvo em 3; reduz o ataque do usuário em 1. Atribuído a: Avião de Caça.
* **Bomba dissolvente:** Tem como alvo um lutador inimigo. Efeitos: causa 2-10 de dano; reduz o ataque do usuário em 2; reduz a defesa do alvo em 4. Atribuído a: Avião de Caça.
* **Esfera divina:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 5-9 de saúde; aumenta a defesa do alvo em 2; aumenta a velocidade do alvo em 3. Atribuído a: Mago Mestre.
* **Soco tonto:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a velocidade do alvo em 8. Atribuído a: Boxeador.
* **Drenar:** Tem como alvo um lutador inimigo. Efeitos: causa 10-12 de dano e cura o usuário em 33% do dano causado. Atribuído a: Lutador Fantasmagórico.
* **Tirar sangue:** Tem como alvo um lutador inimigo. Efeitos: causa 1-1 de dano; reduz a velocidade do usuário em 8; reduz a defesa do alvo em 4. Atribuído a: Soldado de Baixa Patente.
* **Cotovelada:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano. Atribuído a: Soldado de Baixa Patente, Boxeador Iniciante.
* **Choque elétrico:** Tem como alvo um lutador inimigo. Efeitos: causa 2-6 de dano; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 20. Atribuído a: Avião de Caça, Mestre da Tempestade.
* **Esfera elétrica:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a velocidade do alvo em 6. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Explosão elétrica:** Tem como alvo um lutador inimigo. Efeitos: causa 14-28 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do alvo em 10. Atribuído a: Avião de Caça, Mestre da Tempestade.
* **Espada eletrificada:** Tem como alvo um lutador inimigo. Efeitos: causa 8-10 de dano. Atribuído a: O Grande Lutador, O Guerreiro Mágico.
* **Arco longo élfico:** Tem como alvo um lutador inimigo. Efeitos: causa 5-12 de dano; reduz a velocidade do alvo em 10. Atribuído a: Mago Mestre.
* **Brasa:** Tem como alvo um lutador inimigo. Efeitos: causa 2-5 de dano; reduz o ataque do alvo em 1; reduz a velocidade do alvo em 5. Atribuído a: O Leão Ardente.
* **Explodir das sombras:** Tem como alvo um lutador inimigo. Efeitos: causa 18-26 de dano; reduz a velocidade do usuário em 35. Atribuído a: Lutador Fantasmagórico.
* **Laser ocular:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; reduz a defesa do alvo em 4; reduz a velocidade do usuário em 4. Atribuído a: Avião de Caça.
* **Mordida feroz:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: O Lobo Alfa, O Leão Ardente.
* **Machado de guerra feérico:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2. Atribuído a: O Leão Ardente, O Grande Lutador, O Guerreiro Mágico.
* **Faca de fogo:** Tem como alvo um lutador inimigo. Efeitos: causa 2-14 de dano; reduz a defesa do usuário em 1; aumenta a velocidade do usuário em 6; reduz a defesa do alvo em 1. Atribuído a: O Leão Ardente, O Grande Lutador.
* **Bola de fogo:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 8. Atribuído a: Mago Mestre, O Leão Ardente.
* **Barragem de socos:** Tem como alvo um lutador inimigo. Efeitos: causa 10-18 de dano; reduz o ataque do usuário em 2; reduz a defesa do alvo em 1; reduz a velocidade do alvo em 10. Atribuído a: Boxeador.
* **Flecha de chama:** Tem como alvo um lutador inimigo. Efeitos: causa 7-15 de dano; reduz o ataque do usuário em 4; reduz a defesa do alvo em 3. Atribuído a: Mago Mestre, O Leão Ardente, O Guerreiro Mágico.
* **Espada de chama:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a velocidade do usuário em 7; reduz a defesa do alvo em 3. Atribuído a: Lutador Fantasmagórico, O Leão Ardente, O Grande Lutador.
* **Esfera flamejante:** Tem como alvo um lutador inimigo. Efeitos: causa 5-11 de dano; reduz o ataque do usuário em 2; reduz o ataque do alvo em 2. Atribuído a: Mago Mestre, O Leão Ardente.
* **Rajada de golpes:** Tem como alvo um lutador inimigo. Efeitos: causa 11-15 de dano; reduz o ataque do usuário em 1; reduz a defesa do usuário em 1; reduz a velocidade do usuário em 5. Atribuído a: Boxeador.
* **Chute voador:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do usuário em 3; aumenta a velocidade do usuário em 8; reduz a defesa do alvo em 2; aumenta a velocidade do alvo em 2. Atribuído a: Boxeador.
* **Chutes frenéticos:** Tem como alvo um lutador inimigo. Efeitos: causa 2-12 de dano; reduz a defesa do usuário em 6; aumenta a velocidade do usuário em 20. Atribuído a: Boxeador.
* **Riso assustador:** Tem como alvo um lutador inimigo. Efeitos: aumenta a defesa do usuário em 1; aumenta a velocidade do usuário em 3; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 10. Atribuído a: Lutador Fantasmagórico.
* **Adaga congelada:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; reduz a velocidade do alvo em 10. Atribuído a: O Grande Lutador.
* **Grito fantasmagórico:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz o ataque do alvo em 3; aumenta a defesa do alvo em 3. Atribuído a: Lutador Fantasmagórico.
* **Agarrão:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano; reduz a velocidade do usuário em 10; reduz a velocidade do alvo em 10. Atribuído a: O Lobo Alfa.
* **Cura maior:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 12-18 de saúde; aumenta a velocidade do alvo em 2. Atribuído a: Mago Mestre.
* **Conduzir ao chão:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano; reduz a defesa do usuário em 5; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 5. Atribuído a: O Lobo Alfa.
* **Drenar guarda:** Tem como alvo um lutador inimigo. Efeitos: aumenta a defesa do usuário em 3; reduz a defesa do alvo em 3. Atribuído a: Lutador Fantasmagórico.
* **Soco estomacal:** Tem como alvo um lutador inimigo. Efeitos: causa 10-14 de dano; reduz o ataque do alvo em 4; reduz a defesa do usuário em 1. Atribuído a: Boxeador.
* **Granada de mão:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz a defesa do alvo em 2. Atribuído a: Avião de Caça, Soldado de Alta Patente.
* **Velocidade:** Tem como alvo apenas o usuário. Efeitos: aumenta a velocidade do usuário em 12. Atribuído a: Soldado de Alta Patente.
* **Chave de cabeça:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; aumenta a defesa do usuário em 3; reduz a velocidade do usuário em 1; reduz a defesa do alvo em 4; reduz a velocidade do alvo em 8. Atribuído a: O Lobo Alfa.
* **Curar:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 8-14 de saúde. Atribuído a: Mago Mestre.
* **Taser pesado:** Tem como alvo um lutador inimigo. Efeitos: causa 7-11 de dano; reduz a velocidade do alvo em 12; reduz o ataque do alvo em 2; reduz a velocidade do usuário em 3. Atribuído a: Avião de Caça, Mestre da Tempestade.
* **Uivo:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 2. Atribuído a: O Lobo Alfa.
* **Bola de gelo:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Cubo de gelo:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano; aumenta o ataque do usuário em 3; aumenta a defesa do usuário em 3. Atribuído a: Mago Mestre.
* **Faca de gelo:** Tem como alvo um lutador inimigo. Efeitos: causa 2-5 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 5. Atribuído a: O Grande Lutador.
* **Espada de gelo:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz o ataque do usuário em 1; reduz a velocidade do alvo em 7. Atribuído a: O Grande Lutador.
* **Intimidar:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz o ataque do alvo em 3. Atribuído a: Lutador Fantasmagórico, Soldado de Alta Patente.
* **Soco no queixo:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; reduz a defesa do alvo em 2. Atribuído a: Boxeador.
* **Joelhada:** Tem como alvo um lutador inimigo. Efeitos: causa 3-6 de dano; reduz o ataque do alvo em 2. Atribuído a: Soldado de Baixa Patente, Boxeador Iniciante.
* **Golpe de nocaute:** Tem como alvo um lutador inimigo. Efeitos: causa 10-30 de dano; reduz o ataque do usuário em 5; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 30. Atribuído a: Boxeador.
* **Kunai:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; aumenta a velocidade do usuário em 4; reduz a defesa do alvo em 3. Atribuído a: Soldado de Baixa Patente, O Grande Lutador.
* **Arma laser:** Tem como alvo um lutador inimigo. Efeitos: causa 5-18 de dano; reduz a velocidade do usuário em 6. Atribuído a: Avião de Caça, Soldado de Alta Patente.
* **Cruzado esquerdo:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Boxeador Iniciante.
* **Jab esquerdo:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Boxeador, Boxeador Iniciante.
* **Chave de perna:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano; reduz a defesa do alvo em 4. Atribuído a: O Lobo Alfa.
* **Jab leve:** Tem como alvo um lutador inimigo. Efeitos: causa 3-8 de dano. Atribuído a: Boxeador, Boxeador Iniciante.
* **Flecha de raio:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz a defesa do alvo em 1. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Raio:** Tem como alvo um lutador inimigo. Efeitos: causa 8-15 de dano; reduz o ataque do usuário em 3; reduz a velocidade do alvo em 10. Atribuído a: Mago Mestre, Mestre da Tempestade, O Guerreiro Mágico.
* **Garra de leão:** Tem como alvo um lutador inimigo. Efeitos: causa 10-13 de dano; aumenta o ataque do usuário em 3; reduz a velocidade do alvo em 4. Atribuído a: O Lobo Alfa.
* **Preso em combate:** Tem como alvo um lutador inimigo. Efeitos: causa 4-6 de dano; aumenta o ataque do usuário em 3; aumenta a velocidade do usuário em 10; aumenta o ataque do alvo em 3; aumenta a velocidade do alvo em 10. Atribuído a: Soldado de Alta Patente.
* **Metralhadora:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta a velocidade do usuário em 5. Atribuído a: Avião de Caça, Soldado de Alta Patente, Soldado de Baixa Patente.
* **Negociação mágica:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; aumenta o ataque do alvo em 3. Atribuído a: Soldado de Alta Patente.
* **Escudo mágico:** Tem como alvo apenas o usuário. Efeitos: aumenta a defesa do usuário em 4. Atribuído a: Lutador Fantasmagórico, Mago Mestre.
* **Esfera mágica:** Tem como alvo um lutador inimigo. Efeitos: causa 7-9 de dano. Atribuído a: Mago Mestre.
* **Força mágica:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 4. Atribuído a: Mago Mestre, O Guerreiro Mágico.
* **Despedaçar:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a velocidade do usuário em 12; reduz o ataque do alvo em 2; reduz a defesa do alvo em 3. Atribuído a: O Lobo Alfa.
* **Cutelo de carne:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano e cura o usuário em 30% do dano causado. Atribuído a: Soldado de Baixa Patente, O Grande Lutador.
* **Mini drenar:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano e cura o usuário em 25% do dano causado. Atribuído a: Lutador Fantasmagórico.
* **Cassetete:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 8. Atribuído a: Soldado de Baixa Patente, O Grande Lutador.
* **Soco no nariz:** Tem como alvo um lutador inimigo. Efeitos: causa 10-12 de dano. Atribuído a: Boxeador.
* **Imobilizar:** Tem como alvo um lutador inimigo. Efeitos: causa 10-13 de dano; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 20. Atribuído a: O Lobo Alfa.
* **Canhão de plasma:** Tem como alvo um lutador inimigo. Efeitos: causa 16-24 de dano; reduz a defesa do usuário em 6. Atribuído a: Avião de Caça, Soldado de Alta Patente.
* **Bomba de veneno:** Tem como alvo um lutador inimigo. Efeitos: causa 1-10 de dano; reduz o ataque do usuário em 2; reduz a velocidade do alvo em 12. Atribuído a: Avião de Caça.
* **Drenar poder:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; reduz o ataque do alvo em 3. Atribuído a: Lutador Fantasmagórico.
* **Soco contínuo:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; aumenta a defesa do usuário em 3; reduz a velocidade do usuário em 5; reduz a defesa do alvo em 3; aumenta a velocidade do alvo em 3. Atribuído a: Boxeador.
* **Corte rápido:** Tem como alvo um lutador inimigo. Efeitos: causa 1-7 de dano; aumenta a velocidade do usuário em 8. Atribuído a: O Grande Lutador, O Guerreiro Mágico.
* **Chuva de gelo:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 3. Atribuído a: Mago Mestre.
* **Chuva de faíscas:** Tem como alvo um lutador inimigo. Efeitos: causa 12-16 de dano; reduz o ataque do usuário em 4. Atribuído a: Mestre da Tempestade, O Leão Ardente.
* **Conter:** Tem como alvo um lutador inimigo. Efeitos: causa 4-7 de dano; reduz a velocidade do alvo em 12. Atribuído a: Soldado de Baixa Patente, O Lobo Alfa.
* **Acelerar:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 2; reduz a defesa do usuário em 2; aumenta a velocidade do usuário em 5. Atribuído a: Soldado de Alta Patente.
* **Cruzado direito:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Soldado de Baixa Patente, Boxeador Iniciante.
* **Jab direito:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Boxeador, Boxeador Iniciante.
* **Rugido:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 3; reduz a velocidade do usuário em 5. Atribuído a: Lutador Fantasmagórico, O Lobo Alfa, O Leão Ardente, O Guerreiro Mágico.
* **Tacle de rúgbi:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; reduz a defesa do alvo em 5; aumenta a velocidade do alvo em 5. Atribuído a: O Lobo Alfa.
* **Fugir:** Tem como alvo apenas o usuário. Efeitos: reduz o ataque do usuário em 5; reduz a defesa do usuário em 5; aumenta a velocidade do usuário em 20. Atribuído a: Soldado de Baixa Patente.
* **Investida:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 4; reduz a defesa do usuário em 5; aumenta a velocidade do usuário em 15. Atribuído a: Soldado de Baixa Patente.
* **Sacrifício por guarda:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta a defesa do usuário em 5; aumenta a defesa do alvo em 5. Atribuído a: Soldado de Alta Patente.
* **Sacrifício por poder:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta o ataque do usuário em 5; aumenta o ataque do alvo em 5. Atribuído a: Soldado de Alta Patente.
* **Sacrifício por velocidade:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta a velocidade do usuário em 20; aumenta a velocidade do alvo em 20. Atribuído a: Soldado de Alta Patente.
* **Arranhão:** Tem como alvo um lutador inimigo. Efeitos: causa 3-9 de dano. Atribuído a: O Lobo Alfa.
* **Explosão sísmica:** Tem como alvo um lutador inimigo. Efeitos: causa 18-22 de dano; reduz a velocidade do usuário em 10; reduz a defesa do alvo em 4. Atribuído a: Mago Mestre, Mestre da Tempestade.
* **Adaga das sombras:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 6. Atribuído a: O Grande Lutador.
* **Espingarda:** Tem como alvo um lutador inimigo. Efeitos: causa 6-16 de dano; reduz o ataque do usuário em 2. Atribuído a: Avião de Caça, Soldado de Baixa Patente.
* **Chute rápido:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a velocidade do usuário em 12; reduz a defesa do alvo em 4; reduz a velocidade do alvo em 8. Atribuído a: Boxeador Iniciante.
* **Mandíbula estalando:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 3. Atribuído a: O Lobo Alfa.
* **Rifle de precisão:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano; reduz a velocidade do usuário em 8. Atribuído a: Avião de Caça, Soldado de Alta Patente.
* **Alteração espectral:** Tem como alvo um lutador inimigo. Efeitos: causa 8-10 de dano; aumenta o ataque do usuário em 4; aumenta a velocidade do usuário em 4; aumenta o ataque do alvo em 4; aumenta a velocidade do alvo em 4. Atribuído a: Lutador Fantasmagórico.
* **Drenar velocidade:** Tem como alvo um lutador inimigo. Efeitos: aumenta a velocidade do usuário em 12; reduz a velocidade do alvo em 12. Atribuído a: Lutador Fantasmagórico.
* **Corte giratório:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; reduz o ataque do usuário em 1; aumenta a velocidade do usuário em 5. Atribuído a: O Grande Lutador.
* **Chute giratório:** Tem como alvo um lutador inimigo. Efeitos: causa 13-16 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 5. Atribuído a: Boxeador.
* **Soco giratório:** Tem como alvo um lutador inimigo. Efeitos: causa 15-18 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 2; aumenta a velocidade do usuário em 3; reduz a velocidade do alvo em 6. Atribuído a: Boxeador.
* **Soco espiritual:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; aumenta o ataque do usuário em 2; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 4. Atribuído a: Boxeador.
* **Espada de aço:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2; aumenta o ataque do alvo em 2. Atribuído a: O Grande Lutador, O Guerreiro Mágico.
* **Martelo de guerra de aço:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano. Atribuído a: O Grande Lutador.
* **Chicote com ponta de aço:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; aumenta o ataque do usuário em 1; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 5. Atribuído a: Lutador Fantasmagórico, O Grande Lutador.
* **Soco de pedra:** Tem como alvo um lutador inimigo. Efeitos: causa 11-15 de dano; aumenta a defesa do usuário em 2; reduz a velocidade do usuário em 5; reduz a velocidade do alvo em 3. Atribuído a: Boxeador.
* **Soco surpresa:** Tem como alvo um lutador inimigo. Efeitos: causa 9-12 de dano; reduz a defesa do alvo em 2. Atribuído a: Boxeador.
* **Mergulho suicida:** Tem como alvo um lutador inimigo. Efeitos: causa 20-30 de dano; reduz o ataque do usuário em 4; reduz a defesa do usuário em 4; reduz a velocidade do alvo em 30. Atribuído a: Soldado de Baixa Patente.
* **Super drenar:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano e cura o usuário em 50% do dano causado. Atribuído a: Lutador Fantasmagórico.
* **Arremesso:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano; reduz o ataque do usuário em 3; reduz o ataque do alvo em 3; reduz a defesa do alvo em 3. Atribuído a: Boxeador.
* **Nuvem de tempestade:** Tem como alvo um lutador inimigo. Efeitos: reduz a defesa do usuário em 3; reduz a velocidade do usuário em 10; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 20. Atribuído a: Mestre da Tempestade.
* **Onda de trovão:** Tem como alvo um lutador inimigo. Efeitos: reduz o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 10; reduz a velocidade do alvo em 30. Atribuído a: Mestre da Tempestade.
* **Relâmpago:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; reduz a velocidade do alvo em 5. Atribuído a: Mestre da Tempestade, O Guerreiro Mágico.
* **Rasteira:** Tem como alvo um lutador inimigo. Efeitos: causa 4-9 de dano; reduz o ataque do usuário em 2; aumenta a velocidade do usuário em 4; aumenta o ataque do alvo em 2; aumenta a velocidade do alvo em 1. Atribuído a: Soldado de Baixa Patente, Boxeador Iniciante.
* **Gancho ascendente:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; aumenta o ataque do usuário em 2; aumenta a defesa do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 2. Atribuído a: Boxeador Iniciante.
* **Mordida vampírica:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano e cura o usuário em 60% do dano causado. Atribuído a: Lutador Fantasmagórico.
* **Martelo de guerra vulcânico:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a defesa do alvo em 5. Atribuído a: O Grande Lutador.
* **Voleio de bolas de fogo:** Tem como alvo um lutador inimigo. Efeitos: causa 12-16 de dano; aumenta o ataque do usuário em 2. Atribuído a: O Leão Ardente.
* **Vórtice dos falecidos:** Tem como alvo um lutador inimigo. Efeitos: causa 9-15 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz a velocidade do usuário em 2. Atribuído a: Lutador Fantasmagórico.
* **Lâmina mágica de proteção:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; aumenta a defesa do usuário em 1; reduz o ataque do alvo em 1. Atribuído a: O Guerreiro Mágico.
* **Enfraquecer:** Tem como alvo um lutador inimigo. Efeitos: reduz o ataque do alvo em 3; reduz a velocidade do alvo em 5. Atribuído a: Lutador Fantasmagórico.

# **Atalhos de Teclado**

* **S:** Lê o status da batalha.
* **Shift+S:** Abre o status detalhado da batalha como uma lista.
* **V:** Lê o plantel de combate completo. Isso fica bloqueado durante a seleção de lutadores.
* **A:** Em modos baseados em equipe, visualiza apenas os lutadores aliados vivos.
* **E:** Em modos baseados em equipe, visualiza apenas os lutadores inimigos vivos.
* **U:** Anula a escolha de lutador mais recente durante a seleção.
* **D:** Termina a seleção em modos ilimitados.
* **T:** Ouve de quem é o turno ou se o jogo ainda está na seleção.
