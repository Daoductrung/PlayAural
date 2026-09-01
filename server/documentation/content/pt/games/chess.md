**Xadrez**

Xadrez é um duelo de cálculo, tempo e planejamento de longo prazo em um campo de batalha de 8 por 8. Dois jogadores comandam exércitos opostos, cada um tentando romper a posição, defender seu rei e aplicar o xeque-mate antes que o outro lado possa fazer o mesmo.

**Jogabilidade**

Cada lado começa com dezesseis peças. As brancas movem primeiro, e então os jogadores alternam turnos pelo resto do jogo.

O tabuleiro é uma grade de 8 por 8. No seu turno, você escolhe uma de suas próprias peças e depois escolhe uma casa de destino legal.

Você também pode digitar um movimento diretamente. A entrada aceita formatos comuns de xadrez, incluindo notação de coordenadas como `e2e4`, notação algébrica como `Nf3` ou `Rae1`, roque como `O-O` ou `O-O-O`, e promoção como `e8=Q`.

* Os peões movem-se para frente, capturam na diagonal e podem avançar duas casas a partir de sua fileira inicial.
* Os cavalos movem-se em formato de L e podem saltar sobre outras peças.
* Os bispos movem-se na diagonal através de qualquer número de casas abertas.
* As torres movem-se horizontalmente ou verticalmente através de qualquer número de casas abertas.
* As damas combinam o movimento de torre e bispo.
* Os reis movem-se uma casa em qualquer direção.

Você nunca pode fazer um movimento que deixe seu próprio rei em xeque. Se o seu rei estiver sob ataque, você deve responder a essa ameaça imediatamente movendo o rei, bloqueando a linha de ataque ou capturando a peça atacante.

Se um relógio estiver ativado, apenas o relógio do jogador ativo corre. Após a conclusão de um movimento legal, qualquer acréscimo do controle de tempo selecionado é adicionado ao tempo restante desse jogador. Se uma oferta de empate ou pedido de desfazer estiver aguardando resposta, o relógio é pausado até que essa resposta seja resolvida.

**Mecânicas Especiais**

* **Roque:** O roque é legal se o rei e a torre envolvidos não se moveram, as casas entre eles estão vazias, o rei não está atualmente em xeque e não passa por nem termina em uma casa sob ataque.
* **En passant:** Se um peão oposto avança duas casas em um único movimento e termina ao lado do seu peão, você pode capturá-lo imediatamente como se ele tivesse se movido apenas uma casa.
* **Promoção:** Quando um peão alcança a última fileira, ele deve ser promovido a uma dama, torre, bispo ou cavalo.
* **Xeque-mate:** O jogo termina imediatamente quando um jogador está em xeque e não tem nenhum movimento legal.
* **Afogamento:** O jogo empata se o lado a mover não estiver em xeque, mas não tiver nenhum movimento legal.
* **Material insuficiente:** O jogo empata automaticamente se nenhum dos lados tiver material suficiente para forçar o xeque-mate.
* **Tempo esgotado:** Se o relógio de um jogador chega a zero, esse jogador perde por tempo, a menos que o oponente não tenha material suficiente para jamais dar xeque-mate, caso em que o jogo empata.

**Empates, Reivindicações e Acordos**

O xadrez inclui várias maneiras para um jogo terminar em empate.

* **Tríplice repetição:** Se a mesma posição ocorre três vezes com o mesmo lado para mover e os mesmos direitos, o jogo pode ser empatado.
* **Quíntupla repetição:** Se a mesma posição ocorre cinco vezes, o jogo empata automaticamente.
* **Regra dos cinquenta movimentos:** Se cada jogador fez cinquenta movimentos consecutivos sem nenhum movimento de peão ou captura, o jogo pode ser empatado.
* **Regra dos setenta e cinco movimentos:** Se cada jogador fez setenta e cinco movimentos consecutivos sem nenhum movimento de peão ou captura, o jogo empata automaticamente, a menos que o movimento final tenha dado xeque-mate.
* **Oferta de empate:** Se as ofertas de empate estiverem ativadas para a mesa, um jogador pode oferecer um empate após ambos os jogadores terem feito pelo menos um movimento, e o oponente pode aceitar ou recusar.
* **Pedido para desfazer:** Se os pedidos para desfazer estiverem ativados para a mesa, um jogador pode pedir para retomar o movimento mais recente e o oponente pode aceitar ou recusar.

O anfitrião decide se a tríplice repetição e a regra dos cinquenta movimentos são tratadas automaticamente ou devem ser reivindicadas pelo jogador que está na vez. A quíntupla repetição e a regra dos setenta e cinco movimentos são sempre automáticas.

**Opções Personalizáveis**

* **Controle de Tempo:** Escolha a predefinição de relógio para ambos os jogadores (padrão `Untimed`, opções: `Bullet 1+0`, `Bullet 2+1`, `Blitz 3+0`, `Blitz 3+2`, `Blitz 5+0`, `Rapid 10+0`, `Rapid 10+5`, `Classical 30+0`).
* **Tratamento de Empate:** Escolha se a tríplice repetição e a regra dos cinquenta movimentos são automáticas ou devem ser reivindicadas. A quíntupla repetição e a regra dos setenta e cinco movimentos são sempre automáticas (padrão `Automatic`, opções: `Automatic` ou `Claim required`).
* **Permitir Ofertas de Empate:** Se os jogadores podem oferecer empates durante o jogo (padrão `On`).
* **Permitir Pedidos para Desfazer:** Se os jogadores podem pedir aos seus oponentes para retomar movimentos (padrão `Off`).

**Atalhos de Teclado**

* **Enter:** Selecionar a casa destacada no tabuleiro.
* **V:** Ler o tabuleiro.
* **C:** Verificar o status atual do jogo.
* **M:** Digitar um movimento diretamente.
* **F:** Inverter a orientação do tabuleiro.
* **Shift+T:** Verificar ambos os relógios.
* **Shift+C:** Reivindicar um empate quando a posição atual se qualificar.
* **Shift+D:** Oferecer um empate.
* **Shift+U:** Solicitar um desfazer.
* **Y:** Aceitar uma oferta de empate ou pedido para desfazer.
* **N:** Recusar uma oferta de empate ou pedido para desfazer.
