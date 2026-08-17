# Lounge chat room messages

game-name-lounge = Sala de Charla

# Room lifecycle
lounge-welcome = Bienvenido a la Sala de Charla. Esta mesa es solo para hablar: usa el chat de mesa, lanza gestos y abre las herramientas de sala desde tu menú.
lounge-welcome-spectator = Bienvenido a la Sala de Charla. Estás como espectador, así que puedes leer la sala y seguir el chat, pero los gestos y las herramientas de sala son para quienes están sentados.
lounge-cannot-start = La Sala de Charla siempre está abierta, así que no hay ninguna partida que iniciar. El chat, los gestos y las herramientas de sala están disponibles para todos desde el momento en que se sientan.
lounge-no-bots = La Sala de Charla es una sala para personas, así que aquí no se pueden añadir bots. Invita a alguien desde la lista de jugadores.
lounge-no-save = Una Sala de Charla es una sala viva, así que no hay nada que guardar. La sala se cierra sola cuando se va la última persona.

# Emote labels
lounge-emote-wave = Saludar
lounge-emote-laugh = Reír
lounge-emote-applaud = Aplaudir
lounge-emote-boo = Abuchear
lounge-emote-toast = Brindar
lounge-emote-facepalm = Llevarse la mano a la cara
lounge-emote-think = Pensárselo
lounge-emote-celebrate = Celebrar
lounge-emote-description = Lanza este gesto, con su sonido, para toda la sala.

# Emote announcements
lounge-emote-wave-you = Saludas a la sala.
lounge-emote-wave-other = { $player } saluda a la sala.
lounge-emote-laugh-you = Te echas a reír.
lounge-emote-laugh-other = { $player } se echa a reír.
lounge-emote-applaud-you = Aplaudes.
lounge-emote-applaud-other = { $player } aplaude.
lounge-emote-boo-you = Abucheas.
lounge-emote-boo-other = { $player } abuchea.
lounge-emote-toast-you = Brindas por la sala.
lounge-emote-toast-other = { $player } brinda por la sala.
lounge-emote-facepalm-you = Te llevas la mano a la cara.
lounge-emote-facepalm-other = { $player } se lleva la mano a la cara.
lounge-emote-think-you = Te lo piensas en silencio.
lounge-emote-think-other = { $player } se lo piensa en silencio.
lounge-emote-celebrate-you = Celebras.
lounge-emote-celebrate-other = { $player } celebra.

# Nudge
lounge-nudge = Dar un toque a alguien
lounge-nudge-description = Envía un sonido privado y un mensaje corto a una persona de la sala.
lounge-nudge-prompt = Elige a quién dar un toque
lounge-nudge-you = Das un toque a { $target }.
lounge-nudge-target = { $player } te da un toque.
lounge-nudge-other = { $player } da un toque a { $target }.
lounge-nudge-no-targets = Todavía no hay nadie más en la sala a quien dar un toque. Espera a que alguien se siente.
lounge-nudge-target-left = { $target } ya no está en la sala, así que el toque no se envió.
lounge-nudge-self = No puedes darte un toque a ti mismo. Elige a otra persona de la sala.

# Party tools
lounge-roll-dice = Tirar dos dados
lounge-roll-dice-description = Tira dos dados de seis caras en voz alta para toda la sala.
lounge-roll-you = Sacas { $first } y { $second }, con un total de { $total }.
lounge-roll-other = { $player } saca { $first } y { $second }, con un total de { $total }.
lounge-flip-coin = Lanzar una moneda
lounge-flip-coin-description = Lanza una moneda en voz alta para toda la sala.
lounge-flip-you = Lanzas una moneda y cae en { $side }.
lounge-flip-other = { $player } lanza una moneda y cae en { $side }.
lounge-coin-heads = cara
lounge-coin-tails = cruz

# Away
lounge-mark-away = Marcarte como ausente
lounge-mark-back = Volver de la ausencia
lounge-away-description = Avisa a la sala de que te has apartado un momento. Conservas tu sitio y puedes volver cuando quieras.
lounge-away-you = Ahora estás marcado como ausente. Conservas tu sitio y todos ven que te has apartado.
lounge-away-other = { $player } está ausente.
lounge-back-you = Has vuelto de la ausencia.
lounge-back-other = { $player } ha vuelto.

# Topic
lounge-set-topic = Poner el tema de la sala
lounge-set-topic-description = Solo el anfitrión puede cambiar de qué trata la sala. Todos escuchan el tema nuevo.
lounge-set-topic-prompt = Escribe el tema nuevo de la sala, o envíalo vacío para borrar el actual
lounge-read-topic = Leer el tema de la sala
lounge-read-topic-description = Escucha de qué trata la sala ahora mismo.
lounge-topic-set-you = Pones el tema de la sala en: { $topic }
lounge-topic-set-other = { $player } pone el tema de la sala en: { $topic }
lounge-topic-cleared-you = Has borrado el tema de la sala.
lounge-topic-cleared-other = { $player } ha borrado el tema de la sala.
lounge-topic-unchanged = El tema de la sala ya dice exactamente eso, así que no ha cambiado nada.
lounge-topic-already-empty = La sala no tiene ningún tema que borrar.
lounge-topic-current = Tema de la sala, puesto por { $player }: { $topic }
lounge-topic-none = Esta sala todavía no tiene tema. El anfitrión puede poner uno desde las herramientas de sala.
lounge-topic-not-host = Solo el anfitrión puede poner el tema de la sala. Pídele a { $host } que lo cambie.
lounge-topic-too-long = Ese tema es demasiado largo. No pases de { $max } caracteres; el tuyo tenía { $count }.
lounge-topic-unreadable = Ese tema no tenía ningún texto legible, así que el tema de la sala se quedó como estaba.

# Room information
lounge-room-info = Información de la sala
lounge-room-info-description = Lee el tema, quién está aquí, quién está ausente y los ajustes actuales de la sala.
lounge-info-host = Anfitrión: { $host }.
lounge-info-topic = Tema: { $topic }
lounge-info-topic-none = Tema: todavía sin poner.
lounge-info-topic-author = Tema puesto por { $player }.
lounge-info-people = Sentados: { $count } { $count ->
        [one] persona
       *[other] personas
    }.
lounge-info-spectators = Como espectadores: { $count }.
lounge-info-away = Ausentes ahora mismo: { $count }.
lounge-info-emotes = Gestos lanzados en esta sala: { $count }.
lounge-info-person = { $player }
lounge-info-person-host = { $player } (anfitrión)
lounge-info-person-away = { $player } (ausente)
lounge-info-person-host-away = { $player } (anfitrión, ausente)
lounge-info-person-spectator = { $player } (mirando)
lounge-info-settings = Ajustes de la sala: gestos { $emotes }, toques { $nudges }, dados y moneda { $party }, espera entre acciones de sala { $cooldown } { $cooldown ->
        [one] segundo
       *[other] segundos
    }.

# Blocked actions
lounge-emotes-disabled = Los gestos están desactivados en esta sala. El anfitrión puede volver a activarlos en los ajustes de la sala.
lounge-nudges-disabled = Los toques están desactivados en esta sala. El anfitrión puede volver a activarlos en los ajustes de la sala.
lounge-party-tools-disabled = Los dados y la moneda están desactivados en esta sala. El anfitrión puede volver a activarlos en los ajustes de la sala.
lounge-cooldown-wait = Espera { $seconds } { $seconds ->
        [one] segundo
       *[other] segundos
    } más antes de tu próximo gesto, toque, tirada de dados o lanzamiento de moneda.
lounge-spectator-blocked = Eso solo pueden hacerlo quienes están sentados en la sala. Siéntate si quieres participar.

# Options
lounge-set-allow-emotes = Gestos: { $enabled }
lounge-option-changed-allow-emotes = Gestos establecido en { $enabled }.
lounge-desc-allow-emotes = Cuando está activado, todos los sentados pueden lanzar gestos con su sonido para toda la sala (activado por defecto).
lounge-set-allow-nudges = Toques: { $enabled }
lounge-option-changed-allow-nudges = Toques establecido en { $enabled }.
lounge-desc-allow-nudges = Cuando está activado, todos los sentados pueden enviar a una persona un toque privado con sonido (activado por defecto).
lounge-set-allow-party-tools = Dados y moneda: { $enabled }
lounge-option-changed-allow-party-tools = Dados y moneda establecido en { $enabled }.
lounge-desc-allow-party-tools = Cuando está activado, todos los sentados pueden tirar dos dados o lanzar una moneda para la sala (activado por defecto).
lounge-set-action-cooldown = Espera entre acciones de sala: { $seconds } { $seconds ->
        [one] segundo
       *[other] segundos
    }
lounge-prompt-action-cooldown = Indica cuántos segundos debe esperar cada persona entre gestos, toques, tiradas de dados y lanzamientos de moneda
lounge-option-changed-action-cooldown = Espera entre acciones de sala establecida en { $seconds } { $seconds ->
        [one] segundo
       *[other] segundos
    }.
lounge-desc-action-cooldown = Cuánto espera cada persona entre gestos, toques, tiradas de dados y lanzamientos de moneda, para que la sala siga siendo cómoda de escuchar (3 segundos por defecto, rango 0-60).
