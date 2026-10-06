auth-username-password-required = Se requieren un nombre de usuario y una contraseña.
auth-registration-success = ¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.
auth-username-taken = Ese nombre de usuario ya está en uso. Elige otro.
auth-registration-error = El registro falló debido a un error del servidor. Inténtalo de nuevo.
auth-error-wrong-password = Contraseña incorrecta.
auth-error-user-not-found = El usuario no existe.
username-ambiguous = Más de una cuenta antigua coincide con “{ $username }”. Ingresa la ortografía exacta con la que está registrada.
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

play = Jugar
view-active-tables = Ver mesas activas
options = Opciones
logout = Cerrar sesión
back = Atrás
go-back = Volver
context-menu = Menú contextual.
no-actions-available = No hay acciones disponibles.
table-new-host-promoted = { $player } ahora es el anfitrión de la mesa.
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
table-listing-game-composition-status = { $game } [{ $status }]: mesa de { $host }. { $composition }.
table-composition-human-players = { $count } { $count ->
    [one] jugador
   *[other] jugadores
}: { $names }
table-composition-bots = { $count } { $count ->
    [one] bot
   *[other] bots
}
table-composition-spectators = { $count ->
    [one] Espectador
   *[other] Espectadores
}: { $names }
table-composition-spectators-more = Espectadores: { $names }; y { $remaining } más
table-composition-spectator-host = { $host } (anfitrión)
table-composition-two = { $first }; { $second }
table-composition-three = { $first }; { $second }; { $third }
table-composition-empty = sin participantes
table-status-waiting = Esperando
table-status-playing = Jugando
table-status-finished = Terminada
table-not-exists = La mesa ya no existe.
table-full = La mesa está llena.
table-join-social-blocked = No puedes entrar a esta mesa porque el contacto social directo no está disponible entre tú y su anfitrión. Aun así puedes recuperar un asiento ya reservado para ti.
table-closed-disconnect-timeout = La mesa se cerró porque ningún jugador activo regresó dentro de { $minutes } minutos.
player-replaced-by-bot = { $bot } ahora está jugando en nombre de { $player }.
player-reclaimed-from-bot = { $player } regresó y recuperó { GENDER_TERM($player_gender, "possessive-determiner") } asiento de manos de { $bot }.
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
user-not-online = El usuario { $target } no está en línea.
kick-confirm = ¿Seguro que quieres expulsar a { $player }?
no-users-to-kick = No hay usuarios disponibles para expulsar.
usage-kick = Uso: /kick <nombre de usuario>
online-users-none = No hay usuarios en línea.
online-users-summary = { $count ->
    [one] { $count } usuario en línea. { $groups }
   *[other] { $count } usuarios en línea. { $groups }
}
online-users-group = { $role ->
    [dev] { $count ->
        [one] { $count } desarrollador: { $users }.
       *[other] { $count } desarrolladores: { $users }.
    }
    [admin] { $count ->
        [one] { $count } administrador: { $users }.
       *[other] { $count } administradores: { $users }.
    }
   *[user] { $staff_count ->
        [0] { $users }.
       *[other] { $count ->
            [one] { $count } usuario: { $users }.
           *[other] { $count } usuarios: { $users }.
        }
    }
}
online-users-more = { $count } más
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
option-multiselect-group = { $group } ({ $count } de { $total } seleccionados)
option-min-selected = Debes seleccionar al menos { $count }.
option-max-selected = Puedes seleccionar como máximo { $count }.

custom-bot-names-option = Nombres personalizados de bots: { $status }
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
pref-desc-clear-kept-on-roll = En juegos de dados compatibles como Yahtzee, suelta todos los dados guardados después de cada lanzamiento. Tu próximo lanzamiento vuelve a tirar todos los dados a menos que guardes algunos de nuevo; con Valores de los dados, usa Shift+1-6 para guardar los dados que coincidan.
pref-desc-dice-keeping-style = Posición de los dados: usa 1-5, o 1-6 en Midnight, para alternar dados por posición. Valores de los dados: usa 1-6 para soltar un dado guardado con ese valor y Shift+1-6 para guardar un dado suelto que coincida. Durante la fase de intercambio de Tradeoff, 1-6 guarda un dado que coincida y Shift+1-6 lo marca para intercambiar; durante la fase de toma, 1-6 toma un dado que coincida del montón.

cancel = Cancelar
enter-bot-name = Ingresa el nombre del bot
bot-name-invalid-length = Los nombres de bot deben tener entre 3 y 30 caracteres.
bot-name-invalid-characters = Los nombres de bot solo pueden contener letras, números y espacios.
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
menu-item-with-hint = { $label }: { $hint }

general-desc-profile = Consulta y edita los datos de tu perfil público.
general-desc-friends = Gestiona amigos, solicitudes de amistad, mensajes privados y acciones de mesa con amigos.
general-desc-my-stats = Revisa tus victorias, derrotas, puntuaciones y estadísticas de los juegos compatibles.
general-desc-general-options = Ajusta el idioma, el chat global, el audio, la accesibilidad, las notificaciones y las preferencias de juego.
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
general-desc-menu-hints = Muestra las descripciones disponibles directamente en las filas del menú. Cuando está desactivado, enfoca un elemento con descripción y pulsa F1 en Escritorio o en la Web con un teclado físico, o toca una vez con tres dedos en el modo de autolectura móvil para escucharla.
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
saved-table-blocked-by-you = Esta mesa guardada incluye jugadores que bloqueaste: { $players }. Para restaurarla, abre Personal y Opciones, Amigos, y luego Usuarios Bloqueados para desbloquearlos. La restauración solo puede continuar si el contacto social directo está disponible para todos. La mesa guardada se conservó.
saved-table-social-blocked = Esta mesa guardada no se puede restaurar porque el contacto social directo no está disponible entre tú y: { $players }. La mesa guardada se conservó.
saved-table-social-blocked-mixed = Esta mesa guardada incluye jugadores que bloqueaste: { $blocked }. Abre Personal y Opciones, Amigos, y luego Usuarios Bloqueados para desbloquearlos. El contacto social directo tampoco está disponible con: { $unavailable }. La mesa guardada se conservó.
saved-table-invalid = Esta mesa guardada ya no se puede restaurar porque sus datos de partida o de jugadores están incompletos o son incompatibles. La mesa guardada se conservó.
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
action-start-needs-human-player = No se puede iniciar solo con bots. Al menos un humano debe participar como jugador. Cambia de espectador a jugador; si la mesa está llena, primero elimina a un bot.
action-no-bots = No hay bots para quitar.
action-bots-cannot = Los bots no pueden hacer esto.
options-category-audio = Audio
options-category-accessibility = Accesibilidad
options-category-notifications = Notificaciones
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
menu-hints-option = Ayudas del menú: { $status }
menu-hints-changed = Las ayudas del menú ahora están { $status }.
play-typing-sounds-option = Reproducir sonidos de tecleo: { $status }
invalid-volume = Volumen no válido.

dice-not-rolled = Aún no has lanzado los dados.
dice-no-dice = No hay dados disponibles.
table-no-players = No hay jugadores.
table-players-one = { $count } jugador: { $players }.
table-players-many = { $count } jugadores: { $players }.
table-spectators = Espectadores: { $spectators }.
table-host-suffix = (Anfitrión)
table-voice-chat-suffix = (en chat de voz)
table-members-summary-compact = Resumen de la mesa: { $composition }.
table-summary-human-players = { $count } { $count ->
    [one] jugador humano
   *[other] jugadores humanos
}
table-summary-bots = { $count } { $count ->
    [one] bot
   *[other] bots
}
table-summary-spectators = { $count } { $count ->
    [one] espectador
   *[other] espectadores
}
table-members-empty = No hay miembros de la mesa listados por ahora. Usa Atrás para volver y actualizar la vista de la mesa.
table-member-entry = { $player }: { $status }
table-member-status-host = Anfitrión
table-member-status-player = Jugador
table-member-status-spectator = Espectador
table-member-status-bot = Bot
table-member-status-online = En línea
table-member-status-offline = Desconectado
table-member-status-voice-chat = en chat de voz
table-member-status-bot-takeover = bot jugando en { GENDER_TERM($member_gender, "possessive-determiner") } nombre: { $bot }
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
leaderboard-rating-entry = { $rank }. { $player }: puntuación { $rating }
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
my-stats-rating = Puntuación de habilidad: { $value }
my-stats-no-rating = Aún no hay puntuación de habilidad
my-stats-custom = { $name }: { $value }
my-stats-avg-per-turn = Promedio de puntos por turno: { $value }
my-stats-best-turn = Mejor turno individual: { $value }
my-stats-score-per-round = Puntuación por ronda: { $value }
my-stats-most-enemies-defeated = Más enemigos derrotados: { $value }
my-stats-deepest-wave-reached = Oleada más profunda alcanzada: { $value }

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
admin-role-target-changed = { $player } ya no tiene el rol esperado. Actualiza la lista e inténtalo de nuevo.
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
chat-rate-limited = ¡Más despacio! Estás enviando mensajes demasiado rápido.
chat-global-disabled-send = El chat global está desactivado en tus opciones. Actívalo antes de enviar mensajes globales.
chat-table-disabled-send = El chat de mesa está desactivado en tus opciones. Actívalo antes de enviar mensajes en la mesa.
chat-invalid-channel = Ese canal de chat no está disponible.
chat-invalid-message = Ese mensaje no se pudo enviar porque su formato no es válido.
chat-message-too-long = Ese mensaje es demasiado largo. Los mensajes pueden tener como máximo { $limit } caracteres.

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
unknown-user = Usuario desconocido
user-account-unavailable = Esta cuenta de usuario ya no está disponible.

logout-confirm-title = ¿Seguro que quieres cerrar sesión y salir del juego?
logout-confirm-yes = Sí, cerrar sesión
logout-confirm-no = No, quedarme

system-name = Sistema
server-restarting = El servidor se reiniciará en { $seconds } segundos...
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
server-error-changing-language = No se pudo cambiar el idioma. Tu interfaz anterior sigue activa.
default-save-name = { $game } - { $date }

speech-settings = Configuración de voz
speech-mode-option = Modo de voz: { $status }
speech-rate-option = Velocidad de voz: { $value }%
speech-voice-option = Voz: { $voice }
select-voice = Seleccionar voz
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
profile-date-unknown = Desconocida

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
friends-block-user = Bloquear a un usuario
friends-list-empty = Aún no tienes amigos.
friend-status-offline = Desconectado
friend-list-entry = { $username } ({ $status })

view-profile = Ver perfil
join-table = Unirse a la mesa
remove-friend = Eliminar amigo
friend-remove-confirm = ¿Eliminar a { $username } de tu lista de amigos?
friend-remove-not-friends = { $username } ya no está en tu lista de amigos.
already-in-table = Ya estás en esta mesa.
friend-removed-success = { $username } fue eliminado de tu lista de amigos.
friend-removed-notify = { $username } te eliminó de { GENDER_TERM($username_gender, "possessive-determiner") } lista de amigos.

no-pending-requests = No hay solicitudes pendientes.
accept = Aceptar
decline = Rechazar
friend-accepted-success = Ahora eres amigo de { $username }.
friend-accepted-notify = ¡{ $username } aceptó tu solicitud de amistad!
request-not-found = La solicitud de amistad ya no existe.
friend-declined-success = Solicitud de amistad rechazada.
friend-declined-notify = { $username } rechazó tu solicitud de amistad.

enter-friend-username = Ingresa el nombre de usuario de la persona que quieres agregar como amigo:
enter-block-username = Ingresa el nombre de usuario de la persona que quieres bloquear:
friend-error-self = No puedes enviarte una solicitud de amistad a ti mismo.
friend-error-already-friends = Ya eres amigo de este usuario.
friend-error-duplicate = Ya tienes una solicitud de amistad pendiente con este usuario.
friend-error-blocked = Las solicitudes de amistad no están disponibles entre tú y { $username }.
friend-error-blocked-by-you = Bloqueaste a { $username }. Desbloquéa{ GENDER_TERM($username_gender, "object") } antes de enviarle una solicitud de amistad.
friend-request-sent = Solicitud de amistad enviada a { $username }.
friend-request-received = Recibiste una nueva solicitud de amistad de { $username }.

block-confirm = ¿Bloquear a { $username }? Esto elimina cualquier amistad y solicitud de amistad pendiente entre ustedes. Ninguno de los dos podrá enviarle al otro solicitudes de amistad, mensajes privados ni invitaciones a mesas, y los mensajes de chat normales quedarán ocultos en ambas direcciones. Hasta que se desbloquee, ninguno de los dos podrá entrar de nuevo a una mesa organizada por el otro ni restaurar una mesa guardada que incluya a ambos jugadores. Bloquear no saca a ningún jugador de una mesa compartida, no impide recuperar un asiento reservado, ni silencia el chat de voz de la mesa.
block-success = Bloqueaste a { $username }. El contacto social directo ya no está disponible entre ustedes, sus mensajes de chat normales quedan ocultos, y ninguno de los dos puede entrar de nuevo a una mesa organizada por el otro ni restaurar una mesa guardada que incluya a ambos usuarios.
block-error-self = No puedes bloquearte a ti mismo.
block-already-active = Ya bloqueaste a { $username }.
block-no-longer-active = Este bloqueo ya no está activo.
unblock-success = Desbloqueaste a { $username }. Las amistades y solicitudes anteriores no se restauraron.
unblock-user = Desbloquear usuario
block-user = Bloquear usuario
friends-blocked-users = { $count ->
    [0] Usuarios Bloqueados
   *[other] Usuarios Bloqueados ({ $count })
}
friends-blocked-empty = No has bloqueado a nadie.

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
pm-error-blocked = Los mensajes privados no están disponibles entre tú y este jugador.
pm-error-offline = { $username } no está en línea en este momento.
pm-error-self = No puedes enviarte un mensaje privado a ti mismo.
pm-error-message-required = Escribe un mensaje privado. Si usas el chat, incluye un nombre de usuario, por ejemplo: @Usuario hola.
pm-sent-content = Tú a { $username }: { $message }
pm-received = Mensaje privado de { $username }: { $message }

host-management = Gestión del anfitrión
table-spectator-suffix = (Espectador)
host-management-set-private = Establecer mesa como privada
host-management-set-public = Establecer mesa como pública
host-management-invite = Invitar a un amigo
host-management-voice = Gestionar el chat de voz
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
host-invite-friend-unavailable = Ese amigo ya no está disponible para ser invitado.
host-invite-already-pending = Ya hay una invitación pendiente para ese amigo.
host-invite-friend-busy = Ese amigo ya está en una partida.
host-invite-declined = { $player } rechazó tu invitación a la mesa.
table-invite-received = { $host } te invitó a { GENDER_TERM($host_gender, "possessive-determiner") } mesa de { $game }.
table-invite-queued = { $host } te invitó a { GENDER_TERM($host_gender, "possessive-determiner") } mesa de { $game }. Termina tu entrada actual para responder.
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
voice-member-status-connected = conectado al chat de voz
voice-member-status-not-connected = no conectado al chat de voz
voice-member-status-host-muted = micrófono desactivado por el anfitrión
voice-member-status-host-unmuted = puede usar el micrófono
voice-member-entry = { $player }: { $status }
voice-host-management-no-members = No hay más miembros de la mesa que puedas moderar.
voice-host-target-summary = Estado de voz de { $player }: { $voice_status }; { $moderation_status }.
voice-host-mute-action = Desactivar el micrófono de { $player }
voice-host-unmute-action = Permitir que { $player } use su micrófono
voice-host-cannot-mute-self = Como anfitrión, no puedes desactivar tu propio micrófono.
voice-host-moderation-rate-limited = La moderación del chat de voz está cambiando demasiado rápido. Inténtalo de nuevo dentro de { $seconds } segundos.
voice-host-muted-actor = Desactivaste el micrófono de { $player } en esta mesa. Puede seguir escuchando, pero no puede transmitir el audio de su micrófono.
voice-host-muted-target = { $host } desactivó tu micrófono en esta mesa. Puedes seguir escuchando, pero no puedes activar tu micrófono.
voice-host-muted-observer = { $host } desactivó el micrófono de { $player } en esta mesa.
voice-host-unmuted-actor = Permitiste que { $player } volviera a usar su micrófono. El micrófono permanece desactivado hasta que lo active explícitamente.
voice-host-unmuted-target = { $host } te permitió volver a usar tu micrófono. Tu micrófono permanece desactivado hasta que lo actives explícitamente.
voice-host-unmuted-observer = { $host } permitió que { $player } volviera a usar su micrófono.
voice-host-unmuted-self = Volviste a permitir el uso de tu propio micrófono. Permanece desactivado hasta que lo actives explícitamente.
voice-personal-settings-action = Configuración personal de voz
voice-personal-settings-summary = Configuración personal de voz para { $player }: volumen al { $volume } por ciento; { $mute_status }; { $connection_status }.
voice-personal-status-muted = silenciado solo para ti
voice-personal-status-unmuted = no silenciado para ti
voice-personal-mute-action = Silenciar a { $player } solo para mí
voice-personal-unmute-action = Dejar de silenciar a { $player } solo para mí
voice-personal-volume-action = Cambiar el volumen personal, actualmente al { $volume } por ciento
voice-personal-volume-choice = { $volume } por ciento
voice-personal-reset-action = Restablecer la configuración personal de voz
voice-personal-muted = Silenciaste a { $player } solo para ti. Solo tú dejarás de escuchar a { $player }.
voice-personal-unmuted = Dejaste de silenciar a { $player } solo para ti.
voice-personal-volume-set = Estableciste el volumen personal de voz de { $player } al { $volume } por ciento.
voice-personal-reset = Restableciste tu configuración personal de voz para { $player }.
voice-member-left = Ese miembro ya no está en esta mesa. La configuración de voz que se conserva en la mesa no se modificó.
voice-settings-limit-reached = Esta mesa alcanzó el límite de seguridad de la configuración de voz. No se modificó ningún ajuste.
voice-settings-invalid = Esa configuración de voz no es válida. No se modificó ningún ajuste.
voice-invalid-participant = Ese participante del chat de voz no es válido.
voice-moderation-provider-failed = No se pudo aplicar la moderación del chat de voz en este momento. No se modificó ningún ajuste; inténtalo de nuevo.

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

auth-username-reserved = Este nombre está reservado por PlayAural. Elige otro nombre de usuario.
action-role-change-rate-limited = Estás cambiando demasiado rápido entre jugador y espectador. Inténtalo de nuevo dentro de { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
}.
general-desc-global-chat-channel = Elige el canal de idioma que usarás para enviar y recibir mensajes del chat global. Se necesita un canal aunque el chat global esté activado.
global-chat-channel-option = Idioma del chat global: { $channel }
global-chat-channel-none = Ningún canal seleccionado
global-chat-channel-none-current = Ningún canal seleccionado (actual)
global-chat-channel-name = { $language }
global-chat-channel-recommended = { $language } (recomendado para el idioma de tu interfaz)
global-chat-channel-current = { $language } (actual)
global-chat-channel-current-recommended = { $language } (actual, recomendado para el idioma de tu interfaz)
global-chat-channel-selected = El idioma del chat global se estableció en { $language }. El chat global no se supervisa en tiempo real. Si alguien usa palabras malsonantes o te insulta, bloquéalo. Reporta los abusos graves o reiterados para que puedan revisarse después.
global-chat-channel-cleared = No hay ningún idioma seleccionado para el chat global. No enviarás ni recibirás mensajes globales.

admin-moderation = Moderación del chat
admin-moderation-global-chat-toggle = Chat global: { $status }
admin-moderation-global-chat-toggle-description = Activa o desactiva el envío de mensajes en todos los canales de idioma del chat global. Esta configuración se conserva después de reiniciar el servidor.
admin-moderation-global-chat-status-description = Estado actual para todo el servidor. Solo un desarrollador puede cambiar esta configuración.
admin-moderation-global-chat-update-failed = No se pudo guardar la configuración del chat global, así que no se hizo ningún cambio. Inténtalo de nuevo.
global-chat-availability-enabled = El desarrollador activó el chat global. Selecciona un canal de idioma antes de enviar o recibir mensajes globales.
global-chat-availability-disabled = El desarrollador desactivó temporalmente el chat global.
admin-moderation-section-reports = Reportes
admin-moderation-open-reports = Reportes abiertos: { $count }
admin-moderation-closed-reports = Reportes cerrados: { $count }
admin-moderation-all-reports = Todos los reportes conservados: { $count }
admin-moderation-section-messages = Historial de mensajes globales
admin-moderation-browse-messages = Explorar y filtrar todos los mensajes globales
admin-moderation-find-history = Buscar el historial del chat global por nombre de usuario exacto
admin-moderation-retained-summary = Pruebas conservadas: { $messages } mensajes globales y { $closed } reportes cerrados.
admin-moderation-section-retention = Eliminación permanente
admin-moderation-clear-history = Borrar todos los mensajes conservados del chat global ({ $count })
admin-moderation-clear-closed-reports = Borrar todos los reportes cerrados ({ $count })
admin-moderation-open-report-list = Reportes abiertos, los más recientes primero
admin-moderation-closed-report-list = Reportes cerrados, los más recientes primero
admin-moderation-all-report-list = Todos los reportes conservados, los más recientes primero
admin-moderation-report-row = Reporte n.º { $id }, enviado el { $time }. Usuario reportado: { $target }, ID { $target_id }. Motivo: { $reason }. Quien reportó: { $reporter }. Estado: { $status }.
admin-moderation-no-reports = Ningún reporte coincide con esta vista.
admin-moderation-value-unknown = desconocido
admin-moderation-status-open = abierto
admin-moderation-status-reviewed = revisado
admin-moderation-status-dismissed = descartado
admin-moderation-status-actioned = acción registrada
admin-moderation-status-unknown = desconocido
admin-moderation-report-unavailable = Este reporte ya no existe. Es posible que otro desarrollador lo haya eliminado.
admin-moderation-report-id = ID del reporte: { $id }
admin-moderation-report-time = Enviado el: { $time }
admin-moderation-report-status = Estado: { $status }
admin-moderation-report-origin = Origen: { $origin }
admin-moderation-origin-manual = enviado por un usuario
admin-moderation-origin-automatic = generado automáticamente por el Sistema
admin-moderation-report-reporter = Quien reportó: { $username }. ID de cuenta: { $uuid }
admin-moderation-report-target = Usuario reportado: { $username }. ID de cuenta: { $uuid }
admin-moderation-report-reason = Motivo: { $reason }
admin-moderation-report-channel = Canal de contexto del chat global: { $channel }
admin-moderation-report-scope = Detectado en: { $scope }
admin-moderation-scope-global = chat global
admin-moderation-scope-table = chat de mesa
admin-moderation-detection-rate-limited = mensajes enviados demasiado rápido
admin-moderation-detection-repeated-message = mensajes coincidentes repetidos
admin-moderation-automatic-evidence = Generado automáticamente por el Sistema solo para revisión manual; no se aplicó ninguna sanción. En { $scope }, el detector observó { $incidents } incidentes de spam separados y rechazó { $rejected } intentos durante un intervalo de observación de { $window }. Se aceptaron { $accepted } mensajes recientes. Detección: { $detection }. Último mensaje rechazado: { $sample }
admin-moderation-automatic-evidence-unavailable = Este reporte fue generado automáticamente por el Sistema solo para revisión manual y no se aplicó ninguna sanción. Sus pruebas de detección estructuradas no están disponibles o pertenecen a una versión no compatible.
admin-moderation-report-anchor = ID del mensaje de anclaje de contexto guardado: { $id }
admin-moderation-report-anchor-unavailable = No hay ningún mensaje de anclaje de contexto guardado. Puede que la cuenta reportada no haya enviado un mensaje conservado en este canal o que se haya borrado el historial del chat.
admin-moderation-report-details = Detalles adicionales: { $details }
admin-moderation-report-review = Revisado por { $reviewer }, ID de cuenta { $reviewer_id }, el { $time }.
admin-moderation-view-context = Ver la conversación alrededor de la hora del reporte
admin-moderation-view-target-history = Ver todos los mensajes globales conservados del ID de cuenta reportado
admin-moderation-mark-reviewed = Marcar como revisado sin sanción registrada
admin-moderation-dismiss-report = Descartar reporte
admin-moderation-mark-actioned = Marcar la acción como registrada. Esto no aplica ninguna sanción.
admin-moderation-context-heading = Contexto del reporte n.º { $id }, enviado el { $time }. Canal: { $channel }. Los mensajes están en orden cronológico; los mensajes del usuario reportado se identifican expresamente.
admin-moderation-context-message = { $username }: { $message } Mensaje n.º { $id }, enviado el { $time }. ID de cuenta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-target-message = Usuario reportado { $username }: { $message } Mensaje n.º { $id }, enviado el { $time }. ID de cuenta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-anchor-message = Mensaje anclado del usuario reportado { $username }: { $message } Mensaje n.º { $id }, enviado el { $time }. ID de cuenta: { $uuid }. Idioma: { $channel }.
admin-moderation-context-empty = No quedan mensajes globales conservados alrededor de la hora de este reporte.
admin-moderation-copy-page = { $count ->
    [one] Copiar el mensaje de esta página (1)
   *[other] Copiar los mensajes de esta página ({ $count })
}
admin-moderation-copy-page-success = { $count ->
    [one] Se copió 1 mensaje de esta página al portapapeles.
   *[other] Se copiaron { $count } mensajes de esta página al portapapeles.
}
admin-moderation-copy-page-failed = No se pudo copiar esta página al portapapeles. Comprueba el permiso del portapapeles e inténtalo de nuevo.
admin-moderation-history-prompt = Escribe el nombre de usuario exacto cuyo historial conservado del chat global quieres buscar. Los ID de cuentas históricas con el mismo nombre se mostrarán por separado.
admin-moderation-sender-results-heading = Identidades de remitentes conservadas que coinciden exactamente con el nombre de usuario «{ $username }».
admin-moderation-sender-result = { $username }, ID de cuenta { $uuid }. { $count } mensajes desde { $first } hasta { $last }.
admin-moderation-no-sender-history = Ningún historial conservado del chat global coincide exactamente con el nombre de usuario «{ $username }».
admin-moderation-history-heading = Historial conservado del chat global de { $username }, ID de cuenta { $uuid }: { $count } mensajes, los más recientes primero.
admin-moderation-history-message = { $username }: { $message } Mensaje n.º { $id }, enviado el { $time }. Idioma: { $channel }.
admin-moderation-history-empty = No quedan mensajes globales conservados para este ID de cuenta.
admin-moderation-message-list-heading = Historial de mensajes globales. Coinciden { $count } mensajes. Orden: { $sort }. Idioma: { $channel }. Período: { $period }. Todas las horas están en UTC.
admin-moderation-message-row = { $username }: { $message } Mensaje n.º { $id }, enviado el { $time }. ID de cuenta: { $uuid }. Idioma: { $channel }.
admin-moderation-message-list-empty = Ningún mensaje global conservado coincide con estos filtros.
admin-moderation-message-filter-sort = Orden: { $sort }
admin-moderation-message-filter-language = Idioma: { $channel }
admin-moderation-message-filter-period = Período: { $period }
admin-moderation-message-filter-reset = Restablecer todos los filtros de mensajes
admin-moderation-message-sort-newest = más recientes primero
admin-moderation-message-sort-oldest = más antiguos primero
admin-moderation-message-language-all = todos los idiomas
admin-moderation-message-period-all = todo el período
admin-moderation-message-period-today = hoy
admin-moderation-message-period-yesterday = ayer
admin-moderation-message-period-last-7-days = últimos 7 días
admin-moderation-message-period-last-30-days = últimos 30 días
admin-moderation-message-period-current-month = mes natural actual
admin-moderation-message-period-previous-month = mes natural anterior
admin-moderation-message-language-menu = Filtra los mensajes por idioma. El filtro actual es { $channel }.
admin-moderation-message-period-menu = Filtra los mensajes por período en UTC. El filtro actual es { $period }.
admin-moderation-message-filter-current = { $value } (actual)
admin-moderation-clear-history-confirm = ¿Eliminar permanentemente los { $count } mensajes conservados del chat global? Esta acción no se puede deshacer. Los { $open } reportes abiertos se conservarán, pero se eliminarán sus mensajes de anclaje y el contexto de la conversación.
admin-moderation-clear-closed-confirm = ¿Eliminar permanentemente los { $count } reportes cerrados? Los reportes abiertos y el historial del chat global se conservarán. Esta acción no se puede deshacer.
admin-moderation-report-already-closed = Otra acción de revisión ya había cerrado este reporte. Se volvió a cargar el registro actual.
admin-moderation-report-status-updated = El reporte n.º { $id } ahora está marcado como { $status }. No se aplicó ninguna sanción automática.
admin-new-manual-report = Nuevo reporte de moderación n.º { $id }: { $reporter } reportó a { $target }.
admin-new-automatic-report = El nuevo reporte de spam del Sistema n.º { $id } requiere revisión manual: { $target }.
admin-moderation-history-cleared = Se eliminaron permanentemente { $count } mensajes conservados del chat global. Los reportes existentes se conservan sin mensajes de anclaje. Si no queda ningún mensaje, la numeración se reiniciará en 1.
admin-moderation-closed-reports-cleared = Se eliminaron permanentemente { $count } reportes cerrados. Los reportes abiertos se conservan. Si no queda ningún reporte, la numeración se reiniciará en 1.

admin-database-management = Gestión de la base de datos
admin-database-management-summary = Mantenimiento de la base de datos exclusivo para desarrolladores. El análisis es de solo lectura. La copia de seguridad, la limpieza y la compactación pausan temporalmente el juego y los cambios de cuentas en todo el servidor.
admin-database-backup = Crear copia de seguridad de la base de datos
admin-database-backup-confirm = ¿Crear ahora una copia de seguridad de la base de datos? El juego y los cambios de cuentas se pausarán mientras SQLite crea y verifica una instantánea de recuperación. La copia se conservará en el directorio de copias de seguridad del servidor hasta que un operador la elimine.
admin-database-backup-success = Copia de seguridad de la base de datos completada: { $filename } ({ $size }).
admin-database-backup-failed = Falló la copia de seguridad de la base de datos. No se publicó ninguna copia parcial. Consulta el registro del servidor para obtener más información.
admin-database-size-bytes = { $value ->
    [one] 1 byte
   *[other] { NUMBER($value, maximumFractionDigits: 0) } bytes
}
admin-database-size-kib = { NUMBER($value, maximumFractionDigits: 1) } KiB
admin-database-size-mib = { NUMBER($value, maximumFractionDigits: 1) } MiB
admin-database-size-gib = { NUMBER($value, maximumFractionDigits: 1) } GiB
admin-database-storage-analyze = Analizar candidatos para la limpieza
admin-database-storage-analysis-summary = Tamaño de la base de datos: { $size }. Espacio reutilizable de SQLite: { $reusable }. Registros aptos para eliminar: { $records }.
admin-database-storage-analysis-failed = El análisis del almacenamiento falló sin cambiar ningún dato. Consulta el registro del servidor para obtener más información.
admin-database-storage-refresh-analysis = Actualizar el análisis del almacenamiento
admin-database-storage-cleanup = Ejecutar la limpieza del almacenamiento
admin-database-storage-cleanup-confirm = ¿Ejecutar ahora la limpieza segura del almacenamiento? El juego y los cambios de cuentas se pausarán mientras el servidor crea y verifica una copia de seguridad de precaución, elimina únicamente los registros transitorios o huérfanos indicados y valida el resultado. El archivo de la base de datos no se compactará.
admin-database-storage-cleanup-not-needed = No es necesario limpiar el almacenamiento. No se encontraron registros aptos ni archivos temporales de copias de seguridad abandonados.
admin-database-storage-cleanup-success = Limpieza del almacenamiento completada. Registros eliminados: { $records }. Archivos temporales de copias de seguridad abandonados eliminados: { $files } ({ $file_size }). Espacio reutilizable de SQLite: { $reusable }. Ejecuta la compactación por separado para reducir el tamaño del archivo. Copia de seguridad de precaución: { $filename }.
admin-database-storage-cleanup-failed = Falló la limpieza del almacenamiento. Se conservó cualquier copia de seguridad de precaución completada. Consulta el registro del servidor antes de volver a intentarlo.
admin-database-storage-no-record-candidates = En este momento no hay registros de la base de datos aptos para una limpieza segura.
admin-database-storage-temporary-files = Archivos temporales abandonados de copias de seguridad de PlayAural: { $count } ({ $size }).
admin-database-storage-invalid-timestamps = Advertencia de seguridad: { $count } registros contienen marcas de tiempo de conservación no válidas. La limpieza nunca los considerará caducados suponiendo su antigüedad; revísalos manualmente.
admin-database-storage-exclusions = Siempre se excluyen de la limpieza automática: mesas guardadas, resultados de partidas, historial del chat global, reportes de moderación, cuentas de usuario, bloqueos válidos, datos activos, estadísticas de juegos registrados, datos de compatibilidad, copias de seguridad válidas y registros. Las mesas guardadas solo se eliminan mediante una acción expresa de su propietario o de un desarrollador.
admin-database-storage-category-row = { $category }: { $count }
admin-database-storage-category-expired-table-checkpoints = Puntos de control transitorios de mesas caducados
admin-database-storage-category-expired-password-reset-tokens = Códigos de restablecimiento de contraseña caducados
admin-database-storage-category-expired-bans = Registros de baneo conservados durante más de { $days } días después de caducar
admin-database-storage-category-stale-pending-friend-requests = Solicitudes de amistad pendientes con más de { $days } días
admin-database-storage-category-orphaned-friendships = Registros de amistad huérfanos
admin-database-storage-category-orphaned-user-blocks = Registros de bloqueo de usuarios huérfanos
admin-database-storage-category-stale-user-notifications = Notificaciones de usuario con más de { $days } días
admin-database-storage-category-orphaned-user-notifications = Registros de notificaciones de usuario huérfanos
admin-database-storage-category-expired-mutes = Registros de silenciamiento caducados
admin-database-storage-category-orphaned-mutes = Registros de silenciamiento huérfanos
admin-database-compact = Compactar la base de datos y recuperar el espacio sin usar
admin-database-compact-confirm = ¿Compactar ahora la base de datos? El juego y los cambios de cuentas se pausarán. Se creará una copia de seguridad de precaución verificada antes de que SQLite reconstruya la base de datos activa. Esta operación requiere bastante espacio temporal en el disco y debería ejecutarse en un período de poca actividad.
admin-database-compact-success = Compactación de la base de datos completada. El tamaño del archivo cambió de { $before } a { $after }; se recuperaron { $reclaimed }. Copia de seguridad de precaución: { $filename }.
admin-database-compact-failed = Falló la compactación de la base de datos. La base de datos activa no se modificó intencionadamente y se conservó cualquier copia de seguridad de precaución completada. Consulta el registro del servidor para obtener más información.
admin-database-maintenance-busy = Ya hay otra operación exclusiva del servidor en curso. Espera a que termine antes de iniciar el mantenimiento de la base de datos.
database-maintenance-operation-backup = copia de seguridad de la base de datos
database-maintenance-operation-cleanup = limpieza del almacenamiento
database-maintenance-operation-compaction = compactación de la base de datos
database-maintenance-not-active = El mantenimiento de la base de datos no está activo en este momento.
database-maintenance-input-blocked = La { $operation } del servidor está en curso. El juego, el inicio de sesión, el registro y los cambios de cuentas están pausados temporalmente. Tu menú actual sigue disponible, pero las acciones no se ejecutarán hasta que termine el mantenimiento.
database-maintenance-auth-blocked = El mantenimiento de la base de datos del servidor está en curso. El inicio de sesión, el registro y los cambios de contraseña no están disponibles temporalmente. Inténtalo de nuevo cuando termine el mantenimiento.
database-maintenance-backup-started = El desarrollador está creando una copia de seguridad de la base de datos del servidor. El juego y los cambios de cuentas están pausados temporalmente; los menús actuales siguen visibles. Se te avisará cuando se reanude el servicio normal.
database-maintenance-backup-completed = La copia de seguridad de la base de datos del servidor terminó. El juego y el acceso a las cuentas se están reanudando.
database-maintenance-backup-failed = No se pudo completar la copia de seguridad de la base de datos del servidor. No se publicó ninguna copia parcial. El juego y el acceso a las cuentas se están reanudando.
database-maintenance-cleanup-started = El desarrollador está limpiando el almacenamiento del servidor. El juego y los cambios de cuentas están pausados temporalmente, pero los menús actuales siguen visibles. Primero se está creando una copia de seguridad de precaución verificada. Se te avisará cuando se reanude el servicio normal.
database-maintenance-cleanup-completed = La limpieza del almacenamiento y la validación de la base de datos del servidor terminaron. El juego y el acceso a las cuentas se están reanudando.
database-maintenance-cleanup-failed = La limpieza del almacenamiento del servidor no pudo completarse de forma segura. El juego y el acceso a las cuentas se están reanudando.
database-maintenance-compaction-started = El desarrollador está compactando la base de datos del servidor. El juego y los cambios de cuentas están pausados temporalmente; los menús actuales siguen visibles. Se te avisará cuando se reanude el servicio normal.
database-maintenance-compaction-completed = La compactación de la base de datos del servidor terminó. El juego y el acceso a las cuentas se están reanudando.
database-maintenance-compaction-failed = No se pudo completar la compactación de la base de datos del servidor. El juego y el acceso a las cuentas se están reanudando sin aplicar la compactación.
database-maintenance-reopen-failed = Error crítico de mantenimiento: la base de datos activa no pudo volver a abrirse de forma segura, por lo que el servidor sigue inmovilizado. Espera a que el desarrollador restablezca el servicio.

chat-repeated-message = Por favor, no repitas el mismo mensaje.
chat-global-channel-required-send = Selecciona un idioma para el chat global antes de enviar mensajes. El chat global no se supervisa en tiempo real. Si alguien usa palabras malsonantes o te insulta, bloquéalo. Reporta los abusos graves o reiterados para que puedan revisarse después.
chat-global-log-unavailable = El chat global no está disponible temporalmente porque este mensaje no se pudo guardar de forma segura. Inténtalo de nuevo más tarde.
chat-global-temporarily-disabled-send = El desarrollador desactivó temporalmente el chat global.

report-user = Reportar a un usuario
enter-report-username = Escribe el nombre de usuario que quieres reportar.
report-error-self = No puedes reportar tu propia cuenta.
report-select-reason = Reportar a { $username }: selecciona el motivo que mejor describa su conducta.
report-reason-spam = Spam o interrupciones reiteradas
report-reason-harassment = Acoso o insultos personales
report-reason-hateful-content = Contenido de odio
report-reason-sexual-content = Contenido sexual
report-reason-threats = Amenazas de daño
report-reason-personal-information = Divulgación de información personal
report-reason-other = Otra mala conducta grave
report-channel-unspecified = ningún canal de chat global seleccionado
report-confirm-summary = Reportar a { $username } por { $reason }. Canal de contexto: { $channel }. El reporte se guardará para revisión manual. El usuario no recibirá una notificación ni una sanción automática.
report-submit = Enviar reporte
report-change-reason = Cambiar el motivo
report-submitted = Tu reporte sobre { $username } se guardó con la hora exacta de envío para su revisión manual. El usuario no recibió ninguna notificación. También puedes bloquear{ GENDER_TERM($username_gender, "object") } para impedir el contacto directo y ocultar sus mensajes globales.
report-target-cooldown = Reportaste a { $username } recientemente. Espera { $duration } antes de enviar otro reporte; usa Bloquear ahora si no quieres recibir { GENDER_TERM($username_gender, "possessive-determiner") } mensajes.
report-rate-limited = Has enviado varios reportes recientemente. Inténtalo de nuevo dentro de { $duration }.
report-failed = No se pudo guardar el reporte de forma segura. Inténtalo de nuevo más tarde.

server-power-maintenance-active = No se puede programar una operación de energía del servidor mientras el mantenimiento de la base de datos esté activo. Espera a que termine e inténtalo de nuevo.

# Formas gramaticales compartidas para el género de la cuenta. Los juegos
# pueden sustituir una forma mediante <context>-gender-term-<form> al llamar a
# GENDER_TERM; los nombres técnicos context y form no deben traducirse.
# Sujeto opcional. Incluye el espacio final: "él ", "ella " o nada. Escribe el
# mensaje pegado al verbo ("así que { GENDER_TERM(...) }intercambia"). Sin género
# definido (también los bots) el sujeto se omite, como es natural en español.
gender-term-subject =
    { $gender ->
        [male] { "él " }
        [female] { "ella " }
       *[other] { "" }
    }
gender-term-subject-capitalized =
    { $gender ->
        [male] Él
        [female] Ella
       *[other] Esa persona
    }
gender-term-subject-be =
    { $gender ->
        [male] él está
        [female] ella está
       *[other] está
    }
gender-term-subject-be-capitalized =
    { $gender ->
        [male] Él está
        [female] Ella está
       *[other] Está
    }
gender-term-subject-have =
    { $gender ->
        [male] él tiene
        [female] ella tiene
       *[other] tiene
    }
gender-term-subject-have-capitalized =
    { $gender ->
        [male] Él tiene
        [female] Ella tiene
       *[other] Tiene
    }
# Pronombre átono de objeto: "lo", "la" o "le" (sin género definido, también los
# bots). Va delante del verbo ("{ GENDER_TERM(...) } deja") o pegado al gerundio,
# infinitivo o imperativo ("dejándo{ GENDER_TERM(...) }"). No se escribe tras "a".
gender-term-object =
    { $gender ->
        [male] lo
        [female] la
       *[other] le
    }
gender-term-possessive-determiner =
    { $gender ->
        [male] su
        [female] su
       *[other] su
    }
gender-term-possessive-determiner-capitalized =
    { $gender ->
        [male] Su
        [female] Su
       *[other] Su
    }
gender-term-possessive-pronoun =
    { $gender ->
        [male] el suyo
        [female] el suyo
       *[other] el suyo
    }
gender-term-reflexive =
    { $gender ->
        [male] a sí mismo
        [female] a sí misma
       *[other] a sí
    }

friends-sent-requests = { $count ->
    [0] Solicitudes enviadas
   *[other] Solicitudes enviadas ({ $count })
}
friend-status-offline-last-online = Desconectado, última conexión { $relative_time }
no-sent-requests = No tienes solicitudes de amistad enviadas pendientes.
friend-request-to = Solicitud de amistad enviada a { $username }
friend-request-manage-sent = Gestionar solicitud de amistad enviada
friend-request-accept-action = Aceptar solicitud de amistad
friend-request-cancel-action = Cancelar solicitud de amistad
friend-request-cancel-confirm = ¿Cancelar tu solicitud de amistad pendiente para { $username }?
friend-request-cancelled = Se canceló tu solicitud de amistad para { $username }.
friend-request-cancel-unavailable = Esta solicitud de amistad ya no está pendiente, por lo que no se canceló.
relative-time-just-now = ahora mismo
relative-time-minutes-ago = { $count ->
    [one] hace 1 minuto
   *[other] hace { $count } minutos
}
relative-time-hours-ago = { $count ->
    [one] hace 1 hora
   *[other] hace { $count } horas
}
relative-time-days-ago = { $count ->
    [one] hace 1 día
   *[other] hace { $count } días
}
relative-time-weeks-ago = { $count ->
    [one] hace 1 semana
   *[other] hace { $count } semanas
}
relative-time-months-ago = { $count ->
    [one] hace 1 mes
   *[other] hace { $count } meses
}
relative-time-years-ago = { $count ->
    [one] hace 1 año
   *[other] hace { $count } años
}

host-management-switch-game = Cambiar a otro juego
host-management-player-substitution = Sustitución de jugadores
host-game-switch-current = Juego actual: { $game }. Esta mesa tiene { $seats } { $seats ->
    [one] asiento activo
   *[other] asientos activos
}. Solo se muestran los juegos que admiten todos los asientos activos.
host-game-switch-no-compatible-games = Ningún otro juego admite actualmente los { $seats } { $seats ->
    [one] asiento activo
   *[other] asientos activos
}.
host-game-switch-confirm = ¿Cambiar el juego de esta mesa de { $old_game } a { $new_game }? Todas las personas presentes pasarán a la nueva sala de espera con la misma función de jugador o espectador, y los bots permanecerán. Se descartarán la partida o configuración actual, las opciones, los equipos y el estado de preparación. Se conservarán el anfitrión, la privacidad, los baneos y el chat de voz. Se cancelarán las invitaciones pendientes del juego anterior.
host-game-switch-target-unavailable = Ese juego ya no está disponible como destino del cambio. No se modificó ningún estado de la mesa.
host-game-switch-roster-invalid = Los miembros presentes en la mesa ya no coinciden con los asientos del juego. El cambio se bloqueó para evitar que alguien quedara fuera. Vuelve a la mesa e inténtalo de nuevo después de que se actualice la lista.
host-game-switch-too-many-seats = No se puede cambiar a { $game }: admite como máximo { $max } { $max ->
    [one] asiento activo
   *[other] asientos activos
}, pero esta mesa necesita { $seats }.
host-game-switch-failed = No se pudo cambiar de juego de forma segura. La mesa y el juego actuales permanecieron sin cambios.
host-game-switch-you = Cambiaste el juego de esta mesa de { $old_game } a { $new_game }. Todos están ahora en la nueva sala de espera; el chat de voz de la mesa sigue conectado.
host-game-switch-player = { $player } cambió el juego de esta mesa de { $old_game } a { $new_game }. Todos están ahora en la nueva sala de espera; el chat de voz de la mesa sigue conectado.

player-substitution-offer-action = Colocar a un espectador en este asiento
player-substitution-seat-bot = Asiento del bot: { $bot }
player-substitution-seat-replacement = { $bot }, jugando en el asiento reservado de { $player }
player-substitution-seat-self = Tu asiento: { $player }
player-substitution-seat-player = Asiento del jugador: { $player }
player-substitution-no-seats = (No hay asientos de jugadores activos disponibles)
player-substitution-seat-unavailable = Ese asiento ya no está disponible para una sustitución. No se cambió ninguna función.
player-substitution-no-spectators = (No hay espectadores aptos disponibles)
player-substitution-spectator-unavailable = Ese espectador ya no está disponible para una sustitución. No se cambió ninguna función.
player-substitution-user-busy = { $player } está completando otra entrada o vista de estado. Inténtalo de nuevo cuando ya no tenga esa vista abierta.
player-substitution-game-busy = El juego está completando una elección sincronizada o una recuperación de la mesa que bloquea temporalmente las sustituciones. Inténtalo de nuevo cuando termine.
player-substitution-offer-sent = Se ofreció el asiento de { $seat } a { $player }. Debe aceptar antes de que cambie el control.
player-substitution-self-offer-sent = Se ofreció tu asiento a { $player }. Si { GENDER_TERM($player_gender, "subject") }acepta la oferta, pasarás a ser espectador y seguirás como anfitrión; el resultado final del asiento se registrará a nombre de { $player }.
player-substitution-self-incoming-consent-sent = Pediste a { $player } que te cediera { GENDER_TERM($player_gender, "possessive-determiner") } asiento. Si { GENDER_TERM($player_gender, "subject") }acepta la solicitud, tomarás el control de inmediato porque al elegirte ya confirmaste tu consentimiento.
player-substitution-outgoing-consent-sent = Pediste a { $player } que cediera { GENDER_TERM($player_gender, "possessive-determiner") } asiento a { $substitute }. Si { $player } acepta la solicitud, { $substitute } también deberá aceptar antes de que cambie el control.
player-substitution-offer-pending = { $player } ya tiene una solicitud de sustitución pendiente de respuesta.
player-substitution-seat-offer-pending = El asiento de { $seat } ya tiene una solicitud de sustitución pendiente de respuesta.
player-substitution-self-seat-offer-pending = Tu asiento ya tiene una solicitud de sustitución pendiente de respuesta.
player-substitution-request-outgoing = { $host } quiere que { $player } te sustituya en tu asiento actual. Si aceptas, pasarás a ser espectador y { $player } recibirá exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento. No se reiniciará ningún temporizador.
player-substitution-request-outgoing-host-incoming = { $host } quiere sustituirte en tu asiento actual. Si aceptas, pasarás a ser espectador y { $host } recibirá exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento. No se reiniciará ningún temporizador.
player-substitution-request-player = { $host } te ofrece el asiento de { $player } con { GENDER_TERM($player_gender, "possessive-determiner") } consentimiento. Si aceptas, heredarás exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento; no se reiniciará ningún temporizador y { $player } pasará a ser espectador.
player-substitution-request-host-seat = { $host } te ofrece su propio asiento. Si aceptas, heredarás exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento; no se reiniciará ningún temporizador y { $host } pasará a ser espectador, pero seguirá siendo el anfitrión.
player-substitution-request-bot = { $host } te ofrece el asiento controlado por { $bot }. Si aceptas, heredarás exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento; no se reiniciará ningún temporizador.
player-substitution-request-replacement = { $host } te ofrece el asiento reservado de { $player }, controlado actualmente por { $bot }. Si aceptas, heredarás exactamente el estado de la partida, la información privada, el tiempo de turno restante y la atribución del resultado final del asiento; no se reiniciará ningún temporizador y { $player } ya no podrá recuperar ese asiento.
player-substitution-decline = Rechazar sustitución
player-substitution-accept = Aceptar sustitución
player-substitution-offer-expired = La solicitud de sustitución caducó. No se cambió ninguna función.
player-substitution-offer-expired-host = { $player } no respondió antes de que caducara la solicitud de sustitución. No se cambió ninguna función.
player-substitution-offer-declined = { $player } rechazó la solicitud de sustitución. No se cambió ninguna función.
player-substitution-no-longer-available = Esa solicitud de sustitución ya no está disponible. No se cambió ninguna función.
player-substitution-awaiting-incoming = { $player } ya puede aceptar o rechazar la sustitución. Todavía no se cambió ninguna función.
player-substitution-complete-player-you = Tomaste el control del antiguo asiento de { $player }. { GENDER_TERM($player_gender, "subject-be-capitalized") } ahora como espectador.
player-substitution-complete-outgoing-you = { $player } tomó el control de tu antiguo asiento. Ahora eres espectador.
player-substitution-complete-player = { $player } tomó el control del antiguo asiento de { $outgoing }. { $outgoing } está ahora como espectador.
player-substitution-complete-host-player-you = Tomaste el control del antiguo asiento de { $player }. { GENDER_TERM($player_gender, "subject-be-capitalized") } ahora como espectador y conserva la función de anfitrión.
player-substitution-complete-outgoing-host-you = { $player } tomó el control de tu antiguo asiento. Ahora eres espectador y sigues siendo el anfitrión.
player-substitution-complete-host = { $player } tomó el control del antiguo asiento de { $outgoing }. { $outgoing } está ahora como espectador y sigue siendo el anfitrión.
player-substitution-complete-bot-you = Tomaste el control del asiento de { $bot }.
player-substitution-complete-bot = { $player } tomó el control del asiento de { $bot }.
player-substitution-complete-replacement-you = Tomaste el control del asiento reservado de { $replaced_player }, que estaba en manos de { $bot }. La reserva anterior terminó.
player-substitution-complete-replacement = { $player } tomó el control del asiento reservado de { $replaced_player }, que estaba en manos de { $bot }. La reserva anterior terminó.

host-invite-pair-cooldown = Espera { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
} antes de volver a invitar a ese amigo.
host-invite-rate-limited = Estás enviando invitaciones de mesa demasiado rápido. Inténtalo de nuevo dentro de { $seconds ->
    [one] 1 segundo
   *[other] { $seconds } segundos
}.
table-invite-no-longer-available = Esa invitación de mesa ya no está disponible.
