game-name-battleship = Hundir la Flota

# Options
battleship-set-grid-size = Zona de combate: { $size }
battleship-select-grid-size = Selecciona el tamaño de la zona de combate
battleship-select-orientation = Selecciona la orientación de despliegue
battleship-option-changed-grid-size = Zona de combate establecida en { $size }.
battleship-desc-grid-size = Elige el tamaño de la cuadrícula del océano en Hundir la Flota; las cuadrículas más grandes hacen búsquedas más largas.

battleship-set-placement-mode = Despliegue: { $mode }
battleship-select-placement-mode = Selecciona el modo de despliegue
battleship-option-changed-placement-mode = Modo de despliegue establecido en { $mode }.
battleship-desc-placement-mode = Elige si los barcos se colocan automática o manualmente antes de que comience la batalla.

battleship-set-replay-on-hit = Disparo extra al acertar: { $enabled }
battleship-option-changed-replay-on-hit = Disparo extra al acertar establecido en { $enabled }.
battleship-desc-replay-on-hit = Cuando está activado, un jugador que acierta un disparo dispara de inmediato otra vez.

battleship-set-turn-timer = Temporizador de turno: { $seconds }
battleship-select-turn-timer = Selecciona el temporizador de turno
battleship-option-changed-turn-timer = Temporizador de turno establecido en { $seconds }.
battleship-desc-turn-timer = Límite de tiempo opcional para cada turno de Hundir la Flota; si se acaba el tiempo, la partida dispara a una coordenada al azar. Elige Ilimitado para desactivar el temporizador.

# Option choice labels
battleship-grid-6x6 = 6 por 6
battleship-grid-8x8 = 8 por 8
battleship-grid-10x10 = 10 por 10
battleship-grid-12x12 = 12 por 12

battleship-placement-auto = Automático
battleship-placement-manual = Manual

battleship-timer-off = Desactivado
battleship-timer-30 = 30 segundos
battleship-timer-45 = 45 segundos
battleship-timer-60 = 60 segundos

# Setup validation
battleship-error-invalid-grid-size = El tamaño de zona de combate { $size } no es compatible.
battleship-error-grid-too-small = La zona de combate de { $size } por { $size } es demasiado pequeña para la flota completa. Usa al menos { $minimum } por { $minimum }.
battleship-error-invalid-placement-mode = El modo de despliegue { $mode } no es compatible.
battleship-error-invalid-turn-timer = El temporizador de turno { $seconds } no es compatible.

# Ship names
battleship-ship-carrier = Portaaviones
battleship-ship-battleship = Acorazado
battleship-ship-destroyer = Destructor
battleship-ship-submarine = Submarino
battleship-ship-patrol = Lancha Patrullera
battleship-ship-unknown = Nave

# Orientations
battleship-horizontal = Horizontal
battleship-vertical = Vertical

# Actions
battleship-orient-horizontal = Desplegar en horizontal
battleship-orient-vertical = Desplegar en vertical
battleship-orient-horizontal-at = Desplegar { $ship } en horizontal en { $coord }
battleship-orient-vertical-at = Desplegar { $ship } en vertical en { $coord }
battleship-toggle-view = Cambiar cuadrícula
battleship-read-fleet = Estado de la flota
battleship-read-enemy-fleet = Información de la flota enemiga

# Deployment phase
battleship-deploy-start = Fase de despliegue. Coloca tu { $ship }, de { $size } sectores de largo. Selecciona una coordenada y luego elige la orientación.
battleship-choose-orientation = Desplegando { $ship } en { $coord }, { $size } sectores. Elige la orientación.
battleship-ship-placed = { $ship } desplegado en { $coord }, orientación { $orientation }.
battleship-cannot-place = No se puede desplegar { $ship } en { $coord } { $orientation }. La nave no cabe o se superpone con otro barco.
battleship-place-next-ship = Siguiente nave: { $ship }, { $size } sectores.
battleship-deploy-done = Flota desplegada. En espera del enemigo.
battleship-deploy-complete = Despliegue completo.
battleship-select-cell-first = Primero selecciona una coordenada en la cuadrícula.
battleship-deploy-in-progress = El despliegue todavía está en curso.
battleship-deploy-status-header = Fase de colocación de barcos.
battleship-deploy-status-ready-self = Estás listo.
battleship-deploy-status-ready-other = { $player } está listo.
battleship-deploy-status-not-ready-self = Aún no estás listo.
battleship-deploy-status-not-ready-other = { $player } aún no está listo.

# Battle phase
battleship-battle-start = Todos los barcos en posición. ¡Comienza el fuego!

# Hit — first-person (shooter), second-person (target), third-person (spectator)
battleship-hit-self = Disparas a { $coord }. ¡Impacto directo!
battleship-hit-target = { $player } dispara a tu { $coord }. ¡Impacto directo!
battleship-hit-spectator = { $player } dispara a { $coord } de { $target }. ¡Impacto directo!

# Miss — first/second/third
battleship-miss-self = Disparas a { $coord }. Fallaste.
battleship-miss-target = { $player } dispara a tu { $coord }. Falló.
battleship-miss-spectator = { $player } dispara a { $coord } de { $target }. Falló.

# Sunk — first/second/third
battleship-sunk-self = ¡Hundiste el { $ship } enemigo!
battleship-sunk-target = ¡{ $player } hundió tu { $ship }!
battleship-sunk-spectator = ¡{ $player } hundió el { $ship } de { $target }!

# Victory — first/second/third
battleship-victory-self = ¡Ganas! Todas las naves enemigas fueron hundidas.
battleship-victory-target = ¡{ $player } gana! Todas tus naves fueron hundidas.
battleship-victory-spectator = ¡{ $player } gana! Todas las naves de { $target } fueron hundidas.

battleship-shot-in-flight = Un proyectil todavía está en el aire. Espera el resultado antes de volver a disparar.
battleship-not-your-turn = No es tu turno para disparar. Espera a que { $player } elija una coordenada.
battleship-wait-for-turn = Espera la siguiente orden de fuego antes de elegir una coordenada.
battleship-already-shot = Ya disparaste a { $coord }. Elige una coordenada sin explorar.
battleship-switch-to-shots = Estás viendo tus propias aguas, así que no puedes disparar. Presiona V para cambiar a la cuadrícula del objetivo.
battleship-timeout-fire = ¡Se acabó el tiempo! Disparo automático a { $coord }.

# View toggle
battleship-view-own = Viendo tus aguas.
battleship-view-shots = Viendo la cuadrícula del objetivo.

# Cell labels
battleship-cell-empty = { $coord }, agua abierta.
battleship-cell-ship-placed = { $coord }, { $ship }.
battleship-cell-unknown = { $coord }, sin explorar.
battleship-cell-hit = { $coord }, impacto.
battleship-cell-sunk = { $coord }, { $ship }, hundido.
battleship-cell-miss = { $coord }, fallo.
battleship-cell-own-ship = { $coord }, tu { $ship }.
battleship-cell-own-hit = { $coord }, tu { $ship }, impactado.
battleship-cell-own-sunk = { $coord }, tu { $ship }, hundido.
battleship-cell-own-miss = { $coord }, disparo enemigo fallido.

# Fleet status
battleship-fleet-header = Tu Flota
battleship-status-intact = Listo para el combate
battleship-status-damaged = Dañado ({ $hits } de { $size } impactos)
battleship-status-sunk = Hundido

battleship-enemy-fleet-header = Flota Enemiga
battleship-enemy-fleet-summary = { $sunk } de { $total } naves enemigas hundidas.
battleship-enemy-ship-sunk = { $ship } (tamaño { $size }): Hundido

# End screen
battleship-winner-line = ¡{ $player } gana!
battleship-stats-line = { $player }: { $shots } disparos realizados, { $hits } impactos, { $accuracy }% de precisión
