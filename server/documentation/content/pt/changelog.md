# Changelog

Quinta-feira, 27 de agosto de 2026

Novas Adições:

* O português agora está disponível no servidor, no aplicativo para computador, na web, em dispositivos móveis e nos guias para jogadores, graças à tradução comunitária de Tadeu Junior. O conteúdo ainda não traduzido para o português será exibido em inglês.

Melhorias:

* O atualizador de computador do Windows agora instala as atualizações do PlayAural e dos pacotes de som em uma janela dedicada e acessível. Ele verifica o pacote baixado antes de alterar a instalação, espera todas as janelas do PlayAural fecharem, verifica se o cliente atualizado inicia corretamente e restaura a versão de trabalho anterior se a inicialização falhar. Atualizações com falha ou canceladas também limpam os arquivos temporários e fornecem instruções de recuperação mais claras.
* Os Sons de Digitação do Play agora funcionam na caixa de chat do computador e nas caixas de texto abertas pelos jogos, bem como no chat e nas caixas de texto da web suportados. Teclas comuns usam uma variedade maior de sons, enquanto teclas numéricas, Delete e Enter têm feedback distinto. O teclado vietnamita Telex integrado do Windows e outros teclados de idiomas agora mantêm um som para cada tecla sem duplicatas ao formar caracteres acentuados.
* O Backgammon agora inclui uma visualização ao vivo de Movimentos legais; feedback mais claro de Desmarcar, remoção de peça com falha, Desfazer, Status, Contagem de pontos, Dados, Cubo e pontuação; texto personalizado para o jogador que está movendo e para todos os demais; foco de toque mais estável; e um guia para iniciantes reconstruído. Jogadores de toque rolam os dados tocando em qualquer ponto do tabuleiro sem mover o foco, enquanto 'Próximo destino' e 'Destino anterior' movem o foco apenas quando solicitado.
* O bloqueio de jogadores, os resumos de associação à mesa e o jogo do cubo de redobro do Backgammon agora estão disponíveis em espanhol.

Correções de bugs:

* Iniciar uma mesa apenas com bots e sem nenhum jogador humano ativo agora é interrompido antes do início do jogo. A mesa permanece aberta e explica que um humano deve retornar a uma cadeira de jogador, em vez de iniciar e depois ser cancelada.
* O Backgammon agora pontua corretamente dobras aceitas e recusadas, a posse do cubo, jogos Crawford, vitórias normais, gammons e backgammons. Ele também impede uma dobra desnecessária quando o valor atual do cubo já é suficiente para vencer a partida, e Desfazer restaura uma peça capturada com feedback claro para todos na mesa.

Terça-feira, 25 de agosto de 2026

Novas Adições:

* O bloqueio de jogadores agora está disponível a partir de solicitações de amizade, perfis, menus de jogadores online e membros da mesa, ou em Pessoal e Opções > Amigos > Bloquear um usuário. O bloqueio remove qualquer amizade e solicitações pendentes entre as duas contas, impede solicitações de amizade, mensagens privadas, convites de mesa e chat comum em ambas as direções, e impede que qualquer uma das pessoas entre novamente em uma mesa hospedada pela outra. Usuários Bloqueados permite revisar e desbloquear pessoas posteriormente. O bloqueio não remove ninguém de uma mesa compartilhada, não silencia o Chat de Voz de mesa e não impede que nenhuma das pessoas recupere um assento reservado; mesas salvas contendo as duas pessoas permanecem armazenadas com segurança, mas exigem que o bloqueio seja removido antes da restauração.

Melhorias:

* Assentos reservados em mesas ativas, incluindo mesas privadas, agora permanecem recuperáveis por meio de desconexões comuns e reinicializações planejadas do servidor. Jogadores que retornam são colocados de volta em sua mesa automaticamente. Se o único jogador humano ativo se desconectar e deixar a mesa sem supervisão, o jogo é pausado por até 15 minutos antes de a mesa fechar; esse período de tolerância é preservado em uma reinicialização planejada sem contar o tempo enquanto o servidor está offline.
* Restaurar uma mesa salva agora é exclusivo do proprietário e "tudo ou nada": todos os participantes são transferidos com sucesso, ou a mesa e o salvamento originais permanecem inalterados. Assentos humanos ocupados por bots de substituição são restaurados corretamente, e jogadores indisponíveis, dados salvos incompatíveis ou conflitos de bloqueio agora produzem orientações claras sem excluir o salvamento.
* Os resumos de Quem está na mesa agora omitem categorias vazias. As listagens de mesas ativas nomeiam todos os jogadores humanos, relatam os bots apenas como uma contagem, mostram uma breve prévia de espectadores com qualquer total restante e identificam claramente o host quando o host está assistindo.
* A remoção de peças no Backgammon agora é mais rápida e clara. Ativar uma peça a remove imediatamente quando esse é o seu único destino legal; quando um movimento no tabuleiro também é possível, a peça permanece selecionada para que uma segunda ativação possa removê-la. Tentativas inválidas explicam se restam peças fora do tabuleiro de casa ou na barra, se os dados não cabem ou se um ponto mais alto ocupado bloqueia o movimento. O status agora inclui as peças de cada cor fora do tabuleiro de casa, e as restrições de dobra fornecem explicações específicas.
* Chegadas à mesa, saídas voluntárias, expulsões, desconexões de rede e retornos de assento reservado agora têm dicas de áudio distintas. Alterações simultâneas de mesa e Chat de Voz não acumulam mais sons duplicados, enquanto eventos que ocorrem separadamente permanecem audíveis individualmente. As notificações do sistema também usam um conjunto mais variado de dicas, e o feedback de chat, mensagens privadas, convites, digitação e Chat de Voz foi renovado.
* O Chat de Voz para Dispositivos Móveis agora preserva de forma mais firme o áudio de jogo estéreo de qualidade total e a rota com fio, Bluetooth ou alto-falante selecionada pelo dispositivo. Música, atmosfera, efeitos comuns e efeitos em loop continuam de forma independente enquanto o Chat de Voz está ativo, e o microfone continua sendo ligado apenas após uma ação explícita do usuário.
* O chat agora fornece feedback claro quando um canal está indisponível ou uma mensagem é inválida ou longa demais, em vez de falhar silenciosamente ou enviá-la pela conversa errada.

Correções de bugs:

* O Backgammon agora avalia cada movimento em relação à rolagem restante completa, de modo que pessoas, bots e navegação por teclado usem consistentemente ambos os dados quando possível e o dado maior quando apenas um pode ser jogado. Isso corrige sequências legais que anteriormente ficavam paradas após o primeiro movimento, incluindo a remoção de peças com o dado restante após uma captura.

Terça-feira, 18 de agosto de 2026

Melhorias:

* Monopoly agora está totalmente disponível em espanhol, incluindo tabuleiros, menus, anúncios e o guia para iniciantes, graças ao tradutor da comunidade UnDuende (Storm Demoner).
* As telas de contas em espanhol agora incluem orientações sobre os caracteres do nome de usuário durante o registro e instruções claras quando um nome de conta mais antigo corresponder a mais de uma variação de letras maiúsculas e minúsculas.
* Menus de escolha agora podem ser atualizados enquanto permanecem abertos, sem perder o foco do leitor de tela. Opções, rótulos, descrições e saldos acompanham o estado atual do jogo; enviar ou cancelar retorna o foco ao controle que abriu a janela de prompt; entradas de texto não são reiniciadas por atualizações em segundo plano; e a fala ou os sons de abertura não se repetem durante essas atualizações. Isso mantém as escolhas de Ler todas as carteiras, Gerenciar propriedades e Propor uma troca no Monopoly, os rumos de posicionamento manual no Battleship, o prompt de carta jogável no Mile by Mile e as escolhas de Alterar carta no 21 (Regras de Sobrevivência) estáveis durante atualizações e reconexões de partidas.
* Os controles de leilão do Monopoly agora permanecem visíveis para todos os participantes que estão dando lances, são atualizados para mostrar o lance mínimo atual e continuam indisponíveis enquanto outro licitante estiver agindo. Eles fecham apenas quando você sai do leilão ou quando o leilão termina.
* A liquidação de aluguel no Monopoly agora fornece ao proprietário do imóvel, ao jogador pagante e aos demais ouvintes uma mensagem concisa a partir da perspectiva apropriada. Anúncios breves permanecem mais curtos, e avisos de aluguel duplicados foram removidos.
* Escolher explicitamente Terminar turno no Monopoly agora retorna o foco apenas para Rolar dados; o turno ou a ação de outro jogador não move o seu cursor. O guia também esclarece que não ter dinheiro nem propriedades não é falência, a menos que você posteriormente contraia uma dívida que não possa cobrir.

Correções de bugs:

* Pressionar Espaço para Rolar dados no Monopoly agora realiza exatamente uma rolagem. Durante a configuração inicial, De quem é o turno informa que ninguém tem o turno ainda e ações que mudam o jogo pedem que você aguarde; enquanto uma rolagem, movimento de peão, rolagem de aluguel ou efeito de carta estiver sendo resolvido, controles sobrepostos permanecem indisponíveis, mas as visualizações de informações continuam acessíveis.
* Escolher Propor uma troca agora pausa outras ações que mudam o jogo até que você selecione um parceiro de troca ou cancele, de modo que a rolagem de outro jogador não possa mais fechar o menu de seleção.
* Serviços de utilidade pública e marcos de Hanói agora sempre usam uma nova rolagem de aluguel e cobram o mesmo valor, independentemente de seu proprietário ser uma pessoa ou um bot. No tabuleiro de Hanói, o Pagode de Pilar Único e a Ponte Long Biên cobram 4.000 VND por ponto nos dados quando o proprietário possui um marco, ou 10.000 VND por ponto quando o proprietário possui ambos; cartas que enviam você para o serviço público mais próximo usam a taxa de grupo completo conforme necessário.
* Uma tela de resultado concluída do Monopoly agora mantém a moeda do tabuleiro que foi jogada, mesmo se o host selecionar um tabuleiro diferente para a próxima partida.

Domingo, 16 de agosto de 2026

Novas Adições:

* Monopoly foi adicionado para 2 a 8 jogadores. Escolha entre os tabuleiros dos Estados Unidos, Londres, Paris, Alemanha, Itália, Madri, Tóquio, Austrália, Nova Zelândia e Hanói (Vietnã), cada um com seus próprios espaços, moeda, cartas, transporte e termos de desenvolvimento. O jogo inclui compra e leilão de propriedades, cobrança de aluguel, conclusão de grupos de cores, desenvolvimento equilibrado, hipotecas, trocas, prisão, dívidas e falência, regras da casa configuráveis, bots estratégicos, Anúncios breves, visualizações de propriedades e tabuleiros amigáveis para leitores de tela, música e som dedicados, além de guias para iniciantes em inglês e vietnamita.

Melhorias:

* O Chat de Voz para Computadores agora permanece fluido quando várias pessoas falam ou as conexões flutuam brevemente, reduzindo chiados, engasgos, cortes de palavras e áudio atrasado, preservando a qualidade estéreo de entrada.
* Jogadores de espanhol agora veem os lutadores predefinidos e os movimentos do Battle em espanhol, e os nomes dos atalhos de teclado são consistentes em todos os guias de jogadores em espanhol.

Correções de bugs:

* O registro de conta agora raramente falha com um erro de servidor enquanto outros registros de conta ou de jogo estão sendo atualizados.
* Menus de escolha e prompts de texto agora permanecem vinculados ao estado atual da mesa. Respostas de um menu desatualizado são ignoradas, e prompts que não se aplicam mais fecham com segurança em vez de carregar uma decisão anterior para uma parte posterior do jogo.

Quarta-feira, 5 de agosto de 2026

Novas Adições:

* O espanhol agora está disponível em todo o servidor, aplicativo para computador, web, dispositivos móveis e guias de jogadores como uma tradução da comunidade por UnDuende (Storm Demoner). O conteúdo ainda não traduzido para o espanhol retorna ao inglês.
* Dicas de Menu agora mostram as descrições disponíveis diretamente nas escolhas de menu por padrão em cada cliente. Desative-as em Pessoal e Opções > Opções gerais > Acessibilidade > Dicas de Menu para linhas mais curtas; usuários de computador ainda podem pressionar Espaço para obter ajuda nas escolhas suportadas de sistema e configuração de jogo.
* Nomes de novas contas agora podem usar letras em qualquer idioma, números e espaços únicos, tornando possíveis nomes completos em vietnamita, mantendo o limite de 3 a 30 caracteres.

Melhorias:

* BANG! The Bullet: as ações de informação agora são mais fáceis de revisar: De quem é o turno relata escolhas pendentes fora do turno, Ler distâncias permanece aberto como um painel de status ao vivo, Ler sua mão e cartas em jogo inclui suas cartas viradas para cima, Ler a mesa mantém as linhas de cartas públicas concisas e as escolhas de alvo identificam cada personagem.
* BANG! The Bullet agora usa termos de defesa específicos para ataques e sons para tiros, Faca, Soco e outros ataques com um símbolo BANG!. Sua trilha sonora e atmosfera ocidentais também foram atualizadas.
* O Chat de Voz para Computadores agora entra e sai mais rapidamente, permanece responsivo durante sessões longas e preserva a qualidade do áudio de entrada, incluindo estéreo. O ruído do microfone e o cancelamento de eco afetam apenas o áudio que você envia.
* A correspondência de nomes de usuário agora não diferencia maiúsculas de minúsculas em todo o login, solicitações de amizade, perfis e mensagens privadas, enquanto cada cliente continua mostrando a grafia registrada da conta.

Correções de bugs:

* Em BANG! The Bullet, Jourdonnais agora pode usar suas verificações de Barril embutidas e equipadas antes de jogar uma defesa de sua mão. Quando dois jogadores têm a habilidade de Vulture Sam, aquele mais próximo do jogador eliminado no sentido horário pega a primeira carta, e então eles dividem as cartas restantes alternadamente.
* Espectadores desconectados agora são removidos de Quem está na mesa em vez de permanecerem na lista.
* Enviar uma mensagem privada para si mesmo não relata mais que você não é amigo da sua própria conta.

Sábado, 1 de agosto de 2026

Melhorias:

* No Android, música, atmosfera e efeitos em loop agora continuam tocando pelo tempo que o jogo exigir. Com o TalkBack ativo, o áudio do jogo também permanece nos fones de ouvido com fio selecionados pelo sistema, no dispositivo Bluetooth ou no alto-falante do telefone, em vez de oscilar entre as saídas.

Sexta-feira, 31 de julho de 2026

Novas Adições:

* BANG! The Bullet foi adicionado para 3 a 8 jogadores. Os hosts podem desativar Cartas e personagens expandidos para o jogo clássico de 80 cartas e 19 personagens para 4 a 7 jogadores, ou deixá-los ativados para o jogo de 120 cartas e 34 personagens para 3 a 8, podendo adicionar High Noon, A Fistful of Cards ou eventos mistos de mudança de turno. O jogo inclui regras básicas e expandidas fiéis, confrontos de papéis ocultos, papéis públicos para as regras especiais de três jogadores, escolhas de cartas privadas guiadas e revelações públicas exigidas pelas regras, informações acessíveis e menus de reação para telas de toque e teclado, bots estratégicos, áudio ocidental dedicado e guias para iniciantes em inglês e vietnamita.

Melhorias:

* Efeitos sonoros, música e atmosfera agora se comportam de maneira consistente em computadores, web e dispositivos móveis. Efeitos em loop param com o evento ao qual pertencem, música e atmosfera mudam suavemente, e o som ambiental pode passar perfeitamente por uma introdução, loop e encerramento. A reconexão restaura a paisagem sonora ao vivo sem reproduzir sua abertura, enquanto sair ou encerrar uma mesa permite que os encerramentos criados terminem sem que o áudio o siga de volta aos menus.
* A música do menu principal agora continua enquanto você navega por Jogar, Pessoal e Opções e seus submenus. As salas de espera são sempre silenciosas, cada cliente fornece áudio de conexão e as introduções dos jogos começam sem que a música do menu ou da sala de espera seja reproduzida por cima delas.
* Mover a mesma conta para outro dispositivo agora mantém a mesa atual, cronômetros de turno, eventos de jogo em andamento e áudio ativo intactos, enquanto reconstrói os controles corretos para o novo cliente de computador, web ou móvel. O dispositivo anterior se desconecta com segurança sem substituir temporariamente o jogador por um bot.
* Alertas online e offline agora suprimem duplicatas rápidas e reconexões breves, respeitam as configurações de notificação de cada ouvinte, mesmo para administradores e desenvolvedores, e usam o som de administrador ou desenvolvedor em vez do som genérico de amigo quando essa pessoa é um amigo.
* Os prompts de atualização agora usam o download correto para Windows ou Android em vez de abrir o pacote de outra plataforma. Se um download não estiver disponível para a plataforma atual, o cliente explica isso claramente.

Correções de bugs:

* Fazer login não restaura mais um prompt antigo de Logoff ou outra confirmação de uso único, e o som de boas-vindas agora toca uma vez no momento correto no computador, web e dispositivos móveis.

Segunda-feira, 20 de julho de 2026

Novas Adições:

* O Mile by Mile agora mantém cada oportunidade de Jogada Suja de 7 segundos aberta enquanto o jogo comum continua. Um remédio correspondente fecha apenas essa oportunidade, a primeira Segurança ou remédio válido decide o resultado quando ambos são jogados quase juntos, e os turnos ganhos começam após o término do turno atual. Anúncios de equipe também identificam o jogador que agiu de forma mais clara.
* Os bots do Mile by Mile agora planejam com base em finais exatos, pontuações de corrida e de partida, Perigos, remédios, Seguranças, Jogadas Sujas, Carma, companheiros de equipe e pilhas de compra e descarte, levando a jogadas e descartes mais fortes.
* A administração agora fornece uma tela de tradução para a Mensagem do Dia, motivos planejados de reinicialização ou desligamento do servidor e motivos personalizados de banimento ou silenciamento. Idiomas oficiais são obrigatórios, enquanto idiomas da comunidade podem usar um fallback para que os avisos cheguem a cada jogador em um idioma adequado.

Sábado, 18 de julho de 2026

Novas Adições:

* Exploding Kittens foi adicionado para 2 a 5 jogadores com o jogo completo da Edição Original de 56 cartas; bots altamente estratégicos que usam apenas informações que um jogador poderia saber; opções de Jogo mais rápido e Combos avançados; respostas de Não Pode configuráveis de 2, 3, 5, 10, 15 ou 20 segundos; escolhas guiadas claras para combos, alvos, Favores, Desarmes e colocação de Gatinhos; áudio dedicado; restauração segura de partidas inacabadas; e guias para iniciantes em inglês e vietnamita.
* O persa agora está disponível em todo o servidor, aplicativo para computador, web e dispositivos móveis. Quando um jogo ou guia mais recente ainda não foi traduzido, seu conteúdo retorna ao inglês.

Melhorias:

* O texto em vietnamita e o guia do Mile by Mile agora usam termos de corrida mais claros e consistentes e anúncios mais curtos e amigáveis para leitores de tela.
* As rolagens de dados agora usam um conjunto variado de sons em Pig, Farkle, Yahtzee e outros jogos baseados em dados.

Domingo, 5 de julho de 2026

Novas Adições:

* O Tien Len agora usa moedas iniciais como banca, com uma opção de partida rápida de 20 moedas, eliminação com 0 moedas, pagamentos padrão de colocação, corte, sobra e vitória instantânea, e liquidações de término de mão detalhadas e concisas.

Melhorias:

* O foco do menu é mais estável em computadores, web e dispositivos móveis: quando a linha em foco desaparece, o foco agora se move para o próximo item de menu útil em vez de saltar pela posição antiga.
* Quando uma partida começa, o foco agora se move do menu da sala de espera para o primeiro item ativo do jogo, de modo que as cartas e as ações de turno fiquem imediatamente disponíveis.

Correções de bugs:

* O Tien Len agora mantém os jogadores que passaram bloqueados da jogada atual até que ela seja limpa, permitindo ainda respostas válidas de corte do sul.

Sábado, 4 de julho de 2026

Novas Adições:

* O Mile by Mile agora inclui pontuação de Ação Atrasada para viagens concluídas após o esgotamento da pilha de compra, com resumos de pontuação e documentação atualizados.

Melhorias:

* O UNO está mais limpo em todos os dispositivos: jogadores de computador usam U, jogadores de toque recebem o UNO fixado na parte superior do menu de turno, e as escolhas de cor curinga movem o foco para uma carta útil ou item de menu.
* As penalidades de interceptação do UNO, verificações de pontuação, anúncios de cartas iniciais, anúncios de escolha de cor e verificações de contagem de cartas são mais curtos e claros.
* Os bots do Battle agora escolhem lutadores fortes e movimentos com mais variedade, mantendo escolhas táticas de ataque e suporte.
* O fluxo de rodadas do Tien Len agora tem anúncios voltados para áudio mais limpos.

Correções de bugs:

* Os menus de jogo e de mesa agora se recuperam de forma mais confiável após caixas de status, confirmações de saída, ações obsoletas, reconexões, restaurações e convites de mesa aceitos, para que os jogadores tenham menos probabilidade de ver menus em branco ou travados.
* O UNO agora aplica os efeitos oficiais de carta inicial para Pular, Inverter, Comprar Dois e Curinga, e retorna o Curinga Compra Quatro para o baralho antes de virar uma nova carta inicial.
* Os avisos de UNO agora permitem que os jogadores peguem um UNO esquecido antes da próxima jogada ou compra, e tentativas inválidas de UNO fornecem feedback mais claro.
* As cartas de Segurança do Mile by Mile agora limpam perigos ativos correspondentes com mais precisão, e os resultados finais agora relatam a pontuação vencedora e a distância de corrida corretas.
* O Battle não bloqueia mais a configuração com configurações de equipe ocultas após sair da Batalha em Equipe.
* O Tien Len agora reconhece mãos de vitória instantânea mais padrão do sul, incluindo sequência de dragão, quatro 2s e três trincas consecutivas.
* O Tien Len agora segue regras mais rígidas de abertura de primeira mão e corte.

Sexta-feira, 3 de julho de 2026

Novas Adições:

* O Ninety Nine agora corresponde aos controles de contagem decrescente entre rodadas do Scopa, para que os hosts possam pausar a espera ou iniciar a próxima rodada imediatamente.
* As opções de configuração de jogo agora incluem texto de ajuda mais claro em inglês e vietnamita, com termos consistentes para padrões, intervalos e escolhas nos manuais e menus de opções.
* A seleção de idiomas agora mostra informações mais claras sobre os idiomas suportados, incluindo crédito do tradutor e status oficial/da comunidade quando disponível.

Correções de bugs:

* Quem está na mesa e os menus de ações de membros não exigem mais pressionamentos extras de Voltar após ações bloqueadas ou obsoletas, e as linhas de substituição offline ou remoção de bot se comportam de forma mais confiável.
* O fallback de idioma e documentação é mais seguro no servidor, web e dispositivos móveis, para que traduções parciais permaneçam legíveis e documentos ausentes retornem ao inglês em vez de expor chaves brutas ou páginas em branco.
* A ajuda de opções e preferências agora segue exatamente a linha em que você está focado e ignora pacotes de menu de Voltar ou obsoletos.
* O Scopa agora lida com layouts de abertura inválidos, varreduras de Asso piglia tutto, situações de pontuação alvo empatada, pilhas de pontuação de jogadores ativos e opções de configuração conflitantes com mais precisão.
* O Ninety Nine agora mantém o topo do descarte seguro ao reciclar o baralho, relata compras manuais vazias com clareza, mantém os controles de mão fora do turno estáveis para usuários de toque e documenta que as penalidades do marco 33/66 se aplicam apenas quando o total é elevado até esses números.
* O Crazy Eights agora move o foco para a melhor carta seguinte da mão após escolher um naipe para um 8 curinga, com um fallback seguro para o menu de ação principal.
* A pontuação de mão bloqueada do Crazy Eights agora concede apenas as diferenças da menor mão, e as mensagens de compra forçada agora correspondem ao número de cartas efetivamente compradas.

Segunda-feira, 29 de junho de 2026

Novas Adições:

* O 21 (Regras de Sobrevivência) agora suporta de dois a quatro jogadores, com resultados de sobrevivência em todos os jogadores restantes e escolhas de alvo para Cartas de Mudança que afetam um oponente.
* A administração agora inclui Gerenciamento de Energia do Servidor para agendar reinicializações ou desligamentos com motivos claros, motivos personalizados multilíngues, avisos de contagem decrescente e reinicializações planejadas que preservam mesas ativas enquanto os clientes se reconectam.
* Grandes menus de servidor agora suportam pesquisa e páginas de 100 itens com intervalos de página claros, controles de Primeira página, Página anterior, Próxima página e Última página.

Correções de bugs:

* Quem está na mesa agora lista jogadores ativos antes dos espectadores e relata claramente o status online, offline, de chat de voz e de assumido por bot.
* Quem está na mesa e menus de lista relacionados agora mantêm Voltar disponível, evitam estados de menu duplicados ou vazios e preservam o foco durante atualizações.
* O modo TalkBack móvel agora mantém os anúncios do servidor responsivos, interrompe a fala antiga quando você move o foco e evita mensagens atrasadas ou repetidas.
* O Color Game agora mantém a confirmação de all-in dentro do menu de apostas da cor selecionada para que você possa pressionar a mesma escolha de All-in novamente para confirmar.
* O Ludo agora explica que você deve mover uma peça antes de rolar novamente quando uma rolagem já tiver produzido um movimento legal.
* O Sorry! agora explica que você deve escolher um movimento legal antes de comprar novamente após uma carta já ter sido comprada.

Sexta-feira, 26 de junho de 2026

Novas Adições:

* Quem está na mesa agora é uma lista interativa com um resumo da mesa, os papéis de cada pessoa, ações de host, ações de amigo e remoção de bot quando disponível.
* Jogadores Online agora abre o menu completo de ações de amigo diretamente quando você seleciona alguém que já é seu amigo.
* Pirates of the Lost Seas agora mostra Verificar posição para jogadores de toque durante partidas ao vivo.
* O Chat de Voz para Computador e web agora usa Alt+V para entrar ou sair e Alt+Shift+V para silenciar ou ativar o microfone.
* Os sons de clique e ativação de menu móvel foram atualizados.

Correções de bugs:

* As listas de passar host, expulsar e expulsar e banir do Gerenciamento de Host agora são atualizadas automaticamente quando as pessoas entram ou saem da mesa.
* O cliente de computador agora aplica alterações de idioma do servidor imediatamente, sem exigir reinicialização.
* As alterações de volume de efeitos sonoros no computador agora afetam sons que já estão sendo reproduzidos.
* O menu de voz TTS móvel agora seleciona vozes do sistema corretamente e mantém com segurança as vozes salvas quando o Android retorna temporariamente uma lista de vozes vazia.
* A mensagem de incompatibilidade de atualização/versão da web agora está localizada em vez de mostrar texto de fallback em inglês bruto.

Quinta-feira, 25 de junho de 2026

Novas Adições:

* A versão web foi reestruturada em um cliente PlayAural mais completo com navegação por teclado mais forte, layout de toque, chat de voz, recuperação de senha, suporte a CAPTCHA, buffers de histórico estáveis e uma interface mais clara para baixa visão.
* A versão web agora tenta se reconectar por até 30 segundos após uma queda de rede ou reinicialização do servidor antes de exibir uma mensagem clara de falha.
* O Dead Man's Poker agora usa um botão de Desistir contextual em vez de botões separados de Desistir e Desistência de Covarde.
* O Dead Man's Poker agora abre Ler mesa e Ler revólveres como telas de status ao vivo modernas.

Correções de bugs:

* O Five Card Draw agora retorna você ao menu de apostas principal imediatamente após comprar cartas ou ficar na mesa.
* Texas Hold'em e Five Card Draw agora param de mostrar ações de jogo para jogadores falidos.
* O Dead Man's Poker agora permite que Pagar e All-in paguem corretamente o valor de all-in de um oponente.
* As listas de amigos e de jogadores agora distinguem pessoas no menu principal de pessoas aguardando em uma mesa.
* As telas de resultado de fim de jogo agora são individuais, de modo que fechar seus resultados não fecha mais os resultados de outro jogador.
* As telas de resultado de fim de jogo não desaparecem mais quando alguém entra ou sai da mesa.
* Os fluxos de convite, passar host, expulsar e expulsar e banir do Gerenciamento de Host agora permanecem abertos após uma ação para que os hosts possam continuar gerenciando a mesa.
* A conexão de jogo móvel agora permanece ativa quando o aplicativo é minimizado ou a tela está desligada.
* Os microfones de chat de voz móvel agora continuam transmitindo em segundo plano em dispositivos que anteriormente paravam após vários segundos.
* O chat de voz móvel não força mais o áudio do jogo para mono.
* Os gestos de auto-vocalização móvel agora respondem de forma mais confiável durante o jogo.
* As caixas de edição móveis agora leem seus conteúdos com mais confiabilidade no modo de auto-vocalização.
* As alterações de voz TTS móvel agora se aplicam com mais confiabilidade sem reiniciar.
* As alterações de velocidade TTS móvel agora se aplicam com mais confiabilidade sem reiniciar.
* A navegação por Tabulação na web agora percorre o menu, o histórico e o chat durante o jogo.
* A navegação por Escape na web agora funciona a partir de mais menus do servidor, incluindo listas de jogadores online.
* Os prompts de entrada na web agora escolhem campos de linha única ou multilinhas do tipo de solicitação do servidor e enviam entradas de linha única com Enter.
* Os sons de menu da web agora seguem o feedback de navegação estilo computador de forma mais próxima.
* Os sons de digitação na web agora são reproduzidos durante prompts de entrada.
* O silenciamento de buffer F4 na web agora funciona a partir do buffer ativo.
* Os atalhos de volume de música e atmosfera na web agora ajustam o áudio ativo do navegador.
* A saída de Web Speech e ARIA ao vivo na web agora evita mensagens ignoradas com mais confiabilidade.
* Os atalhos de leitura de buffer na web agora funcionam no modo Web Speech.
* Os controles de seleção de voz e velocidade de fala na web são mais claros em Windows, Android, iOS e macOS.
* A localização na web e as mensagens de conexão são mais claras em inglês e vietnamita.

Domingo, 21 de junho de 2026

Novas Adições:

* O Yahtzee agora suporta prática solo sem afetar as classificações competitivas.
* O Yahtzee agora permite que jogadores e espectadores pressionem Shift+C para verificar a súmula de qualquer jogador.
* O portal Pirates of the Lost Seas agora inclui um Destino aleatório que pode escolher qualquer espaço de mapa válido, incluindo mares vazios.
* O Rolling Balls agora inclui conjuntos de bolas de Volta ao Mundo e Jornada Através do Vietnã mais ricos e precisos.
* A documentação do Rolling Balls agora credita claramente o projeto de código aberto original PlayPalace.
* O Chaos Bear agora suporta Anúncios breves.
* A Pontuação Alvo padrão do Farkle agora é 1000.

Correções de bugs:

* O anúncio de turno em toda a plataforma agora diz ao jogador ativo "É o seu turno", enquanto todos os outros ouvem de quem é o turno.
* Os anúncios de tempo limite e xeque do Xadrez agora usam termos pessoais e públicos separados.
* Os anúncios de vencedor final do Citadels agora usam termos pessoais e públicos separados.
* Os anúncios de vencedor final do Sorry! agora usam termos pessoais e públicos separados.
* Os anúncios de eliminação, pontuação e vencedor final do UNO agora usam termos pessoais e públicos separados.
* Os resumos de batalha do Age of Heroes agora usam termos de atacante, defensor e observador separados.
* O foco do menu agora é restaurado com mais confiabilidade ao retornar da Administração, Gerenciamento de Host, Opções, menus de mesa, telas de status e prompts de ação.
* A opção Iniciar jogo agora permanece visível nas salas de espera e explica problemas de configuração quando selecionada.
* As preferências de manutenção de dados agora explicam Índices de dados e Valores de dados com mais clareza e aparecem apenas em jogos que os utilizam.
* As verificações de pontuação padrão do Yahtzee agora mostram totais reais do Yahtzee.
* Pontuar uma categoria no Yahtzee agora retorna o foco de toque para Rolar dados.
* A aceitação de anulação no Xadrez não resolve mais o jogo como um empate.
* O histórico de desfazer do Xadrez é limpo corretamente.
* O Xadrez mantém Inserir movimento visível como uma âncora de foco estável e retorna o foco de toque para lá após enviar um movimento.
* Instinto de Marinheiro do Pirates of the Lost Seas não cria mais escolhas em branco.
* A estratégia de bot do Pirates of the Lost Seas é mais forte e usa habilidades com mais inteligência.
* O equilíbrio de habilidades, mensagens de habilidade e feedback de bloqueio de portal do Pirates of the Lost Seas estão mais claros.
* As regras, manuais, terminologia de bolas e anúncios do Rolling Balls estão mais claros em inglês e vietnamita.
* O Mile by Mile agora explica os limites de cartas de distância com clareza e permite cartas legais que não ultrapassam a linha de chegada.
* O Mile by Mile agora respeita corretamente as opções de Exigir chegada exata e ultrapassagem.
* Os prompts de descarte do Mile by Mile agora restauram o foco para a carta de onde você veio.
* Snakes and Ladders agora fornece anúncios mais claros de início, escada, cobra, salto para trás, chegada exata e vitória.
* O Midnight agora mantém o foco de rolagem e bloqueio de pontuação mais estável para clientes de toque.
* O Threes agora mantém o foco do menu de resultado de dados, rolagem e pontuação mais estável para clientes de toque.
* O Toss Up agora retorna o foco de toque suavemente após depositar pontos, sem roubá-lo durante a navegação normal.
* O Pig agora retorna o foco de toque suavemente após reter pontos, sem roubá-lo durante a navegação normal.
* O Tradeoff agora mantém os menus de rolagem, troca e pontuação mais estáveis para clientes de toque.
* O Bunko agora mantém os menus de rolagem e status mais estáveis para clientes de toque.
* O Farkle agora mantém os menus de escolha de dados e rolagem mais estáveis para clientes de toque.
* O Color Game agora mantém os menus de apostas e status mais estáveis para clientes de toque.
* O Light Turret agora mantém os menus de disparo, melhoria e status mais estáveis para clientes de toque.
* O Left Right Center agora mantém os menus de rolagem e status de fichas mais estáveis para clientes de toque.
* O Metal Pipe agora mantém os menus de ação e status mais estáveis para clientes de toque.
* Os bots do Farkle agora tomam decisões mais fortes de risco versus recompensa.
* Os bots do Rolling Balls agora tomam decisões mais fortes.
* Os bots do Tradeoff agora tomam decisões mais fortes.
* Os bots do Pirates of the Lost Seas agora usam movimento, ataques e habilidades de forma mais estratégica.
* O UNO agora preserva uma pilha de Compra pendente corretamente quando uma carta de Compra vence a mão.
* Cards Against Humanity agora fornece feedback mais claro para submissões, julgamento, configuração de múltiplos juízes, tamanhos maiores de mão e texto de carta apenas em inglês.
* As dicas sonoras do Cards Against Humanity agora são roteadas corretamente entre os clientes.

Quarta-feira, 17 de junho de 2026

Novas Adições:

* O UNO agora tem documentação completa para iniciantes em inglês e vietnamita.
* O Xadrez agora suporta entrada de movimento digitada usando notação comum de xadrez e movimentos no estilo de coordenadas.
* O Xadrez agora possui um bot delimitado mais forte.
* O Battle agora suporta Batalha em Equipe por meio do fluxo de configuração de equipe padrão.
* As habilidades de lutadores do Battle foram concluídas, reequilibradas e explicadas no jogo.
* Caixas de status ao vivo agora permitem que placares, tabuleiros, classificações, listas e outras telas de status permaneçam abertos e sejam atualizados enquanto o jogo muda.

Correções de bugs:

* O Coup agora possui anúncios mais claros e menus de leitores de tela mais estáveis.
* O Citadels agora possui anúncios mais claros e feedback de configuração mais seguro.
* O Backgammon agora possui anúncios mais claros e menus de leitores de tela mais estáveis.
* O Battle agora possui anúncios mais claros e feedback de habilidade mais seguro.
* O Battleship agora possui anúncios mais claros e menus de implantação mais estáveis.
* O Xadrez agora possui anúncios mais claros e menus de entrada de movimento mais estáveis.
* O Crazy Eights agora possui anúncios mais claros e menus de escolha de naipe mais estáveis.
* O Chaos Bear agora possui anúncios mais claros e menus de leitores de tela mais estáveis.
* O Dead Man's Deck agora possui anúncios mais claros e menus de ação mais estáveis.
* O Dead Man's Poker agora possui anúncios mais claros e menus de apostas mais estáveis.
* O Senet agora possui anúncios mais claros e menus de tabuleiro mais estáveis.
* O Ludo agora possui anúncios mais claros e menus de peças mais estáveis.
* O Sorry! agora possui anúncios mais claros e menus de peões mais estáveis.
* O Threes agora possui anúncios mais claros e menus de dados mais estáveis.
* O 21 (Regras de Sobrevivência) agora possui anúncios mais claros e feedback de ação mais seguro.
* O Xadrez agora segue a contagem padrão de movimentos completos e fornece Anúncios breves mais curtos quando ativados.
* O Battleship agora fornece feedback mais claro de implantação e disparo.
* A colocação manual de navios do Battleship usa o menu de posicionamento isolado novamente.
* O Battleship agora relata a prontidão de implantação de cada jogador ao verificar de quem é o turno durante a configuração.
* O Crazy Eights agora lida com a escolha de naipe do 8 curinga de forma mais parecida com o UNO e evita erros irrelevantes de não é seu turno para atalhos de naipe.
* O Dead Man's Poker mantém os menus de ação de toque ancorados durante trocas de cartas e eventos de mesa.
* Os anúncios de confronto do Dead Man's Poker são menos repetitivos e mãos empatadas são relatadas como empates.
* Os bots do Dead Man's Poker agora jogam de forma mais agressiva e inteligente.
* O Dead Man's Deck fornece feedback de regras mais claro, informações de status, blefe, desafio e anúncios de sobrevivência.
* O Coup agora aplica a regra oficial de moedas do primeiro turno para dois jogadores, mesmo quando o primeiro jogador é um bot.
* Os menus de troca do Coup agora mantêm as cartas selecionadas visíveis e marcam as cartas trocadas.
* O Citadels agora fornece feedback mais claro de construção, personagem e pontuação.
* O Senet agora lida com espectadores corretamente e usa os atalhos de pontuação padrão S e Shift+S.
* O Senet não sobrescreve mais outro menu aberto durante atualizações do tabuleiro.
* O Backgammon agora torna os Anúncios breves genuinamente breves.
* O Ludo agora torna os Anúncios breves genuinamente breves.
* O Sorry! agora torna os Anúncios breves genuinamente breves.
* O Backgammon agora fornece um erro claro se você tentar se mover antes de rolar.
* O Ludo mantém o foco de toque mais estável após rolagens, movimentos automáticos e escolhas manuais de peças.
* O Sorry! mantém o foco de toque mais estável após compras, movimentos automáticos e escolhas manuais de peões.
* Os prompts de movimento do Sorry! agora incluem a posição atual de cada peão.
* Midnight e Farkle agora movem o foco para a primeira escolha de dados após uma rolagem pedir para você reter dados.
* O 21 (Regras de Sobrevivência) não revela mais o total oculto de um oponente quando ele para.
* O 21 (Regras de Sobrevivência) agora explica quando um efeito ativo impede a compra.
* O Age of Heroes agora lida com solicitações de construção de estradas recusadas ou indisponíveis com segurança.
* Verificações de pontuação básica agora falam cada jogador ou equipe separadamente.
* Verificações de pontuação detalhadas agora usam telas de status linha por linha claras quando apropriado.
* Menus de placar agora ocultam jogos que não suportam placares.
* Dados de placar antigos sem suporte são limpos com segurança.
* Convites de mesa não podem mais ser recusados pressionando o título do convite.
* Convites de mesa que chegam enquanto você está digitando esperam até que você termine a entrada.
* O filtro de categoria Jogar não vaza mais para Documentação, Placares ou Minhas Estatísticas.
* As páginas de documentação renderizam Markdown escapado de forma mais consistente.
* Como Jogar (Ctrl+F1 no computador) não deixa mais o menu de ação vazio após fechar a tela de regras.

Terça-feira, 9 de junho de 2026

Novas Adições:

* Age of Heroes foi adicionado com menus localizados e documentação.
* Metal Pipe foi adicionado com menus localizados e documentação.
* Nine foi adicionado com menus localizados e documentação.
* Senet foi adicionado com menus localizados e documentação.
* Cards Against Humanity foi adicionado com menus localizados, documentação, áudio dedicado e texto de carta em inglês.
* 21 (Regras de Sobrevivência) foi adicionado com menus localizados e documentação.
* O UNO foi adicionado como substituto do Last Card.
* O menu Jogar agora possui um filtro de categoria para navegar pelos jogos por tipo.
* As opções agora são divididas em seções mais claras de Opções Gerais e Opções de Jogo.
* As Opções de Jogo agora suportam substituições de preferências por jogo.
* Confirmar ações arriscadas e Anúncios breves foram adicionados como opções de jogo pessoais onde os jogos se beneficiam deles.
* O Volume de Efeitos Sonoros foi adicionado juntamente com o volume de Música, Atmosfera e Chat de Voz.
* Dispositivos móveis agora possuem abas de navegação superiores para Principal, Chat, Histórico e Atalhos quando a auto-vocalização está desativada.
* Clientes web e móveis agora respeitam os sons de destaque por item, incluindo sons de quadrados de tabuleiro de Backgammon.

Correções de bugs:

* O Scopa agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Blackjack agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Ninety Nine agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Mile by Mile agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Dominos agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O 21 agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Tien Len agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Pusoy Dos agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Five Card Draw agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Texas Hold'em agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Ludo agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Sorry! agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Backgammon agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Citadels agora possui regras mais claras, melhores prompts e anúncios mais naturais.
* O Blackjack agora pula jogadores falidos, usa fichas de forma consistente, bloqueia apostas quando confirmadas e espaça as compras de cartas do dealer.
* O Ninety Nine agora exclui jogadores eliminados de distribuições futuras.
* O Ninety Nine agora inicia cada nova rodada com um primeiro jogador aleatório e faz uma pausa breve entre as rodadas.
* O Ninety Nine agora restaura menus localizados corretamente após a reconexão.
* O Ninety Nine agora corrige um raro bug de estouro de contagem.
* O Dead Man's Poker agora rastreia vitórias de confronto corretamente e lida com empates com anúncios de compra mais claros.
* O Dead Man's Poker agora permite uma troca de cartas por mão e bloqueia ações de All-in na primeira rodada.
* O Mile by Mile agora reconhece Jogada Suja quando a carta de segurança correta é jogada durante a janela de reação.
* Cartas não jogáveis do Mile by Mile agora explicam o motivo e oferecem descarte ou cancelamento.
* O Dominos agora mantém os ramos de "spinner" estáveis.
* O Dominos agora permite que o jogador inicial correto escolha sua peça de abertura.
* O Tien Len agora segue os detalhes das regras do sul e do norte com mais precisão.
* O Tien Len agora suporta jogo continuado para colocações restantes, vitórias instantâneas, regras de corte, terminologia do sul do Vietnã e pontuação em moedas.
* O Pusoy Dos agora valida regras com mais rigor.
* O Pusoy Dos agora fornece mensagens localizadas mais claras.
* Os bots do Pusoy Dos agora tomam melhores decisões.
* Passagens arriscadas no Pusoy Dos agora usam tratamento de confirmação mais seguro.
* O Five Card Draw agora mantém ações de informação úteis disponíveis em clientes de toque durante a mão.
* O Texas Hold'em agora mantém ações de informação úteis disponíveis em clientes de toque durante a mão.
* O Ludo agora respeita a preferência de Anúncios breves de cada jogador.
* O Sorry! agora respeita a preferência de Anúncios breves de cada jogador.
* O Ludo agora mantém o foco do leitor de tela direcionado para a próxima ação útil após interações diretas de rolagem ou movimento.
* O Sorry! agora mantém o foco do leitor de tela direcionado para a próxima ação útil após interações diretas de compra ou movimento.
* Clientes de toque agora mantêm as ações principais visíveis como âncoras de foco, emitindo erros claros quando as ações não são permitidas.
* Os sons de turno são mais consistentes.
* Os sons de entrada e saída de espectadores do Crazy Eights agora são reproduzidos novamente.
* Os sons de entrada e saída de mesa agora também são reproduzidos para expulsões e banimentos.
* Jogadores humanos não podem mais registrar nomes reservados para bots.
* Bots não podem mais se passar por jogadores humanos na mesma mesa.
* Detalhes de status móveis agora aparecem na parte inferior da ordem do leitor de tela em vez de antes do conteúdo principal do jogo.
* O roteamento de atalhos de computador é mais confiável para jogos de grade e tabuleiro adicionados recentemente.

Terça-feira, 5 de maio de 2026

Novas Adições:

* O Dead Man's Poker foi adicionado com documentação completa para iniciantes e localização em inglês/vietnamita.
* As opções foram reorganizadas em submenus categorizados.
* O Volume do Chat de Voz foi adicionado às Opções.
* O computador agora suporta o controle de Volume do Chat de Voz.
* A web agora suporta o controle de Volume do Chat de Voz.
* Dispositivos móveis agora suportam o controle de Volume do Chat de Voz.

Correções de bugs:

* A cronometragem do áudio de introdução do Dead Man's Deck foi refinada para um início cinematográfico mais suave.
* Os caminhos de retorno do submenu de opções agora são restaurados com mais confiabilidade após a edição de valores ou saída.

Sábado, 2 de maio de 2026

Novas Adições:

* O arranjo de equipes foi adicionado para que os hosts possam atribuir e trocar equipes antes de jogos em equipe suportados.
* A exclusão de amigos agora pede confirmação antes de remover alguém.

Correções de bugs:

* As verificações de pontuação agora anunciam unidades exatas de pontuação para cada jogo em vez de termos genéricos.
* As verificações de pontuação agora mostram nomes de bots de substituição corretamente quando um jogador desconectado foi assumido.

Quarta-feira, 29 de abril de 2026

Novas Adições:

* Os bots de substituição agora usam um nome de bot diferente em vez de pegar o nome exato do jogador desconectado.
* Jogadores desconectados podem recuperar seu assento exato enquanto a partida atual ainda estiver em andamento.
* A limpeza do lobby agora converte jogadores sentados desconectados em bots de substituição recuperáveis antes que o host inicie uma partida.
* Sons e anúncios de transferência de assento agora identificam tanto o humano original quanto o bot de substituição.

Correções de bugs:

* Nomes de bots personalizados não podem mais coincidir com ninguém na mesa ou com qualquer jogador registrado.
* Espectadores desconectados agora são removidos antes do início de uma partida.

Terça-feira, 28 de abril de 2026

Novas Adições:

* O Dead Man's Deck foi adicionado com documentação para iniciantes.
* O Dead Man's Deck está totalmente localizado em inglês e vietnamita.

Domingo, 26 de abril de 2026

Novas Adições:

* Adicionar um bot agora atribui automaticamente um nome de bot aleatório, a menos que Nomes de bots personalizados esteja ativado.
* Nomes de bots personalizados agora exigem nomes exclusivos de 3 a 30 caracteres.

Correções de bugs:

* Convites de mesa que chegam enquanto você está digitando em uma caixa de entrada agora esperam com segurança até que você termine.
* Reivindicar um assento de um bot de substituição agora anuncia o retorno para toda a mesa.
* Comandos de barra inválidos não são mais transmitidos como mensagens de bate-papo regulares.
* Ações de cancelamento de entrada móvel não congelam mais o menu.
* Os gestos de auto-vocalização móvel são mais suaves e confiáveis.

Quinta-feira, 23 de abril de 2026

Novas Adições:

* O Citadels foi adicionado com documentação abrangente.
* O Citadels está totalmente localizado em inglês e vietnamita.
* Os dispositivos móveis ganharam suporte experimental para execução em segundo plano.

Correções de bugs:

* A interface do computador agora funciona de forma mais suave e confiável.
* As verificações de ping móvel agora retornam resultados quando a auto-vocalização está desativada.
* Jogadores móveis agora podem descartar cartas do Mile by Mile com o gesto de pressionar e segurar do leitor de tela.
* A detecção de idioma do dispositivo móvel é mais suave na primeira inicialização.
* A conexão de rede móvel é mais estável e responsiva.

Domingo, 19 de abril de 2026

Novas Adições:

* O Gerenciamento de Host agora possui Reiniciar Jogo para retornar uma mesa à sala de espera sem recriá-la.
* Cartas de escolha do Ninety Nine, como 10 e Ás, agora incluem Cancelar.
* O Ninety Nine agora fornece feedback claro de Não é seu turno.
* O Mile by Mile agora fornece feedback claro de Não é seu turno.
* O Scopa agora fornece feedback claro de Não é seu turno.

Correções de bugs:

* A atmosfera e a música de fundo de uma mesa anterior não continuam mais após a troca de mesas.
* A entrada de chat do computador funciona melhor com teclados em vietnamita.
* Jogadores móveis podem navegar de volta a partir do menu de ação do jogo com mais confiabilidade.
* A atmosfera e a música de fundo móveis não cortam mais ao entrar no chat de voz.
* As notificações de jogos móveis agora chegam ao leitor de tela do sistema quando a auto-vocalização está desativada.
* O foco do leitor de tela móvel é mais estável ao usar o leitor de tela do sistema.
* Tabuleiros de grade móveis, como Battleship e Xadrez, agora são exibidos e navegados com mais confiabilidade.

Quinta-feira, 16 de abril de 2026

Novas Adições:

* O Chat de Voz de mesa em tempo real foi adicionado.
* O computador agora inclui controles de Chat de Voz de mesa.
* O computador agora permite que você escolha um dispositivo de entrada de áudio para o Chat de Voz.
* Os dispositivos móveis agora incluem o Chat de Voz de mesa na aba Chat.
* A web agora inclui o Chat de Voz de mesa na área de Chat.

Terça-feira, 14 de abril de 2026

Novas Adições:

* As descrições de habilidades do Battle foram adicionadas diretamente dentro do menu de habilidades.
* Sons de notificação de mesa criada foram adicionados.
* Sons de notificação de convite de mesa foram adicionados.

Correções de bugs:

* A jogabilidade do Chaos Bear foi reequilibrada para partidas mais justas.
* O Battle não trava mais em um caso raro de fim de partida.
* O Battle agora reproduz sons mais claros para lutadores destruídos, jogadores eliminados e vitória na partida.

Segunda-feira, 13 de abril de 2026

Novas Adições:

* O Battle foi adicionado com documentação para iniciantes.
* O Battle está totalmente localizado em inglês e vietnamita.
* Dispositivos móveis agora permitem que os jogadores desativem a auto-vocalização e usem o leitor de tela do sistema do dispositivo.
* Os dispositivos móveis mostram botões padrão na tela para chat e atalhos quando a auto-vocalização está desativada.

Correções de bugs:

* Os sons de entrada na mesa não são mais reproduzidos incorretamente imediatamente após o término de uma rodada de jogo.
* Espectadores de Backgammon não recebem mais mensagens falsas de detentor do cubo de redobro.
* O Crazy Eights não permite mais que um jogador jogue outra carta imediatamente após mudar o naipe com um 8 curinga.

Sábado, 11 de abril de 2026

Novas Adições:

* O aplicativo móvel PlayAural foi lançado para Android.
* O aplicativo móvel inclui auto-vocalização integrada para jogar sem o leitor de tela do sistema.

Quinta-feira, 9 de abril de 2026

Novas Adições:

* O Color Game foi adicionado com documentação para iniciantes.
* O Color Game está totalmente localizado em inglês e vietnamita.

Correções de bugs:

* O Tien Len agora classifica as cartas do menor para o maior e fornece feedback de jogada inválida mais claro.
* O Pusoy Dos agora classifica as cartas do menor para o maior.
* Os bots do Ninety Nine agora tomam decisões mais naturais.

Terça-feira, 7 de abril de 2026

Novas Adições:

* O Tien Len foi adicionado com variantes de regras do sul e do norte.
* O Tien Len está totalmente localizado em inglês e vietnamita.

Segunda-feira, 6 de abril de 2026

Novas Adições:

* O Bunko foi adicionado com regras completas e documentação para iniciantes.
* O Bunko está totalmente localizado em inglês e vietnamita.

Sexta-feira, 3 de abril de 2026

Novas Adições:

* O Sorry! foi adicionado com regras completas e documentação para iniciantes.
* O Sorry! está totalmente localizado em inglês e vietnamita.

Quinta-feira, 2 de abril de 2026

Novas Adições:

* Jogadores substituídos por um bot podem recuperar seu assento original por meio de convites ou do menu de entrada.
* Entrar em uma nova mesa enquanto já está em um jogo agora deixa a partida atual com segurança primeiro.

Correções de bugs:

* A visibilidade de mesas privadas e a troca de mesas são mais confiáveis.
* A inicialização e a confiabilidade de tempo de execução do Windows foram melhoradas.

Quarta-feira, 1 de abril de 2026

Novas Adições:

* O Xadrez foi adicionado com regras completas e documentação.
* O Backgammon foi adicionado com regras completas e documentação.
* O Xadrez inclui predefinições de relógio, ofertas de empate, solicitações de anulação e detecção automática de empate.
* O Backgammon inclui o cubo de redobro e regras de torneio internacional.
* O Xadrez está totalmente localizado em inglês e vietnamita.
* O Backgammon está totalmente localizado em inglês e vietnamita.

Terça-feira, 31 de março de 2026

Novas Adições:

* O Ludo foi adicionado com regras completas e documentação detalhada.
* O Ludo usa terminologia natural em inglês e vietnamita.

Domingo, 29 de março de 2026

Novas Adições:

* A lista de usuários online agora exibe o idioma atual de cada jogador.
* Os bots do Coup agora se lembram de padrões de jogo, blefam estrategicamente, adaptam-se às fases do jogo e lutam com mais afinco para sobreviver.

Correções de bugs:

* Os status online da lista de amigos agora lidam com a capitalização de nomes de usuário de forma consistente.
* Logins duplicados causados por diferentes capitalizações de nomes de usuário são bloqueados.
* A lista de usuários online agora foca na primeira pessoa em vez do botão Voltar.
* Os jogadores do Coup agora são eliminados corretamente após perderem todas as cartas de influência.
* As contagens de troca do Coup agora funcionam corretamente quando o baralho está quase vazio.
* O foco do computador permanece mais estável em listas de atualização automática, como Amigos.
* A tecla Escape no computador agora funciona de forma mais confiável após atualizações de menu em segundo plano.
* O gerenciamento de cursor da web agora mantém a navegação da lista estável durante atualizações automáticas.

Sexta-feira, 27 de março de 2026

Novas Adições:

* Os botões de ação de pôquer na web foram reordenados para que as ações móveis importantes fiquem mais fáceis de alcançar.
* Ações inválidas de pôquer agora fornecem feedback mais claro.
* Vários botões de pôquer foram renomeados de Revelar para Ler para maior clareza.
* Os anúncios da primeira e segunda rodada de apostas do Five Card Draw agora são distintos.

Correções de bugs:

* Texas Hold'em e Five Card Draw agora ocultam os botões de ação Desistir, Pagar, Aumentar e semelhantes após o término de uma mão ou durante o confronto.
* Os limites de apostas de pôquer agora permitem que um jogador vá totalmente all-in.
* Os anúncios de pôquer agora usam gramática mais clara e relatam o lucro real de pote não contestado.
* O Five Card Draw agora anuncia a fase de apostas antes de anunciar de quem é o turno.
* Os anúncios de vencedores de pôquer agora usam o canal de som de jogo correto.

Quarta-feira, 25 de março de 2026

Novas Adições:

* O PlayAural foi lançado como uma plataforma de jogos online voltada para áudio para jogadores cegos.
* O primeiro lançamento incluiu 25 jogos em famílias de jogos de cartas, dados, estratégia e sociais.
* O cliente de computador foi lançado com suporte nativo a leitor de tela e baixa latência.
* O cliente web foi lançado com um layout amigável para dispositivos móveis.
* O suporte a inglês e vietnamita foi lançado em toda a plataforma.
* As contas de jogadores foram lançadas com progresso salvo, classificações de habilidade, amigos e chat.
* O modo espectador foi lançado para ouvir mesas ativas.
* Atalhos de teclado para computador e layouts de botão amigáveis para dispositivos móveis foram lançados.
