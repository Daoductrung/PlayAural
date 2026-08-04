game-name-pirates = Piratas de los Mares Perdidos

# Configuración y flujo de ronda
pirates-welcome = Bienvenido a Piratas de los Mares Perdidos. Navega la ruta de cuarenta espacios, recupera las gemas dispersas y supera en maniobras a las tripulaciones rivales.
pirates-welcome-brief = Bienvenido a Piratas de los Mares Perdidos.
pirates-oceans = Tu travesía cruza { $oceans }.
pirates-gems-placed = Las { $total } gemas fueron escondidas a lo largo de la ruta. El cargamento de mayor valor gana después de recuperar la última gema.
pirates-gems-placed-brief = { $total } gemas están escondidas a lo largo de la ruta.
pirates-golden-moon = La Luna Dorada se alza en la ronda { $round }. Toda ganancia de XP se triplica esta ronda.
pirates-golden-moon-brief = Luna Dorada: XP triple en la ronda { $round }.
pirates-turn-you = Tu turno en la ronda { $round }. Estás en la posición { $position } en { $ocean }.
pirates-turn-you-brief = Tu turno. Posición { $position }.
pirates-turn = Turno de { $player } en la ronda { $round }, en la posición { $position } en { $ocean }.
pirates-turn-brief = Turno de { $player }.

# Movimiento e información del mapa
pirates-move-left = Navegar un espacio a la izquierda
pirates-move-right = Navegar un espacio a la derecha
pirates-move-2-left = Navegar dos espacios a la izquierda
pirates-move-2-right = Navegar dos espacios a la derecha
pirates-move-3-left = Navegar tres espacios a la izquierda
pirates-move-3-right = Navegar tres espacios a la derecha
pirates-move-you = Navegas { $tiles } { $tiles ->
    [one] espacio
   *[other] espacios
} hacia la { $direction } hasta la posición { $position } en { $ocean }.
pirates-move-you-brief = Navegas hasta la posición { $position }.
pirates-move = { $player } navega { $tiles } { $tiles ->
    [one] espacio
   *[other] espacios
} hacia la { $direction } hasta la posición { $position } en { $ocean }.
pirates-move-brief = { $player } navega hasta la posición { $position }.
pirates-map-edge = No puedes navegar más lejos en esa dirección; la posición { $position } es el borde de la ruta. Elige otra acción.
pirates-dir-left = izquierda
pirates-dir-right = derecha
pirates-your-position = Estás en la posición { $position }, sector { $sector }, en { $ocean }.
pirates-check-position = Ver posición
pirates-check-moon = Ver Luna Dorada
pirates-moon-active = La Luna Dorada está activa en la ronda { $round }. La XP se triplica. Las tripulaciones han recuperado { $collected } de { $total } gemas, quedan { $remaining }.
pirates-moon-inactive = La Luna Dorada no está activa en la ronda { $round }. Regresa en { $rounds } { $rounds ->
    [one] ronda
   *[other] rondas
}. Las tripulaciones han recuperado { $collected } de { $total } gemas, quedan { $remaining }.

# Estado y resultados
pirates-check-status = Ver estado de la tripulación
pirates-check-status-detailed = Estado detallado de la tripulación
pirates-status-line = { $player }: nivel { $level}; { $xp } de XP total, { $progress } de { $needed } XP hacia el siguiente nivel; { $points }; { $gem_count } { $gem_count ->
    [one] gema
   *[other] gemas
}{ $detail ->
    [yes] ; posición { $position } en { $ocean }; cargamento: { $gems }; efectos activos: { $skills }
   *[no] { "" }
}.
pirates-end-score-line = { $rank }. { $player}: { $points }, nivel { $level }
pirates-all-gems-collected = Se recuperó la última gema. Las tripulaciones comparan su cargamento.
pirates-all-gems-collected-brief = Última gema recuperada.
pirates-you-win = Ganas con { $score } puntos.
pirates-you-win-brief = Ganas: { $score } puntos.
pirates-winner = { $player } gana con { $score } puntos.
pirates-winner-brief = { $player } gana: { $score } puntos.
pirates-you-tie = Empatas en primer lugar con { $players } con { $score } puntos.
pirates-you-tie-brief = Empatas en primer lugar con { $score }.
pirates-players-tie = { $players } empatan en primer lugar con { $score } puntos.
pirates-players-tie-brief = { $players } empatan con { $score }.

# Gemas y XP
pirates-gem-found-you = Recuperas { $gem }, con un valor de { $value } { $value ->
    [one] punto
   *[other] puntos
}. Tu cargamento ahora vale { $score } puntos; quedan { $remaining } gemas en el mar.
pirates-gem-found-you-brief = Recuperas { $gem }. Puntuación: { $score }.
pirates-gem-found = { $player } recupera { $gem }, con un valor de { $value } { $value ->
    [one] punto
   *[other] puntos
}. Su cargamento ahora vale { $score } puntos; quedan { $remaining } gemas en el mar.
pirates-gem-found-brief = { $player } recupera { $gem }.
pirates-xp-gained-you = Ganas { $xp } XP por { $reason ->
    [gem] recuperar una gema
    [attack] acertar un disparo de cañón
    [defense] repeler un ataque de cañón
   *[other] completar una acción
}. Ahora tienes { $total } XP en total.
pirates-xp-gained-you-brief = Ganas { $xp } XP. Total: { $total }.
pirates-xp-gained-player = { $player } gana { $xp } XP por { $reason ->
    [gem] recuperar una gema
    [attack] acertar un disparo de cañón
    [defense] repeler un ataque de cañón
   *[other] completar una acción
}, alcanzando { $total } XP en total.
pirates-xp-gained-player-brief = { $player } gana { $xp } XP.
pirates-level-up-you = Alcanzas el nivel { $level }.
pirates-level-up-you-brief = Alcanzas el nivel { $level }.
pirates-level-up = { $player } alcanza el nivel { $level }.
pirates-level-up-brief = { $player } alcanza el nivel { $level }.
pirates-level-up-multiple-you = Ganas { $levels } niveles y alcanzas el nivel { $level }.
pirates-level-up-multiple-you-brief = Alcanzas el nivel { $level }.
pirates-level-up-multiple = { $player } gana { $levels } niveles y alcanza el nivel { $level }.
pirates-level-up-multiple-brief = { $player } alcanza el nivel { $level }.
pirates-skills-unlocked-you = En el nivel { $level }, desbloqueas { $skills }.
pirates-skills-unlocked-you-brief = Desbloqueas { $skills }.
pirates-skills-unlocked = En el nivel { $level }, { $player } desbloquea { $skills }.
pirates-skills-unlocked-brief = { $player } desbloquea { $skills }.

# Combate con cañones
pirates-cannonball = Disparar bala de cañón
pirates-select-cannon-target = Elige un barco dentro del alcance del cañón
pirates-target-option = { $player }, a { $distance } { $distance ->
    [one] espacio
   *[other] espacios
}, { $score } puntos, cargando { $gems } { $gems ->
    [one] gema
   *[other] gemas
}
pirates-target-unavailable = Barco no disponible
pirates-no-targets = Ningún barco rival está dentro de tu alcance actual de cañón de { $range } espacios. Elige moverte u otra habilidad disponible.
pirates-target-out-of-range = { $target } ya no está dentro de tu alcance de cañón de { $range } espacios desde la posición { $position }. Elige otra acción.
pirates-attack-you-fire = Disparas una bala de cañón contra { $target }.
pirates-attack-you-fire-brief = Disparas contra { $target }.
pirates-attack-incoming = { $attacker } dispara una bala de cañón contra ti.
pirates-attack-incoming-brief = { $attacker } dispara contra ti.
pirates-attack-fired = { $attacker } dispara una bala de cañón contra { $defender }.
pirates-attack-fired-brief = { $attacker } dispara contra { $defender }.
pirates-combat-rolls-you = Tu dado de ataque es { $attack_die}, más { $attack_bonus}, para { $attack_total}. El dado de defensa de { $defender } es { $defense_die}, más { $defense_bonus}, para { $defense_total}.
pirates-combat-rolls-you-brief = Ataque { $attack_total}; defensa { $defense_total}.
pirates-combat-rolls-defender = { $attacker } ataca con { $attack_die}, más { $attack_bonus}, para { $attack_total}. Tu dado de defensa es { $defense_die}, más { $defense_bonus}, para { $defense_total}.
pirates-combat-rolls-defender-brief = Ataque { $attack_total}; tu defensa { $defense_total}.
pirates-combat-rolls-observer = { $attacker } ataca con { $attack_die}, más { $attack_bonus}, para { $attack_total}. { $defender } defiende con { $defense_die}, más { $defense_bonus}, para { $defense_total}.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total}; { $defender } { $defense_total}.
pirates-attack-hit-you = Impacto directo. Tu { $attack_total } supera el { $defense_total } de { $target }; elige una acción de abordaje disponible.
pirates-attack-hit-you-brief = Le pegas a { $target }, { $attack_total } contra { $defense_total}.
pirates-attack-hit-them = { $attacker } te pega, { $attack_total } contra { $defense_total}, y ahora puede abordar tu barco.
pirates-attack-hit-them-brief = { $attacker } te pega, { $attack_total } contra { $defense_total}.
pirates-attack-hit = { $attacker } le pega a { $defender }, { $attack_total } contra { $defense_total}, y puede abordar.
pirates-attack-hit-brief = { $attacker } le pega a { $defender }.
pirates-attack-hit-no-boarding-you = Impacto directo. Tu { $attack_total } supera el { $defense_total } de { $target }. Este impacto de Acorazado otorga XP pero sin acción de abordaje.
pirates-attack-hit-no-boarding-you-brief = Le pegas a { $target }, { $attack_total } contra { $defense_total}; sin abordaje.
pirates-attack-hit-no-boarding-them = { $attacker } te pega, { $attack_total } contra { $defense_total}. Los impactos de Acorazado no otorgan acciones de abordaje.
pirates-attack-hit-no-boarding-them-brief = { $attacker } te pega; sin abordaje.
pirates-attack-hit-no-boarding = { $attacker } le pega a { $defender }, { $attack_total } contra { $defense_total}. Este impacto de Acorazado no otorga acción de abordaje.
pirates-attack-hit-no-boarding-brief = { $attacker } le pega a { $defender}; sin abordaje.
pirates-attack-miss-you = Tu total de ataque de { $attack_total } no supera el total de defensa de { $target } de { $defense_total}. Tu turno termina.
pirates-attack-miss-you-brief = Fallas contra { $target }, { $attack_total } contra { $defense_total}.
pirates-attack-miss-them = Repeles a { $attacker } con un total de defensa de { $defense_total } contra { $attack_total}.
pirates-attack-miss-them-brief = Repeles a { $attacker }, { $defense_total } contra { $attack_total}.
pirates-attack-miss = { $defender } repele a { $attacker }, { $defense_total } contra { $attack_total}.
pirates-attack-miss-brief = { $attacker } falla contra { $defender }.

# Abordaje
pirates-resolve-boarding = Resolver abordaje
pirates-select-boarding-action = El cañón impactó. Elige cómo resolver la acción de abordaje
pirates-boarding-steal = Intentar robar una gema
pirates-boarding-push-left = Embestir al defensor hacia la izquierda
pirates-boarding-push-right = Embestir al defensor hacia la derecha
pirates-boarding-option-unknown = Acción de abordaje desconocida
pirates-must-resolve-boarding = Resuelve tu acción de abordaje pendiente antes de realizar otra acción de turno.
pirates-no-pending-boarding = No tienes ninguna acción de abordaje pendiente para resolver.
pirates-boarding-stale = La acción de abordaje pendiente ya no tiene un defensor válido, así que fue cancelada. Elige otra acción de turno.
pirates-boarding-option-unavailable = { $action } ya no está disponible contra { $defender }. Elige una de las opciones de abordaje actuales.
pirates-push-you = Embistes a { $target } hacia la { $direction } desde la posición { $old_pos } hasta { $new_pos }, moviéndolo { $distance } espacios. Tu bono de Embestida aportó { $bonus } espacios extra.
pirates-push-you-brief = Embistes a { $target } hasta la posición { $position }.
pirates-push-them = { $attacker } te embiste hacia la { $direction } desde la posición { $old_pos } hasta { $new_pos }, moviéndote { $distance } espacios.
pirates-push-them-brief = { $attacker } te embiste hasta la posición { $position }.
pirates-push = { $attacker } embiste a { $defender } hacia la { $direction } desde la posición { $old_pos } hasta { $new_pos }, una distancia de { $distance } espacios.
pirates-push-brief = { $attacker } embiste a { $defender } hasta la posición { $position }.
pirates-steal-rolls-you = Tu total de robo es { $steal}; el total de guardia de { $target } es { $defend}.
pirates-steal-rolls-you-brief = Robo { $steal}; guardia { $defend}.
pirates-steal-rolls-defender = El total de robo de { $attacker } es { $steal}; tu total de guardia es { $defend}.
pirates-steal-rolls-defender-brief = Robo { $steal}; tu guardia { $defend}.
pirates-steal-rolls-observer = { $attacker } intenta robarle a { $defender}: robo { $steal}, guardia { $defend}.
pirates-steal-rolls-observer-brief = { $attacker } roba con { $steal } contra { $defender } con { $defend}.
pirates-steal-success-you = Le robas { $gem } a { $target }. Tu cargamento vale { $attacker_score } puntos; el suyo vale { $defender_score}.
pirates-steal-success-you-brief = Le robas { $gem } a { $target }.
pirates-steal-success-them = { $attacker } te roba { $gem }. Su cargamento vale { $attacker_score } puntos; el tuyo vale { $defender_score}.
pirates-steal-success-them-brief = { $attacker } te roba { $gem }.
pirates-steal-success = { $attacker } le roba { $gem } a { $defender }. Sus cargamentos ahora valen { $attacker_score } y { $defender_score } puntos respectivamente.
pirates-steal-success-brief = { $attacker } le roba { $gem } a { $defender }.
pirates-steal-failed-you = Tu total de robo de { $steal } no supera el total de guardia de { $target } de { $defend}. No robas nada.
pirates-steal-failed-you-brief = Tu robo falla, { $steal } contra { $defend}.
pirates-steal-failed-defender = Detienes el robo de { $attacker }, { $defend } contra { $steal}, y conservas tu cargamento.
pirates-steal-failed-defender-brief = Detienes el robo de { $attacker }.
pirates-steal-failed = { $defender } detiene el robo de { $attacker }, { $defend } contra { $steal}.
pirates-steal-failed-brief = { $attacker } no logra robarle a { $defender }.
pirates-steal-no-gems-you = No puedes robarle a { $target } porque ya no lleva ninguna gema. Elige un empujón en su lugar.
pirates-steal-no-gems-you-brief = { $target } no tiene ninguna gema para robar.
pirates-steal-no-gems-defender = { $attacker } no puede robarte porque tu cargamento no contiene gemas.
pirates-steal-no-gems-defender-brief = No tienes ninguna gema para que { $attacker } robe.
pirates-steal-no-gems = { $attacker } no puede robarle a { $defender } porque el defensor no lleva gemas.
pirates-steal-no-gems-brief = { $defender } no tiene ninguna gema para robar.

# Habilidades y estado de habilidades
pirates-use-skill = Usar una habilidad
pirates-select-skill = Elige una habilidad desbloqueada
pirates-unknown-skill = Habilidad desconocida
pirates-skill-error = { $message }
pirates-skill-selection-stale = Esa selección de habilidad ya no está disponible en tu nivel o estado de partida actual. Vuelve a abrir el menú de habilidades y elige una disponible.
pirates-req-level = { $skill } requiere el nivel { $required}; estás en el nivel { $current}.
pirates-requires-level = { $action ->
    [move_2] Navegar dos espacios
    [move_3] Navegar tres espacios
   *[other] Esa acción
} requiere el nivel { $required}; estás en el nivel { $current}.
pirates-skill-cooldown = { $name } se está recuperando por { $turns } turnos más tuyos.
pirates-skill-active = { $name } ya está activa por { $turns } turnos más tuyos.
pirates-skill-already-activated-this-turn = Ya activaste una mejora de combate este turno. Realiza una acción de movimiento o de cañón a continuación.
pirates-skill-no-uses = Buscador de Gemas no tiene usos restantes en esta partida.
pirates-skill-no-gems = Buscador de Gemas no puede encontrar un objetivo porque no quedan gemas sin recuperar.
pirates-skill-no-targets = Ningún barco rival está dentro del alcance actual de { $range } espacios para esta habilidad.
pirates-skill-incompatible = { $skill } no se puede activar mientras { $active } está activa. Espera a que el efecto actual expire.
pirates-battleship-after-buff = Acorazado no se puede lanzar después de activar una mejora de combate este turno. Usa la mejora con un disparo de cañón normal, o espera a tu próximo turno.
pirates-menu-active = { $name } (activa por { $turns } turnos más)
pirates-menu-cooldown = { $name } (recuperándose por { $turns } turnos más)
pirates-menu-activate = Activar { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } usos restantes)
pirates-active-skill-status = { $skill }, quedan { $turns } turnos
pirates-no-active-skills = ninguna
pirates-skill-activated = { $player } activa { $skill}. { $effect }
pirates-skill-activated-brief = { $player } activa { $skill}.
pirates-buff-expired-you = Tu efecto de { $skill } expira antes de que comience este turno.
pirates-buff-expired-you-brief = Tu { $skill } expira.
pirates-buff-expired = El efecto de { $skill } de { $player } expira antes de que comience su turno.
pirates-buff-expired-brief = { $skill } de { $player } expira.

pirates-skill-instinct-name = Instinto del Marinero
pirates-skill-instinct-desc = Revisa cada sector de cinco espacios, incluidas las gemas sin recuperar y los barcos rivales. Esta acción de información no termina el turno.
pirates-instinct-header = Mapa de Instinto del Marinero, dividido en ocho sectores:
pirates-instinct-sector = Sector { $sector}, posiciones { $start } a { $end}: { $gems } { $gems ->
    [one] gema sin recuperar
   *[other] gemas sin recuperar
}, { $players } { $players ->
    [one] barco rival
   *[other] barcos rivales
}.

pirates-skill-portal-name = Portal
pirates-skill-portal-desc = Elige un océano diferente ocupado por un rival, o elige Aleatorio para teletransportarte a cualquier espacio del mapa. Enfriamiento: 3 de tus turnos.
pirates-resolve-portal = Elegir destino del Portal
pirates-select-portal-ocean = Elige un océano diferente ocupado por un rival, o elige Aleatorio para cualquier espacio del mapa
pirates-portal-option = { $ocean }; barcos: { $ships}; { $gems } { $gems ->
    [one] gema sin recuperar
   *[other] gemas sin recuperar
}
pirates-portal-option-random = Espacio aleatorio del mapa
pirates-portal-option-unavailable = Ese océano no es un destino válido de Portal porque es tu océano actual o ningún barco rival lo ocupa. Elige otro destino.
pirates-must-resolve-portal = Como usaste Portal, tu turno queda fijado a esa habilidad. Elige un destino, o elige Aleatorio, para completar el Portal y terminar tu turno.
pirates-no-pending-portal = No tienes ningún destino de Portal pendiente por resolver.
pirates-portal-no-ships = No hay ningún destino específico de Portal en océano rival disponible, pero Aleatorio aún puede enviarte a cualquier espacio del mapa.
pirates-portal-fizzle-you = Tu destino de Portal ya no es válido. Elige Aleatorio para teletransportarte a cualquier lugar del mapa, o elige otro destino válido.
pirates-portal-fizzle-you-brief = Elige Aleatorio u otro destino válido de Portal.
pirates-portal-fizzle = El destino de Portal de { $player } ya no es válido.
pirates-portal-fizzle-brief = { $player } debe elegir otro destino de Portal.
pirates-portal-success-you = Viajas a través del Portal hasta { $ocean}, llegando a la posición { $position}. Portal entra en enfriamiento por 3 de tus turnos.
pirates-portal-success-you-brief = Te teletransportas a la posición { $position } en { $ocean}.
pirates-portal-success = { $player } viaja a través de un Portal hasta { $ocean}, llegando a la posición { $position}.
pirates-portal-success-brief = { $player } se teletransporta a la posición { $position}.

pirates-skill-seeker-name = Buscador de Gemas
pirates-skill-seeker-desc = Revela la posición exacta de una gema sin recuperar. Tres usos por partida; usarla no termina el turno.
pirates-gem-seeker-reveal = Buscador de Gemas localiza { $gem } en la posición { $position}. Te quedan { $uses } usos en esta partida.

pirates-skill-sword-name = Espadachín
pirates-skill-sword-desc = Gana +2 de ataque por 3 de tus turnos. Enfriamiento: 6 turnos. No se puede superponer con Capitán Experto.
pirates-sword-fighter-activated = Activas Espadachín: +{ $bonus } de ataque por { $turns } de tus turnos. Enfriamiento: { $cooldown } turnos. Aún puedes moverte o disparar este turno.
pirates-sword-fighter-activated-brief = Espadachín activo: +{ $bonus } de ataque.

pirates-skill-push-name = Velocidad de Embestida
pirates-skill-push-desc = Añade 2 espacios a los empujones de abordaje por 3 de tus turnos. Enfriamiento: 6 turnos.
pirates-push-activated = Activas Velocidad de Embestida: +{ $bonus } espacios a los empujones de abordaje por { $turns } de tus turnos. Enfriamiento: { $cooldown } turnos. Aún puedes moverte o disparar este turno.
pirates-push-activated-brief = Velocidad de Embestida activa: +{ $bonus } de distancia de empuje.

pirates-skill-captain-name = Capitán Experto
pirates-skill-captain-desc = Gana +1 de ataque y +1 de defensa por 4 de tus turnos. Enfriamiento: 7 turnos. No se puede superponer con Espadachín.
pirates-skilled-captain-activated = Activas Capitán Experto: +{ $attack } de ataque y +{ $defense } de defensa por { $turns } de tus turnos. Enfriamiento: { $cooldown } turnos. Aún puedes moverte o disparar este turno.
pirates-skilled-captain-activated-brief = Capitán Experto activo: +{ $attack } de ataque, +{ $defense } de defensa.

pirates-skill-battleship-name = Acorazado
pirates-skill-battleship-desc = Dispara dos tiros de cañón dirigidos a tripulaciones, sin recompensas de abordaje. Esto termina el turno. Enfriamiento: 4 turnos.
pirates-battleship-activated = Lanzas Acorazado por { $shots } disparos de cañón. Tu tripulación elige el objetivo más valioso al alcance para cada disparo; los impactos no otorgan abordaje. Enfriamiento: { $cooldown } turnos.
pirates-battleship-activated-brief = Lanzas Acorazado por { $shots } disparos.
pirates-battleship-activated-player = { $player } lanza Acorazado por { $shots } disparos de cañón. Los impactos de estos disparos no otorgan abordaje.
pirates-battleship-activated-player-brief = { $player } lanza Acorazado.
pirates-battleship-shot = Tu tripulación dispara el tiro { $shot } de Acorazado contra { $target}.
pirates-battleship-shot-brief = Tiro { $shot } contra { $target}.
pirates-battleship-shot-player = La tripulación de { $player } dispara el tiro { $shot } de Acorazado contra { $target}.
pirates-battleship-shot-player-brief = { $player } dispara contra { $target}.
pirates-battleship-no-targets = Tu tripulación no puede disparar el tiro { $shot } porque ningún rival queda dentro de { $range } espacios. Acorazado termina.
pirates-battleship-no-targets-brief = Sin objetivo para el tiro { $shot}.
pirates-battleship-no-targets-player = { $player } no puede disparar el tiro { $shot } de Acorazado porque ningún rival queda dentro de { $range } espacios.
pirates-battleship-no-targets-player-brief = { $player } no tiene objetivo para el tiro { $shot}.

pirates-skill-devastation-name = Devastación Doble
pirates-skill-devastation-desc = Aumenta el alcance normal del cañón de 5 a 10 espacios por 3 de tus turnos. Enfriamiento: 10 turnos. Incompatible con Acorazado.
pirates-double-devastation-activated = Activas Devastación Doble: el alcance del cañón se vuelve { $range } espacios por { $turns } de tus turnos. Enfriamiento: { $cooldown } turnos. Aún puedes moverte o disparar este turno.
pirates-double-devastation-activated-brief = Devastación Doble activa: alcance { $range}.

# Opciones y validación
pirates-set-combat-xp-multiplier = Multiplicador de XP de combate: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Ingresa un multiplicador de XP de combate de 0.1 a 3.0
pirates-option-changed-combat-xp = Multiplicador de XP de combate establecido en { $combat_multiplier}.
pirates-desc-combat-xp-multiplier = Escala la XP de los impactos de cañón y las defensas exitosas. El multiplicador de la Luna Dorada se aplica por separado (por defecto 1.0, rango 0.1-3.0).
pirates-set-find-gem-xp-multiplier = Multiplicador de XP de recuperación de gemas: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Ingresa un multiplicador de XP de recuperación de gemas de 0.1 a 3.0
pirates-option-changed-find-gem-xp = Multiplicador de XP de recuperación de gemas establecido en { $find_gem_multiplier}.
pirates-desc-find-gem-xp-multiplier = Escala la XP otorgada cuando un barco recupera una gema, incluso tras un movimiento forzado (por defecto 1.0, rango 0.1-3.0).
pirates-set-gem-stealing = Robo de gemas: { $mode }
pirates-select-gem-stealing = Elige cómo los tiros de robo por abordaje usan los bonos de combate
pirates-option-changed-stealing = Robo de gemas establecido en { $mode}.
pirates-desc-gem-stealing = Controla si el robo de gemas está disponible después de un impacto directo y si los bonos activos de ataque y defensa modifican el tiro de robo.
pirates-stealing-with-bonus = Activado con bonos de combate
pirates-stealing-no-bonus = Activado sin bonos de combate
pirates-stealing-disabled = Desactivado; el abordaje solo puede empujar
pirates-error-combat-xp-range = El multiplicador de XP de combate es { $value}, fuera del rango permitido de { $min } a { $max}. Ajústalo dentro de ese rango antes de empezar.
pirates-error-gem-xp-range = El multiplicador de XP de recuperación de gemas es { $value}, fuera del rango permitido de { $min } a { $max}. Ajústalo dentro de ese rango antes de empezar.
pirates-error-stealing-mode = El modo de robo de gemas guardado, { $mode}, no es compatible. Elige uno de los modos de robo de gemas listados antes de empezar.

# Nombres de océanos
pirates-ocean-rory = Océano de Rory
pirates-ocean-dev = Abismo del Desarrollador
pirates-ocean-par = Mar del Paraíso del Programador
pirates-ocean-pal = Aguas del Palacio
pirates-ocean-sil = Estrecho de Silva
pirates-ocean-kai = Corriente de Kai
pirates-ocean-gam = Golfo del Jugador
pirates-ocean-ser = Mar de la Sala de Servidores
pirates-ocean-bat = Bahía de Batalla
pirates-ocean-cod = Canal de Compilación de Código
pirates-ocean-unknown = Océano Desconocido

# Nombres de gemas
pirates-gem-0 = ópalo
pirates-gem-1 = rubí
pirates-gem-2 = granate
pirates-gem-3 = diamante
pirates-gem-4 = zafiro
pirates-gem-5 = esmeralda
pirates-gem-6 = gema del palacio
pirates-gem-7 = gema grande de plástico
pirates-gem-8 = impresionante piedra azul de mala muerte
pirates-gem-9 = amatista
pirates-gem-10 = anillo dorado
pirates-gem-11 = impresionante piedra roja pulposa
pirates-gem-12 = impresionante piedra roja sangrienta
pirates-gem-13 = piedra lunar
pirates-gem-14 = lapislázuli
pirates-gem-15 = ámbar
pirates-gem-16 = citrino
pirates-gem-17 = perla negra definitivamente no maldita (MR)
pirates-gem-unknown = gema desconocida
pirates-gem-none = sin gemas
