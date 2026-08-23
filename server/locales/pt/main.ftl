auth-username-password-required = Nome de usuário e senha são obrigatórios.
auth-registration-success = Cadastro realizado com sucesso! Agora você pode fazer login com suas credenciais.
auth-username-taken = Nome de usuário já em uso. Escolha um nome de usuário diferente.
auth-username-reserved-bot = Este nome é reservado para bots do PlayAural. Escolha um nome de usuário diferente.
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

main-menu-title = Menu Principal

play = Jogar
view-active-tables = Ver mesas ativas
options = Opções
logout = Sair
back = Voltar
go-back = Voltar
context-menu = Menu de contexto.
no-actions-available = Nenhuma ação disponível.
table-new-host-promoted = { $player } agora é o host da mesa.
return-to-lobby = Retornar ao lobby
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
table-listing = Mesa de { $host } ({ $count } usuários)
table-listing-one = Mesa de { $host } ({ $count } usuário)
table-listing-with = Mesa de { $host } ({ $count } usuários) com { $members }
table-listing-game = { $game }: Mesa de { $host } ({ $count } usuários)
table-listing-game-one = { $game }: Mesa de { $host } ({ $count } usuário)
table-listing-game-with = { $game }: Mesa de { $host } ({ $count } usuários) com { $members }
table-listing-game-status = { $game } [{ $status }]: Mesa de { $host } ({ $count } usuários)
table-listing-game-one-status = { $game } [{ $status }]: Mesa de { $host } ({ $count } usuário)
table-listing-game-with-status = { $game } [{ $status }]: Mesa de { $host } ({ $count } usuários) com { $members }
table-status-waiting = Aguardando
table-status-playing = Jogando
table-status-finished = Finalizado
table-not-exists = A mesa não existe mais.
table-full = A mesa está cheia.
player-replaced-by-bot = { $bot } está jogando no lugar de { $player }.
player-reclaimed-from-bot = { $player } retornou e reassumiu seu lugar que estava com { $bot }.
player-took-over = { $player } reassumiu seu lugar que estava com { $bot }.
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
permission-denied = Você não tem permissão para realizar esta ação em um Desenvolvedor.
kick-user = Expulsar Usuário
kick-broadcast = { $target } foi expulso por { $actor }.
you-were-kicked = Você foi expulso por { $actor }.
user-not-online = O usuário { $target } não está online.
kick-immune = Você não pode expulsar este usuário.
kick-confirm = Tem certeza de que deseja expulsar { $player }?
no-users-to-kick = Nenhum usuário disponível para expulsar.
usage-kick = Uso: /kick <nome_de_usuário>
online-users-none = Nenhum usuário online.
online-users-one = 1 usuário: { $users }
online-users-many = { $count } usuários: { $users }
online-user-not-in-game = Menu principal
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
online-user-actions-title = Ações para { $username }
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

turn-sound-option = Som de turno: { $status }

custom-bot-names-option = Nomes de bot personalizados: { $status }
confirm-destructive-option = Confirmar ações arriscadas: { $status }
clear-kept-option = Limpar dados guardados ao rolar: { $status }
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
no-bot-names-available = Nenhum nome de bot disponível.
enter-bot-name = Insira o nome do bot
bot-name-invalid-length = Os nomes dos bots devem ter entre 3 e 30 caracteres.
bot-name-invalid-characters = Os nomes dos bots só podem conter letras, números e espaços.
bot-name-already-used = Um jogador ou bot com este nome já está nesta mesa.
bot-name-registered-account = Este nome pertence a uma conta registrada. Escolha um nome de bot diferente.
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
general-desc-general-options = Ajuste configurações de idioma, áudio, acessibilidade e notificações de toda a conta.
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
general-desc-menu-hints = Mostra descrições disponíveis diretamente nas linhas do menu. Quando desligado, as descrições continuam disponíveis sob demanda com Espaço onde suportado.
general-desc-mute-global-chat = Impede que mensagens do chat global sejam lidas automaticamente em voz alta.
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
action-no-bots = Não há bots para remover.
action-bots-cannot = Os bots não podem fazer isso.
action-no-scores = Nenhuma pontuação disponível ainda.

options-category-audio = Áudio
options-category-accessibility = Acessibilidade
options-category-notifications = Notificações
options-category-game = Jogo

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
mute-table-chat-option = Silenciar Chat da Mesa: { $status }
invert-multiline-enter-option = Inverter Comportamento da Tecla Enter: { $status }
menu-hints-option = Dicas de Menu: { $status }
menu-hints-changed = As dicas de menu agora estão { $status }.
play-typing-sounds-option = Tocar Sons de Digitação: { $status }
enter-music-volume = Insira o volume da música (0-100)
enter-ambience-volume = Insira o volume do ambiente (0-100)
enter-voice-volume = Insira o volume do chat de voz (10-100)
invalid-volume = Volume inválido.

dice-not-rolled = Você ainda não rolou os dados.
dice-no-dice = Nenhum dado disponível.
table-no-players = Nenhum jogador.
table-players-one = { $count } jogador: { $players }.
table-players-many = { $count } jogadores: { $players }.
table-spectators = Espectadores: { $spectators }.
table-host-suffix = (Host)
table-voice-chat-suffix = (no chat de voz)
table-members-summary = Resumo da mesa: { $total } { $total ->
    [one] assento
   *[other] assentos
}; { $real } { $real ->
    [one] pessoa real
   *[other] pessoas reais
}, { $bots } { $bots ->
    [one] bot
   *[other] bots
}; { $active } ativo(s), { $spectators } assistindo.
table-members-empty = Nenhum membro da mesa listado no momento. Use Voltar para retornar e atualizar a visualização da mesa.
table-member-entry = { $player }: { $status }
table-member-status-host = Host
table-member-status-player = Jogador
table-member-status-spectator = Espectador
table-member-status-bot = Bot
table-member-status-online = Online
table-member-status-offline = Offline
table-member-status-voice-chat = no chat de voz
table-member-status-bot-takeover = bot jogando em seu lugar: { $bot }
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
leaderboard-rating-entry = { $rank }. { $player }: classificação { $rating } ({ $mu } ± { $sigma })
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
my-stats-rating = Classificação de habilidade: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Sem classificação de habilidade ainda
my-stats-avg-per-turn = Média de pontos por turno: { $value }
my-stats-best-turn = Melhor turno único: { $value }
my-stats-score-per-round = Pontuação por rodada: { $value }
my-stats-most-enemies-defeated = Mais Inimigos Derrotados: { $value }
my-stats-deepest-wave-reached = Onda Mais Profunda Alcançada: { $value }

predict-outcomes = Prever resultados
predict-header = Resultados Previstos (por classificação de habilidade)
predict-note-multiplayer = Percentuais de vitória são exibidos apenas para partidas de 2 jogadores. Com 3 ou mais jogadores humanos, apenas as classificações de habilidade são mostradas.
predict-entry = { $rank }. { $player } (classificação: { $rating })
predict-entry-2p = { $rank }. { $player } (classificação: { $rating }, { $probability }% de chance de vitória)
predict-unavailable = Previsões de classificação não estão disponíveis.
predict-need-players = São necessários pelo menos 2 jogadores humanos para previsões.
action-need-more-humans = São necessários mais jogadores humanos.
confirm-leave-game = Tem certeza de que deseja sair da mesa?
confirm-yes = Sim
confirm-no = Não

administration = Administração

account-approval = Aprovação de Conta
no-pending-accounts = Nenhuma conta pendente.
approve-account = Aprovar
decline-account = Recusar
account-approved = A conta de { $player } foi aprovada.
account-declined = A conta de { $player } foi recusada e excluída.

waiting-for-approval = Sua conta está aguardando aprovação de um administrador. Aguarde...
account-approved-welcome = Sua conta foi aprovada! Bem-vindo ao PlayAural!
account-declined-goodbye = Sua solicitação de conta foi recusada.

account-request = solicitação de conta
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
auto-muted-seconds = Você foi temporariamente silenciado por spam. Restam { $seconds } segundos.
auto-muted-minutes = Você foi temporariamente silenciado por spam. Restam { $minutes } minutos.
auto-muted-applied-seconds = Você foi silenciado automaticamente por { $seconds } segundos devido a excesso de spam no chat.
auto-muted-applied-minutes = Você foi silenciado automaticamente por { $minutes } minutos devido a excesso de spam no chat.
chat-rate-limited = Devagar! Você está enviando mensagens muito rapidamente.
chat-global-disabled-send = O chat global está desativado nas suas opções. Ative o chat global novamente antes de enviar mensagens globais.
chat-table-disabled-send = O chat da mesa está desativado nas suas opções. Ative o chat da mesa novamente antes de enviar mensagens para a mesa.
admin-spam-alert = Aviso: { $username } está fazendo spam excessivo no chat e foi silenciado automaticamente.

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

logout-confirm-title = Tem certeza de que deseja sair e encerrar o jogo?
logout-confirm-yes = Sim, sair
logout-confirm-no = Não, ficar

system-name = Sistema
server-restarting = O servidor será reiniciado em { $seconds } segundos...
server-restarting-now = O servidor está sendo reiniciado agora. Reconecte-se em breve.
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
server-error-changing-language = Erro ao alterar o idioma: { $error }
default-save-name = { $game } - { $date }

speech-settings = Configurações de Fala
speech-mode-option = Modo de Fala: { $status }
speech-rate-option = Velocidade da Fala: { $value }%
speech-voice-option = Voz: { $voice }
select-voice = Selecionar Voz
enter-speech-rate = Insira a velocidade da fala (50-300)
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
friends-list-empty = Você ainda não tem amigos.
friend-status-offline = Offline
friend-status-playing = Jogando { $game }
friend-status-spectating = Assistindo a { $game }
friend-status-lobby = Menu principal
friend-list-entry = { $username } ({ $status })

friend-actions-title = Ações para { $username }
view-profile = Ver Perfil
join-table = Entrar na Mesa
remove-friend = Remover Amigo
friend-remove-confirm = Remover { $username } da sua lista de amigos?
friend-remove-not-friends = { $username } não está mais na sua lista de amigos.
already-in-table = Você já está nesta mesa.
friend-removed-success = { $username } foi removido da sua lista de amigos.
friend-removed-notify = { $username } removeu você da lista de amigos dele.

no-pending-requests = Nenhuma solicitação pendente.
friend-request-from = Solicitação de amizade de { $username }
accept = Aceitar
decline = Recusar
friend-accepted-success = Agora vocês são amigos de { $username }._fixed -> friend-accepted-success = Agora vocês são amigos.
friend-accepted-notify = { $username } aceitou sua solicitação de amizade!
request-not-found = A solicitação de amizade não existe mais.
friend-declined-success = Solicitação de amizade recusada.
friend-declined-notify = { $username } recusou sua solicitação de amizade.

public-profile-title = Perfil de { $username }
enter-friend-username = Insira o nome de usuário da pessoa que deseja adicionar como amiga:
friend-error-self = Você não pode enviar uma solicitação de amizade para si mesmo.
friend-error-already-friends = Você já é amigo deste usuário.
friend-error-duplicate = Você já tem uma solicitação de amizade pendente para este usuário.
friend-request-sent = Solicitação de amizade enviada para { $username }.
friend-request-received = Você recebeu uma nova solicitação de amizade de { $username }.

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
pm-error-offline = { $username } não está online no momento.
pm-sent-success = Mensagem enviada para { $username }.
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
table-invite-received = { $host } convidar você para a mesa de { $game }._fixed -> table-invite-received = { $host } convidou você para a mesa de { $game }.
table-invite-queued = { $host } convidou você para a mesa de { $game }. Conclua sua entrada atual para responder.
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
