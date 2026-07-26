# Mensajes del juego Era de los Héroes
# Un juego de cartas de construcción de civilizaciones para 2-6 jugadores

# Nombre del juego
game-name-ageofheroes = Era de los Héroes

# Tribus
ageofheroes-tribe-egyptians = Egipcios
ageofheroes-tribe-romans = Romanos
ageofheroes-tribe-greeks = Griegos
ageofheroes-tribe-babylonians = Babilonios
ageofheroes-tribe-celts = Celtas
ageofheroes-tribe-chinese = Chinos

# Recursos especiales (para monumentos)
ageofheroes-special-limestone = Piedra caliza
ageofheroes-special-concrete = Concreto
ageofheroes-special-marble = Mármol
ageofheroes-special-bricks = Ladrillos
ageofheroes-special-sandstone = Arenisca
ageofheroes-special-granite = Granito

# Recursos estándar
ageofheroes-resource-iron = Hierro
ageofheroes-resource-wood = Madera
ageofheroes-resource-grain = Grano
ageofheroes-resource-stone = Piedra
ageofheroes-resource-gold = Oro

# Eventos
ageofheroes-event-population-growth = Crecimiento Poblacional
ageofheroes-event-earthquake = Terremoto
ageofheroes-event-eruption = Erupción
ageofheroes-event-hunger = Hambruna
ageofheroes-event-barbarians = Bárbaros
ageofheroes-event-olympics = Juegos Olímpicos
ageofheroes-event-hero = Héroe
ageofheroes-event-fortune = Fortuna

# Edificios
ageofheroes-building-army = Ejército
ageofheroes-building-fortress = Fortaleza
ageofheroes-building-general = General
ageofheroes-building-road = Camino
ageofheroes-building-city = Ciudad

# Acciones
ageofheroes-action-tax-collection = Recaudación de Impuestos
ageofheroes-action-construction = Construcción
ageofheroes-action-war = Guerra
ageofheroes-action-do-nothing = No Hacer Nada
ageofheroes-play = Jugar
ageofheroes-play-card-label = Jugar { $card }
ageofheroes-card-count = { $count } { $card }
ageofheroes-player-tribe = { $player } ({ $tribe })
ageofheroes-player-tribe-direction = { $player } ({ $tribe }) - { $direction }

# Objetivos de guerra
ageofheroes-war-conquest = Conquista
ageofheroes-war-plunder = Saqueo
ageofheroes-war-destruction = Destrucción

# Opciones de la partida
ageofheroes-set-victory-cities = Ciudades para la victoria: { $cities }
ageofheroes-enter-victory-cities = Ingresa el número de ciudades para ganar (3-7)
ageofheroes-set-victory-monument = Monumento completado: { $progress }%
ageofheroes-set-max-hand = Tamaño máximo de mano: { $cards } cartas

# Anuncios de cambio de opciones
ageofheroes-option-changed-victory-cities = La victoria requiere { $cities } ciudades.
ageofheroes-desc-victory-cities = Cuántas ciudades debe controlar un bando para ganar Era de los Héroes (por defecto 5, rango 3-7).
ageofheroes-option-changed-victory-monument = Umbral de monumento completado establecido en { $progress }%.
ageofheroes-option-changed-max-hand = Tamaño máximo de mano establecido en { $cards } cartas.

# Fase de preparación inicial
ageofheroes-setup-start = Eres el líder de la tribu { $tribe }. Tu recurso especial de monumento es { $special }. Lanza los dados para determinar el orden de turnos.
ageofheroes-setup-viewer = Los jugadores están lanzando los dados para determinar el orden de turnos.
ageofheroes-roll-dice = Lanzar los dados
ageofheroes-war-roll-dice = Lanzar los dados
ageofheroes-dice-result = Sacaste { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = { $player } sacó { $total }.
ageofheroes-dice-tie = Varios jugadores empataron con { $total }. Lanzando de nuevo...
ageofheroes-first-player = { $player } sacó el más alto con { $total } y va primero.
ageofheroes-first-player-you = Con { $total } puntos, vas primero.
ageofheroes-whose-turn-setup = Fase de preparación inicial. Esperando a que { $players } lancen para el orden de turnos.
ageofheroes-whose-turn-setup-resolving = Fase de preparación inicial. Todos los dados están listos; se está resolviendo el orden de turnos.
ageofheroes-whose-turn-prepare = Fase de preparación. Se están resolviendo eventos y desastres.
ageofheroes-whose-turn-fair = Fase de mercado. { $players } todavía pueden intercambiar.
ageofheroes-whose-turn-fair-resolving = Fase de mercado. Se están resolviendo los intercambios.
ageofheroes-whose-turn-road = Fase de permiso de camino. { $responder } debe responder a la solicitud de { $requester }.
ageofheroes-whose-turn-olympics = Guerra declarada. { $defender } debe decidir si usa los Juegos Olímpicos contra { $attacker }.
ageofheroes-whose-turn-war-attack = Preparación de guerra. { $attacker } está eligiendo sus fuerzas contra { $defender }.
ageofheroes-whose-turn-war-defense = Preparación de guerra. { $defender } está eligiendo sus fuerzas defensoras contra { $attacker }.
ageofheroes-whose-turn-war-roll = Fase de batalla. Esperando a que { $players } lancen los dados.
ageofheroes-whose-turn-game-over = La partida ha terminado.

# Fase de preparación
ageofheroes-prepare-start = Los jugadores deben jugar cartas de evento y descartar desastres.
ageofheroes-prepare-your-turn = Tienes { $count } { $count ->
    [one] carta
    *[other] cartas
} para jugar o descartar.
ageofheroes-prepare-done = Fase de preparación completa.

# Eventos jugados/descartados
ageofheroes-population-growth = { $player } juega Crecimiento Poblacional y construye una nueva ciudad.
ageofheroes-population-growth-you = Juegas Crecimiento Poblacional y construyes una nueva ciudad.
ageofheroes-discard-card = { $player } descarta { $card }.
ageofheroes-discard-card-you = Descartas { $card }.
ageofheroes-earthquake = Un terremoto golpea a la tribu de { $player }; sus ejércitos entran en recuperación.
ageofheroes-earthquake-you = Un terremoto golpea a tu tribu; tus ejércitos entran en recuperación.
ageofheroes-eruption = Una erupción destruye una de las ciudades de { $player }.
ageofheroes-eruption-you = Una erupción destruye una de tus ciudades.

# Efectos de desastre
ageofheroes-hunger-strikes = Golpea la hambruna.
ageofheroes-lose-card-hunger = Pierdes { $card }.
ageofheroes-barbarians-pillage = Los bárbaros atacan los recursos de { $player }.
ageofheroes-barbarians-attack = Los bárbaros atacan los recursos de { $player }.
ageofheroes-barbarians-attack-you = Los bárbaros atacan tus recursos.
ageofheroes-lose-card-barbarians = Pierdes { $card }.
ageofheroes-block-with-card = { $player } bloquea el desastre usando { $card }.
ageofheroes-block-with-card-you = Bloqueas el desastre usando { $card }.

# Cartas de desastre dirigidas (Terremoto/Erupción)
ageofheroes-select-disaster-target = Selecciona un objetivo para { $card }.
ageofheroes-no-targets = No hay objetivos válidos disponibles.
ageofheroes-earthquake-strikes-you = { $attacker } juega Terremoto contra ti. Tus ejércitos quedan inhabilitados.
ageofheroes-earthquake-strikes = { $attacker } juega Terremoto contra { $player }.
ageofheroes-armies-disabled = { $count } { $count ->
    [one] ejército queda inhabilitado
    *[other] ejércitos quedan inhabilitados
} por un turno.
ageofheroes-eruption-strikes-you = { $attacker } juega Erupción contra ti. Una de tus ciudades es destruida.
ageofheroes-eruption-strikes = { $attacker } juega Erupción contra { $player }.
ageofheroes-city-destroyed = Una ciudad es destruida por la erupción.

# Fase de mercado
ageofheroes-fair-start = Amanece en el mercado.
ageofheroes-fair-draw-base = Robas { $count } { $count ->
    [one] carta
    *[other] cartas
}.
ageofheroes-fair-draw-roads = Robas { $count } { $count ->
    [one] carta adicional
    *[other] cartas adicionales
} gracias a tu red de caminos.
ageofheroes-fair-draw-other = { $player } roba { $count } { $count ->
    [one] carta
    *[other] cartas
}.

# Intercambio/Subasta
ageofheroes-auction-start = Comienza la subasta.
ageofheroes-offer-trade = Ofrecer intercambio
ageofheroes-offer-made = { $player } ofrece { $card } por { $wanted }.
ageofheroes-offer-made-you = Ofreces { $card } por { $wanted }.
ageofheroes-trade-accepted = { $player } acepta la oferta de { $other } e intercambia { $give } por { $receive }.
ageofheroes-trade-accepted-you = Aceptas la oferta de { $other } y recibes { $receive }.
ageofheroes-trade-cancelled = { $player } retira su oferta de { $card }.
ageofheroes-trade-cancelled-you = Retiras tu oferta de { $card }.
ageofheroes-stop-trading = Dejar de comerciar
ageofheroes-select-request = Estás ofreciendo { $card }. ¿Qué quieres a cambio?
ageofheroes-cancel = Cancelar
ageofheroes-left-auction = { $player } se retira.
ageofheroes-left-auction-you = Te retiras del mercado.
ageofheroes-already-left-auction = Ya te retiraste del mercado.
ageofheroes-any-card = Cualquier carta
ageofheroes-cannot-trade-own-special = No puedes intercambiar tu propio recurso especial de monumento.
ageofheroes-resource-not-in-game = Este recurso especial no se está usando en esta partida.

# Fase principal de juego
ageofheroes-play-start = Fase de juego.
ageofheroes-day = Día { $day }
ageofheroes-draw-card = { $player } roba una carta del mazo.
ageofheroes-draw-card-you = Robas { $card } del mazo.
ageofheroes-draw-card-brief = { $player } roba.
ageofheroes-draw-card-you-brief = Robas: { $card }.
ageofheroes-your-action = ¿Qué quieres hacer?
ageofheroes-your-action-brief = ¿Acción?

# Recaudación de Impuestos
ageofheroes-tax-collection = { $player } elige Recaudación de Impuestos: { $cities } { $cities ->
    [one] ciudad
    *[other] ciudades
} recauda { $cards } { $cards ->
    [one] carta
    *[other] cartas
}.
ageofheroes-tax-collection-you = Eliges Recaudación de Impuestos: { $cities } { $cities ->
    [one] ciudad
    *[other] ciudades
} recauda { $cards } { $cards ->
    [one] carta
    *[other] cartas
}.
ageofheroes-tax-collection-brief = { $player } impuestos: { $cards } de { $cities }.
ageofheroes-tax-collection-you-brief = Impuestos: { $cards } de { $cities }.
ageofheroes-tax-no-city = Recaudación de Impuestos: No tienes ciudades sobrevivientes. Descarta una carta para robar una nueva.
ageofheroes-tax-no-city-done = { $player } elige Recaudación de Impuestos pero no tiene ciudades, así que intercambia una carta.
ageofheroes-tax-no-city-done-you = Recaudación de Impuestos: Intercambiaste { $card } por una carta nueva.

# Construcción
ageofheroes-construction-menu = ¿Qué quieres construir?
ageofheroes-construction-done = { $player } construyó { $building }.
ageofheroes-construction-done-you = Construiste { $building }.
ageofheroes-build-cost-resource = { $count ->
    [one] { $resource }
    *[other] { $count }x { $resource }
}
ageofheroes-build-menu-label = { $building } ({ $cost })
ageofheroes-construction-stop = Dejar de construir
ageofheroes-construction-stopped = Decidiste dejar de construir.
ageofheroes-road-select-neighbor = Selecciona a qué vecino construirle un camino.
ageofheroes-direction-left = A tu izquierda
ageofheroes-direction-right = A tu derecha
ageofheroes-road-request-sent = Solicitud de camino enviada. Esperando la aprobación del vecino.
ageofheroes-road-request-received = { $requester } solicita permiso para construir un camino hacia tu tribu.
ageofheroes-road-request-denied-you = Rechazaste la solicitud de camino.
ageofheroes-road-request-denied = { $denier } rechazó tu solicitud de camino.
ageofheroes-road-built = { $tribe1 } y { $tribe2 } ahora están conectados por camino.
ageofheroes-road-no-target = No hay tribus vecinas disponibles para construir un camino.
ageofheroes-approve = Aprobar
ageofheroes-deny = Rechazar
ageofheroes-supply-exhausted = No hay más { $building } disponibles para construir.

# No hacer nada
ageofheroes-do-nothing = { $player } pasa.
ageofheroes-do-nothing-you = Pasas...
ageofheroes-do-nothing-brief = { $player } pasa.
ageofheroes-do-nothing-you-brief = Pasas.
ageofheroes-confirm-do-nothing = Pasar omite tu acción por este turno. Presiona No Hacer Nada de nuevo para confirmar.

# Guerra
ageofheroes-war-declare = { $attacker } declara la guerra a { $defender }. Objetivo: { $goal }.
ageofheroes-war-prepare = Selecciona tus ejércitos para { $action }.
ageofheroes-war-no-army = No tienes ejércitos ni cartas de héroe disponibles.
ageofheroes-war-no-tribe = No tienes una tribu en esta batalla.
ageofheroes-war-no-targets = No hay objetivos válidos para la guerra.
ageofheroes-war-no-valid-goal = No hay objetivos de guerra válidos contra este objetivo.
ageofheroes-war-invalid-forces = Esas fuerzas ya no son válidas. Revisa tus ejércitos, generales y cartas de Héroe disponibles.
ageofheroes-war-select-target = Selecciona a qué jugador atacar.
ageofheroes-war-select-goal = Selecciona tu objetivo de guerra.
ageofheroes-war-prepare-attack = Selecciona tus fuerzas atacantes.
ageofheroes-war-prepare-defense = { $attacker } te está atacando; selecciona tus fuerzas defensoras.
ageofheroes-war-force-add-armies = Añadir un ejército. Ejércitos comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-armies = Quitar un ejército. Ejércitos comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-generals = Añadir un general. Generales comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-generals = Quitar un general. Generales comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-hero-armies = Añadir un Héroe como ejército. Ejércitos Héroe comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-hero-armies = Quitar un ejército Héroe. Ejércitos Héroe comprometidos: { $current } de { $max }.
ageofheroes-war-force-add-hero-generals = Añadir un Héroe como general. Generales Héroe comprometidos: { $current } de { $max }.
ageofheroes-war-force-remove-hero-generals = Quitar un general Héroe. Generales Héroe comprometidos: { $current } de { $max }.
ageofheroes-war-force-unit-armies = ejércitos
ageofheroes-war-force-unit-generals = generales
ageofheroes-war-force-unit-hero-armies = ejércitos Héroe
ageofheroes-war-force-unit-hero-generals = generales Héroe
ageofheroes-war-force-max = Ya está en el máximo: { $unit } ({ $max }).
ageofheroes-war-force-min = Ninguno comprometido: { $unit }.
ageofheroes-war-force-updated = Fuerzas comprometidas: { $armies } ejércitos, { $generals } generales, { $hero_armies } ejércitos Héroe, { $hero_generals } generales Héroe.
ageofheroes-war-attack = Atacar...
ageofheroes-war-defend = Defender...
ageofheroes-war-clear-forces = Borrar fuerzas
ageofheroes-war-prepared = Tus fuerzas: { $armies } { $armies ->
    [one] ejército
    *[other] ejércitos
}{ $generals ->
    [0] {""}
    [one] {" y 1 general"}
    *[other] { " y " }{ $generals } generales
}{ $heroes ->
    [0] {""}
    [one] {" y 1 héroe"}
    *[other] { " y " }{ $heroes } héroes
}.
ageofheroes-war-roll-you = Sacas { $roll }.
ageofheroes-war-roll-other = { $player } saca { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] +1 por fortaleza = { $total } en total
        *[other] +{ $fortress } por fortalezas = { $total } en total
    }
    *[other] { $fortress ->
        [0] +{ $general } por general = { $total } en total
        [1] +{ $general } por general, +1 por fortaleza = { $total } en total
        *[other] +{ $general } por general, +{ $fortress } por fortalezas = { $total } en total
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] { $player }: +1 por fortaleza = { $total } en total
        *[other] { $player }: +{ $fortress } por fortalezas = { $total } en total
    }
    *[other] { $fortress ->
        [0] { $player }: +{ $general } por general = { $total } en total
        [1] { $player }: +{ $general } por general, +1 por fortaleza = { $total } en total
        *[other] { $player }: +{ $general } por general, +{ $fortress } por fortalezas = { $total } en total
    }
}
ageofheroes-war-bonuses-you-brief = Bono +{ $bonus } = { $total }.
ageofheroes-war-bonuses-other-brief = { $player } bono +{ $bonus } = { $total }.

# Batalla
ageofheroes-battle-start = Comienza la batalla. Los { $att_armies } { $att_armies ->
    [one] ejército
    *[other] ejércitos
} de { $attacker } contra los { $def_armies } { $def_armies ->
    [one] ejército
    *[other] ejércitos
} de { $defender }.
ageofheroes-battle-start-brief = Batalla: { $attacker } { $att_armies } contra { $defender } { $def_armies }.
ageofheroes-dice-roll-detailed = { $name } saca { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } por general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 por fortaleza" }
    *[other] { " + { $fortress } por fortalezas" }
} = { $total }.
ageofheroes-dice-roll-detailed-you = Sacas { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } por general" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 por fortaleza" }
    *[other] { " + { $fortress } por fortalezas" }
} = { $total }.
ageofheroes-round-attacker-wins = { $attacker } gana la ronda ({ $att_total } contra { $def_total }). { $defender } pierde un ejército.
ageofheroes-round-defender-wins = { $defender } se defiende con éxito ({ $def_total } contra { $att_total }). { $attacker } pierde un ejército.
ageofheroes-round-draw = Ambos bandos empatan en { $total }. No se pierden ejércitos.
ageofheroes-round-attacker-wins-brief = { $attacker } { $att_total } supera a { $defender } { $def_total }. { $defender } -1 ejército.
ageofheroes-round-defender-wins-brief = { $defender } { $def_total } supera a { $attacker } { $att_total }. { $attacker } -1 ejército.
ageofheroes-round-draw-brief = Empate { $total }. Sin pérdidas.
ageofheroes-you-win-battle-as-attacker = Derrotas a { $defender }.
ageofheroes-you-lose-battle-as-defender = { $attacker } te derrota.
ageofheroes-battle-victory-attacker = { $attacker } derrota a { $defender }.
ageofheroes-you-lose-battle-as-attacker = { $defender } se defiende con éxito contra ti.
ageofheroes-you-win-battle-as-defender = Te defiendes con éxito contra { $attacker }.
ageofheroes-battle-victory-defender = { $defender } se defiende con éxito contra { $attacker }.
ageofheroes-you-draw-battle = Tú y { $opponent } pierden todas las fuerzas comprometidas en la batalla.
ageofheroes-battle-mutual-defeat = Tanto { $attacker } como { $defender } pierden todas las fuerzas comprometidas en la batalla.
ageofheroes-general-bonus = +{ $count } por { $count ->
    [one] general
    *[other] generales
}
ageofheroes-fortress-bonus = +{ $count } por defensa de fortaleza
ageofheroes-battle-winner = { $winner } gana la batalla.
ageofheroes-battle-draw = La batalla termina en empate...
ageofheroes-battle-continue = Continuar la batalla.
ageofheroes-battle-end = La batalla ha terminado.

# Resultados de guerra
ageofheroes-conquest-success = { $attacker } conquista { $count } { $count ->
    [one] ciudad
    *[other] ciudades
} de { $defender }.
ageofheroes-plunder-success = { $attacker } saquea { $count } { $count ->
    [one] carta
    *[other] cartas
} de { $defender }.
ageofheroes-destruction-success = { $attacker } destruye { $count } { $count ->
    [one] recurso
    *[other] recursos
} de monumento de { $defender }.
ageofheroes-conquest-success-brief = { $attacker } toma { $count } { $count ->
    [one] ciudad
    *[other] ciudades
} de { $defender }.
ageofheroes-plunder-success-brief = { $attacker } toma { $count } { $count ->
    [one] carta
    *[other] cartas
} de { $defender }.
ageofheroes-destruction-success-brief = { $attacker } destruye { $count } { $count ->
    [one] recurso de monumento
    *[other] recursos de monumento
} de { $defender }.
ageofheroes-army-losses = { $player } pierde { $count } { $count ->
    [one] ejército
    *[other] ejércitos
}.
ageofheroes-army-losses-you = Pierdes { $count } { $count ->
    [one] ejército
    *[other] ejércitos
}.

# Regreso del ejército
ageofheroes-army-return-road = Tus tropas regresan de inmediato por camino.
ageofheroes-army-return-delayed = { $count } { $count ->
    [one] unidad regresa
    *[other] unidades regresan
} al final de tu próximo turno.
ageofheroes-army-returned = Las tropas de { $player } han regresado de la guerra.
ageofheroes-army-returned-you = Tus tropas han regresado de la guerra.
ageofheroes-army-recover = Los ejércitos de { $player } se recuperan del terremoto.
ageofheroes-army-recover-you = Tus ejércitos se recuperan del terremoto.

# Juegos Olímpicos
ageofheroes-you-cancel-war-with-olympics = Juegas Juegos Olímpicos, cancelando la guerra declarada.
ageofheroes-player-cancels-war-with-olympics = { $player } juega Juegos Olímpicos, cancelando la guerra declarada.
ageofheroes-olympics-prompt = { $attacker } ha declarado la guerra. Tienes Juegos Olímpicos, ¿lo usas para cancelarla?
ageofheroes-yes = Sí
ageofheroes-no = No

# Progreso del monumento
ageofheroes-monument-progress = El monumento de { $player } está { $count }/5 completo.
ageofheroes-monument-progress-you = Tu monumento está { $count }/5 completo.

# Gestión de la mano
ageofheroes-discard-excess = Tienes más de { $max } cartas. Descarta { $count } { $count ->
    [one] carta
    *[other] cartas
}.
ageofheroes-discard-excess-other = { $player } debe descartar cartas sobrantes.
ageofheroes-discard-more = Descarta { $count } { $count ->
    [one] carta más
    *[other] cartas más
}.

# Victoria
ageofheroes-victory-cities = ¡{ $player } ha construido { $cities } ciudades! Imperio de Ciudades.
ageofheroes-victory-cities-you = ¡Has construido { $cities } ciudades! Imperio de Ciudades.
ageofheroes-victory-monument = ¡{ $player } ha completado su monumento! Portadores de la Gran Cultura.
ageofheroes-victory-monument-you = ¡Has completado tu monumento! Portadores de la Gran Cultura.
ageofheroes-victory-last-standing = ¡{ $player } es la última tribu en pie! El Más Persistente.
ageofheroes-victory-last-standing-you = ¡Eres la última tribu en pie! El Más Persistente.
ageofheroes-game-over = Fin de la Partida.
ageofheroes-final-winner = Ganador: { $player }
ageofheroes-final-days = Días jugados: { $days }

# Eliminación
ageofheroes-eliminated = { $player } ha sido eliminado.
ageofheroes-eliminated-you = Has sido eliminado.

# Mano
ageofheroes-check-hand = Ver mano
ageofheroes-hand-empty = No tienes cartas.
ageofheroes-initial-hand = Tu mano inicial ({ $count } { $count ->
    [one] carta
    *[other] cartas
}): { $cards }
ageofheroes-hand-contents = Tu mano ({ $count } { $count ->
    [one] carta
    *[other] cartas
}): { $cards }

# Estado
ageofheroes-check-status = Ver estado
ageofheroes-check-status-detailed = Estado detallado
ageofheroes-status = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] ciudad
    *[other] ciudades
}, { $armies } { $armies ->
    [one] ejército
    *[other] ejércitos
}, monumento { $monument }/5
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-cities = Ciudades: { $count }
ageofheroes-status-armies = Ejércitos: { $count }
ageofheroes-status-generals = Generales: { $count }
ageofheroes-status-fortresses = Fortalezas: { $count }
ageofheroes-status-monument = Monumento: { $count }/5
ageofheroes-status-roads = Caminos: { $left }{ $right }
ageofheroes-status-road-left = izquierda
ageofheroes-status-road-right = derecha
ageofheroes-status-none = ninguno
ageofheroes-status-earthquake-armies = Ejércitos en recuperación: { $count }
ageofheroes-status-returning-armies = Ejércitos regresando: { $count }
ageofheroes-status-returning-generals = Generales regresando: { $count }
ageofheroes-status-detailed-line = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] ciudad
    *[other] ciudades
}, { $armies } { $armies ->
    [one] ejército
    *[other] ejércitos
}, { $generals } { $generals ->
    [one] general
    *[other] generales
}, { $fortresses } { $fortresses ->
    [one] fortaleza
    *[other] fortalezas
}, monumento { $monument }/5, caminos: { $roads }{ $details }
ageofheroes-status-detail-recovering-armies = { $count } { $count ->
    [one] ejército recuperándose
    *[other] ejércitos recuperándose
}
ageofheroes-status-detail-returning-armies = { $count } { $count ->
    [one] ejército regresando
    *[other] ejércitos regresando
}
ageofheroes-status-detail-returning-generals = { $count } { $count ->
    [one] general regresando
    *[other] generales regresando
}

# Información del mazo
ageofheroes-deck-empty = No quedan más cartas de { $card } en el mazo.
ageofheroes-deck-count = Cartas restantes: { $count }
ageofheroes-deck-reshuffled = El descarte se volvió a barajar en el mazo.

# Rendirse
ageofheroes-give-up-confirm = ¿Seguro que quieres rendirte?
ageofheroes-gave-up = ¡{ $player } se rindió!
ageofheroes-gave-up-you = ¡Te rendiste!

# Carta de héroe
ageofheroes-hero-use = ¿Usar como ejército o general?
ageofheroes-hero-army = Ejército
ageofheroes-hero-general = General

# Carta de fortuna
ageofheroes-you-use-fortune = Usas Fortuna para volver a lanzar el dado de batalla.
ageofheroes-player-uses-fortune = { $player } usa Fortuna para volver a lanzar el dado de batalla.
ageofheroes-fortune-prompt = Perdiste la tirada. ¿Usar Fortuna para volver a lanzar?

# Motivos de acción deshabilitada
ageofheroes-not-your-turn = No es tu turno.
ageofheroes-game-not-started = La partida aún no ha comenzado.
ageofheroes-wrong-phase = Esta acción no está disponible en la fase actual.
ageofheroes-invalid-player = Esta acción no está disponible para ti.
ageofheroes-not-in-game = No estás en esta partida.
ageofheroes-not-in-war = No estás involucrado en esta guerra.
ageofheroes-already-rolled = Ya lanzaste los dados.
ageofheroes-invalid-card-index = Esa carta ya no está disponible.
ageofheroes-no-card-selected = Selecciona una carta primero.
ageofheroes-no-cards-to-discard = No tienes cartas para descartar.
ageofheroes-disaster-too-early = Las cartas de desastre solo se pueden jugar a partir del día 2.
ageofheroes-no-resources = No tienes los recursos necesarios.
ageofheroes-cannot-accept-own-offer = No puedes aceptar tu propia oferta de intercambio.
ageofheroes-offerer-unavailable = Esa oferta de intercambio ya no está disponible.
ageofheroes-offered-card-unavailable = La carta ofrecida ya no está disponible.
ageofheroes-trade-card-type-mismatch = Tu carta seleccionada no coincide con el tipo de carta solicitado.
ageofheroes-trade-card-subtype-mismatch = Tu carta seleccionada no coincide con la carta solicitada.
ageofheroes-trade-offer-label = { $player }: { $offered } por { $wanted }

# Costos de construcción (para mostrar)
ageofheroes-cost-army = 2 Grano, Hierro
ageofheroes-cost-fortress = Hierro, Madera, Piedra
ageofheroes-cost-general = Hierro, Oro
ageofheroes-cost-road = 2 Piedra
ageofheroes-cost-city = 2 Madera, Piedra
