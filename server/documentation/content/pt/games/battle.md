# **Battle**

Battle é um jogo de combate baseado em turnos onde você constrói um pequeno plantel de lutadores predefinidos e tenta durar mais que o outro lado. Algumas habilidades causam dano direto, algumas restauram a saúde e algumas alteram estatísticas de combate importantes, como ataque, defesa e velocidade.

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
* **Modos ilimitados:** em modos como **Cada um por si caótico**, **Arena**, **Sobrevivência** e **Ondas**, o host define o número máximo de lutadores que cada jogador pode trazer.
* **Batalha em Equipe:** quando o host escolhe um modo de equipe compartilhado, como **2 equipes de 2** ou **2 equipes de 3**, a tela de organização de equipe padrão é aberta antes da seleção de lutadores para que o host possa confirmar ou trocar os membros da equipe.
* **Ordem de turno:** se a mesa usar **Iniciativa**, o próximo lutador é escolhido por meio de uma rolagem de iniciativa ponderada pela velocidade. Se a mesa usar **Rodízio**, os lutadores se revezam em uma ordem repetida.
* **Estatísticas importam:** o ataque torna as habilidades ofensivas mais fortes, a defesa amacia o dano recebido e a velocidade ajuda a determinar o fluxo do turno e também pode decidir se um lutador permanece ativo.
* **Combate de alvo único:** cada habilidade no conjunto de regras atual afeta um alvo de cada vez. Não há habilidades de área de efeito.
* **Descrições de habilidades:** com **Dicas de Menu** ativadas, cada linha de habilidade inclui seu tipo de alvo e efeitos. Desative as Dicas de Menu em **Pessoal e Opções > Opções gerais > Acessibilidade** se preferir que as linhas de habilidades contenham apenas nomes.
* **Grupos de inimigos Clássicos vs Mistos:** em vários modos solo ou de resistência, **Clássico** significa que os lutadores inimigos vêm todos de uma predefinição escolhida, enquanto **Misto** significa que os inimigos são sorteados aleatoriamente de todo o plantel empacotado.

# **Modos**

* **Cada um por si caótico:** cada lutador se torna seu próprio lado. Se você selecionou mais de um lutador, pode acabar controlando lutadores que estão tentando derrotar uns aos outros.
* **1 Cada / 2 Cada / 3 Cada:** cada jogador traz 1, 2 ou 3 lutadores. Todos os lutadores escolhidos pelo mesmo jogador pertencem ao mesmo lado.
* **Batalha em Equipe:** os jogadores são atribuídos a equipes compartilhadas antes da partida. Cada jogador então escolhe até o limite de lutadores configurado, e todos os lutadores da mesma equipe organizada lutam juntos.
* **Imagem Espelhada:** os jogadores primeiro escolhem o plantel aliado, depois o jogo cria clones inimigos correspondentes a partir dessas mesmas predefinições.
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
* O Battle registra **Partidas Jogadas** para cada partida concluída.
* Sobrevivência e Ondas também alimentam recordes de resistência:
* **Mais Inimigos Derrotados:** sua melhor contagem de mortes em uma corrida de resistência.
* **Onda Mais Profunda Alcançada:** seu melhor número de ondas em uma corrida de Ondas.

# **Opções Personalizáveis**

* **Modo de Jogo:** Escolha a variante geral do Battle (padrão: `1 Cada`, opções: `Cada um por si caótico`, `1 Cada`, `2 Cada`, `3 Cada`, `Batalha em Equipe`, `Imagem Espelhada`, `Arena Clássica`, `Arena Mista`, `Sobrevivência Clássica`, `Sobrevivência Mista`, `Ondas Clássicas`, `Ondas Mistas`).
* **Modo de Equipe:** Usado apenas por `Team Battle`; iniciar `Team Battle` exige um modo de equipe não individual que se ajuste ao número atual de jogadores (padrão: `Individual`, as opções dependem da contagem de jogadores e incluem `2 equipes de 2`, `3 equipes de 2` e `2 equipes de 3` onde válido).
* **Modo de Turno:** Escolha se a ordem dos turnos segue a iniciativa ou a ordem da mesa (padrão: `Iniciativa`, opções: `Iniciativa`, `Rodízio`).
* **Modo de Equilíbrio:** Quando ativado, qualquer predefinição cuja linha de estatísticas esteja fora da linha de base equilibrada é reiniciada para `50 de saúde`, `0 de ataque`, `0 de defesa` e `100 de velocidade` (padrão: `Desligado`, opções: `Ligado` ou `Desligado`).
* **Limite de Lutadores em Modo Ilimitado:** Usado por `Chaos Free For All`, `Team Battle`, `Spitting Image`, `Classic Arena`, `Mixed Arena`, `Classic Survival`, `Mixed Survival`, `Classic Waves` e `Mixed Waves` (padrão: `3`, intervalo: `1` a `6`).
* **Predefinição Inimiga Clássica:** Usado apenas por `Classic Arena`, `Classic Survival` e `Classic Waves` (padrão: `Novice Boxer`, opções: `Novice Boxer`, `Boxer`, `The Great Fighter`, `Fighter Plane`, `Low-Rank Soldier`, `High-Rank Soldier`, `Ghostly Fighter`, `The Alpha Wolf`, `The Fiery Lion`, `Master Mage`, `The Wizardly Warrior`, `Master of the Storm`).
* **Dificuldade da Arena:** Usado apenas quando o jogo gera inimigos de arena, sobrevivência ou onda (padrão: `Normal`, opções: `Fácil`, `Normal`, `Difícil`, `Insano`, `Profissional`, `Último`).
* **Alvo de Sobrevivência:** Usado apenas por `Classic Survival`, `Mixed Survival`, `Classic Waves` e `Mixed Waves`; um valor de `0` significa infinito (padrão: `0`, intervalo: `0` a `10000`).
* **Porcentagem de Cura de Sobrevivência:** Após cada surgimento de substituição em Sobrevivência, ou após cada onda limpa em Ondas, os lutadores aliados vivos recuperam esta porcentagem de sua saúde máxima. Usado apenas por `Classic Survival`, `Mixed Survival`, `Classic Waves` e `Mixed Waves` (padrão: `0`, intervalo: `0` a `100`).

# **Predefinições de Personagens**

* **Novice Boxer:** Saúde 52, ataque 1, defesa 0, velocidade 100. Carga: Jab leve, Jab esquerdo, Jab direito, Cruzado esquerdo, Cruzado direito, Contragolpe, Upper, Chute rápido, Rasteira, Cotovelada, Joelhada.
* **Boxer:** Saúde 50, ataque 1, defesa 0, velocidade 100. Carga: Jab leve, Jab direito, Jab esquerdo, Soco no nariz, Soco no queixo, Soco giratório, Soco tonto, Soco estomacal, Golpe de nocaute, Soco surpresa, Soco combo, Barragem de socos, Soco espiritual, Soco de pedra, Chute combo, Chute giratório, Chute voador, Chutes frenéticos, Rajada de golpes, Pancada corporal, Arremesso, Soco contínuo, Briga.
* **The Great Fighter:** Saúde 60, ataque 2, defesa 1, velocidade 100. Carga: Espada de aço, Espada de chama, Espada de icicle, Espada eletrificada, Espada amaldiçoada, Espada animada, Corte rápido, Corte giratório, Chicote com ponta de aço, Martelo de guerra vulcânico, Martelo de guerra antigo, Martelo de guerra de aço, Machado de guerra feérico, Arremesso de machado, Adaga sangrenta, Faca de fogo, Adaga congelada, Faca de icicle, Adaga das sombras, Kunai, Cutelo de carne, cassetete.
* **Fighter Plane:** Saúde 72, ataque 2, defesa 1, velocidade 95. Carga: Canhão de aeronave, Canhão de plasma, Metralhadora de aeronave, Arma laser, Laser ocular, Metralhadora, Espingarda, Rifle de precisão, Granada de mão, Taser pesado, Choque elétrico, Explosão elétrica, Granada disruptora, Bomba dissolvente, Bomba de veneno.
* **Low-Rank Soldier:** Saúde 50, ataque 1, defesa 1, velocidade 100. Carga: Cruzado direito, Metralhadora, Espingarda, Rasteira, Rolamento de combate, Cassetete, Cutelo de carne, Kunai, Conter, Investida, Fugir, Tirar sangue, Contragolpe, Cotovelada, Joelhada, Mergulho suicida.
* **High-Rank Soldier:** Saúde 64, ataque 1, defesa 1, velocidade 100. Carga: Rifle de precisão, Metralhadora, Arma laser, Granada de mão, Canhão de plasma, Rolamento de combate, Armadura de batalha, Forja de batalha, Frenesi, Acelerar, Velocidade, Preso em combate, Sacrifício por poder, Sacrifício por guarda, Sacrifício por velocidade, Negociação mágica, Intimidar.
* **Ghostly Fighter:** Saúde 50, ataque 2, defesa 0, velocidade 105. Carga: Espada de chama, Martelo de guerra antigo, Chicote com ponta de aço, Grito fantasmagórico, Alteração espectral, Rugido, Riso assustador, Comer cérebro, Explodir das sombras, Vórtice dos falecidos, Drenar, Mini drenar, Drenar guarda, Drenar poder, Drenar velocidade, Super drenar, Mordida vampírica, Enfraquecer, Intimidar, Escudo mágico.
* **The Alpha Wolf:** Saúde 55, ataque 3, defesa 0, velocidade 100. Carga: Uivo, Círculo, Mordida, Mordida feroz, Imobilizar, Mandíbula estalando, Garra, Arranhão, Garra de leão, Despedaçar, Tacle de rúgbi, agarrão, Chave de cabeça, Chave de braço, Chave de perna, Conduzir ao chão, Rugido, Conter.
* **The Fiery Lion:** Saúde 60, ataque 2, defesa 0, velocidade 100. Carga: Bola de fogo, Flecha de chama, Esfera flamejante, Brasa, Mordida feroz, Rugido, Garra, Pó ardente, Voleio de bolas de fogo, Faca de fogo, Machado de guerra feérico, Espada de chama, Chuva de faíscas.
* **Master Mage:** Saúde 46, ataque 4, defesa 0, velocidade 105. Carga: Bola de fogo, Bola de gelo, Esfera flamejante, Raio, Flecha de chama, Flecha de raio, Criosfera, Esfera elétrica, Arco longo élfico, Cubo de gelo, Chuva de gelo, Avalanche, Esfera mágica, Força mágica, Escudo mágico, Curar, Cura maior, Esfera divina, Explosão sísmica.
* **The Wizardly Warrior:** Saúde 58, ataque 2, defesa 2, velocidade 100. Carga: Espada de aço, Martelo de guerra antigo, Raio, Flecha de chama, Pancada corporal, Rugido, Machado de guerra feérico, Espada eletrificada, Espada amaldiçoada, Espada animada, Lâmina mágica de proteção, Força mágica, Armadura de batalha, Relâmpago, Corte rápido.
* **Master of the Storm:** Saúde 50, ataque 4, defesa 0, velocidade 100. Carga: Nuvem de tempestade, Relâmpago, Onda de trovão, Esfera elétrica, Choque elétrico, Flecha de raio, Chuva de faíscas, Raio, Explosão elétrica, Explosão sísmica, Avalanche, Bola de gelo, Criosfera, Taser pesado.

# **Diretório de Habilidades**

* Cada habilidade abaixo usa o nome embutido exato do registro empacotado.
* **Aircraft Cannon:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do alvo em 3. Atribuído a: Fighter Plane.
* **Aircraft Machine Gun:** Tem como alvo um lutador inimigo. Efeitos: causa 2-8 de dano; aumenta a velocidade do usuário em 5; aumenta a velocidade do alvo em 5. Atribuído a: Fighter Plane.
* **Ancient Warhammer:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; aumenta o ataque do usuário em 4; reduz a velocidade do usuário em 4. Atribuído a: Ghostly Fighter, The Great Fighter, The Wizardly Warrior.
* **Animated Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; aumenta o ataque do usuário em 3. Atribuído a: The Great Fighter, The Wizardly Warrior.
* **Armlock:** Tem como alvo um lutador inimigo. Efeitos: causa 4-9 de dano; reduz a defesa do alvo em 2. Atribuído a: The Alpha Wolf.
* **Avalanche:** Tem como alvo um lutador inimigo. Efeitos: causa 12-20 de dano; reduz o ataque do usuário em 4; reduz a velocidade do alvo em 10. Atribuído a: Master Mage, Master of the Storm.
* **Axe Throw:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano; reduz o ataque do usuário em 2; reduz a velocidade do alvo em 10. Atribuído a: The Great Fighter.
* **Backhand:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 10. Atribuído a: Low-Rank Soldier, Novice Boxer.
* **Battle Armor:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: aumenta a defesa do alvo em 3; reduz a velocidade do alvo em 2. Atribuído a: High-Rank Soldier, The Wizardly Warrior.
* **Battleforge:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: aumenta o ataque do alvo em 2; aumenta a defesa do alvo em 1. Atribuído a: High-Rank Soldier.
* **Berserk:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3. Atribuído a: High-Rank Soldier.
* **Bite:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano. Atribuído a: The Alpha Wolf.
* **Bloody Dagger:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz o ataque do alvo em 1. Atribuído a: The Great Fighter.
* **Body Slam:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do alvo em 3. Atribuído a: Boxer, The Wizardly Warrior.
* **Brain Eat:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 2; reduz a velocidade do alvo em 15. Atribuído a: Ghostly Fighter.
* **Brawl:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2; aumenta a defesa do usuário em 2; aumenta a velocidade do usuário em 10; aumenta o ataque do alvo em 2; aumenta a defesa do alvo em 2; aumenta a velocidade do alvo em 10. Atribuído a: Boxer.
* **Burning Powder:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 12. Atribuído a: The Fiery Lion.
* **Circle:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; aumenta o ataque do alvo em 3. Atribuído a: The Alpha Wolf.
* **Claw:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a defesa do alvo em 1. Atribuído a: The Alpha Wolf, The Fiery Lion.
* **Combat Roll:** Tem como alvo um lutador inimigo. Efeitos: causa 1-5 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 4; aumenta a velocidade do usuário em 12. Atribuído a: High-Rank Soldier, Low-Rank Soldier.
* **Combo Kick:** Tem como alvo um lutador inimigo. Efeitos: causa 10-16 de dano; reduz o ataque do usuário em 2; reduz a velocidade do usuário em 2. Atribuído a: Boxer.
* **Combo Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 1. Atribuído a: Boxer.
* **Cryosphere:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 25. Atribuído a: Master Mage, Master of the Storm.
* **Cursed Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 5. Atribuído a: The Great Fighter, The Wizardly Warrior.
* **Disruptor Grenade:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; reduz o ataque do alvo em 3; reduz a defesa do alvo em 3; reduz o ataque do usuário em 1. Atribuído a: Fighter Plane.
* **Dissolving Bomb:** Tem como alvo um lutador inimigo. Efeitos: causa 2-10 de dano; reduz o ataque do usuário em 2; reduz a defesa do alvo em 4. Atribuído a: Fighter Plane.
* **Divine Sphere:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 5-9 de saúde; aumenta a defesa do alvo em 2; aumenta a velocidade do alvo em 3. Atribuído a: Master Mage.
* **Dizzying Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a velocidade do alvo em 8. Atribuído a: Boxer.
* **Drain:** Tem como alvo um lutador inimigo. Efeitos: causa 10-12 de dano e cura o usuário em 33% do dano causado. Atribuído a: Ghostly Fighter.
* **Draw Blood:** Tem como alvo um lutador inimigo. Efeitos: causa 1-1 de dano; reduz a velocidade do usuário em 8; reduz a defesa do alvo em 4. Atribuído a: Low-Rank Soldier.
* **Elbow:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano. Atribuído a: Low-Rank Soldier, Novice Boxer.
* **Electric Shock:** Tem como alvo um lutador inimigo. Efeitos: causa 2-6 de dano; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 20. Atribuído a: Fighter Plane, Master of the Storm.
* **Electric Sphere:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a velocidade do alvo em 6. Atribuído a: Master Mage, Master of the Storm.
* **Electrical Explosion:** Tem como alvo um lutador inimigo. Efeitos: causa 14-28 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do alvo em 10. Atribuído a: Fighter Plane, Master of the Storm.
* **Electrified Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 8-10 de dano. Atribuído a: The Great Fighter, The Wizardly Warrior.
* **Elven Longbow:** Tem como alvo um lutador inimigo. Efeitos: causa 5-12 de dano; reduz a velocidade do alvo em 10. Atribuído a: Master Mage.
* **Ember:** Tem como alvo um lutador inimigo. Efeitos: causa 2-5 de dano; reduz o ataque do alvo em 1; reduz a velocidade do alvo em 5. Atribuído a: The Fiery Lion.
* **Explode From The Shadows:** Tem como alvo um lutador inimigo. Efeitos: causa 18-26 de dano; reduz a velocidade do usuário em 35. Atribuído a: Ghostly Fighter.
* **Eye Laser:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; reduz a defesa do alvo em 4; reduz a velocidade do usuário em 4. Atribuído a: Fighter Plane.
* **Ferocious Bite:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: The Alpha Wolf, The Fiery Lion.
* **Fiery War Axe:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2. Atribuído a: The Fiery Lion, The Great Fighter, The Wizardly Warrior.
* **Fire Knife:** Tem como alvo um lutador inimigo. Efeitos: causa 2-14 de dano; reduz a defesa do usuário em 1; aumenta a velocidade do usuário em 6; reduz a defesa do alvo em 1. Atribuído a: The Fiery Lion, The Great Fighter.
* **Fireball:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 8. Atribuído a: Master Mage, The Fiery Lion.
* **Fist Barrage:** Tem como alvo um lutador inimigo. Efeitos: causa 10-18 de dano; reduz o ataque do usuário em 2; reduz a defesa do alvo em 1; reduz a velocidade do alvo em 10. Atribuído a: Boxer.
* **Flame Arrow:** Tem como alvo um lutador inimigo. Efeitos: causa 7-15 de dano; reduz o ataque do usuário em 4; reduz a defesa do alvo em 3. Atribuído a: Master Mage, The Fiery Lion, The Wizardly Warrior.
* **Flame Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz a velocidade do usuário em 7; reduz a defesa do alvo em 3. Atribuído a: Ghostly Fighter, The Fiery Lion, The Great Fighter.
* **Flaming Sphere:** Tem como alvo um lutador inimigo. Efeitos: causa 5-11 de dano; reduz o ataque do usuário em 2; reduz o ataque do alvo em 2. Atribuído a: Master Mage, The Fiery Lion.
* **Flurry Of Blows:** Tem como alvo um lutador inimigo. Efeitos: causa 11-15 de dano; reduz o ataque do usuário em 1; reduz a defesa do usuário em 1; reduz a velocidade do usuário em 5. Atribuído a: Boxer.
* **Flying Kick:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a defesa do usuário em 3; aumenta a velocidade do usuário em 8; reduz a defesa do alvo em 2; aumenta a velocidade do alvo em 2. Atribuído a: Boxer.
* **Frantic Kicking:** Tem como alvo um lutador inimigo. Efeitos: causa 2-12 de dano; reduz a defesa do usuário em 6; aumenta a velocidade do usuário em 20. Atribuído a: Boxer.
* **Frightening Laugh:** Tem como alvo um lutador inimigo. Efeitos: aumenta a defesa do usuário em 1; aumenta a velocidade do usuário em 3; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 10. Atribuído a: Ghostly Fighter.
* **Frozen Dagger:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; reduz a velocidade do alvo em 10. Atribuído a: The Great Fighter.
* **Ghostly Scream:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz o ataque do alvo em 3; aumenta a defesa do alvo em 3. Atribuído a: Ghostly Fighter.
* **Grapple:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano; reduz a velocidade do usuário em 10; reduz a velocidade do alvo em 10. Atribuído a: The Alpha Wolf.
* **Greater Heal:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 12-18 de saúde; aumenta a velocidade do alvo em 2. Atribuído a: Master Mage.
* **Ground'n'pound:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano; reduz a defesa do usuário em 5; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 5. Atribuído a: The Alpha Wolf.
* **Guard Drain:** Tem como alvo um lutador inimigo. Efeitos: aumenta a defesa do usuário em 3; reduz a defesa do alvo em 3. Atribuído a: Ghostly Fighter.
* **Gutbuster Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 10-14 de dano; reduz o ataque do alvo em 4; reduz a defesa do usuário em 1. Atribuído a: Boxer.
* **Hand Grenade:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz a defesa do alvo em 2. Atribuído a: Fighter Plane, High-Rank Soldier.
* **Haste:** Tem como alvo apenas o usuário. Efeitos: aumenta a velocidade do usuário em 12. Atribuído a: High-Rank Soldier.
* **Headlock:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; aumenta a defesa do usuário em 3; reduz a velocidade do usuário em 1; reduz a defesa do alvo em 4; reduz a velocidade do alvo em 8. Atribuído a: The Alpha Wolf.
* **Heal:** Tem como alvo um lutador aliado, incluindo o usuário. Efeitos: restaura 8-14 de saúde. Atribuído a: Master Mage.
* **Heavy Taser:** Tem como alvo um lutador inimigo. Efeitos: causa 7-11 de dano; reduz a velocidade do alvo em 12; reduz o ataque do alvo em 2; reduz a velocidade do usuário em 3. Atribuído a: Fighter Plane, Master of the Storm.
* **Howl:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 2. Atribuído a: The Alpha Wolf.
* **Ice Ball:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano. Atribuído a: Master Mage, Master of the Storm.
* **Ice Cube:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano; aumenta o ataque do usuário em 3; aumenta a defesa do usuário em 3. Atribuído a: Master Mage.
* **Icicle Knife:** Tem como alvo um lutador inimigo. Efeitos: causa 2-5 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 5. Atribuído a: The Great Fighter.
* **Icicle Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; reduz o ataque do usuário em 1; reduz a velocidade do alvo em 7. Atribuído a: The Great Fighter.
* **Intimidate:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz o ataque do alvo em 3. Atribuído a: Ghostly Fighter, High-Rank Soldier.
* **Jaw Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; reduz a defesa do alvo em 2. Atribuído a: Boxer.
* **Knee:** Tem como alvo um lutador inimigo. Efeitos: causa 3-6 de dano; reduz o ataque do alvo em 2. Atribuído a: Low-Rank Soldier, Novice Boxer.
* **Knockout Hit:** Tem como alvo um lutador inimigo. Efeitos: causa 10-30 de dano; reduz o ataque do usuário em 5; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 30. Atribuído a: Boxer.
* **Kunai:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; aumenta a velocidade do usuário em 4; reduz a defesa do alvo em 3. Atribuído a: Low-Rank Soldier, The Great Fighter.
* **Laser Gun:** Tem como alvo um lutador inimigo. Efeitos: causa 5-18 de dano; reduz a velocidade do usuário em 6. Atribuído a: Fighter Plane, High-Rank Soldier.
* **Left Hook:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Novice Boxer.
* **Left Jab:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Boxer, Novice Boxer.
* **Leglock:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano; reduz a defesa do alvo em 4. Atribuído a: The Alpha Wolf.
* **Light Jab:** Tem como alvo um lutador inimigo. Efeitos: causa 3-8 de dano. Atribuído a: Boxer, Novice Boxer.
* **Lightning Arrow:** Tem como alvo um lutador inimigo. Efeitos: causa 4-8 de dano; reduz a defesa do alvo em 1. Atribuído a: Master Mage, Master of the Storm.
* **Lightning Bolt:** Tem como alvo um lutador inimigo. Efeitos: causa 8-15 de dano; reduz o ataque do usuário em 3; reduz a velocidade do alvo em 10. Atribuído a: Master Mage, Master of the Storm, The Wizardly Warrior.
* **Lions Claw:** Tem como alvo um lutador inimigo. Efeitos: causa 10-13 de dano; aumenta o ataque do usuário em 3; reduz a velocidade do alvo em 4. Atribuído a: The Alpha Wolf.
* **Locked In Combat:** Tem como alvo um lutador inimigo. Efeitos: causa 4-6 de dano; aumenta o ataque do usuário em 3; aumenta a velocidade do usuário em 10; aumenta o ataque do alvo em 3; aumenta a velocidade do alvo em 10. Atribuído a: High-Rank Soldier.
* **Machine Gun:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta a velocidade do usuário em 5. Atribuído a: Fighter Plane, High-Rank Soldier, Low-Rank Soldier.
* **Magic Deal:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; aumenta o ataque do alvo em 3. Atribuído a: High-Rank Soldier.
* **Magic Shield:** Tem como alvo apenas o usuário. Efeitos: aumenta a defesa do usuário em 4. Atribuído a: Ghostly Fighter, Master Mage.
* **Magic Sphere:** Tem como alvo um lutador inimigo. Efeitos: causa 7-9 de dano. Atribuído a: Master Mage.
* **Magic Strength:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 4. Atribuído a: Master Mage, The Wizardly Warrior.
* **Maul:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a velocidade do usuário em 12; reduz o ataque do alvo em 2; reduz a defesa do alvo em 3. Atribuído a: The Alpha Wolf.
* **Meat Cleaver:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano e cura o usuário em 30% do dano causado. Atribuído a: Low-Rank Soldier, The Great Fighter.
* **Mini Drain:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano e cura o usuário em 25% do dano causado. Atribuído a: Ghostly Fighter.
* **Nightstick:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 8. Atribuído a: Low-Rank Soldier, The Great Fighter.
* **Nose Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 10-12 de dano. Atribuído a: Boxer.
* **Pin Down:** Tem como alvo um lutador inimigo. Efeitos: causa 10-13 de dano; reduz a defesa do usuário em 5; reduz a velocidade do alvo em 20. Atribuído a: The Alpha Wolf.
* **Plasma Cannon:** Tem como alvo um lutador inimigo. Efeitos: causa 16-24 de dano; reduz a defesa do usuário em 6. Atribuído a: Fighter Plane, High-Rank Soldier.
* **Poison Bomb:** Tem como alvo um lutador inimigo. Efeitos: causa 1-10 de dano; reduz o ataque do usuário em 2; reduz a velocidade do alvo em 12. Atribuído a: Fighter Plane.
* **Power Drain:** Tem como alvo um lutador inimigo. Efeitos: aumenta o ataque do usuário em 3; reduz o ataque do alvo em 3. Atribuído a: Ghostly Fighter.
* **Pummel:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; aumenta a defesa do usuário em 3; reduz a velocidade do usuário em 5; reduz a defesa do alvo em 3; aumenta a velocidade do alvo em 3. Atribuído a: Boxer.
* **Quick Slash:** Tem como alvo um lutador inimigo. Efeitos: causa 1-7 de dano; aumenta a velocidade do usuário em 8. Atribuído a: The Great Fighter, The Wizardly Warrior.
* **Rain Of Ice:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 3. Atribuído a: Master Mage.
* **Rain Of Sparks:** Tem como alvo um lutador inimigo. Efeitos: causa 12-16 de dano; reduz o ataque do usuário em 4. Atribuído a: Master of the Storm, The Fiery Lion.
* **Restrain:** Tem como alvo um lutador inimigo. Efeitos: causa 4-7 de dano; reduz a velocidade do alvo em 12. Atribuído a: Low-Rank Soldier, The Alpha Wolf.
* **Rev Up:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 2; reduz a defesa do usuário em 2; aumenta a velocidade do usuário em 5. Atribuído a: High-Rank Soldier.
* **Right Hook:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Low-Rank Soldier, Novice Boxer.
* **Right Jab:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano. Atribuído a: Boxer, Novice Boxer.
* **Roar:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 3; reduz a velocidade do usuário em 5. Atribuído a: Ghostly Fighter, The Alpha Wolf, The Fiery Lion, The Wizardly Warrior.
* **Rugby Tackle:** Tem como alvo um lutador inimigo. Efeitos: causa 8-13 de dano; reduz a defesa do alvo em 5; aumenta a velocidade do alvo em 5. Atribuído a: The Alpha Wolf.
* **Run Away:** Tem como alvo apenas o usuário. Efeitos: reduz o ataque do usuário em 5; reduz a defesa do usuário em 5; aumenta a velocidade do usuário em 20. Atribuído a: Low-Rank Soldier.
* **Rush In:** Tem como alvo apenas o usuário. Efeitos: aumenta o ataque do usuário em 4; reduz a defesa do usuário em 5; aumenta a velocidade do usuário em 15. Atribuído a: Low-Rank Soldier.
* **Sacrifice For Guard:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta a defesa do usuário em 5; aumenta a defesa do alvo em 5. Atribuído a: High-Rank Soldier.
* **Sacrifice For Power:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta o ataque do usuário em 5; aumenta o ataque do alvo em 5. Atribuído a: High-Rank Soldier.
* **Sacrifice For Speed:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; aumenta a velocidade do usuário em 20; aumenta a velocidade do alvo em 20. Atribuído a: High-Rank Soldier.
* **Scratch:** Tem como alvo um lutador inimigo. Efeitos: causa 3-9 de dano. Atribuído a: The Alpha Wolf.
* **Seismic Blast:** Tem como alvo um lutador inimigo. Efeitos: causa 18-22 de dano; reduz a velocidade do usuário em 10; reduz a defesa do alvo em 4. Atribuído a: Master Mage, Master of the Storm.
* **Shadowknife:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 6. Atribuído a: The Great Fighter.
* **Shotgun:** Tem como alvo um lutador inimigo. Efeitos: causa 6-16 de dano; reduz o ataque do usuário em 2. Atribuído a: Fighter Plane, Low-Rank Soldier.
* **Snap Kick:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; reduz a velocidade do usuário em 12; reduz a defesa do alvo em 4; reduz a velocidade do alvo em 8. Atribuído a: Novice Boxer.
* **Snapping Jaw:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 3. Atribuído a: The Alpha Wolf.
* **Sniper Rifle:** Tem como alvo um lutador inimigo. Efeitos: causa 12-15 de dano; reduz a velocidade do usuário em 8. Atribuído a: Fighter Plane, High-Rank Soldier.
* **Spectral Alteration:** Tem como alvo um lutador inimigo. Efeitos: causa 8-10 de dano; aumenta o ataque do usuário em 4; aumenta a velocidade do usuário em 4; aumenta o ataque do alvo em 4; aumenta a velocidade do alvo em 4. Atribuído a: Ghostly Fighter.
* **Speed Drain:** Tem como alvo um lutador inimigo. Efeitos: aumenta a velocidade do usuário em 12; reduz a velocidade do alvo em 12. Atribuído a: Ghostly Fighter.
* **Spinning Cut:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; reduz o ataque do usuário em 1; aumenta a velocidade do usuário em 5. Atribuído a: The Great Fighter.
* **Spinning Kick:** Tem como alvo um lutador inimigo. Efeitos: causa 13-16 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 5. Atribuído a: Boxer.
* **Spinning Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 15-18 de dano; reduz o ataque do usuário em 3; reduz a defesa do usuário em 2; aumenta a velocidade do usuário em 3; reduz a velocidade do alvo em 6. Atribuído a: Boxer.
* **Spirit Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 8-12 de dano; aumenta o ataque do usuário em 2; reduz o ataque do alvo em 2; reduz a velocidade do alvo em 4. Atribuído a: Boxer.
* **Steel Sword:** Tem como alvo um lutador inimigo. Efeitos: causa 5-9 de dano; aumenta o ataque do usuário em 2; aumenta o ataque do alvo em 2. Atribuído a: The Great Fighter, The Wizardly Warrior.
* **Steel Warhammer:** Tem como alvo um lutador inimigo. Efeitos: causa 9-13 de dano. Atribuído a: The Great Fighter.
* **Steel-tipped Whip:** Tem como alvo um lutador inimigo. Efeitos: causa 6-12 de dano; aumenta o ataque do usuário em 1; reduz a defesa do alvo em 2; reduz a velocidade do alvo em 5. Atribuído a: Ghostly Fighter, The Great Fighter.
* **Stone Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 11-15 de dano; aumenta a defesa do usuário em 2; reduz a velocidade do usuário em 5; reduz a velocidade do alvo em 3. Atribuído a: Boxer.
* **Sucker Punch:** Tem como alvo um lutador inimigo. Efeitos: causa 9-12 de dano; reduz a defesa do alvo em 2. Atribuído a: Boxer.
* **Suicide Dive:** Tem como alvo um lutador inimigo. Efeitos: causa 20-30 de dano; reduz o ataque do usuário em 4; reduz a defesa do usuário em 4; reduz a velocidade do alvo em 30. Atribuído a: Low-Rank Soldier.
* **Super Drain:** Tem como alvo um lutador inimigo. Efeitos: causa 5-8 de dano e cura o usuário em 50% do dano causado. Atribuído a: Ghostly Fighter.
* **Throw:** Tem como alvo um lutador inimigo. Efeitos: causa 5-10 de dano; reduz o ataque do usuário em 3; reduz o ataque do alvo em 3; reduz a defesa do alvo em 3. Atribuído a: Boxer.
* **Thunder Cloud:** Tem como alvo um lutador inimigo. Efeitos: reduz a defesa do usuário em 3; reduz a velocidade do usuário em 10; reduz a defesa do alvo em 3; reduz a velocidade do alvo em 20. Atribuído a: Master of the Storm.
* **Thunder Wave:** Tem como alvo um lutador inimigo. Efeitos: reduz o ataque do usuário em 3; reduz a defesa do usuário em 3; reduz a velocidade do usuário em 10; reduz a velocidade do alvo em 30. Atribuído a: Master of the Storm.
* **Thunderbolt:** Tem como alvo um lutador inimigo. Efeitos: causa 6-9 de dano; reduz a velocidade do alvo em 5. Atribuído a: Master of the Storm, The Wizardly Warrior.
* **Trip:** Tem como alvo um lutador inimigo. Efeitos: causa 4-9 de dano; reduz o ataque do usuário em 2; aumenta a velocidade do usuário em 4; aumenta o ataque do alvo em 2; aumenta a velocidade do alvo em 1. Atribuído a: Low-Rank Soldier, Novice Boxer.
* **Uppercut:** Tem como alvo um lutador inimigo. Efeitos: causa 8-14 de dano; aumenta o ataque do usuário em 2; aumenta a defesa do usuário em 2; reduz o ataque do alvo em 2; reduz a defesa do alvo em 2. Atribuído a: Novice Boxer.
* **Vampiric Bite:** Tem como alvo um lutador inimigo. Efeitos: causa 7-10 de dano e cura o usuário em 60% do dano causado. Atribuído a: Ghostly Fighter.
* **Volcanic Warhammer:** Tem como alvo um lutador inimigo. Efeitos: causa 10-15 de dano; reduz a defesa do alvo em 5. Atribuído a: The Great Fighter.
* **Volley Of Fireballs:** Tem como alvo um lutador inimigo. Efeitos: causa 12-16 de dano; aumenta o ataque do usuário em 2. Atribuído a: The Fiery Lion.
* **Vortex Of The Deceased:** Tem como alvo um lutador inimigo. Efeitos: causa 9-15 de dano; reduz o ataque do usuário em 2; reduz a defesa do usuário em 2; reduz a velocidade do usuário em 2. Atribuído a: Ghostly Fighter.
* **Warding Spellblade:** Tem como alvo um lutador inimigo. Efeitos: causa 6-10 de dano; aumenta a defesa do usuário em 1; reduz o ataque do alvo em 1. Atribuído a: The Wizardly Warrior.
* **Weaken:** Tem como alvo um lutador inimigo. Efeitos: reduz o ataque do alvo em 3; reduz a velocidade do alvo em 5. Atribuído a: Ghostly Fighter.

# **Atalhos de Teclado**

* **S:** Lê o status da batalha.
* **Shift+S:** Abre o status detalhado da batalha como uma lista.
* **V:** Lê o plantel de combate completo. Isso fica bloqueado durante a seleção de lutadores.
* **A:** Em modos baseados em equipe, visualiza apenas os lutadores aliados vivos.
* **E:** Em modos baseados em equipe, visualiza apenas os lutadores inimigos vivos.
* **U:** Anula a escolha de lutador mais recente durante a seleção.
* **D:** Termina a seleção em modos ilimitados.
* **T:** Ouve de quem é o turno ou se o jogo ainda está na seleção.
