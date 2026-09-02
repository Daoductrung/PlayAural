**Ludo**



Ludo é o jogo de corrida do PlayAural baseado no formato tradicional de cruz e círculo de quatro cores. Cada jogador controla quatro peões, tira-os do pátio, move-os pela pista externa compartilhada e, em seguida, guia-os para uma pista de chegada particular. O primeiro jogador a terminar todos os quatro peões vence o jogo imediatamente.



**Jogabilidade**



O Ludo aceita de 2 a 4 jogadores. No início do jogo, cada jogador recebe uma cor na ordem de assento: Vermelho, Azul, Verde e depois Amarelo. Cada jogador começa com quatro peões em seu próprio pátio.



No seu turno, primeiro você rola o dado.



* Se nenhum peão puder se mover com essa rolagem, seu turno termina automaticamente após o anúncio da rolagem.

* Se exatamente um peão puder se mover, o jogo move esse peão automaticamente.

* Se vários peões puderem se mover, o jogo solicita que você escolha qual peão mover.



A exibição de pontuação rastreia quantos dos quatro peões de cada jogador já chegaram em casa, mas este ainda é um jogo de corrida única em vez de uma partida de várias rodadas. Assim que um jogador leva todos os quatro peões para casa, esse jogador vence.



**Regras de Movimento**



* **Sair do pátio:** Um peão só pode sair do pátio com uma rolagem de 6. Quando isso acontece, ele entra no tabuleiro na casa de partida dessa cor.

* **Pista externa:** Assim que um peão está no tabuleiro, ele se move para frente ao redor da pista compartilhada de 52 casas de acordo com a rolagem do dado. A pista dá a volta, permitindo que os peões passem pelo lado inicial e continuem em direção à casa.

* **Entrada na reta final:** Cada cor tem seu próprio ponto de entrada perto do final de uma volta completa. Quando um peão passa por esse ponto de entrada, ele deixa a pista compartilhada e entra em sua pista particular de chegada.

* **Reta final:** A pista de chegada tem 6 casas de comprimento. Um peão só pode se mover na pista se a rolagem não ultrapassar o final.

* **Terminar:** Um peão que chega ao final da pista de chegada é marcado como finalizado e não se move mais.



**Casas Seguras e Pilhas**



Determinadas casas são seguras e não podem ser usadas para capturas. Nesta implementação, as casas 9, 22, 35 e 48 são sempre seguras.



O anfitrião também pode ativar uma opção que torna todas as quatro casas de partida coloridas seguras. Quando essa opção está ativada, entrar em uma casa de partida é protegido mesmo que um peão oponente já esteja lá.



Os peões têm permissão para se empilhar na mesma casa. O empilhamento pode acontecer com seus próprios peões, com peões oponentes em casas seguras ou em outras situações onde nenhuma captura ocorre.



**Capturas**



Se o seu peão parar em uma casa insegura da pista externa ocupada por um oponente, você captura o peão daquele oponente e o manda de volta para o pátio.



Se essa casa contiver uma pilha de peões de um oponente, você captura todos os peões daquele oponente na casa de uma só vez. Seus próprios peões nunca são capturados pelo seu próprio movimento, mesmo que você pare em uma casa onde seus próprios peões já estejam empilhados.



Capturas não acontecem dentro da pista de chegada e não acontecem em casas seguras.



**Rolando um 6**



Rolar um 6 normalmente concede um turno extra após a resolução do movimento.



No entanto, o anfitrião pode limitar quantos 6s podem ser rolados consecutivamente na mesma sequência de turnos. Por padrão, o limite é 3.



Se o limite for atingido, a penalidade é severa: todos os movimentos feitos durante essa sequência de turnos são desfeitos, a cadeia de turnos extras termina e o jogo passa para o próximo jogador. Definir o limite como 0 desativa essa penalidade completamente.



**Pontuação**



O Ludo no PlayAural usa pontuação de corrida direta:



* O primeiro jogador a terminar todos os quatro peões vence o jogo.

* Durante o jogo, o sistema de pontuação rastreia quantos peões cada jogador já levou para casa.

* Não há pontos de rodada, totais de pontos de pip ou pontuações cumulativas entre as corridas na implementação atual.



**Opções Personalizáveis**



O anfitrião pode ajustar as seguintes opções antes de o jogo começar:



* **Máximo de 6s consecutivos:** O número de 6s que um jogador pode rolar em sequência antes que a penalidade de reversão seja aplicada. Definir como 0 desativa a penalidade (padrão 3, intervalo de 0 a 5).

* **Casas iniciais seguras:** Quando ativado, todas as casas de partida coloridas contam como casas seguras e não podem ser usadas para capturas. Padrão: Ligado.



**Atalhos de Teclado**



* **R:** Rolar o dado.

* **1-4:** Mover o peão de 1 a 4 quando o jogo pedir para você escolher um peão.

* **V:** Ler o status completo do tabuleiro, incluindo a cor de cada jogador, a contagem de peões finalizados e a localização de cada peão.

* **T:** Verificar de quem é o turno.

* **S:** Verificar a exibição da pontuação atual.
