auth-username-password-required = Se requieren un nombre de usuario y una contraseña.
auth-registration-success = ¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.
auth-username-taken = Ese nombre de usuario ya está en uso. Elige otro.
auth-username-reserved-bot = Este nombre está reservado para los bots de PlayAural. Elige otro nombre de usuario.
auth-registration-error = El registro falló debido a un error del servidor. Inténtalo de nuevo.
auth-error-wrong-password = Contraseña incorrecta.
auth-error-user-not-found = El usuario no existe.
auth-kicked-logged-in-elsewhere = Se cerró tu sesión porque tu cuenta se inició desde otro dispositivo.

chat-global = { $player } dice en el chat global: { $message }

admin-smtp-updated-success = Configuración SMTP actualizada correctamente
admin-smtp-settings = Configuración SMTP
email-reset-subject = Código de restablecimiento de contraseña de PlayAural
email-reset-body = Hola { $username },\n\nSolicitaste restablecer la contraseña de tu cuenta de PlayAural.\nTu código de restablecimiento de 6 dígitos es: { $code }\n\nEste código caducará en 15 minutos.\nSi no solicitaste esto, ignora este correo.
email-reset-body-html = <p>Hola { $username },</p>
    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta de PlayAural.</p>
    <p>Tu código de recuperación de 6 dígitos es:</p>
    <h2>{ $code }</h2>
    <p>Este código caducará en exactamente 15 minutos.</p>
    <p>Si no solicitaste esto, ignora este correo. Tu cuenta sigue segura.</p>
    <p>Saludos,<br>Trung</p>
email-test-subject = Prueba de SMTP de PlayAural
email-test-body = Este es un correo de prueba del servidor de PlayAural para verificar tu configuración SMTP.
email-test-body-html = <p>Hola,</p>
    <p>Este es un correo de prueba del servidor de PlayAural.</p>
    <p>Si estás leyendo esto, tu configuración SMTP está enviando correos HTML correctamente.</p>
smtp-test-sending = Probando la conexión, espera un momento...
smtp-test-success = ¡Correo de prueba enviado correctamente a { $email }!
smtp-test-failed = No se pudo enviar el correo de prueba: { $error }
smtp-host = Host: { $value }
smtp-port = Puerto: { $value }
smtp-username = Usuario: { $value }
smtp-password = Contraseña: { $value }
smtp-from-email = Correo remitente: { $value }
smtp-from-name = Nombre remitente: { $value }
smtp-encryption = Cifrado: { $value }
smtp-test-connection = Probar conexión
smtp-not-set = Sin configurar
smtp-prompt-host = Ingresa el host SMTP (por ejemplo, smtp.gmail.com):
smtp-prompt-port = Ingresa el puerto SMTP (por ejemplo, 587 o 465):
smtp-prompt-username = Ingresa el usuario SMTP:
smtp-prompt-password = Ingresa la contraseña SMTP:
smtp-prompt-from-email = Ingresa la dirección de correo remitente:
smtp-prompt-from-name = Ingresa el nombre del remitente (por ejemplo, Soporte de PlayAural):
smtp-prompt-test-email = Ingresa la dirección de correo de destino para la prueba:
smtp-enc-none = Sin cifrado
smtp-enc-ssl = Usar SSL
smtp-enc-tls = Habilitar cifrado TLS automáticamente (STARTTLS)
smtp-current-enc = * { $value }

main-menu-title = Menú principal

play = Jugar
view-active-tables = Ver mesas activas
options = Opciones
logout = Cerrar sesión
back = Atrás
go-back = Volver
context-menu = Menú contextual.
no-actions-available = No hay acciones disponibles.
table-new-host-promoted = { $player } ahora es el anfitrión de la mesa.
return-to-lobby = Volver al vestíbulo
return-to-table = Volver a la mesa
create-table = Crear una mesa nueva
leave-table = Salir de la mesa
start-game = Iniciar partida
add-bot = Añadir bot
remove-bot = Quitar bot
actions-menu = Menú de acciones
save-table = Guardar mesa
whose-turn = De quién es el turno
whos-at-table = Quién está en la mesa
check-scores = Ver puntuaciones
check-scores-detailed = Puntuaciones detalladas

game-player-skipped = Se saltó el turno de { $player }.

table-created = { $host } creó una nueva mesa de { $game }.
table-created-broadcast = { $host } creó una nueva mesa de { $game }.
table-joined = { $player } se unió a la mesa.
table-left = { $player } salió de la mesa.
new-host = { $player } ahora es el anfitrión.
waiting-for-players = Esperando jugadores. Mínimo {$min}, máximo { $max }.
game-starting = ¡La partida está por comenzar!
table-listing = Mesa de { $host } ({ $count } usuarios)
table-listing-one = Mesa de { $host } ({ $count } usuario)
table-listing-with = Mesa de { $host } ({ $count } usuarios) con { $members }
table-listing-game = { $game }: mesa de { $host } ({ $count } usuarios)
table-listing-game-one = { $game }: mesa de { $host } ({ $count } usuario)
table-listing-game-with = { $game }: mesa de { $host } ({ $count } usuarios) con { $members }
table-listing-game-status = { $game } [{ $status }]: mesa de { $host } ({ $count } usuarios)
table-listing-game-one-status = { $game } [{ $status }]: mesa de { $host } ({ $count } usuario)
table-listing-game-with-status = { $game } [{ $status }]: mesa de { $host } ({ $count } usuarios) con { $members }
table-status-waiting = Esperando
table-status-playing = Jugando
table-status-finished = Terminada
table-not-exists = La mesa ya no existe.
table-full = La mesa está llena.
player-replaced-by-bot = { $bot } ahora está jugando en nombre de { $player }.
player-reclaimed-from-bot = { $player } regresó y recuperó su asiento de manos de { $bot }.
player-took-over = { $player } recuperó su asiento de manos de { $bot }.
spectator-joined = Te uniste a la mesa de { $host } como espectador.

spectate = Observar
now-playing = { $player } ahora está jugando.
now-spectating = { $player } ahora está observando.
spectator-left = { $player } dejó de observar.

welcome = ¡Bienvenido a PlayAural!
goodbye = ¡Hasta luego!

user-online = { $player } se conectó.
user-offline = { $player } se desconectó.
friend-online = Tu amigo { $player } ya está en línea.
friend-offline = Tu amigo { $player } se desconectó.
permission-denied = No tienes permiso para realizar esta acción sobre un desarrollador.
kick-user = Expulsar usuario
kick-broadcast = { $actor } expulsó a { $target }.
you-were-kicked = { $actor } te expulsó.
user-not-online = El usuario { $target } no está en línea.
kick-immune = No puedes expulsar a este usuario.
kick-confirm = ¿Seguro que quieres expulsar a { $player }?
no-users-to-kick = No hay usuarios disponibles para expulsar.
usage-kick = Uso: /kick <nombre de usuario>
online-users-none = No hay usuarios en línea.
online-users-one = 1 usuario: { $users }
online-users-many = { $count } usuarios: { $users }
online-user-not-in-game = Menú principal
online-user-waiting-approval = Esperando aprobación
presence-status-main-menu = Menú principal
presence-status-waiting-table = Esperando en una mesa de { $game }
presence-status-playing = Jugando { $game }
presence-status-spectating = Observando { $game }
presence-status-watching-table = Viendo una mesa de { $game }
presence-status-reviewing-results = Revisando resultados de { $game }
presence-status-spectating-results = Viendo resultados de { $game }
user-role-dev = Desarrollador
user-role-admin = Administrador
user-role-user = Usuario
client-type-web = Web
client-type-python = Escritorio
client-type-mobile = Móvil
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
online-user-actions-title = Acciones para { $username }
user-not-online-anymore = Este usuario ya no está en línea.
close-menu = Cerrar

language = Idioma
language-option = Idioma: { $language }
language-changed = Idioma establecido en { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. Idioma oficial de PlayAural. Traductores: { $translators }.
       *[false] { $language }. Traducción de la comunidad. Traductores: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. Metadatos del traductor no disponibles.
language-menu-current-entry = Actual: { $entry }

option-on = Activado
option-off = Desactivado

# Multi-select option sub-menu controls
option-back = Atrás
option-select-all = Seleccionar todo
option-deselect-all = Deseleccionar todo
option-selected-count = { $count } seleccionados
option-deselected-count = { $count } deseleccionados
option-min-selected = Debes seleccionar al menos { $count }.
option-max-selected = Puedes seleccionar como máximo { $count }.

turn-sound-option = Sonido de turno: { $status }

custom-bot-names-option = Nombres personalizados de bots: { $status }
confirm-destructive-option = Confirmar acciones arriesgadas: { $status }
clear-kept-option = Soltar dados guardados al lanzar: { $status }
option-notify-table-created = Avisar cuando se crea una mesa: { $status }
option-notify-user-presence = Notificaciones de conexión/desconexión de usuarios: { $status }
option-notify-friend-presence = Notificaciones de conexión/desconexión de amigos: { $status }
dice-keeping-style-option = Estilo para guardar dados: { $style }
dice-keeping-style-changed = Estilo para guardar dados establecido en { $style }.
dice-keeping-style-indexes = Posición de los dados
dice-keeping-style-values = Valores de los dados

# Personal options split: general vs game options
general-options = Opciones generales
game-options = Opciones de juego

# Game Options (declarative preferences with per-game overrides)
pref-category-display = Visualización
pref-set-brief-announcements = Anuncios breves: { $status }
pref-changed-brief-announcements = Anuncios breves { $status }.
pref-desc-brief-announcements = Acorta los anuncios de jugadas y eventos en partida; desactívalo para un comentario hablado más completo.
pref-category-sounds = Sonidos
pref-category-gameplay = Jugabilidad
pref-category-dice = Dados
pref-default = Predeterminado
pref-per-game-for = { $game }: { $value }
pref-reset-all = Restablecer todas las opciones de juego
pref-reset-category = Restablecer opciones de { $category }
pref-reset-done = Opciones de juego restablecidas.
pref-set-play-turn-sound = Sonido de turno: { $status }
pref-set-confirm-destructive-actions = Confirmar acciones arriesgadas: { $status }
pref-set-allow-custom-bot-names = Nombres personalizados de bots: { $status }
pref-set-clear-kept-on-roll = Soltar dados guardados al lanzar: { $status }
pref-set-dice-keeping-style = Estilo para guardar dados: { $choice }
pref-changed-play-turn-sound = Sonido de turno { $status }.
pref-changed-confirm-destructive-actions = Confirmar acciones arriesgadas { $status }.
pref-changed-allow-custom-bot-names = Nombres personalizados de bots { $status }.
pref-changed-clear-kept-on-roll = Soltar dados guardados al lanzar { $status }.
pref-changed-dice-keeping-style = Estilo para guardar dados establecido en { $choice }.
pref-desc-play-turn-sound = Reproduce un sonido cuando llega tu turno.
pref-desc-confirm-destructive-actions = Pide confirmación antes de acciones arriesgadas o irreversibles, como pasar en Pusoy Dos.
pref-desc-allow-custom-bot-names = Te permite poner nombres personalizados a los bots que añadas a una mesa.
pref-desc-clear-kept-on-roll = En juegos de dados compatibles como Yahtzee, suelta todos los dados guardados después de cada lanzamiento. Tu próximo lanzamiento vuelve a tirar todos los dados a menos que guardes algunos de nuevo; con Valores de los dados, usa Mayús+1-6 para guardar los dados que coincidan.
pref-desc-dice-keeping-style = Posición de los dados: usa 1-5, o 1-6 en Midnight, para alternar dados por posición. Valores de los dados: usa 1-6 para soltar un dado guardado con ese valor y Mayús+1-6 para guardar un dado suelto que coincida. Durante la fase de intercambio de Tradeoff, 1-6 guarda un dado que coincida y Mayús+1-6 lo marca para intercambiar; durante la fase de toma, 1-6 toma un dado que coincida del montón.

cancel = Cancelar
no-bot-names-available = No hay nombres de bot disponibles.
enter-bot-name = Ingresa el nombre del bot
bot-name-invalid-length = Los nombres de bot deben tener entre 3 y 30 caracteres.
bot-name-invalid-characters = Los nombres de bot solo pueden contener letras, números y espacios.
bot-name-already-used = Ya hay un jugador o bot con ese nombre en esta mesa.
bot-name-registered-account = Este nombre pertenece a una cuenta registrada. Elige otro nombre de bot.
table-name-already-used = Ya hay un jugador o bot con ese nombre en esta mesa.
no-options-available = No hay opciones disponibles.
no-scores-available = No hay puntuaciones disponibles.

option-desc-generic = { $label }. Predeterminado: { $default }.
option-desc-integer = { $label }. Ingresa un número entero de { $min } a { $max }. Predeterminado: { $default }.
option-desc-number = { $label }. Ingresa un número de { $min } a { $max }. Predeterminado: { $default }.
option-desc-menu = { $label }. Elige uno de: { $choices }. Predeterminado: { $default }.
option-desc-bool = { $label }. Activa este elemento para alternar entre activado y desactivado. Predeterminado: { $default }.
option-desc-multiselect = { $label }. Seleccionados ahora: { $selected }. Selecciones mínimas: { $min }. Selecciones máximas: { $max }. Seleccionados por defecto: { $default }.
option-desc-no-choices = no hay opciones disponibles por ahora
option-desc-none-selected = ninguno
option-desc-no-maximum = sin máximo

general-desc-profile = Consulta y edita los datos de tu perfil público.
general-desc-friends = Gestiona amigos, solicitudes de amistad, mensajes privados y acciones de mesa con amigos.
general-desc-my-stats = Revisa tus victorias, derrotas, puntuaciones y estadísticas de los juegos compatibles.
general-desc-general-options = Ajusta el idioma, el audio, la accesibilidad y las notificaciones de toda la cuenta.
general-desc-game-options = Ajusta preferencias de juego que pueden aplicarse de forma global o a juegos específicos.
general-desc-language = Elige el idioma que usan los menús, mensajes y documentación del servidor cuando estén disponibles.
general-desc-audio = Ajusta el volumen de la música, los efectos de sonido, el ambiente, el chat de voz, los sonidos de tecleo y el dispositivo de entrada de audio en escritorio.
general-desc-accessibility = Ajusta el comportamiento de lectura, entrada y del cliente relacionado con la accesibilidad disponible en este dispositivo.
general-desc-notifications = Elige qué notificaciones de chat, presencia y creación de mesas quieres escuchar.
general-desc-music-volume = Cambia el volumen de la música de fondo. Ponerlo en Desactivado silencia la música.
general-desc-sound-volume = Cambia el volumen de los efectos de sonido del juego. Los efectos se mantienen al menos al diez por ciento para que las señales importantes sigan siendo audibles.
general-desc-ambience-volume = Cambia el volumen del ambiente de fondo. Ponerlo en Desactivado silencia el ambiente.
general-desc-voice-volume = Cambia el volumen de reproducción del chat de voz de la mesa.
general-desc-audio-input-device = Elige el micrófono o dispositivo de entrada que usa el cliente de escritorio para el chat de voz.
general-desc-play-typing-sounds = Reproduce pequeños sonidos de tecleo al escribir en los campos de texto del cliente.
general-desc-web-speech-settings = Configura la salida de voz del navegador, incluido el modo ARIA live o Web Speech, la velocidad de habla y la voz.
general-desc-mobile-speech-settings = Configura el motor de texto a voz móvil, la voz y la velocidad de habla.
general-desc-invert-multiline-enter = Intercambia el comportamiento de enviar y salto de línea en los campos de texto multilínea del cliente de escritorio.
general-desc-mute-global-chat = Evita que los mensajes del chat global se lean en voz alta automáticamente.
general-desc-mute-table-chat = Evita que los mensajes del chat de mesa se lean en voz alta automáticamente.
general-desc-notify-user-presence = Anuncia cuando los usuarios se conectan o desconectan.
general-desc-notify-friend-presence = Anuncia cuando tus amigos se conectan o desconectan.
general-desc-notify-table-created = Anuncia cuando se crea una nueva mesa pública.
general-desc-speech-mode = Elige si el cliente web envía los anuncios al lector de pantalla mediante ARIA live o los lee con la API Web Speech del navegador.
general-desc-speech-rate = Cambia la velocidad de habla del cliente web.
general-desc-speech-voice = Elige la voz que usa la API Web Speech del cliente web, o vuelve a la predeterminada del navegador.
general-desc-mobile-tts-engine = Elige el motor de texto a voz móvil. Android usa actualmente el motor gestionado por el sistema.
general-desc-mobile-tts-voice = Elige la voz de texto a voz móvil, o vuelve a la predeterminada del sistema.
general-desc-mobile-tts-rate = Cambia la velocidad del texto a voz móvil.

saved-tables = Mesas guardadas
no-saved-tables = No tienes mesas guardadas.
no-active-tables = No hay mesas activas.
no-active-tables-all = No hay mesas activas disponibles.
no-active-tables-waiting = No hay mesas en espera disponibles.
no-active-tables-playing = No hay mesas en juego disponibles.
active-tables-filter = Filtro: { $filter }
filter-name-all = Todas
filter-name-waiting = Esperando
filter-name-playing = Jugando
game-category-filter = Categoría: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = Todas
game-category-cards = Juegos de cartas
game-category-poker = Juegos de póker
game-category-dice = Juegos de dados
game-category-board = Juegos de mesa
game-category-arcade = Juegos arcade
game-category-misc = Varios
no-games-in-category = No hay juegos disponibles en esta categoría.
restore-table = Restaurar
delete-saved-table = Eliminar
saved-table-deleted = Mesa guardada eliminada.
missing-players = No se puede restaurar: estos jugadores no están disponibles: { $players }
table-restored = ¡Mesa restaurada! Todos los jugadores fueron transferidos.
table-saved-destroying = ¡Mesa guardada! Volviendo al menú principal.
game-type-not-found = Ese tipo de juego ya no existe.

action-not-your-turn = No es tu turno.
action-not-playing = La partida aún no ha comenzado.
action-spectator = Los espectadores no pueden hacer esto.
action-not-host = Solo el anfitrión puede hacer esto.
action-not-available = Esa acción no está disponible en este momento.
action-game-in-progress = No puedes hacer esto mientras la partida está en curso.
action-need-more-players = Se necesitan más jugadores para empezar.
action-table-full = La mesa está llena.
action-start-needs-more-players = No se puede iniciar. Jugadores activos: { $current }. Mínimo requerido: { $minimum }.
action-start-has-too-many-players = No se puede iniciar. Jugadores activos: { $current }. Máximo permitido: { $maximum }.
action-start-requires-exact-players = No se puede iniciar. Jugadores activos: { $current }. Se requieren exactamente: { $required }.
action-no-bots = No hay bots para quitar.
action-bots-cannot = Los bots no pueden hacer esto.
action-no-scores = Aún no hay puntuaciones disponibles.

options-category-audio = Audio
options-category-accessibility = Accesibilidad
options-category-notifications = Notificaciones
options-category-game = Juego

music-volume-option = Volumen de música: { $value }%
sound-volume-option = Volumen de efectos de sonido: { $value }%
ambience-volume-option = Volumen de ambiente: { $value }%
voice-volume-option = Volumen del chat de voz: { $value }%
volume-choice-off = Desactivado
volume-choice-percent = { $value }%
volume-choice-current = { $label } (actual)
audio-input-device-option = Dispositivo de entrada de audio: { $device }
audio-input-device-default = Dispositivo de entrada predeterminado del sistema

mute-global-chat-option = Silenciar chat global: { $status }
mute-table-chat-option = Silenciar chat de mesa: { $status }
invert-multiline-enter-option = Invertir comportamiento de la tecla Enter: { $status }
play-typing-sounds-option = Reproducir sonidos de tecleo: { $status }
enter-music-volume = Ingresa el volumen de música (0-100)
enter-ambience-volume = Ingresa el volumen de ambiente (0-100)
enter-voice-volume = Ingresa el volumen del chat de voz (10-100)
invalid-volume = Volumen no válido.

dice-not-rolled = Aún no has lanzado los dados.
dice-no-dice = No hay dados disponibles.
table-no-players = No hay jugadores.
table-players-one = { $count } jugador: { $players }.
table-players-many = { $count } jugadores: { $players }.
table-spectators = Espectadores: { $spectators }.
table-host-suffix = (Anfitrión)
table-voice-chat-suffix = (en chat de voz)
table-members-summary = Resumen de la mesa: { $total } { $total ->
    [one] asiento
   *[other] asientos
}; { $real } { $real ->
    [one] persona real
   *[other] personas reales
}, { $bots } { $bots ->
    [one] bot
   *[other] bots
}; { $active } activos, { $spectators } observando.
table-members-empty = No hay miembros de la mesa listados por ahora. Usa Atrás para volver y actualizar la vista de la mesa.
table-member-entry = { $player }: { $status }
table-member-status-host = Anfitrión
table-member-status-player = Jugador
table-member-status-spectator = Espectador
table-member-status-bot = Bot
table-member-status-online = En línea
table-member-status-offline = Desconectado
table-member-status-voice-chat = en chat de voz
table-member-status-bot-takeover = bot jugando en su nombre: { $bot }
table-member-no-actions = No hay acciones disponibles para { $player }.
table-member-left = Esa persona ya no está en esta mesa.
table-member-bot-left = Ese bot ya no está en esta mesa.
game-over = Fin de la partida
game-final-scores = Puntuaciones finales
game-points = { $count } { $count ->
    [one] punto
   *[other] puntos
}

leaderboards = Tablas de clasificación
leaderboard-no-data = Aún no hay datos de clasificación para este juego.

leaderboard-type-wins = Líderes en victorias
leaderboard-type-rating = Puntuación de habilidad
leaderboard-type-total-score = Puntuación total
leaderboard-type-high-score = Puntuación máxima
leaderboard-type-games-played = Partidas jugadas
leaderboard-type-avg-points-per-turn = Promedio de puntos por turno
leaderboard-type-best-single-turn = Mejor turno individual
leaderboard-type-score-per-round = Puntuación por ronda
leaderboard-type-most-enemies-defeated = Más enemigos derrotados
leaderboard-type-deepest-wave-reached = Oleada más profunda alcanzada


leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] victoria
   *[other] victorias
} { $losses } { $losses ->
    [one] derrota
   *[other] derrotas
}, { $percentage }% de victorias
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } partidas
leaderboard-avg-entry = { $rank }. { $player }: { $value }

leaderboard-no-player-stats = Aún no has jugado este juego.

leaderboard-no-ratings = Aún no hay datos de puntuación para este juego.
leaderboard-rating-entry = { $rank }. { $player }: puntuación { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Aún no tienes una puntuación para este juego.

my-stats = Mis estadísticas
my-stats-select-game = Elige un juego para ver tus estadísticas
my-stats-no-data = Aún no has jugado este juego.
my-stats-no-games = Aún no has jugado ninguna partida.
my-stats-header = { $game } - Tus estadísticas
my-stats-wins = Victorias: { $value }
my-stats-losses = Derrotas: { $value }
my-stats-winrate = Porcentaje de victorias: { $value }%
my-stats-games-played = Partidas jugadas: { $value }
my-stats-total-score = Puntuación total: { $value }
my-stats-high-score = Puntuación máxima: { $value }
my-stats-rating = Puntuación de habilidad: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Aún no hay puntuación de habilidad
my-stats-avg-per-turn = Promedio de puntos por turno: { $value }
my-stats-best-turn = Mejor turno individual: { $value }
my-stats-score-per-round = Puntuación por ronda: { $value }
my-stats-most-enemies-defeated = Más enemigos derrotados: { $value }
my-stats-deepest-wave-reached = Oleada más profunda alcanzada: { $value }

predict-outcomes = Predecir resultados
predict-header = Resultados predichos (según puntuación de habilidad)
predict-note-multiplayer = Los porcentajes de victoria solo se muestran en partidas de 2 jugadores. Con 3 o más jugadores humanos, solo se muestran las puntuaciones de habilidad.
predict-entry = { $rank }. { $player } (puntuación: { $rating })
predict-entry-2p = { $rank }. { $player } (puntuación: { $rating }, { $probability }% de probabilidad de ganar)
predict-unavailable = Las predicciones de puntuación no están disponibles.
predict-need-players = Se necesitan al menos 2 jugadores humanos para las predicciones.
action-need-more-humans = Se necesitan más jugadores humanos.
confirm-leave-game = ¿Seguro que quieres salir de la mesa?
confirm-yes = Sí
confirm-no = No

administration = Administración

account-approval = Aprobación de cuentas
no-pending-accounts = No hay cuentas pendientes.
approve-account = Aprobar
decline-account = Rechazar
account-approved = La cuenta de { $player } ha sido aprobada.
account-declined = La cuenta de { $player } fue rechazada y eliminada.

waiting-for-approval = Tu cuenta está esperando la aprobación de un administrador. Por favor espera...
account-approved-welcome = ¡Tu cuenta fue aprobada! ¡Bienvenido a PlayAural!
account-declined-goodbye = Tu solicitud de cuenta fue rechazada.

account-request = solicitud de cuenta
account-action = acción de cuenta realizada

promote-admin = Ascender a administrador
demote-admin = Degradar administrador
ban-user = Banear usuario
unban-user = Quitar baneo
no-users-to-promote = No hay usuarios disponibles para ascender.
no-admins-to-demote = No hay administradores disponibles para degradar.
admin-search-users = Buscar por nombre de usuario
admin-search-users-current = Buscar por nombre de usuario. Búsqueda actual: { $query }.
admin-search-prompt = Ingresa todo o parte de un nombre de usuario para buscar. Déjalo en blanco para explorar todos los resultados por página.
menu-page-summary = Mostrando { $start }-{ $end } de { $total } entradas. Página { $page } de { $pages }.
menu-page-summary-query = Búsqueda "{ $query }": mostrando { $start }-{ $end } de { $total } entradas. Página { $page } de { $pages }.
menu-page-refresh = Actualizar lista
menu-list-refreshed = Lista actualizada.
menu-page-first = Primera página
menu-page-previous = Página anterior
menu-page-next = Página siguiente
menu-page-last = Última página
admin-search-no-results = No se encontraron usuarios coincidentes. Usa Buscar por nombre de usuario para probar con otro término.
confirm-promote = ¿Seguro que quieres ascender a { $player } a administrador?
confirm-demote = ¿Seguro que quieres degradar a { $player } de administrador?
broadcast-to-all = Anunciar a todos los usuarios
broadcast-to-admins = Anunciar solo a administradores
broadcast-to-nobody = Silencioso (sin anuncio)
promote-announcement = ¡{ $player } fue ascendido a administrador!
promote-announcement-you = ¡Fuiste ascendido a administrador!
demote-announcement = { $player } fue degradado de administrador.
demote-announcement-you = Fuiste degradado de administrador.
not-admin-anymore = Ya no eres administrador y no puedes realizar esta acción.
dev-only-action = Esta acción está restringida solo a desarrolladores.

ban-duration-1h = 1 hora
ban-duration-6h = 6 horas
ban-duration-12h = 12 horas
ban-duration-1d = 1 día
ban-duration-3d = 3 días
ban-duration-1w = 1 semana
ban-duration-1m = 1 mes
ban-duration-permanent = Permanente

reason-spam = Spam
reason-harassment = Acoso
reason-cheating = Hacer trampa
reason-inappropriate = Comportamiento inapropiado
reason-custom = Otro / Personalizado

no-users-to-ban = No hay usuarios disponibles para banear.
no-banned-users = No hay usuarios baneados actualmente.
admin-active-ban-entry = { $username }. Vencimiento del baneo: { $expires }. Motivo: { $reason }. Emitido por: { $admin }.
admin-active-mute-entry = { $username }. Vencimiento del silencio: { $expires }. Motivo: { $reason }. Emitido por: { $admin }.
admin-penalty-expiry-permanent = permanente
admin-penalty-expiry-unknown = vencimiento desconocido
admin-penalty-expiry-expired = ya venció
admin-penalty-expiry-timed = { $date } (quedan { $remaining })
admin-penalty-reason-unknown = motivo no especificado
admin-penalty-admin-unknown = administrador desconocido
admin-penalty-remaining-days = { $count ->
    [one] 1 día
   *[other] { $count } días
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

ban-broadcast = { $actor } baneó a { $target } por { $reason }. Duración: { $duration }.
unban-broadcast = { $actor } le quitó el baneo a { $target }.

banned-menu-title = Cuenta baneada
banned-reason = Motivo: { $reason }
banned-expires = Vence: { $expires }
banned-permanent = Vence: Permanente
disconnect = Desconectar


mute-user = Silenciar usuario
unmute-user = Quitar silencio
no-users-to-mute = No hay usuarios disponibles para silenciar.
no-muted-users = No hay usuarios silenciados actualmente.
mute-duration-5m = 5 minutos
mute-duration-15m = 15 minutos
mute-duration-30m = 30 minutos
mute-duration-1h = 1 hora
mute-duration-6h = 6 horas
mute-duration-1d = 1 día
mute-duration-permanent = Permanente
mute-broadcast = { $actor } silenció a { $target } por { $reason }. Duración: { $duration }.
unmute-broadcast = { $actor } le quitó el silencio a { $target }.
you-have-been-muted = Fuiste silenciado. Motivo: { $reason }. Duración: { $duration }.
you-have-been-unmuted = Se te quitó el silencio. Ya puedes chatear de nuevo.
muted-remaining-seconds = Estás silenciado. Quedan { $seconds } segundos.
muted-remaining-minutes = Estás silenciado. Quedan { $minutes } minutos.
muted-permanent = Estás silenciado de forma permanente. Contacta a un administrador para más información.
auto-muted-seconds = Fuiste silenciado temporalmente por hacer spam. Quedan { $seconds } segundos.
auto-muted-minutes = Fuiste silenciado temporalmente por hacer spam. Quedan { $minutes } minutos.
auto-muted-applied-seconds = Se te silenció automáticamente por { $seconds } segundos por exceso de spam en el chat.
auto-muted-applied-minutes = Se te silenció automáticamente por { $minutes } minutos por exceso de spam en el chat.
chat-rate-limited = ¡Más despacio! Estás enviando mensajes demasiado rápido.
chat-global-disabled-send = El chat global está desactivado en tus opciones. Actívalo antes de enviar mensajes globales.
chat-table-disabled-send = El chat de mesa está desactivado en tus opciones. Actívalo antes de enviar mensajes en la mesa.
admin-spam-alert = Advertencia: { $username } está haciendo spam excesivo en el chat y fue silenciado automáticamente.

broadcast-announcement = Anuncio general
admin-broadcast-prompt = Ingresa el mensaje para anunciar a todos los usuarios en línea. (¡Esto se enviará a todos!)
admin-broadcast-sent = Anuncio enviado a { $count } usuarios.

manage-motd = Gestionar mensaje del día
create-update-motd = Crear/Actualizar mensaje del día
view-motd = Ver mensaje del día activo
delete-motd = Eliminar mensaje del día
motd-version-prompt = Ingresa el número de versión del nuevo mensaje del día (debe ser mayor que 0):
invalid-motd-version = Versión de mensaje del día no válida. Debe ser un número positivo.
motd-created = Se creó correctamente la versión { $version } del mensaje del día.
motd-deleted = El mensaje del día fue eliminado.
motd-delete-empty = No hay ningún mensaje del día activo para eliminar.
motd-not-exists = No existe ningún mensaje del día activo.
motd-announcement = Mensaje del día
motd-broadcast = Nuevo mensaje del día: { $message }
error-no-languages = Error: No se encontraron idiomas.
ok = Aceptar

unknown-player = Jugador desconocido

logout-confirm-title = ¿Seguro que quieres cerrar sesión y salir del juego?
logout-confirm-yes = Sí, cerrar sesión
logout-confirm-no = No, quedarme

system-name = Sistema
server-restarting = El servidor se reiniciará en { $seconds } segundos...
server-restarting-now = El servidor se está reiniciando ahora. Vuelve a conectarte en un momento.
server-shutting-down = El servidor se apagará en { $seconds } segundos...
server-shutting-down-now = El servidor se está apagando ahora. ¡Hasta luego!
server-power-management = Gestión de energía del servidor
server-power-reboot = Reiniciar servidor
server-power-shutdown = Apagar servidor
server-power-cancel = Cancelar acción de energía programada
server-power-active-status = { $action } programado. Motivo: { $reason }.
server-power-action-reboot = reinicio
server-power-action-shutdown = apagado
server-power-delay-30s = En 30 segundos
server-power-delay-1m = En 1 minuto
server-power-delay-5m = En 5 minutos
server-power-delay-10m = En 10 minutos
server-power-delay-30m = En 30 minutos
server-power-delay-1h = En 1 hora
server-power-delay-2h = En 2 horas
server-power-delay-custom = Retraso personalizado en minutos
server-power-custom-delay-prompt = Ingresa el retraso en minutos, de 1 a { $max }:
server-power-invalid-custom-delay = Retraso no válido. Ingresa un número entero de minutos de 1 a { $max }.
server-power-reason-update = Actualización
server-power-reason-maintenance = Mantenimiento
server-power-reason-security = Seguridad
server-power-reason-technical = Problema técnico
server-power-reason-custom = Motivo personalizado
server-power-reason-unspecified = motivo no especificado
server-power-confirm-summary = Confirmar { $action } del servidor en { $duration }. Motivo: { $reason }.
server-power-scheduled = { $action } del servidor programado en { $duration }.
server-power-already-scheduled = Ya hay una acción de energía del servidor programada. Cancélala antes de programar otra.
server-power-cancel-none = No hay ninguna acción de energía del servidor programada actualmente.
server-power-cancelled = Se canceló la acción de energía del servidor programada.
server-power-cancelled-broadcast = { $admin } canceló el { $action } programado del servidor.
server-power-command-removed = Los comandos de chat /reboot y /stop fueron eliminados. Usa Administración, Gestión de energía del servidor en su lugar.
server-power-finalizing-input-blocked = El servidor está finalizando un reinicio o apagado. Espera a que el cliente se desconecte.
server-power-finalize-failed = El { $action } programado del servidor no pudo completarse de forma segura. El servidor sigue en línea; contacta a un administrador.
server-power-reboot-warning = Reinicio del servidor en { $duration }. Motivo: { $reason }. No te desconectes manualmente; tu cliente se reconectará automáticamente y las mesas activas se conservarán.
server-power-shutdown-warning = Apagado del servidor en { $duration }. Motivo: { $reason }. El servidor se desconectará; guarda las partidas que quieras conservar antes del apagado.
server-power-reboot-now = El servidor se está reiniciando ahora. Motivo: { $reason }. No te desconectes manualmente; tu cliente se reconectará automáticamente y las mesas activas se conservarán.
server-power-shutdown-now = El servidor se está apagando ahora. Motivo: { $reason }. El servidor quedará fuera de línea.
server-power-restore-waiting = Esta mesa se restauró después de un reinicio planificado. Esperando hasta { $seconds } segundos a que los demás jugadores se reconecten antes de reemplazar los asientos faltantes con bots.
server-power-restore-input-blocked = Esta mesa todavía se está recuperando del reinicio planificado. La partida está en pausa hasta { $seconds } segundos más mientras se espera a { $players }; inténtalo de nuevo cuando termine el periodo de gracia.
server-power-restore-missing-players-fallback = los jugadores restantes
server-power-restore-complete = Todos los jugadores activos se reconectaron después del reinicio planificado. Partida reanudada.
server-power-restore-complete-with-bots = El periodo de gracia terminó tras el reinicio planificado. Los asientos faltantes fueron reemplazados con bots y la partida se está reanudando.
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
duration-minutes-seconds = { $minutes } minutos y { $seconds } segundos
duration-hours-minutes = { $hours } horas y { $minutes } minutos
server-error-changing-language = Error al cambiar el idioma: { $error }
default-save-name = { $game } - { $date }

speech-settings = Configuración de voz
speech-mode-option = Modo de voz: { $status }
speech-rate-option = Velocidad de voz: { $value }%
speech-voice-option = Voz: { $voice }
select-voice = Seleccionar voz
enter-speech-rate = Ingresa la velocidad de voz (50-300)
invalid-rate = Velocidad de voz no válida. Usa un valor entre 50 y 300.
mode-aria = Aria-live
mode-web-speech = API Web Speech
default-voice = Voz predeterminada
mobile-speech-settings = Configuración de voz móvil
mobile-tts-engine-option = Motor de TTS: { $engine }
mobile-tts-engine-system = Predeterminado del sistema
mobile-tts-engine-system-selected = Motor de TTS predeterminado del sistema
mobile-tts-engine-api-note = En esta versión, la selección del motor en Android se gestiona desde la configuración del sistema.
mobile-tts-voice-option = Voz móvil: { $voice }
mobile-tts-rate-option = Velocidad de voz móvil: { $value }%
mobile-tts-enter-rate = Ingresa la velocidad de voz móvil (50-200)
mobile-tts-invalid-rate = Velocidad de voz móvil no válida. Usa un valor entre 50 y 200.

player-kicked-offline = El jugador { $player } fue expulsado (desconectado).
game-paused-host-disconnect = Partida en pausa. Esperando a que { $player } se reconecte...
game-resumed = { $player } se reconectó. ¡Partida reanudada!

auth-error-username-length = El nombre de usuario debe tener entre 3 y 30 caracteres.
auth-error-username-invalid-chars = El nombre de usuario solo puede contener letras, números y espacios (sin espacios consecutivos ni caracteres especiales).
auth-error-password-weak = La contraseña debe tener al menos 8 caracteres e incluir letras y números.

personal-and-options = Personal y opciones
profile = Perfil
friends = Amigos
profile-registration-date = Fecha de registro: { $date }
profile-username = Nombre de usuario: { $username }
profile-email = Correo: { $email }
admin-view-email = Vista de administrador - Correo: { $email }
profile-gender = Género: { $gender }
profile-bio = Biografía: { $bio }
profile-bio-empty = Sin definir
profile-email-empty = Sin definir

gender-male = Masculino
gender-female = Femenino
gender-non-binary = No binario
gender-not-set = Sin definir

action-set-edit = Definir / Editar
action-delete = Eliminar
bio-already-empty = La biografía ya está vacía.
bio-deleted = Biografía eliminada.
bio-updated = Biografía actualizada.

enter-email = Ingresa tu nueva dirección de correo:
email-updated = Dirección de correo actualizada.
enter-bio = Ingresa tu biografía:

gender-updated = Género actualizado.
no-changes-made = No se realizaron cambios.
confirm-email-change = ¿Seguro que quieres cambiar tu correo a { $email }?

mandatory-email-notice = Debes establecer un correo para seguir participando. Tu correo es privado y solo tú lo conoces.
error-email-empty = El correo es obligatorio y no puede estar vacío.
error-email-invalid = Formato de correo no válido. Proporciona una dirección de correo válida.
reg-error-email = Se requiere un correo para registrarte.

error-email-taken = Este correo ya está en uso por otra cuenta.

error-bio-length = La biografía no puede superar los 250 caracteres.
error-captcha-failed = La verificación falló. Inténtalo de nuevo.
error-rate-limit-login = Demasiados intentos fallidos de inicio de sesión. Inténtalo de nuevo en 15 minutos.
error-rate-limit-register = Alcanzaste el número máximo de registros de cuenta permitidos por hoy.
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = Mis amigos
friends-pending-requests = Solicitudes pendientes ({ $count })
friends-no-pending-requests = Solicitudes pendientes
friends-send-request = Enviar solicitud de amistad
friends-list-empty = Aún no tienes amigos.
friend-status-offline = Desconectado
friend-status-playing = Jugando { $game }
friend-status-spectating = Observando { $game }
friend-status-lobby = Menú principal
friend-list-entry = { $username } ({ $status })

friend-actions-title = Acciones para { $username }
view-profile = Ver perfil
join-table = Unirse a la mesa
remove-friend = Eliminar amigo
friend-remove-confirm = ¿Eliminar a { $username } de tu lista de amigos?
friend-remove-not-friends = { $username } ya no está en tu lista de amigos.
already-in-table = Ya estás en esta mesa.
friend-removed-success = { $username } fue eliminado de tu lista de amigos.
friend-removed-notify = { $username } te eliminó de su lista de amigos.

no-pending-requests = No hay solicitudes pendientes.
friend-request-from = Solicitud de amistad de { $username }
accept = Aceptar
decline = Rechazar
friend-accepted-success = Ahora eres amigo de { $username }.
friend-accepted-notify = ¡{ $username } aceptó tu solicitud de amistad!
request-not-found = La solicitud de amistad ya no existe.
friend-declined-success = Solicitud de amistad rechazada.
friend-declined-notify = { $username } rechazó tu solicitud de amistad.

public-profile-title = Perfil de { $username }
enter-friend-username = Ingresa el nombre de usuario de la persona que quieres agregar como amigo:
friend-error-self = No puedes enviarte una solicitud de amistad a ti mismo.
friend-error-already-friends = Ya eres amigo de este usuario.
friend-error-duplicate = Ya tienes una solicitud de amistad pendiente con este usuario.
friend-request-sent = Solicitud de amistad enviada a { $username }.
friend-request-received = Recibiste una nueva solicitud de amistad de { $username }.

friends-grouped-requests = Tienes solicitudes de amistad pendientes de: { $usernames }
friends-grouped-accepted = Tus solicitudes de amistad fueron aceptadas por: { $usernames }
friends-grouped-declined = Tus solicitudes de amistad fueron rechazadas por: { $usernames }
friends-grouped-removed = Fuiste eliminado de la lista de amigos por: { $usernames }
friends-and-others = { $names } y { $count } { $count ->
    [one] más
   *[other] más
}

send-private-message = Enviar mensaje privado
enter-pm-message = Ingresa tu mensaje para { $username }:
pm-error-not-friends = Solo puedes enviar mensajes privados a tus amigos.
pm-error-offline = { $username } no está en línea en este momento.
pm-sent-success = Mensaje enviado a { $username }.
pm-sent-content = Tú a { $username }: { $message }
pm-received = Mensaje privado de { $username }: { $message }

host-management = Gestión del anfitrión
table-spectator-suffix = (Espectador)
host-management-set-private = Establecer mesa como privada
host-management-set-public = Establecer mesa como pública
host-management-invite = Invitar a un amigo
host-management-pass-host = Ceder el anfitrionazgo a otro jugador
host-management-kick = Expulsar a un jugador
host-management-kick-ban = Expulsar y banear a un jugador
host-management-restart-game = Reiniciar partida
host-management-table-now-private = Esta mesa ahora es privada. Solo los jugadores invitados pueden unirse.
host-management-table-now-public = Esta mesa ahora es pública.
host-restart-confirm = ¿Reiniciar la partida actual y devolver esta mesa a la sala de espera? Los jugadores actuales y el chat de voz seguirán conectados, pero la partida en curso se cancelará.
host-restart-broadcast = { $player } reinició la partida. La mesa volvió a la sala de espera.
host-restart-not-playing = No hay ninguna partida activa para reiniciar.
host-invite-no-friends = (No hay amigos disponibles para invitar)
host-invite-sent = Invitación enviada a { $player }.
host-invite-friend-unavailable = Ese amigo no está en línea en este momento.
host-invite-already-pending = Ya hay una invitación pendiente para ese amigo.
host-invite-friend-busy = Ese amigo ya está en una partida.
host-invite-declined = { $player } rechazó tu invitación a la mesa.
table-invite-received = { $host } te invitó a su mesa de { $game }.
table-invite-queued = { $host } te invitó a su mesa de { $game }. Termina tu entrada actual para responder.
table-invite-expired = La invitación a la mesa caducó.
invite-accept = Aceptar invitación
invite-decline = Rechazar invitación
host-management-no-longer-host = Ya no eres el anfitrión de esta mesa.
host-pass-no-candidates = (No hay jugadores disponibles para ceder el anfitrionazgo)
host-pass-no-longer-host = Cediste el anfitrionazgo a otro jugador. Ya no eres el anfitrión de esta mesa.
host-passed = { $player } ahora es el anfitrión.
host-pass-failed = No se pudo transferir el anfitrionazgo. Es posible que el jugador se haya ido.
host-kick-no-candidates = (No hay jugadores disponibles para expulsar)
host-kick-invalid-target = Objetivo de expulsión no válido.
host-kick-broadcast = { $player } fue expulsado de la mesa.
host-kick-ban-broadcast = { $player } fue expulsado y baneado de la mesa.
host-kick-you = { $host } te expulsó de la mesa.
host-kick-ban-you = { $host } te expulsó y baneó de la mesa.
table-you-are-banned = Estás baneado de esta mesa.
table-private-invite-only = Esta mesa es privada. El anfitrión debe invitarte para que puedas unirte.

voice-room-table-label = Voz de la mesa de { $game }
voice-unavailable = El chat de voz no está disponible en este momento.
voice-invalid-context = Esa solicitud de sala de voz no es válida.
voice-not-at-table = Aún no te has unido a una mesa. Únete a una mesa antes de iniciar el chat de voz.
voice-not-in-context = Debes estar en esa mesa antes de unirte a su chat de voz.
voice-rate-limited = Más despacio. El chat de voz está cambiando demasiado rápido en este momento.
voice-muted-seconds = Estás silenciado y no puedes unirte al chat de voz. Quedan { $seconds } segundos.
voice-muted-minutes = Estás silenciado y no puedes unirte al chat de voz. Quedan { $minutes } minutos.
voice-muted-permanent = Estás silenciado y no puedes unirte al chat de voz.
voice-status-connected = { $player } se conectó al chat de voz de la mesa.
voice-status-disconnected = { $player } se desconectó del chat de voz.
voice-status-connection-lost = { $player } perdió la conexión y fue eliminado del chat de voz.
voice-status-left-table = { $player } salió de la mesa y del chat de voz.

error-smtp-not-configured = La recuperación de contraseña está desactivada actualmente por el administrador.
error-email-not-found = No se encontró ninguna cuenta con ese correo.
success-reset-email-sent = Se envió un código de restablecimiento a tu correo.
error-smtp-send-failed = No se pudo enviar el correo de restablecimiento. Inténtalo de nuevo más tarde.
error-invalid-reset-code = Código de restablecimiento no válido o caducado.
success-password-reset = Tu contraseña se restableció correctamente. Ya puedes iniciar sesión.

admin-localized-text-subject-motd = mensaje del día
admin-localized-text-subject-power = motivo de energía del servidor
admin-localized-text-subject-ban = motivo de baneo personalizado
admin-localized-text-subject-mute = motivo de silencio personalizado
admin-localized-text-instructions = Edita las traducciones de { $subject }. Los idiomas oficiales son obligatorios. Los idiomas de la comunidad son opcionales y usan { $fallback } cuando están vacíos.
admin-localized-text-motd-version = Versión del mensaje del día: { $version }
admin-localized-text-official-heading = Idiomas oficiales, obligatorio
admin-localized-text-community-heading = Idiomas de la comunidad, opcional
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = ingresado, obligatorio
admin-localized-text-required-missing = no ingresado, obligatorio
admin-localized-text-optional-set = ingresado, opcional
admin-localized-text-optional-fallback = no ingresado, opcional, usa el valor de respaldo
admin-localized-text-prompt = Ingresa el { $subject } en { $language }. Máximo { $max } caracteres.
admin-localized-text-too-long = Esa traducción es demasiado larga. El máximo es { $max } caracteres.
admin-localized-text-missing-required = Ingresa primero todas las traducciones obligatorias. Faltan: { $languages }.
admin-localized-text-publish-motd = Publicar mensaje del día
admin-localized-text-continue = Continuar
admin-localized-text-apply-ban = Aplicar baneo
admin-localized-text-apply-mute = Aplicar silencio
