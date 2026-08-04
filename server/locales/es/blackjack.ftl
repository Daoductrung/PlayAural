# Blackjack

game-name-blackjack = Blackjack

blackjack-set-rules-profile = Perfil de reglas: { $profile }
blackjack-select-rules-profile = Selecciona el perfil de reglas
blackjack-option-changed-rules-profile = Perfil de reglas establecido en { $profile }.
blackjack-desc-rules-profile = Aplica un paquete de reglas predefinido de Blackjack: Las Vegas, Europeo o Amistoso.

blackjack-set-starting-chips = Fichas iniciales: { $count }
blackjack-enter-starting-chips = Ingresa las fichas iniciales
blackjack-option-changed-starting-chips = Fichas iniciales establecidas en { $count }.
blackjack-desc-starting-chips = Con cuántas fichas empieza cada jugador en la mesa de Blackjack (por defecto 500, rango 50-1000000).

blackjack-set-base-bet = Apuesta base: { $count }
blackjack-enter-base-bet = Ingresa la apuesta base
blackjack-option-changed-base-bet = Apuesta base establecida en { $count }.
blackjack-desc-base-bet = La apuesta predeterminada que se ofrece entre manos de Blackjack (por defecto 10, rango 1-100000).
blackjack-enter-bet = Ingresa tu apuesta de fichas
blackjack-option-changed-bet = Apuesta establecida en { $count } fichas.

blackjack-set-table-min-bet = Apuesta mínima de mesa: { $count }
blackjack-enter-table-min-bet = Ingresa la apuesta mínima de mesa
blackjack-option-changed-table-min-bet = Apuesta mínima de mesa establecida en { $count }.
blackjack-desc-table-min-bet = La apuesta más pequeña permitida en Blackjack (por defecto 5, rango 1-100000).

blackjack-set-table-max-bet = Apuesta máxima de mesa: { $count }
blackjack-enter-table-max-bet = Ingresa la apuesta máxima de mesa
blackjack-option-changed-table-max-bet = Apuesta máxima de mesa establecida en { $count }.
blackjack-desc-table-max-bet = La apuesta más grande permitida en Blackjack (por defecto 100, rango 1-100000).

blackjack-set-deck-count = Número de barajas: { $count }
blackjack-enter-deck-count = Ingresa el número de barajas
blackjack-option-changed-deck-count = Número de barajas establecido en { $count }.
blackjack-desc-deck-count = Cuántas barajas estándar de 52 cartas se mezclan en el zapato de Blackjack (por defecto 4, rango 1-8).

blackjack-set-dealer-soft-17 = El repartidor pide en 17 blando: { $enabled }
blackjack-option-changed-dealer-soft-17 = El repartidor pide en 17 blando establecido en { $enabled }.
blackjack-desc-dealer-hits-soft-17 = Controla si el repartidor debe pedir carta con un 17 blando, como As más 6.

blackjack-set-dealer-peek-blackjack = El repartidor revisa si tiene blackjack: { $enabled }
blackjack-option-changed-dealer-peek-blackjack = Revisión de blackjack del repartidor establecida en { $enabled }.
blackjack-desc-dealer-peeks-blackjack = Controla si el repartidor revisa si tiene Blackjack cuando muestra un As o una carta de valor diez.

blackjack-set-players-cards-face-up = Cartas de los jugadores boca arriba: { $enabled }
blackjack-option-changed-players-cards-face-up = Cartas de los jugadores boca arriba establecido en { $enabled }.
blackjack-desc-players-cards-face-up = Controla si las cartas de los jugadores son visibles para toda la mesa.

blackjack-set-allow-insurance = Ofrecer seguro y pago igualado: { $enabled }
blackjack-option-changed-allow-insurance = Seguro y pago igualado establecido en { $enabled }.
blackjack-desc-allow-insurance = Controla si se ofrecen las opciones de seguro y pago igualado cuando el repartidor muestra un As.

blackjack-set-allow-late-surrender = Permitir rendición tardía: { $enabled }
blackjack-option-changed-allow-late-surrender = Rendición tardía establecida en { $enabled }.
blackjack-desc-allow-late-surrender = Controla si los jugadores pueden rendirse antes de pedir carta; esto requiere que el repartidor revise si tiene blackjack.

blackjack-set-blackjack-payout = Pago de blackjack: { $mode }
blackjack-select-blackjack-payout = Selecciona el pago de blackjack
blackjack-option-changed-blackjack-payout = Pago de blackjack establecido en { $mode }.
blackjack-desc-blackjack-payout = Define el pago por un Blackjack natural: 3 a 2, 6 a 5, o pago igualado.

blackjack-set-double-down-rule = Regla de doblar: { $mode }
blackjack-select-double-down-rule = Selecciona la regla de doblar
blackjack-option-changed-double-down-rule = Regla de doblar establecida en { $mode }.
blackjack-desc-double-down-rule = Controla qué totales iniciales pueden doblar: cualquier par de cartas, solo 9-11, o solo 10-11.

blackjack-set-allow-double-after-split = Doblar después de dividir: { $enabled }
blackjack-option-changed-allow-double-after-split = Doblar después de dividir establecido en { $enabled }.
blackjack-desc-allow-double-after-split = Controla si las manos divididas pueden doblar.

blackjack-set-split-rule = Regla de división: { $mode }
blackjack-select-split-rule = Selecciona la regla de división
blackjack-option-changed-split-rule = Regla de división establecida en { $mode }.
blackjack-desc-split-rule = Controla si una división requiere exactamente el mismo rango o solo el mismo valor de carta.

blackjack-set-max-split-hands = Máximo de manos divididas: { $count }
blackjack-enter-max-split-hands = Ingresa el máximo de manos divididas
blackjack-option-changed-max-split-hands = Máximo de manos divididas establecido en { $count }.
blackjack-desc-max-split-hands = Número máximo de manos que un jugador puede crear al dividir (por defecto 2, rango 1-2).

blackjack-set-split-aces-one-card = Los ases divididos reciben solo una carta: { $enabled }
blackjack-option-changed-split-aces-one-card = Regla de una carta para ases divididos establecida en { $enabled }.
blackjack-desc-split-aces-one-card-only = Controla si cada As dividido recibe exactamente una carta y luego se planta.

blackjack-set-split-aces-blackjack = Los ases divididos pueden contar como blackjack: { $enabled }
blackjack-option-changed-split-aces-blackjack = Regla de blackjack para ases divididos establecida en { $enabled }.
blackjack-desc-split-aces-count-as-blackjack = Controla si As más una carta de valor diez después de dividir Ases cuenta como un Blackjack natural.

blackjack-set-turn-timer = Temporizador de turno: { $mode }
blackjack-select-turn-timer = Selecciona el temporizador de turno
blackjack-option-changed-turn-timer = Temporizador de turno establecido en { $mode }.
blackjack-desc-turn-timer = Límite de tiempo opcional para cada decisión de Blackjack; elige Ilimitado para desactivar el temporizador.

blackjack-rules-profile-vegas = Las Vegas
blackjack-rules-profile-european = Europeo
blackjack-rules-profile-friendly = Amistoso
blackjack-payout-3-to-2 = 3 a 2
blackjack-payout-6-to-5 = 6 a 5
blackjack-payout-1-to-1 = 1 a 1
blackjack-double-rule-any-two = Cualquier par de cartas
blackjack-double-rule-9-to-11 = Totales de 9 a 11
blackjack-double-rule-10-to-11 = Totales de 10 a 11
blackjack-split-rule-same-value = Mismo valor
blackjack-split-rule-same-rank = Mismo rango

blackjack-hit = Pedir
blackjack-stand = Plantarse
blackjack-double-down = Doblar
blackjack-split = Dividir
blackjack-surrender = Rendirse
blackjack-take-insurance = Tomar seguro
blackjack-decline-insurance = Rechazar seguro
blackjack-even-money = Tomar pago igualado
blackjack-read-hand = Leer mano
blackjack-read-dealer = Leer repartidor
blackjack-read-bets = Leer apuestas
blackjack-table-status = Estado de la mesa
blackjack-read-rules = Leer reglas

blackjack-not-player-phase = Los jugadores no están realizando acciones en este momento.
blackjack-not-insurance-phase = Las decisiones de seguro no están activas en este momento.
blackjack-hand-complete = Tu mano está completa.
blackjack-error-bet-too-high = La apuesta base no puede ser mayor que las fichas iniciales.
blackjack-error-starting-chips-below-min = Las fichas iniciales no pueden ser menores que la apuesta mínima de mesa.
blackjack-error-table-limits-invalid = La apuesta mínima de mesa no puede ser mayor que la apuesta máxima de mesa.
blackjack-error-bet-below-min = La apuesta no puede ser menor que la apuesta mínima de mesa.
blackjack-error-bet-above-max = La apuesta no puede ser mayor que la apuesta máxima de mesa.
blackjack-error-bet-above-chips = No puedes apostar más fichas de las que tienes.
blackjack-error-late-surrender-requires-peek = La rendición tardía requiere que la revisión de blackjack del repartidor esté activada.
blackjack-cannot-split = No puedes dividir esta mano.
blackjack-cannot-double-down = No puedes doblar en este momento.
blackjack-cannot-surrender = No puedes rendirte en esta mano.
blackjack-insurance-closed = No puedes tomar una decisión de seguro en este momento.
blackjack-cannot-insure = No puedes tomar seguro en este momento.
blackjack-cannot-even-money = No puedes tomar el pago igualado en este momento.
blackjack-bet-already-locked = Tu apuesta ya está bloqueada para esta mano.
blackjack-out-of-chips = Te quedaste sin fichas.

blackjack-hand-start = Mano { $hand }. Coloca tus apuestas.
blackjack-you-bet = Apuestas { $amount }.
blackjack-player-bets = { $player } apuesta { $amount }.
blackjack-bet-locked = Apuesta bloqueada en { $amount } fichas.
blackjack-insurance-offer = El seguro está disponible.
blackjack-insurance-prompt = Seguro disponible. Puedes asegurarte por { $amount } fichas o rechazar.
blackjack-insurance-prompt-player = Decisión de seguro para { $player }.
blackjack-insurance-prompt-even-money = Ahora puedes tomar el pago igualado.
blackjack-insurance-prompt-even-money-player = { $player } puede tomar el pago igualado.

blackjack-dealer-shows = El repartidor muestra { $card }.
blackjack-dealer-reveals = El repartidor revela { $card }, para un total de { $total }.
blackjack-dealer-hits = El repartidor saca { $card }, para un total de { $total }.
blackjack-dealer-stands = El repartidor se planta con { $total }.
blackjack-dealer-bust = El repartidor se pasa con { $total }.
blackjack-dealer-blackjack = El repartidor tiene blackjack.

blackjack-you-have = Tienes { $cards } ({ $total }).
blackjack-player-has = { $player } tiene { $cards } ({ $total }).
blackjack-you-blackjack = Tienes blackjack.
blackjack-player-blackjack = { $player } tiene blackjack.

blackjack-you-hit = Sacas { $card }.
blackjack-player-hits = { $player } saca { $card }.
blackjack-you-stand = Te plantas.
blackjack-player-stands = { $player } se planta.
blackjack-you-double-down = Doblas por { $amount } fichas.
blackjack-player-double-downs = { $player } dobla por { $amount } fichas.
blackjack-you-split = Divides tu mano y añades { $amount } fichas.
blackjack-player-splits = { $player } divide su mano y añade { $amount } fichas.
blackjack-you-surrender = Te rindes y pierdes { $amount } fichas.
blackjack-player-surrenders = { $player } se rinde y pierde { $amount } fichas.
blackjack-you-take-insurance = Colocas una apuesta de seguro de { $amount } fichas.
blackjack-player-takes-insurance = { $player } coloca una apuesta de seguro de { $amount } fichas.
blackjack-you-decline-insurance = Rechazas el seguro.
blackjack-player-declines-insurance = { $player } rechaza el seguro.
blackjack-you-take-even-money = Tomas el pago igualado.
blackjack-player-takes-even-money = { $player } toma el pago igualado.
blackjack-you-split-aces-auto-stand = Los ases divididos reciben una carta cada uno y se plantan automáticamente.
blackjack-player-splits-aces-auto-stand = { $player } divide sus ases y ambas manos se plantan.
blackjack-you-stand-auto = Te plantas con 21.
blackjack-player-stands-auto = { $player } se planta con 21.
blackjack-you-bust = Te pasas con { $total }.
blackjack-player-bust = { $player } se pasa con { $total }.
blackjack-your-total = Tu total es { $total }.
blackjack-player-total = { $player } tiene { $total }.
blackjack-your-total-hand = Mano { $hand }: { $total }.
blackjack-player-total-hand = { $player } mano { $hand }: { $total }.

blackjack-you-win = Ganas { $amount } fichas.
blackjack-player-wins = { $player } gana { $amount } fichas.
blackjack-you-even-money-win = El pago igualado paga { $amount } fichas.
blackjack-player-even-money-win = { $player } recibe { $amount } fichas por el pago igualado.
blackjack-you-lose = Pierdes { $amount } fichas.
blackjack-player-loses = { $player } pierde { $amount } fichas.
blackjack-you-push = Empate.
blackjack-player-push = { $player } empata.
blackjack-you-win-hand = Mano { $hand }: Ganas { $amount } fichas.
blackjack-player-wins-hand = { $player } mano { $hand } gana { $amount } fichas.
blackjack-you-lose-hand = Mano { $hand }: Pierdes { $amount } fichas.
blackjack-player-loses-hand = { $player } mano { $hand } pierde { $amount } fichas.
blackjack-you-push-hand = Mano { $hand }: Empate.
blackjack-player-push-hand = { $player } mano { $hand } empata.
blackjack-you-insurance-wins = El seguro gana { $amount } fichas.
blackjack-player-insurance-wins = { $player } gana { $amount } fichas del seguro.
blackjack-you-insurance-loses = El seguro pierde { $amount } fichas.
blackjack-player-insurance-loses = { $player } pierde una apuesta de seguro de { $amount } fichas.
blackjack-you-broke = Te quedaste sin fichas.
blackjack-player-broke = { $player } se quedó sin fichas.
blackjack-you-win-game = Ganas la partida con { $chips } fichas.
blackjack-player-wins-game = { $player } gana la partida con { $chips } fichas.

blackjack-total-soft = { $total } blando
blackjack-total-hard = { $total }

blackjack-read-hand-response = Tu mano es { $cards } ({ $total }).
blackjack-read-hand-response-split = Mano 1: { $hand1 } ({ $total1 }). Mano 2: { $hand2 } ({ $total2 }). Mano activa: { $active }.
blackjack-no-hand = No estás en la mano actual.
blackjack-no-dealer-cards = El repartidor aún no tiene cartas.
blackjack-read-dealer-up = El repartidor muestra { $card }.
blackjack-read-dealer-full = El repartidor tiene { $cards } ({ $total }).
blackjack-rule-yes = sí
blackjack-rule-no = no
blackjack-rules-readout = Reglas: perfil { $profile }. Límites de mesa { $min_bet } a { $max_bet }, apuesta base { $base_bet }. El repartidor pide en 17 blando: { $soft_17 }. El repartidor revisa blackjack: { $peek }. Cartas de jugadores boca arriba: { $players_cards_face_up }. Seguro y pago igualado: { $insurance }. Rendición tardía: { $surrender }. Pago de blackjack: { $payout }. Regla de doblar: { $double_rule }. Doblar después de dividir: { $das }. Regla de división: { $split_rule }. Máximo de manos divididas: { $split_hands }. Regla de una carta para ases divididos: { $split_aces_one }. Blackjack en ases divididos: { $split_aces_blackjack }.

blackjack-status-line = { $player }: { $chips } fichas
blackjack-status-line-out = { $player }: sin fichas
blackjack-status-line-bet = { $player }: { $chips } fichas, apuesta { $bet }
blackjack-status-line-hand = { $player }: { $chips } fichas, apuesta { $bet }, total { $total }
blackjack-status-line-hands = { $player }: { $chips } fichas, mano 1 apuesta { $bet1 } total { $total1 }, mano 2 apuesta { $bet2 } total { $total2 }
blackjack-status-dealer = Repartidor: { $cards } ({ $total })
blackjack-status-dealer-up = Repartidor: mostrando { $card }
blackjack-no-active-players = No hay jugadores activos.
blackjack-waiting-for-bets = Esperando apuestas de { $players }.
blackjack-bet-previous-label = Apostar { $amount }
blackjack-end-screen-line = { $rank }. { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
blackjack-change-bet = Cambiar apuesta
