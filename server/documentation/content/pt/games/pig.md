**Porquinho**

Porquinho é um jogo de dados de arriscar a sorte para 2 a 6 jogadores. Em cada turno, você rola repetidamente um dado e acumula um total de turno temporário. Você pode guardar esse total com segurança a qualquer momento, mas rolar um 1 faz você perder todos os pontos não acumulados do turno.

O primeiro jogador ou equipe a acumular pontos suficientes para atingir a meta vence imediatamente.

**Jogabilidade**

No seu turno, escolha entre **Rolar** e **Guardar**:

* **Rolar:** Role o dado. Um resultado de 2 até a face mais alta é adicionado ao total do seu turno, e você pode escolher novamente.
* **Rolar um 1:** Você perde todo o total do turno, não pontua nada para esse turno e o jogo passa para o próximo jogador.
* **Guardar:** Adicione o total atual do turno à sua pontuação permanente e encerre seu turno com segurança.

O jogo continua ao redor da mesa até que um jogador ou equipe acumule pontos suficientes para atingir ou superar a meta. Não há rodada final de turnos iguais: atingir a meta encerra o jogo imediatamente.

**Estratégia**

Cada rolagem arrisca o total completo do turno. Com o dado padrão de seis lados, uma linha de base comum é guardar com cerca de 20 a 25 pontos de turno, ajustando em seguida para a pontuação:

* Guarde mais cedo quando você estiver confortavelmente à frente.
* Assuma mais riscos quando um oponente estiver perto de vencer.
* Se o total do seu turno atual for vencer o jogo, guardar garante a vitória imediatamente.

Os bots consideram o número de lados do dado, a guarda mínima, a diferença de pontuação e quantos pontos restam para vencer.

**Equipes**

Nos modos de equipe, os companheiros de equipe compartilham uma pontuação permanente. Cada membro ainda faz um turno individual, e qualquer membro pode guardar pontos para a equipe. A equipe vence imediatamente quando sua pontuação compartilhada atinge a meta.

**Opções Personalizáveis**

* **Pontuação Alvo:** O total necessário para vencer (padrão 100, intervalo de 10 a 1.000).
* **Guarda mínima:** O total de turno necessário antes que a opção Guardar esteja disponível. Um valor de 0 segue o Porquinho padrão. Deve permanecer abaixo da pontuação alvo (padrão 0, intervalo de 0 a 999).
* **Lados do dado:** Rolar 1 sempre perde o total do turno, então mais lados reduzem a chance de perder pontos em cada rolagem (padrão dado de 6 lados, intervalo de 4 a 20 lados).
* **Modo de Equipe:** Jogue individualmente ou em arranjos de equipe suportados. O arranjo selecionado deve corresponder ao número de jogadores ativos.

**Opções Pessoais de Jogo**

* **Anúncios breves:** Usa mensagens mais curtas de rolagem, salvamento, estouro, rodada e vencedor, mantendo todas as pontuações essenciais.
* **Confirmar ações arriscadas:** Quando ativado, uma rolagem de alto risco deve ser pressionada uma segunda vez em até 10 segundos. Isso se aplica quando o total do turno atinge o limite de retenção estratégica do dado ou quando guardar já venceria o jogo.

**Status do Turno**

**Verificar status do turno** abre um painel ao vivo mostrando a meta, a rodada atual, a pontuação acumulada e o total de turno do jogador ativo, a pontuação que ele teria após guardar e a classificação atual.

**Atalhos de Teclado**

* **R:** Rolar o dado.
* **H:** Guardar o total atual do turno.
* **C:** Verificar o status do turno.
* **T:** Verificar de quem é o turno.
* **S:** Verificar pontuações.
* **Shift+S:** Abrir pontuações detalhadas.
