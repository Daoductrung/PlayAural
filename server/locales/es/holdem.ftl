game-name-holdem = Póker Texas Hold'em

holdem-set-starting-chips = Fichas iniciales: { $count }
holdem-enter-starting-chips = Ingresa las fichas iniciales
holdem-option-changed-starting-chips = Fichas iniciales establecidas en { $count }.
holdem-desc-starting-chips = Pila inicial de cada jugador en Texas Hold'em, de 100 a 1,000,000 de fichas. Por defecto: 20,000.

holdem-set-big-blind = Ciega grande: { $count }
holdem-enter-big-blind = Ingresa la ciega grande
holdem-option-changed-big-blind = Ciega grande establecida en { $count }.
holdem-desc-big-blind = Monto base de la ciega grande. Debe ser menor que la pila inicial (por defecto 200, rango 1-1,000,000 de fichas).

holdem-set-ante = Ante: { $count }
holdem-enter-ante = Ingresa el ante
holdem-option-changed-ante = Ante establecido en { $count }.
holdem-desc-ante = Contribución forzosa opcional que aporta cada jugador activo cuando los antes están activos, de 0 a 1,000,000 de fichas. Por defecto: 0.

holdem-set-ante-start = El ante empieza en el nivel: { $count }
holdem-enter-ante-start = Ingresa el nivel de ciegas en el que se activa el ante
holdem-option-changed-ante-start = Nivel de inicio del ante establecido en { $count }.
holdem-desc-ante-start-level = Nivel de ciegas en el que empiezan los antes. Un ante mayor que 0 está activo desde la primera mano cuando este valor es 0 (por defecto 0, rango 0-20).

holdem-set-turn-timer = Temporizador de turno: { $mode }
holdem-select-turn-timer = Selecciona el temporizador de turno
holdem-option-changed-turn-timer = Temporizador de turno establecido en { $mode }.
holdem-desc-turn-timer = Límite de tiempo opcional para cada decisión en Hold'em: 5, 10, 15, 20, 30, 45, 60 o 90 segundos, o Ilimitado. Por defecto: Ilimitado.

holdem-set-blind-timer = Temporizador de ciegas: { $mode }
holdem-select-blind-timer = Selecciona el temporizador de ciegas
holdem-option-changed-blind-timer = Temporizador de ciegas establecido en { $mode }.
holdem-desc-blind-timer = Minutos entre cada aumento de ciegas: 5, 10, 15, 20 o 30. Por defecto: 20 minutos.

holdem-set-raise-mode = Modo de subida: { $mode }
holdem-select-raise-mode = Selecciona el modo de subida
holdem-option-changed-raise-mode = Modo de subida establecido en { $mode }.
holdem-desc-raise-mode = Estilo de límite de subida: Sin límite, Límite de bote o Límite de doble bote. Por defecto: Sin límite.

holdem-set-max-raises = Máximo de subidas por ronda de apuestas: { $count }
holdem-enter-max-raises = Ingresa el máximo de subidas por ronda de apuestas (0 para ilimitado)
holdem-option-changed-max-raises = Máximo de subidas por ronda de apuestas establecido en { $count }.
holdem-desc-max-raises = Máximo de subidas permitidas en una ronda de apuestas, de 0 a 10. Usa 0 para no limitar las subidas. Por defecto: 0.

holdem-error-big-blind-too-high = La ciega grande ({ $blind } fichas) debe ser menor que la pila inicial ({ $chips } fichas).
holdem-error-ante-too-high = El ante ({ $ante } fichas) debe ser menor que la pila inicial ({ $chips } fichas).
holdem-error-forced-bets-too-high = Con los antes activos desde el nivel 0, el ante más la ciega grande ({ $ante } + { $blind } fichas) debe ser menor que la pila inicial ({ $chips } fichas).

holdem-antes-posted = Se pagaron los antes. El bote ahora tiene { $amount } fichas.
holdem-you-post-small-blind = Pagas la ciega pequeña ({ $sb } fichas). { $bb_player } paga la ciega grande ({ $bb } fichas).
holdem-you-post-big-blind = { $sb_player } paga la ciega pequeña ({ $sb } fichas). Pagas la ciega grande ({ $bb } fichas).
holdem-players-post-blinds = { $sb_player } paga la ciega pequeña ({ $sb } fichas). { $bb_player } paga la ciega grande ({ $bb } fichas).

holdem-raise-invalid = Ingresa un número entero mayor que 0 para el monto a subir.
holdem-raise-cap-reached = Ya se alcanzó el límite de { $count } subidas en esta ronda de apuestas. Puedes igualar o retirarte.
holdem-raise-over-stack = Intentaste subir { $requested } fichas, pero solo te quedan { $chips } fichas. Ingresa una subida menor o elige All in.
holdem-raise-too-small = Intentaste subir { $requested } fichas. La subida mínima es { $minimum } fichas.
holdem-raise-over-limit = Intentaste subir { $requested } fichas. Bajo { $mode ->
    [pot_limit] límite de bote
    [double_pot] límite de doble bote
   *[other] el modo de subida seleccionado
}, la subida máxima disponible después de igualar es { $maximum } fichas.
holdem-all-in-over-limit = No puedes ir All in con las { $stack } fichas que te quedan porque { $mode ->
    [pot_limit] el límite de bote
    [double_pot] el límite de doble bote
   *[other] el modo de subida seleccionado
} actualmente permite una subida de máximo { $maximum } fichas después de igualar. Usa Subir para ingresar un monto permitido.
holdem-all-in-raise-cap-reached = No puedes ir All in como subida completa porque ya se alcanzó el límite de { $count } subidas. Puedes igualar o retirarte.
holdem-all-in-unavailable-raise-cap = All in no está disponible porque sería una subida completa después de alcanzar el límite de subidas. Puedes igualar o retirarte.
holdem-all-in-unavailable-limit = All in no está disponible porque tu pila supera el límite de apuestas actual. Usa Subir para ingresar un monto permitido.
holdem-raise-unavailable-cap = No puedes subir porque esta ronda de apuestas ya alcanzó su límite de subidas.
holdem-raise-unavailable-limit = No hay una subida completa disponible con tu pila y el límite de apuestas actual. Puedes igualar, retirarte o usar All in cuando sea legal.

holdem-current-bet = La apuesta actual en la mesa es de { $amount } fichas.
holdem-raise-range = La subida mínima es { $minimum } fichas. Puedes subir hasta { $maximum } fichas después de igualar.
holdem-no-full-raise-available = Necesitas { $to_call } fichas para igualar y solo te quedan { $chips } fichas, así que no puedes hacer una subida completa. Puedes igualar con todo o retirarte.
holdem-button-unavailable = Todavía no hay una posición de botón para la mano actual.
holdem-position-unavailable = No estás activo en la mano actual, así que no tienes una posición de apuesta.
holdem-reveal-no-live-hand = Solo puedes revelar tus cartas cuando llegaste al showdown con una mano viva.
holdem-private-hand-unavailable = Te quedaste sin fichas y ya no tienes una mano viva para leer.

holdem-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
