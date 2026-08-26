**Color Game**

Color Game é a adaptação da PlayAural do tradicional jogo de apostas com dados de cores *perya* das Filipinas. Todos apostam em uma ou mais cores, três dados de cores são lançados juntos, e cada aposta de cor é paga estritamente de acordo com quantos dados mostraram essa mesma cor.

**Jogabilidade**

* O tabuleiro possui **6 cores de apostas**: vermelho, azul, amarelo, verde, branco e laranja.
* Cada rodada usa **3 dados de cores**.
* Cada dado contém as mesmas 6 cores, portanto uma cor pode aparecer **0, 1, 2 ou 3 vezes** em uma rodada.
* No início da partida, cada jogador recebe uma **bancada inicial** (bankroll) com base na configuração do anfitrião.
* Uma rodada começa com uma **fase de apostas compartilhada**. Esta não é uma vez estrita de um jogador por vez. Todos os jogadores ativos podem fazer ou alterar apostas durante a mesma janela de cronômetro.
* Um **jogador ativo** significa um jogador cuja bancada ainda pode cobrir a Aposta Mínima da mesa.
* Durante as apostas, você pode colocar fichas em **uma cor** ou dividir o seu total entre **várias cores**.
* Cada aposta de cor é tratada de forma independente. Você não está escolhendo uma única cor vencedora geral para toda a rodada.
* Selecionar uma cor abre um **menu de aposta rápida**. Ele oferece valores predefinidos legais com base na sua bancada restante e no limite de rodada da mesa, incluindo 25 por cento, 50 por cento e o maior valor permitido no momento.
* Escolha **Entrada personalizada** quando precisar de um valor exato. Digitar 0 limpa essa cor.
* Escolher **All-in** usa toda a capacidade de aposta ainda disponível para essa cor na rodada atual. A Aposta Total Máxima Por Rodada do anfitrião ainda se aplica, portanto esta escolha nunca contorna o limite da mesa.
* Quando estiver satisfeito com suas apostas, use **Bloquear apostas**.
* Se todos os jogadores ativos bloquearem suas apostas antes que o cronômetro expire, os dados são lançados imediatamente.
* Se o cronômetro expirar primeiro, cada jogador ativo restante é bloqueado automaticamente com sua planilha de apostas atual, incluindo a possibilidade de bloquear **nenhuma aposta**.
* Após a resolução do lançamento, as bancadas são atualizadas, a classificação é anunciada e uma nova rodada de apostas começa, a menos que a partida tenha terminado.

**Mecânicas Especiais**

* **Fase de apostas compartilhada:** todos os jogadores ativos podem agir durante a mesma janela de apostas.
* **Apostas bloqueadas:** assim que você bloquear suas apostas para a rodada, não poderá editá-las novamente até a próxima rodada.
* **Ficar de fora:** você pode bloquear uma planilha de apostas vazia. Nesse caso, você não ganha nem perde fichas nessa rodada.
* **Jogadores abaixo do mínimo:** se a sua bancada cair abaixo da Aposta Mínima da mesa, você permanece na classificação, mas fica de fora das apostas porque nenhuma aposta legal é possível.
* **Cronômetro da rodada:** o cronômetro não descarta suas apostas atuais. Ele simplesmente bloqueia o que você já tiver quando o tempo esgotar.
* **Confirmar ações arriscadas:** quando sua preferência pessoal está ativada, All-in e o bloqueio de uma planilha de apostas vazia exigem a mesma escolha uma segunda vez dentro de 10 segundos.
* **Anúncios breves:** quando ativado nas suas Opções de Jogo pessoais, as mensagens de rodada, lançamento, bloqueio e pagamento usam redação compacta focada em dados.

**Pontuação**

Color Game trata fundamentalmente de **gerenciamento de bancada**.

* Seu principal valor competitivo é a sua **bancada** atual.
* A classificação também rastreia:
* **Rodadas lucrativas:** quantas rodadas terminaram com um ganho líquido positivo
* **Maior vitória:** seu maior lucro individual em uma única rodada

**Lógica de Pagamento**

O código usa o seguinte modelo de pagamento exato para **cada aposta de cor individual**:

* **0 correspondências:** a alteração líquida é **-aposta**
* **1 correspondência:** a alteração líquida é **+aposta**
* **2 correspondências:** a alteração líquida é **+2 × aposta**
* **3 correspondências:** a alteração líquida é **+3 × aposta**

Isso corresponde à estrutura tradicional de Color Game **1:1, 2:1, 3:1**.

Exemplo:

* Você coloca 5 fichas no vermelho e 3 fichas no azul.
* Os dados saem vermelho, vermelho, verde.
* Sua aposta no vermelho correspondeu a **2 dados**, então seu resultado líquido é **+10**.
* Sua aposta no azul correspondeu a **0 dados**, então seu resultado líquido é **-3**.
* O seu resultado líquido total para a rodada é, portanto, **+7 fichas**.

**Vencendo a Partida**

O jogo suporta duas condições de vitória:

* **Último Jogador de Pé**
* **Maior Bancada No Limite de Rodadas**

Ambos os modos também compartilham uma regra prática de término antecipado:

* Se apenas **um jogador capaz de pagar a aposta mínima** restar, a partida termina imediatamente, mesmo que o limite de rodadas ainda não tenha sido alcançado.

Isso significa que o comportamento exato é:

* **Último Jogador de Pé:**
* Se apenas um jogador ainda tiver fichas, esse jogador vence imediatamente.
* Se o limite de rodadas for alcançado primeiro, o jogador com a maior bancada vence.
* **Maior Bancada No Limite de Rodadas:**
* O foco pretendido é a bancada no final do limite.
* Se apenas um jogador ainda tiver fichas antes do limite, a partida termina porque nenhum outro jogador pode fazer outra aposta ou alterar a classificação.

Se os jogadores estiverem empatados no topo, o desempate é feito nesta ordem exata:

* maior bancada
* mais rodadas lucrativas
* maior vitória em rodada única
* se ainda houver empate, o resultado permanece empatado

**Opções Personalizáveis**

* **Bancada Inicial:** Cada jogador começa a partida com esta quantidade de fichas (padrão **100**, intervalo válido **10 a 1000**).

* **Aposta Mínima:** Cada aposta de cor diferente de zero deve ser pelo menos deste valor (padrão **1**, intervalo válido **1 a 100**).

* **Aposta Total Máxima Por Rodada:** O limite real por rodada de um jogador é o menor entre sua bancada atual e este valor de opção. A validação adicional exige que seja:
* pelo menos a Aposta Mínima
* não maior que a Bancada Inicial
* Padrão **20**, intervalo válido no controle de opções **1 a 1000**.

* **Cronômetro de Apostas:** O cronômetro compartilhado para a fase de apostas de cada rodada (padrão **15 segundos**, intervalo válido **5 a 60 segundos**).

* **Limite de Rodadas:** Assim que este número de rodadas for concluído, o jogo termina e a classificação é finalizada (padrão **20**, intervalo válido **1 a 100**).

* **Condição de Vitória:** Determina como o vencedor é decidido (padrão **Último Jogador de Pé**, opções: **Último Jogador de Pé** ou **Maior Bancada No Limite de Rodadas**).

**Atalhos de Teclado**

* **R:** Abre o menu de aposta rápida do vermelho.
* **U:** Abre o menu de aposta rápida do azul.
* **Y:** Abre o menu de aposta rápida do amarelo.
* **G:** Abre o menu de aposta rápida do verde.
* **W:** Abre o menu de aposta rápida do branco.
* **O:** Abre o menu de aposta rápida do laranja.
* **C:** Limpa suas apostas atuais.
* **Espaço:** Bloqueia suas apostas para a rodada atual.
* **E:** Ouve a fase atual, cronômetro, bancada, estado de bloqueio e líder.
* **V:** Ouve a planilha de apostas atual de cada jogador.
* **D:** Ouve o lançamento anterior e o resultado de cada jogador a partir desse lançamento.
* **T:** Ouve o prompt da fase atual.
* **S:** Ouve a classificação.
* **Ctrl+U:** Ouve quem está na mesa.
