# Bolas Rodantes

game-name-rollingballs = Bolas Rodantes

# Acciones
rb-take = Tomar { $count } { $count ->
    [one] bola
   *[other] bolas
}
rb-reshuffle-action = Volver a barajar el frente del tubo (quedan { $remaining } usos)
rb-view-pipe-action = Previsualizar el tubo (quedan { $remaining } usos)
rb-check-pipe-status = Ver estado del tubo
rb-key-reshuffle-pipe = Volver a barajar el frente del tubo
rb-key-view-pipe = Previsualizar el tubo

# Tomar y revelar bolas
rb-you-take = Te comprometes a tomar { $count } { $count ->
    [one] bola
   *[other] bolas
} del frente del tubo de { $remaining } bolas.
rb-player-takes = { $player } se compromete a tomar { $count } { $count ->
    [one] bola
   *[other] bolas
} del frente del tubo de { $remaining } bolas.
rb-you-take-brief = Tomas { $count } { $count ->
    [one] bola
   *[other] bolas
}.
rb-player-takes-brief = { $player } toma { $count } { $count ->
    [one] bola
   *[other] bolas
}.
rb-you-forced-take = Solo { $count ->
    [one] queda 1 bola
   *[other] quedan { $count } bolas
}, menos que el mínimo de { $minimum }, así que debes tomar el resto.
rb-player-forced-takes = Solo { $count ->
    [one] queda 1 bola
   *[other] quedan { $count } bolas
}, menos que el mínimo de { $minimum }, así que { $player } debe tomar el resto.
rb-you-forced-take-brief = Debes tomar las últimas { $count } { $count ->
    [one] bola
   *[other] bolas
}.
rb-player-forced-takes-brief = { $player } debe tomar las últimas { $count } { $count ->
    [one] bola
   *[other] bolas
}.

rb-your-ball-plus = Tu bola { $num }: { $description }. Más { $value } { $value ->
    [one] punto
   *[other] puntos
}.
rb-player-ball-plus = La bola { $num } de { $player }: { $description }. Más { $value } { $value ->
    [one] punto
   *[other] puntos
}.
rb-your-ball-minus = Tu bola { $num }: { $description }. Menos { $value } { $value ->
    [one] punto
   *[other] puntos
}.
rb-player-ball-minus = La bola { $num } de { $player }: { $description }. Menos { $value } { $value ->
    [one] punto
   *[other] puntos
}.
rb-your-ball-zero = Tu bola { $num }: { $description }. Sin cambio en la puntuación.
rb-player-ball-zero = La bola { $num } de { $player }: { $description }. Sin cambio en la puntuación.

rb-your-draw-summary = Tu robo de { $count } bolas tiene un valor neto de { $delta } puntos. Tu puntuación ahora es { $score }, con { $remaining } bolas restantes en el tubo.
rb-player-draw-summary = El robo de { $count } bolas de { $player } tiene un valor neto de { $delta } puntos. La puntuación de { $player } ahora es { $score }, con { $remaining } bolas restantes en el tubo.
rb-your-draw-summary-brief = Neto { $delta }; tu puntuación es { $score }. Quedan { $remaining } bolas.
rb-player-draw-summary-brief = { $player }: neto { $delta }, puntuación { $score }. Quedan { $remaining } bolas.
rb-your-score-legacy = Tu puntuación ahora es { $score }, con { $remaining } bolas restantes en el tubo.
rb-player-score-legacy = La puntuación de { $player } ahora es { $score }, con { $remaining } bolas restantes en el tubo.

# Volver a barajar
rb-you-reshuffle = Vuelves a barajar las primeras { $count } bolas. { $penalty ->
    [0] No hay penalización
   *[other] Pagas una penalización de { $penalty } puntos
}; tu puntuación ahora es { $score }, y te quedan { $remaining } barajadas.
rb-player-reshuffles = { $player } vuelve a barajar las primeras { $count } bolas. { $penalty ->
    [0] No hay penalización
   *[other] { $player } paga una penalización de { $penalty } puntos
}; su puntuación ahora es { $score }, y le quedan { $remaining } barajadas.
rb-you-reshuffle-brief = Vuelves a barajar { $count } bolas; penalización { $penalty }, puntuación { $score }, quedan { $remaining } usos.
rb-player-reshuffles-brief = { $player } vuelve a barajar { $count } bolas; penalización { $penalty }, puntuación { $score }, quedan { $remaining } usos.

# Vista previa y estado del tubo
rb-view-pipe-header = Mostrando las próximas { $shown } de { $total } bolas. Te quedan { $remaining } vistas previas nuevas.
rb-view-pipe-ball = { $num }: { $description }. Valor: { $value } puntos.
rb-status-pipe = Ronda { $round }. Quedan { $count } bolas en el tubo.
rb-status-take-range = Cada turno normal requiere entre { $min } y { $max } bolas.
rb-status-turn = Turno actual: { $player }.
rb-status-resources = Te quedan { $views } vistas previas nuevas del tubo y { $reshuffles } barajadas.

# Inicio y flujo de ronda
rb-pipe-filled = El tubo se llenó con { $count } bolas únicas de: { $packs }.
rb-round-start = Comienza la ronda { $round } con { $count } bolas restantes en el tubo.
rb-round-start-brief = Ronda { $round }; quedan { $count } bolas.

# Fin de la partida
rb-pipe-empty = El tubo está vacío.
rb-winner = { $player } gana con { $score } puntos.
rb-you-win = Ganas con { $score } puntos.
rb-you-tie = Compartes la victoria con { $players }; todos terminaron con { $score } puntos.
rb-tie = { $players } comparten la victoria con { $score } puntos.
rb-line-format = { $rank }. { $player }: { $points }

# Opciones
rb-set-min-take = Mínimo de bolas por turno: { $count }
rb-enter-min-take = Ingresa el mínimo de bolas por turno, de 1 a 5:
rb-option-changed-min-take = Mínimo de bolas por turno establecido en { $count }.
rollingballs-desc-min-take = Número mínimo de bolas que un jugador debe tomar en un turno (por defecto 1, rango 1-5).
rb-set-max-take = Máximo de bolas por turno: { $count }
rb-enter-max-take = Ingresa el máximo de bolas por turno, de 1 a 5:
rb-option-changed-max-take = Máximo de bolas por turno establecido en { $count }.
rollingballs-desc-max-take = Número máximo de bolas que un jugador puede tomar en un turno. La partida no puede empezar si esto es menor que el mínimo (por defecto 3, rango 1-5).
rb-set-view-pipe-limit = Vistas previas nuevas del tubo por jugador: { $count }
rb-enter-view-pipe-limit = Ingresa las vistas previas nuevas del tubo por jugador, de 0 a 100; 0 desactiva las vistas previas:
rb-option-changed-view-pipe-limit = Vistas previas nuevas del tubo por jugador establecidas en { $count }.
rollingballs-desc-view-pipe-limit = Cuántas bolas próximas se pueden previsualizar del tubo. Usa 0 para desactivar las vistas previas (por defecto 5, rango 0-100).
rb-set-reshuffle-limit = Barajadas por jugador: { $count }
rb-enter-reshuffle-limit = Ingresa las barajadas por jugador, de 0 a 100; 0 desactiva el volver a barajar:
rb-option-changed-reshuffle-limit = Barajadas por jugador establecidas en { $count }.
rollingballs-desc-reshuffle-limit = Cuántas barajadas están disponibles antes de agotar el tubo (por defecto 3, rango 0-100).
rb-set-reshuffle-penalty = Penalización por barajar: { $points } puntos
rb-enter-reshuffle-penalty = Ingresa la penalización por barajar, de 0 a 5 puntos:
rb-option-changed-reshuffle-penalty = Penalización por barajar establecida en { $points } puntos.
rollingballs-desc-reshuffle-penalty = Penalización de puntuación aplicada cuando se usa una barajada. Esta opción solo aparece cuando hay barajadas disponibles (por defecto 1, rango 0-5).
rb-set-ball-packs = Conjuntos de bolas ({ $count } de { $total } seleccionados)
rb-option-changed-ball-packs = Se cambió la selección de conjuntos de bolas.
rollingballs-desc-ball-packs = Elige qué conjuntos temáticos de bolas se incluyen en el tubo. Debe quedar seleccionado al menos un conjunto.

# Motivos de deshabilitado contextuales y validación de configuración
rb-draw-resolving = Espera a que termine el robo de bolas actual de { $player } antes de iniciar otra acción del tubo.
rb-take-not-your-turn = No puedes tomar { $count } bolas ahora porque es el turno de { $player }.
rb-take-outside-range = Intentaste tomar { $count } bolas, pero esta partida permite de { $min } a { $max } por turno normal.
rb-not-enough-balls = Intentaste tomar { $count } bolas, pero solo quedan { $remaining } en el tubo.
rb-reshuffle-not-your-turn = No puedes volver a barajar ahora porque es el turno de { $player }.
rb-no-reshuffles-left = Ya usaste las { $limit } barajadas de esta partida.
rb-already-reshuffled = Ya volviste a barajar durante este turno. Toma bolas para terminar el turno.
rb-not-enough-balls-to-reshuffle = Volver a barajar necesita al menos { $required } bolas, pero solo quedan { $remaining }. Toma bolas en su lugar.
rb-no-views-left = El tubo cambió, y ya usaste las { $limit } vistas previas nuevas. Aún puedes reabrir una vista previa sin cambios antes de que el tubo avance.
rb-error-min-take-invalid = El mínimo para tomar es { $count }; debe estar entre { $min } y { $max }.
rb-error-max-take-invalid = El máximo para tomar es { $count }; debe estar entre { $min } y { $max }.
rb-error-take-range-conflict = El mínimo para tomar es { $min }, por encima del máximo de { $max }. Baja el mínimo o sube el máximo antes de empezar.
rb-error-view-limit-invalid = El límite de vistas previas es { $count }; debe estar entre { $min } y { $max }.
rb-error-reshuffle-limit-invalid = El límite de barajadas es { $count }; debe estar entre { $min } y { $max }.
rb-error-reshuffle-penalty-invalid = La penalización por barajar es { $points }; debe estar entre { $min } y { $max } puntos.
rb-error-no-ball-packs = Selecciona al menos un conjunto de bolas antes de empezar Bolas Rodantes.
rb-error-invalid-ball-packs = La selección contiene { $count } { $count ->
    [one] conjunto de bolas no disponible
   *[other] conjuntos de bolas no disponibles
}. Quita los conjuntos no disponibles antes de empezar.

# Conjuntos de bolas
rb-pack-all = Todos los conjuntos mezclados
rb-pack-international = Alrededor del Mundo
rb-pack-vietnam = Viaje por Vietnam

# Alrededor del Mundo: -5
rb-ball-paris-pickpocket = Pasaporte y billetera robados en el extranjero
rb-ball-lost-luggage-in-london = Visita médica de emergencia en el extranjero
rb-ball-tokyo-train-delay = Pierdes la última conexión internacional
rb-ball-sahara-sandstorm = Evacuación por clima severo
rb-ball-passport-lost-before-flight = Pasaporte perdido antes de la salida
# Alrededor del Mundo: -4
rb-ball-venice-flood = Una inundación cierra tu alojamiento
rb-ball-new-york-traffic = Cancelación de vuelo nocturno
rb-ball-amazon-mosquito-swarm = Equipaje esencial enviado al país equivocado
rb-ball-berlin-club-rejected = Reserva de hotel perdida al llegar
rb-ball-hotel-booking-vanished = Ruta de montaña cerrada por varios días
# Alrededor del Mundo: -3
rb-ball-spilled-coffee-in-rome = El teléfono se rompe durante un traslado
rb-ball-sydney-sunburn = El agotamiento por calor cancela una excursión
rb-ball-istanbul-bazaar-scam = Se cancela una reserva de tour prepagada
rb-ball-moscow-blizzard = Una tormenta de nieve retiene tu tren
rb-ball-dubai-heatwave = El vehículo alquilado se avería
# Alrededor del Mundo: -2
rb-ball-mexico-city-smog = La mala calidad del aire cambia el itinerario
rb-ball-cairo-camel-spit = Mareo en un viaje largo
rb-ball-athens-ruins-trip = Tobillo torcido en un recorrido a pie
rb-ball-rio-carnival-hangover = Te quedas dormido y pierdes el tour matutino
rb-ball-bali-belly = Malestar estomacal te cuesta una tarde
# Alrededor del Mundo: -1
rb-ball-swiss-alps-avalanche = Sendero escénico cerrado por seguridad
rb-ball-amsterdam-bicycle-crash = Llanta de bicicleta pinchada
rb-ball-bangkok-tuk-tuk-breakdown = El tuk-tuk se detiene en el tráfico
rb-ball-iceland-volcano-ash = Una alerta meteorológica retrasa el vuelo
rb-ball-cape-town-wind = Viento fuerte cierra el mirador
# Alrededor del Mundo: 0
rb-ball-neutral-passport = Un sello nuevo en el pasaporte
rb-ball-airport-layover = Una escala tranquila en el aeropuerto
rb-ball-hotel-lobby = Esperando en el vestíbulo del hotel
rb-ball-tourist-map = Desdoblando el mapa de la ciudad
rb-ball-souvenir-magnet = Eligiendo un imán de recuerdo
# Alrededor del Mundo: +1
rb-ball-free-museum-day = Entrada gratuita al museo
rb-ball-street-food-snack = Un excelente bocadillo callejero
rb-ball-post-card-home = Postal enviada a casa
rb-ball-friendly-local = Indicaciones útiles de un local
rb-ball-sunny-day = Clima perfecto para explorar
# Alrededor del Mundo: +2
rb-ball-eiffel-tower-view = El horizonte de París desde la Torre Eiffel
rb-ball-taj-mahal-sunrise = Amanecer en el Taj Mahal
rb-ball-great-wall-hike = Caminata en la Gran Muralla
rb-ball-machu-picchu-climb = Mañana en Machu Picchu
rb-ball-kyoto-cherry-blossoms = Cerezos en flor en Kioto
# Alrededor del Mundo: +3
rb-ball-colosseum-tour = Visita guiada al Coliseo
rb-ball-pyramids-exploration = Explorando el complejo de pirámides de Giza
rb-ball-santorini-sunset = Atardecer en Santorini
rb-ball-aurora-borealis = Aurora boreal sobre tu cabeza
rb-ball-safari-lion-sighting = Avistamiento responsable de fauna en safari
# Alrededor del Mundo: +4
rb-ball-bora-bora-villa = Estancia en la laguna de Bora Bora
rb-ball-maldives-scuba = Buceo en el arrecife de Maldivas
rb-ball-niagara-falls-boat = Paseo en bote por las Cataratas del Niágara
rb-ball-grand-canyon-heli = Vuelo panorámico sobre el Gran Cañón
rb-ball-serengeti-migration = La Gran Migración en el Serengeti
# Alrededor del Mundo: +5
rb-ball-first-class-upgrade = Mejora sorpresa a primera clase
rb-ball-lottery-in-macau = Ganas un pase de tren de un año
rb-ball-private-jet = Viaje único a una isla, una vez en la vida
rb-ball-royal-palace-invite = Visita privada a un museo fuera de horario
rb-ball-world-tour-ticket = Boleto de vuelta al mundo

# Viaje por Vietnam: -5
rb-ball-stolen-motorbike = Pasaporte y billetera robados durante el viaje
rb-ball-flooded-street-saigon = Una inundación obliga a una reubicación de emergencia
rb-ball-food-poisoning-bun-mam = Una emergencia médica interrumpe el viaje
rb-ball-fake-taxi-scam = Una avería de transporte causa un vuelo perdido
rb-ball-passport-lost-at-airport = Pasaporte perdido en el aeropuerto
# Viaje por Vietnam: -4
rb-ball-typhoon-in-central-vietnam = Evacuación por tifón en la costa central
rb-ball-lost-wallet-ben-thanh = Equipaje esencial perdido en tránsito
rb-ball-traffic-jam-hanoi = Cancelación del tren nocturno
rb-ball-pickpocketed-in-bui-vien = Teléfono robado en un distrito concurrido
rb-ball-mountain-road-landslide = Paso de montaña cerrado por un derrumbe
# Viaje por Vietnam: -3
rb-ball-spilled-pho = Cámara dañada por una lluvia repentina
rb-ball-overcharged-for-coffee = Confusión con la reserva del hotel
rb-ball-sunburn-in-mui-ne = Agotamiento por calor en Mui Ne
rb-ball-missed-train-to-sapa = Pierdes el tren nocturno a Lao Cai
rb-ball-loud-karaoke-next-door = Noche sin dormir antes de una salida temprana
# Viaje por Vietnam: -2
rb-ball-broken-flip-flop = Se rompe la correa de una sandalia en un recorrido a pie
rb-ball-sudden-downpour = Aguacero tropical repentino
rb-ball-dog-chased-you = Parada de autobús equivocada, lejos del hotel
rb-ball-bitten-by-mosquitoes = Una noche de picaduras de mosquito
rb-ball-out-of-gas = La motocicleta se queda sin combustible
# Viaje por Vietnam: -1
rb-ball-spicy-chili-bite = Un ají inesperadamente picante
rb-ball-delayed-flight = Breve retraso en un vuelo nacional
rb-ball-wifi-disconnected = Señal débil en las montañas
rb-ball-forgot-umbrella = Impermeable olvidado en el hotel
rb-ball-minor-scratch = Giro equivocado en el Casco Antiguo
# Viaje por Vietnam: 0
rb-ball-plastic-stool = Un asiento en un banquito de la acera
rb-ball-iced-tea-tra-da = Un vaso de tra da
rb-ball-waiting-for-green-light = Esperando en un semáforo rojo eterno
rb-ball-bamboo-hat = Probándote un non la
rb-ball-motorbike-helmet = Abrochándote el casco de la motocicleta
# Viaje por Vietnam: +1
rb-ball-tasty-banh-mi = Un banh mi crujiente para desayunar
rb-ball-free-sugar-cane-juice = Jugo de caña de azúcar fresco
rb-ball-friendly-street-vendor = Cálida bienvenida de un vendedor del mercado
rb-ball-cool-breeze = Brisa fresca después de la lluvia
rb-ball-found-10k-vnd = Un viaje en autobús local a buen precio
# Viaje por Vietnam: +2
rb-ball-delicious-pho-bowl = Un tazón fragante de pho
rb-ball-egg-coffee-in-hanoi = Café de huevo en Hanói
rb-ball-boat-ride-in-ninh-binh = Paseo en sampán por el complejo paisajístico de Trang An
rb-ball-lantern-festival-hoian = Noche de faroles en el casco antiguo de Hoi An
rb-ball-motorbike-road-trip = Paseo en bote por los huertos del delta del Mekong
# Viaje por Vietnam: +3
rb-ball-ha-long-bay-cruise = Crucero por la bahía de Ha Long y el archipiélago de Cat Ba
rb-ball-golden-bridge-bana-hills = El Puente Dorado sobre las colinas de Ba Na
rb-ball-phu-quoc-sunset = Atardecer en Phu Quoc
rb-ball-sapa-terraced-fields = Campos en terrazas alrededor de Sa Pa
rb-ball-phong-nha-cave-exploration = Recorrido por las cuevas de Phong Nha - Ke Bang
# Viaje por Vietnam: +4
rb-ball-tet-holiday-lucky-money = Reunión de Tet y dinero de la suerte
rb-ball-vip-ticket-to-concert = Amanecer en el circuito de Ha Giang
rb-ball-luxury-resort-stay = Visita de conservación comunitaria en Con Dao
rb-ball-business-class-flight = Litera panorámica en el Expreso de la Reunificación
rb-ball-won-lottery-vietlott = Noche de festival entre los monumentos de Hue
# Viaje por Vietnam: +5
rb-ball-billionaire-inheritance = Expedición a Son Doong
rb-ball-found-gold-treasure = Taller cultural privado con maestros artesanos
rb-ball-free-house-in-district-1 = Viaje en tren de un mes por Vietnam
rb-ball-national-hero-award = Invitado de honor en un festival de pueblo
rb-ball-ultimate-happiness = Viaje soñado de Ha Giang a Ca Mau
