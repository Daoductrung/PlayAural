**Senet**

Senet é um antigo jogo de tabuleiro egípcio, muito provavelmente o jogo de tabuleiro mais antigo ainda jogado hoje, com origens que remontam a mais de cinco mil anos. Tabuleiros foram encontrados em túmulos em todo o Egito, e o faraó Tutancâmon foi enterrado com vários próprios. Dois jogadores correm com cinco peças cada ao longo de uma pista em forma de S de trinta casas, lançando gravetos em vez de dados e tentando retirar todas as suas peças do tabuleiro antes que o oponente possa fazê-lo.

Senet é jogado por **exatamente dois jogadores**.

**Posição Inicial**

Cada jogador começa com cinco peças, colocadas alternadamente ao longo das primeiras dez casas:

* Jogador 1: casas 1, 3, 5, 7 e 9.
* Jogador 2: casas 2, 4, 6, 8 e 10.

As duas funções são atribuídas aleatoriamente no início do jogo, mas o Jogador 1 sempre lança primeiro.

**Layout do Tabuleiro**

O tabuleiro é uma grade de três linhas por dez colunas. As peças percorrem um caminho em forma de S que percorre a extensão de cada linha por vez:

* Linha 1 (superior): casas 1 a 10, da esquerda para a direita.
* Linha 2 (meio): casas 11 a 20, da direita para a esquerda.
* Linha 3 (inferior): casas 21 a 30, da esquerda para a direita.

Ambos os jogadores viajam na mesma direção, da casa 1 em direção à casa 30. Como o tabuleiro é organizado como uma grade física, a linha do meio é lida ao contrário: a casa 20 fica na borda esquerda e a casa 11 na direita, refletindo o vai e vem do caminho.

**Lançando os Gravetos**

O Senet usa quatro gravetos de lançamento em vez de dados. Cada graveto tem um lado marcado e um lado em branco, e seu movimento é decidido por quantos caem com o lado marcado para cima. No seu turno, pressione Enter em qualquer casa para lançar:

* **1 marcado:** mova 1 casa e lance novamente (lançamento bônus).
* **2 marcados:** mova 2 casas.
* **3 marcados:** mova 3 casas.
* **4 marcados:** mova 4 casas e lance novamente (lançamento bônus).
* **0 marcado (todos em branco):** mova 5 casas e lance novamente (lançamento bônus).

Uma rolagem de 1, 4 ou 5 rende um lançamento bônus: você faz seu movimento para a rolagem atual e imediatamente lança novamente. Os lançamentos bônus se encadeiam, de modo que uma sequência de rolagens que concedem bônus pode levar uma peça longe em um único turno.

**Movendo as Peças**

Após o lançamento, selecione uma de suas próprias peças para movê-la. Cada peça tem no máximo um destino legal para uma dada rolagem, então selecionar uma peça a move direto para lá. As regras de movimento são:

* As peças só se movem para a frente, em direção à casa 30.
* Você pode passar por cima de peças que estão em seu caminho.
* Você não pode chegar a uma casa que já contenha uma de suas próprias peças.
* Se você chegar a uma casa que contenha uma única peça oponente, as duas peças **trocam de lugar**: a sua assume o destino e a peça do oponente recua para a casa que você deixou.
* Se você não tiver nenhum movimento legal para uma rolagem, você perde o movimento, mas ainda recebe qualquer lançamento bônus que a rolagem tenha rendido.

**Proteção e Bloqueio**

Duas ou mais de suas peças em casas adjacentes formam um grupo protegido. Peças protegidas **não podem ser capturadas** — um oponente não pode pousar e, portanto, não pode trocar de lugar com uma peça que tenha um vizinho de sua própria cor.

Uma sequência de três ou mais peças oponentes consecutivas forma uma parede intransponível: você não pode passar por cima de tal formação, e qualquer movimento que leve uma peça através dela é ilegal.

**Casas Especiais**

Seis casas têm significado especial:

* **Casa 15 — Casa do Renascimento:** a casa segura para a qual as peças enviadas de volta da Casa da Água retornam.
* **Casa 26 — Casa da Felicidade:** cada peça **deve** pousar aqui a caminho de casa. Você não pode passar por cima da casa 26, portanto, uma rolagem que leve uma peça além dela sem parar não é um movimento legal. Uma vez que uma peça tenha descansado na casa 26, ela se move normalmente em um turno posterior. Esta casa é segura contra captura.
* **Casa 27 — Casa da Água:** pousar aqui é infortúnio. A peça é enviada direto de volta para a Casa do Renascimento (casa 15). Se a casa 15 estiver ocupada, a peça vai para a casa vazia mais próxima antes dela. Mesmo uma peça que chega trocando de lugar com a água é enviada de volta desta forma.
* **Casa 28 — Casa das Três Verdades:** uma peça que chega aqui fica trancada com segurança no lugar e só pode sair retirando-se com uma rolagem exata de **3**.
* **Casa 29 — Casa de Ré-Atum:** igual à casa 28, mas a peça se retira apenas com uma rolagem exata de **2**.
* **Casa 30 — Casa de Hórus:** uma peça se retira com uma rolagem exata de **1**. Ela também sai automaticamente no início do seu lançamento se você não tiver mais peças na primeira linha. Ao contrário das casas protegidas antes dela, esta casa final não é segura contra captura.

As casas especiais marcadas da casa 15 até a casa 29 são protegidas contra captura. A casa 30 é a casa final e ainda pode ser alvo de troca de lugar pelo oponente.

**Retirada do Tabuleiro (Bearing Off)**

As peças deixam o tabuleiro apenas a partir das três casas finais, e cada uma exige sua rolagem exata:

* Da casa 28: exatamente 3.
* Da casa 29: exatamente 2.
* Da casa 30: exatamente 1, ou automaticamente no início do seu lançamento quando sua primeira linha estiver limpa.

Nenhuma peça pode se retirar de nenhuma outra casa. As peças devem alcançar essas casas finais e esperar lá pelo lançamento certo.

**Vitória**

O primeiro jogador a retirar todas as cinco peças do tabuleiro vence o jogo.

**Opções do Jogo**

* **Dificuldade do Bot:** Como os bots escolhem seus movimentos (padrão Simples, opções: Simples, onde o bot avalia seus movimentos com uma heurística, ou Aleatório, onde o bot joga um movimento legal aleatório).

**Atalhos de Teclado**

* **Enter (em qualquer casa da grade):** Lança os gravetos ou move a peça selecionada durante a fase de movimento.
* **Ctrl+Setas Para Baixo ou Para a Direita:** Percorre para a frente através de suas peças que têm um movimento legal.
* **Ctrl+Setas Para Cima ou Para a Esquerda:** Percorre para trás através de suas peças que têm um movimento legal.
* **E:** Lê o status do jogo — peças retiradas, a fase atual e a rolagem atual.
* **C:** Lê o resultado do lançamento atual dos gravetos.
* **S:** Lê a pontuação, a contagem de peças que cada jogador retirou.
* **Shift+S:** Abre a visualização de pontuação detalhada.
* **T:** Conferir de quem é a vez.

**Dicas de Estratégia**

* **Esvazie a Casa da Felicidade cedo.** Cada peça deve parar na casa 26, então é um gargalo. Passar peças por ela mais cedo deixa você com mais liberdade depois.
* **Fique longe da água.** A casa 27 arremessa uma peça todo o caminho de volta para a casa 15. Planeje em torno dela, especialmente para peças que já viajaram muito.
* **Avance em pares.** Duas peças adjacentes protegem uma à outra contra captura. Mover peças juntas, em vez de espalhá-las, é mais seguro onde o oponente espreita por perto.
* **Gaste os lançamentos bônus com sabedoria.** Rolagens de 1, 4 e 5 concedem lançamentos extras, e uma longa cadeia pode ser decisiva. Dentro de uma cadeia, pondere qual peça ganha mais com cada rolagem.
* **Construa uma parede.** Três ou mais peças em uma linha são intransponíveis. Um bloqueio no lugar certo pode deixar seu oponente preso por vários turnos.
* **Troque de lugar com intenção.** Uma captura envia a peça do oponente de volta para onde a sua estava. Quanto mais atrás sua peça estivesse, mais a troca os machuca — e mais você deve evitar deixar peças sozinhas onde o oponente lucraria com a mesma troca.
* **O final de jogo é um jogo de rolagens exatas.** As casas 28, 29 e 30 precisam cada uma de um lançamento específico para retirar. Manter peças em diferentes casas trancadas permite que você coloque quase qualquer rolagem para uso.
