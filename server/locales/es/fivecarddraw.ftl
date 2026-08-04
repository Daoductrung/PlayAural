game-name-fivecarddraw = Póker de Cinco Cartas

draw-set-starting-chips = Fichas iniciales: { $count }
draw-enter-starting-chips = Ingresa las fichas iniciales
draw-option-changed-starting-chips = Fichas iniciales establecidas en { $count }.
fivecarddraw-desc-starting-chips = Pila inicial de cada jugador en Póker de Cinco Cartas, de 100 a 1,000,000 de fichas. Por defecto: 20,000.

draw-set-ante = Ante: { $count }
draw-enter-ante = Ingresa el monto del ante
draw-option-changed-ante = Ante establecido en { $count }.
fivecarddraw-desc-ante = Contribución forzosa que aporta cada jugador activo antes de cada mano. Debe ser menor que la pila inicial (por defecto 100, rango 0-1,000,000 de fichas).

draw-set-turn-timer = Temporizador de turno: { $mode }
draw-select-turn-timer = Selecciona el temporizador de turno
draw-option-changed-turn-timer = Temporizador de turno establecido en { $mode }.
fivecarddraw-desc-turn-timer = Límite de tiempo opcional para cada decisión de apuesta o descarte: 5, 10, 15, 20, 30, 45, 60 o 90 segundos, o Ilimitado. Por defecto: Ilimitado.

draw-set-raise-mode = Modo de subida: { $mode }
draw-select-raise-mode = Selecciona el modo de subida
draw-option-changed-raise-mode = Modo de subida establecido en { $mode }.
fivecarddraw-desc-raise-mode = Estilo de límite de subida: Sin límite, Límite de bote o Límite de doble bote. Los modos basados en el bote requieren un ante mayor que 0 para que la primera ronda de apuestas pueda abrirse con normalidad (por defecto Sin límite).

draw-set-max-raises = Máximo de subidas por ronda de apuestas: { $count }
draw-enter-max-raises = Ingresa el máximo de subidas por ronda de apuestas (0 para ilimitado)
draw-option-changed-max-raises = Máximo de subidas por ronda de apuestas establecido en { $count }.
fivecarddraw-desc-max-raises = Máximo de subidas permitidas en una ronda de apuestas, de 0 a 10. Usa 0 para no limitar las subidas. Por defecto: 0.

draw-set-draw-limit = Regla de descarte: { $mode }
draw-select-draw-limit = Selecciona la regla de descarte
draw-option-changed-draw-limit = Regla de descarte establecida en { $mode }.
fivecarddraw-desc-draw-limit = Regla de descarte: cambiar hasta 3 cartas, o permitir 4 cartas solo si conservas un As. Por defecto: hasta 3 cartas.
draw-limit-three-cards = Hasta 3 cartas (estándar)
draw-limit-four-with-ace = Hasta 4 cartas si conservas un As

draw-error-ante-too-high = El ante ({ $ante } fichas) debe ser menor que la pila inicial ({ $chips } fichas) para que los jugadores puedan seguir tomando decisiones de apuesta después del reparto.
draw-error-capped-mode-needs-ante = { $mode ->
    [pot_limit] Límite de bote
    [double_pot] Límite de doble bote
   *[other] Este modo de subida limitado
} requiere un ante mayor que 0 para que el primer jugador tenga un monto basado en el bote disponible para apostar.

draw-antes-posted = Se pagaron los antes. El bote ahora tiene { $amount } fichas.
draw-betting-round-1 = Primera ronda de apuestas.
draw-betting-round-2 = Segunda ronda de apuestas.
draw-begin-draw = Fase de descarte. Empezando por el primer jugador activo a la izquierda del repartidor, elige las cartas para cambiar o plántate con las tuyas.
draw-not-draw-phase = El descarte solo está disponible después de la primera ronda de apuestas. Continúa con la acción de apuesta actual.
draw-not-betting = No se puede apostar durante la fase de descarte. Selecciona las cartas que quieras cambiar y luego elige Descartar cartas.
draw-fold-not-available = No puedes retirarte durante la fase de descarte. Selecciona las cartas que quieras cambiar y luego elige Descartar cartas.

draw-toggle-discard = Selecciona la carta { $index } para cambiar
draw-card-keep = { $card }
draw-card-discard = { $card }, seleccionada para cambiar
draw-draw-cards = Descartar cartas
draw-draw-cards-count = { $count ->
    [0] Plantarte con tu mano
    [one] Cambiar 1 carta
   *[other] Cambiar { $count } cartas
}
draw-dealt-cards = Tus cinco cartas son { $cards }.
draw-you-drew-cards = { $count ->
    [one] Tu carta de reemplazo es
   *[other] Tus cartas de reemplazo son
} { $cards }.
draw-you-draw = Cambias { $count } { $count ->
    [one] carta
   *[other] cartas
}.
draw-player-draws = { $player } cambia { $count } { $count ->
    [one] carta
   *[other] cartas
}.
draw-you-stand-pat = Te plantas y conservas las cinco cartas.
draw-player-stands-pat = { $player } se planta y conserva las cinco cartas.
draw-you-discard-limit = No puedes cambiar más de { $count } cartas bajo la regla de descarte seleccionada.
draw-four-requires-kept-ace = Cambiar 4 cartas requiere que conserves al menos un As. Deselecciona un As o cambia como máximo 3 cartas.

draw-raise-invalid = Ingresa un número entero mayor que 0 para el monto a subir.
draw-raise-cap-reached = Ya se alcanzó el límite de { $count } subidas en esta ronda de apuestas. Puedes igualar o retirarte.
draw-raise-over-stack = Intentaste subir { $requested } fichas, pero solo te quedan { $chips } fichas. Ingresa una subida menor o elige All in.
draw-raise-too-small = Intentaste subir { $requested } fichas. La subida mínima es { $minimum } fichas.
draw-raise-over-limit = Intentaste subir { $requested } fichas. Bajo { $mode ->
    [pot_limit] límite de bote
    [double_pot] límite de doble bote
   *[other] el modo de subida seleccionado
}, la subida máxima disponible después de igualar es { $maximum } fichas.
draw-all-in-over-limit = No puedes ir All in con las { $stack } fichas que te quedan porque { $mode ->
    [pot_limit] el límite de bote
    [double_pot] el límite de doble bote
   *[other] el modo de subida seleccionado
} actualmente permite una subida de máximo { $maximum } fichas después de igualar. Usa Subir para ingresar un monto permitido.
draw-all-in-raise-cap-reached = No puedes ir All in como subida completa porque ya se alcanzó el límite de { $count } subidas. Puedes igualar o retirarte.
draw-all-in-unavailable-raise-cap = All in no está disponible porque sería una subida completa después de alcanzar el límite de subidas. Puedes igualar o retirarte.
draw-all-in-unavailable-limit = All in no está disponible porque tu pila supera el límite de apuestas actual. Usa Subir para ingresar un monto permitido.
draw-raise-unavailable-cap = No puedes subir porque esta ronda de apuestas ya alcanzó su límite de subidas.
draw-raise-unavailable-limit = No hay una subida completa disponible con tu pila y el límite de apuestas actual. Puedes igualar, retirarte o usar All in cuando sea legal.

draw-current-bet = La apuesta actual en la mesa es de { $amount } fichas.
draw-raise-range = La subida mínima es { $minimum } fichas. Puedes subir hasta { $maximum } fichas después de igualar.
draw-no-full-raise-available = Necesitas { $to_call } fichas para igualar y solo te quedan { $chips } fichas, así que no puedes hacer una subida completa. Puedes igualar con todo o retirarte.
draw-dealer-unavailable = Todavía no hay una posición de repartidor para la mano actual.
draw-position-unavailable = No estás activo en la mano actual, así que no tienes una posición de apuesta.

draw-card-key = Tecla de carta { $index }

draw-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
