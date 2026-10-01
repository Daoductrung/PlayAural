auth-username-password-required = Nome de usuário e senha são obrigatórios.
auth-registration-success = Cadastro realizado com sucesso! Agora você pode fazer login com suas credenciais.
auth-username-taken = Nome de usuário já em uso. Escolha um nome de usuário diferente.
auth-registration-error = Falha no cadastro devido a um erro no servidor. Tente novamente.
auth-error-wrong-password = Senha incorreta.
auth-error-user-not-found = O usuário não existe.
username-ambiguous = Mais de uma conta antiga corresponde a "{ $username }". Insira a grafia exata registrada.
auth-kicked-logged-in-elsewhere = Você foi desconectado porque sua conta foi acessada em outro dispositivo.

chat-global = { $player } diz globalmente: { $message }

admin-smtp-updated-success = Configuração SMTP atualizada com sucesso
admin-smtp-settings = Configurações SMTP
email-reset-subject = Código de redefinição de senha do PlayAural
email-reset-body = Olá { $username },\n\nVocê solicitou a redefinição de senha para sua conta no PlayAural.\nSeu código de redefinição de 6 dígitos é: { $code }\n\nEste código expirará em 15 minutos.\nSe você não solicitou isso, ignore este e-mail.
email-reset-body-html = <p>Olá, { $username },</p>
    <p>Recebemos uma solicitação para redefinir a senha da sua conta no PlayAural.</p>
    <p>Seu código de recuperação de 6 dígitos é:</p>
    <h2>{ $code }</h2>
    <p>Este código expirará exatamente em 15 minutos.</p>
    <p>Se você não solicitou isso, ignore este e-mail. Sua conta permanece segura.</p>
    <p>Atenciosamente,<br>Trung</p>
email-test-subject = Teste de SMTP do PlayAural
email-test-body = Este é um e-mail de teste do servidor PlayAural para verificar sua configuração de SMTP.
email-test-body-html = <p>Olá,</p>
    <p>Este é um e-mail de teste do servidor PlayAural.</p>
    <p>Se você está lendo isso, sua configuração de SMTP está enviando e-mails em HTML com sucesso.</p>
smtp-test-sending = Testando conexão, aguarde...
smtp-test-success = E-mail de teste enviado com sucesso para { $email }!
smtp-test-failed = Falha ao enviar e-mail de teste: { $error }
smtp-host = Host: { $value }
smtp-port = Porta: { $value }
smtp-username = Nome de usuário: { $value }
smtp-password = Senha: { $value }
smtp-from-email = E-mail de remetente: { $value }
smtp-from-name = Nome de remetente: { $value }
smtp-encryption = Criptografia: { $value }
smtp-test-connection = Testar Conexão
smtp-not-set = Não definido
smtp-prompt-host = Insira o Host SMTP (ex: smtp.gmail.com):
smtp-prompt-port = Insira a Porta SMTP (ex: 587 ou 465):
smtp-prompt-username = Insira o Nome de usuário SMTP:
smtp-prompt-password = Insira a Senha SMTP:
smtp-prompt-from-email = Insira o endereço de E-mail de remetente:
smtp-prompt-from-name = Insira o Nome de remetente (ex: Suporte PlayAural):
smtp-prompt-test-email = Insira o endereço de e-mail de destino para o teste:
smtp-enc-none = Sem criptografia
smtp-enc-ssl = Usar SSL
smtp-enc-tls = Ativar criptografia TLS automaticamente (STARTTLS)
smtp-current-enc = * { $value }

play = Jogar
view-active-tables = Ver mesas ativas
options = Opções
logout = Sair
back = Voltar
go-back = Voltar
context-menu = Menu de contexto.
no-actions-available = Nenhuma ação disponível.
table-new-host-promoted = { $player } agora é o host da mesa.
return-to-table = Retornar à mesa
create-table = Criar uma nova mesa
leave-table = Sair da mesa
start-game = Iniciar jogo
add-bot = Adicionar bot
remove-bot = Remover bot
actions-menu = Menu de ações
save-table = Salvar mesa
whose-turn = De quem é a vez
whos-at-table = Quem está na mesa
check-scores = Ver placar
check-scores-detailed = Pontuações detalhadas

game-player-skipped = A vez de { $player } foi pulada.

table-created = { $host } criou uma nova mesa de { $game }.
table-created-broadcast = { $host } criou uma nova mesa de { $game }.
table-joined = { $player } entrou na mesa.
table-left = { $player } saiu da mesa.
new-host = { $player } agora é o host.
waiting-for-players = Aguardando jogadores. Mínimo de {$min}, máximo de { $max }.
game-starting = O jogo está começando!
table-listing-game-composition-status = { $game } [{ $status }]: mesa de { $host }. { $composition }.
table-composition-human-players = { $count } { $count ->
    [one] jogador
   *[other] jogadores
}: { $names }
table-composition-bots = { $count } { $count ->
    [one] bot
   *[other] bots
}
table-composition-spectators = { $count ->
    [one] Espectador
   *[other] Espectadores
}: { $names }
table-composition-spectators-more = Espectadores: { $names }; e mais { $remaining }
table-composition-spectator-host = { $host } (host)
table-composition-two = { $first }; { $second }
table-composition-three = { $first }; { $second }; { $third }
table-composition-empty = sem participantes
table-status-waiting = Aguardando
table-status-playing = Jogando
table-status-finished = Finalizado
table-not-exists = A mesa não existe mais.
table-full = A mesa está cheia.
table-closed-disconnect-timeout = A mesa foi fechada porque nenhum jogador ativo retornou dentro de { $minutes } minutos.
player-replaced-by-bot = { $bot } está jogando no lugar de { $player }.
player-reclaimed-from-bot = { $player } retornou e reassumiu o lugar { GENDER_TERM($player_gender, "possessive-determiner") } que estava com { $bot }.
spectator-joined = Entrou na mesa de { $host } como espectador.

spectate = Assistir
now-playing = { $player } agora está jogando.
now-spectating = { $player } agora está assistindo.
spectator-left = { $player } parou de assistir.

welcome = Bem-vindo ao PlayAural!
goodbye = Até logo!

user-online = { $player } ficou online.
user-offline = { $player } ficou offline.
friend-online = Seu amigo { $player } agora está online.
friend-offline = Seu amigo { $player } ficou offline.
permission-denied = Você não tem permissão para realizar esta ação contra um Desenvolvedor.
kick-user = Expulsar Usuário
kick-broadcast = { $target } foi expulso por { $actor }.
user-not-online = O usuário { $target } não está online.
kick-confirm = Tem certeza de que deseja expulsar { $player }?
no-users-to-kick = Nenhum usuário disponível para expulsar.
usage-kick = Uso: /kick <nome_de_usuário>
online-users-none = Nenhum usuário online.
online-users-summary = { $count ->
    [one] { $count } usuário online. { $groups }
   *[other] { $count } usuários online. { $groups }
}
online-users-group = { $role ->
    [dev] { $count ->
        [one] { $count } desenvolvedor: { $users }.
       *[other] { $count } desenvolvedores: { $users }.
    }
    [admin] { $count ->
        [one] { $count } administrador: { $users }.
       *[other] { $count } administradores: { $users }.
    }
   *[user] { $staff_count ->
        [0] { $users }.
       *[other] { $count ->
            [one] { $count } usuário: { $users }.
           *[other] { $count } usuários: { $users }.
        }
    }
}
online-users-more = mais { $count }
online-user-waiting-approval = Aguardando aprovação
presence-status-main-menu = Menu principal
presence-status-waiting-table = Aguardando na mesa de { $game }
presence-status-playing = Jogando { $game }
presence-status-spectating = Assistindo a { $game }
presence-status-watching-table = Observando a mesa de { $game }
presence-status-reviewing-results = Revisando resultados de { $game }
presence-status-spectating-results = Assistindo aos resultados de { $game }
user-role-dev = Desenvolvedor
user-role-admin = Administrador
user-role-user = Usuário
client-type-web = Web
client-type-python = Desktop
client-type-mobile = Celular
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
user-not-online-anymore = Este usuário não está mais online.
close-menu = Fechar

language = Idioma
language-option = Idioma: { $language }
language-changed = Idioma definido para { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. Idioma oficial do PlayAural. Tradutores: { $translators }.
       *[false] { $language }. Tradução da comunidade. Tradutores: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. Metadados do tradutor indisponíveis.
language-menu-current-entry = Atual: { $entry }

option-on = Ligado
option-off = Desligado

# Multi-select option sub-menu controls
option-back = Voltar
option-select-all = Selecionar todos
option-deselect-all = Desmarcar todos
option-selected-count = { $count } selecionado(s)
option-deselected-count = { $count } desmarcado(s)
option-min-selected = Você deve selecionar pelo menos { $count }.
option-max-selected = Você pode selecionar no máximo { $count }.

custom-bot-names-option = Nomes de bot personalizados: { $status }
option-notify-table-created = Notificar quando mesa for criada: { $status }
option-notify-user-presence = Notificações de usuário online/offline: { $status }
option-notify-friend-presence = Notificações de amigo online/offline: { $status }
dice-keeping-style-option = Estilo de retenção de dados: { $style }
dice-keeping-style-changed = Estilo de retenção de dados definido para { $style }.
dice-keeping-style-indexes = Índices de dados
dice-keeping-style-values = Valores de dados

# Personal options split: general vs game options
general-options = Opções gerais
game-options = Opções de jogo

# Game Options (declarative preferences with per-game overrides)
pref-category-display = Exibição
pref-set-brief-announcements = Anúncios breves: { $status }
pref-changed-brief-announcements = Anúncios breves { $status }.
pref-desc-brief-announcements = Encurta os anúncios de jogadas e eventos no jogo; desative para narração falada mais completa.
pref-category-sounds = Sons
pref-category-gameplay = Jogabilidade
pref-category-dice = Dados
pref-default = Padrão
pref-per-game-for = { $game }: { $value }
pref-reset-all = Redefinir todas as opções de jogo
pref-reset-category = Redefinir opções de { $category }
pref-reset-done = Opções de jogo redefinidas.
pref-set-play-turn-sound = Som de turno: { $status }
pref-set-confirm-destructive-actions = Confirmar ações arriscadas: { $status }
pref-set-allow-custom-bot-names = Nomes de bot personalizados: { $status }
pref-set-clear-kept-on-roll = Limpar dados guardados ao rolar: { $status }
pref-set-dice-keeping-style = Estilo de retenção de dados: { $choice }
pref-changed-play-turn-sound = Som de turno { $status }.
pref-changed-confirm-destructive-actions = Confirmar ações arriscadas { $status }.
pref-changed-allow-custom-bot-names = Nomes de bot personalizados { $status }.
pref-changed-clear-kept-on-roll = Limpar dados guardados ao rolar { $status }.
pref-changed-dice-keeping-style = Estilo de retenção de dados definido para { $choice }.
pref-desc-play-turn-sound = Toca um som quando for a sua vez.
pref-desc-confirm-destructive-actions = Pede confirmação antes de ações arriscadas ou irreversíveis, como passar a vez no Pusoy Dos.
pref-desc-allow-custom-bot-names = Permite definir nomes personalizados para os bots que você adicionar a uma mesa.
pref-desc-clear-kept-on-roll = Em jogos de dados compatíveis, como Yahtzee, libera todos os dados guardados após cada rolagem. Sua próxima rolagem rola todos os dados novamente, a menos que você guarde alguns; com Valores de dados, use Shift+1-6 para guardar dados correspondentes.
pref-desc-dice-keeping-style = Índices de dados: use de 1 a 5 (ou 1 a 6 no Midnight) para alternar dados por posição. Valores de dados: use de 1 a 6 para liberar um dado guardado com esse valor de face e Shift+1-6 para guardar um dado liberado correspondente. Durante a fase de troca do Tradeoff, de 1 a 6 guarda um dado correspondente e Shift+1-6 marca um para troca; durante a fase de captação, de 1 a 6 simples pega um dado correspondente do pool.

cancel = Cancelar
enter-bot-name = Insira o nome do bot
bot-name-invalid-length = Os nomes dos bots devem ter entre 3 e 30 caracteres.
bot-name-invalid-characters = Os nomes dos bots só podem conter letras, números e espaços.
table-name-already-used = Um jogador ou bot com este nome já está nesta mesa.
no-options-available = Nenhuma opção disponível.
no-scores-available = Nenhuma pontuação disponível.

option-desc-generic = { $label }. Padrão: { $default }.
option-desc-integer = { $label }. Insira um número inteiro de { $min } a { $max }. Padrão: { $default }.
option-desc-number = { $label }. Insira um número de { $min } a { $max }. Padrão: { $default }.
option-desc-menu = { $label }. Escolha um entre: { $choices }. Padrão: { $default }.
option-desc-bool = { $label }. Ative este item para ligar ou desligar a configuração. Padrão: { $default }.
option-desc-multiselect = { $label }. Selecionados agora: { $selected }. Seleções mínimas: { $min }. Seleções máximas: { $max }. Selecionados por padrão: { $default }.
option-desc-no-choices = nenhuma escolha disponível no momento
option-desc-none-selected = nenhum
option-desc-no-maximum = sem máximo
menu-item-with-hint = { $label }: { $hint }

general-desc-profile = Visualize e edite os detalhes do seu perfil público.
general-desc-friends = Gerencie amigos, solicitações de amizade, mensagens privadas e ações de mesa de amigos.
general-desc-my-stats = Revise suas vitórias, derrotas, classificações e estatísticas de jogos suportados.
general-desc-general-options = Ajuste idioma, chat global, áudio, acessibilidade, notificações e preferências de jogo.
general-desc-game-options = Ajuste preferências de jogabilidade que podem se aplicar globalmente ou a jogos suportados.
general-desc-language = Escolha o idioma usado pelos menus, mensagens e documentação do servidor quando disponível.
general-desc-audio = Ajuste volume de música, efeitos sonoros, ambiente, chat de voz, sons de digitação e configurações de dispositivo de entrada de áudio.
general-desc-accessibility = Ajuste leituras relacionadas à acessibilidade, entrada e comportamento do cliente disponíveis neste dispositivo.
general-desc-notifications = Escolha quais notificações de chat, presença e criação de mesa você deseja ouvir.
general-desc-music-volume = Altere o volume da música de fundo. Definir como Desligado silencia a música.
general-desc-sound-volume = Altere o volume dos efeitos sonoros do jogo. Os efeitos sonoros permanecem em pelo menos dez porcento para que dicas importantes continuem audíveis.
general-desc-ambience-volume = Altere o volume do ambiente de fundo. Definir como Desligado silencia o ambiente.
general-desc-voice-volume = Altere o volume de reprodução do chat de voz da mesa.
general-desc-audio-input-device = Escolha o microfone ou dispositivo de entrada usado pelo cliente de desktop para o chat de voz.
general-desc-play-typing-sounds = Toca pequenos sons de digitação ao inserir texto nos campos de edição do cliente.
general-desc-web-speech-settings = Configure a saída de fala do navegador, incluindo modo ARIA live ou Web Speech, velocidade da fala e voz.
general-desc-mobile-speech-settings = Configure o motor de texto para fala (TTS), voz e velocidade da fala no celular.
general-desc-invert-multiline-enter = Troca o comportamento de envio e nova linha para campos de texto multilinha no cliente de desktop.
general-desc-menu-hints = Mostra descrições disponíveis diretamente nas linhas do menu. Quando desligado, foque um item com descrição e pressione F1 no Desktop ou na Web com um teclado físico, ou toque uma vez com três dedos no modo de auto-vocalização móvel para ouvi-la.
general-desc-mute-global-chat = Impede que mensagens do chat global sejam lidas automaticamente em voz alta.
general-desc-global-chat-channel = Escolha o canal de idioma usado para enviar e receber mensagens no chat global. Um canal é obrigatório mesmo quando o chat global está ativado.
general-desc-mute-table-chat = Impede que mensagens do chat da mesa sejam lidas automaticamente em voz alta.
general-desc-notify-user-presence = Anuncia quando os usuários entram ou saem do modo online.
general-desc-notify-friend-presence = Anuncia quando seus amigos entram ou saem do modo online.
general-desc-notify-table-created = Anuncia quando uma nova mesa pública é criada.
general-desc-speech-mode = Escolha se o cliente web envia anúncios para o leitor de tela através de ARIA live ou os fala com a API Web Speech do navegador.
general-desc-speech-rate = Altere a velocidade da fala do cliente web.
general-desc-speech-voice = Escolha a voz usada pela API Web Speech do cliente web ou retorne ao padrão do navegador.
general-desc-mobile-tts-engine = Escolha o motor de texto para fala móvel. Atualmente, o Android usa o motor gerenciado pelo sistema.
general-desc-mobile-tts-voice = Escolha a voz de texto para fala móvel ou retorne ao padrão do sistema.
general-desc-mobile-tts-rate = Altere a velocidade de texto para fala no celular.

saved-tables = Mesas Salvas
no-saved-tables = Você não tem mesas salvas.
no-active-tables = Nenhuma mesa ativa.
no-active-tables-all = Nenhuma mesa ativa disponível.
no-active-tables-waiting = Nenhuma mesa aguardando disponível.
no-active-tables-playing = Nenhuma mesa jogando disponível.
active-tables-filter = Filtro: { $filter }
filter-name-all = Todos
filter-name-waiting = Aguardando
filter-name-playing = Jogando
game-category-filter = Categoria: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = Todos
game-category-cards = Jogos de Cartas
game-category-poker = Jogos de Pôquer
game-category-dice = Jogos de Dados
game-category-board = Jogos de Tabuleiro
game-category-arcade = Jogos de Fliperama
game-category-misc = Diversos
no-games-in-category = Nenhum jogo disponível nesta categoria.
restore-table = Restaurar
delete-saved-table = Excluir
saved-table-deleted = Mesa salva excluída.
missing-players = Não é possível restaurar: estes jogadores não estão disponíveis: { $players }
saved-table-blocked-by-you = Esta mesa salva inclui jogadores que você bloqueou: { $players }. Para restaurá-la, abra Pessoal e Opções, Amigos e depois Usuários Bloqueados e desbloqueie-os. A restauração só pode prosseguir se o contato social direto estiver disponível para todos. A mesa salva foi mantida.
saved-table-social-blocked = Esta mesa salva não pode ser restaurada porque o contato social direto não está disponível entre você e: { $players }. A mesa salva foi mantida.
saved-table-social-blocked-mixed = Esta mesa salva inclui jogadores que você bloqueou: { $blocked }. Abra Pessoal e Opções, Amigos e depois Usuários Bloqueados e desbloqueie-os. O contato social direto também não está disponível com: { $unavailable }. A mesa salva foi mantida.
saved-table-invalid = Esta mesa salva não pode mais ser restaurada porque seus dados de jogo ou de jogadores estão incompletos ou são incompatíveis. A mesa salva foi mantida.
table-restored = Mesa restaurada! Todos os jogadores foram transferidos.
table-saved-destroying = Mesa salva! Retornando ao menu principal.
game-type-not-found = O tipo de jogo não existe mais.

action-not-your-turn = Não é a sua vez.
action-not-playing = O jogo não começou.
action-spectator = Espectadores não podem fazer isso.
action-not-host = Apenas o host pode fazer isso.
action-not-available = Essa ação não está disponível no momento.
action-game-in-progress = Não é possível fazer isso enquanto o jogo está em andamento.
action-need-more-players = São necessários mais jogadores para iniciar.
action-table-full = A mesa está cheia.
action-start-needs-more-players = Não é possível iniciar. Jogadores ativos: { $current }. Mínimo necessário: { $minimum }.
action-start-has-too-many-players = Não é possível iniciar. Jogadores ativos: { $current }. Máximo permitido: { $maximum }.
action-start-requires-exact-players = Não é possível iniciar. Jogadores ativos: { $current }. Necessário: exatamente { $required }.
action-start-needs-human-player = Não é possível iniciar apenas com bots. Pelo menos um humano deve participar como jogador. Mude de espectador para jogador; se a mesa estiver cheia, remova um bot primeiro.
action-no-bots = Não há bots para remover.
action-bots-cannot = Os bots não podem fazer isso.
options-category-audio = Áudio
options-category-accessibility = Acessibilidade
options-category-notifications = Notificações
music-volume-option = Volume da Música: { $value }%
sound-volume-option = Volume dos Efeitos Sonoros: { $value }%
ambience-volume-option = Volume do Ambiente: { $value }%
voice-volume-option = Volume do Chat de Voz: { $value }%
volume-choice-off = Desligado
volume-choice-percent = { $value }%
volume-choice-current = { $label } (atual)
audio-input-device-option = Dispositivo de Entrada de Áudio: { $device }
audio-input-device-default = Dispositivo de Entrada Padrão do Sistema

mute-global-chat-option = Silenciar Chat Global: { $status }
global-chat-channel-option = Idioma do Chat Global: { $channel }
global-chat-channel-none = Nenhum canal selecionado
global-chat-channel-none-current = Nenhum canal selecionado (atual)
global-chat-channel-name = { $language }
global-chat-channel-recommended = { $language } (recomendado para o idioma da sua interface)
global-chat-channel-current = { $language } (atual)
global-chat-channel-current-recommended = { $language } (atual, recomendado para o idioma da sua interface)
global-chat-channel-selected = Idioma do chat global definido como { $language }. O chat global não é monitorado em tempo real. Se alguém usar palavrões ou insultar você, bloqueie essa pessoa. Denuncie abusos graves ou repetidos para análise posterior.
global-chat-channel-cleared = Nenhum idioma de chat global está selecionado. Você não enviará nem receberá mensagens globais.
mute-table-chat-option = Silenciar Chat da Mesa: { $status }
invert-multiline-enter-option = Inverter Comportamento da Tecla Enter: { $status }
menu-hints-option = Dicas de Menu: { $status }
menu-hints-changed = As dicas de menu agora estão { $status }.
play-typing-sounds-option = Tocar Sons de Digitação: { $status }
invalid-volume = Volume inválido.

dice-not-rolled = Você ainda não rolou os dados.
dice-no-dice = Nenhum dado disponível.
table-no-players = Nenhum jogador.
table-players-one = { $count } jogador: { $players }.
table-players-many = { $count } jogadores: { $players }.
table-spectators = Espectadores: { $spectators }.
table-host-suffix = (Host)
table-voice-chat-suffix = (no chat de voz)
table-members-summary-compact = Resumo da mesa: { $composition }.
table-summary-human-players = { $count } { $count ->
    [one] jogador humano
   *[other] jogadores humanos
}
table-summary-bots = { $count } { $count ->
    [one] bot
   *[other] bots
}
table-summary-spectators = { $count } { $count ->
    [one] espectador
   *[other] espectadores
}
table-members-empty = Nenhum membro da mesa listado no momento. Use Voltar para retornar e atualizar a visualização da mesa.
table-member-entry = { $player }: { $status }
table-member-status-host = Host
table-member-status-player = Jogador
table-member-status-spectator = Espectador
table-member-status-bot = Bot
table-member-status-online = Online
table-member-status-offline = Offline
table-member-status-voice-chat = no chat de voz
table-member-status-bot-takeover = bot jogando no lugar { GENDER_TERM($member_gender, "possessive-determiner") }: { $bot }
table-member-no-actions = Nenhuma ação disponível para { $player }.
table-member-left = Essa pessoa não está mais nesta mesa.
table-member-bot-left = Esse bot não está mais nesta mesa.
game-over = Fim de Jogo
game-final-scores = Pontuações Finais
game-points = { $count } { $count ->
    [one] ponto
   *[other] pontos
}

leaderboards = Placar de Líderes
leaderboard-no-data = Ainda não há dados de placar para este jogo.

leaderboard-type-wins = Líderes em Vitórias
leaderboard-type-rating = Classificação de Habilidade
leaderboard-type-total-score = Pontuação Total
leaderboard-type-high-score = Pontuação Máxima
leaderboard-type-games-played = Jogos Disputados
leaderboard-type-avg-points-per-turn = Média de Pontos por Turno
leaderboard-type-best-single-turn = Melhor Turno Único
leaderboard-type-score-per-round = Pontuação por Rodada
leaderboard-type-most-enemies-defeated = Mais Inimigos Derrotados
leaderboard-type-deepest-wave-reached = Onda Mais Profunda Alcançada


leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] vitória
   *[other] vitórias
} { $losses } { $losses ->
    [one] derrota
   *[other] derrotas
}, { $percentage }% de aproveitamento
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } jogos
leaderboard-avg-entry = { $rank }. { $player }: { $value }

leaderboard-no-player-stats = Você ainda não jogou este jogo.

leaderboard-no-ratings = Ainda não há dados de classificação para este jogo.
leaderboard-rating-entry = { $rank }. { $player }: classificação { $rating }
leaderboard-no-player-rating = Você ainda não tem uma classificação para este jogo.

my-stats = Minhas Estatísticas
my-stats-select-game = Selecione um jogo para ver suas estatísticas
my-stats-no-data = Você ainda não jogou este jogo.
my-stats-no-games = Você ainda não jogou nenhum jogo.
my-stats-header = { $game } - Suas Estatísticas
my-stats-wins = Vitórias: { $value }
my-stats-losses = Derrotas: { $value }
my-stats-winrate = Taxa de vitórias: { $value }%
my-stats-games-played = Jogos disputados: { $value }
my-stats-total-score = Pontuação total: { $value }
my-stats-high-score = Pontuação máxima: { $value }
my-stats-rating = Classificação de habilidade: { $value }
my-stats-no-rating = Sem classificação de habilidade ainda
my-stats-avg-per-turn = Média de pontos por turno: { $value }
my-stats-best-turn = Melhor turno único: { $value }
my-stats-score-per-round = Pontuação por rodada: { $value }
my-stats-most-enemies-defeated = Mais Inimigos Derrotados: { $value }
my-stats-deepest-wave-reached = Onda Mais Profunda Alcançada: { $value }

confirm-leave-game = Tem certeza de que deseja sair da mesa?
confirm-yes = Sim
confirm-no = Não

administration = Administração

admin-moderation = Moderação de Chat
admin-moderation-global-chat-toggle = Chat global: { $status }
admin-moderation-global-chat-toggle-description = Liga ou desliga o envio de mensagens em todos os canais de idioma do chat global. Esta configuração persiste após reiniciar o servidor.
admin-moderation-global-chat-status-description = Estado atual em todo o servidor. Apenas um Desenvolvedor pode alterar esta configuração.
admin-moderation-global-chat-update-failed = A configuração do chat global não pôde ser salva, então nenhuma alteração foi feita. Tente novamente.
global-chat-availability-enabled = O chat global foi ativado pelo desenvolvedor. Selecione um canal de idioma antes de enviar ou receber mensagens globais.
global-chat-availability-disabled = O chat global foi temporariamente desativado pelo desenvolvedor.
admin-moderation-section-reports = Denúncias
admin-moderation-open-reports = Denúncias abertas: { $count }
admin-moderation-closed-reports = Denúncias fechadas: { $count }
admin-moderation-all-reports = Todas as denúncias retidas: { $count }
admin-moderation-section-messages = Histórico de mensagens globais
admin-moderation-browse-messages = Navegar e filtrar todas as mensagens globais
admin-moderation-find-history = Encontrar histórico do chat global por nome de usuário exato
admin-moderation-retained-summary = Evidências retidas: { $messages } mensagens globais e { $closed } denúncias fechadas.
admin-moderation-section-retention = Exclusão permanente
admin-moderation-clear-history = Limpar todas as mensagens retidas do chat global ({ $count })
admin-moderation-clear-closed-reports = Limpar todas as denúncias fechadas ({ $count })
admin-moderation-open-report-list = Denúncias abertas, mais recentes primeiro
admin-moderation-closed-report-list = Denúncias fechadas, mais recentes primeiro
admin-moderation-all-report-list = Todas as denúncias retidas, mais recentes primeiro
admin-moderation-report-row = Denúncia nº { $id }, enviada em { $time }. Usuário denunciado: { $target }, ID { $target_id }. Motivo: { $reason }. Denunciante: { $reporter }. Status: { $status }.
admin-moderation-no-reports = Nenhuma denúncia corresponde a esta visualização.
admin-moderation-value-unknown = desconhecido
admin-moderation-status-open = aberta
admin-moderation-status-reviewed = revisada
admin-moderation-status-dismissed = descartada
admin-moderation-status-actioned = ação registrada
admin-moderation-status-unknown = desconhecido
admin-moderation-report-unavailable = Esta denúncia não existe mais. Outro desenvolvedor pode tê-la limpado.
admin-moderation-report-id = ID da denúncia: { $id }
admin-moderation-report-time = Enviada em: { $time }
admin-moderation-report-status = Status: { $status }
admin-moderation-report-origin = Origem: { $origin }
admin-moderation-origin-manual = enviada por um usuário
admin-moderation-origin-automatic = gerada automaticamente pelo Sistema
admin-moderation-report-reporter = Denunciante: { $username }. ID da conta: { $uuid }
admin-moderation-report-target = Usuário denunciado: { $username }. ID da conta: { $uuid }
admin-moderation-report-reason = Motivo: { $reason }
admin-moderation-report-channel = Canal de contexto do chat global: { $channel }
admin-moderation-report-scope = Detectado em: { $scope }
admin-moderation-scope-global = chat global
admin-moderation-scope-table = chat da mesa
admin-moderation-detection-rate-limited = mensagens enviadas rápido demais
admin-moderation-detection-repeated-message = mensagens repetidas correspondentes
admin-moderation-automatic-evidence = Gerada automaticamente pelo Sistema apenas para análise manual; nenhuma penalidade foi aplicada. Em { $scope }, o detector observou { $incidents } incidentes separados de spam e rejeitou { $rejected } tentativas durante uma janela de observação de { $window }. { $accepted } mensagens recentes foram aceitas. Detecção: { $detection }. Última mensagem rejeitada: { $sample }
admin-moderation-automatic-evidence-unavailable = Esta denúncia foi gerada automaticamente pelo Sistema apenas para análise manual, e nenhuma penalidade foi aplicada. Suas evidências estruturadas de detecção estão indisponíveis ou são de uma versão não suportada.
admin-moderation-report-anchor = ID da mensagem de âncora de contexto salva: { $id }
admin-moderation-report-anchor-unavailable = Nenhuma mensagem de âncora de contexto salva está disponível. A conta denunciada pode não ter enviado uma mensagem retida neste canal, ou o histórico do chat pode ter sido limpo.
admin-moderation-report-details = Detalhes adicionais: { $details }
admin-moderation-report-review = Revisada por { $reviewer }, ID da conta { $reviewer_id }, em { $time }.
admin-moderation-view-context = Ver conversa ao redor do horário da denúncia
admin-moderation-view-target-history = Ver todas as mensagens globais retidas do ID da conta denunciada
admin-moderation-mark-reviewed = Marcar como revisada sem penalidade registrada
admin-moderation-dismiss-report = Descartar denúncia
admin-moderation-mark-actioned = Marcar ação registrada. Isto não aplica uma penalidade.
admin-moderation-context-heading = Contexto da denúncia nº { $id }, enviada em { $time }. Canal: { $channel }. As mensagens estão em ordem cronológica; mensagens do usuário denunciado são identificadas explicitamente.
admin-moderation-context-message = { $username }: { $message } Mensagem nº { $id }, enviada em { $time }. ID da conta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-target-message = Usuário denunciado { $username }: { $message } Mensagem nº { $id }, enviada em { $time }. ID da conta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-anchor-message = Mensagem ancorada do usuário denunciado { $username }: { $message } Mensagem nº { $id }, enviada em { $time }. ID da conta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-empty = Nenhuma mensagem global retida permanece ao redor do horário desta denúncia.
admin-moderation-history-prompt = Insira o nome de usuário exato cujo histórico retido do chat global você quer encontrar. IDs de conta históricos com o mesmo nome de usuário serão listados separadamente.
admin-moderation-sender-results-heading = Identidades de remetente retidas que correspondem ao nome de usuário exato "{ $username }".
admin-moderation-sender-result = { $username }, ID da conta { $uuid }. { $count } mensagens de { $first } até { $last }.
admin-moderation-no-sender-history = Nenhum histórico retido do chat global corresponde ao nome de usuário exato "{ $username }".
admin-moderation-history-heading = Histórico retido do chat global para { $username }, ID da conta { $uuid }: { $count } mensagens, mais recentes primeiro.
admin-moderation-history-message = { $username }: { $message } Mensagem nº { $id }, enviada em { $time }. Idioma: { $channel }.
admin-moderation-history-empty = Nenhuma mensagem global retida permanece para este ID de conta.
admin-moderation-message-list-heading = Histórico de mensagens globais. { $count } mensagens correspondem. Ordem: { $sort }. Idioma: { $channel }. Período: { $period }. Todos os horários estão em UTC.
admin-moderation-message-row = { $username }: { $message } Mensagem nº { $id }, enviada em { $time }. ID da conta: { $uuid }. Idioma: { $channel }.
admin-moderation-message-list-empty = Nenhuma mensagem global retida corresponde a estes filtros.
admin-moderation-message-filter-sort = Ordem de classificação: { $sort }
admin-moderation-message-filter-language = Idioma: { $channel }
admin-moderation-message-filter-period = Período: { $period }
admin-moderation-message-filter-reset = Redefinir todos os filtros de mensagens
admin-moderation-message-sort-newest = mais recentes primeiro
admin-moderation-message-sort-oldest = mais antigas primeiro
admin-moderation-message-language-all = todos os idiomas
admin-moderation-message-period-all = todo o período
admin-moderation-message-period-today = hoje
admin-moderation-message-period-yesterday = ontem
admin-moderation-message-period-last-7-days = últimos 7 dias
admin-moderation-message-period-last-30-days = últimos 30 dias
admin-moderation-message-period-current-month = mês calendário atual
admin-moderation-message-period-previous-month = mês calendário anterior
admin-moderation-message-language-menu = Filtrar mensagens por idioma. O filtro atual é { $channel }.
admin-moderation-message-period-menu = Filtrar mensagens por período em UTC. O filtro atual é { $period }.
admin-moderation-message-filter-current = { $value } (atual)
admin-moderation-clear-history-confirm = Excluir permanentemente todas as { $count } mensagens retidas do chat global? Isto não pode ser desfeito. { $open } denúncias abertas permanecerão, mas suas âncoras de mensagem salvas e contexto de conversa serão removidos.
admin-moderation-clear-closed-confirm = Excluir permanentemente todas as { $count } denúncias fechadas? Denúncias abertas e o histórico do chat global permanecerão. Isto não pode ser desfeito.
admin-moderation-report-already-closed = Esta denúncia já foi fechada por outra ação de revisão. O registro atual foi recarregado.
admin-moderation-report-status-updated = A denúncia nº { $id } agora está marcada como { $status }. Nenhuma penalidade automática foi aplicada.
admin-new-manual-report = Nova denúncia de moderação nº { $id }: { $reporter } denunciou { $target }.
admin-new-automatic-report = Nova denúncia de spam do Sistema nº { $id } requer análise manual: { $target }.
admin-moderation-history-cleared = { $count } mensagens retidas do chat global foram excluídas permanentemente. Denúncias existentes permanecem sem âncoras de mensagem. Se nenhuma mensagem restar, a numeração de mensagens reiniciará em 1.
admin-moderation-closed-reports-cleared = { $count } denúncias fechadas foram excluídas permanentemente. Denúncias abertas permanecem. Se nenhuma denúncia restar, a numeração de denúncias reiniciará em 1.

admin-database-management = Gerenciamento do Banco de Dados
admin-database-management-summary = Manutenção do banco de dados apenas para Desenvolvedores. A análise é somente leitura. Backup, limpeza e compactação pausam temporariamente a jogabilidade e as alterações de conta em todo o servidor.
admin-database-backup = Fazer backup do banco de dados
admin-database-backup-confirm = Fazer backup do banco de dados agora? A jogabilidade e as alterações de conta serão pausadas enquanto o SQLite cria e verifica uma cópia de recuperação. O backup ficará retido no diretório de backups do servidor até que um operador o remova.
admin-database-backup-success = Backup do banco de dados concluído: { $filename } ({ $size }).
admin-database-backup-failed = Falha no backup do banco de dados. Nenhum backup parcial foi publicado. Verifique o log do servidor para detalhes.
admin-database-size-bytes = { $value ->
    [one] 1 byte
   *[other] { NUMBER($value, maximumFractionDigits: 0) } bytes
}
admin-database-size-kib = { NUMBER($value, maximumFractionDigits: 1) } KiB
admin-database-size-mib = { NUMBER($value, maximumFractionDigits: 1) } MiB
admin-database-size-gib = { NUMBER($value, maximumFractionDigits: 1) } GiB
admin-database-storage-analyze = Analisar candidatos à limpeza
admin-database-storage-analysis-summary = Tamanho do banco de dados: { $size }. Espaço SQLite reutilizável: { $reusable }. Registros de banco elegíveis: { $records }.
admin-database-storage-analysis-failed = A análise de armazenamento falhou sem alterar dados. Verifique o log do servidor para detalhes.
admin-database-storage-refresh-analysis = Atualizar análise de armazenamento
admin-database-storage-cleanup = Executar limpeza de armazenamento
admin-database-storage-cleanup-confirm = Executar limpeza segura de armazenamento agora? A jogabilidade e as alterações de conta serão pausadas enquanto o servidor cria e verifica um backup de segurança, remove apenas os registros transitórios ou órfãos listados e valida o resultado. O arquivo do banco de dados não será compactado.
admin-database-storage-cleanup-not-needed = A limpeza de armazenamento não é necessária. Nenhum registro de banco elegível ou arquivo temporário de backup abandonado foi encontrado.
admin-database-storage-cleanup-success = Limpeza de armazenamento concluída. Registros de banco removidos: { $records }. Arquivos temporários de backup abandonados removidos: { $files } ({ $file_size }). Espaço SQLite reutilizável: { $reusable }. Execute a compactação separadamente para reduzir o tamanho do arquivo do banco de dados. Backup de segurança: { $filename }.
admin-database-storage-cleanup-failed = Falha na limpeza de armazenamento. Qualquer backup de segurança concluído foi mantido. Verifique o log do servidor antes de tentar novamente.
admin-database-storage-no-record-candidates = Nenhum registro de banco está elegível para limpeza segura no momento.
admin-database-storage-temporary-files = Arquivos temporários de backup abandonados do PlayAural: { $count } ({ $size }).
admin-database-storage-invalid-timestamps = Aviso de segurança: { $count } registros contêm carimbos de data/hora de retenção inválidos. A limpeza nunca os classificará como expirados por adivinhação de idade; revise-os manualmente.
admin-database-storage-exclusions = Sempre excluídos da limpeza automatizada: mesas salvas, resultados de jogos, histórico do chat global, denúncias de moderação, contas de usuários, bloqueios válidos, dados ativos, estatísticas de jogos registrados, dados de compatibilidade, backups válidos e logs. Mesas salvas são removidas apenas por ação explícita do proprietário ou de um Desenvolvedor.
admin-database-storage-category-row = { $category }: { $count }
admin-database-storage-category-expired-table-checkpoints = Checkpoints transitórios de mesa expirados
admin-database-storage-category-expired-password-reset-tokens = Tokens expirados de redefinição de senha
admin-database-storage-category-expired-bans = Registros de banimento retidos por mais de { $days } dias após a expiração
admin-database-storage-category-stale-pending-friend-requests = Solicitações de amizade pendentes com mais de { $days } dias
admin-database-storage-category-orphaned-friendships = Registros de amizade órfãos
admin-database-storage-category-orphaned-user-blocks = Registros de bloqueio de usuário órfãos
admin-database-storage-category-stale-user-notifications = Notificações de usuário com mais de { $days } dias
admin-database-storage-category-orphaned-user-notifications = Registros de notificação de usuário órfãos
admin-database-storage-category-expired-mutes = Registros de silenciamento expirados
admin-database-storage-category-orphaned-mutes = Registros de silenciamento órfãos
admin-database-compact = Compactar banco de dados e recuperar espaço não usado
admin-database-compact-confirm = Compactar o banco de dados agora? A jogabilidade e as alterações de conta serão pausadas. Um backup de segurança verificado será criado antes que o SQLite reconstrua o banco de dados ativo. Esta operação exige espaço temporário substancial em disco e deve ser executada em um período calmo.
admin-database-compact-success = Compactação do banco de dados concluída. O tamanho do arquivo mudou de { $before } para { $after }; { $reclaimed } foi recuperado. Backup de segurança: { $filename }.
admin-database-compact-failed = Falha na compactação do banco de dados. O banco de dados ativo não foi alterado intencionalmente, e qualquer backup de segurança concluído foi mantido. Verifique o log do servidor para detalhes.
admin-database-maintenance-busy = Outra operação exclusiva do servidor já está ativa. Aguarde ela terminar antes de iniciar a manutenção do banco de dados.
database-maintenance-operation-backup = backup do banco de dados
database-maintenance-operation-cleanup = limpeza de armazenamento
database-maintenance-operation-compaction = compactação do banco de dados
database-maintenance-not-active = A manutenção do banco de dados não está ativa no momento.
database-maintenance-input-blocked = { $operation } do servidor em andamento. Jogabilidade, login, cadastro e alterações de conta estão temporariamente pausados. Seu menu atual continua disponível, mas ações não serão executadas até a manutenção terminar.
database-maintenance-auth-blocked = A manutenção do banco de dados do servidor está em andamento. Login, cadastro e alterações de senha estão temporariamente indisponíveis. Tente novamente após o término da manutenção.
database-maintenance-backup-started = O desenvolvedor está fazendo backup do banco de dados do servidor. A jogabilidade e as alterações de conta estão temporariamente pausadas; os menus atuais permanecem visíveis. Você será avisado quando o serviço normal for retomado.
database-maintenance-backup-completed = O backup do banco de dados do servidor foi concluído. A jogabilidade normal e o acesso às contas estão sendo retomados agora.
database-maintenance-backup-failed = O backup do banco de dados do servidor não pôde ser concluído. Nenhum backup parcial foi publicado. A jogabilidade normal e o acesso às contas estão sendo retomados agora.
database-maintenance-cleanup-started = O desenvolvedor está executando a limpeza de armazenamento do servidor. A jogabilidade e as alterações de conta estão temporariamente pausadas, mas os menus atuais permanecem visíveis. Um backup de segurança verificado está sendo criado primeiro. Você será avisado quando o serviço normal for retomado.
database-maintenance-cleanup-completed = A limpeza de armazenamento e a validação do banco de dados do servidor foram concluídas. A jogabilidade normal e o acesso às contas estão sendo retomados agora.
database-maintenance-cleanup-failed = A limpeza de armazenamento do servidor não pôde ser concluída com segurança. A jogabilidade normal e o acesso às contas estão sendo retomados agora.
database-maintenance-compaction-started = O desenvolvedor está compactando o banco de dados do servidor. A jogabilidade e as alterações de conta estão temporariamente pausadas; os menus atuais permanecem visíveis. Você será avisado quando o serviço normal for retomado.
database-maintenance-compaction-completed = A compactação do banco de dados do servidor foi concluída. A jogabilidade normal e o acesso às contas estão sendo retomados agora.
database-maintenance-compaction-failed = A compactação do banco de dados do servidor não pôde ser concluída. A jogabilidade normal e o acesso às contas estão sendo retomados sem aplicar a compactação.
database-maintenance-reopen-failed = Erro crítico de manutenção do banco de dados: o banco de dados ativo não pôde ser reaberto com segurança, então o servidor permanece congelado. Aguarde o desenvolvedor restaurar o serviço.

account-approval = Aprovação de Conta
no-pending-accounts = Nenhuma conta pendente.
approve-account = Aprovar
decline-account = Recusar
account-approved = A conta de { $player } foi aprovada.
account-declined = A conta de { $player } foi recusada e excluída.

waiting-for-approval = Sua conta está aguardando aprovação de um administrador. Aguarde...
account-approved-welcome = Sua conta foi aprovada! Bem-vindo ao PlayAural!
account-declined-goodbye = Sua solicitação de conta foi recusada.

account-action = ação de conta realizada

promote-admin = Promover a Administrador
demote-admin = Rebaixar Administrador
ban-user = Banir Usuário
unban-user = Desbanir Usuário
no-users-to-promote = Nenhum usuário disponível para promover.
no-admins-to-demote = Nenhum administrador disponível para rebaixar.
admin-search-users = Pesquisar por nome de usuário
admin-search-users-current = Pesquisar por nome de usuário. Pesquisa atual: { $query }.
admin-search-prompt = Insira todo ou parte de um nome de usuário para pesquisar. Deixe em branco para navegar por todos os resultados por página.
menu-page-summary = Mostrando { $start }-{ $end } de { $total } entradas. Página { $page } de { $pages }.
menu-page-summary-query = Pesquisa "{ $query }": mostrando { $start }-{ $end } de { $total } entradas. Página { $page } de { $pages }.
menu-page-refresh = Atualizar lista
menu-list-refreshed = Lista atualizada.
menu-page-first = Primeira página
menu-page-previous = Página anterior
menu-page-next = Próxima página
menu-page-last = Última página
admin-search-no-results = Nenhum usuário correspondente encontrado. Use a pesquisa por nome de usuário para tentar um termo diferente.
confirm-promote = Tem certeza de que deseja promover { $player } a administrador?
confirm-demote = Tem certeza de que deseja rebaixar { $player } de administrador?
admin-role-target-changed = { $player } não tem mais a função esperada. Atualize a lista e tente novamente.
broadcast-to-all = Anunciar para todos os usuários
broadcast-to-admins = Anunciar apenas para administradores
broadcast-to-nobody = Silencioso (sem anúncio)
promote-announcement = { $player } foi promovido a administrador!
promote-announcement-you = Você foi promovido a administrador!
demote-announcement = { $player } foi rebaixado de administrador.
demote-announcement-you = Você foi rebaixado de administrador.
not-admin-anymore = Você não é mais um administrador e não pode realizar esta ação.
dev-only-action = Esta ação é restrita apenas a Desenvolvedores.

ban-duration-1h = 1 hora
ban-duration-6h = 6 horas
ban-duration-12h = 12 horas
ban-duration-1d = 1 dia
ban-duration-3d = 3 dias
ban-duration-1w = 1 semana
ban-duration-1m = 1 mês
ban-duration-permanent = Permanente

reason-spam = Spam
reason-harassment = Assédio
reason-cheating = Trapaça
reason-inappropriate = Comportamento inapropriado
reason-custom = Outro / Personalizado

no-users-to-ban = Nenhum usuário disponível para banir.
no-banned-users = Nenhum usuário banido no momento.
admin-active-ban-entry = { $username }. Expiração do banimento: { $expires }. Motivo: { $reason }. Aplicado por: { $admin }.
admin-active-mute-entry = { $username }. Expiração do silenciamento: { $expires }. Motivo: { $reason }. Aplicado por: { $admin }.
admin-penalty-expiry-permanent = permanente
admin-penalty-expiry-unknown = expiração desconhecida
admin-penalty-expiry-expired = já expirado
admin-penalty-expiry-timed = { $date } ({ $remaining } restante(s))
admin-penalty-reason-unknown = motivo não especificado
admin-penalty-admin-unknown = administrador desconhecido
admin-penalty-remaining-days = { $count ->
    [one] 1 dia
   *[other] { $count } dias
}
admin-penalty-remaining-hours = { $count ->
    [one] 1 hora
   *[other] { $count } horas
}
admin-penalty-remaining-minutes = { $count ->
    [one] 1 minuto
   *[other] { $count } minutos
}
admin-penalty-remaining-less-minute = menos de 1 minuto

ban-broadcast = { $target } foi banido por { $actor } por { $reason }. Duração: { $duration }.
unban-broadcast = { $target } foi desbanido por { $actor }.

banned-menu-title = Conta Banida
banned-reason = Motivo: { $reason }
banned-expires = Expira em: { $expires }
banned-permanent = Expira em: Permanente
disconnect = Desconectar


mute-user = Silenciar Usuário
unmute-user = Reativar Som do Usuário
no-users-to-mute = Nenhum usuário disponível para silenciar.
no-muted-users = Nenhum usuário silenciado no momento.
mute-duration-5m = 5 minutos
mute-duration-15m = 15 minutos
mute-duration-30m = 30 minutos
mute-duration-1h = 1 hora
mute-duration-6h = 6 horas
mute-duration-1d = 1 dia
mute-duration-permanent = Permanente
mute-broadcast = { $target } foi silenciado por { $actor } por { $reason }. Duração: { $duration }.
unmute-broadcast = { $target } teve o som reativado por { $actor }.
you-have-been-muted = Você foi silenciado. Motivo: { $reason }. Duração: { $duration }.
you-have-been-unmuted = Seu som foi reativado. Você pode conversar novamente.
muted-remaining-seconds = Você está silenciado. Restam { $seconds } segundos.
muted-remaining-minutes = Você está silenciado. Restam { $minutes } minutos.
muted-permanent = Você está permanentemente silenciado. Entre em contato com um administrador para obter mais informações.
chat-rate-limited = Devagar! Você está enviando mensagens muito rapidamente.
chat-repeated-message = Não repita a mesma mensagem.
chat-global-disabled-send = O chat global está desativado nas suas opções. Ative o chat global novamente antes de enviar mensagens globais.
chat-global-channel-required-send = Selecione um idioma para o chat global antes de enviar mensagens. O chat global não é monitorado em tempo real. Se alguém usar palavrões ou insultar você, bloqueie essa pessoa. Denuncie abusos graves ou repetidos para análise posterior.
chat-global-log-unavailable = O chat global está temporariamente indisponível porque esta mensagem não pôde ser salva com segurança. Tente novamente mais tarde.
chat-table-disabled-send = O chat da mesa está desativado nas suas opções. Ative o chat da mesa novamente antes de enviar mensagens para a mesa.
chat-global-temporarily-disabled-send = O chat global foi temporariamente desativado pelo desenvolvedor.
chat-invalid-channel = Esse canal de chat não está disponível.
chat-invalid-message = Essa mensagem não pôde ser enviada porque o formato dela é inválido.
chat-message-too-long = Essa mensagem é muito longa. As mensagens podem ter no máximo { $limit } caracteres.

report-user = Denunciar um usuário
enter-report-username = Insira o nome de usuário a denunciar.
report-error-self = Você não pode denunciar sua própria conta.
report-select-reason = Denunciar { $username }: selecione o motivo que melhor descreve o comportamento.
report-reason-spam = Spam ou perturbação repetida
report-reason-harassment = Assédio ou insultos pessoais
report-reason-hateful-content = Conteúdo de ódio
report-reason-sexual-content = Conteúdo sexual
report-reason-threats = Ameaças de dano
report-reason-personal-information = Compartilhamento de informações pessoais
report-reason-other = Outra má conduta grave
report-channel-unspecified = nenhum canal de chat global selecionado
report-confirm-summary = Denunciar { $username } por { $reason }. Canal de contexto: { $channel }. A denúncia será salva para análise manual. O usuário não será notificado nem penalizado automaticamente.
report-submit = Enviar denúncia
report-change-reason = Alterar motivo
report-submitted = Sua denúncia sobre { $username } foi salva com o horário exato de envio para análise manual. O usuário não foi notificado. Você também pode bloquear { GENDER_TERM($username_gender, "object") } para interromper o contato direto e ocultar as mensagens globais { GENDER_TERM($username_gender, "possessive-determiner") }.
report-target-cooldown = Você denunciou { $username } recentemente. Adicione outra denúncia somente após { $duration }; use Bloquear agora se não quiser receber as mensagens { GENDER_TERM($username_gender, "possessive-determiner") }.
report-rate-limited = Você enviou várias denúncias recentemente. Tente novamente após { $duration }.
report-failed = A denúncia não pôde ser salva com segurança. Tente novamente mais tarde.

broadcast-announcement = Anúncio de Transmissão
admin-broadcast-prompt = Insira a mensagem para transmitir a todos os usuários online. (Isso será enviado para todos!)
admin-broadcast-sent = Transmissão enviada para { $count } usuários.

manage-motd = Gerenciar AVISO (MOTD)
create-update-motd = Criar/Atualizar AVISO
view-motd = Ver AVISO Ativo
delete-motd = Excluir AVISO
motd-version-prompt = Insira o número da nova versão do AVISO (deve ser > 0):
invalid-motd-version = Versão do AVISO inválida. Deve ser um número positivo.
motd-created = A versão { $version } do AVISO foi criada com sucesso.
motd-deleted = O AVISO foi excluído.
motd-delete-empty = Não há nenhum AVISO ativo para excluir.
motd-not-exists = Nenhum AVISO ativo existe.
motd-announcement = Mensagem do Dia
motd-broadcast = Nova Mensagem do Dia: { $message }
error-no-languages = Erro: Nenhum idioma encontrado.
ok = OK

admin-localized-text-subject-motd = Mensagem do Dia
admin-localized-text-subject-power = motivo de energia do servidor
admin-localized-text-subject-ban = motivo de banimento personalizado
admin-localized-text-subject-mute = motivo de silenciamento personalizado
admin-localized-text-instructions = Edite as traduções para { $subject }. Idiomas oficiais são obrigatórios. Idiomas da comunidade são opcionais e usam { $fallback } quando vazios.
admin-localized-text-motd-version = Versão do AVISO: { $version }
admin-localized-text-official-heading = Idiomas oficiais, obrigatórios
admin-localized-text-community-heading = Idiomas da comunidade, opcionais
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = inserido, obrigatório
admin-localized-text-required-missing = não inserido, obrigatório
admin-localized-text-optional-set = inserido, opcional
admin-localized-text-optional-fallback = não inserido, opcional, usa o padrão alternativo
admin-localized-text-prompt = Insira o { $subject } em { $language }. Máximo de { $max } caracteres.
admin-localized-text-too-long = Essa tradução é muito longa. O máximo é { $max } caracteres.
admin-localized-text-missing-required = Insira todas as traduções obrigatórias primeiro. Faltando: { $languages }.
admin-localized-text-publish-motd = Publicar AVISO
admin-localized-text-continue = Continuar
admin-localized-text-apply-ban = Aplicar banimento
admin-localized-text-apply-mute = Aplicar silenciamento

unknown-player = Jogador desconhecido
unknown-user = Usuário desconhecido
user-account-unavailable = Esta conta de usuário não está mais disponível.

logout-confirm-title = Tem certeza de que deseja sair e encerrar o jogo?
logout-confirm-yes = Sim, sair
logout-confirm-no = Não, ficar

system-name = Sistema
server-restarting = O servidor será reiniciado em { $seconds } segundos...
server-shutting-down = O servidor será desligado em { $seconds } segundos...
server-shutting-down-now = O servidor está sendo desligado agora. Até logo!
server-power-management = Gerenciamento de Energia do Servidor
server-power-reboot = Reiniciar Servidor
server-power-shutdown = Desligar Servidor
server-power-cancel = Cancelar Ação de Energia Agendada
server-power-active-status = Agendado: { $action }. Motivo: { $reason }.
server-power-action-reboot = reinicialização
server-power-action-shutdown = desligamento
server-power-delay-30s = Em 30 segundos
server-power-delay-1m = Em 1 minuto
server-power-delay-5m = Em 5 minutos
server-power-delay-10m = Em 10 minutos
server-power-delay-30m = Em 30 minutos
server-power-delay-1h = Em 1 hora
server-power-delay-2h = Em 2 horas
server-power-delay-custom = Atraso personalizado em minutos
server-power-custom-delay-prompt = Insira o atraso em minutos, de 1 a { $max }:
server-power-invalid-custom-delay = Atraso inválido. Insira um número inteiro de minutos de 1 a { $max }.
server-power-reason-update = Atualização
server-power-reason-maintenance = Manutenção
server-power-reason-security = Segurança
server-power-reason-technical = Problema técnico
server-power-reason-custom = Motivo personalizado
server-power-reason-unspecified = motivo não especificado
server-power-confirm-summary = Confirmar { $action } do servidor em { $duration }. Motivo: { $reason }.
server-power-scheduled = { $action } do servidor agendada para daqui a { $duration }.
server-power-already-scheduled = Uma ação de energia do servidor já está agendada. Cancele-a antes de agendar outra.
server-power-cancel-none = Nenhuma ação de energia do servidor está agendada no momento.
server-power-cancelled = Ação de energia do servidor agendada cancelada.
server-power-cancelled-broadcast = { $admin } cancelou a { $action } agendada do servidor.
server-power-command-removed = Os comandos de chat /reboot e /stop foram removidos. Use Administração > Gerenciamento de Energia do Servidor.
server-power-finalizing-input-blocked = O servidor está finalizando uma reinicialização ou desligamento. Aguarde a desconexão do cliente.
server-power-maintenance-active = Uma operação de energia do servidor não pode ser agendada enquanto a manutenção do banco de dados está ativa. Aguarde a manutenção terminar e tente novamente.
server-power-finalize-failed = A { $action } agendada do servidor não pôde ser concluída com segurança. O servidor continuará online; entre em contato com um administrador.
server-power-reboot-warning = Reinicialização do servidor em { $duration }. Motivo: { $reason }. Não se desconecte manualmente; seu cliente se reconectará automaticamente e as mesas ativas serão preservadas.
server-power-shutdown-warning = Desligamento do servidor em { $duration }. Motivo: { $reason }. O servidor ficará offline; salve quaisquer jogos que deseja manter antes do desligamento.
server-power-reboot-now = O servidor está reiniciando agora. Motivo: { $reason }. Não se desconecte manualmente; seu cliente se reconectará automaticamente e as mesas ativas serão preservadas.
server-power-shutdown-now = O servidor está sendo desligado agora. Motivo: { $reason }. O servidor ficará offline.
server-power-restore-waiting = Esta mesa foi restaurada após uma reinicialização planejada. Aguardando até { $seconds } segundos para que os outros jogadores se reconectem antes de substituir os assentos vazios por bots.
server-power-restore-input-blocked = Esta mesa ainda está se recuperando da reinicialização planejada. A jogabilidade está pausada por até mais { $seconds } segundos enquanto aguarda { $players }; tente novamente após o término do período de carência.
server-power-restore-missing-players-fallback = os jogadores restantes
server-power-restore-complete = Todos os jogadores ativos se reconectaram após a reinicialização planejada. Jogo retomado.
server-power-restore-complete-with-bots = O período de carência de reconexão terminou após a reinicialização planejada. Os assentos vazios foram substituídos por bots e o jogo está sendo retomado.
duration-seconds = { $count ->
    [one] 1 segundo
   *[other] { $count } segundos
}
duration-minutes = { $count ->
    [one] 1 minuto
   *[other] { $count } minutos
}
duration-hours = { $count ->
    [one] 1 hora
   *[other] { $count } horas
}
duration-minutes-seconds = { $minutes } minutos e { $seconds } segundos
duration-hours-minutes = { $hours } horas e { $minutes } minutos
server-error-changing-language = Não foi possível alterar o idioma. A interface no idioma anterior continua ativa.
default-save-name = { $game } - { $date }

speech-settings = Configurações de Fala
speech-mode-option = Modo de Fala: { $status }
speech-rate-option = Velocidade da Fala: { $value }%
speech-voice-option = Voz: { $voice }
select-voice = Selecionar Voz
invalid-rate = Velocidade da fala inválida. Use um valor entre 50 e 300.
mode-aria = Aria-live
mode-web-speech = API Web Speech
default-voice = Voz Padrão
mobile-speech-settings = Configurações de Fala do Celular
mobile-tts-engine-option = Motor TTS: { $engine }
mobile-tts-engine-system = Padrão do sistema
mobile-tts-engine-system-selected = Motor TTS padrão do sistema
mobile-tts-engine-api-note = A seleção do motor Android é gerenciada pelas configurações do sistema nesta versão.
mobile-tts-voice-option = Voz Móvel: { $voice }
mobile-tts-rate-option = Velocidade da Fala Móvel: { $value }%
mobile-tts-enter-rate = Insira a velocidade da fala móvel (50-200)
mobile-tts-invalid-rate = Velocidade da fala móvel inválida. Use um valor entre 50 e 200.

player-kicked-offline = O jogador { $player } foi expulso (offline).
game-paused-host-disconnect = Jogo pausado. Aguardando { $player } se reconectar...
game-resumed = { $player } se reconectou. Jogo retomado!

auth-error-username-length = O nome de usuário deve ter entre 3 e 30 caracteres.
auth-error-username-invalid-chars = O nome de usuário pode conter apenas letras, números e espaços (sem espaços consecutivos e sem caracteres especiais).
auth-error-password-weak = A senha deve ter pelo menos 8 caracteres e conter letras e números.

personal-and-options = Pessoal e Opções
profile = Perfil
friends = Amigos
profile-registration-date = Data de Registro: { $date }
profile-date-unknown = Desconhecida
profile-username = Nome de usuário: { $username }
profile-email = E-mail: { $email }
admin-view-email = Visualização de Admin - E-mail: { $email }
profile-gender = Gênero: { $gender }
profile-bio = Biografia: { $bio }
profile-bio-empty = Não definida
profile-email-empty = Não definido

gender-male = Masculino
gender-female = Feminino
gender-non-binary = Não-binário
gender-not-set = Não definido

action-set-edit = Definir / Editar
action-delete = Excluir
bio-already-empty = A biografia já está vazia.
bio-deleted = Biografia excluída.
bio-updated = Biografia atualizada.

enter-email = Insira o novo endereço de e-mail:
email-updated = Endereço de e-mail atualizado.
enter-bio = Insira sua biografia:

gender-updated = Gênero atualizado.
no-changes-made = Nenhuma alteração feita.
confirm-email-change = Tem certeza de que deseja alterar seu e-mail para { $email }?

mandatory-email-notice = Você deve definir um e-mail para continuar participando. Seu e-mail é privado e conhecido apenas por você.
error-email-empty = O e-mail é obrigatório e não pode ficar vazio.
error-email-invalid = Formato de e-mail inválido. Forneça um endereço de e-mail válido.
reg-error-email = O e-mail é obrigatório para o cadastro.

error-email-taken = Este e-mail já está em uso por outra conta.

error-bio-length = A biografia não deve exceder 250 caracteres.
error-captcha-failed = Falha na verificação. Tente novamente.
error-rate-limit-login = Muitas tentativas de login falhas. Tente novamente em 15 minutos.
error-rate-limit-register = Você atingiu o número máximo de cadastros de conta para hoje.
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = Meus Amigos
friends-pending-requests = Solicitações Pendentes ({ $count })
friends-no-pending-requests = Solicitações Pendentes
friends-send-request = Enviar Solicitação de Amizade
friends-block-user = Bloquear um usuário
enter-block-username = Digite o nome de usuário da pessoa que você quer bloquear:
friends-blocked-users = { $count ->
    [0] Usuários Bloqueados
   *[other] Usuários Bloqueados ({ $count })
}
friends-blocked-empty = Você não bloqueou ninguém.
friends-list-empty = Você ainda não tem amigos.
friend-status-offline = Offline
friend-list-entry = { $username } ({ $status })

view-profile = Ver Perfil
block-user = Bloquear usuário
unblock-user = Desbloquear usuário
join-table = Entrar na Mesa
remove-friend = Remover Amigo
friend-remove-confirm = Remover { $username } da sua lista de amigos?
friend-remove-not-friends = { $username } não está mais na sua lista de amigos.
already-in-table = Você já está nesta mesa.
friend-removed-success = { $username } foi removido da sua lista de amigos.
friend-removed-notify = { $username } removeu você da lista de amigos { GENDER_TERM($username_gender, "possessive-determiner") }.

no-pending-requests = Nenhuma solicitação pendente.
accept = Aceitar
decline = Recusar
friend-accepted-success = Agora você é amigo de { $username }.
friend-accepted-notify = { $username } aceitou sua solicitação de amizade!
request-not-found = A solicitação de amizade não existe mais.
friend-declined-success = Solicitação de amizade recusada.
friend-declined-notify = { $username } recusou sua solicitação de amizade.

enter-friend-username = Insira o nome de usuário da pessoa que deseja adicionar como amiga:
friend-error-self = Você não pode enviar uma solicitação de amizade para si mesmo.
friend-error-already-friends = Você já é amigo deste usuário.
friend-error-duplicate = Você já tem uma solicitação de amizade pendente para este usuário.
friend-error-blocked-by-you = Você bloqueou { $username }. Desbloqueie { GENDER_TERM($username_gender, "object") } antes de enviar uma solicitação de amizade.
friend-error-blocked = As solicitações de amizade não estão disponíveis entre você e { $username }.
friend-request-sent = Solicitação de amizade enviada para { $username }.
friend-request-received = Você recebeu uma nova solicitação de amizade de { $username }.
block-confirm = Bloquear { $username }? Isso remove qualquer amizade e solicitação de amizade pendente entre vocês. Nenhum de vocês poderá enviar ao outro solicitações de amizade, mensagens privadas ou convites para mesas, e as mensagens de chat normais ficarão ocultas nas duas direções. Até o desbloqueio, nenhum de vocês poderá entrar novamente em uma mesa organizada pelo outro nem restaurar uma mesa salva que inclua os dois. Bloquear não remove jogadores de uma mesa compartilhada, não impede a recuperação de um assento reservado nem silencia o chat de voz da mesa.
block-success = Você bloqueou { $username }. O contato social direto não está mais disponível entre vocês, as mensagens comuns de chat { GENDER_TERM($username_gender, "possessive-determiner") } ficam ocultas, e nenhum de vocês pode entrar novamente em uma mesa organizada pelo outro nem restaurar uma mesa salva que inclua os dois usuários.
block-error-self = Você não pode se bloquear.
block-already-active = Você já bloqueou { $username }.
block-no-longer-active = Este bloqueio não está mais ativo.
unblock-success = Você desbloqueou { $username }. Amizades e solicitações anteriores não foram restauradas.

friends-grouped-requests = Você tem solicitações de amizade pendentes de: { $usernames }
friends-grouped-accepted = Suas solicitações de amizade foram aceitas por: { $usernames }
friends-grouped-declined = Suas solicitações de amizade foram recusadas por: { $usernames }
friends-grouped-removed = Você foi removido da lista de amigos por: { $usernames }
friends-and-others = { $names } e mais { $count } { $count ->
    [one] outro
   *[other] outros
}

send-private-message = Enviar Mensagem Privada
enter-pm-message = Insira sua mensagem para { $username }:
pm-error-not-friends = Você só pode enviar mensagens privadas para amigos.
pm-error-blocked = As mensagens privadas não estão disponíveis entre você e este jogador.
pm-error-offline = { $username } não está online no momento.
pm-error-self = Você não pode enviar uma mensagem privada para si mesmo.
pm-error-message-required = Digite uma mensagem privada. Ao usar o chat, inclua um nome de usuário, por exemplo: @Jogador olá.
pm-sent-content = Você para { $username }: { $message }
pm-received = Mensagem privada de { $username }: { $message }

host-management = Gerenciamento de Host
table-spectator-suffix = (Espectador)
host-management-set-private = Definir Mesa como Privada
host-management-set-public = Definir Mesa como Pública
host-management-invite = Convidar um Amigo
host-management-pass-host = Passar Host para Outro Jogador
host-management-kick = Expulsar um Jogador
host-management-kick-ban = Expulsar e Banir um Jogador
host-management-restart-game = Reiniciar Jogo
host-management-table-now-private = Esta mesa agora é privada. Apenas jogadores convidados podem entrar.
host-management-table-now-public = Esta mesa agora é pública.
host-restart-confirm = Reiniciar o jogo atual e retornar esta mesa para a sala de espera? Os jogadores atuais e o chat de voz continuarão conectados, mas a partida atual será cancelada.
host-restart-broadcast = { $player } reiniciou o jogo. A mesa está de volta à sala de espera.
host-restart-not-playing = Não há nenhum jogo ativo para reiniciar.
host-invite-no-friends = (Nenhum amigo disponível para convidar)
host-invite-sent = Convite enviado para { $player }.
host-invite-friend-unavailable = Esse amigo não está online no momento.
host-invite-already-pending = Já existe um convite pendente para esse amigo.
host-invite-friend-busy = Esse amigo já está em um jogo.
host-invite-declined = { $player } recusou o convite para a mesa.
table-invite-received = { $host } convidou você para a mesa { GENDER_TERM($host_gender, "possessive-determiner") } de { $game }.
table-invite-queued = { $host } convidou você para a mesa { GENDER_TERM($host_gender, "possessive-determiner") } de { $game }. Conclua sua entrada atual para responder.
table-invite-expired = O convite para a mesa expirou.
invite-accept = Aceitar Convite
invite-decline = Recusar Convite
host-management-no-longer-host = Você não é mais o host desta mesa.
host-pass-no-candidates = (Nenhum jogador disponível para passar o host)
host-pass-no-longer-host = Você passou o host para outro jogador. Você não é mais o host desta mesa.
host-passed = { $player } agora é o host.
host-pass-failed = Falha ao transferir o host. O jogador pode ter saído.
host-kick-no-candidates = (Nenhum jogador disponível para expulsar)
host-kick-invalid-target = Alvo de expulsão inválido.
host-kick-broadcast = { $player } foi expulso da mesa.
host-kick-ban-broadcast = { $player } foi expulso e banido da mesa.
host-kick-you = Você foi expulso da mesa por { $host }.
host-kick-ban-you = Você foi expulso e banido da mesa por { $host }.
table-you-are-banned = Você está banido desta mesa.
table-private-invite-only = Esta mesa é privada. Você deve receber um convite do host para entrar.
table-join-social-blocked = Você não pode entrar nesta mesa porque o contato social direto não está disponível entre você e o host dela. Ainda assim, você pode recuperar um assento já reservado para você.

voice-room-table-label = Voz da mesa de { $game }
voice-unavailable = O chat de voz não está disponível no momento.
voice-invalid-context = Essa solicitação de sala de voz é inválida.
voice-not-at-table = Você ainda não entrou em uma mesa. Entre em uma mesa antes de iniciar o chat de voz.
voice-not-in-context = Você deve estar nessa mesa antes de entrar no chat de voz dela.
voice-rate-limited = Devagar. O chat de voz está mudando muito rapidamente agora.
voice-muted-seconds = Você está silenciado e não pode entrar no chat de voz. Restam { $seconds } segundos.
voice-muted-minutes = Você está silenciado e não pode entrar no chat de voz. Restam { $minutes } minutos.
voice-muted-permanent = Você está silenciado e não pode entrar no chat de voz.
voice-status-connected = { $player } conectou-se ao chat de voz da mesa.
voice-status-disconnected = { $player } desconectou-se do chat de voz.
voice-status-connection-lost = { $player } perdeu a conexão e foi removido do chat de voz.
voice-status-left-table = { $player } saiu da mesa e do chat de voz.

error-smtp-not-configured = A recuperação de senha está desativada no momento pelo administrador.
error-email-not-found = Nenhuma conta encontrada com esse endereço de e-mail.
success-reset-email-sent = Um código de redefinição foi enviado para o seu endereço de e-mail.
error-smtp-send-failed = Falha ao enviar o e-mail de redefinição. Tente novamente mais tarde.
error-invalid-reset-code = Código de redefinição inválido ou expirado.
success-password-reset = Sua senha foi redefinida com sucesso. Agora você pode fazer login.

auth-username-reserved = Este nome é reservado pelo PlayAural. Escolha outro nome de usuário.
action-role-change-rate-limited = Você está alternando rápido demais entre jogador e espectador. Tente novamente em { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
}.

admin-moderation-copy-page = { $count ->
    [one] Copiar mensagem desta página (1)
   *[other] Copiar mensagens desta página ({ $count })
}
admin-moderation-copy-page-success = { $count ->
    [one] 1 mensagem desta página foi copiada para a área de transferência.
   *[other] { $count } mensagens desta página foram copiadas para a área de transferência.
}
admin-moderation-copy-page-failed = Não foi possível copiar esta página para a área de transferência. Verifique a permissão da área de transferência e tente novamente.

# Formas gramaticais compartilhadas para o gênero da conta. Os jogos podem
# substituir uma forma por <context>-gender-term-<form> ao chamar GENDER_TERM;
# os nomes técnicos context e form devem permanecer inalterados.
gender-term-subject =
    { $gender ->
        [male] ele
        [female] ela
       *[other] essa pessoa
    }
gender-term-subject-capitalized =
    { $gender ->
        [male] Ele
        [female] Ela
       *[other] Essa pessoa
    }
gender-term-subject-be =
    { $gender ->
        [male] ele está
        [female] ela está
       *[other] essa pessoa está
    }
gender-term-subject-be-capitalized =
    { $gender ->
        [male] Ele está
        [female] Ela está
       *[other] Essa pessoa está
    }
gender-term-subject-have =
    { $gender ->
        [male] ele tem
        [female] ela tem
       *[other] essa pessoa tem
    }
gender-term-subject-have-capitalized =
    { $gender ->
        [male] Ele tem
        [female] Ela tem
       *[other] Essa pessoa tem
    }
gender-term-object =
    { $gender ->
        [male] ele
        [female] ela
       *[other] essa pessoa
    }
gender-term-possessive-determiner =
    { $gender ->
        [male] dele
        [female] dela
       *[other] dessa pessoa
    }
gender-term-possessive-determiner-capitalized =
    { $gender ->
        [male] Dele
        [female] Dela
       *[other] Dessa pessoa
    }
gender-term-possessive-pronoun =
    { $gender ->
        [male] o dele
        [female] o dela
       *[other] o dessa pessoa
    }
gender-term-reflexive =
    { $gender ->
        [male] a si mesmo
        [female] a si mesma
       *[other] a si
    }

friends-sent-requests = { $count ->
    [0] Solicitações enviadas
   *[other] Solicitações enviadas ({ $count })
}
friend-status-offline-last-online = Offline, visto por último { $relative_time }
no-sent-requests = Você não tem solicitações de amizade enviadas pendentes.
friend-request-to = Solicitação de amizade enviada para { $username }
friend-request-manage-sent = Gerenciar solicitação de amizade enviada
friend-request-accept-action = Aceitar solicitação de amizade
friend-request-cancel-action = Cancelar solicitação de amizade
friend-request-cancel-confirm = Cancelar sua solicitação de amizade pendente para { $username }?
friend-request-cancelled = Sua solicitação de amizade para { $username } foi cancelada.
friend-request-cancel-unavailable = Esta solicitação de amizade não está mais pendente e, por isso, não foi cancelada.
relative-time-just-now = agora mesmo
relative-time-minutes-ago = { $count ->
    [one] há 1 minuto
   *[other] há { $count } minutos
}
relative-time-hours-ago = { $count ->
    [one] há 1 hora
   *[other] há { $count } horas
}
relative-time-days-ago = { $count ->
    [one] há 1 dia
   *[other] há { $count } dias
}
relative-time-weeks-ago = { $count ->
    [one] há 1 semana
   *[other] há { $count } semanas
}
relative-time-months-ago = { $count ->
    [one] há 1 mês
   *[other] há { $count } meses
}
relative-time-years-ago = { $count ->
    [one] há 1 ano
   *[other] há { $count } anos
}

host-management-switch-game = Trocar de jogo
host-management-player-substitution = Substituição de jogador
host-game-switch-current = Jogo atual: { $game }. Esta mesa tem { $seats } { $seats ->
    [one] assento ativo
   *[other] assentos ativos
}. Apenas jogos que comportam todos os assentos ativos são exibidos.
host-game-switch-no-compatible-games = Nenhum outro jogo comporta atualmente todos os { $seats } { $seats ->
    [one] assento ativo
   *[other] assentos ativos
}.
host-game-switch-confirm = Trocar o jogo desta mesa de { $old_game } para { $new_game }? Todos que ainda estiverem presentes entrarão na nova sala de espera com a mesma função de jogador ou espectador, e os bots permanecerão. A partida ou configuração atual, as opções, as equipes e o estado de prontidão serão descartados. O dono da mesa, a privacidade, os banimentos e o chat de voz continuarão conectados. Os convites pendentes do jogo antigo serão cancelados.
host-game-switch-target-unavailable = Esse jogo não está mais disponível como destino da troca. Nenhum estado da mesa foi alterado.
host-game-switch-roster-invalid = Os participantes presentes na mesa não correspondem mais aos assentos do jogo. A troca foi bloqueada para evitar que alguém seja removido. Volte à mesa e tente novamente depois que a lista for atualizada.
host-game-switch-too-many-seats = Não é possível trocar para { $game }: o jogo aceita no máximo { $max } { $max ->
    [one] assento ativo
   *[other] assentos ativos
}, mas esta mesa precisa de { $seats }.
host-game-switch-failed = Não foi possível trocar de jogo com segurança. A mesa e o jogo atuais permaneceram inalterados.
host-game-switch-you = Você trocou o jogo desta mesa de { $old_game } para { $new_game }. Todos estão agora na nova sala de espera; o chat de voz da mesa continua conectado.
host-game-switch-player = { $player } trocou o jogo desta mesa de { $old_game } para { $new_game }. Todos estão agora na nova sala de espera; o chat de voz da mesa continua conectado.

player-substitution-offer-action = Colocar um espectador neste assento
player-substitution-seat-bot = Assento do bot: { $bot }
player-substitution-seat-replacement = { $bot }, jogando no assento reservado de { $player }
player-substitution-seat-self = Seu assento: { $player }
player-substitution-seat-player = Assento do jogador: { $player }
player-substitution-no-seats = (Não há assentos de jogadores ativos disponíveis)
player-substitution-seat-unavailable = Esse assento não está mais disponível para substituição. Nenhuma função foi alterada.
player-substitution-no-spectators = (Não há espectadores elegíveis disponíveis)
player-substitution-spectator-unavailable = Esse espectador não está mais disponível para substituição. Nenhuma função foi alterada.
player-substitution-user-busy = { $player } está concluindo outra entrada ou visualização de status. Tente novamente quando essa visualização não estiver mais aberta para { GENDER_TERM($player_gender, "object") }.
player-substitution-game-busy = O jogo está concluindo uma escolha sincronizada ou uma recuperação da mesa que bloqueia temporariamente as substituições. Tente novamente quando terminar.
player-substitution-offer-sent = O assento de { $seat } foi oferecido a { $player }. { GENDER_TERM($player_gender, "subject-capitalized") } precisa aceitar antes que o controle mude.
player-substitution-self-offer-sent = Seu assento foi oferecido a { $player }. Se a oferta for aceita por { GENDER_TERM($player_gender, "object") }, você se tornará espectador e continuará como dono da mesa; o resultado final do assento será registrado para { GENDER_TERM($player_gender, "object") }.
player-substitution-self-incoming-consent-sent = Você pediu a { $player } o assento { GENDER_TERM($player_gender, "possessive-determiner") }. Se o pedido for aceito por { GENDER_TERM($player_gender, "object") }, você assumirá o controle imediatamente, pois escolher a si mesmo já confirmou seu consentimento.
player-substitution-outgoing-consent-sent = Você pediu a { $player } que cedesse o assento { GENDER_TERM($player_gender, "possessive-determiner") } a { $substitute }. Se o pedido for aceito por { GENDER_TERM($player_gender, "object") }, { $substitute } também precisará aceitar antes que o controle mude.
player-substitution-offer-pending = { $player } já tem um pedido de substituição aguardando resposta.
player-substitution-seat-offer-pending = O assento de { $seat } já tem um pedido de substituição aguardando resposta.
player-substitution-self-seat-offer-pending = Seu assento já tem um pedido de substituição aguardando resposta.
player-substitution-request-outgoing = { $host } quer que { $player } ocupe seu assento atual. Se você aceitar, passará a ser espectador, e { GENDER_TERM($player_gender, "subject") } receberá exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento. Nenhum cronômetro será reiniciado.
player-substitution-request-outgoing-host-incoming = { $host } quer ocupar seu assento atual. Se você aceitar, passará a ser espectador, e { GENDER_TERM($host_gender, "subject") } receberá exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento. Nenhum cronômetro será reiniciado.
player-substitution-request-player = { $host } está oferecendo a você o assento de { $player }, com o consentimento { GENDER_TERM($player_gender, "possessive-determiner") }. Se aceitar, você herdará exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento; nenhum cronômetro será reiniciado, e { GENDER_TERM($player_gender, "subject") } passará a ser espectador.
player-substitution-request-host-seat = { $host } está oferecendo a você o próprio assento. Se aceitar, você herdará exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento; nenhum cronômetro será reiniciado, e { GENDER_TERM($host_gender, "subject") } passará a ser espectador, mas continuará como dono da mesa.
player-substitution-request-bot = { $host } está oferecendo a você o assento controlado por { $bot }. Se aceitar, você herdará exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento; nenhum cronômetro será reiniciado.
player-substitution-request-replacement = { $host } está oferecendo a você o assento reservado de { $player }, controlado atualmente por { $bot }. Se aceitar, você herdará exatamente o estado do jogo, as informações privadas, o tempo restante do turno e a atribuição do resultado final do assento; nenhum cronômetro será reiniciado, e { GENDER_TERM($player_gender, "subject") } não poderá mais recuperar esse assento.
player-substitution-decline = Recusar substituição
player-substitution-accept = Aceitar substituição
player-substitution-offer-expired = O pedido de substituição expirou. Nenhuma função foi alterada.
player-substitution-offer-expired-host = { $player } não respondeu antes que o pedido de substituição expirasse. Nenhuma função foi alterada.
player-substitution-offer-declined = { $player } recusou o pedido de substituição. Nenhuma função foi alterada.
player-substitution-no-longer-available = Esse pedido de substituição não está mais disponível. Nenhuma função foi alterada.
player-substitution-awaiting-incoming = { $player } já pode aceitar ou recusar a substituição. Nenhuma função foi alterada ainda.
player-substitution-complete-player-you = Você assumiu o antigo assento de { $player }. { GENDER_TERM($player_gender, "subject-be-capitalized") } agora como espectador.
player-substitution-complete-outgoing-you = { $player } assumiu seu antigo assento. Agora você é espectador.
player-substitution-complete-player = { $player } assumiu o antigo assento de { $outgoing }. { GENDER_TERM($outgoing_gender, "subject-be-capitalized") } agora como espectador.
player-substitution-complete-host-player-you = Você assumiu o antigo assento de { $player }. { GENDER_TERM($player_gender, "subject-be-capitalized") } agora como espectador, e o cargo de dono da mesa continua com { GENDER_TERM($player_gender, "object") }.
player-substitution-complete-outgoing-host-you = { $player } assumiu seu antigo assento. Agora você é espectador e continua como dono da mesa.
player-substitution-complete-host = { $player } assumiu o antigo assento de { $outgoing }. { GENDER_TERM($outgoing_gender, "subject-be-capitalized") } agora como espectador e continua como dono da mesa.
player-substitution-complete-bot-you = Você assumiu o assento de { $bot }.
player-substitution-complete-bot = { $player } assumiu o assento de { $bot }.
player-substitution-complete-replacement-you = Você assumiu o assento reservado de { $replaced_player }, que estava com { $bot }. A reserva anterior terminou.
player-substitution-complete-replacement = { $player } assumiu o assento reservado de { $replaced_player }, que estava com { $bot }. A reserva anterior terminou.

host-invite-pair-cooldown = Aguarde { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
} antes de convidar esse amigo novamente.
host-invite-rate-limited = Você está enviando convites de mesa rápido demais. Tente novamente em { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
}.
table-invite-no-longer-available = Esse convite de mesa não está mais disponível.
